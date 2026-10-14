"""``python -m scripts.v3.harness`` entry point."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.v3.harness.run import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
