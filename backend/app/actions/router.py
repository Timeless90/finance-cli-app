from __future__ import annotations

from fastapi import APIRouter

from app.actions.action_management import (
    ActionCatalogueService,
    ActionImpact,
    ActionPortfolioPrioritizer,
    ActionReviewService,
    ActionSimulationEngine,
    BenefitObservation,
    BenefitTrackingService,
    ManagementAction,
)
from app.actions.schemas import (
    ActionImpactPayload,
    ActionRequest,
    ActionSelectionRequest,
    BenefitObservationPayload,
    BenefitTrackingRequest,
    ReviewRequest,
    StatusChangeRequest,
)


def _to_action(payload: ActionRequest) -> ManagementAction:
    return ManagementAction(
        action_id=payload.action_id,
        title=payload.title,
        owner=payload.owner,
        due_period=payload.due_period,
        cost=payload.cost,
        impacts=tuple(ActionImpact(**item.model_dump()) for item in payload.impacts),
        confidence=payload.confidence,
        status=payload.status,
        description=payload.description,
    )


def build_action_router(
    catalogue: ActionCatalogueService,
    simulation_engine: ActionSimulationEngine,
    prioritizer: ActionPortfolioPrioritizer,
    review_service: ActionReviewService,
    benefit_tracking: BenefitTrackingService,
) -> APIRouter:
    router = APIRouter(prefix="/actions", tags=["actions"])

    @router.post("/register")
    def register_action(payload: ActionRequest) -> dict[str, object]:
        return {"action": catalogue.register(_to_action(payload))}

    @router.get("")
    def list_actions() -> dict[str, object]:
        return {"actions": catalogue.list()}

    @router.get("/{action_id}")
    def get_action(action_id: str) -> dict[str, object]:
        return {"action": catalogue.get(action_id)}

    @router.post("/simulate")
    def simulate_actions(payload: ActionSelectionRequest) -> dict[str, object]:
        actions = tuple(catalogue.get(action_id) for action_id in payload.action_ids)
        return {"result": simulation_engine.simulate(actions)}

    @router.post("/portfolio/prioritize")
    def prioritize_actions(payload: ActionSelectionRequest) -> dict[str, object]:
        actions = tuple(catalogue.get(action_id) for action_id in payload.action_ids)
        return {"priorities": prioritizer.prioritize(actions)}

    @router.post("/{action_id}/status")
    def change_status(
        action_id: str, payload: StatusChangeRequest
    ) -> dict[str, object]:
        return {"action": catalogue.change_status(action_id, payload.status)}

    @router.post("/{action_id}/review")
    def review_action(action_id: str, payload: ReviewRequest) -> dict[str, object]:
        return {
            "review": review_service.review(
                catalogue.get(action_id), payload.current_period
            )
        }

    @router.post("/benefits/track")
    def track_benefits(payload: BenefitTrackingRequest) -> dict[str, object]:
        observations = tuple(
            BenefitObservation(**item.model_dump()) for item in payload.observations
        )
        return {"results": benefit_tracking.summarize(observations)}

    return router


__all__ = [
    "ActionImpactPayload",
    "ActionRequest",
    "ActionSelectionRequest",
    "BenefitObservationPayload",
    "BenefitTrackingRequest",
    "ReviewRequest",
    "StatusChangeRequest",
    "_to_action",
    "build_action_router",
]
