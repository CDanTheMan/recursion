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
  [ -e "$NS_PATH" ] && mountpoint -q "$NS_PATH" \
    || { echo "provider-network: namespace capability is absent" >&2; return 96; }
  [ "$(stat -c %u "$NS_PATH")" = 0 ] \
    && [ $((8#$(stat -c %a "$NS_PATH") & 022)) -eq 0 ] \
    || { echo "provider-network: namespace capability ownership is invalid" >&2; return 96; }
  [ "$(ip -n "$NS" -o link show | wc -l)" = 1 ] \
    && ip -n "$NS" -o link show lo >/dev/null \
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
      chmod 0600 "$NS_PATH"
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
    python3 "$ROOT/scripts/provider-connect-proxy.py" probe \
      --namespace "$NS_PATH" --listen-port "$PROXY_PORT" --allow "$PROVIDER_AUTHORITY"
    ;;
  probe)
    namespace_check
    systemctl is-active --quiet recursion-provider-network.service \
      && systemctl is-active --quiet recursion-provider-proxy.service \
      || { echo "provider-network: provider services are not active" >&2; exit 96; }
    python3 "$ROOT/scripts/provider-connect-proxy.py" probe --live \
      --namespace "$NS_PATH" --listen-port "$PROXY_PORT" --allow "$PROVIDER_AUTHORITY"
    ;;
  *)
    echo "usage: provider-network.sh {create|delete|namespace-check|check|probe}" >&2
    exit 2
    ;;
esac
