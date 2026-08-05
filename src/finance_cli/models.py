from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, model_validator


class SimulationMethod(StrEnum):
    NORMAL = "normal"
    STUDENT_T = "student_t"
    HISTORICAL_BOOTSTRAP = "historical_bootstrap"
    BLOCK_BOOTSTRAP = "block_bootstrap"
    MARKOV_REGIME = "markov_regime"


class RegimeInnovation(StrEnum):
    GAUSSIAN = "gaussian"
    STUDENT_T = "student_t"


class InitialRegime(StrEnum):
    FILTERED = "filtered"
    STATIONARY = "stationary"
    NORMAL = "normal"
    CRISIS = "crisis"


class ContributionTiming(StrEnum):
    MONTH_START = "month_start"
    MONTH_END = "month_end"


class DataConfig(BaseModel):
    csv_path: Path | None = None
    date_column: str = "date"
    price_column: str = "price"
    returns_are_net_of_fund_fees: bool = True


class CalibrationConfig(BaseModel):
    lookback_years: int | None = Field(default=10, ge=1, le=100)
    assumed_annual_return: float = Field(default=0.06, gt=-0.99, lt=1.0)
    mean_shrinkage_months: float = Field(default=60.0, gt=0)
    volatility_shrinkage_months: float = Field(default=36.0, gt=0)


class PortfolioConfig(BaseModel):
    initial_value: float = Field(default=34932.42, ge=0)
    monthly_contribution: float = Field(default=1200.0, ge=0)
    contribution_timing: ContributionTiming = ContributionTiming.MONTH_END
    annual_inflation: float = Field(default=0.02, ge=-0.5, lt=1.0)
    annual_external_fee: float = Field(default=0.0, ge=0, lt=1.0)


class RegimeConfig(BaseModel):
    enabled: bool = False
    states: int = Field(default=2, ge=2, le=2)
    innovation: RegimeInnovation = RegimeInnovation.GAUSSIAN
    minimum_observations: int = Field(default=180, ge=120, le=1200)
    random_starts: int = Field(default=20, ge=1, le=200)
    em_iterations: int = Field(default=10, ge=0, le=100)
    max_iterations: int = Field(default=500, ge=50, le=5000)
    tolerance: float = Field(default=1e-8, gt=0, lt=1e-2)
    student_t_degrees_of_freedom: float | None = Field(default=None, gt=2.0, le=100)
    initial_regime: InitialRegime = InitialRegime.FILTERED
    crisis_start_probability: float | None = Field(default=None, ge=0.0, le=1.0)
    crisis_persistence_override: float | None = Field(default=None, ge=0.0, lt=1.0)
    normal_to_crisis_multiplier: float = Field(default=1.0, gt=0.0, le=100.0)
    parallel_streams: int = Field(default=1, ge=1, le=128)
    export_diagnostics: bool = True
    rolling_backtest_enabled: bool = False
    rolling_training_months: int = Field(default=180, ge=120, le=1200)
    gof_monte_carlo_samples: int = Field(default=0, ge=0, le=999)


class SimulationConfig(BaseModel):
    method: SimulationMethod = SimulationMethod.STUDENT_T
    years: int = Field(default=30, ge=1, le=100)
    paths: int = Field(default=10000, ge=100, le=1_000_000)
    seed: int = 20260804
    block_length_months: int = Field(default=3, ge=1, le=60)
    student_t_degrees_of_freedom: float | None = Field(default=None, gt=2.0, le=200)
    regime: RegimeConfig = RegimeConfig()


class RiskConfig(BaseModel):
    annual_risk_free_rate: float = Field(default=0.02, gt=-0.99, lt=1.0)
    annual_omega_threshold: float = Field(default=0.0, gt=-0.99, lt=1.0)
    confidence_level: float = Field(default=0.95, gt=0.5, lt=1.0)


class DiagnosticsConfig(BaseModel):
    enabled: bool = True
    rolling_training_months: int = Field(default=60, ge=24, le=600)
    interval_coverage: float = Field(default=0.90, gt=0.5, lt=1.0)
    monte_carlo_samples: int = Field(default=999, ge=99, le=100000)


class TaxConfig(BaseModel):
    enabled: bool = False
    partial_exemption: float = Field(default=0.30, ge=0.0, lt=1.0)
    saver_allowance: float = Field(default=1000.0, ge=0.0)
    capital_gains_tax_rate: float = Field(default=0.25, ge=0.0, lt=1.0)
    solidarity_surcharge_rate: float = Field(default=0.055, ge=0.0, lt=1.0)
    church_tax_rate: float = Field(default=0.0, ge=0.0, lt=1.0)


class OutputConfig(BaseModel):
    directory: Path = Path("runs/latest")
    export_charts: bool = True


class AppConfig(BaseModel):
    data: DataConfig = DataConfig()
    calibration: CalibrationConfig = CalibrationConfig()
    portfolio: PortfolioConfig = PortfolioConfig()
    simulation: SimulationConfig = SimulationConfig()
    risk: RiskConfig = RiskConfig()
    diagnostics: DiagnosticsConfig = DiagnosticsConfig()
    tax: TaxConfig = TaxConfig()
    output: OutputConfig = OutputConfig()

    @property
    def output_dir(self) -> Path:
        return self.output.directory

    @model_validator(mode="after")
    def validate_historical_input(self) -> AppConfig:
        historical_methods = {
            SimulationMethod.HISTORICAL_BOOTSTRAP,
            SimulationMethod.BLOCK_BOOTSTRAP,
            SimulationMethod.MARKOV_REGIME,
        }
        if self.simulation.method in historical_methods and self.data.csv_path is None:
            raise ValueError(f"{self.simulation.method.value} requires data.csv_path")
        if self.simulation.method == SimulationMethod.MARKOV_REGIME:
            self.simulation.regime.enabled = True
        return self
