# Recursion ownership identity and field compatibility map

Proposed integration map for the repository pin `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. No candidate record below is ratified wire, an implemented validator or a new canonical store. Static field compatibility and runtime evidence closure are separate. The machine-readable [compatibility map](field-compatibility.json) records exact source hashes and comparisons.

## Authority and implementation responsibility

A lane owns a design proposal, not a new runtime authority. The existing fenced canonical writer commits accepted mutable domain facts. Authenticated runtime/receiver observations supply evidence; a projection cannot promote itself to an authoritative observation. Refused-command and duplicate-delivery journals retain their declared separate cuts.

| Domain object or action | Design source | Runtime semantic owner | Consumer and forbidden substitution |
|---|---|---|---|
| GoalSpec and accepted instructions | Existing control plane | Owner acceptance and canonical admission | Every loop; summary or room text cannot amend them |
| PlanRevision and tactical step | Existing role contract plus J/R | Current authorized executive role; canonical writer commits | Step coordinator proposes; Head rights and ARM executive rights remain distinct |
| CommandIntent and operation catalog | L | Kernel admission; catalog defines meaning | CLI/TUI/GUI translate; widget or operation label confers no right |
| Query and ExplainResult | L/V | Authenticated bounded read service at an explicit cut | Reads need current scope, not necessarily a new writer transaction |
| WorkPacket and dispatch intent | Kernel plus architecture | Canonical writer derives exact bounded execution contract | Runtime dispatches; schedule claim or room message is insufficient |
| Logical effect and retry owner | F/R/X/Y plus core | One operation coordinator under canonical authority | SDK/workflow/transport retries cannot become additional semantic owners |
| Receiver fence and effect observation | X/U/E plus core | Trusted exact receiving actuator/store within qualified profile | Canonical revocation alone does not establish remote installation |
| Process and descendant inventory | K/U/X | Qualified runtime supervisor, per incarnation and ownership root | PID, pane ID and upstream session name are insufficient |
| Scoped Stop | D022 plus J/K/L/R/T/U/X | Canonical command/fence, runtime delivery, independent observation | UI close, cancel ACK, exit and settlement stay separate |
| Reservation and settlement | Existing two-ledger contract plus O/R/S/T/V/X | Canonical resource/effect ledger | All helpers/children/observers attach; no lane owns another budget |
| ArtifactRef and ContentEnvelope base | Q extending P | Canonical metadata admission; governed artifact storage | T/Y extend; X carries; private digests never become public identity |
| Media representation and transform/loss | T | Admitted producer plus shared artifact/lineage owner | Parser or route adapter cannot declassify or infer completeness |
| MemoryProjection and copy/deletion projection | Q | Derived projection, with canonical policy/lineage/copy facts | Memory cannot issue a grant, remember an executable plan or certify global erasure |
| WorkspaceManifest and WorkspaceBinding | Y | Canonical registration/binding authority | Paths/remotes/branches are locators or observations |
| SourceSnapshot and Materialization | Y | Source-capture/restore evidence admitted under core | Copy, clone or byte match creates no lease or coherent-cut proof |
| ChangeSet and ApplicationIntent | Y | Canonical effect admission plus protected receiver | Rebase, apply or reset cannot be a hidden retry |
| Room membership and CoordinationLease | J | Accepted Head/role authority; canonical writer | Messaging permission and terminal input lease are not plan rights |
| CampaignBinding and WakeIntent | R | Accepted campaign plus canonical occurrence ledger | Dispatcher proposes eligibility and bounded claims |
| Policy candidate and promotion | S | Learner proposes; independent verifier/authorized controller approves | Reward, model verdict or shadow score cannot promote itself |
| DecisionRecord and replay diagnostics | V | Recorded historical decision; read-only interpreter | Re-derived history is neither current permission nor re-execution |
| Membership and placement | X | Owner-authorized enrollment and canonical work admission | Authenticated node is not a task authority or private-data recipient |
| Import translation and plugin lifecycle | G/I/M/U | Admitted lifecycle service under core | Package origin/signature/hook result is evidence, not permission |
| Configuration revision | L/O/S/U | Shared resolver plus compare-and-apply authority | Local UI state, file arrival or rollback cannot widen policy |
| ProjectionManifest and view state | J/K/L/N/V | Rebuildable projection service; renderer owns local layout | Installed cursor must match bytes; view loss does not stop work |

## Identity domains and explicit adapters

Do not establish equality by name similarity. Each reference needs its domain, exact immutable revision where applicable, issuer and a qualified relation to the current object. Monotonicity applies inside a declared fence domain; comparing numbers from different domains is meaningless.

| Meaning | Existing proposed names | Required integration rule |
|---|---|---|
| Canonical writing | writer_fence, writer_epoch | Adapter binds both to one named writer domain only where source semantics agree; never equate with filesystem lock ownership |
| Work execution | work_epoch, work_lease_epoch, work_fence | Bind exact task/step/holder and receiver installation; retain source name/profile; proposed canonical EpochSet mapping needs adoption |
| Scoped Stop | pause_epoch, stop_pause_epoch, pause_fence, stop fence | Bind target ownership root, mode and current pause policy; never infer from process exit |
| Role and coordination | role_lease_epoch, executive lease, CoordinationLease step fence | Independent from work execution and terminal control; both may be required for adoption |
| OS lifetime | process_incarnation, node_incarnation | Creation-time identity plus supervisor scope; PID reuse or copied session text cannot match |
| Route assignment and descriptor | route_epoch versus T route_descriptor_epoch | Assignment identity differs from exact descriptor revision/digest/profile evidence; a descriptor update need not create an assignment, and a new assignment cannot cure stale capability evidence |
| Context | context_epoch | Compiled-context revision remains distinct from route assignment and descriptor; changes require current loss/authority checks |
| Configuration content and activation | configuration_revision / effective_config_ref versus Y configuration_epoch | Content revision differs from target effective/application generation and its adoption receipt; rollback installs a new revision/fence |
| Release content and activation | release_identity/revision versus Y release_epoch | Artifact closure/revision differs from target activation epoch, schema compatibility and permission; successful boot is not history readability or resumability |
| Intent | GoalSpec revision, goal epoch, PlanRevision, step revision | Exact references; historical summaries cannot choose a current revision |
| Input control | input_lease, resize_lease, unified control-holder binding | Frozen M1B fields stay unchanged; proposed acquire/transfer contract joins them atomically per target |
| Idempotency | command_id, logical_operation_id, attempt_id | Command delivery identity, semantic effect identity and dispatch attempt are separate; one operation may have multiple observed attempts |
| Scheduling | schedule_id/revision/nominal_occurrence_id | Identifies eligibility once; not a new task budget or grant |
| Source identity | workspace_id, repository_id, instance_id, snapshot_ref, materialization_id | Logical identity, physical instance, captured bytes and executable working state never collapse |
| Evidence position | canonical ordinal, receipt-journal cut, observation sequence, stream cursor, byte offset, projection generation | Explicit cut vectors and causal joins; no invented global clock or total order |

R-U's generic grant `epoch` is a candidate binding whose intended domain must be stated. It cannot silently stand for every row above. R-V's EpochSet is useful as an explicit typed envelope, but this synthesis does not retrofit it into frozen M1 schemas.

## Shared content base

Q's ArtifactRef fields are all required: `object_type`, `id`, `version`, `content_digest`. The reference is internal to the project's privacy domain. An outward `opaque_handle` is a separately scoped locator, not a serialized ArtifactRef and not a grant. It resolves only after authenticated current audience/purpose authorization. The fact that a handle looks random cannot justify this claim: actual possession-based authority must be classified and protected separately.

The exact eighteen Q ContentEnvelope required names are:

`schema_revision`, `unit_ref`, `source_kind`, `authenticated_origin_or_unknown`, `claimed_author`, `source_revision`, `source_locator`, `integrity_class`, `confidentiality_class`, `allowed_readers`, `project_and_audience`, `privacy_domain_id`, `retention_rights`, `parent_units`, `observed_input_set`, `transform_identity_version_config`, `coverage_and_loss`, `authority_carried_none`.

`authority_carried_none` is true for imported/model-derived content. References to accepted instructions or approvals resolve against current canonical objects separately. A self-asserted flag cannot authenticate the producer, justify a disclosure or make a grant current.

| Incoming name or dimension | Integrated location | Status and required check |
|---|---|---|
| P unit_ref | Q ContentEnvelope.unit_ref | Exact base reuse; full four-field ArtifactRef |
| P raw_digest | unit_ref.content_digest | Explicit normalization, same current bytes/algorithm/domain; conflicting duplicates reject |
| P output_digest | T ContentEnvelope.extensions.output_digest | Checked compatibility alias of produced unit digest; parents still identify original sources |
| P span_or_time_locator | Q source_locator | Typed normalization; same source/revision and coordinate meaning |
| P media_type | T media_facets.media_type_declared | Split; independently validated type is separate and cannot be inferred from declaration |
| P retrieval_operation / retrieval_time | T ContentEnvelope.extensions | Explicit carried P extensions; exact operation and typed clock observation, absent from Q base |
| P source_authenticity_evidence | T ContentEnvelope.extensions | Evidence or unknown; cannot promote trust/authority by copying |
| P disposition | T ContentEnvelope.extensions.disposition | Projection of canonical disposition, not independently writable status |
| P canonical_refs_resolved_separately | T ContentEnvelope.extensions | Invariant with actual resolver evidence; not self-asserted consent |
| Q MemoryProjection.project_id | MemoryProjection only | Not a ContentEnvelope alias; cannot replace project_and_audience/privacy_domain_id |
| Q MemoryProjection.allowed_purposes | T explicit allowed_purposes extension | Semantic precedent only; current purpose/rights intersection required; unknown denies protected use |
| Q source_locator plus T source_locators | Base locator plus media selector extension | Source revision, time/coordinate/render mapping must agree; conflict rejects |
| Q coverage_and_loss plus T loss_manifest | One record/reference with typed facets | No two writable loss truths; unknown semantic preservation remains unknown |
| T representation_kind | T media_facets | Distinct governed artifact for each representation; raw/preview/caption never substituted |
| Y workspace_facets.representation_kind | Y namespaced extension | Workspace-specific representation tag; map to T only through explicit declared relation, not an unqualified global alias |
| Y workspace_facets | Shared envelope extension | Binds immutable workspace/source/candidate/materialization evidence; no active authority |
| X content_envelope_ref / artifact_ref_or_scoped_handle | TransferBinding | Exactly one resolved representation in its domain; validates current policy and recipient, creates no artifact owner |

T's field-map revision 2 enumerates 214 data-field mappings, including route media facets, selectors, transform/loss, exact payload, counters and partial receipts. This map is referenced rather than copied. Its input pins are compared to current P/Q bytes in `field-compatibility.json`. Unknown mandatory fields or inconsistent aliases refuse before exposure; there is no silent precedence repair. A field omitted by another lane is not automatically zero, none, an empty set or inherited by convention.

## Operation and receipt compatibility

L's ReceiptFacts, T's PartialTransferReceipt, X's OperationReceipt and Y's application receipts describe different scopes. They cannot be flattened into a single success boolean or mapped solely by matching words.

| Fact | Source evidence required | What it cannot establish |
|---|---|---|
| saved locally | Client-local outbox/durability receipt | Canonical command acceptance |
| transport received | Named receiver/segment/connection observation | Exact full payload, durable admission or execution |
| command accepted | Canonical disposition bound to exact intent and current guards | Receiver start, remote fence or external effect |
| durably admitted | Exact store/profile commit evidence | Physical-media or cross-service durability beyond that profile |
| dispatched / locally offered | Actual attempt/bytes and boundary | Remote receipt or zero effect after timeout |
| delivered / receiver accepted | Exact recipient, payload/operation and stated meaning | Model consumption, semantic adoption or settlement |
| applied observed | Exact target/base/result and observation coverage | Independent byte verification or effect settlement |
| model-visible consumed | Qualified route observation at exact turn | Agreement, truth or adopted plan |
| settled | Original effect/financial identity reconciled with valid evidence | Independent task acceptance or retroactive cancellation |
| independently verified | Gate/verifier/evidence/candidate identity | Unexamined effects or charges are settled |

**Audited L/V mismatch:** L Q01 and CommandIntent originally define deduplication in authority-domain/principal/command-ID scope. V ReceiptLookupBoundary uses authority-domain plus immutable command ID/digest with actor/auth_ref bound in bytes. They are not equivalent for a changed principal. Proposed resolution: canonical key `(admitted_authority_domain, command_id)`; immutable principal/auth_ref in the digest; transport/client IDs separate. A principal-scoped client ID must pass a declared injective mapping into the canonical ID before admission/lookup. Same canonical ID with changed actor/auth_ref conflicts. Receipt lookup also checks current reader authorization. Current L/V candidate contracts now reflect this correction. The integration proposal still needs adoption and independent vectors while frozen M1A remains exact.

A receipt can prove an old command was accepted while current admission is revoked. Return it as history; do not dispatch it anew. Refusal receipts may live in the authoritative receipt journal without a state-changing event. Required joins include the canonical event cut, receipt cut and artifact manifest, with declared coverage.

For partial media transfer retain locally offered bytes, transport accepted bytes, remotely evidenced receipt and remote processing/settlement separately. If the recipient boundary is unknown, a justified range may be recorded; a local socket count is not exact remote disclosure. For workspace application distinguish staged, partially applied, applied observed, verified and uncertain. A copy receipt is not an application receipt.

## Disclosure registration and publication ordering

The initial X TransferBinding sequence published a verified representation before recording copy/evidence/accounting receipts. Q requires lineage/copy registration before exposure. This is an audited integration defect, not compatibility. The proposed resolution separates remote disclosure from task publication:

1. Privately stage locally within an admitted resource envelope
2. Before the first restricted manifest metadata or chunk leaves for a remote node, durably register exact disclosure intent, expected potential-copy inventory linkage, known lineage and applicable reservation
3. At the actual release boundary recheck current recipient, rights, purpose and fences; emit only the admitted metadata/segment
4. Record actual receipt/copy observations, verify actual allowed representation, and register its copy/lineage before making it task-visible
5. Recheck current rights at task publication, then append publication/disclosure observations and reconcile settlement

A remote node has received information even when its task parser keeps it quarantined. Before-transfer intent does not establish transmission; after a crash, possible disclosure remains unknown until evidence narrows it. Q CopyRecord has no planned/staged enum: use a separately proposed intent/expected-inventory relation, or explicitly version a schema extension. Never silently add statuses or mark an intended remote copy present. The deletion inventory must conservatively include unresolved potential copies at its fence cut. IT-03 tests these distinctions.

## Resource compatibility

R/S/T/V/X use one cumulative allocation lineage and the existing attribution/quantity plus financial/capacity ledgers.

The resource contract must declare gross versus net limit and reserve representation. For a gross cumulative cap with disjoint headroom, use settled + outstanding + withheld + proposed <= gross limit. For an ordinary-work net cap, subtract withheld exactly once from the limit; a tagged reserve already inside outstanding adds no second term. Recovery moves withheld allowance into outstanding atomically. Current host-capacity admission is a separate typed predicate over occupancy/live allocations and proposed peak, never cumulative settled spend treated as current occupancy.

 Shared invariants are:

1. Settled consumption and outstanding reservations are disjoint
2. Uncertain liabilities annotate outstanding reservations and are not added a second time
3. Recovery/control reserves are disjoint or tagged once under a documented shared-reserve rule
4. A strict cap requires a trustworthy finite upper bound; missing upper bound refuses affected-pool expansion
5. Settlement transfers reservation to consumption atomically and releases only proven unused remainder
6. Cumulative resets, inclusive parent/child totals, cache subsets and late corrections require explicit reconciliation evidence
7. Retry, fork, new route/session, machine loss and policy change cannot recredit a task

T Counter, V KnowledgeValue/MeterObservation, S outcomes and O metric budgets have distinct roles. Retain raw source values separately from validated knowledge. A raw crash-time zero may be invalid rather than known zero. Keep unit and source inclusion semantics through every conversion. Synthetic capacity/margin constants are fixture inputs; they are not observations, adopted ceilings or runtime conformance.

## Outcomes evidence eligibility and promotion

W's immutable first-reviewed submission controls the first-review endpoint. S's phrase first complete submitted candidate cannot erase an incomplete submission that entered review and failed; drafts before submission remain separate. Keep all assigned eligible episodes, missing/unreviewed outcomes, audit coverage and delayed corrections. Observed zero greens makes conditional false-green rate undefined; unknown greens are a different missingness state.

O's no-benefit disposition maps to justified equivalence or exclusion of the registered practical gain. Insufficient precision or power stays inconclusive, and S's exact boundary equality remains inconclusive. A classifier may establish eligibility for independent review; it cannot issue promotion authority or install a policy. A separate current exact-artifact authorization and independent evidence remain required.

## Read boundaries and frozen compatibility

The proposed production query service supports bounded authorized same-cut inspection without obligatorily mutating canonical state. Hydration may create a disclosure/copy obligation; an external query may have effects. Resolve the actual boundary before selecting the operation class.

M1A's current PAUSE-sensitive observation admission is preserved. Historical inspection does not create a new observation event. M1C pure trace classification remains evidence for that bounded classifier only. M1B's exact union and refusal semantics remain unchanged: its `GAP` meaning is not a new wire arm, and Stop is not inserted into the frozen union. New production operations, extension fields and epoch names require separately versioned compatibility/adoption, independent vectors and explicit loss.

## Compatibility disposition and open joins

The exact shared Q base is textually compatible with T/X/Y candidate declarations at the pinned intake. That is a useful integration result, not an implemented guarantee. Remaining joins requiring decision or evidence are:

- Adopt a versioned semantic map for differently named writer/work/pause/configuration epochs; do not mutate frozen contracts
- Freeze receipt retention and unique logical-command replay mapping separately from repeated delivery journal occurrences
- Define digest algorithm/domain binding at the containing schema; four-field ArtifactRef alone does not carry every interpretation parameter
- Bind provenance registration, payload installation and publication as distinct receipts with crash recovery
- Freeze each exact route's input, Stop, child ownership, compaction, metering and required C/T support
- Qualify coherent dirty capture and protected apply on exact workspace/platform profiles, including aliases and missing external objects
- Establish receiver fence installation barriers and pre-install exposure classification before conflicting takeover effects
- Obtain independent runtime evidence and adopted evaluation values; schema agreement and artifact QA do not supply them

Actual lane names are E launch, F delegation, G import, H counsel, I source study, J rooms, K TUI, L interface platform, M terminal mods, N GUI, O performance, P injection, Q memory, R autonomy, S adaptation, T media, U isolation, V observability, W evaluation, X node fabric and Y workspace. The stale final mapping in ARCHITECTURE-COVERAGE is not used.
