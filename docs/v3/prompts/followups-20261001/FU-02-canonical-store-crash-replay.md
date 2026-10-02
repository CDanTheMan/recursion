---
title: FU-02 — Canonical state store crash and replay benchmark
status: ready-for-explicit-invocation
last-updated: 2026-10-01
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# FU-02 — Canonical state store crash and replay benchmark

This is a follow-up to gap G-02 in [GAPS.md](../../research-lane/GAPS.md) and source lane DS-21 (Domain A).

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone harness and harness orchestrator; Hermes is a retired control plane and an optional upstream integration. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- DS-21 returned an explicit **no store selection yet**. The Milestone-2 finalists are
  segmented append-only JSON Text Sequence/JSONL + CAS versus SQLite WAL + the identical CAS,
  with LMDB 1.0.1 and redb 4.3.0 as secondary challengers, RocksDB only if LSM behavior is
  required, and PostgreSQL 18.6 only when multi-node authority is real.
- Pins at the 2026-09-30 freeze: SQLite 3.53.4 with `journal_mode=WAL`, `synchronous=FULL` and
  an explicit checkpoint policy; a March-2026 WAL-reset corruption race fixed in 3.51.3 gives a
  mandatory version pin and a 3.51.2 negative control. JSON Text Sequence framing is RFC 7464,
  which governs framing only and provides no sequence, CRC, chaining, fencing or transaction
  grouping.
- It recorded that serialization is not authority: a database writer lock must never be read as
  "my writer epoch is authorized"; the authority remains the admitted writer epoch plus the
  canonical event sequence/digest.
- It left open: no Recursion workload measurement, throughput/latency/RSS/total-bytes unknown by
  design, stale `-wal`/`-shm` behavior, cross-filesystem/network durability and Windows
  power-cut behavior unverified; and the availability/authority contract (G-06) is still
  undecided.
- This lane blocks Milestone 2 (the canonical writer), which must beat the JSONL baseline on a
  crash/replay/fault matrix before SQLite can be adopted.

## Purpose

Produce the preregistered canonical crash/replay/fault benchmark specification and the
candidate-neutral acceptance oracle for the persistence layer, so the Owner can decide the store
and the durability promise. This is a specification-and-evidence lane: it fixes the experiment,
the fault matrix, the oracles and the version pins; it does not run the benchmark and does not
select a store.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Preserve the current Hermes constitution; propose amendments, never edit it. Public Deep
Research receives only public or synthetic briefs. **DO NOT select SQLite, JSONL, LMDB, redb,
RocksDB, PostgreSQL or any storage engine as a product default.** Do not decide the durability
promise or the availability/authority contract; those are Owner gaps (G-06). No database is
created or modified, and no repository, provider, auth, spending, deployment, publication or
merge action is authorized. No version is certified by this file.

## Inputs to read

None. This handoff is self-contained; the prior lane's conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Finalists, profiles and version pins

1. What is the exact strong-durability profile for each finalist, stated as machine-checkable
   settings (for SQLite: journal mode, synchronous, checkpoint policy, busy handling, VFS; for
   JSONL: complete-frame write, `fdatasync`/`fsync`, directory sync on segment/manifest
   publish), and what is the candidate-neutral equivalent durability promise between them?
2. What are the pinning and negative-control rules — the WAL-reset regression fixture, the
   wrapper/baseline pin, and the rule that a documentation boundary is not certification for
   Recursion's VFS/filesystem/workload?

### Fault matrix and oracles

3. What is the exact crash/fault matrix (power loss, torn/short write, rename/replace
   interruption, disk full, stale `-wal`/`-shm`, process kill at each append stage, network
   storage interruption), and what is the expected observable for each cell?
4. What is the canonical **replay parity oracle** — canonical ordinal event identity and
   state/projection digest — as distinct from equal rendered projection, and what makes it
   candidate-neutral?
5. What is the **stale-writer exclusion** oracle, enforced at admission and again at the durable
   mutation boundary, and how does it differ from a database lock or `SQLITE_BUSY`?
6. What is the **duplicate-command reuse** oracle, and what is the disposition when the store is
   uncertain rather than failed (never blind retry, explicit reconciliation)?

### Durability boundaries, platform and multi-node

7. Which durability claims are local filesystem only, and what exact fault corpus must pass
   before SMB/NFS or `/mnt/c` is qualified rather than rejected?
8. What separates a SQLite VFS/Windows power-cut result from a Linux result, and what
   cross-filesystem and directory-entry-sync facts must the benchmark state explicitly?
9. If multi-node canonical availability (G-06) is treated as a requirement, what additional
   cells does PostgreSQL or a replicated authority add, and what makes those cells out of scope
   otherwise?

### Accounting, backup and decision rule

10. How are all bytes counted together (database/log plus sidecars plus CAS), and what are the
    denominators for append latency, replay/recovery time, WAL/log growth and RSS per million
    events?
11. What is the candidate-neutral backup/snapshot/restore oracle (state high-water, checkpoint
    digest, schema epoch, immutable artifact set), and what distinguishes a consistent snapshot
    from files merely copied?
12. What is the ordered acceptance rule (hard correctness floors first, then privacy/operability,
    then resource ranking), and what single fault falsifies each finalist?
13. What is the exact decision rule that converts the matrix into an Owner recommendation,
    including the no-selection/keep-baseline outcome and the Owner inputs (durability promise,
    batching delay, filesystem targets, latency/space budgets, backup RPO/RTO, key scope,
    read-observer age) that must exist before it can run?

## Deliverable

A source-pinned report containing: a claim table (claim, source, version/date, classification,
confidence, expiry trigger); the two finalist profiles with exact settings and candidate-neutral
durability equivalence; the fault matrix with expected observables; the replay-parity,
stale-writer and duplicate-reuse oracles; the all-bytes accounting method and metric
denominators; the backup/restore oracle; a per-finalist decisive falsifier and the ordered
acceptance rule; and the Owner inputs required before the benchmark can run. No store is
selected as a product default.

## Non-goals

- No selection or certification of any store, version, engine or wrapper.
- No database created, modified or benchmarked by this session.
- No decision of the durability promise or the availability/authority contract.
- No exactly-once external-effect claim.
- No numeric budget invented before measurement.
- No third-party benchmark treated as comparable to the Recursion workload.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- Both finalists carry exact versions, settings and a candidate-neutral durability profile, or
  the missing cell is explicitly `unverified`.
- The fault matrix names every cell, its injected fault and its expected observable.
- Replay parity, stale-writer exclusion and duplicate-command reuse are stated as separate
  oracles, not collapsed into one.
- All bytes are counted together and every metric carries a denominator.
- The backup/restore oracle is candidate-neutral and distinguishes a consistent snapshot from
  copied files.
- Each finalist has a decisive falsifier, and the ordered acceptance rule is stated.
- The recommendation preserves an explicit no-selection outcome and names the Owner inputs that
  block the run.
- Protected paths are untouched; privacy and secret scan are clean.
