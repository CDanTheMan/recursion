---
title: Recursion v3 constitutional amendment application packet
status: owner-authorized-proposal-not-operative
last-updated: 2026-09-03
authority: OR-018 OR-019 OR-020
---

# Constitutional amendment application packet

Lucas ratified the direction in `OR-018`–`OR-020`. This file is the exact docs-only proposal for a
later authorized control-plane application. It does **not** amend `CONTROL_PLANE.md`,
`state/DECISIONS.md`, configuration, deployment or the current PAUSE behavior. Until an exact
candidate is applied and recorded, Hermes remains the live executive named by the current
constitution and PAUSE means immediate halt.

## Amendment scope

Replace only the constitutional clauses governing:

1. canonical executive/harness ownership and external dependencies;
2. the future PAUSE family and its effect-state behavior; and
3. verifier assurance classes, downgrade receipts and terminal labels.

No clause here grants spending, credentials, deployment, publication, merge, audit erasure,
unbounded self-grant or runtime construction authority. Lucas remains final authority.

## Proposed normative clauses

### `CA-V3-001` — Recursion-owned control plane

The versioned Recursion release is the sole canonical harness and control-plane dependency. The
canonical logical `Head` is owned by Recursion and is accountable to Lucas. Head owns admitted
Owner goals, ARM lifecycle, cross-goal/ARM conflicts and escalation. Each admitted ARM exclusively
owns semantic proposals for its bounded plan and task DAG. Workers execute immutable WorkPackets.
Verifiers judge evidence. Only the deterministic Recursion kernel admits authoritative
transitions, writes canonical events, enforces authority/privacy/budget/PAUSE/fences/effects and
admits publication.

External models, providers, CLIs, Hermes, terminals, plugins, databases, storage engines and
frontends are optional typed adapters or libraries. They may propose commands or observations but
cannot own, amend or reconstruct canonical identity, GoalSpec, plan, grant, budget, PAUSE, lease,
effect, evidence, verification or publication state. The kernel must boot, replay, reconcile and
provide owner-readable status with every optional adapter absent. Ordinary pinned libraries are
permitted only inside the Recursion release's artifact, lock, provenance, license and SBOM
boundary. “Sole dependency” does not mean zero third-party libraries.

Logical actor identity is stable across admitted route/model/provider/engine replacement. The new
route receives no authority from the old provider session; the kernel rebinds it to the same actor,
GoalSpec, plan, policy, privacy, budget and lease epoch. Unknown or incompatible adapters are
read-only, quarantined or refused.

### `CA-V3-002` — amendment and fencing

Only authenticated Lucas may accept or amend the parent GoalSpec or this constitution. A child,
worker, verifier, plugin, route, external harness, stale executive lease or model output cannot do
so. Restrictions to egress, paths, capabilities, spending, deadlines or PAUSE may tighten
immediately. Widening or semantic replacement requires a new authorization and safe checkpoint;
credential, spending, publication, deployment, merge and grant-administration changes require
their separately authorized capability.

Every accepted GoalSpec, constitution, plan, route-policy or PAUSE amendment advances the relevant
policy/goal/fencing epoch. The kernel deterministically classifies active plans, tasks, packets,
leases, effects and evidence as retained, invalidated, quarantined or superseded. Exact digest and
policy compatibility is required for retention. Old packets and leases never regain authority by
replay or adapter reconnect. Dispatched or ambiguous external effects are reconciled, never erased
or relabeled as rolled back.

### `CA-V3-003` — future PAUSE object

The future `PauseDirective` binds:

```text
pause_id, aggregate_scope, mode, reason, issued_by, authority_receipt,
constitution_digest, goal/policy digests, new_pause_epoch, issued_logical_time,
checkpoint_deadline, process_disposition, notification_policy, command_digest
```

Modes are:

- `checkpoint` — the default. Immediately refuse new goals/plans/tasks/packets, model/tool calls,
  route activation, effect preparation/dispatch and publication. An already-running pure local
  segment may finish only to its declared, kernel-recognized checkpoint before the deadline. An
  already-issued model response may be received and stored as untrusted staged evidence, but may
  not cause another model/tool/effect transition. No new external effect is dispatched.
- `interrupt` — apply checkpoint prohibitions, revoke execution leases and request cooperative
  cancellation/termination. On deadline, perform the packet's preauthorized containment action.
  Unknown termination or effect state is `ambiguous`, never success.
- `drain` — refuse all new admission and dispatch; already-running pure work and observation of an
  already-dispatched effect may reach their declared terminal/reconciliation boundary. Drain does
  not authorize a new effect merely because it was planned.
- `emergency` — immediately revoke execution/input/effect leases and attempt the preauthorized
  containment stop without waiting for a checkpoint. Canonical awareness, replay, status and
  evidence capture remain available. Anything not proven stopped is quarantined/ambiguous.

Resume requires authenticated Lucas authority, a new PAUSE epoch, reconciliation of every
ambiguous process/effect, fresh leases and newly derived packets. Clearing the file/flag or
reconnecting an adapter is never sufficient.

### `CA-V3-004` — PAUSE operation matrix

| Operation at directive admission | `checkpoint` | `interrupt` | `drain` | `emergency` |
|---|---|---|---|---|
| owner status and canonical replay | continue read-only | same | same | same |
| typed awareness evidence for an already-admitted operation | append only a bounded observation/late-result/cancellation/receipt record as staged, stale, quarantined or reconciled; it cannot admit a goal, plan, packet, route, plugin, follow-up or effect | same | same | same |
| new GoalSpec/plan/task/packet/route/plugin admission | refuse | refuse | refuse | refuse |
| queued but not running packet | cancel/fence | cancel/fence | cancel/fence | cancel/fence |
| active pure deterministic kernel reduction | finish current atomic append, then stop | finish atomic append only | finish current admitted reduction | finish atomic append only |
| active model/provider request | receive/stage response until deadline; no follow-up | request cancel; stage any late response | receive/stage; no follow-up | request cancel immediately; late response stale |
| active pure worker segment | reach declared checkpoint until deadline | cancel then containment deadline | reach terminal/checkpoint | contain immediately |
| terminal process | input lease revoked; reach declared process checkpoint or typed stop at deadline | cooperative then forced packet policy | no new input/effect; observe to declared boundary | containment stop now |
| prepared, not dispatched effect | cancel/fence | cancel/fence | cancel/fence | cancel/fence |
| dispatched effect without receipt | observe/reconcile only; `ambiguous` if unknown | same plus cancellation request when safe | observe/reconcile only | contain when possible; otherwise `ambiguous` |
| completed effect with durable receipt | retain fact; run no follow-on | same | same | same |
| verifier already judging immutable evidence | may finish and record, but cannot publish | cancel or finish atomic decision per packet | may finish | stop after atomic append |
| publication/merge/deploy/notification effect | refuse unless it was already dispatched; reconcile reality | refuse/reconcile | refuse/reconcile | refuse/reconcile |

The future matrix is fail closed. A packet may declare a narrower disposition. An adapter may not
declare a wider one. Failure to reach a deadline deterministically escalates from `checkpoint` or
`drain` to the recorded interrupt/containment action; it does not silently continue.

### `CA-V3-005` — verifier assurance classes

Independence is a vector, not a model label:

```text
actor, workspace/state, evidence acquisition, implementation authorship,
model family, provider, account/capacity pool, host/failure domain, evaluator/oracle
```

Same-family Sol/Luna/Terra review is useful separation of actor/context but is never reported as
cross-family independence.

| Class | Work type | Minimum assurance | Downgrade rule |
|---|---|---|---|
| `V0-mechanical` | schemas, links, formatting, deterministic docs/fixtures | deterministic gate plus a separately identified verifier or reproducible exact rerun | policy may accept deterministic-only evidence; label the absent dimensions |
| `V1-routine-reversible` | bounded local, reversible, no sensitive authority/effect | separate verifier actor/context, clean candidate, exact gate rerun and dissent | a policy-listed same-family/provider/host downgrade is allowed only with a bound receipt and yields downgraded status |
| `V2-sensitive` | security, privacy, authority, migration, process containment, plugins or ambiguous effects | V1 plus an independent failure domain: different model family/provider, deterministic specialist/oracle or human review, and adversarial fault gate | blocked unless Lucas signs an exact exception; never full independence |
| `V3-constitutional-release` | constitution, public release/publication, deployment, credentials/spend/grants, irreversible/high-impact effect | deterministic gates, separate verifier, required independent failure domain and authenticated Lucas approval | no autonomous downgrade; only an exact single-use Lucas exception may yield `terminal-verified-downgraded` |

Missing verifier is `blocked/missing`. Failed verifier is `fail`. A risk-approved exception can
produce `downgraded-pass` only for its exact candidate and terminal projection
`terminal-verified-downgraded`; neither may be displayed, queried or published as `pass`, full
verification or cross-family review.

### `CA-V3-006` — verifier downgrade receipt

`VerifierDowngradeReceipt` is single-use and binds:

```text
receipt_id, authenticated_owner, authority_receipt, risk_class, exact candidate/release digest,
GoalSpec digest, PlanRevision digest, verifier-policy version/digest,
operative constitution digest, required independence vector, observed vector,
explicit missing dimensions, reason, evidence and fault-gate digests,
allowed terminal label, issued logical time, expiry logical time, consumed command/event IDs
```

Unknown fields/versions, missing/mismatched bindings, expiry, reuse or a requested label stronger
than `terminal-verified-downgraded` fail closed. A verifier cannot issue its own exception, change
the risk class or rewrite the plan. A plugin or external harness cannot supply canonical verifier
identity.

## Current-to-future conflict and migration map

| Current operative clause | Proposed future clause | Safe transition |
|---|---|---|
| Hermes is the named executive control plane | Recursion-owned logical Head; Hermes optional adapter | Freeze admission; import identity/state through a read-only compatibility adapter; compare replay digests; establish one Recursion writer; fence Hermes; retain legacy read-only until removal gates pass. |
| PAUSE means immediate halt | `checkpoint` default plus explicit `interrupt`, `drain`, `emergency` | Keep current behavior through migration. Install schema/fixtures first; require process/effect fault tests; activate only by an authenticated versioned constitutional event. |
| verification policy does not define complete risk classes | `V0`–`V3` plus exact downgrade receipt | Classify current gates conservatively; missing class maps to the stricter applicable class; never upgrade historical evidence by relabeling. |
| external runtime/session can appear to carry actor continuity | kernel event state owns identity; route is replaceable | Bind old sessions as optional affinity references; restart from canonical capsule/epoch; reject unprovable mappings. |

## Application gates

This proposal may be applied to the live control plane only when a separately authorized
control-plane task supplies all of the following:

1. exact before/after diff limited to authorized constitutional and decision-record paths;
2. authenticated Lucas approval for that exact digest;
3. deterministic schema/fixture results for every PAUSE row and `V0`–`V3` outcome;
4. formal-model counterexamples for removed fence/PAUSE/verifier guards;
5. a frozen legacy-state import and one-writer/fence rehearsal with rollback before effects;
6. native Windows/Linux process/effect ambiguity tests for the supported release surface;
7. independent `V3` review or an exact Lucas downgrade exception visibly labeled;
8. clean release identity, provenance, SBOM, rollback instructions and owner-readable diff;
9. no active ambiguous external effect; and
10. a post-application boot/replay/status check with every optional harness absent.

Failure before the first external effect restores the previous verified constitution and writer
epoch. After any real or ambiguous external effect, rollback is forbidden as a claim of erasure;
the system reconciles forward and preserves both amendment/effect histories.

## Decisions deliberately not made here

This amendment does not choose a language, storage engine, renderer, plugin runtime, native model
loop, numeric resource ceiling, audit-erasure power, unsigned-plugin grant bundle or public canary.
Those remain separate owner or experiment decisions. Applying this proposal is also a separate
Lucas decision because this campaign is docs-only.
