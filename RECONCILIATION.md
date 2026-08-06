# Reconciliation branch — `reconcile/loop-auto`

**Purpose.** `origin/master` (GitHub main) and `loop/auto` (the box's live, deployed working branch)
had **divergent histories** — main was still at the dispatcher-v1 era while `loop/auto` carried 40
newer commits built on a parallel history. They were not fast-forwardable, and a force-push was off
the table (it would discard main's unique commits). This branch is a **clean merge of both**, prepared
for your review so you can land it on `main` and end the divergence.

**How to review:** `git fetch && git diff origin/master...reconcile/loop-auto` (or open it as a PR).

## Resolution policy

| Kind | Winner | Why |
|---|---|---|
| **Live loop CODE** (13 conflicts: `bin/recursion`, `scripts/{board,cycle,dispatch,fallback-watch,pause,resume}.sh`, `loop/supervisor/run.sh`, `loop/config/routing.yaml`) | **loop/auto** | It is the version actually running and tested on the box — the deployed truth. |
| **`state/DECISIONS.md`** | **merged clean (no conflict)** | **D-001 … D-008 all preserved** — both histories' decisions are present. |
| **`docs/architecture.md`** | **origin/master** | Docs: completeness wins, not deployment. main's version is fuller (240 vs 130 lines — it has the model-roster / observability / PC-escape-hatch / AI-compute sections loop/auto's lacked). |
| **`docs/access.md`** | loop/auto | Both 62 lines / equivalent. |
| **`docs/chiron-design.md`** | preserved (main-only file) | main's unique design doc — kept. |
| **`.gitignore`, `.env.example`** | **union** | Kept every entry from both sides so no ignore-rule or documented var is lost. `.env.example` verified free of real secrets. |
| all new loop/auto files (work.sh, reflect.sh, gates, drain/plan/publish, gsc-renderer roadmap, chiron scaffold, …) | loop/auto | main didn't have them. |

## Verified after merge
- All resolved shell scripts pass `bash -n`.
- `state/DECISIONS.md` contains D-001 … D-008.
- `docs/chiron-design.md` present; live code + gates + chiron scaffold present.
- `.env.example` carries no real secret values.

## After you merge this to `main`
Tell me (or just merge) and I will **fast-forward `loop/auto` to `main`** so the box's working branch
== main from then on — **zero divergence going forward**, and the autonomous Chiron chain can build
pages 2–5 off a coherent base (I'll re-enable `RECURSION_AUTO_PLAN=1` at that point).

Nothing here is on `main` yet — this is a review branch. `main` is untouched until you merge.

---

## RESOLVED 2026-08-06 — the divergence is gone

Measured on the box: `git rev-list --left-right --count origin/master...loop/auto` = **0 / 16**.
`origin/master` has **no** commits that `loop/auto` lacks, so `loop/auto` is now a strict
superset and `master` is **fast-forwardable** to it. `apps/chiron` is present on `origin/master`,
which also clears the 2026-08-05 chain-bootstrap blocker (a task branching from a scaffold-less
base and reinventing the app).

The body above is retained as the record of WHY the histories diverged and how the merge policy
was decided — that reasoning is still the precedent for the next divergence. Only its "currently
divergent / not fast-forwardable" *status* is stale.

**Merge order for the current review queue** (a dependency lands before what builds on it):
`loop/auto` → then the `rebase/*` branches in their numbered order.
