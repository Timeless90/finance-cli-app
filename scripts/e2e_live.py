"""Run live UAT against a unique test database in the new local PostgreSQL server."""
import os
from pathlib import Path
import subprocess
from uuid import uuid4
import psycopg
from psycopg import sql
ROOT = Path(__file__).resolve().parents[1]
name = 'finance_uat_' + uuid4().hex[:12]
admin = 'postgresql://template:template-local@127.0.0.1:15432/template'
with psycopg.connect(admin, autocommit=True) as connection:
    connection.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
    try:
        env = {**os.environ, 'CFO_LIVE_E2E':'1', 'CFO_FOUNDRY_MODE':'echo', 'CFO_GOVERNANCE_DATABASE_URL':admin.rsplit('/',1)[0]+'/'+name, 'CFO_IMPORT_STORAGE_PATH':str(ROOT/'.local/uat'/name)}
        env['CFO_TEST_DATABASE_URL'] = env['CFO_GOVERNANCE_DATABASE_URL']
        subprocess.run(['uv','run','--project','backend','pytest','backend/tests/test_postgres_governance.py'],cwd=ROOT,env=env,check=True)
        result = subprocess.run(['pnpm','e2e'],cwd=ROOT/'frontend',env=env)
    finally:
        connection.execute(sql.SQL('DROP DATABASE {} WITH (FORCE)').format(sql.Identifier(name)))
raise SystemExit(result.returncode)
