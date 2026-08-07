from decimal import Decimal

import pytest

from cfo_platform.action_management import (
    ActionCatalogueService,
    ActionImpact,
    ActionPortfolioPrioritizer,
    ActionReviewService,
    ActionSimulationEngine,
    ActionStatus,
    BenefitObservation,
    BenefitTrackingService,
    EscalationLevel,
    ImpactMetric,
    InMemoryActionRepository,
    ManagementAction,
)


def _action(
    action_id: str,
    *,
    cost: str = "100",
    confidence: str = "1",
    due_period: int = 3,
    status: ActionStatus = ActionStatus.PLANNED,
    impacts: tuple[ActionImpact, ...] | None = None,
) -> ManagementAction:
    return ManagementAction(
        action_id=action_id,
        title=f"Action {action_id}",
        owner="FP&A",
        due_period=due_period,
        cost=Decimal(cost),
        confidence=Decimal(confidence),
        status=status,
        impacts=impacts
        or (
            ActionImpact(
                period=2,
                metric=ImpactMetric.EBITDA,
                amount=Decimal("300"),
                impact_key=f"{action_id}:ebitda",
            ),
        ),
    )


def test_action_catalogue_and_status_workflow() -> None:
    catalogue = ActionCatalogueService(InMemoryActionRepository())
    action = _action("A1", status=ActionStatus.DRAFT)

    catalogue.register(action)
    planned = catalogue.change_status("A1", ActionStatus.PLANNED)
    active = catalogue.change_status("A1", ActionStatus.ACTIVE)
    completed = catalogue.change_status("A1", ActionStatus.COMPLETED)

    assert planned.status == ActionStatus.PLANNED
    assert active.status == ActionStatus.ACTIVE
    assert completed.status == ActionStatus.COMPLETED
    assert catalogue.get("A1") == completed

    with pytest.raises(ValueError, match="invalid action status transition"):
        catalogue.change_status("A1", ActionStatus.ACTIVE)


def test_action_simulation_integrates_timing_financials_and_confidence() -> None:
    engine = ActionSimulationEngine()
    action = _action(
        "A1",
        cost="200",
        confidence="0.5",
        impacts=(
            ActionImpact(
                period=1,
                metric=ImpactMetric.EBITDA,
                amount=Decimal("400"),
                impact_key="A1:ebitda:p1",
            ),
            ActionImpact(
                period=2,
                metric=ImpactMetric.CASH,
                amount=Decimal("300"),
                impact_key="A1:cash:p2",
            ),
            ActionImpact(
                period=2,
                metric=ImpactMetric.COVENANT,
                amount=Decimal("0.20"),
                impact_key="A1:leverage:p2",
                covenant_id="leverage",
            ),
        ),
    )

    result = engine.simulate((action,))

    assert result.total_cost == Decimal("200")
    assert result.expected_ebitda_effect == Decimal("200.0")
    assert result.expected_cash_effect == Decimal("150.0")
    assert result.covenant_effects == (("leverage", Decimal("0.100")),)
    assert result.periods[0].period == 1
    assert result.periods[0].ebitda_effect == Decimal("200.0")
    assert result.periods[1].cash_effect == Decimal("150.0")


def test_action_simulation_rejects_duplicate_financial_impacts() -> None:
    engine = ActionSimulationEngine()
    duplicate = "shared:pricing:ebitda"
    first = _action(
        "A1",
        impacts=(
            ActionImpact(
                period=1,
                metric=ImpactMetric.EBITDA,
                amount=Decimal("100"),
                impact_key=duplicate,
            ),
        ),
    )
    second = _action(
        "A2",
        impacts=(
            ActionImpact(
                period=1,
                metric=ImpactMetric.EBITDA,
                amount=Decimal("50"),
                impact_key=duplicate,
            ),
        ),
    )

    with pytest.raises(ValueError, match="duplicate financial impact detected"):
        engine.simulate((first, second))


def test_action_portfolio_prioritization_is_deterministic() -> None:
    prioritizer = ActionPortfolioPrioritizer()
    high = _action("HIGH", cost="100", due_period=1)
    low = _action("LOW", cost="300", due_period=6)

    first = prioritizer.prioritize((low, high))
    second = prioritizer.prioritize((low, high))

    assert first == second
    assert first[0].action_id == "HIGH"
    assert first[0].score > first[1].score


def test_review_escalates_blocked_and_overdue_actions() -> None:
    service = ActionReviewService()
    blocked = _action("BLOCKED", status=ActionStatus.BLOCKED)
    overdue = _action("OVERDUE", due_period=2, status=ActionStatus.ACTIVE)

    blocked_review = service.review(blocked, current_period=2)
    overdue_review = service.review(overdue, current_period=3)

    assert blocked_review.escalation == EscalationLevel.CRITICAL
    assert blocked_review.reason == "action is blocked"
    assert overdue_review.escalation == EscalationLevel.WARNING
    assert overdue_review.reason == "action is overdue"


def test_benefit_tracking_measures_realized_vs_planned() -> None:
    service = BenefitTrackingService()
    results = service.summarize(
        (
            BenefitObservation(
                action_id="A1",
                metric=ImpactMetric.EBITDA,
                period=1,
                planned_amount=Decimal("100"),
                realized_amount=Decimal("80"),
            ),
            BenefitObservation(
                action_id="A1",
                metric=ImpactMetric.CASH,
                period=2,
                planned_amount=Decimal("50"),
                realized_amount=Decimal("60"),
            ),
        )
    )

    assert len(results) == 1
    result = results[0]
    assert result.planned_amount == Decimal("150")
    assert result.realized_amount == Decimal("140")
    assert result.variance == Decimal("-10")
    assert result.realization_ratio == Decimal("140") / Decimal("150")
