#!/usr/bin/env bash
# Create a virtualenv, install this checkout, and run recursion doctor.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

if [[ -n "${PYTHON:-}" ]]; then
  py="$PYTHON"
elif command -v python3 >/dev/null 2>&1; then
  py="python3"
else
  py="python"
fi

"$py" -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/recursion doctor

cat <<'EOF'

Next steps:
  source .venv/bin/activate
  recursion --help
  recursion run --task "Say hello" --provider fixture

The fixture provider starts no CLI. With only that provider, review has no
second candidate, so the run is unreviewed and exits 2 unless
review.accept_unreviewed is true. A live provider needs --allow-live.
See docs/USER-GUIDE.md.
EOF
