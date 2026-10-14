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
  recursion run --task "Say hello"

The shipped config enables fixture and fixture-b. Neither starts a CLI.
That run is reviewed by the other fixture and can finish without setting
review.accept_unreviewed. Pinning one provider with --provider leaves no
distinct reviewer. A live provider needs --allow-live.
See docs/USER-GUIDE.md.
EOF
