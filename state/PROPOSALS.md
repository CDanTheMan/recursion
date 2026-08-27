# Recursion — self-improvement proposals (human-review queue)

Reflect.sh appends; a human applies or rejects. NOTHING here is auto-applied (CLAUDE.md rule 3).
[APPLY-SAFE] = low-risk, likely-approve. [NEEDS-APPROVAL] = touches config/auth/model/cron/gate/spend/mining.

## 2026-08-05 20:28 — [NEEDS-APPROVAL] Add a native-diff numeric acceptance gate for GSC frontier tasks
status: DONE 2026-08-05 — built as scripts/gsc-nativediff-gate.sh (commit 8a6755f); baseline state/gsc/nativediff-baseline.tsv; roadmap state/roadmaps/gsc-renderer.md

[NEEDS-APPROVAL] Add a native-diff numeric acceptance gate for GSC frontier tasks
**Evidence:** “GSC corpus deployed; conformance is COMPLETE” says 211 tests yield 206 pass, 0 FAIL, 5 skip and explicitly identifies native-diff quality as the frontier requiring “a NUMERIC acceptance gate (error must strictly decrease + a control reproducing the old golden).”
**Change:** Human to design and approve a native-mesh error baseline/control and strict-decrease gate, then add its task-planner integration under the GSC overnight workflow.
**Fitness:** Reduces GSC native-diff error and restores productive build-loop work without re-running already-green conformance tasks.
**Risk:** Changes acceptance gates and task selection; baseline design could reward misleading aggregate improvements, so it requires human approval.

## 2026-08-06 — [NEEDS-APPROVAL] Turn OFF autonomous merge to the default branch
status: OPEN — awaiting a human to flip the flag (rule 3: the loop cannot flip its own)

**Evidence:** `RECURSION_ALLOW_AUTOMERGE=1` is live in `.env`. `chiron-001` and `chiron-003`
are `status: passed` with `automerge: yes` / `automerge_scope: apps/chiron`, so
`work.sh integrate_remote` (and `publish.sh`) will ff-push `loop/work/<id>` straight to the
default branch on the next qualifying run.

**Conflict:** this contradicts (a) Lucas's 2026-08-06 directive — the loop may commit and push
branches but never merge to main, everything ships as sequential review branches — and
(b) `CONTROL_PLANE.md` invariant 4, "no autonomous merge to a protected or default branch."

**Change (human):**
1. Set `RECURSION_ALLOW_AUTOMERGE=0` in `/opt/recursion/.env`.
2. Drop `automerge: yes` + `automerge_scope:` from `state/tasks/chiron-00{1,3}.md`.
3. Confirm branch protection on the default branch of every repo the box holds a write key
   for: `recursion` (default is **master**, not main), `golden-stallion-client`, `chiron`,
   `guerra-construction-group`, `santa-clara-construction`.

**Why the flag alone is not enough:** the box now holds WRITE deploy keys for seven repos. A
write key can push anywhere the repo allows, so GitHub branch protection — not an env flag —
is the actual enforcement. The flag stops *our* code path; protection stops *any* path.

**Risk of applying:** none to correctness — it only removes an autonomous write. The chiron
chain will publish review branches instead of self-merging, which is the intended model.

## PROPOSAL 2026-08-06 — point notifications at The Cockpit (two human-only steps)

The routing code is merged and tested; it is INERT until both of these happen, and it fails safe
in the meantime (every message goes to the current chat, exactly as before).

**1. Grant the bot topic rights.** ~~DONE 2026-08-06~~ — Lucas promoted @recursion_manager_bot to
administrator, `topics.sh ensure` created all eight topics (recursion=3, golden-stallion=4,
golden-stallion-extension=5, golden-stallion-client=6, ai-investment-cockpit=7,
edgar-morning-brew=8, guerra-construction-group=9, chiron=10), the ids are in
`state/portfolio.tsv`, a second `ensure` created 0, and `check` verifies all eight.
Routing was confirmed end-to-end on BOTH delivery paths: the API reports the message landing in
`message_thread_id: 10` of "The Cockpit".

**2. Add two lines to `.env`** (a human edits .env — CLAUDE.md rule 3):

    RECURSION_TELEGRAM_CHAT=-1003894008732
    RECURSION_TELEGRAM_HOME_THREAD=1

`TELEGRAM_CHAT_ID` is currently `8913126684`, which `getChat` reports as `type=private` — a DM,
not the supergroup. Leave it: it stays the fallback, so nothing that works today stops working.

**Why not just change .env myself:** it is the one file the loop may never edit, because it holds
the flags that decide what the loop is allowed to do. That rule is worth more than the
convenience of skipping this note.

**Falsifier:** after both steps, a build message from a chiron task should appear in the `chiron`
topic and not in General. If it lands in General, the registry has a topic id that `message_thread_id`
is not receiving.

## 2026-08-26 — [NEEDS-APPROVAL] Declarative engine plugins (Cursor / Gemini / OpenCode / Sentry-local)
status: IN AUTHORING — Lucas approved the scope in-session (D-015 draft); implementation on a review branch

**Evidence:** worker plane supports only `claude` and `hermes`; `deepseek|openrouter` exit 91
("no file tools — needs a file-emission protocol"). Subscriptions are moving; Lucas wants
Cursor + ChatGPT as the drive pair and a toggle-able local Qwen arm on the Sentry PC.
**Change:** engine manifests under `scripts/engines/`, fail-closed `resolve-engine.py`,
generalized model aliases, generic sandbox exec path, availability-probe requeue.
Full plan: `docs/plans/engine-plugin-architecture.md`.
**Fitness:** engines/models become human-owned configuration; September reshuffle needs no code.
**Risk:** touches `work.sh`/`worker-sandbox.sh` (protected paths). Mitigated: builtin paths
byte-identical, plugins inert until `.env` flags a human sets, red controls before green.
**Human steps after merge:** box CLI/flag verification, provider-allowlist entries, `.env`
enable flags + alias values, Sentry server + tunnel (deployment section of the plan).

## 2026-08-26 — [NEEDS-APPROVAL] Loop telemetry + governance rollout (same authoring session)
status: IN AUTHORING — implementation on the same review branch as D-015

**Shipped (all inert or read-only):** `scripts/usage-reconcile.py` (per-run cost ledger +
weekly one-page rollup; every row split receipted / policy-record / unreconciled — Cursor's
receipt-less metered spend prints as UNKNOWN, which is the September decision input);
`scripts/engine-scorecard.py` (pass/retry/wall-clock/escalations per engine+alias from
on-disk evidence); `scripts/verify-branch-protection.py` + the `plan.sh` automerge-seam
closure (esc-0001); the worker-sandbox hermes usage-file fix (property ordering + mount
target moved out of the masked /run into PrivateTmp; confirm with one metered run); Component 6
connector scaffolding (notify.sh / outbox untouched, zero loadable manifests, five unset
human-owned links before anything can execute); `docs/audits/unlanded-branches-2026-08-26.md`
(all 13 unlanded branches already on master — deletion hygiene only).

**Human steps proposed:**
1. Cron (a human edits cron — rule 3): weekly `usage-reconcile.py ingest` then `rollup`, and
   `engine-scorecard.py --out state/reports/engine-scorecard.md`, after the Sunday brief;
   `verify-branch-protection.py --json state/reports/branch-protection.json` weekly once a
   token exists.
2. `.env`: `RECURSION_ALLOW_AUTOMERGE=0` tombstone; `GITHUB_TOKEN` (repo-admin read) for the
   verifier. Shapes documented in `.env.example`.
3. Branch hygiene: approve the deletion list in `docs/audits/unlanded-branches-2026-08-26.md`.
4. `DECISIONS.md`: record the 2026-08-12/13 review-branch-workflow bypass that audit found,
   and confirm it is no longer happening.

## 2026-08-27 — [NEEDS-APPROVAL] Production-side findings from the cross-platform test-suite pass
status: PARTIALLY APPLIED — Lucas approved the low-risk set in-session (2026-08-27);
items 1–7 and 9–10 are applied on this review branch. Still open: **8** (deploy-box gate —
a design decision) and **11** (shlex escape handling — would change Linux parsing of
backslash-carrying gate commands, so it stays a proposal).

**Context:** post-#77 merge, the full suite was run on Windows and on clean Linux (WSL,
non-root, named branch, no env pollution). Test-side fixes (fixture staging closures,
off-box skip guards, Windows shims) are on this branch. The following need a human call
because they touch production scripts or change Linux behavior.

1. `scripts/worker-sandbox.sh` — logical mode performs NO plan-file permission check; the
   root-only test control expects exit 95 on a group/other-writable plan (check exists only
   in the real-run path, ~lines 210-215). Suggest a mode-only refusal at plan load in all
   modes; root-ownership stays real-run-only. Production real path already enforces both.
2. `scripts/cycle.sh:171` — board commit runs with no `-c` identity and `|| true` swallows
   the failure; as any account without a usable ident the commit silently drops and state
   stays staged (found: non-root Linux). work.sh:341 already does this right. Supply the
   identity and log on failure.
3. Five atomic writers call `os.fchmod` on an open fd (`runtime-state.py:125`,
   `transition_receipt.py:73`, `jsonl_durable.py:126,217`, `notification-outbox.py:102`);
   absent on Windows, and the cleanup's unlink-of-open-file masks the real exception as
   WinError 32 "lock contention". Guard with `hasattr(os, "fchmod")` (style precedent:
   runtime-state.py:983). Latent on Linux too: any pre-fdopen failure leaks the fd and the
   cleanup can replace the primary exception — wrap cleanup, close the descriptor.
4. `notification-outbox.py:89` and `worker-evidence.py:35` — `fsync_dir` lacks the
   `os.name == "nt"` early return the other six modules have.
5. `scripts/audit/hermes-pilot-phase0-baseline.sh:36` — git-common-dir absolute test only
   accepts `/*`; Git Bash returns `C:/...` for linked worktrees, so the shared-authority
   refusal fires via the wrong path off-box. Accept `[A-Za-z]:[/\]*` too.
6. `scripts/intake.sh:66,78` + `scripts/taskctl.sh:58,72` — `$$` handed to the witnessed
   lock is the MSYS pid under Git Bash; `$(cat /proc/$$/winpid 2>/dev/null || echo $$)`
   falls back byte-identically on Linux and unblocks intake/pause-semantics on Windows.
7. `.gitattributes` — pin `state/portfolio.tsv` (and other parser-read tracked files) to
   LF; today only `*.sh` is pinned, so the registry's status column parses as `active\r`
   on Windows checkouts.
8. Design question (control-plane): portfolio-lint's GHOST/STALE/NOKEY against the real
   registry are deploy-box-local, not Linux-local; gating them on `uname` cannot express
   that. Suggest an explicit `RECURSION_DEPLOY_BOX=1` in the box env. Until decided,
   non-box Linux reports 1 FAILED there (a probe like `[ -d /opt/recursion ]` would be
   circular and neuter GHOST on the box).
9. `scripts/tests/intake.test.sh:210,238,250,483,512` — `set -e` at the restore sites of
   `set +e` blocks turns errexit ON for a file that never enabled it, truncating the suite
   on the first nonzero (why it reported rc=73/74 with ~25 checks unreported). Test-side
   but Linux-behavior-changing, so listed here rather than fixed.
10. `scripts/project_authority.py:101` — the `file://` branch gates on
    `Path(parsed.path).is_absolute()`; an RFC 8089 file-URL path is POSIX, so on Windows
    (`WindowsPath`) `/var/tmp/x.git` reads as non-absolute and the transport is refused.
    `PurePosixPath(parsed.path).is_absolute()` is identical on Linux.
11. `scripts/validate-gate.py:152` — `shlex.split()` runs in POSIX mode, destroying
    backslashes before the `.replace("\\", "/")` normalizations at lines 73/96 can act —
    both Windows-tolerance guards are permanently unreachable. Dormant on the box; pairs
    with 10 as latent portability defects.
