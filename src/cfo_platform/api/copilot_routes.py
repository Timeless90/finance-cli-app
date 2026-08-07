from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from cfo_platform.ai_foundry import (
    AIWorkload,
    CopilotRequest,
    FinanceCopilotService,
    FinanceModule,
    GroundedFact,
    ModelInvocationError,
    ModelRoutingTable,
    PromptSecurityError,
)
from cfo_platform.rbac import Principal, Role


class PrincipalPayload(BaseModel):
    user_id: str = Field(min_length=1)
    roles: list[Role] = Field(min_length=1)
    company_scopes: list[str] = Field(default_factory=list)


class GroundedFactPayload(BaseModel):
    fact_id: str = Field(min_length=1)
    value: str
    source_ref: str = Field(min_length=1)
    approved: bool = True
    company: str | None = None


class CopilotRequestPayload(BaseModel):
    module: FinanceModule
    workload: AIWorkload
    question: str = Field(min_length=1)
    facts: list[GroundedFactPayload] = Field(min_length=1)
    principal: PrincipalPayload


def build_copilot_router(
    service: FinanceCopilotService,
    routing: ModelRoutingTable,
) -> APIRouter:
    router = APIRouter(prefix="/copilot", tags=["copilot"])

    @router.get("/routes")
    def list_routes() -> dict[str, Any]:
        return {
            "routes": [
                {
                    "route_id": route.route_id,
                    "module": route.module.value if route.module else None,
                    "workload": route.workload.value,
                    "deployment": route.deployment,
                    "strategy": route.strategy.value,
                    "fallback_deployments": list(route.fallback_deployments),
                    "max_output_tokens": route.max_output_tokens,
                }
                for route in routing.list_routes()
            ]
        }

    @router.get("/routes/resolve")
    def resolve_route(module: FinanceModule, workload: AIWorkload) -> dict[str, Any]:
        try:
            route = routing.resolve(module, workload)
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return {
            "route": {
                "route_id": route.route_id,
                "module": route.module.value if route.module else None,
                "workload": route.workload.value,
                "deployment": route.deployment,
                "strategy": route.strategy.value,
                "fallback_deployments": list(route.fallback_deployments),
                "max_output_tokens": route.max_output_tokens,
            }
        }

    @router.post("/respond")
    def respond(payload: CopilotRequestPayload) -> dict[str, Any]:
        principal = Principal(
            user_id=payload.principal.user_id,
            roles=frozenset(payload.principal.roles),
            company_scopes=frozenset(payload.principal.company_scopes),
        )
        request = CopilotRequest(
            module=payload.module,
            workload=payload.workload,
            question=payload.question,
            facts=tuple(GroundedFact(**fact.model_dump()) for fact in payload.facts),
        )
        try:
            answer = service.respond(request, principal)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except PromptSecurityError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ModelInvocationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        return {"answer": answer}

    return router
