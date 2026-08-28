#!/usr/bin/env bash
# Launch one model worker as a hardened transient service. systemd constructs the private
# mount namespace as root, then drops to the dedicated runner uid before executing the arm.
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
export RECURSION_ROOT="$ROOT"
PYTHON="${RECURSION_PYTHON:-python3}"
ENGINE=""; WT=""; PROMPT=""; MODEL=""; USAGE_FILE=""; ROLE="implementer"
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
    --gate-command) GATE_COMMAND="${2:-}"; shift 2 ;;
    --workdir) WORKDIR_PATH="${2:-}"; shift 2 ;;
    *) echo "worker-sandbox: unknown argument: $1" >&2; exit 2 ;;
  esac
done
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
PLAN_EXE=""; PLAN_ARGV=(); PLAN_MODEL_SUFFIX=(); PLAN_ENV_PASS=(); PLAN_OK=0; PLAN_MREQ=0
PLAN_RUNTIME_MODE="executable-only"; PLAN_RUNTIME_SOURCE=""; PLAN_RUNTIME_TARGET=""; PLAN_RUNTIME_ENTRY=""
PLAN_AUTH_REQUIRED=0; PLAN_AUTH_MODE="none"; PLAN_AUTH_MARKER=""
PLAN_OUTPUT_FORMAT="text"; PLAN_STRUCTURED=0; PLAN_CANCEL_SIGNAL="TERM"; PLAN_CANCEL_GRACE=5
PLAN_EXIT_CODES='{"success":[0],"auth":[1,2],"runtime":[126,127],"egress":[60,65]}'
PLAN_NETWORK_PROFILE=""; PLAN_NETWORK_PROVIDER=""; PLAN_NETWORK_ENDPOINTS=(); PLAN_PROXY_PORT=""
ENGINE_ENV_FILE=""
if [ -n "$ENGINE_PLAN" ]; then
  [ -f "$ENGINE_PLAN" ] || { echo "worker-sandbox: engine plan is missing" >&2; exit 92; }
  while IFS= read -r plan_line; do
    plan_line="${plan_line%$'\r'}"   # a Windows-native python3 emits CRLF; the box's does not
    case "$plan_line" in
      EXE=*)  PLAN_EXE="${plan_line#EXE=}" ;;
      ARG=*)  PLAN_ARGV+=("${plan_line#ARG=}") ;;
      MSFX=*) PLAN_MODEL_SUFFIX+=("${plan_line#MSFX=}") ;;
      ENVP=*) PLAN_ENV_PASS+=("${plan_line#ENVP=}") ;;
      RTMODE=*) PLAN_RUNTIME_MODE="${plan_line#RTMODE=}" ;;
      RTSOURCE=*) PLAN_RUNTIME_SOURCE="${plan_line#RTSOURCE=}" ;;
      RTTARGET=*) PLAN_RUNTIME_TARGET="${plan_line#RTTARGET=}" ;;
      RTENTRY=*) PLAN_RUNTIME_ENTRY="${plan_line#RTENTRY=}" ;;
      NETPROFILE=*) PLAN_NETWORK_PROFILE="${plan_line#NETPROFILE=}" ;;
      NETPROVIDER=*) PLAN_NETWORK_PROVIDER="${plan_line#NETPROVIDER=}" ;;
      NETEND=*) PLAN_NETWORK_ENDPOINTS+=("${plan_line#NETEND=}") ;;
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
  done < <("$PYTHON" - "$ENGINE_PLAN" "$ENGINE" <<'PY' || true
import json, os, re, sys
try:
    plan = json.load(open(sys.argv[1]))
except Exception:
    raise SystemExit(92)
engine = plan.get("engine")
if plan.get("schema_version") != 1 or engine != sys.argv[2] \
        or not isinstance(engine, str) or not re.fullmatch(r"[a-z][a-z0-9-]{1,31}", engine):
    raise SystemExit(92)
exe = plan.get("executable"); argv = plan.get("argv")
if not isinstance(exe, str) or not re.fullmatch(r"[a-z][a-z0-9-]{1,31}", exe):
    raise SystemExit(92)
if not isinstance(argv, list) or not argv or argv[0] != "{{EXE}}" \
        or argv.count("{{EXE}}") != 1 or argv.count("{{PROMPT}}") != 1 \
        or argv.count("{{MODEL}}") > 1:
    raise SystemExit(92)
suffix = plan.get("model_argv_suffix") or []
if not isinstance(suffix, list) or suffix.count("{{MODEL}}") > 1:
    raise SystemExit(92)
for element in list(argv) + list(suffix):
    if not isinstance(element, str) or any(ord(ch) < 32 or ord(ch) == 127 for ch in element):
        raise SystemExit(92)
    if element.startswith("{{") and element.endswith("}}") \
            and element not in ("{{EXE}}", "{{PROMPT}}", "{{MODEL}}"):
        raise SystemExit(92)
for element in suffix:
    if element in ("{{EXE}}", "{{PROMPT}}"):
        raise SystemExit(92)
if plan.get("model_required"):
    print("MREQ=1")
print("EXE=" + exe)
for element in argv:
    print("ARG=" + element)
for element in suffix:
    print("MSFX=" + element)
for name in plan.get("env_passthrough") or []:
    if not isinstance(name, str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{2,63}", name):
        raise SystemExit(92)
    print("ENVP=" + name)
network = plan.get("network")
if network is not None:
    if not isinstance(network, dict) or network.get("policy") != "provider-only" \
            or not isinstance(network.get("profile"), str) \
            or not re.fullmatch(r"[a-z][a-z0-9-]{1,63}", network["profile"]) \
            or not isinstance(network.get("endpoints"), list) \
            or not all(isinstance(v, str) and re.fullmatch(r"[a-z0-9]([a-z0-9.-]*[a-z0-9])?", v) for v in network["endpoints"]):
        raise SystemExit(92)
    profile_config = json.load(open(os.path.join(os.environ.get("RECURSION_ROOT", "."), "scripts", "provider-egress-profiles.json")))
    profile = profile_config.get("profiles", {}).get(network["profile"])
    if not isinstance(profile, dict) or profile.get("provider") != plan.get("billing", {}).get("provider") \
            or sorted(profile.get("endpoints", [])) != sorted(network["endpoints"]):
        raise SystemExit(92)
    print("NETPROFILE=" + network["profile"])
    print("NETPROVIDER=" + str(plan.get("billing", {}).get("provider", "")))
    for endpoint in network["endpoints"]:
        print("NETEND=" + endpoint)
layout = plan.get("runtime_layout")
if layout is not None:
    if not isinstance(layout, dict) or layout.get("mode") not in ("executable-only", "sibling-tree"):
        raise SystemExit(92)
    if layout.get("mode") == "sibling-tree":
        source = layout.get("source", layout.get("root"))
        target = layout.get("target", ".recursion-runtime")
        entry = layout.get("entrypoint")
        if source != "executable-directory" or not isinstance(target, str) or not isinstance(entry, str):
            raise SystemExit(92)
        if target.startswith("/") or entry.startswith("/") or not target or not entry \
                or any(ord(ch) < 32 or ord(ch) == 127 for ch in target + entry) \
                or "\\" in target or "\\" in entry \
                or any(part in ("", ".", "..") for part in target.split("/")) \
                or any(part in ("", ".", "..") for part in entry.split("/")):
            raise SystemExit(92)
        print("RTMODE=sibling-tree")
        print("RTSOURCE=" + source)
        print("RTTARGET=" + target)
        print("RTENTRY=" + entry)
    else:
        print("RTMODE=executable-only")
auth = plan.get("auth")
if auth is not None:
    if not isinstance(auth, dict) or auth.get("mode") not in ("none", "runner-home-marker") \
            or not isinstance(auth.get("required"), bool):
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
    if not isinstance(execution, dict):
        raise SystemExit(92)
    output = execution.get("output_format", "text")
    if output not in ("text", "json"):
        raise SystemExit(92)
    print("EXOUT=" + output)
    if execution.get("structured_output") is True:
        print("EXSTRUCT=1")
    cancellation = execution.get("cancellation") or {}
    if set(cancellation) != {"signal", "grace_s"} \
            or cancellation.get("signal") not in ("TERM", "INT") \
            or not isinstance(cancellation.get("grace_s"), int) \
            or not 1 <= cancellation["grace_s"] <= 60:
        raise SystemExit(92)
    print("CANCEL=" + cancellation["signal"])
    print("CGRACE=" + str(cancellation["grace_s"]))
    codes = execution.get("exit_codes")
    if not isinstance(codes, dict) or set(codes) != {"success", "auth", "runtime", "egress"}:
        raise SystemExit(92)
    seen = set()
    for values in codes.values():
        if not isinstance(values, list) or not values or any(not isinstance(v, int) or not 0 <= v <= 255 for v in values) \
                or len(set(values)) != len(values) or seen.intersection(values):
            raise SystemExit(92)
        seen.update(values)
    print("EXCODES=" + json.dumps(codes, sort_keys=True, separators=(",", ":")))
print("OK=1")
PY
)
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
  [ -z "$PLAN_NETWORK_PROFILE" ] || [ "$NETWORK_POLICY" = provider-only ] \
    || { echo "worker-sandbox: provider network plan cannot be downgraded to a different policy" >&2; exit 92; }
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
    mkdir -p "$(dirname "$EXECUTION_EVIDENCE")" || return 1
    "$PYTHON" - "$EXECUTION_EVIDENCE" "$ENGINE" "$MODEL" "$status" "$rc" "$classification" \
      "$PLAN_RUNTIME_MODE" "$PLAN_RUNTIME_TARGET" "$PLAN_RUNTIME_ENTRY" "$PLAN_OUTPUT_FORMAT" \
      "$PLAN_STRUCTURED" "$PLAN_CANCEL_SIGNAL" "$PLAN_CANCEL_GRACE" "$PLAN_EXIT_CODES" \
      "$PLAN_NETWORK_PROFILE" "$PLAN_NETWORK_PROVIDER" "${PLAN_NETWORK_ENDPOINTS[*]}" \
      "${PLAN_RUN[@]}" <<'PY'
import json, os, sys, tempfile
path, engine, model, status, rc, classification = sys.argv[1:7]
runtime_mode, runtime_target, runtime_entry = sys.argv[7:10]
output_format, structured, cancel_signal, cancel_grace, exit_codes = sys.argv[10:15]
network_profile, network_provider, network_endpoints = sys.argv[15:18]
argv = sys.argv[18:]
value = {"schema_version": 1, "engine": engine, "status": status,
         "exit_code": int(rc), "exit_classification": classification,
         "model": model, "argv": argv,
         "real_execution_capability": "unproven-without-auth",
         "auth_required": os.environ.get("RECURSION_AUTH_REQUIRED", "0") == "1",
         "output_format": output_format, "structured_output": structured == "1",
         "cancellation": {"signal": cancel_signal, "grace_s": int(cancel_grace)},
         "exit_codes": json.loads(exit_codes) if exit_codes else {},
         "runtime_layout": {"mode": runtime_mode}}
if network_profile:
    value["network"] = {"policy": "provider-only", "profile": network_profile,
                         "provider": network_provider, "endpoints": network_endpoints.split()}
if runtime_mode == "sibling-tree":
    value["runtime_layout"].update(target=runtime_target, entrypoint=runtime_entry)
fd, tmp = tempfile.mkstemp(prefix=".execution-evidence.", dir=os.path.dirname(path) or ".")
with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as out:
    json.dump(value, out, indent=2, sort_keys=True); out.write("\n"); out.flush(); os.fsync(out.fileno())
os.replace(tmp, path)
PY
  }
}
classify_exit_code(){
  "$PYTHON" - "$PLAN_EXIT_CODES" "$1" <<'PY'
import json, sys
codes = json.loads(sys.argv[1]); code = int(sys.argv[2])
for name, values in codes.items():
    if code in values:
        print({"success":"success", "auth":"auth-failed", "runtime":"runtime-failed", "egress":"egress-failed"}[name])
        break
else:
    print("process-exit")
PY
}
check_plan_auth(){
  [ "$PLAN_AUTH_REQUIRED" = 1 ] || return 0
  [ "$PLAN_AUTH_MODE" = runner-home-marker ] && [ -n "$PLAN_AUTH_MARKER" ] || {
    echo "worker-sandbox: refusal=missing-auth invalid runner-home auth contract" >&2; return 90;
  }
  local home="${1:-${RECURSION_TEST_RUNNER_HOME:-${RECURSION_RUNNER_HOME:-${HOME:-}}}}" expected_uid="${2:-$(id -u)}" marker_path="" home_path="" marker_mode="" marker_owner="" marker_type=""
  home_path="$(realpath -e -- "$home" 2>/dev/null || true)"
  [ -n "$home_path" ] && [ -d "$home_path" ] || { echo "worker-sandbox: refusal=missing-auth runner home is absent" >&2; return 90; }
  marker_path="$home_path/$PLAN_AUTH_MARKER"
  [ -f "$marker_path" ] && [ ! -L "$marker_path" ] || { echo "worker-sandbox: refusal=missing-auth runner auth marker is absent or not regular" >&2; return 90; }
  [ "$(realpath -e -- "$marker_path" 2>/dev/null || true)" = "$marker_path" ] || { echo "worker-sandbox: refusal=missing-auth auth marker escapes runner home" >&2; return 90; }
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
[ -d "$WT" ] || { echo "worker-sandbox: worktree is missing" >&2; exit 95; }
WT="$(realpath -e "$WT")"
HOST_CWD="$(realpath -e "$WT/${WORKDIR_PATH:-.}" 2>/dev/null || true)"
case "$HOST_CWD" in
  "$WT"|"$WT"/*) ;;
  *) echo "worker-sandbox: working directory escapes the worktree" >&2; exit 95 ;;
esac
SANDBOX_CWD="/workspace${HOST_CWD#$WT}"
READ_ONLY_HOSTS=(); READ_ONLY_DESTS=()
for item in "${READ_ONLY_PATHS[@]}"; do
  case "$item" in ''|/*|*..*) echo "worker-sandbox: invalid read-only worktree path" >&2; exit 95 ;; esac
  host="$(realpath -e "$WT/$item" 2>/dev/null || true)"
  case "$host" in
    "$WT"/*) READ_ONLY_HOSTS+=("$host"); READ_ONLY_DESTS+=("/workspace/${item#./}") ;;
    *) echo "worker-sandbox: read-only path escapes or is absent: $item" >&2; exit 95 ;;
  esac
done
[ -z "$EVIDENCE_DIR" ] || { mkdir -p "$EVIDENCE_DIR"; EVIDENCE_DIR="$(realpath -e "$EVIDENCE_DIR")"; }
export RECURSION_WORKER_ROLE="$ROLE"
[ -z "$EVIDENCE_DIR" ] || export RECURSION_EVIDENCE_DIR="$EVIDENCE_DIR"

case "${RECURSION_TEST_WORKER:-}" in
  logical)
    # Existing hermetic envelope tests exercise the logical scope gate, not the OS boundary.
    # This bypass is accepted only for disposable /tmp controllers and is never valid on /opt.
    case "$(realpath -m "$ROOT")" in /tmp/*) ;; *) echo "worker-sandbox: test bypass refused" >&2; exit 95;; esac
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
        cd "$WT"; claude -p "$PROMPT" --permission-mode acceptEdits \
          --allowedTools 'Bash(node:*)' ${MODEL:+--model "$MODEL"}
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
          mkdir -p "$(dirname "$logical_runtime_host")"
          "$PYTHON" "$(dirname "$0")/runtime-layout.py" stage \
            --source "$(dirname "$(realpath -e "$logical_exe")")" --destination "$logical_runtime_host" \
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
    [ -n "$PROVIDER_PROFILE" ] && [ "$PLAN_NETWORK_PROVIDER" = "$("$PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["billing"]["provider"])' "$ENGINE_PLAN")" ] \
      || { echo "worker-sandbox: refusal=missing-egress provider profile is not bound to the plan" >&2; exit 96; }
  elif [ "$ENGINE" = claude ]; then
    PROVIDER_PROFILE=anthropic
    PLAN_NETWORK_PROVIDER=anthropic-claude-code
    PLAN_NETWORK_ENDPOINTS=(api.anthropic.com)
  else
    echo "worker-sandbox: refusal=missing-egress provider profile is absent" >&2; exit 96
  fi
  PROVIDER_JSON="$("$PYTHON" "$ROOT/scripts/provider-egress.py" "$PROVIDER_PROFILE" --provider "$PLAN_NETWORK_PROVIDER" $(printf -- '--endpoint %q ' "${PLAN_NETWORK_ENDPOINTS[@]}"))" \
    || { echo "worker-sandbox: refusal=missing-egress provider profile is invalid" >&2; exit 96; }
  PROVIDER_NETNS="/run/netns/$("$PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["namespace"])' "$PROVIDER_JSON")"
  PROVIDER_PROXY_PORT="$("$PYTHON" -c 'import json,sys; print(json.loads(sys.argv[1])["proxy_port"])' "$PROVIDER_JSON")"
  export RECURSION_PROVIDER_PROFILE="$PROVIDER_PROFILE" RECURSION_PROVIDER_ID="$PLAN_NETWORK_PROVIDER"
  export RECURSION_PROVIDER_ENDPOINTS="${PLAN_NETWORK_ENDPOINTS[*]}"
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
  case "$(realpath -m "$ROOT")" in
    /tmp/*) RUNNER_USER=nobody; RUNNER_UID="$(id -u nobody)"; RUNNER_GID="$(id -g nobody)"; RUNNER_HOME="" ;;
    *) echo "worker-sandbox: dedicated recursion-runner account is missing" >&2; exit 95 ;;
  esac
fi
[ -z "$RUNNER_HOME" ] || RUNNER_HOME="$(realpath -e -- "$RUNNER_HOME" 2>/dev/null || true)"
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
[ "$ENGINE" = gate ] || EXE_REAL="$(realpath -e "$EXE")" \
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
    rm -rf -- "$SANDBOX_BIN"
    install -d -o 0 -g "$RUNNER_GID" -m 0710 "$SANDBOX_BIN"
    install -o 0 -g "$RUNNER_GID" -m 0550 "$EXE_REAL" "$SANDBOX_BIN/$ENGINE"
    INNER_EXE="/workspace/.recursion-sandbox/$ENGINE"
    ;;
esac
if [ "$ENGINE" != gate ] && [ "$PLAN_RUNTIME_MODE" = sibling-tree ]; then
  RUNTIME_HOST="$WT/$PLAN_RUNTIME_TARGET"
  RUNTIME_DEST="/workspace/$PLAN_RUNTIME_TARGET"
  RUNTIME_ENTRY="$PLAN_RUNTIME_ENTRY"
  mkdir -p "$(dirname "$RUNTIME_HOST")"
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
  rm -rf -- "$SANDBOX_BIN"
  [ -z "$RUNTIME_HOST" ] || rm -rf -- "$RUNTIME_HOST"
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
        --setenv CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
  )
fi
for name in RECURSION_VERIFICATION_COMMIT RECURSION_IMPLEMENTER_RUN_ID; do
  value="${!name:-}"; [ -z "$value" ] || RUN+=(--setenv "$name=$value")
done

if [ "$ENGINE" != gate ] && [ -n "$RUNNER_HOME" ] && [ -d "$RUNNER_HOME" ]; then
  RUN+=(--property "BindReadOnlyPaths=$RUNNER_HOME:/home/runner")
fi
if [ "${RECURSION_TEST_WORKER:-}" = sandbox ]; then
  case "$(realpath -m "$ROOT")" in /tmp/*) ;; *) echo "worker-sandbox: sandbox test env refused" >&2; exit 95;; esac
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
