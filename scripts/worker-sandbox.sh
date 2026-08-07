#!/usr/bin/env bash
# Launch one model worker as a hardened transient service. systemd constructs the private
# mount namespace as root, then drops to the dedicated runner uid before executing the arm.
set -euo pipefail

ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
ENGINE=""; WT=""; PROMPT=""; MODEL=""; USAGE_FILE=""; ROLE="implementer"
NETWORK_POLICY="provider-only"; READ_ONLY_WORKTREE=0; EVIDENCE_DIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --engine) ENGINE="${2:-}"; shift 2 ;;
    --worktree) WT="${2:-}"; shift 2 ;;
    --prompt) PROMPT="${2:-}"; shift 2 ;;
    --model) MODEL="${2:-}"; shift 2 ;;
    --usage-file) USAGE_FILE="${2:-}"; shift 2 ;;
    --role) ROLE="${2:-}"; shift 2 ;;
    --network-policy) NETWORK_POLICY="${2:-}"; shift 2 ;;
    --read-only-worktree) READ_ONLY_WORKTREE=1; shift ;;
    --evidence-dir) EVIDENCE_DIR="${2:-}"; shift 2 ;;
    *) echo "worker-sandbox: unknown argument: $1" >&2; exit 2 ;;
  esac
done
case "$ENGINE" in claude|hermes) ;; *) echo "worker-sandbox: invalid engine" >&2; exit 92;; esac
case "$ROLE" in implementer|verifier) ;; *) echo "worker-sandbox: invalid worker role" >&2; exit 92;; esac
case "$NETWORK_POLICY" in provider-only|none) ;; *) echo "worker-sandbox: invalid network policy" >&2; exit 92;; esac
[ -d "$WT" ] || { echo "worker-sandbox: worktree is missing" >&2; exit 95; }
WT="$(realpath -e "$WT")"
[ -z "$EVIDENCE_DIR" ] || { mkdir -p "$EVIDENCE_DIR"; EVIDENCE_DIR="$(realpath -e "$EVIDENCE_DIR")"; }
export RECURSION_WORKER_ROLE="$ROLE"
[ -z "$EVIDENCE_DIR" ] || export RECURSION_EVIDENCE_DIR="$EVIDENCE_DIR"

case "${RECURSION_TEST_WORKER:-}" in
  logical)
    # Existing hermetic envelope tests exercise the logical scope gate, not the OS boundary.
    # This bypass is accepted only for disposable /tmp controllers and is never valid on /opt.
    case "$(realpath -m "$ROOT")" in /tmp/*) ;; *) echo "worker-sandbox: test bypass refused" >&2; exit 95;; esac
    case "$ENGINE" in
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
    esac
    exit $?
    ;;
  ""|sandbox) ;;
  *) echo "worker-sandbox: invalid test mode" >&2; exit 95 ;;
esac

[ "$(id -u)" = 0 ] || { echo "worker-sandbox: controller must be root" >&2; exit 95; }
command -v systemd-run >/dev/null 2>&1 \
  || { echo "worker-sandbox: systemd-run unavailable" >&2; exit 95; }

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
[ "$RUNNER_UID" != 0 ] && [ "$RUNNER_GID" != 0 ] \
  || { echo "worker-sandbox: runner identity is privileged" >&2; exit 95; }

case "$ENGINE" in
  claude) EXE="$(command -v claude 2>/dev/null || true)"; [ -n "$EXE" ] || exit 90 ;;
  hermes) EXE="$(command -v hermes 2>/dev/null || true)"; [ -n "$EXE" ] || exit 94 ;;
esac
EXE_REAL="$(realpath -e "$EXE")"

# The disposable worktree is the only writable project mount. A test stub outside /usr is copied
# in as one read-only executable and removed before the controller evaluates the diff.
chown -R "$RUNNER_UID:$RUNNER_GID" "$WT"
INNER_EXE="$EXE"
SANDBOX_BIN="$WT/.recursion-sandbox"
case "$EXE_REAL" in
  /usr/*) ;;
  *)
    rm -rf -- "$SANDBOX_BIN"; mkdir -p "$SANDBOX_BIN"
    cp "$EXE_REAL" "$SANDBOX_BIN/$ENGINE"; chmod 0555 "$SANDBOX_BIN/$ENGINE"
    INNER_EXE="/workspace/.recursion-sandbox/$ENGINE"
    ;;
esac

safe_engine="${ENGINE//[^A-Za-z0-9_.-]/-}"
UNIT="recursion-worker-${safe_engine}-$$-${RANDOM}.service"
client_pid=""
stop_unit(){
  systemctl kill --kill-whom=all --signal=TERM "$UNIT" >/dev/null 2>&1 || true
  local i
  for i in $(seq 1 50); do
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
  stop_unit || true
  rm -rf -- "$SANDBOX_BIN"
  chown -R 0:0 "$WT" 2>/dev/null || true
}
trap 'cleanup; exit 143' TERM INT
trap cleanup EXIT

RUN=(systemd-run --quiet --wait --collect --pipe --service-type=exec --unit "$UNIT"
  --uid "$RUNNER_USER" --gid "$RUNNER_GID" --working-directory /workspace
  --property NoNewPrivileges=yes --property CapabilityBoundingSet=
  --property AmbientCapabilities= --property PrivateTmp=yes --property PrivateDevices=yes
  --property ProtectSystem=strict --property ProtectHome=yes
  --property ProtectKernelTunables=yes --property ProtectKernelModules=yes
  --property ProtectKernelLogs=yes --property ProtectControlGroups=yes
  --property RestrictSUIDSGID=yes --property LockPersonality=yes
  --property UMask=0077 --property KillMode=control-group
  --property "InaccessiblePaths=/opt /srv"
  --property "InaccessiblePaths=-/workspace/.env -/workspace/.git -/workspace/state -/workspace/CONTROL_PLANE.md -/workspace/ANCHOR.md -/workspace/CLAUDE.md"
  --property "ReadOnlyPaths=-/workspace/scripts -/workspace/.github"
  --setenv HOME=/home/runner --setenv USER="$RUNNER_USER" --setenv LOGNAME="$RUNNER_USER"
  --setenv LANG=C.UTF-8 --setenv PATH=/usr/local/bin:/usr/bin:/bin
  --setenv RECURSION_WORKER_ROLE="$ROLE")

if [ "$READ_ONLY_WORKTREE" = 1 ]; then
  RUN+=(--property "BindReadOnlyPaths=$WT:/workspace" --property ReadOnlyPaths=/workspace)
else
  RUN+=(--property "BindPaths=$WT:/workspace" --property ReadWritePaths=/workspace)
fi
if [ -n "$EVIDENCE_DIR" ]; then
  chown -R "$RUNNER_UID:$RUNNER_GID" "$EVIDENCE_DIR"
  RUN+=(--property "BindPaths=$EVIDENCE_DIR:/evidence" --property ReadWritePaths=/evidence
        --setenv RECURSION_EVIDENCE_DIR=/evidence)
fi
if [ "$NETWORK_POLICY" = none ]; then RUN+=(--property PrivateNetwork=yes); fi
for name in RECURSION_VERIFICATION_COMMIT RECURSION_IMPLEMENTER_RUN_ID; do
  value="${!name:-}"; [ -z "$value" ] || RUN+=(--setenv "$name=$value")
done

if [ -n "$RUNNER_HOME" ] && [ -d "$RUNNER_HOME" ]; then
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
  claude)
    RUN+=(/usr/bin/env "$INNER_EXE" -p "$PROMPT" --permission-mode acceptEdits --allowedTools 'Bash(node:*)')
    [ -n "$MODEL" ] && RUN+=(--model "$MODEL")
    ;;
  hermes)
    RUN+=(/usr/bin/env "$INNER_EXE" -z "$PROMPT" -m "${MODEL:-gpt-5.6-sol}" -t file,terminal --yolo)
    if [ -n "$USAGE_FILE" ]; then
      : > "$USAGE_FILE"; chown "$RUNNER_UID:$RUNNER_GID" "$USAGE_FILE"
      RUN+=(--property "BindPaths=$USAGE_FILE:/run/recursion-worker-usage.json")
      RUN+=(--usage-file /run/recursion-worker-usage.json)
    fi
    ;;
esac

"${RUN[@]}" & client_pid=$!
if wait "$client_pid"; then rc=0; else rc=$?; fi
client_pid=""
exit "$rc"
