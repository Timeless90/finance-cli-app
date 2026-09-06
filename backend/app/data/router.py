from __future__ import annotations

import base64

from fastapi import APIRouter, Header, HTTPException, Response, status

from app.data.data_publication import FinanceImport, FinanceImportPublicationService
from app.data.data_reconciliation import ReconciliationRule
from app.data.schemas import (
    DataImportRequest,
    DataImportResponse,
    FindingResponse,
    ImportTransitionRequest,
    PlanningAccountMappingRequest,
    PlanningBaselinePublishRequest,
    PlanningBaselineResponse,
    PlanningMappingCreateRequest,
    PlanningMappingResponse,
    PlanningMappingTransitionRequest,
    ReconciliationResponse,
    ReconciliationRuleRequest,
    SnapshotResponse,
    SourceAccountResponse,
)
from app.planning.planning_baseline import (
    PlanningAccountMapping,
    PlanningBaseline,
    PlanningBaselineService,
    PlanningMappingSet,
)
from app.shared.principal import parse_principal


def build_data_router(
    service: FinanceImportPublicationService,
    planning_baselines: PlanningBaselineService,
) -> APIRouter:
    router = APIRouter(prefix="/data", tags=["data"])

    def actor(user: str, roles: str, companies: str):
        try:
            return parse_principal(user, roles, companies)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    def response_for(item: FinanceImport) -> DataImportResponse:
        snapshot = service.snapshot_metadata(item.snapshot_id)
        return DataImportResponse(
            import_id=item.import_id,
            file_name=item.file_name,
            file_type=item.file_type,
            company_ids=list(item.company_ids),
            status=item.status.value,
            created_by=item.created_by,
            created_at=item.created_at.isoformat(),
            reviewed_by=item.reviewed_by,
            approved_by=item.approved_by,
            published_by=item.published_by,
            note=item.note,
            row_count=item.quality_report.row_count,
            quality_score=item.quality_report.score,
            quality_blocking=item.quality_report.blocking,
            reconciliation_blocking=item.reconciliation_report.blocking,
            run_eligible=item.run_eligible,
            snapshot_id=item.snapshot_id,
            content_hash=snapshot.content_hash if snapshot else None,
            unmapped_accounts=list(item.unmapped_accounts),
            findings=[
                FindingResponse(
                    code=finding.code,
                    severity=finding.severity.value,
                    message=finding.message,
                    row_number=finding.row_number,
                )
                for finding in item.quality_report.findings
            ],
            reconciliations=[
                ReconciliationResponse(
                    rule_id=result.rule_id,
                    actual_total=result.actual_total,
                    expected_total=result.expected_total,
                    variance=result.variance,
                    status=result.status.value,
                    blocking=result.blocking,
                )
                for result in item.reconciliation_report.results
            ],
        )

    def mapping_response(item: PlanningMappingSet) -> PlanningMappingResponse:
        return PlanningMappingResponse(
            mapping_set_id=item.mapping_set_id,
            company_id=item.company_id,
            source_snapshot_id=item.source_snapshot_id,
            version_label=item.version_label,
            status=item.status.value,
            created_by=item.created_by,
            created_at=item.created_at.isoformat(),
            reviewed_by=item.reviewed_by,
            approved_by=item.approved_by,
            note=item.note,
            mappings=[
                PlanningAccountMappingRequest(
                    source_account=mapping.source_account,
                    category=mapping.category,
                    sign_multiplier=mapping.sign_multiplier,
                )
                for mapping in item.mappings
            ],
        )

    def baseline_response(item: PlanningBaseline) -> PlanningBaselineResponse:
        return PlanningBaselineResponse(
            baseline_id=item.baseline_id,
            company_id=item.company_id,
            period_id=item.period_id,
            scenario_id=item.scenario_id,
            source_snapshot_id=item.source_snapshot_id,
            mapping_set_id=item.mapping_set_id,
            values=item.values_by_category(),
            missing_categories=[category.value for category in item.missing_categories],
            forecast_eligible=item.forecast_eligible,
            created_at=item.created_at.isoformat(),
            published_by=item.published_by,
        )

    @router.post(
        "/imports",
        response_model=DataImportResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def import_finance_data(
        payload: DataImportRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> DataImportResponse:
        try:
            content = base64.b64decode(payload.content_base64, validate=True)
            item = service.create(
                actor(x_user, x_roles, x_companies),
                file_name=payload.file_name,
                content=content,
                file_type=payload.file_type,
                column_mapping=payload.column_mapping,
                allowed_currencies=payload.allowed_currencies,
                required_dimensions=payload.required_dimensions,
                sheet_name=payload.sheet_name,
                reconciliation_rules=tuple(
                    ReconciliationRule(**rule.model_dump())
                    for rule in payload.reconciliation_rules
                ),
            )
            return response_for(item)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except (ValueError, UnicodeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.get("/imports", response_model=list[DataImportResponse])
    def list_imports(
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[DataImportResponse]:
        try:
            return [
                response_for(item)
                for item in service.list(actor(x_user, x_roles, x_companies))
            ]
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.post("/imports/{import_id}/review", response_model=DataImportResponse)
    def review_import(
        import_id: str,
        payload: ImportTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> DataImportResponse:
        try:
            return response_for(
                service.review(
                    actor(x_user, x_roles, x_companies), import_id, payload.note
                )
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="import not found") from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/imports/{import_id}/approve", response_model=DataImportResponse)
    def approve_import(
        import_id: str,
        payload: ImportTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> DataImportResponse:
        try:
            return response_for(
                service.approve(
                    actor(x_user, x_roles, x_companies), import_id, payload.note
                )
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="import not found") from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post("/imports/{import_id}/publish", response_model=DataImportResponse)
    def publish_import(
        import_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> DataImportResponse:
        try:
            return response_for(
                service.publish(actor(x_user, x_roles, x_companies), import_id)
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="import not found") from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.get("/imports/{import_id}/source")
    def download_source(
        import_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> Response:
        try:
            item, content = service.source(
                actor(x_user, x_roles, x_companies), import_id
            )
            return Response(
                content,
                media_type="application/octet-stream",
                headers={
                    "Content-Disposition": f'attachment; filename="{item.file_name}"'
                },
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="import not found") from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.get(
        "/imports/{import_id}/accounts", response_model=list[SourceAccountResponse]
    )
    def list_source_accounts(
        import_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[SourceAccountResponse]:
        try:
            return [
                SourceAccountResponse(account=account, total=total)
                for account, total in planning_baselines.source_accounts(
                    actor(x_user, x_roles, x_companies), import_id
                )
            ]
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="import not found") from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post(
        "/planning-mappings",
        response_model=PlanningMappingResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def create_planning_mapping(
        payload: PlanningMappingCreateRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> PlanningMappingResponse:
        try:
            item = planning_baselines.create_mapping(
                actor(x_user, x_roles, x_companies),
                company_id=payload.company_id,
                source_snapshot_id=payload.source_snapshot_id,
                version_label=payload.version_label,
                mappings=tuple(
                    PlanningAccountMapping(**mapping.model_dump())
                    for mapping in payload.mappings
                ),
            )
            return mapping_response(item)
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="data snapshot not found"
            ) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @router.get("/planning-mappings", response_model=list[PlanningMappingResponse])
    def list_planning_mappings(
        company_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[PlanningMappingResponse]:
        try:
            return [
                mapping_response(item)
                for item in planning_baselines.list_mappings(
                    actor(x_user, x_roles, x_companies), company_id=company_id
                )
            ]
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.post(
        "/planning-mappings/{mapping_set_id}/review",
        response_model=PlanningMappingResponse,
    )
    def review_planning_mapping(
        mapping_set_id: str,
        payload: PlanningMappingTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> PlanningMappingResponse:
        try:
            return mapping_response(
                planning_baselines.review_mapping(
                    actor(x_user, x_roles, x_companies), mapping_set_id, payload.note
                )
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="planning mapping not found"
            ) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post(
        "/planning-mappings/{mapping_set_id}/approve",
        response_model=PlanningMappingResponse,
    )
    def approve_planning_mapping(
        mapping_set_id: str,
        payload: PlanningMappingTransitionRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> PlanningMappingResponse:
        try:
            return mapping_response(
                planning_baselines.approve_mapping(
                    actor(x_user, x_roles, x_companies), mapping_set_id, payload.note
                )
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="planning mapping not found"
            ) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.post(
        "/planning-baselines",
        response_model=PlanningBaselineResponse,
        status_code=status.HTTP_201_CREATED,
    )
    def publish_planning_baseline(
        payload: PlanningBaselinePublishRequest,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> PlanningBaselineResponse:
        try:
            return baseline_response(
                planning_baselines.publish_baseline(
                    actor(x_user, x_roles, x_companies),
                    mapping_set_id=payload.mapping_set_id,
                    period_id=payload.period_id,
                    scenario_id=payload.scenario_id,
                )
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="planning mapping or data snapshot not found"
            ) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @router.get("/planning-baselines", response_model=list[PlanningBaselineResponse])
    def list_planning_baselines(
        company_id: str,
        period_id: str,
        scenario_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> list[PlanningBaselineResponse]:
        try:
            return [
                baseline_response(item)
                for item in planning_baselines.list_baselines(
                    actor(x_user, x_roles, x_companies),
                    company_id=company_id,
                    period_id=period_id,
                    scenario_id=scenario_id,
                )
            ]
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc

    @router.get("/snapshots/{snapshot_id:path}", response_model=SnapshotResponse)
    def get_snapshot(
        snapshot_id: str,
        x_user: str = Header(...),
        x_roles: str = Header(...),
        x_companies: str = Header(default=""),
    ) -> SnapshotResponse:
        try:
            snapshot = service.snapshot(
                actor(x_user, x_roles, x_companies), snapshot_id
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="Data snapshot not found"
            ) from exc
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        return SnapshotResponse(
            snapshot_id=snapshot.snapshot_id,
            content_hash=snapshot.content_hash,
            row_count=snapshot.row_count,
        )

    return router


__all__ = [
    "DataImportRequest",
    "DataImportResponse",
    "FindingResponse",
    "ImportTransitionRequest",
    "PlanningAccountMappingRequest",
    "PlanningBaselinePublishRequest",
    "PlanningBaselineResponse",
    "PlanningMappingCreateRequest",
    "PlanningMappingResponse",
    "PlanningMappingTransitionRequest",
    "ReconciliationResponse",
    "ReconciliationRuleRequest",
    "SnapshotResponse",
    "SourceAccountResponse",
    "build_data_router",
]
