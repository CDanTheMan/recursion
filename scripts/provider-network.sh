#!/usr/bin/env bash
# Provision and prove the fixed, root-owned provider-only network capability.
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
NS=recursion-provider-only
NS_PATH="/run/netns/$NS"
PROXY_PORT=18080
PROVIDER_AUTHORITY=api.anthropic.com:443

[ "$(id -u)" = 0 ] || { echo "provider-network: root is required" >&2; exit 95; }
command -v ip >/dev/null 2>&1 || { echo "provider-network: iproute2 is required" >&2; exit 95; }

namespace_check(){
  local interfaces
  command -v nsenter >/dev/null 2>&1 \
    || { echo "provider-network: util-linux nsenter is required" >&2; return 95; }
  command -v awk >/dev/null 2>&1 \
    || { echo "provider-network: awk is required" >&2; return 95; }
  [ -e "$NS_PATH" ] && mountpoint -q "$NS_PATH" \
    || { echo "provider-network: namespace capability is absent" >&2; return 96; }
  [ "$(stat -c %u "$NS_PATH")" = 0 ] \
    && [ $((8#$(stat -c %a "$NS_PATH") & 022)) -eq 0 ] \
    || { echo "provider-network: namespace capability ownership is invalid" >&2; return 96; }
  interfaces="$(nsenter --net="$NS_PATH" -- awk -F: '
    NR > 2 { name=$1; gsub(/^[[:space:]]+|[[:space:]]+$/, "", name); print name }
  ' /proc/self/net/dev)" \
    || { echo "provider-network: namespace interfaces are unreadable" >&2; return 96; }
  [ "$interfaces" = lo ] \
    || { echo "provider-network: namespace has a non-loopback interface" >&2; return 96; }
}

case "${1:-}" in
  create)
    created=0
    if [ ! -e "$NS_PATH" ]; then
      ip netns add "$NS"
      created=1
      trap '[ "$created" = 0 ] || ip netns delete "$NS" >/dev/null 2>&1 || true' EXIT
      ip -n "$NS" link set lo up
      # nsfs fixes namespace-handle metadata and rejects chmod with EPERM;
      # namespace_check rejects any group/other-writable capability.
    fi
    namespace_check
    created=0
    ;;
  delete)
    [ ! -e "$NS_PATH" ] || ip netns delete "$NS"
    ;;
  namespace-check)
    namespace_check
    ;;
  check)
    namespace_check
    systemctl is-active --quiet recursion-provider-network.service \
      && systemctl is-active --quiet recursion-provider-proxy.service \
      || { echo "provider-network: provider services are not active" >&2; exit 96; }
    if [ "${2:-}" = --engine ] && [ -n "${3:-}" ]; then
      admission="$(python3 "$ROOT/scripts/provider-egress.py" admit-engine "$3")" \
        || { echo "provider-network: engine/provider admission refused" >&2; exit 96; }
      authority="$(python3 - "$admission" <<'PY'
import json,sys
try:
    raw=sys.argv[1]
    if len(raw.encode("utf-8")) > 2 * 1024 * 1024:
        raise ValueError("provider admission is too large")
    row=json.loads(raw, parse_constant=lambda name: (_ for _ in ()).throw(ValueError(name)))
    values=row.get("authorities") or [] if isinstance(row,dict) else []
    if not isinstance(row,dict) or not isinstance(values,list) or len(values) < 1 \
            or not isinstance(values[0],str):
        raise ValueError("provider admission has no authority")
    print(values[0])
except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError):
    raise SystemExit(2)
PY
      )" || { echo "provider-network: provider admission had no authority" >&2; exit 96; }
    elif [ -z "${2:-}" ]; then
      # Explicit v1 compatibility path: only callers without a Phase 4 assignment may use the
      # historical Anthropic capability. Phase 4 workers must always supply --engine.
      authority="$PROVIDER_AUTHORITY"
    else
      echo "provider-network: check usage is check [--engine ENGINE]" >&2; exit 96
    fi
    python3 "$ROOT/scripts/provider-connect-proxy.py" probe \
      --namespace "$NS_PATH" --listen-port "$PROXY_PORT" --allow "$authority"
    ;;
  probe)
    namespace_check
    systemctl is-active --quiet recursion-provider-network.service \
      && systemctl is-active --quiet recursion-provider-proxy.service \
      || { echo "provider-network: provider services are not active" >&2; exit 96; }
    if [ "${2:-}" = --engine ] && [ -n "${3:-}" ]; then
      authority="$(python3 "$ROOT/scripts/provider-egress.py" admit-engine "$3" | python3 -c \
        'import json,sys
try:
    raw=sys.stdin.buffer.read(2*1024*1024+1)
    if len(raw)>2*1024*1024: raise ValueError("provider admission is too large")
    row=json.loads(raw.decode("utf-8","strict"),parse_constant=lambda n: (_ for _ in ()).throw(ValueError(n)))
    values=row.get("authorities") or [] if isinstance(row,dict) else []
    if not isinstance(row,dict) or not isinstance(values,list) or not values or not isinstance(values[0],str): raise ValueError("provider admission has no authority")
    print(values[0])
except (json.JSONDecodeError,ValueError,TypeError,UnicodeError,OverflowError,RecursionError): raise SystemExit(2)')" \
        || { echo "provider-network: engine/provider admission refused" >&2; exit 96; }
    elif [ -z "${2:-}" ]; then
      authority="$PROVIDER_AUTHORITY"
    else
      echo "provider-network: probe usage is probe [--engine ENGINE]" >&2; exit 96
    fi
    [ -n "${RECURSION_PROVIDER_PROBE_TOKEN:-}" ] \
      && [ -n "${RECURSION_PROVIDER_PROBE_IDENTITY:-}" ] \
      || { echo "provider-network: live probe requires a short-lived assignment capability" >&2; exit 96; }
    python3 "$ROOT/scripts/provider-connect-proxy.py" probe --live \
      --namespace "$NS_PATH" --listen-port "$PROXY_PORT" --allow "$authority"
    ;;
  *)
    echo "usage: provider-network.sh {create|delete|namespace-check|check|probe} [--engine ENGINE]" >&2
    exit 2
    ;;
esac
