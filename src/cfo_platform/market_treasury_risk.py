from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import log, sqrt
from statistics import NormalDist

import numpy as np
from numpy.typing import NDArray
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import chi2, genpareto, multivariate_t, rankdata, t

FloatArray = NDArray[np.float64]


class ExposureType(StrEnum):
    FX = "fx"
    INTEREST_RATE = "interest_rate"
    COMMODITY = "commodity"
    FUNDING = "funding"


@dataclass(frozen=True, slots=True)
class MarketExposure:
    exposure_id: str
    exposure_type: ExposureType
    risk_factor: str
    amount: float
    currency: str
    delta: float = 1.0

    def __post_init__(self) -> None:
        if not self.exposure_id.strip():
            raise ValueError("exposure_id must not be empty")
        if not self.risk_factor.strip():
            raise ValueError("risk_factor must not be empty")
        if not self.currency.strip():
            raise ValueError("currency must not be empty")


@dataclass(frozen=True, slots=True)
class NetExposure:
    risk_factor: str
    gross_long: float
    gross_short: float
    net_amount: float
    delta_equivalent: float


class ExposureManagementService:
    def aggregate(self, exposures: list[MarketExposure]) -> list[NetExposure]:
        grouped: dict[str, list[MarketExposure]] = {}
        for exposure in exposures:
            grouped.setdefault(exposure.risk_factor, []).append(exposure)
        result: list[NetExposure] = []
        for risk_factor, items in sorted(grouped.items()):
            gross_long = sum(max(item.amount, 0.0) for item in items)
            gross_short = sum(abs(min(item.amount, 0.0)) for item in items)
            result.append(
                NetExposure(
                    risk_factor=risk_factor,
                    gross_long=gross_long,
                    gross_short=gross_short,
                    net_amount=sum(item.amount for item in items),
                    delta_equivalent=sum(item.amount * item.delta for item in items),
                )
            )
        return result


@dataclass(frozen=True, slots=True)
class SensitivityResult:
    risk_factor: str
    base_value: float
    shock: float
    pnl_impact: float
    shocked_value: float


class SensitivityEngine:
    def evaluate(
        self,
        exposures: list[NetExposure],
        shocks: dict[str, float],
    ) -> list[SensitivityResult]:
        results: list[SensitivityResult] = []
        for exposure in exposures:
            shock = shocks.get(exposure.risk_factor, 0.0)
            pnl = exposure.delta_equivalent * shock
            results.append(
                SensitivityResult(
                    risk_factor=exposure.risk_factor,
                    base_value=exposure.net_amount,
                    shock=shock,
                    pnl_impact=pnl,
                    shocked_value=exposure.net_amount + pnl,
                )
            )
        return results


@dataclass(frozen=True, slots=True)
class VarEsResult:
    confidence: float
    value_at_risk: float
    expected_shortfall: float
    method: str
    sample_size: int


class MarketRiskMetrics:
    @staticmethod
    def _validate_losses(losses: FloatArray, confidence: float) -> FloatArray:
        values = np.asarray(losses, dtype=float)
        if values.ndim != 1 or values.size < 30:
            raise ValueError("at least 30 one-dimensional observations are required")
        if not 0.5 < confidence < 1.0:
            raise ValueError("confidence must be between 0.5 and 1.0")
        if not np.all(np.isfinite(values)):
            raise ValueError("losses must be finite")
        return values

    def historical(self, losses: FloatArray, confidence: float = 0.99) -> VarEsResult:
        values = self._validate_losses(losses, confidence)
        var = float(np.quantile(values, confidence, method="linear"))
        tail = values[values >= var]
        es = float(np.mean(tail)) if tail.size else var
        return VarEsResult(confidence, var, es, "historical", int(values.size))

    def student_t(self, losses: FloatArray, confidence: float = 0.99) -> VarEsResult:
        values = self._validate_losses(losses, confidence)
        df, loc, scale = t.fit(values)
        if df <= 2.0 or scale <= 0.0:
            raise ValueError("invalid Student-t fit")
        q = float(t.ppf(confidence, df=df, loc=loc, scale=scale))
        z = float(t.ppf(confidence, df=df))
        density = float(t.pdf(z, df=df))
        es = loc + scale * ((df + z * z) / (df - 1.0)) * density / (1.0 - confidence)
        return VarEsResult(confidence, q, float(es), "student_t", int(values.size))


@dataclass(frozen=True, slots=True)
class GarchFit:
    omega: float
    alpha: float
    beta: float
    degrees_of_freedom: float
    conditional_variance: tuple[float, ...]
    log_likelihood: float
    bic: float
    baseline_bic: float
    enabled: bool
    reason: str


class GarchTModel:
    def fit(self, returns: FloatArray, *, bic_improvement: float = 2.0) -> GarchFit:
        values = np.asarray(returns, dtype=float)
        if values.ndim != 1 or values.size < 100:
            raise ValueError("GARCH requires at least 100 observations")
        centered = values - np.mean(values)
        variance = float(np.var(centered, ddof=1))
        if variance <= 0.0:
            raise ValueError("returns must have positive variance")

        def conditional_variance(params: FloatArray) -> FloatArray:
            omega, alpha, beta, _ = params
            h = np.empty(values.size, dtype=float)
            h[0] = variance
            for index in range(1, values.size):
                h[index] = omega + alpha * centered[index - 1] ** 2 + beta * h[index - 1]
            return np.maximum(h, 1e-12)

        def neg_log_likelihood(params: FloatArray) -> float:
            omega, alpha, beta, df = params
            if omega <= 0.0 or alpha < 0.0 or beta < 0.0 or alpha + beta >= 0.999 or df <= 2.05:
                return 1e30
            h = conditional_variance(params)
            standardized = centered / np.sqrt(h)
            scale = sqrt((df - 2.0) / df)
            ll = t.logpdf(standardized / scale, df=df) - np.log(scale) - 0.5 * np.log(h)
            if not np.all(np.isfinite(ll)):
                return 1e30
            return float(-np.sum(ll))

        initial = np.array([variance * 0.05, 0.08, 0.90, 8.0], dtype=float)
        bounds = [
            (variance * 1e-8, variance * 10.0),
            (1e-6, 0.6),
            (1e-6, 0.999),
            (2.05, 50.0),
        ]
        result = minimize(neg_log_likelihood, initial, method="L-BFGS-B", bounds=bounds)
        if not result.success:
            raise ValueError(f"GARCH optimization failed: {result.message}")
        params = np.asarray(result.x, dtype=float)
        if params[1] + params[2] >= 0.999:
            raise ValueError("non-stationary GARCH fit")
        h = conditional_variance(params)
        ll = float(-result.fun)
        bic = 4.0 * log(values.size) - 2.0 * ll
        baseline_ll = float(np.sum(t.logpdf(centered, df=8.0, loc=0.0, scale=sqrt(variance))))
        baseline_bic = 2.0 * log(values.size) - 2.0 * baseline_ll
        enabled = bic + bic_improvement < baseline_bic
        reason = "BIC improves over static-volatility baseline" if enabled else "no sufficient BIC improvement"
        return GarchFit(
            omega=float(params[0]),
            alpha=float(params[1]),
            beta=float(params[2]),
            degrees_of_freedom=float(params[3]),
            conditional_variance=tuple(float(item) for item in h),
            log_likelihood=ll,
            bic=float(bic),
            baseline_bic=float(baseline_bic),
            enabled=enabled,
            reason=reason,
        )

    def forecast_variance(self, fit: GarchFit, last_return: float) -> float:
        last_variance = fit.conditional_variance[-1]
        return fit.omega + fit.alpha * last_return**2 + fit.beta * last_variance


@dataclass(frozen=True, slots=True)
class HmmFit:
    transition_matrix: tuple[tuple[float, float], tuple[float, float]]
    state_variances: tuple[float, float]
    filtered_probabilities: tuple[tuple[float, float], ...]
    log_likelihood: float
    bic: float
    baseline_bic: float
    enabled: bool
    reason: str


class GaussianHmmRegimeModel:
    def fit(
        self,
        returns: FloatArray,
        *,
        max_iter: int = 75,
        bic_improvement: float = 2.0,
    ) -> HmmFit:
        values = np.asarray(returns, dtype=float)
        if values.ndim != 1 or values.size < 120:
            raise ValueError("HMM requires at least 120 observations")
        centered = values - np.mean(values)
        base_variance = float(np.var(centered, ddof=1))
        if base_variance <= 0.0:
            raise ValueError("returns must have positive variance")
        variances = np.array([base_variance * 0.5, base_variance * 2.0], dtype=float)
        transition = np.array([[0.95, 0.05], [0.10, 0.90]], dtype=float)
        initial = np.array([0.8, 0.2], dtype=float)

        def emission(var: FloatArray) -> FloatArray:
            result = np.empty((values.size, 2), dtype=float)
            for state in range(2):
                result[:, state] = np.exp(-0.5 * centered**2 / var[state]) / sqrt(2.0 * np.pi * var[state])
            return np.maximum(result, 1e-300)

        previous_ll = -np.inf
        gamma = np.empty((values.size, 2), dtype=float)
        for _ in range(max_iter):
            emissions = emission(variances)
            alpha = np.empty_like(gamma)
            scales = np.empty(values.size, dtype=float)
            alpha[0] = initial * emissions[0]
            scales[0] = float(np.sum(alpha[0]))
            alpha[0] /= scales[0]
            for index in range(1, values.size):
                alpha[index] = (alpha[index - 1] @ transition) * emissions[index]
                scales[index] = float(np.sum(alpha[index]))
                alpha[index] /= scales[index]
            beta = np.ones_like(gamma)
            for index in range(values.size - 2, -1, -1):
                beta[index] = transition @ (emissions[index + 1] * beta[index + 1])
                beta[index] /= scales[index + 1]
            gamma = alpha * beta
            gamma /= np.sum(gamma, axis=1, keepdims=True)
            xi_sum = np.zeros((2, 2), dtype=float)
            for index in range(values.size - 1):
                xi = (
                    alpha[index][:, None]
                    * transition
                    * (emissions[index + 1] * beta[index + 1])[None, :]
                )
                denominator = float(np.sum(xi))
                if denominator > 0.0:
                    xi_sum += xi / denominator
            transition = xi_sum / np.maximum(np.sum(xi_sum, axis=1, keepdims=True), 1e-12)
            initial = gamma[0]
            for state in range(2):
                weight = float(np.sum(gamma[:, state]))
                variances[state] = float(np.sum(gamma[:, state] * centered**2) / max(weight, 1e-12))
            variances = np.maximum(variances, base_variance * 1e-4)
            ll = float(np.sum(np.log(scales)))
            if abs(ll - previous_ll) < 1e-7:
                break
            previous_ll = ll

        order = np.argsort(variances)
        variances = variances[order]
        transition = transition[np.ix_(order, order)]
        gamma = gamma[:, order]
        ll = previous_ll
        bic = 5.0 * log(values.size) - 2.0 * ll
        baseline_ll = float(
            np.sum(-0.5 * (np.log(2.0 * np.pi * base_variance) + centered**2 / base_variance))
        )
        baseline_bic = 1.0 * log(values.size) - 2.0 * baseline_ll
        variance_ratio = float(variances[1] / variances[0])
        persistence = float(min(transition[0, 0], transition[1, 1]))
        enabled = (
            bic + bic_improvement < baseline_bic
            and variance_ratio >= 1.5
            and persistence >= 0.60
        )
        reason = (
            "BIC, state separation and persistence gates passed"
            if enabled
            else "regime overlay did not pass all activation gates"
        )
        probabilities = tuple((float(row[0]), float(row[1])) for row in gamma)
        return HmmFit(
            transition_matrix=(
                (float(transition[0, 0]), float(transition[0, 1])),
                (float(transition[1, 0]), float(transition[1, 1])),
            ),
            state_variances=(float(variances[0]), float(variances[1])),
            filtered_probabilities=probabilities,
            log_likelihood=ll,
            bic=float(bic),
            baseline_bic=float(baseline_bic),
            enabled=enabled,
            reason=reason,
        )


@dataclass(frozen=True, slots=True)
class EvtTailFit:
    threshold_quantile: float
    threshold: float
    shape: float
    scale: float
    exceedances: int
    enabled: bool
    reason: str


class EvtTailOverlay:
    def fit(
        self,
        losses: FloatArray,
        *,
        threshold_quantile: float = 0.95,
        min_exceedances: int = 30,
    ) -> EvtTailFit:
        values = np.asarray(losses, dtype=float)
        if values.ndim != 1 or values.size < 200:
            raise ValueError("EVT requires at least 200 observations")
        if not 0.90 <= threshold_quantile < 0.995:
            raise ValueError("threshold_quantile must be between 0.90 and 0.995")
        threshold = float(np.quantile(values, threshold_quantile))
        excess = values[values > threshold] - threshold
        if excess.size < min_exceedances:
            return EvtTailFit(
                threshold_quantile,
                threshold,
                0.0,
                0.0,
                int(excess.size),
                False,
                "insufficient exceedances",
            )
        shape, _, scale = genpareto.fit(excess, floc=0.0)
        enabled = bool(np.isfinite(shape) and np.isfinite(scale) and scale > 0.0 and shape < 1.0)
        reason = "POT-GPD diagnostics passed" if enabled else "unstable GPD fit"
        return EvtTailFit(
            threshold_quantile=threshold_quantile,
            threshold=threshold,
            shape=float(shape),
            scale=float(scale),
            exceedances=int(excess.size),
            enabled=enabled,
            reason=reason,
        )

    def quantile(self, fit: EvtTailFit, probability: float, sample_size: int) -> float:
        if not fit.enabled:
            raise ValueError("EVT overlay is not enabled")
        if not fit.threshold_quantile < probability < 1.0:
            raise ValueError("probability must be above the EVT threshold quantile")
        tail_probability = fit.exceedances / sample_size
        scaled = (1.0 - probability) / tail_probability
        if fit.shape == 0.0:
            excess = -fit.scale * log(scaled)
        else:
            excess = fit.scale / fit.shape * (scaled ** (-fit.shape) - 1.0)
        return fit.threshold + excess


@dataclass(frozen=True, slots=True)
class CopulaFit:
    family: str
    degrees_of_freedom: float | None
    correlation: tuple[tuple[float, ...], ...]
    log_likelihood: float
    aic: float
    enabled: bool
    reason: str
    minimum_tail_dependence: float


class CopulaDependenceModel:
    @staticmethod
    def _pseudo_uniform(data: FloatArray) -> FloatArray:
        rows, columns = data.shape
        uniforms = np.empty_like(data, dtype=float)
        for column in range(columns):
            uniforms[:, column] = rankdata(data[:, column], method="average") / (rows + 1.0)
        return np.clip(uniforms, 1e-8, 1.0 - 1e-8)

    @staticmethod
    def _nearest_psd(correlation: FloatArray) -> FloatArray:
        symmetric = (correlation + correlation.T) / 2.0
        values, vectors = np.linalg.eigh(symmetric)
        values = np.maximum(values, 1e-8)
        rebuilt = vectors @ np.diag(values) @ vectors.T
        diagonal = np.sqrt(np.diag(rebuilt))
        return rebuilt / np.outer(diagonal, diagonal)

    def fit(self, returns: FloatArray, *, aic_improvement: float = 2.0) -> CopulaFit:
        data = np.asarray(returns, dtype=float)
        if data.ndim != 2 or data.shape[0] < 200 or data.shape[1] < 2:
            raise ValueError("copula fit requires at least 200 rows and two risk factors")
        uniforms = self._pseudo_uniform(data)
        gaussian_scores = np.vectorize(NormalDist().inv_cdf)(uniforms)
        gaussian_corr = self._nearest_psd(np.corrcoef(gaussian_scores, rowvar=False))
        gaussian_ll = self._gaussian_copula_loglik(gaussian_scores, gaussian_corr)
        gaussian_aic = 2.0 * (data.shape[1] * (data.shape[1] - 1) / 2.0) - 2.0 * gaussian_ll

        def objective(df: float) -> float:
            scores = t.ppf(uniforms, df=df)
            corr = self._nearest_psd(np.corrcoef(scores, rowvar=False))
            joint = multivariate_t.logpdf(scores, shape=corr, df=df)
            marginal = np.sum(t.logpdf(scores, df=df), axis=1)
            return float(-np.sum(joint - marginal))

        result = minimize_scalar(objective, bounds=(2.1, 40.0), method="bounded")
        df = float(result.x)
        t_scores = t.ppf(uniforms, df=df)
        t_corr = self._nearest_psd(np.corrcoef(t_scores, rowvar=False))
        t_ll = float(-result.fun)
        t_parameters = data.shape[1] * (data.shape[1] - 1) / 2.0 + 1.0
        t_aic = 2.0 * t_parameters - 2.0 * t_ll
        tail_dependences: list[float] = []
        for row in range(data.shape[1]):
            for column in range(row + 1, data.shape[1]):
                rho = float(t_corr[row, column])
                argument = -sqrt((df + 1.0) * (1.0 - rho) / max(1.0 + rho, 1e-12))
                tail_dependences.append(float(2.0 * t.cdf(argument, df=df + 1.0)))
        minimum_tail = min(tail_dependences) if tail_dependences else 0.0
        use_t = t_aic + aic_improvement < gaussian_aic and max(tail_dependences, default=0.0) > 0.01
        if use_t:
            return CopulaFit(
                family="student_t",
                degrees_of_freedom=df,
                correlation=tuple(tuple(float(item) for item in row) for row in t_corr),
                log_likelihood=t_ll,
                aic=float(t_aic),
                enabled=True,
                reason="Student-t copula materially improves AIC and captures tail dependence",
                minimum_tail_dependence=float(minimum_tail),
            )
        return CopulaFit(
            family="gaussian",
            degrees_of_freedom=None,
            correlation=tuple(tuple(float(item) for item in row) for row in gaussian_corr),
            log_likelihood=float(gaussian_ll),
            aic=float(gaussian_aic),
            enabled=False,
            reason="tail-dependent copula did not demonstrate sufficient improvement",
            minimum_tail_dependence=0.0,
        )

    @staticmethod
    def _gaussian_copula_loglik(scores: FloatArray, correlation: FloatArray) -> float:
        inverse = np.linalg.inv(correlation)
        sign, log_det = np.linalg.slogdet(correlation)
        if sign <= 0.0:
            raise ValueError("correlation matrix must be positive definite")
        identity = np.eye(correlation.shape[0])
        quadratic = np.einsum("ij,jk,ik->i", scores, inverse - identity, scores)
        return float(np.sum(-0.5 * log_det - 0.5 * quadratic))


@dataclass(frozen=True, slots=True)
class HedgeEffectivenessResult:
    hedge_ratio: float
    unhedged_variance: float
    hedged_variance: float
    variance_reduction: float
    correlation: float


class HedgeScenarioEngine:
    def evaluate(
        self,
        exposure_returns: FloatArray,
        hedge_returns: FloatArray,
        *,
        hedge_ratio: float,
    ) -> HedgeEffectivenessResult:
        exposure = np.asarray(exposure_returns, dtype=float)
        hedge = np.asarray(hedge_returns, dtype=float)
        if exposure.shape != hedge.shape or exposure.ndim != 1 or exposure.size < 30:
            raise ValueError("hedge series must be aligned one-dimensional arrays")
        unhedged_variance = float(np.var(exposure, ddof=1))
        hedged = exposure - hedge_ratio * hedge
        hedged_variance = float(np.var(hedged, ddof=1))
        reduction = 1.0 - hedged_variance / unhedged_variance if unhedged_variance > 0.0 else 0.0
        correlation = float(np.corrcoef(exposure, hedge)[0, 1])
        return HedgeEffectivenessResult(
            hedge_ratio=hedge_ratio,
            unhedged_variance=unhedged_variance,
            hedged_variance=hedged_variance,
            variance_reduction=float(reduction),
            correlation=correlation,
        )

    def optimal_ratio(self, exposure_returns: FloatArray, hedge_returns: FloatArray) -> float:
        exposure = np.asarray(exposure_returns, dtype=float)
        hedge = np.asarray(hedge_returns, dtype=float)
        covariance = float(np.cov(exposure, hedge, ddof=1)[0, 1])
        hedge_variance = float(np.var(hedge, ddof=1))
        if hedge_variance <= 0.0:
            raise ValueError("hedge variance must be positive")
        return covariance / hedge_variance


@dataclass(frozen=True, slots=True)
class VarBacktestResult:
    observations: int
    exceptions: int
    expected_exception_rate: float
    kupiec_lr: float
    kupiec_p_value: float
    christoffersen_lr: float
    christoffersen_p_value: float
    passed_unconditional_coverage: bool
    passed_independence: bool


class VarBacktester:
    def evaluate(
        self,
        realized_losses: FloatArray,
        var_forecasts: FloatArray,
        *,
        confidence: float,
        significance: float = 0.05,
    ) -> VarBacktestResult:
        losses = np.asarray(realized_losses, dtype=float)
        forecasts = np.asarray(var_forecasts, dtype=float)
        if losses.shape != forecasts.shape or losses.ndim != 1 or losses.size < 50:
            raise ValueError("aligned loss and VaR arrays with at least 50 observations are required")
        if not 0.5 < confidence < 1.0:
            raise ValueError("confidence must be between 0.5 and 1.0")
        exceptions = losses > forecasts
        n = exceptions.size
        x = int(np.sum(exceptions))
        expected_rate = 1.0 - confidence
        observed_rate = x / n
        eps = 1e-12
        null_ll = (n - x) * log(max(1.0 - expected_rate, eps)) + x * log(max(expected_rate, eps))
        alt_ll = (n - x) * log(max(1.0 - observed_rate, eps)) + x * log(max(observed_rate, eps))
        kupiec_lr = max(0.0, -2.0 * (null_ll - alt_ll))
        kupiec_p = float(chi2.sf(kupiec_lr, df=1))

        n00 = n01 = n10 = n11 = 0
        for previous, current in zip(exceptions[:-1], exceptions[1:], strict=True):
            if not previous and not current:
                n00 += 1
            elif not previous and current:
                n01 += 1
            elif previous and not current:
                n10 += 1
            else:
                n11 += 1
        pi0 = n01 / max(n00 + n01, 1)
        pi1 = n11 / max(n10 + n11, 1)
        pi = (n01 + n11) / max(n00 + n01 + n10 + n11, 1)
        independent_ll = (
            n00 * log(max(1.0 - pi, eps))
            + n01 * log(max(pi, eps))
            + n10 * log(max(1.0 - pi, eps))
            + n11 * log(max(pi, eps))
        )
        markov_ll = (
            n00 * log(max(1.0 - pi0, eps))
            + n01 * log(max(pi0, eps))
            + n10 * log(max(1.0 - pi1, eps))
            + n11 * log(max(pi1, eps))
        )
        christoffersen_lr = max(0.0, -2.0 * (independent_ll - markov_ll))
        christoffersen_p = float(chi2.sf(christoffersen_lr, df=1))
        return VarBacktestResult(
            observations=n,
            exceptions=x,
            expected_exception_rate=expected_rate,
            kupiec_lr=kupiec_lr,
            kupiec_p_value=kupiec_p,
            christoffersen_lr=christoffersen_lr,
            christoffersen_p_value=christoffersen_p,
            passed_unconditional_coverage=kupiec_p >= significance,
            passed_independence=christoffersen_p >= significance,
        )
