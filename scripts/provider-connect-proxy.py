#!/usr/bin/env python3
"""Root-opened, privilege-dropping HTTP CONNECT proxy for one provider capability.

The listening socket is created inside a loopback-only worker network namespace.  The
process then returns to the host network namespace and permanently drops privilege
before it accepts requests or creates outbound sockets.  CONNECT metadata is never
logged, and all application traffic remains inside the end-to-end TLS tunnel.
"""

from __future__ import annotations

import argparse
import asyncio
import ctypes
import ipaddress
import json
import os
import pathlib
import re
import socket
import ssl
import stat
import sys
from collections.abc import Iterable

try:
    import pwd
except ImportError:  # Allows parser/unit tests on the Windows review workstation.
    pwd = None  # type: ignore[assignment]


CLONE_NEWNET = 0x40000000
PR_SET_NO_NEW_PRIVS = 38
MAX_REQUEST = 8192
HEADER_TIMEOUT = 5.0
CONNECT_TIMEOUT = 15.0
IDLE_TIMEOUT = 300.0
HOST_RE = re.compile(r"(?=.{1,253}\Z)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")
HEADER_RE = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")


class MalformedConnect(ValueError):
    """The client did not send one unambiguous HTTP/1.1 CONNECT request."""


class ConnectDenied(PermissionError):
    """The requested authority is not controller-authorized."""


def parse_authority(value: str) -> tuple[str, int]:
    if value.count(":") != 1 or any(ch.isspace() for ch in value):
        raise ValueError("authority must be a DNS name and explicit port")
    host, port_text = value.rsplit(":", 1)
    host = host.lower()
    if not HOST_RE.fullmatch(host) or not port_text.isascii() or not port_text.isdecimal():
        raise ValueError("authority must be a canonical DNS name and explicit port")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("IP-literal authorities are forbidden")
    port = int(port_text, 10)
    if not 1 <= port <= 65535:
        raise ValueError("authority port is out of range")
    return host, port


def parse_allowlist(values: Iterable[str]) -> set[tuple[str, int]]:
    allowed = {parse_authority(value) for value in values}
    if not allowed:
        raise ValueError("at least one provider authority is required")
    return allowed


def parse_connect_request(request: bytes, allowed: set[tuple[str, int]]) -> tuple[str, int]:
    if len(request) > MAX_REQUEST or not request.endswith(b"\r\n\r\n"):
        raise MalformedConnect("request framing is invalid")
    if request[:-4].find(b"\r\n\r\n") >= 0 or b"\x00" in request:
        raise MalformedConnect("multiple requests are forbidden")
    try:
        text = request.decode("ascii", "strict")
    except UnicodeDecodeError as exc:
        raise MalformedConnect("request is not ASCII") from exc
    lines = text[:-4].split("\r\n")
    if not lines or any("\n" in line or "\r" in line for line in lines):
        raise MalformedConnect("request line endings are invalid")
    parts = lines[0].split(" ")
    if len(parts) != 3 or any(not part for part in parts):
        raise MalformedConnect("request line is invalid")
    method, authority_text, version = parts
    if method != "CONNECT":
        raise ConnectDenied("only CONNECT is permitted")
    if version != "HTTP/1.1":
        raise MalformedConnect("only HTTP/1.1 is accepted")
    try:
        authority = parse_authority(authority_text)
    except ValueError as exc:
        raise MalformedConnect("CONNECT authority is invalid") from exc
    for line in lines[1:]:
        if not line or line[:1] in " \t" or ":" not in line:
            raise MalformedConnect("header syntax is invalid")
        name, _ = line.split(":", 1)
        if not HEADER_RE.fullmatch(name):
            raise MalformedConnect("header name is invalid")
        if name.lower() in {"content-length", "transfer-encoding"}:
            raise MalformedConnect("CONNECT bodies are forbidden")
    if authority not in allowed:
        raise ConnectDenied("authority is not allowed")
    return authority


def _libc_call(name: str, *args: object) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    result = getattr(libc, name)(*args)
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def setns(fd: int) -> None:
    _libc_call("setns", ctypes.c_int(fd), ctypes.c_int(CLONE_NEWNET))


def validate_namespace_file(path: pathlib.Path) -> None:
    if not path.is_absolute() or path.parent != pathlib.Path("/run/netns"):
        raise RuntimeError("provider namespace must be a fixed /run/netns capability")
    descriptor = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        info = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if info.st_uid != 0 or not stat.S_ISREG(info.st_mode) or info.st_mode & 0o022:
        raise RuntimeError("provider namespace is not root-owned and non-writable")


def open_listener_in_namespace(namespace: pathlib.Path, port: int) -> socket.socket:
    validate_namespace_file(namespace)
    host_fd = os.open("/proc/self/ns/net", os.O_RDONLY | os.O_CLOEXEC)
    provider_fd = os.open(namespace, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    listener: socket.socket | None = None
    entered = False
    try:
        setns(provider_fd)
        entered = True
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", port))
        listener.listen(128)
        listener.setblocking(False)
    finally:
        if entered:
            try:
                setns(host_fd)
            except Exception:
                if listener is not None:
                    listener.close()
                os._exit(97)
        os.close(provider_fd)
        os.close(host_fd)
    if listener is None:
        raise RuntimeError("provider listener was not created")
    return listener


def drop_privileges(user_name: str) -> None:
    if pwd is None:
        raise RuntimeError("POSIX account support is required")
    if os.geteuid() != 0:
        raise RuntimeError("provider proxy must begin as root")
    account = pwd.getpwnam(user_name)
    if account.pw_uid == 0 or account.pw_gid == 0:
        raise RuntimeError("provider proxy identity must be unprivileged")
    os.setgroups([])
    os.setgid(account.pw_gid)
    os.setuid(account.pw_uid)
    _libc_call("prctl", ctypes.c_int(PR_SET_NO_NEW_PRIVS), ctypes.c_ulong(1), 0, 0, 0)
    if os.geteuid() == 0 or os.getegid() == 0:
        raise RuntimeError("provider proxy failed to drop privilege")


async def _pipe(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while True:
            data = await asyncio.wait_for(reader.read(65536), timeout=IDLE_TIMEOUT)
            if not data:
                break
            writer.write(data)
            await writer.drain()
    except (asyncio.TimeoutError, ConnectionError, OSError):
        pass
    finally:
        try:
            writer.write_eof()
        except (AttributeError, ConnectionError, OSError):
            pass


class ConnectProxy:
    def __init__(
        self,
        allowed: set[tuple[str, int]],
        resolutions: dict[str, str],
        concurrency: int,
    ) -> None:
        self.allowed = allowed
        self.resolutions = resolutions
        self.concurrency = concurrency
        self.active = 0

    async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        upstream_writer: asyncio.StreamWriter | None = None
        if self.active >= self.concurrency:
            writer.write(b"HTTP/1.1 503 Service Unavailable\r\nConnection: close\r\n\r\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()
            return
        self.active += 1
        try:
            try:
                request = await asyncio.wait_for(reader.readuntil(b"\r\n\r\n"), HEADER_TIMEOUT)
                host, port = parse_connect_request(request, self.allowed)
            except ConnectDenied:
                writer.write(b"HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n")
                await writer.drain()
                return
            except (MalformedConnect, asyncio.IncompleteReadError, asyncio.LimitOverrunError, asyncio.TimeoutError):
                writer.write(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n")
                await writer.drain()
                return
            destination = self.resolutions.get(host, host)
            try:
                upstream_reader, upstream_writer = await asyncio.wait_for(
                    asyncio.open_connection(destination, port), CONNECT_TIMEOUT
                )
            except (asyncio.TimeoutError, OSError):
                writer.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n")
                await writer.drain()
                return
            writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await writer.drain()
            await asyncio.gather(
                _pipe(reader, upstream_writer),
                _pipe(upstream_reader, writer),
            )
        except (ConnectionError, OSError):
            pass
        finally:
            self.active -= 1
            if upstream_writer is not None:
                upstream_writer.close()
                try:
                    await upstream_writer.wait_closed()
                except (ConnectionError, OSError):
                    pass
            writer.close()
            try:
                await writer.wait_closed()
            except (ConnectionError, OSError):
                pass


async def run_server(listener: socket.socket, proxy: ConnectProxy) -> None:
    server = await asyncio.start_server(proxy.handle, sock=listener, limit=MAX_REQUEST)
    async with server:
        await server.serve_forever()


def parse_resolutions(values: Iterable[str], namespace: pathlib.Path) -> dict[str, str]:
    values = list(values)
    if not values:
        return {}
    if os.environ.get("RECURSION_PROVIDER_PROXY_TEST") != "1" or not namespace.name.startswith("recursion-provider-test-"):
        raise ValueError("resolver overrides are restricted to disposable integration tests")
    result: dict[str, str] = {}
    for value in values:
        if value.count("=") != 1:
            raise ValueError("resolver override is invalid")
        host, address = value.split("=", 1)
        canonical, _ = parse_authority(f"{host}:1")
        socket.inet_pton(socket.AF_INET, address)
        result[canonical] = address
    return result


def namespace_inventory() -> dict[str, object]:
    interfaces = sorted(name for _, name in socket.if_nameindex())
    routes = []
    route_file = pathlib.Path("/proc/net/route")
    if route_file.exists():
        routes = [line for line in route_file.read_text().splitlines()[1:] if line.strip()]
    return {"interfaces": interfaces, "ipv4_routes": len(routes)}


def proxy_response(port: int, authority: str) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
        client.sendall(f"CONNECT {authority} HTTP/1.1\r\nHost: {authority}\r\n\r\n".encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response and len(response) <= 4096:
            block = client.recv(4096)
            if not block:
                break
            response += block
        return response


def probe_namespace(namespace: pathlib.Path, port: int, authority: tuple[str, int], live: bool) -> dict[str, object]:
    validate_namespace_file(namespace)
    host_fd = os.open("/proc/self/ns/net", os.O_RDONLY | os.O_CLOEXEC)
    provider_fd = os.open(namespace, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    result: dict[str, object] = {}
    try:
        setns(provider_fd)
        inventory = namespace_inventory()
        if inventory != {"interfaces": ["lo"], "ipv4_routes": 0}:
            raise RuntimeError("provider namespace is not loopback-only")
        denied = proxy_response(port, "example.com:443")
        if not denied.startswith(b"HTTP/1.1 403"):
            raise RuntimeError("provider proxy did not deny an unlisted authority")
        try:
            socket.create_connection(("1.1.1.1", 443), timeout=0.25)
        except OSError:
            pass
        else:
            raise RuntimeError("provider namespace has direct host-network egress")
        result.update(inventory)
        result["denied_authority"] = True
        result["direct_egress"] = False
        if live:
            authority_text = f"{authority[0]}:{authority[1]}"
            with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
                client.sendall(
                    f"CONNECT {authority_text} HTTP/1.1\r\nHost: {authority_text}\r\n\r\n".encode("ascii")
                )
                response = b""
                while b"\r\n\r\n" not in response and len(response) <= 4096:
                    response += client.recv(4096)
                if not response.startswith(b"HTTP/1.1 200"):
                    raise RuntimeError("provider proxy could not establish the allowed tunnel")
                context = ssl.create_default_context()
                with context.wrap_socket(client, server_hostname=authority[0]) as tls:
                    result["tls_version"] = tls.version()
            result["allowed_authority"] = authority_text
    finally:
        setns(host_fd)
        os.close(provider_fd)
        os.close(host_fd)
    return result


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    serve = commands.add_parser("serve")
    serve.add_argument("--namespace", type=pathlib.Path, required=True)
    serve.add_argument("--listen-port", type=int, default=18080)
    serve.add_argument("--allow", action="append", required=True)
    serve.add_argument("--resolve", action="append", default=[])
    serve.add_argument("--drop-user", required=True)
    serve.add_argument("--concurrency", type=int, default=16)
    probe = commands.add_parser("probe")
    probe.add_argument("--namespace", type=pathlib.Path, required=True)
    probe.add_argument("--listen-port", type=int, default=18080)
    probe.add_argument("--allow", required=True)
    probe.add_argument("--live", action="store_true")
    return parser


def main() -> int:
    args = make_parser().parse_args()
    try:
        if args.command == "serve":
            if not 1 <= args.listen_port <= 65535 or not 1 <= args.concurrency <= 128:
                raise ValueError("listener or concurrency is out of range")
            allowed = parse_allowlist(args.allow)
            resolutions = parse_resolutions(args.resolve, args.namespace)
            listener = open_listener_in_namespace(args.namespace, args.listen_port)
            drop_privileges(args.drop_user)
            asyncio.run(run_server(listener, ConnectProxy(allowed, resolutions, args.concurrency)))
            return 0
        authority = parse_authority(args.allow)
        result = probe_namespace(args.namespace, args.listen_port, authority, args.live)
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"provider-connect-proxy: {exc}", file=sys.stderr)
        return 96


if __name__ == "__main__":
    raise SystemExit(main())
