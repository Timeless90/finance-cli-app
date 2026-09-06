from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Header, HTTPException

from app.copilot.ai_foundry import (
    AIWorkload,
    CopilotRequest,
    FinanceCopilotService,
    FinanceModule,
    GroundedFact,
    ModelInvocationError,
    ModelRoutingTable,
    PromptSecurityError,
)
from app.copilot.schemas import (
    CopilotMessageRequest,
    CopilotRequestPayload,
    CopilotSessionRequest,
    GroundedFactPayload,
    PrincipalPayload,
    _Session,
)
from app.shared.principal import parse_principal
from app.shared.rbac import Principal
from app.workspace.workspace_integration import (
    ContextCatalogService,
    WorkspaceReadModelService,
)


def build_copilot_router(
    service: FinanceCopilotService,
    routing: ModelRoutingTable,
    contexts: ContextCatalogService,
    read_models: WorkspaceReadModelService,
) -> APIRouter:
    router = APIRouter(prefix="/copilot", tags=["copilot"])
    sessions: dict[str, _Session] = {}

    def actor(user: str, roles: str, companies: str) -> Principal:
        try:
            return parse_principal(user, roles, companies)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @router.post("/sessions")
    def create_session(
        payload: CopilotSessionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> dict[str, Any]:
        principal = actor(x_user, x_roles, x_companies)
        try:
            context = contexts.resolve(
                principal,
                company_id=payload.company_id,
                period_id=payload.period_id,
                scenario_id=payload.scenario_id,
            )
            projection = read_models.workspace(
                "reporting",
                principal,
                company_id=payload.company_id,
                period_id=payload.period_id,
                scenario_id=payload.scenario_id,
            )
        except PermissionError as exc:
            raise HTTPException(
                status_code=403, detail="copilot context is not permitted"
            ) from exc
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="no published copilot sources for this context"
            ) from exc
        source_ids = tuple(projection.source_snapshot_ids)
        if not source_ids:
            raise HTTPException(
                status_code=422,
                detail="published copilot context has no approved sources",
            )
        facts = tuple(
            GroundedFact(
                fact_id=f"published-source-{index + 1}",
                value=f"Published finance source for {context.company_id} {context.period_id} {context.scenario_id}",
                source_ref=source_id,
                approved=True,
                company=context.company_id,
            )
            for index, source_id in enumerate(source_ids)
        )
        session_id = str(uuid4())
        sessions[session_id] = _Session(
            session_id=session_id,
            principal=principal,
            request=CopilotRequest(
                module=payload.module,
                workload=payload.workload,
                question="",
                facts=facts,
            ),
        )
        route = routing.resolve(payload.module, payload.workload)
        return {
            "session_id": session_id,
            "context": context,
            "source_refs": list(source_ids),
            "route_id": route.route_id,
            "model_status": "configured",
        }

    @router.post("/sessions/{session_id}/messages")
    def send_message(
        session_id: str,
        payload: CopilotMessageRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> dict[str, Any]:
        session = sessions.get(session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="copilot session not found")
        principal = actor(x_user, x_roles, x_companies)
        if principal.user_id != session.principal.user_id:
            raise HTTPException(
                status_code=403, detail="copilot session is not permitted"
            )
        request = CopilotRequest(
            module=session.request.module,
            workload=session.request.workload,
            question=payload.question,
            facts=session.request.facts,
        )
        try:
            answer = service.respond(request, principal)
        except PermissionError as exc:
            raise HTTPException(
                status_code=403, detail="copilot request is not permitted"
            ) from exc
        except PromptSecurityError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except LookupError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ModelInvocationError as exc:
            raise HTTPException(
                status_code=503, detail="copilot model is unavailable"
            ) from exc
        return {"answer": answer}

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

    @router.post("/respond", deprecated=True, include_in_schema=False)
    def respond(payload: CopilotRequestPayload) -> dict[str, Any]:
        """Retained only as a compatibility signal; never accept browser facts.

        Governed clients must create a context-bound session and submit a
        message through its server-assembled source pack.
        """
        raise HTTPException(
            status_code=410,
            detail="use the governed copilot session endpoints",
        )

    return router


__all__ = [
    "CopilotMessageRequest",
    "CopilotRequestPayload",
    "CopilotSessionRequest",
    "GroundedFactPayload",
    "PrincipalPayload",
    "_Session",
    "build_copilot_router",
]
