"""Export deterministic UAT contracts for frontend integration tests (no database)."""
import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.factory import create_app
from app.shared.config import ApiSettings

ROOT = Path(__file__).resolve().parents[1]
paths = [f'/api/v1/{name}/workspace' for name in ['planning','performance','profitability','liquidity','risk','market-risk','actions','capital','reporting','data-governance']]
paths += ['/api/v1/command-center/overview','/api/v1/context/principal','/api/v1/context/companies','/api/v1/context/periods','/api/v1/context/scenarios','/api/v1/data/imports','/api/v1/data/planning-mappings','/api/v1/data/planning-baselines','/api/v1/decision-runs','/health/ready','/api/v1/platform']
fixtures = {}
with TestClient(create_app(ApiSettings(environment='uat', governance_database_url=None, governance_database_path=None))) as client:
    for path in paths:
        response = client.get(path, params={'company_id':'AURELIA','period_id':'2026-08','scenario_id':'downside'}, headers={'X-User':'uat-cfo','X-Roles':'cfo','X-Companies':'AURELIA,EUROPE'})
        response.raise_for_status()
        fixtures[path] = response.json()
target = ROOT/'frontend/src/shared/test/fixtures/uat.json'
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(fixtures,indent=2)+'\n')
