# Recursion Shared Contract Reconciliation

2026-10-02 · R-SC · Parent goal `goal-recursion-v3-harness-orchestrator`

## Decision and evidence status

**Propose one shared-contract candidate for Owner adoption:** a typed identity vector; canonical command key `(admitted_authority_domain, command_id)`; the exact four-field `ArtifactRef` and eighteen-field `ContentEnvelope`; one immutable loss record with typed facets; subject-specific receipt facts; precommitted disclosure intent before remote release; and one conserving cumulative resource algebra. The final sections resolve the seven shared joins and specify the independent observations needed to qualify them.

“Accepted candidate” in this report means the one option recommended within this reconciliation. It does **not** mean Owner-ratified contract, accepted wire format, implemented guarantee, qualified route, or executed test. Lucas retains adoption authority. All synthetic vectors below are specifications, **UNEXECUTED**. Their expected outcomes are inferred design requirements, not observed outcomes.

### Fresh source pin and provenance

The source of truth is [Recursion commit `5b55e55a103fad2d82d625983080b39f2db21c0e`](https://github.com/NotSkittlz/recursion/commit/5b55e55a103fad2d82d625983080b39f2db21c0e), the merged result of [PR 147](https://github.com/NotSkittlz/recursion/pull/147). PR metadata records merger on 2026-10-02 at 16:50:21 UTC; the freshly resolved `master` equaled that commit. Read-only acquisition verified all 1,379 tracked blobs, 37,752,780 bytes and all 191 trees, including root tree `c5efe438a91b15a318fb0ed70d1488cb51c30034`. The supplied packet’s three files match their merged repository bytes. These are locally observed source-acquisition facts, not product validation.

The lane documents preserve their original research baseline `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Citations here point to their **current merged locations and bytes** at `5b55e55…`; the old baseline inside them remains historical provenance. This distinction matters:

- The original L/V command-key disagreement is already textually corrected in the current L/V declarations
- The initial X publish-before-registration defect is already addressed by the revised `TransferBinding` and explicit `ExposureIntent`
- T’s revision-2 mapping already preserves the exact Q base and rejects conflicting aliases
- Those corrections supply candidate agreement. They do not demonstrate that a runtime enforces it

See the current [ownership map](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L109-L125), [X disclosure contract](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L183-L230), and [T alias rules](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L464-L470).

### Fixed authority and scope

The operative [CONTROL_PLANE](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/CONTROL_PLANE.md#L1-L70), [ANCHOR](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/ANCHOR.md#L1-L57), [AGENTS](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/AGENTS.md#L1-L43) and accepted [D-018 through D-033](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/state/DECISIONS.md#L37-L355) constrain this proposal. Recursion is a standalone native harness and harness orchestrator; Hermes is optional upstream integration. The comprehensive surface ships opt-in. Productive continuity preserves authority, evidence and honest accounting. Savings require workload measurements and never establish vendor intent. No accepted Owner decision is reopened.

All mutable canonical facts remain owned by the existing fenced canonical writer. A named design owner in a field table owns the **proposal’s semantics**, not an independent runtime authority. A receiver/supervisor supplies attributable evidence; a projection can display or interpret that evidence but cannot promote itself into its origin. Frozen M1A/M1B/M1C bytes and meanings remain unchanged, including `GAP` and Stop. Application envelopes and maps are additive versioned contracts outside the frozen wire.

The report selects no language, package manager, store, framework, runtime, sandbox, transport, encoding, schema format, contract-definition language, model or vendor. Existing field names such as `wire_encoding` are obligations to declare a future interpretation, not selections. No repository implementation, target script, target test or import ran; no model/provider/account/receiver/live-host interaction, installation, spending, credential action, repository edit, publication or merge was performed as research execution.

### Reading the field maps and vectors

Evidence classes are **SD** (what a pinned source declares), **LO** (static source/artifact observation), **IN** (this report’s candidate inference), and **U** (unverified or unmeasured runtime behavior). All recommendation rows are IN grounded in SD/LO; runtime fulfillment is U. A source’s claim of a past PASS is not a new local observation or independent acceptance.

Each table states an exact candidate name, one proposed design owner, source lane, consumers and binding relation. Qualified field paths disambiguate names without renaming them. Terms explicitly called “proposed metadata” are an additive semantic requirement whose final field spelling and representation are not ratified. Refusal words not already declared source codes describe required dispositions; they do not extend a frozen error alphabet.

Every vector needs a useful authorized positive control, the stated adverse mutation, and an observer independent of the producer’s own verdict. A refusal-only system and a blind observer cannot pass. A “falsifier” is the concrete forbidden observation that rejects the candidate on that vector. It never authorizes weakening an Owner invariant. Real conforming alternatives are distinguished from unsafe negative controls throughout.


## Q1 accepted-candidate identity field map

A design owner below is a single proposed semantic-design owner, not a new runtime authority. The existing fenced canonical writer admits mutable domain facts; runtime/receiver evidence remains attributable to its actual observer. Consumers cannot promote a projection into an observation. “Binding relation” means the relation that must resolve to the exact current object before protected use, with historical references retaining historical meaning. [S10]

All rows are **IN** reconciliations grounded in **LO** source declarations. Each row's falsifier is named in the next section; representation competitors and non-proofs are part of the same recommendation.

| Exact source field or identity | Independent domain | Single proposed design owner; source lane | Consumers | Required binding relation |
|---|---|---|---|---|
| `writer_fence` | Canonical writer ownership | Kernel writer-fencing contract; X, Y | L, V, X, Y; every writer | Issued through the kernel/store/availability seam for one writer domain, current holder and committed prefix; acceptance gate compares only that domain's floor [S11][S12] |
| `writer_epoch` | Same writer domain **only through an explicit source-profile mapping** | Kernel writer-fencing contract; V | L, V, X, Y | `SourceCut.writer_domain` + `writer_epoch` + source event binding; map to `writer_fence` only when issuer/scope/advance semantics agree [S04][S13] |
| `work_epoch` | Admitted task/step execution | Kernel work-lease contract; X | L, T, V, X, Y | `Lease.task_ref`, `step_ref`, `work_packet_digest`, holder/process target and `canonical_admission_receipt`; required receiver installation remains separate [S12] |
| `work_lease_epoch` | Work-lease generation, explicitly mapped to the above domain | Kernel work-lease contract; V | L, V, X, Y | Exact task/step/holder lease reference; not writer ownership and not the whole lease record [S04][S13] |
| `work_fence` | Receiver-enforced work-authority floor/reference | Kernel work-lease contract; Y | T, X, Y | `ApplicationIntent`'s exact task/binding/operation to applicable receiver work domain and installed floor; an epoch number alone is insufficient [S04][S07][S14] |
| `lease_id` (`Lease`) | Particular bounded execution grant | Kernel work-lease contract; X | L, V, X, Y | Immutable lease identity joins its exact holder incarnation, task/step, bounds, grant, work/pause refs and admission receipt; a current epoch without the applicable lease cannot authorize execution [S12] |
| `pause_epoch` | Scoped Stop/admission boundary | Scoped Stop contract; X | J, K, L, T, V, X, Y | Target ownership root/scope, Aggressive/Full/Lazy mode, current pause policy and canonical Stop decision; delivery/install observations join but do not define the canonical decision [S04][S12][S15] |
| `stop_pause_epoch` | Same scoped Stop domain through declared mapping | Scoped Stop contract; V | L, V, X, Y | Preserve source name in `EpochSet`; resolve exact scope/mode/policy, never process-exit shorthand [S04][S13] |
| `pause_fence` | Applicable protected Stop fence/reference | Scoped Stop contract; T, Y | P, Q, T, X, Y | Exact payload/application scope to current Stop reference at disclosure/effect gate; no widening from source-name parity [S07][S16] |
| `role_lease_epoch`; executive-role lease (prose record) | Tactical/executive role authority | Executive-role contract; V with J | J, L, V, X | Current principal/role run + accepted goal/version + role's permitted plan rights; issuer follows the accepted role authority, with canonical commitment [S13][S17] |
| `CoordinationLease`, including `room_id`, `workflow_step_id`, step revision and step fence | Bounded one-step coordination, separate from executive role | Coordination contract; J | J, L, V, X | Issuer Head role, holder principal/role run, exact goal, room/step, participants/audience, expiry/revocation and conflict-policy revision; adoption additionally requires executive rights where specified [S17] |
| `input_lease` | Terminal input ownership | Runtime control-lease contract; K, L | J, K, L, V | Authenticated holder + exact target + daemon/process incarnations + lease generation/validity; current effect authority checked independently [S18][S19] |
| `resize_lease` | Terminal upstream-resize ownership | Runtime control-lease contract; K, L | J, K, L, V | Separate typed token for same target; proposed atomic acquisition/transfer with input holder does not merge namespaces or authorize passive resize [S18][S19] |
| `process_incarnation` | One observed process/containment lifetime | Runtime process-identity contract; X, V, Y, K | J, K, L, V, X, Y | Qualified supervisor's creation-time/process-containment observation, node/daemon scope and ownership root; PID/session text alone cannot satisfy it [S11][S18] |
| `node_incarnation` | One enrolled node runtime lifetime | Node-identity contract; X, V | L, V, X, Y | `NodeIdentity.domain_id`, `node_id`, enrollment/trust/revocation refs and authenticated incarnation; separate process relation is mandatory [S12] |
| `route_epoch` | Assignment of a route to an execution subject | Route-assignment contract; X, V, T, Y | L, P, Q, T, V, X, Y | Canonical assignment transition binds task/attempt, exact harness/interface/model/pool/host and independently pinned descriptor/evidence; source session IDs remain aliases within this assignment [S05][S11][S16][S20] |
| `route_descriptor_epoch` | Exact capability-descriptor revision | Route-capability contract; T | L, T, V, X, Y | `CompiledPayloadManifest` to exact descriptor revision/digest/profile and qualified evidence used for payload admission; descriptor change does not itself assign a route [S05][S16] |
| `context_epoch` | Installed compiled-context generation | Context-compilation contract; V | L, Q, T, V, X, Y | Exact pre/post manifests, single governor, declared transform/loss, installation evidence and canonical context transition; summary production is insufficient [S13][S21] |
| `configuration_revision` | Canonical configuration content/meaning | Shared configuration resolver contract; L, X, V, T | All admission/payload/application consumers | Scope + immutable content/semantic digest + pinned resolver/schema + canonical compare-and-apply receipt; restrictive authority is checked immediately even if preferences await application [S22][S23] |
| `effective_config_ref`; T `RouteMediaFacet.bindings.config_revision` | Reference to resolved configuration content | Shared configuration resolver contract; Y, T | T, X, Y | Explicit versioned source mapping to exact resolved configuration object; not an alias for target application generation [S06][S16][S24] |
| `configuration_epoch` | Target effective/application generation | Configuration-application contract; Y | L, T, V, X, Y | Target recipient + exact content ref/revision + compiled/validated/staged/effective adoption receipt; new content alone cannot establish effective generation [S05][S06][S22][S24] |
| `release_identity`; `release_revision` | Code/schema artifact closure or revision | Release-identity contract; X; V | L, V, X, Y | Exact artifact/build/schema compatibility identity with qualified evidence; name mapping only when content semantics agree [S04][S11][S13] |
| `release_epoch` | Target release activation generation | Release-activation contract; Y | L, V, X, Y | Target incarnation + admitted activation + exact release identity/compatibility evidence; never grants or repairs work authority [S05][S07] |
| `command_id` | Canonical command-delivery identity | Kernel command-admission contract; L/V, X/Y | L, T, V, X, Y | `(admitted_authority_domain, command_id)` to one immutable command/digest and original disposition; L's `canonical_command_id` mapping label resolves to this exact field [S01][S02][S03] |
| `logical_operation_id` | One logical external effect | Logical-effect coordination contract; X | L, T, V, X, Y | Exact effect intent/receiver scope/body, one `retry_owner`, original authority/reservation lineage and all attempts; Y's `operation_id` maps only by explicit operation-type relation [S07][S14][S25] |
| `attempt_id` | One actual dispatch attempt | Logical-effect coordination contract; X; V | L, T, V, X, Y | `attempt_of_operation` edge to stable logical operation plus route/process/node and observed dispatch boundary; reconnect alone creates no new attempt [S14][S26] |
| `workspace_id` | Registered logical workspace | Workspace-identity contract; Y | Q, T, V, X, Y | `WorkspaceManifest.registration_ref` + privacy/project scope + immutable `manifest_revision`; one workspace per active binding revision [S06] |
| `repository_id` | Registered logical repository | Workspace-identity contract; Y | Q, V, X, Y | `RepositoryIdentity.registration_ref` + lineage and privacy domain; admitted membership joins workspace, not equal bytes/path/remote [S06][S27] |
| `repository_instance_id` (**not** an unqualified candidate field `instance_id`) | Physical repository instance | Workspace-instance contract; Y | V, X, Y | Exact `repository_id`, `host_incarnation`, `locator_ref`, shared-admin resources, observation cut and capability profile; clone association is explicitly admitted [S06] |
| `snapshot_ref`; binding-side `source_snapshot_ref` | Immutable captured source representation | Source-snapshot contract; Y | Q, T, V, X, Y | Binding points to the exact `SourceSnapshot` and its repository, declared captured set, interpretation, capture class/coherence evidence and coverage; reference alias mapping is explicit [S06][S28] |
| `materialization_id`; binding-side `materialization_ref` | Mutable executable working state | Source-materialization contract; Y | V, X, Y | Exact source snapshot, repository instance, host/root/profile, `materialization_revision`, `mutation_generation`, isolation and verification refs; it creates no grant [S06][S28] |
| R-U `grant.required_bindings.epoch` | **Only the single declared grant/revocation domain**, if defined by the additive map | Grant-admission contract; U | P, T, U, X, Y | Map must name exact grant domain/issuer/subject and relation to current canonical grant. An unspecified generic epoch is unusable for protected admission; separate writer/work/pause/etc. checks remain mandatory [S04][S29] |

**Generic `epoch` disposition.** No unqualified scalar, maximum, lexicographic tuple or “latest generation” is admissible as a replacement for the vector. An exact legacy field named `epoch` can remain only when its source-profile map names **one** specific domain (for R-U, the grant/revocation generation) and its authorized issuer, subject, advancement and comparison relation. Its original bytes stay intact. It cannot mean “the newest of process/work/pause/release.” Missing domain or an unresolved current binding refuses protected use; missing values stay typed unknown/not-applicable and never zero. [S04][S11][S13][S29]

## Q2 independent collapse vectors and exact refusal outcomes

These are **designed, unexecuted** vectors. The listed outcome is the candidate's required refusal, not a newly ratified error-code alphabet. The sole quoted existing code `stale_work_fence` is X's candidate code; all descriptive refusals remain application-layer proposals and do not alter frozen M1B reasons. Each vector has a valid-current positive control so blanket refusal cannot pass.

| Vector | Decisive independent change | Required outcome and falsifier |
|---|---|---|
| ID-01 writer versus work | Advance authorized writer fence W7→W8 while holder A's work epoch remains revoked | Refuse A's work/effect under stale work authority; permit only a separately current writer action. Any automatic lease/approval renewal falsifies the map [S11][S12] |
| ID-02 work epoch versus lease | Supply current numerical work epoch but another task's `lease_id`, wrong holder or expired maximum operations | Refuse wrong/expired task-step-holder lease; equality of one number cannot satisfy the grant [S12] |
| ID-03 work fence versus process | Work 7 revoked; process incarnation P2 replaces P1 and presents delayed work-7 effect after receiver has installed floor 8 | Refuse `stale_work_fence`; zero new receiver mutation. A lexicographic `(P2,7) > (P1,8)` authorization falsifies the map [S11][S14] |
| ID-04 pause versus work/reconnect | Valid work lease reconnects into a scope whose Full Stop is current | Refuse new dispatch/current continuation; retain permitted history and unresolved liabilities. Fresh socket/session/work observation cannot clear Stop [S15][S19] |
| ID-05 executive versus coordination | Current one-step coordinator lacks executive tactical-plan rights, then current executive lacks required step lease | Refuse adoption in each respective missing-right case. Evidence/proposal may be retained through an allowed path; neither lease implies the other [S17] |
| ID-06 work versus terminal control | Worker has work lease but no input lease; terminal controller has input lease but no execution grant | Refuse raw input in the first case and effect admission in the second. Focus/attach cannot mint either right [S18][S19] |
| ID-07 input versus resize | Passive client resizes its viewport or presents input token in resize-token slot | Local viewport change may succeed; upstream `RESIZE` refuses absent exact current resize binding. Proposed atomic holder transfer cannot accept swapped token domains [S18][S19] |
| ID-08 PID/process/session reuse | PID reused after process exit; copied session text still names old process; process creation evidence differs | Refuse stale process/control target; do not signal or adopt result for the new process via old binding [S11][S18] |
| ID-09 process versus node | Node N1 restarts as N2 while copied process P1/lease/session references are supplied; converse: P2 starts within N1 | Refuse stale node-holder binding in first case; P2 does not create a new node identity or heal prior work authority in second. Copied-key ambiguity remains unknown/quarantined, never unique-hardware proof [S11][S12] |
| ID-10 descriptor versus assignment | Descriptor D4→D5 changes a required media capability while route assignment R9 stays unchanged | Do not create R10. Refuse use of payload/capability evidence frozen against D4 when required D5 compatibility is unknown; require revalidation/recompilation [S05][S16] |
| ID-11 assignment versus descriptor | Assign R10 but carry stale D4 capability evidence | Refuse required unsupported/unknown capability; new assignment does not cure stale descriptor evidence [S05][S20] |
| ID-12 context versus route | Produce summary/context candidate C6 under unchanged R9, omit a pending approval or install receipt | Refuse effective-context advancement/use; route identity stays R9 and missing exact control remains missing. A generated summary is not installed context [S21] |
| ID-13 configuration revision versus activation | Accept content revision C8 while recipient still effective at application generation G4 using C7 | Report C8 accepted/staged as evidenced but refuse a requirement for C8-effective until exact adoption receipt; do not fabricate G5. Restrictive revocation still fences immediately [S05][S22][S23] |
| ID-14 configuration activation versus authority | Install G5 while old work remains revoked; rollback preferences using a new accepted revision | Refuse stale work. Rollback never decrements work/pause/grant floors or revives old credential authority [S22][S23] |
| ID-15 release identity versus activation | Release artifact R2 verified, old target still activated at A1/R1 | Refuse requirement for R2-active without target activation evidence; artifact verification is insufficient [S04][S05] |
| ID-16 release activation versus work | Advance release activation A1→A2 with still-revoked work epoch 7 | Refuse stale work exactly as ID-03; successful boot/activation cannot clear revocation or prove old history readable [S05][S30] |
| ID-17 command versus logical operation | Lost reply followed by a fresh transport/command ID targeting the same unsettled logical effect | Hold/reconcile original logical effect; refuse blind redispatch/new liability. Canonical command dedup alone cannot protect duplicate effects under different command IDs [S25][S31] |
| ID-18 operation versus attempt | Crash/session replacement creates proposed attempt A2 while operation O remains unknown at receiver | Refuse A2 dispatch until O reconciles or an evidenced sink-idempotency protocol makes it safe; preserve O and its reservation. Multiple attempts remain one logical effect; distinct observed attempt charges must still each be accounted once [S14][S25] |
| ID-19 workspace versus repository | Two workspaces contain the same repository/commit; task changes cwd or copies manifest | Refuse implicit workspace rebind; require admitted exact workspace membership/binding. Shared bytes do not merge workspaces [S06][S27] |
| ID-20 repository versus instance | Clone identical bytes at another path/host, then claim same instance or a new logical fork without admitted association | Record new physical instance; refuse ambiguous logical association and protected use until registered. Rename of an admitted locator alone does not create new repository identity [S06][S27] |
| ID-21 snapshot versus working materialization | Materialization mutates M3→M4 while its base `snapshot_ref` stays S2; compare equal commit IDs | Refuse apply bound to stale M3/base; immutable snapshot reference does not certify mutable working/index/untracked bytes [S07][S28] |
| ID-22 materialization versus snapshot/location | Restore same S2 on new host with old `materialization_id` receipt or unavailable external objects | Refuse currently executable binding until new/explicitly revalidated materialization and coverage evidence; a historical copy receipt is not current authority/availability [S06][S24][S28] |
| ID-23 generic epoch | Grant map omits domain or chooses maximum across work, process, configuration and release | Refuse unbound/mismapped required authority reference. Any unrelated-generation “repair” of stale work falsifies the generic-epoch interpretation [S04][S11][S29] |

**Conforming representation competitor:** keep separate source-profile reference records and require an explicit join manifest at each protected operation, instead of a single additive vector envelope. Both preserve exactly the domains above. The decisive comparative vector is a mixed-profile object carrying all current bindings except revoked work: either design must reject it while admitting an otherwise identical all-current positive. A conforming competitor can win on independently measured integration/verification burden later. The forbidden one-number design is a negative control, not the only rival. Passing these finite vectors does not prove physical non-overlap, remote host honesty, artifact coherence, cryptographic uniqueness or universally safe authority enforcement. [S04][S11][S30]

## Q3 evidence positions, permitted joins and required unknowns

**Accepted candidate (IN): a cut vector plus typed causal relations.** A canonical append sequence orders admitted records in one writer domain, not all remote physical actions. Receipt refusal/delivery journals retain their own ordered cut. An observation sequence orders an observer's records within its node/stream incarnation. A stream cursor is unit-bound. An artifact byte offset addresses a representation. A projection generation identifies reconstructable output. None is a generic timestamp, grant or global order. [S13][S26][S32]

| Position; exact available source name | Proposed owner; source/consumers | Valid binding/order and join |
|---|---|---|
| Canonical ordinal: X `OperationReceipt.canonical_ordinal`; V `SourceCut.writer_domain`, `writer_epoch`, `event_sequence`, `event_digest` | Canonical evidence-position contract; X/V → all lanes | Compare only same declared canonical domain/history. Writer-epoch transition needs recorded continuity; never blindly compare fresh sequence after reset. Join receipt/observation via exact admitted receipt/evidence identity and causal edge [S13][S14] |
| Receipt-journal cut: V `receipt_journal_revision`, `receipt_digest` | Authoritative receipt-journal contract; V/L → V/L/X/Y | Own journal identity/revision and digest; includes refused commands and repeated delivery occurrences. Join canonical cut by explicit command/receipt/event group and coherent capture, not equal counters [S09][S13] |
| Observation sequence: X literal cursor-domain label `node observation sequence`; `source_observation_id` in `OperationReceipt` | Runtime observation contract; X → L/V/X/Y | Bind exact observer/node/process/stream incarnation and occurrence identity. A late local start observation can join a later canonical ordinal with `observation_of`; recording order is not physical occurrence order [S14][S25][S32] |
| Stream cursor: frozen `event` / `utf8-byte` cursor units | Runtime stream contract; K/L → J/L/V/X | Bind stream ID + daemon/stream incarnation + unit + count; joins source events only through source-event mapping and snapshot manifest. Events advance by one; byte counts use decoded UTF-8 bytes, not encoded base64 characters/code points/cells [S19][S33] |
| Byte offset: X literal `artifact byte offset`; V diagnostic byte/container position | Artifact representation-position contract; X/V → T/V/X/Y | Bind immutable representation identity/digest, encoding/coverage and range; join to event only with verified framing/index relation. Corrupt framing without trustworthy sequence yields byte/container location and unknown event number [S09][S32] |
| Projection generation: V `SourceCut.projection_generation`, `ProjectionManifest.generation`; Q `projection_generation` | Projection contract; V/L/Q → J/L/Q/V | Bind projection/schema/reducer/filter/audience/policy identity and explicit event/receipt/artifact cuts. Installation receipt joins actual verified bytes and installed cursor atomically; larger generation is not newer canonical truth by itself [S13][S34][S35] |

**Join rules, including pairs that can only conditionally join:**

- Canonical cut ↔ receipt cut: a coherent captured vector and exact command/receipt/event-group relation; a refusal may have no state-changing event. No bijection is assumed. Equal ordinal numbers do not join them
- Observation sequence ↔ canonical ordinal: attributable `source_observation_id`/admitted evidence plus `observation_of` edge. Canonical ingestion can occur later or out of physical order; it only proves recording order
- Observation ↔ receipt: exact operation/attempt/receiver/representation and observer evidence. Matching timestamp, PID or upstream session text is insufficient
- Stream cursor ↔ canonical/receipt/observation position: a declared projection/source mapping and actual snapshot/cursor installation. Filtering, coalescing and redaction may make the mapping non-injective or omit events; retained gaps stay explicit
- `event` cursor ↔ `utf8-byte` cursor ↔ artifact byte offset: only a pinned representation/framing map that declares how records occupy ranges. A four-byte character, two records in one chunk and split-frame delivery must not be collapsed to one unit
- Projection generation ↔ any source position: the manifest's declared cut vector plus verified materialized bytes/installation facts. Generation 11 built from old cut 5 is not more current than generation 10 at cut 6
- Distinct nodes/streams/writer domains, unrecorded fork joins, absent mapping, unsynchronized source clocks or redacted/missing dependencies: cross-domain order is **unknown**. Independently sourced timestamps may carry uncertainty intervals but never create an exact causal edge or global clock. A deterministic display sort is labeled presentation order only

**Rival / falsifier / non-proof.** Rival: derive the causal graph on demand from complete typed events/receipts, or persist a bounded rebuildable edge index keyed by the same source cuts. Both retain the cut vector. Decisive vector: observe B before receiving A's report, record A at canonical 12 and B at 11, use receipt occurrence 12 for a duplicate and project only one filtered item; the result must preserve the actual declared joins and leave unproved A↔B physical order unknown. A cross-domain timestamp sort presented as causal fact, receipt 12 equated with event 12, byte cursor treated as event ordinal, or cursor advanced before snapshot install falsifies it. A passing source-map test proves neither clock synchronization, physical causality, actual durable storage nor receiver truth. [S09][S19][S26][S34]

## Q4 to Q6 canonical command, effect and retry boundary

### Accepted candidate and exact field rules

**IN: accept `(admitted_authority_domain, command_id)` as the one canonical command key.** `content_digest` is the immutable equality/conflict predicate under that key, not a third key component. Otherwise `(D,C,h1)` and `(D,C,h2)` could create two operations where the contract requires a conflicting duplicate. The immutable content binds `actor_id`, `auth_ref`, semantic operation/version, exact body/arguments, target/revision/fence scope and other effect-relevant bytes. It excludes only explicitly declared non-authoritative transport/audit fields under a pinned interpretation. L calls its immutable intent digest `semantic_digest` and uses `principal_grant_ref`; their source-schema map must retain those spellings and prove binding equivalence rather than blindly rename bytes. X's `body_digest` and sink `exact_body_digest` refer to their declared effect/body domains, not an assumed byte-identical substitute for the entire canonical command digest. [S01][S02][S03][S14]

`actor_id`/`auth_ref` belong inside the immutable command because a repeated ID cannot change who authorized it or its grant meaning merely by choosing another key subnamespace. Authentication of the *current presenter* and authorization of *current read disclosure* are separate from the historical command's actor/auth binding. Authorize current caller/domain/audience/purpose before lookup **including existence metadata**; recheck disclosure. An old effect authority does not grant present read access, and present read access does not renew effect authority. [S03][S08]

| Shared field/rule | Single proposed design owner; source lane | Consumers | Binding relation |
|---|---|---|---|
| `admitted_authority_domain` | Kernel command-admission contract; V with L | L/V/X/Y | Authenticated canonical command namespace; command ID alone never crosses it [S03] |
| `command_id` (`canonical_command_id` mapping label in L) | Kernel command-admission contract; L/V | L/T/V/X/Y | Unique immutable command under admitted domain; explicit durable ingress mapping precedes lookup [S02][S03] |
| `content_digest` ↔ L `semantic_digest` (declared mapping, not unconditional alias) | Command-content identity contract; V/L | L/V/X/Y | Pinned immutable content semantics including embedded principal/grant; mismatch under existing key conflicts [S02][S03] |
| `actor_id` | Command-content identity contract; V/L | L/V/X/Y | Historical authenticated command actor bound immutably inside the complete command; not the current reader [S02][S03] |
| `auth_ref` | Command-content identity contract; V/L | L/V/X/Y | Exact historical authority reference bound into immutable command content; current authority resolves separately and no raw credential is carried [S02][S03] |
| L `principal_grant_ref` | Command-content identity contract; V/L | L/V/X/Y | L’s exact combined principal/grant source field maps to actor/auth meaning only through a declared immutable-content interpretation [S02][S03] |
| Principal-local ingress mapping | Kernel command-admission contract; L/V | All client ingress/receipt/replay consumers | Declared stable injective mapping from client/principal namespace and local ID into admitted canonical ID; durable across restart and used before every lookup [S02][S03] |
| `current_caller` | Receipt-disclosure contract; V | L/V/X/Y | Currently authenticated presenter/reader, independently identified before historical lookup; may differ from the immutable command actor [S03] |
| `current_read_scope` | Receipt-disclosure contract; V | L/V/X/Y | Current authorized domain, audience, purpose and object scope; checked before lookup including existence metadata and at disclosure [S03] |
| `historical_receipt` | Authoritative receipt-journal contract; V/L | L/V/X/Y | Original disposition and cut for original immutable command; no dispatch side effect [S03][S09] |
| `logical_operation_id` | Logical-effect coordination contract; X | L/T/V/X/Y | Stable semantic effect identity spanning deliveries and attempts, with exact authority/receiver/reservation lineage [S14][S25] |
| `retry_owner` | Logical-effect coordination contract; X | L/T/V/X/Y | The one currently admitted coordinator allowed to reconcile or propose retries for the logical effect; ownership transfer is explicit [S14][S25] |
| `receiver_scope` | Logical-effect coordination contract; X | L/T/V/X/Y | Exact receiving actuator/resource namespace for the operation and sink effect key; not merely host or transport identity [S14][S25] |
| `body_digest` | Logical-effect coordination contract; X | L/T/V/X/Y | Immutable effect-body identity under its declared representation/domain; not automatically the whole-command digest and never an extra idempotency namespace [S14][S25] |
| `attempt_id` | Logical-effect coordination contract; X | L/T/V/X/Y | One actual admitted dispatch occurrence joined to the stable logical operation; reconnection or evidence-only recovery creates no attempt [S14] |
| `process_incarnation` | Runtime process-identity contract; X | L/T/V/X/Y | Bind the effect attempt to its qualified observed process lifetime and node/supervisor scope; one process may contain many attempts [S14] |
| `source_observation_id` | Runtime observation contract; X | L/T/V/X/Y | Exact attributable observer occurrence joined to the operation/attempt and observer incarnation; not dispatch identity or a canonical ordinal [S14] |
| Sink key `(receiver_scope, effect_id)` with `exact_body_digest` | Receiver idempotency contract; X | T/X/Y and V evidence | Atomically bind exact body and result/mutation under one sink key; digest is equality predicate, never extra sink namespace [S14] |

### All five Q5 decisive vectors

Each scenario has independent expected disposition/effect count, a changed-content negative and current-authorized positive as appropriate. These remain unexecuted designs.

| Q5 vector | Accepted outcome | Exact falsifier / non-proof |
|---|---|---|
| (a) Same D/C, same complete immutable bytes/digest, same principal | After current reader authorization, return original disposition/cut; record new delivery occurrence if permitted; **zero new dispatch**. One logical-command replay input remains | New admission/effect, overwritten original receipt or discarded delivery occurrence falsifies. Passing does not prove receiver once-only execution under unobserved historical attempts [S01][S09] |
| (b1) Same D/C and complete bytes, changed *current caller/presenter* while embedded actor/auth stays unchanged | Independently authorize new caller's present read scope. If allowed, return same historical receipt with no dispatch; if denied, refuse without existence disclosure | Always accepting changed caller leaks history; always treating an independently authorized new reader as conflicting confuses reader with author. Passing does not establish the original actor was truthful or authorized [S03][S08] |
| (b2) Same D/C and payload but changed embedded `actor_id`/`auth_ref` or L `principal_grant_ref` | Complete immutable bytes have changed even if caller says “same bytes.” Return conflicting-duplicate refusal; do not create a second principal namespace or dispatch | Returning duplicate-success, accepting a new command, or excluding actor/auth from digest falsifies. A digest match asserted by a caller cannot override byte/schema binding [S02][S03] |
| (c) Same D/C, changed body/payload/target | Conflicting duplicate; retain original command unchanged and no new effect. Read-denied callers still receive no private existence detail | Treating digest as third key or last-write-wins body replacement falsifies. A passing hash-equality test alone proves no collision resistance or source authenticity [S03][S14] |
| (d1) Two principal-local namespaces collide on local ID `7`, with declared injective durable mapping | Map `(client/principal A,7)` and `(client/principal B,7)` to distinct canonical IDs before lookup. Independent legitimate commands may be admitted under current authority; retries of each recover its own canonical ID even after crash | Collision, unstable remapping on restart or lookup before mapping falsifies. The mapping itself confers no current grant or permission for two effects aimed at one logical operation [S02][S03] |
| (d2) Same collision without declared injective durable mapping | Refuse/hold ambiguous ingress namespace. Do not silently add principal to the canonical key, guess a canonical ID or reuse the other receipt | Either client admitted through guessed alias or changed namespace would falsify. Safe refusal is not proof that namespace migration is complete [S02][S03] |
| (e) Deduplication history expired/unavailable for a previously possible dispatch | `receipt-history-unavailable`; reconcile/hold the same operation, retain existing liability/uncertainty, prohibit blind same-ID or new-ID dispatch. A surviving sufficient tombstone may still prove duplicate/conflict, but absent required evidence never means unused | Any dispatch merely because lookup found nothing, or reservation release on expiry, falsifies. A tombstone can preserve identity/disposition without sufficient payload to fully replay history [S01][S09][S36] |

**Competition.** The audited rival `(domain, principal, local command ID)` as a second *canonical* namespace has different semantics: mutating actor under the same intended canonical ID can evade conflict. Reject it at the canonical boundary by (b2). A conforming principal-local design remains viable **at ingress**, using the explicit durable injective map in (d1); another conforming design allocates canonical IDs directly and uses client IDs only as audit metadata. Compare those two on namespace durability and interoperability, not by weakening semantic identity. Digest-as-key and volatile mappings are negative controls. Passing all five vectors does not prove production authentication, permission-policy correctness, indefinite receipt durability, external effect settlement or global exactly-once execution. [S01][S03][S30]

### Retry-owner key and recovery cases

The canonical *delivery deduplicator* keys on `(admitted_authority_domain, command_id)`. The single *semantic retry owner* keys on the stable `logical_operation_id` in its admitted authority/receiver scope, with immutable effect/body and original reservation lineage; it never keys only on `attempt_id`, upstream session ID, socket request ID or node incarnation. Receiver-side idempotency uses the explicitly joined `(receiver_scope, effect_id)` key and atomically bound body/result. One command can request/describe effects, but command and effect cardinality must be declared, not assumed one-to-one. [S14][S20][S25]

| Disturbance | Identity retained and permitted action | Refusal / falsifier |
|---|---|---|
| Crash before/after dispatch boundary | Recover original D/C, logical operation, reservation and last known boundary; query/reconcile before retry. Create a new `attempt_id` only for an actually admitted new dispatch | Uncertain original classified as absent, fresh operation created or liability recredited |
| Reconnect/lost ACK | Transport/session identifiers may change; D/C and logical effect persist; replay/return receipt evidence only | Reattachment counted as attempt or new effect |
| Provider-session replacement | Record new route/session alias as applicable; same task and unsettled logical operation remain. Route assignment changes are explicit, not inferred from socket replacement | New provider session treated as permission/budget reset or retries owned by both SDK and coordinator |
| New node incarnation/machine recovery | Record new process/node and revalidate work/receiver fences; preserve logical effect and uncertainty. Conflicting replacement waits for safe receiver/quiescence boundary | New incarnation “heals” revoked work or erases unknown old effect |
| Historical receipt after effect revocation | A still-authorized reader may receive old accepted disposition at old cut; show later revocation separately; **zero redispatch** | Old acceptance restored as current grant, or replay reactivates live lease/permit |

Rival: durable centralized operation coordinator versus bounded operation coordinators with disjoint admitted ownership and a canonical owner-transfer record. Both have exactly one current semantic retry owner. Decisive crash vector: hand ownership over while the last dispatch outcome is unknown; only one owner may reconcile, no conflicting new effect may occur, and reservation identity stays constant. Passing does not prove physical old-process termination or truth of a disconnected receiver. [S20][S25][S31]



## Q7 and Q8 Shared content base and exact field map

**Accepted candidate C1:** retain one internal `ArtifactRef` with exactly `(object_type, id, version, content_digest)`. Its digest identifies declared bytes inside the declared privacy domain, subject to the containing-schema interpretation in Q17. It is neither authenticity evidence nor an authority grant. An outward `opaque_handle` is a separately authorized audience/purpose-scoped locator. Resolving it requires current authorization before sensitive metadata is revealed; serializing the four internal fields under a random-looking wrapper does not make it safe.

The conforming alternative is independently represented domain envelopes with explicit, total, versioned adapters preserving these same identities and restrictions. The shared base is preferred because it reduces the number of mappings whose completeness must be established. This is a semantic-contract preference, not a shared-library or implementation choice. If a handle actually authorizes by possession, it must be classified as a bearer capability and governed accordingly; relabeling it “opaque” cannot make it non-authorizing. A valid authorized handle resolution is the positive control. A copied handle used by a different audience without authorization must disclose neither object existence nor bytes (C1-H). A pass establishes only those observer-bound cases, not cryptographic privacy or side-channel resistance.

The exact source declarations are [Q ArtifactRef and ContentEnvelope](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L11-L47), [T base and extension ownership](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L5-L68), and [X unchanged base](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L11-L45). These are compatible declarations, not tested implementations.

### Exact base field map

The design owner of every base row is R-Q, extending R-P’s provenance discipline; canonical metadata admission remains the existing writer. “All content lanes” below means P/Q/T/X/Y, with L/V consuming authorized receipt/evidence projections. Binding requirements apply at every round trip, not merely at initial parsing.

| Exact field | Proposed design owner | Source lane | Consuming lanes | Required binding |
|---|---|---|---|---|
| `ArtifactRef.object_type` | R-Q | Q; reused T/X/Y | All content lanes; L/V | Expected canonical/artifact type of this reference; no type substitution |
| `ArtifactRef.id` | R-Q | Q; reused T/X/Y | All content lanes; L/V | Scope-local identity inside the containing privacy domain |
| `ArtifactRef.version` | R-Q | Q; reused T/X/Y | All content lanes; L/V | Exact immutable revision, never “latest” inferred from locator |
| `ArtifactRef.content_digest` | R-Q | Q; reused T/X/Y | All content lanes; L/V | Exact declared byte representation under Q17’s algorithm/domain/coverage interpretation |
| `opaque_handle` | R-Q | Q outward projection; T/X/Y reuse | L/T/X/Y/V | Locator bound to authorized audience, purpose, object resolution and current rights; not an internal-reference serialization or grant |
| `ContentEnvelope.schema_revision` | R-Q | Q from P | All content lanes; L/V | Exact supported envelope interpretation; unknown mandatory security semantics refuse |
| `ContentEnvelope.unit_ref` | R-Q | Q from P | All content lanes; L/V | Complete four-field reference to this representation |
| `ContentEnvelope.source_kind` | R-Q | Q from P | All content lanes; L/V | Actual admitted source class; imported/model-derived content stays data |
| `ContentEnvelope.authenticated_origin_or_unknown` | R-Q | Q from P | All content lanes; L/V | Verified origin evidence or explicit unknown with reason; not claimed authorship |
| `ContentEnvelope.claimed_author` | R-Q | Q from P | All content lanes; L/V | Attributed author claim only, independently of authenticated origin |
| `ContentEnvelope.source_revision` | R-Q | Q from P | All content lanes; L/V | Exact source revision/set governing provenance and freshness |
| `ContentEnvelope.source_locator` | R-Q | Q from P | All content lanes; L/V | Authorized source/revision plus declared coordinate semantics; a locator is not authority or availability |
| `ContentEnvelope.integrity_class` | R-Q | Q from P | All content lanes; L/V | Source/authenticity evidence class, independent of confidentiality |
| `ContentEnvelope.confidentiality_class` | R-Q | Q from P | All content lanes; L/V | Conservatively retained restrictions; incomparable labels remain conjunctive |
| `ContentEnvelope.allowed_readers` | R-Q | Q from P | All content lanes; L/V | Intersection of all influential inputs and current policy; no default wildcard |
| `ContentEnvelope.project_and_audience` | R-Q | Q from P | All content lanes; L/V | Exact project and intended audience/recipient binding, checked at use |
| `ContentEnvelope.privacy_domain_id` | R-Q | Q explicit addition | All content lanes; L/V | Domain in which identity/digest/equality and metadata access are interpreted |
| `ContentEnvelope.retention_rights` | R-Q | Q from P | All content lanes; L/V | Current operation-specific retention/replay/redisplay/export rights, destinations and expiry; unknown denies protected use |
| `ContentEnvelope.parent_units` | R-Q | Q from P | All content lanes; L/V | Immediate immutable lineage parents, not all possible influence by themselves |
| `ContentEnvelope.observed_input_set` | R-Q | Q from P | All content lanes; L/V | All possibly influential visible inputs; model citations cannot prune the set |
| `ContentEnvelope.transform_identity_version_config` | R-Q | Q from P | All content lanes; L/V | Exact producer/transform version and admitted configuration/receipt |
| `ContentEnvelope.coverage_and_loss` | R-Q | Q from P; T typed facets | All content lanes; L/V | The one loss record in Q9; aliases are projections of that record |
| `ContentEnvelope.authority_carried_none` | R-Q | Q from P | All content lanes; L/V | Required `true` for imported/model-derived content; canonical authority references resolve separately |

This list contains **18 base-envelope names**, with no `project_id` or `allowed_purposes` added. `MemoryProjection.project_id` is a memory scope field. It is not the missing audience binding, and cannot substitute for `project_and_audience` or `privacy_domain_id`. T’s `ContentEnvelope.extensions.allowed_purposes` is an explicit extension required before protected media processing; it is not an inherited nineteenth Q-base field. The source distinguishes these precisely in [T extension and shared-validation rules](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L417-L470).

### Extension and alias ownership

| Exact source field or path | Proposed design owner | Source lane | Consumers | Binding and permitted mapping |
|---|---|---|---|---|
| P `raw_digest` | R-P | P | Q/T/X/Y/V | Compatibility projection of `unit_ref.content_digest` only for the same bytes, algorithm and domain |
| P `output_digest` / T `ContentEnvelope.extensions.output_digest` | R-P | P; carried T | Q/T/X/Y/V | Produced unit’s digest; never overwrites parent identities; contradictory duplicate refuses |
| P `span_or_time_locator` | R-P | P; normalized T | Q/T/X/Y/V | Explicit typed map to base `source_locator` with identical source/revision/coordinate meaning |
| P `media_type` / T `media_facets.media_type_declared` | R-T | P; T split | Q/T/X/Y/V | Declaration maps only to declared type; validated type needs independent evidence |
| `ContentEnvelope.extensions.retrieval_operation` | R-P | P; carried T | Q/T/X/Y/V | Exact admitted retrieval operation; no grant |
| `ContentEnvelope.extensions.retrieval_time` | R-P | P; carried T | Q/T/X/Y/V | Typed retrieval clock observation; not capture/ingestion time |
| `ContentEnvelope.extensions.source_authenticity_evidence` | R-P | P; carried T | Q/T/X/Y/V | Evidence reference or unknown; cannot promote content into authority |
| `ContentEnvelope.extensions.disposition` | R-P | P; carried T | Q/T/X/Y/V | Read-only projection of canonical disposition/receipt |
| `ContentEnvelope.extensions.canonical_refs_resolved_separately` | R-P | P; carried T | Q/T/X/Y/V | Invariant supported by actual canonical resolution, not self-asserted consent |
| `ContentEnvelope.extensions.allowed_purposes` | R-T | T; Q MemoryProjection precedent | P/Q/T/X/Y/V | Current purpose intersection; null/unknown blocks protected processing |
| `media_facets` | R-T | T | P/Q/X/Y/V/L | Adds media semantics bound to the same base `unit_ref`, scope and immutable sources |
| `media_facets.representation_kind` | R-T | T | P/Q/X/Y/V/L | Distinct artifact for original, thumbnail, transcript, embedding, compiled payload, etc.; no representation swap |
| `media_facets.media_type_validated` | R-T | T | P/Q/X/Y/V | Actual validation evidence; never inferred from filename/declaration |
| `media_facets.byte_identity` | R-T | T | Q/X/Y/V | Binds `digest_algorithm`, `digest`, `byte_length`, `completeness`, `domain_ref` to this representation; incomplete stream has no invented final digest |
| `media_facets.byte_identity.digest_algorithm` | R-T | T | Q/X/Y/V | Declared algorithm interpretation, not a selected algorithm |
| `media_facets.byte_identity.digest` | R-T | T | Q/X/Y/V | Digest of this exact representation, consistent with `unit_ref.content_digest` under the same domain |
| `media_facets.byte_identity.byte_length` | R-T | T | Q/X/Y/V | Exact evidenced length or unknown; not assumed equal to encoded wire length |
| `media_facets.byte_identity.completeness` | R-T | T | Q/X/Y/V | Whether the declared byte coverage is complete; incomplete streams cannot claim a final-object identity |
| `media_facets.byte_identity.domain_ref` | R-T | T | Q/X/Y/V | Exact interpretation/privacy domain joined to the containing envelope |
| `media_facets.source_locators` | R-T | T | P/Q/X/Y/V/L | Typed selectors must agree with base source locator and exact source revision |
| `media_facets.transform_ref_or_none` | R-T | T | P/Q/X/Y/V | Exact transform or evidenced no-transform relation |
| `media_facets.loss_manifest` | R-T | T | P/Q/X/Y/V/L | Typed view/reference to the single Q9 loss record |
| `media_facets.completeness` | R-T | T | Q/X/Y/V/L | Completeness of this representation/coverage, not global semantic completeness |
| `media_facets.evidence_class` | R-T | T | P/Q/X/Y/V/L | Source-documented, observed, inferred or unknown basis for this representation |
| `media_facets.verification_status` | R-T | T | P/Q/X/Y/V/L | Exact independent review status and scope; separate from parse success |
| `media_facets.capture_time_claim` | R-T | T | Q/X/Y/V | Source’s capture claim with evidence/clock quality, not trusted global time |
| `media_facets.ingestion_time` | R-T | T | Q/X/Y/V | Receiving/admission observation, distinct from capture time |
| `workspace_facets` | R-Y | Y | Q/T/X/V/L | Workspace/source/candidate/materialization extension; no new artifact owner or active authority |
| `workspace_facets.representation_kind` | R-Y | Y | Q/T/X/V/L | Workspace-local tag; relates to T only through explicit mapping, never a global alias |
| `TransferBinding.content_envelope_ref` | R-X | X | P/Q/T/Y/V | Immutable reference to the shared envelope, not a transport-owned copy of its meaning |
| `TransferBinding.artifact_ref_or_scoped_handle` | R-X | X | P/Q/T/Y/V | Exactly one representation resolved in its authorized domain; outward handle requires current resolver authorization |

The full revision-2 [T field map](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/field-map.json#L1-L37) enumerates 214 media data-field mappings. Its domain-private selector/counter/capability subfields remain owned there; this reconciliation adopts the shared bindings above rather than creating a competing media catalog. The current synthesis [explicitly distinguishes these alias locations](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L64-L92).

### Content conflict vectors

The real competitor for C1/C2 is a separately versioned domain envelope with a complete checked adapter; blindly accepting a synonym or omitting restrictions is a negative control, not a competing safe design.

| Vector | Concrete mutation and accepted outcome | Exact falsifier | Passing does not prove |
|---|---|---|---|
| C1-R | Round-trip a valid four-field reference through Q→T→X→Y. Remove each field in turn or substitute thumbnail bytes under the original version; refuse the malformed or mismatched reference before exposure | Any omitted identity component or swapped representation resolves as the original | Authentic origin, availability, authority or universal collision resistance |
| C1-H | Equal private bytes exist in projects A and B. B presents A’s locator without current read rights; deny without disclosing A’s existence. Authorized A resolution succeeds | Raw digest/equality or unauthorized payload is exposed, or a handle’s appearance supplies authority | Timing/size noninterference outside the declared observer envelope |
| C2-A | Delete `project_and_audience` from an otherwise valid envelope; refuse missing required scope before metadata/hydration | Consumer guesses the audience from directory, sender or `project_id` | Full privacy enforcement beyond this boundary |
| C2-B | Substitute `project_id` for `project_and_audience`; refuse missing base field and unrecognized base alias | Substitution silently produces a broader or inferred audience | Correctness of every future compatibility map |
| C2-C | Delete `privacy_domain_id`; refuse absent identity/privacy interpretation before digest lookup | Cross-domain equality or resolution proceeds on a default domain | Cryptographic unlinkability |
| C2-D | Add unknown mandatory security field under an unsupported revision; refuse/quarantine protected use pending recognized interpretation | Decoder ignores the field and exposes content | Detection of malicious meaning hidden in an allowed string |
| C2-E | T’s output digest, byte identity or locator disagrees with the base under the same interpretation; refuse conflicting aliases, never choose precedence | One alias silently wins while another reader sees different bytes/scope | Actual transform fidelity |
| C2-F | Output cites only public input P but observed input set includes private N; keep N’s restriction. Unknown required purpose refuses | Citation selection removes N from influence or null purpose becomes wildcard | Completeness of an unobserved real input inventory |

For every required base field, the same removal test generalizes C2: remove exactly that name without changing the revision, and the record cannot become eligible as a complete shared envelope. A narrower diagnostic read may still be separately authorized, but cannot hydrate or dispatch the incomplete object as valid.

## Q9 One loss record with typed facets

**Accepted candidate C3:** `ContentEnvelope.coverage_and_loss` identifies one immutable loss record, with the T `LossManifest` facets below. `media_facets.loss_manifest` is a revision-bound projection/reference to that same record, not another writable declaration. A correction creates a new loss-record revision and newly bound envelope/representation; it cannot mutate an already approved payload’s meaning. Q owns the shared record binding; T owns the named media facets.

A conforming alternative stores one inline typed loss record in the envelope and derives every media view mechanically. Both are viable. The shared immutable-reference candidate is preferred for lineage reuse across multiple consumers without duplicating writable truths. No record format or storage implementation is selected. If both old views arrive, resolve their declared common record/version and compare overlapping facets under the same interpretation. Missing mandatory facets, conflicting values, incompatible inputs/outputs or differing transform identity **reject**; no “most specific wins” repair. An unknown preservation claim stays unknown even if the other view omits it.

The exact [T LossManifest](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L176-L210) supplies these names:

| Exact field | Proposed design owner | Source | Consumers | Binding |
|---|---|---|---|---|
| `LossManifest.input_refs` | R-T | T | P/Q/X/Y/V/L | Immutable affected inputs; consistent with complete influence set |
| `LossManifest.output_refs` | R-T | T | P/Q/X/Y/V/L | Exact derived representations, not source IDs reused |
| `LossManifest.transform_ref` | R-T | T | P/Q/X/Y/V/L | Same admitted transform as envelope lineage |
| `LossManifest.coverage` | R-T | T | P/Q/X/Y/V/L | Declared regions/times/ranges and omissions, unknown where unmeasured |
| `LossManifest.dimensions` | R-T | T | P/Q/X/Y/V/L | Property-specific facets listed below, never a global semantic score |
| `LossManifest.unknown_reasons` | R-T | T | P/Q/X/Y/V/L | Reasons attached to affected unknown facets |
| `LossManifest.task_loss_policy_ref` | R-T | T | P/Q/X/Y/V/L | Current task’s admitted tolerances; cannot be inferred from transform confidence |
| `LossManifest.independent_review_ref_or_unknown` | R-T | T | P/Q/X/Y/V/L | Exact independent evidence or explicit unknown, distinct from producer claim |

| Exact `LossManifest.dimensions` entry | Proposed design owner | Source | Consumers | Preserved property to bind |
|---|---|---|---|---|
| `byte_reversibility` | R-T | T | P/Q/X/Y/V/L | Whether the source bytes can be recovered exactly |
| `spatial_detail` | R-T | T | P/Q/X/Y/V/L | Spatial resolution/detail relevant to the task |
| `color_alpha_orientation` | R-T | T | P/Q/X/Y/V/L | Color, transparency and orientation changes |
| `layout_reading_order` | R-T | T | P/Q/X/Y/V/L | Layout and reading-order relationships |
| `tables_formulas` | R-T | T | P/Q/X/Y/V/L | Table structure and formula semantics |
| `temporal_coverage_sync` | R-T | T | P/Q/X/Y/V/L | Included time intervals and synchronization |
| `channels_speaker_attribution` | R-T | T | P/Q/X/Y/V/L | Channel separation and speaker binding |
| `speech_words` | R-T | T | P/Q/X/Y/V/L | Spoken-word fidelity, including negation |
| `non_speech_sound` | R-T | T | P/Q/X/Y/V/L | Task-relevant non-speech sound preservation |
| `prosody` | R-T | T | P/Q/X/Y/V/L | Intonation/rhythm information |
| `language_translation` | R-T | T | P/Q/X/Y/V/L | Language/translation transformation |
| `numerical_precision` | R-T | T | P/Q/X/Y/V/L | Precision, signs, decimal places and units |
| `citation_coverage` | R-T | T | P/Q/X/Y/V/L | Source support actually covered by locators |
| `selection_summary` | R-T | T | P/Q/X/Y/V/L | Selection, truncation and summarization omissions |

Each facet uses exactly `preserved`, `changed`, `omitted`, `unknown` or `not_applicable`, with reason and relevant evidence. Preservation of one dimension does not imply another. “No transform” can establish unchanged bytes only with appropriate byte evidence; it is not a blanket semantic-verification label.

**C3-L decisive vectors:** (1) Q’s record marks `speech_words=unknown`, while T’s alias claims `preserved` for the same output and transform: reject contradictory declarations; accepting either by precedence falsifies C3. (2) A well-formed transcript reverses “do not release” into “release,” with perfectly consistent IDs/lineage: structural validation may succeed, but semantic preservation must remain unknown or fail independent review; schema PASS reported as semantic PASS falsifies the claimed boundary. (3) OCR omits a table row and its later summary labels `tables_formulas=preserved`: retain the omission through composition, refusing an incompatible task-loss policy; recovered precision without evidence is a falsifier. These cases do not prove arbitrary OCR/ASR accuracy, complete real influence capture or semantic equivalence.

## Q10 Receipt facts and their observers

**Accepted candidate C4:** preserve independent attributable facts, each naming its subject, observer, evidence reference, source cut/sequence, exact candidate/operation/attempt and applicable scope. This is a semantic record requirement, not a new universal receipt enum. A receiver may produce an observation before a delayed local ACK arrives. Verification of output bytes can coexist with unsettled financial liability. Missing stages stay unknown; later unrelated success does not fill them in.

The conforming alternative is separate stage-specific journals joined by exact references and declared cuts, rather than a common fact-vector projection. The candidate chooses a common **read projection** of those independent facts because it exposes partial knowledge consistently, while leaving their original evidence owners intact. A single monotone `success` status is an inadmissible negative control.

| Vocabulary and exact source fields | Single proposed design owner | Source lanes | Consumers | Subject, required observer and evidence | Explicit non-proof |
|---|---|---|---|---|---|
| `saved_locally`; L `ReceiptFacts.saved_locally` | R-L | L | L/V | Client outbox’s exact immutable command; local durability observation under stated profile | Canonical acceptance, remote receipt or permission to execute |
| `received`; X `transport_received`; T `bytes_transport_accepted` | R-X | X/T | L/Q/T/V/Y | Named segment/connection and explicitly named accepting endpoint, which may be sender-local; exact coverage | Full payload receipt, durable admission or execution |
| `delivered`; L `delivered_applied`; X `receiver_accepted`; T `bytes_remote_acknowledged` | R-L | L/X/T | L/P/Q/T/V/X/Y | Exact recipient incarnation, operation/payload/segment and qualified receiver acknowledgment with declared meaning | Model consumption, semantic adoption, independent application verification or settlement |
| `admitted`; L `accepted_or_refused`; X `command_accepted`, `durable_admission` | R-L | L/X/Q | All seven lanes | Canonical command disposition bound to guards and exact bytes; durability separately evidenced at the declared store/profile commit | Remote start, installed remote fence, physical durability beyond the profile or external effect |
| `started`; X `local_started_observed` | R-X | X; runtime supervisor | L/T/V/Y | Exact work/process incarnation and qualified supervisor’s start observation | Remote receiver acceptance, useful completion or settlement |
| `observed`; L `outcome_observed`; X `effect_observed`; Y `applied_observed` | R-V | V/L/X/Y | All seven lanes | Exact target/base/result/effect and observer coverage, with unknown reasons | Independent verification, completeness of hidden effects or financial settlement |
| `settled`; L `effect_settlement`; X `settled`; T `billing_settlement` | Core resource/effect contract | L/T/V/X/Y | All seven lanes | Original logical effect/financial identity reconciled by canonical ledger using valid receiver/meter evidence | Task acceptance, independent output correctness, external rollback or settlement of unrelated effects |
| `verified`; L `verification`; X `independently_verified`; Y `independently_verified`, `bytes_verified`, `independently_accepted` | R-V | V/L/X/Y | All seven lanes | Named gate, exact candidate, evidence cut and independent verifier disposition | Every unexamined effect or charge settled, universal safety or route qualification |

`admitted` includes at least two distinguishable subfacts: command admission and evidenced durable commitment. Q further distinguishes `write_accepted`, `canonical_registration_durably_committed`, `payload_durability_evidenced`, and `projection_published`. None can be substituted for another. A receipt may describe a refusal with no state-changing canonical event.

The source terms grouped in a row are related facets, not equivalence aliases. In particular, `bytes_transport_accepted` can mean acceptance by a sender-local transport boundary: name that endpoint explicitly and do not infer remote receipt. `bytes_remote_acknowledged` proves only the recipient and scope stated by that acknowledgment, not application delivery or model consumption unless separately evidenced.

Exact declarations: [L ReceiptFacts](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/proposed-contracts.json#L95-L114), [X OperationReceipt](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L259-L293), [T PartialTransferReceipt](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L348-L377), [synthesis receipt boundaries](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L91-L113).

### Partial transfer field map

Each row below has design owner R-T, source T `PartialTransferReceipt`, consumers L/Q/V/X/Y. These remain media-specific evidence dimensions carried under the shared fact projection; none implies another.

| Exact field | Proposed design owner | Source | Consumers | Binding |
|---|---|---|---|---|
| `operation_ref` | R-T | T | L/Q/V/X/Y | Original logical operation |
| `attempt_ref` | R-T | T | L/Q/V/X/Y | Actual attempt, not a replacement logical effect |
| `segment_ref` | R-T | T | L/Q/V/X/Y | Exact bounded stream segment |
| `source_coverage` | R-T | T | L/Q/V/X/Y | Source ranges represented in this segment |
| `bytes_offered` | R-T | T | L/Q/V/X/Y | Sender observation only |
| `bytes_transport_accepted` | R-T | T | L/Q/V/X/Y | Named transport observation only |
| `bytes_remote_acknowledged` | R-T | T | L/Q/V/X/Y | Receiver evidence for exact acknowledged scope |
| `remote_disclosure_lower_upper_or_unknown` | R-T | T | L/Q/V/X/Y | Evidence-bounded exposure range; no fabricated equality with local bytes |
| `object_completion` | R-T | T | L/Q/V/X/Y | Full object completeness, distinct from a segment |
| `processing_state` | R-T | T | L/Q/V/X/Y | Receiver processing observation or unknown |
| `billing_settlement` | R-T | T | L/Q/V/X/Y | Original charge/capacity liability and canonical settlement |
| `stop_request` | R-T | T | L/Q/V/X/Y | Canonically admitted scoped Stop request |
| `local_fence` | R-T | T | L/Q/V/X/Y | Local installed boundary and evidence |
| `remote_fence` | R-T | T | L/Q/V/X/Y | Exact receiver installed-boundary observation or unknown |
| `cleanup_state` | R-T | T | L/Q/V/X/Y | Authorized cleanup evidence, never inferred from connection close |
| `unresolved_effects` | R-T | T | L/Q/V/X/Y | Original affected effects with preserved liabilities |

**C4-R decisive vectors:** save an outbox item while disconnected, receive only the first 40 of 100 synthetic bytes, admit a command without starting it, observe an applied result without independent review, and verify output bytes while a charge remains unknown. Each fact must remain at its own subject/scope, with the other facts unknown or separately evidenced. A global success badge, invented full receipt or settlement is the falsifier. Also delay the transport ACK until after a receiver observation; a projection that rejects the valid causal facts merely because its enum expects an ACK first fails. Passing proves these fact joins, not remote honesty or completeness of actual instrumentation.

D-022 keeps **Aggressive / Full / Lazy** as modes and `checkpoint` / `interrupt` / `drain` as mechanisms. Maintain separate facts for request accepted, local fence installed, remote fence observed, interrupt delivered, process exited, containment empty, effects settled and independently verified. C4-S stops a process after an external sink accepted an effect: `process exited` may become true while settlement remains unknown. Reporting external rollback or containment empty from exit alone falsifies the projection. This does not prove that all descendants or uncontrolled effects were observed.

## Q11 One publication ordering for every transferring lane

**Accepted candidate P1:** use the current X `ExposureIntent` as a transport-specific relation admitted through the existing canonical owner, while Q retains lineage/copy semantics and the core retains reservations. This is already a current candidate declaration, not a newly discovered runtime fix. Every transferring lane, including T media, Q memory derivatives and Y workspace materialization, must satisfy the same dependency order.

The genuine alternative is an explicitly versioned Q lifecycle extension that represents expected-copy obligations separately from observed-copy truth. It could satisfy the same semantics, but would broaden Q’s shared state machine. The accepted candidate reuses X’s explicit relation and leaves Q’s current statuses unchanged. Merely moving writes after publication is a rejected negative control.

| Step and exact source relation | Proposed design owner | Source lanes | Consumers | Required binding and receipt |
|---|---|---|---|---|
| P0 private local staging; `local_private_staging` | R-X | X; Q/T/Y | P/Q/T/V/Y | Only admitted local scope/resource envelope; no remote metadata release |
| P1 durable pre-registration; `ExposureIntent`, `exposure_intent_ref` | R-X | X; Q lineage/copy; core reservation | P/Q/T/V/Y | Exact disclosure intent, expected potential-copy inventory, known lineage and applicable reservation committed before any restricted release |
| P2 first current check | R-P | P/X/T | Q/T/V/X/Y | Current recipient, rights, purpose, grant, work/pause fences and deletion cut at the actual release gate |
| P3 release admitted metadata/segment | R-X | X/T | P/Q/T/V/Y | Only exact authorized manifest/range/chunk; actual sender boundary observed under original identity |
| P4 verify and register received material | R-Q | Q with X/T/Y evidence | P/T/V/X/Y | Actual received representation, lengths, integrity, provenance and scoped materialization; observed copy/lineage registered before task visibility |
| P5 second current check | R-P | P/X/T/Q/Y | Q/T/V/X/Y | Current rights/fences/inventory cut rechecked at protected task-publication gate, including after restart |
| P6 task publication | R-X | X coordinated Q/T/Y | P/Q/T/V/Y/L | Publish only verified registered material under exact operation/transfer and current authority |
| P7 observation and reconciliation | R-V | V/X/Q/T/Y; core ledger | P/Q/T/X/Y/L | Append actual publication/disclosure evidence; reconcile original settlement; uncertain facts stay unknown |

These eight steps refine the synthesis’s five grouped steps without adding an invented global order across unrelated operations. P2 and P5 are checks at the protected boundaries, not stale “checked earlier” flags. A check/release or check/publication implementation must make the dependency indivisible relative to revocation or prove the qualified barrier that enforces it. No distributed transaction is assumed.

[Current X ordering and recovery](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L217-L229), [explicit ExposureIntent](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L483-L504) and [IT-03’s independent oracle](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L56-L68) ground this order.

### Exact intent and transfer field map

| Exact field | Proposed design owner | Source lane | Consumers | Binding |
|---|---|---|---|---|
| `ExposureIntent.exposure_intent_id` | R-X | X | P/Q/T/V/X/Y/L | Immutable identity of the potential-disclosure obligation |
| `ExposureIntent.logical_operation_id` | R-X | X | P/Q/T/V/X/Y/L | Original effect lineage, shared with the retry owner |
| `ExposureIntent.transfer_id` | R-X | X | P/Q/T/V/X/Y/L | Exact transfer whose releases this intent covers |
| `ExposureIntent.task_ref` | R-X | X | P/Q/T/V/X/Y/L | Exact admitted task context |
| `ExposureIntent.recipient_scope` | R-X | X | P/Q/T/V/X/Y/L | Actual recipient/audience, including relevant incarnation |
| `ExposureIntent.artifact_representation_refs` | R-X | X | P/Q/T/V/X/Y/L | Exact permitted source/representation identities; no raw/preview substitution |
| `ExposureIntent.expected_copy_record_ref` | R-X | X | P/Q/T/V/X/Y/L | Potential-copy inventory obligation only; not proof that a CopyRecord is present |
| `ExposureIntent.lineage_registration_ref` | R-X | X | P/Q/T/V/X/Y/L | Canonical registration of known source/derivation lineage |
| `ExposureIntent.reservation_refs` | R-X | X | P/Q/T/V/X/Y/L | References to existing admitted liabilities; no copied active reservation |
| `ExposureIntent.policy_revision` | R-X | X | P/Q/T/V/X/Y/L | Exact policy under which registration was admitted, rechecked at use |
| `ExposureIntent.deletion_inventory_cut_ref` | R-X | X | P/Q/T/V/X/Y/L | Inventory cut that must account for this unresolved obligation |
| `ExposureIntent.current_control_fence_refs` | R-X | X | P/Q/T/V/X/Y/L | Typed current applicable fences; no cross-domain substitution |
| `ExposureIntent.canonical_registration_receipt` | R-X | X | P/Q/T/V/X/Y/L | Durable registration evidence required before first restricted release |
| `ExposureIntent.publication_observation_ref_or_null` | R-X | X | P/Q/T/V/X/Y/L | Actual publication evidence or null; null is not nonpublication |

| Exact field | Proposed design owner | Source lane | Consumers | Binding |
|---|---|---|---|---|
| `TransferBinding.transfer_id` | R-X | X | P/Q/T/V/X/Y/L | Stable transfer identity across restart and acknowledgment loss |
| `TransferBinding.task_ref` | R-X | X | P/Q/T/V/X/Y/L | Exact task binding |
| `TransferBinding.workspace_binding_ref` | R-X | X | P/Q/T/V/X/Y/L | Y-owned immutable workspace binding where applicable |
| `TransferBinding.control_capsule_ref` | R-X | X | P/Q/T/V/X/Y/L | Current minimum authorized control capsule, not copied live grants |
| `TransferBinding.artifact_ref_or_scoped_handle` | R-X | X | P/Q/T/V/X/Y/L | One authorized internal reference or freshly resolved outward locator |
| `TransferBinding.content_envelope_ref` | R-X | X | P/Q/T/V/X/Y/L | Exact shared envelope and current restrictions |
| `TransferBinding.representation_ref` | R-X | X | P/Q/T/V/X/Y/L | Exact approved representation, distinct from other derivatives |
| `TransferBinding.recipient_node_incarnation` | R-X | X | P/Q/T/V/X/Y/L | Actual destination lifetime, not merely node name |
| `TransferBinding.purpose` | R-X | X | P/Q/T/V/X/Y/L | Exact authorized purpose; no inferred wildcard |
| `TransferBinding.policy_revision` | R-X | X | P/Q/T/V/X/Y/L | Current policy binding at protected use |
| `TransferBinding.authorized_range` | R-X | X | P/Q/T/V/X/Y/L | Admitted byte/segment/source coverage |
| `TransferBinding.byte_ceiling` | R-X | X | P/Q/T/V/X/Y/L | Finite transfer bound within resource envelope |
| `TransferBinding.chunk_integrity_refs` | R-X | X | P/Q/T/V/X/Y/L | Per-segment byte identity under declared domains |
| `TransferBinding.full_object_integrity_ref` | R-X | X | P/Q/T/V/X/Y/L | Final-object evidence only when full coverage is known |
| `TransferBinding.expiry` | R-X | X | P/Q/T/V/X/Y/L | Exact validity condition; restart does not renew it |
| `TransferBinding.copy_record_refs` | R-X | X | P/Q/T/V/X/Y/L | Observed Q copies, distinct from expected inventory obligations |
| `TransferBinding.reservation_refs` | R-X | X | P/Q/T/V/X/Y/L | Existing canonical reservation lineage |
| `TransferBinding.last_boundary` | R-X | X | P/Q/T/V/X/Y/L | Evidence-qualified latest known boundary, not an optimistic stage |
| `TransferBinding.unknown_reasons` | R-X | X | P/Q/T/V/X/Y/L | Explicit reasons for unresolved exposure/publication/effect facts |
| `TransferBinding.exposure_intent_ref` | R-X | X | P/Q/T/V/X/Y/L | P1 durable pre-release intent |
| `TransferBinding.lineage_registration_ref` | R-X | X | P/Q/T/V/X/Y/L | Registered source/output lineage before task visibility |
| `TransferBinding.publication_observation_ref` | R-X | X | P/Q/T/V/X/Y/L | Actual task-publication observation, not dispatch intent |

| Exact field | Proposed design owner | Source lane | Consumers | Binding |
|---|---|---|---|---|
| `CopyRecord.copy_id` | R-Q | Q | P/Q/T/V/X/Y/L | Identity of this observed governed copy |
| `CopyRecord.artifact_ref` | R-Q | Q | P/Q/T/V/X/Y/L | Exact copied representation |
| `CopyRecord.copy_class` | R-Q | Q | P/Q/T/V/X/Y/L | Declared Q copy class, including residual external/offline classes |
| `CopyRecord.controller_domain` | R-Q | Q | P/Q/T/V/X/Y/L | Who controls this copy; not assumed local |
| `CopyRecord.storage_locator_ref` | R-Q | Q | P/Q/T/V/X/Y/L | Authorized locator without uncontrolled disclosure |
| `CopyRecord.created_before_inventory_cut` | R-Q | Q | P/Q/T/V/X/Y/L | Evidence relation to fenced deletion inventory, not guessed time |
| `CopyRecord.key_scope_ref` | R-Q | Q | P/Q/T/V/X/Y/L | Relevant key scope where applicable |
| `CopyRecord.key_recovery_paths` | R-Q | Q | P/Q/T/V/X/Y/L | All relevant restore/escrow/recovery paths or explicit unknown |
| `CopyRecord.status` | R-Q | Q | P/Q/T/V/X/Y/L | One existing Q status justified by evidence, never planned/staged |
| `CopyRecord.residual_expiry` | R-Q | Q | P/Q/T/V/X/Y/L | Governed residual window, not proof of actual erasure |
| `CopyRecord.evidence_ref` | R-Q | Q | P/Q/T/V/X/Y/L | Observation establishing the stated copy disposition |
| `CopyRecord.observation_freshness` | R-Q | Q | P/Q/T/V/X/Y/L | Freshness/coverage limits of that evidence |
| `CopyRecord.current_policy_ref` | R-Q | Q | P/Q/T/V/X/Y/L | Current rights/hold/deletion policy, independently resolved |

Q’s exact `CopyRecord.statuses` are `present`, `removed`, `verified_unrecoverable`, `expiry_bound`, `retention_held`, `legal_hold`, `disconnected_unknown`, `external_unverified`, `not_applicable_evidenced`. Neither `planned` nor `staged` exists. A record with either value under this unchanged contract is refused as an unrecognized status; it is not silently interpreted as `present`. A registered intent remains an unresolved inventory obligation until copy evidence exists.

The [Q copy record and deletion predicates](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L176-L275) control observed copy truth. All three tables preserve exact source spellings. Field agreement alone does not establish that every actual or possible copy was registered.

## Q12 Crash cuts and the publication conflict table

Remote quarantine is already disclosure **to that node**, because that receiver has obtained information even if its task parser cannot yet consume it. Task publication is a later boundary. Conversely, a durable intent proves an obligation exists, not that transmission or a present copy exists. Sender evidence can establish bytes offered, but does not generally establish exact remote receipt. Preserve a justified lower/upper bound or `unknown`; never upgrade it from a local socket count.

### Crash before and after each step

The oracle for every row knows the synthetic sender release schedule, actual receiver-copy creation, task visibility and inventory cut independently of the implementation. Crash windows lacking that independent evidence remain unknown. All recovery uses the same operation/transfer identity and existing reservation, revalidates current rights, and reconciles before any repeat. The rows specify both sides of **every** P0–P7 step.

| Vector | Crash immediately before | Crash immediately after | Exact falsifying observation |
|---|---|---|---|
| P-C0 staging | No new staged artifact or remote disclosure attributable to this operation | Only a governed private local staged copy; no remote release yet. Recover or clean only under current authority | Staging itself releases metadata remotely or creates an unbounded/unregistered task-visible artifact |
| P-C1 pre-registration | No restricted release permitted. If staging exists, it remains local and governed | Durable intent/inventory/lineage/reservation relation recovered. Remote copy still unknown/unobserved, not present | Release without recovered registration; intent marked delivered/present without receiver evidence |
| P-C2 first current check | No next release until current rights/fences can be resolved | Check result alone authorizes no later stale release. Restart must recheck immediately at protected release | A persisted “check passed” flag bypasses intervening revocation |
| P-C3 release | No claim of actual transmission merely because the intent is present; resolve whether release began | If bytes may have crossed, retain possible disclosure and potential-copy obligation; receipt scope unknown until evidence narrows it | Claim of zero copies/no disclosure from missing ACK, or blind new transfer of the same effect |
| P-C4 verify and register | Known or possible remote quarantine remains disclosure; task visibility prohibited | Exact verified representation and registered observed copy/lineage can be recovered; task publication still separate | Unverified representation published; copy marked removed/complete with no matching evidence |
| P-C5 second current check | Task publication waits for a current protected-gate check | Restart/intervening revoke requires revalidation; earlier successful check is not a durable permit | Publication proceeds using stale grant, work/pause fence or deletion cut |
| P-C6 publication | Intent/copy registration does not prove task publication; if boundary is uncertain, hold | Lost observation produces `publication_unknown` until independently reconciled under original identity | Lost ACK causes a second publication/effect, presumed nonpublication or premature reservation release |
| P-C7 observations and settlement | Actual publication may have happened while its evidence is incomplete; retain unknown and liability | Recover recorded facts and exactly-once settlement; duplicate observations do not create new charges/credits | Observer/journal absence erases a disclosure, or duplicate reconciliation settles/releases twice |

A crash “before release” is a proved no-release state only when the exact boundary/observer establishes that fact. An uncertain recovery point cannot infer it from a missing record. A crash inside registration or settlement requires their atomicity/durability contract to decide committed versus unresolved; no local atomicity automatically extends to an unrelated remote recipient.

### Remaining decisive races

| Vector and genuine competing reading | Accepted candidate outcome | Exact falsifier | Passing does not prove |
|---|---|---|---|
| P-X original X order versus corrected precommit order | Under the historical order, inject crash after task visibility but before copy/accounting registration: independent observer finds an exposed unregistered copy. Corrected order refuses release without P1 and publication without P4/P5 | Corrected candidate exhibits that same invisible exposure | The historical defect ever existed in a deployed runtime |
| P-R1 revoke after P0 before P3 | Keep staged bytes governed; refuse first remote release. Intent may remain as history, without asserting transmission | Revoked bytes/metadata cross the sender gate | Erasure of unrelated prior copies |
| P-R2 revoke after P3/P4 before P6 | Refuse task publication; preserve actual/possible remote disclosure and its residual copies. Cleanup needs current authority | Revocation is represented as undoing remote disclosure, or stale publication proceeds | Remote destruction or unreadability already achieved |
| P-A lose ACK after P6 | Query/reconcile original identity; retain `publication_unknown` until evidence. No new effect or recredit | New transfer ID recreates publication, or missing reply is taken as proof of absence | Exactly-once effect capability of an unqualified receiver |
| P-D race deletion inventory fence with derivative/intent | Pre-fence unresolved intents enter conservative closed inventory; post-fence intent cannot evade current revoke/deletion checks. Incomplete inventory blocks completion | Inventory says complete while a pre-fence potential copy or late derivative is omitted | Global erasure of uncontrolled/prior-recipient copies |
| P-S separate intent relation versus explicitly versioned Q expected-copy extension | Chosen separate relation leaves Q statuses unchanged. Both designs must preserve potential versus observed copy truth | `planned`/`staged` silently accepted as Q status, or intended copy reported present | That either representation has a proven implementation |

P1’s recommendation is falsified by any such unregistered exposure, stale publication or concealed uncertainty. A fully registered, authorized transfer with verified receiver bytes and independent publication evidence is the useful positive control; refusing it without a stated unmet condition is also a failure of the intended contract. Passing these synthetic schedules establishes bounded ordering and inventory behavior only. It does not prove real durability, arbitrary concurrency coverage, erasure, privacy side-channel resistance or actual route delivery semantics.


## Q13 and Q14 One conserving algebra, with a declared representation

### Resource field map

Use the existing R-V `ResourceReservationAccounting` names, rather than inventing a different shared resource record. Proposed design owner is the **core resource-accounting contract**; R-V is the exact declaration/source lane. All participating Q/T/V/X/Y producers and L read/control surfaces consume the same canonical allocation lineage. R-V reports evidence; it does not own a new ledger. [V1][O2]

| Exact field | Single proposed design owner | Source lane | Consumers | Binding relation |
|---|---|---|---|---|
| `settled_consumption` | Core resource accounting | V | Q/T/V/X/Y/L | Validated consumed quantity for one explicit pool, unit, scope and cumulative window; disjoint from still-outstanding reserved liability |
| `outstanding_reserved_upper_bound` | Core resource accounting | V | Q/T/V/X/Y/L | Sum of unique currently outstanding reservation upper bounds in that pool; already includes admitted recovery and uncertain liabilities |
| `control_reserve` | Core resource accounting | V | Q/T/V/X/Y/L | Still-unallocated protected headroom, disjoint from outstanding under the chosen representation; no independent budget |
| `proposed_reservation` | Core resource accounting | V | Q/T/V/X/Y/L | Trustworthy finite upper bound for the exact proposed operation and its admitted children/helpers; same dimension as the pool |
| `approved_limit` | Core resource accounting | V | Q/T/V/X/Y/L | Approved gross limit in the chosen candidate; typed unit/window/scope cannot be inferred from a naked number |
| `representation` | Core resource accounting | V | Q/T/V/X/Y/L | Select exactly `disjoint_withheld_headroom` for this candidate; existing conforming alternative is `tagged_control_inside_outstanding` |

Source: R-V's exact six-field declaration and its accounting rules. [V1] The gross-versus-net meaning must be bound by the containing, versioned accounting/profile interpretation: **there is no existing third `representation` enum for net caps**. This proposal does not silently extend that enum. A net view must carry an unambiguous relationship to the same gross limit and withheld amount. [V1][O2]

Meter evidence must preserve its original dimensions; it is not a second spend account:

| Exact field | Single proposed design owner | Source lane | Consumers | Binding relation |
|---|---|---|---|---|
| `Counter.value` | R-T quantity projection | T | V/core/Q/X/Y | Typed source observation or null, never a default zero |
| `Counter.unit` | R-T quantity projection | T | V/core | Registered dimension; no implicit token-to-money or token-to-subscription-debit conversion |
| `Counter.availability` | R-T quantity projection | T | V/core/L | Exactly `observed`, `modeled`, `inferred` or `unavailable`; this is not V's knowledge enum |
| `Counter.reason` | R-T quantity projection | T | V/core/L | Why a quantity is absent/unavailable or otherwise constrained |
| `Counter.scope` | R-T quantity projection | T | V/core/X/Y | Task/operation/recipient coverage of the quantity |
| `Counter.source` | R-T quantity projection | T | V/core | Actual reporting boundary, separate from authoritative settlement |
| `Counter.source_version` | R-T quantity projection | T | V/core | Exact meter/report interpretation |
| `Counter.observation_time_window` | R-T quantity projection | T | V/core | Named observed interval, not an invented universal clock |
| `Counter.delta_or_cumulative` | R-T quantity projection | T | V/core | Determines valid dedup/delta conversion |
| `Counter.uncertainty` | R-T quantity projection | T | V/core | Quantity uncertainty; does not allocate a second liability |
| `Counter.included_subsets` | R-T quantity projection | T | V/core | Exact inclusion algebra for parent/child/cache/media subtotals |
| `MeterObservation.raw` | R-V evidence interpretation | V | Core/L | Retain presence, raw value, unit, source version, report ID, interval, epoch, cumulative/delta mode and inclusion set |
| `MeterObservation.validated` | R-V evidence interpretation | V | Core/L | `KnowledgeValue` plus exact validation rule/version; raw zero can remain invalid while actual use is unknown |
| `MeterObservation.attribution` | R-V evidence interpretation | V | Core/Q/T/X/Y | Task/parent/child/role/operation/attempt/route/session/meter segment; survives movement and retries |
| `MeterObservation.reconciliation` | R-V evidence interpretation | V | Core | Dedup keys, inclusive/exclusive grouping, reset evidence and source-report references |
| `MeterObservation.ledger_effect` | R-V evidence interpretation | V | Core | Validated consumption increment or retained liability, bound to the original reservation identity |
| `MeterObservation.coverage` | R-V evidence interpretation | V | Core/L | Instrumented/uninstrumented roles and collector sensitivity; absent observation is not zero |
| `MeterObservation.classes` | R-V evidence interpretation | V | Core/L | Tokens, cache classes, native debit, money, host resources and human time remain distinct |
| `MeterObservation.reservation_accounting` | R-V evidence interpretation | V | Core | Reference to the same `ResourceReservationAccounting`; a meter cannot reallocate protected headroom |

Sources: exact T counter and V meter fields. [T1][V2] Do not equate T `availability=observed` with V `knowledge=known`: an observed raw crash report can be invalid evidence of actual use. V distinguishes `known|unknown|unavailable|stale|invalid|redacted`; only a known validated numeric value permits zero. [V3]

### Candidate algebra and transitions

For each independent cumulative pool, let S, O, H, P and L denote the above `settled_consumption`, `outstanding_reserved_upper_bound`, `control_reserve`, `proposed_reservation` and gross `approved_limit`. These are explanatory mathematical symbols, not renamed contract fields.

**Chosen candidate:** `representation=disjoint_withheld_headroom`; ordinary-work admission requires **S + O + H + P ≤ L**. All terms are nonnegative quantities in the same declared unit/window. P is the bounded new liability before admission; after admission it is transferred into O, so it is never counted as both proposed and outstanding. The ordinary-work net view is exactly **S + O + P ≤ L − H**. It subtracts H once; its right-hand side is not then combined with another H addend. [O2][M1]

**Real conforming competitor:** `tagged_control_inside_outstanding`, where protected allowance is represented exactly once inside total outstanding. Then the check is **S + O_tagged + P ≤ L**, with no separate H addend. Changing representation requires an identity-preserving conserving conversion, not relabeling the same allowance into two records. Gross-disjoint is preferable as the initial shared candidate because still-unallocated recovery/control capacity is visibly different from admitted work; this is a clarity rationale, not measured superiority. [V1]

Required shared invariants:

1. S and O are disjoint at every canonical cut. A consumption amount cannot remain outstanding after the same settlement transfer.
2. Uncertain liability is an annotation/subset of an existing reservation in O, never `+ uncertainty` in either formula. Exact use may be unknown while a qualified finite upper bound remains reserved.
3. Protected writer/Stop/evidence/observer/recovery headroom is disjoint or tagged once under an explicit shared-reserve rule. A single unit serving several control categories does not become several units by labeling.
4. Strict-cap expansion requires a trustworthy finite upper bound. An uncertainty policy may supply a justified conservative finite bound; it cannot declare an unknown bound infinite and claim a finite strict cap. A separately admitted non-strict profile is not a silent fallback for a strict-required task. [T2]
5. Settlement is one canonical operation against the original reservation/effect and evidence. For ordinary reservation r and proven measured use c ≤ r: atomically O decreases by r, S increases by c, and only r−c becomes available. If measured use exceeds r, retain the observation, declare the bound/conformance failure and block unsafe further admission; do not clip it to hide an overrun. Conflicting or insufficient evidence holds the unresolved part. Partial settlement, if supported, must partition the same liability without overlapping slices.
6. Recovery admission moves an authorized k from H into O atomically: `(S,O,H) → (S,O+k,H−k)`. It mints no capacity. Proven-unused recovery remainder returns to its protected originating allowance under the same recorded policy; it is not quietly converted into ordinary-work permission. Under tagged representation the corresponding allocation is a relabel/partition of the existing protected reservation.
7. Retry, fork, new upstream session, route switch, machine loss, workflow continuation and calendar rollover do not reduce S, discard O, duplicate an active reservation or renew the task limit. An approved periodic allocation has a separately explicit renewal rule and does not erase old liabilities. A reservation split is its own canonical conservation operation, not copy-on-fork. [M1][Q1][X1]
8. Instantaneous capacity is a **separate typed predicate** over current occupancy, admitted live allocations, protected capacity and proposed peak demand with declared overlap semantics. Cumulative settled CPU time/spend is not current RAM occupancy; different resource dimensions and review capacity cannot be numerically merged without an independently justified conversion. [M1]

### Decisive synthetic resource vectors

Every number below is a fixture constant, not an adopted production bound. Independent expected ledger totals, rather than the candidate's own final number, are the oracle. The first two rows also discriminate positive valid admissions from blanket refusal. [I1]

| Vector | Accepted candidate outcome | Competing reading / decisive falsifier | Explicit non-proof |
|---|---|---|---|
| R13-A: L=20, S=3, O=5, H=3, P=9; 2 of O's 5 are uncertain | Gross 3+5+3+9=20; net 3+5+9=17≤20−3; admit within the remaining guards | Adding uncertainty yields 22 and falsely rejects the positive control; removing its reservation yields understated liability | Arithmetic equality does not validate the meter or the finite bound |
| R13-B: same state, tagged representation O_tagged=8 (5 work +3 protected), P=9 | 3+8+9=20; same admission and remaining protection as gross-disjoint | Adding H again gives 23; subtracting H from L and retaining its left addend also double counts | Equivalent vectors do not select a store or prove concurrent atomicity |
| R13-C: L=20,S=3,O=5,H=3,P=unknown | Refuse affected strict-pool expansion; retain existing O and H; allow separately authorized unaffected/control work only under its own bounds | Null→0, null→∞ with a claimed finite cap, or automatic weaker-mode continuation falsifies | Refusal does not establish future route cost or task completion |
| R13-D: recovery k=2 from S=3,O=5,H=3 | S=3,O=7,H=1; accounted total remains 11. If it settles at c=1, S=4,O=5,H=2, total still 11 | Keeping H=3 when adding 2 to O double counts; adding 2 to both free ordinary headroom and O recredits | Conservation does not prove the reserve can service Stop on a failing disk |
| R14-E: meter PARENT=120 includes CHILD-A=40 and CHILD-B=30 | Total unique consumption=120; with proven complete inclusion, parent-exclusive residual=50. Never 120+40+30=190 | Add all reports, or subtract children without a declared common scope/inclusion relation | A correct sum does not prove uninstrumented helpers cost zero |
| R14-F: an attempt held at r=5 crashes; raw final report says `0` without a valid final meter | Preserve raw 0; validated value=null with invalid/unavailable evidence reason, actual consumption unknown; keep original possible liability in O | Convert raw 0 into known-zero settlement/release of 5 | Retained liability is not a measurement that 5 were consumed |
| R14-G: S=3,O=5,H=3, unique reservation r=4 settles once at c=3 | S=6,O=1,H=3; proven-unused 1 released. Identical duplicate settlement leaves exactly that state; conflicting body under same identity refuses/reconciles | Duplicate gives S=9, negative/out-of-range O, another release, or a new effect/settlement identity | Idempotent accounting does not make arbitrary external effects exactly once |
| R14-H: S=6,O=4,H=2,L=20; fork/new session/new node at midnight | The original allocation lineage remains S=6,O=4,H=2; new work P=9 refuses (21>20). A separately admitted split 4→1+3 preserves total O=4 | Reinitialize S/O, copy O=4 into both forks, or mint a second recovery allowance | Continuity of accounting does not prove useful continuity or savings |
| R14-I: measured instantaneous RAM occupancy falls after process exit, cumulative spend stays unchanged | Capacity may be reconsidered under current capacity evidence; cumulative S does not decrease | “Process exited” refunds settled spend, or lifetime spend is treated as occupied RAM | Capacity observation does not establish quiescence or external settlement |



## Q15 versioned additive semantic map proposal

**Accepted candidate (IN): adopt a separately versioned semantic mapping registry plus typed per-object reference vector.** It is an application/evidence layer, not a format/contract-language choice and not additions to frozen payloads. Each map entry carries:

1. Its mapping identity, immutable version and source-schema/profile/version identity, exact record and field path, and retained original source bytes or authenticated reference
2. One semantic **domain**, authorized **issuer**, exact **subject scope/object reference**, and source revision/value with explicit known/unknown/not-applicable disposition
3. The **relation** binding it to the current object: grant-of, admitted-lease-for, installed-floor-for, assigned-route-for, descriptor-of, effective-config-on-target, activated-release-on-target, compiled-context-for, instance-of, snapshot-of or materialization-of as applicable. These are proposed relation meanings, not silently declared source field names
4. Equality/order/advance semantics within that domain, valid comparison bounds, alias mapping direction, any loss and current-resolution evidence. A numeric value may be a monotonic floor in one source and an opaque identity in another; numeric resemblance cannot establish equality
5. Historical source cut and current resolver/admission evidence separately; changes to mappings produce a new map version and cannot rewrite source history

**Required concrete map dispositions:**

| Source pair/set | Candidate relation | Refused substitution |
|---|---|---|
| X/Y `writer_fence` ↔ V `writer_epoch` | Same named writer domain only after issuer/scope/order semantics match | Filesystem lock, process lifetime, consensus term or membership generation |
| X `work_epoch`, V `work_lease_epoch`, Y `work_fence` | Explicit work-domain links among lease generation and protected receiver floor, including exact task/step/holder and install receipt | A lease ID or floor integer silently substituted for the entire grant; process/release/configuration advancement |
| X `pause_epoch`, V `stop_pause_epoch`, T/Y `pause_fence` | Same declared Stop domain/scope/mode/policy through exact map | Socket close, PID exit, interruption ACK or bare global pause bit |
| L/X/V/T `configuration_revision`, T `config_revision`, Y `effective_config_ref` | Configuration-content/reference mappings by pinned source schema | Y `configuration_epoch` target effective/application generation |
| Y `configuration_epoch` | Adoption/effective relation from exact target to exact configuration content and application evidence | New content revision, ACK or preference coalescing |
| X `release_identity`, V `release_revision` | Exact code/schema content identity/closure only where source semantics agree | Y `release_epoch` activation, work authority or successful boot |
| R-U `epoch` | Grant/revocation-domain binding only when the map defines it completely | Generic epoch catch-all or numeric maximum across domains |

**Refusal boundary:** unsupported map/source version, unknown security-relevant mandatory relation, unbound issuer/subject/domain, conflicting alias values, non-injective identity map, unsupported ordering, or missing current required binding refuses the affected protected operation. Preserve the raw record and safely report an explicit gap/unsupported status where authorized. No silent renaming, coercion, new frozen field, new M1B arm, widened integer range or reinterpretation of `GAP`/Stop is permitted. [S04][S05][S19][S37]

**Rival / decisive vector / non-proof.** Rival: source-version-specific typed adapters with no common envelope, provided the exact semantic join map is still explicit at operation boundaries; for historical replay, version-specific pure interpreters compete with a bounded migration to a common versioned representation. Decisive vector: old frozen command plus X lease, Y application and V evidence carry a higher process/configuration/release generation but revoked work; preserve old bytes exactly and refuse stale work under both old/new map versions. Also supply same-named fields from different issuers and an unsupported mandatory map version: neither may silently join. A mismapped equality/order or accepted stale work falsifies the candidate. Passing proves only declared finite mapping compatibility, not authentication, receiver enforcement, complete schema evolution or correctness of original decisions. [S04][S11][S37]

## Q16 receipt retention and unique logical-command replay

**Accepted candidate (IN): maintain a policy-bound authoritative identity/disposition record and separately retained delivery-occurrence evidence; derive the unique replay view without destroying either conflicts or occurrences.** No particular storage mechanism, retention duration or schema format is selected.

- **Retention domain:** bind policy/version, authority/privacy domain, command identity/digest, original disposition/cuts, operation/attempt/reservation references, payload/interpretation availability and retry/reconciliation window. Retention/tombstones must cover unresolved effects and the declared retry window. V's documented 30-day successful and 90-day failed/disputed *raw-session* defaults are not universal command-dedup TTLs and cannot override unresolved-effect safety or current rights. [S01][S36]
- **Current disclosure:** retained does not mean readable. Authenticate and authorize the current caller/domain/audience/purpose before lookup and again at disclosure. Suppressed/redacted/expired payloads and existence metadata remain governed; lawful purge cannot be defeated by keeping unrestricted digests or reconstructable content only for replay convenience. Preserve the minimum permitted tombstone and explicit replay limitation. [S03][S09][S36]
- **Delivery journal:** each repeated delivery is a distinct occurrence at its own receipt-journal position, retaining its original-command reference, observed delivery context and returned disposition. It does not create another canonical state event or second unique logical-command replay input. Refusals can be journal facts without state mutations. [S09][S10]
- **Unique replay derivation:** select the authorized coherent event/receipt/artifact cut; bind each canonical D/C to one immutable digest/content and original disposition; fold exact duplicate occurrences into references to that unique logical-command input while preserving journal occurrence lineage. A different digest is a conflict, not another replay input and not a duplicate to drop. State replay follows exact source-schema event/receipt grouping and checkpoint convention, including M1A's initial `CheckpointRecorded`; it never assumes raw delivery journal = replay input. [S09]
- **Missing history:** absent digest/disposition/required payload or interpretation yields explicit `receipt-history-unavailable`, dependency gap/incomplete/unsupported as appropriate. Reconcile/hold the same logical operation; never silently reissue with old/new ID, synthesize history, release uncertainty or replenish budget. A sufficient identity tombstone may still answer a duplicate/conflict query while full replay remains incomplete. If policy disallows retaining the needed discriminator, safety is preserved by refusal/hold rather than treating missing evidence as unused identity. [S01][S09][S36]
- **Read-only replay:** consume retained recorded inputs and historical predicates with pinned versions. Record `replayed_recorded_input` versus `rederived_deterministic_result`; `reexecuted_new_attempt` is a distinct newly admitted operation with current authority, resource/fence checks and reconciled effects. It is not part of replay. Historical state may describe a formerly live lease, but no live grant/approval/permit/lease/writer/reservation is activated by reconstructing that description. [S09][S38]

**Conforming rival:** retain the full permitted command/receipt payload through the retry window, versus retain a minimal sufficient identity/disposition tombstone plus governed payload/artifact references and explicit replay availability. Both preserve occurrence/unique-input separation and fail safely if information is insufficient. Direct source-version replay also competes with pure versioned migration, under identical historical and current-read boundaries. [S36][S37]

**Decisive vectors:**

1. Deliver the same D/C/digest three times at journal cuts 4, 7 and 9; expect three delivery occurrences, one original disposition, one unique logical-command replay input, zero replay dispatch and no triple-counted accounting
2. Replace the third occurrence with a changed embedded actor/body digest; preserve/flag conflict and refuse it, rather than silently deduplicating or replaying a second command
3. Retain a receipt after effect revocation: authorized history lookup succeeds without effect; revoked read authorization refuses even existence disclosure
4. Expire payload but retain sufficient tombstone: safe duplicate classification may remain available; state/decision replay requiring expired bytes stops at last verified cut. Delete the needed identity discriminator too: return `receipt-history-unavailable`/hold, never a new effect
5. Replay checkpoint/suffix with M1A's declared initial checkpoint event; changing that convention or treating occurrence count as command count must diverge from independent expected state
6. Supply command-looking recorded response bytes, a fresh node incarnation, or a new provider session during replay: zero actuator/model/network dispatch attempts under a separately qualified independent observation boundary; any such attempt falsifies the pure replay claim

**Non-proof:** a passing retention/replay corpus proves neither legal right to retain all content, universal erasure, true original facts, durable storage outside the qualified profile, complete hidden helper accounting, original decision quality, current execution authority nor productive recovery. No expiry duration is adopted here, and no runtime vector has executed. [S09][S36][S38]



## Q17 Digest-domain binding belongs to the containing interpretation

**Candidate:** preserve internal `ArtifactRef` exactly `(object_type, id, version, content_digest)`. Freeze its interpretation by the containing `ContentEnvelope.schema_revision`, `privacy_domain_id`, representation/byte-identity declaration and referenced interpretation profile. Do not add fields to the four-field base, select a digest algorithm/encoding, expose private digests across domains, or silently normalize raw bytes. [Q2][O3]

| Exact candidate field | Single proposed design owner | Source lane | Consumers | Required binding |
|---|---|---|---|---|
| `ArtifactRef.content_digest` | R-Q shared artifact base | Q | P/T/V/X/Y | Exact bytes of the named immutable representation inside its admitted domain; equality is not origin, permission or semantic fidelity |
| `ContentEnvelope.schema_revision` | R-Q shared envelope base | Q | P/T/V/X/Y | Immutable containing interpretation/version, including approved extension and digest interpretation mapping |
| `ContentEnvelope.privacy_domain_id` | R-Q shared envelope base | Q | P/T/V/X/Y | Internal identity/equality/privacy domain; T `domain_ref` must resolve to the same permitted binding |
| `ContentEnvelope.unit_ref` | R-Q shared envelope base | Q | P/T/V/X/Y | Complete four-field reference; extensions bind this unit, never a separate writable alias |
| `ContentEnvelope.transform_identity_version_config` | R-Q shared envelope base | P→Q | T/V/X/Y | Exact transformation, configuration and normalization relation where a derivative exists |
| `ContentEnvelope.coverage_and_loss` | R-Q shared loss record | P→Q | T/V/X/Y | Coverage of the actual representation and the one loss record; not proof that omitted bytes were covered |
| `media_facets.representation_kind` | R-T media extension | T | Q/V/X/Y | Distinguish original bytes, decoded values, OCR, preview, compiled payload and other declared representations |
| `media_facets.byte_identity.digest_algorithm` | R-T media extension | T | Q/V/X/Y | Exact declared algorithm plus interpretation profile; never guessed from digest length |
| `media_facets.byte_identity.digest` | R-T media extension | T | Q/V/X/Y | Checked equality alias of this unit's digest under the same algorithm/domain/representation |
| `media_facets.byte_identity.byte_length` | R-T media extension | T | Q/V/X/Y | Length of the covered exact byte representation, not decoded size, token count or remote-received amount |
| `media_facets.byte_identity.completeness` | R-T media extension | T | Q/V/X/Y | Complete object vs bounded segment/partial representation; no invented final digest before stream completion |
| `media_facets.byte_identity.domain_ref` | R-T media extension | T | Q/V/X/Y | Explicit resolution to the containing privacy and digest domain |
| P `raw_digest` | R-P source-envelope interpretation | P | Q/T/V/X/Y | Compatibility alias only for the designated raw unit in identical bytes/algorithm/domain; not an alternate truth |
| `ContentEnvelope.extensions.output_digest` | R-P extension meaning | P→T | Q/V/X/Y | Compatibility alias only for the produced `unit_ref.content_digest`; original inputs remain parent references |
| `SourceSnapshot.content_identity_codec_ref` | R-Y workspace extension | Y | Q/V/X | Referenced source-manifest identity/codec interpretation; distinct raw/logical/coherence coverage remains explicit |
| `SourceSnapshot.vcs_object_format_or_none` | R-Y workspace extension | Y | Q/V/X | VCS object identity's declared domain; a VCS tree/object or pack digest is not automatically an artifact-byte digest |

Sources: exact base, T byte identity/alias rules, P original names and Y snapshot fields. [Q2][T3][P1][Y1]

The containing profile must additionally bind **algorithm/domain version and any parameters; object/representation kind; raw-vs-derived normalization policy; exact coverage and ordering; byte length/completeness; source/schema and interpretation version**. For state/replay digests bind the namespace, schema/reducer/canonicalizer and state cut as V explicitly requires. These are semantic obligations for a separately versioned containing profile, **not claims that Q already declares additional fields with those spellings**. No canonicalization algorithm is chosen. Raw-byte identity uses the original bytes without EOL/Unicode/decoding normalization; a normalized result is a distinct versioned derivative with original parent and loss relation. [V4][Y2]

**Conflict rule:** within one admitted privacy domain, an immutable `(object_type,id,version)` object slot cannot be rebound to another `content_digest`, algorithm/domain interpretation or covered representation. Identical repeats under the same full interpretation are idempotent observations. Conflicting duplicates refuse/quarantine and preserve conflict evidence; adding a changed digest to the lookup key cannot turn a mutation of that immutable object into a second valid version. A deliberate new representation needs an admitted new identity/version and lineage. Conflicting P raw/output/T digest aliases reject rather than choose a precedence. [O3][T3]

**Real competitor:** materialize the full digest interpretation inline in every versioned containing envelope, versus referencing one immutable schema/profile binding. Both preserve the same four-field base and exact checks. Choose the referenced binding candidate to avoid interpretation drift across consumers; a missing/unavailable profile must then block verification. Neither competitor is a license to use a globally correlated public content address.

| Synthetic vector | Required outcome / decisive falsifier | Non-proof |
|---|---|---|
| D17-A: same private slot/version and digest text, but first declaration says algorithm/domain A and second says B | Reject conflict; a consumer that accepts because text matches falsifies | Does not prove cryptographic collision resistance |
| D17-B: original bytes `41 0d 0a` and normalized bytes `41 0a` claim the same raw unit/version | Refuse the alias; accept only a separately admitted derivative with its own identity/transform/loss | Digest match never proves semantic equivalence |
| D17-C: complete 10-byte object and first 6-byte segment share a declared final digest | Refuse unsupported completeness; keep partial/segment identity and no invented final value | Local covered bytes do not prove remote receipt |
| D17-D: equal bytes in privacy domains A and B | No cross-domain lookup/dedup/existence/equality disclosure; separately authorized outward handles remain independent | Does not establish absence of every timing/equality side channel |
| D17-E: inline profile and immutable referenced profile encode identical interpretation | Both verify the same known valid bytes. Remove the referenced profile and expect unavailable/refusal, never an inferred default | Positive parity does not ratify an encoding or migration |
| D17-F: unit digest d1 and `extensions.output_digest` d2 for the same output | Reject conflict, no “last field wins” repair | Consistency does not prove output truth or authenticity |

## Q18 Freeze the exact route inputs before admission

**Candidate:** bind every admitted work packet/compiled payload to one immutable, versioned route-input manifest of exact existing references and semantics. This is a proposed join, not an invented existing `RouteFreeze` wire type. A lazy resolver is a real competitor only if it resolves and seals the identical complete input vector before the protected admission/release boundary. “Latest” configuration, ambient defaults and route-name-only matching cannot substitute for the vector. Exact sources distinguish assignment, descriptor revision, effective settings, account class and conformance. [M2][O4]

The required frozen set is:

| Frozen component | Single proposed design owner; source | Exact existing names / required semantics | Consumers and binding |
|---|---|---|---|
| Route assignment | Core route admission; V/X/T | `route_epoch` | X/T/Y/V/L join the exact admitted assignment; it is not the descriptor revision |
| Exact media route identity | R-T route-media facet; T | `provider`, `endpoint`, `hosting_platform`, `harness_interface_build`, `model_revision`, `account_plan_class`, `route_epoch`, `config_revision` | Descriptor applicability is conjunction over all eight `RouteMediaFacet.bindings`; no cross-interface inference |
| Descriptor used for payload | R-T payload contract; T | `CompiledPayloadManifest.route_descriptor_epoch` | Exact descriptor revision/digest/profile evidence used by admission, distinct from assignment |
| Effective configuration | Core configuration resolver; synthesis/T/Y | `configuration_revision`, T route `config_revision`, Y `effective_config_ref` and `configuration_epoch` retain their declared typed relationships | Content revision and target activation are separate; frozen interpretation map must prove equality where aliases apply |
| Interface/control surface | Core route admission; synthesis | Exact build, interface/transport, method set, supported extension/mode and correlated session/turn/attempt mapping | X/L/T/V; do not reinterpret unsupported steer as queue, or protocol ACK as effect settlement |
| Required media cells | R-T; T | `direction`, `content_placement`, `bounded_or_streaming`, `delivery_form`, `media_type`, `container_codec_profile`, `native_or_transformed` | Each required cell must be supported/current; no one “supports media” boolean |
| Media bounds | R-T; T | `source_bytes`, `encoded_request_bytes`, `decoded_bytes`, `item_count`, `pixels_dimensions`, `patches_tiles`, `duration`, `channels`, `frames`, `pages`, `context_units` | Apply every relevant bound; only comparable units/semantics may be intersected numerically |
| Capability/trust evidence | Core route admission; synthesis/T/P | T `documented_bound`, `observed_bound`, `effective_bound`, `source_url_version`, `discovery_method`, `evidence_time`, `expiry`, `conflict_refs`; exact launch/isolation trust profile and required evidence | Documentation, installed-build observation and entitlement/privacy are distinct. `unknown`, `stale`, `unsupported`, `currently_unavailable` cannot become supported by assignment |
| Stop contract | Core Stop semantics; D022/L/X/T | Aggressive / Full / Lazy; exact target/ownership closure, local fence, remote install requirement, interrupt/cancel behavior, named Lazy boundary, finite deadline and escalation; `checkpoint`, `interrupt`, `drain` remain mechanisms | Required mode must be implementable at the exact route; stopped socket/PID is not external rollback |
| Child ownership/retry | Core operation coordinator; synthesis/X | Exact owned subtree/descendants/relaunchers, `retry_owner`, `logical_operation_id`, bounded child/helper allowance and allocation inclusion | All SDK/adapter/scheduler retries map to one retry owner. If child interception is unavailable, the whole permitted subtree must be observable/enforceably bounded and pre-reserved, otherwise refuse effectful fan-out |
| Reasoning-role closure | Core route admission; synthesis | Explicit solver/planner/reviewer/compactor/memory/media/router/recovery role dispositions, including disabled roles | In upstream-only mode each enabled role is deterministic or explicitly eligible upstream; no hidden native helper or weight/network fallback |
| Compaction/caches | Core context governor; synthesis/Q/T | One governor per `route_epoch`; distinct `context_epoch`; exact required capsule, loss/rehydration references, upstream vs separately admitted Recursion compactor, cache scope/retention | Q/T/V/Y; switch of governor is an explicit context boundary; provider hidden state cannot be declared portable |
| Metering | Core resource accounting; V/T | T `quantity_units`, `estimator_version`, `reported_counters`, `included_subset_semantics`, `billing_class`, `native_quota_unit`, `unavailable_reason`; exact V attribution/inclusion/reset rules | Canonical allocation references include all roles, retries, child subtotals, recovery and unknowns; no parent+child double sum |
| Compiled input and recipient | R-T payload contract; T with P/Q/Y | `operation_ref`, `attempt_ref`, `task_goal_revision`, `authority_decision_ref`, `privacy_rights_revision`, `pause_fence`, `route_descriptor_epoch`, `configuration_revision`, `recipient`, `purpose`, `ordered_content_refs`, `exact_content_digest_or_stream_manifest`, `content_length_bound`, `wire_encoding`, `budget_reservation_ref` | All text/media, filenames/metadata, relevant non-credential headers, URL/redirect disposition, audience, transform/loss; actual bytes/handles checked at release. `wire_encoding` is an exact per-profile binding, not a selection by this report |
| Workspace and current authority | Core work admission; Y/X/P | Current GoalSpec/plan/grant/rights, writer/work/pause dependencies, `WorkspaceBinding`/source/materialization and exact `platform_profile_ref`; historical `authority_decision_ref` is evidence only | Resolve current protections again at irreversible gates; manifest freezing does not freeze permission forever |
| Required C/T separation | Core trusted-launch admission; synthesis/P | Exact unmodified build's support separating credential-facing C from untrusted tool/output T, or independently demonstrated equivalent; explicit credential trusted computing base, direct/induced paths and attacker model | **C/T is credential/tool separation**, not a generic media/capability abbreviation. Missing required support refuses strong-required work; policy-only needs separate operator admission and cannot be automatic fallback |

Exact T fields and support states: [T4][T5]. General route/child/retry and context/authority joins: [M2][M3][Y3]. D022/Stop and reserved control-path scopes: [L1][X2]. C/T prerequisite: [I2][P2]. No credentials, account identifiers or live route are needed to specify this synthetic freeze set.

**Pre-admission decision:** seal the exact vector, validate every required capability and trust floor against current applicable evidence, and bind reservation plus exact inputs. A descriptor may advance from d4 to d5 while assignment `route_epoch=7` remains the same. Queued work bound to d4 must not silently use d5; it either remains valid under explicitly current d4 evidence or is freshly resolved/re-admitted against d5. A new assignment 8 with the same expired d4 evidence is still ineligible. Admission and final egress rechecks are separate, so an immutable vector does not preserve expired permission. [O4][T4][T5]

| Synthetic vector | Accepted outcome / decisive falsifier | Non-proof |
|---|---|---|
| RF18-A: assignment7, descriptor4; descriptor5 changes input mode while work waits | Assignment remains7 until an actual new assignment; old payload cannot silently change descriptor or mode; explicit revalidation/re-admission or refusal | Does not qualify either real descriptor |
| RF18-B: expired descriptor4, newly minted assignment8 | Required capability remains stale; refuse. Epoch increment alone is falsifying “refresh” | No account entitlement follows |
| RF18-C: route can spawn two hidden children, subtree budget only covers parent, child meter unknown | Refuse effectful bounded fan-out unless exact whole-subtree enforcement/pre-reservation is demonstrated; a separately admitted proposal-only profile is distinct | Does not establish that unknown helpers are absent |
| RF18-D: upstream-only compaction activates a native OCR/model helper | Refuse before helper dispatch; native call under an apparently continuous session falsifies | No quality or cost benefit follows from correct refusal |
| RF18-E: strong C/T requirement, rich protocol controls but no demonstrated build-specific C/T separation | Strong-required admission refuses; no automatic policy-only continuation | Structured protocol is not confinement proof |
| RF18-F: eager vector vs lazy resolution; config changes between initial request and protected gate | Both bind the same current complete vector or explicitly refuse/re-admit; divergent effective meaning falsifies one | No latency/engineering-effort winner is measured |
| RF18-G: required Lazy boundary has no observable checkpoint and no finite deadline/escalation | Refuse that unsupported required Stop profile; socket close is not a substituted Lazy completion | Does not establish remote cancellation or settlement |

## Q19 Coherent capture and protected apply on exact profiles

### Exact field bindings and the three conceptual capture classes

R-Y remains the single proposed design owner for source/workspace capture and application records; core owns admission and current resource/authority facts. X carries governed bytes, T/Q govern their envelope, V records independent observations. The following fields do not become execution authority merely by being present. [Y1][Y3]

| Exact field | Design owner / source | Consumers | Binding |
|---|---|---|---|
| `WorkspaceBinding.platform_profile_ref` | R-Y / Y | X/T/Q/V/core | Exact OS/build/filesystem/mount/case/path/metadata and supported-operation profile |
| `WorkspaceBinding.capture_requirement` | R-Y / Y | X/Q/V/core | Required byte, logical and/or coherent preservation claim |
| `WorkspaceBinding.profile_set_ref` | R-Y / Y | X/Q/V/core | Immutable selected profile set, separate from grants |
| `WorkspaceBinding.permitted_resource_set` | R-Y / Y | X/V/core | Exact writable/readable resources, including shared repository administration where applicable |
| `SourceSnapshot.capture_class` | R-Y / Y | X/Q/V | Exact source enum, not a fuzzy “snapshot succeeded” label |
| `SourceSnapshot.preservation_relation` | R-Y / Y | X/Q/V | Logical VCS state, exact included working bytes and coherent-cut claims remain separate |
| `SourceSnapshot.coherence_evidence_ref` | R-Y / Y | X/Q/V | Evidence of valid global cut or exact scope/interval, never endpoint hashes alone |
| `SourceSnapshot.capture_interval` | R-Y / Y | X/Q/V | Recorded capture observation interval; not global atomicity |
| `SourceSnapshot.source_cut` | R-Y / Y | X/Q/V | Declared source cut and evidence joins |
| `SourceSnapshot.coverage_ref` | R-Y / Y | X/Q/V | Included, missing, excluded, unsupported and unknown components |
| `SourceSnapshot.external_object_refs` | R-Y / Y | X/Q/V | Exact required external/LFS objects and availability; absent is not empty or auto-fetchable |
| `SourceSnapshot.nested_source_refs` | R-Y / Y | X/Q/V | Nested repository/gitlink/index/working scope; no implicit recursive hydration |
| `SourceSnapshot.retention_pin_refs` | R-Y / Y | X/Q/V | Required immutable closure retained through capture/verification |
| `SourceSnapshot.member_fields.alias_group_ref_or_unknown` | R-Y / Y | X/Q/V | Aliases in declared scope; unknown out-of-scope writable aliases defeat exclusivity claims |
| `SourceSnapshot.member_fields.observed_file_identity_ref` | R-Y / Y | X/Q/V | File identity observed on the exact profile, distinct from a path string |
| `Materialization.mutation_generation` | R-Y / Y | X/V/core | Current destination mutation generation; not source identity |
| `Materialization.mutation_owner_ref_or_none` | R-Y / Y | X/V/core | Current admitted mutator over the specified resource set, never a copied source grant |
| `Materialization.shared_resource_refs` | R-Y / Y | X/V/core | Shared VCS administration/aliases/caches requiring separate protection |
| `Materialization.verification_refs` | R-Y / Y | X/Q/V/core | Actual destination bytes/types/metadata/closure evidence |
| `ApplicationIntent.exact_base_source_vector` | R-Y / Y | X/V/core | Exact base against which apply is admitted and protected through the write window |
| `ApplicationIntent.desired_candidate_vector` | R-Y / Y | X/Q/V/core | Exact reviewed desired result; review is not current application permission |
| `ApplicationIntent.target_materialization_refs` | R-Y / Y | X/V/core | Exact authorized destinations |
| `ApplicationIntent.expected_target_generations` | R-Y / Y | X/V/core | Compare against actual destination generation at protected apply |
| `ApplicationIntent.permitted_resource_set` | R-Y / Y | X/V/core | Exact resources whose mutation is admitted |
| `ApplicationIntent.operation_id` | R-Y / Y | X/V/core | Stable application effect identity through crash/lost reply |
| `ApplicationIntent.retry_owner` | R-Y / Y | X/V/core | One owner reconciles that operation; no blind new patch identity |
| `ApplicationIntent.verification_gate_ref` | R-Y / Y | X/V/core | Exact independent postcondition/gate, distinct from observed apply |

These are literal candidate names, including the nested member-field descriptors; source paths are in [Y1][Y3][Y4]. The application also preserves its exact `writer_fence`, `work_fence`, `process_incarnation`, `configuration_epoch`, `release_epoch`, `pause_fence`, current policy/authority and expiry; the other identity section owns their domain mapping. [Y4]

The brief's three conceptual classes must not erase a fourth **exact enum spelling** already declared by Y:

| Conceptual class | Existing exact `capture_class` values | Admission claim |
|---|---|---|
| A: Immutable closure / qualified stable read view | `immutable_closure`; separately declared `qualified_storage_snapshot` | Coherent only with complete required immutable closure, a coherent dirty overlay where required, retained objects and qualified scope/volume boundaries |
| B: Enforced quiescence | `enforced_all_writer_quiescence` | Coherent only when every relevant writer is excluded for the whole capture interval; indexes, refs, working/nested state and aliases included |
| C: Bounded validated capture | `bounded_observed_capture` | Exact captured artifact and observation interval only; **must refuse a coherent-fork requirement**, even with equal before/after hashes |

Source exact enums and coherence rule: [Y1]; conceptual rationale: [Y2]. A qualified storage snapshot is a separately named stable-read mechanism, not proof that every platform supports one. No filesystem freeze or snapshot technology is selected or run here.

### Exact profile and window obligations

Freeze source and destination workspace identities, member/resource set, OS/build/architecture, filesystem/volume/mount semantics, permitted metadata/types, name encoding/case/normalization, external-object closure, capture method/coverage, and protection/exclusion of all writers and aliases. D028's native Windows/Linux floors are accepted facts, **not** automatic workspace qualification: Windows 11 25H2/build 26200 Home/Pro and 24H2/build 26100 Enterprise, x64 primary, local NTFS; Linux 6.12 primary/6.6 compatibility, cgroup v2/local ext4; WSL2-ext4 and WSL2 `/mnt/c` are distinct dev/test profiles. Source shares/removable volumes and cross-volume behavior require explicit support dispositions; do not extend canonical-state storage claims to every workspace. [D28][Y2]

A valid immutable closure includes the required committed objects, logical index/stages, working/untracked/explicitly allowed ignored bytes, relevant attributes/configuration, nested objects and LFS material. A pointer is not the pointed-to object. Exclusions and missing required material remain explicit; no hidden fetch, helper, indexer or model fills them. Raw-byte identity excludes silent EOL/encoding/filter transformations. Symlink text/type is captured without traversal by default; hardlink/reparse/ancestor swaps and unknown alias reach must not escape the declared boundary. Required ACL/xattr/ADS/mode facets and target name/case representability are checked, not silently normalized. [Y2]

The protected sequence is enumeration→safe open→coherent read→complete byte/lineage registration→copy→**actual destination verification**→current protected apply→durable same-operation receipt/reconciliation. The same file handle avoids one path-swap race but does not exclude writes to that inode. A sender hash or successful copy syscall is insufficient destination evidence. Stage restore into a new empty contained destination; do not overlay an existing tree as implicit restore. [Y2]

**Apply candidate:** publish a staged immutable candidate into a newly admitted materialization under current authority and exact target semantics. **Real conforming rival:** protected in-place application with a qualified exclusive mutation boundary over the entire check-to-write interval, exact expected generations, retained per-path evidence and independently observed postcondition. Both can be conforming; no universal winner is selected. A cooperative lock while external writers remain active is a negative control. No single transaction across unrelated repositories or rollback follows from either option. [Y4][Y5]

### Decisive synthetic capture/apply vectors

| Vector | Required outcome / falsifier | Non-proof |
|---|---|---|
| Y19-A: independent writer states `(x,y)=(0,0)→(1,0)→(1,1)→(1,0)→(0,0)`. Before and after scans both hash `(0,0)`; capturer reads x=0 first and y=1 during `(1,1)` | Captured `(0,1)` never existed. `bounded_observed_capture` may record those exact bytes/interval, but must refuse coherent-fork status; coherent status from endpoint equality falsifies | Rejecting this schedule does not prove all-interleaving coherence |
| Y19-B: immutable committed closure but dirty overlay changes during capture | Reject coherent claim unless overlay itself has qualified immutable/quiescent coherence; committed pin alone is insufficient | No hermetic build/environment claim |
| Y19-C: destination file hardlinks original; candidate mutation changes original | Refuse usable independent materialization; independent alias graph and original before/after bytes expose failure | Same content hashes do not prove isolation |
| Y19-D: source has valid LFS pointer but object missing; nested source also missing | Required exact restoration blocks with missing coverage; no lazy download, empty file or fabricated substitute | Does not prove unavailable content is recoverable |
| Y19-E: source includes distinct `A` and `a`, destination profile cannot represent both | Exact restore refuses or requires a separately admitted explicitly lossy derivative; never silent overwrite/rename | No universal filesystem compatibility |
| Y19-F: apply preview checks base a, external writer changes it to c before write | Protected in-place either prevents the concurrent mutation or refuses before stale overwrite; new materialization preserves original. Bare check-then-apply fails | A single-file success is not multi-repository atomicity |
| Y19-G: apply first repository, crash before second/reply | Retain partial/uncertain state under original `operation_id`; reconcile exact effects and authority; no new-ID retry/reset/clean/stash/rebase/fetch | No rollback or eventual completion guarantee |
| Y19-H: true complete immutable view and separately enforced all-writer quiescent view capture identical valid state | Both pass their declared scoped coherence relation; blanket refusal fails positive utility control | Does not select snapshot technology or prove performance superiority |

The independent oracle must supply writer schedule/valid global cuts, expected bytes/types/metadata, alias graph, destination state, original preservation and per-repository effect identities. Candidate hashes and its own `coherent=true` verdict cannot be that oracle. [I3]

## Q20 Receiver fence installation is a distinct barrier

**Candidate:** a pushed durable receiver fence is installed and evidenced at the trusted final irreversible-acceptance boundary before conflicting successor work can rely on it. The receiver serializes installation and effect acceptance; a check followed by an unguarded write is invalid. An unrelated external service is not included in the receiver's local transaction by assertion. [X2]

| Exact `ReceiverFence` field | Single proposed design owner / source | Consumers | Binding |
|---|---|---|---|
| `issuer_ref` | R-X receiver contract / X | Core/L/V/Y/T | Authorized issuer/install provenance; an authenticated node's arbitrary larger number is insufficient |
| `receiver_resource_scope` | R-X receiver contract / X | Core/L/V/Y/T | Exact receiving actuator/resource, not every sink on that host |
| `fence_domain` | R-X receiver contract / X | Core/L/V/Y/T | Typed writer/work/pause domain being fenced |
| `current_floor` | R-X receiver contract / X | Core/L/V/Y/T | Durable monotonic installed floor within that domain/scope |
| `expected_revision` | R-X receiver contract / X | Core/V | Compare-and-install precondition, preventing stale installation |
| `installation_command_id` | R-X receiver contract / X | Core/V/L | Immutable current installation operation identity |
| `durability_receipt` | R-X receiver contract / X | Core/V/L | Actual installed-floor evidence under exact receiver persistence/restart profile |
| `receiver_incarnation` | R-X receiver contract / X | Core/V/L | Exact receiver instance to which that installation evidence applies |

Source exact fields/checks: [X3]. Candidate `race_states` remain distinct facts: `revocation_accepted`, `installation_pending`, `fence_installed`, `preinstall_effect_unknown`, `quiescence_observed_or_unknown`. These are not a linear success enum; different resources/observers may have different states simultaneously. [X3]

Canonical revocation proves a decision at the canonical boundary, not a remote installation. Between canonical revocation and receiver installation, a previously admitted request may still reach the old receiver boundary or an external sink. Preserve the canonical cut, last valid dispatch boundary, receiver high-water/incarnation, possible operation/effect identity, receipt coverage and held reservation. Do not announce remote Stop completion, zero effect or released liability from an absent ACK or a stopped process. Installing the new floor closes later acceptance at that receiver; it does **not** settle an effect already dispatched outside it. [X2][X4]

Conflicting replacement has three distinct prerequisites: relevant accepting sinks must reject old work; earlier possible conflicting effects must be reconciled or protected by a demonstrated stable-idempotency/postcondition contract; and any required physical non-overlap must have independent old-process quiescence evidence. If required evidence is unavailable, hold (`replacement_blocked_unknown` in X's report). Independently established quiescence/no-effect can close an applicable old-executor risk, but process exit alone cannot cancel an already-dispatched external effect. A new current lease, process incarnation or writer election cannot manufacture any of these facts. [X2][X4]

**Real conforming competitor:** online serialized admission at a trusted final actuator, failing closed when it cannot verify current authority. Compare it against pushed durable scoped fences plus acknowledged installation barriers and explicit exposure classification. Both require the final irreversible gate and honest treatment of already-dispatched effects. Cached time-bounded leases alone are a forbidden shortcut, not the conforming rival. [X2]

| Synthetic vector | Required outcome / falsifier | Non-proof |
|---|---|---|
| F20-A: A work7 delayed; canonical authority revokes7, R durably installs8; A7 then reaches R | Refuse `stale_work_fence`; independent sink mutation count=0; after restart same request still refuses | No instantaneous revocation at offline receivers |
| F20-B: canonical revocation8 committed, R still installed7, old effect already dispatched, ACK lost | `installation_pending` and `preinstall_effect_unknown`; original liability held; conflicting B8 cannot dispatch | Missing receipt does not prove actual effect count0 or1 |
| F20-C: after F20-B, R installs8 but old external effect remains unresolved | Local install can be established; external effect stays unresolved and conflicting replacement holds until proper reconciliation/idempotent protection | Receiver installation is not external rollback |
| F20-D: receiver restarts from stale persisted7 after acknowledged installed8 | Must recover floor8 or refuse service; accepting7 falsifies profile durability | Local file-size/fsync evidence is not declared reset/replay qualification |
| F20-E: untrusted enrolled node submits floor999 or valid floor for different scope | Refuse unauthorized/wrong-scope installation; do not revoke current holder by numeric magnitude | Authentication is not authority |
| F20-F: install check passes, then unprotected mutation occurs after revocation races | Independent sink exposes stale mutation; check and irreversible gate must be protected together | Passing one schedule is not all-interleaving safety |
| F20-G: both conforming alternatives receive one currently authorized operation and one stale operation | Exactly one allowed effect and zero stale effects under the admitted fault/scope assumptions; blanket refusal does not pass | No exactly-once promise for arbitrary sinks or physical non-overlap without quiescence |

## Q21 Independent evidence still missing before adoption/acceptance

### What this reconciliation actually establishes

**Locally observed static evidence:** the inspected declarations contain the exact field names and proposed rules cited here. The synthesis describes Q/T/X/Y textual compatibility and corrected candidate joins. **Inferred:** the single-owner map, explicit gross-disjoint selection, containing digest interpretation, route freeze and capture/fence resolutions in this report. **Unverified/unexecuted:** all synthetic outcomes, runtime enforcement, physical durability, privacy behavior, conservation under concurrency, qualification and performance. Static parity is not ratification or an independent runtime oracle. [O5][I4]

No field map moves to accepted merely because a JSON/schema validator, shared library or two implementations agree. An independently authored oracle must not derive its expected answers from the same candidate reducer, field-map generator or self-reported producer flag. Two independently conforming implementations are a useful competitor to a single reference-semantics oracle, but agreement alone is insufficient if both share assumptions or miss effects. Both need independently held ground truth, sensitive positive controls and bounded coverage. [I4][L2]

### Required evidence package

| Join | Independent runtime observations required | Decisive falsifier | Passing scope / non-proof |
|---|---|---|---|
| Identity command and replay | Independently supplied issuer/domain/object bindings and frozen source bytes; actual lookup disclosures and effect counts; three duplicate delivery occurrences versus one unique replay input; conflicting embedded actor/body bytes; expired identity history; zero replay dispatch across crash/session/node changes | Any cross-domain authority repair, unauthorized existence disclosure, changed-content duplicate accepted, extra unique replay input, blind resend on expiry or replay-caused actuator/model call | Exact identity and historical-disclosure corpus only; no production authentication, unlimited retention or external exactly-once guarantee |
| Receipt cuts and projections | Independent canonical and receipt-journal cuts, observer/stream incarnations, exact event and UTF-8-byte framing maps, source manifests and actual installed snapshot/cursor observations | Receipt ordinal equated with canonical ordinal, byte/event unit substitution, invented cross-domain order or cursor advanced beyond installed bytes | Declared causal joins only; no synchronized global clock, physical causality or hidden-stage completion |
| Cumulative conservation | Hand-authored unique-liability ledger; actual reservation/admission/settlement cuts; raw/validated meters; parent/child inclusion; unknown/reset/correction records; concurrency and duplicate settlement fault cuts | Any synthetic R13/R14 discrepancy, phantom free capacity or double release | Exact typed-pool/corpus semantics only; no native debit accuracy, savings or vendor-intent claim |
| Digest interpretation | Independently retained input bytes, exact domains/profile versions, partial/complete coverage, derived normalization and conflicting duplicate/alias cases | A mismatch is accepted or private equality/lookup widens | This representation/profile corpus, not cryptographic security, authenticity or semantic fidelity |
| Route closure | Independently trapped synthetic dispatch/helper/child paths; exact role manifest; input/descriptor/config freezes; owned process graph, loss/compaction and complete meter coverage | Hidden native helper, stale capability admitted, unsupported control substitution, unbounded child or second retry owner | Synthetic route seam only; no real route, account, entitlement or C/T qualification |
| Capture/apply | Independent writer schedule/valid cuts, bytes/types/metadata, original state, alias graph, missing external objects, protected receiver/write-window events and effect identities | ABA/mixed-time accepted as coherent; stale-base write; shared alias; hidden hydration or new-ID retry | Exact workspace/platform profile; no hermeticity, arbitrary filesystem support or cross-repository atomicity |
| Receiver barrier | Independently observed durable installed floors/incarnations, canonical commit/ACK cuts, actual synthetic sink mutations, external-dispatch uncertainty, restart recovery, current/old ownership and quiescence when required | Stale-after-install mutation; install ACK with regressed recovery; conflicting replacement during unresolved exposure | Exact receiver/fault assumptions only; no instantaneous offline Stop or external rollback |
| Publication/content joins  | Independent copy/exposure schedule, actual bytes/recipient, inventory cut, disclosure intent, actual copy and publication observations | Any unregistered actual/possible disclosure, alias widening or stale publication | Corpus lifecycle only; no global erasure or complete privacy guarantee |
| Disabled/zero-activity claims | Every independent probe first detects its own admitted harmless synthetic sensitivity event, then resets to the declared baseline for the absence run | Blind/missing probe reported as zero or task success used as detector calibration | Observed graph/interval only; zero dispatch attempts is not a billing fact |

The later admitted package must freeze exact source/candidate bytes, profile, corpus, observers, causal/evidence cuts, fault points, finite limits, result classes and independent review. Include successful authorized work as well as rejection vectors. Preserve raw expected-versus-observed artifacts, observer loss, all attempts and unknowns. A failed or blind oracle yields unknown/blocked, not PASS. Pure/model checks, separately authorized synthetic OS/runtime tests and independently authorized real route comparisons remain separate layers; passing one authorizes none of the others. [I4][I5]

Native platform durability must use its declared fault model: an acknowledged canonical commit under D028's application-consistent abrupt-VM-reset requirement needs independent replay parity, not a process-kill/fsync/file-size surrogate. Current historical FU04 and reduced FU03 results do not fill these joins. A successful synthetic sink does not qualify a real provider. A route/profile can become accepted only after its specific evidence and independent review, with Owner adoption for design/acceptance decisions; this research performs neither. [D28][I4][I6]

**Global explicit non-proofs:** no technology/encoding/schema-format/transport/vendor selection; no live route, provider, model, node, account, credential or receiver contact; no contract deployment; no change to frozen M1A/M1B/M1C; no qualified privacy, erasure, containment, durability, performance, cost, native-quota or economic advantage; no vendor-intent inference; no rollback or instantaneous offline revocation; no cloned grants/approvals/leases/launch permits/reservations; no reopening of accepted Owner decisions.



## Compact conflict register 

| Conflict / open join | Accepted candidate | Genuine conforming competitor; rejected shortcut | Decisive vector | Non-proof |
|---|---|---|---|---|
| All identities versus one epoch | Typed per-domain map/vector, source names preserved | Separate typed source records plus exact join manifest; reject lexicographic/max epoch | ID-03/14/16/23 | Physical enforcement, current host honesty |
| Writer/work/pause source-name drift | Same-domain maps only with issuer/subject/advance relation | Source-profile-specific adapters without common envelope; reject silent alias | Old-source map + new process, stale work must refuse | Frozen-contract semantic implementation |
| Role/coordination/work/input conflation | Separate independent required grants/leases | Explicit Head-mediated coordination queue with same executive/work/control guards; reject room/focus authority | ID-05/06/07 | Safe arbitrary autonomy or terminal containment |
| Route descriptor/assignment conflation | Descriptor evidence separate from assignment | Re-resolve exact descriptor on each protected use versus sealed descriptor with invalidation; both have current checks | ID-10/11 | Route qualification |
| Config/release content versus activation | Content identity plus per-target application/activation receipt | Eager target adoption versus staged per-target adoption, both explicit; reject content-equals-effective | ID-13/15/16 | Successful application/boot, external rollback |
| Workspace logical/physical/capture/apply identities | Registered workspace/repository plus instance/snapshot/materialization relations | Eager sealed binding versus lazy hydration sealed before use; reject path/commit identity | ID-19–22 | Coherence, hermeticity, current execution rights |
| Evidence global order | Explicit source cut vector and causal joins | On-demand causal fold versus persisted rebuildable index; reject timestamp/global-counter join | Q3 mixed-order/duplicate/filtered byte case | Physical causality or durable storage |
| Original L/V namespace mismatch | Canonical D/C with immutable actor/auth/body digest | Direct canonical IDs versus durable injective principal-local ingress map; reject second canonical principal namespace | Q5(b2)/(d) | Authorization-policy correctness or exactly-once remote effects |
| Digest made a key component | Equality/conflict predicate under fixed command/sink key | Full immutable-byte comparison versus pinned digest plus exact-byte binding checks; reject changed-body new namespace | Q5(c) | Collision resistance/authenticity |
| Command/operation/attempt collapse | One stable logical-effect retry owner, distinct delivery and attempts | Canonical centralized owner versus disjoint bounded coordinators with explicit owner transfer; reject SDK+workflow double ownership | ID-17/18 and unknown-dispatch handover | Receiver truth or physical quiescence |
| Receipt occurrence versus unique replay input | Retain occurrence journal; derive unique immutable-command view | Full retained payload versus sufficient tombstone plus governed refs; reject raw-journal replay | Q16(1)/(2)/(5) | Full reconstruction when dependencies expire |
| Retention expiry versus unused identity | Hold/reconcile with `receipt-history-unavailable` | Sufficient tombstone versus full retention; reject resend on cache miss | Q5(e)/Q16(4) | Indefinite history availability |
| Historical receipt versus fresh effect authority | Current read check; historical disposition preserved; zero redispatch | Indexed receipt lookup versus bounded pure replay for history; reject old-acceptance replay | Q16(3)/(6) | Current grant or productive continuation |



## Content and publication conflict register

These rows join the detailed field maps to competing interpretations. “Rejected reading” identifies the concrete ambiguity or unsafe shortcut; the conforming competitor remains a viable design under the same required semantics.

| Conflict | One accepted candidate | Rejected reading and genuine conforming competitor | Decisive vectors | Non-proof |
|---|---|---|---|---|
| Internal ArtifactRef versus outward locator | Four-field internal identity; separately authorized audience/purpose locator | Reject serialized private digest/identity as a public grant. Rival: domain envelopes with total checked identity adapters | C1-R/C1-H | Secrecy, authenticity, availability or side-channel resistance |
| Q base versus P/T/Y extensions | Exact eighteen names; extensions explicitly namespaced/versioned | Reject `project_id` as base audience/domain alias or implicit nineteenth base field. Rival: independently mapped domain records preserving all eighteen semantics | C2-A/B/C/D | Runtime access enforcement or complete schema evolution |
| Base digest/locator versus compatibility alias | One immutable binding under declared interpretation; conflicting duplicates reject | Reject last-writer-wins/“most specific” precedence. Rival: one inline canonical value with mechanically derived alias views | C2-E and Q17 vectors | Cryptographic integrity or actual source fidelity |
| Possible influence versus selected citations | Complete observed-input union and restrictive audience/purpose intersection | Reject citation-pruned provenance or unknown-purpose wildcard. Rival: conservative whole-context lineage versus independently justified fine-grained deterministic lineage | C2-F | Completeness of real unobserved input sets |
| Q `coverage_and_loss` versus T `loss_manifest` | One immutable loss record with fourteen typed media facets | Reject two writable loss truths or semantic recovery from a later summary. Rival: one inline typed loss record and read-only derived views | C3-L | Arbitrary semantic accuracy or universal equivalence |
| Receipt words with different scopes | Independent subject/observer facts and source-term-specific meanings | Reject one success enum or transport/application aliases. Rival: separate journals joined on exact identities/cuts instead of common projection | C4-R/C4-S | Receiver honesty, physical durability or external rollback |
| X historical publication-before-registration | Durable exact exposure intent first; verified copy registration and current gate before task publication | Reject post-publication bookkeeping. Rival: explicitly versioned Q expected-copy lifecycle extension with the same potential-versus-observed distinction | P-X, P-C0–P-C7 | Runtime implementation or complete concurrency coverage |
| Potential copy versus Q CopyRecord truth | Intent creates inventory obligation, not `present`; current Q statuses unchanged | Reject silently added `planned`/`staged` states. Rival: explicit separate expectation type in a future Q version, still not observed-copy status | P-S/P-D | Complete deletion or disappearance of external copies |
| Disclosure versus task visibility | Remote quarantine is disclosure; task publication has its own second current check | Reject “quarantined means private to sender.” Rival: keep all staging sender-local until a single authorized transfer, while preserving both boundary facts | P-R1/P-R2/P-A | Erasure or no remote observation after revocation |
| Missing acknowledgment versus no effect | Retain original identity, unknown disclosure/publication and liability; reconcile | Reject new-ID resend or zero from silence. Rival: independently evidenced sink-idempotent repeat under the same effect key where qualified | P-C3/P-C6/P-C7/P-A | Exactly-once external execution on an unqualified sink |


## Reconciled join disposition

The synthesis lists seven contract joins, followed by the independent-evidence obligation. This report proposes one disposition for each; none is Owner-adopted merely by appearing here.

| Join | Single candidate | Decision and vector coverage |
|---|---|---|
| Epoch and identity map | Versioned additive semantic mapping; typed issuer/domain/object relations; no frozen rename | Q1–Q3 and Q15 |
| Receipt retention and replay | Authorized historical evidence; repeated delivery occurrences remain separate from unique logical-command replay; expired history holds | Q4–Q6 and Q16 |
| Digest-domain binding | Containing interpretation fixes algorithm/domain/normalization/coverage/schema, with conflicting duplicates refused | Q7–Q9 and Q17 |
| Registration installation and publication | Durable potential-disclosure obligation before release; actual verified copy registration before task publication; two current checks | Q10–Q12 |
| Route freeze | Exact per-route capability/trust/input/Stop/children/context/metering interpretation and evidence frozen before admission | Q18 |
| Coherent capture and protected apply | Qualified immutable closure or all-writer quiescence for coherence; bounded observed capture cannot satisfy coherent fork; protected exact-base apply | Q19 |
| Receiver install barrier | Current receiver installation evidence or independently sufficient quiescence before conflicting replacement; pre-install exposure remains explicit | Q20 |

The separate Q21 obligation is an independent runtime oracle over an explicitly admitted implementation/profile, plus Owner adoption. Source agreement, field parity, report review and the arithmetic of examples cannot replace it.

## Explicit non proofs

This reconciliation does not establish:

- Implemented semantics, an executable shared contract, adopted wire, migration compatibility or a qualified route
- A universal total order across evidence cuts, trustworthy clocks, or current permission from historical receipts
- Complete provenance from matching names, semantic preservation from parse success, authenticity from a digest, or authority from an opaque locator
- Privacy, absence of membership/timing leakage, successful erasure, provider unlearning, disappearance of disconnected copies, or erasure of prior recipient knowledge
- Physical durability, power-loss recovery, containment, all-child visibility, receiver honesty, instantaneous offline revocation, or rollback of external effects
- Exactly-once external execution on a receiver lacking the required idempotency/atomicity evidence
- Coherent source capture from matching endpoint hashes, hermetic builds, cross-repository atomicity, or portable workspace behavior on unqualified platforms
- Correct real native quota measurement, comparative performance, lower cost, improved recall, task-quality gains, legal clearance or vendor intent
- Independent runtime acceptance: every vector in this report remains UNEXECUTED, and no runtime oracle ran

The competing safe designs remain live where the decisive evidence favors them. Fixed Owner floors are not negotiable experimental variables. A failed vector rejects the candidate implementation or representation; it does not authorize a lower safety/authority/privacy/resource requirement.

## Question and completion coverage

| Brief obligation | Answer location and decisive material |
|---|---|
| Q1 independent identities | Identity field map; issuer/object relations and generic-epoch disposition |
| Q2 collapse refusals | Identity collapse-vector table, including PID reuse, stale work under fresh process/config/release and route-descriptor independence |
| Q3 evidence positions | Evidence cuts and causal-join table, event versus UTF-8-byte cursor and unknown ordering |
| Q4 canonical key | Current L/V correction and canonical-key proposal; immutable actor/auth binding |
| Q5 five key vectors | Same bytes, changed presenter versus changed embedded actor, changed payload, colliding client IDs with/without mapping, expired history |
| Q6 command effect attempt | Retry ownership across crash/reconnect/session/node change; historical receipt after revocation |
| Q7 ArtifactRef | Four exact fields, scoped outward locator, authority classification and extension owners |
| Q8 ContentEnvelope | Eighteen exact fields; C2-A/B/C/D missing-scope/substitution/unknown-mandatory vectors |
| Q9 one loss truth | Single record with typed facets; exact fourteen loss dimensions; C3-L contradictions and semantic non-proof |
| Q10 receipt stages | Eight vocabulary stages with subjects/observers/non-proofs; exact source mappings and partial-transfer fields |
| Q11 publication ordering | P0–P7 single order shared by all transferring lanes, with both current checks |
| Q12 publication failures | P-C0–P-C7 before/after every step; P-X/P-R1/P-R2/P-A/P-D/P-S races and unchanged CopyRecord statuses |
| Q13 conserving algebra | Gross-cap choice, equivalent net view, disjoint settled/outstanding/withheld and atomic settlement |
| Q14 accounting vectors | Finite bound, uncertainty/reserve double count, parent-inclusive meter, invalid crash zero and duplicate settlement |
| Q15 semantic epoch map | Versioned additive mapping, domain/issuer/relation/version and frozen compatibility |
| Q16 retention and replay | Historical disclosure, repeated delivery journal occurrences and unique replay inputs; expired history hold |
| Q17 digest domain | Containing-schema interpretation and conflicting duplicate refusal |
| Q18 route freeze | Exact admission freeze set and route-assignment/descriptor distinction |
| Q19 capture and apply | Three conceptual classes/four exact Y spellings, ABA, aliases, missing external objects, platform profile and protected apply |
| Q20 receiver barrier | Installed receiver floor and pre-install exposure classification; conflicting replacement hold |
| Q21 independent evidence | Exact candidate/profile/corpus/oracle requirements, positive controls, mutations and remaining unknowns |

| Completion gate | Research deliverable disposition | Product acceptance disposition |
|---|---|---|
| G1 all identity domains and collapse vectors | Covered by the per-field maps and independently specified negative/positive outcomes | UNEXECUTED |
| G2 canonical key and five command cases | One candidate, exact content/auth/client-mapping distinctions, history cannot redispatch | Unratified; UNEXECUTED |
| G3 exact content base loss and stages | Four plus eighteen fields, one loss record, exact alias rules and stage-specific non-proofs | Static declarations only |
| G4 one publication order and crash cuts | Pre-release registration, two checks, verify/register, publish/reconcile and every before/after cut | Runtime atomicity/durability unknown |
| G5 resource algebra and six adverse cases | Gross representation, equivalent net interpretation, exactly-once counting and explicit unknowns | Meter/conservation implementation unverified |
| G6 open joins | Seven dispositions above plus Q21 independent-evidence obligation | Adoption and qualification pending |
| G7 field map conflicts and non-proofs | Exact source names, single proposed design owners, consumers/bindings and competing options with falsifiers | No technology selected; no route qualified |
| G8 protected paths privacy and secret scan | Read-only source export; only report and its own QA artifacts written; bounded final-artifact checks recorded below | Bounded scan is not universal secret-absence proof |

## Document coverage appendix

All source links below are pinned to the same fresh merged commit. Reading a source’s historical public-evidence notes does not revalidate those external products; this report’s conclusions use the repository’s current shared-contract declarations and accepted decisions. The attached brief is identical to the pinned repository packet. Supplementary sources are used only to resolve exact names or accepted profile constraints, without opening a new research lane.

| Pinned input | Coverage and use |
|---|---|
| [CONTROL_PLANE.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/CONTROL_PLANE.md#L1-L74) | Operative authority, independent acceptance and protected paths |
| [ANCHOR.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/ANCHOR.md#L1-L57) | Recursion scope and success criteria |
| [AGENTS.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/AGENTS.md#L1-L46) | Bounded task and non-normative specification rules |
| [docs/v3/START-HERE.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/START-HERE.md#L1-L121) | Current versus retired work and frozen contract orientation |
| [state/DECISIONS.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/state/DECISIONS.md#L1-L355) | D-018 through D-033, including fixed native platform floors |
| [docs/v3/prompts/dot-reconciliation-20261002c/R-SC-shared-contract-reconciliation.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/prompts/dot-reconciliation-20261002c/R-SC-shared-contract-reconciliation.md#L1-L375) | All 21 questions and 8 completion gates |
| [docs/v3/prompts/dot-reconciliation-20261002c/README.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/prompts/dot-reconciliation-20261002c/README.md#L1-L70) | Packet invocation and structural gate scope |
| [docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L1-L170) | Current owners, historical corrections and seven joins |
| [docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L1-L207) | Typed state, control/receiver boundaries, resource algebra |
| [docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L1-L191) | Independent oracle requirements and designed crash/mutation cases |
| [docs/v3/research-lane/overnight-20261002/synthesis/field-compatibility.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/field-compatibility.json#L1-L217) | Historical static comparison claims, exact source pin context |
| [docs/v3/research-lane/overnight-20261002/rl/report.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L1-L379) | Command ingress, receipt facts and client semantics |
| [docs/v3/research-lane/overnight-20261002/rl/proposed-contracts.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/proposed-contracts.json#L1-L313) | Command ingress, receipt facts and client semantics |
| [docs/v3/research-lane/overnight-20261002/rq/report.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/report.md#L1-L350) | Content base, lineage, copy inventory, memory and deletion |
| [docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L1-L357) | Content base, lineage, copy inventory, memory and deletion |
| [docs/v3/research-lane/overnight-20261002/rp/report.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rp/report.md#L1-L389) | Untrusted input, provenance, exact effect/disclosure boundary |
| [docs/v3/research-lane/overnight-20261002/rp/proposed-contracts.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rp/proposed-contracts.json#L1-L68) | Untrusted input, provenance, exact effect/disclosure boundary |
| [docs/v3/research-lane/overnight-20261002/rt/report.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/report.md#L1-L357) | Media extension, fourteen loss facets, partial receipts and revision-2 mapping |
| [docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L1-L472) | Media extension, fourteen loss facets, partial receipts and revision-2 mapping |
| [docs/v3/research-lane/overnight-20261002/rt/field-map.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/field-map.json#L1-L2181) | Media extension, fourteen loss facets, partial receipts and revision-2 mapping |
| [docs/v3/research-lane/overnight-20261002/rv/report.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L1-L341) | Identity/cuts, receipt replay, accounting knowledge and independent evidence |
| [docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L1-L352) | Identity/cuts, receipt replay, accounting knowledge and independent evidence |
| [docs/v3/research-lane/overnight-20261002/rx/report.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L1-L462) | ExposureIntent, corrected TransferBinding, receiver fence and recovery |
| [docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L1-L535) | ExposureIntent, corrected TransferBinding, receiver fence and recovery |
| [docs/v3/research-lane/overnight-20261002/ry/report.md](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/report.md#L1-L698) | Workspace identities, coherent capture and protected application |
| [docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L1-L453) | Workspace identities, coherent capture and protected application |

The supplementary identity/route/capture references cited in the relevant sections retain their exact line anchors and the same commit. No historical test receipt was promoted to fresh execution evidence.

### Final artifact verification boundary

The report’s bounded document checks verify the eighteen exact Q-base field rows, one top-level title, consistent Markdown table delimiters, resolved reference labels and pinned source paths/line ranges. All 1,379 exported source blobs were rehashed against the fetched Git object manifest after authoring, with no mismatch; protected paths and all other source bytes are unchanged. A finite scan of the final text found no private-key blocks, common API/access-token patterns or private execution-workspace paths. This is a clean result for those searched patterns, not proof that arbitrary secrets are absent.

These checks read source data and inspect this authored deliverable only. They do not execute repository code, the supplied structural checker, target tests, runtime vectors, models or providers. Independent document review assesses whether the report covers its questions and source claims; it is not independent runtime acceptance or Owner ratification.


## Pinned citation register

All links below use the fresh inspected repository pin. Short identifiers are citation labels, not alternative contract field names.

- **O1** — [synthesis/OWNERSHIP-AND-FIELD-MAP.md, lines 5–34](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L5-L34): design vs runtime owners
- **O2** — [synthesis/OWNERSHIP-AND-FIELD-MAP.md, lines 127–143](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L127-L143): resource algebra and shared invariants
- **O3** — [synthesis/OWNERSHIP-AND-FIELD-MAP.md, lines 60–90](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L60-L90): base and digest/loss alias rules
- **O4** — [synthesis/OWNERSHIP-AND-FIELD-MAP.md, lines 38–58](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L38-L58): distinct identity domains
- **O5** — [synthesis/OWNERSHIP-AND-FIELD-MAP.md, lines 157–168](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L157-L168): static compatibility and open joins
- **M1** — [synthesis/MODEL-ARCHITECTURE.md, lines 143–153](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L143-L153): gross/net, instantaneous capacity, allocation continuity, Stop facts
- **M2** — [synthesis/MODEL-ARCHITECTURE.md, lines 75–89](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L75-L89): route, role, child, retry closure
- **M3** — [synthesis/MODEL-ARCHITECTURE.md, lines 93–125](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L93-L125): C/T, authority, context, compaction, capture and forks
- **V1** — [rv/candidate-contracts.json, lines 77–92](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L77-L92): exact ResourceReservationAccounting
- **V2** — [rv/candidate-contracts.json, lines 270–290](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L270-L290): exact MeterObservation
- **V3** — [rv/candidate-contracts.json, lines 11–24](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L11-L24): KnowledgeValue and invalid raw zero
- **V4** — [rv/report.md, lines 155–184](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L155-L184): interpretation, migration and state digest domains
- **T1** — [rt/artifact-contract.json, lines 315–345](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L315-L345): Counter
- **T2** — [rt/report.md, lines 213–231](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/report.md#L213-L231): finite strict bounds, context and accounting
- **T3** — [rt/artifact-contract.json, lines 53–94](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L53-L94) and [lines 436–470](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L436-L470): byte identity and checked aliases
- **T4** — [rt/artifact-contract.json, lines 212–280](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L212-L280): exact RouteMediaFacet
- **T5** — [rt/artifact-contract.json, lines 282–313](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L282-L313) and [rt/report.md, lines 182–184](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/report.md#L182-L184): exact payload and release check
- **P1** — [rp/proposed-contracts.json, lines 5–44](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rp/proposed-contracts.json#L5-L44): original digest names and non-authority invariants
- **P2** — [rp/report.md, lines 314–327](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rp/report.md#L314-L327): exact C/T seam
- **Q1** — [rq/candidate-contracts.json, lines 311–318](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L311-L318): fork and accounting invariants
- **Q2** — [rq/candidate-contracts.json, lines 11–44](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L11-L44): four-field ArtifactRef and eighteen-field envelope
- **X1** — [rx/report.md, lines 220–250](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L220-L250): recovery, liabilities and idempotent settlement
- **X2** — [rx/report.md, lines 147–164](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L147-L164): replacement barrier and revocation/install race
- **X3** — [rx/candidate-contracts.json, lines 231–257](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L231-L257): exact ReceiverFence
- **X4** — [rx/report.md, lines 169–180](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L169-L180): receipt boundaries and unknown liability
- **Y1** — [ry/candidate-contracts.json, lines 152–224](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L152-L224): snapshot/member/materialization exact fields and enums
- **Y2** — [ry/report.md, lines 195–241](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/report.md#L195-L241): capture, ABA, preservation, races and profiles
- **Y3** — [ry/candidate-contracts.json, lines 104–150](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L104-L150): WorkspaceBinding
- **Y4** — [ry/candidate-contracts.json, lines 347–390](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L347-L390): ApplicationIntent
- **Y5** — [ry/report.md, lines 336–342](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/report.md#L336-L342): conforming apply alternatives and uncertainty
- **L1** — [rl/report.md, lines 272–288](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L272-L288): control reserve and Stop facts
- **L2** — [rl/report.md, lines 338–358](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L338-L358): independent oracle and positive cases
- **D28** — [state/DECISIONS.md, lines 240–266](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/state/DECISIONS.md#L240-L266): accepted platform and reset floors, still unqualified
- **I1** — [synthesis/INTEGRATION-TEST-HANDOFF.md, lines 162–170](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L162-L170): accounting oracle
- **I2** — [synthesis/INTEGRATION-TEST-HANDOFF.md, lines 70–90](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L70-L90): C/T and role closure oracles
- **I3** — [synthesis/INTEGRATION-TEST-HANDOFF.md, lines 112–120](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L112-L120): capture/apply oracle
- **I4** — [synthesis/INTEGRATION-TEST-HANDOFF.md, lines 3–3](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L3), [lines 28–30](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L28-L30), and [lines 187–191](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L187-L191): unexecuted scope and independent acceptance
- **I5** — [synthesis/INTEGRATION-TEST-HANDOFF.md, lines 44–68](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L44-L68) and [lines 144–150](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L144-L150): fence/content and sensitivity oracles
- **I6** — [synthesis/INTEGRATION-TEST-HANDOFF.md, lines 172–191](https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L172-L191): later useful-work evidence and historical limits


[S01]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L49-L65
[S02]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/proposed-contracts.json#L39-L76
[S03]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L94-L110
[S04]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L36-L58
[S05]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L27-L45
[S06]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L58-L224
[S07]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L347-L380
[S08]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L83-L87
[S09]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L162-L168
[S10]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L5-L34
[S11]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L97-L114
[S12]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L105-L164
[S13]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L27-L59
[S14]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L231-L292
[S15]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L98-L105
[S16]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L212-L298
[S17]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rj/report.md#L152-L184
[S18]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rk/report.md#L42-L56
[S19]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L114-L126
[S20]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L75-L89
[S21]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L89-L96
[S22]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L129-L139
[S23]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L198-L205
[S24]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L127-L129
[S25]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L143-L180
[S26]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L117-L123
[S27]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/report.md#L40-L54
[S28]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/report.md#L56-L81
[S29]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ru/candidate-contracts.json#L25-L69
[S30]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L44-L54
[S31]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L155-L169
[S32]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L390-L401
[S33]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rk/report.md#L54-L64
[S34]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L173-L194
[S35]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L46-L110
[S36]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L125-L132
[S37]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L152-L159
[S39]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L92-L111
[S38]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L170-L186


[O1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L5-L34
[O2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L127-L143
[O3]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L60-L90
[O4]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L38-L58
[O5]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/OWNERSHIP-AND-FIELD-MAP.md#L157-L168
[M1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L143-L153
[M2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L75-L89
[M3]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/MODEL-ARCHITECTURE.md#L93-L125
[V1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L77-L92
[V2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L270-L290
[V3]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/candidate-contracts.json#L11-L24
[V4]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rv/report.md#L155-L184
[T1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L315-L345
[T2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/report.md#L213-L231
[T3]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L53-L94
[T4]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L212-L280
[T5]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rt/artifact-contract.json#L282-L313
[P1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rp/proposed-contracts.json#L5-L44
[P2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rp/report.md#L314-L327
[Q1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L311-L318
[Q2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rq/candidate-contracts.json#L11-L44
[X1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L220-L250
[X2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L147-L164
[X3]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/candidate-contracts.json#L231-L257
[X4]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rx/report.md#L169-L180
[Y1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L152-L224
[Y2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/report.md#L195-L241
[Y3]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L104-L150
[Y4]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/candidate-contracts.json#L347-L390
[Y5]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/ry/report.md#L336-L342
[L1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L272-L288
[L2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/rl/report.md#L338-L358
[D28]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/state/DECISIONS.md#L240-L266
[I1]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L162-L170
[I2]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L70-L90
[I3]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L112-L120
[I4]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L3
[I5]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L44-L68
[I6]: https://github.com/NotSkittlz/recursion/blob/5b55e55a103fad2d82d625983080b39f2db21c0e/docs/v3/research-lane/overnight-20261002/synthesis/INTEGRATION-TEST-HANDOFF.md#L172-L191