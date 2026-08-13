#!/usr/bin/env bash
# Disposable root integration test: loopback-only netns -> CONNECT FD -> unprivileged host dial.
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
if [ "$(id -u)" != 0 ] || ! command -v ip >/dev/null 2>&1; then
  echo "provider-network-root: SKIP (root and iproute2 required)"
  exit 0
fi

NS="recursion-provider-test-$$"
UNIT="recursion-provider-test-proxy-$$.service"
TMP="$(mktemp -d)"
proxy_pid=""; proxy_unit=0; upstream_pid=""
cleanup(){
  if [ "$proxy_unit" = 1 ]; then
    systemctl stop "$UNIT" >/dev/null 2>&1 || true
    systemctl reset-failed "$UNIT" >/dev/null 2>&1 || true
  else
    [ -z "$proxy_pid" ] || kill "$proxy_pid" >/dev/null 2>&1 || true
  fi
  [ -z "$upstream_pid" ] || kill "$upstream_pid" >/dev/null 2>&1 || true
  wait "$proxy_pid" >/dev/null 2>&1 || true
  wait "$upstream_pid" >/dev/null 2>&1 || true
  ip netns delete "$NS" >/dev/null 2>&1 || true
  rm -rf "$TMP"
}
trap cleanup EXIT

ip netns add "$NS"
ip -n "$NS" link set lo up
chmod 0444 "/run/netns/$NS"

# Root-owned local echo fixture represents the provider side of the tunnel.
python3 - "$TMP/port" <<'PY' &
import socket, sys
s = socket.socket()
s.bind(("127.0.0.1", 0))
s.listen()
open(sys.argv[1], "w", encoding="ascii").write(str(s.getsockname()[1]))
while True:
    c, _ = s.accept()
    with c:
        while data := c.recv(4096):
            c.sendall(data)
PY
upstream_pid=$!
for _ in $(seq 1 50); do [ -s "$TMP/port" ] && break; sleep 0.05; done
[ -s "$TMP/port" ] || { echo "provider-network-root: fixture failed" >&2; exit 1; }
port="$(cat "$TMP/port")"

if command -v systemd-run >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
  systemd-run --quiet --collect --unit "$UNIT" --service-type=exec \
    --property NoNewPrivileges=yes \
    --property 'CapabilityBoundingSet=CAP_SYS_ADMIN CAP_SETUID CAP_SETGID CAP_SETPCAP' \
    --property 'AmbientCapabilities=CAP_SYS_ADMIN CAP_SETUID CAP_SETGID CAP_SETPCAP' \
    --property PrivateDevices=yes --property ProtectSystem=strict --property ProtectHome=yes \
    --property ProtectKernelTunables=yes --property ProtectKernelModules=yes \
    --property ProtectKernelLogs=yes --property ProtectControlGroups=yes \
    --property ProtectClock=yes --property ProtectHostname=yes \
    --property ProtectProc=invisible --property ProcSubset=pid \
    --property 'RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6' \
    --property RestrictSUIDSGID=yes --property LockPersonality=yes \
    --property MemoryDenyWriteExecute=yes --property RemoveIPC=yes --property UMask=0077 \
    --property "StandardOutput=append:$TMP/proxy.out" \
    --property "StandardError=append:$TMP/proxy.err" \
    --setenv RECURSION_PROVIDER_PROXY_TEST=1 \
    python3 "$ROOT/scripts/provider-connect-proxy.py" serve \
      --namespace "/run/netns/$NS" --listen-port 18080 \
      --allow "fixture.invalid:$port" --resolve "fixture.invalid=127.0.0.1" \
      --drop-user nobody
  proxy_unit=1
else
  RECURSION_PROVIDER_PROXY_TEST=1 python3 "$ROOT/scripts/provider-connect-proxy.py" serve \
    --namespace "/run/netns/$NS" --listen-port 18080 \
    --allow "fixture.invalid:$port" --resolve "fixture.invalid=127.0.0.1" \
    --drop-user nobody >"$TMP/proxy.out" 2>"$TMP/proxy.err" &
  proxy_pid=$!
fi

for _ in $(seq 1 50); do
  ip netns exec "$NS" python3 - <<'PY' >/dev/null 2>&1 && break || true
import socket
with socket.create_connection(("127.0.0.1", 18080), timeout=.2) as s:
    s.sendall(b"CONNECT denied.invalid:443 HTTP/1.1\r\n\r\n")
    assert s.recv(64).startswith(b"HTTP/1.1 403")
PY
  sleep 0.05
done

if [ "$proxy_unit" = 1 ]; then
  proxy_pid="$(systemctl show --property MainPID --value "$UNIT")"
fi
[ -n "$proxy_pid" ] && [ "$proxy_pid" != 0 ] && [ -r "/proc/$proxy_pid/status" ]
awk '$1 == "Uid:" { exit !($2 != 0 && $2 == $3 && $3 == $4 && $4 == $5) }' "/proc/$proxy_pid/status"
grep -Eq '^CapEff:[[:space:]]+0+$' "/proc/$proxy_pid/status"
grep -Eq '^NoNewPrivs:[[:space:]]+1$' "/proc/$proxy_pid/status"

PROVIDER_FIXTURE_PORT="$port" ip netns exec "$NS" python3 - <<'PY'
import os, socket
port = int(os.environ["PROVIDER_FIXTURE_PORT"])

def client_hello(sni):
    host = sni.encode("ascii")
    server_name = b"\x00" + len(host).to_bytes(2, "big") + host
    ext = (0).to_bytes(2, "big") + (len(server_name) + 2).to_bytes(2, "big") \
        + len(server_name).to_bytes(2, "big") + server_name
    body = (0x0303).to_bytes(2, "big") + b"\x00" * 32 + b"\x00" \
        + (2).to_bytes(2, "big") + b"\x13\x01" + b"\x01\x00" \
        + len(ext).to_bytes(2, "big") + ext
    handshake = b"\x01" + len(body).to_bytes(3, "big") + body
    return b"\x16\x03\x01" + len(handshake).to_bytes(2, "big") + handshake

secret = b"must-not-appear-in-proxy-output"
hello = client_hello("fixture.invalid")
with socket.create_connection(("127.0.0.1", 18080), timeout=2) as s:
    request = (f"CONNECT fixture.invalid:{port} HTTP/1.1\r\n".encode()
               + b"Proxy-Authorization: " + secret + b"\r\n\r\n")
    s.sendall(request)
    response = s.recv(4096)
    assert response.startswith(b"HTTP/1.1 200"), response
    s.sendall(hello)
    echoed = b""
    while len(echoed) < len(hello):
        block = s.recv(4096)
        assert block, "tunnel closed before the pinned ClientHello was echoed"
        echoed += block
    assert echoed == hello, echoed
with socket.create_connection(("127.0.0.1", 18080), timeout=2) as s:
    s.sendall(f"CONNECT fixture.invalid:{port} HTTP/1.1\r\n\r\n".encode())
    assert s.recv(64).startswith(b"HTTP/1.1 200")
    s.sendall(client_hello("wrong.example.com"))
    assert s.recv(64) == b"", "wrong-SNI tunnel was not failed closed"
with socket.create_connection(("127.0.0.1", 18080), timeout=2) as s:
    s.sendall(f"CONNECT fixture.invalid:{port} HTTP/1.1\r\n\r\n".encode())
    assert s.recv(64).startswith(b"HTTP/1.1 200")
    s.sendall(b"not-a-tls-record")
    assert s.recv(64) == b"", "non-TLS tunnel was not failed closed"
with socket.create_connection(("127.0.0.1", 18080), timeout=2) as s:
    s.sendall(b"CONNECT example.com:443 HTTP/1.1\r\n\r\n")
    assert s.recv(64).startswith(b"HTTP/1.1 403")
try:
    socket.create_connection(("1.1.1.1", 443), timeout=.25)
except OSError:
    pass
else:
    raise AssertionError("loopback-only namespace reached host network directly")
PY

[ "$(ip -n "$NS" -o link show | wc -l)" = 1 ]
grep -q 'must-not-appear-in-proxy-output' "$TMP/proxy.out" "$TMP/proxy.err" && {
  echo "provider-network-root: proxy logged a request secret" >&2; exit 1;
}
if [ "$proxy_unit" = 1 ]; then boundary=systemd-transient; else boundary=direct; fi
echo "provider-network-root: ALL PASS ($boundary, unprivileged, zero effective capabilities)"
