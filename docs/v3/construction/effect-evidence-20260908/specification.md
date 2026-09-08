# Literal effect evidence experiment — 2026-09-08

Parent: `goal-recursion-v2-execution-fabric`. Frozen input commit and limits are in
[goal.json](goal.json), [manifest.json](manifest.json), and [plan.json](plan.json).
This specification precedes the first admitted experiment. No runtime permission,
production authentication, distributed completeness or full formal freeze follows.

## Competing mechanisms and disposition

1. Translate the M1A aggregate label directly into M1C receipt records: **reject**.
   The closed M1A observation lacks original key, target, payload, admission and
   ordered attempts; admission of a label does not establish external truth.
2. Authenticate each supplied observation independently: **insufficient alone**.
   Removing a later unresolved attempt can leave an authentic successful prefix.
3. Join a historical observation to a separately authenticated original intent,
   admission, ordered evidence inventory and explicit cut: **construct locally**.
   Reuse immutable M1 validators and the pure M1C oracle; build only the restricted
   adapter, test evidence and independent expected-result audit. No upstream fork.

The test uses standard-library HMAC-SHA256 with fresh, external, synthetic keys.
This is an executable provenance counterexample mechanism, not a product crypto
choice. A separately supplied verifier keyring fixes collector, dispatcher and
observer roles. MACs bind a domain, role, issuer and exact body. The collector binds
the full ordered inventory, historical prefix length, M1A records and current
assessment context. The dispatcher binds original intent/admission and starts;
the observer binds each non-start record and ordinal. Neither an observer MAC nor
an M1C `authenticity=verified` string grants dispatcher authority. The trusted
collector's knowledge of completeness is an assumption, not a proved property.

## Mapping contract

Retain the exact observation, packet, GoalSpec, plan, work lease, route and budget
records. Validate their M1A schema, digest and exact references. M1C IDs use explicit
typed prefixes around M1A IDs. M1A bare digests retain their original codec and
become opaque `sha256:` references, never rehashed with M1C canonical bytes.
Original idempotency key and provider-operation references use declared raw UTF-8
SHA256; receipt digest uses the exact M1C canonical receipt bytes, including LF.
These digest interpretations restrict this adapter; arbitrary historical digest
provenance cannot be recovered and must be rejected or separately supplied.
Check internal plan→goal/task, budget→goal/plan/task, lease→task and route→actor
relationships too; valid signatures and outward references do not replace them.

Supplemental original intent supplies target, payload, dispatch command identity,
deadline and admission. Its effect, actor, GoalSpec/plan, lease, policy, privacy,
route and budget must bind the retained packet context. The synthetic grant binds
that packet and its authority IDs; it is not an operational authority grant.
Packet `attempt` and effect `attempt_number` are distinct. No equality is assumed.
Typed mapping records declare the source PAUSE epoch and goal fence and their
fixture M1C domains: fixture admission epoch = PAUSE epoch + 1, fence = goal fence.
This explicit embedding does not identify the authority domains. UTC timestamps
are supplied original fixture evidence; logical time is not converted to UTC.

The immutable observation label is checked against its signed historical prefix,
using original assessment epochs. The full evidence cut is independently schema
validated and classified using separately supplied current epochs. Every original
receipt/operation digest must bind a specific record in that prefix. A late receipt
cannot replace those bindings. Missing evidence blocks the join; the adapter never
creates an observation to force the aggregate label to agree. Successful output is
classification **as of the supplied trusted cut**, with no permit and no writes.

Construction-stage preregistration refinement before run03: literal M1C can report
an earlier success when a later start has no external observation yet. Preserve
that literal result, but separately track ordered unsettled starts and require a
runtime reconciliation hold. Test `later-start-only` explicitly. This diagnostic
is a conservative experimental addition; it neither changes M1C nor clears M1A.

## Preregistered discriminating cases

- Literal success and failure; dispatched ambiguous prefix; late same-attempt
  receipt and reconciliation; unverified possible effect; conflicts; unresolved
  earlier attempt followed by a later receipt; stale current epochs with retained
  historical success. Each has a hand-stated expected status/reason requirement.
- Missing supplemental fields; wrong key, target, payload, issuer, role, MAC or
  domain; changed packet/goal/plan; wrong digest codec or provider identity;
  omitted/reordered inventory; malformed attempt ordering/time and duplicate IDs.
  Separate binding/authentication failures from literal schema-invalid inputs.
- Remove one adapter guard at a time in an explicit test argument; require a
  counterexample for context binding, trusted inventory and role isolation.
- Replay frozen F-M1A-014 setup through the actual kernel. The same otherwise-valid
  observation payload accepts while running and refuses `E-PAUSED` after literal
  `apply-pause`; only expected projection digest/version and envelope seal change.
  Refusal emits no event and leaves the projection unchanged; its journal grows.
- Temporarily remove only the observation command from the actual in-memory
  `PAUSE_SENSITIVE` set, restoring it in `finally`: the paused command must accept.
  Frozen files remain unchanged. An exact duplicate accepted before PAUSE returns
  its original receipt, with no event; it is not a fresh admission.
- Record ambiguity and later success through actual M1A admission: retained
  ambiguity/quarantine must remain. M1C settlement cannot silently clear it.

## Limits and interpretation

One provider-free process, at most 256 cases, 180 seconds, 512 MiB observed peak,
128 MiB retained artifacts. Timeout kills and waits for the owned process. There
is no OS sandbox claim. No live provider call, product write or credential is used.
All admitted sources are committed first; every attempt and its raw sources,
synthetic inputs, output, failure and timing remain outside the candidate.

This adds partial literal fixture evidence for effect-join, PAUSE and uncertainty,
plus limited epoch separation; it does not discharge their complete formal
obligations. Preserve all six obligations and all 27 traces, highlighting only
13–15 here. Remaining construction: authoritative cut ownership, real issuer
verification, explicit canonical quarantine settlement, arbitrary attempt mapping
and common-writer integration. No language/store/framework selection or M1 edit.

Primary paths inspected at the frozen start: M1A-WIRE-PROFILE.md (effect observation),
M1C-WIRE-PROFILE.md (effects), planning validation/canonical.py and contracts.py,
planning replay/kernel.py, integrity schema.test.py and reference_oracle.py,
F-M1A-014/F-M1A-016 and F-M1C-007. Both independent method challenges confirmed
the missing-evidence, prefix, PAUSE and quarantine limits before construction.
