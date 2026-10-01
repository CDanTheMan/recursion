# DS-01 — Pause, cancellation, and effect fencing (synthesis)

## Provenance

- Raw report: `raw/ds-DS-01-pause-cancellation.md`.
- Source prompt: DS-01 — pause/cancellation/effect fencing.
- Session: Wave B Deep Research (self-contained handoff, run 2); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved: source-documented, locally directed, inferred, and unverified.
- The report's confidence values describe research support, not probability. Its "expiry" values are review triggers: `Freeze`, `Version`, and `P90`.
- The report states that no implementation, deployment, provider/auth change, spending, PAUSE invocation, merge, or constitutional edit occurred.

## The question

How should a future per-effect PAUSE family be specified so it is safe and mechanically testable, without changing the operative constitution in which ordinary PAUSE is immediate halt?

- The report treats `checkpoint` as the selected *future* ordinary default under `OR-004`, and `OR-020` as authorizing a future policy family.
- Neither is operative until the authorized amendment is actually applied; the report does not reopen either ruling.
- The future family is `checkpoint`, `interrupt`, explicit `drain`, and an independent emergency stop.

## Key findings

**(a) Stopping scheduling or cancelling a process is not sufficient.**

- Admission fencing: a monotonic admission epoch makes pre-epoch, not-yet-executing work `stale` and fail closed.
- Execution containment: running local work reaches a mode-specific terminal boundary (checkpoint, cancellation, enumerated drain, or hard containment) with OS/scheduler process-tree semantics.
- External-effect reconciliation: an effect possibly accepted externally is never treated as undone merely because its caller was killed.
- Unresolved external effects are reconciled through provider identity/status or left `ambiguous` + `quarantined`.

**(b) The invariant is receiver-side fencing.**

- Chubby is cited: a delayed request from a former lock holder can reach a server after ownership changes.
- Proposed invariant: an effect may cross an irreversible boundary only if the recipient, a trusted mediation point immediately before it, or an atomic local transaction validates the current admission epoch and fencing token.
- A controller-only `paused=true` does not prove this invariant.
- Kubernetes force deletion can remove a resource from the API before processes actually stop; Temporal Activity cancellation is cooperative and often heartbeat-mediated.

**(c) Per-effect dispositions differ by class and mode.**

- The report pins 28 claims (7 effect classes × 4 modes): model turn, local transaction, subprocess, remote/disconnected action, read-only gate, publication, and ambiguous external effect.
- Publication and opaque harnesses are consistently narrowed under a "narrower adapter, never wider" rule; a terminal model message that proposes a tool is not a safe checkpoint because an unresolved proposed effect remains.

**(d) Containment primitives are OS/scheduler constructs, not agent APIs.**

- Linux cgroup v2 exposes `cgroup.kill` and observable `cgroup.freeze`.
- Windows Job Objects expose `TerminateJobObject` and nested child jobs; breakaway is flagged as a containment weakness.
- Slurm uses a TERM → `KillWait` → KILL sequence with explicit wait-for-quiescence.
- Agent-level "interrupted" is rejected as proof of process-tree quiescence.

**(e) Model boundaries need protocol evidence.**

- OpenAI's app-server contract distinguishes `turn/completed` statuses `completed`, `failed`, and `interrupted`; the Responses lifecycle exposes terminal completion, and Anthropic streams end with `message_stop`.
- A safe checkpoint requires terminal model evidence *and* no unresolved effect dispatch.
- Where a harness exposes only process/session boundaries, the operation stays opaque unless the adapter proves no effects can escape the admitted envelope; silence or session idleness must not be read as a turn boundary.

**(f) Acknowledgements separate admission closure from quiescence.**

- A pause request can be acknowledged once the epoch advances and the admission gate closes.
- `paused` is reserved until all controllable execution is terminal and every nonterminal external effect is reconciled or explicitly `ambiguous` + `quarantined`.
- Proposed labels: `pause_accepted`, `pausing`, `paused`, `contained`, `stale`, `ambiguous`, `quarantined`, `completed` — each with explicit non-meanings.

**(g) No timeout value is justified; only the rule is.**

- On checkpoint/drain deadline miss without proof of quiescence, the state machine moves to containment.
- Further continuation is then forbidden, the effect-specific interrupt/hard-containment rule applies, and unresolved external effects are classified ambiguous/quarantined.
- Actual durations remain a configuration/Owner question, not a research conclusion.

**(h) Precedence orders control decisions, not history.**

- Order: emergency > revocation > interrupt > checkpoint.
- An emergency stop cannot reverse a durable database commit or an externally accepted action.
- `drain` is not placed in the precedence chain; its arbitration against `checkpoint` is an open schema/Owner question.

**(i) Crash-stage coverage is explicit.**

- Stages B0–B4: before prepare, after prepare, during call, after effect before receipt, after receipt before projection.
- Each mode has a full matrix with disposition codes `S`, `F`, `C`, `K`, `R`, `Q`, `H`, `P`, `D`, `N`; lost receipts are reconciled through provider identity and unresolved mutations are never blind-retried.

**(j) Publication and disconnect get narrower rules.**

- Publication is staged as an immutable private artifact followed by a single conditional visibility mutation (conditional writes / generation-match preconditions).
- A pause before the flip leaves it private; a race is reconciled.
- Signed evidence over disconnect authenticates bytes but not current authorization; reconnect must revalidate GoalSpec version, grant, lease, epoch, fence, PAUSE, and revocation before evidence or derived action is admitted.

## Recommendation and falsifier

- Freeze the future pause family around explicit admission fencing, mode-specific continuation boundaries, typed ambiguity, and proof-based quiescence — not around cancellation requests themselves.
- Each recommendation has a competing option and a decisive falsifier (for example, controller-only checking wins only if no delayed/queued/duplicated old-epoch action crosses a boundary across every transport).
- The report compares keeping immediate halt indefinitely, activating the full future family after the authorized amendment, and staging adoption.
- A single reproducible stale-effect escape falsifies readiness for activation.

## What this does not prove

- It does not change or promote the operative constitution, decide the default, or implement anything.
- It does not select a containment technology or a timeout value.
- It does not show every provider adapter can place a fence close to its irreversible boundary, that opaque harnesses expose equivalent turn boundaries, that provider idempotency/status stays queryable, or that every publication backend supports conditional visibility.
- Local process death is never treated as provider-state evidence, and an accepted external effect is not converted to `failed` or `rolled_back`.

## Open Owner decisions

- Whether `drain` is mutually exclusive with `checkpoint`, and the default drain allowlist (possibly empty).
- Whether publication is ever drain-eligible.
- Whether emergency may perform narrowly defined control-plane reconciliation reads.
- Whether status may read `paused` while remote effects stay ambiguous/quarantined, or needs a distinct `paused_with_ambiguity`.
- Per-effect deadline defaults and maxima.
- The exact capacity-exhaustion field and the definition of an opened-but-not-yet-mutating transaction for checkpoint.
- How long ambiguous effects remain auto-quarantined.
- Whether quiescence proofs are typed evidence objects or adapter-emitted status codes.

## Relevance to later waves

- The fencing/epoch, typed ambiguity, and proof-based quiescence vocabulary is the substrate later pause, revocation, disconnect, and admission work must use.
- The crash-stage matrix and the "exactly one explainable disposition per irreversible effect" invariant are natural model-checking and adapter-conformance targets.
- The open drain/publication/status questions are candidates for explicit Owner decision records rather than further research.
