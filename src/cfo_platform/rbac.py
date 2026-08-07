from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    CFO = "cfo"
    FP_AND_A = "fp_and_a"
    RISK = "risk"
    TREASURY = "treasury"
    CONTROLLER = "controller"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class Permission(StrEnum):
    READ_DATA = "read_data"
    WRITE_DATA = "write_data"
    CREATE_RUN = "create_run"
    VALIDATE_RUN = "validate_run"
    APPROVE_RUN = "approve_run"
    RETIRE_RUN = "retire_run"
    MANAGE_SCENARIOS = "manage_scenarios"
    MANAGE_MODELS = "manage_models"
    READ_AUDIT = "read_audit"
    MANAGE_ACCESS = "manage_access"


_ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.CFO: frozenset({Permission.READ_DATA, Permission.CREATE_RUN, Permission.APPROVE_RUN, Permission.READ_AUDIT}),
    Role.FP_AND_A: frozenset({Permission.READ_DATA, Permission.WRITE_DATA, Permission.CREATE_RUN, Permission.VALIDATE_RUN, Permission.MANAGE_SCENARIOS}),
    Role.RISK: frozenset({Permission.READ_DATA, Permission.CREATE_RUN, Permission.VALIDATE_RUN, Permission.MANAGE_MODELS, Permission.READ_AUDIT}),
    Role.TREASURY: frozenset({Permission.READ_DATA, Permission.CREATE_RUN, Permission.MANAGE_SCENARIOS}),
    Role.CONTROLLER: frozenset({Permission.READ_DATA, Permission.WRITE_DATA, Permission.CREATE_RUN, Permission.VALIDATE_RUN}),
    Role.REVIEWER: frozenset({Permission.READ_DATA, Permission.APPROVE_RUN, Permission.READ_AUDIT}),
    Role.ADMIN: frozenset(Permission),
}


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str
    roles: frozenset[Role]
    company_scopes: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not self.user_id.strip():
            raise ValueError("user_id must not be empty")
        if not self.roles:
            raise ValueError("at least one role is required")


class AccessControlService:
    def permissions_for(self, principal: Principal) -> frozenset[Permission]:
        permissions: set[Permission] = set()
        for role in principal.roles:
            permissions.update(_ROLE_PERMISSIONS[role])
        return frozenset(permissions)

    def require(
        self,
        principal: Principal,
        permission: Permission,
        *,
        company: str | None = None,
    ) -> None:
        if permission not in self.permissions_for(principal):
            raise PermissionError(f"missing permission: {permission.value}")
        if company is not None and principal.company_scopes and company not in principal.company_scopes:
            raise PermissionError(f"company out of scope: {company}")

    def can_access_company(self, principal: Principal, company: str) -> bool:
        return not principal.company_scopes or company in principal.company_scopes
