from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from re import fullmatch


@dataclass(frozen=True, slots=True)
class CurrencyCode:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.upper()
        if fullmatch(r"[A-Z]{3}", normalized) is None:
            raise ValueError("CurrencyCode must be a three-letter ISO-style code")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Money:
    amount: Decimal
    currency: CurrencyCode

    def __post_init__(self) -> None:
        if not self.amount.is_finite():
            raise ValueError("Money amount must be finite")

    def __add__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other: Money) -> Money:
        self._assert_same_currency(other)
        return Money(self.amount - other.amount, self.currency)

    def _assert_same_currency(self, other: Money) -> None:
        if self.currency != other.currency:
            raise ValueError("Money operations require matching currencies")


@dataclass(frozen=True, order=True, slots=True)
class FiscalPeriod:
    year: int
    month: int

    def __post_init__(self) -> None:
        if self.year < 1900 or self.year > 9999:
            raise ValueError("Fiscal period year is outside the supported range")
        if self.month < 1 or self.month > 12:
            raise ValueError("Fiscal period month must be between 1 and 12")

    @classmethod
    def parse(cls, value: str) -> FiscalPeriod:
        if fullmatch(r"\d{4}-\d{2}", value) is None:
            raise ValueError("Fiscal period must use YYYY-MM format")
        year, month = value.split("-")
        return cls(int(year), int(month))

    def __str__(self) -> str:
        return f"{self.year:04d}-{self.month:02d}"


@dataclass(frozen=True, slots=True)
class VersionId:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise ValueError("VersionId must not be empty")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
