"""Framework-independent quantitative model contracts and adapters."""

from app.shared.quant.interfaces import QuantModel, QuantModelInput, QuantModelOutput
from app.shared.quant.registry import QuantModelRegistry

__all__ = ["QuantModel", "QuantModelInput", "QuantModelOutput", "QuantModelRegistry"]
