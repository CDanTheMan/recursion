# R-Y — Workspace and repository graph

Status: decision-ready design candidate; UNIMPLEMENTED, UNEXECUTED, independently unreviewed. No technology, integration, store, watcher, language, forge or vendor selected; no route qualified.

Research date: 2026-10-02 UTC. Authoritative source commit: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. All repository observations below concern that committed source, not an unseen local working copy.

## Decision-ready findings

A workspace is an explicitly registered logical identity, not a directory, remote URL, commit, editor window or grant. Give each repository a separate identity; bind a task to one versioned workspace manifest and a vector of exact source states. Content identity establishes byte equality within its declared coverage. It does not establish project identity, authority, availability or coherent capture of a changing checkout.

The candidate separates six operations often called “fork”: conversation-history branching; logical source lineage; disposable worktree allocation; source capture; branch/ref creation; and candidate application. Each has an independent operation identity, admission and receipt. Evidence and accounting history may be referenced by both descendants. Active grants, writer ownership, approvals, process leases and reservations are never cloned.

Two coherent capture approaches deserve local comparison: an admitted immutable source closure, including a qualified storage-snapshot mechanism where available, versus capture under enforceable quiescence covering every relevant writer. A before/after scan is a third, weaker observation profile. Equal endpoint hashes can miss ABA or mixed-time reads; that profile must refuse a task requiring an atomic coherent dirty-tree fork.

The highest-value unexecuted tests are mixed-cut/ABA capture, shared-ref/worktree isolation, stale-base application, opaque-handle privacy, disabled-indexer traps and dirty-tree fork/lost-machine recovery. These attack distinct claims. None has run here. Invalidation accuracy, throughput, snapshot fidelity, latency, resource cost and productive-continuity benefit remain `unknown`.

<a id="ry-s0"></a>
## S0 — Authority, evidence and current-source reconciliation

Evidence labels: **SD-public** means a retrieved primary source documents a mechanism; **SD-repository** means the pinned repository states a requirement or historical claim; **LO-record** means static inspection of committed implementation/evidence bytes; **Proposal** means the design in this report; **Unknown** means no qualifying evidence. A source record is not an execution result.

The authoritative current instruction and D018–D033 preserve a native harness and upstream-only harness orchestration, comprehensive built-but-opt-in capabilities, one canonical writer with core fencing and an availability seam, and Aggressive / Full / Lazy Stop plus checkpoint / interrupt / drain. Workspace operations cannot stop an actor. D020's automatic takeover capability is required through the opt-in first-party remote/full plugin; it is not default consensus. D029's trusted launch boundary applies to upstream access, including output-mediated secret export. Native helper inference may not silently appear in upstream-only continuation. D031 forbids vendor-intent narratives.

The baked brief's “no GUI required” line and older interface release wording lag the accepted comprehensive D019 scope. Use TUI-first construction and one backend; exact GUI release timing needs Owner interpretation, without quietly choosing a smaller release. Old architecture coverage's R-P workspace assignment is stale: this report answers R-Y. G06/G07/G11 Owner decisions are closed, while their implementation qualification remains open.

### Static record observations

- `CONTEXT.md` pins repository/source/candidate references outside compaction, privacy-scoped content identity and rehydration, and a repository-map invalidation experiment still unrun. DS12 has no new context experiment here. DS21 selects no canonical store, so this report inherits no measured snapshot durability.
- `INTERFACE-STRATEGY.md` distinguishes generated/tested/reviewed/accepted/published and explicitly includes the unfinished dirty-source fork journey. A UI fork button therefore cannot be evidence of source capture.
- `experiments/v3/generation-authority/authority.py` has bounded generation publication and reader-pin checks, a writer boot/serial/parent revision, and reparse checks during fixture reclamation. This is a cooperating-process fixture, not a workspace resolver or adversarial filesystem containment implementation. Static path checks there do not prove race-free read/copy/apply.
- `experiments/v3/replay-store-evidence/admit.py` requires clean source, compares selected working bytes with committed blobs after CRLF normalization, and separately records working/blob hashes. That limited clean-source admission is neither a dirty-tree snapshot nor an exact raw-byte equivalence proof. It was not run here.
- `experiments/v3/shared-reservations/wr_domain.py` retains separate reservation, generation, reader-pin, copy, receipt and incarnation state in a finite fixture. It supplies useful distinctions, not workspace implementation or a newly measured accounting result.

No workspace identity resolver, graph index, coherent dirty snapshot or fork-binding implementation is established by the inspected records. Remote committed source does not include unseen local dirty/index/untracked/ignored work. Input hashes identify the actual inspected files in `input-pins.json`; no supplied script was imported or executed.

### Public facts and aggregate-source discipline

[Appendix A](#ry-sources) is this lane's sole concentrated public-source fact sheet. Other sections are original proposals applying those facts. Upstream comparative facts are owned by [R-I worktree dispatch](../ri/report.md#7-r-i-q07-worktree-dispatch-and-cross-harness-comparison), [R-K per-cell comparison](../rk/report.md#r-k-q12-per-cell-prior-art-comparison), [R-K Codex commands](../rk/report.md#codex-tui-command-facts) and [R-F route facts](../rf/report.md). This lane adds no independent vendor-summary allowance and makes no superiority claim.

<a id="ry-q01"></a>
## Q01 — Stable workspace and repository identity

**Proposal Y-R01.** Register an opaque, random `workspace_id` in a project/privacy domain, with immutable `WorkspaceManifest` revisions. It contains member repository identities, authorized coupling edges, policy references and logical mount names. The canonical writer owns registration and membership changes. Machine-local paths are separately revocable locator observations; editor names and remotes are aliases. A repository receives its own opaque `repository_id` and lineage record. Same bytes do not merge identities; renaming changes an alias only.

A move or machine change keeps identity only through an admitted relocation/rehydration mapping, not path heuristics. A clone is a new physical repository instance. It can represent the same logical repository after explicit association, or become a new logical repository with a clone/fork ancestry edge. If that intent is unavailable, the resolver returns ambiguity. Blindly copying a manifest cannot authorize registration or prove continuity. Concurrent restored copies share historical identity but require distinct instance IDs and fresh execution ownership.

Four comparison families are retained without selection:

1. Path-oriented resolver plus canonical stable identity and explicit relocation receipts
2. Remote/URL alias resolver plus the same registration and ambiguity rules
3. Content-revision locator plus project-scoped registered identity
4. Versioned workspace-manifest locator plus registered instance and content validation

Pure path, URL or commit-as-identity designs fail fixed requirements and are negative controls, not admissible competitors. A manifest is also insufficient without a canonical registration check. Falsifiers and costs are in Y-R01/Y-R02; fixtures Y-F01/Y-F02/Y-F16 distinguish them.

<a id="ry-q02"></a>
## Q02 — Snapshot, source fork, branch and working state

**Proposal Y-R02.** `SourceSnapshot` is an immutable, policy-qualified manifest over a declared captured set; its internal content identity includes encoding/schema, typed paths, file kinds, byte identities, selected metadata and exclusions. It pins VCS type/object-format plus commit/tree identities where present. Working tree, logical index, branch-pointer observations, untracked set and allowed ignored set are separate components. A Git commit alone names none of the last four.

`SourceFork` names a parent source snapshot, new logical lineage, destination workspace revision, source-map correspondence, required authority revalidation and independent accounting references. It is a canonical fact of derivation, not a live grant. A mutable working tree is `Materialization` plus mutation generation; a ref is an observation of a name-to-object relation at a recorded time/cut; a remote is a locator and disclosure destination. A conversation fork is only retained-history lineage unless separate source operations are admitted.

A snapshot proves reproduced bytes only if every claimed member is present, each independently checked byte/type/metadata predicate matches and the capture-coherence class satisfies the task. Missing external LFS objects, absent sparse paths and omitted secrets are explicit coverage, not empty files. Neither copied bytes nor a passing digest check proves they existed together at one instant.

<a id="ry-q03"></a>
## Q03 — Private identifiers, locators and equality leakage

**Proposal Y-R03.** Reuse R-Q/R-T `ArtifactRef` and `ContentEnvelope`; add workspace-specific facets rather than a second artifact store. Internal content digests remain in the project trust domain. Cross-domain references are audience/purpose-scoped random opaque handles with expiry and no derivable digest. An authorized resolver maps handle to internal manifest, checks current rights, and issues bounded retrieval; possession is never bearer authority by itself.

Private content deduplicates, if enabled at all, only within the same explicit project privacy namespace. Equal bytes in separate projects require separate logical objects, encryption/key domains, billing/cache namespaces and copy inventories. Neither cache hits nor missing-object responses may leak cross-project existence. Restricted manifests contain real paths, lengths, digests and exact capture times; projections expose only permitted aliases and coarsened metadata.

Compare per-audience random handles plus private content maps with domain-keyed internal object names plus separately randomized external handles. Both prohibit cross-project equality sharing. Bucketed lengths, bounded batching and normalized denial responses reduce specific observations but do not prove traffic-analysis resistance. An observer with host/storage access is a separate threat; when its permitted view cannot meet the declared observation contract, refuse that privacy profile. No zero-leakage or cryptographic implementation claim is made. Y-F10/Y-F18 cover synthetic membership probes; the adversary's visibility must be explicit.

<a id="ry-q04"></a>
## Q04 — Exact task binding and re-resolution

**Proposal Y-R04.** `WorkspaceBinding` records task/GoalSpec/plan refs; workspace ID and manifest revision; repository source vector; candidate/change-set refs; materialization IDs and capture class; effective repository profiles and configuration digests; privacy/rights revisions; source observation cut; route/configuration epochs; current authority decision reference; qualified platform profile; permitted read/write set; and evidence/coverage refs. The grant reference is resolved against canonical state at admission, never copied as self-validating data.

There is exactly one workspace identity per active task binding revision. A task spanning repositories uses members of that manifest. Changing the workspace is a canonical rebind event with parent binding, source correspondence and refusal-visible loss; it is not an implicit cwd switch. Compare eagerly sealed bindings at admission with lazily hydrated bindings whose exact member vector is sealed before use; both revalidate before effects.

Re-resolve on explicit rebind, source divergence, route/host incarnation change, profile/config/policy update, compaction recovery, lost-machine restore or stale observation. Distinguish “same historical binding” from “currently executable binding.” A missing source, multiple matching registrations, changed dirty generation, unknown capture class, policy denial or an unobserved base yields a typed refusal. Lookup cannot guess `origin`, choose the nearest path, fetch missing objects, index the tree or ask a model.

<a id="ry-q05"></a>
## Q05 — Multi-repository membership and coupling

A workspace manifest is a versioned member set, not a super-repository. Each member has a logical mount name, repository/instance refs, source ref, profile ref, privacy domain and permitted verbs. Coupling edges declare purpose, producer/consumer revisions, owner, interface contract and whether a task requires joint compatibility. Cross-project members still retain separate private storage and visibility rules; joining a workspace never creates a dedup or disclosure exception.

**Proposal Y-R05.** Compare a manifest-wide source vector sealed for each multi-repo task with independently sealed member bindings plus an immutable coupling receipt. Both reject mixed vectors when a task requires a common acceptance set. No VCS transaction is assumed to atomically update multiple repositories. Applying changes uses separate effects and a canonical coordination record showing per-repository prepared/applied/verified/uncertain state. An interrupted sequence is partial, not “workspace committed.” Cross-repository release or merge remains Owner-controlled.

Cycles in declared dependency metadata need not imply invalid source history; cyclic build/service relationships are allowed as typed relations with an explicit execution policy. A schedule cannot fabricate a topological order when no such order exists. Missing members and unknown external dependencies block claims that require completeness, while explicitly independent work may remain eligible.

<a id="ry-q06"></a>
## Q06 — Worktrees as disposable execution contexts

**Proposal Y-R06.** `Materialization` binds a physical instance to repository identity, admitted source snapshot and execution profile. It records an opaque root locator, host incarnation, mount policy, mutation owner/generation, shared administrative resources, availability and loss disposition. A Git worktree is one adapter-specific materialization. Its deletion removes an execution context, not task history, source evidence or actor identity. A missing checkout becomes unavailable; resumption requires a new admitted materialization.

Parallel task isolation compares linked worktrees with shared repository-administration fencing against independently materialized private copies from the same snapshot. Both need disjoint writable output roots, current mutation permits and control of shared resources. Git's worktree lock is an administrative retention mechanism, not Recursion's exclusive mutation permit. A common object/ref/config store, build cache, lockfile outside roots, hardlinked file or submodule directory is an explicit shared resource.

Moving a materialization updates its locator after root/instance verification and may require a separately admitted adapter repair. Closing a view, detaching or removing a locator has no Stop semantics. A task with running owned processes cannot have their workspace silently deleted; cleanup needs quiescence evidence and its own approved effect. Otherwise retain the data and report the blocker.

<a id="ry-q07"></a>
## Q07 — Bounded monorepo work without default indexing

Required dimensions are independent: logical file count; bytes and maximum blob; directories/depth; commit/history/ref counts; changed paths; sparse materialization; partial object availability; nested repositories/submodules; vendored/generated trees; binaries/LFS; symlink/hardlink topology; case/encoding; and index/dependency-edge count. No observed scale limit or numeric product budget exists.

**Proposal Y-R07.** Compare demand-bounded tree/diff traversal with opt-in persistent dependency indexing. Default binding reads only bounded registered metadata and explicitly requested source references. It does no whole-root discovery, profiling, graph construction, watcher start, inference or index activation. An indexer may run only after separate admission; minimal disabled capability metadata is still attributable and not claimed literally free.

Traversal has explicit file/byte/time/depth/history/edge budgets, cancellable batches, retained progress cursor tied to source/config and typed `budget_exhausted` coverage. Incremental work uses verified immutable subtree identities and change sets, not mtimes alone. Sparse-not-materialized and promisor-unavailable differ from absent. Demand fetching, recursive submodule discovery and generated build-rule execution are additional effects, never automatic traversal conveniences.

Report cold/warm costs, invalidation fanout, bytes read, objects fetched, memory, index disk and review effort using R-O's measurement envelope. Google-scale literature establishes a workload class, not Recursion's target or a reason to require its architecture. Aider-style ranked maps are optional lossy context views; omitted symbols cannot become proof of nonexistence.

<a id="ry-q08"></a>
## Q08 — Repository profiles and precedence

**Proposal Y-R08.** Profiles are versioned declarative inputs. The candidate precedence for ordinary settings is product defaults → workspace defaults → repository overrides → explicit admitted task overrides. Repository-specific build/test/lint commands, language hints and ignore settings override workspace defaults where the schema permits. Per-key origin and rejected conflicts appear in the effective profile; no arbitrary merge of commands or arrays is inferred.

Authority, secret exclusions, publication/egress rights, isolation minima and budget ceilings combine by intersection/most restrictive bound. A repository file cannot override an Owner deny, broaden filesystem access or activate an indexer. Task overrides cannot widen these bounds. When two required settings are incompatible, refuse rather than choosing whichever file was read last. Unknown requirements stay unknown.

Profiles supplied by a repository are untrusted proposals until admitted. Inspecting their declarative fields executes no build system, plugin, shell hook, extension installer or package manager. A pinned command is still an effect requiring permitted execution, environment and output boundaries. Separate secret exclusions from VCS ignores: ignored files may be harmless, while tracked files may contain secrets. Exclusion policy is evaluated before read/copy/index/egress where feasible, not only after a prompt is assembled.

Compare an eager per-member effective-profile compilation with demand compilation keyed by all input refs; both use the same deterministic precedence and current deny semantics. Y-F04/Y-F12 falsify stale-policy reuse and profile-driven authority expansion.

<a id="ry-q09"></a>
## Q09 — Concurrency, checkout mutation and isolation

**Proposal Y-R09.** The canonical owner admits one active checkout mutation owner for each writable resource set and generation. The execution broker enforces that permit at the protected boundary. A task process owns neither the canonical writer nor other worktrees simply because it can see a shared VCS object database. Observations are revision-tagged, potentially stale facts; no globally coherent live index is assumed.

Compare per-task writable materializations with repository-administration serialization against a shared checkout with enforced single mutator and read generations. The latter is admissible only where unmanaged writers are excluded and readers can bind to immutable or properly isolated views. An ordinary cooperative lock with external editors still writing is not an enforced exclusivity proof. If enforcement is unavailable, restrict operations to observation/proposal and refuse coherent application or capture claims.

Each read declares immutable-source or validated-live semantics. Watcher events invalidate observations but do not allocate authority. Worktree file isolation does not isolate shared branch updates, configuration, hooks, caches or external tools. Operations touching those require their own resource permits. Current source/base, authority and pause fences are rechecked immediately before application; a check followed by an unprotected write window is insufficient. The next sections separate copy and apply races from graph freshness.

<a id="ry-q10"></a>
## Q10 — Change graph without fictional linear history

**Proposal Y-R10.** Change identity is independent from a commit. `ChangeSet` binds an immutable base source vector, exact path operations and resulting candidate source vector. A task may produce several candidates; a commit may include several change sets; a squash may represent several predecessors. Record `produced_by`, `based_on`, `includes`, `reviewed_as`, `applied_to`, `observed_at_ref` and `supersedes_candidate` as distinct edge types with issuer, evidence, immutable endpoint versions and canonical recording cursor.

Rebase/amend/squash create new revision identities. A correspondence edge records an observed or verified relation, with explicit mapping/loss; patch similarity is only inferred. Force-push and branch deletion are external observations, never authorized actions here. Historical source/evidence refs remain immutable even if reachability changes. A moving ref cannot silently retarget an old review. If referenced objects were not retained, report evidence unavailable rather than fabricate reconstruction from a current branch.

Canonical event order governs Recursion admission and acceptance; the VCS DAG governs observed commit ancestry. Neither rewrites the other. Compare append-only typed change events with materialized derived graph views against append-only per-change receipts with graph views reconstructed on demand. Both retain many-to-many relationships and exact source/candidate refs. A review applies to the exact candidate and policy under which it was issued, not all future incarnations of a similarly named branch.

<a id="ry-q11"></a>
## Q11 — Source graph and edge authority

**Proposal Y-R11.** Model the requested chain as typed relations, not a strict containment hierarchy. A repository has materialization instances; each materialization observes a revision and optional dirty snapshot; a revision names a root tree; tree entries bind byte-encoded names, kinds/modes and object refs. Blobs have no intrinsic path or project ownership. A worktree can be detached, unborn, sparse or conflicted, so `worktree → revision` is not always a single present commit.

Three provenance tiers prevent a graph cache becoming authority:

- Canonical domain facts: registered workspace membership, binding/rebind, mutation ownership, accepted configuration, accepted review and application admission. Only the existing canonical writer accepts them
- Source observations: validated VCS commit/tree/object relations, observed refs/index entries, captured bytes and filesystem kinds. They are authoritative only about the validated source/cut and declared coverage, not permission
- Re-derivable interpretations: symbol/import/call graph, ownership suggestions, rename similarity, inferred dependency/coupling, generated maps and summaries. Pin parser/version/config/source coverage and retain uncertainty

An ownership file or signed commit is evidence about declared responsibility/origin, not an authenticated Owner instruction. Cyclic semantic dependencies are allowed; the immutable derivation/influence graph must not create impossible self-parentage. Unknown language/parser support cannot produce a “no dependencies” edge set. Every graph query returns coverage and exact source refs along with its payload.

<a id="ry-q12"></a>
## Q12 — Invalidation and unknown coverage

**Proposal Y-R12.** Cache keys include project/privacy domain, repository source snapshot, selected member set, index logical state when relevant, sparse/partial manifest, effective profile/configuration, ignore/exclusion/rights revisions, parser/tool/transform version and dependency observations. A root tree digest alone cannot key a working-tree map. Invalidations originate from canonical changes, source-object changes, observed live edits, profile/config/rights changes, parser updates or lost observation coverage.

A file move invalidates path-dependent labels and reverse edges even if blob bytes match. New files can change name resolution; deletion can change fallback resolution; symlink target changes can change traversal; attribute changes can change interpretation without changing a source file. Changed dependents are conservatively invalidated until their exact trace is revalidated. Unknown dynamic inputs prohibit a complete-cache claim.

Coverage has `complete_for_declared_set`, `partial`, `stale`, `unknown`, `unsupported` and `unavailable` states, with included/excluded/unmaterialized sets and reasons. Watchers are hints. Queue overflow, dropped rename pairing, mount loss, unexplained gap or change during rescan marks affected scope unknown; a bounded rescan can restore only what it actually checks. Do not launch a full walk in the default binding path to hide this uncertainty.

Compare full rebuild of the explicitly authorized bounded set with dependency-trace incremental reconstruction. The decisive falsifier is any stale supposedly valid edge versus an independent fresh oracle over the same frozen synthetic source. A pass proves only that corpus and declared dependency class; cost and accuracy are still null until execution. Y-F05/Y-F13 include config-only changes and overflow, not just commits.

<a id="ry-q13"></a>
## Q13 — Attribution, provenance and ownership labels

Use shared `ContentEnvelope` fields exactly: `project_and_audience` and `privacy_domain_id`; do not invent an inherited `project_id` alias. The shared four-field `ArtifactRef` remains object_type/id/version/content_digest. `workspace_facets` is a proposed extension containing workspace/member/source/change refs, representation kind, snapshot coverage and local-materialization evidence. All shared records remain unratified proposals.

**Proposal Y-R13.** A source/change can be labeled generated, adopted, ported, forked or mixed at the finest supported path/span/blob granularity. Record claimed author separately from authenticated producer, source lineage, transformation, tool/model identity when legitimately observable, reviewer, accepting Owner decision, license/notice boundary and allowed uses. “Ported” is a declared transformation with parent evidence, not proof of compatibility or cheapness. Missing rights are unknown; do not infer them from public availability.

Possible-influence lineage includes every visible input, not only model-chosen citations. A generated map, binary preview, OCR or code summary is a derivative with inherited restrictions and registered copies. Project-private source names, emails, paths and digests stay in restricted evidence; outward reports use approved aliases. Compare path-level attribution plus span exceptions against span/blob-first attribution with aggregated views; both retain uncertainty and license boundaries. Neither proves originality, copyright ownership, legal clearance or the semantic correctness of attribution. R-H owns legal analysis; R-Q/R-T own shared retention, copying and media loss contracts.

<a id="ry-q14"></a>
## Q14 — Native versus delegated Git boundary

**Proposal Y-R14.** Recursion natively owns identity, policy evaluation, binding, provenance, receipt interpretation and evidence comparisons. A VCS adapter proposes observed histories and authorized operations. Compare calling a pinned user-provided Git implementation in a constrained broker with an independently implemented/library-backed adapter for a declared subset. Both must report unsupported semantics and pass the same corpus; neither becomes a second VCS history authority.

“Read command” is not “intrinsically side-effect-free.” Git may consult configuration, attributes, external diff/textconv, fsmonitor, credential helpers, hooks on some operations, or a promisor remote. Read-only intent therefore needs a qualified no-network/no-helper profile and bounded inputs; if required semantics cannot be supplied without extra effects, return unavailable. Do not copy private config to public diagnostics. This report ran no Git command against the target.

| State or operation | Candidate disposition |
|---|---|
| Detached or unborn HEAD | Preserve exact state; no guessed branch or auto-created ref |
| Dirty working tree | Record base/index/working distinctions and capture class; no stash/reset/clean fallback |
| Merge/rebase/cherry-pick/sequencer in progress | Read as conflicted/in-progress; preserve index stages and evidence. Generic application/resume refuses unless a separately qualified operation-specific profile was admitted |
| Submodule | Separate repository/materialization/source record. Parent gitlink is a pin, not all nested bytes or permission to initialize/fetch |
| Hooks, filters, signing | Declarative detection before execution. Execution and signer access require explicit capability/admission; never silently bypass a required hook or claim signed status without evidence |
| Commit/ref update | Separately admitted VCS effect with exact expected old/new identity. No autonomous merge/force-push/deployment |
| Ref observation | Timestamp/cut-tagged evidence. Do not manufacture a new authoritative branch database |
| Adapter failure | Typed refused/partial/uncertain result, preserved bytes and diagnostic scope. No alternative destructive “repair” |

Signed commits supply bounded origin/integrity evidence, not ownership, permission or acceptance. Adapter version, object hash algorithm, config/attributes, environment boundary and captured commands belong in the eventual evidence.

<a id="ry-q15"></a>
## Q15 — Deterministic snapshots, restoration and race windows

**Proposal Y-R15.** A snapshot is a versioned manifest with a declared preservation relation. Three separate claims are useful: logical VCS state; exact included working bytes; and coherent capture of a specified multi-file state. None implies all host/environment inputs or durability. The manifest declares which it offers.

### Capture classes and ABA

A: immutable closure capture uses admitted immutable objects plus an admitted coherent dirty overlay. A qualified COW/storage snapshot can supply a stable read view, but is not assumed available on every filesystem or across volumes. Object retention is pinned through capture and verification.

B: enforced-quiescence capture excludes all relevant writers for the whole capture interval, stabilizes index/ref/working and nested state, then records the cut. A cooperative application mutex alone cannot exclude editors, antivirus/filter transformations, separate Git processes or hardlink aliases. Unenforceable quiescence makes the coherent claim unavailable.

C: bounded validated capture reads a manifest and bytes with repeated identity checks and records start/end observations. It may detect changes but can miss an A→B→A transition and can assemble a combination that never existed simultaneously. It offers only the exact captured artifact plus observation interval, not an atomic source snapshot. A task whose acceptance requires coherent source-fork continuity must reject C, even if all before/after hashes agree. Y-F14's oracle contains the writer schedule and valid global cuts, not just the capturer's hashes.

### Inclusion and preservation matrix

| Component | Required manifest and restore behavior |
|---|---|
| Committed objects | VCS algorithm + full commit/tree/blob identity; verified required closure and retention pin. Pack-container identity is separately recorded, never substituted for semantic object identity |
| Index | Logical entries, raw path bytes, kinds/modes, stages 0–3, intent/skip/sparse flags where supported; raw index backup optional and separately version-bound. Stat cache is not portable semantic state |
| Working files | Exact raw bytes, type, executable/required metadata and divergence from index. Text decoding/line-ending conversion is never part of the raw-byte digest |
| Untracked files | Explicit admitted selection; unknown/unscanned set marked. No assumption that a VCS status sample covers all files |
| Ignored files | Default excluded except an explicit allowed artifact set. Record exclusion class privately; no secret names/hashes in outward absence proofs |
| Attributes and transforms | Relevant attributes, encoding/EOL/filter configuration and tool identity. Store original and transformed identities separately; do not run clean/smudge/textconv to “normalize” evidence silently |
| Symlinks | Capture link text and type without following by default. Traversal needs a separately allowed target and handle-relative containment. Restore as a link only on qualified profile; substituting a text file is a different result |
| Hardlinks | Detect alias groups within declared scope where possible. Mutable candidate output must not share inode/file identity with the original or another private domain. Copy bytes to independent files or preserve a declared in-scope link group; unknown out-of-scope aliases forbid exclusivity claims |
| Reparse points/junctions/mounts | Record supported kind and target metadata without traversing. Unknown reparse tags, magic links, mount boundaries and link escapes refuse materialization under the strict profile |
| Submodules/nested repos | Record expected gitlink, observed nested HEAD/index/working state and nested coverage; missing objects stay missing. Never automatically fetch or recurse across scope |
| LFS/binaries | Distinguish pointer bytes, referenced object identity, verified object availability and materialized bytes. No lazy download. Binary diffs use exact byte artifacts plus optional separate previews |
| Case/Unicode/name restrictions | Preserve source path encoding/case. Preflight representability and collisions on target. Case-folding collisions, reserved names, normalization loss and unsupported path lengths fail exact restore rather than rename silently |
| ACL/xattr/ADS/security metadata | Explicit preserved/omitted/unsupported facets. Do not copy broad ACLs, owner IDs or executable trust blindly. Required omitted facets block exact-profile acceptance |
| External state | Toolchains, environment, generated external dependencies, services, secrets and human context are not captured unless separately admitted; never claim hermeticity from a source snapshot |

### Read, copy and apply windows

1. Enumeration → opening: constrain each open relative to a qualified root, reject unexpected links/mounts and validate file identity. String canonicalization followed by normal open leaves a swap window
2. Open → reading: same handle avoids path replacement confusion but not concurrent writes to that inode; require capture-class evidence, not only stat equality
3. Reading → content registration: verify complete byte counts/digests and source provenance; incomplete objects remain quarantined. No canonical writer lock spans a full tree scan
4. Copy/transfer → destination verification: independently verify the actual destination object, type/metadata and closure before publishing a usable materialization; copy completion or sender hash is insufficient
5. Verification → apply: current authority/base/policy and target identity must be protected until effect completion. A prior applicability check cannot stop later writes
6. Apply → receipt: durable application identity precedes dispatch; lost acknowledgement is reconciliation of the same operation, not a new patch application

Stage restoration into a new empty, contained destination. Validate names, kinds, exclusions and complete closure before exposure; never overlay an existing checkout as a hidden restore. Register materialization only after the declared byte/logical/coherence checks. A crash leaves staged/partial/uncertain state and preserved evidence, not cleanup or rollback fiction.

### Platform boundaries

D028 canonical state floors remain local NTFS on native Windows 11 25H2/build 26200 Home/Pro and qualification of 24H2/build 26100 Enterprise; x64 primary. Linux is kernel 6.12 LTS primary, 6.6 compatibility minimum, cgroup v2 and local ext4. WSL2-ext4 and WSL2 `/mnt/c` are separate development/test profiles. Canonical-state SMB/NFS, ReFS/xfs/btrfs and physical-platter interruption are out of current scope.

These are not an automatic workspace support matrix. Workspace source on a share/removable volume, cross-volume hardlinks, remote materialization, or a filesystem with different case/metadata behavior each needs an explicit support disposition and test. No network-store guarantee is supplied. VSS and filesystem freeze are source-documented mechanisms, not a selected implementation or permission to freeze a user's machine. Ext4 alone does not promise native COW snapshots. Abrupt-VM-reset replay qualification remains separate from file-copy fidelity.

<a id="ry-q16"></a>
## Q16 — Fork continuity without copied authority

**Proposal Y-R16.** A source fork proceeds through admitted source capture → lineage proposal → destination membership/privacy check → fresh materialization → exact-byte/coherence verification → canonical rebind → fresh execution admission. All are independently visible facts. A conversation branch may occur earlier without allocating any checkout or source fork. A branch/ref may be absent throughout.

Preserve original source and candidate evidence through retention pins and independent output storage. Fork source correspondence records every preserved, omitted, transformed and unknown facet. A source fork from a dirty original must reference the admitted dirty snapshot; pinning the old commit alone is not continuity. A restore cannot claim lost unsnapshotted dirty bytes were recovered. Required missing bytes yield a blocker with the last reproducible source state.

History carries forward as immutable evidence and an accounting lineage reference. Current GoalSpec/policy may authorize a fresh attenuated continuation, but no active grant, approval, lease, writer token, launch permit, reservation or balance is copied. Existing consumed amounts and uncertain liabilities remain with their canonical owners. A budget split, if allowed, is an atomic canonical reservation operation; it is neither a duplicate nor an erased uncertainty. Losing the original machine leaves its in-flight effects unknown until the relevant owner reconciles them.

Compare explicit child-workspace lineage and rebind with a new materialization/revision inside the same workspace plus a first-class fork record. Both keep old and new source evidence and fresh admission; neither treats “fork” as automatic task authority. Y-F07/Y-F17 distinguish historical continuity from unauthorized duplicate execution.

<a id="ry-q17"></a>
## Q17 — Forge and VCS neutrality

**Proposal Y-R17.** Core identities and records use opaque repository IDs, typed source refs and capability declarations. Git commit/tree/ref concepts are adapter facets, not mandatory fields for every source. A local unversioned manifest snapshot can bind a task without a remote or hosted account. Other VCS adapters may expose native revision relationships with declared loss rather than fabricating Git-shaped history.

GitHub/GitLab/editor workspaces remain optional alias/metadata adapters. Their hosted fork, visibility and issue/review relationships are not portable workspace authority. Compare a minimal generic snapshot/change interface with separately negotiated rich VCS/forge facets against a broader capability graph with per-feature required semantics. Both support a useful local-only baseline and explicit unsupported/unknown cells.

Neutrality is falsified if equivalent allowed source/binding operations require a GitHub/GitLab account, a Git branch, a particular remote named `origin`, hidden native inference, or a vendor ID in canonical identity. The fixture replays the same synthetic workflow with no VCS, Git-local and two mocked forge facets, comparing invariant outcomes rather than identical optional features. A pass does not guarantee cross-forge review, permissions, LFS or history equivalence. No product is adopted merely because its documentation supplies a comparison mechanism.

<a id="ry-q18"></a>
## Q18 — Exact evidence across route change, compaction and machine loss

**Proposal Y-R18.** The non-droppable capsule retains binding ID/revision, workspace manifest ref, complete source vector, candidate/change-set refs, capture class/coverage, profile/config/rights refs, acceptance gate, source locators, last settled effect, unresolved effects and accounting references. Raw paths/digests are disclosed only inside their permitted domain. A model summary cannot replace any of these controls.

Harness change preserves the logical binding and produces a new route-specific compiled payload plus loss report. Compaction rehydrates original source/evidence under current policy; a stale summary cannot select a newer branch. A source fork creates a new binding revision with explicit source correspondence. Lost-machine continuation uses retained admissible snapshots and new host/materialization identity; source unavailability is visible, never repaired through an unauthorized fetch.

R-X consumes these source identities through authorized artifact transfer and materialization receipts. Transport acceptance, verified destination bytes, execution admission, process start, candidate production and accepted verification remain separate. The execution host cannot become a second canonical writer or mint source authority. Work, writer, process, configuration, release, route and pause identities remain distinct; reconnect resolves current fences and unsettled operations. Copy-reader pins are not process invocation pins.

A result records input snapshot, actual candidate bytes, operation/attempt, output change set, tool/profile/config/host evidence and independent verification target. “Built on branch X” is a human label only. Compare full explicit capsule fields with opaque capsule references hydrated before admission; both reject missing critical controls. No native compactor or recovery model is silently required.

<a id="ry-q19"></a>
## Q19 — Ownership and visibility at every boundary

**Proposal Y-R19.** The canonical control plane owns workspace membership and current policy. Human/project principals own policy decisions; task grants attenuate allowed member/path/action sets. Repository author, reviewer, maintainer, source owner and accepting Owner are distinct roles. Neither a familiar path, code-owner file, remote, signature nor previous successful run widens authority.

Visibility is checked before metadata retrieval, traversal, indexing, context ranking, copy and compilation, and again on exact recipient-bound dispatch. Use R-Q copy inventory for source copies, graph/index postings, previews, temporary files, local spools, backups and external disclosures. Deletion/expiry/revocation invalidates derived references according to shared lineage rules; removing one checkout does not prove every copy erased. Content equality across private projects remains undisclosed.

Upstream harnesses receive only admitted mounted/materialized inputs, minimal output paths and bounded environment through the R-E/R-U isolation profile. Cwd and prompt instructions are not containment. Shared home/config, helper tools, symlink/hardlink aliases, plugin search and output channels need coverage. A harness unable to operate without broader access is ineligible for a strict workspace-isolation claim; preserving an artifact handle is not permission to hydrate it.

Compare per-task isolated materializations with a mediated authorized filesystem view, both with current grant intersection and controlled egress. Unknown containment blocks protected use rather than asserting success from lack of observed leaks. Synthetic-canary tests establish only their declared paths and channels, not universal secrecy or credential-boundary qualification.

<a id="ry-q20"></a>
## Q20 — Provider-free acceptance predicates

The full handoff in `UNEXECUTED-local-test-handoffs.md` and `local-test-handoffs.json` specifies inputs, prerequisites, actions, independent oracles, expected receipts, stop conditions and non-proofs for 22 fixtures. `synthetic-fixtures.json` supplies data-only case definitions, not runnable target code. There is no verified workspace target entrypoint; inventing a `recursion test-workspace` command would be misleading. All target commands remain unset until an admitted implementation exists.

| Fixture | Exact outcome predicate |
|---|---|
| Y-F01 identity stability | Explicit relocation and authorized instance association preserve workspace/repository IDs; locator/instance changes are recorded; absent association refuses |
| Y-F02 distinct workspaces | Equal tree bytes, URL/name/path hints never merge independently registered IDs; copied manifest registration is refused or explicitly adopted with fresh authority |
| Y-F03 parallel isolation | Authorized task writes alter only its candidate; original/peer bytes, refs/config and shared resources remain unchanged unless separately admitted |
| Y-F04 stale binding | Any changed required manifest/source/config/profile/rights/fence ref refuses effect before dispatch; unchanged valid binding completes the bounded control |
| Y-F05 invalidation on commit | Old graph cannot return valid-at-new-source results; fresh oracle parity holds for declared coverage, with unknown regions explicit |
| Y-F06 snapshot round-trip | Exact included bytes/types and declared logical index state reproduce; all omitted/unsupported facets are visible and block required fidelity |
| Y-F07 fork continuity | Dirty captured source survives to new materialization; original unchanged; live authority/reservations not copied; fresh attenuated admission required |
| Y-F08 dirty/merge handling | Index/working/stage differences preserved; unsupported in-progress operation refuses without stash/reset/clean/merge |
| Y-F09 neutrality | Useful local-only operation needs no forge identity, Git branch or provider; declared optional facet losses remain visible |
| Y-F10 secret exclusion | Excluded synthetic bytes and restricted path/digest metadata absent from every unauthorized sink; bypass traces refuse before exposure |
| Y-F11 default inertness | Binding invokes no model/indexer/import/watcher/timer/helper/network activation; measured active probes demonstrate detector sensitivity |
| Y-F12 authority non-expansion | Identical canonical request/grants have identical admission despite malicious workspace/profile/branch/history content |
| Y-F13 watcher/config gaps | Loss/overflow/config-only/file-move cases mark stale/unknown until justified reconstruction; never false absent/complete |
| Y-F14 ABA capture | A non-coexistent mixed set cannot receive coherent status even with equal endpoint hashes; true immutable/quiescent capture passes its class |
| Y-F15 path/link races | Symlink/reparse/ancestor swaps and out-of-scope hardlink alias writes cannot escape admitted read/copy/apply scope |
| Y-F16 clone/worktree/ref semantics | Clone instance, repository lineage, branch observation and worktree identity remain separate; ambiguous same-byte origin refuses |
| Y-F17 lost-machine liabilities | Recovery preserves historical evidence and unsettled effect/reservation ownership; old host tokens cannot authorize new effects |
| Y-F18 private membership oracle | Unauthorized observations meet the declared alias/size/error/timing contract and no cross-project object/cache sharing occurs |
| Y-F19 apply/check race | Target divergence after preview refuses or remains isolated; no stale-base partial success; lost ACK reconciles same operation |
| Y-F20 sparse/LFS/submodule closure | Missing required objects remain unavailable; no fetch/helper/network effect; pointer-only result cannot claim materialized bytes |
| Y-F21 cross-platform restore | Representable data matches declared relation on each pinned profile; collisions/loss refuse exact status; no floor extrapolation |
| Y-F22 non-linear graph | Rebase/amend/squash/delete retain immutable historical refs and many-to-many lineage; a review never silently retargets |

A pass is an independently verified, exact-source/profile/corpus-scoped result. Research coverage is not runtime qualification. Unknown or unrun is not zero passes or a failed product claim; it is an explicit missing observation.

<a id="ry-q21"></a>
## Q21 — Default no-work, grant and privacy proof obligations

Y-F11 compares absent indexer, installed-disabled indexer, enabled-idle and explicitly active states. Independent tripwires cover module import, executable start, subprocess/thread/timer/watcher, network, filesystem enumeration/read, context/tool enumeration, model/provider request, reservation/debit and event subscriptions. The bind-only arm may perform bounded canonical identity/policy lookup and emit its normal receipt; this attributable metadata cost is measured separately. Trap calibration deliberately activates each detector in a contained synthetic control. Fixture counters initialized to zero are not observations.

Y-F12 mutates untrusted profile content, names, commit signatures, old approvals, manifests and conversation forks while holding canonical request/grants fixed. Any authority difference is a failure. Negative requests must be refused before protected effect admission; positive least-privilege controls prevent “refuse everything” from passing. Fork tests preserve prior liabilities without duplicating or dropping them.

Y-F10/Y-F18 use synthetic secret and path canaries across permitted and forbidden projects. Inspect captures, logs, indexes, previews, manifests, errors, transport payloads, remote spool and external mock sink, including filenames and equality handles. Exclusion and audience checks must precede unauthorized source hydration. No provider call, auth file or real credential participates. Timing observations are bounded experiments with preregistered adversary and acceptance rule; they do not prove absence of every side channel. Fixture runtime itself is UNEXECUTED here.

<a id="ry-q22"></a>
## Q22 — What the candidate does not establish

No measured invalidation accuracy, traversal/index cost, snapshot fidelity, retention durability, latency, scale, savings or productive-continuity advantage follows. No snapshot is claimed to capture every host input, secret, service, toolchain, environment variable or human context. No semantic correctness, build reproducibility, rights clearance, attribution correctness or security of a change set follows from hashing it.

No cross-forge feature/permission equivalence, remote-store durability, universal filesystem support, all-interleaving atomic capture, unlimited history, zero metadata overhead, universal secret detection, traffic-analysis resistance or complete upstream containment is established. A verified committed source pin proves no unseen dirty work. A source fork does not transfer active authority, reservations or process ownership, and an offline source remains unknown. No technology choice or route qualification has been made.

Blocked decisions have precise next steps: Y-F14/Y-F15 establish admissible capture/isolation profiles; Y-F06/Y-F21 establish preservation relations per platform; Y-F05/Y-F13 compare invalidation correctness and costs; Y-F10/Y-F18 constrain privacy claims; Y-F07/Y-F17/Y-F19 establish continuity/application evidence before any end-to-end D024 claim. Run them only in an explicitly admitted disposable synthetic local session against a pinned candidate, with independent verification. Passing those bounded fixtures still requires later whole-workflow comparison under R-W.

<a id="ry-application"></a>
## Application contract — candidate bytes are not an approved write

**Proposal Y-R20.** Applying a candidate is a separately admitted effect, not part of identity lookup, snapshot restoration, conversation fork or graph refresh. `ApplicationIntent` binds stable operation/command identities, exact base and desired candidate, destination materialization/generation, path operations, policy/authority and distinct work/writer/process/configuration/release/pause fences. A review receipt names the exact candidate. A valid review alone cannot authorize application.

Compare staged immutable candidate publication into a newly admitted materialization against protected in-place application with a qualified exclusive mutation boundary and retained per-path evidence. Both require explicit authorized targets and recovery semantics. If the in-place profile cannot exclude all writers and protect the check-to-write interval, it is ineligible; a bare check-then-apply sequence is a negative control. Multi-file in-place completion is not advertised atomic without independent platform evidence.

Record prepared, durably admitted, dispatched, partially applied, observed, independently verified, refused and uncertain separately. A lost acknowledgement queries/reconciles the original operation. No repeated patch, new operation ID, overwrite, stash, reset, clean, merge, rebase or fetch is an automatic repair. A partial application retains original/candidate evidence and requires a new authorized reconciliation action when needed. Evidence verification does not silently commit, publish or merge. Y-F19 is the decisive stale-base and lost-reply probe.

<a id="ry-sources"></a>
## Appendix A — Primary public-source fact sheet

These source-documented facts are bounded premises. The design and falsifiers above are proposals, not vendor guarantees or Recursion observations. Registers record date/version/hash limits.

<a id="ry-source-y-s01"></a>
### Y-S01 — Git worktree manual

Linked worktrees share repository data but have per-worktree HEAD/index and some refs. Shared configuration requires explicit handling. Move/remove/repair and administrative locking have distinct semantics. A worktree is not an isolated authority domain. [Primary source](https://git-scm.com/docs/git-worktree/2.56.0)

<a id="ry-source-y-s02"></a>
### Y-S02 — Git glossary

Git distinguishes commits, trees, blobs, refs, index and working tree. A content object and a mutable name are different identities. The glossary is descriptive of Git, not a generic workspace identity or access-control contract. [Primary source](https://git-scm.com/docs/gitglossary/2.56.0)

<a id="ry-source-y-s03"></a>
### Y-S03 — Git status manual

Porcelain formats are intended for machine parsing; version 2 distinguishes detailed working/index states and unmerged entries. Status is an observation, not an atomic multi-file snapshot or a promise that all ignored content was captured. [Primary source](https://git-scm.com/docs/git-status)

<a id="ry-source-y-s04"></a>
### Y-S04 — Git attributes manual

Attributes can change line endings, encoding and clean/smudge behavior; configured filters can execute processes. Stored object bytes and checked-out bytes can differ. Attribute/config identity therefore matters to byte-preservation claims. [Primary source](https://git-scm.com/docs/gitattributes/2.56.0)

<a id="ry-source-y-s05"></a>
### Y-S05 — Git sparse-checkout manual

Sparse checkout controls which tracked paths appear in the working directory; sparse-index behavior is a separate mechanism. Non-materialized paths are not necessarily absent from the repository. [Primary source](https://git-scm.com/docs/git-sparse-checkout)

<a id="ry-source-y-s06"></a>
### Y-S06 — Git submodules manual

A submodule has independent history. The superproject gitlink records an expected commit, while .gitmodules supplies location hints. That pin does not contain the nested working tree, dirty state or every required object. [Primary source](https://git-scm.com/docs/gitsubmodules)

<a id="ry-source-y-s07"></a>
### Y-S07 — Git partial clone design

Partial clones can omit objects and retrieve missing ones dynamically. Object lookup can lead to a fetch subprocess; missing-object handling must therefore be explicit in a no-network read profile. [Primary source](https://git-scm.com/docs/partial-clone/2.56.0)

<a id="ry-source-y-s08"></a>
### Y-S08 — Git pack format

Packfiles may hold compressed and delta-encoded objects. Object IDs remain tied to reconstructed object content/type rather than a particular pack layout; SHA-1 and SHA-256 repositories use different object/checksum identities. [Primary source](https://git-scm.com/docs/gitformat-pack)

<a id="ry-source-y-s09"></a>
### Y-S09 — Git update-ref manual

Ref updates can verify an expected old object and group updates. The manual warns that concurrent readers may observe a subset of multiple ref modifications even though each individual ref update is atomic. [Primary source](https://git-scm.com/docs/git-update-ref)

<a id="ry-source-y-s10"></a>
### Y-S10 — Git apply manual

Applicability checking and applying are distinct operations. --index has joint index/working-tree requirements. Applying a patch does not create a commit. These behaviors do not make an earlier check safe against subsequent concurrent edits. [Primary source](https://git-scm.com/docs/git-apply)

<a id="ry-source-y-s11"></a>
### Y-S11 — Git hooks manual

Git hooks are programs invoked at defined operation boundaries. Their presence and configuration are part of an execution profile, not inert repository prose or an independent authorization mechanism. [Primary source](https://git-scm.com/docs/githooks)

<a id="ry-source-y-s12"></a>
### Y-S12 — Git index format

The index contains entry metadata and object references; conflict stages and extensions carry state beyond a single root tree. Raw index representation and logical index meaning are distinct portability concerns. [Primary source](https://git-scm.com/docs/gitformat-index)

<a id="ry-source-y-s13"></a>
### Y-S13 — Git configuration manual

Git configuration includes filesystem-monitor, helper and other command behavior. A constrained adapter must account for effective configuration instead of equating a nominally read-oriented command with effect-free execution. [Primary source](https://git-scm.com/docs/git-config/2.56.0)

<a id="ry-source-y-s14"></a>
### Y-S14 — Git LFS pointer specification

LFS pointer text carries a version, hash-qualified object ID and byte size; large object storage is distinct from that Git blob. Its clean/smudge integration can materialize different bytes than the pointer. [Primary source](https://raw.githubusercontent.com/git-lfs/git-lfs/v3.7.0/docs/spec.md)

<a id="ry-source-y-s15"></a>
### Y-S15 — Linux openat2 manual

The [common resolution premises](../re/report.md#object-resolution-facts) also apply here. Additional SD: openat2 supports handle-relative beneath-root, no-symlink and no-magic-link constraints; O_NOFOLLOW alone constrains only the final component. These primitives do not supply a multi-file snapshot. [Primary source](https://man7.org/linux/man-pages/man2/openat2.2.html)

<a id="ry-source-y-s16"></a>
### Y-S16 — Linux inotify manual

inotify queues can overflow and lose events. Applications must recover their view rather than assuming an event stream proves complete current filesystem state. [Primary source](https://man7.org/linux/man-pages/man7/inotify.7.html)

<a id="ry-source-y-s17"></a>
### Y-S17 — Windows reparse points

Reparse points attach filesystem behavior to stored reparse data and tags. Treating every directory-looking entry as ordinary traversal can cross an unintended boundary. [Primary source](https://learn.microsoft.com/en-us/windows/win32/fileio/reparse-points) Shared OS context: [resolution premises](../re/report.md#object-resolution-facts).

<a id="ry-source-y-s18"></a>
### Y-S18 — Windows ReadDirectoryChangesW

The API can report that not all changes were recorded and require enumeration. Change notifications therefore cannot by themselves certify a complete source map. [Primary source](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-readdirectorychangesw)

<a id="ry-source-y-s19"></a>
### Y-S19 — Windows names and namespaces

Windows file APIs impose naming, namespace, reserved-name, case and path semantics that differ from arbitrary repository byte strings. Exact restoration needs representability and collision checks, not only content hashes. [Primary source](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file)

<a id="ry-source-y-s20"></a>
### Y-S20 — Linux link manual

A hard link adds another name for the same file. A separate path name does not imply independent mutable storage, so path-only isolation can miss aliases. [Primary source](https://man7.org/linux/man-pages/man2/link.2.html)

<a id="ry-source-y-s21"></a>
### Y-S21 — Windows hard links and junctions

Windows distinguishes file hard links from junctions. Hard-linked names share a file; junctions can redirect directory access. Both matter to copy/isolation policies. [Primary source](https://learn.microsoft.com/en-us/windows/win32/fileio/hard-links-and-junctions)

<a id="ry-source-y-s22"></a>
### Y-S22 — Why Google stores billions of lines in one repository

The authors describe a very large monolithic repository, supporting systems and tradeoffs. This documents a scale problem and specialized infrastructure, not a Recursion capacity target or measured need for a particular store. [Primary source](https://research.google/pubs/why-google-stores-billions-of-lines-of-code-in-a-single-repository/)

<a id="ry-source-y-s23"></a>
### Y-S23 — Build Systems à la Carte

The paper separates scheduling and rebuilding strategies and studies dynamic dependencies and early cutoff. Correct reuse depends on what dependencies are tracked; its models do not prove a Recursion repository map complete. [Primary source](https://www.microsoft.com/en-us/research/wp-content/uploads/2018/03/build-systems-final.pdf)

<a id="ry-source-y-s24"></a>
### Y-S24 — Bazel hermeticity

Hermetic builds depend on controlled tools/dependencies as well as source identity. Host binaries, environment and stateful source writes can break reproducibility; a source snapshot alone does not establish a hermetic build. [Primary source](https://bazel.build/basics/hermeticity)

<a id="ry-source-y-s25"></a>
### Y-S25 — Aider repository map

Aider describes symbol-oriented repository context and graph-ranked selection within a token budget. This is a selective context representation, not proof that every dependency or symbol is present in a delivered map. [Primary source](https://aider.chat/docs/repomap.html)

<a id="ry-source-y-s26"></a>
### Y-S26 — DupLESS

Use the [canonical DupLESS note](../rq/report.md#e09). **Proposal:** avoid public equality oracles; the research does not authorize cross-project deduplication or establish this candidate cryptographically secure.

<a id="ry-source-y-s27"></a>
### Y-S27 — GitHub forks

GitHub forks participate in a repository network with platform-specific visibility and deletion behavior. Hosted fork metadata is not a portable task, authority or local-source snapshot contract. [Primary source](https://docs.github.com/en/pull-requests/reference/forks)

<a id="ry-source-y-s28"></a>
### Y-S28 — GitLab forks

GitLab describes a namespace-local project fork with repository and selected settings, excluding some other project content. Its visibility and relationship rules are platform-specific and require explicit loss mapping. [Primary source](https://docs.gitlab.com/user/project/repository/forking_workflow/)

<a id="ry-source-y-s29"></a>
### Y-S29 — VS Code multi-root workspaces

An editor workspace can list multiple folder paths and settings, with separate folder naming and scope rules. This is a useful presentation/import surface, not durable source identity or authority. [Primary source](https://code.visualstudio.com/docs/editing/workspaces/multi-root-workspaces)

<a id="ry-source-y-s30"></a>
### Y-S30 — VSS backup processing overview

VSS backup processing coordinates requesters, writers and providers around shadow-copy creation. A usable application-consistent capture depends on the participating scope and process; a documentation reference does not qualify a Recursion NTFS capture profile. [Primary source](https://learn.microsoft.com/en-us/windows/win32/vss/overview-of-processing-a-backup-under-vss)

<a id="ry-source-y-s31"></a>
### Y-S31 — Linux fsfreeze manual

Filesystem freeze suspends modifications for a supported filesystem and is intended for snapshot-related operations. It is not itself a complete snapshot implementation, portable all-volume transaction or permission to freeze a live workspace host. [Primary source](https://man7.org/linux/man-pages/man8/fsfreeze.8.html)

<a id="ry-recommendations"></a>
## Appendix B — Competing designs, falsifiers and non-proofs

All alternatives below preserve fixed authority/privacy/ownership invariants. Negative controls are deliberately invalid and are not the sole competitor. No candidate is selected.

### Y-R01 — Identity resolution

- Candidate: Registered manifest resolver with explicit move/clone association
- Admissible rival: Path or remote alias resolver backed by the same canonical stable IDs and explicit association
- Decisive falsifier: Admitted move splits identity, equal bytes merge distinct registrations, or copied manifest self-authorizes
- Passing non-proof: Stability does not prove source fidelity or access rights
- Negative control only: Pure path/URL/commit identity
- Discriminating fixtures: Y-F01, Y-F02, Y-F16

### Y-R02 — Snapshot identity

- Candidate: Typed manifest content address with explicit logical/raw/coherence facets
- Admissible rival: Separate typed component manifests with one sealed closure receipt
- Decisive falsifier: Two distinct promised states share admitted identity, or a missing component receives complete status
- Passing non-proof: Digest does not prove coherent capture or durable availability
- Negative control only: Commit hash alone for dirty work
- Discriminating fixtures: Y-F06, Y-F14, Y-F20

### Y-R03 — Private addressing

- Candidate: Per-audience random external handles with project-private content maps
- Admissible rival: Domain-keyed internal names plus independently randomized external handles
- Decisive falsifier: Cross-project equality, unauthorized metadata or observable cache membership violates declared contract
- Passing non-proof: No universal traffic-analysis/cryptographic security proof
- Negative control only: Global private-content digest/dedup namespace
- Discriminating fixtures: Y-F10, Y-F18

### Y-R04 — Binding

- Candidate: Eager exact source/profile vector sealed at admission
- Admissible rival: Lazy hydration with same exact vector sealed before use
- Decisive falsifier: Ambiguous/stale source is guessed or any required ref changes without readmission
- Passing non-proof: A valid binding is not current effect authority
- Negative control only: Cwd or branch name accepted as binding
- Discriminating fixtures: Y-F04, Y-F12

### Y-R05 — Multi-repo coupling

- Candidate: Manifest-wide exact source vector
- Admissible rival: Independent member bindings plus immutable coupling receipt
- Decisive falsifier: Required coupled task silently runs with mixed incompatible member vector
- Passing non-proof: Does not provide multi-repository atomic VCS update
- Negative control only: Assume all repos commit atomically
- Discriminating fixtures: Y-F04, Y-F09, Y-F22

### Y-R06 — Parallel materialization

- Candidate: Linked worktrees plus fenced shared-administration operations
- Admissible rival: Independent private materializations from the same source closure
- Decisive falsifier: One task mutates peer/original/shared refs outside admitted resources
- Passing non-proof: File isolation does not prove environment/network isolation
- Negative control only: Shared checkout without enforced writer exclusion
- Discriminating fixtures: Y-F03, Y-F15, Y-F16

### Y-R07 — Monorepo traversal

- Candidate: Demand-bounded tree/diff reads with explicit coverage
- Admissible rival: Opt-in persistent incremental index with identical policy and bounds
- Decisive falsifier: Bind starts an indexer/full walk, or bounded query mislabels missing coverage
- Passing non-proof: No scale or cost benefit follows before measurement
- Negative control only: Unbounded full traversal on every task
- Discriminating fixtures: Y-F05, Y-F11, Y-F13, Y-F20

### Y-R08 — Profile resolution

- Candidate: Eager deterministic per-repo compilation with restrictive policy meet
- Admissible rival: Demand compilation cached by complete input and rights revisions
- Decisive falsifier: Repo override defeats deny, command activates silently, or changed policy reuses stale output
- Passing non-proof: Schema correctness does not prove command safety
- Negative control only: Last-read-file wins authority
- Discriminating fixtures: Y-F04, Y-F12

### Y-R09 — Checkout concurrency

- Candidate: Per-task writable contexts with shared-resource permit serialization
- Admissible rival: Enforced single-mutator shared checkout with immutable/isolation-qualified readers
- Decisive falsifier: Unmanaged writer can alter admitted target inside claimed protected interval
- Passing non-proof: No all-host exclusion guarantee from cooperative locks
- Negative control only: Advisory mutex claimed as universal containment
- Discriminating fixtures: Y-F03, Y-F14, Y-F19

### Y-R10 — Change history

- Candidate: Canonical append-only typed change events plus derived graph
- Admissible rival: Canonical per-change immutable receipts with on-demand graph reconstruction
- Decisive falsifier: Rewrite discards historical candidate or retargets a review without new evidence
- Passing non-proof: No semantic patch equivalence or acceptance
- Negative control only: Single linear branch history as task truth
- Discriminating fixtures: Y-F22

### Y-R11 — Source graph

- Candidate: Typed observed object graph plus separately labeled interpretations
- Admissible rival: Sparse on-demand typed graph reconstructed from immutable source and canonical facts
- Decisive falsifier: Inferred import/owner edge becomes authority or unsupported language becomes complete-empty
- Passing non-proof: No universal dependency completeness
- Negative control only: One unlabeled graph for authority and similarity
- Discriminating fixtures: Y-F05, Y-F12, Y-F22

### Y-R12 — Invalidation

- Candidate: Exact dependency-trace incremental reconstruction
- Admissible rival: Fresh bounded rebuild of the same admitted frozen set
- Decisive falsifier: Valid-at-current query differs from independent fresh oracle or hides unknown inputs
- Passing non-proof: No measured accuracy/cost outside corpus
- Negative control only: Watcher-only complete map
- Discriminating fixtures: Y-F05, Y-F13

### Y-R13 — Attribution

- Candidate: Path-level provenance with explicit span/blob exceptions
- Admissible rival: Span/blob-first provenance with aggregated restricted views
- Decisive falsifier: Influential input or license boundary is silently dropped in a derivative
- Passing non-proof: No originality, ownership or legal clearance
- Negative control only: Signature or public URL grants rights
- Discriminating fixtures: Y-F10, Y-F12, Y-F22

### Y-R14 — VCS boundary

- Candidate: Pinned user Git under qualified constrained broker
- Admissible rival: Alternative adapter implementation for an explicitly declared subset and same corpus
- Decisive falsifier: Nominal read runs unadmitted helper/fetch or adapter loss is hidden
- Passing non-proof: No implementation/vendor selected or whole-Git equivalence
- Negative control only: Every Git read intrinsically side-effect-free
- Discriminating fixtures: Y-F08, Y-F20

### Y-R15 — Coherent capture

- Candidate: Admitted immutable closure or qualified storage-snapshot read view
- Admissible rival: Enforced all-relevant-writer quiescence for declared capture scope
- Decisive falsifier: Mixed-time/ABA set receives coherent status or required metadata silently changes
- Passing non-proof: No complete host/environment snapshot or durability guarantee
- Negative control only: Before/after digest equality proves atomic snapshot
- Discriminating fixtures: Y-F06, Y-F14, Y-F15, Y-F21

### Y-R16 — Fork continuity

- Candidate: Child workspace lineage plus new binding and admission
- Admissible rival: New materialization in same workspace with explicit fork lineage and new binding
- Decisive falsifier: Original mutates, dirty bytes disappear, or active grants/reservations duplicate
- Passing non-proof: No productive-continuity superiority without whole-workflow evidence
- Negative control only: Conversation fork clones authority or source implicitly
- Discriminating fixtures: Y-F07, Y-F17

### Y-R17 — Neutrality

- Candidate: Generic snapshot/change core with optional rich VCS/forge facets
- Admissible rival: Capability-negotiated broader adapter graph with same local-only baseline
- Decisive falsifier: Core requires forge/account/branch/vendor identity or hides optional-feature loss
- Passing non-proof: No cross-forge functional/permission equivalence
- Negative control only: GitHub or Git identity mandatory everywhere
- Discriminating fixtures: Y-F09

### Y-R18 — Continuity evidence

- Candidate: Full non-droppable exact binding controls in capsule
- Admissible rival: Opaque capsule ref hydrated and revalidated before admission
- Decisive falsifier: Route/compaction/recovery loses exact source or uncertain effects and resumes anyway
- Passing non-proof: No hidden inference permission or route qualification
- Negative control only: Summary text/branch label is sufficient recovery
- Discriminating fixtures: Y-F04, Y-F07, Y-F17

### Y-R19 — Ownership boundary

- Candidate: Per-task isolated admitted input/output materializations
- Admissible rival: Mediated authorized filesystem view with equivalent source and egress controls
- Decisive falsifier: Unauthorized source/path metadata is hydrated or exported, or cwd is treated as isolation
- Passing non-proof: No universal containment or secret-detection proof
- Negative control only: Prompt-only stay in workspace instruction
- Discriminating fixtures: Y-F10, Y-F12, Y-F15, Y-F18

### Y-R20 — Candidate application

- Candidate: Stage immutable candidate and expose a new admitted materialization
- Admissible rival: Qualified protected in-place application with exact base and partial-state receipts
- Decisive falsifier: Stale-base write succeeds or lost ACK causes duplicate application
- Passing non-proof: No atomic multi-file durability or semantic correctness without evidence
- Negative control only: Unprotected check-then-apply with cleanup fallback
- Discriminating fixtures: Y-F19

<a id="ry-qa"></a>
## Appendix C — Coverage and artifact verification

The exact 22 questions and 11 completion-gate bullets are mapped in `coverage.json`, with report anchors and explicit runtime status. The contract, 20 recommendation records and 22 local handoffs are machine-readable. No verified target entrypoint exists; no fabricated runnable command is supplied.

Artifact-only QA parses JSON, verifies counts/IDs/anchors and internal references, checks source-input hashes against the supplied independently verified committed manifest, checks restricted-path/credential-pattern absence in deliverables, and hashes the final files. These are document checks, not workspace, Git, filesystem, provider, performance or recovery tests. The protected non-credential governance files match their initial snapshot identities. No repository write was performed; authentication/credential files were not read.

The scan found no private absolute execution/capture paths or credential-shaped values in this output. Synthetic canaries are explicitly marked harmless fixture data. A bounded pattern/content review does not prove universal absence of sensitive data, nor is it independent acceptance. Final review remains pending. Source-register page hashes are null because full page bytes were not captured; local input hashes and output hashes have narrower, explicit meanings.

Delivered research files: `report.md`, `candidate-contracts.json`, `recommendations.json`, `source-register.json`, `source-register.md`, `input-pins.json`, `coverage.json`, `synthetic-fixtures.json`, `local-test-handoffs.json` and `UNEXECUTED-local-test-handoffs.md`. [Packet quality notes](../QUALITY-NOTES.md) and the [global manifest](../MANIFEST.json) describe release verification and delivered bytes; per-report production logs and duplicate source-usage bookkeeping are not bundled.
