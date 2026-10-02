# R-M provider-free acceptance handoffs — ALL UNEXECUTED

These are independent source/evidence and synthetic semantic checks, not executable mod tests. No Claude binary, supplied repository script or mod is run, imported, installed or compiled. No provider, account, credential or live-host call is allowed. No verified executable entrypoint exists, so no runnable commands are invented. Successful review accepts a research inference, not an implementation or license.

## F01 — Source identity and date/version reconciliation

- Status: UNEXECUTED
- Dispositions: D10, D13, D14
- Inputs: source-register.json; source-file-pins.json; Official announcement/release/design-issue metadata; Pinned public Git tree and independently retrieved selected file bytes
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Recompute Git blob identity and SHA-256 using passive file hashing only; Read date fields separately: publication, commit, issue creation and dated update heading; Label 2.1.277 declaration versus 2.1.287 documented target; do not merge them
- Independent oracle: Every claim binds to its actual primary source and version/date kind; wrong-version evidence cannot qualify a newer host Source: Pinned Git objects plus official release metadata, not report assertions
- Useful positive control: Old declarations may support an explicitly historical claim while current-doc statements remain independently scoped
- Negative control: Change header version to 2.1.287 in a synthetic metadata copy while retaining old digest; oracle must reject
- Expected evidence: Verification worksheet, full hash results, source/date crosswalk and discrepancy record
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Historical rollout completeness, source/binary parity, functional correctness or legal rights
- Blocker: No runtime attempt authorized; independent review pending

## F02 — Schema drift and static graph completeness

- Status: UNEXECUTED
- Dispositions: D06, D10
- Inputs: Pinned declarations and current reference; Synthetic capability table with known, missing and renamed fields; Selected registration modules and declared imports as plain text
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: List differences without compiling/importing modules; Mark version-specific capabilities unknown when only older declarations exist; Introduce an imported callback with an undeclared process effect into a synthetic graph, not executable code
- Independent oracle: No missing/renamed field is silently defaulted and no incomplete graph proves absence of effects Source: Independent schema/source reading and graph membership, not a tool-reported validation pass
- Useful positive control: An exact matching documented read-only field is kept as documented, still unqualified
- Negative control: A missing current MCP permission contract is filled from the old no-prompt declaration; reject
- Expected evidence: Version/loss map, declared versus reachable effect table, unknown list
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Completeness of vendor static analysis, actual dispatcher behavior or stable compatibility
- Blocker: No runtime attempt authorized; independent review pending

## F03 — Observe, rewrite and answer semantics

- Status: UNEXECUTED
- Dispositions: D01, D02
- Inputs: Synthetic original request A at epoch 7; rewritten request B with different arguments; Observation-only events O1/O2; Synthetic returned result R with no external effect record
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Swap O1/O2 order and compare canonical effects in a hand-calculated table; Bind B to its new action digest and preserve A as origin; Represent returned R as synthetic answer, not settled external work
- Independent oracle: Observation order cannot create authority; changed action requires re-admission; synthetic answer is not effect settlement Source: Recursion accepted identity/admission/receipt invariants
- Useful positive control: Authorized unchanged A can progress and its real effect receipt remains distinct from observations
- Negative control: B reuses A approval or R becomes settled=true without recipient evidence; reject
- Expected evidence: Truth table for every case, original/changed identity fields and explicit result class
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Correct middleware implementation, exactly-once effects or performance
- Blocker: No runtime attempt authorized; independent review pending

## F04 — Guard failure and single admission path

- Status: UNEXECUTED
- Dispositions: D02, D03, D09, D12
- Inputs: Synthetic denied operation A and permitted independent operation B; Guard outcomes: allow, deny, throw, timeout, invalid result, short-circuit, missing guard; CLI/TUI/GUI/tool callbacks for the same action and old/current epochs
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Fill a decision table for each source and guard outcome; Ensure final effect eligibility depends on current independent grant and exact action; Ensure a failed optional observer cannot disable otherwise authorized B
- Independent oracle: A stays refused under all UI/guard origins; B stays possible under valid grant; neither origin nor string reply is authority Source: Current accepted command-schema and authority contract
- Useful positive control: B at current epoch reaches eligible status through all supported surfaces
- Negative control: Timed-out guard or direct button callback executes A while CLI path denies it; reject
- Expected evidence: Cross-surface decision table, denied-effect count as modeled count, explicit UNKNOWN runtime result
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Runtime security, authentication, actual timeouts or process containment
- Blocker: No runtime attempt authorized; independent review pending

## F05 — Reload, disable and revision boundaries

- Status: UNEXECUTED
- Dispositions: D05, D07
- Inputs: Synthetic module digest d1 replaced with d2; Outstanding d1 callback/timer; epoch rises 7 to 8; projection cache remains; Declared no-import disabled inventory phase
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Enumerate before-reload, staged, active, draining and unknown-cleanup states as proposed states; Require d2 re-admission and reject d1 new dispatch after fence; Retain unsettled prior effects rather than assigning them to d2
- Independent oracle: Code identity and authority revision are bound per attempt; cleanup uncertainty is explicit; disabled means no activation effects Source: D-024 continuity and accepted plugin/configuration requirements
- Useful positive control: Read-only replay of retained evidence is available after disabling module
- Negative control: Old timer runs as new grant or default session state overwrites canonical truth; reject
- Expected evidence: Revision/epoch worksheet, pending-cleanup record, old/new ownership ledger
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Real disposal guarantees, crash durability or safe hot reload
- Blocker: No runtime attempt authorized; independent review pending

## F06 — Installed-disabled and model-free phase matrix

- Status: UNEXECUTED
- Dispositions: D05, D06, D18
- Inputs: Synthetic phases: known metadata, dependency eligible, disabled, admitted, activated; Effect categories: import, registration, subprocess, network, credential, inference; Inventory CPU/disk column distinct from effects
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Complete phase-by-effect matrix; Keep metadata observation permissible without claiming zero resource cost; Add a dependency that starts while parent is disabled to negative copy
- Independent oracle: Disabled and no-action phases have no active plugin effects; ordinary inventory overhead is separately unknown/measurable Source: R-L contribution contract and committed PLUGINS-AND-EDITIONS inertness invariant
- Useful positive control: List component identity and missing-dependency reason without import
- Negative control: Listing a disabled mod triggers dependency initialization or helper inference; reject
- Expected evidence: Phase matrix, static dependency path, zero-effect requirement versus unmeasured overhead distinction
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Actual zero activity, absence of hidden code or lower idle cost
- Blocker: No runtime attempt authorized; independent review pending

## F07 — Direct and indirect credential-domain paths

- Status: UNEXECUTED
- Dispositions: D08, D15
- Inputs: Synthetic secret label SECRET_FIXTURE_A, never a credential; Graph nodes: operator launcher, authenticated host, mod, tool process, output filter, network and Recursion observer; D-029 boundary and R-E qualification requirements
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Draw graph as data records, not a deployed network; Mark every read and output edge, including CLI/process-mediated export; Require independent enforcement boundary for each path and mark unmodeled edges unknown
- Independent oracle: No unauthorized edge from credential domain to Recursion-readable/output domain; banning direct reads alone is insufficient Source: D-021/D-029 and independent source-documented reachability
- Useful positive control: An allowed sanitized operation result crosses without secret material
- Negative control: Direct file read blocked but process echoes secret into tool output; reject strong non-access claim
- Expected evidence: Complete modeled path table, edge authority, refusal/unknown classifications
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Actual secrets safety, OS-enforced isolation or complete attack coverage
- Blocker: No runtime attempt authorized; independent review pending

## F08 — Stop, owned work and rendering independence

- Status: UNEXECUTED
- Dispositions: D07, D11
- Inputs: Synthetic selected task with local child, relauncher, unrelated task, unreachable remote and unsettled external operation; Aggressive/Full/Lazy plus checkpoint/interrupt/drain vocabulary; Saturated output projection and closed/reloaded pane
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Classify each observation separately: request accepted, fence installed, local result, remote receipt, external settlement; Keep unresolved remote/external facts visible after pane closes; Preserve unrelated authorized task and a logical Stop control path during projection saturation
- Independent oracle: No close/abort acknowledgement implies rollback; selected scope and owned set remain explicit; no indefinite wait disguised as success Source: D-022 and terminal/interface accepted contract
- Useful positive control: Independent unrelated operation remains eligible; scoped Stop records remaining uncertainty
- Negative control: Pane disappearance labels Full settled despite unreachable node, or stops unrelated task; reject
- Expected evidence: Owned-set table, mode-specific receipt state, unresolved effect records, control-path dependency diagram
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Whole-tree kill behavior, control latency or remote settlement
- Blocker: No runtime attempt authorized; independent review pending

## F09 — Projection coalescing, follow-mode and notification boundary

- Status: UNEXECUTED
- Dispositions: D03, D04, D17
- Inputs: Synthetic durable sequence with receipt, ordinary progress, revocation, replay gap and question; Coalesced frame proposals at two geometries; Reader anchored to historical item; pending output; literal ESC-containing text
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Compare frame content to durable-event ledger without executing renderer; Require unchanged semantic anchor while reading history; Keep notification requests distinct from raw text; classify disallowed controls as data/refused
- Independent oracle: Only disposable visual intermediates coalesce; durable control/evidence facts remain reconstructable; safe text does not become terminal authority Source: R-K Q06–09 and common state projection contract
- Useful positive control: Progress-only frames may merge; explicit return-to-live restores following
- Negative control: Coalescing deletes a fence or question, resize jumps to wrong source item, or ESC text controls clipboard/cursor; reject
- Expected evidence: Projection/event mapping, anchor IDs, geometry revision and escaped-output cases
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Actual partial-write correctness, synchronized output support, flicker or input latency
- Blocker: No runtime attempt authorized; independent review pending

## F10 — Port rights, dependency closure and matched cost

- Status: UNEXECUTED
- Dispositions: D10, D13, D14
- Inputs: port-candidates.json; license-terms-ledger.json; Selected source manifests/imports as plain text; Unfilled matched port/native effort worksheet
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Keep rights gate unresolved until a specific counsel finding exists; List dependencies and hidden host services before calling artifact portable; Compare accepted scope and all cost components; retain all absent hours as null
- Independent oracle: No code candidate is qualified by file count, public visibility, nominal license metadata or unevaluated cost cells Source: D-026/D-027/D-033 and per-artifact evidence
- Useful positive control: Retain useful behavioral requirements as prior art with no copied code
- Negative control: Public repository is labeled Apache-compatible or null port hours converted to 0; reject
- Expected evidence: Rights matrix, dependency unknowns, cost categories and explicit unqualified disposition
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Legal fitness, feasible-port count or cheap porting
- Blocker: Counsel outcome, full selected-closure audit and separately admitted matched implementations are absent

## F11 — Unicode meaning and accessible task equivalence

- Status: UNEXECUTED
- Dispositions: D03, D13, D16, D17
- Inputs: Synthetic labels and diff lines containing tabs, combining marks, joiners, variation selectors, bidi controls and literal terminal controls; Original-byte reference and independently authored safe display expectations; Paired pane/text question, approval and Stop records
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Inspect how the proposed display transformation affects each input without running the mod; Keep source identity/bytes separate from escaped representation; Compare keyboard/text routes for identical target/action/uncertainty information; do not claim screen-reader validation
- Independent oracle: Control safety cannot silently destroy meaningful source distinctions; all control semantics remain reachable in accessible representation Source: R-K grapheme and accessibility requirements plus human-readable expected semantic records
- Useful positive control: Escaped bidi/control text remains inspectable and a labeled text approval names exact action
- Negative control: Deleting a joiner changes displayed meaning with no marker, or a text-only user cannot identify Stop target; reject
- Expected evidence: Input/expected-display pairs, semantic parity checklist and untested-assistive-tech matrix
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: User-tested accessibility, terminal width calculation, grapheme coverage or display-engine correctness
- Blocker: No runtime attempt authorized; independent review pending

## F12 — Accounting and hidden helper effects

- Status: UNEXECUTED
- Dispositions: D15, D18
- Inputs: Synthetic events: attach, status, deterministic command, optional explicit model helper; Counters with source, time window and values present/absent; Source helper API description; no actual model request
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Classify each operation effect and whether helper inference is independently authorized; Keep unavailable token/debit/cost values null with reasons; Separate mod computation, provider use and external process/network cost
- Independent oracle: No mandatory helper on deterministic view path; no missing meter becomes zero; tokens and subscription debit are distinct Source: D-031 and committed performance/accounting requirements
- Useful positive control: Authorized optional helper is disclosed as distinct and metered only to available evidence
- Negative control: Attach secretly adds inference, or unavailable debit becomes zero savings; reject
- Expected evidence: Effect/accounting worksheet, source-bound counter states and no-savings conclusion
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Actual spend, quota debit, performance or savings
- Blocker: No runtime attempt authorized; independent review pending

## F13 — Adapter removal and native continuity

- Status: UNEXECUTED
- Dispositions: D10, D12, D14
- Inputs: Synthetic native-to-upstream-to-native task lineage; Canonical grants/receipts/evidence independent of view state; Missing upstream adapter, absent capability and incompatible revision cases
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Check that native boot/recovery/inspection depends on no upstream module; Map each requested capability to supported, unsupported or unknown without silent fallback; Retain dirty-source/effect/evidence identity through switch proposal
- Independent oracle: Adapter is replaceable; native loop remains first-class; missing capability is explicit; no helper inference required by upstream-only workflow Source: D-018/D-024 plus R-L common graph and accepted incompatibility modes
- Useful positive control: Native inspection continues and a supported native operation stays eligible
- Negative control: Uninstalling adapter loses task truth or adds hidden inference to recreate it; reject
- Expected evidence: Dependency/continuity table, loss/refusal records and retained identifiers
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Implemented productive continuity, task quality or measured advantage
- Blocker: No runtime attempt authorized; independent review pending

## F14 — Origin and queue-receipt translation

- Status: UNEXECUTED
- Dispositions: D02, D12, D18
- Inputs: Synthetic component-origin prompt labeled as user in upstream presentation; Source receipt isDelivered=true with queue boundary only; Recursion identities: proposal origin, principal grant, action digest, delivery boundary
- Prerequisites: Independent verifier other than author; Exact pinned report/source metadata and local authority baseline; Synthetic data only; no real credential or private content; Read-only public retrieval available if source recheck needed; Do not install/import/run mods, upstream binaries or repository scripts
- Procedure: Translate source queue acknowledgement to queued status only; Retain component origin even if upstream text omits sender sentence; Require separate evidence for consumption/adoption/settlement and reject duplicate changed action
- Independent oracle: Source field spelling never expands evidence boundary or grants; presentation cannot authenticate principal intent Source: R-J receipt contract, R-L admission contract and D-022
- Useful positive control: A queue receipt remains useful progress while consumed state is unknown
- Negative control: Queue receipt becomes consumed/settled or synthetic as-user text grants authority; reject
- Expected evidence: Origin/cause mapping, source receipt boundary and distinct consumption/settlement fields
- Stop conditions: Stop this check at missing source bytes, revision ambiguity, authority ambiguity or unavailable oracle; record UNKNOWN, not PASS; Reject the specific disposition rationale when its negative control is accepted or permitted control is rejected without an explicit constraint; Do not cross into binary execution, model/provider calls, accounts, installs, credentials or live-host effects
- Non-proof: Actual delivery, identity authentication, authorization or message consumption
- Blocker: No runtime attempt authorized; independent review pending
