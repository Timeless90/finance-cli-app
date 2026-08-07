from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import isfinite

import numpy as np


@dataclass(frozen=True, slots=True)
class CapitalProject:
    project_id: str
    name: str
    initial_investment: float
    cash_flows: tuple[float, ...]
    annual_nopat: tuple[float, ...] = ()
    terminal_value: float = 0.0
    strategic_score: float = 0.0
    cash_headroom_impact: float = 0.0
    leverage_delta: float = 0.0
    interest_cover_delta: float = 0.0


@dataclass(frozen=True, slots=True)
class ProjectValuation:
    project_id: str
    discount_rate: float
    npv: float
    irr: float | None
    roic: float | None
    payback_years: float | None


@dataclass(frozen=True, slots=True)
class MonteCarloNpvResult:
    project_id: str
    paths: int
    seed: int
    mean_npv: float
    p10: float
    p50: float
    p90: float
    probability_negative_npv: float


@dataclass(frozen=True, slots=True)
class PortfolioConstraints:
    budget: float
    opening_cash_headroom: float
    minimum_cash_headroom: float
    base_leverage: float
    maximum_leverage: float
    base_interest_cover: float
    minimum_interest_cover: float


@dataclass(frozen=True, slots=True)
class PortfolioSelection:
    selected_project_ids: tuple[str, ...]
    total_investment: float
    total_risk_adjusted_npv: float
    ending_cash_headroom: float
    ending_leverage: float
    ending_interest_cover: float
    constraints_satisfied: bool


@dataclass(frozen=True, slots=True)
class FundingOption:
    option_id: str
    amount: float
    annual_rate: float
    term_years: int
    upfront_fee: float = 0.0
    amortizing: bool = True


@dataclass(frozen=True, slots=True)
class FundingScenario:
    option_id: str
    gross_proceeds: float
    net_proceeds: float
    annual_interest: float
    annual_principal: float
    annual_debt_service: float
    leverage_after: float
    interest_cover_after: float
    covenant_headroom: float


class ProjectValuationService:
    def evaluate(self, project: CapitalProject, discount_rate: float) -> ProjectValuation:
        if discount_rate <= -1.0:
            raise ValueError("discount_rate must be greater than -100%")
        if project.initial_investment <= 0.0:
            raise ValueError("initial_investment must be positive")
        if not project.cash_flows:
            raise ValueError("at least one project cash flow is required")

        npv = -project.initial_investment
        for year, cash_flow in enumerate(project.cash_flows, start=1):
            value = cash_flow
            if year == len(project.cash_flows):
                value += project.terminal_value
            npv += value / ((1.0 + discount_rate) ** year)

        return ProjectValuation(
            project_id=project.project_id,
            discount_rate=discount_rate,
            npv=float(npv),
            irr=self._irr(project),
            roic=self._roic(project),
            payback_years=self._payback(project),
        )

    def _irr(self, project: CapitalProject) -> float | None:
        cash_flows = [-project.initial_investment, *project.cash_flows]
        cash_flows[-1] += project.terminal_value

        def objective(rate: float) -> float:
            return sum(value / ((1.0 + rate) ** period) for period, value in enumerate(cash_flows))

        low = -0.999
        high = 10.0
        f_low = objective(low)
        f_high = objective(high)
        if f_low == 0.0:
            return low
        if f_high == 0.0:
            return high
        if f_low * f_high > 0.0:
            return None

        for _ in range(200):
            mid = (low + high) / 2.0
            value = objective(mid)
            if abs(value) < 1e-10:
                return mid
            if f_low * value <= 0.0:
                high = mid
                f_high = value
            else:
                low = mid
                f_low = value
        result = (low + high) / 2.0
        return result if isfinite(result) else None

    def _roic(self, project: CapitalProject) -> float | None:
        if not project.annual_nopat:
            return None
        return float(np.mean(project.annual_nopat) / project.initial_investment)

    def _payback(self, project: CapitalProject) -> float | None:
        remaining = project.initial_investment
        for year, cash_flow in enumerate(project.cash_flows, start=1):
            prior = remaining
            remaining -= cash_flow
            if remaining <= 0.0:
                if cash_flow <= 0.0:
                    return float(year)
                fraction = prior / cash_flow
                return float(year - 1 + fraction)
        return None


class MonteCarloNpvEngine:
    def simulate(
        self,
        project: CapitalProject,
        *,
        discount_rate: float,
        paths: int = 10_000,
        seed: int = 42,
        cash_flow_volatility: float = 0.15,
        risk_event_probability: float = 0.0,
        risk_event_impact: float = 0.0,
        scenario_multiplier: float = 1.0,
    ) -> MonteCarloNpvResult:
        if paths < 100:
            raise ValueError("paths must be at least 100")
        if cash_flow_volatility < 0.0:
            raise ValueError("cash_flow_volatility cannot be negative")
        if not 0.0 <= risk_event_probability <= 1.0:
            raise ValueError("risk_event_probability must be between 0 and 1")
        if scenario_multiplier <= 0.0:
            raise ValueError("scenario_multiplier must be positive")

        rng = np.random.default_rng(seed)
        base = np.asarray(project.cash_flows, dtype=float)
        multipliers = rng.lognormal(
            mean=-0.5 * cash_flow_volatility**2,
            sigma=cash_flow_volatility,
            size=(paths, len(base)),
        )
        simulated = base[None, :] * multipliers * scenario_multiplier

        if risk_event_probability > 0.0 and risk_event_impact != 0.0:
            events = rng.random(paths) < risk_event_probability
            simulated[events, :] *= 1.0 + risk_event_impact

        discount = np.power(1.0 + discount_rate, np.arange(1, len(base) + 1, dtype=float))
        npvs = -project.initial_investment + np.sum(simulated / discount[None, :], axis=1)
        if project.terminal_value:
            npvs += project.terminal_value / discount[-1]

        return MonteCarloNpvResult(
            project_id=project.project_id,
            paths=paths,
            seed=seed,
            mean_npv=float(np.mean(npvs)),
            p10=float(np.quantile(npvs, 0.10)),
            p50=float(np.quantile(npvs, 0.50)),
            p90=float(np.quantile(npvs, 0.90)),
            probability_negative_npv=float(np.mean(npvs < 0.0)),
        )


class CapitalPortfolioOptimizer:
    def optimize(
        self,
        projects: list[CapitalProject],
        *,
        risk_adjusted_npvs: dict[str, float],
        constraints: PortfolioConstraints,
        strategic_weight: float = 0.0,
    ) -> PortfolioSelection:
        if len(projects) > 22:
            raise ValueError("exact optimizer supports at most 22 projects")
        if constraints.budget < 0.0:
            raise ValueError("budget cannot be negative")

        best_score = float("-inf")
        best: PortfolioSelection | None = None

        for size in range(len(projects) + 1):
            for subset in combinations(projects, size):
                investment = sum(project.initial_investment for project in subset)
                cash = constraints.opening_cash_headroom + sum(
                    project.cash_headroom_impact - project.initial_investment for project in subset
                )
                leverage = constraints.base_leverage + sum(project.leverage_delta for project in subset)
                interest_cover = constraints.base_interest_cover + sum(
                    project.interest_cover_delta for project in subset
                )
                satisfied = (
                    investment <= constraints.budget
                    and cash >= constraints.minimum_cash_headroom
                    and leverage <= constraints.maximum_leverage
                    and interest_cover >= constraints.minimum_interest_cover
                )
                if not satisfied:
                    continue

                total_npv = sum(risk_adjusted_npvs.get(project.project_id, 0.0) for project in subset)
                score = total_npv + strategic_weight * sum(project.strategic_score for project in subset)
                if score <= best_score:
                    continue

                best_score = score
                best = PortfolioSelection(
                    selected_project_ids=tuple(project.project_id for project in subset),
                    total_investment=float(investment),
                    total_risk_adjusted_npv=float(total_npv),
                    ending_cash_headroom=float(cash),
                    ending_leverage=float(leverage),
                    ending_interest_cover=float(interest_cover),
                    constraints_satisfied=True,
                )

        if best is not None:
            return best

        return PortfolioSelection(
            selected_project_ids=(),
            total_investment=0.0,
            total_risk_adjusted_npv=0.0,
            ending_cash_headroom=constraints.opening_cash_headroom,
            ending_leverage=constraints.base_leverage,
            ending_interest_cover=constraints.base_interest_cover,
            constraints_satisfied=(
                constraints.opening_cash_headroom >= constraints.minimum_cash_headroom
                and constraints.base_leverage <= constraints.maximum_leverage
                and constraints.base_interest_cover >= constraints.minimum_interest_cover
            ),
        )


class FundingScenarioEngine:
    def evaluate(
        self,
        option: FundingOption,
        *,
        base_debt: float,
        base_ebitda: float,
        base_interest_expense: float,
        maximum_leverage: float,
    ) -> FundingScenario:
        if option.amount <= 0.0:
            raise ValueError("funding amount must be positive")
        if option.term_years <= 0:
            raise ValueError("term_years must be positive")
        if option.annual_rate < 0.0:
            raise ValueError("annual_rate cannot be negative")
        if base_ebitda <= 0.0:
            raise ValueError("base_ebitda must be positive")

        annual_interest = option.amount * option.annual_rate
        annual_principal = option.amount / option.term_years if option.amortizing else 0.0
        debt_after = base_debt + option.amount
        interest_after = base_interest_expense + annual_interest
        leverage_after = debt_after / base_ebitda
        interest_cover_after = base_ebitda / interest_after if interest_after > 0.0 else float("inf")

        return FundingScenario(
            option_id=option.option_id,
            gross_proceeds=option.amount,
            net_proceeds=option.amount - option.upfront_fee,
            annual_interest=annual_interest,
            annual_principal=annual_principal,
            annual_debt_service=annual_interest + annual_principal,
            leverage_after=leverage_after,
            interest_cover_after=interest_cover_after,
            covenant_headroom=maximum_leverage - leverage_after,
        )
