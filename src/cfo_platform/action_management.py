from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from enum import StrEnum


ZERO = Decimal("0")
ONE = Decimal("1")


class ActionStatus(StrEnum):
    DRAFT = "draft"
    PLANNED = "planned"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ImpactMetric(StrEnum):
    EBITDA = "ebitda"
    CASH = "cash"
    COVENANT = "covenant"


class EscalationLevel(StrEnum):
    NONE = "none"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class ActionImpact:
    period: int
    metric: ImpactMetric
    amount: Decimal
    impact_key: str
    covenant_id: str | None = None

    def __post_init__(self) -> None:
        if self.period < 1:
            raise ValueError("impact period must be positive")
        if not self.impact_key.strip():
            raise ValueError("impact_key must not be empty")
        if self.metric == ImpactMetric.COVENANT and not self.covenant_id:
            raise ValueError("covenant impacts require covenant_id")
        if self.metric != ImpactMetric.COVENANT and self.covenant_id is not None:
            raise ValueError("covenant_id is only valid for covenant impacts")


@dataclass(frozen=True, slots=True)
class ManagementAction:
    action_id: str
    title: str
    owner: str
    due_period: int
    cost: Decimal
    impacts: tuple[ActionImpact, ...]
    confidence: Decimal = ONE
    status: ActionStatus = ActionStatus.DRAFT
    description: str = ""

    def __post_init__(self) -> None:
        if not self.action_id.strip():
            raise ValueError("action_id must not be empty")
        if not self.title.strip() or not self.owner.strip():
            raise ValueError("action title and owner must not be empty")
        if self.due_period < 1:
            raise ValueError("due_period must be positive")
        if self.cost < ZERO:
            raise ValueError("action cost must be non-negative")
        if not ZERO <= self.confidence <= ONE:
            raise ValueError("confidence must be between 0 and 1")
        keys = [impact.impact_key for impact in self.impacts]
        if len(keys) != len(set(keys)):
            raise ValueError("an action must not contain duplicate impact keys")


class InMemoryActionRepository:
    def __init__(self) -> None:
        self._actions: dict[str, ManagementAction] = {}

    def save(self, action: ManagementAction) -> ManagementAction:
        if action.action_id in self._actions:
            raise ValueError(f"action already exists: {action.action_id}")
        self._actions[action.action_id] = action
        return action

    def replace(self, action: ManagementAction) -> ManagementAction:
        if action.action_id not in self._actions:
            raise KeyError(action.action_id)
        self._actions[action.action_id] = action
        return action

    def get(self, action_id: str) -> ManagementAction:
        try:
            return self._actions[action_id]
        except KeyError as exc:
            raise KeyError(f"unknown action: {action_id}") from exc

    def list(self) -> tuple[ManagementAction, ...]:
        return tuple(self._actions[key] for key in sorted(self._actions))


class ActionCatalogueService:
    def __init__(self, repository: InMemoryActionRepository) -> None:
        self._repository = repository

    def register(self, action: ManagementAction) -> ManagementAction:
        return self._repository.save(action)

    def get(self, action_id: str) -> ManagementAction:
        return self._repository.get(action_id)

    def list(self) -> tuple[ManagementAction, ...]:
        return self._repository.list()

    def change_status(self, action_id: str, status: ActionStatus) -> ManagementAction:
        action = self._repository.get(action_id)
        self._validate_transition(action.status, status)
        updated = replace(action, status=status)
        return self._repository.replace(updated)

    @staticmethod
    def _validate_transition(current: ActionStatus, target: ActionStatus) -> None:
        allowed = {
            ActionStatus.DRAFT: {ActionStatus.PLANNED, ActionStatus.CANCELLED},
            ActionStatus.PLANNED: {ActionStatus.ACTIVE, ActionStatus.CANCELLED},
            ActionStatus.ACTIVE: {
                ActionStatus.BLOCKED,
                ActionStatus.COMPLETED,
                ActionStatus.CANCELLED,
            },
            ActionStatus.BLOCKED: {
                ActionStatus.ACTIVE,
                ActionStatus.CANCELLED,
            },
            ActionStatus.COMPLETED: set(),
            ActionStatus.CANCELLED: set(),
        }
        if target == current:
            return
        if target not in allowed[current]:
            raise ValueError(f"invalid action status transition: {current} -> {target}")


@dataclass(frozen=True, slots=True)
class ActionSimulationPeriod:
    period: int
    ebitda_effect: Decimal
    cash_effect: Decimal
    covenant_effects: tuple[tuple[str, Decimal], ...]


@dataclass(frozen=True, slots=True)
class ActionSimulationResult:
    selected_action_ids: tuple[str, ...]
    total_cost: Decimal
    expected_ebitda_effect: Decimal
    expected_cash_effect: Decimal
    covenant_effects: tuple[tuple[str, Decimal], ...]
    periods: tuple[ActionSimulationPeriod, ...]


class ActionSimulationEngine:
    def simulate(self, actions: tuple[ManagementAction, ...]) -> ActionSimulationResult:
        if not actions:
            raise ValueError("at least one action is required")
        self._check_duplicate_impacts(actions)
        by_period: dict[int, dict[str, Decimal]] = {}
        covenant_by_period: dict[int, dict[str, Decimal]] = {}
        total_cost = ZERO

        for action in actions:
            if action.status == ActionStatus.CANCELLED:
                continue
            total_cost += action.cost
            for impact in action.impacts:
                weighted = impact.amount * action.confidence
                bucket = by_period.setdefault(
                    impact.period,
                    {"ebitda": ZERO, "cash": ZERO},
                )
                if impact.metric == ImpactMetric.EBITDA:
                    bucket["ebitda"] += weighted
                elif impact.metric == ImpactMetric.CASH:
                    bucket["cash"] += weighted
                else:
                    assert impact.covenant_id is not None
                    covenant_bucket = covenant_by_period.setdefault(impact.period, {})
                    covenant_bucket[impact.covenant_id] = (
                        covenant_bucket.get(impact.covenant_id, ZERO) + weighted
                    )

        periods = tuple(
            ActionSimulationPeriod(
                period=period,
                ebitda_effect=by_period.get(period, {}).get("ebitda", ZERO),
                cash_effect=by_period.get(period, {}).get("cash", ZERO),
                covenant_effects=tuple(sorted(covenant_by_period.get(period, {}).items())),
            )
            for period in sorted(set(by_period) | set(covenant_by_period))
        )
        covenant_totals: dict[str, Decimal] = {}
        for values in covenant_by_period.values():
            for covenant_id, amount in values.items():
                covenant_totals[covenant_id] = covenant_totals.get(covenant_id, ZERO) + amount

        return ActionSimulationResult(
            selected_action_ids=tuple(action.action_id for action in actions),
            total_cost=total_cost,
            expected_ebitda_effect=sum(
                (period.ebitda_effect for period in periods), start=ZERO
            ),
            expected_cash_effect=sum(
                (period.cash_effect for period in periods), start=ZERO
            ),
            covenant_effects=tuple(sorted(covenant_totals.items())),
            periods=periods,
        )

    @staticmethod
    def _check_duplicate_impacts(actions: tuple[ManagementAction, ...]) -> None:
        owners: dict[str, str] = {}
        for action in actions:
            if action.status == ActionStatus.CANCELLED:
                continue
            for impact in action.impacts:
                previous = owners.get(impact.impact_key)
                if previous is not None and previous != action.action_id:
                    raise ValueError(
                        "duplicate financial impact detected for "
                        f"{impact.impact_key}: {previous}, {action.action_id}"
                    )
                owners[impact.impact_key] = action.action_id


@dataclass(frozen=True, slots=True)
class ActionPriority:
    action_id: str
    score: Decimal
    expected_benefit: Decimal
    cost: Decimal
    benefit_cost_ratio: Decimal | None


class ActionPortfolioPrioritizer:
    def prioritize(self, actions: tuple[ManagementAction, ...]) -> tuple[ActionPriority, ...]:
        priorities: list[ActionPriority] = []
        for action in actions:
            if action.status == ActionStatus.CANCELLED:
                continue
            benefit = sum(
                (
                    impact.amount * action.confidence
                    for impact in action.impacts
                    if impact.metric in {ImpactMetric.EBITDA, ImpactMetric.CASH}
                ),
                start=ZERO,
            )
            ratio = benefit / action.cost if action.cost > ZERO else None
            urgency = ONE / Decimal(action.due_period)
            efficiency = ratio if ratio is not None else benefit
            score = efficiency * Decimal("0.6") + urgency * Decimal("0.4")
            priorities.append(
                ActionPriority(
                    action_id=action.action_id,
                    score=score,
                    expected_benefit=benefit,
                    cost=action.cost,
                    benefit_cost_ratio=ratio,
                )
            )
        priorities.sort(key=lambda item: (item.score, item.action_id), reverse=True)
        return tuple(priorities)


@dataclass(frozen=True, slots=True)
class ActionReview:
    action_id: str
    status: ActionStatus
    current_period: int
    due_period: int
    escalation: EscalationLevel
    reason: str | None


class ActionReviewService:
    def review(self, action: ManagementAction, current_period: int) -> ActionReview:
        if current_period < 1:
            raise ValueError("current_period must be positive")
        if action.status == ActionStatus.BLOCKED:
            return ActionReview(
                action_id=action.action_id,
                status=action.status,
                current_period=current_period,
                due_period=action.due_period,
                escalation=EscalationLevel.CRITICAL,
                reason="action is blocked",
            )
        if (
            current_period > action.due_period
            and action.status not in {ActionStatus.COMPLETED, ActionStatus.CANCELLED}
        ):
            return ActionReview(
                action_id=action.action_id,
                status=action.status,
                current_period=current_period,
                due_period=action.due_period,
                escalation=EscalationLevel.WARNING,
                reason="action is overdue",
            )
        return ActionReview(
            action_id=action.action_id,
            status=action.status,
            current_period=current_period,
            due_period=action.due_period,
            escalation=EscalationLevel.NONE,
            reason=None,
        )


@dataclass(frozen=True, slots=True)
class BenefitObservation:
    action_id: str
    metric: ImpactMetric
    period: int
    planned_amount: Decimal
    realized_amount: Decimal
    covenant_id: str | None = None

    def __post_init__(self) -> None:
        if self.period < 1:
            raise ValueError("benefit period must be positive")
        if self.metric == ImpactMetric.COVENANT and not self.covenant_id:
            raise ValueError("covenant benefit observations require covenant_id")


@dataclass(frozen=True, slots=True)
class BenefitTrackingResult:
    action_id: str
    planned_amount: Decimal
    realized_amount: Decimal
    variance: Decimal
    realization_ratio: Decimal | None


class BenefitTrackingService:
    def summarize(
        self,
        observations: tuple[BenefitObservation, ...],
    ) -> tuple[BenefitTrackingResult, ...]:
        grouped: dict[str, tuple[Decimal, Decimal]] = {}
        for observation in observations:
            planned, realized = grouped.get(observation.action_id, (ZERO, ZERO))
            grouped[observation.action_id] = (
                planned + observation.planned_amount,
                realized + observation.realized_amount,
            )

        results = []
        for action_id in sorted(grouped):
            planned, realized = grouped[action_id]
            results.append(
                BenefitTrackingResult(
                    action_id=action_id,
                    planned_amount=planned,
                    realized_amount=realized,
                    variance=realized - planned,
                    realization_ratio=realized / planned if planned != ZERO else None,
                )
            )
        return tuple(results)
