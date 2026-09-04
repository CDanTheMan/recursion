---
title: M1C source, effect, publication and persistence requirement contracts
status: frozen-for-local-construction
last-updated: 2026-09-04
---

# M1C source, effect, publication and persistence requirement contracts

## Boundary

M1C freezes inert requirements for five integrity lanes that later runtime components must
satisfy: source/evidence, external effects, publication, canonical-state migration and artifact
retention/deletion. It consumes M1A planning and M1B execution identities only as opaque immutable
bindings. It does not retrieve a source, decide scientific truth, execute or reconcile a real
effect, mutate Git, select or open a database, import operational state, migrate an aggregate,
touch an artifact or key, or perform deletion, backup or restore.

The pure test-only operations are:

```text
assess_evidence(fixture input) -> exact evidence decision
classify_effect_trace(fixture input) -> exact effect decision
assess_publication(fixture input) -> exact publication decision
assess_state_contract(fixture input) -> exact state decision
assess_retention(fixture input) -> exact retention decision
```

They observe no filesystem beyond committed fixtures, network, environment, wall time, random
source, process, plugin, provider, repository remote, database, secret store or production module.
Every output is derived only from the supplied canonical input.

## Source and evidence contract

`SourceRecord@1` separates identity, discovery, retrieval, verification, access, editorial,
license, privacy and expiry state. A canonical URI or persistent identifier is data until its
supplied identity evidence is `verified`; the oracle does not perform resolution. Retrieval and
content digests bind the exact representation. Old, corrected, superseded and retracted records
remain addressable rather than being rewritten.

`ResearchClaim@1` is one scoped, falsifiable proposition represented by a proposition digest. It
classifies the claim as fact, inference, hypothesis, proposal or Owner direction, and separately
classifies its evidence target as external mechanism, local structural fit or empirical fit. An
external paper cannot silently satisfy local or empirical scope.

`EvidenceEdge@1` binds one claim and one source with an exact relation, locator and extraction
digest. Relations are `supports`, `contradicts`, `qualifies`, `replicates`, `updates`, `mentions`,
`metadata-only` or `inapplicable`. Applicability and extraction verification are independent.
Contradictions and qualifications are always retained in the decision.

A source may support an ordinary current claim only when all required identity, retrieval,
content, verification, access, editorial, applicability, privacy, license and freshness evidence
is explicitly eligible. Metadata, snippets, citation count, model narrative, unverifiable
extraction, inapplicable workload, unknown access/license, retraction or expiry never becomes
support. The result is `supported` only for structurally admissible scoped support, `contested`
when admissible support and contradiction coexist, `unknown` when no admissible support remains,
and `refused` for a binding, privacy or export-policy violation. These statuses are evidence-graph
outcomes, not declarations of universal scientific truth.

## Effect and reconciliation contract

`EffectIntent@1` binds the exact GoalSpec, plan, policy, grant, privacy, route, budget, actor,
lease, admission epoch, fence epoch, command, idempotency key, target and payload digest. An
`EffectAdmission@1` is valid only for that identical intent and records a pre-effect decision; it
is not evidence that the external world changed.

An effect trace progresses through explicit observations:

```text
intent -> admitted -> attempt-started -> external observation -> receipt
                               \-> ambiguous -> reconciliation observation -> reconciled
```

No external observation leaves the trace `prepared`; attempt start alone is `executing`.
Authenticated rejection is `failed`. Possible or observed acceptance without an exact matching
authenticated receipt is `ambiguous`, including the crash interval after remote acceptance and
before receipt persistence. A success receipt binds the effect, attempt, idempotency key, target,
payload, observer, result and fence. Contradictory or inexact observations remain ambiguous.

An ambiguous effect cannot be retried or used to admit a dependent effect until an authenticated
reconciliation observation resolves the same external operation. Reconciliation may produce
`reconciled-succeeded` or `reconciled-failed`; it never changes the historical observations.
Compensation is a separate effect with its own authorization, intent, receipt and possible
ambiguity. `reversible` means a compensation protocol exists, not that rollback occurred.

## Publication contract

Publication has a pure preflight and an effect receipt. M1C can make only a review-branch intent
`eligible`; it never authorizes a protected/default merge, deployment or release. Eligibility
requires exact GoalSpec/policy/grant/privacy bindings, source and candidate full Git identities,
known source ancestry, a clean candidate, the exact review ref, all required gates passing on that
candidate, acceptable verifier evidence, and every artifact cleared for the intended audience
after secret/privacy/license/redaction checks.

Publication authority is separate from implementation, verification, merge and deployment.
Missing or downgraded verification is explicit and follows supplied risk policy; it never becomes
full independence. A publisher receipt binds the exact intent, effect, remote, ref and candidate.
An unknown remote observation after a possible push is `ambiguous`, not unpublished and not safe
to retry blindly. A pushed ref is an external fact and cannot be undone by restoring local state.

## Canonical state and migration-readiness contract

M1C is store neutral. A canonical event binds aggregate, sequence, event and command identities,
idempotency, causation, correlation, writer, fence epoch, logical time, schema, previous digest,
payload digest and current digest. Exact duplicate commands return the prior outcome; conflicting
duplicates and stale writers add no event. Hash chaining does not authenticate a writer.

The only fixture boundary admitted in M1C is a synthetic `fabric-only` state contract with
immutable assignment input and no task, run/evidence, accepted-result, remote, Git, publication or
external-effect write. Readiness requires an exact expected/observed writer inventory, one
canonical writer, mechanical refusal of every other writer, one monotonic fence epoch, contiguous
authenticated events, lossless import, exact replay, projection comparison, backup/restore proof,
reverse compatibility reading, rollback admission and no active lease, open or ambiguous effect,
pending publication or partial saga.

Projection equality alone is `projection-only` and cannot prove event order, writer exclusion,
crash behavior or replay. Unknown deployment revision, a new or renamed writer, a torn/digest-gap
history or lossy field blocks. Before any accepted external effect a later runtime may restore a
verified checkpoint and legacy writer only under the proven rollback protocol. After a possibly
accepted effect it must retain the record and reconcile forward.

M1C does not execute the `UNIMPORTED -> ... -> CHECKPOINTED` migration progression. It validates
whether supplied synthetic evidence satisfies the requirements for a named transition. The broad
execution-attempt/lease rehearsal remains blocked until all overlapping writers share an exact
machine-checkable boundary and fence.

## Retention and deletion-proof contract

Raw private artifacts and durable proof are distinct. `RetentionAssessmentInput@1` binds an
artifact class, project/privacy scope, policy, key scope, legal-hold state, every recoverable copy
and a minimal tombstone. Deletion is not a boolean and soft-delete or a provider delete marker is
not physical deletion evidence.

Raw-artifact deletion is `complete` only when local content is gone, its non-shared scoped key is
destroyed, and every recoverable cache, replica, backup and disconnected spool has authenticated
deletion evidence or a reached policy-bound expiry. The tombstone retains policy, class,
responsible component, request/disposition times and non-sensitive copy outcomes, but no content,
secret, raw locator or unnecessary equality-revealing digest.

Pending, disconnected, unknown, soft-deleted or delete-marker-only copies make deletion
`incomplete`. Shared/active keys, contradictory evidence, sensitive tombstones or a legal hold
make it `blocked`. Deleting authority, audit, gate, publication or effect receipts additionally
requires an explicit supplied Owner erasure policy. M1C represents `unknown` policy and blocks;
ordinary Full Access or `grant-admin` never implies erasure authority.

## PAUSE and historical truth

The operative profile remains `current-immediate`. No intent admits when supplied PAUSE state is
paused or its admission epoch is stale. Future checkpoint/interrupt/drain values may be carried as
inert proposed policy data only; they do not alter current effect or publication admission.
Historical sources, contradictions, observations, events and receipts remain immutable even when
superseded, reconciled, compensated, migrated or deleted at the raw-artifact layer.

## Closed outcome ownership

Exact input/output fields, bounds, conditional shapes and closed reason alphabets are owned by
[M1C-WIRE-PROFILE.md](M1C-WIRE-PROFILE.md). The 24 required literal outcomes are owned by
[M1C-FIXTURE-ORACLES.md](M1C-FIXTURE-ORACLES.md). Unknown type, version, state, relation, effect,
publication, writer, copy disposition or reason fails schema validation rather than being ignored.

## Completion boundary

M1C is complete only when the gates in
[M1C-CONSTRUCTION-CAMPAIGN.md](M1C-CONSTRUCTION-CAMPAIGN.md#machine-checkable-gates) pass on one
exact candidate and an independent reviewer records limitations. It proves only deterministic
schema/oracle conformance over synthetic in-memory fixtures. It does not prove source truth,
provider behavior, exactly-once effects, Git safety, database durability, deletion, migration,
performance or production fitness.
