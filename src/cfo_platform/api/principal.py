from __future__ import annotations

from cfo_platform.rbac import Principal, Role


def parse_principal(user: str, roles: str, companies: str = "") -> Principal:
    parsed_roles = frozenset(
        Role(item.strip()) for item in roles.split(",") if item.strip()
    )
    scopes = frozenset(
        item.strip() for item in companies.split(",") if item.strip()
    )
    return Principal(
        user_id=user,
        roles=parsed_roles,
        company_scopes=scopes,
    )
