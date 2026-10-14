"""Start coverage in the check programs this suite launches."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("COVERAGE_PROCESS_START", str(ROOT / "pyproject.toml"))
