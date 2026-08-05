# Inbox

Where agents write instead of guessing. Clear this manually.

Format:
```
## YYYY-MM-DD HH:MM — <one line>
**Blocked on:** what decision or fact is missing
**Context:** where this came up
```

---

_(empty)_

## build escalation — chiron-001  (2026-08-05T11:05:13Z)
**Workstream:** chiron
**Pointer:** state/tasks/chiron-001.md · branch loop/work/chiron-001 · arm log loop/logs/2026-08-05-arm-chiron-001-110508.out
Blocked on: acceptance test failed after retry
Acceptance: `npm install && npm run build` exited 254
Options: inspect the worktree/branch, fix the task or its acceptance, then `recursion work chiron-001`.

## resolved 2026-08-05T11:26:47Z — chiron-001 PASSED
claude /login done on box; re-ran and acceptance (npm install && npm run build) went green.
Auto-committed to loop/work/chiron-001 (ba02110) at $0.00 on flat Max. Nothing to action.

## build escalation — cubic-castles-001  (2026-08-05T12:53:40Z)
**Workstream:** cubic-castles
**Pointer:** state/tasks/cubic-castles-001.md · branch loop/work/cubic-castles-001 · arm log loop/logs/2026-08-05-arm-cubic-castles-001-121558.out
Blocked on: acceptance test failed after retry
Acceptance: `bash /opt/recursion/scripts/gsc-conformance-gate.sh` exited 2
Options: inspect the worktree/branch, fix the task or its acceptance, then `recursion work cubic-castles-001`.

## DECISION NEEDED — GSC overnight blocked on the model corpus  (2026-08-05T12:58Z)
**Workstream:** cubic-castles (golden-stallion-client renderer)
**What happened:** the build-loop drove cubic-castles-001 (water vertex-alpha). The arm did NOT
fabricate a pass — it correctly diagnosed there is no code defect: the alpha lane is already
implemented, and the two "failing" tests fail only on whole-mesh TOTALS that need the block
model corpus. That corpus (`user-client/render/data/models/blocks`, 1,464 `.modl` ~12 MB) is
**gitignored + Steam/PC-local**, so it is absent from the box clone (0 .modl on disk).
**Scope:** ALL 48 of the 211 conformance tests that fail on the box trace to this one absence.
The gate REQUIRES progress (>=1 failing test flips green), so no task targeting those tests can
ever pass here. 001 failed (exit 2 = no-progress); 002/003 are now `blocked`; the driver stopped
itself after 2 non-passes (no Max quota wasted).
**Unblock (one-time, ~12 MB, NOT anti-cheat sensitive — static model files, no live game):**
  scp the corpus from the PC checkout to the box, e.g. from the machine that has it:
    scp -r golden-stallion-client/user-client/render/data/models  \
        gs-recursion:/opt/golden-stallion-client/user-client/render/data/
  (or regenerate from DynaContent/models/blocks per that repo's .gitignore note.)
**After it is present:** re-queue with `sed -i "s/^status: blocked/status: queued/" state/tasks/cubic-castles-00{1,2,3}.md`
then relaunch `nohup env RECURSION_ROOT=/opt/recursion GSC_DEADLINE_MIN=360 bash scripts/gsc-overnight.sh &`.
Only then does the offline gate have tractable PROGRESS to measure.

## 2026-08-05 12:58 — Provide the PC-local block-model corpus to unblock Cubic Castles conformance
**Workstream:** cubic-castles
**Pointer:** CURRENT INBOX: “DECISION NEEDED — GSC overnight blocked on the model corpus”; `golden-stallion-client/user-client/render/data/models/blocks`
**Blocked on:** the 1,464 gitignored `.modl` files (~12 MB) are absent from the box; all relevant conformance tasks require them.
**Context:** cubic-castles-001 correctly found the alpha lane already implemented, but the gate cannot measure whole-mesh totals without the corpus. Tasks 002–003 are blocked.
**Options:** copy `user-client/render/data/models` from the PC checkout to `/opt/golden-stallion-client/user-client/render/data/`; or regenerate `models/blocks` from `DynaContent/models/blocks`.
