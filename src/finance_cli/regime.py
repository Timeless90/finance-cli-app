from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.special import logsumexp

from .models import InitialRegime, RegimeConfig, RegimeInnovation

_EPS = 1e-12


@dataclass(frozen=True)
class RegimeCalibrationResult:
    innovation: str
    means: np.ndarray
    standard_deviations: np.ndarray
    transition_matrix: np.ndarray
    initial_probabilities: np.ndarray
    filtered_probabilities: np.ndarray
    smoothed_probabilities: np.ndarray
    log_likelihood: float
    aic: float
    bic: float
    converged: bool
    iterations: int
    student_t_df: float | None
    occupancy: np.ndarray
    expected_durations_months: np.ndarray

    def to_json_dict(self) -> dict[str, object]:
        raw = asdict(self)
        return {
            key: value.tolist() if isinstance(value, np.ndarray) else value
            for key, value in raw.items()
        }


def _validate_returns(values: np.ndarray, minimum_observations: int) -> np.ndarray:
    data = np.asarray(values, dtype=float)
    if data.ndim != 1:
        raise ValueError("Regime calibration requires a one-dimensional return series")
    if data.size < minimum_observations:
        raise ValueError(
            f"Regime calibration requires at least {minimum_observations} observations; "
            f"received {data.size}"
        )
    if not np.all(np.isfinite(data)):
        raise ValueError("Return series contains non-finite values")
    if float(np.std(data, ddof=1)) <= 0.0:
        raise ValueError("Return series must have positive variance")
    return data


def _stationary_distribution(transition: np.ndarray) -> np.ndarray:
    eigenvalues, eigenvectors = np.linalg.eig(transition.T)
    index = int(np.argmin(np.abs(eigenvalues - 1.0)))
    vector = np.real(eigenvectors[:, index])
    vector = np.maximum(vector, 0.0)
    if float(vector.sum()) <= 0.0:
        vector = np.ones(transition.shape[0], dtype=float)
    return vector / vector.sum()


def _log_emissions(
    values: np.ndarray,
    means: np.ndarray,
    stds: np.ndarray,
    innovation: RegimeInnovation,
    student_t_df: float | None,
) -> np.ndarray:
    if innovation == RegimeInnovation.GAUSSIAN:
        return np.column_stack(
            [stats.norm.logpdf(values, loc=means[k], scale=stds[k]) for k in range(2)]
        )
    df = float(student_t_df or 8.0)
    scales = stds * np.sqrt((df - 2.0) / df)
    return np.column_stack(
        [stats.t.logpdf(values, df=df, loc=means[k], scale=scales[k]) for k in range(2)]
    )


def _forward_backward(
    log_emissions: np.ndarray,
    transition: np.ndarray,
    initial: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    n_obs, n_states = log_emissions.shape
    log_transition = np.log(np.clip(transition, _EPS, 1.0))
    log_initial = np.log(np.clip(initial, _EPS, 1.0))

    alpha = np.empty((n_obs, n_states), dtype=float)
    alpha[0] = log_initial + log_emissions[0]
    for t in range(1, n_obs):
        alpha[t] = log_emissions[t] + logsumexp(
            alpha[t - 1][:, None] + log_transition, axis=0
        )
    log_likelihood = float(logsumexp(alpha[-1]))

    beta = np.zeros((n_obs, n_states), dtype=float)
    for t in range(n_obs - 2, -1, -1):
        beta[t] = logsumexp(
            log_transition + log_emissions[t + 1][None, :] + beta[t + 1][None, :],
            axis=1,
        )

    log_gamma = alpha + beta - log_likelihood
    gamma = np.exp(log_gamma)
    gamma /= np.clip(gamma.sum(axis=1, keepdims=True), _EPS, None)

    xi = np.empty((n_obs - 1, n_states, n_states), dtype=float)
    for t in range(n_obs - 1):
        log_xi = (
            alpha[t][:, None]
            + log_transition
            + log_emissions[t + 1][None, :]
            + beta[t + 1][None, :]
            - log_likelihood
        )
        xi[t] = np.exp(log_xi - logsumexp(log_xi))

    filtered = np.exp(alpha - logsumexp(alpha, axis=1, keepdims=True))
    return filtered, gamma, xi, log_likelihood


def _initial_parameters(values: np.ndarray, rng: np.random.Generator) -> tuple[np.ndarray, ...]:
    quantiles = np.quantile(values, [0.30, 0.70])
    jitter = rng.normal(0.0, max(float(np.std(values)) * 0.10, 1e-6), size=2)
    means = quantiles + jitter
    total_std = max(float(np.std(values, ddof=1)), 1e-6)
    stds = np.array([0.65 * total_std, 1.45 * total_std])
    stds *= rng.uniform(0.85, 1.15, size=2)
    persistence = rng.uniform(0.80, 0.98, size=2)
    transition = np.array(
        [[persistence[0], 1.0 - persistence[0]], [1.0 - persistence[1], persistence[1]]]
    )
    initial = _stationary_distribution(transition)
    return means, stds, transition, initial


def _fit_single_start(
    values: np.ndarray,
    cfg: RegimeConfig,
    rng: np.random.Generator,
    student_t_df: float | None,
) -> RegimeCalibrationResult:
    means, stds, transition, initial = _initial_parameters(values, rng)
    previous = -np.inf
    converged = False
    filtered = np.empty((values.size, 2))
    gamma = np.empty((values.size, 2))
    log_likelihood = -np.inf

    for iteration in range(1, cfg.max_iterations + 1):
        emissions = _log_emissions(values, means, stds, cfg.innovation, student_t_df)
        filtered, gamma, xi, log_likelihood = _forward_backward(
            emissions, transition, initial
        )

        weights = np.clip(gamma.sum(axis=0), _EPS, None)
        means = (gamma * values[:, None]).sum(axis=0) / weights
        variances = (
            gamma * np.square(values[:, None] - means[None, :])
        ).sum(axis=0) / weights
        stds = np.sqrt(np.maximum(variances, 1e-10))

        transition = xi.sum(axis=0)
        transition /= np.clip(transition.sum(axis=1, keepdims=True), _EPS, None)
        transition = np.clip(transition, 1e-6, 1.0 - 1e-6)
        transition /= transition.sum(axis=1, keepdims=True)
        initial = np.clip(gamma[0], _EPS, None)
        initial /= initial.sum()

        if np.isfinite(previous) and abs(log_likelihood - previous) <= cfg.tolerance * (
            1.0 + abs(previous)
        ):
            converged = True
            break
        previous = log_likelihood

    n_parameters = 2 + 2 + 2 + 1
    if cfg.innovation == RegimeInnovation.STUDENT_T:
        n_parameters += 1
    n_obs = values.size
    aic = 2.0 * n_parameters - 2.0 * log_likelihood
    bic = np.log(n_obs) * n_parameters - 2.0 * log_likelihood
    occupancy = gamma.mean(axis=0)
    durations = 1.0 / np.clip(1.0 - np.diag(transition), _EPS, None)
    return RegimeCalibrationResult(
        innovation=cfg.innovation.value,
        means=means,
        standard_deviations=stds,
        transition_matrix=transition,
        initial_probabilities=initial,
        filtered_probabilities=filtered,
        smoothed_probabilities=gamma,
        log_likelihood=log_likelihood,
        aic=float(aic),
        bic=float(bic),
        converged=converged,
        iterations=iteration,
        student_t_df=student_t_df,
        occupancy=occupancy,
        expected_durations_months=durations,
    )


def _relabel_by_volatility(result: RegimeCalibrationResult) -> RegimeCalibrationResult:
    order = np.argsort(result.standard_deviations)
    transition = result.transition_matrix[np.ix_(order, order)]
    return RegimeCalibrationResult(
        innovation=result.innovation,
        means=result.means[order],
        standard_deviations=result.standard_deviations[order],
        transition_matrix=transition,
        initial_probabilities=result.initial_probabilities[order],
        filtered_probabilities=result.filtered_probabilities[:, order],
        smoothed_probabilities=result.smoothed_probabilities[:, order],
        log_likelihood=result.log_likelihood,
        aic=result.aic,
        bic=result.bic,
        converged=result.converged,
        iterations=result.iterations,
        student_t_df=result.student_t_df,
        occupancy=result.occupancy[order],
        expected_durations_months=result.expected_durations_months[order],
    )


def calibrate_regime_model(
    log_returns: np.ndarray,
    cfg: RegimeConfig,
    *,
    seed: int,
) -> RegimeCalibrationResult:
    values = _validate_returns(log_returns, cfg.minimum_observations)
    student_t_df = cfg.student_t_degrees_of_freedom
    if cfg.innovation == RegimeInnovation.STUDENT_T and student_t_df is None:
        fitted_df, _, _ = stats.t.fit((values - values.mean()) / values.std(ddof=1), floc=0)
        student_t_df = float(np.clip(fitted_df, 2.1, 100.0))

    seeds = np.random.SeedSequence(seed).spawn(cfg.random_starts)
    candidates = [
        _fit_single_start(values, cfg, np.random.default_rng(child), student_t_df)
        for child in seeds
    ]
    finite = [candidate for candidate in candidates if np.isfinite(candidate.log_likelihood)]
    if not finite:
        raise RuntimeError("All regime-model calibration attempts failed")
    best = max(finite, key=lambda candidate: candidate.log_likelihood)
    return _relabel_by_volatility(best)


def _apply_transition_stress(
    transition: np.ndarray,
    cfg: RegimeConfig,
) -> np.ndarray:
    stressed = transition.copy()
    if cfg.normal_to_crisis_multiplier != 1.0:
        crisis_probability = min(
            stressed[0, 1] * cfg.normal_to_crisis_multiplier, 1.0 - 1e-6
        )
        stressed[0] = [1.0 - crisis_probability, crisis_probability]
    if cfg.crisis_persistence_override is not None:
        persistence = cfg.crisis_persistence_override
        stressed[1] = [1.0 - persistence, persistence]
    return stressed


def _simulation_initial_probabilities(
    result: RegimeCalibrationResult,
    cfg: RegimeConfig,
    transition: np.ndarray,
) -> np.ndarray:
    if cfg.crisis_start_probability is not None:
        return np.array([1.0 - cfg.crisis_start_probability, cfg.crisis_start_probability])
    if cfg.initial_regime == InitialRegime.NORMAL:
        return np.array([1.0, 0.0])
    if cfg.initial_regime == InitialRegime.CRISIS:
        return np.array([0.0, 1.0])
    if cfg.initial_regime == InitialRegime.STATIONARY:
        return _stationary_distribution(transition)
    probabilities = result.filtered_probabilities[-1].copy()
    return probabilities / probabilities.sum()


def simulate_regime_log_returns(
    result: RegimeCalibrationResult,
    cfg: RegimeConfig,
    *,
    n_paths: int,
    n_months: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    transition = _apply_transition_stress(result.transition_matrix, cfg)
    initial = _simulation_initial_probabilities(result, cfg, transition)
    stream_count = min(cfg.parallel_streams, n_paths)
    child_seeds = np.random.SeedSequence(seed).spawn(stream_count)
    chunk_sizes = np.full(stream_count, n_paths // stream_count, dtype=int)
    chunk_sizes[: n_paths % stream_count] += 1

    return_chunks: list[np.ndarray] = []
    state_chunks: list[np.ndarray] = []
    for child_seed, chunk_size in zip(child_seeds, chunk_sizes, strict=True):
        rng = np.random.default_rng(child_seed)
        states = np.empty((chunk_size, n_months), dtype=np.int8)
        states[:, 0] = rng.choice(2, size=chunk_size, p=initial)
        for month in range(1, n_months):
            probabilities = transition[states[:, month - 1]]
            uniforms = rng.random(chunk_size)
            states[:, month] = (uniforms >= probabilities[:, 0]).astype(np.int8)

        if result.innovation == RegimeInnovation.STUDENT_T.value:
            df = float(result.student_t_df or 8.0)
            shocks = rng.standard_t(df, size=(chunk_size, n_months))
            shocks *= np.sqrt((df - 2.0) / df)
        else:
            shocks = rng.standard_normal((chunk_size, n_months))
        simulated = result.means[states] + result.standard_deviations[states] * shocks
        return_chunks.append(simulated)
        state_chunks.append(states)

    return np.vstack(return_chunks), np.vstack(state_chunks)


def export_regime_results(
    output_dir: Path,
    result: RegimeCalibrationResult,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    labels = ["normal", "crisis"]
    parameters = pd.DataFrame(
        {
            "regime": [0, 1],
            "label": labels,
            "monthly_log_mean": result.means,
            "monthly_volatility": result.standard_deviations,
            "annualized_log_mean": result.means * 12.0,
            "annualized_volatility": result.standard_deviations * np.sqrt(12.0),
            "occupancy": result.occupancy,
            "expected_duration_months": result.expected_durations_months,
        }
    )
    parameters.to_csv(output_dir / "regime-parameters.csv", index=False)
    pd.DataFrame(
        result.transition_matrix,
        index=["from_normal", "from_crisis"],
        columns=["to_normal", "to_crisis"],
    ).to_csv(output_dir / "regime-transition-matrix.csv")
    probabilities = pd.DataFrame(
        {
            "observation": np.arange(result.smoothed_probabilities.shape[0]),
            "filtered_normal": result.filtered_probabilities[:, 0],
            "filtered_crisis": result.filtered_probabilities[:, 1],
            "smoothed_normal": result.smoothed_probabilities[:, 0],
            "smoothed_crisis": result.smoothed_probabilities[:, 1],
        }
    )
    probabilities.to_csv(output_dir / "regime-probabilities.csv", index=False)
    (output_dir / "regime-diagnostics.json").write_text(
        json.dumps(result.to_json_dict(), indent=2), encoding="utf-8"
    )
