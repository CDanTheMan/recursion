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
