"""Install workspace recommendations in an optional existing VS Code profile."""

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    code = shutil.which("code")
    if not code:
        raise SystemExit("VS Code CLI fehlt; Empfehlungen über VS Code installieren.")
    project = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
    profile = project["vscode_profile"]
    command = [code, "--profile", profile] if profile else [code]
    installed = set(
        subprocess.check_output(command + ["--list-extensions"], text=True)
        .lower()
        .splitlines()
    )
    recommendations = json.loads(
        (ROOT / ".vscode/extensions.json").read_text(encoding="utf-8")
    )["recommendations"]
    for name in recommendations:
        if name.lower() not in installed:
            subprocess.run(command + ["--install-extension", name], check=True)


if __name__ == "__main__":
    main()
