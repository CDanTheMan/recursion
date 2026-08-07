#!/usr/bin/env bash
# Phase 7 reporting/outbox falsifiers. The Python harness uses only inert transports.
set -euo pipefail
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/hermes-pilot-phase7-red.py"
