"""Validate profile selection without touching the user's VS Code installation."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "install_extensions", ROOT / "scripts/install_extensions.py"
)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class ExtensionTests(unittest.TestCase):
    def test_standard_and_named_profile_preserve_installed_extensions(self):
        for profile in ("", "Meine Arbeit"):
            with self.subTest(profile=profile), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / ".vscode").mkdir()
                (root / "project.json").write_text(
                    json.dumps({"vscode_profile": profile})
                )
                (root / ".vscode/extensions.json").write_text(
                    json.dumps({"recommendations": ["installed.one", "new.two"]})
                )
                with (
                    patch.object(installer, "ROOT", root),
                    patch.object(installer.shutil, "which", return_value="/bin/code"),
                    patch.object(
                        installer.subprocess,
                        "check_output",
                        return_value="Installed.One\n",
                    ) as listing,
                    patch.object(installer.subprocess, "run") as run,
                ):
                    installer.main()
                command = ["/bin/code"] + (["--profile", profile] if profile else [])
                listing.assert_called_once_with(
                    command + ["--list-extensions"], text=True
                )
                run.assert_called_once_with(
                    command + ["--install-extension", "new.two"], check=True
                )


if __name__ == "__main__":
    unittest.main()
