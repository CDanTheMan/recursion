# DS-21 — canonical state store and persistence faults (synthesis)

## Provenance

- Raw report: `raw/ds-4-DS-21-state-store.md` — "DS-21 Research Report: Canonical State Store
  and Persistence Faults". Handoff answered:
  `docs/v3/prompts/research-suite-20260929/DS-21-canonical-state-store-and-persistence-faults.md`.
- Session: Wave A Deep Research (self-contained handoff), retrieved 2026-09-30. Status: research
  evidence, not a decision; not independently verified by Recursion, no rerun. Per the report, no
  database was created or modified, no private repository was read, and there are no locally observed
  performance or fault results. Published behavior is *source-documented*; consequences are
  *inferred*; platform/workload questions are *unverified*. "Current" versions are as verified for
  the report on 2026-09-30 and must be revalidated before any experiment.

## The question

Choose the physical persistence layer for Recursion v3's canonical event/projection boundary: the
`JSONL`/JSON-Sequence + CAS baseline versus single-writer SQLite WAL + CAS, with embedded-KV and
PostgreSQL alternatives for multi-node. The store must satisfy one fenced writer per aggregate, a
monotonic sequence, content-addressed immutable artifacts, deterministic replay, duplicate-command
idempotence, stale-writer rejection, rebuildable projections, and recovery that reproduces the exact
digest or returns a typed gap/corrupt/ambiguous refusal. It must never become a second authority.

## Key findings

- **Two Milestone-2 finalists.** The decision stays between (a) a segmented append-only JSON Text
  Sequence/JSONL log plus CAS and (b) SQLite WAL plus the identical CAS. SQLite is the stronger
  implementation challenger: transactions, checksummed page/WAL machinery, single-writer
  serialization, concurrent WAL readers, online backup, integrity checking and mature Windows/Linux
  VFS implementations. The JSON baseline is the control: minimal hidden state, inspectable bytes.
- **Serialization is not authority.** A SQLite mutex, LMDB/RocksDB/redb write transaction, PostgreSQL
  row/index lock or file lock may serialize access, but the authority remains the admitted writer
  epoch plus canonical event sequence/digest. Obtaining a database writer lock must never be read as
  "my writer epoch is authorized". This follows from the DS-21 invariants, not any vendor claim.
- **Recommended SQLite durability profile: WAL + `synchronous=FULL`.** `NORMAL` is a different
  durability promise, not a cheaper equivalent: it preserves consistency but can lose recently
  committed transactions after a system/power failure; `OFF` weakens this further and can permit
  corruption. Checkpoint policy is a separate dimension (`PASSIVE` does not wait; FULL/RESTART/
  TRUNCATE can acquire the writer lock and invoke the busy handler). Long-lived readers can prevent
  complete checkpoints and grow the WAL, so maximum reader age, WAL size and checkpoint time are
  first-class benchmark outputs. `SQLITE_BUSY` is an availability result, not a stale-writer proof.
- **March-2026 WAL-reset incident → version/compile-option pin.** The report's sources record a rare
  WAL-reset corruption race affecting SQLite from WAL's introduction through **3.51.2**, fixed in
  **3.51.3 on 2026-03-13** (named backports). The current stable line found is **3.53.4, released
  2026-07-24**. This establishes a mandatory version/compile-option pin and a regression fixture —
  3.51.2 as negative control, 3.51.3/3.53.4 as fixed-line controls — not certification of 3.53.4 for
  Recursion. Stale `-wal`/`-shm` behavior on old versus new builds remains unverified.
- **Status of the embedded-KV alternatives.** None presently displaces both finalists. **LMDB
  1.0.1** (2026-08-06) is attractive (MVCC, serialized writes, low machinery) but adds map-size/
  mmap-file management and still needs Recursion's frame/epoch/integrity contract; kept as a secondary
  challenger. **RocksDB 11.8.1** (release notes 2026-07-28) is mature but LSM compaction, write stalls
  and a larger configuration surface do not obviously benefit a small coordinator metadata store;
  admitted only if scale measurements require LSM behavior. **sled 0.34.7** calls itself beta/
  unstable, advises reliability-first users to use SQLite, and warns of manual pre-1.0 format
  migration; it does not clear a conservative maturity floor today. **redb 4.3.0** (package
  2026-09-15, changelog 2026-09-14) shows stable-format/ACID claims, but 4.3 only introduces
  *experimental* multi-process read/write after several 2026 releases with significant correctness/
  data-loss fixes; a challenger test, not assumed equivalence.
- **PostgreSQL is the multi-node candidate.** **PostgreSQL 18.6** (2026-08-13) is current stable;
  **19 Beta 4** (2026-09-24) is explicitly not a production release. PostgreSQL supplies server-side
  concurrency control, WAL, unique constraints, replication and backup, but shifts the boundary from
  an embedded store to a network service, and still cannot decide Recursion's writer epoch or make an
  external side effect exactly-once. Evaluate it only when multi-node authority is a real requirement.
- **Other pinned facts.** JSON Text Sequence framing is RFC 7464 (2015-02); it governs framing only
  and deliberately provides no Recursion sequence, CRC, chaining, fencing or transaction grouping.
  Linux `fsync(file)` does not make the containing directory entry durable; Windows
  `FlushFileBuffers`/`ReplaceFileW` have distinct contracts, so Linux results are not transferable.
  SQLite WAL does not support ordinary network filesystems (coordination needs shared memory).
  Encryption is unselected; SQLCipher 4.19.0 (2026-09-08) is current, and its 4.14.0 release moved its
  SQLite baseline to 3.51.3 for the WAL-reset fix — why the wrapper's SQLite baseline must be pinned.

## Recommendation and falsifier

**No store selection yet.** The gate is the canonical crash/replay benchmark. Run it against
**SQLite 3.53.4 WAL + CAS versus segmented JSON Text Sequence + identical CAS first**, under strong
durability profiles (SQLite `journal_mode=WAL`, `synchronous=FULL`, explicit checkpoint policy,
bounded busy handling; JSON: complete frame write, `fdatasync`/`fsync`, directory sync when publishing
segments/manifests). Retain LMDB 1.0.1 and redb 4.3.0 as secondary challengers, admit RocksDB only if
measurements require LSM behavior, and evaluate PostgreSQL when multi-node authority is real.

- **SQLite decisive falsifier:** any strong-profile fault in which an acknowledged event is silently
  absent or divergent after power loss, any accepted history with the wrong canonical digest,
  inability to bound WAL/checkpoint behavior under the four-reader workload, or total resource use
  outside the Owner-set floor. Passing `PRAGMA integrity_check` alone proves neither chain nor CAS.
- **JSON Sequence decisive falsifier:** any crash/short-write/rename sequence where recovery cannot
  unambiguously determine the last durable frame and instead needs heuristics, failure to provide
  robust cross-process writer fencing on both Windows and Linux, or materially worse p99/fsync/
  resource cost after equal durability semantics.

The acceptance rule is ordered: hard correctness floors first (exact replay digest, stale-writer
exclusion, duplicate-command reuse, no silent tail repair, no missing/wrong CAS, promised power-loss
durability, clean-host restore), then privacy/operability floors, and only then resource ranking.

## What this does not prove

- It does not select a store, certify any version, or claim the named WAL bug is present or fixed.
  It contains no Recursion workload measurements: throughput, latency, RSS and total bytes are unknown
  by design, and third-party benchmarks are not comparable to the DS-21 workloads and mixes.
- It does not prove 3.53.4 safe for Recursion's VFS/filesystem/workload (the version boundary is
  documentation only), nor resolve stale `-wal`/`-shm` behavior, cross-filesystem/network-FS
  durability, or Windows power-cut behavior; these remain unverified fixture assignments.
- It does not establish exactly-once external effects (the crash gap is unavoidable) nor cross-project
  CAS dedup safety; the report keeps a hard floor against private cross-domain dedup.

## Open Owner decisions

The missing decisions are the durability promise and deployment envelope, not technology names:

- Whether a success response means per-command power-loss durability or permits group commit, and the
  maximum accepted batching delay.
- Target local filesystems on Windows and Linux; whether SMB/NFS is explicitly forbidden.
- Whether multi-node canonical availability is a v3 requirement or future optionality.
- Maximum permitted p99 append latency, replay/recovery time, WAL/log growth, RSS and bytes per 1M
  events; the durability unit (command, transaction group, or time-bounded batch).
- Backup RPO/RTO and backup-expiry window; privacy/deletion key scope; the maximum age of a read
  observer before it must refresh.

## Relevance to later waves

DS-21 blocks Milestone 2 (the canonical writer), which must beat the JSONL baseline on a
crash/replay/fault matrix before SQLite can be adopted. This synthesis fixes that experiment's shape:
the two finalists and their strong profiles, the version pins and WAL-reset negative control, the
candidate-neutral backup/restore oracle, canonical ordered-event identity as the replay parity test
(not equal rendered projection), and the decisive falsifiers. Later waves must apply the ordered
acceptance rule and count all bytes (database/log plus sidecars plus CAS) together.
