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
import base64
import binascii
import ctypes
import hashlib
import hmac
import ipaddress
import json
import os
import pathlib
import re
import secrets
import socket
import ssl
import stat
import sys
import time
from collections.abc import Iterable

try:
    from provider_contract import enabled_allowlist, enabled_profile_names, load_profile, parse_authority
except ModuleNotFoundError:  # importlib-based hermetic tests load this file by path.
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from provider_contract import enabled_allowlist, enabled_profile_names, load_profile, parse_authority

try:
    import pwd
except ImportError:  # Allows parser/unit tests on the Windows review workstation.
    pwd = None  # type: ignore[assignment]


CLONE_NEWNET = 0x40000000
PR_SET_NO_NEW_PRIVS = 38
MAX_REQUEST = 8192
HEADER_TIMEOUT = 5.0
CONNECT_TIMEOUT = 15.0
CLIENT_HELLO_TIMEOUT = 15.0
IDLE_TIMEOUT = 300.0
CAPABILITY_TTL_SECONDS = 900
CAPABILITY_CLOCK_SKEW_SECONDS = 30
MAX_CLIENT_HELLO = 65536
TLS_HANDSHAKE = 0x16
TLS_CLIENT_HELLO = 0x01
SERVER_NAME_EXTENSION = 0x0000
HEADER_RE = re.compile(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+\Z")
# Control-plane identifiers are 128 characters; the separator and 64-character contract digest
# make the generated assignment identity at most 193 characters.  Keep a round 255-character
# ceiling while remaining entirely safe as a Basic userinfo username.
ASSIGNMENT_RE = re.compile(r"[A-Za-z0-9._-]{1,255}\Z")


class MalformedConnect(ValueError):
    """The client did not send one unambiguous HTTP/1.1 CONNECT request."""


class ConnectDenied(PermissionError):
    """The requested authority is not controller-authorized."""


class MalformedClientHello(ValueError):
    """The tunnel's first bytes are not one pinned TLS ClientHello."""


class ClientHelloMismatch(ValueError):
    """The ClientHello SNI does not match the CONNECT authority."""


def issue_capability(profile: str, assignment: str, secret: bytes, *,
                     now: int | None = None, ttl: int = CAPABILITY_TTL_SECONDS,
                     jti: str | None = None) -> str:
    """Create an opaque, signed transport capability for exactly one assignment/profile."""
    if len(secret) < 32:
        raise ValueError("capability key is too short")
    if not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", profile) \
            or not ASSIGNMENT_RE.fullmatch(assignment):
        raise ValueError("capability identity is invalid")
    issued = int(time.time()) if now is None else int(now)
    if not 1 <= ttl <= 86400:
        raise ValueError("capability lifetime is invalid")
    nonce = jti or secrets.token_urlsafe(24)
    if not re.fullmatch(r"[A-Za-z0-9_-]{22,128}", nonce):
        raise ValueError("capability nonce is invalid")
    payload = json.dumps({"assignment": assignment, "profile": profile,
                          "iat": issued, "nbf": issued,
                          "exp": issued + ttl, "jti": nonce},
                         sort_keys=True, separators=(",", ":")).encode("ascii")
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=")
    signature = hmac.new(secret, encoded, hashlib.sha256).digest()
    return encoded.decode("ascii") + "." + base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")


def verify_capability(token: str, secret: bytes, *, now: int | None = None,
                      revoked_jtis: set[str] | None = None) -> dict[str, str]:
    try:
        encoded, signed = token.split(".", 1)
        expected = hmac.new(secret, encoded.encode("ascii"), hashlib.sha256).digest()
        observed = base64.urlsafe_b64decode(signed + "=" * (-len(signed) % 4))
        if not hmac.compare_digest(observed, expected):
            raise ValueError
        payload = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
    except (ValueError, UnicodeError, json.JSONDecodeError, TypeError, binascii.Error):
        raise ConnectDenied("transport capability is invalid") from None
    if not isinstance(payload, dict) or not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", str(payload.get("profile", ""))) \
            or not ASSIGNMENT_RE.fullmatch(str(payload.get("assignment", ""))) \
            or not re.fullmatch(r"[A-Za-z0-9_-]{22,128}", str(payload.get("jti", ""))):
        raise ConnectDenied("transport capability is invalid")
    try:
        issued = int(payload["iat"]); not_before = int(payload["nbf"]); expires = int(payload["exp"])
    except (KeyError, TypeError, ValueError):
        raise ConnectDenied("transport capability is invalid") from None
    current = int(time.time()) if now is None else int(now)
    if issued != not_before or expires <= issued or expires - issued > 86400 \
            or not_before > current + CAPABILITY_CLOCK_SKEW_SECONDS \
            or expires < current - CAPABILITY_CLOCK_SKEW_SECONDS:
        raise ConnectDenied("transport capability is expired or not yet valid")
    jti = str(payload["jti"])
    if revoked_jtis is not None and jti in revoked_jtis:
        raise ConnectDenied("transport capability has been revoked")
    return {"profile": str(payload["profile"]), "assignment": str(payload["assignment"]), "jti": jti}


def load_revoked_jtis(path: pathlib.Path | None) -> set[str]:
    """Load only a root-owned, mode-0600 revocation set from ephemeral runtime state."""
    if path is None:
        return set()
    if path.is_symlink() or not path.is_file():
        raise ConnectDenied("capability revocation state is unavailable")
    info = path.stat()
    if stat.S_IMODE(info.st_mode) != 0o600 or (hasattr(os, "geteuid") and os.geteuid() == 0 and info.st_uid != 0):
        raise ConnectDenied("capability revocation state ownership/mode is unsafe")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ConnectDenied("capability revocation state is invalid") from None
    revoked = value.get("revoked_jtis", []) if isinstance(value, dict) else None
    if not isinstance(revoked, list) or any(not isinstance(item, str) or
                                             not re.fullmatch(r"[A-Za-z0-9_-]{22,128}", item)
                                             for item in revoked):
        raise ConnectDenied("capability revocation state is invalid")
    return set(revoked)


def parse_allowlist(values: Iterable[str]) -> set[tuple[str, int]]:
    allowed = {parse_authority(value) for value in values}
    if not allowed:
        raise ValueError("at least one provider authority is required")
    return allowed


def parse_connect_request(
    request: bytes,
    allowed: set[tuple[str, int]] | None = None,
    *,
    capability_key: bytes | None = None,
    profile_authorities: dict[str, set[tuple[str, int]]] | None = None,
    active_assignment: str | None = None,
    revoked_jtis: set[str] | None = None,
) -> tuple[str, int]:
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
    proxy_authorization: str | None = None
    active_identity: str | None = None
    for line in lines[1:]:
        if not line or line[:1] in " \t" or ":" not in line:
            raise MalformedConnect("header syntax is invalid")
        name, _ = line.split(":", 1)
        if not HEADER_RE.fullmatch(name):
            raise MalformedConnect("header name is invalid")
        if name.lower() in {"content-length", "transfer-encoding"}:
            raise MalformedConnect("CONNECT bodies are forbidden")
        if name.lower() == "proxy-authorization":
            if proxy_authorization is not None:
                raise MalformedConnect("duplicate proxy authorization")
            proxy_authorization = line.split(":", 1)[1].strip()
    if capability_key is not None:
        if profile_authorities is None or not proxy_authorization:
            raise ConnectDenied("transport authorization is required")
        if proxy_authorization.startswith("Basic "):
            try:
                basic = base64.b64decode(proxy_authorization[6:], validate=True).decode("ascii")
                active_identity, token = basic.split(":", 1)
            except (ValueError, UnicodeError, binascii.Error):
                raise ConnectDenied("transport authorization is invalid") from None
        else:
            raise ConnectDenied("Basic assignment identity is required")
        if not active_identity or active_identity == "assignment":
            raise ConnectDenied("active assignment identity is required")
        capability = verify_capability(token, capability_key, revoked_jtis=revoked_jtis)
        if active_identity != capability["assignment"]:
            raise ConnectDenied("transport capability identity does not match its assignment")
        if active_assignment is not None and capability["assignment"] != active_assignment:
            raise ConnectDenied("transport capability is not bound to the active assignment")
        allowed = profile_authorities.get(capability["profile"])
        if allowed is None:
            raise ConnectDenied("transport profile is not admitted")
    if allowed is None or authority not in allowed:
        raise ConnectDenied("authority is not allowed")
    return authority


def _u16(data: bytes, offset: int) -> int:
    return (data[offset] << 8) | data[offset + 1]


def parse_client_hello(data: bytes) -> tuple[str, int] | None:
    """Return ``(sni, consumed)`` for a complete ClientHello, or ``None`` if more bytes are needed.

    Raises ``MalformedClientHello`` the moment the accumulated bytes cannot be a TLS ClientHello,
    so the proxy fails closed on non-TLS input, a non-ClientHello handshake, truncation, or
    oversize. ``sni`` is lower-cased; no payload byte is ever reflected into an error message.
    """
    if len(data) < 5:
        return None
    if data[0] != TLS_HANDSHAKE or data[1] != 3 or data[2] not in (1, 2, 3, 4):
        raise MalformedClientHello("first record is not a supported TLS handshake")
    handshake = b""
    pos = 0
    while True:
        if len(data) < pos + 5:
            return None
        if data[pos] != TLS_HANDSHAKE:
            raise MalformedClientHello("interleaved non-handshake record")
        record_len = _u16(data, pos + 3)
        if record_len == 0:
            raise MalformedClientHello("empty TLS record")
        if len(data) < pos + 5 + record_len:
            return None
        handshake += data[pos + 5:pos + 5 + record_len]
        pos += 5 + record_len
        if len(handshake) > MAX_CLIENT_HELLO:
            raise MalformedClientHello("ClientHello exceeds the 64 KiB bound")
        if len(handshake) >= 4:
            message_len = int.from_bytes(handshake[1:4], "big")
            if message_len == 0:
                raise MalformedClientHello("empty handshake message")
            if 4 + message_len > MAX_CLIENT_HELLO:
                raise MalformedClientHello("handshake message exceeds the 64 KiB bound")
            if len(handshake) >= 4 + message_len:
                break
    if handshake[0] != TLS_CLIENT_HELLO:
        raise MalformedClientHello("first handshake message is not a ClientHello")
    body = handshake[4:4 + int.from_bytes(handshake[1:4], "big")]
    return _client_hello_sni(body), pos


def _client_hello_sni(body: bytes) -> str:
    if len(body) < 2 + 32 + 1:
        raise MalformedClientHello("truncated ClientHello")
    pos = 2 + 32
    session_len = body[pos]
    pos += 1
    if len(body) < pos + session_len:
        raise MalformedClientHello("truncated session id")
    pos += session_len
    if len(body) < pos + 2:
        raise MalformedClientHello("truncated cipher suites")
    cipher_len = _u16(body, pos)
    pos += 2
    if len(body) < pos + cipher_len:
        raise MalformedClientHello("truncated cipher suites")
    pos += cipher_len
    if len(body) < pos + 1:
        raise MalformedClientHello("truncated compression methods")
    compression_len = body[pos]
    pos += 1
    if len(body) < pos + compression_len:
        raise MalformedClientHello("truncated compression methods")
    pos += compression_len
    if len(body) < pos + 2:
        raise MalformedClientHello("ClientHello has no extensions")
    extensions_len = _u16(body, pos)
    pos += 2
    end = pos + extensions_len
    if len(body) < end:
        raise MalformedClientHello("truncated extensions")
    while pos < end:
        if len(body) < pos + 4:
            raise MalformedClientHello("truncated extension")
        ext_type = _u16(body, pos)
        ext_len = _u16(body, pos + 2)
        pos += 4
        if len(body) < pos + ext_len:
            raise MalformedClientHello("truncated extension")
        if ext_type == SERVER_NAME_EXTENSION:
            return _parse_server_name(body[pos:pos + ext_len])
        pos += ext_len
    raise MalformedClientHello("ClientHello lacks a server_name extension")


def _parse_server_name(data: bytes) -> str:
    if len(data) < 2:
        raise MalformedClientHello("truncated server_name extension")
    list_len = _u16(data, 0)
    if len(data) < 2 + list_len:
        raise MalformedClientHello("truncated server_name list")
    pos = 2
    end = 2 + list_len
    host_name: str | None = None
    while pos < end:
        if len(data) < pos + 3:
            raise MalformedClientHello("truncated server name")
        name_type = data[pos]
        name_len = _u16(data, pos + 1)
        pos += 3
        if len(data) < pos + name_len:
            raise MalformedClientHello("truncated server name value")
        value = data[pos:pos + name_len]
        pos += name_len
        if name_type == 0:
            try:
                host_name = value.decode("ascii", "strict")
            except UnicodeDecodeError as exc:
                raise MalformedClientHello("server_name is not ASCII") from exc
    if host_name is None:
        raise MalformedClientHello("server_name extension has no host_name")
    if not host_name or "\x00" in host_name or len(host_name) > 253:
        raise MalformedClientHello("server_name is invalid")
    return host_name.lower()


async def read_client_hello(reader: asyncio.StreamReader, expected_sni: str) -> tuple[bytes, bytes]:
    """Read and pin the client's TLS ClientHello to the CONNECT authority, forwarding nothing else.

    Returns ``(initial, trailing)`` where ``initial`` is the complete ClientHello record stream and
    ``trailing`` is any already-read bytes beyond it (normally empty). Raises
    ``MalformedClientHello`` or ``ClientHelloMismatch`` to fail closed before any tunnel payload is
    forwarded.
    """
    data = b""
    while True:
        chunk = await asyncio.wait_for(reader.read(4096), CLIENT_HELLO_TIMEOUT)
        if not chunk:
            raise MalformedClientHello("connection closed before a TLS ClientHello")
        data += chunk
        parsed = parse_client_hello(data)
        if parsed is None:
            if len(data) > MAX_CLIENT_HELLO:
                raise MalformedClientHello("ClientHello exceeds the 64 KiB bound")
            continue
        sni, consumed = parsed
        if sni != expected_sni:
            raise ClientHelloMismatch()
        return data[:consumed], data[consumed:]


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


def forbidden_destination(address: str) -> bool:
    """Reject every non-public destination class before a socket is created."""
    try:
        value = ipaddress.ip_address(address)
    except ValueError:
        return True
    return not value.is_global or value.is_private or value.is_loopback or value.is_link_local \
        or value.is_reserved or value.is_multicast or value.is_unspecified


def resolve_approved_addresses(
    host: str, port: int, overrides: dict[str, str] | None = None,
) -> list[tuple[int, int, int, tuple[object, ...], str]]:
    """Resolve once, reject unsafe answers, and return the exact peer set for dialing."""
    override = (overrides or {}).get(host)
    allow_test_private = bool(override) and os.environ.get("RECURSION_PROVIDER_PROXY_TEST") == "1"
    if override:
        infos = [(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", (override, port))]
    else:
        try:
            infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ConnectDenied("destination resolution failed") from exc
    approved: list[tuple[int, int, int, tuple[object, ...], str]] = []
    seen: set[tuple[int, str]] = set()
    for family, socktype, proto, _, sockaddr in infos:
        address = str(sockaddr[0])
        if (family, address) in seen:
            continue
        if forbidden_destination(address) and not allow_test_private:
            raise ConnectDenied("destination resolves to a forbidden address")
        seen.add((family, address))
        approved.append((family, socktype, proto, tuple(sockaddr), address))
    if not approved:
        raise ConnectDenied("destination has no approved addresses")
    return approved


async def open_approved_connection(
    destinations: list[tuple[int, int, int, tuple[object, ...], str]], port: int,
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    del port  # The port is already part of each approved sockaddr.
    loop = asyncio.get_running_loop()
    last_error: OSError | None = None
    for family, socktype, proto, sockaddr, approved_ip in destinations:
        sock = socket.socket(family, socktype, proto)
        sock.setblocking(False)
        try:
            await asyncio.wait_for(loop.sock_connect(sock, sockaddr), CONNECT_TIMEOUT)
            peer = sock.getpeername()
            connected_ip = str(peer[0])
            if connected_ip != approved_ip or forbidden_destination(connected_ip) and \
                    os.environ.get("RECURSION_PROVIDER_PROXY_TEST") != "1":
                raise ConnectDenied("connected peer is outside the approved DNS answer")
            return await asyncio.open_connection(sock=sock)
        except ConnectDenied:
            sock.close()
            raise
        except (asyncio.TimeoutError, OSError) as exc:
            last_error = exc
            sock.close()
    raise OSError("all approved upstream addresses refused the connection") from last_error


class ConnectProxy:
    def __init__(
        self,
        allowed: set[tuple[str, int]],
        resolutions: dict[str, str],
        concurrency: int,
        capability_key: bytes | None = None,
        profile_authorities: dict[str, set[tuple[str, int]]] | None = None,
        active_assignment: str | None = None,
        revoked_jtis: set[str] | None = None,
    ) -> None:
        self.allowed = allowed
        self.resolutions = resolutions
        self.concurrency = concurrency
        self.capability_key = capability_key
        self.profile_authorities = profile_authorities
        self.active_assignment = active_assignment
        self.revoked_jtis = revoked_jtis or set()
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
                host, port = parse_connect_request(
                    request, self.allowed, capability_key=self.capability_key,
                    profile_authorities=self.profile_authorities,
                    active_assignment=self.active_assignment,
                    revoked_jtis=self.revoked_jtis,
                )
            except ConnectDenied:
                writer.write(b"HTTP/1.1 403 Forbidden\r\nConnection: close\r\n\r\n")
                await writer.drain()
                return
            except (MalformedConnect, asyncio.IncompleteReadError, asyncio.LimitOverrunError, asyncio.TimeoutError):
                writer.write(b"HTTP/1.1 400 Bad Request\r\nConnection: close\r\n\r\n")
                await writer.drain()
                return
            destinations = resolve_approved_addresses(host, port, self.resolutions)
            try:
                upstream_reader, upstream_writer = await open_approved_connection(
                    destinations, port
                )
            except (asyncio.TimeoutError, OSError):
                writer.write(b"HTTP/1.1 502 Bad Gateway\r\nConnection: close\r\n\r\n")
                await writer.drain()
                return
            writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await writer.drain()
            initial, trailing = await read_client_hello(reader, host)
            if initial:
                upstream_writer.write(initial)
            if trailing:
                upstream_writer.write(trailing)
            await upstream_writer.drain()
            await asyncio.gather(
                _pipe(reader, upstream_writer),
                _pipe(upstream_reader, writer),
            )
        except (MalformedClientHello, ClientHelloMismatch):
            pass
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
        if forbidden_destination(address) and os.environ.get("RECURSION_PROVIDER_PROXY_TEST") != "1":
            raise ValueError("resolver override is a forbidden destination")
        result[canonical] = address
    return result


def namespace_inventory() -> dict[str, object]:
    interfaces = sorted(name for _, name in socket.if_nameindex())
    routes = []
    route_file = pathlib.Path("/proc/net/route")
    if route_file.exists():
        routes = [line for line in route_file.read_text().splitlines()[1:] if line.strip()]
    return {"interfaces": interfaces, "ipv4_routes": len(routes)}


def _proxy_authorization(capability_token: str | None, capability_identity: str | None) -> str:
    if capability_token is None and capability_identity is None:
        return ""
    if capability_token is None or capability_identity is None or not ASSIGNMENT_RE.fullmatch(capability_identity):
        raise ValueError("probe capability requires an exact assignment identity and token")
    basic = base64.b64encode(f"{capability_identity}:{capability_token}".encode("ascii")).decode("ascii")
    return f"Proxy-Authorization: Basic {basic}\r\n"


def proxy_response(port: int, authority: str, capability_token: str | None = None,
                   capability_identity: str | None = None) -> bytes:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
        authorization = _proxy_authorization(capability_token, capability_identity)
        client.sendall(
            f"CONNECT {authority} HTTP/1.1\r\nHost: {authority}\r\n{authorization}\r\n".encode("ascii")
        )
        response = b""
        while b"\r\n\r\n" not in response and len(response) <= 4096:
            block = client.recv(4096)
            if not block:
                break
            response += block
        return response


def probe_namespace(namespace: pathlib.Path, port: int, authority: tuple[str, int], live: bool,
                    capability_token: str | None = None,
                    capability_identity: str | None = None) -> dict[str, object]:
    validate_namespace_file(namespace)
    host_fd = os.open("/proc/self/ns/net", os.O_RDONLY | os.O_CLOEXEC)
    provider_fd = os.open(namespace, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    result: dict[str, object] = {}
    try:
        setns(provider_fd)
        inventory = namespace_inventory()
        if inventory != {"interfaces": ["lo"], "ipv4_routes": 0}:
            raise RuntimeError("provider namespace is not loopback-only")
        denied = proxy_response(port, "example.com:443", capability_token, capability_identity)
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
            if capability_token is None or capability_identity is None:
                raise RuntimeError("live probe requires an explicit short-lived assignment capability")
            authority_text = f"{authority[0]}:{authority[1]}"
            with socket.create_connection(("127.0.0.1", port), timeout=5) as client:
                authorization = _proxy_authorization(capability_token, capability_identity)
                client.sendall(
                    f"CONNECT {authority_text} HTTP/1.1\r\nHost: {authority_text}\r\n"
                    f"{authorization}\r\n".encode("ascii")
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
    serve.add_argument("--allow", action="append", default=[])
    serve.add_argument("--profile-dir", type=pathlib.Path)
    serve.add_argument("--profile", action="append", default=[])
    serve.add_argument("--enabled-profiles", action="store_true",
                       help="select only profiles explicitly marked enabled")
    serve.add_argument("--capability-key-file", type=pathlib.Path)
    serve.add_argument("--active-assignment")
    serve.add_argument("--capability-revocation-file", type=pathlib.Path)
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
            if args.profile_dir is not None:
                if args.allow:
                    raise ValueError("--allow cannot be combined with --profile-dir")
                if args.profile and args.enabled_profiles:
                    raise ValueError("--profile and --enabled-profiles are mutually exclusive")
                if args.enabled_profiles:
                    selected = enabled_profile_names(args.profile_dir)
                else:
                    selected = args.profile
                if not selected:
                    raise ValueError("at least one provider profile is required")
                profiles = [load_profile(args.profile_dir / f"{name}.json", name) for name in selected]
                if any(profile["namespace"] != args.namespace.name for profile in profiles):
                    raise ValueError("provider profile namespace does not match --namespace")
                if any(not profile["enabled"] for profile in profiles):
                    raise ValueError("provider egress profile is disabled")
                if args.capability_key_file is None:
                    raise ValueError("shared provider proxy requires an assignment capability key")
                key_path = args.capability_key_file
                if key_path.is_symlink() or not key_path.is_file():
                    raise ValueError("provider capability key is unavailable")
                key_info = key_path.stat()
                if key_info.st_mode & 0o077 or (
                        hasattr(os, "geteuid") and os.geteuid() == 0 and key_info.st_uid != 0):
                    raise ValueError("provider capability key ownership/mode is unsafe")
                capability_key = key_path.read_bytes()
                if len(capability_key) < 32:
                    raise ValueError("provider capability key is too short")
                profile_authorities = {
                    profile["id"]: {parse_authority(item) for item in profile["authorities"]}
                    for profile in profiles
                }
            else:
                if args.capability_key_file is not None:
                    raise ValueError("capability keys require --profile-dir")
                allowed = parse_allowlist(args.allow)
            resolutions = parse_resolutions(args.resolve, args.namespace)
            listener = open_listener_in_namespace(args.namespace, args.listen_port)
            drop_privileges(args.drop_user)
            asyncio.run(run_server(listener, ConnectProxy(
                allowed if args.profile_dir is None else set(), resolutions, args.concurrency,
                capability_key if args.profile_dir is not None else None,
                profile_authorities if args.profile_dir is not None else None,
                args.active_assignment,
                load_revoked_jtis(args.capability_revocation_file),
            )))
            return 0
        authority = parse_authority(args.allow)
        result = probe_namespace(
            args.namespace, args.listen_port, authority, args.live,
            os.environ.get("RECURSION_PROVIDER_PROBE_TOKEN"),
            os.environ.get("RECURSION_PROVIDER_PROBE_IDENTITY"),
        )
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        print(f"provider-connect-proxy: {exc}", file=sys.stderr)
        return 96


if __name__ == "__main__":
    raise SystemExit(main())
