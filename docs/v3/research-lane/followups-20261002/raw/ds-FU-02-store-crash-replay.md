---
title: Canonical state store crash and replay benchmark
source-prompt: FU-02 — canonical store crash/replay
session: Codex Dot follow-up research — specification only, target experiments NOT run
retrieved: 2026-10-02
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; target experiments not run
---

# Canonical state store crash and replay benchmark

FU02 research findings and preregistered acceptance specification

Evidence review 1 October 2026 | Report completed 2 October 2026 | Owner decision pending

## 1 Findings and disposition

No storage engine is selected. The two finalists remain segmented append only JSON Text Sequences plus a content addressed artifact store, and SQLite WAL plus the identical artifact store. This report defines the comparison, failure observables, rejection conditions and evidence needed for an Owner recommendation. It does not certify a version, run an experiment, create a database or decide the durability and availability contract.

The decisive finding is that logical correctness must be tested across the whole commit unit: admitted authority, canonical events, state, command receipt, effect outbox and referenced immutable artifacts. A successful database commit alone cannot certify the external artifact set, stale writer exclusion or exactly once external effects. Equal rendered output cannot substitute for equal ordinal event identities and canonical state.

The named SQLite 3.53.4 pin is documented by its official release record. SQLite 3.51.3 documents the WAL reset fix, and 3.51.2 is an appropriate historical negative control. Release identity is not platform qualification. The wrapper, CAS implementation, JSON sequence baseline, build manifests and regression fixture bytes remain unverified. [S01–S03]

The strongest proposed local profile acknowledges only after all referenced artifact content and required names, plus the canonical transaction, have crossed the declared persistence boundary. Whether that boundary survives a process crash, guest reset, host reset or physical power interruption must be qualified separately. A process kill does not test loss of operating system caches. A virtual machine reset does not test loss of host or drive caches.

Standard SQLite WAL is documented as unsuitable for network filesystems. Passing selected SMB or NFS tests does not override that documented boundary. A different supported VFS or local authority service would be a separately pinned candidate requiring a new preregistration. JSON sequence storage likewise gains no network guarantee from framing or rename alone. [S04, S12]

All performance, space, memory, recovery and power interruption outcomes are unknown. They are not zero and not passes. The current recommendation is to retain both finalists for evidence collection, preserve the JSON baseline as the comparison reference, and withhold a product selection until the Owner inputs and hard gates below are complete. Retaining the baseline for comparison does not assert that an unqualified baseline is safe for production.

## 2 Authority and evidence rules

The latest Owner clarification supersedes the handoff’s historical Hermes description: Hermes is retired, and v3 is a standalone harness that both executes natively and wraps or orchestrates other harnesses. Lucas remains final Owner; workers remain bounded executors. An implementer’s own PASS is not acceptance. No protected constitution is amended by this report. The supplied handoff, README and current Owner clarification provide the product context; no private repository or connector evidence has been assumed. Any legacy milestone or migration language is historical context, not a revived v2 control plane. Public research queries used only public technical subjects. Work on this report is limited to source research, a proposed specification and document preparation.

Evidence classes are source documented, locally observed, inferred and unverified. Source documented means an identified primary source states the claim. Inferred includes the proposed design, test oracle and reasoning derived from those facts; it does not mean measured success. Locally observed is reserved here for document generation and inspection, never storage behavior. Unverified means no qualifying evidence was obtained. Confidence describes support for the stated claim, not a numerical reliability estimate.

Immutable standards and release records are pinned where possible. Live documentation is date bounded, not falsely presented as immutable source. Local execution must archive exact relevant source bytes and hashes before its freeze. A change to engine, wrapper, compiler, build flags, filesystem, VFS, OS build, firmware, storage topology, contract, schema, corpus or injector invalidates the affected qualification. No claim of a clean CVE posture is made. Checking release notes for one corruption fix is not a security review.

## 3 Pins and prerequisite contracts

### 3.1 Engine and baseline pins

| Component | Verified public pin | What remains unverified |
|---|---|---|
| SQLite finalist | 3.53.4 released 2026-07-24; source ID and amalgamation digest below | Local artifact, compile options, link mode, wrapper, VFS behavior and every experiment |
| SQLite fix reference | 3.51.3 released 2026-03-13; release explicitly records WAL reset fix | Exact local regression fixture, build and result |
| SQLite negative control | 3.51.2 released 2026-01-09 | Ability of the approved injector to trigger the specific historical fault |
| JSON sequence baseline | RFC 7464, February 2015, framing standard | Baseline implementation commit, serializer, frame schema, group footer, indexes, CAS, runtime and build digest |
| LMDB challenger | Official announcement validates 1.0.1, 2026-08-06 | Source artifact hash and full challenger profile; not admitted to finalist ranking |
| redb challenger | Official v4.3.0 release, September 2026; release page points to 2de02fa | Complete immutable build pin and Recursion results |
| PostgreSQL conditional branch | Official 18.6 release notes, 2026-08-13 | Replication manager, topology, quorum, authority, build and workload qualification |
| RocksDB conditional branch | No version supplied or selected | Exact version, LSM requirement and complete profile |

SQLite 3.53.4 SQLITE_SOURCE_ID is 2026-07-24 19:02:57 bf7c7f30031888f4e796e429ab3978879485813aaca6f641c7b33e4e09459bcc. Its published sqlite3.c SHA3-256 is 67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16. [S01]

SQLite 3.51.3 SQLITE_SOURCE_ID is 2026-03-13 10:38:09 737ae4a34738ffa0c3ff7f9bb18df914dd1cad163f28fd6b6e114a344fe6d618. Its published sqlite3.c SHA3-256 is 32d5424f97e0a7fc5ed2f6335afbb58be4e0298bd7117a34e39d345ff13d859e. SQLite 3.51.2 SQLITE_SOURCE_ID is 2026-01-09 17:27:48 b270f8339eb13b504d0b2ba154ebca966b7dde08e40c3ed7d559749818cb2075; its sqlite3.c SHA3-256 is 733b3fcc6cccb1e334424b9b91a9d68b618385b76ebfcbb106690bd3a9e61367. These are source hashes, not claimed download archive hashes. [S02, S03]

LMDB 1.0.1 is a historical nominated pin, not the newest release at the handoff’s freeze. The official project also announced 1.0.2 on 2026-09-08, including a Windows WRITEMAP correction. Preserve 1.0.1 in the record; do not silently substitute 1.0.2. If LMDB is admitted later, the Owner must explicitly approve the rebaseline and relevant Windows regression review. redb 4.3.0 documents crash recovery, storage error and Windows zero write fixes; that makes those scenarios useful challenger controls, not evidence that this workload passes. [S24–S26]

### 3.2 Shared semantic contract

FU03 supplies the candidate completion CAND-RCV1-20261001. It is a proposed corpus interface, not recovered accepted product wire semantics. FU02 imports its identity, duplicate, digest and refusal rules rather than independently inventing incompatible ones. Execution is blocked until an Owner approved semantic schema, independently reviewed literal corpus, manifest SHA-256 and executable oracle pins exist.

The candidate identity is aggregate_id plus canonical ordinal plus event_digest. The genesis state has ordinal 0. The first committed event has ordinal 1 and a 32 zero byte previous-event digest sentinel. The genesis state digest is computed from canonical genesis state and is distinct from that zero event-tail sentinel. Event bodies contain schema epoch, aggregate ID, ordinal, previous digest, command digest, event kind, payload and writer epoch. The stored digest is excluded from its own preimage. A receipt contains command digest, ordinal interval, final event digest, result class and result bytes; it contains no post-state digest or pointer back to state. The state digest can therefore include the canonical receipt index without self-reference, as specified by FU03. The shared digest construction is D(type,x) = SHA256(ASCII("RCV1/") followed by ASCII(type), one zero byte, u16be schema epoch 1, u64be canonical byte length, and canonical CBOR(x)). The shared type domains include event, state, command, packet and the separately derived projection domain. FU03’s restricted canonical CBOR profile, not generic JSON rendering, determines semantic bytes.

For JSON sequence persistence, a proposed physical envelope carries those canonical bytes as an opaque encoded field. JSON field order, whitespace or number parsing must never reconstruct a different semantic event. RFC 7464 governs the outer RS and LF framing only. A JSONL variant, if retained, is a separately versioned framing profile and must face the same corruption corpus; it is not silently equivalent to RFC 7464. JCS canonicalization used elsewhere in the fabric is a different layer. Neither a broker JCS envelope nor an RCV1 test frame is automatically the persistence format. [S10, S11]

Candidate refusal codes inherited from FU03 include MALFORMED, NONCANONICAL, UNSUPPORTED_SCHEMA, UNKNOWN_KIND, FIELD_INVALID, COMMAND_CONFLICT, EXPECTED_STATE_MISMATCH, AUTHORITY_DENIED, GOAL_EPOCH_STALE, PLAN_REVISION_STALE, LEASE_EPOCH_STALE, PAUSED, PAUSE_EPOCH_STALE, ATTEMPT_INVALID, CANCELLED, EFFECT_UNSAFE, VERIFIER_INVALID and CHAIN_MISMATCH. Storage outcomes such as uncertain commit, I/O failure and recovery quarantine are adapter or harness outcomes, not extra semantic refusal codes. Diagnostic strings and engine error text never enter canonical equality.

### 3.3 Shared platform result contract

FU04’s result key is profile_key plus fixture_id and version, variant_id, cutpoint, failure_domain and contract_digest. The profile key is null until exact identity pins are supplied; unknown fields cannot be hashed into a fictional verified machine. Qualification values are qualified, rejected and unknown; unknown is displayed as Unqualified. The candidate qualified identity requires FU04’s Owner approved and independently reviewed JCS identity projection and the prefix fu04-p1:sha256:; FU02 does not independently redefine that projection. Upstream harness product, version, configuration digest and delegated-work boundary are included when execution is delegated.

Failure domains remain distinct: process_crash, guest_reset, host_reset, physical_power_loss, network_partition and server_restart. There is no automatic implication ladder. Every storage result binds OS and kernel build, architecture, filesystem and mount options, VFS, storage device and firmware, cache and power loss protection configuration, virtualization, protocol/client/server versions when applicable, and the exact local or network topology. FU04 evidence supplies platform premises; FU02 still must test the integrated store and CAS.

## 4 Candidate neutral durability and authority

### 4.1 Proposed strong local promise

For an explicitly qualified local profile and declared failure domain, every command for which the independent client witness records a durable acknowledgement must recover with exactly one committed receipt and the same complete event group, state and outbox changes, with every referenced immutable artifact available and matching its content digest. No partial group, unauthorized mutation, ordinal gap, silently altered event or false acknowledgement is permitted.

An unacknowledged command may be absent or may have committed in full. Its outcome is uncertain until reconciliation. Successful recovery cannot merely erase it to make the observed history look cleaner. Returned refusals that precede any durable mutation must leave the canonical state unchanged. A failure after possible mutation cannot be reclassified as a definite refusal without evidence.

This is a proposed test contract awaiting the Owner’s durability choice. It is not a guarantee against arbitrary media destruction, malicious raw disk writes, lying hardware, compromised keys or every undiscovered software bug. For injected faults outside the selected storage model, detecting damage and refusing unsafe continuation is the expected safety result; that is not the same as successful availability or recovery within RTO.

### 4.2 Common commit unit and CAS ordering

Both finalists use the same pinned CAS implementation, digest algorithm, object sizes, encryption and compression choices, permissions, key scope and garbage collection policy. Sharing an artifact implementation controls a major confounder, but it also creates a common mode failure. The CAS must therefore be tested independently of each engine as well as through both.

Proposed ordering is: validate the command; recognize an already committed duplicate; validate current admission; prepare immutable artifacts; verify their length and digest; flush their bytes; publish each final name on the same filesystem; make required directory changes durable; reacquire the canonical mutation serialization boundary; recheck authority and expected high water; atomically commit events, state transition, receipt, reference set and outbox; satisfy the engine persistence boundary; only then acknowledge.

Before object publication, establish an in flight CAS retention pin that survives or can be reconciled after a crash. Hold it until the canonical reference commits or a definite abort is established; uncertainty retains the pin. A grace period alone is insufficient when a writer can pause longer than that period. An existing object at the content address must be verified for length and digest before reuse. CAS objects may become durable without a referring command. They are orphans, not committed work. A committed command may never depend on an unflushed temporary object or on a future rename. Cleanup cannot delete objects reachable from current canonical state, retained event history, a retained snapshot or an in progress backup pin. An orphan grace period and reachability generation are Owner controlled retention parameters; no arbitrary time budget is invented here.

For separate filesystems, flushes and publication must complete on each before the canonical reference commits. There is no cross-filesystem atomic rename and no inferred transaction across two volumes. An interruption can leave orphans, but cannot justify acknowledging a dangling reference. If the required names cannot be made durable on a profile, the strong profile stays unqualified.

### 4.3 Fencing must linearize with mutation

Admission checks reject unauthorized work before expensive preparation. At the durable mutation boundary, the implementation must compare the admitted writer epoch and the expected canonical high water or digest against the current authoritative values under the same serialization boundary as commit. Authority takeover must itself linearize in that authority mechanism. A check followed by an unfenced write is a time of check race.

A database lock, successful BEGIN IMMEDIATE, operating system lock or SQLITE_BUSY result only describes serialization or contention. It does not prove that the holder’s epoch remains authorized. If an external lease service can revoke authority without atomically fencing the store, a second local check still does not close the race. That architecture requires an Owner approved fencing protocol or a narrower single host authority contract; until then stale writer exclusion is unverified.

The JSON adapter needs a single admitted mutation gate shared by every process that can modify canonical files, with revalidation under its serialization lock. The SQLite adapter needs the equivalent conditional authority/high water mutation inside its transaction. A process with unrestricted raw write access can bypass either adapter; operating system isolation and the threat model must state whether that adversary is excluded or separately controlled.

## 5 Exact finalist profiles

The following values are proposed experiment settings, not commands executed in this session. An explicit unverified field blocks the run; it is not permission to use a platform default.

### 5.1 SQLite WAL profile SQL1

| Setting or component | Required value or rule |
|---|---|
| Engine | SQLite 3.53.4, source identity in section 3; local artifact hash must match approved build manifest |
| Journal | PRAGMA journal_mode=WAL; returned value must be wal; check on every database open |
| Synchronization | PRAGMA synchronous=FULL, read back numeric 2 on every writable connection, including maintenance connections |
| Automatic checkpoint | PRAGMA wal_autocheckpoint=0 on each writer connection |
| Checkpoint algorithm CP1 | One coordinator requests PASSIVE after every committed group; coalesce pending requests; record return status, log frames and checkpointed frames |
| Checkpoint completion | At each preregistered drain, pause new admissions, finish or revoke observers under approved age rule, then TRUNCATE; require success and verified drain or record incomplete maintenance |
| Busy behavior | sqlite3_busy_timeout(connection,0), no engine busy callback; surface contention to the common harness; no hidden transaction retry |
| Transaction | One database, BEGIN IMMEDIATE, conditional authority/high water check, all events/state/receipt/outbox/reference index changes, then COMMIT |
| VFS | Explicit unix on native Linux profile; explicit win32 on native Windows profile; exact source, runtime selection and injected shim stack recorded |
| Prohibited substitutions | No no-lock VFS, no silent NORMAL/OFF synchronous, no unrelated ATTACHed canonical state, no unsafe immutable URI on a live mutable store |
| Observer settings | Read only or query_only observers, consistent snapshot per read, bounded age from Owner; no observer authority inferred |
| Schema and indexes | Version and DDL digest unverified; primary identities and unique command binding mandatory, indexes not semantic authority. Set foreign_keys=ON before transactions and read back 1 on every connection when using declared foreign keys |
| Remaining build knobs | Wrapper/version/hash, compile options, page size, cache size, mmap size, temp storage and encryption profile must be pinned and recorded before execution |

FULL in WAL mode adds a commit sync; it does not remove the need to verify the VFS and storage stack. PASSIVE may be incomplete, and TRUNCATE may wait or fail through contention. CP1 deliberately exposes maintenance costs instead of hiding them in an unspecified default. CP1 is a proposed benchmark policy, not a claim of optimal checkpoint frequency. An alternate CP2 policy may be a separately preregistered arm, never a post hoc tuning advantage. [S04–S08]

Keep one database connection live during an append window so close time cleanup does not silently replace the chosen checkpoint policy. Include shutdown and final checkpoint costs in a separately measured drain and in end to end throughput. Log all result and extended result codes. If a COMMIT error leaves transaction status or durability uncertain, stop admissions and reconcile from recovered canonical state. Do not translate an I/O error into a definitely absent command. [S07, S08]

### 5.2 Segmented JSON sequence profile JS1

| Setting or component | Required value or rule |
|---|---|
| Framing | RFC 7464 UTF-8 JSON Text Sequences, each physical record RS then complete JSON text then LF |
| Semantic payload | Exact canonical bytes from the shared corpus, opaque encoded field; serializer and encoding profile pinned, currently unverified |
| Complete frame write | Loop over positive short writes until all bytes written; explicit handling for interrupted calls; zero progress or error is failure, never successful append |
| Transaction group | Ordered event records plus receipt/state/outbox/reference metadata and a final group commit record binding lengths, counts, identities and digests |
| Replay acceptance | Only contiguous complete groups passing all checks; no RFC resynchronization that silently skips a malformed interior canonical record |
| Data durability | fsync on the active segment after the complete group commit record before acknowledgement; fdatasync permitted only as separately qualified JS1D arm |
| Segment publication | Create temporary file on target filesystem, initialize and fsync it, publish final name, fsync required parent directory entries before use |
| Manifest publication | Write complete next manifest to temporary same-directory file, fsync it, atomic same-filesystem replacement, fsync parent; preserve recoverable predecessor until publication established |
| Rotation | Seal and sync old segment, durably publish new empty segment, publish manifest binding old tail and new segment, then admit new groups |
| Indexes | Rebuildable accelerators only; corrupt or missing indexes must not change canonical replay |
| Writer control | One admitted mutation gate, epoch/high water recheck while serialized; OS lock alone is insufficient |
| Windows mapping | File flush and publication adapter must be pinned and pass FU04; POSIX directory sync cannot be assumed; strong Windows publication remains unverified |
| Remaining pins | Baseline commit/build, physical frame/group schema, CRC choice if any, manifest encoding, segment threshold and runtime unverified |

RFC 7464 is framing, not transactions, checksums or ordering. The added group and manifest rules are this report’s candidate design. A cryptographic digest helps detect changed content but is not a fencing token, authenticated history or rollback protection by itself. A CRC, if chosen, is a corruption detector with a separate polynomial and byte coverage pin; neither CRC nor digest prevents a writer from replacing an entire unauthenticated history. [S10, S28]

The active segment must already be durably named by the manifest before its first acknowledged append. A complete unacknowledged terminal group may survive and must be reconciled. A partial terminal group can be ignored or quarantined only when the agreed recovery rule proves that it is beyond the committed high water. Interior corruption, unexplained sequence gaps, altered groups or missing acknowledged data require quarantine, not skip-and-continue.

The manifest is a locator and generation boundary, not permission to delete otherwise acknowledged history. Recovery validates its generation, segment names, chain and high water against preserved evidence. If both old and new manifests are plausible but disagree and no approved rule distinguishes them, recovery remains uncertain. It must not pick the newest timestamp. Filesystem timestamps are not authority.

### 5.3 Equivalence and controlled differences

Both arms must share command order, canonical bytes, batching semantics, artifact set, authority checks, observer ages, workload seeds, acknowledgement definition, backup retention and target failure domain. Engine specific representations and recovery machinery may differ. For v3 native execution and orchestration of upstream harnesses, normalize the admitted command and evidence into the same canonical contract before persistence. Upstream completion text or process exit is not an authoritative durable receipt. Bind upstream run identity to the canonical command identity, record the adapter version, and exercise redelivery, conflicting reuse and stale completion through F28–F32; an upstream retry must not create a second mutation. Neither arm may gain performance by acknowledging before the shared barrier, omitting receipt/outbox work, leaving CAS durability to later, or excluding maintenance and temporary files from accounting.

SQLite stores exact canonical bytes in BLOB fields and separately indexed metadata; SQL type coercion must not change digest input. JS1 stores the same bytes in an envelope and verifies its decoded length. Physical bytes need not match across engines. Canonical identity, command result and reducer state must match exactly. A schema or serialization migration requires a new versioned comparison, not a cosmetic projection equivalence.

## 6 Acceptance oracles

### 6.1 O1 Replay parity

For each recovered aggregate, extract the ordered sequence of (aggregate_id, ordinal, event_digest), the exact canonical event bytes and group boundaries. Validate the previous digest chain, schema epoch, command binding and authority transition. Replay with an independently pinned reference reducer from the approved genesis or checkpoint. Compare canonical state bytes and digest at every committed group boundary, not just the final state. Separately compare each projection’s version, high water and projection digest.

The oracle is three way: finalist A equals finalist B equals the independently reviewed normative corpus. Neither finalist’s output becomes expected output by convenience. Equal final state can hide a missing event later cancelled by another event; equal projection can hide a corrupt receipt or authority epoch. Both are insufficient.

An independent acknowledgement witness records command identity, returned receipt bytes, group high water, timing and durability class outside the fault domain. Recovered state must contain all witnessed acknowledged groups in canonical order. An unacknowledged suffix may contain full groups, but no invented command and no partial group. If witness durability or clock association is uncertain, the run is inconclusive, not evidence of either loss or safety.

### 6.2 O2 Stale writer exclusion

Suspend writer W at each cutpoint after admission. Establish and durably commit a higher authority epoch through the approved authority mechanism; then resume W. For a new command from W, require the exact inherited authority or stale epoch refusal and no canonical mutation. Run the variant where W reacquires a free database or file lock, proving that lock ownership does not confer authority. Run another where takeover races the mutation boundary; the committed history must identify exactly one permitted linearization.

Returning an already committed exact duplicate receipt is allowed before current epoch checks under FU03. That is reuse, not new mutation. Any fresh effect dispatch must revalidate its effect boundary epochs. If a takeover cannot be serialized with the commit boundary, mark the authority contract blocked rather than fabricating a passing stale writer test.

### 6.3 O3 Duplicate command reuse and uncertainty

The same command ID and same canonical command digest must return the exact committed receipt, produce no new event or outbox item and not repeat an external effect. The same ID with different canonical bytes must return COMMAND_CONFLICT. A receipt cache lost in a crash must be reconstructible from the authoritative committed record; process memory is not enough.

Test duplicates before execution, during the in flight command, after commit before acknowledgement, after acknowledgement, after restart, after authority change and after restore. The lookup scope and retention period are Owner inputs. If a restored backup predates a command receipt, a downstream external effect may already have happened; absence from the restored store is not proof that it never happened.

For an uncertain commit, stop dependent dispatch and reconcile command_id plus digest against the recovered authoritative chain. A verified committed receipt returns reuse. A verified absence under an unambiguous recovered high water can allow controlled re-admission of that command under the approved policy. Conflicting digests, missing evidence, unreadable storage or unknown external effect disposition require quarantine or manual reconciliation. A timeout, connection loss or I/O error never authorizes blind external retry.

### 6.4 O4 Artifact closure and O5 recovery integrity

O4 verifies every referenced immutable object’s existence, exact length and content digest at the same checkpoint/high water used by O1. It also verifies that garbage collection and backup pins preserve the object until no retained root requires it. Unreferenced objects are counted and may be reclaimed only under the approved policy.

O5 verifies engine structure, physical group framing, metadata generation and replay integrity. SQLite integrity_check and foreign_key_check where applicable are diagnostic inputs, not replacements for O1–O4. A structurally valid database can contain the wrong canonical history; a valid JSON document can be the wrong event. Recovery must be repeatable: two recovery attempts over preserved identical evidence produce the same classification and canonical result, without hidden destructive repair on the only copy. [S05, S19]

## 7 Preregistered crash and fault matrix

Every cell is expanded for both finalists unless marked engine specific, at every applicable cutpoint below, under each requested FU04 profile and declared failure domain. A cell ID includes candidate/profile/fixture/version/variant/cutpoint/failure domain/seed/replicate/contract digest. The manifest explicitly enumerates expansions before execution. Missing, unsupported and not applicable cells have reasons; none count as passes.

### 7.1 Mutation and maintenance cutpoints

| ID | Boundary |
|---|---|
| P00 | Before admission and duplicate lookup |
| P01 | After admission, before artifact preparation |
| P02 | During CAS temporary creation or partial data write |
| P03 | After CAS data write, before content flush |
| P04 | After content flush, before final object publication |
| P05 | After object publication, before directory durability |
| P06 | After complete durable artifact closure, before mutation lock |
| P07 | After mutation lock, before authority/high water recheck |
| P08 | After successful recheck, before first canonical write |
| P09 | During event or row mutation, before complete group/transaction |
| P10 | After full logical mutation, before engine persistence barrier |
| P11 | During fsync or SQLite commit sync |
| P12 | After engine barrier, before acknowledgement emission |
| P13 | During acknowledgement delivery and witness recording |
| P14 | After witnessed durable acknowledgement |
| P15 | During segment sealing or WAL checkpoint page copy |
| P16 | During manifest publish or WAL reset/truncation |
| P17 | During checkpoint snapshot and backup publication |
| P18 | During CAS reclamation or retention metadata update |
| P19 | During recovery itself, including a second injected failure |

The injector must establish that it reached the named boundary. A process killed near a line of code without proof of completed I/O is not a precise fsync cutpoint. Record operation number, requested/completed bytes, offsets, sync start/end/status, rename status, lock/epoch observations and acknowledgement witness. Instrumentation must preserve the native storage semantics except for the declared injected fault.

### 7.2 Failure cells and expected observables

O1–O5 refer to section 6. “Prefix or full” below means an allowed complete unacknowledged suffix with all acknowledged groups retained; it never permits dropping acknowledged history. “Quarantine” is an explicit detected unsafe state that blocks mutation and dispatch. A quarantine may satisfy detection in an out of model cell while failing availability or the strong recovery promise in an in scope cell.

| Cell | Fault and required variants | Expected observable |
|---|---|---|
| F01 | No fault control, every operation and maintenance path | O1–O5 exact; every scheduled hook reached; no unexpected refusal |
| F02 | Abrupt process termination at P00–P19 | Recover allowed complete history; acknowledged groups retained; no claim about OS cache loss |
| F03 | Guest reset at P02–P19, guest caches discarded | Same oracle for declared guest domain; host cache survival explicitly recorded |
| F04 | Host reset at P02–P19 | Same oracle for host domain; device cache behavior not inferred |
| F05 | Actual physical power interruption at P02–P19 using approved isolated rig | Full strong promise for qualified hardware; power evidence independent; no process kill substitution |
| F06 | Positive short writes at first, middle and final byte ranges in CAS and canonical data | Correct completion loop or explicit failure; no premature ACK; O1–O5 |
| F07 | Zero byte write or repeated interrupted write at same stages | Bounded failure/cancellation under approved watchdog; no endless success loop or partial ACK |
| F08 | Torn write within frame, footer, WAL frame, page, manifest and artifact | Valid prefix/full or detected quarantine according to fault model; never silent altered history |
| F09 | Drop, reorder or duplicate unsynced writes under declared storage model | No acknowledged loss within promised model; complete groups only; record surviving unacknowledged groups |
| F10 | Flush returns error; delayed writeback error; flush interrupted | No new durable ACK; uncertain status reconciled; preserve evidence and prior acknowledged prefix |
| F11 | Flush reports success but data is lost, declared lying device variant | Detect discrepancy if observable; fail the strong platform promise; do not blame framing alone |
| F12 | ENOSPC or quota at CAS write, log/WAL growth, checkpoint, manifest, backup | No false ACK or corrupt prior history; explicit stage/error and controlled recovery after space restored |
| F13 | EIO, media read error, permissions removed or read only transition | Fail closed or recover under approved scope; no silent empty genesis or dropped command |
| F14 | Same filesystem name publish interrupted before and after directory barrier | Names/generations and data reconcile; prior acknowledged references remain reachable |
| F15 | Cross filesystem rename or Windows cross volume move attempt | Reject unsupported atomic publication; no copy/delete fallback presented as atomic |
| F16 | Windows ReplaceFile partial error states or sharing violation | Enumerate actual surviving names/content; reconcile or quarantine; no universal old-or-new assumption |
| F17 | JSON tail truncated at every framing/group boundary | Incomplete unacknowledged terminal group isolated; committed prefix exact; never skip interior corruption |
| F18 | JSON duplicate, missing, reordered or altered interior record/group | O1 chain/ordinal/group check rejects; no rendered-view-only acceptance |
| F19 | Missing/corrupt/stale JSON manifest and rebuildable index separately | Index rebuild preserves history; manifest ambiguity quarantines; no timestamp authority |
| F20 | Segment rotation P15/P16 before/after new segment and manifest publication | No split group, missing durable segment or newly acknowledged unreachable suffix |
| F21 | SQLite matching hot WAL after process crash | SQLite recovery plus O1–O5; never manually delete required WAL to make open succeed |
| F22 | SQLite missing WAL with acknowledged data not checkpointed | Detect lost high water/receipt against witness and fail; a clean database open is insufficient |
| F23 | SQLite mismatched or stale WAL from another generation or database | Canonical identity and lineage reject mispairing or quarantine; never accept wrong replay |
| F24 | SQLite absent, stale or damaged SHM with matching DB/WAL; repeat with competing opener | Engine may rebuild transient index; require O1–O5 and correct contention; no claim SHM equals durable WAL |
| F25 | SQLite recovery opener concurrent with second/third connections | Busy is surfaced and bounded; no authority inferred; eventual result measured within Owner RTO |
| F26 | SQLite checkpoint starvation from long reader, overlapping readers and maximum allowed age | History correct; WAL growth measured; approved observer age/backpressure policy enforced |
| F27 | SQLite WAL reset regression schedule and negative control | Historical control demonstrates sensitivity; patched pin passes same schedule and O1–O5; else gate fails |
| F28 | Writer epoch changes at P01/P06/P07/P08; resume stale writer with available lock | O2 rejects new stale mutation; committed exact duplicate may reuse receipt |
| F29 | Two contenders concurrently propose same ordinal or authority takeover | Exactly one valid canonical successor; loser stable refusal or reconciliation; no fork |
| F30 | Same command ID/digest repeated at every P00–P14 stage | O3 exact reuse or in flight reconciliation; no additional canonical mutation |
| F31 | Same command ID with changed body, expected digest or authority tokens | COMMAND_CONFLICT with no mutation; no redefinition of identity after crash |
| F32 | Commit succeeds but response drops, timeout occurs or client restarts | Uncertain then reconciled to original receipt; no blind new command/effect |
| F33 | CAS object missing, truncated, wrong digest or wrong encryption scope | O4 blocks acceptance/recovery; no successful canonical state with broken artifact closure |
| F34 | CAS GC races append, observer, backup and restore retention pins | No reachable object removed; orphan accounting exact; GC interruption recoverable |
| F35 | Backup interrupted during copy, flush and manifest publish | Previous complete backup remains eligible; incomplete backup never labeled restorable |
| F36 | Restore mismatched high water, schema epoch, checkpoint digest or artifact set | Reject before dispatch; exact matching snapshot restores O1–O5 |
| F37 | Crash or I/O failure during recovery and repeat recovery | Evidence preserved; deterministic result or explicit uncertainty; no cumulative silent repair |
| F38 | Network interruption, partition/heal, lost response, server restart and stale client state | Profile remains unqualified until supported architecture and full network corpus; no split authority |
| F39 | Clock rollback/jump and stale observer advertised as current | Ordinal authority unaffected; observer age proof valid or unknown; no timestamp-based winner |
| F40 | Schema/format mismatch, unknown event kind, integer/length boundary or malformed canonical payload | Exact FU03 refusal or quarantine at correct layer; no engine-specific semantic coercion |
| F41 | Rollback to older otherwise valid store and backup after external dispatch | Lineage/high water evidence detects rollback where promised; no automatic redispatch from absent receipt |
| F42 | Combined disk full or EIO while handling crash recovery or backup failure | Prior evidence retained; correct uncertain/quarantine outcome; compound failure never omitted silently |

### 7.3 WAL reset regression sensitivity

The upstream description identifies a complete checkpoint, a second checkpoint starting, a concurrent writer resetting the WAL, later writes extending it, and another checkpoint skipping data because of stale checkpoint state. The regression fixture must deliberately exercise that schedule and validate data after checkpoint and reopen. The official account distinguishes source injected triggering from an ordinary workload reproducer; merely running concurrent writes until a timer expires does not prove that the race was reached. [S04]

Local sessions must resolve the exact upstream regression file and immutable revision, review the permitted hook or reproducible schedule, and record its hash. Source access to a guessed file path did not establish a verified fixture during this research; no filename or fabricated fixture hash is certified. Require the 3.51.2 negative control to expose the intended historical failure under the declared trigger, and the 3.51.3 reference and 3.53.4 candidate to avoid it under the same oracle. If the control never triggers, mark sensitivity unproven. Do not score the candidate as safe on that basis. Historical vulnerable controls stay in disposable synthetic environments and never open real user data.

SQLite’s upstream anomaly tests describe simulated I/O and crash failures. They justify fault categories and negative controls, not a claim that Recursion’s wrapper, CAS, Windows machine or power hardware has already been tested. [S20]

## 8 Filesystem and platform qualification

Linux fsync documentation separates file content/metadata synchronization from the directory entry, which requires a directory sync. fdatasync can omit metadata not needed to retrieve content, so it is not a universal substitute for publication durability. Successful write alone does not establish persistence, and a short successful write must be handled. Linux rename is atomic in the namespace within its documented constraints, but that does not make data and directory changes power durable. Cross mounted filesystems can reject rename. [S13–S15]

On Windows, FlushFileBuffers documents flushing a specified file; that statement is not a POSIX directory fsync guarantee. ReplaceFileW documents unsupported WRITE_THROUGH and partial failure states. MoveFileEx can implement a cross volume move as copy/delete when requested, which is not the single atomic publication assumed by JS1. Therefore native Windows win32 VFS and JSON publication adapters need separate source inspection and native fault evidence. A Linux result cannot qualify their ordering, sharing flags, antivirus interference, volume metadata or drive cache behavior. [S16–S18]

WSL native Linux filesystem storage and a Windows mounted drive such as /mnt/c are separate profiles. Microsoft’s cross-filesystem guidance is performance/interoperability guidance, not a crash durability certificate. Bind WSL version, guest kernel, virtual disk, host filesystem and host storage stack. Include guest reset, host reset and physical power loss separately when requested. [S22]

For SMB/NFS, the minimum prerequisite is a supported architecture and declared ownership topology, not just a successful mount. Then enumerate protocol dialect, client/server versions, cache and lease/lock semantics, reconnect behavior, stable write/flush semantics, server persistence boundary, failover, server and client clocks, authentication scope and CAS topology. Required cells include F06–F16 and F21–F42 as applicable, plus client crash before/after server commit, server restart before/after stable ACK, partition after write but before response, lock or lease revocation, competing writers after reconnect, stale handles, delayed cached reads, server failover, directory publication and recovery of both store and CAS.

Every network experiment must retain both sides’ durable observations and independent command receipts. If the server’s ACK only means receipt in volatile memory, the strong profile is unavailable regardless of client fsync. If two clients can simultaneously believe they own the canonical writer, authority is unqualified. Standard SQLite WAL over a network filesystem remains rejected as a candidate profile under its documented constraints; qualifying a new architecture requires an explicit scope change. JSON sequence plus network CAS or logs remains unknown until the supported server contract and full integrated matrix pass. No passing sample broadens a vendor’s stated support contract. [S04, S12]

## 9 Workloads measurement and uncertainty

### 9.1 Workload freeze

The experiment manifest must freeze a synthetic command corpus with exact canonical payloads, command/event ratios, per command event count distribution, aggregate count and skew, artifact count/size distribution, duplicate fraction, changed-body conflict fraction, refusal fraction, authority turnover schedule, observer concurrency/age, snapshot frequency, checkpoint/rotation schedule, CAS reuse ratio, retention/GC schedule and warm/cold recovery conditions. These dimensions are part of the workload, not adjustable explanations after results arrive.

Include event-only, artifact-heavy, high duplicate, authority contention, long observer, sustained append plus maintenance, cold replay, checkpoint replay and restore strata. Include small and maximum allowed values, Unicode and numeric boundary corpus cases inherited from FU03. A million events is a reporting normalization, not a requirement to pretend a tiny trial is representative. Publish actual event and command counts beside every normalized number.

The Owner must supply representative weightings or explicitly choose an unweighted stratified comparison. No production mix is inferred from third-party benchmarks. Use the identical batch count B and maximum delay D for both finalists. B, D, event sizes, concurrency and memory limits remain unresolved until frozen. Constants chosen to make an injector finite are labeled harness bounds, never product capacity promises.

### 9.2 Metric definitions

| Metric | Numerator and denominator |
|---|---|
| Append service latency | Monotonic time from admitted command entering store transaction path to durable receipt ready; one sample per distinct committed command |
| End to end command latency | Client scheduled arrival to received durable ACK; includes admission queue, batching, CAS and contention; one sample per attempted command, with outcome |
| Group commit latency | First member arrival and final member arrival to group durability reported separately; one sample per physical commit group |
| Event throughput | Newly committed canonical events divided by wall seconds including scheduled maintenance and final drain; duplicates do not add events |
| Command throughput | Distinct durable command receipts divided by same wall seconds; attempted, refused, reused and uncertain commands shown separately |
| Replay time | Cold or warm start until O1/O4 validated canonical high water and requested projections ready; seconds per actual event count and per million replayed events |
| Recovery time | Failure detection or explicitly defined restart start to safe serving eligibility; report engine reopen, validation, CAS closure and projection rebuild separately |
| Restore RTO | Declared disaster start to validated restored service; includes locating backup, transfer, decryption, validation, replay and authority reestablishment |
| RPO | Missing acknowledged groups/events and elapsed witness time between latest acknowledged and restored valid high water; never inferred only from file timestamps |
| Live retained bytes | Logical lengths and allocated bytes for all live store files, sidecars, CAS and required metadata at exact high water; bytes per actual unique event |
| Peak and maintenance bytes | Peak simultaneous allocated bytes including temp/backup staging/compaction/quarantine; bytes per same committed event denominator |
| Growth | Change in logical and allocated WAL/log plus total store/CAS bytes divided by newly committed events in measured interval; negative changes shown honestly |
| Write amplification | OS/device bytes written divided by canonical payload plus newly materialized artifact bytes; layer and counter scope explicitly named |
| Memory | Peak and time weighted RSS per process, PSS where supported, and process tree totals; report absolute bytes and bytes per million committed events at stated N |
| CPU and recovery work | CPU seconds and bytes scanned divided by actual commands/events/replayed bytes; include CAS and maintenance processes |
| Failure rates | Violations, inconclusive, blocked and successful recoveries divided by attempted injected trials, separately for every stratum |

RSS per million events is a normalized observation at N, not an assertion of linear memory growth. Shared memory may be counted twice when RSS is summed, so report process sum and proportional/shared accounting separately. OS page cache, memory mapped residency and device cache are not magically absent because they are outside one process’s RSS. A refused or timed out command is not removed from latency reporting to improve the tail.

### 9.3 All bytes rule

For SQLite include main database, WAL, SHM, rollback or temporary journals if created, temporary sort/storage files, checkpoint/backup outputs, schema/index overhead, receipt/outbox/reference tables and diagnostics required to operate safely. For JS1 include active and sealed segments, manifests and retained predecessors, indexes, temporary files, checkpoints, backup copies, corruption quarantine and reclamation metadata. For both include all CAS objects, directories and object metadata where measurable, orphan and temporary objects, encryption/compression overhead, retained backups and manifests.

Report logical bytes and filesystem allocated bytes independently. Count a shared physical object once in the deployment total, while disclosing per-root logical references; do not subtract deduplicated objects twice. Hard links, reflinks, sparse files and compression make naive file size sums misleading. If underlying physical allocation cannot be measured, label it unknown. Report live required, reclaimable/orphan, backup retention and transient peak subtotals, with an inclusive total at the same instant. Backup destinations and replication copies count in deployment resource totals even when on another volume.

### 9.4 Preregistration and statistical interpretation

Before execution, freeze candidate builds, all knobs, cell enumeration, seed list, trial counts per stratum, failure schedules, warmup, arrival schedule, observation windows, timeout definitions, exclusion rules, machine resets, instrument overhead controls, confidence level, effect size threshold and multiplicity policy. Randomize or counterbalance paired candidate order on identical hardware; preserve workload seeds and compare paired runs. Use an open-loop offered arrival schedule when measuring queueing to avoid concealing overload through coordinated omission.

Report median and tail quantiles with the number of observations and confidence intervals that respect run-level clustering. Bootstrap at independent run or machine blocks, not millions of correlated events as if they were independent machines. A confidence interval crossing the Owner’s meaningful difference boundary is inconclusive, not a victory. Correctness violations are hard failures, not statistical outliers to discard.

For zero observed violations in n independent Bernoulli trials, the one-sided upper probability bound at confidence 1-alpha is 1-alpha^(1/n). This formula is a proposed reporting convention, with its independence assumption explicit; correlated fault schedules cannot use event count as n. If independence is unjustified, report empirical coverage and cluster counts without a probability guarantee. Exact sample sizes, alpha and minimum meaningful improvement remain preregistration fields for approval, not invented product requirements.

Excluded runs require a prespecified reason, retained raw evidence and an exclusion count. Timeout, injector failure, lost witness and unavailable hardware are reported as inconclusive or blocked. They cannot be converted to pass by retrying until a favorable run occurs. A rerun follows a documented correction with a new manifest revision; original evidence remains.

## 10 Backup snapshot and restore oracle

A snapshot is a coherent canonical cut with a bound immutable artifact set, not a folder copied at approximately the right time. Its candidate neutral manifest contains store/lineage ID, schema epoch, corpus and reducer version, aggregate high water vector or approved total-order high water, event-chain checkpoint digest, canonical state digest, projection versions and digests if included, exact committed receipt/outbox cut, immutable artifact IDs with lengths/digests, encryption key scope identifier without key material, source profile, snapshot generation and creation completion status.

The producer first pins a canonical read cut and all artifacts reachable at that cut. The backup must contain that exact cut or a later separately verified coherent cut, never metadata from one cut paired with data from another. It writes immutable backup data and artifacts, verifies them, flushes and publishes a complete manifest last. Partial data remains incomplete staging. Retention and GC cannot release the source artifact pin until backup closure and publication are verified.

For SQLite, use a pinned supported snapshot method such as the Online Backup API and inspect completion/error results. The API’s consistency applies to database content, not the separate CAS. Incremental backup can restart as concurrent writes occur, so derive and verify high water from the completed snapshot rather than assuming wall-clock start identifies it. Copying only the main database while committed WAL exists is not a consistent backup method. [S09, S21]

For JS1, capture immutable sealed segments and the complete prefix of the active segment ending at the chosen committed group. Either coordinate sealing or copy that verified prefix under a pinned snapshot protocol; copying an actively changing file without a cut is insufficient. Include manifest lineage and exact artifact closure. A rebuilt index is acceptable only if it reproduces the same canonical high water and state.

Restore into an isolated empty destination using approved keys. Verify manifest, schema/reducer compatibility, file and artifact digests, group/event chain and state at the declared high water before enabling mutation. Rebuild optional projections and compare separately. Restore command receipts and outbox state; do not reset idempotency history. Acquire fresh authority through the approved takeover contract before any new dispatch.

Pass requires O1–O5 at the manifest cut, exact artifact closure, no unintended effect dispatch during verification, recorded restore time and measured RPO against the independent ACK witness. An older valid backup can be internally consistent yet miss the Owner RPO or leave external effects requiring reconciliation. Successful file extraction, an engine integrity check or an application screen opening is not the restore oracle.

## 11 Conditional multi node branch

This branch is inactive unless the Owner makes multi-node canonical availability a requirement under G06. PostgreSQL 18.6 is a documented nominated version, not an automatic solution. PostgreSQL documents asynchronous replication’s loss window and distinct synchronous commit levels; waiting for receipt, durable remote flush and remote apply are different promises. PostgreSQL failover also requires ensuring that an old primary cannot resume conflicting authority. [S27, S29, S30]

A separately approved multi-node profile must pin fsync, full_page_writes, synchronous_commit, synchronous_standby_names, WAL/replication retention, failover manager, fencing, topology, replication slots, consistency of CAS replication and client retry behavior. Exact values depend on the Owner’s failure tolerance and availability decision; these fields are unverified here.

Additional mandatory cells are primary loss before/after local WAL flush; loss before/after synchronous replica ACK; replica loss and quorum loss; partition yielding competing leaders; old leader rejoin; stale follower reads; promotion before complete receipt/outbox/CAS transfer; failed archive or exhausted WAL retention; lagging standby with checkpoint/backup; client timeout after server commit; topology change during failover; and combined site or power domain loss. Expected results are the same O1–O5, plus no two admitted canonical writers, the approved acknowledged-loss bound, explicit availability refusal when authority is unavailable, and verified read-observer age.

Replication cannot make external side effects exactly once, and a database commit replicated without its artifact closure is still incomplete. If G06 remains single host, these cells are recorded out of scope with the Owner decision, not failed or passed. Do not burden or favor one finalist by adding a distributed service requirement halfway through the local comparison.

## 12 Ordered decision rule and decisive falsifiers

### 12.1 Hard floors before resource ranking

Gate A is evidence readiness: Owner inputs, frozen contracts, build pins, reviewed literal corpus, FU04 profile identity, negative-control sensitivity, independent oracle, privacy-safe synthetic data and safe fault rig. Missing any required field means no run or no recommendation.

Gate B is correctness: no violation of O1–O5 in any required in scope cell, no unauthorized writer, no duplicate mutation, no dangling acknowledged artifact, no silent canonical corruption, no partial atomic group and no false certainty after an uncertain commit. One valid counterexample rejects the affected profile. An inconclusive required cell prevents qualification.

Gate C is privacy and operability: approved key scope, artifact/receipt retention, logs without secrets, trustworthy restore and reconciliation procedures, diagnosable errors, observer age handling, bounded resource exhaustion behavior, reproducible pins, supportable platform contract and independently reviewed recovery evidence. A fast store that cannot be safely restored does not reach ranking.

Gate D is resource comparison among profiles that pass A–C. Apply Owner budgets for end to end latency, throughput, space, peak memory, maintenance, RPO and RTO. Compare the preregistered paired estimates and uncertainty with minimum meaningful differences. Use Pareto dominance first; apply only Owner-approved weights or tie-breakers to tradeoffs. Do not invent an aggregate score that trades correctness for speed.

### 12.2 Per option recommendation competitor and falsifier

| Option | Why retain or conditionally examine it | Competing option | Decisive falsifier and nonclaim |
|---|---|---|---|
| JS1 plus common CAS | Transparent append history and independently inspectable baseline | SQL1 with identical semantic/CAS contract | One witnessed acknowledged complete group is lost, altered or made unreachable after an in-scope fault; does not prove simplicity, low resource use or network durability |
| SQL1 plus common CAS | Transactional grouping and indexed receipt/authority checks merit comparison | JS1 baseline | One valid WAL-reset or checkpoint/crash trace loses or changes acknowledged canonical data, or permits stale mutation; release fix alone does not prove wrapper/VFS/CAS correctness |
| LMDB 1.0.1 historical challenger | Examine only if finalist results expose a relevant need | Both finalists, or explicit rebaseline to newer LMDB | Any admitted strong-profile acknowledgement disappears after declared fault; no performance or Windows suitability claimed |
| redb 4.3.0 challenger | Examine only under separately frozen workload and build | Both finalists or LMDB | Commit/repair/reopen sequence silently changes canonical history; release notes are not Recursion proof |
| RocksDB branch | Examine only if a real LSM behavior requirement is established | Existing finalists | Required correctness/retention/compaction fault breaks O1–O5 or fails approved resource envelope; no version or suitability claimed |
| PostgreSQL/replicated authority | Examine only if G06 explicitly requires multi-node canonical availability | Qualified local authority with accepted availability limits | Partition/promotion creates two admitted writers or loses ACK beyond approved bound; replication does not establish external exactly-once |

### 12.3 Recommendation algorithm

If any Owner input, normative corpus, sensitivity control or required platform cell remains missing, recommend no selection and name the blockers. If both finalists fail a hard floor, recommend neither; keep the baseline only as a diagnostic comparison and repair the shared contract or implementation before a new freeze. If only one passes all hard floors, report conditional eligibility for the qualified profiles, but do not bypass Owner budgets or interpret that as a product default.

If both pass, SQLite can be recommended over the baseline only when it satisfies the predeclared definition of “beats the baseline” on the approved objectives, with uncertainty resolved and no hard floor or budget regression. If results are tied, conflicting, workload-specific or underpowered, recommend no change/keep baseline for comparison and report the tradeoff. If the baseline is already an accepted deployed choice, retaining it still requires that its targeted durability promise is actually qualified; this report does not assume that status.

The Owner makes the final store and durability decision after independent review. The report supplies evidence and a deterministic recommendation rule, not a hidden default selection.

## 13 Owner inputs required before execution

| Input | Decision needed and why it blocks |
|---|---|
| Durability promise | Required failure domains, tolerated acknowledged loss and behavior after corruption; determines expected outcomes |
| G06 authority and availability | Single host versus multi-node, epoch takeover/fencing, refusal when authority unavailable; closes mutation race |
| Semantic freeze | Approved FU03 schema, digest and refusal rules, literal corpus and independent reviewer acceptance |
| Batching | Maximum batch count and delay, semantics of per-command versus group ACK; controls equivalence |
| Filesystem targets | Exact native Linux/Windows/WSL/network profiles and excluded deployment paths |
| Workload and budgets | Representative strata/weights, latency and throughput requirements, live/peak space, memory and maintenance limits |
| Backup objectives | RPO, RTO, retention, snapshot frequency, disaster domain and restore target |
| Key and privacy scope | Per goal/user/store key scope, encryption requirements, equality leakage from CAS IDs, diagnostic disclosure and key recovery policy |
| Read observer age | Maximum snapshot age, lag visibility, expiry/revocation/backpressure; controls checkpoint starvation |
| Command identity retention | Identity scope, duplicate retention and restored-history reconciliation; avoids unsafe forgotten receipts |
| Experimental precision | Sample sizes, confidence level, effect-size threshold, multiplicity rule, exclusion/watchdog policy |
| Authorized local rig | Disposable targets, physical power/network fault approval, independent ACK witness, recovery evidence storage and reviewer |

These are decisions, not implementation chores that a local agent may silently choose. Test code, wrapper pins and artifact hashes are execution prerequisites after the decisions, not substitutes for them.

## 14 Local execution handoff

The user’s local agent sessions need to execute the work below. Nothing in this section claims that a test has already run. The report does not start a local session or grant new destructive power-test permissions. Local sessions must use isolated synthetic targets and the user’s explicit execution authorization, preserving the operative constitution.

| Task | Prerequisites and exact work | Required evidence and pass or stop rule |
|---|---|---|
| L01 Freeze Owner decisions | Complete section 13; assign approved experiment and contract revisions | Signed/recorded choices and immutable manifest; stop if any required choice unknown |
| L02 Resolve exact pins | Obtain SQLite source artifacts, wrapper/runtime/build pins, JSON baseline, CAS and oracle commits; resolve verified WAL-reset fixture | Hashes, build/link flags, source IDs and regression reference; mismatch or floating version stops run |
| L03 Freeze semantic corpus | Use approved FU03 literals, IDs, refusal bytes and digest manifest; independent review | Both adapters equal normative corpus before crash tests; any byte mismatch rejects build |
| L04 Qualify platform premises | Execute required FU04 fixtures for each exact target and failure domain | profile_key, fixture/version/cutpoint, raw observations, contract digest and reviewer; missing profile remains unknown |
| L05 Audit common commit path | Review authority linearization, CAS publish order, atomic receipt/outbox binding, GC roots and recovery refusal logic | Reviewed ordering map tied to P00–P19 and source lines; unclosed fence or dangling-reference path stops |
| L06 Validate injector and witness | Prove hook reachability, stable independent receipt capture and exact failure domain; run no-fault controls | Trace/digest, fault trigger evidence, clock scope, observer loss handling; invisible or misplaced fault is inconclusive |
| L07 Run sensitivity controls | Exercise WAL-reset 3.51.2 negative control plus 3.51.3 and 3.53.4 references; frame/CRC/digest/fence guard mutations on disposable copies | Historical control fails for intended reason and fixed controls pass; insensitive oracle or untriggered schedule blocks qualification |
| L08 Run deterministic fault matrix | Expand F01–F42 across candidates, applicable P points and approved profiles; retain every run | Per-cell O1–O5 outcome, raw images, ACK witness, counters and errors; one in-scope correctness violation rejects affected profile |
| L09 Run native reset and power cells | Separate process, guest, host and physical power experiments on explicitly approved isolated equipment | Independent power/reset evidence plus reconstructed history; simulated fault cannot fill physical power cell |
| L10 Run backup and restore | Snapshot during activity, interrupt every stage, restore exact/mismatched/older sets and verify external-effect quarantine | Manifest cut, artifact closure, RPO/RTO, receipt/outbox result; copied files without validated cut fail |
| L11 Run resource comparison | Only after correctness readiness, use frozen seeds, paired order, offered load and maintenance policy | Full denominator inventory, raw latency/outcome streams, all bytes, memory and uncertainty; post hoc tuning requires new arm |
| L12 Evaluate and independently review | Apply sections 12–13 and inspect exclusions, every hard-failure trace and unresolved cells | Reviewer separate from implementer; Owner recommendation conditional on exact profile; no selection if evidence incomplete |

Deliver a local evidence bundle containing the preregistration, pin/build manifests, workload and corpus hashes, FU04 profile/result records, fault schedule and hook trace, independent acknowledgement ledger, preserved recovery images, canonical event/state/projection comparisons, CAS closure inventory, error/result logs, resource streams, backup/restore manifests, exclusions, confidence analysis and independent review. Use synthetic identifiers in shareable summaries; keep secrets, credentials, personal data and infrastructure identifiers out of public research artifacts.

Stop immediately on unintended target access, non-synthetic data, mismatched artifact hashes, unapproved power/network mutation, a correctness counterexample, witness loss or an unclosed authority ambiguity. Preserve evidence before repair. Diagnose and propose a new revision; do not erase failures by changing the oracle or quietly widening the claim. A completed local run answers only its frozen workload, profile and failure domain.

## 15 Completion gate and remaining uncertainty

| Gate from handoff | Report disposition |
|---|---|
| Both finalist versions and settings | SQLite release pin verified; SQL1 and JS1 settings specified; wrapper/baseline/Windows publication missing fields explicitly unverified |
| Exact fault cells and expected observables | F01–F42 plus P00–P19, expansion key, witness and missing-cell rules specified; execution unknown |
| Separate replay stale writer and duplicate oracles | O1, O2 and O3 specified separately, with O4/O5 closure and recovery support |
| All bytes and denominators | Inclusive inventory, logical/allocated/peak distinctions and per-metric denominators specified; values unknown |
| Candidate neutral backup/restore | Coherent cut, manifest, immutable artifact set and restore qualification specified |
| Decisive falsifier and acceptance order | Per option counterexamples; correctness/privacy/operability precede resource comparison |
| No selection and Owner blockers | Preserved explicitly in sections 1, 12 and 13 |
| Protected paths and privacy | No product repository or protected constitution edited; document QA and privacy checks accompany delivery |

The specification deliverable is complete subject to independent document review. Empirical qualification remains wholly unverified. This distinction is deliberate: missing local proof is never converted into a pass. Local sessions must complete section 14; the Owner must decide section 13.

## 16 Claim table

Classification abbreviations: SD source documented; I inferred/proposed; U unverified; LO locally observed. High confidence in a source statement does not certify a platform. All live pages were consulted on 1 October 2026 unless stated otherwise.

| Claim | Source and version or date | Class | Confidence | Expiry or review trigger |
|---|---|---|---|---|
| SQLite 3.53.4 identity and source digest | S01, 2026-07-24 | SD | High | Different source/build or corrected release record |
| WAL reset fix in 3.51.3 and historical 3.51.2 control | S02–S04, 2026-03-13 and live WAL page updated 2026-08-25 | SD | High | Upstream correction or new relevant regression |
| FULL/WAL, checkpoint and busy semantics | S04–S08, live API docs | SD | High | Engine version, VFS or API changes |
| Standard WAL network limitation | S04/S12, live docs | SD | High | Explicit supported architecture or VFS change |
| RFC 7464 provides framing only | S10, February 2015 | SD | High | New framing profile or protocol extension |
| JCS and canonical semantic layers differ | S11, June 2020; FU03 candidate | SD/I | High | Accepted semantic schema differs |
| File sync and directory sync are separate on Linux | S13, Linux man-pages, live pages | SD | High | OS/filesystem or mount change |
| Short write and rename constraints | S14/S15, Linux man-pages, live pages | SD | High | Kernel/filesystem profile change |
| Windows flush/replace do not establish universal POSIX publication equivalence | S16–S18, Microsoft API docs | SD/I | High | Native API/profile evidence or documentation change |
| Consistent SQLite backup does not include external CAS automatically | S09/S21 plus artifact design | SD/I | High | Backup protocol or CAS topology change |
| Upstream simulation is not local physical power evidence | S20 plus failure-domain distinction | SD/I | High | Local qualified evidence supplied |
| WSL mounted Windows drive separate from Linux storage | S22, Microsoft 2022-03-03 | SD/I | High | WSL/storage stack change |
| LMDB 1.0.1 exists and 1.0.2 supersedes it before freeze | S24/S25, 2026-08-06/09-08 | SD | High | Release correction or explicit rebaseline |
| redb 4.3.0 exists and documents relevant recovery fixes | S26, September 2026 | SD | High | Pin or source change |
| PostgreSQL 18.6 exists; replication levels/failover differ | S27/S29/S30, 18.6 and version-18 docs | SD | High | G06 decision, topology or version change |
| SHA256 is defined; digest alone is not authority or rollback prevention | S28 plus threat model reasoning | SD/I | High | Digest/threat model change |
| Shared bytes, codes and identity are candidate completion | FU03 CAND-RCV1-20261001 | I | Conditional | Owner acceptance or schema revision |
| Profile key and domain qualification are conditional | FU04 candidate contract | I | Conditional | Platform or contract revision |
| SQL1/JS1/CAS ordering and O1–O5 are proposed acceptance contract | Sections 4–6 | I | Conditional | Independent review counterexample or Owner change |
| F01–F42, denominators and statistical rules are proposed preregistration | Sections 7–10 | I | Conditional | Approved workload/injector/statistical revision |
| Engine/wrapper/CAS/platform correctness and resource values | No local experiment | U | Unknown | Qualified local evidence and independent review |
| Named upstream regression file/hash | Public release/race facts established; exact fixture not resolved | U | Unknown | Local immutable fixture verification |
| Security or CVE cleanliness of any candidate | No comprehensive security assessment | U | Unknown | Separate scoped security review |

## 17 Primary source ledger

S01. SQLite release 3.53.4, 24 July 2026. Official release identity, source ID and sqlite3.c digest. https://sqlite.org/releaselog/3_53_4.html

S02. SQLite release 3.51.3, 13 March 2026. Official WAL-reset fix and source hashes. https://sqlite.org/releaselog/3_51_3.html

S03. SQLite release 3.51.2, 9 January 2026. Official negative-control identity and source hashes. https://sqlite.org/releaselog/3_51_2.html

S04. SQLite Write Ahead Logging, page updated 25 August 2026. Network restriction, WAL persistence and reset race. Live documentation, not immutable build evidence. https://sqlite.org/wal.html

S05. SQLite PRAGMA statements. synchronous, journal_mode and validation interfaces; live documentation. https://sqlite.org/pragma.html

S06. SQLite sqlite3_wal_checkpoint_v2. Checkpoint modes, progress counters and contention behavior; live documentation. https://sqlite.org/c3ref/wal_checkpoint_v2.html

S07. SQLite busy timeout and transaction documentation. Busy handler behavior and transaction error considerations; live documentation. https://sqlite.org/c3ref/busy_timeout.html and https://sqlite.org/lang_transaction.html

S08. SQLite result and error codes. I/O, busy, full and related result distinctions; live documentation. https://sqlite.org/rescode.html

S09. SQLite Online Backup API reference. Completion, locking and error semantics; live documentation. https://sqlite.org/c3ref/backup_finish.html

S10. RFC 7464, JSON Text Sequences, February 2015. Immutable framing standard. https://www.rfc-editor.org/rfc/rfc7464.txt

S11. RFC 8785, JSON Canonicalization Scheme, June 2020. Canonical JSON and Unicode/numeric constraints. https://www.rfc-editor.org/rfc/rfc8785.txt

S12. SQLite OS Interface or VFS, page updated 31 May 2025, and I/O methods reference. VFS/locking/source boundaries and sync interfaces. https://sqlite.org/vfs.html and https://sqlite.org/c3ref/io_methods.html

S13. Linux man-pages fsync(2), live page. File and directory synchronization distinction. https://man7.org/linux/man-pages/man2/fsync.2.html

S14. Linux man-pages rename(2), live page. Namespace atomicity, same-filesystem limits and error cases. https://man7.org/linux/man-pages/man2/rename.2.html

S15. Linux man-pages write(2), live page. Partial writes, delayed errors and persistence limits. https://man7.org/linux/man-pages/man2/write.2.html

S16. Microsoft FlushFileBuffers and File Caching. Native flush and write-back cache documentation. https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers and https://learn.microsoft.com/en-us/windows/win32/fileio/file-caching

S17. Microsoft ReplaceFileW, updated 1 June 2023. Unsupported WRITE_THROUGH and partial failure states. https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew

S18. Microsoft MoveFileExW, updated 1 June 2023. Move/copy/delete and write-through conditions. https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw

S19. SQLite How To Corrupt An SQLite Database File. Mispairing, locking and broken sync risks; live documentation. https://sqlite.org/howtocorrupt.html

S20. SQLite How SQLite Is Tested. Upstream I/O/crash simulation and compound fault methods; live documentation. https://sqlite.org/testing.html

S21. SQLite Online Backup API overview, page updated 13 November 2025. Consistent snapshots and concurrent backup restarts. https://sqlite.org/backup.html

S22. Microsoft Working across Windows and Linux file systems, updated 3 March 2022. WSL and mounted Windows filesystem distinction. https://learn.microsoft.com/en-us/windows/wsl/filesystems

S23. SQLite Atomic Commit. Storage assumptions and commit concepts; this rollback-oriented discussion is not substituted for WAL qualification. https://sqlite.org/atomiccommit.html

S24. OpenLDAP project announcement LMDB 1.0.1, 6 August 2026, accessible in official announcement archive. https://lists.openldap.org/hyperkitty/search?mlist=openldap-announce%40openldap.org&page=1&q=lmdb&sort=date-desc

S25. OpenLDAP project announcement LMDB 1.0.2, 8 September 2026, same official archive. The version and date are source documented; an immutable source archive hash remains unverified. https://lists.openldap.org/hyperkitty/search?mlist=openldap-announce%40openldap.org&page=1&q=lmdb&sort=date-desc

S26. redb official v4.3.0 release. Release facts, recovery/storage error fixes and release-linked commit 2de02fa. https://github.com/cberner/redb/releases/tag/v4.3.0

S27. PostgreSQL 18.6 official release notes, 13 August 2026. Version existence only; no blanket security certification. https://www.postgresql.org/docs/18/release-18-6.html

S28. NIST FIPS 180-4 Secure Hash Standard, August 2015 update. SHA-256 specification. https://csrc.nist.gov/pubs/fips/180-4/upd1/final

S29. PostgreSQL 18 Log Shipping Standby Servers and WAL settings. Synchronous replication/commit distinctions; versioned major documentation may evolve with minor releases. https://www.postgresql.org/docs/18/warm-standby.html and https://www.postgresql.org/docs/18/runtime-config-wal.html

S30. PostgreSQL 18 Failover. Old-primary/failover coordination considerations. https://www.postgresql.org/docs/18/warm-standby-failover.html

Source handling note: Public release pages establish nominated version facts. Live API pages establish documented behavior on the review date. Local sessions must preserve exact cited source snapshots and relevant immutable code references with the experiment evidence. No private source, hidden reasoning, proprietary benchmark or vendor marketing claim is used as a correctness oracle.
