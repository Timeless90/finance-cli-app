"""Framework-independent quantitative model contracts and adapters."""

from .interfaces import QuantModel, QuantModelInput, QuantModelOutput
from .registry import QuantModelRegistry

__all__ = ["QuantModel", "QuantModelInput", "QuantModelOutput", "QuantModelRegistry"]
