#!/usr/bin/env bash
# capacity.sh — decide whether this box can take on one more piece of work, before it starts.
#
# WHY IT IS NOT JUST A CONCURRENCY NUMBER. conduct.sh bounds parallelism with
# RECURSION_CONDUCT_CONCURRENCY, a fixed count, and a fixed count assumes every unit of work
# costs the same. On this box they do not, and the difference is large: a build ARM is an LLM
# call, so it spends its life blocked on the network and costs almost nothing locally, while a
# GATE is `node --test` over a real corpus and is the thing that actually eats the machine
# (2 cores, 3.8G, 2G swap — measured 2026-08-05: "arms are I/O-bound, GATES are the constraint").
# Two arms is comfortable. Two heavy gates is a thrash: they push into swap, every gate gets
# slower, and the timeouts that fire look like flaky tests rather than like a starved box.
#
# So capacity is per-CLASS, and heavy gates additionally hold a BOX-WIDE MUTEX.
#
# ★ AN UNREADABLE METRIC IS NOT A HEALTHY ONE. If /proc or df cannot be read, this exits 3
# ("cannot tell") rather than admitting. The same discipline as resync.sh: a probe that could not
# answer must not be allowed to answer, and the default answer must not be the permissive one.
#
#   capacity.sh check <arm|gate|light>     0 admit · 3 cannot tell · 4 defer (reason on stdout)
#   capacity.sh decide <class> <mem_mb> <load1> <disk_mb> <swap_mb>
#                                          the pure decision, no collection — what the tests drive
#   capacity.sh heavy acquire <tag>        take the box-wide heavy-gate lock (0 got it, 4 busy)
#   capacity.sh heavy release              give it back
#   capacity.sh heavy status               who holds it
#   capacity.sh report                     one block for the Hermes brief
#
# Thresholds are env-overridable so a bigger box does not need a code change:
#   RECURSION_CAP_ARM_MEM_MB   (400)   RECURSION_CAP_GATE_MEM_MB   (900)
#   RECURSION_CAP_ARM_LOADX    (2.0)   RECURSION_CAP_GATE_LOADX    (1.5)   x cores
#   RECURSION_CAP_ARM_DISK_MB  (2048)  RECURSION_CAP_GATE_DISK_MB  (3072)
#   RECURSION_CAP_ARM_SWAP_MB  (512)   RECURSION_CAP_GATE_SWAP_MB  (256)
set -uo pipefail
export LC_ALL=C
ROOT="${RECURSION_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
# ★ A root we cannot enter is not a healthy box, it is an unmeasurable one. Without this
# the `cd` failed, the script continued in whatever directory it started in (no `set -e`),
# and df measured a filesystem nobody asked about — a confident answer about the wrong box.
cd "$ROOT" 2>/dev/null || { echo "CANNOT TELL: RECURSION_ROOT '$ROOT' is not a directory"; exit 3; }
[ -f .env ] && { set -a; . ./.env; set +a; }
# .env pins RECURSION_ROOT for the deployed checkout. Sourcing it must never RETARGET a
# caller who passed a different root: that silently made a "sandbox" enqueue ten decisions
# into production on 2026-08-12. ROOT and RECURSION_ROOT agree from here on.
RECURSION_ROOT="$ROOT"; export RECURSION_ROOT
# Git Bash's $$ / $PPID are MSYS identities, while the bundled Windows Python runtime
# witnesses Win32 identities.  The parent owns a lock beyond this helper's short lifetime;
# retain the explicit override for callers that already have a translated owner.
PROBE_PID="$(cat /proc/$$/winpid 2>/dev/null || echo $$)"
OWNER_PID="${RECURSION_HEAVY_PID:-$(cat /proc/$PPID/winpid 2>/dev/null || echo $PPID)}"
LOCKDIR="$ROOT/state/.locks"; mkdir -p "$LOCKDIR" 2>/dev/null || true
HEAVY="$LOCKDIR/heavy-gate.lock"
CMD="${1:-report}"; shift 2>/dev/null || true

CORES="$(nproc 2>/dev/null || echo 1)"
num(){ case "${1:-}" in ''|*[!0-9.]*) return 1 ;; *) return 0 ;; esac; }

# --- collection. Each returns empty on failure; empty propagates to "cannot tell". -----------
mem_avail_mb(){ awk '/^MemAvailable:/{printf "%d",$2/1024; found=1} END{if(!found) exit 1}' /proc/meminfo 2>/dev/null; }
swap_used_mb(){ awk '/^SwapTotal:/{t=$2} /^SwapFree:/{f=$2; printf "%d",(t-f)/1024; found=1} END{if(!found) exit 1}' /proc/meminfo 2>/dev/null; }
load1(){ cut -d' ' -f1 /proc/loadavg 2>/dev/null; }
disk_free_mb(){ df -Pk "$ROOT" 2>/dev/null | awk 'NR==2{printf "%d",$4/1024}'; }

# --- the pure decision. One definition, called by `check` and driven directly by the tests, so
# the suite exercises the code that runs rather than a restatement of its rules. --------------
decide(){ # decide <class> <mem_mb> <load1> <disk_mb> <swap_mb> -> 0 admit / 4 defer
  local class="$1" mem="$2" load="$3" disk="$4" swap="$5" mmin lmax dmin smax
  case "$class" in
    gate)  mmin="${RECURSION_CAP_GATE_MEM_MB:-900}"; lmax="${RECURSION_CAP_GATE_LOADX:-1.5}"
           dmin="${RECURSION_CAP_GATE_DISK_MB:-3072}"; smax="${RECURSION_CAP_GATE_SWAP_MB:-256}" ;;
    arm)   mmin="${RECURSION_CAP_ARM_MEM_MB:-400}";  lmax="${RECURSION_CAP_ARM_LOADX:-2.0}"
           dmin="${RECURSION_CAP_ARM_DISK_MB:-2048}"; smax="${RECURSION_CAP_ARM_SWAP_MB:-512}" ;;
    light) mmin=100; lmax=8.0; dmin=256; smax=1800 ;;
    *) echo "capacity: unknown class '$class'"; return 2 ;;
  esac
  local lcap; lcap="$(awk -v c="$CORES" -v x="$lmax" 'BEGIN{printf "%.2f", c*x}')"

  [ "$mem"  -lt "$mmin" ] 2>/dev/null && { echo "DEFER $class: ${mem}MB available, needs ${mmin}MB"; return 4; }
  [ "$disk" -lt "$dmin" ] 2>/dev/null && { echo "DEFER $class: ${disk}MB disk free, needs ${dmin}MB"; return 4; }
  [ "$swap" -gt "$smax" ] 2>/dev/null && { echo "DEFER $class: ${swap}MB swap in use (>${smax}MB) — the box is already thrashing"; return 4; }
  if awk -v l="$load" -v c="$lcap" 'BEGIN{exit !(l>c)}'; then
    echo "DEFER $class: load $load over $lcap (${CORES} cores x $lmax)"; return 4
  fi
  # A heavy gate is exclusive regardless of headroom: two gates that each FIT still ruin each
  # other's timings, and a gate whose verdict depends on what else was running is not a gate.
  if [ "$class" = "gate" ] && ! heavy_available; then
    echo "DEFER gate: the heavy-gate lock is held by $(cat "$HEAVY/holder" 2>/dev/null || echo '?')"; return 4
  fi
  echo "ADMIT $class: ${mem}MB mem, load $load/$lcap, ${disk}MB disk, ${swap}MB swap"; return 0
}

heavy_held(){ [ -d "$HEAVY" ]; }
heavy_available(){
  [ -x "$ROOT/scripts/runtime-state.py" ] || return 1
  python3 "$ROOT/scripts/runtime-state.py" lock-acquire "$HEAVY" "$PROBE_PID" >/dev/null 2>&1 \
    || return 1
  python3 "$ROOT/scripts/runtime-state.py" lock-release "$HEAVY" "$PROBE_PID" >/dev/null 2>&1
}

case "$CMD" in

decide)
  [ "$#" -ge 5 ] || { echo "usage: capacity.sh decide <class> <mem_mb> <load1> <disk_mb> <swap_mb>"; exit 2; }
  decide "$1" "$2" "$3" "$4" "$5" ;;

check)
  CLASS="${1:?usage: capacity.sh check <arm|gate|light>}"
  MEM="$(mem_avail_mb)"; LOAD="$(load1)"; DISK="$(disk_free_mb)"; SWAP="$(swap_used_mb)"
  # ★ Fail to "cannot tell", never to "fine". Admitting on an unreadable metric is how a
  # governor becomes decorative exactly when the box is in the state it exists to catch.
  for pair in "mem:$MEM" "load:$LOAD" "disk:$DISK" "swap:$SWAP"; do
    v="${pair#*:}"
    if [ -z "$v" ] || ! num "$v"; then
      echo "CANNOT TELL: ${pair%%:*} unreadable (got '${v}') — refusing to call that healthy"; exit 3
    fi
  done
  decide "$CLASS" "$MEM" "$LOAD" "$DISK" "$SWAP" ;;

heavy)
  SUB="${1:-status}"; TAG="${2:-${RECURSION_HEAVY_TAG:-unnamed}}"
  case "$SUB" in
    acquire)
      if python3 "$ROOT/scripts/runtime-state.py" lock-acquire "$HEAVY" "$OWNER_PID" \
           >/dev/null 2>&1; then
        if ! printf '%s (pid %s, since %s)\n' "$TAG" "$OWNER_PID" "$(date -u +%FT%TZ)" \
             > "$HEAVY/holder"; then
          python3 "$ROOT/scripts/runtime-state.py" lock-release "$HEAVY" "$OWNER_PID" \
            >/dev/null 2>&1 || true
          echo "capacity: heavy lock metadata write failed" >&2; exit 3
        fi
        echo "ACQUIRED $TAG"; exit 0
      fi
      echo "BUSY $(cat "$HEAVY/holder" 2>/dev/null || echo '?')"; exit 4 ;;
    release)
      python3 "$ROOT/scripts/runtime-state.py" lock-release "$HEAVY" "$OWNER_PID" \
        >/dev/null 2>&1 || { echo "capacity: heavy lock release failed" >&2; exit 3; }
      echo "RELEASED" ;;
    status)  heavy_held && echo "HELD $(cat "$HEAVY/holder" 2>/dev/null)" || echo "FREE" ;;
    *) echo "usage: capacity.sh heavy <acquire|release|status> [tag]"; exit 2 ;;
  esac ;;

report)
  MEM="$(mem_avail_mb)"; LOAD="$(load1)"; DISK="$(disk_free_mb)"; SWAP="$(swap_used_mb)"
  echo "cores: $CORES  load: ${LOAD:-?}  mem avail: ${MEM:-?}MB  swap used: ${SWAP:-?}MB  disk free: ${DISK:-?}MB"
  echo "in-flight arms: $(find "$LOCKDIR" -maxdepth 1 \( -name 'project-*.lock' -o -name 'ws-*.lock' \) 2>/dev/null | wc -l | tr -d ' ')"
  echo "heavy gate: $(heavy_held && cat "$HEAVY/holder" 2>/dev/null || echo FREE)"
  for c in arm gate; do
    out="$(RECURSION_ROOT="$ROOT" bash "$0" check "$c" 2>&1)"; printf '  %s\n' "$out"
  done ;;

*) sed -n '20,27p' "$0"; exit 2 ;;
esac
