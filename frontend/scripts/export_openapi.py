from __future__ import annotations

import json
from pathlib import Path

from cfo_platform.api.main import app


def main() -> None:
    frontend_root = Path(__file__).resolve().parents[1]
    target = frontend_root / "openapi" / "backend-openapi.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Exported FastAPI OpenAPI contract to {target}")


if __name__ == "__main__":
    main()
