#!/usr/bin/env bash
# worker-sandbox-hermes-usage.test.sh — regression control for the hermes --usage-file arm's
# systemd-run argv ordering.
#
# WHY. RUN is a flat array handed to systemd-run: everything up to the command element is a
# systemd-run OPTION (--property, --setenv, ...); everything from the command element onward is
# the target program's OWN argv. A --property appended after the command not only fails to apply
# (the mount never happens) — it is silently handed to the target program as a bogus CLI argument.
# This bit worker-sandbox.sh's hermes arm: the `--property BindPaths=...` for the usage-file mount
# landed after the `/usr/bin/env "$INNER_EXE" ...` command element, so the usage file was never
# bind-mounted and hermes received `--property BindPaths=...` as junk argv.
#
# APPROACH. The real script requires root + systemd-run to run its sandbox path. Off-box (and even
# on-box, to keep this hermetic and side-effect-free) we stub `id`, `systemd-run`, `chown`, and `install` on
# PATH ahead of any real ones: `id` reports uid 0 for the controller check and a fixed non-root
# uid/gid for the runner-account lookup; `systemd-run` just records "$@" and exits 0 instead of
# actually launching a unit; `install` performs the plain mkdir/copy/chmod it's asked for without
# the chown a non-root test process cannot perform. `getent`/`systemctl`/`mountpoint` are left
# unstubbed: the script already tolerates their absence (falls back to a disposable-root runner
# account; treats a stopped/unknown unit as already-stopped during cleanup), so this exercises the
# REAL code path, not a rewritten one. This works identically on Linux and on Windows Git Bash.
#
# THE ASSERTION: in the captured systemd-run argv, no element beginning with --property or
# --setenv may appear at or after the first `/usr/bin/env` element (the start of the command argv).
# A second assertion pins the fix's positive intent: the usage-file BindPaths property must still
# be present somewhere in the (pre-command) argv — an ordering fix that silently dropped the
# property instead of relocating it would pass the first assertion for the wrong reason.
#
#   run: bash scripts/tests/worker-sandbox-hermes-usage.test.sh
set -uo pipefail
export LC_ALL=C
SRC="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
SANDBOX_SCRIPT="$SRC/scripts/worker-sandbox.sh"
fails=0
ok(){ printf 'ok    %s\n' "$1"; }
no(){ printf 'FAIL  %s\n' "$1"; fails=$((fails+1)); }

for tool in bash mktemp realpath chown install; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "SKIP - worker-sandbox-hermes-usage.test: required tool '$tool' is absent off-box"
    exit 0
  }
done
[ -f "$SANDBOX_SCRIPT" ] || { echo "SKIP - worker-sandbox-hermes-usage.test: $SANDBOX_SCRIPT not found"; exit 0; }

TMP="$(mktemp -d)" || { echo "SKIP - worker-sandbox-hermes-usage.test: mktemp -d failed"; exit 0; }
trap 'rm -rf "$TMP"' EXIT

BIN="$TMP/bin"; mkdir -p "$BIN"
R="$TMP/repo"; mkdir -p "$R/scripts"
cp "$SANDBOX_SCRIPT" "$R/scripts/worker-sandbox.sh"
cp "$SRC/scripts/phase5_safety.py" "$R/scripts/phase5_safety.py"
chmod +x "$R/scripts/worker-sandbox.sh"

# --- stub: id — uid 0 for the bare controller check; a fixed non-root id for the runner lookup.
cat > "$BIN/id" <<'STUB'
#!/usr/bin/env bash
case "${1:-}" in
  -u) if [ -n "${2:-}" ]; then echo 65534; else echo 0; fi ;;
  -g) if [ -n "${2:-}" ]; then echo 65534; else echo 0; fi ;;
  *)  echo 0 ;;
esac
STUB
chmod +x "$BIN/id"

# --- stub: chown — same reasoning as install below: a non-root test process cannot change
# ownership, and the real script performs it only as the actual root controller on the box.
# Succeeding silently keeps the REAL code path running through to the systemd-run capture.
cat > "$BIN/chown" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
chmod +x "$BIN/chown"

# --- stub: install — mkdir/copy/chmod only; no chown (a non-root test process cannot chown to
# uid 0, which the real script legitimately does on the box as the actual root controller).
cat > "$BIN/install" <<'STUB'
#!/usr/bin/env bash
dflag=0; mode=""; positional=()
while [ $# -gt 0 ]; do
  case "$1" in
    -d) dflag=1; shift ;;
    -o) shift 2 ;;
    -g) shift 2 ;;
    -m) mode="$2"; shift 2 ;;
    *) positional+=("$1"); shift ;;
  esac
done
if [ "$dflag" = 1 ]; then
  for d in "${positional[@]}"; do mkdir -p "$d"; [ -n "$mode" ] && chmod "$mode" "$d"; done
else
  n=${#positional[@]}; dest="${positional[$((n-1))]}"
  for ((j=0; j<n-1; j++)); do cp -f "${positional[$j]}" "$dest"; done
  [ -n "$mode" ] && chmod "$mode" "$dest"
fi
exit 0
STUB
chmod +x "$BIN/install"

# --- stub: hermes — never actually executed (systemd-run is stubbed too); only needs to resolve.
cat > "$BIN/hermes" <<'STUB'
#!/usr/bin/env bash
exit 0
STUB
chmod +x "$BIN/hermes"

mk_systemd_run_stub(){ # argv-capture-file
  cat > "$BIN/systemd-run" <<STUB
#!/usr/bin/env bash
: > "$1"
for a in "\$@"; do printf '%s\n' "\$a" >> "$1"; done
exit 0
STUB
  chmod +x "$BIN/systemd-run"
}

run_sandbox(){ # worktree extra-args... ; writes stdout/stderr/rc into globals
  local wt="$1"; shift
  set +e
  PATH="$BIN:$PATH" RECURSION_ROOT="$R" \
    bash "$R/scripts/worker-sandbox.sh" \
      --engine hermes --worktree "$wt" --prompt "hello" \
      --role implementer --network-policy none "$@" \
      >"$TMP/stdout.log" 2>"$TMP/stderr.log"
  RC=$?
  set -e
}

assert_no_property_after_command(){ # argv-file -> sets ASSERT_OK, ASSERT_MSG
  local file="$1" cmd_idx=-1 i=0 line bad=0 detail=""
  while IFS= read -r line; do
    if [ "$cmd_idx" = -1 ] && [ "$line" = "/usr/bin/env" ]; then cmd_idx=$i; fi
    if [ "$cmd_idx" != -1 ] && [ "$i" -gt "$cmd_idx" ]; then
      case "$line" in
        --property*|--setenv*) bad=$((bad+1)); detail="$detail [$i]='$line'" ;;
      esac
    fi
    i=$((i+1))
  done < "$file"
  if [ "$cmd_idx" = -1 ]; then
    ASSERT_OK=1; ASSERT_MSG="no /usr/bin/env command element found in argv at all"
  elif [ "$bad" -gt 0 ]; then
    ASSERT_OK=1; ASSERT_MSG="$bad --property/--setenv element(s) after the command (index $cmd_idx):$detail"
  else
    ASSERT_OK=0; ASSERT_MSG="command at index $cmd_idx, $i total elements, none offending"
  fi
}

# --- 1) hermes + --usage-file: the BindPaths property must precede the command, and still exist -
WT1="$TMP/wt1"; mkdir -p "$WT1"
USAGE_FILE="$TMP/usage.json"
mk_systemd_run_stub "$TMP/argv-1.out"
run_sandbox "$WT1" --usage-file "$USAGE_FILE"
if [ "$RC" -eq 0 ]; then
  ok "hermes + --usage-file: worker-sandbox.sh exits 0"
else
  no "hermes + --usage-file: worker-sandbox.sh exited $RC"
  sed 's/^/        /' "$TMP/stderr.log"
fi
if [ -f "$TMP/argv-1.out" ]; then
  assert_no_property_after_command "$TMP/argv-1.out"
  if [ "$ASSERT_OK" -eq 0 ]; then
    ok "★ no --property/--setenv element appears at/after the command argv ($ASSERT_MSG)"
  else
    no "★ a --property/--setenv element leaked into the command's own argv ($ASSERT_MSG)"
    cat -n "$TMP/argv-1.out" | sed 's/^/        /'
  fi
  if grep -qF "BindPaths=$USAGE_FILE:/tmp/recursion-worker-usage.json" "$TMP/argv-1.out"; then
    ok "the usage-file BindPaths property is still present (not silently dropped)"
  else
    no "the usage-file BindPaths property is missing from the composed argv"
  fi
  if grep -qxF -- "--usage-file" "$TMP/argv-1.out" \
     && grep -qxF "/tmp/recursion-worker-usage.json" "$TMP/argv-1.out"; then
    ok "hermes's own --usage-file flag is still present"
  else
    no "hermes's own --usage-file flag is missing"
  fi
  # The hermes arm masks /run and /var/run as InaccessiblePaths, and systemd drops any mount
  # entry shadowed by an inaccessible path — so a bind TARGET under /run is silently discarded.
  # Bind sources under the host /run are equally suspect here. PrivateTmp=/tmp is the sanctioned
  # target; this pins the retarget so nobody moves it back.
  if grep -E '^(Bind(ReadOnly)?Paths=)?[^=]*:/(run|var/run)(/|$)' "$TMP/argv-1.out" \
       | grep -q .; then
    no "a bind mount targets the masked /run — systemd will drop it (shadowed by InaccessiblePaths)"
    grep -E ':/(run|var/run)(/|$)' "$TMP/argv-1.out" | sed 's/^/        /'
  else
    ok "no bind mount targets the masked /run or /var/run"
  fi
else
  no "hermes + --usage-file: systemd-run stub never captured argv (script exited before dispatch)"
fi

# --- 2) hermes without --usage-file: behavior is unchanged (no usage-file property/flag at all) -
WT2="$TMP/wt2"; mkdir -p "$WT2"
mk_systemd_run_stub "$TMP/argv-2.out"
run_sandbox "$WT2"
if [ "$RC" -eq 0 ]; then
  ok "hermes without --usage-file: worker-sandbox.sh exits 0"
else
  no "hermes without --usage-file: worker-sandbox.sh exited $RC"
fi
if [ -f "$TMP/argv-2.out" ]; then
  if grep -q -- '--usage-file\|recursion-worker-usage' "$TMP/argv-2.out"; then
    no "an empty USAGE_FILE must add no usage-file property or flag, but one was found"
    cat -n "$TMP/argv-2.out" | sed 's/^/        /'
  else
    ok "an empty USAGE_FILE adds no usage-file property or flag (behavior preserved)"
  fi
else
  no "hermes without --usage-file: systemd-run stub never captured argv"
fi

echo
[ "$fails" -eq 0 ] && { echo "worker-sandbox-hermes-usage: ALL PASS"; exit 0; }
echo "worker-sandbox-hermes-usage: $fails FAILED"; exit 1
