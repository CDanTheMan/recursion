#!/usr/bin/env python3
"""Read-only Git authority proofs shared by Phase-8 pilot controllers.

The project checkout remains the exact measured source. Remote history is materialized only in
disposable bare storage; the measured checkout, object store, refs, and index remain untouched.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


OID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
AUTHORITY_V2_SCHEMA = "recursion-project-authority-contract/v2"
AUTHORITY_V2_RELATIONSHIPS = {"equal", "remote-descends-from-source"}
REMOTE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]{0,127}$")


class AuthorityError(RuntimeError):
    def __init__(self, message: str, code: int = 4) -> None:
        super().__init__(message)
        self.code = code


def _git_env(*, ceiling: Path | None = None) -> dict[str, str]:
    """Build a minimal environment without ambient Git, askpass, proxy, or object redirects."""
    keep = {
        "PATH", "HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "SystemRoot",
        "SYSTEMROOT", "WINDIR", "COMSPEC", "PATHEXT",
    }
    env = {key: value for key, value in os.environ.items() if key in keep}
    env.update({
        "LC_ALL": "C", "LANG": "C", "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0", "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    })
    if ceiling is not None:
        env["GIT_CEILING_DIRECTORIES"] = str(ceiling.resolve())
        env["GIT_DISCOVERY_ACROSS_FILESYSTEM"] = "0"
    return env


def _require_git_version() -> None:
    """Require the first Git release that honors GIT_CONFIG_GLOBAL isolation."""
    try:
        result = subprocess.run(
            ["git", "--version"], env=_git_env(), stdin=subprocess.DEVNULL,
            text=True, capture_output=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuthorityError("Git authority tooling is unavailable", 74) from exc
    match = re.fullmatch(
        r"git version (\d+)\.(\d+)(?:\.(\d+))?(?:\..*)?\s*", result.stdout,
    )
    version = tuple(int(part or 0) for part in match.groups()) if match else (0, 0, 0)
    if result.returncode or match is None or version < (2, 35, 2):
        raise AuthorityError("Git 2.35.2 or newer is required for isolated authority proof", 74)


def _safe_urlsplit(value: str):
    try:
        return urlsplit(value)
    except ValueError as exc:
        raise AuthorityError("project remote transport is malformed") from exc


def _is_scp_like(value: str) -> bool:
    return "://" not in value and re.fullmatch(
        r"(?:[A-Za-z0-9._-]+@)?[A-Za-z0-9][A-Za-z0-9.-]*:[^:\s][^\s]*", value,
    ) is not None


def _transport_shape(value: str, repo: Path) -> tuple[str, str]:
    """Return a normalized endpoint and one explicitly permitted Git protocol."""
    if not value or any(ord(char) < 32 or ord(char) == 127 for char in value):
        raise AuthorityError("project remote transport is absent or ambiguous")
    if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*::", value):
        raise AuthorityError("project remote helpers are not permitted")
    windows_path = re.fullmatch(r"[A-Za-z]:[\\/].+", value) is not None
    parsed = _safe_urlsplit(value)
    scp_like = not windows_path and _is_scp_like(value)
    if not windows_path and not parsed.scheme and not scp_like and not Path(value).is_absolute():
        value = str((repo / value).resolve())
        windows_path = re.fullmatch(r"[A-Za-z]:[\\/].+", value) is not None
        parsed = _safe_urlsplit(value)
        scp_like = not windows_path and _is_scp_like(value)
    try:
        parsed_port = parsed.port
    except ValueError as exc:
        raise AuthorityError("project remote transport is malformed") from exc
    if windows_path or (not parsed.scheme and not scp_like and Path(value).is_absolute()):
        return value, "file"
    if parsed.scheme == "file" and parsed.hostname in {None, "", "localhost"} \
            and parsed.username is None and parsed.password is None \
            and not parsed.query and not parsed.fragment and Path(parsed.path).is_absolute():
        return value, "file"
    if scp_like:
        return value, "ssh"
    if parsed.scheme == "ssh" and parsed.hostname and parsed.password is None \
            and not parsed.query and not parsed.fragment:
        return value, "ssh"
    if parsed.scheme == "https" and parsed.hostname and parsed.password is None \
            and not parsed.query and not parsed.fragment:
        return value, "https"
    raise AuthorityError("project remote transport is not explicitly permitted")


def _scratch_parent() -> Path:
    """Choose a fixed OS scratch root rather than attacker-controlled TMP* variables."""
    if os.name == "nt":
        system_root = Path(os.environ.get("SystemRoot") or os.environ.get("WINDIR") or "C:/Windows")
        candidates = (system_root / "Temp", Path(tempfile.gettempdir()))
    else:
        candidates = (Path("/var/tmp"), Path("/tmp"))
    for candidate in candidates:
        try:
            if candidate.is_dir() and not candidate.is_symlink():
                return candidate.resolve(strict=True)
        except OSError:
            continue
    raise AuthorityError("trusted authority scratch root is unavailable", 74)


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "--no-replace-objects", "-c", f"safe.directory={repo}",
             "-c", "core.fsmonitor=false", "-C", str(repo), *args],
            env=env or _git_env(), stdin=subprocess.DEVNULL, text=True,
            capture_output=True, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuthorityError("project Git evidence could not be measured", 74) from exc


def _exact_repository_root(value: object) -> Path:
    """Resolve one configured checkout without allowing Git to discover an ancestor repo."""
    raw = str(value or "")
    if not raw:
        raise AuthorityError("project repository path is absent")
    candidate = Path(raw)
    try:
        repo = candidate.resolve(strict=True)
    except OSError as exc:
        raise AuthorityError("project repository is unavailable", 74) from exc
    if not repo.is_dir():
        raise AuthorityError("project repository is unavailable", 74)
    marker = repo / ".git"
    try:
        if marker.is_symlink() or not (marker.is_file() or marker.is_dir()):
            raise AuthorityError("project repository root marker is absent", 74)
    except OSError as exc:
        raise AuthorityError("project repository root marker is unavailable", 74) from exc
    top = _git(repo, "rev-parse", "--path-format=absolute", "--show-toplevel")
    if top.returncode:
        raise AuthorityError("project repository root could not be measured", 74)
    try:
        measured = Path(top.stdout.strip()).resolve(strict=True)
    except OSError as exc:
        raise AuthorityError("project repository root could not be resolved", 74) from exc
    if measured != repo:
        raise AuthorityError("project repository path is not its exact Git worktree root")
    return repo


def _remote_access(config: dict, repo: Path) -> tuple[str, str, dict[str, str]]:
    """Resolve one local-config endpoint and bind an explicit transport/auth policy."""
    remote = str(config.get("remote") or "origin")
    windows_path = re.fullmatch(r"[A-Za-z]:[\\/].+", remote) is not None
    parsed_remote = _safe_urlsplit(remote)
    direct = windows_path or bool(parsed_remote.scheme) or Path(remote).is_absolute() or bool(
        _is_scp_like(remote)
    ) or remote.startswith(("./", "../", ".\\", "..\\"))
    if direct:
        transport = remote
    else:
        if not REMOTE_NAME.fullmatch(remote) or ".." in remote or "@{" in remote:
            raise AuthorityError("project named remote identity is invalid")
        resolved = _git(
            repo, "config", "--local", "--no-includes", "--null", "--get-all",
            f"remote.{remote}.url",
        )
        values = resolved.stdout.split("\0") if resolved.returncode == 0 else []
        if values and values[-1] == "":
            values.pop()
        if len(values) != 1:
            raise AuthorityError("project named remote URL is absent or ambiguous")
        transport = values[0]
    transport, protocol = _transport_shape(transport, repo)
    env = _git_env()
    if protocol == "ssh":
        key = Path(os.path.expanduser(str(config.get("deploy_key_ref") or "")))
        if not key.is_file() or key.is_symlink():
            raise AuthorityError("project remote freshness credential is absent", 74)
        env["GIT_SSH_COMMAND"] = (
            f"ssh -F none -i {shlex.quote(str(key))} -o IdentitiesOnly=yes "
            "-o BatchMode=yes -o PreferredAuthentications=publickey "
            "-o PasswordAuthentication=no -o KbdInteractiveAuthentication=no "
            "-o StrictHostKeyChecking=yes -o ProxyCommand=none -o PermitLocalCommand=no "
            "-o ClearAllForwardings=yes -o ConnectTimeout=15"
        )
    return transport, protocol, env


def _protocol_args(protocol: str) -> list[str]:
    return ["-c", "protocol.allow=never", "-c", f"protocol.{protocol}.allow=always"]


def observe_clean_source(config: dict) -> tuple[Path, str, str]:
    """Return the clean configured branch tip without consulting or mutating its remote."""
    _require_git_version()
    repo = _exact_repository_root(config.get("repo"))
    branch = str(config.get("default_branch") or "")
    if not branch:
        raise AuthorityError("project configured default branch is absent")
    head_result = _git(repo, "rev-parse", "--verify", "HEAD^{commit}")
    branch_result = _git(repo, "rev-parse", "--verify", f"refs/heads/{branch}^{{commit}}")
    current_result = _git(repo, "branch", "--show-current")
    dirty = _git(repo, "status", "--porcelain=v1", "--untracked-files=all")
    index_flags = _git(repo, "ls-files", "-v", "-z")
    if any(item.returncode for item in (
        head_result, branch_result, current_result, dirty, index_flags,
    )):
        raise AuthorityError("project repository identity or cleanliness could not be measured", 74)
    head = head_result.stdout.strip()
    branch_head = branch_result.stdout.strip()
    current = current_result.stdout.strip()
    if not OID.fullmatch(head) or current != branch or branch_head != head:
        raise AuthorityError("project repository HEAD is not the configured default-branch tip")
    if dirty.stdout.strip():
        raise AuthorityError("project repository must be exactly clean before authority is proven")
    entries = [entry for entry in index_flags.stdout.split("\0") if entry]
    if any(len(entry) < 3 or entry[1] != " " for entry in entries):
        raise AuthorityError("project repository index flags could not be measured", 74)
    if any(entry[0] == "S" or entry[0].islower() for entry in entries):
        raise AuthorityError("project repository index hides tracked worktree changes")
    _require_unrewritten_history(repo, "project")
    return repo, branch, head


def _object_format(repo: Path) -> str:
    result = _git(repo, "rev-parse", "--show-object-format")
    value = result.stdout.strip()
    if result.returncode or value not in {"sha1", "sha256"}:
        raise AuthorityError("project object format could not be proven", 74)
    return value


def _require_unrewritten_history(repo: Path, label: str) -> Path:
    common_dir_result = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if common_dir_result.returncode:
        raise AuthorityError(f"{label} common Git directory cannot be resolved", 74)
    common_dir = Path(common_dir_result.stdout.strip())
    for unsafe in (
        common_dir / "shallow", common_dir / "info" / "grafts",
        common_dir / "objects" / "info" / "alternates",
    ):
        try:
            if unsafe.is_file() and unsafe.stat().st_size:
                raise AuthorityError(f"{label} ancestry uses external or rewritten history")
        except OSError as exc:
            raise AuthorityError(f"{label} ancestry metadata cannot be inspected", 74) from exc
    return common_dir


def _authenticated_remote_observation(
    config: dict, branch: str,
) -> tuple[str, str, str, dict[str, str]]:
    """Read exactly one authenticated branch ref and retain its resolved endpoint policy."""
    repo = _exact_repository_root(config.get("repo"))
    transport, protocol, env = _remote_access(config, repo)
    expected_ref = f"refs/heads/{branch}"
    try:
        with tempfile.TemporaryDirectory(
            prefix="recursion-ls-remote-", dir=_scratch_parent(),
        ) as raw_scratch:
            scratch = Path(raw_scratch)
            scratch.chmod(0o700)
            if _inside(scratch, repo):
                raise AuthorityError("authority scratch overlaps the measured project", 74)
            isolated_env = dict(env)
            # The ceiling must be a strict ancestor of cwd.  Binding it to cwd itself
            # does not stop Git from discovering and loading a repository above scratch.
            isolated_env.update(_git_env(ceiling=scratch.parent))
            if "GIT_SSH_COMMAND" in env:
                isolated_env["GIT_SSH_COMMAND"] = env["GIT_SSH_COMMAND"]
            result = subprocess.run(
                ["git", "--no-replace-objects", *_protocol_args(protocol), "ls-remote", "--",
                 transport, expected_ref], cwd=str(scratch), env=isolated_env,
                stdin=subprocess.DEVNULL, text=True, capture_output=True,
                timeout=20, check=False,
            )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuthorityError("project remote freshness could not be measured", 74) from exc
    lines = result.stdout.splitlines()
    if result.returncode:
        raise AuthorityError("project remote freshness could not be measured", 74)
    if not lines:
        raise AuthorityError("project remote freshness returned no branch evidence", 74)
    if len(lines) != 1:
        raise AuthorityError("project remote freshness returned ambiguous branch evidence")
    oid, separator, ref = lines[0].partition("\t")
    if separator != "\t" or not OID.fullmatch(oid) or ref != expected_ref:
        raise AuthorityError("project remote freshness returned a malformed or wrong ref")
    return oid, transport, protocol, env


def authenticated_remote_head(config: dict, branch: str) -> str:
    return _authenticated_remote_observation(config, branch)[0]


def _fetch_authority_graph(
    proof: Path, branch: str, current_remote: str,
    transport: str, protocol: str, env: dict[str, str],
) -> None:
    """Materialize authenticated remote history only inside a disposable bare repo."""
    # Fetch the complete reachable graph.  A partial clone can retain promisor metadata and make
    # a later local-looking ancestry command hydrate an object through Git's ambient transport
    # path.  The bounded proof must perform its only network operation here, under the explicit
    # protocol and credential policy below.
    command_env = dict(env)
    command_env.update(_git_env(ceiling=proof.parent))
    if "GIT_SSH_COMMAND" in env:
        command_env["GIT_SSH_COMMAND"] = env["GIT_SSH_COMMAND"]
    argv = [
        "git", "--no-replace-objects", *_protocol_args(protocol), "-C", str(proof),
        "fetch", "--quiet", "--no-tags", "--no-write-fetch-head",
        "--no-auto-maintenance", "--", transport,
        f"refs/heads/{branch}:refs/heads/current",
    ]
    try:
        result = subprocess.run(
            argv, cwd=str(proof.parent), env=command_env, stdin=subprocess.DEVNULL,
            text=True, capture_output=True, timeout=120, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuthorityError("authority history could not be fetched into scratch", 74) from exc
    if result.returncode:
        raise AuthorityError("authority history could not be fetched into scratch", 74)
    fetched = _git(proof, "rev-parse", "--verify", "refs/heads/current^{commit}")
    if fetched.returncode or fetched.stdout.strip() != current_remote:
        raise AuthorityError("authenticated remote advanced during its bounded proof", 74)


def require_ancestor(repo: Path, ancestor: str, descendant: str) -> str:
    """Prove an exact, locally present commit relation with replacements and shallow history off."""
    if not OID.fullmatch(ancestor) or not OID.fullmatch(descendant):
        raise AuthorityError("project authority contains an invalid commit identity")
    _require_unrewritten_history(repo, "project")
    for label, oid in (("source", ancestor), ("remote", descendant)):
        resolved = _git(repo, "rev-parse", "--verify", f"{oid}^{{commit}}")
        if resolved.returncode or resolved.stdout.strip() != oid:
            raise AuthorityError(
                f"project {label} commit is absent from the verified local object store", 74,
            )
    relation = _git(repo, "merge-base", "--is-ancestor", ancestor, descendant)
    if relation.returncode == 1:
        raise AuthorityError("project authenticated remote tip does not descend from the exact source")
    if relation.returncode:
        raise AuthorityError("project remote ancestry could not be proven", 74)
    return "equal" if ancestor == descendant else "remote-descends-from-source"


def prove_current_remote_lineage(config: dict, source_head: str,
                                 anchored_remote_head: str | None = None,
                                 observed_repo: Path | None = None) -> tuple[str, str]:
    """Prove source <= anchor <= current in disposable storage, never the measured checkout."""
    if observed_repo is None:
        repo, branch, observed_source = observe_clean_source(config)
    else:
        repo = observed_repo
        branch = str(config.get("default_branch") or "")
        observed_source = source_head
    if observed_source != source_head:
        raise AuthorityError("project exact measured source moved after authority binding")
    current_remote, transport, protocol, env = _authenticated_remote_observation(config, branch)
    anchor = anchored_remote_head or current_remote
    object_format = _object_format(repo)
    expected_oid_length = 40 if object_format == "sha1" else 64
    if not OID.fullmatch(source_head) or not OID.fullmatch(anchor) \
            or len(source_head) != expected_oid_length or len(anchor) != expected_oid_length \
            or len(current_remote) != expected_oid_length:
        raise AuthorityError("project authority contains an invalid commit identity")
    try:
        with tempfile.TemporaryDirectory(
            prefix="recursion-authority-", dir=_scratch_parent(),
        ) as raw_proof:
            proof = Path(raw_proof)
            proof.chmod(0o700)
            if _inside(proof, repo):
                raise AuthorityError("authority scratch overlaps the measured project", 74)
            try:
                initialized = subprocess.run(
                    ["git", "init", "--bare", "--quiet", f"--object-format={object_format}",
                     str(proof)], env=_git_env(ceiling=proof.parent), cwd=str(proof),
                    stdin=subprocess.DEVNULL, text=True, capture_output=True,
                    timeout=30, check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise AuthorityError("authority scratch repository could not be created", 74) from exc
            if initialized.returncode:
                raise AuthorityError("authority scratch repository could not be created", 74)
            _fetch_authority_graph(
                proof, branch, current_remote, transport, protocol, env,
            )
            source_present = _git(
                proof, "rev-parse", "--verify", f"{source_head}^{{commit}}",
            )
            if source_present.returncode or source_present.stdout.strip() != source_head:
                raise AuthorityError(
                    "project authenticated remote history does not contain the exact source"
                )
            anchor_present = _git(proof, "rev-parse", "--verify", f"{anchor}^{{commit}}")
            if anchor_present.returncode or anchor_present.stdout.strip() != anchor:
                raise AuthorityError(
                    "project authenticated remote history no longer contains its anchored tip"
                )
            relationship = require_ancestor(proof, source_head, anchor)
            try:
                require_ancestor(proof, anchor, current_remote)
            except AuthorityError as exc:
                if exc.code == 4:
                    raise AuthorityError(
                        "project authenticated remote tip rolled back or diverged from its anchor"
                    ) from exc
                raise
    except OSError as exc:
        raise AuthorityError("authority scratch repository could not be managed", 74) from exc
    final_repo, final_branch, final_source = observe_clean_source(config)
    if final_repo != repo or final_branch != branch or final_source != source_head:
        raise AuthorityError("project exact measured source moved during authority verification")
    return current_remote, relationship
