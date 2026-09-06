from pathlib import Path
import json
from app.factory import create_app
from app.shared.config import ApiSettings
ROOT = Path(__file__).resolve().parents[1]
settings = ApiSettings(_env_file=None, governance_database_url=None, governance_database_path=None, environment="test", telemetry_enabled=False)
application = create_app(settings)
try:
    (ROOT / "backend/openapi.json").write_text(json.dumps(application.openapi(), indent=2, sort_keys=True) + "\n")
finally:
    application.state.container.shutdown()
