import os

import psycopg
import pytest

from app.governance.governance import GovernedRunService, RunLineage
from app.governance.governance_persistence import (
    PostgresAuditEventRepository,
    PostgresGovernedRunRepository,
)


def test_postgres_governance_round_trip_and_immutable_integer():
    url = os.environ.get("CFO_TEST_DATABASE_URL")
    if not url:
        pytest.skip("Run make e2e-live for the isolated PostgreSQL test database.")
    runs = PostgresGovernedRunRepository(url)
    audit = PostgresAuditEventRepository(url)
    service = GovernedRunService(runs, audit)
    lineage = RunLineage.from_parameters(
        model_id="migration-test",
        model_version="1",
        code_version="test",
        snapshot_id="test-snapshot",
        parameters={"paths": 100},
        random_seed=42,
    )
    created = service.create(
        lineage=lineage, actor="preparer", correlation_id="migration-test"
    )
    service.validate(created.run_id, actor="validator", correlation_id="migration-test")
    approved = service.approve(
        created.run_id, actor="approver", correlation_id="migration-test"
    )
    assert PostgresGovernedRunRepository(url).get(created.run_id) == approved
    assert len(audit.list_for("governed_run", created.run_id)) == 3
    with psycopg.connect(url) as connection:
        assert connection.execute(
            "SELECT immutable FROM governed_runs WHERE run_id = %s", (created.run_id,)
        ).fetchone() == (1,)
    with pytest.raises(ValueError, match="cannot be overwritten"):
        runs.replace(created)
