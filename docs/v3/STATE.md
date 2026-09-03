---
title: Recursion v3 state and persistence hypothesis
status: hypothesis
last-updated: 2026-09-02
---

# Recursion v3 state and persistence hypothesis

## Canonical model

V3 should use lightweight SQLite-first persistence in WAL mode for canonical control events and projections, with large immutable artifacts stored as content-addressed files. Human-readable YAML/JSON remains configuration and import/export; Markdown remains documentation and rendered status. They do not compete as live task truth.

The design target is one daemon per authority domain/OS account, not one supervisor process per checked-out Recursion fork.

## Write path

```text
input
  -> authenticate principal or component
  -> validate schema and authority
  -> begin SQLite transaction
  -> append immutable event
  -> update required projections
  -> enqueue idempotent action/outbox item
  -> commit
```

Only deterministic controller code writes canonical state. Models propose typed decisions. Remote nodes submit signed results that the controller validates and records.

## Event and projection split

Durable lineage events include:

- intent recorded, clarified, or superseded;
- GoalSpec drafted, accepted, or amended;
- executive/ARM created, leased, checkpointed, replaced, blocked, or closed;
- task created, admitted, assigned, started, checkpointed, verified, integrated, or cancelled;
- route resolved, rejected, failed over, or exhausted;
- budget reserved, consumed, released, or denied;
- node enrolled, attested, quarantined, revoked, disconnected, or reconciled;
- evidence accepted or invalidated;
- publication proposed, admitted, published, or rejected.

Ephemeral operational events—progress ticks, streaming deltas, health samples, UI presence—use a bounded live channel or sampled tables and are not forced into the permanent lineage log unless they affect a decision.

Projections serve queues, status, budgets, lineage, routing history, artifact reachability, branch inventory, and observer interfaces. Every projection must be rebuildable from durable events plus immutable artifacts.

## Exactly-once effect posture

Distributed side effects cannot be assumed exactly once. V3 instead requires:

- idempotency keys;
- prepare/execute/reconcile states;
- leases with expiry and fencing tokens;
- authenticated result receipts;
- exact repository and source bindings;
- replay-safe actuators;
- ambiguity recovery that inspects external state before repeating an effect.

## Artifact store

Large prompts, transcripts, repository maps, patches, logs, gate output, and context capsules live outside hot relational rows. The database stores digest, type, size, classification, owner project, encryption status, dependencies, lifecycle state, and locator.

Storage classes:

1. active control/checkpoint state;
2. acceptance and audit evidence;
3. retained raw session material;
4. rebuildable repository indexes and caches;
5. temporary downloads and streams.

When free-space floors are crossed, v3 removes expired temporary and rebuildable data first, then freezes new admissions before threatening canonical state or acceptance evidence.

## Retention hypothesis

The session direction proposes:

- successful raw sessions: 30 days;
- failed or disputed raw sessions: 90 days;
- compact metadata, lineage, decisions, receipts, and accepted evidence: indefinite or project-policy governed;
- explicit pinning for important sessions;
- project-specific shorter or longer policies within legal and storage constraints.

Retention and privacy deletion need a dedicated review because append-only integrity and deletion obligations can conflict. Cryptographic erasure and tombstone events are candidate mechanisms, not yet accepted designs.

## Performance posture

- One bounded writer path; many read-only projections.
- WAL checkpointing based on measured write volume and disk behavior.
- Prepared statements and batch event ingestion where ordering permits.
- No eager ORM object graph or plugin-specific columns in core tables.
- Bounded indexes justified by actual observer/routing queries.
- Incremental artifact garbage collection from reachability roots.
- Debounced telemetry writes and event-driven scheduling.
- Plugins communicate through typed interfaces rather than opening the database directly.

## Migration

V2 Markdown, JSON, and JSONL state should be imported through versioned adapters with:

- source file digest and commit;
- deterministic identity mapping;
- duplicate and conflict reports;
- dry-run projection comparison;
- reversible backup;
- replay and crash injection;
- refusal to fabricate missing or malformed state.

For a period, v3 may render legacy-compatible read-only views. Dual writable sources of truth are forbidden.

## Backup and recovery

Required proof includes:

- consistent SQLite plus artifact snapshot;
- encrypted offsite option;
- restore onto a fresh host;
- key and credential references excluded or separately provisioned;
- migration forward and rollback where schema permits;
- simulated torn write, disk full, process death, duplicate delivery, and stale lease;
- reconciliation of remote-node spools after controller recovery.

## Open questions

- Which v2 records belong in canonical event history versus import evidence?
- Is a single SQLite writer sufficient for every intended authority domain, or should high-volume telemetry use a separate store?
- How should artifact encryption keys rotate without breaking content identity?
- Which projections must be transactionally synchronous and which may be eventually rebuilt?
- What measured event volume and database size should define the VPS acceptance envelope?
