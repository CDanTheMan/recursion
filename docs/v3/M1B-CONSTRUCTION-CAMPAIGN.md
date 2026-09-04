---
title: M1B route, plugin and process contract campaign
status: executing-local-construction
last-updated: 2026-09-04
---

# M1B route, plugin and process contract campaign

## Owner intent and immutable GoalSpec

Owner authorization received 2026-09-04:

> M1A is merged to master. I approve the M1B campaign.

This authorization follows the accepted sequence: freeze M1A, then construct inert M1B route,
plugin and process requirement contracts. It authorizes bounded local documents, schemas,
sanitized fixtures, deterministic test-only oracles, tests and coherent commits. It does not
authorize a provider/model/network call, process launch, plugin import or execution, credential
access, external effect, migration, publication, push, merge, deployment, service/configuration
change, metered spending or constitutional change.

| Field | Frozen value |
|---|---|
| Goal ID | `GOAL-REC-V3-M1B-001` |
| Parent goal | Advance the ratified Recursion-owned Option 2 architecture after the verified M1A planning kernel contract |
| Outcome | Freeze strict, fail-closed route, plugin, process and broker requirement schemas plus 24 literal sanitized oracle cases |
| Starting commit | `aecaefcc2fba3e03ad73571208a13fc6450b1c3a` |
| Required ancestor | M1A terminal receipt `0960481683e2b17ff213a824bbd4b4d559f1c91a` |
| Branch | `codex/v3-m1b-contracts` |
| Worktree | `C:\Users\Lucas\Documents\GitHub\recursion-v3-m1b-contracts` |
| Falsifier | Any gate requires live provider/plugin/process behavior, chooses an open Owner policy, weakens M1A, or cannot represent an unknown/ambiguous observation without treating it as success |
| Terminal condition | Every M1B gate passes twice on one exact clean candidate and an independent exact-candidate review records PASS and limitations |

This GoalSpec serves Recursion's architecture and construction capacity in support of the shipped
work and employable-stack outcomes in `ANCHOR.md`. It does not create a new portfolio project.

## Allowed paths

Only these paths may change:

- `schemas/control-plane/v3/execution/**`
- `scripts/tests/v3/execution/**`
- `docs/v3/**`

Everything else is denied. In particular, M1A production/test bytes, the operative control plane,
state, scripts outside the dedicated test path, configuration, authentication and environment
files are read-only.

## Canonical ownership and resolved source conflict

- [M1B-EXECUTION-CONTRACTS.md](M1B-EXECUTION-CONTRACTS.md) owns M1B semantics and gates.
- [M1B-WIRE-PROFILE.md](M1B-WIRE-PROFILE.md) owns exact JSON fields, unions, bounds and digest omissions.
- [M1B-FIXTURE-ORACLES.md](M1B-FIXTURE-ORACLES.md) owns the closed fixture IDs and expected outcomes.
- [ROUTE-CAPABILITIES.md](ROUTE-CAPABILITIES.md), [PLUGINS-AND-EDITIONS.md](PLUGINS-AND-EDITIONS.md),
  [TERMINAL-RUNTIME.md](TERMINAL-RUNTIME.md), [SECURITY.md](SECURITY.md) and
  [CONSTRUCTION-RUNBOOK.md](CONSTRUCTION-RUNBOOK.md) remain source requirements.
- [CONTROL_PLANE.md](../../CONTROL_PLANE.md) remains operative authority.

An older sentence in [ARCHITECTURE-PROOF.md](ARCHITECTURE-PROOF.md) assigned scientific contracts
to M1B. The later milestone definitions in `ROADMAP.md`, `M1A-AUTONOMOUS-PLANNING.md` and
`CONSTRUCTION-RUNBOOK.md`, plus the Owner's current approval of the recommended sequence, assign
scientific/source/effect/persistence contracts to M1C. M1B therefore excludes them. The stale
sentence will be corrected as documentation reconciliation, not silently followed.

## Privacy, egress, route and spending boundary

All fixtures use synthetic identifiers and digests. M1B reads only repository files, imports no
plugin implementation, enumerates no account or credential store, performs no network or process
operation and spends no provider quota. Credential fields are opaque references only. Route
availability, billing, privacy and platform support use explicit supported/unsupported/unknown or
fresh/stale states; missing evidence never becomes zero, free, safe or available.

## PlanRevision 1

`PLAN-M1B-001@1` is the initial immutable construction plan.

| Task | Depends on | Output | Gate |
|---|---|---|---|
| M1B-01 | Owner approval and merged M1A | campaign, semantics, wire profile and closed oracle | canonical owners agree; open policy seams remain explicit |
| M1B-02 | M1B-01 | strict Draft 2020-12 execution schema | every record/union closes; materialization is byte-identical |
| M1B-03 | M1B-02 | 24 literal fixture bundles and digest manifest | exact IDs/digests; every bundle structurally valid |
| M1B-04 | M1B-03 | deterministic test-only route/plugin/process/broker oracle | expected outcomes reproduced twice without I/O or ambient state |
| M1B-05 | M1B-04 | adversarial, static and M1A/v2 compatibility closure | fail-closed negatives and unchanged regressions pass |
| M1B-06 | M1B-05 | exact-candidate independent adjudication and terminal receipt | PASS or smallest inspectable dissent |

No production resolver, loader, broker or process adapter is an output of this DAG.

## Machine-checkable gates

1. The schema and fixture materializers reproduce committed bytes exactly.
2. Strict JSON rejects duplicate keys, invalid UTF-8, floats/constants, excessive depth and unknown fields.
3. Every object is closed and every version, union arm, enum, ID, digest, integer and collection bound fails closed.
4. Route records keep engine, provider, model, pool, account reference, host and sandbox separate.
5. Route selection considers only explicitly ranked candidates that remain eligible inside current capability, privacy, egress, billing and policy bounds; it never substitutes or enables metered use.
6. Unknown, stale, unavailable, ambiguous-component and missing-evidence route cases block with complete ordered reasons.
7. Plugin resolution occurs from manifest metadata before code import and rejects missing dependencies, cycles, conflicts, substitution and unknown protocol/capability arms.
8. Effective plugin authority is the intersection of manifest declaration, GoalSpec/policy, route, privacy, budget and separate Owner grant dimensions; every deny is retained.
9. Disabled-plugin traces contain zero implementation imports, processes, threads, timers, watchers, network, credential reads, quota/spend activity, context injection, tools and subscriptions.
10. Reload/revocation advances an epoch, fences old packets/leases/subscriptions and preserves old evidence; digest rotation never reuses an old grant.
11. Process requirements separate requested transport/containment from observed support; unknown or missing containment blocks, and termination never proves an external effect succeeded or rolled back.
12. Broker traces enforce daemon epoch, monotonic byte/event cursors, bounded credit, one fenced input/resize lease, replay or explicit `RESET+GAP`, and attach/detach without launching work.
13. Current `current-immediate` PAUSE remains the only operative profile; future profiles are representable but inert.
14. All 24 literal cases pass twice; static scans show no network/provider/plugin/process/database/Git/effect/clock/random/environment dependency; M1A and v2 regressions pass unchanged; path, diff, link and secret scans pass; exact-candidate independent review passes.

## Construction decisions and open Owner seams

`CD-M1B-001`: schemas live under the semantic `execution` area, not a milestone-number package.
The contract can remain stable when M1B becomes historical.

`CD-M1B-002`: M1B accepts an already policy-ranked route candidate order and validates eligibility;
it does not choose a production scoring model or weights. A later router may optimize only inside
the eligible set.

`CD-M1B-003`: plugin functional verbs and workspace scope may share one digest-specific local
acknowledgement, matching the ratified novice-path floor. Credential, network, model launch,
route/account, quota, spend, update, downgrade and grant-administration dimensions remain separate
nullable grant references. M1B does not decide which may later share an Owner acknowledgement.

`CD-M1B-004`: process capability is evidence, not platform reputation. Every containment feature
is tri-state and source-bound. A requested required feature must be `supported`; `unknown` blocks.

`CD-M1B-005`: the broker wire is a requirements profile, not a stable runtime ABI. Cursors declare
`utf8-byte` or `event` units explicitly; a view cannot create a process, actor, model turn or effect.

## PlanRevision 2 — reachable billing refusal and scalar strictness

`PLAN-M1B-001@2` was triggered during M1B-04 self-review of the frozen schema/fixture lineage at
`bdccb786aa43dba49fdfabe92ddc624667503317`. The closed route alphabet included
`metered-budget-exceeded`, but the input carried ceilings without an explicit task estimate. That
made the refusal unreachable without inventing a cost. The review also found that the exact UTC
and decoded-base64 requirements relied on lexical patterns alone.

- Retained: Owner intent, GoalSpec, boundaries, all 24 fixture purposes/outcomes and the M1B DAG.
- Superseded: the first `RouteRequirement@1` shape and the schema/fixture digests derived from it.
- Re-admitted: M1B-02/M1B-03 repair, then M1B-04.
- Change: add nullable `estimated_metered_microunits`; unknown blocks as `billing-unknown` and an
  estimate above any pool/requirement/policy ceiling blocks as `metered-budget-exceeded`.
- Change: validate calendar-correct canonical UTC timestamps and canonical base64 with a 65,536
  decoded-byte ceiling.
- Falsifier: any metered decision still needs an inferred amount, an invalid calendar timestamp or
  non-canonical/oversized payload reaches the oracle, or a fixture purpose/outcome changes.

Still reserved for Lucas or a later measured campaign: production route scoring; numeric resource
defaults; provider/terminal support matrix; which sensitive plugin grants share consent; signing,
sandbox, renderer and process-library selections; constitutional amendment; migration; and any
live or external effect.

## PlanRevision 3 — independent fail-closed repair

`PLAN-M1B-001@3` was triggered by the TERRA-M1B-01 exact-candidate review of
`5171473c875b84cbe7c67e10da9e9799eba6a332` and a concurrent lead audit. Although every supplied
gate passed twice, the verifier reproduced four schema-valid false greens: lexical negative zero,
empty requirement egress, grant/policy context mismatch and non-cumulative or absent broker
credit. The lead audit found adjacent missing component, lifecycle, process-result and broker
binding checks. The candidate is rejected; its passing receipt is not terminal evidence.

- Retained: Owner intent, GoalSpec, allowed paths, no-runtime boundary, DAG, all 24 fixture IDs,
  purposes and expected outcome classes.
- Re-admitted: M1B-02 through M1B-06 on a repaired exact candidate.
- Change: reject lexical `-0`; apply the documented no-additional-restriction meaning only to
  requirement allowlists while policy authority sets remain fail-closed.
- Change: require route capability component backing, plugin grant/policy and lifecycle bindings,
  one dependency provider per required capability, and exact process result/termination shapes.
- Change: broker traces bind one stream/client and current leases, consume explicit credit and
  queue capacity cumulatively, reject forward ACKs and conflicting idempotency keys, and recover
  exhaustion only through explicit RESET.
- Gate extension: add independent adversarial probes for every reproduced falsifier and adjacent
  binding rule; regenerate all schema/fixture digests; repeat every compatibility and hygiene gate;
  obtain a new exact-candidate independent verdict.
- Falsifier: any reproduced TERRA counterexample remains accepted, any repaired rule changes a
  fixture's intended outcome class, or the repair introduces runtime I/O or an Owner policy choice.

## PlanRevision 4 — SOL semantic closure

`PLAN-M1B-001@4` was triggered by two independent SOL reviews of
`a074dd723da38b804e509b6c92404108570e0a22`. Both confirmed the four PlanRevision 3 repairs and
rejected the candidate for generalized schema-valid false greens. Material findings covered
unknown/contradictory pool and sandbox state; manifest authority beyond declared capability;
reload dependency bypass; stale lifecycle sub-epochs; cycle-dependent propagation; termination
identity; zero-cursor unit changes; replay-gap and RESET rollback; and route-decision output
invariants. One review also showed that the required mutation matrix had only been sampled on the
route union.

- Retained: all prior Owner intent, boundaries, tasks, fixture IDs, purposes and expected outcome
  classes. This remains an inert schema/oracle campaign with no production runtime.
- Re-admitted: M1B-02 through M1B-06 on one new exact candidate. Prior passing sweeps and both SOL
  dissent receipts are diagnostic evidence only.
- Change: unknown billing and known-zero available capacity block; sandbox mode must back its
  claimed egress/capability state; route result validation binds status and first eligible route.
- Change: effective plugin functionality is bounded by the manifest declaration; lifecycle and
  all binding epochs agree; cycle rejection propagates to noncycle dependents; dependency order
  may serialize exclusive ownership; self-contained reload refuses unresolved dependencies.
- Change: termination observations bind the exact requirement; broker cursor units bind even at
  zero, WELCOME ranges cannot regress, replay gaps require RESET, RESET cannot roll back or appear
  without a gap/exhaustion condition, and new output after RESET requires fresh credit.
- Gate extension: every fixture union family receives unknown-field, discriminator/version, ID,
  digest, integer, ordering, uniqueness and collection-bound mutations (48 matrix cases), plus the
  exact SOL falsifiers.
- Falsifier: any SOL counterexample remains accepted, route/plugin/process/broker output can claim
  a mismatched identity or authority, or a RESET/ordering rule permits ambiguous continuation.

## PlanRevision 5 — replay-gap ordering fence

`PLAN-M1B-001@5` was triggered by the holistic SOL review of exact candidate
`4ae893e4588ea8c41e0b24a894fe046539d7b4b8`. The second SOL reviewer passed its six focused
falsifiers, but the holistic reviewer produced one remaining schema-valid false green:
WELCOME established a replay gap, CREDIT and EVENT continued the stream, and a later RESET masked
that invalid continuation as `accepted-reset`.

- Retained: every PlanRevision 4 repair, fixture outcome class, boundary and gate.
- Re-admitted: M1B-04 through M1B-06 on one new exact candidate. The split SOL verdict on
  `4ae893e4588ea8c41e0b24a894fe046539d7b4b8` is diagnostic evidence only.
- Change: once WELCOME establishes an unrecovered replay gap, RESET is the only permitted next
  coherent-stream message. Any other continuation records permanent `replay-gap-continuation`
  refusal; a later valid RESET may advance recovery state but cannot erase that violation.
- Gate extension: reproduce WELCOME gap, CREDIT, EVENT, RESET exactly and require a refused trace
  carrying `replay-gap-continuation`.
- Falsifier: any non-RESET message is processed while a replay gap is pending, or a later RESET
  turns such a trace into `accepted-reset`.

## Stop conditions

Stop and append a PlanRevision if a canonical rule conflicts, an oracle must be weakened, a test
requires external state, an open Owner decision must be chosen, M1A bytes must change, a required
verifier is unavailable, or any changed path leaves the allowlist. No dissent is resolved by
majority vote or hidden reasoning.
