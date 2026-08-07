#!/usr/bin/env bash
# Read-only live Phase 1 controls. Expected to fail before Phase 1 implementation.
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-/opt/recursion}"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

[ -f "$ROOT/state/PAUSE" ] || { echo "FATAL remote PAUSE is absent"; exit 90; }
ok "remote PAUSE is present"

prop(){ systemctl show hermes-gateway --property="$1" --value --no-pager 2>/dev/null; }
user="$(prop User)"; group="$(prop Group)"; nnp="$(prop NoNewPrivileges)"
pt="$(prop PrivateTmp)"; pd="$(prop PrivateDevices)"; ps="$(prop ProtectSystem)"
ph="$(prop ProtectHome)"; umask="$(prop UMask)"
if [ -n "$user" ] && [ "$user" != root ] && [ -n "$group" ] && [ "$group" != root ] \
   && [ "$nnp" = yes ] && [ "$pt" = yes ] && [ "$pd" = yes ] \
   && { [ "$ps" = strict ] || [ "$ps" = full ]; } \
   && { [ "$ph" = yes ] || [ "$ph" = read-only ]; } \
   && { [ "$umask" = 0077 ] || [ "$umask" = 0027 ]; }; then
  ok "hermes-gateway runs as a hardened non-root service"
else
  no "hermes-gateway is unrestricted (User=$user Group=$group NNP=$nnp PrivateTmp=$pt PrivateDevices=$pd ProtectSystem=$ps ProtectHome=$ph UMask=$umask)"
fi

# Audit the exact installed Hermes Python environment against OSV without installing anything.
PY="$(systemctl show hermes-gateway --property=ExecStart --value --no-pager 2>/dev/null \
  | sed -n 's#^{ path=\([^ ;]*\).*#\1#p')"
[ -x "$PY" ] || PY=/usr/local/lib/hermes-agent/venv/bin/python
audit="$($PY - <<'PY' 2>&1
import importlib.metadata as md, json, urllib.request
packages=sorted(set((d.metadata.get('Name'),d.version) for d in md.distributions()
                    if d.metadata.get('Name')),key=lambda x:x[0].lower())
payload={'queries':[{'package':{'ecosystem':'PyPI','name':n},'version':v} for n,v in packages]}
req=urllib.request.Request('https://api.osv.dev/v1/querybatch',data=json.dumps(payload).encode(),
                           headers={'Content-Type':'application/json','User-Agent':'recursion-phase0-readonly-audit'})
with urllib.request.urlopen(req,timeout=30) as response: data=json.load(response)
rows=[]
for (name,version),result in zip(packages,data.get('results',[])):
    ids=[v.get('id','?') for v in (result.get('vulns') or [])]
    if ids: rows.append((name,version,ids))
print('AUDITED='+str(len(packages)))
for name,version,ids in rows: print(name+'|'+version+'|'+','.join(ids))
raise SystemExit(1 if rows else 0)
PY
)"; audit_rc=$?
printf '%s\n' "$audit"
[ "$audit_rc" -eq 0 ] && ok "installed gateway dependencies have no known OSV advisories" \
                       || no "installed gateway dependencies have known advisories or could not be audited"

[ -f "$ROOT/state/PAUSE" ] || { echo "FATAL remote PAUSE disappeared"; exit 91; }
echo
[ "$fails" -eq 0 ] && { echo "hermes-pilot-live-phase1-red: ALL PASS"; exit 0; }
echo "hermes-pilot-live-phase1-red: $fails FAILED (expected before Phase 1 fixes)"; exit 1
