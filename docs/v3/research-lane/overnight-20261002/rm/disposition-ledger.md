# R-M full disposition ledger

Every row is an inferred Recursion recommendation, conditional on accepted invariants. No code port is cleared. Provider-free checks are UNEXECUTED and assess rationale, not runtime qualification.

## D01 — Typed event observations: adopt

- Scope: Design prior art only; read-only projection subscriptions
- Evidence: RM-S04
- Competing option: Query snapshots with explicit observers and no mutable middleware chain
- Decisive falsifier: In a synthetic trace, swapping two observers changes an admitted effect, current authority or canonical state
- Reversal/narrowing condition: Prefer snapshot/query observers if ordering cannot remain presentation-only without central middleware complexity
- Check: F03: inspect typed event/result separation and reorder observation traces
- Non-proof: Throughput, stable event delivery, or the cheapest observation mechanism

## D02 — Observe/rewrite/answer distinction: adopt

- Scope: Typed outcomes; rewriting is a proposal subject to fresh admission
- Evidence: RM-S04, RM-S03
- Competing option: Separate transform and command handlers without generic continuation interception
- Decisive falsifier: A changed action inherits approval for original arguments, or a synthetic answer is recorded as an external-effect receipt
- Reversal/narrowing condition: Drop generic interception if separate handlers preserve meaning with fewer ambiguous paths
- Check: F03/F04: original-versus-rewritten action and synthetic-answer truth tables
- Non-proof: Permission enforcement by the upstream host or semantic equivalence for every event

## D03 — Declarative panes and above-prompt contributions: adopt

- Scope: Candidate bounded presentation over common projections, not renderer choice
- Evidence: RM-S06
- Competing option: Fixed built-in views plus external read-only projection clients
- Decisive falsifier: A tree callback writes canonical state, changes a grant, or hides required scope/Stop/question information
- Reversal/narrowing condition: Use the fixed-view competitor where contributions cannot preserve shared semantics and accessible fallback
- Check: F04/F09/F11: inspect contribution contract and paired visual/text records
- Non-proof: Non-flicker behavior, human comprehension, toolkit fitness or accessibility

## D04 — Reactive redraw-on-subscription: adopt

- Scope: Presentation invalidation may coalesce; authoritative records may not
- Evidence: RM-S06
- Competing option: Bounded polling of versioned snapshots
- Decisive falsifier: A skipped intermediate update erases revocation, receipt, replay-gap marker or unresolved question
- Reversal/narrowing condition: Prefer polling if bounded subscription disposal cannot be shown without leaked work
- Check: F08/F09: compare durable-event history to coalesced frame proposals
- Non-proof: Measured idle cost, frame latency or delivered-notification completeness

## D05 — Inspectable plugin packaging and identity: adopt

- Scope: Manifest/version/digest/dependency concepts only; no format chosen
- Evidence: RM-S02, RM-S23
- Competing option: Capabilities built natively with separately declared contribution manifests
- Decisive falsifier: Listing an installed-disabled contribution imports code or starts a dependency
- Reversal/narrowing condition: Prefer native declarations if package enumeration cannot remain inert and inspectable
- Check: F06: zero-effect static phase matrix for inventory, admission and activation
- Non-proof: Universal plugin import, license grant, installation safety or zero inventory cost

## D06 — Static effect inventory before activation: adopt

- Scope: Comparison candidate; inventory evidence never implies enforcement
- Evidence: RM-S02, RM-S07
- Competing option: Manual manifest/capability review plus independent mediation at every effect
- Decisive falsifier: An indirect or imported side effect is absent from the inventory and that omission is accepted as authorization
- Reversal/narrowing condition: Keep inventory informational only if completeness cannot be established; broker enforcement still required
- Check: F02/F06: inspect graph and intentionally omitted callback/import effect
- Non-proof: Static analyzer completeness, sandboxing or safe execution

## D07 — In-session hot reload as production recovery: avoid

- Scope: Avoid unreviewed active-code replacement; watch only disposable development acceleration
- Evidence: RM-S02, RM-S06
- Conforming candidate: Disable in-session reload and use immutable process replacement with drain/fence and state revalidation
- Competing option: Digest-bound staged activation at a declared boundary with old-epoch refusal
- Negative control (avoided behavior): In-session hot reload as production recovery
- Comparative falsifier: On identical required traces, one remedy cannot preserve required authority, lifecycle or evidence semantics while the other can; both still face the original decisive falsifier
- Decisive falsifier: Candidate reload leaves an old timer/callback active, overwrites persisted truth from defaults, or resumes effects without revalidation
- Reversal/narrowing condition: Narrow to an admitted development-only loop after revision fencing and cleanup receipts are specified; never make it canonical recovery
- Check: F05/F08: reload/revocation/clear truth tables
- Non-proof: Actual cleanup, recovery durability or production safety

## D08 — Same-user unsandboxed extension execution: avoid

- Scope: Never claim this supplies D-029 containment
- Evidence: RM-S01, RM-S22
- Conforming candidate: Operator-provisioned isolated OS workers with mediated capability-scoped execution
- Competing option: Independently qualified restricted runtime under the same operator-provisioned D-029 direct/induced-flow boundary
- Negative control (avoided behavior): Same-user unsandboxed extension execution
- Comparative falsifier: On identical required traces, one remedy cannot preserve required authority, lifecycle or evidence semantics while the other can; both still face the original decisive falsifier
- Decisive falsifier: Synthetic credential-domain data can leave through file read, environment, tool/process output or network without the independent boundary rejecting it
- Reversal/narrowing condition: Reconsider only a different confined candidate whose complete effect graph respects D-029; not the original full-access design
- Check: F07: enumerate direct and indirect egress graph with synthetic secrets only
- Non-proof: Real OS isolation, complete exfiltration resistance, malicious-host safety or policy compliance

## D09 — Guard middleware as permission authority: avoid

- Scope: A guard may advise/refuse within its scope; it cannot replace admission
- Evidence: RM-S04, RM-S07, RM-S11, RM-S34
- Conforming candidate: Centralized non-overridable sink admission gate using current grants
- Competing option: Receiver-recomputed current-grant gate at the actual effect boundary with identical authority and refusal semantics
- Negative control (avoided behavior): Guard middleware as permission authority
- Comparative falsifier: On identical required traces, one remedy cannot preserve required authority, lifecycle or evidence semantics while the other can; both still face the original decisive falsifier
- Decisive falsifier: Handler error, reordering, injected allow or absent guard permits a previously denied operation
- Reversal/narrowing condition: An independently mediated candidate can be considered if its guard disappears without weakening admission; this preserves the exclusion
- Check: F04: timeout, exception, short-circuit and unavailable-policy cases plus permitted control
- Non-proof: Host permission behavior, exhaustive race freedom or safety of all guard implementations

## D10 — Unstable vendor API as native dependency: avoid

- Scope: Watch replaceable exact-build adapters; no core dependency
- Evidence: RM-S09, RM-S10, RM-S03
- Conforming candidate: Bounded exact-build external adapter removable without native boot/recovery dependency
- Competing option: Native command/query contribution seam with optional documented host adapter
- Negative control (avoided behavior): Unstable vendor API as native dependency
- Comparative falsifier: On identical required traces, one remedy cannot preserve required authority, lifecycle or evidence semantics while the other can; both still face the original decisive falsifier
- Decisive falsifier: Native boot/recovery needs a Claude module, or an unknown schema is silently accepted as compatible
- Reversal/narrowing condition: Reconsider only the adapter-specific dependency after version evidence and explicit losses; a stable publisher contract alone cannot select the core mechanism
- Check: F01/F02/F13: old/new schema mismatch and adapter-removal checklist
- Non-proof: Future compatibility, portability, vendor support, route qualification or entitlement

## D11 — Hook deny/abort/close as Stop settlement: avoid

- Scope: Keep Aggressive/Full/Lazy and checkpoint/interrupt/drain distinct
- Evidence: RM-S04, RM-S05
- Conforming candidate: Eager indexed canonical fence and owned-process/external-effect receipts
- Competing option: Receiver generation-gated admission with the same bounded ownership reconciliation and D-022 receipts
- Negative control (avoided behavior): Hook deny/abort/close as Stop settlement
- Comparative falsifier: On identical required traces, one remedy cannot preserve required authority, lifecycle or evidence semantics while the other can; both still face the original decisive falsifier
- Decisive falsifier: Closed pane or interrupted hook produces Full=settled while a child, relauncher, remote node or external effect remains unresolved
- Reversal/narrowing condition: A separately qualified adapter may report a bounded interruption observation; it still cannot declare rollback
- Check: F08: owned/unowned/remote/uncertain trace worksheet
- Non-proof: Physical process termination, remote settlement or external rollback

## D12 — Second admission path through callbacks or commands: avoid

- Scope: All view/CLI/tool controls compile into the same schema and gate
- Evidence: RM-S05, RM-S06
- Conforming candidate: Shared generated command compiler routing all controls to common admission
- Competing option: Independently authored command encoders using the same common gate, schema, identity and semantic goldens
- Negative control (avoided behavior): Second admission path through callbacks or commands
- Comparative falsifier: On identical required traces, one remedy cannot preserve required authority, lifecycle or evidence semantics while the other can; both still face the original decisive falsifier
- Decisive falsifier: UI callback executes with expired grant or old revision while the identical CLI request is rejected
- Reversal/narrowing condition: An equivalent callback becomes eligible only when it reaches the same gate with same identity/idempotency semantics
- Check: F04/F13/F14: cross-surface equivalence and duplicate/stale requests
- Non-proof: Backend enforcement, authentication or semantic parity of an untested host

## D13 — Diff helper and fixture port candidates: watch

- Scope: Potential port only after rights, closure and matched-cost gates; none cleared
- Evidence: RM-S12, RM-S30, RM-S15, RM-S40
- Competing option: Clean-room diff/view implementation preserving original bytes and R-K contracts
- Decisive falsifier: Missing reuse rights, private host dependency, meaning-changing Unicode treatment or total accepted port cost greater than native rewrite
- Reversal/narrowing condition: Move to a separately admitted port experiment only after counsel resolves rights and the same acceptance corpus is frozen
- Check: F10/F11: source/dependency/rights worksheet and Unicode representation pairs
- Non-proof: Cheaper port, licensed redistribution, binary parity or complete Unicode correctness

## D14 — Instruction-file ordering fixtures: watch

- Scope: Use behavioral questions as prior art; do not copy source or host prompt authority
- Evidence: RM-S13, RM-S39, RM-S15
- Competing option: Native context-source adapter from Recursion provenance/authority requirements
- Decisive falsifier: Port makes upstream file name or placement confer higher authority, loses source identity, or changes accepted context provenance
- Reversal/narrowing condition: Consider a narrow rights-cleared fixture port after independently specifying required ordering and source identities
- Check: F10/F13: dependency and provenance tables with conflicting instruction origins
- Non-proof: Prompt-injection resistance, host instruction equivalence or lower engineering cost

## D15 — Host-credential telemetry pipeline: avoid

- Scope: Avoid direct transplant; retain only independently specified observation requirements
- Evidence: RM-S14, RM-S38, RM-S42
- Conforming candidate: Event-linked accounting receipts with an explicitly authorized credential-independent exporter
- Competing option: Independent immutable cohort receipts with the same complete accounting, unknowns and authorized exporter
- Negative control (avoided behavior): Host-credential telemetry pipeline
- Comparative falsifier: On identical required traces, one remedy cannot preserve required authority, lifecycle or evidence semantics while the other can; both still face the original decisive falsifier
- Decisive falsifier: Exporter obtains a host credential, sends source content outside grant, or treats unavailable cost as zero
- Reversal/narrowing condition: Consider a new credential-independent exporter with explicit audience/data and complete accounting semantics; no reuse clearance implied
- Check: F07/F12: data-flow and unknown-meter classification
- Non-proof: Billing equivalence, privacy compliance or measured savings

## D16 — Linear accessible text alternative: adopt

- Scope: Existing accessibility requirement, not upstream implementation selection
- Evidence: RM-S27
- Competing option: Keyboard-first semantic CLI/text projection alongside fixed TUI views
- Decisive falsifier: Text path cannot identify target, action, scope, pending question or unresolved effect shown visually
- Reversal/narrowing condition: Use an independently designed text-first contribution where visual tree cannot preserve task equivalence
- Check: F11: paired semantic records and keyboard action worksheet
- Non-proof: Assistive-technology compatibility or human accessibility without admitted user testing

## D17 — Allowlisted terminal notification mediation: adopt

- Scope: Prior art for a distinct bounded output capability; no raw control passthrough
- Evidence: RM-S18, RM-S28
- Competing option: Semantic notification events rendered by the trusted terminal writer
- Decisive falsifier: Untrusted text emits clipboard/cursor/control sequences or a notification includes private content outside audience policy
- Reversal/narrowing condition: Prefer semantic-only notifications if byte-level allowlisting cannot preserve injection and privacy invariants
- Check: F09/F11: escaped literal controls versus permitted notification requests
- Non-proof: Terminal support, race-free writes, confidentiality or mod innovation

## D18 — Model-free inspection and controls: adopt

- Scope: Require no mandatory inference on view attach/status/deterministic controls; helper effects explicit
- Evidence: RM-S05
- Competing option: Native deterministic command/query service with no loaded extension
- Decisive falsifier: Opening a view or handling a status query silently triggers model helper, timer-driven inference or provider fallback
- Reversal/narrowing condition: Prefer direct native queries if the optional adapter cannot disclose and bound all helper effects
- Check: F06/F12/F14: phase/effect graph and nullable meter worksheet
- Non-proof: Zero total cost, subscription savings or model-free behavior of every upstream API method
