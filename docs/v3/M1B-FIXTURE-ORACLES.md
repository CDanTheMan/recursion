---
title: M1B closed fixture and oracle blueprint
status: construction-contract
last-updated: 2026-09-04
---

# M1B closed fixture and oracle blueprint

## Fixture carrier

Each committed `F-M1B-NNN.json` is one `M1BFixtureBundle@1` with exactly one typed input and one
typed expected decision. Fixtures are sanitized, self-contained strict JSON. `manifest.json`
binds every filename to its SHA-256 digest. IDs, order and expected results below are closed for
this campaign; a changed oracle requires an appended campaign PlanRevision before implementation.

## Route cases

| ID | Required behavior | Expected status / decisive reason |
|---|---|---|
| `F-M1B-001` | First fully eligible subscription route is selected from explicit priority order | `selected` |
| `F-M1B-002` | Subscription exhaustion cannot fall through to metered without authority and budget | `blocked` / `metered-not-authorized` |
| `F-M1B-003` | Stale descriptor cannot be selected | `blocked` / `descriptor-stale` |
| `F-M1B-004` | Private work cannot use a route lacking private eligibility | `blocked` / `privacy-mismatch` |
| `F-M1B-005` | Unknown billing control is not treated as free or subscription | `blocked` / `billing-unknown` |
| `F-M1B-006` | An unavailable preferred route does not authorize an unlisted substitute | `blocked` / `route-unavailable` |
| `F-M1B-007` | Missing required model/tool capability blocks with complete sorted reasons | `blocked` / `capability-unsupported` |
| `F-M1B-008` | Component-reference mismatch cannot be hidden by a valid route digest | `blocked` / `component-mismatch` |

## Plugin cases

| ID | Required behavior | Expected status / decisive reason |
|---|---|---|
| `F-M1B-009` | Valid acyclic manifest graph resolves in stable dependency order | `resolved` |
| `F-M1B-010` | Missing required plugin dependency fails before import | `blocked` / `dependency-missing` |
| `F-M1B-011` | Complete-graph cycle detection rejects every cycle member | `blocked` / `dependency-cycle` |
| `F-M1B-012` | Explicit conflict or shared exclusive resource without order fails closed | `blocked` / `exclusive-resource-conflict` |
| `F-M1B-013` | Artifact or dependency-lock substitution invalidates the digest-bound grant | `blocked` / `grant-digest-mismatch` |
| `F-M1B-014` | Functional acknowledgement cannot imply network, credential, route, quota or spend grants | `blocked` / `sensitive-grant-missing` |
| `F-M1B-015` | Installed-but-disabled plugin trace contains metadata work only and zero active work | `resolved-disabled` |
| `F-M1B-016` | Reload advances the epoch and rejects an old packet, lease and subscription | `resolved-reload` / `stale-plugin-epoch` for old bindings |

## Process and broker cases

| ID | Required behavior | Expected status / decisive reason |
|---|---|---|
| `F-M1B-017` | Synthetic Windows descriptor satisfying every explicit requirement is eligible | `admitted` |
| `F-M1B-018` | Unknown Job breakaway prevention blocks containment claim | `blocked` / `containment-unknown` |
| `F-M1B-019` | Linux PTY/process-group evidence cannot substitute for required cgroup containment | `blocked` / `containment-unsupported` |
| `F-M1B-020` | Attach/detach trace changes views only and records zero launches/model turns/effects | `accepted` |
| `F-M1B-021` | Stale input or resize lease is refused deterministically | `refused` / `stale-lease` |
| `F-M1B-022` | Exhausted credit disconnects a slow view and requires explicit reset/gap recovery | `accepted-reset` |
| `F-M1B-023` | Fragmented multibyte output advances a UTF-8-byte cursor by encoded bytes, not characters | `accepted` |
| `F-M1B-024` | Immediate PAUSE plus process termination does not assert effect success or rollback | `accepted` / effect conclusion `not-evaluated` |

## Required adversarial mutations

For each union family, tests mutate version, discriminator, unknown field, ID, digest, integer,
enum, ordering, uniqueness and collection bound. Cross-record probes additionally cover duplicate
route priority, unreferenced component, unsupported component claims, empty requirement versus
policy allowlists, unknown capability, metered budget overflow, private egress widening,
self-dependency, hidden graph cycle, missing or ambiguous capability provider, transitive lock
substitution, grant/policy and lifecycle mismatch, trust-as-grant, disabled activity, reload
without fence, platform mismatch, stale or chronologically invalid evidence, exact termination
shape, mixed cursor units, non-monotonic or forward ACK cursor, absent/exhausted cumulative credit,
cumulative queue overflow, stream/client/lease mismatch, conflicting command replay,
output-as-command, passive-client input and attach that increments a launch counter. Lexical
decoder probes include negative zero.

The reference oracle is test-only. A fixture passes only when strict schema validation succeeds,
the independently computed decision equals the literal expected decision byte-for-byte after
canonicalization, and a second clean run produces the same digest.
