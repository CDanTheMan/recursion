---
title: M1B exact JSON wire profile
status: construction-contract
last-updated: 2026-09-04
---

# M1B exact JSON wire profile

## Encoding and common rules

M1B uses UTF-8 I-JSON objects validated with JSON Schema Draft 2020-12. Duplicate keys,
non-shortest or invalid UTF-8, byte-order marks, floats, negative zero, `NaN`, infinities and
non-JSON constants are rejected before schema validation. Maximum decode depth is 64 and maximum
canonical object size is 262,144 UTF-8 bytes.

Canonicalization is RFC 8785. Digests are lowercase `sha256:` plus 64 hexadecimal characters.
Every object has exactly the named fields; unknown fields fail. Missing and `null` differ. A field
is nullable only where this profile says so. Arrays marked set are strictly ascending by the
canonical scalar/key and contain no duplicates. Other arrays preserve semantic order.

| Alias | Exact representation |
|---|---|
| `Id` | string, 1–96 UTF-8 bytes, `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$` |
| `Capability` | string, 1–96 UTF-8 bytes, same pattern as `Id` |
| `Digest` | string, `^sha256:[0-9a-f]{64}$` |
| `OpaqueRef` | string, 1–160 UTF-8 bytes, `^[A-Za-z0-9][A-Za-z0-9._:/-]*$` |
| `Timestamp` | UTC string `YYYY-MM-DDTHH:MM:SSZ`; evidence only, never ambient time |
| `Count` | integer 0–2,147,483,647; booleans are not integers |
| `PositiveCount` | integer 1–2,147,483,647; booleans are not integers |
| `Microunits` | integer 0–9,007,199,254,740,991; booleans are not integers |
| `TriState` | `supported`, `unsupported` or `unknown` |
| `PrivacyClass` | `public`, `internal`, `private` or `restricted` |
| `BillingBasis` | `subscription`, `metered`, `local` or `unknown` |

All scalar-set arrays contain at most 128 entries. Catalog/manifest/message arrays contain at most
256 entries unless stated otherwise. Human explanation strings are 1–512 UTF-8 bytes. Raw test
payloads are base64 strings of at most 65,536 decoded bytes.

## Evidence and route records

`EvidenceBinding@1` has `source_ids` (nonempty sorted `Id` set), `observed_at`, nullable
`expires_at`, and `evidence_digest`. Dates establish provenance only; the explicit eligibility
state is the fixture input. When present, expiry must be strictly later than observation; neither
field authorizes consulting an ambient clock.

`RouteComponentCatalog@1` has the following arrays, each strictly ordered by `id`:

| Array/object | Exact fields |
|---|---|
| `engines[]` | `id`, nonempty sorted `protocol_versions`, nonempty sorted `capabilities` |
| `providers[]` | `id`, nonempty sorted `endpoint_ids`, nonempty sorted `privacy_classes` |
| `models[]` | `id`, `provider_id`, nonempty sorted `capabilities`, sorted `reasoning_modes` |
| `pools[]` | `id`, `billing_basis`, nullable `account_ref`, sorted `model_ids`, `state` (`available`,`exhausted`,`unknown`,`disabled`), nullable `remaining_units`, nullable `metered_limit_microunits` |
| `hosts[]` | `id`, `platform` (`windows`,`linux`,`macos`,`unknown`), nonempty sorted `capabilities` |
| `sandboxes[]` | `id`, `filesystem_mode` (`none`,`read-only`,`workspace-write`,`full`), `network_mode` (`denied`,`allowlist`,`full`), `process_mode` (`denied`,`isolated`,`full`), sorted `allowed_paths`, sorted `allowed_destinations`, sorted `capabilities` |

For a pool, `remaining_units` is non-null only when state is `available` or `exhausted`;
`metered_limit_microunits` is non-null only for `metered`; `account_ref` may be null only for
`local` or `unknown`. These are structure rules, not live entitlement claims.

`CapabilityState@1` has `name` and `state`; arrays are ordered by `name`.

`RouteCapabilityDescriptor@1` has `type`, `id`, the seven component references `engine_id`,
`provider_id`, `model_id`, `pool_id`, nullable `account_ref`, `host_id`, `sandbox_id`,
`eligibility_state`, ordered `capabilities`, sorted `privacy_classes`, sorted
`egress_destinations`, `billing_control`, `evidence`, and `descriptor_digest`.

- `type` is `RouteCapabilityDescriptor@1`.
- `eligibility_state` is `verified-current`, `documented`, `observed-uncertain`, `stale` or
  `unavailable`.
- `billing_control` is `verified`, `unverified` or `unknown`.
- `descriptor_digest` is computed over the whole object with only `descriptor_digest` omitted.

`RouteRequirement@1` has `type`, `id`, sorted nonempty `required_capabilities`, `privacy_class`,
sorted nonempty `allowed_billing`, sorted `allowed_route_ids`, sorted `allowed_host_ids`, sorted
`allowed_egress_destinations`, nullable `estimated_metered_microunits`, nullable
`max_metered_microunits`, and sorted
`required_sandbox_capabilities`. Empty allowed route/host/egress sets mean no additional allowlist,
not permission to widen another bound.

`estimated_metered_microunits` is the explicit task estimate used for admission. A metered
candidate blocks with `billing-unknown` when it is null and with `metered-budget-exceeded` when it
exceeds the pool, requirement or policy ceiling. It is evidence for admission, not a price claim.

`RoutePolicyEnvelope@1` has `type`, `id`, `goal_spec_digest`, `authority_digest`, `policy_digest`,
sorted `permitted_route_ids`, `permitted_host_ids`, `permitted_account_refs`,
`permitted_egress_destinations`, `metered_authorized`, nullable `max_metered_microunits`, and
`pause_epoch`. The metered maximum is non-null exactly when metered authorization is true.
Policy `permitted_*` sets are authority bounds: an empty route or host set permits no route, an
empty account set permits no non-null account reference, and an empty egress set permits only a
route with no egress destinations. They never inherit the requirement's empty-set convention.

`RouteResolutionInput@1` has `type`, `catalog`, nonempty descriptor array ordered by descriptor
`id`, `requirement`, `policy`, and nonempty ordered unique `ranked_route_ids`. Every ranked ID must
name one descriptor; unranked descriptors are not substitutes.

`RouteCandidateEvaluation@1` has `route_id`, `eligible`, and sorted unique `reasons`. Reasons use
the closed route alphabet below. `RouteResolutionDecision@1` has `type`, `status`
(`selected` or `blocked`), nullable `selected_route_id`, and `candidate_evaluations` in exact
ranked order. Selected requires exactly one selected ID and its evaluation eligible; blocked
requires null and no eligible evaluation.

A required route capability must be explicitly `supported` by the route descriptor and present
in both its referenced engine and model descriptors. A route declaration cannot synthesize
component support.

Closed route reasons:

`account-mismatch`, `billing-basis-denied`, `billing-unknown`, `capability-unknown`,
`capability-unsupported`, `component-mismatch`, `descriptor-not-current`, `descriptor-stale`,
`egress-denied`, `host-denied`, `metered-budget-exceeded`, `metered-not-authorized`,
`pool-disabled`, `pool-exhausted`, `pool-unknown`, `privacy-mismatch`, `route-denied`,
`route-unavailable`, `sandbox-capability-missing`.

## Plugin records

`PluginDependency@1` has `plugin_id`, `artifact_digest` and `dependency_lock_digest`; dependencies
are ordered by `plugin_id`.

`PluginGrantDimensions@1` has sorted sets `functional_capabilities`, `workspace_paths`,
`network_destinations`, `credential_refs`, `model_refs`, `route_account_refs`; nullable
`quota_units` and `spend_microunits`; and booleans `update`, `downgrade`, `grant_admin`. Each field
is an independent dimension; a true/nonempty value never implies another.

`ResourceEnvelope@1` has `max_cpu_millis`, `max_memory_bytes`, `max_disk_bytes`,
`max_concurrency`, `max_queue_events` and `max_queue_bytes`, all positive.

`PluginManifest@1` has:

- `type`, `id`, `plugin_id`, `version`, `protocol_version`, `artifact_digest`,
  `dependency_lock_digest`, `trust_tier`;
- sorted `provided_capabilities`, `required_capabilities`, `dependencies`,
  `exclusive_resources`, `conflicts_with_plugin_ids`, `durable_subscriptions`,
  `ephemeral_subscriptions`, `lifecycle_hooks`, and `health_probe_ids`;
- `configuration_schema_digest`, `isolation_mode`, `requested_grants`, `resource_envelope`,
  `provenance_digest`, `license_id`, nullable `update_source`, and `manifest_digest`.

`type` is `PluginManifest@1`; trust is `T0-kernel`, `T1-signed-built-in`,
`T2-signed-isolated-third-party`, `T3-untrusted-view` or `T4-external-engine-provider`;
isolation is `typed-in-process`, `isolated-subprocess`, `remote-protocol`, `sandboxed-view` or
`metadata-only`. Lifecycle hooks are from `verify`, `stage`, `activate`, `health`, `drain`,
`revoke`, `retire`. `manifest_digest` omits only itself.

`PluginGrantEnvelope@1` has `type`, `id`, `plugin_id`, `artifact_digest`,
`dependency_lock_digest`, `grant_epoch`, `goal_spec_digest`, `policy_digest`, `dimensions`,
`revoked`, and `grant_digest`; the digest omits only itself.

`PluginPolicyEnvelope@1` has `type`, `id`, `goal_spec_digest`, `policy_digest`, `pause_epoch`,
sorted `allowed_trust_tiers`, `allowed_isolation_modes`, `allowed_capabilities`,
`allowed_workspace_paths`, `allowed_network_destinations`, `allowed_credential_refs`,
`allowed_model_refs`, `allowed_route_account_refs`; `max_quota_units`, `max_spend_microunits`;
and booleans `update_allowed`, `downgrade_allowed`, `grant_admin_allowed`.

`PluginLifecycleRecord@1` has `plugin_id`, `artifact_digest`, `state`, `epoch`,
`packet_epoch`, `lease_epoch`, `subscription_epoch` and nullable `replacement_digest`. State is
`discovered`, `verified`, `admitted`, `staged`, `active`, `quarantined`, `rejected`, `revoked`,
`drain-and-fence`, `retained-evidence`, `retired` or `replaced`.

`PluginResolutionInput@1` has `type`, manifests ordered by `plugin_id`, grants ordered by
`plugin_id`, `policy`, sorted unique `enabled_plugin_ids`, and lifecycle records ordered by
`plugin_id`. `PluginResolutionDecision@1` has `type`, status `resolved` or `blocked`, ordered
`activation_order`, ordered `effective_grants`, and ordered `rejections`. Each rejection has
`plugin_id` and sorted unique reasons.

Every enabled, grant and lifecycle plugin ID must name a manifest. Every manifest required
capability must have exactly one provider among its declared direct dependencies; zero or
ambiguous providers block. A rejected dependency makes its dependents ineligible. Grant GoalSpec
and policy digests must equal the active policy envelope. A lifecycle is required for admission
and must bind the manifest artifact, the grant epoch and an admissible lifecycle state.

Closed plugin reasons:

`ambiguous-capability-provider`, `capability-denied`, `conflict-declared`, `dependency-cycle`,
`dependency-digest-mismatch`, `dependency-ineligible`, `dependency-missing`,
`exclusive-resource-conflict`, `grant-context-mismatch`, `grant-digest-mismatch`,
`grant-revoked`, `isolation-denied`, `lifecycle-digest-mismatch`, `lifecycle-missing`,
`lifecycle-state-denied`, `manifest-digest-mismatch`, `manifest-missing`, `plugin-not-enabled`,
`policy-limit-exceeded`, `required-capability-missing`, `sensitive-grant-missing`,
`stale-plugin-epoch`, `trust-tier-denied`, `unknown-capability`, `unknown-protocol`.

`DisabledPluginInput@1` has `type`, `manifest`, `installed`, and `enabled` fixed false.
`DisabledActivityTrace@1` has `manifest_reads` (0 or 1) and the exact zero-only fields
`implementation_imports`, `payload_scans`, `processes`, `threads`, `timers`, `watchers`,
`network_calls`, `credential_reads`, `quota_reservations`, `spend_actions`, `cache_writes`,
`context_injections`, `tool_registrations`, `callbacks`, `event_subscriptions`.
`DisabledPluginDecision@1` has status `resolved-disabled` and `trace`.

`PluginReloadInput@1` has `type`, `old_lifecycle`, `new_manifest`, `grant`, `policy`, and
`old_binding_epochs` for packet/lease/subscription. `PluginReloadDecision@1` has status
`resolved-reload` or `blocked`, `events`, `new_epoch`, and sorted unique `old_binding_reasons`.
Successful events are exactly `verified`, `staged`, `drain-and-fence`, `replaced`, `active`.
Reload revalidates the new manifest and grant against the supplied policy, requires the old active
lifecycle and replacement digest to identify the transition exactly, and requires all old binding
epochs to equal the old lifecycle epoch before fencing them.

## Process and broker records

`ProcessCapabilityDescriptor@1` has `type`, `id`, `host_id`, `platform`, `platform_version`,
`eligibility_state`, `transport_capabilities`, `containment_capabilities`,
`cancellation_capabilities`, `evidence`, and `descriptor_digest`. Capability arrays are ordered by
name and use `TriState`. Transport names are `pipe`, `pty`, `conpty`; containment names are
`job-object`, `breakaway-prevention`, `process-group`, `session`, `cgroup-v2`, `pidfd`,
`descendant-capture`; cancellation names are `cooperative`, `interrupt`, `tree-terminate`,
`observe-exit`.

`ProcessRequirement@1` has `type`, `id`, `actor_id`, `task_id`, `work_packet_digest`,
`route_descriptor_digest`, `host_id`, `platform`, sorted nonempty `required_transports`,
`required_containment`, `required_cancellation`, `stdio_encoding` fixed `utf-8`,
`max_buffer_bytes`, `attach_allowed`, `operative_pause_policy` fixed `current-immediate`, and
sorted `representable_future_pause_policies` drawn from `checkpoint`, `interrupt`, `drain`,
`emergency`.

`ProcessAdmissionInput@1` has `type`, `requirement` and `descriptor`.
`ProcessAdmissionDecision@1` has `type`, status `admitted` or `blocked`, and sorted unique reasons.
An admitted decision has no reasons; a blocked decision has at least one.
Closed reasons are `cancellation-unknown`, `cancellation-unsupported`, `containment-unknown`,
`containment-unsupported`, `descriptor-not-current`, `host-mismatch`, `platform-mismatch`,
`transport-unknown`, `transport-unsupported`.

`ProcessTerminationObservation@1` has `type`, `process_requirement_id`, `process_epoch`,
`tree_status` (`terminated`,`partial`,`unknown`), sorted `remaining_process_refs`,
`exit_evidence_digest`, and `effect_conclusion` fixed `not-evaluated`.
`terminated` requires an empty remaining set; `partial` requires a nonempty remaining set.

Every broker message has a `type` discriminator and `protocol_version` fixed `m1b-broker/1`.

| Message | Remaining exact fields |
|---|---|
| `HELLO` | `client_id`, `stream_id`, `daemon_epoch`, `last_cursor`, `cursor_unit`, `columns`, `rows`, sorted `capabilities` |
| `WELCOME` | `client_id`, `stream_id`, `daemon_epoch`, `replay_floor`, `snapshot_cursor`, `cursor_unit`, nullable `input_lease`, nullable `resize_lease`, sorted `capabilities` |
| `SNAPSHOT` | `stream_id`, `daemon_epoch`, `cursor`, `cursor_unit`, `snapshot_digest` |
| `EVENT` | `stream_id`, `daemon_epoch`, `cursor`, `cursor_unit`, `event_class`, nullable `process_id`, `payload_base64`, `payload_untrusted` fixed true |
| `ACK` | `client_id`, `stream_id`, `daemon_epoch`, `cursor`, `cursor_unit` |
| `CREDIT` | `client_id`, `stream_id`, `daemon_epoch`, `bytes`, `events` |
| `INPUT` | `command_id`, `client_id`, `stream_id`, `daemon_epoch`, `process_epoch`, `input_lease`, `bytes_base64` |
| `RESIZE` | `command_id`, `client_id`, `stream_id`, `daemon_epoch`, `process_epoch`, `resize_lease`, `columns`, `rows` |
| `RESET` | `client_id`, `stream_id`, `daemon_epoch`, `reason` fixed `gap`, `snapshot_cursor`, `cursor_unit` |

Cursor unit is `utf8-byte` or `event`. Cursor/count fields are `Count`; dimensions are 1–1000;
credit is positive and capped at 16,777,216 bytes and 65,536 events. Lease values are `OpaqueRef`.

`BrokerTraceInput@1` has `type`, `initial_daemon_epoch`, `initial_process_epoch`, nullable current
input/resize leases, positive `queue_limit_bytes`, `queue_limit_events`, ordered `messages`, and
zero-based counters `launch_count`, `model_turn_count`, `actor_create_count`, `effect_count`.
One trace represents one client and one stream; every later identifier must match the first one.
`WELCOME` leases must equal the trace's current leases. CREDIT is required before EVENT delivery,
is additive, and is consumed cumulatively by decoded bytes and event count. Pending queue bytes
and events accumulate until a non-forward ACK releases them. Exhaustion remains unrecovered until
an explicit RESET clears the pending queue and credit. INPUT and RESIZE reuse of a command ID is a
no-op only for the byte-identical command; conflicting reuse is refused.

`BrokerTraceDecision@1` has `type`, status `accepted`, `accepted-reset` or `refused`, sorted unique
reasons, `final_cursor`, `cursor_unit`, the four final counters, and `requires_reset`.
Closed reasons are `ack-ahead`, `attach-created-work`, `client-mismatch`, `credit-exhausted`,
`credit-missing`, `cursor-nonmonotonic`, `cursor-unit-mismatch`,
`duplicate-command-conflict`, `output-command-injection`, `passive-client-input`,
`stale-daemon-epoch`, `stale-lease`, `stale-process-epoch`, `stream-mismatch`,
`utf8-byte-cursor-mismatch`, `welcome-lease-mismatch`.

## Fixture unions and manifest

The closed `M1BFixtureBundle@1` union has six arms:

- `RouteFixtureBundle@1`: `fixture_id`, `input: RouteResolutionInput@1`, `expected: RouteResolutionDecision@1`;
- `PluginFixtureBundle@1`: plugin resolution input/decision;
- `DisabledPluginFixtureBundle@1`: disabled input/decision;
- `PluginReloadFixtureBundle@1`: reload input/decision;
- `ProcessFixtureBundle@1`: process admission input/decision plus nullable termination observation;
- `BrokerFixtureBundle@1`: broker trace input/decision.

Every bundle also has `purpose` and `source_requirement_ids` as a nonempty sorted set. Fixture
files omit no field. `FixtureManifest@1` has `type`, `schema_digest`, and `fixtures` ordered by
`fixture_id`; each entry has `fixture_id`, `path`, `digest` and bundle `type`. The manifest digest
is not self-recorded.
