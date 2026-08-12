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

### The process-count gate matches the audit suite's own fixture processes

The CAS gate counts `recursion-worker|scripts/cycle.sh|scripts/work.sh|hermes-decide|...`.
While the audit suite runs, its phase-5 fixtures spawn exactly such processes in fresh
temporary roots, e.g. `bash scripts/work.sh escalation-record-failure` with a cwd of
`/tmp/tmp.XXXXXXXX/controller`. A production quiescence check run at that moment reports a
non-zero count and fails closed for a non-reason.

**Rule:** qualify the count by working directory, not by command name alone. The question is
"is anything running *against `/opt/recursion`*", which is answered by:

```sh
for p in $(ls /proc | grep -E '^[0-9]+$'); do
  case "$(readlink -f /proc/$p/cwd 2>/dev/null)" in /opt/recursion*) echo "$p";; esac
done
```

Observed 2026-08-11: a bare count read `1` while the CWD-qualified count read `0`, and the
`1` was a test fixture.

The CWD-qualified probe then has its own trap: it counts **itself**. Run from a shell that
has `cd /opt/recursion`, it reports `2` (the script and its command substitution subshell)
on an entirely idle box. Run the probe from outside the checkout - the same box reported
`0`. A quiescence measurement taken from inside the directory being measured is measuring
the observer.

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

## Self-repo git authentication

Production `origin` is `git@github.com:NotSkittlz/recursion.git` and failed with
`Permission denied (publickey)`. The cause was not a missing or revoked key:

- `/root/.ssh/id_deploy` **is** the recursion deploy key. `ssh -i /root/.ssh/id_deploy -T
  git@github.com` answers `Hi NotSkittlz/recursion!` and `git ls-remote` with it returns 42
  refs.
- Git never offered it. The box has **no default-named keys** (`id_rsa`, `id_ed25519`,
  `id_ecdsa` all absent), no `~/.ssh/config`, and no `core.sshCommand` - so ssh had no
  identity to present.

Why this is not cosmetic: every cycle runs `resync.sh observe`, which fetches, and
`work.sh` documents its own historical failure mode in a comment at line 385 - on fetch
failure it "logged *building on local base* and carried on", so an arm builds on a stale base
and re-invents already-merged work. `portfolio.tsv`'s header states the same hazard in
general terms: "a git op run with the wrong key returns EMPTY, and an empty answer reads
exactly like a true negative."

The fix is repo-local, in untracked `.git/config`:

```sh
git -C /opt/recursion config core.sshCommand   'ssh -i /root/.ssh/id_deploy -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=15'
```

Two alternatives were rejected for concrete reasons:

- **A `Host github.com` entry in `~/.ssh/config`** would apply to every repo on the box. The
  nine project clones each have their own deploy key, and a deploy key is scoped to one
  repository, so forcing `id_deploy` globally would make project fetches authenticate as
  `recursion` and fail.
- **Adding a row to `state/portfolio.tsv`** would work mechanically but that file is
  **tracked**, so it would drift the deployed tree away from the reviewed merge. The
  self-repo is also deliberately absent from the registry: `portfolio.tsv` is the registry of
  repos *the control plane is allowed to touch*, not the control plane itself.

`GIT_SSH_COMMAND` (used by `resync.sh`'s `gitk` and by `publish.sh`) takes precedence over
`core.sshCommand`, so per-project key selection is unaffected. Verified after the change:
project keys still authenticate as their own repositories.

## The quiescence gate, corrected

Getting "is anything running against production?" right took three attempts, each failing
closed for a different non-reason. The corrected probe lives at
`/var/backups/recursion/gates/quiescence.sh`.

1. `pgrep -c -f X 2>/dev/null || echo 0` returns `"0
0"` (see above).
2. Matching by command name alone counts the audit suite's own phase-5 fixtures -
   `scripts/work.sh` running under `/tmp/tmp.XXXXXXXX/controller`. Those are not production
   work. Qualifying by working directory fixes it.
3. The CWD-qualified probe then counts **the observer**. `cd /` inside the script is not
   enough, because the *caller's* shell is still sitting in the checkout. Invoked from a
   shell that had `cd /opt/recursion`, an idle box reported `1`.

The probe must therefore stand outside the directory it measures **and** exclude its own
process ancestry:

```sh
cd /
self=$$; ancestors=" $self "; p=$self
while :; do
  [ -r "/proc/$p/stat" ] || break
  p=$(awk '{print $4}' "/proc/$p/stat" 2>/dev/null)
  case "$p" in ''|0|1) break ;; esac
  ancestors="$ancestors$p "
done
# then skip any pid in $ancestors while scanning /proc/*/cwd
```

**Validated with a positive control, not just a zero.** A gate that always returns `0` looks
identical to a correct one on an idle box. Measured: `0` invoked from inside the checkout
(was `1`), `2` with a deliberately planted process whose cwd is in `ROOT`, and `0` again
after it exits. Any quiescence check that has only ever returned zero is unverified.

## Cron resume changes the steady-state `git status`

Under PAUSE the loop writes monitoring artifacts and deliberately does not commit them
("PAUSE preserves self-repo Git state; monitoring artifacts retained locally without
commit"). After one cycle the tree carries a modified `state/escalations.tsv` and a new
untracked `state/briefs/<date>.md` on top of the pre-existing untracked `.env.bak.*`.

A CAS gate that asserts an exact `git status --porcelain` string - as the Phase 8 deployment
gate did - will therefore fail once cron is running. That assertion was correct while cron
was contained and is wrong afterwards. Gate on the absence of *unexpected* entries instead of
on an exact string.

Related: `escalations.tsv` rows are keyed and deduplicated, so a recurring condition bumps
`last_seen` and `count` rather than adding a row. A changed file with an unchanged line count
is the normal shape, not a lost record. `esc-0002` (`recursion: 1 local branch(es) hold
commits on no remote`) and `esc-0003` (`recursion: uncommitted changes in the working tree`)
are both permanently true for the deployed checkout and will keep incrementing every cycle.
That is expected noise, open since 2026-08-07.

## An open instruction cannot be answered while PAUSE holds delivery at zero

Instruction 486 ("Hey Hermes, is the box still paused?", 2026-08-09) is still `status: open`.
It is what drives `heartbeat signal=brief reason=unanswered inbox escalation` on every cycle.
Answering it means delivering a reply, and PAUSE forces `deliver=0`, so the escalation is
structurally unresolvable until PAUSE lifts. Expected noise; not a fault, and not evidence
that intake is broken.

## Two crons on the same minute is a permanent loss, not a race

`recursion-cycle` and `recursion-decide` were both installed at `15 */3 * * *`. They share
`state/.locks/hermes-control.lock`, taken with `flock -n`, so the loser exits 73 immediately.
Because the schedules are identical rather than merely close, the same one loses every time --
the decision turn is not "occasionally skipped", it never runs. The symptom is a single log
line in a file nobody reads, and an executive that appears to be ignoring its operator.

**Check `loop/logs/<date>-decide.log` for `control lock contended` before concluding the model
is idle or unresponsive.**

## A prompt statement is load-bearing state, and it goes stale like any other

Two of the four gate 5 blockers were sentences, not code. The RUNTIME/PAUSE block asserted a
verb set that Phase 8 had widened, and the decision-block spec named a field without its
constraint. Both were true when written. Both silently produced exactly the behaviour they
described -- the model reasoned back the stale sentence nearly verbatim.

The machinery had been tested and was correct in both cases. **A green audit of the executable
path says nothing about whether the prompt describes it accurately**, and the model cannot
discover the discrepancy from inside the prompt. When a verb set, a field constraint or a
permission changes, grep the prompts for the old claim.

## A grep assertion over wrapped shell text passes vacuously

The obvious check for the stale PAUSE claim -- `grep -q "only executable verb while paused is
'noop'"` -- could never match, because the sentence was split across two `echo` lines:

```sh
echo "PAUSED - execution is halted. You may still decide; the only"
echo "executable verb while paused is 'noop'. Say what you WOULD do and why."
```

It passed against both the fixed and the broken file. Running the assertions against
`git show origin/master:<file>` showed 3 of 4 failing where 4 were expected, which is the only
reason it was caught.

**Run every new assertion against the pre-fix bytes and count the failures.** A test that
cannot fail is not evidence, and prose assertions over shell heredocs and multi-line `echo`
blocks are unusually prone to this.

## Replay a real failed artifact rather than building a fixture for it

The four days of `could not be normalized` gave no cause -- the message names the step, not the
field. Piping the exact model output from `loop/logs/*-decide-*.out` through
`decision-queue.py normalize` in a clone returned `ERR goal_id is not a canonical identifier`
in one command. A hand-built fixture would have carried whatever `goal` value the author
thought was normal, and would most likely have passed.
