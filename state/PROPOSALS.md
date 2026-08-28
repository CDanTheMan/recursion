# PROPOSALS — self-improvement proposals for human review

(reset 2026-08-12 for first production launch on Lucas's instruction; pre-Hermes content archived at /var/backups/recursion/pre-launch-scrape-20260812T075324Z)

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
status: APPLIED — Lucas approved the low-risk set in-session (2026-08-27); items 1–7 and
9–10 landed with PR #78. Items 8 and 11 followed the same day on a second review branch at
Lucas's direction: **8** as a tri-state `RECURSION_DEPLOY_BOX` flag (1 = box, 0 = declared
non-box for Linux verification lanes, UNSET falls back to the old uname heuristic — so the
box runs identical rules with no .env or cron change, and weakening its real-registry
checks would take an explicit human act); **11** as a Windows-host-only pre-split backslash
normalization in validate-gate.py — POSIX parsing stays byte-identical, and the sharper
finding is recorded in the tests: on POSIX an unquoted `app\check.py` gate mangles to
`appcheck.py`, which falls OUTSIDE the allowed roots and thereby evades the gate_files
declaration check. Making POSIX normalize too would change Linux parsing, so that
remainder stays open below.

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

## 2026-08-28 — Fixture import chains, round three: the phase-gate audits

status: ON REVIEW BRANCH `claude/phase4-red-intake-chain` — Lucas merges

**Evidence:** the first certification run to include the `hermes-pilot-phase*-red` legs
(box, post-PR77/78 merge `f4e81fa6`) failed phase4-red: its fixture stages `intake.sh`
without `instruction_routing.py`, so poll dies before writing any instruction file.
Verifying the fix exposed the same D-015 disease in `scripts/audit/`: phase2/3/4-green
stage `validate-control-state.py` / `project-pilot.py` / `instruction_routing.py` without
`engine_contract.py` (and, twice in phase3, `pilot_instruction.py`) and die with
ModuleNotFoundError at reviewed master `d632c97` (proven in the WSL lane). Nothing runs
these audits automatically, and phase 4 was the only phase whose green gate never ran its
red leg — that is how both rotted unseen.
**Change (on the branch):** complete the staged chains (tests: phase4-red, author.test.sh;
audits: phase2/3/4-green), and run phase4-red from phase4-green as phases 5–8 already do.
**Verification:** WSL lane red at master (phase4-red rc=1, phase2-green rc=73,
phase3-green rc=1, phase4-green rc=73) → green at the branch tip (all four PASS;
author/intake/phase3-red neighbors PASS). Box red legs 1/2/3/5/6/7/8 all green at
`f4e81fa6`.
**Open residue (not this branch's):** phase1-green, phase1-artifacts, and phase8-green
refuse in the WSL lane for environment reasons (root sandbox, hermes venv, root systemd) —
identically at master and tip, all box-covered. phase6-green fails only its red leg's
check 22 (reversible gate-file tampering vs the OS read-only grading worktree) in the
non-root lane, identically at master and tip, while the same red leg is green on the box
as root — counterintuitive (root normally bypasses read-only) and worth a look; it also
needs >300s there, so any future audit harness should budget 600s. phase6-red's failure
summary hardcodes "(expected on the pre-Phase 6 base)", which misleads when the failure is
current — cosmetic.
