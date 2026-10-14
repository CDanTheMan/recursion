"""The one-step install scripts stay the setup the CI job runs."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_install_scripts_create_a_venv_install_and_run_doctor() -> None:
    shell = (ROOT / "scripts" / "install.sh").read_text(encoding="utf-8")
    powershell = (ROOT / "scripts" / "install.ps1").read_text(encoding="utf-8")
    for text in (shell, powershell):
        assert "venv" in text
        assert "pip install -e ." in text
        assert "doctor" in text
        assert "Next steps:" in text
        assert "recursion --help" in text
    if "set -euo pipefail" not in shell:
        pytest.fail("install.sh does not stop on the first failure")
    if "$LASTEXITCODE" not in powershell:
        pytest.fail("install.ps1 does not check native command exit codes")
