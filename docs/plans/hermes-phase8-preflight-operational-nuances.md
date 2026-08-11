---
title: Hermes Phase 8 preflight — operational nuances and traps
type: reference
status: current
last-verified: 2026-08-11
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-phase8-handoff.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
  - scripts/runtime-state.py
  - scripts/taskctl.sh
  - scripts/audit/hermes-pilot-phase0-baseline.sh
---
# Hermes Phase 8 preflight — operational nuances and traps

Observed while executing the post-merge runbook's read-only proof and the PAUSE-held
preflight on `2026-08-11`. Every item below cost real time or produced a wrong-looking
result before it was understood. Each says what was observed, why it happens, and the
rule that replaces the guess.

The preflight these came from: reviewed merge `ecc93de7fd5f6d92812d5a89687d6e05326b15fc`,
production `loop/auto` at `bcd65ebcc7c1af3f56be1bb3b7530a837793eaf6`, PAUSE
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`.

## Locks

### The canonical control lock cannot be taken by hand with deployed code

`runtime-state.py` gained `lock-acquire` / `lock-release` **in the hardening patch**. The
deployed pre-hardening copy exposes only `rotate-events`, `backup`, `restore`. A runbook
step phrased "acquire the canonical control lock" is therefore **not executable against
production** until the hardening is deployed.

It also must not be attempted. `rotate_events()`, `backup()` and `restore()` each open
`with RuntimeLock(root), EmptyLock(root / "state/.locks/taskctl.lock")` themselves.
Pre-holding either lock makes the snapshot fail closed with
`runtime-state lock is contended; refusing an unlocked mutation`.

**Rule:** let the tool take the lock. Mutual exclusion for a snapshot is provided by
`backup()` itself, which is PAUSE-gated and calls `assert_no_execution_locks()`. Verify the
locks were *released* afterwards instead of taking them first.

### The lock is a directory; the lock *files* present are not held locks

`taskctl.sh` `_lock()` uses `mkdir` as the atomic primitive — the lock is
`state/.locks/taskctl.lock` as a **directory**. Production also carries two 0-byte lock
**files** (`decision-queue.lock`, `hermes-control.lock`, dated Aug 7 and Aug 9). Those are
not held locks and do not indicate contention. Reading `ls state/.locks` as "two locks are
held" is wrong.

`runtime-state.lock` outranks `taskctl.lock`: `_lock()` refuses to acquire at all while the
runtime lock directory exists. `assert_no_execution_locks()` only counts
`action-*.lock`, `ws-*.lock`, `ledger.lock`, `heavy-gate.lock` — those are the execution
locks that block maintenance.

## Shell and harness traps

### `pgrep -c` prints `0` *and* exits non-zero — `|| echo 0` then double-counts

```sh
count=$(pgrep -c -f 'pattern' 2>/dev/null || echo 0)   # WRONG: yields "0\n0" when none match
count=$(pgrep -f 'pattern' 2>/dev/null | wc -l)        # correct
```

`pgrep -c` reports the count on stdout **and** returns exit 1 when nothing matched, so the
`||` branch fires on top of the printed `0`. A gate comparing that to `"0"` fails.

This was caught by dry-running the CAS gate rather than trusting it. It failed **closed**,
which is the safe direction, but it would have blocked an authorized transaction for a
non-reason. **Dry-run every gate before it guards something real** — a gate that has never
been executed is an untested assertion.

### `git bundle create` refuses a bare commit SHA

```sh
git bundle create out.bundle ecc93de7...      # fatal: Refusing to create empty bundle
git update-ref refs/heads/preflight-master ecc93de7...
git bundle create out.bundle refs/heads/preflight-master   # works
```

A bundle must carry at least one **ref**; a bare revision produces no ref and git treats the
result as empty. Related: `git bundle verify` needs to run **inside a repository** — running
it in the staging directory returns `error: need a repository to verify a bundle`. Verify by
SHA-256 across the wire plus a tip-commit and **tree** comparison after cloning, which proves
content rather than transport alone.

### `ssh host 'nohup … &'` still holds the channel

Backgrounding inside a single ssh invocation kept the connection open and the client timed
out at 2 minutes even with `nohup` and full redirection. Use `setsid` plus
`>/dev/null 2>&1 </dev/null`, and then **confirm the job by checking its log grows** — do not
infer success or failure from the ssh exit code. In this run the ssh call reported a timeout
while the detached job was in fact running correctly.

### Nested quoting through ssh breaks silently

Inline `ssh host "… $(cmd | grep -cE '(a|b)') …"` produced `sed: unterminated s command` and
`bash: syntax error near unexpected token '('` — the local shell, the ssh command string, and
the remote shell each consume a layer of quoting. Use a heredoc:

```sh
ssh host 'bash -s' <<'REMOTE'
  … script …
REMOTE
```

### `RECURSION_ROOT` means the opposite thing in the green and red audits

Three conventions coexist, and exporting one value for a whole sweep silently misdirects a
check:

| script | `RECURSION_ROOT` means | live root comes from |
|---|---|---|
| `hermes-pilot-phase0-baseline.sh` | code root (defaults to its own repo) | `RECURSION_LIVE_ROOT`, default `/opt/recursion` |
| `hermes-pilot-phase*-green.sh` | code root (defaults to its own repo) | n/a |
| `hermes-pilot-live-phase1-red.sh` | **live root**, default `/opt/recursion` | same variable |

A driver that does `export RECURSION_ROOT="$CLONE"` for the whole sequence points the live
audit at the clone, which has no `state/PAUSE`, and it exits `90` with:

```text
FATAL remote PAUSE is absent
```

That message reads like a production PAUSE emergency. It is not: it is a harness
misconfiguration, and the audit is behaving correctly by failing closed. Observed exactly
this way on 2026-08-11; the same audit had returned `ALL PASS` minutes earlier and returned
`ALL PASS` again when re-run with `RECURSION_ROOT=/opt/recursion`.

**Rule:** run the live audit with the live root explicit, from the reviewed clone, so the
reviewed audit code is what examines production:

```sh
cd "$CLONE" && RECURSION_ROOT=/opt/recursion bash scripts/audit/hermes-pilot-live-phase1-red.sh
```

Never infer a production fault from a harness exit code without first confirming which root
the script actually read.

### Observed audit timing envelope

From the 2026-08-11 preflight on `gs-recursion`, in a `/var/tmp` clone:

```text
baseline 19/19 suites, 0 failed
phase1=4s  phase2=30s  phase3=18s  phase4=8s  phase5=71s
phase6=969s  phase7=307s  phase8=113s   (whole run 23:11Z to 23:40Z)
```

Phase 6 dominates because its 20 crash/replay scenarios repeatedly exercise fsync-backed
journal, receipt and recovery paths in fresh fixture roots. It is bounded I/O, not a
deadlock, but it is also I/O-bound, so wall time varies with the box: an earlier closure run
recorded roughly 40 minutes for the same phase. Budget for the slower figure and do not
treat a long Phase 6 as a hang.

## Production-specific facts that invalidate generic runbook steps

### Production `origin` cannot authenticate — objects must arrive by bundle

`git ls-remote origin` fails on the box. Any step that assumes `git fetch` will work is not
executable there; that is also why `origin/master` is legitimately stale at
`7e6e21f4…`. This is a known read-only observation and must not be "repaired" as a side
effect of another task.

### `CRON=inactive` means the unit is stopped, not that cron is disarmed

`cron.service` is `inactive` but **`enabled`** — a host reboot resumes it, and the crontab
still holds its four job lines invoking `cycle.sh`, `hermes-decide.sh` and
`fallback-watch.sh`. Containment is runtime-only; PAUSE, not cron state, is the kill switch.

### Counting crontab lines misleads

A "non-comment, non-blank" count returns **5** against a documented "exact four-line root
crontab": one `PATH=` assignment plus four schedule lines. Classify the lines
(`^[A-Z_]+=` vs `^[0-9*@]`) instead of counting them. A bare count is an aggregate that hides
the thing being asserted.

### `restore()` needs PAUSE in the *target* root

`restore(root, snapshot)` calls `require_pause(root)` before anything else, and
`ensure_outside_root()` forbids a snapshot path inside the checkout. A disposable staging
root must therefore be seeded with a copy of `state/PAUSE` **before** the restore, or the
drill fails with `state/PAUSE is absent; refusing runtime-state maintenance`.

### The audit harness depends on live production being PAUSEd

`hermes-pilot-phase0-baseline.sh` exits `3` on a detached HEAD
(`use a named branch, not detached HEAD`) and exits `90` if `/opt/recursion/state/PAUSE` is
missing; it also reads the deployed commit. Consequences: clone with `--branch <name>` (a
bundle clone would otherwise land detached), and accept that the suite **cannot run on a host
without a PAUSEd production checkout**.

## Reconciliation

### Conflict-freedom here is provable statically — do not settle it by trial merge alone

Production's `loop/auto` carries **74 local-only commits** (never pushed) that touch
**exactly 8 files and zero code files**: `state/BOARD.md`, `state/INBOX.md`,
`state/escalations.tsv`, `state/events.jsonl`, and four `state/briefs/*.md`. The incoming
range touches 73 files with **zero intersection**. The merge is therefore conflict-free by
construction; the trial merge confirms it rather than discovering it.

This yields a **parameter-free post-condition** worth more than "the merge succeeded":

```sh
git diff --name-only <merge-result> ecc93de   # must equal exactly those 8 awareness files
git diff --name-only <merge-result> ecc93de -- scripts/ loop/ schemas/ CONTROL_PLANE.md   # must be empty
```

The second check is the one that proves the deployed **executable bytes** equal the reviewed
bytes. A merge that "succeeded" while changing the executable surface is a failed
deployment wearing a success costume.

### Simulate in a clone of production, never in production

`git clone --no-hardlinks /opt/recursion` plus a bundle fetch reproduces both live parents
exactly, so the full reconciliation can be rehearsed with no risk. `--no-hardlinks` avoids
sharing object files with the live repository.

## Tooling outside the box

### An invalid `GITHUB_TOKEN` silently shadows a valid keyring token

`gh auth status` showed a logged-in account **and** `X Failed to log in using token
(GITHUB_TOKEN)`; every `gh api` call returned `Bad credentials` (401). A per-command
`GITHUB_TOKEN= gh api …` override restores the keyring credential without touching stored
configuration. Do not "fix" this by editing config — it is a local environment variable, and
config/auth is a protected path.

## Housekeeping observed

- `/var/backups/recursion` holds **47** retained snapshots (~3.6 G) and `/var/tmp` holds
  **48** `recursion-*` staging clones (~2.4 G) — ~6 G total, on a 38 G disk at 50 % use. The
  snapshot/evidence pattern has no reaper, so every preflight adds to both. Not currently
  blocking; worth a reviewed prune before it is.
- Retained drill backup `hermes-pre-phase8-20260808T224858Z-5a8b2f7464cb` is intact with its
  manifest.

## Corrections to the Phase 8 handoff

The handoff's read-only preflight table and its branch-protection section both still describe
the two live Phase 1 findings (root/unrestricted gateway; `aiohttp` + `cryptography`
advisories) as open, and the branch-protection section lists them as the remaining
pre-deployment gates. They were closed by the corrected Phase 1 deployment recorded later in
the same document. The live audit now returns `ALL PASS` with `rc=0`, 104 packages audited,
and the gateway running as a hardened non-root service.

**Rule:** when a long handoff records a state and a later section supersedes it, fix the
earlier statement rather than relying on the reader reaching the later one. A stale "gate
open" line reads as current and re-blocks work that is already unblocked.
