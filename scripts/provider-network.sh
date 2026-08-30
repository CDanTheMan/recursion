#!/usr/bin/env bash
# Provision and prove a root-owned provider-only network capability selected by profile.
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
NS=""
NS_PATH=""
PROFILE="${RECURSION_PROVIDER_PROFILE:-}"
PROFILE_JSON=""

load_profile(){
  [ -n "$PROFILE" ] || { echo "provider-network: provider profile is required (default deny)" >&2; return 96; }
  local controller_root controller_commit
  local -a args=("$PROFILE" --provider "${RECURSION_PROVIDER_ID:-}") endpoint
  for endpoint in ${RECURSION_PROVIDER_ENDPOINTS:-}; do args+=(--endpoint "$endpoint"); done
  if [ -n "${RECURSION_CONTROLLER_ROOT:-}" ] || [ -n "${RECURSION_CONTROLLER_COMMIT:-}" ]; then
    [ -n "${RECURSION_CONTROLLER_ROOT:-}" ] && [ -n "${RECURSION_CONTROLLER_COMMIT:-}" ] \
      || { echo "provider-network: incomplete controller policy provenance" >&2; return 96; }
    controller_root="$RECURSION_CONTROLLER_ROOT"
    controller_commit="$RECURSION_CONTROLLER_COMMIT"
  else
    controller_root="$ROOT"
    controller_commit="$(git -C "$controller_root" rev-parse --verify HEAD 2>/dev/null || true)"
    [ -n "$controller_commit" ] \
      || { echo "provider-network: controller policy provenance is unavailable" >&2; return 96; }
  fi
  args+=(--controller-root "$controller_root" --controller-commit "$controller_commit")
  PROFILE_JSON="$(python3 "$ROOT/scripts/provider-egress.py" "${args[@]}" 2>/dev/null)" \
    || { echo "provider-network: provider profile is invalid or not provisioned" >&2; return 96; }
  NS="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["namespace"])' "$PROFILE_JSON")"
  NS_PATH="/run/netns/$NS"
  PROXY_PORT="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["proxy_port"])' "$PROFILE_JSON")"
}

[ "$(id -u)" = 0 ] || { echo "provider-network: root is required" >&2; exit 95; }
command -v ip >/dev/null 2>&1 || { echo "provider-network: iproute2 is required" >&2; exit 95; }

namespace_check(){
  local interfaces
  [ -n "$NS_PATH" ] || { echo "provider-network: provider profile was not loaded" >&2; return 96; }
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
    load_profile
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
    load_profile
    [ ! -e "$NS_PATH" ] || ip netns delete "$NS"
    ;;
  namespace-check)
    load_profile
    namespace_check
    ;;
  check)
    load_profile
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
      # Preserve the no-argument compatibility path while deriving its authority from
      # the authenticated profile rather than embedding a provider policy here.
      authority="$(python3 -c 'import json,sys; e=json.loads(sys.argv[1])["endpoints"]; print(e[0]+":443" if e else "")' "$PROFILE_JSON")"
      [ -n "$authority" ] || { echo "provider-network: provider profile has no authority" >&2; exit 96; }
    else
      echo "provider-network: check usage is check [--engine ENGINE]" >&2; exit 96
    fi
    python3 "$ROOT/scripts/provider-connect-proxy.py" probe \
      --namespace "$NS_PATH" --listen-port "$PROXY_PORT" --allow "$authority"
    ;;
  probe)
    load_profile
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
      authority="$(python3 -c 'import json,sys; e=json.loads(sys.argv[1])["endpoints"]; print(e[0]+":443" if e else "")' "$PROFILE_JSON")"
      [ -n "$authority" ] || { echo "provider-network: provider profile has no authority" >&2; exit 96; }
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
