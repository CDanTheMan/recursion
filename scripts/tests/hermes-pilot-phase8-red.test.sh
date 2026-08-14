#!/usr/bin/env bash
# Phase 8 production-pilot falsifiers. Hermetic: no model, network, publisher, sender,
# deployment, or live control-plane state is reachable from this test.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 -u "$HERE/hermes-pilot-phase8-red.py"
python3 -u "$HERE/hermes-pilot-phase8-parallel.py"
python3 -u "$HERE/hermes-pilot-phase8-legacy-journal-red.py"
python3 -u "$HERE/hermes-pilot-phase8-race-red.py"
python3 -u "$HERE/hermes-pilot-phase8-reject-red.py"
python3 -u "$HERE/hermes-phase8-routing-recovery-red.py"
