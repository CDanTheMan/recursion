---
title: M1A autonomous-planning construction campaign
status: active-local-construction
last-updated: 2026-09-03
---

# M1A autonomous-planning construction campaign

This is the inspectable campaign record authorized by Lucas on 2026-09-03. It governs local
construction only. It does not make the proposed v3 constitution operative and does not prove or
create a Recursion v3 runtime.

## Owner intent and immutable GoalSpec

The exact Owner instruction is the 14,467-byte UTF-8 campaign prompt with SHA-256
`fe0d94d8caa3d512d2b673098430ffdde8a6b8a6eeb3e528f4fa8b1b38483511`. Its operative intent is:

> Begin the Recursion v3 M1A autonomous-development campaign. Lucas authorizes construction and
> coherent local commits for M1A under the stated paths, non-goals, execution order, worker
> assignments, stop conditions and acceptance gates. Do not push, merge, publish, deploy, change
> production, create external effects, amend the constitution, change providers or credentials,
> or enable metered spending.

The campaign GoalSpec below is immutable. A change requires a new PlanRevision; this section is
not rewritten.

| Field | Accepted value |
|---|---|
| Goal ID | `GOAL-REC-V3-M1A-001` |
| Parent goal | Demonstrate the pure deterministic autonomous-planning contract described in [M1A](M1A-AUTONOMOUS-PLANNING.md) |
| Outcome | Authenticated Owner intent becomes an accepted GoalSpec, immutable ARM plan/task DAG, admitted task, derived bounded WorkPacket, exact gate outcome, bounded retry/replan/blocker/escalation and verified terminal projection with byte-identical replay |
| Source | Accepted baseline `a59d061a28bc182eedd41f8e29e65bbe7fb1e13f` and the canonical M1A documents named below |
| Branch | `codex/v3-m1a-autonomous-planning` |
| Worktree | Dedicated local `recursion-v3-m1a-autonomous-planning` worktree |
| Output class | Strict schemas, pure Python validation/decision/replay, sanitized literal fixtures, tests and documentation receipts |
| Terminal condition | All thirteen M1A gates pass on one exact clean candidate and exact-candidate Terra adjudication returns PASS |
| Publication | Forbidden |

## Boundaries

Allowed paths are exactly:

- `schemas/control-plane/v3/planning/**`
- `scripts/v3/planning/**`
- `scripts/tests/v3/planning/**`
- `docs/v3/**`

Everything else is denied. M1A code and tests have no provider, model, API, network, terminal,
subprocess, plugin, database, Git, publication, deployment, service, credential, configuration,
live-PAUSE, wall-clock, randomness, environment or ambient-filesystem dependency. The tests may
read only their sanitized fixtures. M1A does not perform an external effect or claim runtime,
performance, superiority, migration, production, private-canary or private-project evidence.

Privacy is synthetic/public-safe only. Egress from M1A code and tests is none. Worker research is
read-only against this local worktree and returns recommendations to Sol. Routes are the
Owner-authorized GPT-5.6 Sol lead, two waves of GPT-5.6 Luna workers and two GPT-5.6 Terra
adjudicators, all at `xhigh` for workers and adjudicators; these are same-family routes. Spending
authority is zero: only the existing non-metered Codex allowance may be used. Sources are the
accepted baseline, the canonical documents below and existing repository conventions; no ambient
or private source is admitted.

Canonical ownership remains:

- [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md) for semantics;
- [M1A-WIRE-PROFILE.md](M1A-WIRE-PROFILE.md) for JSON encoding;
- [M1A-FIXTURE-ORACLES.md](M1A-FIXTURE-ORACLES.md) for the closed oracle;
- [M1A-AUTONOMOUS-PLANNING.md](M1A-AUTONOMOUS-PLANNING.md) for construction and gates; and
- `CONTROL_PLANE.md` for the operative constitution.

## Acceptance gates

The exact gate is the thirteen-item list in [M1A](M1A-AUTONOMOUS-PLANNING.md#machine-checkable-acceptance-gates):

1. reviewed one-to-one strict schema translation;
2. pre-reducer literal red-bundle manifest with exact SHA-256 and final digests;
3. strict parser, meta-schema, version, ID, digest, I-JSON and bound rejection;
4. F-M1A-001–023 pass twice from clean in-memory state;
5. attenuation property tests find no authority/privacy/egress/path/route/budget/effect widening;
6. graph property tests reject cycles, missing dependencies and unordered ownership conflicts;
7. genesis/checkpoint replay is byte/digest identical and corrupt/gapped/unknown events refuse;
8. static isolation scan finds no forbidden adapter, I/O or external-effect dependency;
9. reducer determinism tests find no time/random/environment/filesystem observation;
10. unchanged `scripts/tests/recursion-v2-mvp.test.py` passes without being called v3 proof;
11. candidate-range diff, allowed-path, relative-link and private/secret scans pass;
12. the exact candidate begins and ends its gate clean; and
13. exact-candidate independent rerun records its same-family limitations and returns PASS.

## PlanRevision 1 — initial

`PLAN-M1A-001@1` is the initial immutable revision. Trigger: the Owner instruction digest above.
Prior revision: none. Every node is retained by this initial revision; no task is invalidated,
quarantined or superseded.

| Node | Depends on | Output | Gate |
|---|---|---|---|
| M1A-01 | Owner authorization and preflight | strict schemas and schema-only tests | one-to-one wire translation and reviewed exact commit |
| M1A-02 | M1A-01 | literal red fixtures and digest manifest | structural validation plus expected red behavior before reducer |
| M1A-03 | M1A-02 | RFC 8785 and cross-record attenuation | canonical/digest and attenuation tests |
| M1A-04 | M1A-03 | deterministic DAG/path/effect admission | whole-graph property tests |
| M1A-05 | M1A-04 | decider, reducer, packets, leases, fences and replay | transition/idempotency/replay tests |
| M1A-06 | M1A-05 | complete conformance closure | F-M1A-001–023 and all machine gates pass twice |
| M1A-07 | M1A-06 | exact-candidate disposition | Terra PASS with commands, candidate and limitations |

Any change appends a new revision below with triggering evidence and explicit retained,
invalidated, quarantined and superseded tasks. Revision 1 is never silently edited.

## Worker WorkPackets and verifier assignments

All workers are read-only: no edit, commit, configuration change, Git mutation or nested agent.
Each packet must report worker ID, exact model/effort/candidate, assigned question, inspected files
and commands, findings, contradictory evidence, exact recommendations, decisive falsifier,
confidence and unresolved questions, with no hidden chain of thought.

| Worker | Model / effort | Lane and bounded packet | Candidate / assignment |
|---|---|---|---|
| LUNA-M1A-01 | `gpt-5.6-luna` / `xhigh` | wire-profile record/union/bound/null/sort/digest inventory and unresolved-choice audit | Wave 1; campaign preflight commit |
| LUNA-M1A-02 | `gpt-5.6-luna` / `xhigh` | F-M1A-001–023 literal input/receipt/event/error/state/digest/manifest red plan | Wave 1; campaign preflight commit |
| LUNA-M1A-03 | `gpt-5.6-luna` / `xhigh` | schema/Python/test/dependency/canonicalization convention audit | Wave 1; campaign preflight commit |
| LUNA-M1A-04 | `gpt-5.6-luna` / `xhigh` | adversarial authority, policy, budget, route, amendment, PAUSE, lease and verifier tests | Wave 1; campaign preflight commit |
| LUNA-M1A-05 | `gpt-5.6-luna` / `xhigh` | RFC 8785, I-JSON, duplicate-key, lookup, attenuation and property review | Wave 2; exact schema/red-fixture commits |
| LUNA-M1A-06 | `gpt-5.6-luna` / `xhigh` | DAG, compatibility, lifecycle, gate, novelty, retry, replan and escalation review | Wave 2; exact schema/red-fixture commits |
| LUNA-M1A-07 | `gpt-5.6-luna` / `xhigh` | command/event/receipt reducer, precedence, idempotency, checkpoint, fencing and replay review | Wave 2; exact schema/red-fixture commits |
| LUNA-M1A-08 | `gpt-5.6-luna` / `xhigh` | adversarial minimization, isolation, determinism, dependency and v2-compatibility audit | Wave 2; exact schema/red-fixture commits |
| TERRA-M1A-01 | `gpt-5.6-terra` / `xhigh` | adjudicate exact schemas and red oracle; PASS or DISSENT blocks reducer on material defect | after M1A-01 and M1A-02 |
| TERRA-M1A-02 | `gpt-5.6-terra` / `xhigh` | rerun full gates and inspect exact final candidate; PASS or DISSENT | M1A-07 exact candidate |

Sol is lead, integrator and sole writer. Sol owns preflight, decomposition, implementation,
reconciliation, commits, gate execution and the final report. Terra is same-family adjudication,
not cross-family independence.

## Admission evidence

At campaign start, HEAD was the accepted baseline, the branch and worktree were new and clean,
the baseline was not an ancestor of the then-current `master`, and `state/PAUSE` was absent. The
allowed output directories contained no prior M1A implementation. Before Wave 1, the host had
31.61 GiB free physical memory, 641.44 GiB free on the workspace drive, negligible sampled CPU
load and an 11.8 ms directory probe. Codex reported 27% of the current non-metered window used,
no metered credits and no spend-control block. This admits four read-only Luna workers.

## Stop conditions and Lucas decision seams

Stop on an undocumented schema choice, competing canonical owner, weakened oracle,
nondeterministic reducer input, any descendant widening, current/future constitutional-policy
conflation, ambiguous-effect success, out-of-scope path, missing required verifier, incompatible
newer work, or a requirement for policy, spending, provider, credential or constitutional action.

Lucas remains the only decision seam for GoalSpec/constitution changes, privacy or egress
widening, spending, provider/configuration changes, publication, deployment, merge and an actual
exceptional verifier downgrade. On 2026-09-03 Lucas delegated bounded construction judgment to
Sol for later choices that improve performance, quality, design, configuration or efficiency,
provided each consequential choice is routed through Sol, researched before final disposition and
recorded here. That delegation does not override the allowed paths, non-goals, stop conditions or
operative constitution.

## Later PlanRevisions

### PlanRevision 2 — blocked before M1A-01

`PLAN-M1A-001@2` was appended after all four Wave 1 read-only reviews of exact candidate
`a256ad2ee7104f7abb1b679fc415afc49291556f`. The triggering evidence is recorded in
[M1A-CONSTRUCTION-BLOCKER.md](M1A-CONSTRUCTION-BLOCKER.md).

- Retained: the immutable campaign GoalSpec, allowed paths, non-goals, stop conditions,
  campaign-preflight commit and all four Wave 1 research receipts.
- Invalidated: the assumption that M1A-01 can mechanically translate the accepted profile
  without a schema choice.
- Quarantined: no code, schema or fixture output exists to quarantine.
- Superseded: Revision 1's admission schedule. M1A-01 is blocked; M1A-02 through M1A-07, Wave 2
  and both Terra adjudications are not admitted because their prerequisite exact commits do not
  exist.
- Required actor: Lucas, as Owner of the accepted construction intent and semantic decision seam.
- Exact next action: approve a reviewed canonical-document revision that removes the event/error
  token contradictions and defines acyclic plan/node and receipt/state digest construction. The
  additional closed-wire gaps in the blocker receipt should be resolved in the same review before
  the campaign is resumed.

### PlanRevision 3 — Owner-approved repair and resume

`PLAN-M1A-001@3` is appended from two authenticated Owner messages on 2026-09-03. The first exact
144-byte UTF-8 message has SHA-256
`df3630779501b8c2fc29548fbdf77c2708e3ec62c19618ca2170de29b04ff462`:

> Beautiful! Thank you for the recommendations. They align with my vision. I approve all
> recommended decisions to unblock and resume the campaign.

The second exact 289-byte UTF-8 message has SHA-256
`0fdb666f73355b92d0447799459b74276b84f45a3e6cca0d941567c983969715` and delegates bounded
construction judgment to Sol while requesting researched decisions and coherent commits.

> If other recommended decisions arise. I approve you to make changes as long as it optimizes
> performance, quality, design, configuration, and efficiency. Just make sure decisions go through
> you so they can be researched towards the end of development. Be sure to commit as needed. Thank
> you

The approved canonical repair is exact:

1. PascalCase event names use `EventType`; uppercase `E-*` errors use `ErrorCode`; lowercase
   protocol values continue to use `Token`.
2. `PlanRevision` binds full TaskNode digests while each TaskNode carries only its plan ID/version.
   Projection state stores receipt identity and command digest; each receipt binds the complete
   before/after state digests.
3. Invalid JSON or schema-invalid input returns a typed `DecodeFailure` and creates no
   `CommandReceipt`; structurally valid but refused commands receive a receipt.
4. The closed wire adds the minimum carriers and bindings named in the Wave 1 receipt: pause
   directives, Owner verifier exceptions, executive-lease replacement, atomic Owner amendment
   plus separate ARM plan attestation, verifier assignment, authority/egress/account/capacity/budget
   bindings, exact genesis and derived-digest operands, and isolated cases within each fixture
   bundle.

Disposition:

- Retained: the immutable GoalSpec, all campaign boundaries and non-goals, both prior campaign
  commits and all four Wave 1 receipts.
- Invalidated: Revision 2's unresolved-owner-decision state.
- Quarantined: none; no code, schema or fixture was created under the blocked revision.
- Superseded: only Revision 2's blocked schedule.
- Re-admitted: M1A-01 through M1A-07 in their original sequential dependency order. Wave 2 and
  Terra remain gated on the exact schema/red-fixture commits.

Consequential implementation decisions made under the second authorization will be appended to
this revision with evidence, alternatives and falsifiers. They may refine implementation inside
the approved contract but may not silently amend its semantics.

Construction decision `CD-M1A-001`: composite commands place every newly admitted immutable
record in the event group's `primary_record` or `related_records`, rather than carrying only
unresolvable refs. Receipt/event IDs are deterministic functions of command IDs, accepted receipt
identities alone enter the authoritative projection, and the command admission API carries a
separate explicit receipt journal for refused-command idempotency. Evidence: otherwise event-only
replay cannot reconstruct TaskNodes, transitions, new GoalSpecs, leases or routes, and refusal
receipts would create unaudited state changes despite `NOEVENT`. Rejected alternatives were an
ambient record store and events that point to command payloads. Falsifier: genesis plus the event
and receipt lists cannot reproduce byte-identical projection and duplicate behavior without an
ambient lookup.

Construction decision `CD-M1A-002`: `start-arm-run` carries its initial executive lease, and
`derive-work-packet` carries its initial work lease and route assignment while referring to a
previously admitted budget reservation and capacity observation. Evidence: an empty-genesis happy
path otherwise refers to records that no command can admit. This retains the 21-command alphabet
and gives every authority/capacity/budget binding a replay-visible origin. Falsifier: a closed
happy-path bundle still requires a fabricated or unresolved lease, route, capacity or budget ref.

Construction decision `CD-M1A-003`: WorkPackets are kernel-derived from a closed exact operand
set, use a deterministic seed-based ID, and copy TaskNode action/prohibition sets plus all bounded
GoalSpec/TaskNode/lease/route/budget fields. Evidence: an expected packet digest alone cannot tell
two implementers how to construct the same complete record, and the prior TaskNode shape had no
source for required action/prohibition fields. A caller-supplied complete packet was rejected
because it would make the caller, rather than the kernel, the packet authority. Falsifier: two
implementations following the documented derivation produce different packet bytes or a packet
widens any parent binding.

Construction decision `CD-M1A-004`: the executable contract is one self-contained Draft 2020-12
schema generated deterministically from a checked-in declarative Python materializer. Non-native
byte-size and sorted-array constraints are explicit `x-*` annotations exercised by the strict
schema test validator; duplicate keys, nesting and I-JSON restrictions are enforced before schema
validation. Evidence: splitting 128 mutually recursive definitions across files adds resolver and
packaging failure modes, while raw JSON Schema cannot express UTF-8 byte counts or general sorted
arrays. The materializer is build tooling, not reducer runtime, and regeneration must be byte
identical. Falsifier: a clean regeneration changes `schema.json`, any registered union arm lacks a
valid closed instance, or a strict annotation is accepted without enforcement.

Construction decision `CD-M1A-005`: each fixture case has typed `ReplayExpectation@1` entries
whose event inputs are literal JSON strings. Evidence: F-M1A-018 requires valid, corrupt, gapped
and unknown-version replay inputs and expected errors, but the original bundle shape could encode
only schema-valid initial/expected events and command receipts. Raw event strings preserve the
distinction between decode and replay refusal without weakening the enclosing bundle. This
supersedes the first M1A-01 schema candidate and requires a replacement schema-only commit before
M1A-02 freezes. Falsifier: F-M1A-018 still cannot encode every required replay result literally or
an invalid event escapes into a typed event array.

Construction decision `CD-M1A-006`: leases, route assignments and WorkPackets carry nullable
typed supersession refs. Evidence: replacement events contain no command payload or ambient lookup,
so without the prior ref replay can create the replacement but cannot deterministically fence the
old record. Initial records use null; replacements must name the exact current prior record. This
also supersedes the preceding M1A-01 schema candidate before fixture freeze. Falsifier: replay can
leave two current leases/routes/packets or needs command storage to identify the stale record.

Construction decision `CD-M1A-007`: the final pre-freeze profile adds (a) a typed checkpoint
envelope containing the exact pre-event projection, (b) `record-checkpoint`/
`CheckpointRecorded`, (c) typed sorted refusal witnesses, and (d) structurally representable but
non-operative future PAUSE directive modes. Evidence: without these, checkpoint replay and route
replacement have no admitted checkpoint, graph refusals cannot satisfy the promised stable witness,
and F-M1A-015 becomes a schema failure instead of the required policy refusal. This expands the
closed alphabet to 22 commands and 27 events including five disposition events, and supersedes all
earlier M1A-01 candidates. Falsifier: any required fixture still needs an untyped side channel,
cannot preserve a stable refusal proof, or admits a future PAUSE mode under current policy.

Construction decision `CD-M1A-008`: conflict receipts and disposition records use explicit
digest-derived IDs, and the disposition target type selects one exact event type. Evidence: a
conflict response cannot safely reuse the retained original receipt ID, while ordered disposition
events otherwise lack deterministic record IDs and type selection. Falsifier: identical inputs
produce different IDs/event types, a conflict aliases its original receipt, or replay requires the
amendment command payload to reconstruct a disposition event.

Construction decision `CD-M1A-009`: fixture setup and standalone replay expectations carry the
exact associated command/receipt sequences as well as events. Evidence: an event contains only a
command ID/digest, so replay cannot recheck actor, attestation, lease, before/after state or event
span from the event alone. Explicit provenance prevents hidden trusted fixture state and keeps
invalid events isolated as raw strings. This supersedes the prior schema candidate before fixture
freeze. Falsifier: replay validates an authority/receipt relation using ambient data or a fixture
event has no unique command and receipt source.

Construction decision `CD-M1A-010`: M1A-02 stores one literal bundle per canonical fixture ID,
with isolated named cases inside the bundle, plus one generated byte-addressed manifest. The
manifest enumerates the final 133 schema definitions, 22 commands, 27 events, 27 errors, 25 domain
records, four projection terminal states, and per-bundle command/receipt/event/decode/replay counts
and final projection digests. Evidence: isolated cases preserve the canonical F-M1A-001–023
registry without inventing extra fixture IDs, while complete registry equality prevents an
untested closed union arm from hiding behind a valid bundle. The red runner validates syntax,
schema closure, canonical digests, event chains, receipt bindings, raw replay falsifiers and
manifest bytes before failing only at the absent reducer boundary. Rejected alternatives were
one enormous corpus file and one file per subcase. Falsifier: a required schema/command/event/error/
record disappears without invalidating the manifest, or any literal file differs from regenerated
bytes.

Construction decision `CD-M1A-011`: generated schema, fixture and Python files are pinned to LF by
directory-local Git attributes. The ordered replan disposition leaves its replacement ref null and
uses the typed PlanTransition to bind the exact replacement, avoiding an impossible PlanRevision
self-digest; the refused metered-route candidate carries a typed checkpoint ref while route-spend
precedence remains its oracle. Evidence: `core.autocrlf=true` otherwise makes a clean Windows
checkout change manifest bytes, a PlanRevision cannot contain its own final digest, and a packet
masquerading as a checkpoint would introduce a second failure. Falsifier: clean Windows/Linux
checkouts differ, the transition fails to bind the replacement, or the route case has another
earlier decisive error. These choices are assigned to Wave 2 and Terra for adversarial review.

### M1A-01 and M1A-02 construction receipt

- Final schema-only commit: `ab9707480baf6ef7baff03b6bda444b890d78557`.
- Literal red-oracle commit: `b303ffd2c9af4a00e59d380cd7052395c33c4a4e`.
- Manifest SHA-256: `f6d8ff54ff3d9dcffbfd6607153d7ed68e774a71fdf0a302e3cdc3f12a38f9ca`;
  bound schema SHA-256:
  `b9cf727d5bef625b93b26dcd2510fc0a48f5b1d4c1cdbb8117c7463c4531943a`.
- Corpus: 23 fixture bundles, 34 isolated cases, 242 commands and receipts, 225 events,
  8 decode failures and 6 replay cases; every closed command, event, error and domain-record arm
  appears.
- `python schemas/control-plane/v3/planning/materialize.py --check`: pass.
- `python scripts/tests/v3/planning/schema.test.py`: 15/15 pass.
- `python scripts/tests/v3/planning/materialize_fixtures.py --check`: pass.
- `python scripts/tests/v3/planning/red_fixture.test.py --validate-only`: pass.
- `python scripts/tests/v3/planning/red_fixture.test.py`: expected exit 1 because the reducer is
  absent; all 14 positive fixture bundles stop at that single boundary.
- `git diff --check` and authorized-path scan: pass. No reducer code exists in this receipt.

M1A-01 and M1A-02 are complete construction nodes, not a complete M1A or runtime claim. M1A-03
remains gated on Wave 2 review and TERRA-M1A-01 PASS for this exact candidate lineage.
