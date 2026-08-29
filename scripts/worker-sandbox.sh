#!/usr/bin/env bash
# Launch one model worker as a hardened transient service. systemd constructs the private
# mount namespace as root, then drops to the dedicated runner uid before executing the arm.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
ROOT="${RECURSION_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd -P)}"
PYTHON="${RECURSION_PYTHON:-python3}"
export RECURSION_SCRIPTS_DIR="$SCRIPT_DIR"
safe_directory(){
  "$PYTHON" - "$1" <<'PY'
import os, sys
from pathlib import Path
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, pinned_directory
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    with pinned_directory(Path(sys.argv[1])) as (_, absolute):
        print(absolute)
except (BoundaryError, OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError, RecursionError):
    raise SystemExit(2)
PY
}
safe_mkdir(){
  "$PYTHON" - "$1" <<'PY'
import os, sys
from pathlib import Path
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, ensure_directory
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    print(ensure_directory(Path(sys.argv[1])))
except (BoundaryError, OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError, RecursionError):
    raise SystemExit(2)
PY
}
is_disposable_temp_root(){
  "$PYTHON" - "$1" <<'PY'
import ntpath
import os
import posixpath
import re
import sys

windows = os.name == "nt"


def canonical(value):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        return None
    value = value.strip()
    if windows:
        # Git Bash may spell a Windows path as /c/Users/... while the native
        # environment spells the same path C:\\Users\\....
        value = value.replace("\\", "/")
        match = re.match(r"^/([A-Za-z])(?:/(.*))?$", value)
        if match:
            value = f"{match.group(1).upper()}:/{match.group(2) or ''}"
        try:
            value = os.path.realpath(value)
            value = ntpath.normcase(ntpath.normpath(value))
        except (OSError, ValueError, TypeError):
            return None
    else:
        try:
            value = posixpath.normpath(os.path.realpath(value))
        except (OSError, ValueError, TypeError):
            return None
    try:
        return value if os.path.isdir(value) else None
    except OSError:
        return None


def is_descendant(child, parent):
    try:
        common = ntpath.commonpath((child, parent)) if windows else posixpath.commonpath((child, parent))
    except (ValueError, TypeError):
        return False
    return child != parent and common == parent


root = canonical(sys.argv[1])
if root is None:
    raise SystemExit(1)
temp_values = [os.environ.get(name, "") for name in ("TMPDIR", "TEMP", "TMP")]
if windows:
    try:
        import tempfile
        temp_values.append(tempfile.gettempdir())
    except (OSError, RuntimeError, ValueError):
        pass
else:
    temp_values.append("/tmp")
for value in temp_values:
    temp_root = canonical(value)
    if temp_root is not None and is_descendant(root, temp_root):
        raise SystemExit(0)
raise SystemExit(1)
PY
}
safe_leaf(){
  "$PYTHON" - "$1" <<'PY'
import os, sys
from pathlib import Path
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, verify_leaf
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    value = verify_leaf(Path(sys.argv[1]))
    if value is None:
        raise BoundaryError("path is absent")
    print(os.path.abspath(sys.argv[1]))
except (BoundaryError, OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError, RecursionError):
    raise SystemExit(2)
PY
}
safe_file(){
  "$PYTHON" - "$1" <<'PY'
import os, sys
from pathlib import Path
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, verify_leaf
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    value = verify_leaf(Path(sys.argv[1]), allow_directory=False)
    if value is None:
        raise BoundaryError("path is absent")
    print(os.path.abspath(sys.argv[1]))
except (BoundaryError, OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError, RecursionError):
    raise SystemExit(2)
PY
}
safe_remove_tree(){
  "$PYTHON" - "$1" <<'PY'
import os, shutil, sys
from pathlib import Path
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, verify_leaf
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    path = Path(sys.argv[1])
    value = verify_leaf(path)
    if value is None:
        raise SystemExit(0)
    if not value or not value.st_mode:
        raise BoundaryError("path cannot be inspected")
    shutil.rmtree(path)
except (BoundaryError, OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError, RecursionError):
    raise SystemExit(2)
PY
}
export RECURSION_ROOT="$ROOT"
ROOT="$(safe_directory "$ROOT")" || { echo "worker-sandbox: controller root is not a pinned directory" >&2; exit 95; }
export RECURSION_ROOT="$ROOT"
ENGINE=""; WT=""; PROMPT=""; MODEL=""; USAGE_FILE=""; ROLE="implementer"; ASSIGNMENT_DIGEST=""
NETWORK_POLICY="provider-only"; READ_ONLY_WORKTREE=0; EVIDENCE_DIR=""
GATE_COMMAND=""; WORKDIR_PATH="."; READ_ONLY_PATHS=(); ENGINE_PLAN=""
EXECUTION_EVIDENCE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --engine) ENGINE="${2:-}"; shift 2 ;;
    --engine-plan) ENGINE_PLAN="${2:-}"; shift 2 ;;
    --worktree) WT="${2:-}"; shift 2 ;;
    --prompt) PROMPT="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --usage-file) USAGE_FILE="${2:-}"; shift 2 ;;
    --role) ROLE="${2:-}"; shift 2 ;;
    --network-policy) NETWORK_POLICY="${2:-}"; shift 2 ;;
    --read-only-worktree) READ_ONLY_WORKTREE=1; shift ;;
    --read-only-path) READ_ONLY_PATHS+=("${2:-}"); shift 2 ;;
    --evidence-dir) EVIDENCE_DIR="${2:-}"; shift 2 ;;
    --execution-evidence) EXECUTION_EVIDENCE="${2:-}"; shift 2 ;;
    --assignment-digest) ASSIGNMENT_DIGEST="${2:-}"; shift 2 ;;
    --gate-command) GATE_COMMAND="${2:-}"; shift 2 ;;
    --workdir) WORKDIR_PATH="${2:-}"; shift 2 ;;
    *) echo "worker-sandbox: unknown argument: $1" >&2; exit 2 ;;
  esac
done
[ -z "$ASSIGNMENT_DIGEST" ] || export RECURSION_ASSIGNMENT_DIGEST="$ASSIGNMENT_DIGEST"
case "$ENGINE" in
  claude|hermes|gate)
    [ -z "$ENGINE_PLAN" ] || { echo "worker-sandbox: builtin engines take no engine plan" >&2; exit 92; } ;;
  none|deepseek|openrouter|"") echo "worker-sandbox: invalid engine" >&2; exit 92 ;;
  *)
    # Plugin engines (D-015) run only from a controller-admitted plan file, and the name is
    # revalidated here because it is used as a root-written filename below.
    [ -n "$ENGINE_PLAN" ] || { echo "worker-sandbox: invalid engine" >&2; exit 92; }
    [[ "$ENGINE" =~ ^[a-z][a-z0-9-]{1,31}$ ]] \
      || { echo "worker-sandbox: invalid engine" >&2; exit 92; } ;;
esac
PLAN_EXE=""; PLAN_ARGV=(); PLAN_MODEL_SUFFIX=(); PLAN_ARGV_JSON='[]'; PLAN_MODEL_SUFFIX_JSON='[]'; PLAN_ENV_PASS=(); PLAN_OK=0; PLAN_MREQ=0
PLAN_RUNTIME_MODE="executable-only"; PLAN_RUNTIME_SOURCE=""; PLAN_RUNTIME_TARGET=""; PLAN_RUNTIME_ENTRY=""
PLAN_AUTH_REQUIRED=0; PLAN_AUTH_MODE="none"; PLAN_AUTH_MARKER=""
PLAN_OUTPUT_FORMAT="text"; PLAN_STRUCTURED=0; PLAN_CANCEL_SIGNAL="TERM"; PLAN_CANCEL_GRACE=5
PLAN_EXIT_CODES='{"success":[0],"auth":[1,2],"runtime":[126,127],"egress":[60,65]}'
PLAN_NETWORK_POLICY=""; PLAN_NETWORK_PROFILE=""; PLAN_NETWORK_PROVIDER=""; PLAN_NETWORK_ENDPOINTS=(); PLAN_PROXY_PORT=""
PLAN_CONTROLLER_ROOT=""; PLAN_CONTROLLER_SHA=""
ENGINE_ENV_FILE=""
if [ -n "$ENGINE_PLAN" ]; then
  [ -f "$ENGINE_PLAN" ] || { echo "worker-sandbox: engine plan is missing" >&2; exit 92; }
  plan_parser_output=""
  plan_parser_rc=0
  if plan_parser_output="$("$PYTHON" - "$ENGINE_PLAN" "$ENGINE" <<'PY' 2>&1
import json, os, re, sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", ".")))
try:
    from phase5_safety import BoundaryError, decode_json, is_plain_int, read_bytes
except Exception as exc:
    module_name = getattr(exc, "name", None) or "phase5_safety"
    print(
        f"worker-sandbox: first-party module '{module_name}' is unavailable or malformed; searched "
        f"{os.path.abspath(os.environ.get('RECURSION_SCRIPTS_DIR', '.'))}",
        file=sys.stderr,
    )
    raise SystemExit(95)

class PlanRefusal(Exception):
    pass

def _no_traceback(exc_type, exc, tb):
    print("worker-sandbox: refusal=invalid-engine-plan", file=sys.stderr)
    sys.stderr.flush()
    os._exit(92)
sys.excepthook = _no_traceback
# Validation guards below historically raised SystemExit(92), which bypasses the
# parser's typed-exception hook. Keep the exit code while making every guard a
# distinguishable plan refusal for the boundary sweep.
SystemExit = PlanRefusal
try:
    raw_plan = read_bytes(Path(sys.argv[1]), label="engine plan")
    if raw_plan is None:
        raise BoundaryError("engine plan is absent")
    plan = decode_json(raw_plan, "engine plan")
    if not isinstance(plan, dict):
        raise BoundaryError("engine plan must be an object")
except (BoundaryError, OSError, UnicodeDecodeError, json.JSONDecodeError,
        ValueError, TypeError, OverflowError, RecursionError):
    raise SystemExit(92)
engine = plan.get("engine")
if not is_plain_int(plan.get("schema_version")) or plan.get("schema_version") != 1 or engine != sys.argv[2] \
        or not isinstance(engine, str) or not re.fullmatch(r"[a-z][a-z0-9-]{1,31}", engine):
    raise SystemExit(92)
exe = plan.get("executable"); argv = plan.get("argv")
if not isinstance(exe, str) or not re.fullmatch(r"[a-z][a-z0-9-]{1,31}", exe):
    raise SystemExit(92)
if not isinstance(argv, list) or not argv or \
        any(not isinstance(item, str) or not item or any(ord(ch) < 32 or ord(ch) == 127 for ch in item)
            for item in argv) or len(set(argv)) != len(argv) or argv[0] != "{{EXE}}" \
        or argv.count("{{EXE}}") != 1 or argv.count("{{PROMPT}}") != 1 \
        or argv.count("{{MODEL}}") > 1:
    raise SystemExit(92)
suffix = plan.get("model_argv_suffix", [])
if not isinstance(suffix, list) or \
        any(not isinstance(item, str) or not item or any(ord(ch) < 32 or ord(ch) == 127 for ch in item)
            for item in suffix) or suffix.count("{{MODEL}}") > 1:
    raise SystemExit(92)
for element in list(argv) + list(suffix):
    if not isinstance(element, str) or any(ord(ch) < 32 or ord(ch) == 127 for ch in element):
        raise SystemExit(92)
    if element.startswith("{{") and element.endswith("}}") \
            and element not in ("{{EXE}}", "{{PROMPT}}", "{{MODEL}}"):
        raise SystemExit(92)
for element in suffix:
    if element in ("{{EXE}}", "{{PROMPT}}") \
            or (element.startswith("{{") and element.endswith("}}") and element != "{{MODEL}}"):
        raise SystemExit(92)
if not isinstance(plan.get("model_required"), bool):
    raise SystemExit(92)
if plan.get("model_required") is True:
    print("MREQ=1")
print("EXE=" + exe)
print("ARGVJSON=" + json.dumps(argv, separators=(",", ":")))
print("MSFXJSON=" + json.dumps(suffix, separators=(",", ":")))
for element in argv:
    print("ARG=" + element)
for element in suffix:
    print("MSFX=" + element)
env_names = plan.get("env_passthrough")
if not isinstance(env_names, list) or not all(isinstance(v, str) for v in env_names) \
        or len(set(env_names)) != len(env_names):
    raise SystemExit(92)
billing = plan.get("billing")
if not isinstance(billing, dict) or set(billing) != {"basis", "provider"} \
        or not isinstance(billing.get("basis"), str) or billing.get("basis") not in ("flat-subscription", "metered", "local") \
        or not isinstance(billing.get("provider"), str) \
        or billing.get("provider") not in ("anthropic-claude-code", "cursor", "google-gemini", "openrouter-via-opencode", "sentry-local"):
    raise SystemExit(92)
network = plan.get("network")
if not isinstance(network, dict) or set(network) != {"policy", "profile", "endpoints"} \
        or network.get("policy") not in ("provider-only", "none") \
        or not isinstance(network.get("profile"), str) \
        or not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", network["profile"]) \
        or not isinstance(network.get("endpoints"), list) \
        or any(not isinstance(v, str) or not re.fullmatch(r"[a-z0-9]([a-z0-9.-]*[a-z0-9])?", v)
               for v in network["endpoints"]) \
        or len(set(network["endpoints"])) != len(network["endpoints"]):
    raise SystemExit(92)
if network["profile"] not in ("anthropic", "cursor", "gemini", "openrouter", "sentry-local"):
    raise SystemExit(92)
if network["policy"] == "provider-only" and not network["endpoints"]:
    raise SystemExit(92)
if network["policy"] == "none" and (network["profile"] != "sentry-local"
                                      or plan.get("billing", {}).get("provider") != "sentry-local"
                                      or network["endpoints"]):
    raise SystemExit(92)
try:
    profile_raw = read_bytes(
        Path(os.environ.get("RECURSION_ROOT", ".")) / "scripts" / "provider-egress-profiles.json",
        label="provider profile registry",
    )
    profile_config = decode_json(profile_raw, "provider profile registry")
    if not isinstance(profile_config, dict) or not isinstance(profile_config.get("profiles"), dict):
        raise BoundaryError("provider profile registry is invalid")
    profile = profile_config["profiles"].get(network["profile"])
except (BoundaryError, OSError, ValueError, TypeError, OverflowError,
        RecursionError, UnicodeDecodeError, json.JSONDecodeError):
    raise SystemExit(92)
if not isinstance(profile, dict) or profile.get("provider") != plan.get("billing", {}).get("provider") \
        or not isinstance(profile.get("endpoints"), list) \
        or sorted(profile["endpoints"]) != sorted(network["endpoints"]):
    raise SystemExit(92)
allowed_env = profile.get("env_allowlist")
if not isinstance(allowed_env, list) or any(not isinstance(v, str) for v in allowed_env) \
        or len(set(allowed_env)) != len(allowed_env):
    raise SystemExit(92)
for name in env_names:
    if not isinstance(name, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{2,63}", name) \
            or name not in allowed_env:
        raise SystemExit(92)
    print("ENVP=" + name)
authority = plan.get("authority")
if isinstance(authority, dict):
    if not isinstance(authority, dict) or set(authority) != {"controller_repository", "controller_sha", "policy_files"}:
        raise SystemExit(92)
    authority_root = authority.get("controller_repository")
    if not isinstance(authority_root, str):
        raise SystemExit(92)
    root = os.path.abspath(os.environ.get("RECURSION_ROOT", "."))
    if os.path.normcase(os.path.abspath(authority_root)) != os.path.normcase(root) \
            or not isinstance(authority.get("controller_sha"), str) \
            or not re.fullmatch(r"[0-9a-f]{40,64}", authority["controller_sha"]):
        raise SystemExit(92)
    files = authority.get("policy_files")
    if not isinstance(files, dict) or set(files) != {"scripts/engines/" + engine + ".json",
                                                   "scripts/provider-egress-profiles.json"} \
            or any(not isinstance(v, str) or not re.fullmatch(r"[0-9a-f]{64}", v) for v in files.values()):
        raise SystemExit(92)
    import subprocess
    head = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "HEAD"],
                          capture_output=True, text=True, check=False)
    if head.returncode or head.stdout.strip() != authority["controller_sha"]:
        raise SystemExit(92)
    relative = "scripts/provider-egress-profiles.json"
    committed = subprocess.run(["git", "-C", root, "show", f"{authority['controller_sha']}:{relative}"],
                                capture_output=True, check=False)
    try:
        live = read_bytes(Path(root) / relative, label="provider profile registry")
    except (BoundaryError, OSError, ValueError, TypeError, OverflowError, RecursionError):
        raise SystemExit(92)
    if live is None or committed.returncode or live != committed.stdout \
            or __import__("hashlib").sha256(live).hexdigest() != files[relative]:
        raise SystemExit(92)
    manifest_relative = "scripts/engines/" + engine + ".json"
    manifest_path = os.path.join(root, manifest_relative)
    manifest_committed = subprocess.run(
        ["git", "-C", root, "show", f"{authority['controller_sha']}:{manifest_relative}"],
        capture_output=True, check=False,
    )
    try:
        manifest_live = read_bytes(Path(manifest_path), label="engine manifest")
    except (BoundaryError, OSError, ValueError, TypeError, OverflowError, RecursionError):
        raise SystemExit(92)
    if manifest_live is None or manifest_committed.returncode or manifest_live != manifest_committed.stdout \
            or __import__("hashlib").sha256(manifest_live).hexdigest() != files[manifest_relative]:
        raise SystemExit(92)
    print("CTRROOT=" + str(authority["controller_repository"]))
    print("CTRSHA=" + authority["controller_sha"])
else:
    raise SystemExit(92)
print("NETPOLICY=" + network["policy"])
print("NETPROFILE=" + network["profile"])
print("NETPROVIDER=" + str(plan.get("billing", {}).get("provider", "")))
for endpoint in network["endpoints"]:
    print("NETEND=" + endpoint)
layout = plan.get("runtime_layout")
if layout is not None:
    if not isinstance(layout, dict) or layout.get("mode") not in ("executable-only", "sibling-tree"):
        raise SystemExit(92)
    if layout.get("mode") == "executable-only":
        if set(layout) != {"mode"}:
            raise SystemExit(92)
        print("RTMODE=executable-only")
    else:
        if set(layout) != {"mode", "source", "target", "entrypoint"}:
            raise SystemExit(92)
        source = layout.get("source", layout.get("root"))
        target = layout.get("target", ".recursion-runtime")
        entry = layout.get("entrypoint")
        if source != "executable-directory" or not isinstance(target, str) or not isinstance(entry, str):
            raise SystemExit(92)
        if target.startswith("/") or entry.startswith("/") or ":" in target or ":" in entry \
                or not target or not entry \
                or any(ord(ch) < 32 or ord(ch) == 127 for ch in target + entry) \
                or "\\" in target or "\\" in entry \
                or any(part in ("", ".", "..") for part in target.split("/")) \
                or any(part in ("", ".", "..") for part in entry.split("/")):
            raise SystemExit(92)
        print("RTMODE=sibling-tree")
        print("RTSOURCE=" + source)
        print("RTTARGET=" + target)
        print("RTENTRY=" + entry)
auth = plan.get("auth")
if auth is not None:
    if not isinstance(auth, dict) or set(auth) != {"mode", "required", "marker"} \
            or auth.get("mode") not in ("none", "runner-home-marker") \
            or not isinstance(auth.get("required"), bool):
        raise SystemExit(92)
    if auth["mode"] == "none" and auth.get("marker") is not None:
        raise SystemExit(92)
    if auth.get("mode") == "runner-home-marker":
        marker = auth.get("marker")
        if not isinstance(marker, str) or not marker or any(ord(ch) < 32 or ord(ch) == 127 for ch in marker) \
                or marker.startswith("/") or "\\" in marker \
                or any(part in ("", ".", "..") for part in marker.split("/")):
            raise SystemExit(92)
        print("AUTHREQ=1" if auth.get("required") else "AUTHREQ=0")
        print("AUTHMODE=runner-home-marker")
        print("AUTHMARKER=" + marker)
execution = plan.get("execution")
if execution is not None:
    if not isinstance(execution, dict) or set(execution) != {
            "structured_output", "output_format", "cancellation", "exit_codes"} \
            or not isinstance(execution.get("structured_output"), bool):
        raise SystemExit(92)
    output = execution.get("output_format", "text")
    if output not in ("text", "json"):
        raise SystemExit(92)
    print("EXOUT=" + output)
    if execution.get("structured_output") is True:
        print("EXSTRUCT=1")
    cancellation = execution.get("cancellation")
    if not isinstance(cancellation, dict):
        raise SystemExit(92)
    if set(cancellation) != {"signal", "grace_s"} \
            or cancellation.get("signal") not in ("TERM", "INT") \
            or not is_plain_int(cancellation.get("grace_s")) \
            or not 1 <= cancellation["grace_s"] <= 60:
        raise SystemExit(92)
    print("CANCEL=" + cancellation["signal"])
    print("CGRACE=" + str(cancellation["grace_s"]))
    codes = execution.get("exit_codes")
    if not isinstance(codes, dict) or set(codes) != {"success", "auth", "runtime", "egress"}:
        raise SystemExit(92)
    seen = set()
    for values in codes.values():
        if not isinstance(values, list) or not values or any(not is_plain_int(v) or not 0 <= v <= 255 for v in values) \
                or len(set(values)) != len(values) or seen.intersection(values):
            raise SystemExit(92)
        seen.update(values)
    print("EXCODES=" + json.dumps(codes, sort_keys=True, separators=(",", ":")))
print("OK=1")
PY
)"; then
    :
  else
    plan_parser_rc=$?
  fi
  if [ "$plan_parser_rc" -ne 0 ]; then
    if [[ "$plan_parser_output" == *"worker-sandbox: refusal=invalid-engine-plan"* ]]; then
      # The embedded parser deliberately emits a typed marker for a plan refusal.
      # Command substitution captures stderr along with stdout, so forward only
      # that marker here; parser startup failures must remain a separate class.
      echo "worker-sandbox: refusal=invalid-engine-plan" >&2
      exit 92
    fi
    if [[ "$plan_parser_output" == *"worker-sandbox: first-party module"*"unavailable or malformed; searched "* ]]; then
      printf '%s\n' "$plan_parser_output" >&2
    fi
    echo "worker-sandbox: engine plan parser failed before plan validation (exit $plan_parser_rc)" >&2
    [ "$plan_parser_rc" -eq 92 ] && exit 92
    exit 95
  fi
  while IFS= read -r plan_line; do
    plan_line="${plan_line%$'\r'}"   # a Windows-native python3 emits CRLF; the box's does not
    case "$plan_line" in
      EXE=*)  PLAN_EXE="${plan_line#EXE=}" ;;
      ARGVJSON=*) PLAN_ARGV_JSON="${plan_line#ARGVJSON=}" ;;
      MSFXJSON=*) PLAN_MODEL_SUFFIX_JSON="${plan_line#MSFXJSON=}" ;;
      ARG=*)  PLAN_ARGV+=("${plan_line#ARG=}") ;;
      MSFX=*) PLAN_MODEL_SUFFIX+=("${plan_line#MSFX=}") ;;
      ENVP=*) PLAN_ENV_PASS+=("${plan_line#ENVP=}") ;;
      RTMODE=*) PLAN_RUNTIME_MODE="${plan_line#RTMODE=}" ;;
      RTSOURCE=*) PLAN_RUNTIME_SOURCE="${plan_line#RTSOURCE=}" ;;
      RTTARGET=*) PLAN_RUNTIME_TARGET="${plan_line#RTTARGET=}" ;;
      RTENTRY=*) PLAN_RUNTIME_ENTRY="${plan_line#RTENTRY=}" ;;
      NETPOLICY=*) PLAN_NETWORK_POLICY="${plan_line#NETPOLICY=}" ;;
      NETPROFILE=*) PLAN_NETWORK_PROFILE="${plan_line#NETPROFILE=}" ;;
      NETPROVIDER=*) PLAN_NETWORK_PROVIDER="${plan_line#NETPROVIDER=}" ;;
      NETEND=*) PLAN_NETWORK_ENDPOINTS+=("${plan_line#NETEND=}") ;;
      CTRROOT=*) PLAN_CONTROLLER_ROOT="${plan_line#CTRROOT=}" ;;
      CTRSHA=*) PLAN_CONTROLLER_SHA="${plan_line#CTRSHA=}" ;;
      AUTHREQ=1) PLAN_AUTH_REQUIRED=1 ;;
      AUTHMODE=*) PLAN_AUTH_MODE="${plan_line#AUTHMODE=}" ;;
      AUTHMARKER=*) PLAN_AUTH_MARKER="${plan_line#AUTHMARKER=}" ;;
      EXOUT=*) PLAN_OUTPUT_FORMAT="${plan_line#EXOUT=}" ;;
      EXSTRUCT=1) PLAN_STRUCTURED=1 ;;
      CANCEL=*) PLAN_CANCEL_SIGNAL="${plan_line#CANCEL=}" ;;
      CGRACE=*) PLAN_CANCEL_GRACE="${plan_line#CGRACE=}" ;;
      EXCODES=*) PLAN_EXIT_CODES="${plan_line#EXCODES=}" ;;
      MREQ=1) PLAN_MREQ=1 ;;
      OK=1)   PLAN_OK=1 ;;
    esac
  done <<< "$plan_parser_output"
  [ "$PLAN_OK" = 1 ] || { echo "worker-sandbox: engine plan is invalid" >&2; exit 92; }
  # A group/other-writable plan can be rewritten between resolve and launch by any local
  # process; refuse it in every mode, logical included. Root ownership is asserted only on
  # the real-run path below — a /tmp logical controller cannot own files as uid 0.
  plan_mode_any="$(stat -c %a "$ENGINE_PLAN" 2>/dev/null || echo 777)"
  [ $((8#$plan_mode_any & 022)) -eq 0 ] \
    || { echo "worker-sandbox: engine plan must not be group/other-writable" >&2; exit 95; }
  # model.required is a launch precondition, not advice: without a model the engine would run
  # on its own configured default, off-alias and off-evidence.
  [ "$PLAN_MREQ" != 1 ] || [ -n "$MODEL" ] \
    || { echo "worker-sandbox: engine plan requires a model and none was given" >&2; exit 92; }
  [ -z "$PLAN_NETWORK_PROFILE" ] || [ "$NETWORK_POLICY" = "$PLAN_NETWORK_POLICY" ] \
    || { echo "worker-sandbox: provider network plan cannot be downgraded to a different policy" >&2; exit 92; }
fi
if [ "$ENGINE" = claude ]; then
  # Builtin strict runs still emit the same assignment-bound execution record as plugins.
  PLAN_ARGV_JSON='["claude","-p","{{PROMPT}}","--permission-mode","acceptEdits","--allowedTools","Bash(node:*)"]'
  PLAN_MODEL_SUFFIX_JSON='["--model","{{MODEL}}"]'
  PLAN_NETWORK_POLICY="$NETWORK_POLICY"
  PLAN_NETWORK_PROFILE="anthropic"
  PLAN_NETWORK_PROVIDER="anthropic-claude-code"
  PLAN_NETWORK_ENDPOINTS=(api.anthropic.com)
fi
export RECURSION_AUTH_REQUIRED="$PLAN_AUTH_REQUIRED"
build_plan_argv(){ # resolved-exe -> PLAN_RUN: exact-element placeholder substitution only
  local exe="$1" element
  PLAN_RUN=()
  for element in "${PLAN_ARGV[@]}"; do
    case "$element" in
      '{{EXE}}')    PLAN_RUN+=("$exe") ;;
      '{{PROMPT}}') PLAN_RUN+=("$PROMPT") ;;
      '{{MODEL}}')  PLAN_RUN+=("$MODEL") ;;
      *)            PLAN_RUN+=("$element") ;;
    esac
  done
  if [ -n "$MODEL" ]; then
    for element in "${PLAN_MODEL_SUFFIX[@]}"; do
      case "$element" in
        '{{MODEL}}') PLAN_RUN+=("$MODEL") ;;
        *)           PLAN_RUN+=("$element") ;;
      esac
    done
  fi
}
write_execution_evidence(){ # status rc classification; controller-owned, never worker-written
  local status="$1" rc="$2" classification="$3"
  [ -z "$EXECUTION_EVIDENCE" ] || [ "$ENGINE" = gate ] || {
    "$PYTHON" - "$EXECUTION_EVIDENCE" "$ENGINE" "$MODEL" "$status" "$rc" "$classification" \
      "$PLAN_RUNTIME_MODE" "$PLAN_RUNTIME_TARGET" "$PLAN_RUNTIME_ENTRY" "$PLAN_OUTPUT_FORMAT" \
      "$PLAN_STRUCTURED" "$PLAN_CANCEL_SIGNAL" "$PLAN_CANCEL_GRACE" "$PLAN_EXIT_CODES" \
      "$PLAN_NETWORK_POLICY" "$PLAN_NETWORK_PROFILE" "$PLAN_NETWORK_PROVIDER" "${PLAN_NETWORK_ENDPOINTS[*]}" \
      "$ASSIGNMENT_DIGEST" "$PLAN_ARGV_JSON" "$PLAN_MODEL_SUFFIX_JSON" \
      "${PLAN_RUN[@]}" <<'PY'
import json, os, re, sys
from pathlib import Path
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, atomic_write, decode_json, is_plain_int
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
path, engine, model, status, rc, classification = sys.argv[1:7]
runtime_mode, runtime_target, runtime_entry = sys.argv[7:10]
output_format, structured, cancel_signal, cancel_grace, exit_codes = sys.argv[10:15]
network_policy, network_profile, network_provider, network_endpoints = sys.argv[15:19]
assignment_digest, argv_json, suffix_json = sys.argv[19:22]
argv = sys.argv[22:]
try:
    declared_argv = decode_json(argv_json, "declared argv")
    suffix = decode_json(suffix_json, "declared model suffix")
    codes = decode_json(exit_codes, "declared exit codes") if exit_codes else {}
    if not isinstance(declared_argv, list) or not isinstance(suffix, list) \
            or not isinstance(codes, dict) \
            or not is_plain_int(int(rc)) or not is_plain_int(int(cancel_grace)):
        raise BoundaryError("execution evidence has invalid typed fields")
    if model:
        declared_argv.extend(suffix)
    value = {"schema_version": 1, "engine": engine, "status": status,
             "exit_code": int(rc), "exit_classification": classification,
             "model": model, "argv": declared_argv, "executed_argv": argv,
             "assignment_digest": assignment_digest,
             "assignment_identity": assignment_digest,
             "provider": network_provider, "profile": network_profile,
             "endpoints": network_endpoints.split(),
             "real_execution_capability": "unproven-without-auth",
             "auth_required": os.environ.get("RECURSION_AUTH_REQUIRED", "0") == "1",
             "output_format": output_format, "structured_output": structured == "1",
             "cancellation": {"signal": cancel_signal, "grace_s": int(cancel_grace)},
             "exit_codes": codes,
             "runtime_layout": {"mode": runtime_mode}}
    if network_profile:
        value["network"] = {"policy": network_policy, "profile": network_profile,
                             "provider": network_provider, "endpoints": network_endpoints.split()}
    if runtime_mode == "sibling-tree":
        value["runtime_layout"].update(target=runtime_target, entrypoint=runtime_entry)
    encoded = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    atomic_write(Path(path), encoded, replace=True, mode=0o600, label="execution evidence")
except (BoundaryError, OSError, UnicodeDecodeError, json.JSONDecodeError,
        ValueError, TypeError, OverflowError, RecursionError) as exc:
    raise SystemExit(95) from exc
PY
  }
}
classify_exit_code(){
  "$PYTHON" - "$PLAN_EXIT_CODES" "$1" <<'PY'
import json, sys, os
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, decode_json, is_plain_int
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    codes = decode_json(sys.argv[1], "exit code map")
    code = int(sys.argv[2])
    names = {"success", "auth", "runtime", "egress"}
    if not isinstance(codes, dict) or set(codes) != names or not is_plain_int(code):
        raise BoundaryError("exit code map is invalid")
    seen = set()
    for name in ("success", "auth", "runtime", "egress"):
        values = codes[name]
        if not isinstance(values, list) or not values \
                or any(not is_plain_int(item) or not 0 <= item <= 255 for item in values) \
                or len(set(values)) != len(values) or seen.intersection(values):
            raise BoundaryError("exit code map is invalid")
        seen.update(values)
        if code in values:
            print({"success":"success", "auth":"auth-failed", "runtime":"runtime-failed", "egress":"egress-failed"}[name])
            break
    else:
        print("process-exit")
except (BoundaryError, json.JSONDecodeError, ValueError, TypeError,
        OverflowError, RecursionError, UnicodeDecodeError, OSError, KeyError):
    raise SystemExit(95)
PY
}
check_plan_auth(){
  [ "$PLAN_AUTH_REQUIRED" = 1 ] || return 0
  [ "$PLAN_AUTH_MODE" = runner-home-marker ] && [ -n "$PLAN_AUTH_MARKER" ] || {
    echo "worker-sandbox: refusal=missing-auth invalid runner-home auth contract" >&2; return 90;
  }
  local home="${1:-${RECURSION_TEST_RUNNER_HOME:-${RECURSION_RUNNER_HOME:-${HOME:-}}}}" expected_uid="${2:-$(id -u)}" marker_path="" home_path="" marker_mode="" marker_owner="" marker_type=""
  home_path="$(safe_directory "$home" 2>/dev/null || true)"
  [ -n "$home_path" ] && [ -d "$home_path" ] || { echo "worker-sandbox: refusal=missing-auth runner home is absent" >&2; return 90; }
  marker_path="$home_path/$PLAN_AUTH_MARKER"
  [ -f "$marker_path" ] && [ ! -L "$marker_path" ] || { echo "worker-sandbox: refusal=missing-auth runner auth marker is absent or not regular" >&2; return 90; }
  marker_path="$(safe_file "$marker_path" 2>/dev/null || true)"
  [ -n "$marker_path" ] || { echo "worker-sandbox: refusal=missing-auth auth marker escapes runner home" >&2; return 90; }
  marker_type="$(stat -c %F -- "$marker_path" 2>/dev/null || true)"
  [ "$marker_type" = "regular file" ] || { echo "worker-sandbox: refusal=missing-auth auth marker is not a regular file" >&2; return 90; }
  marker_owner="$(stat -c %u -- "$marker_path" 2>/dev/null || true)"
  marker_mode="$(stat -c %a -- "$marker_path" 2>/dev/null || true)"
  [ "$marker_owner" = "$expected_uid" ] || { echo "worker-sandbox: refusal=missing-auth auth marker ownership is invalid" >&2; return 90; }
  [ "$marker_mode" = 600 ] || { echo "worker-sandbox: refusal=missing-auth auth marker mode is invalid" >&2; return 90; }
}
case "$ROLE" in implementer|verifier|gate) ;; *) echo "worker-sandbox: invalid worker role" >&2; exit 92;; esac
case "$NETWORK_POLICY" in provider-only|none) ;; *) echo "worker-sandbox: invalid network policy" >&2; exit 92;; esac
[ "$ENGINE:$ROLE" = gate:gate ] || { [ "$ENGINE" != gate ] && [ "$ROLE" != gate ]; } \
  || { echo "worker-sandbox: gate engine and role must be paired" >&2; exit 92; }
[ "$ENGINE" != gate ] || [ -n "$GATE_COMMAND" ] \
  || { echo "worker-sandbox: gate command is missing" >&2; exit 92; }
[ "$ROLE" != gate ] || [ "$NETWORK_POLICY" = none ] \
  || { echo "worker-sandbox: acceptance gates are offline; provider-only is invalid" >&2; exit 96; }
[ -n "$WT" ] || { echo "worker-sandbox: worktree is missing" >&2; exit 95; }
WT="$(safe_directory "$WT")" || { echo "worker-sandbox: worktree is not a pinned directory" >&2; exit 95; }
case "${WORKDIR_PATH:-.}" in ''|/*|*..*|*\\*|*:*) echo "worker-sandbox: invalid working directory" >&2; exit 95;; esac
HOST_CWD="$(safe_directory "$WT/${WORKDIR_PATH:-.}" 2>/dev/null || true)"
case "$HOST_CWD" in
  "$WT"|"$WT"/*) ;;
  *) echo "worker-sandbox: working directory escapes the worktree" >&2; exit 95 ;;
esac
SANDBOX_CWD="/workspace${HOST_CWD#$WT}"
READ_ONLY_HOSTS=(); READ_ONLY_DESTS=()
for item in "${READ_ONLY_PATHS[@]}"; do
  case "$item" in ''|/*|*..*|*\\*|*:*) echo "worker-sandbox: invalid read-only worktree path" >&2; exit 95 ;; esac
  host="$(safe_leaf "$WT/$item" 2>/dev/null || true)"
  case "$host" in
    "$WT"/*) READ_ONLY_HOSTS+=("$host"); READ_ONLY_DESTS+=("/workspace/${item#./}") ;;
    *) echo "worker-sandbox: read-only path escapes or is absent: $item" >&2; exit 95 ;;
  esac
done
[ -z "$EVIDENCE_DIR" ] || { EVIDENCE_DIR="$(safe_mkdir "$EVIDENCE_DIR")" || { echo "worker-sandbox: evidence directory is unsafe" >&2; exit 95; }; }
export RECURSION_WORKER_ROLE="$ROLE"
[ -z "$EVIDENCE_DIR" ] || export RECURSION_EVIDENCE_DIR="$EVIDENCE_DIR"

case "${RECURSION_TEST_WORKER:-}" in
  logical)
    # Existing hermetic envelope tests exercise the logical scope gate, not the OS boundary.
    # This bypass is accepted only for disposable platform-temp controllers and is never valid
    # on /opt, the repository, or a user home.
    is_disposable_temp_root "$ROOT" \
      || { echo "worker-sandbox: test bypass refused" >&2; exit 95; }
    if [ "$ENGINE" != gate ]; then
      check_plan_auth || exit $?
    fi
    if [ "$NETWORK_POLICY" = provider-only ] \
       && [ "${RECURSION_TEST_PROVIDER_NETWORK:-}" != logical ]; then
      echo "worker-sandbox: provider-only test capability is absent" >&2; exit 96
    fi
    case "$ENGINE" in
      gate)
        cd "$HOST_CWD"
        env -i HOME=/tmp USER=nobody LOGNAME=nobody LANG=C.UTF-8 \
          PATH=/usr/local/bin:/usr/bin:/bin bash -c "$GATE_COMMAND"
        ;;
      claude)
        command -v claude >/dev/null 2>&1 || exit 90
        write_execution_evidence started 0 prepared || exit 95
        cd "$WT"
        if claude -p "$PROMPT" --permission-mode acceptEdits \
          --allowedTools 'Bash(node:*)' ${MODEL:+--model "$MODEL"}; then logical_rc=0; else logical_rc=$?; fi
        logical_class="$(classify_exit_code "$logical_rc")"
        write_execution_evidence finished "$logical_rc" "$logical_class" || exit 95
        exit "$logical_rc"
        ;;
      hermes)
        command -v hermes >/dev/null 2>&1 || exit 94
        cd "$WT"; hermes -z "$PROMPT" -m "${MODEL:-gpt-5.6-sol}" -t file,terminal --yolo \
          ${USAGE_FILE:+--usage-file "$USAGE_FILE"}
        ;;
      *)
        logical_exe="$(command -v "$PLAN_EXE" 2>/dev/null || true)"
        [ -n "$logical_exe" ] || { echo "worker-sandbox: refusal=missing-runtime executable is unavailable" >&2; exit 94; }
        # Declare the passthrough set so hermetic controls can verify the plan->env plumbing;
        # the real --setenv/EnvironmentFile wiring is exercised only on the box.
        for plan_env_name in "${PLAN_ENV_PASS[@]}"; do
          echo "worker-sandbox: env-passthrough $plan_env_name" >&2
        done
        logical_inner="$logical_exe"
        if [ "$PLAN_RUNTIME_MODE" = sibling-tree ]; then
          logical_runtime_host="$WT/$PLAN_RUNTIME_TARGET"
          "$PYTHON" "$(dirname "$0")/runtime-layout.py" stage \
            --source "$(dirname "$(safe_file "$logical_exe")")" --destination "$logical_runtime_host" \
            --entrypoint "$PLAN_RUNTIME_ENTRY" \
            || { echo "worker-sandbox: refusal=missing-runtime runtime tree could not be staged" >&2; exit 94; }
          logical_inner="$logical_runtime_host/$PLAN_RUNTIME_ENTRY"
        fi
        build_plan_argv "$logical_inner"
        write_execution_evidence started 0 prepared || exit 95
        cd "$WT"
        if "${PLAN_RUN[@]}"; then logical_rc=0; else logical_rc=$?; fi
        logical_class="$(classify_exit_code "$logical_rc")"
        write_execution_evidence finished "$logical_rc" "$logical_class" || exit 95
        exit "$logical_rc"
        ;;
    esac
    exit $?
    ;;
  ""|sandbox) ;;
  *) echo "worker-sandbox: invalid test mode" >&2; exit 95 ;;
esac

# provider-only is not a descriptive label. It requires a root-provisioned namespace whose
# firewall/routing policy is owned outside worker authority. There is deliberately no host-network
# fallback: absent capability means no worker.
PROVIDER_PROFILE=""
PROVIDER_PROXY_PORT=""
PROVIDER_NETNS=""
if [ "$NETWORK_POLICY" = provider-only ]; then
  if [ -n "$ENGINE_PLAN" ]; then
    PROVIDER_PROFILE="$PLAN_NETWORK_PROFILE"
    [ -n "$PROVIDER_PROFILE" ] && [ -n "$PLAN_NETWORK_PROVIDER" ] \
      || { echo "worker-sandbox: refusal=missing-egress provider profile is not bound to the plan" >&2; exit 96; }
  elif [ "$ENGINE" = claude ]; then
    PROVIDER_PROFILE=anthropic
    PLAN_NETWORK_PROVIDER=anthropic-claude-code
    PLAN_NETWORK_ENDPOINTS=(api.anthropic.com)
  else
    echo "worker-sandbox: refusal=missing-egress provider profile is absent" >&2; exit 96
  fi
  PROVIDER_ARGS=("$PROVIDER_PROFILE" --provider "$PLAN_NETWORK_PROVIDER")
  for provider_endpoint in "${PLAN_NETWORK_ENDPOINTS[@]}"; do PROVIDER_ARGS+=(--endpoint "$provider_endpoint"); done
  if [ -n "$PLAN_CONTROLLER_ROOT" ] || [ -n "$PLAN_CONTROLLER_SHA" ]; then
    [ -n "$PLAN_CONTROLLER_ROOT" ] && [ -n "$PLAN_CONTROLLER_SHA" ] \
      || { echo "worker-sandbox: refusal=missing-egress incomplete controller policy provenance" >&2; exit 96; }
    PROVIDER_ARGS+=(--controller-root "$PLAN_CONTROLLER_ROOT" --controller-commit "$PLAN_CONTROLLER_SHA")
  fi
  PROVIDER_JSON="$("$PYTHON" "$ROOT/scripts/provider-egress.py" "${PROVIDER_ARGS[@]}")" \
    || { echo "worker-sandbox: refusal=missing-egress provider profile is invalid" >&2; exit 96; }
  PROVIDER_FIELDS="$("$PYTHON" - "$PROVIDER_JSON" <<'PY'
import json, os, re, sys
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, decode_json, is_plain_int
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    value = decode_json(sys.argv[1], "provider capability")
    if not isinstance(value, dict) or not isinstance(value.get("namespace"), str) \
            or not re.fullmatch(r"[a-z][a-z0-9-]{0,127}", value.get("namespace", "")) \
            or not is_plain_int(value.get("proxy_port")) \
            or not 1 <= value["proxy_port"] <= 65535:
        raise BoundaryError("provider capability is malformed")
    print(value["namespace"])
    print(value["proxy_port"])
except (BoundaryError, json.JSONDecodeError, ValueError, TypeError,
        OverflowError, RecursionError, UnicodeDecodeError, OSError):
    raise SystemExit(96)
PY
  )" || { echo "worker-sandbox: refusal=missing-egress provider capability is malformed" >&2; exit 96; }
  PROVIDER_NETNS="/run/netns/$(printf '%s\n' "$PROVIDER_FIELDS" | sed -n '1p')"
  PROVIDER_PROXY_PORT="$(printf '%s\n' "$PROVIDER_FIELDS" | sed -n '2p')"
  export RECURSION_PROVIDER_PROFILE="$PROVIDER_PROFILE" RECURSION_PROVIDER_ID="$PLAN_NETWORK_PROVIDER"
  export RECURSION_PROVIDER_ENDPOINTS="${PLAN_NETWORK_ENDPOINTS[*]}"
  [ -z "$PLAN_CONTROLLER_ROOT" ] || export RECURSION_CONTROLLER_ROOT="$PLAN_CONTROLLER_ROOT"
  [ -z "$PLAN_CONTROLLER_SHA" ] || export RECURSION_CONTROLLER_COMMIT="$PLAN_CONTROLLER_SHA"
  [ -e "$PROVIDER_NETNS" ] && mountpoint -q "$PROVIDER_NETNS" \
    || { echo "worker-sandbox: refusal=missing-egress provider-only network namespace capability is absent" >&2; exit 96; }
  netns_owner="$(stat -c %u "$PROVIDER_NETNS" 2>/dev/null || true)"
  netns_mode="$(stat -c %a "$PROVIDER_NETNS" 2>/dev/null || true)"
  [ "$netns_owner" = 0 ] && [ -n "$netns_mode" ] \
    && [ $((8#$netns_mode & 022)) -eq 0 ] \
    || { echo "worker-sandbox: refusal=missing-egress provider network capability is not root-owned/read-only" >&2; exit 96; }
fi

[ "$(id -u)" = 0 ] || { echo "worker-sandbox: controller must be root" >&2; exit 95; }
command -v systemd-run >/dev/null 2>&1 \
  || { echo "worker-sandbox: systemd-run unavailable" >&2; exit 95; }
if [ -n "$ENGINE_PLAN" ]; then
  plan_owner="$(stat -c %u "$ENGINE_PLAN" 2>/dev/null || echo x)"
  plan_mode="$(stat -c %a "$ENGINE_PLAN" 2>/dev/null || echo 777)"
  [ "$plan_owner" = 0 ] && [ $((8#$plan_mode & 022)) -eq 0 ] \
    || { echo "worker-sandbox: engine plan must be root-owned and not group/other-writable" >&2; exit 95; }
fi
if [ "$NETWORK_POLICY" = provider-only ]; then
  bash "$ROOT/scripts/provider-network.sh" check >/dev/null \
    || { echo "worker-sandbox: refusal=missing-egress provider-only capability probe failed" >&2; exit 96; }
fi

RUNNER_USER="${RECURSION_RUNNER_USER:-recursion-runner}"
if getent passwd "$RUNNER_USER" >/dev/null 2>&1; then
  RUNNER_UID="$(id -u "$RUNNER_USER")"; RUNNER_GID="$(id -g "$RUNNER_USER")"
  RUNNER_HOME="$(getent passwd "$RUNNER_USER" | cut -d: -f6)"
else
  # Disposable controls run before sysusers.d is deployed but still use a real non-root uid.
  is_disposable_temp_root "$ROOT" \
    || { echo "worker-sandbox: dedicated recursion-runner account is missing" >&2; exit 95; }
  RUNNER_USER=nobody; RUNNER_UID="$(id -u nobody)"; RUNNER_GID="$(id -g nobody)"; RUNNER_HOME=""
fi
[ -z "$RUNNER_HOME" ] || RUNNER_HOME="$(safe_directory "$RUNNER_HOME" 2>/dev/null || true)"
[ -z "$RUNNER_HOME" ] || [ -d "$RUNNER_HOME" ] \
  || { echo "worker-sandbox: runner home is not a canonical directory" >&2; exit 95; }
[ "$RUNNER_UID" != 0 ] && [ "$RUNNER_GID" != 0 ] \
  || { echo "worker-sandbox: runner identity is privileged" >&2; exit 95; }
if [ "$ENGINE" != gate ] && [ "$PLAN_AUTH_REQUIRED" = 1 ]; then
  check_plan_auth "$RUNNER_HOME" "$RUNNER_UID" || exit $?
fi

case "$ENGINE" in
  gate) EXE=""; EXE_REAL="" ;;
  claude) EXE="$(command -v claude 2>/dev/null || true)"; [ -n "$EXE" ] || exit 90 ;;
  hermes) EXE="$(command -v hermes 2>/dev/null || true)"; [ -n "$EXE" ] || exit 94 ;;
  *) EXE="$(command -v "$PLAN_EXE" 2>/dev/null || true)"; [ -n "$EXE" ] \
       || { echo "worker-sandbox: refusal=missing-runtime executable is unavailable" >&2; exit 94; } ;;
esac
[ "$ENGINE" = gate ] || EXE_REAL="$(safe_file "$EXE")" \
  || { echo "worker-sandbox: refusal=missing-runtime executable cannot be resolved" >&2; exit 94; }

# The disposable worktree is the only writable project mount. A test stub outside /usr is copied
# in as one read-only executable and removed before the controller evaluates the diff.
chown -R "$RUNNER_UID:$RUNNER_GID" "$WT"
INNER_EXE="$EXE"
SANDBOX_BIN="$WT/.recursion-sandbox"
RUNTIME_HOST=""; RUNTIME_DEST=""; RUNTIME_ENTRY=""
case "$ENGINE:$EXE_REAL" in
  gate:) ;;
  *:/usr/*) ;;
  *)
    [ ! -e "$SANDBOX_BIN" ] || safe_remove_tree "$SANDBOX_BIN" \
      || { echo "worker-sandbox: sandbox staging path is unsafe" >&2; exit 95; }
    install -d -o 0 -g "$RUNNER_GID" -m 0710 "$SANDBOX_BIN"
    "$PYTHON" - "$EXE_REAL" "$SANDBOX_BIN/$ENGINE" <<'PY'
import os, sys
from pathlib import Path
script_dir = os.path.abspath(os.environ.get("RECURSION_SCRIPTS_DIR", "."))
sys.path.insert(0, script_dir)
try:
    from phase5_safety import BoundaryError, copy_regular
except ModuleNotFoundError as exc:
    if exc.name != "phase5_safety":
        raise
    print(f"worker-sandbox: first-party module 'phase5_safety' not found; searched {script_dir}", file=sys.stderr)
    raise SystemExit(95)
try:
    copy_regular(Path(sys.argv[1]), Path(sys.argv[2]), mode=0o550)
except (BoundaryError, OSError, UnicodeDecodeError, ValueError, TypeError, OverflowError, RecursionError):
    raise SystemExit(2)
PY
    chown 0:"$RUNNER_GID" "$SANDBOX_BIN/$ENGINE"
    INNER_EXE="/workspace/.recursion-sandbox/$ENGINE"
    ;;
esac
if [ "$ENGINE" != gate ] && [ "$PLAN_RUNTIME_MODE" = sibling-tree ]; then
  RUNTIME_HOST="$WT/$PLAN_RUNTIME_TARGET"
  RUNTIME_DEST="/workspace/$PLAN_RUNTIME_TARGET"
  RUNTIME_ENTRY="$PLAN_RUNTIME_ENTRY"
  "$PYTHON" "$ROOT/scripts/runtime-layout.py" stage \
    --source "$(dirname "$EXE_REAL")" --destination "$RUNTIME_HOST" \
    --entrypoint "$PLAN_RUNTIME_ENTRY" \
    || { echo "worker-sandbox: refusal=missing-runtime runtime tree could not be staged" >&2; exit 94; }
  chown -R 0:"$RUNNER_GID" "$RUNTIME_HOST"
  INNER_EXE="$RUNTIME_DEST/$RUNTIME_ENTRY"
fi

safe_engine="${ENGINE//[^A-Za-z0-9_.-]/-}"
UNIT="recursion-worker-${safe_engine}-$$-${RANDOM}.service"
client_pid=""
CLEANUP_DONE=0
stop_unit(){
  local signal="$PLAN_CANCEL_SIGNAL" grace="$PLAN_CANCEL_GRACE" i
  systemctl kill --kill-whom=all --signal="$signal" "$UNIT" >/dev/null 2>&1 || true
  for i in $(seq 1 $((grace * 10))); do
    systemctl is-active --quiet "$UNIT" 2>/dev/null || return 0
    sleep 0.1
  done
  systemctl kill --kill-whom=all --signal=KILL "$UNIT" >/dev/null 2>&1 || true
  systemctl stop "$UNIT" >/dev/null 2>&1 || true
  for i in $(seq 1 50); do
    systemctl is-active --quiet "$UNIT" 2>/dev/null || return 0
    sleep 0.1
  done
  echo "worker-sandbox: worker cgroup did not terminate" >&2
  return 1
}
cleanup(){
  [ "$CLEANUP_DONE" = 1 ] && return 0
  if ! stop_unit; then
    echo "worker-sandbox: quarantine=termination-unconfirmed worktree and evidence retained" >&2
    return 1
  fi
  [ ! -e "$SANDBOX_BIN" ] || safe_remove_tree "$SANDBOX_BIN" || return 1
  [ -z "$RUNTIME_HOST" ] || safe_remove_tree "$RUNTIME_HOST" || return 1
  [ -z "$ENGINE_ENV_FILE" ] || rm -f -- "$ENGINE_ENV_FILE"
  chown -R 0:0 "$WT" 2>/dev/null || true
  CLEANUP_DONE=1
}
cancel_worker(){
  if ! cleanup; then exit 96; fi
  [ "$ENGINE" = gate ] || write_execution_evidence cancelled 143 cancelled || true
  exit 143
}
trap cancel_worker TERM INT
trap 'cleanup || true' EXIT

RUN=(systemd-run --quiet --wait --collect --pipe --service-type=exec --unit "$UNIT"
  --uid "$RUNNER_USER" --gid "$RUNNER_GID" --working-directory "$SANDBOX_CWD"
  --property NoNewPrivileges=yes --property CapabilityBoundingSet=
  --property AmbientCapabilities= --property PrivateTmp=yes --property PrivateDevices=yes
  --property ProtectSystem=strict --property ProtectHome=yes
  --property ProtectKernelTunables=yes --property ProtectKernelModules=yes
  --property ProtectKernelLogs=yes --property ProtectControlGroups=yes
  --property RestrictSUIDSGID=yes --property LockPersonality=yes
  --property UMask=0077 --property KillMode=control-group
  --property "InaccessiblePaths=-/workspace/.env -/workspace/state -/workspace/CONTROL_PLANE.md -/workspace/ANCHOR.md -/workspace/CLAUDE.md /run /var/run"
  --property "ReadOnlyPaths=-/workspace/scripts -/workspace/.github"
  --setenv HOME=/home/runner --setenv USER="$RUNNER_USER" --setenv LOGNAME="$RUNNER_USER"
  --setenv LANG=C.UTF-8 --setenv PATH=/usr/local/bin:/usr/bin:/bin
  --setenv RECURSION_WORKER_ROLE="$ROLE")

# Model workers need only their checkout and provider executable. Gates additionally need the
# repository's read-only git metadata and controller-owned gate scripts/baselines, so they retain
# a read-only view of /opt while still running non-root under ProtectSystem=strict.
# /run and /var/run carry host Unix sockets (systemd's private bus, Docker, journald) and other
# confused deputies. Masking them per-arm here (and in the shared base above) keeps every arm from
# reaching host sockets; provider egress is always the profile-bound TCP loopback CONNECT proxy.
if [ "$ENGINE" != gate ]; then
  RUN+=(--property "InaccessiblePaths=/opt /srv -/workspace/.git /run /var/run")
else
  # Git must remain readable to acceptance suites, but the suite is worker-authored code.
  # Protect the worktree pointer itself; ProtectSystem=strict separately keeps its controller
  # gitdir/refs read-only when that pointer resolves outside /workspace.
  RUN+=(--property "ReadOnlyPaths=-/workspace/.git")
fi

if [ "$READ_ONLY_WORKTREE" = 1 ]; then
  RUN+=(--property "BindReadOnlyPaths=$WT:/workspace" --property ReadOnlyPaths=/workspace)
else
  RUN+=(--property "BindPaths=$WT:/workspace" --property ReadWritePaths=/workspace)
fi
for ((i=0; i<${#READ_ONLY_HOSTS[@]}; i++)); do
  RUN+=(--property "BindReadOnlyPaths=${READ_ONLY_HOSTS[$i]}:${READ_ONLY_DESTS[$i]}")
done
if [ -n "$RUNTIME_DEST" ]; then
  # The runtime tree is staged below the disposable checkout, then made
  # read-only in the worker mount namespace as one complete unit.
  RUN+=(--property "ReadOnlyPaths=$RUNTIME_DEST")
fi
if [ -n "$EVIDENCE_DIR" ]; then
  chown -R "$RUNNER_UID:$RUNNER_GID" "$EVIDENCE_DIR"
  RUN+=(--property "BindPaths=$EVIDENCE_DIR:/evidence" --property ReadWritePaths=/evidence
        --setenv RECURSION_EVIDENCE_DIR=/evidence)
fi
if [ "$NETWORK_POLICY" = none ]; then
  RUN+=(--property PrivateNetwork=yes --property IPAddressDeny=any)
else
  RUN+=(--property "NetworkNamespacePath=$PROVIDER_NETNS")
fi
if [ "$NETWORK_POLICY" = provider-only ]; then
  # Every provider uses the same profile-bound local proxy contract; no engine-specific
  # proxy address or Claude-only routing assumption is permitted.
  RUN+=(--setenv HTTPS_PROXY="http://127.0.0.1:$PROVIDER_PROXY_PORT"
        --setenv HTTP_PROXY="http://127.0.0.1:$PROVIDER_PROXY_PORT"
        --setenv RECURSION_PROVIDER_PROFILE="$PROVIDER_PROFILE"
        --setenv RECURSION_PROVIDER_ID="$PLAN_NETWORK_PROVIDER"
        --setenv RECURSION_PROVIDER_ENDPOINTS="${PLAN_NETWORK_ENDPOINTS[*]}"
  )
fi
for name in RECURSION_VERIFICATION_COMMIT RECURSION_IMPLEMENTER_RUN_ID; do
  value="${!name:-}"; [ -z "$value" ] || RUN+=(--setenv "$name=$value")
done

if [ "$ENGINE" != gate ] && [ -n "$RUNNER_HOME" ] && [ -d "$RUNNER_HOME" ]; then
  RUN+=(--property "BindReadOnlyPaths=$RUNNER_HOME:/home/runner")
fi
if [ "${RECURSION_TEST_WORKER:-}" = sandbox ]; then
  is_disposable_temp_root "$ROOT" \
    || { echo "worker-sandbox: sandbox test env refused" >&2; exit 95; }
  [ -n "${STUB_ARM_SCRIPT:-}" ] && RUN+=(--setenv STUB_ARM_SCRIPT="$STUB_ARM_SCRIPT")
  for name in STUB_SECRET STUB_LEAK STUB_OUTSIDE STUB_UIDLOG STUB_PUBLISHER STUB_PUBLOG STUB_VERIFIER_SCRIPT; do
    value="${!name:-}"; [ -n "$value" ] && RUN+=(--setenv "$name=$value")
  done
  if [ -n "${STUB_STARTED:-}" ]; then
    : > "$STUB_STARTED"
    RUN+=(--setenv STUB_STARTED=/tmp/worker-started)
  fi
fi

case "$ENGINE" in
  gate)
    RUN+=(/usr/bin/env -i HOME=/tmp USER="$RUNNER_USER" LOGNAME="$RUNNER_USER" LANG=C.UTF-8 \
      PATH=/usr/local/bin:/usr/bin:/bin /bin/bash -c "$GATE_COMMAND")
    ;;
  claude)
    write_execution_evidence started 0 prepared || exit 95
    RUN+=(/usr/bin/env "$INNER_EXE" -p "$PROMPT" --permission-mode acceptEdits --allowedTools 'Bash(node:*)')
    [ -n "$MODEL" ] && RUN+=(--model "$MODEL")
    ;;
  hermes)
    # The mount target must not live under /run: this arm masks /run and /var/run as
    # InaccessiblePaths (twice, base set + non-gate set), and systemd drops any mount entry
    # shadowed by an inaccessible path — the bind would be silently discarded and hermes
    # could never write the file. PrivateTmp=yes gives the unit its own writable /tmp, so
    # the usage file is bound there instead.
    if [ -n "$USAGE_FILE" ]; then
      : > "$USAGE_FILE"; chown "$RUNNER_UID:$RUNNER_GID" "$USAGE_FILE"
      RUN+=(--property "BindPaths=$USAGE_FILE:/tmp/recursion-worker-usage.json")
    fi
    RUN+=(/usr/bin/env "$INNER_EXE" -z "$PROMPT" -m "${MODEL:-gpt-5.6-sol}" -t file,terminal --yolo)
    [ -n "$USAGE_FILE" ] && RUN+=(--usage-file /tmp/recursion-worker-usage.json)
    ;;
  *)
    # Plugin engines (D-015): exec exactly the admitted plan argv; no shell, no interpolation.
    # Passthrough values ride a root-owned 0600 EnvironmentFile, never the systemd-run command
    # line, so credentials stay out of /proc/*/cmdline and `systemctl show`.
    if [ "${#PLAN_ENV_PASS[@]}" -gt 0 ]; then
      ENGINE_ENV_FILE="$(mktemp /tmp/recursion-engine-env.XXXXXX)" || exit 95
      chmod 0600 "$ENGINE_ENV_FILE"
      for plan_env_name in "${PLAN_ENV_PASS[@]}"; do
        plan_env_value="${!plan_env_name:-}"
        [ -n "$plan_env_value" ] || continue
        case "$plan_env_value" in
          *$'\n'*|*$'\r'*) echo "worker-sandbox: engine env value contains a newline" >&2; exit 92 ;;
        esac
        printf '%s=%s\n' "$plan_env_name" "$plan_env_value" >> "$ENGINE_ENV_FILE"
      done
      RUN+=(--property "EnvironmentFile=$ENGINE_ENV_FILE")
    fi
    build_plan_argv "$INNER_EXE"
    write_execution_evidence started 0 prepared || exit 95
    RUN+=(/usr/bin/env "${PLAN_RUN[@]}")
    ;;
esac

"${RUN[@]}" & client_pid=$!
if wait "$client_pid"; then rc=0; else rc=$?; fi
client_pid=""
if [ "$ENGINE" != gate ]; then
  execution_class="$(classify_exit_code "$rc")"
  write_execution_evidence finished "$rc" "$execution_class" || exit 95
fi
exit "$rc"
