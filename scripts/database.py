"""Initialize or inspect existing adapters in the explicitly selected local database."""
import os
import sys
import psycopg
from app.shared.composition import build_container
url = os.environ.get("CFO_GOVERNANCE_DATABASE_URL", "postgresql://template:template-local@127.0.0.1:15432/template")
if sys.argv[1:] == ["init"]:
    container = build_container(governance_database_url=url)
    container.shutdown()
    print("Existing adapter schema initialized.")
elif sys.argv[1:] == ["check"]:
    expected = {"governed_runs", "audit_events", "data_snapshots", "finance_imports", "planning_mapping_sets", "planning_baselines", "workspace_read_models"}
    with psycopg.connect(url) as connection:
        actual = {row[0] for row in connection.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")}
    missing = expected - actual
    if missing:
        raise SystemExit("Missing persistence tables: " + ", ".join(sorted(missing)))
    print("PASS existing persistence tables (read-only check).")
else:
    raise SystemExit("Usage: database.py init|check")
