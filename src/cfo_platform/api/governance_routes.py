from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from cfo_platform.governance import GovernedRunService, RunLineage
from cfo_platform.governance_catalog import (
    Assumption,
    ModelLifecycle,
    ModelRegistration,
    ModelRegistryService,
    ScenarioKind,
    ScenarioService,
)
from cfo_platform.rbac import AccessControlService, Permission, Principal, Role


class RunCreateRequest(BaseModel):
    model_id: str
    model_version: str
    code_version: str
    snapshot_id: str
    parameters: dict[str, Any]
    random_seed: int
    output: dict[str, Any] | None = None


class TransitionRequest(BaseModel):
    reason: str = Field(min_length=1)


class ScenarioCreateRequest(BaseModel):
    name: str
    kind: ScenarioKind
    assumptions: list[dict[str, Any]]


class ModelCreateRequest(BaseModel):
    model_id: str
    version: str
    owner: str
    description: str
    limitations: list[str] = []


def build_governance_router(
    run_service: GovernedRunService,
    scenario_service: ScenarioService,
    model_service: ModelRegistryService,
    access: AccessControlService,
) -> APIRouter:
    router = APIRouter(prefix="/governance", tags=["governance"])

    def principal(user: str, roles: str, companies: str) -> Principal:
        parsed_roles = frozenset(Role(item.strip()) for item in roles.split(",") if item.strip())
        scopes = frozenset(item.strip() for item in companies.split(",") if item.strip())
        return Principal(user_id=user, roles=parsed_roles, company_scopes=scopes)

    @router.post("/runs", status_code=201)
    def create_run(
        request: RunCreateRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        x_correlation_id: str = Header(default="api"),
    ) -> dict[str, Any]:
        actor = principal(x_user, x_roles, x_companies)
        access.require(actor, Permission.CREATE_RUN)
        lineage = RunLineage.from_parameters(
            model_id=request.model_id,
            model_version=request.model_version,
            code_version=request.code_version,
            snapshot_id=request.snapshot_id,
            parameters=request.parameters,
            random_seed=request.random_seed,
        )
        run = run_service.create(
            lineage=lineage,
            actor=actor.user_id,
            correlation_id=x_correlation_id,
            output=request.output,
        )
        return {"run_id": run.run_id, "status": run.status.value, "lineage": run_service.lineage(run.run_id)}

    @router.post("/runs/{run_id}/validate")
    def validate_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        x_correlation_id: str = Header(default="api"),
    ) -> dict[str, str]:
        actor = principal(x_user, x_roles, x_companies)
        access.require(actor, Permission.VALIDATE_RUN)
        try:
            run = run_service.validate(run_id, actor=actor.user_id, correlation_id=x_correlation_id)
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"run_id": run.run_id, "status": run.status.value}

    @router.post("/runs/{run_id}/approve")
    def approve_run(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        x_correlation_id: str = Header(default="api"),
    ) -> dict[str, str]:
        actor = principal(x_user, x_roles, x_companies)
        access.require(actor, Permission.APPROVE_RUN)
        try:
            run = run_service.approve(run_id, actor=actor.user_id, correlation_id=x_correlation_id)
        except (KeyError, ValueError, PermissionError) as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"run_id": run.run_id, "status": run.status.value}

    @router.post("/runs/{run_id}/retire")
    def retire_run(
        run_id: str,
        request: TransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
        x_correlation_id: str = Header(default="api"),
    ) -> dict[str, str]:
        actor = principal(x_user, x_roles, x_companies)
        access.require(actor, Permission.RETIRE_RUN)
        run = run_service.retire(
            run_id,
            actor=actor.user_id,
            correlation_id=x_correlation_id,
            reason=request.reason,
        )
        return {"run_id": run.run_id, "status": run.status.value}

    @router.get("/runs/{run_id}/lineage")
    def lineage(
        run_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> dict[str, Any]:
        actor = principal(x_user, x_roles, x_companies)
        access.require(actor, Permission.READ_AUDIT)
        try:
            return dict(run_service.lineage(run_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="run not found") from exc

    @router.post("/scenarios", status_code=201)
    def create_scenario(
        request: ScenarioCreateRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> dict[str, Any]:
        actor = principal(x_user, x_roles, x_companies)
        access.require(actor, Permission.MANAGE_SCENARIOS)
        assumptions = tuple(
            Assumption(
                assumption_id=str(item["id"]),
                name=str(item.get("name", item["id"])),
                value=item["value"],
                owner=str(item.get("owner", actor.user_id)),
                unit=str(item["unit"]) if item.get("unit") is not None else None,
                source=str(item["source"]) if item.get("source") is not None else None,
            )
            for item in request.assumptions
        )
        scenario = scenario_service.create(
            name=request.name,
            kind=request.kind,
            assumptions=assumptions,
            actor=actor.user_id,
        )
        return {"scenario_id": scenario.scenario_id, "version": scenario.version, "status": scenario.status.value}

    @router.post("/models", status_code=201)
    def register_model(
        request: ModelCreateRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> dict[str, str]:
        actor = principal(x_user, x_roles, x_companies)
        access.require(actor, Permission.MANAGE_MODELS)
        model = ModelRegistration(
            model_id=request.model_id,
            version=request.version,
            owner=request.owner,
            description=request.description,
            limitations=tuple(request.limitations),
            lifecycle=ModelLifecycle.DEVELOPMENT,
        )
        model_service.register(model)
        return {"model_id": model.model_id, "version": model.version, "lifecycle": model.lifecycle.value}

    return router
