from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class GermanTaxPolicy:
    enabled: bool = False
    partial_exemption: float = 0.30
    saver_allowance: float = 1000.0
    capital_gains_tax_rate: float = 0.25
    solidarity_surcharge_rate: float = 0.055
    church_tax_rate: float = 0.0

    def validate(self) -> None:
        for name, value in (
            ("partial_exemption", self.partial_exemption),
            ("capital_gains_tax_rate", self.capital_gains_tax_rate),
            ("solidarity_surcharge_rate", self.solidarity_surcharge_rate),
            ("church_tax_rate", self.church_tax_rate),
        ):
            if not 0.0 <= value < 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if self.saver_allowance < 0.0:
            raise ValueError("saver_allowance must be non-negative")


def apply_terminal_tax(
    terminal_values: np.ndarray,
    paid_in_capital: float,
    policy: GermanTaxPolicy,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(terminal_values, dtype=float)
    if not policy.enabled:
        return values.copy(), np.zeros_like(values)
    policy.validate()

    gross_gain = np.maximum(values - paid_in_capital, 0.0)
    taxable_after_exemption = gross_gain * (1.0 - policy.partial_exemption)
    taxable_gain = np.maximum(taxable_after_exemption - policy.saver_allowance, 0.0)
    capital_tax = taxable_gain * policy.capital_gains_tax_rate
    solidarity = capital_tax * policy.solidarity_surcharge_rate
    church_tax = capital_tax * policy.church_tax_rate
    total_tax = capital_tax + solidarity + church_tax
    return values - total_tax, total_tax
