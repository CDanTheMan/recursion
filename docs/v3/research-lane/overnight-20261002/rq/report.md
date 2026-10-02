# Durable memory and knowledge architecture

Research candidate R-Q · 2 October 2026 UTC · source snapshot 73d70505b8c266fbb08d820d304ebd2e68ac7f1b

## Decision summary

Build the required opt-in memory capability around **a disposable, revocable projection of admitted evidence**, with exact canonical references and a complete transformation lineage. Keep current authorization, accepted decisions, deletion policy and operational recovery in the existing canonical control plane. Memory may help find evidence; it may never make an instruction accepted, mint a grant, settle an effect, or satisfy an acceptance gate.

The candidate advance is not that text persists. Editable files and provider-native products already supply meaningful memory mechanisms. The testable advance is continuity of the same task's authority, provenance, privacy, unresolved state and accounting across compaction, machine loss and harness change. Recall quality, total cost and portability benefit remain unknown. A well-maintained file baseline may win.

This report answers all 19 questions and 10 completion bullets. Every behavioral mechanism below is **inferred design**, not an implemented guarantee. All local handoffs are **UNEXECUTED**. Artifact checks concern these deliverables only. No route, account, language, store, database, vector index, embedding model, framework or vendor is selected or qualified.

## Evidence and governance

Four evidence classes apply throughout: **SD** source-documented; **LO** locally observed static source or artifact bytes; **IN** inferred candidate design; **U** unknown or unmeasured. A source describing an experiment is SD about that experiment, not a local observation. Null metrics carry a reason, never a zero.

The current governance and accepted D018–D033 constrain this candidate. D019 requires comprehensive capability built and shipped opt-in; off-by-default is not a release deferral. D020 retains one fenced writer with a separate opt-in availability backend. D022 fixes Aggressive/Full/Lazy plus checkpoint/interrupt/drain. D023 is qualification priority, not qualification. D024 requires productive continuity; D029 bars credential exposure through memory or unconstrained tool output; D030 stream access supplies no blanket reuse rights; D031 excludes vendor-intent claims. D033 leaves porting cost unmeasured. TUI-first and later GUI use one memory query/command backend; this report does not resolve the timing tension between older GUI prose and comprehensive D019 release scope.

LO: the pinned CONTEXT specification already requires scoped artifacts, exact control references, one compaction governor, and revalidation before hydration. DS07 supplies the existing copy/key-ledger deletion contract, DS12 separates context and provider caches, DS30 separates durable intent from generated observations, DS02 separates authority from evidence, and DS14 gates rights before full-text access. This report extends their semantic-memory consequences. The current coverage map's final lane assignment list is stale: R-P owns untrusted inputs, R-Q memory, R-T multimodal artifacts.

LO: static inspection of RIntegrated.tla finds explicit absence of principals, authority dimensions, replay/projection monitors and packet derivation; its effective constants are CmdIds 1..4 and MaxEvents 6 despite an older comment. The FU03 README records reduced-bound historical runs, not a memory qualification. The effect-evidence helper uses exact versioned object references and a separate oracle; that is a reusable *shape*, not evidence of a deployed memory subsystem. No memory-specific entrypoint was verified. Existing source files were only read, never imported or executed. Repository-relative pins are in [input-pins.json](input-pins.json).

The [shared evidence index](../shared-evidence/source-facts.md) is the canonical home for route and protocol facts; none is repeated here. R-P's [candidate envelope and mediation contract](../rp/proposed-contracts.json) is a draft integration dependency. R-H's [output reuse questions](../rh/report.md) remain the legal gate. R-T owns media representations, selectors and modality-specific loss; memory uses that shared artifact reference, without creating another attachment owner.

<a id="q01"></a>
## Q01 Typed records and provenance

The proposed logical record `MemoryProjection` has a closed, versioned shape. Its durable parent is an admitted canonical evidence/source receipt, not a free-floating note. A source receipt authenticates the fact that a claim was observed and retained under policy; it does not make the claim true. The record is immutable within a revision. Corrections, expiry, supersession and revocation are separately ordered canonical metadata events, then projected into current views.

| Field group | Required meaning |
|---|---|
| Identity | Schema version, opaque scope-local record and revision IDs, type, projection generation, canonical input cursor and source-reference set |
| Claim | Bounded subject/predicate/value or concise claim; validity interval; explicit ambiguity; units and source timezone where relevant; absent values typed unknown |
| Provenance | Source artifact ID and revision, authorized locator, observed-at and recorded-at timestamps, original author kind and claimed identity, authenticated origin or unknown, capturing actor, evidence class and source receipts |
| Transformation | Parent artifact revisions, complete possible-influence set, transform/version/config identity, extraction method, output integrity identity within the privacy domain, loss/coverage map |
| Trust | Separate integrity/authenticity/confidentiality dimensions; R-P taint union; confidence value or null, method, calibration population and independent evidence references |
| Scope and rights | User, project, goal, allowed audiences and recipients, purpose constraints, rights-policy reference, permitted retention/replay/redisplay operations, destination restrictions |
| Validity | Source revision, current-status lookup reference, observed policy revisions, expiry time or explicit policy-governed none/unknown, revocation/supersession references and conflict group |
| Non-authority | Fixed authority-carried value `none`; references to accepted decisions resolve separately against current canonical state |
| Disclosure and copies | Lineage registration receipt and governed copy inventory references; exposure operation references, never recipient credentials |

Four tagged payloads keep important differences explicit:

- Fact: proposition, evidence and valid-time interval. An environment observation is not a timeless fact. A tool's successful return may evidence its own report, not the external postcondition
- Preference: whose preference, explicit versus inferred origin, applicability conditions, direct-confirmation receipt if any, and scope. An inferred preference is proposed personalization, never an instruction or consent
- Decision summary: exact canonical decision and acceptance references, selected option and stated reasons, alternatives and supersession. The remembered text cannot mark a proposal accepted; missing decision resolution makes the summary unusable as a current decision
- Lesson: situation, observed action/outcome/evidence, applicability boundaries, counterexample and hypothesis. A correlation is not a proven cause, and a useful procedure is not permission to execute it

Confidence concerns epistemic support, not permission. A numerical score without calibration remains an uncalibrated estimate; use null rather than fabricated certainty. Creation, observation, valid time and last retrieval are distinct. Do not reset freshness when a summary is retrieved or rewritten. [Candidate contracts](candidate-contracts.json) give field types, lineage records and validation predicates. W3C prior art is summarized once in [E01–E02](#e01); no PROV serialization is selected.

<a id="q02"></a>
## Q02 Derived projection and canonical precedence

There are five distinct objects: (1) canonical control events and accepted decisions; (2) retained source artifacts with admitted provenance/rights receipts; (3) semantic memory projections; (4) indexes, embeddings and caches; (5) current model-visible context and summaries. Only the existing fenced canonical writer admits control events or adoption. A source artifact is evidence, not an accepted instruction. A projection store has authority over neither its source nor its own current usability.

Capture consumes a canonical input cursor and eligible source references. It stages an inert candidate, validates schema/lineage/scope/rights, registers the derivative and its known copies through the existing admission path, then publishes a rebuildable projection generation. An interrupted registration cannot expose the staged bytes. Storage of a source artifact is itself governed; newly imported content receives a non-authority evidence receipt before it becomes a projection root. No model may manufacture that receipt.

A rebuild from the same source/revision/transform should retain the same *meaning and lineage*, not necessarily identical generated prose. Where a stochastic transform cannot reproduce bytes, retain the actual candidate identity and verification evidence or mark it irreproducible; do not pretend a seed proves equivalence. Query results include their canonical high-water mark and validity dependencies. A stale index is a locator only; current source status is checked separately. Memory failure must degrade to source-backed retrieval, abstention or explicit unavailability without changing canonical truth.

Canonical instructions/decisions are loaded through their exact current references outside the similarity ranker. Thus an old summary does not compete with an accepted decision for a higher numerical score. Conflicting canonical records follow existing governance and acceptance rules; memory cannot resolve that constitutional conflict.

<a id="q03"></a>
## Q03 Excluding authority by construction

The effect-admission API accepts authenticated command identity, current GoalSpec/grants/policy/recipient, exact effect and data, budget and separate writer/work/Stop/configuration fences. It does not accept a memory confidence score, memory type, retrieval count, model statement of consent or imported decision status as a grant. A memory reference is permitted only in an evidence field. Resolving an authority reference requires the existing authenticated canonical resolver; a copied identifier alone is not an approval.

Current read authorization is checked before even disclosing a candidate's sensitive metadata; payload hydration, prompt compilation and actual recipient dispatch each recheck relevant policy. Model context never receives authority to repair missing grants. A signed note, authenticated human authorship, repeated preference, valid source digest or high recall score remains insufficient. The same rules apply after export, import, compaction and fork. Forks copy admissible evidence, not live leases, reservations or approvals.

Two invariants are separate: `memory changes do not change effective authority` and `requested action is admitted only by current canonical authorization`. The first prevents grant laundering; the second prevents stale execution despite a correct memory. The same canonical state with different memory contents must produce the same authorization decision for the same exact effect. A changed *proposed action* still receives a fresh check. Tests F09/F10 deliberately supply malicious grant-like preferences and stale decision summaries.

<a id="q04"></a>
## Q04 Recoverable state without hidden reasoning

Persist only explicit task state: accepted decision references, concise reasons intended as explanations, source/evidence pointers, attempted actions and receipts, uncertainties, blockers and bounded next-step proposals. A rationale is an attributable, reviewable explanation of a choice and may be incomplete. It is not a reconstruction of the model's internal reasoning.

The ingress allowlist rejects hidden reasoning channels, opaque reasoning/replay tokens, internal scratch traces and unknown typed fields from the memory path. Do not request, decode, display or retain these as memory, including in debug logs, dead-letter queues, export archives or backups. If a supported harness needs opaque session state for its own continuation, that is a separately governed session facility; R-Q gives no permission to persist it or label it portable memory. Lossy summaries cannot replace exact pending approvals, directives or unsettled-effect receipts.

Schema rejection is necessary but insufficient: a model can place unwanted text inside an allowed string. Therefore deterministic source/field allowlists, bounded extraction from approved visible artifacts, explicit producer contracts and independently reviewed samples are needed. F11 can prove rejection of supplied synthetic forbidden-channel canaries, not universal semantic recognition of hidden reasoning. Unexpected content is refused without copying its raw body into a diagnostic. R-P owns broader detection/taint, and the strict authority floor remains independent of a detector's score.

<a id="q05"></a>
## Q05 Scoped retrieval and ordering

The candidate query pipeline is: authenticate requester and exact destination → resolve project/goal/purpose and current policy → select permitted metadata partitions → find eligible candidate references → check canonical validity/revocation → hydrate minimum permitted bytes → assemble exact control kernel plus labelled evidence → recheck disclosure at dispatch. Searching globally and filtering after similarity is prohibited for private content. Query embedding is itself processing/possible egress of the query and requires an admitted route; off or unsupported cannot silently invoke a model.

Eligibility precedes ranking. Exclude unknown provenance, revoked or expired roots, unresolved rights, incompatible purpose/audience and source divergence from ordinary current answers. Historical retrieval is a distinct, authorized query: an old value may be shown as history with its valid interval, never relabelled current.

Within eligible evidence, rank current primary evidence and recent accepted-decision references ahead of supported derived claims, then stale-but-permitted historical explanations and explicitly marked untrusted/inferred leads. Relevant canonical constraints remain non-droppable irrespective of their rank. Short top-k results include source locator, validity interval, evidence class, conflict flag and visible reason for selection. If a relevant source cannot be accessed, return a typed gap rather than substituting a more convenient stale memory.

<a id="q06"></a>
## Q06 Ranking without self reinforcement

A candidate lexicographic policy uses: valid scope/status first; canonical source class next; direct, attributable confirmation for the exact proposition; independent evidence support; task relevance; valid-time proximity; then bounded retrieval cost/diversity. Source trust is multidimensional, not a global popular-author score. Recency uses observation/valid time, not ingestion order. Direct confirmation improves support only for its precise content and audience; it never changes capability scope.

Usage count is diagnostic and a possible cache-placement hint, not confidence evidence. Repeated extraction from one origin collapses to one evidence family; citations through summaries do not create independent corroboration. Model confidence cannot promote itself through another summarizer. Rank logs record features, policy revision and source families so a reviewer can detect loops. Reject future timestamps and distinguish unknown source clocks from reliable canonical event order.

Compare deterministic lexical/structured retrieval with an optional semantic or hybrid candidate generator under identical eligibility gates. No ranker or embedding technology is selected. The minimum decisive ablation repeats a false note thousands of times while adding one authoritative correction: retrieval frequency must not elevate the false note or hide the correction. Quality improvement over flat files is unknown, including for paraphrases.

<a id="q07"></a>
## Q07 Conflict resolution

| Case | Candidate disposition |
|---|---|
| Same proposition, disjoint valid intervals | Preserve both; current query chooses the interval containing its as-of time; explicit history can retrieve older intervals |
| Authenticated source revision explicitly supersedes its predecessor | Update the current projection by source revision and canonical ordering; preserve the supersession link subject to retention |
| Two incomparable sources disagree | Retain a conflict set and show an authorized, minimal explanation; abstain or request resolution if consequential |
| Canonical decision revoked or amended | Immediately make its memory ineligible as current; resolve new canonical state, never infer an acceptance from recency |
| Summary diverges from its exact source | Quarantine that projection generation, record the mismatch, and use accessible primary evidence or a gap |
| Late-arriving old observation | Preserve observed/valid-time meaning; do not overwrite a newer current state merely because it arrived last |
| Lower-trust text claims to revoke a source | Record the allegation as untrusted evidence; only the canonical policy/admission path changes source usability |

Automatic supersession is limited to declared comparable lineage and matching scope/subject. The competing policy escalates every contradiction. The candidate is falsified if it auto-resolves an incomparable contradiction or current decision incorrectly; escalation-only is disfavored only if a preregistered matched workload shows avoidable review burden without reducing escaped errors. A pass proves those labelled cases, not truth discovery or an optimal automation threshold. Never let the conflict notification disclose another project's hidden claim. F02/F03 provide both positive and negative cases.

<a id="q08"></a>
## Q08 Cross-project privacy and metadata leakage

Allocate private indexes and caches by authority/privacy domain. Use opaque audience-scoped handles externally; keep raw content digests, source paths, exact sizes and private cross-reference topology inside their permitted domain. Do not deduplicate private cross-project content through a shared hit/miss API, even if identical bytes exist. Keyed handles alone do not hide access patterns, ciphertext lengths or timing.

A proposed observation contract defines what each audience may see: permitted results, bounded response buckets, no denied-result count, no distinction between nonexistent and unauthorized handles, no shared-cache-hit signal. Derivative registration and deletion status are also sensitive metadata. Partition resources, bound work and evaluate padding/batching only under the declared threat model. Broad timing resistance is unknown; a finite test can demonstrate only the chosen traces and observational envelope. If the required timing/size bound is unset or cannot be met, refuse the cross-boundary sharing path rather than claim privacy.

Use pairwise synthetic worlds differing only in a secret project fact. The other audience's allowed transcript must be identical after explicitly allowed nondeterminism is normalized; timing and packet-size distributions require an independently specified attacker/bound. A random identifier test does not establish absence of a membership oracle. [E09](#e09) motivates the threat, not any selected cryptographic scheme.

<a id="q09"></a>
## Q09 Forgetting redaction and deletion

Four operations are distinct. **Forget/suppress** stops ordinary future retrieval but leaves governed evidence. **Expire** removes current eligibility at a policy boundary and may initiate deletion. **Redact** creates a new derivative with a declared removed scope, invalidates old downstream copies, and requires a separate review before any audience widening. **Hard delete** requests removal or justified unrecoverability of all in-scope retained copies and relevant key paths. A source revocation is immediately enforced even while physical deletion is pending.

Extend DS07 with a lineage closure over source fragments, extracted facts, summaries of summaries, embeddings, index postings, materialized answers, prompts, tool buffers, search/result caches, exports, generated files, backups and disconnected spools. For nondeterministic extraction, the possible-influence set is every visible input, not only citations the model emitted. Transform edges register before output becomes readable. Missing edges or unknown external copies block completeness; syntactic DAG validation does not prove the input inventory was complete.

Candidate `verified_complete(request, cut)` is true only when all the following independently evidenced predicates hold:

1. An authenticated deletion request has an exact scope and current policy/hold/pin decision; a canonical fence prevents new derived exposure and establishes a closed inventory cut
2. Every expected copy class is explicitly present or proven not applicable, and every in-scope derivative reachable through possible influence is inventoried, including copies created concurrently before the fence
3. All controlled payload copies are deleted or satisfy an approved sanitization/unrecoverability method, with every relevant key, backup, escrow and restored-key path resolved
4. Every affected downstream summary or answer is removed, blocked from hydration, or rebuilt solely from authorized unaffected inputs with new lineage; merely deleting an embedding row is insufficient
5. Restore and reconnect gates apply current tombstones/revocations before exposure; no recoverable backup or offline spool can reintroduce the deleted material under the tested policy
6. There is no unresolved in-scope copy, expired residual window awaiting verification, unknown inventory member or unverified evidence; a separate verifier accepts the exact evidence cut

Completion is a derived read-only state. An adapter's `deleted=true`, negative read, deletion log, checksum or key-destruction receipt alone cannot set it. Per-copy dispositions include present, removed, retention-held, legal-hold, expiry-bound, disconnected-unknown, external-unverified and verified-unrecoverable. Overall outcomes remain partial, blocked, expiry-bound or verified-complete; all completion claims name their boundary. A controlled-lineage milestone may be reported while the full request remains partial.

Offline copies cannot be erased retroactively by revoking credentials. Reconnect can block future use under control; it cannot prove a disconnected machine discarded bytes. Prior recipients may have read, copied, photographed, exported or acted on content. Record that disclosure and any requested downstream deletion evidence, but do not promise erasure of human knowledge, unmanaged copies or model weights. Deleting Recursion memory does not untrain a provider. An external-copy residual means the full deletion request cannot honestly say complete.

A minimal tombstone preserves opaque lineage/request identity, policy, date and disposition under its own restricted retention rule. It should not repeat deleted text, raw digests, exact lengths, path or recipient details publicly. Canonical append-only control history must avoid embedding raw memory payloads in the first place; payload erasure cannot be satisfied if an immutable event copied the secret. Whether a legally required record may be erased remains the existing policy/counsel gate. No retention period or new hold authority is selected here. [E03](#e03), [E10–E11](#e10), and R-H bound these proposals; they do not certify deletion.

<a id="q10"></a>
## Q10 Revocation and changing context

A source change, project membership change, goal closure, rights-policy revision, reader revocation or decision amendment invalidates the dependency binding immediately. Every retrieval and hydration checks the current canonical status; caches keyed to old policy epochs are not served merely because invalidation notification was lost. A returned handle is not a durable read permit. Recheck again at prompt/external dispatch and reject stale compiled bytes.

A preference learned in one goal has that goal as an applicability condition. Moving it to a user-wide or other-project scope requires an explicit, separately admitted promotion with source and sharing rights; it cannot be inferred from recurrence. Reusing unaffected content under new authority creates a new admissible envelope, not a reactivation of an old lease. If current authority cannot be contacted or a relevant offline status is unknown, protected hydration fails closed. Already delivered content remains in the disclosure ledger, with the limitations in Q09.

<a id="q11"></a>
## Q11 Strictest input and audience scope

Per-user, per-project, per-goal and per-audience dimensions are intersections, not interchangeable directories. For a derivative, allowed readers and allowed purposes are the intersection of inputs and current policy; confidentiality and taint conservatively accumulate. When label sets are incomparable, preserve both restrictions or refuse. A public source mixed with a private note produces a private derivative; a user-owned record is not automatically shareable to every goal the user owns.

The rule covers metadata, logs, query strings, embeddings, evidence explanations, exports and model-visible context. A model's own assertion that it omitted the secret is not declassification evidence. An explicit reviewed redaction may create a separately admitted public artifact with its own lineage and clearance; it cannot silently strip parent restrictions. Distinguish source truth confidence, disclosure permission, retention rights and copyright/replay rights. Output categories such as grounded content may have distinct retention and redisplay conditions even in one JSON stream. If applicable rights are unknown, retain only permitted non-content metadata or refuse capture; possession of output is not blanket permission to persist it. The effective retention/expiry envelope takes every input restriction into account, using the earliest binding deadline unless an explicit separately reviewed right permits different derivative retention. Summarization, embedding or re-observation cannot restart a retention clock. An unknown required expiry policy blocks protected use rather than becoming unlimited retention.

<a id="q12"></a>
## Q12 Disabled inertness and lifecycle

For a fresh installation/profile where memory is disabled, the attributed memory-effect vector must be exactly zero: extraction and consolidation invocations; embedding/reranker calls; background jobs/watchers; plugin imports or processes; memory reads/hydrations; network egress; memory payloads, derivatives, indexes and artifacts created. General deterministic manifest enumeration and existing canonical receipts are separately accounted baseline work, not a claim of literally zero CPU or disk for the whole program.

Turning memory off after use fences new capture/retrieval/compilation, cancels queued work and revokes stale result handles. It does not pretend old bytes vanish. Existing artifacts become inaccessible to the memory path and follow explicit retention/deletion policy. Canonical revocation, tombstone enforcement and safety reconciliation remain available without activating the memory plugin. A policy-authorized deletion operation is its own maintenance action, not hidden consolidation. A disabled upstream-only configuration must not obtain a native helper model; even enabled inference roles require explicit admitted routes and accounting.

### Stop and durable commit semantics

Memory work has separate states: proposed → staged → registration admitted → projection published; write acceptance, durable canonical receipt and actual durable payload installation are different receipts. Report durable completion only after the chosen store/availability profile's required evidence. No page-cache write or queue acknowledgement proves power-loss durability. D028 platform/VM-reset qualification is separate and unexecuted.

- Aggressive fences selected-agent dispatch and interrupts extraction immediately. Partial candidates stay unexposed; already committed registrations remain records. Descendant state is explicitly reported rather than silently included
- Full applies to the rooted owned set, including consolidators, schedulers and relaunchers. Each local/remote worker returns scoped evidence or unknown; unrelated shared-server work is not killed by assumption
- Lazy fences new dispatch and permits only a previously admitted operation to reach its declared observable boundary/deadline. A new extraction is not implied by reaching a checkpoint
- checkpoint records canonical cursor, pending candidate IDs and uncertainty; it need not finish a semantic summary
- interrupt requests cancellation; it is not a rollback receipt
- drain flushes only already-admitted, bounded, allowlisted local registration/publication work when current Stop/policy fences permit it. It never starts an extraction, embedding call or new egress and never overrides a later revocation

Use a finite allowlist cut and separate control capacity. Memory workers must not hold a canonical writer lock while running a model, scanning an index or waiting on a remote process. Full queues reject/defer projection work, mark lag and preserve canonical progress. Recovery boots with the projection absent and rebuilds later. If a write may have committed before its acknowledgement was lost, reconcile the original operation ID; do not invent a second write. These are proposed refinements under the accepted vocabulary, not reopened Stop decisions.

<a id="q13"></a>
## Q13 Portability contract

A portable bundle consists of a versioned logical manifest; admitted source/evidence references and permitted source bytes; four typed record kinds; valid-time and provenance relations; trust, audience, purpose, rights and expiry constraints; supersession/conflict/revocation/tombstone state; transform/loss metadata; and a source cut identifying the canonical export. An export may include canonical records through the existing authorized snapshot facility, but memory itself does not export a competing canonical authority. Content-addressed internal identity is not a public membership probe; export remapping preserves authorized logical relationships rather than publishing private raw digests.

Exclude credentials, live grants/leases/reservations, hidden reasoning, raw private global digests, provider KV caches and opaque session artifacts. Destination authentication and minimum access are checked before transmission. Import remaps opaque handles with an explicit map inside the authorized boundary. A destination that cannot represent a privacy or revocation field must quarantine/refuse active use rather than silently drop it.

Three fidelity levels are useful: **lossless control/evidence semantics** (all required relations preserved); **lossy presentation adaptation** (bounded truncation or format changes explicitly recorded, with sources still accessible); **nonportable** (opaque artifacts or lost critical labels). Cross-provider embeddings and similarity scores are not assumed compatible. Rebuild an optional index under a newly admitted configuration; it may change ranking, latency and recall. A text-export success proves bytes are exportable, not behavior, rights, deletion propagation or task continuity.

<a id="q14"></a>
## Q14 Recovery and productive continuity

After machine loss, first recover the canonical checkpoint/event chain through the already-defined single-writer/availability seam, establish current writer/Stop/goal/configuration/grant state, reconcile pending effects and verify source inventory. A memory-only backup cannot restore authority. If required canonical roots or accepted instructions are unavailable, the safe result is a hold with missing references, even if a fluent summary exists.

Next verify bundle provenance, integrity inside its scope, retention/reuse rights, source freshness, current recipient access and deletion/tombstone cut. Reject stale or revoked derivatives before hydration. Build a minimum execution capsule of exact task, acceptance gate, approved directives, uncertainties and next bounded action. Add optional memory evidence after the control kernel is valid. A source fork gets new source/goal bindings and separate work authority; a harness switch gets new route/session identity without laundering old permits. A remembered plan binds the current GoalSpec, exact PlanRevision, checkpoint and source references; a wake resolves them afresh, never executes from summary text. Preserve canonical consumed and reserved liabilities and uncertain effects through recovery. Uncertainty may annotate an outstanding reservation and must not be added again. Use the existing cumulative budget formula and refuse strict-cap admission when its necessary upper bound is unknown; memory owns no plan or budget.

Recovery quality should count verified continuation outcomes, wrong-current-fact and missed-constraint rates, needed re-explanations, human correction time, evidence re-fetches, projection rebuild cost and unsettled effects. Unknown counters remain unknown. Recovered source references and successful rebuild are prerequisites; only a matched task-level trial can establish productive benefit.

<a id="q15"></a>
## Q15 Honest baseline comparison

SD entries point to the bounded source facts in the evidence section; IN means architectural consequence or proposed capability; U means not established, not absent. A rich, disciplined context-file baseline is included, rather than deliberately weak notes.

| Property | Versioned context files | ChatGPT native memory | Claude Code memory files | R-Q typed candidate |
|---|---|---|---|---|
| Persistent human-readable context | SD E06; IN ordinary versioned-file baseline | SD E05 | SD E06 | IN specified, U implemented |
| Source review/correction | IN source links and review conventions can be added | SD [E05](#e05); completeness U | SD [E06](#e06); complete lineage U | IN mandatory lineage; U conformance |
| Scope of remembered material | IN directory/loader plus OS access controls; U configured behavior | SD [E05](#e05); U Recursion-compatible audience semantics | SD E06; U Recursion goal/audience fit | IN pre-hydration intersections; U enforcement |
| Automatic knowledge updates | U unless an explicit capture process is added | SD [E05](#e05); U quality | SD [E06](#e06); U correction quality | IN ordered supersession; U semantic quality |
| Authorization and canonical precedence | IN can be implemented outside the files; file content alone is not enforcement | U Recursion contract equivalence | SD [E06](#e06); U whole-route mediation | IN kernel-only authority; U implementation |
| Cross-harness evidence export | IN plain text can move; label preservation depends on conventions | U complete lossless lineage export | SD [E06](#e06); IN transport possible; U semantic preservation | IN schema/loss map; U round-trip and rights qualification |
| Full derived deletion | U across repository history/backups/copies | SD [E05](#e05); U full copy inventory | U full copy inventory | IN explicit predicate; U deletion drill |
| Recall, human burden, latency and total cost | U matched comparison | U matched comparison | U matched comparison | U matched comparison |

The genuine proposed addition is a mechanically checked relation among evidence, source revisions, authorized recipients, current revocation and downstream transformations, usable by multiple harnesses. A file system with the same envelope, resolver and enforcement can implement it: the distinction is the contract, not the storage medium. Conversely a provider feature may be preferable where its documented boundaries satisfy the task and migration is unnecessary. No product is declared inherently insufficient.

<a id="q16"></a>
## Q16 Recommendation register and decisive falsifiers

Every recommendation in this report belongs to one of the following candidate mechanisms. Competing options must satisfy the same fixed authority, privacy and honest-residual floors. Summary-only authority, unrestricted global recall and root-only deletion with hidden descendants are negative controls, never admissible alternatives. Fixed Owner constraints are not experiments to reopen; a falsifier rejects this candidate implementation or its claimed benefit, never authorizes weakening an accepted invariant.

| ID | Candidate and real competitor | Decisive falsifier | Passing does not prove |
|---|---|---|---|
| C01 | Typed projection with registered lineage versus schema-checked context files carrying the same source, validity and access metadata | The candidate loses a required source/revocation/expiry relation, or files deliver equal continuity with lower full cost | Database need or superior recall |
| C02 | Validated dependency-bound evidence capsules versus full scoped source hydration with current canonical checks on every request and effect | A stale/malicious memory changes an effect authorization or a revoked handle still hydrates | Universal mediation on every route |
| C03 | Allowlisted visible-state extraction versus human-authored structured checkpoints containing only permitted visible state | Forbidden synthetic reasoning channels enter any retained memory surface, or essential recoverable state is missing | Semantic detection of all hidden traces |
| C04 | Scoped deterministic retrieval with optional semantic candidates versus strong scoped lexical/files baseline | Lower-trust repeated claims displace current canonical evidence, or baseline matches quality at lower cost | Real-world precision or optimal rank weights |
| C05 | Automatic same-lineage supersession plus escalation versus escalate all conflicts | An incomparable/late claim becomes current automatically, or review burden rises without lower errors | Resolution of adversarial ambiguity |
| C06 | Partitioned indexes and opaque handles versus authorized per-request scoped source scans without a cross-domain shared index | Unauthorized content/metadata observation distinguishes paired secret worlds above the declared bound | Adaptive side-channel resistance |
| C07 | Eager fine-grained lineage cleanup versus policy-bound deferred cleanup using conservative coarse lineage, the same restore gate and honest residual states | Completion is emitted while an inventoried derived copy/key/backup can restore the target | Destruction of unmanaged copies or prior knowledge |
| C08 | Capability-gated asynchronous projection versus bounded deterministic reference capture and admitted on-demand reconstruction, both outside long writer locks | Disabled work creates memory effects, or saturation delays Stop/recovery beyond the preapproved bound | Literally zero program overhead or OS durability |
| C09 | Neutral export with explicit loss map versus provider-native acceleration backed by a complete governed source-file export with the same labels and revalidation | Round-trip loses a required label/revocation/source edge or silently activates imported authority | Provider interoperability or behavior equivalence |
| C10 | Independently authored state-oracle fixtures plus later blinded quality trials versus finite-state model checking and independent replay cases plus the same quality trials | A planted control/privacy failure passes, or typed layer has equal/worse verified outcomes and greater full cost | Adaptive security or production semantic accuracy |

A task-level advantage claim needs preregistered noninferiority, superiority and resource margins accepted outside this report. No numeric margin is invented. Baselines receive equal source access, current instructions, human maintenance time and context budgets. Count capture, rebuild, indexing, extraction, retries, retrieval, context, verification, retention and correction costs, including the no-future-reuse case. Keep API price, subscription usage and local resource use separate.

<a id="q17"></a>
## Q17 Provider-free acceptance fixtures

The full [handoff register](local-test-handoffs.json) supplies each fixture's inputs, common and case-specific prerequisites, independent oracle, steps, exact pass/fail, evidence and stopping conditions. Synthetic inputs are scenario specifications and tagged payloads, not an assertion that an implementation-specific serialized record format already exists. [Synthetic fixture inputs](synthetic-fixtures.json) contain no real user data. These are specifications, **not executed fixtures or runtime results**. No verified memory entrypoint exists, so there are no invented runnable commands.

| Fixture | Required predicate |
|---|---|
| F01 Cross-session recall | A new session using permitted persisted evidence returns the exact eligible record/reference set, preserves all four kinds, and returns unknown for an absent fact |
| F02 Knowledge update | Current query resolves the accepted newer revision despite late arrival of old evidence; history returns correctly labelled intervals |
| F03 Conflict | Incomparable claims return a conflict and no fabricated winner; explicit same-lineage supersession resolves only the declared relation |
| F04 Revocation | Revoked source and every affected derivative cease hydration at the current fence, including warmed caches and lost-notification paths |
| F05 Deletion closure | Every in-scope copy class, descendant and key path resolves before complete; omitting or retaining any one keeps partial/blocked |
| F06 Project and audience isolation | Paired secret worlds have identical unauthorized observer transcripts; raw digests, denied counts, stable handles and tested size/timing channels do not disclose membership |
| F07 Portability round-trip | Required normalized fields/relations remain equal; unsupported security/rights fields force quarantine; no live authority is imported |
| F08 Disabled-path soak | Attributed prohibited-effect vector remains zero through startup, events, restarts and config transitions; retained old artifacts are not served |
| F09 Memory cannot grant | Grant-like preferences, forged confirmations and repetition leave current effect authorization unchanged for the same request |
| F10 Canonical precedence and hydration race | Canonical decision wins and a revocation between candidate lookup and hydration/dispatch prevents exposure |
| F11 Reasoning exclusion | Forbidden typed channels and synthetic canaries never appear in memory payloads, logs, exports, retries, backups or errors |
| F12 Stop and writer isolation | All accepted Stop boundaries/fences hold despite blocked extraction and saturated queues; projection is unnecessary for recovery progress |
| F13 Influence through compaction | Every possible visible input survives in derivative lineage, taint and restrictions through two lossy transforms, even when omitted from model citations |
| F14 Lost-machine rebuild | Trusted canonical snapshot and current tombstones reconstruct valid control state; memory-only or stale-authority backup holds without hydration |
| F15 Rights and recipient changes | Unknown/expired retention or changed destination denies capture/dispatch; transport format does not widen reuse rights |
| F16 Crash and duplicate registration | Each original operation either has one reconciled registration or remains uncommitted; no exposed orphan or duplicate authoritative adoption |
| F17 Repetition and temporal ranking | Duplicate origin, fake recency and usage inflation cannot promote false confidence or displace a current source |
| F18 Restore and disconnected-copy truthfulness | Old backup/spool cannot resurrect active memory on reconnect; an unreachable copy prevents global completion and prior disclosure remains recorded |

All hard safety predicates require every enumerated case, including negative mutations; unknown is not pass. A missed input or uninstrumented surface blocks a completeness claim. F06 performance observables and F12 time/resource bounds require preregistration rather than fabricated tolerances. Positive controls prove instrumentation can see attempted prohibited activity. No model, provider, account or live-system call is needed to evaluate these structural contracts.

<a id="q18"></a>
## Q18 What the fixture suite can prove

The independent oracle consumes the synthetic canonical event order, source labels and a manually authored expected relation, not the candidate retriever's own answer. It checks exact effect eligibility, current-state equivalence, source/derivative closure and observer projections. One implementation's reducer is not reused as its oracle. Tests use inert local sink spies and deterministic producer stubs. Local subprocess fault injection is a later explicitly admitted activity; it does not involve live hosts or actual provider clients.

Mutation targets remove the authority check, privacy prefilter, hydration recheck, source epoch binding, lineage edge, copy class, restore tombstone, unknown-state refusal, reasoning-channel rejection, Stop fence or queue bound. Each relevant mutant must fail for its intended violated postcondition, not merely a parse/type error. Expected failures and reachability are recorded. A bounded negative test does not prove all possible executions; concurrency interleavings and privacy attacker observables must be declared in advance.

For no-blocking, compare a reference canonical trace without the memory worker against an execution with blocked/failed memory workers. Canonical accepted command order, Stop fencing, recovery state and control-progress deadline must match the allowed specification; memory lag/dropped optional candidates may differ. Never infer this from a healthy memory process or from a unit-level zero-call counter. Startup, full queue, slow disk, cancellation race, missing index and restart are distinct cases.

Safety-first ordering is F09/F10/F13/F15, then F04/F05/F06/F18, then F08/F12/F16/F14, then retrieval/portability F01/F02/F03/F07/F17. This is consequence/dependency ordering, not a numeric expected-value claim. The local owner must establish entrypoints and independent acceptance before any run; this report authorizes none.

<a id="q19"></a>
## Q19 Evidence classification and limits

SD public facts are confined to the source notes below. LO covers inspected pinned source bytes and artifact QA only. Every proposed field, rank policy, state transition, deletion predicate, export contract and test oracle is IN. Runtime recall, precision, stale-answer/conflict rates, privacy success, portability fidelity, latency, resource use, independent acceptance and total cost are U. No claim of success is imported from a paper or from older model receipts.

Passing the provider-free suite would establish only the specified synthetic structural behavior of the exact implementation/profile under its enumerated faults. It would not establish real-world semantic extraction, paraphrase recall, causal lesson quality, calibration, cross-provider behavior, entitlement, route qualification, legal clearance, adaptive adversary resistance, physical erasure of inaccessible media, global absence of copies, provider unlearning, or whole-system availability. No source's benchmark is equivalent to Recursion productive continuity.

Next decisions are implementation-contract adoption and explicit local execution admission, independent oracle ownership, scoped privacy/timing and control-progress budgets, rights-policy mapping, recovery inventory completeness and later matched quality-evaluation margins. Existing Owner decisions remain closed. All fixtures remain UNEXECUTED until those prerequisites and a real entrypoint are recorded.

<a id="public-evidence"></a>
## Primary public evidence notes

These compact notes are the sole substantive public-source summaries in this lane. All retrieved 2 October 2026 UTC. Source register contains version, scope and byte-hash limitations. References elsewhere do not expand documentary claims. No direct legal quotations are reproduced.

<a id="e01"></a>
### E01 Provenance vocabulary

W3C PROV-DM (Recommendation, 30 April 2013) separates entities, activities and agents, with derivation, quotation, attribution, revision and invalidation relations. It supports interchange across domain models. It does not determine whether a claimed influence actually happened, authenticate a source, or confer Recursion authority. Those are separate candidate checks. [PROV-DM](https://www.w3.org/TR/2013/REC-prov-dm-20130430/)

<a id="e02"></a>
### E02 Provenance consistency

PROV-CONSTRAINTS defines consistency rules including uniqueness, ordering, typing and impossibility, and compares normalized provenance instances. This is a useful structural prior for rejecting inconsistent lineage; a structurally valid graph does not establish complete capture or truthful content. [W3C Recommendation](https://www.w3.org/TR/2013/REC-prov-constraints-20130430/)

<a id="e03"></a>
### E03 Sanitization boundary

NIST SP 800-88r2, final September 2025, treats sanitization as making target-data access infeasible for a specified effort. Cryptographic erase depends on encryption and key-management preconditions; sanitization validation evaluates effectiveness. A local deletion receipt alone is therefore not a global copy-removal proof. This report does not select a method or certify compliance. [NIST publication](https://csrc.nist.gov/pubs/sp/800/88/r2/final)

<a id="e04"></a>
### E04 Multi-session memory evaluation

LongMemEval v2 (4 March 2025; ICLR 2025) tests extraction, multi-session reasoning, temporal reasoning, updates and abstention. Its answer evaluation uses an LLM judge. Those categories motivate Q17, but its published scores and grading procedure neither measure Recursion nor qualify a provider-free control oracle. [Original paper](https://arxiv.org/html/2410.10813v2)

<a id="e05"></a>
### E05 ChatGPT native memory

The current official page documents personalization from available sources, review/correction controls and potentially displayed sources. It warns that the memory summary and source display need not be exhaustive. Turning memory off, suppressing mentions, deleting a chat and deleting remembered information are different operations; deletion may require action on multiple sources and can take time to propagate. Availability varies. This is a documented product baseline, not a complete lineage-export or Recursion-conformance guarantee. [OpenAI Memory documentation](https://help.openai.com/en/articles/8590148-memory-in-chatgpt)

<a id="e06"></a>
### E06 File-based and harness-native memory

Claude Code documents user-authored instruction files and auto-written memory, both treated as context rather than enforced configuration. It describes repository-scoped, machine-local editable Markdown memory, shared across worktrees, and different handling of transcript versus memory retention. This is a substantive inspectable-file baseline. It does not establish the current Recursion audience, deletion, authorization or portability contract. [Claude Code memory](https://code.claude.com/docs/en/memory)

<a id="e07"></a>
### E07 Conversational and multimodal evaluation

LoCoMo, ACL 2024, evaluates long conversations using question answering, event summarization and multimodal dialogue tasks. Its conversations are generated through a machine-human process and checked by annotators. This motivates temporal/source and multimodal continuity cases, but not a claim about real Recursion task safety or production memory quality. [ACL paper](https://aclanthology.org/2024.acl-long.747/)

<a id="e08"></a>
### E08 Newer environment-memory research

LongMemEval-V2, arXiv v1 dated 12 May 2026, studies evidence gathering over pre-collected browser-environment histories, including changing state, workflows, gotchas and premise awareness. Its limitations distinguish this from online learning and end-to-end task success. Treat this preprint as a candidate later evaluation input, not a replacement for the synthetic authority/privacy suite or proof that one memory architecture wins here. [Original preprint](https://arxiv.org/html/2605.12493v1)

<a id="e09"></a>
### E09 Deduplication threat

DupLESS, USENIX Security 2013, analyzes known-set brute-force exposure in message-locked encryption and proposes a server-assisted construction. It motivates separating identity, deduplication and privacy boundaries. It does not establish that opaque handles alone hide timing or that any chosen Recursion implementation resists membership inference. [Original research](https://www.usenix.org/conference/usenixsecurity13/technical-sessions/presentation/bellare)

<a id="e10"></a>
### E10 Data minimization

The ICO's official guidance relates retained personal data to a specified necessary purpose and recommends review; it also distinguishes opinions from facts with context. The page is explicitly under review following legislative changes. This motivates purpose and evidence fields, not a jurisdictional legal conclusion. [ICO guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/data-minimisation/)

<a id="e11"></a>
### E11 Retention limitation

The ICO's storage-limitation guidance links retention duration to purpose, documented policy and periodic review. It is also marked under review. No universal memory TTL, exemption, or Recursion compliance finding follows. [ICO guidance](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/data-protection-principles/a-guide-to-the-data-protection-principles/storage-limitation/)

<a id="e12"></a>
### E12 Source fragment references

The W3C Web Annotation Data Model, Recommendation 23 February 2017, represents bodies and targets, with selectors and states identifying particular resource portions or representations. It informs use of revision-bound locators. R-T remains responsible for exact modality/selector mappings; this reference does not certify OCR or transcription fidelity. [W3C Recommendation](https://www.w3.org/TR/annotation-model/)

<a id="completion"></a>
## Completion and artifact checks

[coverage.json](coverage.json) maps the exact intake text for 19 questions and 10 completion bullets to report anchors and appendices. [recommendations.json](recommendations.json) supplies candidate, competitor, falsifier and non-proof mappings. The research report records JSON parse, reference coverage, protected-source hash comparison and a bounded privacy/secret-pattern scan as historical artifact checks. [Packet quality notes](../QUALITY-NOTES.md) distinguish those observations from delivered-byte verification; the per-report production log is not bundled. Artifact QA is not independent product acceptance and cannot establish the universal absence of secrets. No repository/protected file was edited, no target test ran, and no public-source body or private capture path is included in delivery files.
