#!/usr/bin/env bash
# Phase 8 production-pilot falsifiers. Hermetic: no model, network, publisher, sender,
# deployment, or live control-plane state is reachable from this test.
set -euo pipefail
exec python3 -u "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/hermes-pilot-phase8-red.py"
