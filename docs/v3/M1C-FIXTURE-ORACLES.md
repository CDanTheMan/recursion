---
title: M1C closed integrity fixture and oracle blueprint
status: frozen-for-local-construction
last-updated: 2026-09-04
---

# M1C closed integrity fixture and oracle blueprint

## Literal corpus rule

Each committed `F-M1C-NNN.json` is one closed fixture bundle with a typed input and a literal
expected decision. Expected bytes are materialized directly from this frozen table and explicit
fixture constructors before the reference oracle is admitted. The materializer must not import,
call or copy output from the oracle. Conformance later compares the independent oracle result to
the committed literal expected bytes twice.

Every identifier, digest, URI, repository, branch, artifact, writer, copy and observation is
synthetic. No fixture names a real private project, credential, remote, source access token,
artifact location, deployment or operational store.

## Evidence fixtures

| ID | Purpose | Literal outcome |
|---|---|---|
| `F-M1C-001` | One current verified primary source with exact applicable extraction supplies structurally admissible scoped support | `supported` |
| `F-M1C-002` | Metadata-only discovery cannot support a claim | `unknown` / `support-insufficient`, `metadata-only` |
| `F-M1C-003` | A retracted source cannot be admitted as current support | `unknown` / `source-retracted`, `support-insufficient` |
| `F-M1C-004` | Applicable verified support and contradiction remain visible together | `contested` with the contradiction edge retained |
| `F-M1C-005` | Private or license-restricted material cannot enter a public export outside supplied policy | `refused` / `export-prohibited` |

The oracle never resolves identifiers or judges truth. It evaluates only supplied typed evidence
and must return all rejected sources, accepted edges and contradiction/qualification edges in
stable sorted order.

## Effect fixtures

| ID | Purpose | Literal outcome |
|---|---|---|
| `F-M1C-006` | Exact admitted intent with no attempt remains prepared and produces zero effects | `prepared` |
| `F-M1C-007` | Matching authenticated acceptance and persisted receipt complete one effect | `succeeded` |
| `F-M1C-008` | Possible external acceptance without the matching receipt is not success | `ambiguous` / `receipt-missing` |
| `F-M1C-009` | A second attempt while the first outcome is ambiguous is fenced | `ambiguous` / `blind-retry-blocked` |
| `F-M1C-010` | Stale admission/fence or current immediate PAUSE refuses before attempt | `refused` / `stale-admission` and/or `paused` |

Every trace reports `effect_count=0` and `external_call_count=0`; these fixtures classify records
and never actuate. A reconciliation observation may resolve ambiguity only when every effect,
attempt, idempotency, target, payload, observer and authentication binding agrees.

## Publication fixtures

| ID | Purpose | Literal outcome |
|---|---|---|
| `F-M1C-011` | Clean exact candidate, known ancestry, review ref, export-safe artifacts, passing gates and acceptable verifier are eligible | `eligible` |
| `F-M1C-012` | A default/protected target or merge/deployment intent is never review-publication eligible | `blocked` / `protected-target` or `publication-kind-prohibited` |
| `F-M1C-013` | Private, unredacted or secret-bearing artifact blocks public publication | `blocked` / `artifact-export-prohibited` |
| `F-M1C-014` | Missing, stale, mismatched or policy-insufficient verification cannot become a pass | `blocked` / `verification-insufficient` |
| `F-M1C-015` | Possible push with unknown remote observation is not safe to repeat or call unpublished | `ambiguous` / `remote-state-unknown` |

The eligible fixture has no receipt and performs no push. A published receipt, when tested
adversarially, must bind the exact repository, review ref and candidate. Local rollback cannot
erase an accepted remote ref.

## Fabric-only state fixtures

| ID | Purpose | Literal outcome |
|---|---|---|
| `F-M1C-016` | Complete synthetic fabric-only inventory, one fenced writer, exact replay and recovery evidence satisfy the state-contract requirements | `eligible` |
| `F-M1C-017` | Missing, unknown, new or renamed writer prevents a complete fence | `blocked` / `writer-inventory-incomplete` |
| `F-M1C-018` | Sequence/digest discontinuity or replay mismatch requires recovery rather than projection trust | `recovery-required` / `replay-mismatch` |
| `F-M1C-019` | Active lease, open/ambiguous effect, pending publication or partial saga blocks ownership transfer | `blocked` / complete open-work reasons |
| `F-M1C-020` | Matching projection without backup/restore/reverse-reader/rollback evidence is not migration proof | `blocked` / `projection-only` plus missing-proof reasons |

All state is synthetic. The admitted aggregate type is exactly `fabric-only`; task, run/evidence,
accepted-result, remote, Git, publication and external-effect writers are excluded. No fixture is
described as the OR-015 broad rehearsal, a cutover or live deployment evidence.

## Retention fixtures

| ID | Purpose | Literal outcome |
|---|---|---|
| `F-M1C-021` | Scoped key destroyed and every recoverable raw copy deleted or past an evidenced expiry with a minimal tombstone completes deletion proof | `complete` |
| `F-M1C-022` | Disconnected, soft-deleted, delete-marker-only, unknown or propagation-pending copies remain incomplete | `incomplete` / `copy-unresolved` |
| `F-M1C-023` | Shared/active key or equality-revealing/content-bearing tombstone invalidates completion | `blocked` / `key-not-isolated` and/or `tombstone-sensitive` |
| `F-M1C-024` | Erasing an authority/effect/audit receipt with unresolved Owner erasure policy is prohibited | `blocked` / `owner-policy-required` |

No fixture deletes content or a key. Expiry is an explicit supplied reached boundary, never a wall
clock comparison; when a tombstone records disposal, that instant must not predate the boundary.
The sealed tombstone binds the exact artifact ID, class and policy. `complete` means the supplied
proof graph is complete, not that M1C inspected a provider, medium, backup or disconnected node.

## Mutation matrix and completion

Every fixture-union family receives at least: unknown field; combined discriminator/version;
fixture ID; digest; exact integer; ordering; uniqueness; and collection-bound mutation. Lane
specific adversarial probes cover identity cross-binding, contradiction retention, inapplicable
support, stale source, effect receipt/attempt/idempotency mismatches, ambiguity retry,
source/candidate/ref/verifier publication mismatches, writer/fence/event chain discontinuity,
projection-only claims, incomplete copy inventories, shared keys and sensitive tombstones.

The corpus is complete only when all 24 bundles validate, their manifest binds exact bytes, the
independent oracle reproduces literal expected bytes twice, every negative mutation fails closed,
and static checks prove construction has no runtime adapter or external dependency.
