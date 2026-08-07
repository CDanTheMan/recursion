#!/usr/bin/env bash
# Offline/read-only acceptance for the Phase 1 service and dependency deployment artifacts.
set -euo pipefail
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
UNIT="$ROOT/deploy/systemd/hermes-gateway.service"
REQ="$ROOT/deploy/requirements/hermes-gateway-phase1.txt"
SYSUSERS="$ROOT/deploy/sysusers.d/recursion.conf"
TMPFILES="$ROOT/deploy/tmpfiles.d/recursion.conf"

systemd-analyze verify "$UNIT" >/dev/null
need(){ grep -qxF "$1" "$UNIT" || { echo "FAIL missing unit control: $1"; exit 1; }; }
need User=hermes-gateway
need Group=hermes-gateway
need NoNewPrivileges=yes
need CapabilityBoundingSet=
need AmbientCapabilities=
need PrivateTmp=yes
need PrivateDevices=yes
need ProtectSystem=strict
need ProtectHome=yes
need UMask=0077
need KillMode=control-group
grep -q '^u hermes-gateway ' "$SYSUSERS"
grep -q '^u recursion-runner ' "$SYSUSERS"
grep -q '^d /var/lib/hermes-gateway 0700 ' "$TMPFILES"
grep -q '^d /var/lib/recursion-runner 0700 ' "$TMPFILES"
grep -qx 'aiohttp==3.14.3' "$REQ"
grep -qx 'cryptography==50.0.0' "$REQ"

python3 - "$REQ" <<'PY'
import json, sys, urllib.request
pins=[]
for line in open(sys.argv[1],encoding='utf-8'):
    line=line.strip()
    if line and not line.startswith('#'):
        name,version=line.split('==',1); pins.append((name,version))
payload={'queries':[{'package':{'ecosystem':'PyPI','name':n},'version':v} for n,v in pins]}
request=urllib.request.Request('https://api.osv.dev/v1/querybatch',
    data=json.dumps(payload).encode(),headers={'Content-Type':'application/json',
    'User-Agent':'recursion-phase1-artifact-audit'})
with urllib.request.urlopen(request,timeout=30) as response: data=json.load(response)
bad=[]
for (name,version),result in zip(pins,data.get('results',[])):
    ids=[v.get('id','?') for v in (result.get('vulns') or [])]
    print(f'{name}=={version}|'+(','.join(ids) if ids else 'OSV_CLEAR'))
    if ids: bad.append((name,ids))
raise SystemExit(1 if bad else 0)
PY

echo "hermes-pilot-phase1-artifacts: ALL PASS"
