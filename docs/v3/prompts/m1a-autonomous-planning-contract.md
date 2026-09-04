# Construction prompt — M1A autonomous-planning contract and replay baseline

This prompt is a handoff artifact. It does not authorize itself. Execute it only after Lucas
supplies an exact repository/worktree, starting commit, branch, implementation authority and
commit policy.

## Goal

Build the pure M1A contract in `docs/v3/M1A-AUTONOMOUS-PLANNING.md` and the canonical semantics in
`docs/v3/AUTONOMOUS-PLANNING.md`: authenticated Owner intent → accepted immutable GoalSpec → ARM
PlanRevision/task DAG → admitted TaskNode → deterministically derived bounded WorkPacket → exact
GateResult → bounded novelty retry/replan/escalation → verified terminal plan, with byte-identical
in-memory replay.

This is schema/validation/replay construction only. It must not claim or create a v3 runtime,
provider integration, performance result or external-effect safety.

## Exact allowed paths

- `schemas/control-plane/v3/planning/**`
- `scripts/v3/planning/**`
- `scripts/tests/v3/planning/**`
- `docs/v3/**`

Do not edit anything else. Preserve newer compatible work. Never reset, discard, rebase or revert
to force a requested starting commit. Stop if the actual branch/source or dirty work overlaps the
task.

## Non-goals and prohibitions

No provider/model/API/network call; terminal or subprocess; plugin import/execution; SQLite or
other database; v1/v2 migration; credential/account/config/environment change; Git operation from
M1A code/tests; publication, push, merge, deployment or service change; live PAUSE change;
external effect; UI; native agent loop; scientific adapter; production default; constitutional
amendment; benchmark/superiority claim; secret/private-canary/private-project fixture.

Unknown fields, unknown schema/policy versions, missing authority/verifier/source/budget/privacy
bindings and ambiguous effects fail closed. Current `current-immediate` PAUSE is operative;
checkpoint/interrupt/drain are representable future policies only.

## Required sequence

1. Read repository instructions, `CONTROL_PLANE.md`, `ANCHOR.md`,
   `docs/v3/AUTONOMOUS-PLANNING.md`, `docs/v3/M1A-AUTONOMOUS-PLANNING.md`, `docs/v3/GLOSSARY.md`,
   `docs/v3/M1A-WIRE-PROFILE.md`, `docs/v3/M1A-FIXTURE-ORACLES.md`, `docs/v3/ACCEPTANCE.md` and
   relevant existing schema/test conventions completely.
2. Record preflight branch, exact HEAD, ancestor, clean status and changed-path boundary.
3. Implement M1A-01 through M1A-07 in dependency order. M1A-01 mechanically translates the exact
   wire profile into strict JSON Schemas and obtains review of that exact schema-only commit. It
   must stop rather than select another field, nesting, union, bound, nullability or digest rule.
4. M1A-02 expands the oracle blueprint into literal strict-JSON red bundles and a manifest with
   literal canonical digests, ordered receipts/events, error codes and final-state digests.
   Validate them against M1A-01, demonstrate they fail before reducer code, and obtain review of
   that exact red commit. Any schema/profile/oracle change is a new reviewed PlanRevision, never
   an implementation convenience.
5. Implement RFC 8785 digesting, cross-record attenuation, amendment disposition,
   DAG/path/effect admission, pure TaskNode/WorkPacket/gate/retry/replan/escalation, lease/PAUSE
   fencing, idempotent commands and pure event replay.
6. Implement every F-M1A-001–023 fixture with its exact expected result and falsifier. Do not
   weaken an oracle to make implementation pass.
7. Run every machine gate in M1A plus the full unchanged
   `scripts/tests/recursion-v2-mvp.test.py` suite. Run replay/fixtures twice.
8. Obtain an exact-candidate independent verifier receipt. Same-family review must be labeled
   same-family; unavailable required verification blocks.
9. Commit only coherent local checkpoints if Lucas's execution prompt authorizes commits. Never
   push, publish, merge or deploy.

## Stop and escalate

Stop with the smallest conflicting fixture if current/future authority cannot be represented
separately; a schema term has two canonical owners; validation needs model judgment, network or
operational state; any child can widen; replay needs wall time/random/environment; ambiguous
effect can become success; implementation requires an out-of-scope path; or a required verifier
is unavailable. Do not decide an Owner/constitutional/provider/spending question in code.

## Acceptance

All thirteen gates and F-M1A-001–023 in `docs/v3/M1A-AUTONOMOUS-PLANNING.md` pass on the exact
candidate. Report starting/final HEAD, local commits, every changed path, exact commands/results,
fixture counts, verifier identity/independence limits, unresolved claims and a clean final tree.
Do not report documentation or fixture conformance as proof that a runtime exists.
