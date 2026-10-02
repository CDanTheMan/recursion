# R-X — Node fabric and remote execution protocol

Research design candidate · 2 October 2026 UTC  
Repository basis: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
All runtime, network, OS, failover and recovery fixtures: **UNEXECUTED**

## Decision summary

Remote execution moves a bounded WorkPacket and its authorized evidence to an execution host. Writer availability moves the right to append canonical state. They are different protocols with different fences. A worker must never become a second canonical writer, admission authority or portfolio executive merely because it is enrolled, reachable, authenticated or holding work.

D020 is fixed: automatic writer takeover is required, user-toggleable and supplied by the first-party availability plugin in remote/full. The shipping core is single-node, owns the monotonic writer fence and store/availability seam, and compiles in no consensus. The requirement does not establish unconditional zero downtime or availability through every partition. D019 still requires comprehensive capabilities built and shipped opt-in; this report does not propose a smaller release.

The candidate's critical safety distinction is **one currently admitted executor versus one physically running process**. A disconnected or malicious old host can continue consuming CPU. A lease timeout cannot prove it stopped. The protocol admits only one current executor per task/step and fences every protected mutation. Where the task requires physical non-overlap, or a sink cannot enforce fencing/idempotency, recovery must wait for independent quiescence or authoritative reconciliation. That restriction is explicit, not disguised as exactly-once execution.

The deliverable provides 22 question answers, 11 exact completion mappings, a transport-neutral protocol candidate, three conforming topology alternatives, identity/fencing/transfer/recovery contracts and 24 provider-free local handoffs. It selects no language, store, consensus framework, runtime, transport, encoding, certificate authority, message bus, orchestrator or vendor. No route is qualified.

## Evidence, authority and current observations

**SD** means retrieved primary-source documentation or a supplied accepted requirement. **LO** means static inspection of supplied source/receipt bytes or checks of these authored artifacts. **IN** means a proposed design or derived consequence. **U** means unknown/unmeasured. All Recursion mechanisms, transition rules and test predicates below are IN; all runtime fit, security, availability, latency, cost and productivity results are U. A citation to another system is not a Recursion result.

Current governance, D017–D033, the active goal, PRODUCT, INTERFACE-STRATEGY, PLUGINS-AND-EDITIONS, research coverage/index/gaps/synthesis, DS20/23/25 and the R-X brief were consumed at the pinned snapshot. Older DS20 questions about whether takeover is required are superseded by D020. G06/G07/G11 Owner decisions are closed; implementation qualification remains open. The final P–Y mapping in ARCHITECTURE-COVERAGE is stale; actual R-Q is memory, R-R autonomy, R-T media, R-U isolation and R-X fabric. TUI-first/later-GUI construction shares one backend; the timing tension with D019's built-opt-in GUI remains an Owner interpretation, never an excuse to remove accepted scope.

LO: `RIntegrated.tla` has separate goal, plan, lease, pause and writer fields, an effect/outbox model and a no-blind-replay guard. Its actual constants are four command IDs and six events; the older header comment differs. Its writer variable remains unchanged in the shown transition relation, and it explicitly lacks principals, authority dimensions, replay/projection monitors and packet derivation. This is useful specification lineage, not evidence of writer takeover or receiver installation. FU03's stored receipts are historical reduced-bound observations. FU04's manifest pins the native floors and explicitly leaves profiles unqualified. Its platform observations cannot establish fabric behavior. The [gap audit](../gaps/report.md) retains the bounded historical evidence and its limitations. No target script was imported or executed here, and no fabric entrypoint was verified.

Draft cross-lane contracts are consumed as proposals: [R-E](../re/report.md) owns trusted launch and credential-flow assurance; [R-Q](../rq/report.md) owns derived memory and current rights checks; [R-R](../rr/report.md) owns bounded wake/retry/cumulative-budget semantics; [R-T](../rt/report.md) owns media representations and exact recipient payloads. R-U owns host isolation qualification. R-X transports their references and evidence without creating another canonical object owner. R-O supplies complete resource-vector measurement, not a demonstrated coordinator capacity.

## Primary evidence capsules

These are the lane's substantive public-source summaries. Later sections are original candidate reasoning. Registers record URLs, versions, retrieval date and hash limitations. Public page bodies are not bundled. No direct quotations are used.

<a id="rx-s01-facts"></a>
- **RX-S01 — TLS 1.3.** The standard separates authenticated handshake and protected records. Client authentication is optional; early data lacks forward secrecy and cross-connection replay guarantees. A secure channel does not decide application authorization. [RFC 8446](https://www.rfc-editor.org/rfc/rfc8446.html), §§1, 2.3, 4, 8, E
<a id="rx-s02-facts"></a>
- **RX-S02 — Certificate validity and revocation.** Certificate validation and timely revocation information are separate concerns; periodic revocation publication creates freshness limits. [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280.html), §§3.3, 6
<a id="rx-s03-facts"></a>
- **RX-S03 — Enrollment.** EST distinguishes authenticated enrollment, client authorization and proof of possession. Its historical protocol details are not a selected modern cryptographic profile. [RFC 7030](https://www.rfc-editor.org/rfc/rfc7030.html), §§3.3–3.7
<a id="rx-s04-facts"></a>
- **RX-S04 — Workload identity.** SPIFFE distinguishes workload identifiers, verifiable identity documents and trust domains; its isolation assumptions do not themselves implement host isolation. [SPIFFE concepts](https://spiffe.io/docs/latest/spiffe-about/spiffe-concepts/)
<a id="rx-s05-facts"></a>
- **RX-S05 — Attestation.** SPIRE distinguishes node and workload attestation and ties issuance to registered selectors and trusted evidence. Its documentation includes single-use join tokens as one bootstrap option. [SPIRE concepts](https://spiffe.io/docs/latest/spire-about/spire-concepts/)
<a id="rx-s06-facts"></a>
- **RX-S06 — Receiver fencing.** Chubby describes sequencers carrying lock-generation information, checked by recipient services to reject stale requests. A lock's existence is insufficient without that receiving-side behavior. [Burrows, OSDI 2006, §2.4](https://storage.googleapis.com/gweb-research2023-media/pubtools/4444.pdf)
<a id="rx-s07-facts"></a>
- **RX-S07 — Replicated log limits.** Raft's paper assumes non-Byzantine server failures and majority communication for availability; terms, log commitment and membership transitions are distinct. Its model does not supply external-effect semantics. [Ongaro and Ousterhout, extended paper](https://raft.github.io/raft.pdf), §§2, 5–6, 8
<a id="rx-s08-facts"></a>
- **RX-S08 — Safety versus progress.** Paxos Made Simple treats safety separately from progress; competing proposers can repeatedly preempt each other. Stable information is necessary across restart in its failure model. [Lamport, 2001](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), §§2.1, 2.4
<a id="rx-s09-facts"></a>
- **RX-S09 — Partition limit.** Gilbert and Lynch prove an impossibility for always-available atomic read/write objects under their asynchronous message-loss model. This is not a blanket statement that every operation must stop. [Original paper, 2002, §3](https://www.cs.princeton.edu/courses/archive/spr22/cos418/papers/cap.pdf)
<a id="rx-s10-facts"></a>
- **RX-S10 — RPC uncertainty.** RFC 5531 explains that a missing reply after retransmission cannot establish how many times a remote procedure executed. [RFC 5531](https://www.rfc-editor.org/rfc/rfc5531.html), §5
<a id="rx-s11-facts"></a>
- **RX-S11 — Convergence is scoped.** The original CRDT report gives sufficient convergence conditions for state- and operation-based replication. Convergence depends on update/merge and delivery assumptions. [Shapiro et al., RR-7506 v1, 2011, §2](https://dsf.berkeley.edu/cs286/papers/crdt-tr2011.pdf)
<a id="rx-s12-facts"></a>
- **RX-S12 — Windows names.** Use [R-Y’s canonical naming note](../ry/report.md#ry-source-y-s19). **IN:** a path spelling cannot serve as the portable object identity.
<a id="rx-s13-facts"></a>
- **RX-S13 — Linux resolution.** Linux path resolution depends on root, current directory, mounts, permissions and symlink traversal. [Linux path_resolution(7)](https://man7.org/linux/man-pages/man7/path_resolution.7.html)
<a id="rx-s14-facts"></a>
- **RX-S14 — Linux durability.** File synchronization alone need not make its directory entry durable. [Linux fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html)
<a id="rx-s15-facts"></a>
- **RX-S15 — Windows durability.** FlushFileBuffers flushes buffered information for the specified file; actual profile recovery still needs fault evidence. [Microsoft FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)
<a id="rx-s16-facts"></a>
- **RX-S16 — Local locking.** Linux flock is advisory and associated with open-file descriptions, including inherited duplicates. [Linux flock(2)](https://man7.org/linux/man-pages/man2/flock.2.html)

Process/isolation facts are centralized in [R-E Q04–Q05](../re/report.md) rather than summarized again. This lane re-inspected the [Windows Job Objects page](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) and [Linux 6.12](https://docs.kernel.org/6.12/admin-guide/cgroup-v2.html)/[6.6](https://docs.kernel.org/6.6/admin-guide/cgroup-v2.html) documentation; they are evidence inputs, not chosen sandbox products.

Upstream comparison facts remain at [Codex App Server](../rf/report.md#codex-app-server-facts) and [OpenCode server](../rf/report.md#opencode-server-facts). Their official pages were re-retrieved; the Codex URL now redirects to [ChatGPT Learn](https://learn.chatgpt.com/docs/app-server). No extra route factual summary or qualification is inferred. MCP edge semantics remain in the [protocol supplement](../protocol-edges/report.md).

<a id="q01"></a>
## Q01 Authorized enrollment and revocable membership

**IN, RX-R01/R02.** Enrollment is an Owner-authorized membership change in the existing canonical domain, not a task grant. Proposed states are `proposed → bootstrap_pending → identity_verified → enrolled_inactive → eligible`, with `quarantined`, `revoked` and `retired` terminal/restricted branches. An authenticated but inactive node receives no WorkPacket or private descriptor inventory.

The enrollment request binds the exact domain, node public identity, bootstrap challenge, intended operator, allowed enrollment role, permitted profile and expiry. The Owner or already-authorized operator approves that binding through the existing command/receipt path. The candidate proves possession of its own locally provisioned private identity material and authenticates the intended domain. Approval of a hostname, certificate chain or discovered address alone is insufficient. The join proof is single-use, expires, and is consumed atomically with canonical membership creation. Replayed enrollment is idempotent only for the same exact request; a changed key/role is a conflict.

Operator provisioning keeps identity private keys outside untrusted task processes. Provider credentials are separately provisioned at the destination under R-E, never supplied by enrollment. Enrollment issues no shell access, writer capability, artifact read grant, portfolio role, subscription entitlement or permission to enroll descendants. A node descriptor is admitted evidence with declared issuer and freshness, not self-authorizing truth.

Revocation commits a membership-generation change and closes new admission, renewal, artifact reads and control-session eligibility. Existing sessions are invalidated; affected receivers must install current revocation/work fences and return separate installation receipts. Certificate revocation/expiry is defense in depth and has its own freshness policy. An unreachable node remains `revocation_pending_remote` with retained copy/effect obligations. Re-enrollment after compromise creates a new incarnation and new approved binding, rather than resetting a revoked generation. Retirement records inventory and residual responsibilities; it does not delete historical receipts or assert physical erasure.

Compare operator-approved key pinning with an operator-approved attestation-backed issuer; both require canonical membership and task grants. RX-F01/F03/F07 are decisive. Neither establishes freedom from stolen keys or malicious administrators.

<a id="q02"></a>
## Q02 Authenticated encrypted transport requirements

**IN, RX-R03.** A transport adapter must demonstrate: bidirectional peer authentication; confidentiality and integrity; an approved forward-secret exchange; fresh session binding; replay-resistant control; explicit protocol/security floors; authenticated version negotiation; endpoint identity binding; and fail-closed certificate/trust/revocation validation. These are requirements, not selection of TLS, a library or transport. RX-S01–S05 supply standards precedent.

The application handshake binds both node/domain identities, their incarnations, trust-bundle and revocation revisions, challenge values, protocol family, supported versions, required capability set, selected version and security-profile digest to the authenticated channel transcript. A peer cannot erase a required fence/Stop capability and still accept the job. A no-overlap version set returns a bounded refusal before content release or execution. Compatibility is explicit; there is no automatic fallback to anonymous, cleartext, older-epoch or weaker-profile control. Security version, fabric schema version, broker version and release identity are separate.

Application operation IDs and durable deduplication survive connection replacement; a secure transport's own sequence protection is insufficient. No mutating command, enrollment, lease, grant, approval, artifact disclosure or renewal is allowed in replayable early-data mode. Message integrity also covers audience, task, recipient and body digest; an authentic message forwarded to another node is not valid for that node. End-to-end node identity may not silently terminate at an inspecting proxy. A deliberately authorized relay is named as a recipient/trust boundary, with its exposure in placement policy.

Validation is two-stage: RX-F02 models handshake decisions and malformed transcripts without contacting a network; a later separately authorized native conformance campaign exercises the selected implementation with synthetic keys on exact D028 floors, endpoint mismatch, expired/revoked chains, stripping, replay, proxy termination, restart and clock uncertainty. Until the latter exists, crypto implementation correctness, forward secrecy and native compatibility are U. Mock certificates cannot prove cryptography.

<a id="q03"></a>
## Q03 Identity and separate epoch domains

**IN, RX-R02/R04.** A stable logical node ID identifies enrollment; a canonical enrollment generation distinguishes revocation/replacement; a key ID identifies its public authenticator; a canonical node-incarnation ID distinguishes boot/restore; a process-incarnation ID identifies an actual executor; and a session ID identifies one authenticated transport. None is a task, grant or writer identity. A node cannot simply announce a larger integer and acquire a fresh incarnation.

The kernel issues/validates separately typed current references:

| Identity or fence | Meaning and authority |
|---|---|
| writer fence | Monotonic canonical-write ownership; issued through kernel/store/availability seam |
| work epoch and lease ID | Exclusive admitted executor for a goal/task/step; independent of writer changes |
| pause/Stop epoch | Selected scope and D022 boundary; not reset by reconnection |
| process incarnation | OS-observed process/containment instance; never PID alone |
| configuration revision | Effective policy/settings identity; accepted and applied differ |
| release identity/epoch | Verified code and compatibility identity; not an authority grant |
| goal/plan revision | Exact accepted task intent and decomposition |
| route assignment epoch | Harness/interface/model/pool/host binding; not a new goal |
| enrollment/revocation generation | Membership eligibility, distinct from every work fence |
| stream incarnation + cursor | Evidence/projection sequencing; never writer authority |

Only values in the same declared domain are ordered. A lexicographic generic epoch that lets a new process compensate for an old work fence is invalid. A proposed envelope carries a typed reference vector, not one magic generation. New writer ownership does not renew old leases or approvals. Unknown current reference means refusal of new effects.

Clone falsifiers: copy a disk image and present the old identity; restart with an old counter; replay another node's session; concurrently present the same key from two hosts. The minimum design detects conflicting live incarnations where observable and quarantines affected admission, but **copied software-held keys can be cryptographically indistinguishable**. A stronger profile can require operator-bound non-exportable key/attestation evidence; the competing software-key profile is admissible only where policy accepts its stated clone risk. Neither can exclude a compromised trust root or host administrator. Never claim a nonce proves unique physical hardware. RX-F03 tests refusal and honest unknowns, not hardware attestation security.

<a id="q04"></a>
## Q04 Control-first delivery and scoped hydration

**IN, RX-R05.** After recipient authorization and durable exposure-intent registration, first send a bounded, recipient-scoped transfer manifest and minimum control capsule. It includes exact accepted GoalSpec/plan/gate references, canonical input cursor and checkpoint identity, current authority/Stop/work/configuration references, pending interactions, unresolved effects/reservations, provenance and rights-policy references, loss/unknown markers and authorized rehydration locators. References must resolve against current canonical state; a signature or digest does not make stale instructions current. No hidden reasoning, provider credential, node private key, bearer grant, live permit or copied spend reservation is recovery content. Non-authorizing references to authority/reservations can travel; new execution rights are separately admitted.

Manifest processing itself is a disclosure: exclude disallowed filenames, digests, stable equality handles, sizes, source titles and participant identities before transmission. Public/cross-scope handles are opaque, audience-specific and non-authorizing. A rehydration locator is a typed logical artifact reference and allowed resolver, not an arbitrary filesystem path, URL fetch or credential-bearing capability.

Hydration/publication sequence: authenticate and authorize metadata, exact recipient and purpose → resolve current control/source/rights scope → durably register a separate exposure intent referring to the expected CopyRecord identity, lineage and existing reservation → deliver the control manifest first, then transfer approved chunks into quarantine → verify declared lengths, chunk/full-object digests, representation lineage and materialization → freshly check current rights, deletion-inventory cut and applicable work/Stop/grant fences at the protected gate → publish only with a durable registered intent → independently observe publication/copies and settle evidence/accounting. Registration uses the existing canonical owner; it is not a second authority or budget ledger. Remote quarantine is already a disclosure to that node: precommit the exposure intent, potential-copy inventory obligation, lineage and reservation before any relevant private manifest metadata or chunk leaves the sender. Separately gate verified task publication after receipt. Authorized local private staging may precede registration because it has not yet crossed the recipient disclosure boundary. The intent claims neither present nor delivered. The intent does not assert that a copy is present and adds no planned/staged status to Q CopyRecord. Copy observation remains UNKNOWN until evidenced. Validation occurs before use; hashes cannot be verified before receiving bytes. An untrusted peer's supplied digest is not an independent reference. Interrupted chunks remain unavailable to execution with bounded storage/retention and attributable transfer evidence.

Crashes before or after publication preserve the same operation/transfer identity, registered intent and reservation. `publication_unknown` is reconciled; it is never guessed absent or blindly retried with a fresh identity. A restart must recover the durable intent before permitting publication. Deletion-inventory cuts include unresolved registered intents and their possible copies, without marking them present. An intent racing a cut, revocation or tombstone must revalidate at the protected publication gate: stale rights/cut provenance refuses or holds for reconciliation. Evidence must distinguish registration, attempted disclosure, verified staging, publication observation and settlement.

Each resume/range request binds transfer ID, artifact revision, exact receiver incarnation, representation/range, policy version and byte ceiling. It is reauthorized, even if content is cached. No widening to a larger source, embedded file, derived representation, redirect destination or another node. Current revocation can stop remaining chunks but cannot retract bytes already disclosed. R-Q/R-T copy and derivation records survive transport; untrusted content remains non-authority. RX-F04/F05/F19 cover tamper, metadata disclosure, authorization races, resumable transfer and credential exclusion.

**Workspace integration (proposed, unratified).** Carry R-Y’s exact `WorkspaceBinding` reference: manifest revision, per-repository `source_snapshot_ref`, optional candidate/change-set references, `materialization_ref`, profile/configuration/rights references and source-observation cut. A successor host needs a fresh or explicitly revalidated materialization with its own host incarnation, root locator, capture class, mutation generation and verification references. Binding history and a copy/materialization receipt grant no current permission, writer identity or budget/effect settlement. Current refs re-resolve before use. R-Y’s `configuration_epoch` and `effective_config_ref` retain their distinct meanings; they are not silently renamed into the fabric’s current configuration reference. Equal before/after hashes can miss an ABA mutation: coherent capture requires an immutable/qualified snapshot or enforced all-writer quiescence. Otherwise record weaker observed capture and refuse a task requiring coherent fork. Q’s `ContentEnvelope.project_and_audience` and `privacy_domain_id` are preserved exactly and match T’s corrected field map; workspace/media facets are extensions. [Shared candidate fields](candidate-contracts.json) include the P→Q→T→X/Y alias map; no `project_id` base-envelope alias is adopted.

<a id="q05"></a>
## Q05 Placement from attributable facts

**IN, RX-R06.** Placement is first a hard eligibility predicate, then an explainable preference comparison. Inputs have issuer, observation time, expiry, evidence class and null reason: exact OS/architecture/filesystem and isolation profile; tool/application/interface/build availability; compatible release/schema; independently observed resource headroom and current admitted load; source/worktree locality and revision; approved data classes/residency/egress/retention; route and credential-boundary availability without credentials; capacity and review reservations; measured latency/bandwidth distribution or unknown; native-unit costs or unknown; task deadline/checkpointability; sink fencing/idempotency; and incident/quarantine status.

A descriptor from a node is an assertion. A self-reported region, tool version or available RAM is not verified residency or headroom. Unknown hard requirements fail eligibility; unknown preferences remain visible and cannot become zero cost or perfect latency. Placement never performs inference merely to choose a host. It evaluates already admitted candidates with deterministic policy.

The `PlacementReceipt` records considered candidates, hard refusals, observed fact versions, preference order, chosen tradeoff, required approvals, residual unknowns and expected capacity reservation. Revalidate at dispatch because capacity, policy and source revision can change. A new recipient, billing class or egress route outside accepted authority blocks rather than silently falling back. An unavailable preferred node can leave the task queued.

Competing conforming designs are a deterministic rule/priority policy and a constrained Pareto frontier with Owner-chosen tie-breaking. The latter must expose dimensions instead of inventing an opaque global score. Compare responsiveness, total transfer/helper/recovery burden and verified outcomes against a locality-first baseline under the same floors. RX-F05/F18 falsify unsafe placement; a passed synthetic filter does not establish scheduling quality or economics.

<a id="q06"></a>
## Q06 Execution leases and the single writer

**IN, RX-R07.** A lease is a revocable bounded permission for one holder incarnation to execute one named step at a current work epoch. The canonical kernel owns its lifecycle: `proposed → granted → receiver_installed → start_permitted → active → closing → settled/expired/revoked/unknown`. The worker may request renewal but cannot renew itself, issue a child lease, release another holder or mint canonical events. Parent/child tasks have separate leases and explicitly partitioned authority/resources.

Grant includes task/step, exact WorkPacket digest, holder and process target, work epoch, grant/Stop/policy/configuration dependencies, maximum duration/operations/resources, allowed effect classes and receivers, renewal conditions and reservation references. The kernel atomically checks that no other current admitted holder exists. A renewal is a durable compare-and-admit against the same lease and current scope, not a heartbeat side effect.

Expiry bounds eligibility, not external truth. A monotonic local clock is suitable for local timeout observation only within a pinned suspend/reboot model; wall time and cross-node clocks cannot establish physical exclusivity. A trusted receiver consults current authorization or its qualified installed fence state before each irreversible boundary. Sleep/wake or loss of validation freshness closes dispatch and requires revalidation. Clock uncertainty cannot prolong a lease.

At most one **current admitted** holder exists. Replacement work that could conflict is gated until all relevant sinks reject the previous work epoch, previous possible effects are reconciled/idempotently protected, and any physical-non-overlap requirement has independent quiescence evidence. Otherwise `replacement_blocked_unknown` is correct. An old CPU may still compute in its isolated staging area; its outputs are evidence candidates, never accepted current mutations. This is the honest boundary of the brief's at-most-one-active-executor requirement. RX-F06/F08/F10 test it; a literal all-processes non-overlap claim for an unreachable hostile machine is not established.

<a id="q07"></a>
## Q07 Receiver fences and the revocation/install race

**IN, RX-R04/R08.** Every mutating request binds operation and attempt IDs, body digest, exact receiver/resource, writer/work/Stop references as applicable, grant/policy version, holder/process incarnation and expiry. The receiving canonical store or effect broker validates the issuer and current scope. A node-supplied higher number is rejected unless accompanied by authorized installation provenance. Fence state is durable and cannot regress on restart, restore or code rollback.

A receiver's irreversible commit gate serializes fence installation and effect acceptance. It cannot check an epoch, release the lock and later perform an unguarded effect. Either the check and mutation are one protected transaction, or a trusted actuator owns the final dispatch gate and records the interval during which an already-dispatched external effect is unresolved. A store transaction cannot atomically cover an unrelated external service unless that service participates in a demonstrated protocol.

**Required negative trace:** holder A owns work epoch 7; receiver R has installed 7. A's request is delayed before R's gate. Canonical authority closes 7, records epoch 8 and orders installation. R durably installs 8, returns an installation receipt, and B becomes eligible for epoch 8. A's delayed epoch-7 request reaches the gate and is refused with `stale_work_fence`; R's independent effect ledger has no new mutation. R restarts and refuses the same request again. A late historical receipt is ingested as evidence, not as a new authorized dispatch.

**The race that must remain visible:** canonical revocation accepted at C is not proof that disconnected R installed it. Before installation, an old already-admitted request can reach R or an external sink. Record `revocation_accepted`, `installation_pending`, receiver high-water, last valid dispatch boundary and unresolved effect separately. Do not announce remote Stop completion. B cannot create a conflicting effect while this is unresolved. Two conforming enforcement options are (a) online serialized admission at a trusted final actuator, failing closed when it cannot verify, and (b) pushed durable receiver fences plus an acknowledged installation barrier and explicit pre-install exposure. Cached time-bounded leases alone are a negative control, not a rival safety design.

RX-F07 enumerates crashes before/after fence persistence and effect commitment, including a stale installation request and a delayed ACK. Monotonic fencing protects accepting sinks; it does not constrain a malicious sink that ignores the protocol, revoke information already read or undo a committed external effect.

<a id="q08"></a>
## Q08 Granted, started, recorded and settled are different facts

**IN, RX-R09.** Ordering is a partial order with named evidence, not a single success flag:

1. Canonical intent, exact admission and reservation commit before a start permit is issued
2. Required receiver fences and control/manifest validation precede eligible start
3. Worker records a local start observation tied to the process incarnation; canonical receipt of it can occur later
4. Before an effect is attempted, the logical effect intent/identity is durable and the final receiver gate rechecks current authority
5. The sink may accept/perform an effect before its reply or canonical result observation arrives
6. Canonical recording of a report is not settlement; settlement needs the declared receiver/postcondition evidence, and independent task verification remains separate

Transport ACK, command accepted, durable admission, local spool persistence, canonical event append, effect dispatch, receiver acceptance, effect completion and verification have different receipts. A network send returning successfully proves none of the later states. There is no claimed total order of physical observations across unsynchronized clocks. Canonical ordinals order accepted records, not retroactive physical history.

Lost acknowledgement yields `unknown_delivery`, `unknown_execution` or `unknown_effect` with the exact last known boundary. Retry owner queries the same operation ID and body digest; it does not invent a new effect ID. Same ID/same bytes returns the prior disposition; same ID/different bytes refuses. Spool ACK permits cleanup only after the required canonical durability/recovery condition and retention policy, not after a socket receipt. Unknown costs remain null and possible liabilities remain attached to existing outstanding reservations. RX-F08 tests every crash cut.

<a id="q09"></a>
## Q09 Core seam, availability plugin and competing topologies

**IN, RX-R10/R11.** The core provides `verify_current_writer`, `append_if_current`, `read_committed`, `consistent_checkpoint` and a typed availability capability seam as abstract obligations, not runnable APIs. Writer-fence advancement and accepted writes must share a linearizable safety boundary. Local single-writer locking plus durable monotonic state can satisfy core-only operation; it cannot be advertised as automatic multi-machine takeover.

The optional first-party availability implementation owns replicated storage/election coordination behind that seam. Its elected process starts non-authoritative until it has the qualified committed prefix, current writer fence, current policy/Stop state and necessary receiver checks. Multiple replicas are physical copies under one logical canonical owner. Consensus protocol terms, membership generations and Recursion writer epochs remain distinct, with an explicit auditable mapping. Membership removal, snapshot install and restoring an old backup may not reset the fencing floor. If the authority needed to prove a new fence is lost, recovery blocks rather than guessing a larger number.

Automatic takeover remains a required, toggleable plugin capability, including after a writer crash when its declared quorum/failure assumptions hold. Disabling the plugin removes the availability promise without changing safety. Neither two isolated writers nor default consensus is admissible. A partition may preserve local evidence capture/read-only status while denying current canonical writes on one side. RX-S07–S09 explain why zero-downtime wording needs a conditional, measured meaning.

| Candidate execution topology | Conforming authority boundary | Real competing option | Decisive falsifier | Passing does not prove |
|---|---|---|---|---|
| Central dispatch, control and artifact relay | One canonical writer; remote worker only proposes observations | Direct task-scoped data plane below the same central authority | Relay causes adopted control/transfer ceilings to fail while direct plane passes equally safe fixtures, or relay can self-admit | Universal capacity or availability |
| Direct peer data/record transfer | Canonically minted receiver-specific transfer/step authorization; no peer admission/election | Central mediated relay | Peer bypasses current rights/fences, becomes a writer, or peer churn defeats required reconciliation/resource bounds | Trust in every peer or privacy against its administrator |
| Delegated upstream execution on an enrolled host | Local trusted boundary wraps a pinned upstream route; Recursion owns goal/admission/evidence, upstream owns its loop | Native remote executor under the same contracts | Exact route cannot provide scoped dispatch, interruption, correlation or ambiguity evidence required by task; hidden helper inference appears | Route qualification, entitlement, subscription portability or native-loop equivalence |

All three preserve the availability seam and single canonical owner. No topology is selected. Codex is first qualification priority, not a qualified remote transport. An upstream server's control capability does not substitute for Recursion enrollment, artifact egress policy or receiver fencing. Existing R-F route facts are the evidence base.

Core-leak falsifier RX-F17: the absent/disabled core build's dependency/import closure, startup trace or idle observation requires consensus code, election traffic, remote runtime activation or a provider. A metadata descriptor has a separately accounted bounded footprint; “disabled” does not imply literally no installed bytes. The lean profile has no active fabric runtime. An opted-in idle execution node holds no work lease and performs no inference; health checks are bounded. Dedicated availability replicas may incur explicit coordination overhead while that plugin is active and must not be mislabeled as idle execution workers.

<a id="q10"></a>
## Q10 Connectivity and lifecycle distinctions

**IN, RX-R12.** Connectivity is observation, not authority. `connected/disconnected/suspected_partition` is independent of `enrolled/revoked`, `process_alive/exited/unknown`, work eligibility and effect settlement.

| Condition | Safe transition and evidence |
|---|---|
| Disconnect/EOF | Record session loss, last contiguous evidence cursor and last observed host state; do not infer crash, cancel or free reservations |
| Reconnect | Fresh authentication and incarnation/policy/fence check; historical spool reconciliation precedes any new admission |
| Partition suspicion | Timeouts identify unavailable communication, not root cause; deny new unsafe admission/renewals, retain unknown effects |
| Node crash | Require independent OS/supervisor observation when available; the observation does not settle previously dispatched effects |
| Retirement | Authorized removal workflow closes placement, drains or records residual unknowns, revokes membership and inventories copies |
| Lost machine | Recovery plan uses retained canonical/evidence state; local-only material or physical erasure remains unknown |

A disconnected worker may finish only an explicitly pre-admitted bounded local computation within its existing containment and policy; no new step, child, unapproved source or external effect is admitted offline. A task requiring online effect freshness cannot continue that effect path. Bounded encrypted/authenticated evidence spooling may continue with hard byte/retention limits; spooling is not canonical publication. Overfull evidence storage closes work rather than dropping mandatory evidence and announcing success. Operational error labels state measured facts, never vendor motive. RX-F09/F10/F16 cover isolation, saturation and reconnection.

<a id="q11"></a>
## Q11 Lost-machine recorded-work recovery

**IN, RX-R13.** Recovery material is a verified checkpoint at canonical high-water H plus the complete committed suffix after H through an independently established recovery cut, referenced immutable artifacts and outstanding operation/reservation state. A checkpoint digest alone is insufficient. “Latest” is unknown without an authoritative cut/commit witness. The capsule must retain current accepted directives/gates, exact dependencies and source revisions, lineage, pending approvals/questions with expiry, receipts, unresolved effects, attribution/settlement references and explicit missing material. R-Q memory summaries are disposable accelerators, never a substitute.

Recovery sequence:

1. Quarantine the successor; verify release/schema compatibility, checkpoint identity/consistency, suffix continuity and artifact availability/rights
2. Reproduce canonical state deterministically or stop on missing bytes, gap, divergence or invalid digest
3. Establish current writer authority through the existing core recovery or D020 plugin seam; never clone writer authority from a backup
4. Revalidate exact GoalSpec/plan, enrollment, destination privacy, launch/isolation profile, route capabilities, current grant/Stop/configuration and cumulative budget
5. Reconcile outstanding effects by stable logical operation ID and receiver evidence; retain reservations/uncertainty
6. Classify each step below, issue a fresh bounded execution lease only where safe, hydrate the minimum approved content and continue the same authorized goal
7. Independently verify useful task progress and preserve a source-to-successor evidence/accounting map

| Class | Sufficient candidate evidence | Disposition |
|---|---|---|
| Re-executable | No effect was dispatched, or independently established no-effect; exact input retained; retry within authorization/budget | New attempt, same logical operation/retry owner and cumulative accounting |
| Resumable | Valid checkpoint/progress cursor; complete required suffix; receiver supports the specific continuation with current fences | Resume from verified boundary; no blind restart of earlier effects |
| Settled | Declared independent effect receipt/postcondition and acceptance evidence match exact identity | Retain result; do not reapply |
| Unknown/blocked | Possible dispatch, missing receiver truth, missing source, unsupported state schema, unresolved rights or unverified old process conflict | Preserve uncertainty, restrict new conflicting work and request the exact missing evidence/authority |

Machine change does not create a new budget, approve stale interactions, reset recovery allowance or copy authentication. Required destination authentication is an operator-provisioned R-E prerequisite. If all work/evidence existed only on the lost disk, recoverability is bounded by what was actually replicated or exported; no RPO of zero follows. Recovery time decomposes detection, writer restoration, fence installation, replay, policy/credential readiness, hydration, effect reconciliation and independently verified productive continuation; each is U. RX-F10/F22/F23 test these boundaries.

<a id="q12"></a>
## Q12 Duplicate prevention and effect evidence

**IN, RX-R09/R14.** Separate command deduplication, attempt identity and external effect idempotency. A canonical unique command receipt prevents repeated state transitions, but does not make an external call exactly once. One declared retry owner coordinates the operation across nodes, adapters and reconnects. Upstream automatic retries, if any, must be bounded and visible under that ownership or the route is incompatible with the task.

For a cooperating synthetic sink, the canonical idempotency key is `(receiver_scope, effect_id)`. Atomically bind that key to the immutable `exact_body_digest`, mutation and durable result. The digest is an equality/conflict check under the same key, never another key component or a new namespace: identical repeats return the existing result; altered bytes under the same receiver/effect key conflict and cause no new mutation. Bind work/Stop checks at the same gate. Retain deduplication evidence at least through the authorized retry/recovery/replay horizon; expired evidence causes reconciliation/hold, never reuse as a fresh operation. A completed receipt arriving after lease replacement is historical settlement evidence and may update accounting, but may not authorize a new action.

For an external sink without this contract, use an independently queryable postcondition or operator reconciliation; if effect occurrence cannot be established, hold the conflicting retry. Compensation, when supported and authorized, is another recorded effect, not rollback or erasure of the original event. A node's signed “done” proves only attributable reporting unless the receiver and verifier meet the required trust model.

RX-F08/F11 count actual mutations in an independently owned synthetic sink ledger through acknowledgement loss, restart, duplicate, reorder, ID collision and deduplication expiry. Expected accepted mutation count is one for an idempotent completed operation and zero for a rejected stale operation; unknown real-world effects are never assigned either value without observation. A passing local sink cannot establish exactly-once behavior at arbitrary providers.

<a id="q13"></a>
## Q13 Drain and D022 Stop semantics

**IN, RX-R15.** `drain` is an authorized node-removal mechanism, not a fourth Stop mode. Freeze new placement and lease renewal; capture owned-work/process/descendant inventory and outstanding transfers/effects; apply the explicitly chosen D022 scope/boundary; retain only the exact drain allowlist; export/verify required durable evidence; fence residual work; reconcile effect receipts; record `drained` only against its declared predicate. A deadline can produce `drain_incomplete`, never invented settlement.

- **Aggressive:** fence further selected-agent dispatch and request forceful interruption without waiting; descendants and remote unknowns remain separately listed
- **Full:** include owned workers, shells, monitors and relaunchers, with ownership snapshot plus concurrently registered descendants covered by the same closure; per-member local process observations, remote fence receipts and unsettled effects remain separate
- **Lazy:** close admission and stop at the named observable operation boundary, with a finite deadline and configured, already-authorized escalation; no unbounded “finish whatever it wants” interpretation
- **checkpoint:** produce verified state/evidence at a declared boundary; it neither ends the lease automatically nor proves external settlement
- **interrupt:** an attempt to halt execution; it is not proof of process exit or effect rollback

The drain allowlist is restricted to evidence flush, authorized checkpoint materialization, existing effect-status reconciliation, control/fence installation and governed cleanup. Publication, new inference, new task steps, new recipients and compensation are not implicitly allowed. A needed compensation has separate admission. Local emergency control may protect local processes while canonical authority is unreachable, but it cannot forge a global Stop receipt.

RX-F12 injects Stop/drain before admission, start, spawn, dispatch, spool flush, ACK and release; a late relaunch callback must reject stale work/Stop/process identities. For a lost node, successful retirement of membership can coexist with `quiescence_unknown` and `remote_copy_deletion_unknown`. Canonical work must survive through independently verified storage, not merely a worker's sent-byte count.

<a id="q14"></a>
## Q14 Reconnect, partitions and explicit gaps

**IN, RX-R12/R16.** Reconnect begins with current membership, authentication and schema negotiation. The node reports its last canonical receipt and local observation spool ranges, including stream incarnation, contiguous high-water, digest chain and any local gaps. The canonical writer returns its committed high-water, replay floor, current fences and exact accepted/refused observation dispositions. Reconciliation never blindly takes the greater timestamp or concatenates local logs as canonical history.

Old evidence can be admitted with both observed-at and newly-recorded-at fields, plus the original source/cursor and confidence. Duplicates preserve one canonical observation identity. Conflicting bodies for an observation ID quarantine that stream. A node's self-signed causal claim does not override independently observed sink evidence. Reordering is represented with causal references; wall-clock sorting is only a presentation with disclosed uncertainty.

If requested history predates the replay floor, or a spool suffix is missing, emit a `GAP/RESET` containing known range, reason, last verified cursor, next available cursor and consistency-defined snapshot locator/digest. Recover a view from an authorized snapshot plus suffix, with a visible reconstruction marker. A snapshot can reconstruct current state without reconstructing every lost event. If missing history is required to justify effects/authority, recovery stays blocked. Cursor rollover starts a new linked stream incarnation; no silent integer wrap.

CRDT-style merging is an admissible option only for explicitly non-authoritative, scope-controlled observations where merge semantics are proven and deletions/retention remain governed. It is not a substitute for exclusive grants, spend reservations, writer election, revocation order or canonical effect settlement. A strict canonical observation inbox is the conforming competitor. RX-F09/F16 test replay floors, duplicates, conflicting IDs and flood pressure. Neither approach can recreate lost evidence.

<a id="q15"></a>
## Q15 Cross-OS contract and native qualification matrix

**IN, RX-R17.** Accepted profiles are Windows 11 25H2 build 26200 Home/Pro, plus 24H2 build 26100 Enterprise, x64/local NTFS; native Linux kernel 6.12 LTS primary and 6.6 LTS compatibility minimum, cgroup v2/local ext4. Arm64 is a later case. WSL2-ext4 and WSL2 `/mnt/c` are separate mandatory development/test cases, never production substitutes. SMB/NFS canonical storage is out of scope, and ReFS/xfs/btrfs are deferred. Record the actual kernel/build/patch/security/filesystem identity; distribution branding is not a kernel pin.

| Area | Candidate normalized meaning | Explicit platform-specific or unknown boundary |
|---|---|---|
| Path/root/drive | Opaque workspace root capability plus validated relative components and source revision; source bytes preserved | Reject drive-relative, UNC/device/alternate-stream, traversal, absolute and ambiguous names unless exact capability permits them; no automatic slash/string rewrite |
| Case/Unicode/name collisions | Detect mapping collisions before materialization; preserve exact recorded name and bytes | `A`/`a`, normalization variants, reserved names, trailing punctuation and long paths may require refusal or explicit renamed derivative; no silent overwrite |
| Line endings/encoding | Original source digest is byte identity; normalization is an explicit derivative with loss/transform record | CRLF/LF and text-mode I/O cannot silently alter a checkpoint or approval-bound payload |
| Process creation | Typed executable/argument/environment/cwd contract and creation-time containment receipt | Windows command-line parsing versus native argument vectors; shell quoting is not a portable encoding; no generic remote shell |
| Process identity/termination | Process incarnation plus containment identity, creation observation, exit observation and restart fence | Windows jobs/console controls and Linux groups/cgroups/signals need native mapping; a signal sent is not a process-tree settlement receipt |
| Filesystem commit | Verified staging followed by profile-qualified atomic visibility and durability protocol | Rename, replace, open-handle, flush, disk-full and reset behavior require exact profile evidence; atomic visibility is not crash durability |
| Locks | Exclusive canonical ownership through the store seam; local lock semantics individually tested | A local advisory/mandatory file lock is neither a distributed lease nor an external-effect fence; inherited handles matter |
| Sandbox/egress | Required capability vector and independently verified isolation profile before placement | R-E/R-U own Windows and Linux enforcement; cgroup membership or a container label alone does not qualify confidentiality or egress |
| Clock/suspend | Separate wall timestamps, local monotonic durations and logical ordinals | Sleep, reboot, rollback and skew invalidate freshness assumptions; no cross-node total order from wall time |

RX-F13 supplies exact accept/refuse/unknown cases on every profile, including symlink/reparse substitution after preflight, case collision, environment leakage, inherited-handle escape, spawn-vs-Stop and partial durable transfer. RX-F23's later native reset campaign uses D028's application-consistency definition at the commit boundary. No process kill substitutes for abrupt VM-reset evidence. All results remain U; fixtures are not commands, and no target provisioning is authorized by this report.

<a id="q16"></a>
## Q16 Enrolled but untrusted node threat model

**IN, RX-R18.** Trust the canonical admission/kernel/store boundary, the qualified final actuators, operator provisioning and declared OS security boundary. Treat task code, node claims, artifact payloads and optional plugins as hostile. A compromised execution host can lie, omit receipts, replay old data, manipulate timing, exhaust quotas/queues and read any plaintext it legitimately receives. A host administrator or compromised kernel may defeat that node's local sandbox. Accordingly, only place private plaintext on nodes whose operator/host trust and residency are approved for it; encrypted transit cannot protect plaintext from its recipient.

An executor can read only the admitted control subset and currently permitted source representations, write only its isolated output staging and bounded evidence spool, and observe only its own scoped queue/control/health data. It receives no canonical-store filesystem access, global inventory, other task's messages, arbitrary artifact lookup or provider credential export. Canonical output publication, extra children, source changes and promotion require existing admission. Shared host load metrics are coarsened/scoped to avoid another tenant's workload disclosure.

Containment includes local least privilege, bounded CPU/RAM/disk/transfer/process counts, allowlisted egress, protected launch identity, separate control queues and rejection before parsing unbounded content. Host-wide isolation is not proven by an authenticated transport. Cross-tenant/hosted service isolation needs its own reviewed threat model; this candidate is not certification.

On compromise: quarantine node, commit revocation/close renewals and artifact reads, install current fences at trusted sinks, stop affected local workers where observable, retain/treat reported evidence with explicit trust status, reconcile effects and copy inventory, and require new operator-approved identity/profile before return. Do not promise remote deletion or historical confidentiality restoration. RX-F14/F19 exercise hostile synthetic claims, not exploit code or a determined attacker.

<a id="q17"></a>
## Q17 Forgery, replay and authority escalation refusals

**IN, RX-R02/R04/R18.** Distinct barriers have distinct falsifiers:

| Attack | Enforcement candidate | Decisive negative observation |
|---|---|---|
| Node grants itself broader scope | Canonical intersection of GoalSpec, role, current grant, policy, receiver scope and reservations | Self-reported capability causes one forbidden admission |
| Node forges completion/event | Worker submits attributed observation; only current canonical writer assigns accepted ordinal/receipt; verifier checks postcondition | Worker-chosen ordinal/status becomes accepted completion without canonical admission/evidence |
| Node replays another peer's request | Authenticated sender, audience and incarnation bound to exact message/operation | Valid message for A accepted as B or in another task/domain |
| Old writer submits after takeover | Canonical store verifies monotonic current writer fence at append | Old writer commits any new event after new ownership gate |
| Node mints a higher fence | Trusted issuer/installation provenance plus scoped monotonic checks | Arbitrary high integer invalidates current owner or gains execution |
| Worker creates portfolio work | No work-packet/lease mint capability; bounded proposals only | New goal/child/effect gets admitted because it came from an enrolled node |
| Stale configuration/approval reused | Compare exact current revisions and approval-bound effect/data/recipient/expiry | Reconnect changes recipient or bytes while reusing approval |

A signature authenticates an issuer's statement, not its truth or permission. Authentication, entitlement, observed conformance, role authority and privacy are independent. A compromised canonical trust root is outside the baseline; a compromised worker is inside it. RX-F14/F15 use receiver and canonical logs as independent oracles, plus negative controls with deliberately removed checks. A type error or disconnected harness that never reaches the intended gate does not count as a killed safety mutant.

<a id="q18"></a>
## Q18 Egress and residency at placement and transfer

**IN, RX-R05/R06/R18.** Attach a `DataPlacementBinding` to the accepted task: data classes and source revisions, allowed node principals/operator domains/regions, exact purposes, permitted representations and recipients, processing/storage/backup/telemetry locations, retention/copy policy, onward-egress bounds and evidence needed for residency. Enforce eligibility before sending private metadata or content. A node's network address is not a residency proof.

Placement records the evidence supporting its residency/operator claim and its expiry. If hardware/location assurance is unavailable, choose an already approved node or block; an encrypted connection, cost preference or urgent deadline does not widen scope. Credentials and source secrets are not inferred to be authorized simply because the task references their location.

The transfer boundary repeats the check immediately before each disclosure; destination process/route/payload compilation and final egress repeat it again under R-E/R-T. Prevent arbitrary locator fetches and redirect widening. Direct peers receive audience-specific permits from existing canonical authority. Exported observability, thumbnails, filenames, timing and hashes are included in disclosure analysis. R-Q source revocation and R-T descendant/copy records travel with artifacts; cache hits do not bypass current rights.

A stale or malicious node can retain already-received bytes; revocation limits future controlled access, not knowledge. Choose coarse trusted-host placement plus minimum disclosure versus a more restrictive isolated execution profile with independently proven egress controls; both preserve the same policy. RX-F05/F19 refuse unknown/out-of-policy destinations and maintain offline-copy unknowns.

<a id="q19"></a>
## Q19 Transport-neutral protocol shape

**IN, RX-R19.** This is a semantic envelope, not a wire encoding or frozen protocol. Each message declares protocol/schema identity, message class/ID, authenticated sender and audience, domain/node/incarnation/session, causal command/operation IDs, body digest and bounded length, and only the typed references required by its class. Unsupported critical fields/capabilities refuse; unrecognized optional evidence is quarantined rather than executed. Sender timestamps are observations, never authority.

| Class | Required class-specific fields and receipt meaning |
|---|---|
| HELLO / WELCOME / REFUSAL | Challenges/transcript binding, offered/selected protocol, security floor, required/negotiated capabilities, trust revisions, session identity; no execution grant |
| DESCRIPTOR / DESCRIPTOR_RECEIPT | Node incarnation, exact capability/profile facts, issuer/evidence, freshness, privacy-safe resource observations; capability is not entitlement |
| ENROLL / REVOKE_MEMBERSHIP | Owner command/approval binding, node/key/incarnation, expected enrollment revision, new canonical revision, per-receiver installation state |
| LEASE_GRANT / RENEW / CLOSE | Task/step/packet, holder, work epoch, bounded duration/resource/grant refs, current policy/Stop/config refs, canonical admission receipt |
| FENCE_INSTALL / FENCE_INSTALLED | Issuer, receiver/resource scope, domain-specific new floor, expected state, durable installation receipt, process/store restart identity |
| CONTROL_MANIFEST / MANIFEST_READY | Checkpoint/canonical cursor, control-kernel digest, scoped artifact entries, rights refs, pending/unknown/reservation references; no credential/permit payload |
| HYDRATE_REQUEST / CHUNK / TRANSFER_RECEIPT | Transfer/object revision, authorized representation/range, destination incarnation, policy, byte bounds, integrity verification and visibility status |
| START / EFFECT_REQUEST / RESULT_OBSERVATION | Stable operation/attempt/body identity, exact target, current work/Stop/grant/config refs, process incarnation, last known boundary |
| RECORD / RECORD_ACK | Observation ID, local stream incarnation/cursor/previous digest, canonical input refs; ACK identifies committed canonical ordinal and durability scope |
| QUERY_OPERATION / DISPOSITION | Stable operation and body digest, authenticated scope, current evidence state; no blind redispatch |
| HEARTBEAT | Observed incarnation, health state, sequence/freshness and bounded queue/resource metrics; does not renew lease or prove quiescence |
| STOP / DRAIN / DRAIN_STATUS | Exact D022 mode/scope, command and pause epoch, owned inventory/cut, boundary/deadline/allowlist, per-member and effect statuses |
| RESET / GAP / SNAPSHOT / REPLAY | Stream incarnation, requested cursor, replay floor/high-water, missing interval/reason, materialization locator/digest, snapshot consistency and authorized projection |
| CREDIT / OBSERVE_ACK | Independent stream/event/byte limits and monotonically contiguous acknowledgement; not command acceptance or effect settlement |

Canonical event cursor, node observation cursor, artifact byte offset, transport sequence and credit accounting are different typed fields. No global timestamp cursor. A record ACK is never a credit grant; a transfer ACK is never a task result. Reconnect rotates session identity while stable command IDs persist. Numeric rollover uses a new linked stream incarnation with a recorded boundary before exhaustion. All byte/event/depth/queue/unfinished-transfer limits have finite profile-bound values; unknown limits mean the capability is not eligible.

Control, evidence and bulk content have independent bounded queues, scheduling/reservation and rejection paths. Artifact or view saturation cannot monopolize authentication, Stop, fences or writer durability. A bad peer cannot force allocation from claimed length or import executable code in negotiation. RX-F16/F20/F24 test bounded synthetic pressure, schema evolution and cursor limits; production performance still requires R-O measurements.

<a id="q20"></a>
## Q20 Broker/IPC relationship and G05 freeze blockers

**LO/IN, RX-R19/R20.** Reuse the broker's semantic identity/command ledger, process incarnation, D022 scopes, explicit uncertainty, bounded credits, separate views and canonical receipts. Do not expose local OS-peer identity assumptions directly as remote authentication. Remote enrollment, node incarnation, trust rotation, transfer policy and cross-node recovery are additional layers, not a second broker authority.

The four G05 blockers remain release obligations:

1. **Version negotiation:** broker v1 exact-match semantics do not become fabric range negotiation by relabeling HELLO; define compatibility/refusal and the shared capability envelope explicitly
2. **Snapshot materialization:** digest-only reference must be completed by an authorized retrievable representation and consistency proof; fabric hydration must not widen its audience
3. **Cursor rollover:** distinguish bounded cursor and stream incarnation, record linked rollover and forbid wrap; numeric limits must match actual schemas, not invented wider integers
4. **ACK-release:** specify strictly forward contiguous release, duplicate no-op, backward refusal and exact durable ownership transfer; no ACK releases a lease, reservation or external effect by implication

A fabric envelope may carry existing canonical bytes as opaque authenticated content with their declared version; it must not silently recanonicalize digests or choose a new encoding. Broker framing/canonical-byte decisions remain in their own conditional freeze process. The fabric semantic design chooses neither framing nor serialization library.

Transport-to-broker adapters preserve one command identity and retry owner. A remote reconnect or UI reattach must not redeliver an approval, rerun a command or revive a process. Snapshot and replay content is scope-filtered before release. MCP subprocess/task behavior follows the version-specific protocol supplement, not generic fabric cancellation assumptions. RX-F20/F24 test integration against frozen synthetic schemas; until those schemas and native conformance pass, fabric protocol freeze stays blocked. This report does not close G05 or G04.

<a id="q21"></a>
## Q21 Provider-free fixture acceptance predicates

All 24 handoffs are **UNEXECUTED**. [local-test-handoffs.json](local-test-handoffs.json) is the full machine specification; [UNEXECUTED-local-test-handoffs.md](UNEXECUTED-local-test-handoffs.md) provides inputs, prerequisites, independent oracle, evidence, exact pass/fail and stopping conditions. No command is supplied because no fabric entrypoint is verified. An implementation, selected crypto/transport and approved disposable native targets require a separately authorized session. No fixture needs a provider/model/account, real credential, external network or spending.

| Fixture | Exact central predicate |
|---|---|
| RX-F01 Enrollment/revocation | One exact Owner-approved join consumes one bootstrap proof; replay/changed binding refuses; enrollment alone permits zero task/effect/artifact access; revoked current generation cannot rejoin |
| RX-F02 Mutual auth/downgrade | Both authenticators/current trust and required version/capabilities are necessary before disclosure; stripped, replayed, wrong-audience, unauthenticated and below-floor variants refuse |
| RX-F03 Clone/incarnation | Stale restored incarnation and cross-node message refuse; observable concurrent clone conflict quarantines; indistinguishable copied-key case is explicitly unknown, never certified unique |
| RX-F04 Control-first hydration | Durable exposure intent/lineage/reservation registration precedes transfer; protected publication requires verified control/artifact and fresh rights/fences, even after restart; crash-unknown publication reconciles under the same identity |
| RX-F05 Placement/egress | Every disallowed or unknown hard-bound destination sees zero protected bytes/metadata; authorized destination succeeds with exact PlacementReceipt |
| RX-F06 Exclusive lease | At every canonical step at most one current admitted holder; renewal/replace obey expected revision; conflicting replacement remains blocked until sink barrier/quiescence predicates |
| RX-F07 Revocation/install race | After durable receiver installation, all old-fence mutations refuse across restart; pre-install interval stays explicitly pending/unknown; arbitrary larger tokens refuse |
| RX-F08 Lost ACK/crash cuts | Canonical admission precedes permit; every uncertain dispatch remains unresolved until evidence; replayed ACK never starts a second effect or releases possible liability |
| RX-F09 Partition replay | No new offline admission; stale spool may become historical evidence only; old work never regains authority when partition heals |
| RX-F10 Lost-machine resume | Valid checkpoint+suffix reproduces state and continues an independently checked useful task; corrupt/missing state blocks; unresolved effects remain blocked and accounting survives |
| RX-F11 Idempotent sink | Duplicate same effect/body mutates once; changed body refuses; dedup expiry produces hold/reconciliation, never fresh unsafe retry |
| RX-F12 Drain/Stop | New placement/renewal closes; exact D022 scope/boundary applies; relaunches reject stale fences; inaccessible members/effects remain unresolved; required evidence survives |
| RX-F13 Cross-OS | Each native/dev case accepts only its declared normalization and containment semantics; collision/traversal/unsafe mapping refuses; untested cells remain unknown |
| RX-F14 Hostile node | Forged authority, event ordinal, other-node replay and self-minted fence cannot cause canonical mutation or disclosure; bad reports remain attributed candidates |
| RX-F15 No second executive/writer | Enrollment/work lease produces zero writer/portfolio/child-admission rights; only admitted kernel commands append/issue work |
| RX-F16 Gap/rollover/pressure | Missing interval emits GAP/RESET; valid snapshot+suffix reconstructs without invented events; wrap/backward ACK refuses; bulk flood preserves bounded control progress |
| RX-F17 Lean and idle | Absent/disabled/idle zero-activity claims require retained per-probe enabled synthetic sensitivity receipts under the same observer/reset/baseline; blind/failed probes remain UNKNOWN. Core has no consensus/fabric activation and idle execution has no inference/work lease |
| RX-F18 Placement comparison | Same hard floors and independently measured native-unit observations for rule versus Pareto candidates; unknown remains null; no unapproved preference tradeoff |
| RX-F19 Privacy/credentials | Current rights checked before metadata and protected publication; deletion cuts include unresolved exposure intents/possible copies without claiming presence; synthetic secrets never enter output; prior/unknown publication remains accounted |
| RX-F20 Protocol/broker boundaries | Negotiation/materialization/rollover/ACK rules agree across adapters; same command remains one identity; projection reconnect has zero effect dispatch |
| RX-F21 Availability seam | Automatic takeover succeeds under the plugin's declared sufficient fault assumptions with one accepted writer; quorum loss blocks unsafe commits; disabled core does not pretend takeover |
| RX-F22 Unknown reservations | Outstanding possible liabilities survive node/attempt/writer change without double-counting or resetting recovery allowance; only authoritative settlement changes them |
| RX-F23 Native durability/supervision | Later authorized profile campaign verifies committed prefix/fence persistence after declared fault cuts; real VM reset and native supervisor races cannot be marked passed by process-kill substitutes |
| RX-F24 Version/resource envelope | Unsupported critical fields/versions and oversized/infinite-credit claims refuse before execution/allocation; cumulative caps persist through reconnect/rollover |

A control trace satisfying the schema is not a crypto, OS or independent-outcome result. Actual refusal must reach the intended gate; no-op harnesses that refuse everything fail positive controls. Verification uses an independent expected-state/receiver ledger, not the implementation's own status string. Scope of each test's non-proof is explicit.

<a id="q22"></a>
## Q22 Ownership, idle and continuity proof obligations

**IN, RX-R10/R14/R20.** RX-F15 attempts canonical append, grant mint, child spawn and portfolio scheduling from both a correctly enrolled no-grant node and an active bounded worker. Both must fail outside the exact grant; positive control uses the existing canonical admission route. Independent audit verifies every accepted event's writer fence and source command, every active work lease's parent and current owner, and every effect's receiver identity. Merely having one process named “writer” is insufficient.

RX-F17 observes absent, installed-disabled, enabled-idle and active profiles separately. Idle means zero inference and work leases, not zero memory, installed metadata or health traffic. Observation includes all descendants, restarters and helper routes; unknown coverage cannot yield zero spend. Dedicated enabled availability coordination has its own declared cost, never hidden under a worker-idle assertion. Every zero-activity observation requires its own enabled synthetic sensitivity control for provider-attempt, helper/descendant activation and work-lease probes, using the same observer configuration, reset procedure and defined baseline. Retain expected-versus-detected control receipts; use inert local provider-attempt sentinels with no provider/network call. Reset into the same declared baseline before absence measurement. A blind, failed or uncalibrated probe is UNKNOWN, never zero; ordinary task acceptance does not calibrate a detector. A calibrated synthetic run can bound absence of provider-dispatch attempts in its observed graph, not establish a subscription billing fact.

RX-F10 completes a useful synthetic task after loss: transform two admitted fixture inputs into an exact independently precomputed output while preserving current instructions, artifact provenance, effect state and total accounting. A hidden independent oracle changes an instruction/revokes an artifact before resume and checks that the successor obeys the current state, not the old summary. Recovery that merely boots, replays bytes or displays “done” fails the productive-continuity predicate. Compare against a strong simple baseline: manually reconstruct from the same retained sources and exact controls, under identical authority and independent outcome checks. Human effort and latency are U until a separately admitted study; success on one deterministic task does not establish general superiority.

## Recommendation register

All recommendations are IN candidates for qualification, not technology selections. Every rival below preserves fixed accepted invariants. Unsafe split brain, stale-cache admission, certificate-as-authority and duplicate retry are negative controls only.

| ID | Candidate and conforming competitor | Decisive falsifier / fixtures | Passing does not establish |
|---|---|---|---|
| RX-R01 | Owner-approved key-bound enrollment versus Owner-approved attestation-backed enrollment | Join replay/wrong binding grants access; F01 | Correct physical identity or entitlement |
| RX-R02 | Canonical incarnation issuance with scoped session binding versus per-incarnation credential issuance with same canonical registry | Stale/clone/cross-node identity accepted or concealed uncertainty; F03/F14 | Hardware uniqueness or key non-exfiltration |
| RX-R03 | Authenticated transcript negotiation versus exact-version mutually authenticated profiles | Downgrade/one-sided auth/early replay produces disclosure; F02/F24 | Crypto implementation security |
| RX-R04 | Online current-state receiver gate versus durable pushed floors with installation barrier | Stale request commits at protected sink after gate/barrier; F07/F21 | Instant offline Stop or malicious-sink obedience |
| RX-R05 | Authorized pull hydration versus bounded push of the exact same approved manifest | Content/metadata precedes authorization or durable exposure intent, publication bypasses fresh rights/fences, or lineage is lost; F04/F19 | No prior disclosure or semantic media fidelity |
| RX-R06 | Deterministic hard-filter/rule placement versus hard-filter/Pareto selection | Ineligible host selected or unknown treated as free/verified; F05/F18 | Best placement or savings |
| RX-R07 | Renewable bounded exclusive step lease versus non-renewable one-step permit with the same current-holder/fence checks | Two admitted holders/conflicting unsafe replacement; F06 | Physical halt of a lost host |
| RX-R08 | Atomic sink epoch+effect transaction versus trusted serialized actuator with explicit external ambiguity | Check/commit race, rollback of floor, forged high epoch; F07/F11 | Exactly-once arbitrary external effects |
| RX-R09 | Durable outbox plus operation-query reconciliation versus synchronous durable-intent RPC plus the same ambiguity/dedup ledger | Lost ACK causes new effect or false success; F08/F11 | No unseen provider retry |
| RX-R10 | Minimal core seam with linked first-party availability plugin versus isolated availability service implementing the same opt-in seam | Consensus/default remote activation leaks into core or stale writer commits; F17/F21 | Availability outside declared fault assumptions |
| RX-R11 | Central relay versus direct scoped peer plane versus upstream-delegated bounded host, each with same canonical admission | One fails safety/resource/control requirements while another satisfies them; F05/F15/F16 | A selected topology, route or universal performance winner |
| RX-R12 | Canonical observation inbox versus scoped non-authority convergent observation set | Merge invents authority/history or heals a gap without evidence; F09/F16 | Global truth from dishonest reporters |
| RX-R13 | Checkpoint+complete committed suffix versus full canonical replay with governed artifact retrieval | State/authority differs or missing record called complete; F10/F23 | General task-quality continuity or zero RPO |
| RX-R14 | Receiver atomic idempotency ledger versus authoritative postcondition reconciliation and hold | Second mutation or unsafe retry on unknown; F11/F22 | Unconditional exactly-once execution |
| RX-R15 | Eager indexed drain/fence inventory versus generation-fenced admission with bounded inventory reconciliation | In-scope relaunch escapes or remote unknown called settled; F12 | External rollback or native tree completeness |
| RX-R16 | Event-sequence replay with snapshots versus bounded segmented observation replay with the same gaps/durability semantics | Silent gap/wrap or ACK releases wrong obligation; F16/F20 | Unlimited retention or complete physical history |
| RX-R17 | Portable strict workspace subset versus explicitly profile-specific materialization with refusal/loss reports | Collision/traversal or byte changes become invisible; F13 | Universal application portability |
| RX-R18 | Trusted-host minimum disclosure versus qualified isolated-host profile plus same privacy grant | Unauthorized source/control/egress path succeeds; F14/F19 | Security against hostile admin/kernel or certification |
| RX-R19 | Shared semantic envelope with class-specific schemas versus distinct typed protocols with audited lossless adapters | Identity/receipt semantics change across a bridge; F20/F24 | A transport/encoding freeze |
| RX-R20 | Independent executable state/receiver oracle versus independently reviewed model monitor plus external evidence adjudication | Vacuous positives, wrong failure attribution or self-PASS counted acceptance; F01–F24 | Unbounded proof, target qualification or superiority |

## Bounded unknowns and next evidence

- Freeze the exact physical-versus-admitted-executor wording for profiles requiring physical non-overlap. RX-F06 must demonstrate safe hold until evidence, not advertise impossible remote process control
- Provide a qualified store/availability implementation and independent model for writer fencing, membership changes, snapshot installation and old-backup restoration. RX-F21 is required before any takeover claim; no library is selected here
- Provide a receiver inventory and effect-class matrix identifying atomic fencing, online gate, idempotency, observable reconciliation and unsupported sinks. Unknown sinks block conflicting recovery
- Adopt finite lease/freshness/replay/dedup/transfer/control-resource and drain thresholds before testing. Values depend on approved profiles and measured workloads; this report invents none
- Freeze G05's four blockers and prove corresponding native G04 behavior. Synthetic protocol agreement cannot fill OS cells
- Provide operator-approved node identity, residency and trusted-launch evidence. Authentication/certificates alone cannot qualify R-E or R-U; credentials never move inside continuity capsules
- Run the exact handoffs in separately authorized provider-free local sessions with independent review, then compare productive continuity with a strong simple baseline under the same correctness/privacy/accounting floors

## Completion and non-proofs

Coverage includes all 22 exact questions and all 11 completion bullets in [coverage.json](coverage.json). The report provides a substantive candidate and bounded unknowns; it is not an implementation plan in place of findings. Runtime status is uniformly UNEXECUTED. Source and artifact structural checks do not constitute independent acceptance.

No availability/failover time, RPO/RTO, transport/placement performance, savings, universal security, hardware clone resistance, route qualification, entitlement, legal clearance, remote rollback, instant offline Stop or exactly-once arbitrary effect is established. There is no guarantee against a determined node controlling its OS or a compromised trusted root. No final language/store/framework/transport/vendor selection occurs. No current Owner decision is reopened. Protected source files were read only; authored-output privacy/secret/path checks and before/after protected-file hashes are recorded in artifact QA. A clean pattern scan is a bounded check, not a universal confidentiality proof.
