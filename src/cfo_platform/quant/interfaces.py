from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class QuantModelInput:
    values: Mapping[str, object]
    parameters: Mapping[str, object]
    random_seed: int | None = None


@dataclass(frozen=True, slots=True)
class QuantModelOutput:
    values: Mapping[str, object]


class QuantModel(Protocol):
    @property
    def model_id(self) -> str: ...

    @property
    def model_version(self) -> str: ...

    def execute(self, model_input: QuantModelInput) -> QuantModelOutput: ...
