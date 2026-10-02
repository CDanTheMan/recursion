# FU-02 — canonical store crash/replay (synthesis)

## Provenance

Synthesis of the raw report at `raw/ds-FU-02-store-crash-replay.md`, the FU-02 research findings and preregistered
acceptance specification for the follow-up wave `followups-20261002`. The report's upstream claims rest on the
report's sources and its own claim table; nothing here is a Recursion rerun. The raw file carries `status:
research-evidence-not-a-decision` and `verification: not independently verified by Recursion; target experiments not
run`. Evidence review 2026-10-01; report completed 2026-10-02; Owner decision pending. This report answers gap G-02.

## The question

Which storage engine should back the canonical state store, and how can that choice be defended without running the
comparison here? The report frames the decision around the whole commit unit — admitted authority, canonical events,
state, command receipt, effect outbox and referenced immutable artifacts — not the database alone. It specifies two
finalists, their exact proposed profiles, the failure observables, rejection conditions, acceptance oracles, fault
matrix and the evidence needed for an Owner recommendation. Its answer is a deliberate **no storage selection**: both
finalists are retained for evidence collection, the JSON baseline is preserved as the comparison reference, and a
product selection is withheld until the Owner inputs and hard gates are complete.

## Key findings

- **No selection, by construction.** No experiment ran, no database was created, no version was certified. Every
  performance, space, memory, recovery and power-interruption outcome is **unknown** — not zero, not a pass. A
  database commit alone cannot certify the artifact set, stale-writer exclusion or exactly-once external effects.
- **Finalists.** Segmented append-only JSON Text Sequences (RFC 7464) plus a content-addressed artifact store, versus
  SQLite WAL plus the identical artifact store. LMDB, redb, PostgreSQL and RocksDB are challengers/conditional
  branches, not admitted to finalist ranking.
- **Pinned candidates (documentary).** SQLite 3.53.4 (2026-07-24) with published `SQLITE_SOURCE_ID` and `sqlite3.c`
  SHA3-256; 3.51.3 (2026-03-13) records the WAL reset fix; 3.51.2 (2026-01-09) is the historical negative control; RFC
  7464 (February 2015) supplies framing only. LMDB 1.0.1 (2026-08-06) is superseded by 1.0.2 (2026-09-08) — preserve
  1.0.1, do not silently substitute. redb 4.3.0 (September 2026, release-linked commit `2de02fa`); PostgreSQL 18.6
  (2026-08-13) is conditional on multi-node G06; RocksDB has no supplied version. Source hashes are not
  download-archive hashes; wrapper, CAS, JSON baseline, manifests and regression fixture bytes are unverified.
- **Shared semantic contract.** FU02 imports FU03's candidate `CAND-RCV1-20261001`: identity is aggregate_id +
  canonical ordinal + event_digest; genesis is ordinal 0; the first committed event is ordinal 1 with a 32-zero-byte
  previous-event digest sentinel; the digest is `D(type,x) = SHA256("RCV1/" + type + 0x00 + u16be schema epoch 1 +
  u64be canonical length + canonical CBOR(x))`. The 18 FU03 refusal codes (0–17) apply; uncertain commit, I/O failure
  and recovery quarantine are adapter outcomes, not semantic codes. Engine error text never enters canonical equality.
- **Commit unit, CAS and fencing.** Validate, recognize duplicates, revalidate admission, prepare and flush artifacts,
  publish final names, make directory changes durable, reacquire the mutation boundary, recheck authority and high
  water, atomically commit events/state/receipt/reference set/outbox, satisfy the engine barrier, then acknowledge. An
  in-flight CAS retention pin must survive or reconcile after a crash; no cross-filesystem atomic rename exists. The
  strong promise: every witnessed durable acknowledgement recovers as exactly one receipt with the same group, state
  and outbox changes and digest-matching artifacts; an unacknowledged command stays uncertain and may not be erased. A
  database lock, `BEGIN IMMEDIATE`, OS lock or `SQLITE_BUSY` describes contention, not authority; without atomic
  fencing, stale-writer exclusion stays unverified.
- **SQL1 profile (proposed).** SQLite 3.53.4; `journal_mode=WAL` verified on open; `synchronous=FULL` read back as 2
  on every writable connection; `wal_autocheckpoint=0`; CP1 requests PASSIVE after every committed group and drains to
  TRUNCATE at preregistered points; `busy_timeout=0` with no hidden retry; one database, `BEGIN IMMEDIATE`,
  conditional authority/high-water check, all event/state/receipt/outbox/reference changes, then COMMIT; explicit
  `unix`/`win32` VFS. No no-lock VFS, silent NORMAL/OFF, unrelated ATTACH, or unsafe immutable URI on a live store.
- **JS1 profile (proposed).** RFC 7464 sequences (RS + complete JSON text + LF); exact canonical bytes as an opaque
  field; short-write completion loop; an ordered group commit record binding lengths, counts, identities and digests;
  fsync on the active segment before acknowledgement (fdatasync only as a separately qualified JS1D arm); temp-file
  create/fsync/publish-final/fsync parent; manifest via same-directory temp file, fsync, atomic replacement, parent
  fsync; rotation seals and syncs the old segment before new groups; one admitted mutation gate with epoch/high-water
  recheck; indexes are rebuildable accelerators only. RFC 7464 is framing, not transactions or ordering; a digest is
  not a fencing token or rollback protection.
- **Acceptance oracles.** O1 replay parity (ordered `(aggregate_id, ordinal, event_digest)`, exact bytes and group
  boundaries, chain, schema epoch, command binding, authority transition, reference reducer, state bytes at every
  group boundary) is three-way: finalist A = finalist B = independently reviewed normative corpus. O2 suspends a
  writer, durably commits a higher epoch, resumes it and requires the exact stale refusal and no mutation. O3 requires
  exact receipt reuse, `COMMAND_CONFLICT` on changed bytes, and reconstructibility from the committed record. O4
  verifies artifact existence, length and digest at the O1 high water including GC and backup pins. O5 verifies engine
  structure, framing, metadata and repeatable recovery. `integrity_check` is diagnostic, not an O1–O4 replacement.
- **Fault matrix (proposed).** Cutpoints P00–P19 run from before admission through recovery; cells F01–F42 cover
  no-fault controls, process/guest/host reset, physical power interruption, short/zero/torn writes, dropped/reordered
  writes, flush lies, ENOSPC/EIO, name publication, JSON tail and interior corruption, manifest ambiguity, SQLite WAL
  matching/missing/stale/mismatched cases, checkpoint starvation, WAL reset regression, writer epoch races, duplicate
  reuse, CAS closure, GC races, backup/restore interruption, rollback and compound failures. Failure domains have no
  implication ladder: a process kill does not test OS cache loss, a guest reset does not test host or drive caches.
  The 3.51.2 control must expose the historical WAL-reset failure and the 3.51.3/3.53.4 pins must avoid it under the
  same oracle, or sensitivity is unproven.
- **Platform, measurement, backup, gates.** Standard SQLite WAL is documented as unsuitable for network filesystems,
  and selected SMB/NFS passes do not override that. Native Windows flush/replace APIs do not establish POSIX
  directory-fsync equivalence, so win32 VFS and JSON publication adapters need separate inspection and native fault
  evidence. Results bind OS/kernel, architecture, filesystem/mount options, VFS, device/firmware, cache/power-loss
  configuration, virtualization and topology. A frozen synthetic corpus is part of the workload; metrics carry
  explicit denominators; the all-bytes rule counts DB, WAL, SHM, temp, checkpoints, backups, CAS, quarantine and
  metadata as logical and allocated bytes separately. Paired order, open-loop load, clustered bootstrap intervals and
  `1 − α^(1/n)` are proposed; sample sizes and minimum meaningful difference are preregistration fields. A snapshot is
  a coherent cut with a bound artifact set and candidate-neutral manifest; restore into an isolated destination,
  verify digests and high water before mutation, rebuild projections and reacquire authority before dispatch. Gates
  A–D order the work: A evidence readiness, B correctness (O1–O5, no unauthorized writer, no dangling acknowledged
  artifact), C privacy/operability, D resource comparison. A fast store that cannot be safely restored does not reach
  ranking.

## Recommendation and falsifier

If any Owner input, normative corpus, sensitivity control or required platform cell is missing, recommend **no
selection** and name the blockers. If both finalists fail a hard floor, recommend neither and repair the shared
contract or implementation before a new freeze. If only one passes, report conditional eligibility for the qualified
profiles without bypassing Owner budgets. If both pass, SQLite may be recommended over the baseline only when it
satisfies the predeclared definition of "beats the baseline" on approved objectives with uncertainty resolved and no
hard floor or budget regression; ties, conflicts, workload-specific results or underpowered evidence recommend keeping
the baseline for comparison. Decisive falsifiers are per option: a witnessed acknowledged complete group lost, altered
or made unreachable after an in-scope fault (JS1); a valid WAL-reset or checkpoint/crash trace losing or changing
acknowledged canonical data, or permitting stale mutation (SQL1); an admitted strong-profile acknowledgement
disappearing after a declared fault (LMDB); a commit/repair/reopen sequence silently changing canonical history
(redb); a required LSM correctness/retention/compaction fault breaking O1–O5 (RocksDB); partition or promotion
creating two admitted writers or losing ACK beyond the approved bound (PostgreSQL/replicated authority). Replication
cannot make external side effects exactly once, and a commit replicated without its artifact closure is still
incomplete. The Owner makes the final store and durability decision after independent review.

## Local execution handoff

The report explicitly proposes, but does not run, the experiment. Owner inputs required before execution (its section
13) are: the durability promise (failure domains, tolerated acknowledged loss, post-corruption behavior); G06
single-host versus multi-node authority, epoch takeover and fencing; the semantic freeze (approved FU03
schema/digest/refusal rules and corpus); batching (maximum batch count and delay, per-command versus group ACK); exact
filesystem targets; workload and budgets; backup RPO/RTO/retention/snapshot frequency; key and privacy scope;
read-observer maximum age; command-identity retention; experimental precision; and the authorized local rig including
physical power/network fault approval and an independent ACK witness. The local sequence is L01–L12: freeze Owner
decisions; resolve exact pins and the verified WAL-reset fixture; freeze the semantic corpus; qualify platform
premises with FU04 fixtures; audit the common commit path against P00–P19; validate the injector and independent
witness with no-fault controls; run sensitivity controls; run the deterministic F01–F42 matrix; run native reset and
physical power cells on approved isolated equipment; run backup/restore; run the resource comparison only after
correctness readiness; and evaluate with a reviewer separate from the implementer. Stop immediately on unintended
target access, non-synthetic data, mismatched artifact hashes, unapproved power/network mutation, a correctness
counterexample, witness loss or an unclosed authority ambiguity — preserve evidence before repair. A completed local
run answers only its frozen workload, profile and failure domain.

## What this does not prove

It does not prove either finalist is correct, durable, fast, space-efficient or Windows-ready, nor that SQLite's
release fix proves wrapper/VFS/CAS correctness, nor that JSON framing alone provides transactions or network
durability. Release identity is not platform qualification. A process-kill pass is not a power-loss pass; a database
writer lock is not an authority lease; a clean database open is not a witness match. No CVE or security-cleanliness
claim is made — checking one corruption fix is not a security review. Upstream simulated I/O and crash tests justify
fault categories and negative controls, not a claim that Recursion's wrapper, CAS, Windows machine or power hardware
has been tested. The exact upstream regression fixture filename and hash were not resolved during research, so
negative-control sensitivity remains unverified until L07.

## Open Owner decisions

The durability promise and required failure domains; G06 single-host versus multi-node authority, epoch
takeover/fencing and refusal when authority is unavailable; acceptance of the FU03 semantic schema, digest and refusal
rules and literal corpus; batching semantics and per-command versus group acknowledgement; exact native
Linux/Windows/WSL/network profiles and excluded deployment paths; representative workload strata/weights and
latency/throughput/space/memory/maintenance budgets; backup RPO/RTO/retention/snapshot frequency and disaster domain;
per-goal/user/store key scope and encryption/privacy policy including CAS equality leakage; read-observer maximum age
and backpressure; command-identity retention and restored-history reconciliation; experimental precision and
exclusion/watchdog policy; and the authorized isolated rig with independent ACK witness and reviewer.

## Relevance to later waves

FU02 consumes FU04's qualified platform profiles and result contract and FU03's accepted corpus and refusal registry,
so downstream admission stays held until those prerequisite artifacts are pinned. Its outputs feed the
durability/availability decision, the canonical replay and backup/restore lanes, the adapter and broker work that
persists admitted commands, and any future multi-node branch under G06. The shared CAS and semantic contract are
deliberately common across both finalists, so later waves must treat the JSON baseline as a live diagnostic comparison
— not an unqualified production default — until the local matrix and independent review complete.
