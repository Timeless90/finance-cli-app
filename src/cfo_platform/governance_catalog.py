from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Protocol
from uuid import uuid4

from cfo_platform.governance import GovernanceStatus, _hash_payload


class ScenarioKind(StrEnum):
    BASE = "base"
    UPSIDE = "upside"
    DOWNSIDE = "downside"
    STRESS = "stress"


class ModelLifecycle(StrEnum):
    DEVELOPMENT = "development"
    VALIDATED = "validated"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


@dataclass(frozen=True, slots=True)
class Assumption:
    assumption_id: str
    name: str
    value: Any
    owner: str
    unit: str | None = None
    source: str | None = None


@dataclass(frozen=True, slots=True)
class ScenarioVersion:
    scenario_id: str
    version: int
    name: str
    kind: ScenarioKind
    assumptions: tuple[Assumption, ...]
    status: GovernanceStatus
    created_by: str
    created_at: datetime
    approved_by: str | None = None
    parent_scenario_id: str | None = None
    content_hash: str = ""

    @property
    def immutable(self) -> bool:
        return self.status in {GovernanceStatus.APPROVED, GovernanceStatus.RETIRED}


@dataclass(frozen=True, slots=True)
class ModelRegistration:
    model_id: str
    version: str
    owner: str
    description: str
    limitations: tuple[str, ...]
    lifecycle: ModelLifecycle
    validation_run_ids: tuple[str, ...] = ()
    approved_by: str | None = None
    created_at: datetime = datetime.min.replace(tzinfo=timezone.utc)


class ScenarioRepository(Protocol):
    def add(self, scenario: ScenarioVersion) -> None: ...
    def get(self, scenario_id: str, version: int | None = None) -> ScenarioVersion | None: ...
    def list_all(self) -> tuple[ScenarioVersion, ...]: ...


class ModelRegistryRepository(Protocol):
    def add(self, model: ModelRegistration) -> None: ...
    def get(self, model_id: str, version: str) -> ModelRegistration | None: ...
    def replace(self, model: ModelRegistration) -> None: ...
    def list_all(self) -> tuple[ModelRegistration, ...]: ...


class InMemoryScenarioRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[str, int], ScenarioVersion] = {}

    def add(self, scenario: ScenarioVersion) -> None:
        key = (scenario.scenario_id, scenario.version)
        if key in self._items:
            raise ValueError("scenario version already exists")
        self._items[key] = scenario

    def get(self, scenario_id: str, version: int | None = None) -> ScenarioVersion | None:
        matches = [item for (sid, _), item in self._items.items() if sid == scenario_id]
        if not matches:
            return None
        if version is None:
            return max(matches, key=lambda item: item.version)
        return self._items.get((scenario_id, version))

    def list_all(self) -> tuple[ScenarioVersion, ...]:
        return tuple(sorted(self._items.values(), key=lambda item: (item.scenario_id, item.version)))


class InMemoryModelRegistryRepository:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], ModelRegistration] = {}

    def add(self, model: ModelRegistration) -> None:
        key = (model.model_id, model.version)
        if key in self._items:
            raise ValueError("model version already exists")
        self._items[key] = model

    def get(self, model_id: str, version: str) -> ModelRegistration | None:
        return self._items.get((model_id, version))

    def replace(self, model: ModelRegistration) -> None:
        key = (model.model_id, model.version)
        if key not in self._items:
            raise KeyError(key)
        self._items[key] = model

    def list_all(self) -> tuple[ModelRegistration, ...]:
        return tuple(self._items.values())


class ScenarioService:
    def __init__(self, repository: ScenarioRepository) -> None:
        self._repository = repository

    def create(
        self,
        *,
        name: str,
        kind: ScenarioKind,
        assumptions: tuple[Assumption, ...],
        actor: str,
        scenario_id: str | None = None,
        parent_scenario_id: str | None = None,
    ) -> ScenarioVersion:
        if not assumptions:
            raise ValueError("scenario must contain assumptions")
        ids = [item.assumption_id for item in assumptions]
        if len(ids) != len(set(ids)):
            raise ValueError("assumption ids must be unique")
        sid = scenario_id or str(uuid4())
        current = self._repository.get(sid)
        version = 1 if current is None else current.version + 1
        payload: Mapping[str, Any] = {
            "name": name,
            "kind": kind.value,
            "assumptions": [
                {"id": item.assumption_id, "value": item.value, "owner": item.owner}
                for item in assumptions
            ],
        }
        scenario = ScenarioVersion(
            scenario_id=sid,
            version=version,
            name=name,
            kind=kind,
            assumptions=assumptions,
            status=GovernanceStatus.DRAFT,
            created_by=actor,
            created_at=datetime.now(timezone.utc),
            parent_scenario_id=parent_scenario_id,
            content_hash=_hash_payload(payload),
        )
        self._repository.add(scenario)
        return scenario

    def clone(self, scenario_id: str, *, actor: str, name: str | None = None) -> ScenarioVersion:
        source = self._require(scenario_id)
        return self.create(
            name=name or f"{source.name} copy",
            kind=source.kind,
            assumptions=source.assumptions,
            actor=actor,
            parent_scenario_id=source.scenario_id,
        )

    def approve(self, scenario_id: str, *, actor: str) -> ScenarioVersion:
        current = self._require(scenario_id)
        if current.created_by == actor:
            raise PermissionError("preparer and approver must be different users")
        approved = replace(current, status=GovernanceStatus.APPROVED, approved_by=actor)
        self._repository.add(replace(approved, version=current.version + 1))
        return replace(approved, version=current.version + 1)

    def compare(self, left_id: str, right_id: str) -> Mapping[str, tuple[Any, Any]]:
        left = self._require(left_id)
        right = self._require(right_id)
        left_map = {item.assumption_id: item.value for item in left.assumptions}
        right_map = {item.assumption_id: item.value for item in right.assumptions}
        keys = set(left_map) | set(right_map)
        return {key: (left_map.get(key), right_map.get(key)) for key in sorted(keys) if left_map.get(key) != right_map.get(key)}

    def _require(self, scenario_id: str) -> ScenarioVersion:
        item = self._repository.get(scenario_id)
        if item is None:
            raise KeyError(scenario_id)
        return item


class ModelRegistryService:
    def __init__(self, repository: ModelRegistryRepository) -> None:
        self._repository = repository

    def register(self, model: ModelRegistration) -> None:
        if not model.owner.strip() or not model.description.strip():
            raise ValueError("owner and description are required")
        self._repository.add(model)

    def validate(self, model_id: str, version: str, *, run_ids: tuple[str, ...]) -> ModelRegistration:
        if not run_ids:
            raise ValueError("at least one validation run is required")
        current = self._require(model_id, version)
        updated = replace(current, lifecycle=ModelLifecycle.VALIDATED, validation_run_ids=run_ids)
        self._repository.replace(updated)
        return updated

    def approve(self, model_id: str, version: str, *, actor: str) -> ModelRegistration:
        current = self._require(model_id, version)
        if current.lifecycle != ModelLifecycle.VALIDATED:
            raise ValueError("only validated models can be approved")
        if current.owner == actor:
            raise PermissionError("model owner cannot self-approve")
        updated = replace(current, lifecycle=ModelLifecycle.APPROVED, approved_by=actor)
        self._repository.replace(updated)
        return updated

    def deprecate(self, model_id: str, version: str) -> ModelRegistration:
        current = self._require(model_id, version)
        updated = replace(current, lifecycle=ModelLifecycle.DEPRECATED)
        self._repository.replace(updated)
        return updated

    def _require(self, model_id: str, version: str) -> ModelRegistration:
        item = self._repository.get(model_id, version)
        if item is None:
            raise KeyError((model_id, version))
        return item
