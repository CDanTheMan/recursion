---
title: M1C exact integrity JSON wire profile
status: frozen-for-local-construction
last-updated: 2026-09-04
---

# M1C exact integrity JSON wire profile

## Encoding and common scalars

M1C uses UTF-8 I-JSON objects validated with JSON Schema Draft 2020-12. Duplicate keys,
surrogate/non-UTF-8 input, NaN/Infinity, floats, booleans in integer fields, unknown fields,
unknown union arms and unknown versions fail before semantic evaluation. Input is bounded to
1,048,576 encoded bytes and nesting depth 32.

Canonical bytes use UTF-8, keys sorted by Unicode code point, no insignificant whitespace,
`ensure_ascii=false`, and one trailing LF. SHA-256 fields are lowercase 64-hex digests over the
documented canonical object with its self-digest field omitted. Nothing hashes a wall clock,
environment value or external lookup.

Common scalars:

- `EntityId`: 3–160 characters matching `^[a-z][a-z0-9-]{1,31}:[A-Za-z0-9._~-]{1,128}$`;
- `OpaqueRef`: 1–192 printable non-whitespace ASCII characters, never a secret value;
- `Digest`: lowercase `sha256:` plus 64 hexadecimal characters;
- `GitSha`: exactly 40 lowercase hexadecimal characters;
- `Timestamp`: canonical UTC `YYYY-MM-DDTHH:MM:SSZ` with a real Gregorian date;
- `Count`: exact integer 0–1,000,000; `PositiveCount`: exact integer 1–1,000,000;
- `Token`: 1–96 characters matching `^[A-Za-z0-9][A-Za-z0-9._:-]{0,95}$`;
- `CanonicalUri`: 1–512 characters, absolute `https://`, `urn:` or `recursion:` URI without
  credentials, whitespace, fragment or control characters.

Every field named `*_ids`, `*_digests`, `*_kinds`, `reasons` or `completed_stages` is a
lexicographically sorted unique set unless this profile explicitly calls it an ordered trace.

## Evidence records

`PersistentIdentifier@1` has exactly:

- `type` fixed `PersistentIdentifier@1`;
- `scheme`: `doi`, `arxiv`, `isbn`, `rfc`, `repo-commit`, `dataset-doi` or `other`;
- `value`: `OpaqueRef`;
- `verification_state`: `verified`, `unverified` or `mismatch`;
- nullable `verification_evidence_digest: Digest`.

`SourceRecord@1` has exactly:

- `type`, `source_id: EntityId`, `canonical_uri: CanonicalUri`;
- `persistent_identifiers`: 1–16 unique records keyed by `(scheme,value)`;
- `title_digest: Digest`, `creator_digests`: 1–64 digests, nullable `publisher_digest: Digest`;
- `source_class`: `paper`, `standard`, `dataset`, `repository`, `official-documentation`,
  `web-secondary` or `experiment`;
- `primary_status`: `primary` or `secondary`;
- `supported_scopes`: nonempty set of `external-mechanism`, `local-structural`, `empirical-fit`;
- `lifecycle`: `discovered`, `identified`, `retrieved`, `verified`, `quarantined` or `expired`;
- `editorial_state`: `current`, `corrected`, `superseded`, `retracted`, `withdrawn` or `unknown`;
- `access_state`: `accessible`, `inaccessible`, `metadata-only` or `unknown`;
- `license_state`: `permitted`, `restricted`, `prohibited` or `unknown`;
- `privacy_class`: `public`, `internal`, `private` or `restricted`;
- `version: Token`, nullable `published_at`, nullable `retrieved_at`, `adapter_ref: OpaqueRef`,
  `adapter_revision: Token`, nullable `request_digest`, nullable `content_digest`, nullable
  `representation_size: Count`, nullable `verification_evidence_digest`;
- `related_source_ids`: 0–64 source IDs; nullable `revalidate_after: Timestamp`.

When lifecycle is `retrieved` or `verified`, retrieval time, request/content/verification digests
and representation size are non-null. Lifecycle `verified` also requires at least one verified
persistent identifier. `metadata-only` requires null content digest and representation size.

`ResearchClaim@1` has exactly `type`, `claim_id`, `goal_spec_id`, `goal_spec_digest`,
`proposition_digest`, `claim_kind`, `evidence_scope`, `intended_use`, `required_source_ids`,
`assumption_digests`, `definition_digests` and nullable `revalidate_after`. `claim_kind` is `fact`,
`inference`, `hypothesis`, `proposal` or `owner-direction`; `evidence_scope` uses the three scope
values above; `intended_use` is `internal` or `public`. The three sets are bounded 0–64 except
`required_source_ids`, which is nonempty.

`EvidenceEdge@1` has exactly `type`, `edge_id`, `claim_id`, `source_id`, `relation`, `locator`,
`extraction_digest`, `source_version`, `applicability`, `extraction_verified`. Relation is one of
`supports`, `contradicts`, `qualifies`, `replicates`, `updates`, `mentions`, `metadata-only`,
`inapplicable`; applicability is `exact`, `partial`, `inapplicable` or `unknown`; locator is a
nonempty `OpaqueRef`.

`EvidenceAssessmentInput@1` has exactly `type`, `observed_at`, `claim`, `sources`, `edges`,
`allowed_privacy_classes`, `allowed_license_states`, and `public_export_authorized`. Sources and
edges are nonempty arrays of at most 128 records keyed uniquely by ID. Every required source ID and
edge endpoint must resolve exactly; extra sources are permitted only when referenced by an edge.

`EvidenceReason` is closed to: `claim-binding-mismatch`, `edge-binding-mismatch`,
`source-missing`, `source-unverified`, `source-stale`, `source-retracted`, `source-superseded`,
`source-inaccessible`, `metadata-only`, `license-prohibited`, `privacy-prohibited`,
`export-prohibited`, `scope-inapplicable`, `extraction-unverified`, `support-insufficient`,
`contradiction-present`, `qualification-present`.

`EvidenceDecision@1` has exactly `type`, status `supported`, `contested`, `unknown` or `refused`,
sorted `reasons`, `accepted_edge_ids`, `contradiction_edge_ids`, `qualification_edge_ids` and
`rejected_source_ids`. Supported has at least one accepted supporting/replicating/updating edge and
no accepted contradiction. Contested has both. Unknown has no admissible support. Refused carries
a binding, privacy or export violation.

## Effect records

`EffectIntent@1` has exactly:

- `type`, `effect_id`, `command_id`, `idempotency_key`, `intent_digest`;
- `effect_class`: `local-reversible`, `local-irreversible`, `external-idempotent`,
  `external-reconciliation-only` or `publication`;
- `target_ref`, `payload_digest`, `goal_spec_id`, `goal_spec_digest`, `plan_digest`,
  `policy_digest`, `grant_digest`, `privacy_digest`, `route_digest`, `budget_digest`;
- `actor_id`, `lease_id`, `admission_epoch`, `fence_epoch`, `deadline`;
- `dependency_effect_ids`; `reversible`; nullable `compensation_effect_id`.

The intent digest seals the record without `intent_digest`. Only `local-reversible` may set
`reversible=true`, and then compensation ID is required. Other classes use false/null.

`EffectAdmission@1` has exactly `type`, `admission_id`, `effect_id`, `intent_digest`, decision
`admitted` or `refused`, `actor_id`, `lease_id`, `admission_epoch`, `fence_epoch`, the six
policy/grant/privacy/route/budget/GoalSpec digests, `pause_profile`, `pause_state`, `admitted_at`
and sorted `reasons`. `pause_profile` is `current-immediate`, `future-checkpoint`,
`future-interrupt` or `future-drain`; `pause_state` is `running` or `paused`. Only
`current-immediate/running` with no reasons may be admitted in M1C.

The ordered `EffectObservation` union contains:

- `AttemptStarted@1`: `type`, `effect_id`, `attempt_id`, `attempt_number`, `idempotency_key`,
  `target_ref`, `payload_digest`, `admission_epoch`, `fence_epoch`, `observed_at`;
- `ExternalObserved@1`: the same identity fields plus `observation_id`, `observer_ref`,
  `authenticity` (`verified`, `unverified`, `mismatch`), outcome `accepted`, `rejected` or
  `unknown`, nullable `remote_operation_ref`, nullable `result_digest`, `observed_at`;
- `ReceiptRecorded@1`: the same identity fields plus `receipt_id`, `observer_ref`, authenticity,
  result `succeeded` or `failed`, `result_digest`, nullable `remote_operation_ref`, `observed_at`;
- `ReconciliationObserved@1`: the same identity fields plus `reconciliation_id`, `observer_ref`,
  authenticity, outcome `succeeded`, `failed` or `unknown`, nullable `result_digest`, nullable
  `remote_operation_ref`, `observed_at`.

Every attempt uses `attempt_number` 1–64. IDs are unique and timestamps are nondecreasing.

`DependencyEffectState@1` has `type`, `effect_id`, and status `succeeded`, `failed`, `ambiguous`,
`reconciled-succeeded` or `reconciled-failed`.

`EffectTraceInput@1` has exactly `type`, `intent`, `admission`, ordered `observations` (0–128),
`dependency_states` keyed by effect ID, `current_admission_epoch`, `current_fence_epoch`,
`effect_count`, `external_call_count`. The counters must be zero.

`EffectReason` is closed to: `admission-refused`, `intent-binding-mismatch`,
`authority-binding-mismatch`, `stale-admission`, `stale-fence`, `paused`,
`future-pause-inoperative`, `dependency-unresolved`, `attempt-binding-mismatch`,
`observation-binding-mismatch`, `observation-unverified`, `receipt-binding-mismatch`,
`receipt-missing`, `observation-conflict`, `blind-retry-blocked`, `reconciliation-required`,
`reconciliation-unverified`, `compensation-not-separate`.

`EffectDecision@1` has exactly `type`, status `refused`, `prepared`, `executing`, `succeeded`,
`failed`, `ambiguous`, `reconciled-succeeded` or `reconciled-failed`, sorted reasons,
`final_attempt_number`, `requires_reconciliation`, `effect_count`, `external_call_count`.

## Publication records

`PublicationArtifact@1` has exactly `type`, `artifact_id`, `content_digest`, `classification`,
`license_state`, `redaction_state`, `secret_scan`, `export_authorized`. Classification is
`public`, `internal`, `private` or `restricted`; license is `permitted`, `restricted`,
`prohibited` or `unknown`; redaction is `not-required`, `verified`, `missing` or `unknown`; secret
scan is `pass`, `fail` or `unknown`.

`GateEvidence@1` has exactly `type`, `gate_id`, `source_sha`, `candidate_sha`, status `pass`,
`fail` or `unavailable`, `evidence_digest`, `observed_at`.

`VerifierEvidence@1` has exactly `type`, `verifier_id`, `source_sha`, `candidate_sha`, status
`pass`, `dissent` or `unavailable`, independence `full`, `downgraded` or `same-actor`,
`policy_sufficient`, `evidence_digest`, `observed_at`.

`PublicationIntent@1` has exactly `type`, `publication_id`, `effect_id`, `intent_digest`,
`publication_kind`, `repository_ref`, `source_sha`, `candidate_sha`, `review_ref`, `target_branch`,
`protected_branch_names`, `goal_spec_id`, `goal_spec_digest`, `policy_digest`, `grant_digest`,
`privacy_digest`, `candidate_tree_digest`, `required_gate_ids`, `required_verifier_ids`,
`artifact_ids`. Publication kind is `review-branch`, `merge`, `release` or `deployment`; review ref
matches `refs/heads/[A-Za-z0-9][A-Za-z0-9._/-]{0,159}` without `..`, `//`, `@{` or `.lock`.

`PublicationReceipt@1` has exactly `type`, `receipt_id`, `publication_id`, `effect_id`,
`repository_ref`, `review_ref`, `candidate_sha`, `publisher_ref`, `remote_state` (`observed`,
`rejected`, `unknown`), nullable `remote_commit_sha`, `observed_at`, `receipt_digest`.

`PublicationAssessmentInput@1` has exactly `type`, `intent`, `artifacts`, `gates`, `verifiers`,
`source_ancestry` (`known-ancestor`, `not-ancestor`, `unknown`), `candidate_tree` (`clean`, `dirty`,
`unknown`), `publication_authority` (`granted`, `denied`, `unknown`), `required_independence`
(`full` or `downgraded`), nullable `receipt`, `git_mutation_count`. The count must be zero.

`PublicationReason` is closed to: `publication-kind-prohibited`, `protected-target`,
`source-not-ancestor`, `source-ancestry-unknown`, `candidate-dirty`, `candidate-state-unknown`,
`authority-missing`, `artifact-missing`, `artifact-binding-mismatch`,
`artifact-export-prohibited`, `secret-scan-failed`, `license-prohibited`, `gate-missing`,
`gate-failed`, `gate-binding-mismatch`, `verification-missing`, `verification-insufficient`,
`verification-binding-mismatch`, `receipt-binding-mismatch`, `remote-state-unknown`.

`PublicationDecision@1` has exactly `type`, status `eligible`, `blocked`, `published`, `rejected`
or `ambiguous`, sorted reasons, `publication_id`, nullable `published_sha`,
`requires_reconciliation`, `git_mutation_count`.

## Fabric-only state records

`WriterRecord@1` has exactly `type`, `writer_id`, `mutation_path_digest`, `observation_state`
(`known` or `unknown`), `can_refuse`, `configured_fence_epoch` and `source_revision: GitSha`.

`CanonicalEvent@1` has exactly `type`, `aggregate_id`, `sequence`, `event_id`, `command_id`,
`idempotency_key`, `causation_id`, `correlation_id`, `writer_id`, `fence_epoch`, `logical_time`,
`schema_version`, nullable `previous_event_digest`, `payload_digest`, `event_digest`,
`authentication_state` (`verified`, `unverified`, `mismatch`). Sequence and logical time are
positive; the first sequence is 1 with null previous digest. Event digest seals the record without
`event_digest`; each later previous digest equals the prior event digest.

`OpenWork@1` has exactly `type`, `work_id`, kind `lease`, `effect`, `publication` or `saga`, and
state `closed`, `active`, `open`, `ambiguous`, `pending` or `partial`.

`StateContractAssessmentInput@1` has exactly:

- `type`, `migration_id`, aggregate type fixed `fabric-only`, `aggregate_id`,
  `source_revision`, `source_state_digest`, `immutable_assignment_digest`;
- `expected_writer_ids`, `observed_writers`, `canonical_writer_id`, `current_fence_epoch`;
- ordered `events` (1–512), `import_state` (`lossless`, `lossy`, `unknown`),
  `expected_replay_digest`, `actual_replay_digest`, `expected_projection_digest`,
  `actual_projection_digest`;
- proof states `writer_refusal`, `backup`, `restore`, `reverse_reader`, `rollback` each
  `verified`, `failed` or `unknown`;
- `completed_stages`: an ordered prefix of `snapshotted`, `validated`,
  `legacy-writers-quiesced`, `fence-established`, `imported`, `replayed`,
  `shadow-read-verified`, `v3-owner-active`, `checkpointed`;
- `open_work`; `deployment_revision_state` (`known` or `unknown`); `state_write_count` fixed zero.

`StateReason` is closed to: `aggregate-scope-mismatch`, `deployment-unknown`,
`writer-inventory-incomplete`, `writer-unknown`, `dual-writer`, `writer-refusal-unproved`,
`stale-fence`, `sequence-gap`, `digest-chain-invalid`, `event-unverified`, `lossy-import`,
`import-unknown`, `replay-mismatch`, `projection-mismatch`, `projection-only`,
`backup-unverified`, `restore-unverified`, `reverse-reader-unverified`, `rollback-unproved`,
`stage-order-invalid`, `open-lease`, `open-effect`, `pending-publication`, `saga-incomplete`.

`StateDecision@1` has exactly `type`, status `eligible`, `blocked` or `recovery-required`, sorted
reasons, `aggregate_id`, `final_sequence`, `current_fence_epoch`, `state_write_count`.

## Retention records

`CopyDisposition@1` has exactly `type`, `copy_id`, kind `local`, `cache`, `replica`, `backup` or
`disconnected-spool`, state `deleted`, `expiry-bound`, `pending`, `soft-deleted`, `delete-marker`,
`disconnected` or `unknown`, `evidence_state` (`verified`, `unverified`, `mismatch`), nullable
`evidence_digest`, nullable `expiry_boundary`, and `expiry_reached`.

`DeletionTombstone@1` has exactly `type`, `tombstone_id`, `artifact_class`, `policy_digest`,
`responsible_component`, `requested_at`, nullable `disposed_at`, `copy_dispositions`,
`contains_content`, `contains_secret`, `contains_global_content_digest`, `tombstone_digest`.
Copy dispositions are sorted by copy ID. Tombstone digest seals the record without itself.

`RetentionAssessmentInput@1` has exactly `type`, `artifact_id`, `artifact_class`, `privacy_class`,
`policy_digest`, `owner_erasure_policy` (`granted`, `denied`, `unknown`, `not-required`),
`legal_hold`, `local_content_deleted`, `key_state` (`destroyed`, `active`, `shared`, `unknown`),
`key_scope` (`artifact`, `project`, `shared`, `unknown`), `copies`, `tombstone`,
`deletion_operation_count` fixed zero. Artifact class is `raw-session`, `temporary`, `cache`,
`accepted-evidence`, `gate-receipt`, `publication-receipt`, `effect-receipt`,
`authority-receipt` or `audit-record`.

`RetentionReason` is closed to: `legal-hold`, `local-content-present`, `key-not-destroyed`,
`key-not-isolated`, `copy-unresolved`, `copy-evidence-unverified`, `expiry-not-reached`,
`copy-inventory-mismatch`, `tombstone-mismatch`, `tombstone-sensitive`,
`owner-policy-required`, `owner-policy-denied`.

`RetentionDecision@1` has exactly `type`, status `complete`, `incomplete` or `blocked`, sorted
reasons, `artifact_id`, `resolved_copy_ids`, `unresolved_copy_ids`,
`deletion_operation_count` fixed zero.

## Fixture unions and manifest

The closed `M1CFixtureBundle@1` union has five arms: `EvidenceFixtureBundle@1`,
`EffectFixtureBundle@1`, `PublicationFixtureBundle@1`, `StateFixtureBundle@1` and
`RetentionFixtureBundle@1`. Each has `type`, `fixture_id`, `purpose`, nonempty sorted
`source_requirement_ids`, typed `input`, and the matching typed literal `expected` decision.

`FixtureManifest@1` has `type`, `schema_digest`, and entries ordered by fixture ID. Each entry has
`fixture_id`, relative `path`, bundle `type` and exact fixture `digest`. The manifest digest is not
self-recorded. Fixture IDs are exactly `F-M1C-001` through `F-M1C-024`.
