from __future__ import annotations

from collections.abc import Iterable

from .interfaces import QuantModel


class QuantModelRegistry:
    def __init__(self, models: Iterable[QuantModel] = ()) -> None:
        self._models: dict[tuple[str, str], QuantModel] = {}
        for model in models:
            self.register(model)

    def register(self, model: QuantModel) -> None:
        key = (model.model_id, model.model_version)
        if key in self._models:
            raise ValueError(f"Model already registered: {model.model_id}@{model.model_version}")
        self._models[key] = model

    def get(self, model_id: str, model_version: str) -> QuantModel:
        try:
            return self._models[(model_id, model_version)]
        except KeyError as exc:
            raise KeyError(f"Unknown model: {model_id}@{model_version}") from exc

    def list_models(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self._models))
