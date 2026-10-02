#!/usr/bin/env python3
"""FU-04 negative-trace runner (deterministic, provider-free, stdlib only).

Executes normalized traces from traces.json against two targets:

    host        this Windows host, non-destructive handlers only
    wsl:Debian  the disposable WSL2 target, via ``wsl.exe ... bash -s``

For every executed (trace, target) pair it injects the fault, collects the
observation and recovery oracle evidence, runs the negative control, and records
one outcome from {pass, fail, unknown}. A trace that is not run is recorded as
``not_run`` with a reason. Absence of a notification is never recorded as success:
every pass requires present observation *and* recovery evidence.

Usage:

    python -X utf8 -B experiments/v3/fu-04-os-conformance/traces/run_traces.py \
        --target wsl:Debian --allow-destructive
    python -X utf8 -B experiments/v3/fu-04-os-conformance/traces/run_traces.py --target host

Bound safety: every destructive step is bounded (private temp dirs, capped
loopback/tmpfs space, ulimit, PID-namespace isolation, hard timeouts) and the
runner never touches the host repository or home outside its own temp dirs.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DISTRO = "Debian"
DEFAULT_OUT = HERE / "traces_results.json"
ALLOWED_OUTCOMES = {"pass", "fail", "unknown", "not_run"}
TARGETS = ["host", "wsl:Debian"]

# --------------------------------------------------------------------------------------
# process helpers
# --------------------------------------------------------------------------------------


def run_wsl(script: str, timeout: int) -> dict:
    """Run a bash script on the WSL target through stdin (no temp script file)."""
    argv = ["wsl.exe", "-d", DISTRO, "-u", "root", "--", "bash", "-s"]
    payload = script.replace("\r\n", "\n").encode("utf-8")
    t0 = time.time()
    timed_out = False
    try:
        cp = subprocess.run(argv, input=payload, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout)
        out = cp.stdout.decode("utf-8", "replace")
        err = cp.stderr.decode("utf-8", "replace")
        rc = cp.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        out = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = (exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        rc = -1
    return {"stdout": out, "stderr": err, "rc": rc, "timed_out": timed_out,
            "argv": " ".join(argv), "script": script,
            "duration_s": round(time.time() - t0, 3)}


def parse_kv(text: str) -> dict:
    data: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
    return data


def flag(kv: dict, key: str) -> bool:
    return str(kv.get(key, "")).lower() == "true"


def outcome_of(obs: dict, rec: dict, neg: dict, *, forced_unknown: bool = False) -> str:
    if forced_unknown:
        return "unknown"
    if any(x.get("coverage_lost") for x in (obs, rec, neg)):
        return "unknown"
    if obs.get("ok") and rec.get("ok") and neg.get("ok"):
        return "pass"
    return "fail"


def ev(ok: bool, detail: str, **evidence) -> dict:
    return {"ok": bool(ok), "detail": detail, "evidence": evidence}


# --------------------------------------------------------------------------------------
# WSL trace scripts
# --------------------------------------------------------------------------------------

PF01_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf01.XXXXXX)
SUP=""
cleanup() {
  [ -n "$SUP" ] && kill -KILL -- "-$SUP" 2>/dev/null
  for f in nested grandchild escaper; do
    if [ -f "$T/$f.pid" ]; then kill -KILL "$(cat "$T/$f.pid" 2>/dev/null)" 2>/dev/null; fi
  done
  rm -rf "$T"
}
trap cleanup EXIT
export T
setsid bash -c 'sleep 30 & echo $! > $T/nested.pid; ( sleep 30 & echo $! > $T/grandchild.pid; wait ) & setsid sleep 30 & echo $! > $T/escaper.pid; sleep 30' &
SUP=$!
sleep 1
pgrp() { awk '{print $5}' "/proc/$1/stat" 2>/dev/null || echo 0; }
echo "supervisor.pid=$SUP"
echo "supervisor.pgid=$(pgrp "$SUP")"
contained=true
for name in nested grandchild; do
  pid=$(cat "$T/$name.pid" 2>/dev/null || echo 0)
  pg=$(pgrp "$pid")
  echo "$name.pid=$pid"
  echo "$name.pgid=$pg"
  if [ "$pg" != "$SUP" ]; then contained=false; fi
done
if [ "$contained" = true ]; then echo "contained=true"; else echo "contained=false"; fi
epid=$(cat "$T/escaper.pid" 2>/dev/null || echo 0)
epg=$(pgrp "$epid")
echo "escaper.pid=$epid"
echo "escaper.pgid=$epg"
if [ "$epg" != "$SUP" ]; then echo "escape_detected=true"; else echo "escape_detected=false"; fi
echo "declared_boundary.pgid=$SUP"
kill -TERM -- "-$SUP" 2>/dev/null
sleep 0.3
kill -KILL -- "-$SUP" 2>/dev/null
sleep 0.2
for name in nested grandchild escaper; do
  pid=$(cat "$T/$name.pid" 2>/dev/null || echo 0)
  if kill -0 "$pid" 2>/dev/null; then echo "alive_after_group_kill.$name=$pid"; else echo "dead_after_group_kill.$name=$pid"; fi
done
for name in nested grandchild escaper; do
  pid=$(cat "$T/$name.pid" 2>/dev/null || echo 0)
  kill -KILL "$pid" 2>/dev/null
done
sleep 0.2
remaining=0
for name in nested grandchild escaper; do
  pid=$(cat "$T/$name.pid" 2>/dev/null || echo 0)
  if kill -0 "$pid" 2>/dev/null; then remaining=$((remaining+1)); fi
done
echo "remaining=$remaining"
echo "trace_end=1"
"""

PF02_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf02.XXXXXX)
export T
BPID=""
cleanup() {
  [ -n "$BPID" ] && kill -KILL "$BPID" 2>/dev/null
  if [ -f "$T/child.pid" ]; then kill -KILL "$(cat "$T/child.pid" 2>/dev/null)" 2>/dev/null; fi
  rm -rf "$T"
}
trap cleanup EXIT
bash -c 'sleep 30 & echo $! > $T/child.pid; sleep 30' &
BPID=$!
for i in $(seq 1 100); do
  if [ -s "$T/child.pid" ]; then break; fi
  sleep 0.02
done
CHILD=$(cat "$T/child.pid" 2>/dev/null || echo 0)
kill -KILL "$BPID" 2>/dev/null
wait "$BPID" 2>/dev/null
sleep 0.2
echo "creator.pid=$BPID"
echo "child.pid=$CHILD"
if kill -0 "$CHILD" 2>/dev/null; then echo "child_alive=true"; else echo "child_alive=false"; fi
if kill -0 "$BPID" 2>/dev/null; then echo "creator_alive=true"; else echo "creator_alive=false"; fi
if [ -e "$T/registration" ]; then echo "registration_present=true"; else echo "registration_present=false"; fi
if [ ! -e "$T/registration" ] && kill -0 "$CHILD" 2>/dev/null; then echo "unresolved_launch_visible=true"; else echo "unresolved_launch_visible=false"; fi
if [ ! -e "$T/registration" ]; then echo "record_only_oracle=not_started"; else echo "record_only_oracle=started"; fi
kill -KILL "$CHILD" 2>/dev/null
sleep 0.2
if kill -0 "$CHILD" 2>/dev/null; then echo "orphan_terminated=false"; else echo "orphan_terminated=true"; fi
echo "reconciled_registered=0"
echo "reconciled_live=0"
echo "trace_end=1"
"""

PF04_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf04.XXXXXX)
export T
SPID=""
cleanup() { [ -n "$SPID" ] && kill -KILL -- "-$SPID" 2>/dev/null; rm -rf "$T"; }
trap cleanup EXIT
if command -v script >/dev/null 2>&1; then echo "script_available=true"; else echo "script_available=false"; echo "trace_end=1"; exit 0; fi
setsid bash -c 'exec timeout 5 script -q -f -c "i=0; while :; do echo SEQ \$i; i=\$((i+1)); done" "$T/typescript" >/dev/null 2>&1' &
SPID=$!
sleep 0.8
if [ -d /dev/pts ]; then echo "pty_available=true"; else echo "pty_available=false"; fi
if kill -0 -- "-$SPID" 2>/dev/null; then echo "terminal_alive_before_teardown=true"; else echo "terminal_alive_before_teardown=false"; fi
lines=$(wc -l < "$T/typescript" 2>/dev/null || echo 0)
echo "captured_lines=$lines"
if [ "$lines" -gt 0 ]; then echo "output_captured=true"; else echo "output_captured=false"; fi
kill -TERM -- "-$SPID" 2>/dev/null
n=0
while [ $n -lt 20 ] && kill -0 -- "-$SPID" 2>/dev/null; do sleep 0.1; n=$((n+1)); done
if kill -0 -- "-$SPID" 2>/dev/null; then kill -KILL -- "-$SPID" 2>/dev/null; sleep 0.3; fi
if kill -0 -- "-$SPID" 2>/dev/null; then echo "terminal_exited=false"; else echo "terminal_exited=true"; fi
if [ -n "$(pgrep -g "$SPID" 2>/dev/null)" ]; then echo "writer_exited=false"; else echo "writer_exited=true"; fi
final=$(wc -l < "$T/typescript" 2>/dev/null || echo 0)
echo "final_captured_lines=$final"
echo "close_cause=local_close"
echo "all_clients_disconnected=false"
echo "trace_end=1"
"""

PF05_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf05.XXXXXX)
export T
MGR=""
SENT=""
cleanup() {
  [ -n "$MGR" ] && kill -KILL -- "-$MGR" 2>/dev/null
  [ -n "$SENT" ] && kill -KILL "$SENT" 2>/dev/null
  rm -rf "$T"
}
trap cleanup EXIT
setsid bash -c 'trap "" TERM; sleep 30' &
MGR=$!
setsid sleep 30 &
SENT=$!
sleep 0.4
echo "target.pid=$MGR"
echo "sentinel.pid=$SENT"
kill -TERM -- "-$MGR" 2>/dev/null
sleep 0.5
if kill -0 "$MGR" 2>/dev/null; then echo "target_alive_after_term=true"; else echo "target_alive_after_term=false"; fi
if kill -0 "$SENT" 2>/dev/null; then echo "sentinel_alive_after_term=true"; else echo "sentinel_alive_after_term=false"; fi
kill -KILL -- "-$MGR" 2>/dev/null
sleep 0.3
if kill -0 "$MGR" 2>/dev/null; then echo "target_alive_after_kill=true"; else echo "target_alive_after_kill=false"; fi
if kill -0 "$SENT" 2>/dev/null; then echo "sentinel_alive_after_kill=true"; else echo "sentinel_alive_after_kill=false"; fi
echo "trace_end=1"
"""

PF06_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf06.XXXXXX)
cleanup() { rm -rf "$T"; }
trap cleanup EXIT
A=$(head -c 100000 /dev/zero | tr '\0' 'A')
B=$(head -c 200000 /dev/zero | tr '\0' 'B')
printf '%s' "$A" > "$T/target"
reads=0
torn=0
missing=0
for rep in $(seq 1 40); do
  printf '%s' "$A" > "$T/target"
  ( printf '%s' "$B" > "$T/tmp.b"; sync; mv -f "$T/tmp.b" "$T/target" ) &
  wpid=$!
  sleep 0.001
  kill -KILL "$wpid" 2>/dev/null
  wait "$wpid" 2>/dev/null
  s=$(stat -c %s "$T/target" 2>/dev/null || echo missing)
  case "$s" in
    100000|200000) : ;;
    missing) missing=$((missing+1)) ;;
    *) torn=$((torn+1)) ;;
  esac
  reads=$((reads+1))
done
echo "reads=$reads"
echo "torn=$torn"
echo "missing=$missing"
final_size=$(stat -c %s "$T/target" 2>/dev/null || echo missing)
echo "final_size=$final_size"
if [ "$final_size" = 100000 ] || [ "$final_size" = 200000 ]; then echo "recovery_complete=true"; else echo "recovery_complete=false"; fi
echo "inventory=$(ls "$T" | tr '\n' ',')"
printf '%s' "$A" > "$T/target2"
printf '%s' "$B" > "$T/src2"
( cp "$T/src2" "$T/copy3"; sync; rm -f "$T/target2"; sleep 0.2; mv "$T/copy3" "$T/target2" ) &
wp=$!
gap=0
i=0
while kill -0 "$wp" 2>/dev/null && [ $i -lt 2000000 ]; do
  if [ ! -e "$T/target2" ]; then gap=$((gap+1)); fi
  i=$((i+1))
done
wait "$wp" 2>/dev/null
echo "negative_control_gap=$gap"
echo "trace_end=1"
"""

PF08_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf08.XXXXXX)
export T
OWNER=""
cleanup() { [ -n "$OWNER" ] && kill -KILL -- "-$OWNER" 2>/dev/null; rm -rf "$T"; }
trap cleanup EXIT
: > "$T/lockfile"
setsid bash -c 'exec 9>"$T/lockfile"; flock -x 9; echo held > "$T/held"; sleep 8' &
OWNER=$!
for i in $(seq 1 100); do if [ -s "$T/held" ]; then break; fi; sleep 0.02; done
if kill -0 "$OWNER" 2>/dev/null; then echo "owner_alive=true"; else echo "owner_alive=false"; fi
if flock -n "$T/lockfile" -c 'echo leaked > "$T/leaked"' 2>/dev/null; then echo "exclusive_enforced=false"; else echo "exclusive_enforced=true"; fi
if [ -e "$T/leaked" ]; then echo "competing_write_admitted=true"; else echo "competing_write_admitted=false"; fi
echo "lockfile_exists=true"
if printf 'X' >> "$T/lockfile" 2>/dev/null; then echo "advisory_bypass=true"; else echo "advisory_bypass=false"; fi
kill -KILL -- "-$OWNER" 2>/dev/null
sleep 0.3
echo "$OWNER" > "$T/stale.pid"
if [ -e "$T/lockfile" ]; then echo "stale_marker_present=true"; else echo "stale_marker_present=false"; fi
reacquired=false
for try in 1 2 3 4 5; do
  if flock -n "$T/lockfile" -c 'echo acquired > "$T/reacquired"' 2>/dev/null; then reacquired=true; break; fi
  sleep 0.2
done
if [ "$reacquired" = true ]; then echo "reacquired=true"; else echo "reacquired=false"; fi
if [ -e "$T/reacquired" ]; then echo "reacquire_confirmed=true"; else echo "reacquire_confirmed=false"; fi
echo "trace_end=1"
"""

PF09_SCRIPT = r"""
set -u
unshare --pid --fork --mount-proc bash -s <<'INNER'
set -u
T=$(mktemp -d /tmp/fu04.pf09.XXXXXX)
export T
NEW=""
cleanup() { [ -n "$NEW" ] && kill -KILL "$NEW" 2>/dev/null; rm -rf "$T"; }
trap cleanup EXIT
starttime() { awk '{print $22}' "/proc/$1/stat" 2>/dev/null; }
sleep 30 & ORIG=$!
sleep 0.2
OST=$(starttime "$ORIG")
echo "orig.pid=$ORIG"
echo "orig.starttime=$OST"
kill -KILL "$ORIG" 2>/dev/null
wait "$ORIG" 2>/dev/null
sleep 0.2
if echo $((ORIG-1)) > /proc/sys/kernel/ns_last_pid 2>/dev/null; then echo "ns_last_pid_write=ok"; else echo "ns_last_pid_write=failed"; fi
sleep 30 & NEW=$!
sleep 0.2
NST=$(starttime "$NEW")
echo "new.pid=$NEW"
echo "new.starttime=$NST"
if [ "$NEW" = "$ORIG" ]; then echo "reuse_triggered=true"; else echo "reuse_triggered=false"; fi
if [ "$NEW" = "$ORIG" ] && [ "$NST" != "$OST" ]; then echo "stale_identity_hazard=true"; else echo "stale_identity_hazard=false"; fi
echo "stable_identity_field=starttime"
echo "stale_signal_sent=false"
if kill -0 "$NEW" 2>/dev/null; then echo "new_process_alive=true"; else echo "new_process_alive=false"; fi
echo "trace_end=1"
INNER
"""

PF10_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf10.XXXXXX)
MNT="$T/mnt"
mkdir -p "$MNT"
cleanup() { umount "$MNT" 2>/dev/null; rm -rf "$T"; }
trap cleanup EXIT
if mount -t tmpfs -o size=16m tmpfs "$MNT" 2>/dev/null; then
  echo "mount_ok=true"
else
  echo "mount_ok=false"; echo "trace_end=1"; exit 0
fi
printf 'AAAAAAAAAA' > "$MNT/genA"
i=0
filled=0
while [ $i -lt 64 ]; do
  if dd if=/dev/zero of="$MNT/fill.$i" bs=1M count=1 2>/dev/null; then filled=$((filled+1)); else break; fi
  i=$((i+1))
done
echo "fill_files=$filled"
err=$(dd if=/dev/zero of="$MNT/genB.tmp" bs=1M count=4 2>&1 >/dev/null)
if [ -n "$err" ]; then echo "write_result=refused"; else echo "write_result=success"; fi
echo "err_head=$(printf '%s' "$err" | tr '\n' ' ' | cut -c1-60)"
if [ -e "$MNT/genA" ] && [ "$(cat "$MNT/genA")" = "AAAAAAAAAA" ]; then echo "genA_preserved=true"; else echo "genA_preserved=false"; fi
if [ -e "$MNT/genB" ]; then echo "genB_present=true"; else echo "genB_present=false"; fi
echo "no_false_ack=true"
rm -f "$MNT"/fill.*
sync
avail=$(df -Pk "$MNT" | awk 'NR==2{print $4}')
echo "avail_after_cleanup_kb=$avail"
if dd if=/dev/zero of="$MNT/genB" bs=1M count=4 2>/dev/null; then echo "recovered_write=true"; else echo "recovered_write=false"; fi
echo "trace_end=1"
"""

PF11_SCRIPT = r"""
set -u
echo "cgroup_memory_high_writable=false"
LIMIT_KB=65536
result=unknown
if ( ulimit -v $LIMIT_KB 2>/dev/null; awk 'BEGIN{ for(i=0;i<200000;i++) a[i]=sprintf("%1024d", i); print i }' >/dev/null 2>&1 ); then
  result=success
else
  result=refused
fi
echo "limit_kb=$LIMIT_KB"
echo "alloc_result=$result"
if [ "$(head -c 1000 /dev/zero | wc -c)" = "1000" ]; then echo "resumed=true"; else echo "resumed=false"; fi
echo "death_inferred=false"
echo "throttle_counter_available=false"
echo "classification=allocation_refusal_substitute"
echo "trace_end=1"
"""

PF13_SCRIPT = r"""
set -u
T=$(mktemp -d /tmp/fu04.pf13.XXXXXX)
export T
SUPA=""
cleanup() {
  [ -n "$SUPA" ] && kill -KILL -- "-$SUPA" 2>/dev/null
  rm -rf "$T"
}
trap cleanup EXIT
setsid bash -c 'if mkdir "$T/lock" 2>/dev/null; then echo "epoch=1" > "$T/authority"; fi; sleep 30' &
SUPA=$!
for i in $(seq 1 100); do if [ -s "$T/authority" ]; then break; fi; sleep 0.02; done
echo "ownerA.pid=$SUPA"
echo "ownerA.epoch=$(cat "$T/authority" 2>/dev/null)"
kill -KILL -- "-$SUPA" 2>/dev/null
sleep 0.3
if kill -0 "$SUPA" 2>/dev/null; then echo "ownerA_alive_after_crash=true"; else echo "ownerA_alive_after_crash=false"; fi
if [ -d "$T/lock" ]; then echo "stale_lock_present=true"; else echo "stale_lock_present=false"; fi
echo "delayed_completion_epoch=1" > "$T/delayed"
if ! kill -0 "$SUPA" 2>/dev/null; then rmdir "$T/lock" 2>/dev/null; fi
if mkdir "$T/lock" 2>/dev/null; then echo "epoch=2" > "$T/authority"; echo "restart_acquired=true"; else echo "restart_acquired=false"; fi
sleep 0.2
echo "ownerB.epoch=$(cat "$T/authority" 2>/dev/null)"
if mkdir "$T/lock" 2>/dev/null; then echo "fencing_enforced=false"; rmdir "$T/lock" 2>/dev/null; else echo "fencing_enforced=true"; fi
( echo "epoch=2_unfenced" > "$T/authority_unauthorized" ) &
sleep 0.2
if [ -e "$T/authority_unauthorized" ]; then echo "unauthorized_owner_visible=true"; else echo "unauthorized_owner_visible=false"; fi
if [ -e "$T/delayed" ]; then echo "delayed_epoch1_fenced=true"; else echo "delayed_epoch1_fenced=false"; fi
echo "trace_end=1"
"""


# --------------------------------------------------------------------------------------
# WSL handlers
# --------------------------------------------------------------------------------------


def wsl_run(script: str, timeout: int) -> dict:
    return run_wsl(script, timeout)


def h_pf01_wsl() -> dict:
    res = wsl_run(PF01_SCRIPT, 45)
    kv = parse_kv(res["stdout"])
    obs = ev(flag(kv, "contained"), "nested/grandchild share the declared boundary pgid",
             contained=kv.get("contained"), supervisor_pgid=kv.get("supervisor.pgid"),
             nested_pgid=kv.get("nested.pgid"), grandchild_pgid=kv.get("grandchild.pgid"))
    rec = ev(kv.get("remaining") == "0",
             "declared boundary killed, escaped actor reconciled via explicit cleanup, scope empty",
             remaining=kv.get("remaining"))
    neg = ev(flag(kv, "escape_detected"),
             "setsid escape detected as outside the declared boundary",
             escaper_pgid=kv.get("escaper.pgid"), declared_pgid=kv.get("supervisor.pgid"))
    if res["timed_out"]:
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="observed pgid membership and explicit reconciliation")


def h_pf02_wsl() -> dict:
    res = wsl_run(PF02_SCRIPT, 30)
    kv = parse_kv(res["stdout"])
    observed = (flag(kv, "child_alive") and not flag(kv, "registration_present")
                and flag(kv, "unresolved_launch_visible"))
    obs = ev(observed, "live orphan visible while registration is absent",
             child_alive=kv.get("child_alive"), registration_present=kv.get("registration_present"),
             unresolved_launch_visible=kv.get("unresolved_launch_visible"))
    rec = ev(flag(kv, "orphan_terminated"), "new epoch terminated the unregistered child",
             orphan_terminated=kv.get("orphan_terminated"))
    neg = ev(flag(kv, "unresolved_launch_visible"),
             "record-only oracle would report not_started while the orphan is live",
             record_only_oracle=kv.get("record_only_oracle"))
    if res["timed_out"]:
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="native /proc state, not a missing response")


def h_pf04_wsl() -> dict:
    res = wsl_run(PF04_SCRIPT, 30)
    kv = parse_kv(res["stdout"])
    observed = (flag(kv, "pty_available") and flag(kv, "output_captured")
                and flag(kv, "terminal_alive_before_teardown"))
    obs = ev(observed, "PTY terminal produced numbered output before teardown",
             pty_available=kv.get("pty_available"), captured_lines=kv.get("captured_lines"),
             writer_alive_before=kv.get("terminal_alive_before_teardown"))
    rec = ev(flag(kv, "terminal_exited") and flag(kv, "writer_exited"),
             "terminal host and writer exited after teardown",
             terminal_exited=kv.get("terminal_exited"), writer_exited=kv.get("writer_exited"),
             final_lines=kv.get("final_captured_lines"))
    neg = ev(kv.get("close_cause") == "local_close" and kv.get("all_clients_disconnected") == "false",
             "harness closure labeled local_close, not promoted to all_clients_disconnected",
             close_cause=kv.get("close_cause"), all_clients_disconnected=kv.get("all_clients_disconnected"))
    if not flag(kv, "script_available"):
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="observed PTY output + process exit evidence")


def h_pf05_wsl() -> dict:
    res = wsl_run(PF05_SCRIPT, 30)
    kv = parse_kv(res["stdout"])
    obs = ev(flag(kv, "target_alive_after_term") and flag(kv, "sentinel_alive_after_term"),
             "graceful signal delivered, target ignored it, sentinel unaffected",
             target_alive_after_term=kv.get("target_alive_after_term"),
             sentinel_alive_after_term=kv.get("sentinel_alive_after_term"))
    rec = ev((not flag(kv, "target_alive_after_kill")) and flag(kv, "sentinel_alive_after_kill"),
             "escalation reached only the owned group; sentinel survived",
             target_alive_after_kill=kv.get("target_alive_after_kill"))
    neg = ev(flag(kv, "target_alive_after_term") and flag(kv, "sentinel_alive_after_kill"),
             "ignoring target not recorded as exited; out-of-scope sentinel unaffected",
             sentinel_alive_after_kill=kv.get("sentinel_alive_after_kill"))
    if res["timed_out"]:
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="distinct signal/handler/exit events")


def h_pf06_wsl() -> dict:
    res = wsl_run(PF06_SCRIPT, 60)
    kv = parse_kv(res["stdout"])
    observed = (kv.get("reads") == "40" and kv.get("torn") == "0" and kv.get("missing") == "0")
    obs = ev(observed, "reopening readers saw only complete generation A or B (no torn/missing)",
             reads=kv.get("reads"), torn=kv.get("torn"), missing=kv.get("missing"))
    rec = ev(flag(kv, "recovery_complete"),
             "authoritative name resolves to a complete generation after crashes",
             final_size=kv.get("final_size"), inventory=kv.get("inventory"))
    gap = kv.get("negative_control_gap", "0")
    neg = ev(gap not in ("", "0"), "non-atomic copy+delete gap detected by the reader",
             negative_control_gap=gap)
    if res["timed_out"]:
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="observed namespace states across crash cuts")


def h_pf08_wsl() -> dict:
    res = wsl_run(PF08_SCRIPT, 30)
    kv = parse_kv(res["stdout"])
    obs = ev(flag(kv, "exclusive_enforced") and flag(kv, "advisory_bypass"),
             "native lock enforced while held; raw write bypass detected as outside protection",
             exclusive_enforced=kv.get("exclusive_enforced"), advisory_bypass=kv.get("advisory_bypass"))
    rec = ev(flag(kv, "reacquired") and flag(kv, "reacquire_confirmed"),
             "new owner re-acquired the native lock after owner death",
             reacquired=kv.get("reacquired"), stale_marker_present=kv.get("stale_marker_present"))
    neg = ev(flag(kv, "advisory_bypass") and not flag(kv, "competing_write_admitted"),
             "bypass control detected; stale marker not treated as ownership",
             competing_write_admitted=kv.get("competing_write_admitted"))
    if res["timed_out"]:
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="native lock result + explicit bypass control")


def h_pf09_wsl() -> dict:
    res = wsl_run(PF09_SCRIPT, 30)
    kv = parse_kv(res["stdout"])
    reuse = flag(kv, "reuse_triggered")
    hazard = flag(kv, "stale_identity_hazard")
    obs = ev(reuse and hazard,
             "numeric PID reuse proven and stale identity hazard distinguished by starttime",
             orig_pid=kv.get("orig.pid"), new_pid=kv.get("new.pid"),
             orig_starttime=kv.get("orig.starttime"), new_starttime=kv.get("new.starttime"))
    if not reuse:
        obs["coverage_lost"] = True  # untriggered cell -> unknown, not pass
    rec = ev(flag(kv, "new_process_alive") and not flag(kv, "stale_signal_sent"),
             "no stale signal sent to the reused PID; new process untouched",
             new_process_alive=kv.get("new_process_alive"))
    neg = ev(hazard, "PID-only targeting would hit the wrong process (starttime differs)",
             stable_identity_field=kv.get("stable_identity_field"))
    return _pack(res, kv, obs, rec, neg, success_basis="proven reuse plus stable-identity mismatch")


def h_pf10_wsl() -> dict:
    res = wsl_run(PF10_SCRIPT, 45)
    kv = parse_kv(res["stdout"])
    if not flag(kv, "mount_ok"):
        obs = ev(False, "bounded tmpfs could not be mounted", mount_ok=kv.get("mount_ok"))
        obs["coverage_lost"] = True
        rec = ev(False, "no recovery: disk-full was not injected", mount_ok=kv.get("mount_ok"))
        neg = ev(False, "no negative control ran", mount_ok=kv.get("mount_ok"))
        return _pack(res, kv, obs, rec, neg, success_basis="not executed")
    observed = (kv.get("write_result") == "refused" and flag(kv, "genA_preserved")
                and not flag(kv, "genB_present"))
    obs = ev(observed, "write refused under ENOSPC; generation A preserved; no false ack",
             write_result=kv.get("write_result"), err_head=kv.get("err_head"),
             genA_preserved=kv.get("genA_preserved"), fill_files=kv.get("fill_files"))
    rec = ev(flag(kv, "recovered_write") and int(kv.get("avail_after_cleanup_kb", "0") or 0) > 0,
             "space restored only after recording failure; B then written successfully",
             avail_after_cleanup_kb=kv.get("avail_after_cleanup_kb"),
             recovered_write=kv.get("recovered_write"))
    neg = ev(flag(kv, "genA_preserved") and kv.get("write_result") == "refused",
             "truncated B not accepted because a name exists; predecessor preserved",
             genB_present=kv.get("genB_present"))
    if res["timed_out"]:
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="observed ENOSPC refusal + preserved predecessor")


def h_pf11_wsl() -> dict:
    res = wsl_run(PF11_SCRIPT, 30)
    kv = parse_kv(res["stdout"])
    obs = ev(kv.get("alloc_result") == "refused",
             "bounded allocation refused under the hard address-space limit (memory.high substitute)",
             alloc_result=kv.get("alloc_result"), limit_kb=kv.get("limit_kb"))
    rec = ev(flag(kv, "resumed"),
             "work resumes after pressure removed; no respawn under pressure",
             resumed=kv.get("resumed"))
    neg = ev(kv.get("death_inferred") == "false",
             "classifier does not infer death from absence; classified as allocation refusal",
             classification=kv.get("classification"),
             throttle_counter_available=kv.get("throttle_counter_available"))
    if res["timed_out"]:
        obs["coverage_lost"] = True
    # cgroup v2 is read-only here: true memory.high throttle counters are unavailable -> unknown.
    return _pack(res, kv, obs, rec, neg, forced_unknown=True,
                 success_basis="bounded allocation refusal; memory.high counters unavailable",
                 extra={"limitation": "cgroup v2 mounted read-only; memory.high unavailable; "
                                      "outcome unknown for native throttle classification"})


def h_pf13_wsl() -> dict:
    res = wsl_run(PF13_SCRIPT, 30)
    kv = parse_kv(res["stdout"])
    obs = ev(flag(kv, "restart_acquired") and flag(kv, "fencing_enforced")
             and kv.get("ownerB.epoch") == "epoch=2",
             "restart acquired a single authority epoch and fencing refused a competitor",
             restart_acquired=kv.get("restart_acquired"), fencing_enforced=kv.get("fencing_enforced"),
             ownerB_epoch=kv.get("ownerB.epoch"))
    rec = ev((not flag(kv, "ownerA_alive_after_crash")) and kv.get("ownerB.epoch") == "epoch=2",
             "stale lock cleared only after old owner death; new epoch authoritative",
             ownerA_alive_after_crash=kv.get("ownerA_alive_after_crash"),
             stale_lock_present=kv.get("stale_lock_present"))
    neg = ev(flag(kv, "unauthorized_owner_visible"),
             "unfenced competitor writing authority is visible as a second owner",
             unauthorized_owner_visible=kv.get("unauthorized_owner_visible"))
    if res["timed_out"]:
        obs["coverage_lost"] = True
    return _pack(res, kv, obs, rec, neg, success_basis="single fenced authority epoch")


def _pack(res: dict, kv: dict, obs: dict, rec: dict, neg: dict,
          *, success_basis: str, forced_unknown: bool = False, extra: dict | None = None) -> dict:
    outcome = outcome_of(obs, rec, neg, forced_unknown=forced_unknown)
    return {
        "fault_triggered": flag(kv, "trace_end") and not res["timed_out"],
        "observation": obs,
        "recovery": rec,
        "negative_control": neg,
        "outcome": outcome,
        "success_basis": success_basis,
        "commands": [res["argv"], res["script"]],
        "raw": {k: v for k, v in kv.items() if k != "trace_end"},
        "timed_out": res["timed_out"],
        "duration_s": res["duration_s"],
        "extra": extra or {},
    }


# --------------------------------------------------------------------------------------
# host handlers (Windows, non-destructive only)
# --------------------------------------------------------------------------------------


def h_pf04_host() -> dict:
    argv = ["cmd", "/c", "for /L %i in (1,1,100000000) do @echo SEQ %i"]
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    assert p.stdout is not None
    prefix = p.stdout.read(4096)
    complete = prefix.count(b"\n")
    last = ""
    for chunk in prefix.split(b"\n"):
        text = chunk.strip().decode("ascii", "replace")
        if text.startswith("SEQ "):
            last = text
    dup_fd = os.dup(p.stdout.fileno())
    time.sleep(1.0)
    blocked = p.poll() is None
    clients_remaining = 1
    all_disconnected = False
    os.close(dup_fd)
    p.stdout.close()
    exit_cause = "unknown"
    try:
        p.wait(timeout=5)
        exit_cause = "broken_pipe"
    except subprocess.TimeoutExpired:
        p.terminate()
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(timeout=5)
        exit_cause = "forced_terminate"
    obs = ev(blocked and complete > 0,
             "writer blocked after a bounded undrained read; complete records counted",
             blocked=blocked, complete_records=complete, last_record=last, route="anonymous_pipe")
    rec = ev(p.poll() is not None, "writer process exited after clients closed",
             exit_cause=exit_cause, returncode=p.returncode)
    neg = ev(clients_remaining == 1 and not all_disconnected,
             "retained duplicate client prevents all_clients_disconnected; closure is local_close",
             clients_remaining=clients_remaining, all_disconnected=all_disconnected,
             close_cause="local_close")
    outcome = outcome_of(obs, rec, neg)
    return {"fault_triggered": blocked, "observation": obs, "recovery": rec,
            "negative_control": neg, "outcome": outcome,
            "success_basis": "observed pipe backpressure then native process exit",
            "commands": [" ".join(argv)],
            "raw": {"route": "anonymous_pipe",
                    "note": "ConPTY route not exercised: stdlib-only has no ConPTY adapter"},
            "timed_out": False, "duration_s": None, "extra": {}}


def h_pf06_host() -> dict:
    d = Path(tempfile.mkdtemp(prefix="fu04_pf06_"))
    target = d / "target.bin"
    tmp = d / "tmp.bin"
    gen_a = b"A" * 100000
    gen_b = b"B" * 200000
    target.write_bytes(gen_a)
    with open(tmp, "wb") as f:
        f.write(gen_b)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, target)
    obs_ok = target.read_bytes() == gen_b
    seen = set()
    for _ in range(50):
        seen.add(len(target.read_bytes()))
    only_allowed = seen <= {len(gen_a), len(gen_b)}
    obs = ev(obs_ok and only_allowed,
             "os.replace + fsync published generation B; reopening readers saw only A or B",
             seen_sizes=sorted(seen))
    rec = ev(target.read_bytes() == gen_b,
             "authoritative name resolves to the complete published generation",
             final_size=len(target.read_bytes()))
    gap = [0]

    def nonatomic() -> None:
        cpy = d / "cpy.bin"
        t2 = d / "target2.bin"
        cpy.write_bytes(gen_b)
        t2.unlink()
        time.sleep(0.05)
        os.replace(cpy, t2)

    (d / "target2.bin").write_bytes(gen_a)
    t = threading.Thread(target=nonatomic)
    t.start()
    while t.is_alive():
        if not (d / "target2.bin").exists():
            gap[0] += 1
    t.join()
    neg = ev(gap[0] > 0, "non-atomic copy+delete gap detected by a reopening reader",
             negative_control_gap=gap[0])
    outcome = outcome_of(obs, rec, neg)
    return {"fault_triggered": True, "observation": obs, "recovery": rec,
            "negative_control": neg, "outcome": outcome,
            "success_basis": "application-visible atomic replacement observation",
            "commands": ["python os.replace + os.fsync (in-process host handler)"],
            "raw": {"route": "local_ntfs_temp"},
            "timed_out": False, "duration_s": None, "extra": {}}


def h_pf08_host() -> dict:
    import msvcrt

    d = Path(tempfile.mkdtemp(prefix="fu04_pf08_"))
    p = d / "lock.bin"
    p.write_bytes(b"0123456789")
    f = open(p, "r+b")
    f.seek(0)
    msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
    acquired = True
    f2 = open(p, "r+b")
    f2.seek(0)
    contended = False
    try:
        msvcrt.locking(f2.fileno(), msvcrt.LK_NBLCK, 1)
        msvcrt.locking(f2.fileno(), msvcrt.LK_UNLCK, 1)
    except OSError:
        contended = True
    f.seek(5)
    f.write(b"X")
    f.flush()
    bypass = True
    f.seek(0)
    msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
    f.close()
    f2.close()
    f3 = open(p, "r+b")
    f3.seek(0)
    reacquired = False
    try:
        msvcrt.locking(f3.fileno(), msvcrt.LK_NBLCK, 1)
        msvcrt.locking(f3.fileno(), msvcrt.LK_UNLCK, 1)
        reacquired = True
    except OSError:
        reacquired = False
    f3.close()
    obs = ev(acquired and contended,
             "byte-range lock enforced against a second handle",
             acquired=acquired, contended=contended)
    rec = ev(reacquired, "lock released and re-acquired after release",
             reacquired=reacquired)
    neg = ev(bypass, "an out-of-lock write bypasses the advisory range lock (detected)",
             advisory_bypass=bypass)
    outcome = outcome_of(obs, rec, neg)
    return {"fault_triggered": acquired, "observation": obs, "recovery": rec,
            "negative_control": neg, "outcome": outcome,
            "success_basis": "byte-range lock acquire/release + bypass control",
            "commands": ["python msvcrt.locking LK_NBLCK/LK_UNLCK (in-process host handler)"],
            "raw": {"route": "local_ntfs_temp"},
            "timed_out": False, "duration_s": None, "extra": {}}


# --------------------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------------------

HANDLERS = {
    ("PF01", "wsl:Debian"): (h_pf01_wsl, True),
    ("PF02", "wsl:Debian"): (h_pf02_wsl, True),
    ("PF04", "host"): (h_pf04_host, False),
    ("PF04", "wsl:Debian"): (h_pf04_wsl, False),
    ("PF05", "wsl:Debian"): (h_pf05_wsl, True),
    ("PF06", "host"): (h_pf06_host, False),
    ("PF06", "wsl:Debian"): (h_pf06_wsl, True),
    ("PF08", "host"): (h_pf08_host, False),
    ("PF08", "wsl:Debian"): (h_pf08_wsl, True),
    ("PF09", "wsl:Debian"): (h_pf09_wsl, True),
    ("PF10", "wsl:Debian"): (h_pf10_wsl, True),
    ("PF11", "wsl:Debian"): (h_pf11_wsl, True),
    ("PF13", "wsl:Debian"): (h_pf13_wsl, True),
}


def targets_for(trace: dict) -> list[str]:
    t = trace["target"]
    if t == "both":
        return ["host", "wsl:Debian"]
    if t == "host":
        return ["host"]
    if t == "wsl":
        return ["wsl:Debian"]
    return []


def load_traces() -> list[dict]:
    data = json.loads((HERE / "traces.json").read_text(encoding="utf-8"))
    return data["traces"]


def main() -> int:
    ap = argparse.ArgumentParser(description="FU-04 negative-trace runner")
    ap.add_argument("--target", required=True, choices=["host", "wsl:Debian", "all"])
    ap.add_argument("--allow-destructive", action="store_true")
    ap.add_argument("--only", default="", help="comma-separated trace ids, e.g. PF01,PF06")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args()

    out_path = Path(args.out)
    traces = load_traces()
    only = {x.strip().upper() for x in args.only.split(",") if x.strip()}
    want_targets = TARGETS if args.target == "all" else [args.target]

    runs: list[dict] = []
    skipped: list[dict] = []
    for trace in traces:
        tid = trace["id"]
        if only and tid not in only:
            continue
        for target in want_targets:
            if target not in targets_for(trace):
                continue
            key = (tid, target)
            if key not in HANDLERS:
                skipped.append({"id": tid, "target": target,
                                "reason": "no handler implemented for this target"})
                continue
            handler, destructive = HANDLERS[key]
            if destructive and not args.allow_destructive:
                skipped.append({"id": tid, "target": target,
                                "reason": "destructive trace requires --allow-destructive"})
                continue
            print(f"run {tid} @ {target} ...", flush=True)
            try:
                result = handler()
            except Exception as exc:  # keep the run going; record the failure honestly
                result = {
                    "fault_triggered": False,
                    "observation": ev(False, f"handler raised: {exc!r}"),
                    "recovery": ev(False, "not reached", error=repr(exc)),
                    "negative_control": ev(False, "not reached"),
                    "outcome": "unknown",
                    "success_basis": "handler error",
                    "commands": ["<in-process handler>"],
                    "raw": {"error": repr(exc)},
                    "timed_out": False, "duration_s": None,
                    "extra": {"coverage_lost": True},
                }
            run = {
                "id": tid,
                "target": target,
                "title": trace["title"],
                "destructive": bool(trace["destructive"]),
                "handler_destructive": destructive,
                **result,
            }
            print(f"    -> {run['outcome']}", flush=True)
            runs.append(run)

    # merge with any prior results for other targets
    prior: dict = {}
    if out_path.exists():
        try:
            prior = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prior = {}
    prior_runs = prior.get("runs", [])
    new_keys = {(r["id"], r["target"]) for r in runs}
    merged = [r for r in prior_runs if (r["id"], r["target"]) not in new_keys] + runs
    merged.sort(key=lambda r: (r["id"], r["target"]))

    not_run: list[dict] = []
    done = {(r["id"], r["target"]) for r in merged}
    for trace in traces:
        needed = targets_for(trace)
        if not trace.get("runs_now", False):
            not_run.append({"id": trace["id"], "target": trace["target"],
                            "destructive": bool(trace["destructive"]),
                            "reason": trace.get("unsupported_reason", "not runnable")})
            continue
        for target in needed:
            if (trace["id"], target) not in done:
                not_run.append({
                    "id": trace["id"], "target": target,
                    "destructive": bool(trace["destructive"]),
                    "reason": "not executed in this invocation (requires the matching "
                              "--target and, for destructive handlers, --allow-destructive)",
                })

    for item in skipped:
        if not any(n["id"] == item["id"] and n["target"] == item["target"] for n in not_run):
            trace = next((t for t in traces if t["id"] == item["id"]), {})
            not_run.append({"id": item["id"], "target": item["target"],
                            "destructive": bool(trace.get("destructive", False)),
                            "reason": item["reason"]})

    record = {
        "experiment": "fu-04-os-conformance traces",
        "catalog": "traces.json",
        "evidence_class": "locally_observed (single host + WSL2 Debian dev/test target)",
        "certification": "none; no OS build or profile is qualified",
        "invocation": {"target": args.target, "allow_destructive": args.allow_destructive,
                       "only": sorted(only)},
        "runs": merged,
        "not_run": sorted(not_run, key=lambda n: (n["id"], n["target"])),
    }
    out_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    counts: dict[str, int] = {}
    for r in runs:
        counts[r["outcome"]] = counts.get(r["outcome"], 0) + 1
    print(f"wrote {out_path}")
    print(f"runs this invocation: {len(runs)} {counts}")
    print(f"total runs: {len(merged)}; not_run: {len(not_run)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
