# Complete evidence and discriminating-work ledger

Source commit: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Static inspection only; no tests or harnesses executed.

117 row entries: 57 architecture edges, 33 gap rows, 27 harness/product rows. Every next test is a proposal requiring its own admitted execution scope. Conforming rivals preserve the same required scope and qualification floors; rejected/unsafe comparisons remain separately visible as negative controls, not implementation choices.

## Architecture edges

### A-01 — Deterministic kernel / four-function boundary
Status: **partial_recorded_model_evidence_not_frozen**. Leverage rank 1 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:41`.
- Current evidence: FU-03 contains RKernel and RIntegrated raw TLC output; 727/727 and 38,837/34,625 generated/distinct states respectively; seven mutant receipts, five killed. M1A has inert planning/replay code.
- Smallest discriminating decision/test: First reconcile exact mutation sites and independent RefState/replay; for M25/M31 provide witnessed reachable nonequivalence or an explicit bounded unreachable/equivalent classification, without weakening unrelated guards. Then classify all 36 rows and publish byte vectors plus two independent implementations.
- Conforming rival: Independently authored event-equation reference semantics versus an independently authored executable reference-state interpreter, with separate replay/projection checks in both arms. Both retain the identical four-function boundary, full integrated bounds, mandatory 36-row classifications, independent monitors, literal byte corpus, two implementations and exact-candidate verification; compare oracle sensitivity and maintenance burden without substituting away a mandatory gate.
- Negative controls, not eligible rivals: Shared reducer/serializer defects in candidate and oracle; baseline-only or reduced-bound PASS promoted to kernel freeze.
- Previous comparison preserved: The same four functions checked by an independent reference semantics, with deliberately shared-bug controls.
- Comparison sources: ../rw/report.md (Q02); ../rp/recommendations.json (RP-R10 / RP-R13)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A reachable defective reducer or packet derivation is accepted by both subject and monitor, or implementations disagree on bytes/refusal.
- Non-proof: Reduced TLC success is neither refinement proof, full kernel coverage, live implementation nor a freeze; effective baseline history is bounded by four fresh command IDs.
- Dependencies: D-022, FU-03 accepted integrated bound
- Packet links: FU-03, R-W

### A-02 — Event log / canonical writer / atomicity
Status: **specified_and_partially_modelled_unqualified**. Leverage rank 10 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:42`.
- Current evidence: STATE/DS-21/FU-02 specify fenced atomic writing; FU-03 symbolic append is single-event; FU-04 has namespace observations but no durable canonical writer.
- Smallest discriminating decision/test: One command-ID retry at each commit cut, with stale-writer overlap and independently captured acknowledgment, must replay to exactly one accepted state.
- Competitor/control: Segmented JSONL+CAS versus SQLite WAL+CAS under the same semantic oracle, without choosing either.
- Falsifier: Two epochs commit, acknowledged canonical state is lost, or duplicate retry changes state.
- Non-proof: Atomic rename, symbolic append and an ACK are not crash durability or writer authorization.
- Dependencies: A-01, A-05, A-51
- Packet links: FU-02, FU-04, R-X

### A-03 — Canonical bytes / digest
Status: **covered_by_design_byte_conformance_open**. Leverage rank 4 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:43`.
- Current evidence: DS-13/18/21/23 prescribe restricted I-JSON+JCS production bytes; FU-03 calls for deterministic-CBOR RCV1 test interchange; they are different layers.
- Smallest discriminating decision/test: A tiny hostile corpus for duplicate keys before object collapse, negative zero, non-finite numbers, Unicode and key ordering must yield identical bytes or typed refusal in two independent stacks.
- Conforming rival: Independently hand-authored byte/refusal goldens plus differential encoder checks versus independently authored metamorphic/generated cases checked against a separately retained literal oracle. Both use the same accepted canonical-byte profile and all mandatory literal FU-03 vectors; generated coverage supplements rather than replaces those vectors or independent implementations.
- Negative controls, not eligible rivals: Intentionally permissive parsing that drops duplicate keys or normalizes forbidden input.
- Previous comparison preserved: A separately authored reference encoder/decoder; intentionally permissive parsing is the negative control.
- Comparison sources: ../rl/recommendation-register.json (C08); ../rp/recommendations.json (RP-R12)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: One accepted input canonicalizes differently or a duplicate key is silently discarded.
- Non-proof: A digest identifies/binds bytes; it does not authenticate origin or grant authority. CBOR test vectors do not select production wire encoding.
- Dependencies: A-01, G-09
- Packet links: FU-03, FU-01

### A-04 — Grants / capability lattice
Status: **authority_contract_specified_implementation_unqualified**. Leverage rank 5 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:45`.
- Current evidence: DS-02/04/13 and R-A/R-B draft reconciliation keep grants, provenance and trust separate; Full Access is a typed vector, not ambient permission.
- Smallest discriminating decision/test: Evaluate one deny at each capability dimension and an attenuated child grant against the same effect at admission and immediately before commit.
- Conforming rival: Central typed meet compilation with authenticated opaque receiver references versus authenticated grant tokens with independent typed receiver checks and a shared reservation ledger. Both enforce the same per-dimension parent containment, current revocation, deny preservation and sibling budget conservation; neither changes accepted Full Access scope.
- Negative controls, not eligible rivals: Ambient process authority or boolean Full Access used instead of typed effect authority.
- Previous comparison preserved: Explicit capability-intersection table versus ambient process authority/boolean Full Access.
- Comparison sources: ../ru/recommendations.json (RU-R01)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A delegated grant expands scope, or revocation after planning still permits the effect.
- Non-proof: Schema validation, signature or conversation membership cannot grant authority.
- Dependencies: A-03, A-05, A-08, D-021, D-029
- Packet links: R-A, R-E, R-P, R-U

### A-05 — Revocation / fencing epoch
Status: **receiver_fence_required_not_qualified**. Leverage rank 3 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:46`.
- Current evidence: DS-01/05/20 require monotonic receiver fencing; FU-03 has lease fields but no effect receiver; FU-04 PF13 demonstrates a lock directory, not stale-epoch rejection. Older IPR-007 records finite recipient-fence/consultation vectors (45,024 schedules and 16 deliberately broken guard variants), explicitly without aggregate/broker refinement or product integration.
- Smallest discriminating decision/test: Deliver one stale operation after authority epoch advancement directly to the irreversible sink; retain the rejection receipt and an unfenced negative control.
- Conforming rival: Online current-state checks at the receiver versus durable pushed fence floors with an acknowledged installation barrier. Both enforce the same monotonic epoch immediately at the protected effect boundary and preserve Stop scope, stale rejection and unavailable-receiver uncertainty.
- Negative controls, not eligible rivals: Controller-only paused flag; lock-file presence or leader liveness treated as a receiver fence.
- Previous comparison preserved: Receiver-side fence versus controller-only paused flag or lock-file presence.
- Comparison sources: ../rx/recommendations.json (RX-R04); ../re/report.md (R07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Old epoch mutates state or settles a new execution.
- Non-proof: Unique leader, dead PID and observed lock exclusion do not prove sink fencing.
- Dependencies: A-02, A-04, D-020, D-022
- Packet links: FU-03, FU-05, R-X, R-E

### A-06 — Pause / stop / quiescence
Status: **owner_vocabulary_closed_behavior_unqualified**. Leverage rank 12 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:47`.
- Current evidence: G-07 is closed by D-022; INTERFACE-STRATEGY defines Aggressive/Full/Lazy and checkpoint/interrupt/drain. FU-03 uses paused boolean, so complete mapping remains absent.
- Smallest discriminating decision/test: One table maps every mode to admission, local descendants, remote receipts and uncertain effects; run a bounded synthetic stop at before-dispatch/after-dispatch cuts when authorized.
- Conforming rival: Eager indexed schedule reaping plus receiver fences versus generation-fenced due-time rejection with bounded registry cleanup. Both implement exactly the accepted D-022 vocabulary, selected scope/boundary and independent per-member receiver observations; compare bounded control/resource cost only after semantic equality.
- Negative controls, not eligible rivals: Divergent configuration/model/broker meanings for the same Stop label.
- Previous comparison preserved: The accepted vocabulary rendered consistently in config, formal model and broker versus divergent surface meanings.
- Comparison sources: ../rr/recommendations.json (RR-R06)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: One Stop label permits incompatible behavior across surfaces or reports external rollback from interruption.
- Non-proof: Closed vocabulary is not quiescence, mode completeness or kill-tree evidence.
- Dependencies: A-04, A-05, A-08, A-18, D-022
- Packet links: FU-03, FU-05, R-J, R-K, R-L

### A-07 — Quarantine / ambiguity / emergency stop
Status: **partial_research_ownership_gap**. Leverage rank 31 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:48`.
- Current evidence: Original edge is a gap; DS-02/08 discuss ambiguity, and R-P/R-U/R-X intersect it. Actual R-Y is workspace, not quarantine. No single accepted ambiguity transition contract is shown.
- Smallest discriminating decision/test: Specify one uncertain-effect transition with exact authority to quarantine, inspect, reconcile and resume; show it cannot auto-convert unknown to success.
- Conforming rival: Per-object bounded quarantine with typed refusal/ambiguity versus a per-route circuit breaker with bounded evidence retention. Both preserve unresolved effects, independently authenticated Stop/recovery, exact current authority and the required useful task; neither silently collapses unknown to success.
- Negative controls, not eligible rivals: Universal paused/error flag without independent effect and recovery state.
- Previous comparison preserved: Explicit uncertainty-preserving state machine versus a universal paused/error flag.
- Comparison sources: ../rp/recommendations.json (RP-R07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A timeout becomes no-effect or automatic retry before reconciliation.
- Non-proof: A document mentioning emergency stop is not an end-to-end emergency path.
- Dependencies: A-04, A-05, A-06, A-38
- Packet links: R-P, R-U, R-X, FU-03

### A-08 — Per-adapter effect fencing
Status: **per_adapter_effect_fencing_open**. Leverage rank 7 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:49`.
- Current evidence: G-17 remains open; source contracts demand receiver-side fencing, but no qualified adapter irreversible-boundary receipt is supplied.
- Smallest discriminating decision/test: For Codex-first adapter contract, identify each supported effect sink and make one late revocation refuse an effect at that sink; downgrade unsupported sinks explicitly.
- Conforming rival: Atomic sink epoch-and-effect transaction versus a trusted serialized actuator checking the same current epoch and retaining explicit external-effect ambiguity. Both must mediate every protected sink in the same declared adapter profile; an external system lacking the required enforcement is unsupported/unknown, not silently advertised as equally fenced.
- Negative controls, not eligible rivals: Best-effort upstream interruption presented as irreversible-boundary fencing.
- Previous comparison preserved: Adapter with a genuine sink fence versus best-effort upstream interruption.
- Comparison sources: ../rx/recommendations.json (RX-R08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Any route claims strong fence while a stale granted operation still commits.
- Non-proof: TLC model, process termination and upstream cancel ACK do not establish remote effect prevention.
- Dependencies: A-04, A-05, A-18, A-33, D-023
- Packet links: FU-05, R-E, R-F, R-X

### A-09 — Head / ARM / assistant identity
Status: **identity_design_covered_runtime_open**. Leverage rank 40 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:51`.
- Current evidence: EXECUTIVES/PRODUCT/DS-15 define actors and lineage; D-017 retires repository Hermes supervision, while product-level Head/ARM concepts remain bounded user-authorized roles.
- Smallest discriminating decision/test: Change a route/session and reconnect a view while preserving actor, task, lease and authority identities; reject an answer for an expired waiter.
- Conforming rival: Central canonical stable-actor registry versus immutable segment-local identities injectively bound to the same canonical actor/operation identities by authenticated manifests. Both retain identical actor/task/lease identity, exact accepted intent and authority across route/session/recovery boundaries; segment identity never renews permission.
- Negative controls, not eligible rivals: Session ID or UI name treated as durable actor identity or authority.
- Previous comparison preserved: Stable actor/operation identities versus session-ID-as-identity.
- Comparison sources: ../rv/recommendations.json (V-R09); ../rl/recommendation-register.json (C04)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Switching model creates authority or loses accepted directive provenance.
- Non-proof: A UI name or transcript does not prove durable identity or authorize an executive.
- Dependencies: A-02, A-04, A-10
- Packet links: R-J, R-L, R-Q

### A-10 — Leases / epochs / forks
Status: **lease_and_fork_contract_partial**. Leverage rank 23 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:52`.
- Current evidence: DS-15 and interface strategy describe bounded step leases and fork reservation split; no demonstrated canonical dirty-source fork or double-spend prevention. R-X is fabric, not a dedicated forks lane.
- Smallest discriminating decision/test: Two concurrent children contend for one step lease and fork one unfinished dirty tree with reservations; prove no duplicate authority or overwritten source.
- Conforming rival: A child workspace with explicit fork lineage and new binding versus a new materialization inside the existing workspace with explicit fork lineage and new binding. Both preserve the same immutable dirty-source closure, original version, newly admitted lease and nonduplicated reservation split; neither copies live authority.
- Negative controls, not eligible rivals: Copy-session/copy-working-directory used as source, lease and budget continuity proof.
- Previous comparison preserved: Single lease-holder plus immutable source snapshot versus copy-session/copy-working-directory.
- Comparison sources: ../ry/recommendations.json (Y-R06 / Y-R16)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Both children spend the same reservation or one fork loses uncommitted source.
- Non-proof: Git branch creation alone does not preserve working-tree state, external effects or budgets.
- Dependencies: A-02, A-04, A-05, A-46, A-54
- Packet links: R-X, R-Y, R-J

### A-11 — Worker lifecycle / fleet
Status: **prompt_and_historical_procedure_only_runtime_open**. Leverage rank 53 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:53`.
- Current evidence: ARCHITECTURE-COVERAGE cites DS-29, but this snapshot has the DS-29 prompt and no corresponding returned lane file under research-lane. CONSTRUCTION-RUNBOOK is historical proposed campaign procedure, not current product-worker qualification or authorization.
- Smallest discriminating decision/test: A bounded synthetic worker transitions launch/admit/run/lose/reconcile/retire with unique epoch and no post-retirement relaunch.
- Conforming rival: Bounded task-scoped workers launched on demand versus a bounded prestarted inert worker pool admitted separately to each task. Both retain identical task ownership, grant/epoch checks, explicit lifecycle and resource bounds, no idle inference and no standing executive; pool availability never creates work authority.
- Negative controls, not eligible rivals: Standing fleet supervisor or reused historical campaign authority.
- Previous comparison preserved: Explicit task-scoped lifecycle versus a standing fleet supervisor.
- Comparison sources: ../rr/recommendations.json (RR-R04 / RR-R05); ../rf/report.md (delegation and admission contract)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Orphan work continues outside owned scope, or worker self-report becomes acceptance.
- Non-proof: Historical campaign throughput does not qualify the v3 product worker lifecycle.
- Dependencies: A-05, A-16, A-18, A-49
- Packet links: R-F, R-R, R-X

### A-12 — Store / persistence faults
Status: **store_choice_open_crash_evidence_insufficient**. Leverage rank 11 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:55`.
- Current evidence: G-02/FU-02 specify crash/replay comparison; FU-04 PF06 observations cover namespace behavior, not D-028 VM-reset durability.
- Smallest discriminating decision/test: Run the same smallest acknowledged-write/reset/replay trace on both store candidates with byte-identical expected state after authorized disposable-target admission.
- Competitor/control: Segmented JSONL+CAS versus SQLite WAL+CAS; secondary challengers only if preregistered.
- Falsifier: Any acknowledged generation is unrecoverable, replay diverges or old writer is accepted.
- Non-proof: Store documentation and clean shutdown do not establish target-profile durability.
- Dependencies: A-01, A-03, A-05, A-51
- Packet links: FU-02, FU-04

### A-13 — Snapshot / export / migration / rollback
Status: **snapshot_and_forward_recovery_specified_unqualified**. Leverage rank 41 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:56`.
- Current evidence: DS-21/25/05 and M1C define migration/recovery evidence; D-017 makes mandatory v2 migration historical. Snapshot digest and engine mechanism remain open.
- Smallest discriminating decision/test: Restore one exact candidate snapshot with its event tail; interrupt forward migration and use a reverse reader without erasing newest accepted work.
- Conforming rival: Verified versioned snapshot plus complete canonical suffix replay versus full replay from retained canonical genesis/closure without snapshot acceleration. Both retain identical newest committed state, exact source/profile bindings, compatibility rules and forward-only external-effect reconciliation; compare recovery cost without dropping obligations.
- Negative controls, not eligible rivals: Copying live store files without a coherent closure; relabeling external-effect rollback.
- Previous comparison preserved: Versioned snapshot plus verified tail replay versus copying live database files or rollback of external effects.
- Comparison sources: ../ry/recommendations.json (Y-R02 / Y-R15); ../rv/recommendations.json (V-R07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Restored state loses a committed event or rolls an already accepted effect into no-effect.
- Non-proof: A backup file existing is not a restore receipt, and greenfield v3 needs no v2 migration dependency.
- Dependencies: A-02, A-12, A-38
- Packet links: FU-02, R-V

### A-14 — DR / restore matrix
Status: **dr_matrix_open**. Leverage rank 42 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:57`.
- Current evidence: DS-25 six update modes by four outcomes and restore trial are still unqualified; D-028 bounds power loss to abrupt VM reset.
- Smallest discriminating decision/test: Choose one representative failure cut and distinguish executable compatibility, state replay, task resume and external settlement separately, then expand all mandatory cells.
- Conforming rival: Reverified compatible rollback executable admitted under a fresh grant epoch versus forward recovery to an independently admitted replacement executable. Both preserve newest canonical work, the same six update modes/four outcome predicates and unresolved external effects; rollback never revives revoked code or old authority.
- Negative controls, not eligible rivals: Full-directory rollback that loses newest state or claims to undo settled external effects.
- Previous comparison preserved: Verified compatible executable with newest state versus full directory rollback.
- Comparison sources: ../ru/recommendations.json (RU-R13)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: One recovered badge masks lost state, unresolved effects or an incompatible reader.
- Non-proof: One restore trial does not fill all 24 outcome cells or establish numeric RPO/RTO.
- Dependencies: A-12, A-13, A-47, D-028
- Packet links: FU-02, FU-04, R-O

### A-15 — Admission / capacity / review debt
Status: **admission_researched_uncalibrated**. Leverage rank 37 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:59`.
- Current evidence: DS-06 min-credit controller includes machine/provider/grant/review/human credits; coordinator-small and review throughput have no local calibration.
- Smallest discriminating decision/test: Replay one burst where review queue saturates before CPU, comparing fixed cap and adaptive admission at equal verified completions.
- Competitor/control: A tuned fixed concurrency cap versus adaptive min-credit controller.
- Falsifier: Adaptive policy raises false-green/review age or violates a hard resource ceiling.
- Non-proof: A formula or queue estimate does not validate Little’s Law, service times or useful concurrency.
- Dependencies: A-04, A-46, A-47, A-49, A-50
- Packet links: R-O, R-S, R-W

### A-16 — Scheduler / daemon / continuous op
Status: **scheduler_recovery_open**. Leverage rank 48 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:60`.
- Current evidence: DS-30 supplies state/resume proposals; DS-29 is an issued construction-fleet prompt without a located return in this snapshot. D-025 permits optional bounded continuing research, not a standing repository executive.
- Smallest discriminating decision/test: Persist one due action, crash before/after dispatch and restart; distinguish missed work, duplicate effect and approved reschedule.
- Conforming rival: Durable wake-intent dispatcher with fresh admission versus demand-activated one-shot validation from canonical due state without long-lived dispatch claims. Both implement the same accepted schedule/cadence, durable due state, restart deduplication, budgets, Stop and current authority; no scheduling capability is removed.
- Negative controls, not eligible rivals: Polling chat loop or volatile in-memory timer as the sole durable scheduler.
- Previous comparison preserved: Durable task-scoped scheduler versus polling chat loop or in-memory timer.
- Comparison sources: ../rr/recommendations.json (RR-R04 / RR-R05)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Restart duplicates an effect, renews authority or starts idle inference in lean profiles.
- Non-proof: A running daemon and a recurring prompt do not establish durable exact-once admission.
- Dependencies: A-02, A-05, A-38, D-025
- Packet links: R-R, R-X

### A-17 — IPC / broker / terminal wire
Status: **broker_contract_conditionally_specified_unqualified**. Leverage rank 9 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:62`.
- Current evidence: G-05/FU-05 cover four freeze blockers; M1B provides inert execution contracts. No complete native chaos matrix is accepted.
- Smallest discriminating decision/test: Resolve version negotiation, snapshot materialization, cursor rollover and ACK-release semantics in one synthetic reconnect trace with a slow observer.
- Conforming rival: Bounded pull pages and consistent-cut snapshots plus notifications versus bounded credited push with replay/reset. Both use the same command receipts, canonical order, negotiated version, cursor/snapshot/ACK semantics, finite resource bounds and independently preserved control path.
- Negative controls, not eligible rivals: Terminal scraping or unbounded mirrored streams used as the authoritative broker contract.
- Previous comparison preserved: Explicit bounded command/event protocol versus terminal scraping or unbounded stream mirroring.
- Comparison sources: ../rv/recommendations.json (V-R06); ../rl/recommendation-register.json (C04 / C11)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: ACK releases causal evidence prematurely, gaps silently lose records or a slow view blocks Stop/writer.
- Non-proof: A JSON transport, successful handshake or receipt-schema PASS is not broker freeze.
- Dependencies: A-03, A-05, A-18, A-51
- Packet links: FU-05, R-F, R-K, R-L

### A-18 — Process containment / termination
Status: **bounded_os_observations_no_containment_qualification**. Leverage rank 33 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:63`.
- Current evidence: FU-04 records WSL process-group escape/reconciliation, orphan/signal/PID observations; its Windows PF04 is an anonymous pipe. Separately, older IPR-001 records one Windows build creation-time Job test and a post-creation association orphan hazard. Neither establishes hostile-escape, inside-CreateProcess crash, ConPTY or full native profile qualification.
- Smallest discriminating decision/test: Demonstrate admitted child containment before execution and whole owned-scope teardown using native profile witnesses; escaped descendants must prevent settled.
- Conforming rival: Birth containment plus independent native scope/identity reconciliation versus a qualified gated launch supervisor plus independent launch and ownership inventory. Both must establish equally complete rooted ownership and effect gating before work on the same exact Windows/Linux profile; PID-only cleanup cannot qualify the second arm.
- Negative controls, not eligible rivals: Process-group/PID-only cleanup presented as complete containment or Full Stop.
- Previous comparison preserved: Windows Job/native Linux cgroup boundary versus process group/PID-only cleanup.
- Comparison sources: ../ru/recommendations.json (RU-R07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: One owned descendant escapes, unrelated process is affected or missing notification implies dead.
- Non-proof: A killed parent/process group, cleanup script or WSL pass does not certify all descendants on Windows/Linux.
- Dependencies: A-05, A-07, A-51
- Packet links: FU-04, FU-05, R-U

### A-19 — Terminal runtime / detachable views
Status: **terminal_semantics_covered_implementation_unqualified**. Leverage rank 34 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:65`.
- Current evidence: TERMINAL-RUNTIME/INTERFACE-STRATEGY baseline ten controls and three Stops; FU-04 partial teardown observations are not detachable terminal runtime evidence.
- Smallest discriminating decision/test: Detach/reattach two views around one queued input and one approval while dropping an event; prove bounded replay and no actor-lifetime change.
- Conforming rival: Integrated broker-managed detachable thin views versus external multiplexer-managed thin views over the same broker. Both keep actor/process ownership outside views, preserve exact control/replay semantics and bounded Stop responsiveness, and do no work merely on attach.
- Negative controls, not eligible rivals: A view-owned process lifecycle or detach that implicitly cancels authorized work.
- Previous comparison preserved: Daemon-owned terminal with attachable projections versus view-owned process.
- Comparison sources: ../rj/recommendations.json (RJ-R04)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Closing the last view kills authorized work or attachment silently launches inference.
- Non-proof: Terminal screenshot, raw PTY transcript or pipe exit does not prove durable interaction controls.
- Dependencies: A-06, A-17, A-18, A-21
- Packet links: R-J, R-K, R-L

### A-20 — Multiplexer / transformative TUI
Status: **issued_research_packets_not_qualified**. Leverage rank 38 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:66`.
- Current evidence: R-J/R-K briefs exist for multi-agent terminal and transformative TUI; issuing them provides scope, not implemented experience.
- Smallest discriminating decision/test: Prototype a provider-free slow-stream/20-view scenario where keyboard Stop and focused steering remain bounded and receipts visible.
- Competitor/control: Thin adapter over a mature multiplexer versus bespoke renderer, compared without selecting either.
- Falsifier: Multiplexing increases control latency, redraw cost or wrong-target input beyond accepted limits.
- Non-proof: A visual layout or one responsive pane is not scheduling, containment or UX benefit.
- Dependencies: A-17, A-19, A-21, A-23, A-44
- Packet links: R-J, R-K, R-M

### A-21 — CLI / TUI / GUI command-query
Status: **common_interface_design_covered_runtime_open**. Leverage rank 20 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:68`.
- Current evidence: INTERFACE-STRATEGY has one command/query object graph and typed receipts; Current explicit direction sequences CLI/TUI construction before GUI; any impact on the D-019 first-release GUI obligation remains an explicit Owner clarification.
- Smallest discriminating decision/test: Send the same synthetic command through CLI and TUI adapters and compare receipt/state; sketch later GUI using the same schema, with no second writable settings store.
- Conforming rival: One semantic catalog with generated surface codecs versus independently implemented surface codecs checked against the same semantic corpus. Both preserve one canonical command/query meaning, admission path, configuration revision and receipt model; independent implementation never means independent authority.
- Negative controls, not eligible rivals: Independent frontend state machines with divergent Stop/configuration meanings or writable policy stores.
- Previous comparison preserved: Headless shared model with thin clients versus independent frontend state machines.
- Comparison sources: ../rl/recommendation-register.json (C01)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A frontend bypasses admission or gives Stop/config a different meaning.
- Non-proof: Common labels or API shape do not establish semantic equivalence. Construction order silently removes neither GUI capability nor the D-019 first-release opt-in obligation; clarify exact release timing if it changes a gate.
- Dependencies: A-04, A-06, A-17, A-55
- Packet links: R-L, R-N

### A-22 — Projections / explain / status
Status: **projection_contract_researched_unqualified**. Leverage rank 44 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:69`.
- Current evidence: DS-26/27 and PRODUCT promise zero-model explanations; interface strategy distinguishes accepted/delivered/observed/settled.
- Smallest discriminating decision/test: Given one denied route and stale observer, reproduce the exact explanation from canonical inputs and expose projection lag/gap.
- Conforming rival: Stored typed decision certificates with independent re-derivation versus complete immutable input snapshots with query-time predicate evaluation. Both provide the same deterministic historical explanations, exact operands, denial provenance, scope and gap markers without model calls.
- Negative controls, not eligible rivals: Model-generated status narrative used as canonical explanation or authority.
- Previous comparison preserved: Deterministic causal explanation versus model-generated status narrative.
- Comparison sources: ../rv/recommendations.json (V-R01)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Explanation invents a reason, loses deny provenance or presents stale state as authoritative.
- Non-proof: A pretty dashboard or plausible prose is not a replayable explanation.
- Dependencies: A-02, A-03, A-47, A-48
- Packet links: R-V, R-L

### A-23 — Accessibility
Status: **accessibility_scoped_no_qualification**. Leverage rank 51 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:70`.
- Current evidence: Old map calls this unowned gap and wrongly assigns R-U; actual R-K covers keyboard/accessibility and R-N covers WCAG 2.2 AA for later GUI.
- Smallest discriminating decision/test: A provider-free keyboard-only and screen-reader path through target selection, exact approval, stop and recovery must remain usable with streaming/no-color modes.
- Competitor/control: Accessible linear command/list view versus spatial panes, compared on completed control tasks.
- Falsifier: Focus loss, invisible authority/status or color-only signaling prevents safe control.
- Non-proof: A framework accessibility claim or WCAG checklist is not tested task accessibility; no stack is selected.
- Dependencies: A-19, A-20, A-21
- Packet links: R-K, R-N

### A-24 — Consultation / rooms / multi-agent UX
Status: **consultation_contract_and_fixtures_unrun**. Leverage rank 39 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:72`.
- Current evidence: DS-15 F01–F24 and INTERACTION-SURFACES describe rooms, direct address and bounded step leases; R-J extends interaction research.
- Smallest discriminating decision/test: One room with two ARMs and an Owner interruption demonstrates exact target, Head awareness and one bounded coordinator lease; then matched direct-addressing comparison.
- Competitor/control: R0 direct interaction without shared-room coordination versus proposed R1 actor/authority contract.
- Falsifier: Room consensus changes accepted intent or a stale actor answer is adopted.
- Non-proof: Attributable chat exchange does not prove authority, better coordination or acceptance.
- Dependencies: A-04, A-09, A-10, A-25, A-26
- Packet links: R-J, R-L

### A-25 — HITL approvals / forwarding
Status: **hitl_pre_effect_contract_unqualified**. Leverage rank 30 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:73`.
- Current evidence: DS-32 and interface strategy specify exact-action approval, durable correlation and expiry. G-31 wording that ten controls are undefined is stale at design level.
- Smallest discriminating decision/test: Expire/revise an approval while the action waits, then deliver the old answer; execution must refuse or require current applicable authority.
- Conforming rival: Durable exact-action approval objects versus an already Owner-approved bounded policy with deterministic selectors and exact per-effect binding. Both must be eligible under the same confirmation policy, action/recipient/data scope, expiry/revision and receiver checks; where action-time approval is mandatory both obtain it.
- Negative controls, not eligible rivals: UI confirmation of an unbound prose summary; stale approval reused for changed action.
- Previous comparison preserved: Digest/revision-bound pre-effect approval versus UI confirmation of a prose summary.
- Comparison sources: ../rp/recommendations.json (RP-D06 / RP-R03)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A stale or wrong-recipient answer authorizes a changed action.
- Non-proof: Approval delivery and upstream hook invocation are not effect receipts or settlement.
- Dependencies: A-04, A-05, A-06, A-17
- Packet links: R-E, R-F, R-J, R-L

### A-26 — Compaction / cache economics
Status: **context_recovery_researched_economics_unmeasured**. Leverage rank 32 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:75`.
- Current evidence: DS-12/CONTEXT specify route capsules and one compaction owner; upstream cache is optional accelerator. No route-by-route synthetic suite or cache debit measurements.
- Smallest discriminating decision/test: Cold-rebuild one task after deleting only the synthetic upstream session, then compare authorized continuation and all-role input/accounting against direct harness.
- Competitor/control: Minimal explicit handoff/cold context versus semantic capsule plus optional cache.
- Falsifier: Intent/authority/evidence is lost, private context crosses audience or measured total burden increases for the claimed workload.
- Non-proof: A short summary, token estimate or cache-hit report does not prove continuity or savings.
- Dependencies: A-02, A-04, A-09, A-46
- Packet links: R-Q, R-T, R-F

### A-27 — Durable memory / knowledge
Status: **memory_packet_issued_contract_candidate**. Leverage rank 46 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:76`.
- Current evidence: DS-30/14/12 propose durable state roles; actual R-Q, omitted by stale final map, owns durable memory and knowledge.
- Smallest discriminating decision/test: Retrieve two contradictory, differently scoped facts across a route change; preserve source/date/authority and enforce deletion/tombstone on every derived index.
- Competitor/control: Provenance-bound structured memory versus freeform prose notes or replay-only retrieval.
- Falsifier: Stale observation overwrites accepted instruction, deletion resurrects a copy or memory grants capability.
- Non-proof: Persisted notes and successful retrieval do not prove freshness, privacy, authority or useful recall.
- Dependencies: A-02, A-26, A-36
- Packet links: R-Q, R-V

### A-28 — Routes / adapters / fan-out
Status: **nine_route_documentation_no_route_qualification**. Leverage rank 17 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:78`.
- Current evidence: R-B maps nine routes; R-F is issued; D-023 requires Codex App Server first; route descriptors must expose losses and stable/experimental split. Earlier Codex/Hermes loopback IPR fixtures provide narrow historical installed-build evidence, not a current authenticated route qualification.
- Smallest discriminating decision/test: Qualify one Codex synthetic submit/steer/question/interrupt/resume/observe cycle with correlated IDs and uncertainty; only then stress a deliberately different adapter under separate authorization.
- Competitor/control: Direct pinned harness use versus Recursion adapter at identical task/authority/accounting boundaries.
- Falsifier: Adapter claims unsupported control, loses an approval or silently substitutes route/account/billing.
- Non-proof: Headless JSON, native subagents or source-code availability is not delegation qualification or entitlement.
- Dependencies: A-04, A-06, A-17, A-33, A-46, D-023
- Packet links: R-F, R-E, R-H

### A-29 — Route legality / entitlement
Status: **counsel_gate_open**. Leverage rank 27 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:79`.
- Current evidence: R-C Q01–Q12 and R-H prepare route/tier/entity/mode questions. D-021/D-030 set preferred delegation architecture; they do not clear provider terms.
- Smallest discriminating decision/test: Complete a route-specific fact sheet distinguishing caller-of-CLI, token custody, redistribution and automation, for Lucas to submit to counsel.
- Conforming rival: Normalized per-profile counsel fact/disposition matrix versus independently complete case dossiers with indexed answers. Both cover every identical material account/entity/auth/mode/distribution variant, same required capability and counsel/technical gates; neither is legal clearance or a narrower release substitute.
- Negative controls, not eligible rivals: Excluded credential relay used as though it were an eligible delegation design; vendor-wide blanket permission.
- Previous comparison preserved: Approved native delegation operating mode versus excluded credential relay; compare exact clauses, not intent.
- Comparison sources: ../rh/report.md (Sections 2, 6 and 7)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Counsel identifies a required mode as prohibited or necessary facts remain unresolvable.
- Non-proof: Open-source license, successful login or Owner product direction is not service entitlement/legal clearance.
- Dependencies: D-021, D-027, D-030, G-32
- Packet links: R-C, R-H

### A-30 — Plugin / capability-graph contract
Status: **plugin_contract_proposed_not_ratified**. Leverage rank 18 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:81`.
- Current evidence: R-A manifest/schema and R-A/R-B reconciliation are draft candidates; PLUGINS-AND-EDITIONS retains accepted opt-in and no-effect disabled invariants.
- Smallest discriminating decision/test: Resolve two conflicting bounded metadata manifests without import, then invoke an incompatible capability and require typed attempted=false/effect=none receipt.
- Conforming rival: Shared capability/assets with per-host digest-bound realizations versus separate native per-host plugin bindings. Both implement the same accepted contribution set, authority/isolation/lifecycle obligations, explicit loss map and disabled-path inertness; no arbitrary runtime emulation is assumed.
- Negative controls, not eligible rivals: Arbitrary upstream runtime emulation claimed equivalent from metadata alone.
- Previous comparison preserved: Small explicit adapter manifests versus arbitrary upstream runtime emulation.
- Comparison sources: ../rg/report.md (Recommendation register R4)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Resolution imports code, dependency conflict is hidden or no-action performs installation/network/model work.
- Non-proof: Schema-valid metadata, signatures or broad compatibility names do not prove runtime behavior.
- Dependencies: A-03, A-04, A-31, A-55, D-019
- Packet links: R-A, R-G, R-U

### A-31 — Sandbox / isolation / supply chain
Status: **isolation_design_unselected_unqualified**. Leverage rank 26 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:82`.
- Current evidence: DS-04/18 and R-U compare process/WASI/native placements; three independent axes are provenance, trust/isolation and authority.
- Smallest discriminating decision/test: One denied filesystem/network/credential capability across candidate runtimes with malicious plugin and disabled-import tripwires; report semantic limits per OS profile.
- Competitor/control: Bounded subprocess/OS isolation versus capability runtime, without choosing either.
- Falsifier: Plugin crosses a denied boundary or disabled payload executes.
- Non-proof: A process, sandbox label, signature, SBOM or WASI use alone is not confinement.
- Dependencies: A-04, A-18, A-33, A-51
- Packet links: R-U, R-E, R-G

### A-32 — Plugin import / cross-harness reuse
Status: **portability_hypothesis_unmeasured**. Leverage rank 47 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:83`.
- Current evidence: D-033 requires validating cheap porting; R-G covers ecosystems, R-I Grok source, R-M Claude terminal modding. Zero acceptable ports remains possible.
- Smallest discriminating decision/test: Port one representative bounded plugin on paper to two harness capability maps; preregister accepted semantic losses and compare actual engineering/review cost with native rewrite in a later authorized trial.
- Competitor/control: Native rewrite or narrow adapter versus import/translation layer.
- Falsifier: No plugin meets required semantics or measured total port cost exceeds rewrite.
- Non-proof: Shared API names, source license or plugin count is not cheap semantic portability.
- Dependencies: A-29, A-30, A-31, D-019, D-033
- Packet links: R-G, R-I, R-M

### A-33 — Credential non-intermediation / launch
Status: **trusted_launch_design_required_not_proven**. Leverage rank 6 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:85`.
- Current evidence: D-029 explicitly rejects same-user CLI driving as strong non-access proof; R-E addresses operator-provisioned boundary outside Recursion-readable domain.
- Smallest discriminating decision/test: First establish exact unmodified-harness support for separating credential-facing code (C) from tool/plugin execution (T), or an equivalent enforced boundary. On each admitted synthetic profile, test direct denied reads and induced credential export through CLI tools, output and artifacts while approved credential use succeeds. Policy-only is a claim ceiling, never an automatic weaker execution mode after strong-required admission fails.
- Conforming rival: Separate credential-principal composition versus externally confined entire orchestrator/tool domain: W-A versus W-B on Windows and L-A versus constrained L-B on Linux. Both require the same exact native floors, unmodified-harness C/T compatibility, direct and induced-flow confidentiality and fail-closed strong-profile admission; policy-only is not an eligible substitute.
- Negative controls, not eligible rivals: Same-user non-reading convention; clean child environment; Job/cgroup label alone.
- Previous comparison preserved: Operator-provisioned separate security boundary versus same-user policy convention.
- Comparison sources: ../re/report.md (Recommendation register R04 / R05)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Recursion directly reads synthetic secret channels or induces export through an allowed CLI/tool/output path; an unsupported C/T boundary or silent weaker fallback invalidates the strong profile.
- Non-proof: Delegating to a logged-in CLI or blocking direct reads alone does not prove whole-domain credential non-access. Unsupported strong-required routes must refuse unless the operator separately admits a weaker mode; no real credentials were inspected.
- Dependencies: A-04, A-18, A-31, A-51, D-021, D-029
- Packet links: R-E, R-U

### A-34 — Untrusted input / prompt injection
Status: **dedicated_packet_issued_no_defense_qualification**. Leverage rank 21 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:86`.
- Current evidence: Old map says no lane and wrongly points R-W; actual R-P owns injection/untrusted-input defense across source, tool output, memory and attachments.
- Smallest discriminating decision/test: Place one malicious instruction in each untrusted ingress and require it stay data without grant or command promotion, including a benign look-alike control.
- Conforming rival: Fine-grained ingest-owned provenance envelopes versus coarse whole-context labels with independently resolved canonical authority records. Both keep control/data separation, complete effect/disclosure mediation and identical current grants; compare required fidelity, utility and overhead after all injection hard floors.
- Negative controls, not eligible rivals: Instruction-only detector, delimiters or content filter used as the authority/security boundary.
- Previous comparison preserved: Deterministic provenance/effect confinement versus instruction-only detector or content filter.
- Comparison sources: ../rp/recommendations.json (RP-R01 / RP-R02)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: An untrusted source changes recipient, effect scope, credential access or policy.
- Non-proof: High detector accuracy and model refusal examples do not prove enforceable authority boundaries.
- Dependencies: A-04, A-25, A-27, A-33, A-40
- Packet links: R-P, R-Q, R-T, R-U

### A-35 — Secrets / egress / lifecycle
Status: **secrets_egress_threat_suite_unrun**. Leverage rank 25 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:87`.
- Current evidence: DS-24 and SECURITY cover egress and credential references; D-029 supersedes any strong claim based only on same-user broker discipline.
- Smallest discriminating decision/test: Mutate recipient/compiled bytes after approval and inject a stale grant at broker dispatch; use synthetic markers to observe every egress channel.
- Conforming rival: Completely mediated mixed-data processing across all release channels versus pre-exposure separation that never combines protected data and outward-capable processing. Both retain complete mediation, exact authorized recipients/compiled effects, useful required workflow, induced C/T/output protection and current revocation; no scanner-only release claim.
- Negative controls, not eligible rivals: Application policy alone; direct file denial plus output scanner treated as complete non-access.
- Previous comparison preserved: Exact-byte/destination-bound broker versus application policy only.
- Comparison sources: ../rp/recommendations.json (RP-R06)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Secret-bearing data leaves an unapproved destination or stale broker decision survives revocation.
- Non-proof: Opaque reference or zero-model preflight is not secret isolation or legal clearance.
- Dependencies: A-04, A-05, A-29, A-33
- Packet links: R-E, R-P, R-U

### A-36 — Privacy / retention / deletion
Status: **deletion_contract_specified_unqualified**. Leverage rank 45 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:88`.
- Current evidence: DS-07/33 distinguish copy inventory, key-recovery ledger, provider residual windows and derived verified-complete. Disconnected-node destruction remains unknown.
- Smallest discriminating decision/test: Delete one synthetic item with a cache/index/export/offline spool copy; a deliberately missing copy receipt must keep completion unresolved.
- Conforming rival: Eager fine-grained lineage cleanup versus policy-bound deferred cleanup with conservative coarse lineage. Both retain the same complete copy/key inventory, restore gate, approved retention constraints, honest residual states and independently derived completion; deferred never means falsely complete.
- Negative controls, not eligible rivals: Tombstone or single-store deletion treated as complete destruction of all copies.
- Previous comparison preserved: Closed copy ledger with independent acceptance versus tombstone or single-store deletion.
- Comparison sources: ../rq/recommendations.json (C07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Completion is reported while a recoverable uncontrolled copy remains or deleted data rehydrates.
- Non-proof: Key deletion, tombstone or provider policy cannot prove destruction on lost nodes.
- Dependencies: A-02, A-27, A-35, A-49
- Packet links: R-Q, R-T, R-V

### A-37 — Canary / adversarial rerun
Status: **canary_protocol_specified_unexecuted**. Leverage rank 57 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:89`.
- Current evidence: DS-08 sealed alias-only canary is designed, not run; R-W is the actual evaluation packet, with R-P/R-U supplying attack controls.
- Smallest discriminating decision/test: A provider-free synthetic candidate with one seeded boundary defect must fail an independently held oracle before any authorized private canary.
- Conforming rival: Independently authored end-state plus causal-evidence oracle versus a separately authored executable reference-state oracle with independent black-box witnesses. Both retain identical seeded negative and positive controls, private-canary boundaries, independent custody and acceptance obligations; compare defect sensitivity before expanding any scope.
- Negative controls, not eligible rivals: Worker self-report, shared oracle defects or characterization-only PASS used as correctness acceptance.
- Previous comparison preserved: Independent authoritative oracle versus worker self-report or characterization-only pass.
- Comparison sources: ../rw/report.md (Q02); ../ru/recommendations.json (RU-R09)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Known bad write-boundary behavior is accepted or the oracle shares the subject defect.
- Non-proof: Passing synthetic controls is not live route, private-target or production qualification.
- Dependencies: A-08, A-34, A-49, A-50
- Packet links: R-W, R-P, R-U

### A-38 — Tool model / effect settlement
Status: **effect_contract_inert_evidence_exists_live_open**. Leverage rank 8 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:91`.
- Current evidence: M1B schemas/fixtures distinguish commands, effect attempts and settlement; FU-03 models simplified outbox but not actual dispatch or independent effect evidence.
- Smallest discriminating decision/test: Lose the response after an admitted synthetic effect and retry the command ID; reconcile from authoritative sink evidence without duplicating the effect.
- Conforming rival: Durable outbox with operation-query reconciliation versus synchronous durable-intent RPC with the same ambiguity/deduplication ledger. Both preserve stable operation/attempt identity, receiver evidence, current authority and outcome_unknown liability across lost responses; neither asserts arbitrary external exactly-once behavior.
- Negative controls, not eligible rivals: Transport ACK or an exactly-once slogan treated as observed/settled effect.
- Previous comparison preserved: Explicit operation/attempt/receipt/effect ledger versus transport ACK or exactly-once slogan.
- Comparison sources: ../rx/recommendations.json (RX-R09)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Lost response becomes no-effect, duplicate effect is emitted or observation becomes success without authority.
- Non-proof: Schema fixtures and ACKs do not prove external exactly-once effects.
- Dependencies: A-02, A-04, A-05, A-17
- Packet links: FU-03, FU-05, R-F

### A-39 — MCP bridge / tool bounds
Status: **mcp_bounds_partial_no_dedicated_frontier_lane**. Leverage rank 24 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:92`.
- Current evidence: DS-23 flags stdio bounds; PLUGINS describes distinct MCP generations and losses. Actual R-V is replay debugging, so old dedicated MCP assignment is wrong. R-G/R-F/FU-05 cover pieces. This overnight run additionally produced protocol-edges/report.md with ten UNEXECUTED MCP fixtures and eight public primary sources; it adds research coverage only.
- Smallest discriminating decision/test: Preregister a bounded stdio/HTTP logical-operation continuation with input-required rounds, cancellation, unknown settlement and principal isolation.
- Conforming rival: Explicit era-specific typed codec versus an SDK-centered bridge with complete canonical interception and intermediate observations. Both retain identical protocol-era/capability binding, logical-operation correlation, finite bounds, approval/authority, uncertainty and independent effect evidence; SDK autonomous retries cannot bypass admission.
- Negative controls, not eligible rivals: Generic/final-result-only protocol pass-through that hides intermediate effects, requests or retries.
- Previous comparison preserved: Narrow capability-scoped MCP bridge versus generic protocol pass-through.
- Comparison sources: ../protocol-edges/report.md (B1 versus B2)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Unbounded rounds/bytes consume budget, a pool crosses privacy domains or cancellation implies settlement.
- Non-proof: MCP compatibility and tool annotations do not establish trusted authority, semantic parity or bounded resource use.
- Dependencies: A-04, A-17, A-30, A-38
- Packet links: FU-05, R-G, R-F, R-U

### A-40 — Multimodal input / output
Status: **multimodal_packet_issued_no_ingestion_qualification**. Leverage rank 55 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:94`.
- Current evidence: Actual R-T owns multimodal/attachments; stale map labels R-Q. No demonstrated common attachment lifecycle/route loss matrix.
- Smallest discriminating decision/test: Pass one image, audio and document reference through admission, route capability refusal, derived text and replay; preserve digest, audience, units and explicit unsupported modality.
- Conforming rival: Shared artifact/derivation graph versus qualified raw pass-through with the same mandatory provenance/loss/rights manifest. Both retain original bytes/digests, modality capability, source/recipient/authority binding, privacy/deletion/accounting and explicit unsupported semantics for the same required workflow.
- Negative controls, not eligible rivals: Flatten-all-to-text without original evidence, loss or rights/recipient binding.
- Previous comparison preserved: Reference-preserving typed attachment pipeline versus flatten-everything-to-text.
- Comparison sources: ../rt/recommendations.json (RT-R01)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Unsupported modality silently degrades meaning or private derived data escapes accounting/deletion policy.
- Non-proof: Rendered preview or OCR text does not prove original evidence, rights, privacy or route support.
- Dependencies: A-26, A-34, A-35, A-36, A-46
- Packet links: R-T, R-Q, R-P

### A-41 — Goal decomposition / GoalSpec
Status: **inert_planning_slice_implemented_live_open**. Leverage rank 50 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:96`.
- Current evidence: M1A planning schema/validation/replay and literal fixtures exist; accepted GoalSpec/amendment semantics are broader than live planner qualification.
- Smallest discriminating decision/test: One proposed amendment with changed effect scope must preserve exact accepted parent intent and fail absent amendment authority under a deterministic replay oracle.
- Conforming rival: Bounded hierarchical decomposition versus a flat gated queue or single admitted coding session/scratchpad for the same task. Both retain exact accepted GoalSpec/revisions, deterministic plan/packet admission, current grants, checkpoints and independent gates; comparison changes decomposition depth, never permits self-amended authority.
- Negative controls, not eligible rivals: Self-revising planner memory used instead of accepted canonical intent.
- Previous comparison preserved: Literal plan/GoalSpec with explicit revisions versus self-revising planner memory.
- Comparison sources: ../rr/recommendations.json (RR-R01)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Worker proposal overwrites accepted intent, cyclic/unsupported plan is admitted or derived packet expands authority.
- Non-proof: Inert M1A artifacts and historical tests do not prove live reasoning quality or autonomous execution.
- Dependencies: A-01, A-03, A-04, A-10
- Packet links: FU-03, R-R

### A-42 — Long-horizon / self-scheduling
Status: **bounded_autonomy_requirement_closed_mechanism_open**. Leverage rank 49 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:97`.
- Current evidence: D-025 requires optional off-by-default research with sources, cadence, budget, stopping and promotion authority; R-R is correctly mapped.
- Smallest discriminating decision/test: One persisted research job loses its source or exhausts budget across restart; it must stop/hold without self-renewal or promotion.
- Conforming rival: Durable wake intents with fresh kernel/effect admission versus demand-activated dispatch from canonical due state without long-lived claims. Both retain the same optional off-by-default D-025 scheduling/research capability, explicit sources/cadence/budget/stops, durable recovery and separate promotion authority.
- Negative controls, not eligible rivals: Persistent self-directed executive or self-renewing research budget/permission.
- Previous comparison preserved: Explicit bounded job scheduler versus persistent self-directed executive.
- Comparison sources: ../rr/recommendations.json (RR-R04 / RR-R05)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Idle inference occurs when disabled, budget/authority renews itself or a research claim promotes itself.
- Non-proof: A recurrence schedule or continuous liveness is not productive or authorized autonomy.
- Dependencies: A-16, A-25, A-41, A-46, D-025
- Packet links: R-R, R-Q, R-S

### A-43 — Scientific research ARM
Status: **scientific_arm_design_unrun**. Leverage rank 56 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:98`.
- Current evidence: DS-14/SCIENTIFIC-RESEARCH specify source discovery, rights gates and hard-floor corpus; no Option A/B/C outcome or rights-operation qualification.
- Smallest discriminating decision/test: One seeded false citation, retracted source and inaccessible full text must be rejected or labeled unknown by an independent verifier before quality comparison.
- Competitor/control: Authority-first federation versus aggregator-only discovery versus direct-source workflow.
- Falsifier: False claim/source receives acceptance or metadata access is treated as permission for full-text reuse.
- Non-proof: Citation count, consensus and retrieval availability are not scientific validity or copyright clearance.
- Dependencies: A-26, A-29, A-34, A-49
- Packet links: R-Q, R-W, R-H

### A-44 — Perf engineering / complexity budget
Status: **optimization_specified_benefit_unmeasured**. Leverage rank 36 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:100`.
- Current evidence: DS-10/PERFORMANCE-PLAN and R-O set hard-floor-first performance vector; Option 2 benefit and complexity ablation remain unmeasured.
- Smallest discriminating decision/test: Measure inert/no-work, cold/warm and disabled-plugin costs under one pinned matched workflow, recording p99 control latency, review cost and all-role usage separately.
- Competitor/control: Strong direct-harness/native minimal baseline and accepted architecture alternatives, without reopening accepted direction.
- Falsifier: Claimed improvement disappears under total-cost accounting or violates any correctness/authorization/recovery floor.
- Non-proof: Fewer lines/processes/tokens or synthetic throughput alone is not user benefit; no weighted score hides regressions.
- Dependencies: A-15, A-46, A-47, A-50
- Packet links: R-O, R-S, R-W

### A-45 — Adaptive learning / route feedback
Status: **adaptation_packet_issued_promotion_unqualified**. Leverage rank 54 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:101`.
- Current evidence: Actual R-S owns adaptive optimization; DS-11/26 supply routing and telemetry; stale map wrongly calls it R-T.
- Smallest discriminating decision/test: In offline replay, compare a fixed eligible-route policy with adaptive ranking on drifted data; require explicit promotion and identical hard constraints.
- Competitor/control: Well-tuned fixed policy versus bounded learned/adaptive policy.
- Falsifier: Reward hacking, stale feedback or exploration widens authority, raises false-green rate or consumes hidden quota.
- Non-proof: Correlation and offline score do not prove causal live savings or authorize policy promotion.
- Dependencies: A-04, A-28, A-46, A-47, A-50
- Packet links: R-S, R-W, R-O

### A-46 — Quota / accounting
Status: **accounting_contract_candidate_values_unmeasured**. Leverage rank 15 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:102`.
- Current evidence: R-B HonestAccounting and R-D preregistration distinguish quantity, attribution and financial/capacity ledgers; all route counters remain candidate surfaces.
- Smallest discriminating decision/test: For one qualified route, reconcile one main turn plus helper/compaction/retry with independent usage observations; preserve null/reason for unavailable subscription debit.
- Competitor/control: Direct same-workload harness with matched quality and full overhead versus wrapper path.
- Falsifier: Missing usage becomes zero, counters overlap/double-count or a savings claim excludes helper/recovery/review cost.
- Non-proof: Token counts, advertised quota or provider intent speculation cannot establish workload subscription savings.
- Dependencies: A-28, A-47, A-49, D-031
- Packet links: R-D, R-F, R-O, R-W

### A-47 — Telemetry / honest counters
Status: **telemetry_adapters_unqualified**. Leverage rank 16 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:104`.
- Current evidence: DS-26/TELEMETRY require observed/modeled/inferred/unavailable labels. FU-04 fault_triggered has a static boolean/string bug, demonstrating why provenance and schema alone are insufficient.
- Smallest discriminating decision/test: Replay reset/missing/duplicate counter segments through one adapter with independent totals and negative controls; reject invented zeros.
- Conforming rival: Event-level disjoint ledger reconciliation versus periodic retained native-unit reconciliation with identical coverage semantics. Both preserve raw provenance, disjoint lineage/segments, units, resets, unknown liability and independently checked totals; compare reconciliation latency/cost without discarding observations.
- Negative controls, not eligible rivals: Normalized dashboard total alone; summed cumulative reports; unavailable counters rendered zero.
- Previous comparison preserved: Raw provenance-qualified event ledger versus normalized dashboard totals alone.
- Comparison sources: ../rv/recommendations.json (V-R08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Reset yields negative usage, duplicate samples inflate totals or missing coverage is shown as exact.
- Non-proof: Typed counters and stored telemetry do not establish truthful measurement or economic value.
- Dependencies: A-02, A-03, A-28
- Packet links: R-V, R-O, R-D

### A-48 — Explain / replay debugging
Status: **replay_debugging_packet_issued_unbuilt**. Leverage rank 43 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:105`.
- Current evidence: Actual R-V owns observability/introspection/replay debugging; old map gives R-S and says no owner. Canonical replay substrate is only partial.
- Smallest discriminating decision/test: Reconstruct one denied admission plus stale-epoch effect from canonical inputs without model calls; intentionally remove a segment and show a gap.
- Conforming rival: Version-specific pure replay interpreters versus pure migration into a common versioned representation followed by independent interpretation. Both preserve exact retained inputs, semantic versions, explicit gaps, authorization/redaction and zero execution during replay; compare fidelity and maintenance cost on identical corpus.
- Negative controls, not eligible rivals: Prose incident summary or model/tool rerun used to invent/repair missing history.
- Previous comparison preserved: Deterministic causal replay with references versus prose incident summary.
- Comparison sources: ../rv/recommendations.json (V-R07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Replay invents absent events, exposes disallowed fields or changes canonical state while inspecting.
- Non-proof: A trace viewer, event list or model explanation is not complete causal replay.
- Dependencies: A-01, A-02, A-22, A-47
- Packet links: R-V, R-L

### A-49 — Verifier independence / acceptance
Status: **independence_policy_closed_empirical_value_open**. Leverage rank 13 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:107`.
- Current evidence: CONTROL_PLANE requires independent exact-candidate verification; DS-03 480-candidate matrix remains unrun. FU-03 recorded model results are not acceptance.
- Smallest discriminating decision/test: First use one seeded-defect family to verify blinding, candidate binding and oracle separation; then preserve the preregistered 480-candidate design for empirical independence claims.
- Conforming rival: Independently authored end-state plus causal-evidence oracle versus a separately authored executable reference-state machine with independent black-box checks. Both retain the same risk/independence requirements, blinded candidate binding, seeded controls and independent exact-candidate rerun; neither substitutes reviewer agreement for the gate.
- Negative controls, not eligible rivals: Implementer self-PASS, model consensus or copied expected outputs treated as independent acceptance.
- Previous comparison preserved: Deterministic independently authored oracle plus blinded reviewer versus implementer self-PASS or model consensus.
- Comparison sources: ../rw/report.md (Q02)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Verifier accepts a known bad candidate or reruns a different tree/artifact.
- Non-proof: Different model family is preferred, not a proof of independent defects; sample pilot does not replace full study.
- Dependencies: A-01, A-37, A-50, CONTROL_PLANE
- Packet links: R-W

### A-50 — Benchmark science
Status: **benchmark_preregistration_open**. Leverage rank 14 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:108`.
- Current evidence: DS-10/11 and R-D/R-W specify science requirements; manifest, local corpus, accepted margins and baseline selection are not yet qualified.
- Smallest discriminating decision/test: Freeze one task class, raw inputs, allocation, stopping, primary endpoint and total-cost denominator before observing outcomes; include a strong direct baseline.
- Competitor/control: Matched direct harness and minimal orchestrator versus Recursion with identical authorized workflow/quality gates.
- Falsifier: Selective exclusions, post-hoc metrics or missing costs reverse the claimed result.
- Non-proof: A demo, 12 recorded OS passes or one successful task does not establish comparative product advantage.
- Dependencies: A-44, A-46, A-47, A-49, D-024, D-031
- Packet links: R-W, R-D, R-O

### A-51 — OS platform profiles
Status: **platform_scope_closed_profiles_unqualified**. Leverage rank 2 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:110`.
- Current evidence: D-028 closes G-11. FU-04 floors map eleven cases; four safe Windows probes and 13 trace rows exist, but all profiles remain unqualified and WSL is dev/test only.
- Smallest discriminating decision/test: Bind one exact native Windows and one native Linux profile to mechanism-specific evidence, then close mandatory missing traces including VM-reset durability on approved disposable targets.
- Conforming rival: Per-floor conformance compiler plus independent semantic corpus versus a common narrow broker IR with per-floor refinement obligations. Both require the same exact D-028 native profiles and independent native mechanism/negative-trace evidence; unsupported arms remain explicit and WSL/other profiles never inherit qualification.
- Negative controls, not eligible rivals: Inheriting native qualification from WSL or compatibility shells; best-effort primitive downgrade retaining a strong badge.
- Previous comparison preserved: Native contract evidence per exact profile versus inherited WSL/compatibility-shell qualification.
- Comparison sources: ../ru/recommendations.json (RU-R05)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Required mechanism fails on a floor, profile identity is ambiguous or VM-reset replay diverges.
- Non-proof: Pinned floor, cgroup presence, Windows build identity and WSL traces are not platform certification.
- Dependencies: D-028, FU-04 approved target and exact profile identity
- Packet links: FU-04, R-U, R-X

### A-52 — Language / runtime
Status: **runtime_selection_open_experiment_specified**. Leverage rank 52 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:111`.
- Current evidence: DS-18/FU-01 define language-neutral hard floors and comparison; all resource/FFI/tail/dependency cells remain unmeasured. Candidate version strings require revalidation before execution.
- Smallest discriminating decision/test: After byte corpus is sufficient, implement only the same deterministic boundary in each admitted candidate and compare hard-floor failures before resource metrics.
- Competitor/control: CPython, Rust and Go arms exactly as preregistered, with free-threaded/GIL split if retained; no winner selected here.
- Falsifier: Any candidate cannot reproduce required bytes/refusals or violates target-profile resource/fault floor.
- Non-proof: Language reputation, ecosystem size or TLC model language is not runtime selection evidence.
- Dependencies: A-01, A-03, A-51, G-01
- Packet links: FU-01, FU-03, FU-04

### A-53 — Multi-node / remote execution
Status: **availability_decision_closed_fabric_unqualified**. Leverage rank 29 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:113`.
- Current evidence: D-020 requires toggleable automatic takeover through first-party availability plugin over single-node fenced core; R-X owns fabric. Default compiles no consensus.
- Smallest discriminating decision/test: Partition old coordinator and promote a new writer while delayed old commands arrive; exactly one receiver epoch may commit, with core-only boot separately preserved.
- Conforming rival: Linked first-party availability plugin at the minimal core seam versus an isolated first-party availability service implementing that same opt-in seam. Both preserve D-020 automatic takeover, single fenced writer, identical failure assumptions and core-only adapter-free recovery, with no default consensus or remote activation.
- Negative controls, not eligible rivals: Mandatory consensus embedded into the default core; election without sink fencing.
- Previous comparison preserved: Single-node fenced core plus optional availability backend versus mandatory consensus core; decision direction remains accepted.
- Comparison sources: ../rx/recommendations.json (RX-R10)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Plugin cannot enforce takeover without bypassing core fence, or default core gains consensus dependency.
- Non-proof: Election, heartbeat timeout or temporary process exclusivity is not safe failover.
- Dependencies: A-02, A-05, A-08, A-12, A-51, D-020
- Packet links: R-X, R-E, FU-04

### A-54 — Workspace / repository graph
Status: **workspace_packet_issued_graph_unqualified**. Leverage rank 22 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:115`.
- Current evidence: Actual R-Y owns workspace/repository graph, not R-P; CONTEXT RepositoryMap is partial. Dirty tree, worktrees, multi-repo identity and accepted candidate bindings remain open.
- Smallest discriminating decision/test: Capture one dirty multi-worktree source graph and fork it; reproduce both source identities including untracked/deleted files without granting authority from repository content.
- Conforming rival: Registered manifest resolver with explicit move/clone association versus path/remote-alias resolution backed by the same canonical stable IDs and explicit association. Both preserve exact source/materialization/dirty-tree bindings, privacy and authority; path aliases locate objects but never replace their identity.
- Negative controls, not eligible rivals: Branch name or path-only identity treated as exact source or task authority.
- Previous comparison preserved: Immutable source manifest plus worktree binding versus branch name or path-only identity.
- Comparison sources: ../ry/recommendations.json (Y-R01 / Y-R04)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Review/gate binds a different tree, dirty content is lost or symlink/path alias crosses scope.
- Non-proof: Git SHA alone does not describe uncommitted source; repository instructions are not Owner grants.
- Dependencies: A-03, A-10, A-34, A-41
- Packet links: R-Y, R-P, R-V

### A-55 — Config architecture / resolver
Status: **configuration_architecture_specified_conformance_open**. Leverage rank 19 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:117`.
- Current evidence: DS-13 freezes design architecture, not syntax; CLI typed edit and deterministic resolver are specified. Privacy/publication lattice and corpus remain open.
- Smallest discriminating decision/test: Compile the same one-setting edit from file and UI under conflicting scopes; reject ambiguous/forbidden merges and retain all deny provenance.
- Conforming rival: One shared deterministic resolver implementation versus independently implemented frontend/adapter resolvers passing the same semantic corpus. Both retain a single semantic configuration contract, typed effective revision, deny/authority provenance and invalidation rules; implementation hashes may differ while semantic bytes/values/refusals must agree.
- Negative controls, not eligible rivals: Frontend-local policy meanings and ad hoc precedence heuristics.
- Previous comparison preserved: Single typed effective-config resolver versus frontend-local settings and precedence heuristics.
- Comparison sources: ../ro/report.md (O-R10); ../rl/recommendation-register.json (C01 / C08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Same revisions resolve differently across OS/surface or an edition/preset expands authority.
- Non-proof: A JSON schema, human syntax or valid file is not an authorized effective configuration.
- Dependencies: A-03, A-04, A-21, A-30
- Packet links: R-L, R-O, R-A

### A-56 — Licensing / provenance / IP
Status: **license_direction_closed_clearance_open**. Leverage rank 28 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:119`.
- Current evidence: D-026 chooses Apache-2.0 direction with license-file/contribution posture pending; D-027 allows packet only; G-32 stays open. D-031 bans vendor-sabotage positioning.
- Smallest discriminating decision/test: Complete per-component provenance/license/terms inventory and exact operating-mode questions for Lucas/counsel; inspect missing LICENSE artifact before any public release claim.
- Conforming rival: Native clean-room implementation versus a rights-cleared narrow source port of the same capability. Both require complete provenance, license/NOTICE/trademark and service-entitlement review plus identical technical/authority behavior; rights-cleared is a future admission prerequisite, not a current finding.
- Negative controls, not eligible rivals: Copying incompatible source; treating an API/source license as service or trademark permission.
- Previous comparison preserved: Narrow licensed adapter/clean-room implementation versus copying incompatible source or assuming API rights.
- Comparison sources: ../ri/report.md (adopt / port / avoid recommendation register); ../rh/report.md (T05 release contents and notices)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: An obligation conflicts with distribution, required provenance is absent or counsel cannot clear an intended mode.
- Non-proof: Permissive source license does not grant trademark, marketplace, account automation or service access rights.
- Dependencies: A-29, A-30, A-32, D-026, D-027, D-031
- Packet links: R-C, R-H, R-G, R-I

### A-57 — Release / update / packaging
Status: **release_contract_comprehensive_packaging_unqualified**. Leverage rank 35 within this ledger. Source: `docs/v3/research-lane/ARCHITECTURE-COVERAGE.md:121`.
- Current evidence: D-019 keeps accepted capabilities available opt-in; PLUGINS requires disabled zero-effect/adapter-free recovery. Packaging/channel remain unselected; current explicit terminal-first direction governs construction order. Exact GUI release timing remains unresolved if it changes a D-019 release gate; no GUI capability or first-release opt-in obligation is silently removed.
- Smallest discriminating decision/test: A minimal offline manifest boots/replays with every optional adapter absent, and an installed-disabled representative plugin triggers no import/network/process/model effect.
- Conforming rival: Lean installation with optional payloads physically absent versus a full installed-but-inert bundle with the same comprehensive capability catalog. Both preserve every accepted D-019 capability, opt-in activation, adapter-free recovery and the same disabled zero-effect/resource obligations; compare payload/install/metadata cost without removing scope.
- Negative controls, not eligible rivals: Always-loaded behavior merely hidden by a checkbox or lean preset silently dropping required capability.
- Previous comparison preserved: Lean physical optionality versus merely hidden features in an always-loaded monolith.
- Comparison sources: ../ro/report.md (O-D5 integration tax); ../rl/recommendation-register.json (C03)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Core cannot recover alone, disabled plugin starts work or a lean preset silently deletes a release obligation.
- Non-proof: Installer size, opt-in checkbox or artifact signature does not prove idle-free behavior, update safety or release acceptance.
- Dependencies: A-13, A-14, A-30, A-31, A-44, A-56, D-019
- Packet links: R-O, R-U, R-G
## Gap register

### G-01 — The decision-producing language/runtime experiment `EXP-FHAR-10` was never run; no implementation language is selected and every resource, tail, FFI, cold-start and dependency-closure cell is unmeasured.
Status: **open_experiment_specification_complete**. Leverage rank 14 within this ledger. Source: `docs/v3/research-lane/GAPS.md:32`.
- Current evidence: FU-01 return exists; EXP-FHAR-10 has not supplied qualifying local candidate measurements. Language remains unselected. Versions in September research are inputs needing validation, not choices.
- Smallest discriminating decision/test: After byte corpus is sufficient, implement only the same deterministic boundary in each admitted candidate and compare hard-floor failures before resource metrics.
- Competitor/control: CPython, Rust and Go arms exactly as preregistered, with free-threaded/GIL split if retained; no winner selected here.
- Falsifier: Any candidate cannot reproduce required bytes/refusals or violates target-profile resource/fault floor.
- Non-proof: Language reputation, ecosystem size or TLC model language is not runtime selection evidence.
- Dependencies: A-01, A-03, A-51
- Packet links: FU-01, FU-03, FU-04

### G-02 — No canonical crash/replay benchmark ran between segmented JSONL + CAS and SQLite WAL + CAS; no store is selected, so exact replay digest, stale-writer exclusion and power-loss durability have no measured basis.
Status: **open_experiment_specification_complete**. Leverage rank 5 within this ledger. Source: `docs/v3/research-lane/GAPS.md:33`.
- Current evidence: FU-02 protocol/oracles exist; no canonical store comparison or D-028 VM-reset replay accepted. FU-04 rename observations are narrower evidence.
- Smallest discriminating decision/test: Run the same smallest acknowledged-write/reset/replay trace on both store candidates with byte-identical expected state after authorized disposable-target admission.
- Competitor/control: Segmented JSONL+CAS versus SQLite WAL+CAS; secondary challengers only if preregistered.
- Falsifier: Any acknowledged generation is unrecoverable, replay diverges or old writer is accepted.
- Non-proof: Store documentation and clean shutdown do not establish target-profile durability.
- Dependencies: A-01, A-03, A-05, A-51
- Packet links: FU-02, FU-04

### G-03 — The TLA+/TLC finite model, the 36 classified reachable mutants, the language-neutral byte-level vector corpus and two independent implementations do not exist; the four-function kernel freeze is conditional.
Status: **open_partial_recorded_execution_stale_absence_claim**. Leverage rank 1 within this ledger. Source: `docs/v3/research-lane/GAPS.md:34`.
- Current evidence: The old claim that no TLA+/TLC model exists is false for this commit. RKernel/RIntegrated and raw outputs exist; 5/7 instantiated mutants killed, 29 mandatory rows uninstantiated. Integrated bound, independent monitors, complete RCV1 byte corpus and two-stack reproduction remain open.
- Smallest discriminating decision/test: First reconcile exact mutation sites and independent RefState/replay; for M25/M31 provide witnessed reachable nonequivalence or an explicit bounded unreachable/equivalent classification, without weakening unrelated guards. Then classify all 36 rows and publish byte vectors plus two independent implementations.
- Conforming rival: Independently authored event-equation reference semantics versus an independently authored executable reference-state interpreter, with separate replay/projection checks in both arms. Both retain the identical four-function boundary, full integrated bounds, mandatory 36-row classifications, independent monitors, literal byte corpus, two implementations and exact-candidate verification; compare oracle sensitivity and maintenance burden without substituting away a mandatory gate.
- Negative controls, not eligible rivals: Shared reducer/serializer defects in candidate and oracle; baseline-only or reduced-bound PASS promoted to kernel freeze.
- Previous comparison preserved: The same four functions checked by an independent reference semantics, with deliberately shared-bug controls.
- Comparison sources: ../rw/report.md (Q02); ../rp/recommendations.json (RP-R10 / RP-R13)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A reachable defective reducer or packet derivation is accepted by both subject and monitor, or implementations disagree on bytes/refusal.
- Non-proof: Neither 5/7 nor 5/36 is the acceptance metric: uninstantiated, unreachable-within-bound and killed are separate. No independent exact-candidate acceptance or kernel freeze.
- Dependencies: D-022, FU-03 accepted integrated bound
- Packet links: FU-03, R-W

### G-04 — No OS native-semantics conformance fixtures or machine-readable platform-profile manifest exist; there are zero measured cells for containment, PTY/ConPTY teardown, atomic-replace durability, lock release or supervisor races.
Status: **open_partial_recorded_execution_stale_zero_claim**. Leverage rank 2 within this ledger. Source: `docs/v3/research-lane/GAPS.md:35`.
- Current evidence: The old no-manifest/zero-cells statement is stale. Machine manifest covers 11 cases; normalized catalog has 20 PF traces; raw results have 13 run rows: 12 pass/1 unknown, plus 10 not_run rows. No exact profile is qualified.
- Smallest discriminating decision/test: First reconcile raw artifact identity, fault-trigger telemetry and oracle claims; then qualify one exact native floor with the missing mechanism-specific traces, without borrowing WSL results.
- Conforming rival: Per-floor conformance compiler plus independent semantic corpus versus a common narrow broker IR with per-floor refinement obligations. Both require the same exact D-028 native profiles and independent native mechanism/negative-trace evidence; unsupported arms remain explicit and WSL/other profiles never inherit qualification.
- Negative controls, not eligible rivals: Inheriting native qualification from WSL or compatibility shells; best-effort primitive downgrade retaining a strong badge.
- Previous comparison preserved: Native contract evidence per exact profile versus inherited WSL/compatibility-shell qualification.
- Comparison sources: ../ru/recommendations.json (RU-R05)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Required mechanism fails on a floor, profile identity is ambiguous or VM-reset replay diverges.
- Non-proof: 13 run rows cover 10 unique trace IDs; pass labels are handler outcomes, not full trace conformance, native floor qualification or VM-reset durability.
- Dependencies: D-028, FU-04 approved target and exact profile identity
- Packet links: FU-04, R-U, R-X

### G-05 — The IPC/process-broker protocol is only conditionally adopted; four freeze blockers (version negotiation, snapshot materialization, cursor rollover, ACK-release wording) and the native Windows/Linux chaos matrix are unpassed.
Status: **open_broker_freeze_and_chaos_gate**. Leverage rank 4 within this ledger. Source: `docs/v3/research-lane/GAPS.md:36`.
- Current evidence: FU-05 return supplies decision materials and preregistration. Version negotiation, snapshot materialization, cursor rollover and ACK-release wording need accepted semantics plus native chaos evidence.
- Smallest discriminating decision/test: Resolve version negotiation, snapshot materialization, cursor rollover and ACK-release semantics in one synthetic reconnect trace with a slow observer.
- Conforming rival: Bounded pull pages and consistent-cut snapshots plus notifications versus bounded credited push with replay/reset. Both use the same command receipts, canonical order, negotiated version, cursor/snapshot/ACK semantics, finite resource bounds and independently preserved control path.
- Negative controls, not eligible rivals: Terminal scraping or unbounded mirrored streams used as the authoritative broker contract.
- Previous comparison preserved: Explicit bounded command/event protocol versus terminal scraping or unbounded stream mirroring.
- Comparison sources: ../rv/recommendations.json (V-R06); ../rl/recommendation-register.json (C04 / C11)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: ACK releases causal evidence prematurely, gaps silently lose records or a slow view blocks Stop/writer.
- Non-proof: A JSON transport, successful handshake or receipt-schema PASS is not broker freeze.
- Dependencies: A-03, A-05, A-18, A-51
- Packet links: FU-05, R-F, R-K, R-L

### G-06 — The availability/authority contract is undecided: may the single fenced canonical writer be temporarily unavailable after coordinator loss?
Status: **owner_decision_closed_implementation_unqualified**. Leverage rank 17 within this ledger. Source: `docs/v3/research-lane/GAPS.md:37`.
- Current evidence: Closed by D-020: automatic takeover is required and toggleable; single-node fenced core plus opt-in availability backend, no default consensus. Do not ask again whether failover belongs in scope.
- Smallest discriminating decision/test: Partition old coordinator and promote a new writer while delayed old commands arrive; exactly one receiver epoch may commit, with core-only boot separately preserved.
- Conforming rival: Linked first-party availability plugin at the minimal core seam versus an isolated first-party availability service implementing that same opt-in seam. Both preserve D-020 automatic takeover, single fenced writer, identical failure assumptions and core-only adapter-free recovery, with no default consensus or remote activation.
- Negative controls, not eligible rivals: Mandatory consensus embedded into the default core; election without sink fencing.
- Previous comparison preserved: Single-node fenced core plus optional availability backend versus mandatory consensus core; decision direction remains accepted.
- Comparison sources: ../rx/recommendations.json (RX-R10)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Plugin cannot enforce takeover without bypassing core fence, or default core gains consensus dependency.
- Non-proof: Closed availability policy does not qualify a consensus implementation, election, replication or receiver fence.
- Dependencies: A-02, A-05, A-08, A-12, A-51, D-020
- Packet links: R-X, R-E, FU-04

### G-07 — No single PAUSE/Stop model is settled across configuration, the formal model and the broker; `checkpoint`/`interrupt`/`drain`/emergency and the drain allowlist remain unresolved.
Status: **owner_decision_closed_conformance_unqualified**. Leverage rank 16 within this ledger. Source: `docs/v3/research-lane/GAPS.md:38`.
- Current evidence: Closed by D-022: Aggressive/Full/Lazy plus checkpoint/interrupt/drain. The remaining issue is complete mapping into config, model, broker and adapter boundaries, not which vocabulary to choose.
- Smallest discriminating decision/test: One table maps every mode to admission, local descendants, remote receipts and uncertain effects; run a bounded synthetic stop at before-dispatch/after-dispatch cuts when authorized.
- Conforming rival: Eager indexed schedule reaping plus receiver fences versus generation-fenced due-time rejection with bounded registry cleanup. Both implement exactly the accepted D-022 vocabulary, selected scope/boundary and independent per-member receiver observations; compare bounded control/resource cost only after semantic equality.
- Negative controls, not eligible rivals: Divergent configuration/model/broker meanings for the same Stop label.
- Previous comparison preserved: The accepted vocabulary rendered consistently in config, formal model and broker versus divergent surface meanings.
- Comparison sources: ../rr/recommendations.json (RR-R06)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: One Stop label permits incompatible behavior across surfaces or reports external rollback from interruption.
- Non-proof: Resolved names do not prove consistent stop semantics, drain allowlist, emergency behavior or external effect rollback.
- Dependencies: A-04, A-05, A-08, A-18, D-022
- Packet links: FU-03, FU-05, R-J, R-K, R-L

### G-08 — The 2-vCPU/4-GiB coordinator-small profile is a target, not a demonstrated capacity point; preflight "seconds", service-topology SLOs, watchdog timeouts and recovery decomposition are unverified.
Status: **open_capacity_experiment**. Leverage rank 22 within this ledger. Source: `docs/v3/research-lane/GAPS.md:39`.
- Current evidence: 2-vCPU/4-GiB coordinator-small is a proposed capacity profile. Preflight latency, topology, watchdog and recovery decomposition have no local acceptance data.
- Smallest discriminating decision/test: On the approved small profile, compare fixed/adaptive admission under one burst with reserved control/writer resources and independent review queue; publish p99 latency and recovery components.
- Competitor/control: A tuned fixed concurrency cap versus adaptive min-credit controller.
- Falsifier: Adaptive policy raises false-green/review age or violates a hard resource ceiling.
- Non-proof: A workstation observation or process-count limit is not capacity evidence for the pinned coordinator profile.
- Dependencies: A-04, A-46, A-47, A-49, A-50
- Packet links: R-O, R-S, R-W

### G-09 — The configuration architecture is frozen in design but has no cross-platform conformance corpus, no chosen human syntax and no agreed authority lattices for privacy exposure and publication.
Status: **open_configuration_conformance_and_narrow_choices**. Leverage rank 8 within this ledger. Source: `docs/v3/research-lane/GAPS.md:40`.
- Current evidence: Configuration architecture is a design baseline, while cross-platform bytes/resolver corpus, human syntax and privacy/publication lattices remain unresolved.
- Smallest discriminating decision/test: Begin with one conflicting layered configuration corpus covering deny preservation and identical canonical bytes; identify only genuinely unmade syntax/lattice decisions, not settled release policy.
- Conforming rival: One shared deterministic resolver implementation versus independently implemented frontend/adapter resolvers passing the same semantic corpus. Both retain a single semantic configuration contract, typed effective revision, deny/authority provenance and invalidation rules; implementation hashes may differ while semantic bytes/values/refusals must agree.
- Negative controls, not eligible rivals: Frontend-local policy meanings and ad hoc precedence heuristics.
- Previous comparison preserved: Single typed effective-config resolver versus frontend-local settings and precedence heuristics.
- Comparison sources: ../ro/report.md (O-R10); ../rl/recommendation-register.json (C01 / C08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Same revisions resolve differently across OS/surface or an edition/preset expands authority.
- Non-proof: A JSON schema, human syntax or valid file is not an authorized effective configuration.
- Dependencies: A-03, A-04, A-21, A-30
- Packet links: R-L, R-O, R-A

### G-10 — The renderer and the plugin runtime remain unselected across every lane.
Status: **open_renderer_and_runtime_evaluation**. Leverage rank 29 within this ledger. Source: `docs/v3/research-lane/GAPS.md:41`.
- Current evidence: No renderer or plugin runtime is selected. R-K/N investigate terminal/later GUI, R-U isolation; no research recommendation is adoption.
- Smallest discriminating decision/test: Use the same keyboard/slow-stream task and malicious-plugin capability fixture across candidate placements, comparing semantic failures before performance.
- Competitor/control: Mature multiplexer/thin view versus bespoke renderer; OS subprocess isolation versus capability runtime. No candidate selected.
- Falsifier: Plugin crosses a denied boundary or disabled payload executes.
- Non-proof: A process, sandbox label, signature, SBOM or WASI use alone is not confinement.
- Dependencies: A-18, A-20, A-23, A-31, A-51
- Packet links: R-U, R-E, R-G

### G-11 — Exact Windows build floors, Linux kernel/distribution profiles, WSL2 production status, SMB/NFS scope and the definition of "survives power loss" are undecided.
Status: **owner_decision_closed_profiles_unqualified**. Leverage rank 18 within this ledger. Source: `docs/v3/research-lane/GAPS.md:42`.
- Current evidence: Closed by D-028: Windows 25H2 26200 Home/Pro and 24H2 26100 Enterprise qualification target; Linux 6.12 primary/6.6 minimum with cgroup v2; WSL dev/test; NTFS/ext4; SMB/NFS excluded; abrupt VM reset definition.
- Smallest discriminating decision/test: Populate exact profile keys and mechanism evidence under already chosen floors; do not reopen platform scope or treat platform-floors.json also_qualified field as completed certification.
- Conforming rival: Per-floor conformance compiler plus independent semantic corpus versus a common narrow broker IR with per-floor refinement obligations. Both require the same exact D-028 native profiles and independent native mechanism/negative-trace evidence; unsupported arms remain explicit and WSL/other profiles never inherit qualification.
- Negative controls, not eligible rivals: Inheriting native qualification from WSL or compatibility shells; best-effort primitive downgrade retaining a strong badge.
- Previous comparison preserved: Native contract evidence per exact profile versus inherited WSL/compatibility-shell qualification.
- Comparison sources: ../ru/recommendations.json (RU-R05)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Required mechanism fails on a floor, profile identity is ambiguous or VM-reset replay diverges.
- Non-proof: The phrase also_qualified is a naming hazard: the same file says qualification none and maps native_windows in_scope_unqualified. All profiles remain unqualified.
- Dependencies: D-028, FU-04 approved target and exact profile identity
- Packet links: FU-04, R-U, R-X

### G-12 — The preregistered 480-candidate blinded verifier-independence matrix (120 per risk class, six defect families, treatments T0–T7) was never run; provider/account/host semantic value stays unverified.
Status: **open_verifier_independence_experiment**. Leverage rank 9 within this ledger. Source: `docs/v3/research-lane/GAPS.md:48`.
- Current evidence: The 480-candidate preregistered blinded matrix is not executed. Independent verifier policy remains mandatory regardless of unmeasured model/provider/account/host marginal benefit.
- Smallest discriminating decision/test: First use one seeded-defect family to verify blinding, candidate binding and oracle separation; then preserve the preregistered 480-candidate design for empirical independence claims.
- Conforming rival: Independently authored end-state plus causal-evidence oracle versus a separately authored executable reference-state machine with independent black-box checks. Both retain the same risk/independence requirements, blinded candidate binding, seeded controls and independent exact-candidate rerun; neither substitutes reviewer agreement for the gate.
- Negative controls, not eligible rivals: Implementer self-PASS, model consensus or copied expected outputs treated as independent acceptance.
- Previous comparison preserved: Deterministic independently authored oracle plus blinded reviewer versus implementer self-PASS or model consensus.
- Comparison sources: ../rw/report.md (Q02)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Verifier accepts a known bad candidate or reruns a different tree/artifact.
- Non-proof: Different model family is preferred, not a proof of independent defects; sample pilot does not replace full study.
- Dependencies: A-01, A-37, A-50, CONTROL_PLANE
- Packet links: R-W

### G-13 — The private canary has never executed: no route was exercised, no write-boundary/oracle path was tested end to end, and no independent authoritative oracle is shown to exist.
Status: **open_canary_execution**. Leverage rank 31 within this ledger. Source: `docs/v3/research-lane/GAPS.md:49`.
- Current evidence: DS-08 has a protocol but no route exercised or accepted private canary result. The bounded synthetic oracle/negative controls are the cheapest preceding discriminator.
- Smallest discriminating decision/test: A provider-free synthetic candidate with one seeded boundary defect must fail an independently held oracle before any authorized private canary.
- Conforming rival: Independently authored end-state plus causal-evidence oracle versus a separately authored executable reference-state oracle with independent black-box witnesses. Both retain identical seeded negative and positive controls, private-canary boundaries, independent custody and acceptance obligations; compare defect sensitivity before expanding any scope.
- Negative controls, not eligible rivals: Worker self-report, shared oracle defects or characterization-only PASS used as correctness acceptance.
- Previous comparison preserved: Independent authoritative oracle versus worker self-report or characterization-only pass.
- Comparison sources: ../rw/report.md (Q02); ../ru/recommendations.json (RU-R09)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Known bad write-boundary behavior is accepted or the oracle shares the subject defect.
- Non-proof: Passing synthetic controls is not live route, private-target or production qualification.
- Dependencies: A-08, A-34, A-49, A-50
- Packet links: R-W, R-P, R-U

### G-14 — No cutover, restore or reverse-reader rehearsal ran for single-writer migration and effect rollback; no complete writer inventory or epoch-enforcing storage path is shown.
Status: **open_v3_writer_transition_evidence_historical_v2_scope_retired**. Leverage rank 23 within this ledger. Source: `docs/v3/research-lane/GAPS.md:50`.
- Current evidence: No accepted writer-inventory/cutover/reverse-reader rehearsal is shown. D-017 retires mandatory v2 migration; apply relevant safety tests to v3 writer/schema/update transitions only.
- Smallest discriminating decision/test: For a synthetic v3 aggregate, enumerate all writers and crash a versioned transition, proving stale writers fail and accepted effects reconcile forward.
- Conforming rival: Verified versioned snapshot plus complete canonical suffix replay versus full replay from retained canonical genesis/closure without snapshot acceleration. Both retain identical newest committed state, exact source/profile bindings, compatibility rules and forward-only external-effect reconciliation; compare recovery cost without dropping obligations.
- Negative controls, not eligible rivals: Copying live store files without a coherent closure; relabeling external-effect rollback.
- Previous comparison preserved: Versioned snapshot plus verified tail replay versus copying live database files or rollback of external effects.
- Comparison sources: ../ry/recommendations.json (Y-R02 / Y-R15); ../rv/recommendations.json (V-R07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Restored state loses a committed event or rolls an already accepted effect into no-effect.
- Non-proof: Retaining historical v2 migration reasoning does not authorize or make v2 a prerequisite of greenfield v3.
- Dependencies: A-02, A-12, A-38
- Packet links: FU-02, R-V

### G-15 — The credential/egress broker has no adversarial threat-suite exercise and no measured zero-model preflight latency, resource use or bypass count; entitlement/distribution/ToS stay unknown.
Status: **open_credential_egress_threat_suite**. Leverage rank 7 within this ledger. Source: `docs/v3/research-lane/GAPS.md:51`.
- Current evidence: No adversarial broker suite or qualified preflight latency/bypass count exists. D-021/D-029 require delegated ownership plus stronger trusted-launch isolation where claimed; R-C/H is not clearance.
- Smallest discriminating decision/test: Mutate recipient/compiled bytes after approval and inject a stale grant at broker dispatch; use synthetic markers to observe every egress channel.
- Conforming rival: Completely mediated mixed-data processing across all release channels versus pre-exposure separation that never combines protected data and outward-capable processing. Both retain complete mediation, exact authorized recipients/compiled effects, useful required workflow, induced C/T/output protection and current revocation; no scanner-only release claim.
- Negative controls, not eligible rivals: Application policy alone; direct file denial plus output scanner treated as complete non-access.
- Previous comparison preserved: Exact-byte/destination-bound broker versus application policy only.
- Comparison sources: ../rp/recommendations.json (RP-R06)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Secret-bearing data leaves an unapproved destination or stale broker decision survives revocation.
- Non-proof: Opaque reference or zero-model preflight is not secret isolation or legal clearance.
- Dependencies: A-04, A-05, A-29, A-33
- Packet links: R-E, R-P, R-U

### G-16 — The deletion evidence contract has no negative-fixture run (copy ledger, key ledger, provider residual windows, disconnected spools); physical destruction on a lost node stays unknown.
Status: **open_deletion_negative_fixture_suite**. Leverage rank 25 within this ledger. Source: `docs/v3/research-lane/GAPS.md:52`.
- Current evidence: Copy/key ledger and derived completion rules are specified. Provider residual periods and physically lost-node destruction remain unavailable evidence, not zero residual.
- Smallest discriminating decision/test: Delete one synthetic item with a cache/index/export/offline spool copy; a deliberately missing copy receipt must keep completion unresolved.
- Conforming rival: Eager fine-grained lineage cleanup versus policy-bound deferred cleanup with conservative coarse lineage. Both retain the same complete copy/key inventory, restore gate, approved retention constraints, honest residual states and independently derived completion; deferred never means falsely complete.
- Negative controls, not eligible rivals: Tombstone or single-store deletion treated as complete destruction of all copies.
- Previous comparison preserved: Closed copy ledger with independent acceptance versus tombstone or single-store deletion.
- Comparison sources: ../rq/recommendations.json (C07)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Completion is reported while a recoverable uncontrolled copy remains or deleted data rehydrates.
- Non-proof: Key deletion, tombstone or provider policy cannot prove destruction on lost nodes.
- Dependencies: A-02, A-27, A-35, A-49
- Packet links: R-Q, R-T, R-V

### G-17 — The pause/effect-fencing crash-stage matrix and per-adapter fence conformance are unrun; no adapter is shown to place a fence near its irreversible boundary.
Status: **open_adapter_fence_crash_matrix**. Leverage rank 3 within this ledger. Source: `docs/v3/research-lane/GAPS.md:53`.
- Current evidence: D-022 resolves vocabulary, not the per-adapter fence site. FU-04 PF13 does not deliver a stale operation to an epoch-checking sink; adapter conformance remains open.
- Smallest discriminating decision/test: For Codex-first adapter contract, identify each supported effect sink and make one late revocation refuse an effect at that sink; downgrade unsupported sinks explicitly.
- Conforming rival: Atomic sink epoch-and-effect transaction versus a trusted serialized actuator checking the same current epoch and retaining explicit external-effect ambiguity. Both must mediate every protected sink in the same declared adapter profile; an external system lacking the required enforcement is unsupported/unknown, not silently advertised as equally fenced.
- Negative controls, not eligible rivals: Best-effort upstream interruption presented as irreversible-boundary fencing.
- Previous comparison preserved: Adapter with a genuine sink fence versus best-effort upstream interruption.
- Comparison sources: ../rx/recommendations.json (RX-R08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Any route claims strong fence while a stale granted operation still commits.
- Non-proof: TLC model, process termination and upstream cancel ACK do not establish remote effect prevention.
- Dependencies: A-04, A-05, A-18, A-33, D-023
- Packet links: FU-05, R-E, R-F, R-X

### G-18 — The Full Access capability-vector model is not shown to be implemented in the kernel or adapters, and adapter fencing/idempotency is explicitly unverified.
Status: **open_typed_authority_implementation**. Leverage rank 6 within this ledger. Source: `docs/v3/research-lane/GAPS.md:54`.
- Current evidence: Full Access capability vector, attenuation and current-grant intersection are design contracts. No common kernel/adapter enforcement demonstrates every dimension.
- Smallest discriminating decision/test: Evaluate one deny at each capability dimension and an attenuated child grant against the same effect at admission and immediately before commit.
- Conforming rival: Central typed meet compilation with authenticated opaque receiver references versus authenticated grant tokens with independent typed receiver checks and a shared reservation ledger. Both enforce the same per-dimension parent containment, current revocation, deny preservation and sibling budget conservation; neither changes accepted Full Access scope.
- Negative controls, not eligible rivals: Ambient process authority or boolean Full Access used instead of typed effect authority.
- Previous comparison preserved: Explicit capability-intersection table versus ambient process authority/boolean Full Access.
- Comparison sources: ../ru/recommendations.json (RU-R01)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A delegated grant expands scope, or revocation after planning still permits the effect.
- Non-proof: Schema validation, signature or conversation membership cannot grant authority.
- Dependencies: A-03, A-05, A-08, D-021, D-029
- Packet links: R-A, R-E, R-P, R-U

### G-19 — Native-plugin containment and cross-runtime capability enforcement are unresolved; the zero-effect disabled invariant has no tripwire run.
Status: **open_containment_and_disabled_tripwires**. Leverage rank 13 within this ledger. Source: `docs/v3/research-lane/GAPS.md:55`.
- Current evidence: Cross-runtime native-plugin containment and no-effect disabled path are not demonstrated. R-U owns the dedicated new isolation/supply-chain brief.
- Smallest discriminating decision/test: Use one inert installed plugin with tripwires on import, thread, subprocess, watcher, network, credential and model entry points, then one admitted malicious plugin with denied capabilities.
- Competitor/control: Bounded subprocess/OS isolation versus capability runtime, without choosing either.
- Falsifier: Plugin crosses a denied boundary or disabled payload executes.
- Non-proof: A process, sandbox label, signature, SBOM or WASI use alone is not confinement.
- Dependencies: A-04, A-18, A-33, A-51
- Packet links: R-U, R-E, R-G

### G-20 — No v2-vs-Options benchmark, R17 ablation or PERF-003 0/10/100 disabled-plugin matrix ran; Option 2's performance benefit is unverified and the benchmark manifest is undefined.
Status: **open_performance_manifest_and_ablation**. Leverage rank 19 within this ledger. Source: `docs/v3/research-lane/GAPS.md:61`.
- Current evidence: No current Option comparison, R17 ablation or 0/10/100 disabled-plugin matrix is accepted. Historical v2 can be a pinned research baseline only; D-017 does not allow it to become a runtime dependency.
- Smallest discriminating decision/test: Freeze a v3-relevant matched benchmark manifest and compare one boundary ablation plus cold/disabled costs; retain full correctness/authority/recovery and accepted feature floors.
- Competitor/control: Strong direct-harness/native minimal baseline and accepted architecture alternatives, without reopening accepted direction.
- Falsifier: Claimed improvement disappears under total-cost accounting or violates any correctness/authorization/recovery floor.
- Non-proof: Fewer lines/processes/tokens or synthetic throughput alone is not user benefit; no weighted score hides regressions.
- Dependencies: A-15, A-46, A-47, A-50
- Packet links: R-O, R-S, R-W

### G-21 — The dual-domain adaptive admission controller has no fixed-vs-adaptive crossover, no per-slot marginal-cost profile on either hardware profile, and no Little's Law validity check.
Status: **open_admission_crossover**. Leverage rank 21 within this ledger. Source: `docs/v3/research-lane/GAPS.md:62`.
- Current evidence: No fixed-versus-adaptive crossover, per-slot marginal profile or Little’s Law validity evidence. Controller watermarks/dwell remain hypotheses.
- Smallest discriminating decision/test: Replay one burst where review queue saturates before CPU, comparing fixed cap and adaptive admission at equal verified completions.
- Competitor/control: A tuned fixed concurrency cap versus adaptive min-credit controller.
- Falsifier: Adaptive policy raises false-green/review age or violates a hard resource ceiling.
- Non-proof: A formula or queue estimate does not validate Little’s Law, service times or useful concurrency.
- Dependencies: A-04, A-46, A-47, A-49, A-50
- Packet links: R-O, R-S, R-W

### G-22 — The routing/delegation confirmatory campaigns, pilot and ARM-count sweep have not run; no local corpus or acceptance margin exists.
Status: **open_routing_and_delegation_campaigns**. Leverage rank 11 within this ledger. Source: `docs/v3/research-lane/GAPS.md:63`.
- Current evidence: R-B supplies nine-harness map and H1 continuity protocol; R-D supplies measurement design. Pilot, confirmatory campaigns and ARM-count sweep are unrun.
- Smallest discriminating decision/test: Freeze one task class and matched direct baseline, then execute only the separately authorized provider-free H1 contract stage before route-specific real-binary qualification.
- Competitor/control: Strong direct-harness/manual continuity baseline B1 and minimal adapter B2, with explicit ablations; no new vendor choice.
- Falsifier: Adapter claims unsupported control, loses an approval or silently substitutes route/account/billing.
- Non-proof: Headless JSON, native subagents or source-code availability is not delegation qualification or entitlement.
- Dependencies: A-04, A-06, A-17, A-33, A-46, D-023
- Packet links: R-F, R-E, R-H

### G-23 — The PERF-010 0/1/5/10/20-view matrix and adversarial containment tests have not run; whole-descendant-tree termination is unverifiable from schema.
Status: **open_terminal_view_and_containment_matrix**. Leverage rank 20 within this ledger. Source: `docs/v3/research-lane/GAPS.md:64`.
- Current evidence: PERF-010 0/1/5/10/20-view matrix is unrun. FU-04 pipe/PTY observations do not qualify detachable terminal controls or universal descendant containment.
- Smallest discriminating decision/test: Saturate one observer while issuing Stop from another; measure bounded control latency and loss markers before scaling the full view-count matrix.
- Conforming rival: Integrated broker-managed detachable thin views versus external multiplexer-managed thin views over the same broker. Both keep actor/process ownership outside views, preserve exact control/replay semantics and bounded Stop responsiveness, and do no work merely on attach.
- Negative controls, not eligible rivals: A view-owned process lifecycle or detach that implicitly cancels authorized work.
- Previous comparison preserved: Daemon-owned terminal with attachable projections versus view-owned process.
- Comparison sources: ../rj/recommendations.json (RJ-R04)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Closing the last view kills authorized work or attachment silently launches inference.
- Non-proof: Terminal screenshot, raw PTY transcript or pipe exit does not prove durable interaction controls.
- Dependencies: A-06, A-17, A-18, A-21
- Packet links: R-J, R-K, R-L

### G-24 — The update/release/DR six-mode by four-outcome matrix and the restore trial are `unknown` in every cell; no engine-specific snapshot mechanism is selected.
Status: **open_update_restore_matrix**. Leverage rank 24 within this ledger. Source: `docs/v3/research-lane/GAPS.md:65`.
- Current evidence: All six-mode by four-outcome release/DR combinations still need mechanism-specific evidence. Snapshot mechanism and numeric RPO/RTO remain unselected/unmeasured.
- Smallest discriminating decision/test: Choose one representative failure cut and distinguish executable compatibility, state replay, task resume and external settlement separately, then expand all mandatory cells.
- Conforming rival: Reverified compatible rollback executable admitted under a fresh grant epoch versus forward recovery to an independently admitted replacement executable. Both preserve newest canonical work, the same six update modes/four outcome predicates and unresolved external effects; rollback never revives revoked code or old authority.
- Negative controls, not eligible rivals: Full-directory rollback that loses newest state or claims to undo settled external effects.
- Previous comparison preserved: Verified compatible executable with newest state versus full directory rollback.
- Comparison sources: ../ru/recommendations.json (RU-R13)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: One recovered badge masks lost state, unresolved effects or an incompatible reader.
- Non-proof: One restore trial does not fill all 24 outcome cells or establish numeric RPO/RTO.
- Dependencies: A-12, A-13, A-47, D-028
- Packet links: FU-02, FU-04, R-O

### G-25 — No telemetry adapter was exercised and no shadow evaluation ran; findings are documentation-qualified, not runtime-qualified.
Status: **open_runtime_telemetry_qualification**. Leverage rank 10 within this ledger. Source: `docs/v3/research-lane/GAPS.md:66`.
- Current evidence: Telemetry adapter and shadow evaluation remain unrun. FU-04 historical raw rows give diagnostic observations, not route accounting conformance.
- Smallest discriminating decision/test: Replay reset/missing/duplicate counter segments through one adapter with independent totals and negative controls; reject invented zeros.
- Conforming rival: Event-level disjoint ledger reconciliation versus periodic retained native-unit reconciliation with identical coverage semantics. Both preserve raw provenance, disjoint lineage/segments, units, resets, unknown liability and independently checked totals; compare reconciliation latency/cost without discarding observations.
- Negative controls, not eligible rivals: Normalized dashboard total alone; summed cumulative reports; unavailable counters rendered zero.
- Previous comparison preserved: Raw provenance-qualified event ledger versus normalized dashboard totals alone.
- Comparison sources: ../rv/recommendations.json (V-R08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Reset yields negative usage, duplicate samples inflate totals or missing coverage is shown as exact.
- Non-proof: Typed counters and stored telemetry do not establish truthful measurement or economic value.
- Dependencies: A-02, A-03, A-28
- Packet links: R-V, R-O, R-D

### G-26 — No Windows PSI equivalent, route-level capacity metrics, portable wakeup count or host monetary cost are established.
Status: **open_missing_resource_and_financial_inputs**. Leverage rank 28 within this ledger. Source: `docs/v3/research-lane/GAPS.md:67`.
- Current evidence: Windows pressure-equivalent semantics, route capacity, portable wakeup accounting and host monetary cost remain undefined/unavailable.
- Smallest discriminating decision/test: Specify units, reset/coverage rules and observation sources for one Windows and one Linux pressure scenario; explicitly refuse a cross-platform equivalence claim where no comparable measurement exists.
- Conforming rival: Direct native counter capture versus an independently implemented external collector/reconciler over the same exact declared observation scope. Both retain native units, timestamp/reset/coverage provenance, explicit incomparable fields and honest monetary/capacity unknowns; no portable equivalence or actual price/debit is invented.
- Negative controls, not eligible rivals: Invented portable pressure scalar; proxy labeled measured native equivalent; missing monetary cost rendered zero.
- Previous comparison preserved: Direct native counters with declared incomparable fields versus invented portable scalar.
- Comparison sources: ../rv/recommendations.json (V-R08); ../ru/recommendations.json (RU-R09)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Proxy pressure/cost is labeled measured equivalent, or missing monetary/usage inputs become zero.
- Non-proof: A correlated proxy or provider list price does not establish native pressure semantics or actual host/subscription debit.
- Dependencies: A-02, A-03, A-28
- Packet links: R-V, R-O, R-D

### G-27 — The context/compaction/cache route-by-route synthetic suite was never run; Recursion's route inventory and all cache economics are unknown.
Status: **open_context_route_suite**. Leverage rank 12 within this ledger. Source: `docs/v3/research-lane/GAPS.md:73`.
- Current evidence: No route-by-route cache/compaction/recovery suite or honest cache debit totals. R-Q/T extend memory and multimodal continuity but remain research proposals.
- Smallest discriminating decision/test: Cold-rebuild one task after deleting only the synthetic upstream session, then compare authorized continuation and all-role input/accounting against direct harness.
- Competitor/control: Minimal explicit handoff/cold context versus semantic capsule plus optional cache.
- Falsifier: Intent/authority/evidence is lost, private context crosses audience or measured total burden increases for the claimed workload.
- Non-proof: A short summary, token estimate or cache-hit report does not prove continuity or savings.
- Dependencies: A-02, A-04, A-09, A-46
- Packet links: R-Q, R-T, R-F

### G-28 — The scientific-ARM hard-floor corpus and the Option A/B/C comparison were specified but not executed; rights operations remain open.
Status: **open_scientific_arm_corpus_and_rights_gate**. Leverage rank 32 within this ledger. Source: `docs/v3/research-lane/GAPS.md:74`.
- Current evidence: Hard-floor research corpus and Option A/B/C comparison are unrun; rights-related access/distribution decisions remain separately gated.
- Smallest discriminating decision/test: One seeded false citation, retracted source and inaccessible full text must be rejected or labeled unknown by an independent verifier before quality comparison.
- Competitor/control: Authority-first federation versus aggregator-only discovery versus direct-source workflow.
- Falsifier: False claim/source receives acceptance or metadata access is treated as permission for full-text reuse.
- Non-proof: Citation count, consensus and retrieval availability are not scientific validity or copyright clearance.
- Dependencies: A-26, A-29, A-34, A-49
- Packet links: R-Q, R-W, R-H

### G-29 — The ARM-conversation F01–F24 fixtures and the matched direct-addressing evaluation were designed but not run.
Status: **open_room_fixtures_and_benefit_evaluation**. Leverage rank 27 within this ledger. Source: `docs/v3/research-lane/GAPS.md:75`.
- Current evidence: DS-15 F01–F24 and matched direct-addressing comparison remain unrun; R-J is correctly dedicated to terminal multi-agent exchange.
- Smallest discriminating decision/test: One room with two ARMs and an Owner interruption demonstrates exact target, Head awareness and one bounded coordinator lease; then matched direct-addressing comparison.
- Competitor/control: R0 direct interaction without shared-room coordination versus proposed R1 actor/authority contract.
- Falsifier: Room consensus changes accepted intent or a stale actor answer is adopted.
- Non-proof: Attributable chat exchange does not prove authority, better coordination or acceptance.
- Dependencies: A-04, A-09, A-10, A-25, A-26
- Packet links: R-J, R-L

### G-30 — The structured-vs-prose resume-error comparison and scheduler/daemon crash-recovery semantics were not run.
Status: **open_bounded_resume_state_and_scheduler_evidence**. Leverage rank 30 within this ledger. Source: `docs/v3/research-lane/GAPS.md:76`.
- Current evidence: Structured-versus-prose resume comparison and durable scheduler recovery remain open. Do not resurrect retired multi-repository executive/supervisor language.
- Smallest discriminating decision/test: Resume one explicitly authorized task from structured versus prose state after a crash and compare instruction loss, duplicate work and human reconstruction effort; restrict to bounded product jobs.
- Competitor/control: Current narrative status convention versus provenance-bound structured current/observed/question/evidence records.
- Falsifier: Restart duplicates an effect, renews authority or starts idle inference in lean profiles.
- Non-proof: A better status summary does not authorize multi-project autonomous supervision or prove persistent scheduler semantics.
- Dependencies: A-02, A-05, A-38, D-025
- Packet links: R-R, R-X

### G-31 — HITL synthetic fixtures are acceptance targets only; the Lazy-Stop observable boundary and the ten terminal controls remain undefined.
Status: **open_hitl_fixtures_stale_undefined_controls_claim**. Leverage rank 26 within this ledger. Source: `docs/v3/research-lane/GAPS.md:77`.
- Current evidence: The old statement that ten controls and Lazy Stop are undefined is stale at design level: INTERFACE-STRATEGY now names them and D-022 closes vocabulary. Observable per-adapter boundaries and synthetic acceptance still need evidence.
- Smallest discriminating decision/test: For a named route capability profile, map Lazy Stop to an observable operation boundary with deadline/escalation, then reject a stale correlated approval at that boundary.
- Conforming rival: Durable exact-action approval objects versus an already Owner-approved bounded policy with deterministic selectors and exact per-effect binding. Both must be eligible under the same confirmation policy, action/recipient/data scope, expiry/revision and receiver checks; where action-time approval is mandatory both obtain it.
- Negative controls, not eligible rivals: UI confirmation of an unbound prose summary; stale approval reused for changed action.
- Previous comparison preserved: Digest/revision-bound pre-effect approval versus UI confirmation of a prose summary.
- Comparison sources: ../rp/recommendations.json (RP-D06 / RP-R03)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A stale or wrong-recipient answer authorizes a changed action.
- Non-proof: Approval delivery and upstream hook invocation are not effect receipts or settlement.
- Dependencies: A-04, A-05, A-06, A-17
- Packet links: R-E, R-F, R-J, R-L

### G-32 — No Recursion-specific licensing/IP analysis exists; counsel review is required before any distribution, publication or training decision.
Status: **open_counsel_release_gate**. Leverage rank 15 within this ledger. Source: `docs/v3/research-lane/GAPS.md:78`.
- Current evidence: R-C/R-H prepare counsel questions. D-026 fixes Apache direction, D-027 authorizes packet preparation only and D-030 remains counsel-subject. No clearance or counsel contact occurs here.
- Smallest discriminating decision/test: Lucas supplies deployment/entity/account-tier and distribution facts, then obtains counsel answers to the scoped packet; technical research cannot close the legal gate.
- Conforming rival: Normalized per-profile counsel fact/disposition matrix versus independently complete case dossiers with indexed answers. Both cover every identical material account/entity/auth/mode/distribution variant, same required capability and counsel/technical gates; neither is legal clearance or a narrower release substitute.
- Negative controls, not eligible rivals: Excluded credential relay used as though it were an eligible delegation design; vendor-wide blanket permission.
- Previous comparison preserved: The same supported capability delivered through a narrower permitted operating mode; any alternative remains an Owner/counsel decision.
- Comparison sources: ../rh/report.md (Sections 2, 6 and 7)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Required route or distribution posture cannot be cleared for the intended facts.
- Non-proof: Prepared question packet, accepted product direction and open-source code license are not legal clearance.
- Dependencies: D-021, D-027, D-030
- Packet links: R-C, R-H

### G-33 — Decision-journaling R1-vs-R0 was not run; no optimal cadence or local calibration benefit is established.
Status: **open_decision_journaling_benefit_experiment**. Leverage rank 33 within this ledger. Source: `docs/v3/research-lane/GAPS.md:79`.
- Current evidence: DS-34 prospective R1-vs-R0 evaluation is unrun; no optimal cadence/local calibration improvement established. It extends the existing decision record, not a parallel authority log.
- Smallest discriminating decision/test: Preregister one bounded decision window comparing reconstruction, timely review and human burden without changing who decides.
- Competitor/control: Existing narrative D-entry convention R0 versus prospective forecast-and-review fields R1.
- Falsifier: Added process fails to improve prespecified reconstruction/review outcomes or increases burden past the agreed limit.
- Non-proof: More decision fields and retrospective confidence do not establish calibration benefit.
- Dependencies: D-017..D-033 remain authoritative, A-49, A-50
- Packet links: R-W
## Harness coverage

### H-01 — Codex / ChatGPT-OAuth
Status: **historical_fixture_evidence_current_profile_unqualified**. Leverage rank 1 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:25`.
- Current evidence: R-B §3.1 documents submit/steer/interrupt/resume/events. ROUTE-CAPABILITIES:9–34 and IPR evidence retain installed Codex 0.149.0 on Windows with scripted loopback Responses, zero actual model calls, simulated usage. HARNESS-COVERAGE uninstalled is only a file-local scope claim, not current repository-wide absence.
- Smallest discriminating decision/test: Pin first Codex App Server profile and reconcile thread/rollback versus thread/revert; bind a stale expectedTurnId, approval expiry and lost-response resume fixture to independent receipts.
- Competitor/control: Direct exact-build Codex plus manual explicit handoff; minimal adapter is ablation.
- Falsifier: Wrong turn steered, stale approval adopted, unsandboxed shell path treated as normal sandbox, or required version control unavailable.
- Non-proof: Old dummy-provider fixture does not qualify current managed ChatGPT auth, entitlement, strong credential isolation, all helper accounting or live model quality.
- Dependencies: D-023, A-17, A-25, A-33, A-46, G-32
- Packet links: R-E, R-F, R-H, R-D

### H-02 — Claude Code
Status: **documented_interfaces_unqualified**. Leverage rank 2 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:26`.
- Current evidence: R-B §3.2 has claude -p/SDK streaming, queue/interrupt/resume and limited rewind; proprietary internals stay partial. R-M studies terminal modding as adopt/port/avoid.
- Smallest discriminating decision/test: Bind exact CLI versus SDK modes and test one queued input through interruption plus one Bash mutation across rewind; record what rewind cannot restore.
- Competitor/control: Direct Claude Code/SDK with documented controls versus Recursion wrapper; no terminal mod package assumed safe.
- Falsifier: Adapter infers full workspace rollback, same-turn steering or queue crash survival from weaker interface evidence.
- Non-proof: SDK availability, output cost or modding claims do not prove full effect mediation, subscription entitlement or helper coverage.
- Dependencies: A-28, A-33, A-38, G-32
- Packet links: R-F, R-M, R-H, R-G

### H-03 — Cursor first-party
Status: **documented_split_profiles_unqualified**. Leverage rank 3 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:27`.
- Current evidence: R-B §3.3 distinguishes CLI/ACP, local/cloud SDK and hosted API. Non-stream JSON can omit tool history/failure terminal result; SDK restrictions may not persist on resume.
- Smallest discriminating decision/test: Pin one first-party profile and resume a bounded synthetic tool restriction while steering; retain complete_delivered versus revert_to_followup and evidence gaps.
- Competitor/control: Direct same first-party interface; independent adapter is separate comparator, not substitute profile.
- Falsifier: Resume drops restrictions, missing terminal JSON becomes success or hosted billing/auth is merged with local cached-auth behavior.
- Non-proof: Cursor editor checkpoint UI does not prove CLI parity; local loop does not imply credential-free or subscription auth.
- Dependencies: A-28, A-33, A-38, A-46, G-32
- Packet links: R-F, R-E, R-H

### H-04 — Cursor third-party
Status: **documented_third_party_adapter_distribution_open**. Leverage rank 8 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:28`.
- Current evidence: SOURCE-REGISTER/RCAP separate independent adapter from first-party Cursor; RCAP records adapter 0.9.1 pinned SDK 1.0.28 and unresolved modified-combination distribution.
- Smallest discriminating decision/test: Diff exact adapter/SDK contracts against first-party route for one steer/resume/tool callback; preserve absent semantics and provenance before any install.
- Competitor/control: First-party ACP/SDK versus independent adapter at same intended workflow.
- Falsifier: Adapter claims new SDK steering from an older dependency or redistribution assumptions fail provenance/terms review.
- Non-proof: Adapter Apache license does not license SDK modifications or prove account entitlement.
- Dependencies: A-28, A-32, A-56, G-32
- Packet links: R-F, R-G, R-H

### H-05 — Gemini / Google CLI
Status: **documented_cli_modes_unqualified**. Leverage rank 4 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:29`.
- Current evidence: R-B §3.4 documents headless/ACP and explicitly separates interactive hints with model acknowledgment; flag seam --acp versus --experimental-acp and mode-dependent permissions remain.
- Smallest discriminating decision/test: Pin exact Gemini CLI binary/profile; feed one permission-required action in headless Plan/ask mode and require explicit denied/unsupported receipt rather than interactive parity.
- Competitor/control: Direct exact-mode Gemini CLI; interactive mode only as separate control.
- Falsifier: Adapter labels headless denied action successful or omits acknowledgment/next-speaker helper usage.
- Non-proof: Successful CLI start and interactive docs do not prove headless permissions, steering or full accounting.
- Dependencies: A-25, A-28, A-46, G-32
- Packet links: R-F, R-D, R-H

### H-06 — Grok Build
Status: **source_documented_unqualified**. Leverage rank 5 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:30`.
- Current evidence: R-I owns source study; R-B §3.5 has ACP/headless, sessions and recent usage fields. RCAP source finds x.ai/interject queued response can ignore channel delivery result; status-line cost resets on resume.
- Smallest discriminating decision/test: Pin exact dispatcher and binary; test interject after receiver closes and resumed meter continuity with a synthetic stream.
- Conforming rival: A qualified explicit-state Recursion adapter versus direct use of the same exact Grok Build route with independently retained delivery, consumption and settlement records. Both use identical route/build/capabilities, task, current authority, full accounting and required evidence; a documented-but-unqualified control remains unknown in both arms. No route is qualified by this comparison.
- Negative controls, not eligible rivals: Queued at face value rather than witnessed consumption.
- Previous comparison preserved: Direct Grok Build plus explicit delivered-consumed receipts versus wrapper accepting queued at face value.
- Comparison sources: ../rf/report.md (per-route delivery/control qualification); ../rv/recommendations.json (V-R03 / V-R08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Queued input is silently stranded/re-targeted or process-local cost is treated as lifetime total.
- Non-proof: Open source, Apache direction or usage fields do not prove runtime delivery, distribution clearance or total accounting.
- Dependencies: A-28, A-32, A-46, G-32
- Packet links: R-I, R-F, R-G, R-D

### H-07 — Hermes Agent
Status: **historical_fixture_evidence_current_profile_unqualified**. Leverage rank 6 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:31`.
- Current evidence: R-B §3.6 documents gateway/ACP/HTTP differences, queued versus consumed steering and live question replay. Sept 7 IPR real-AIAgent loopback fixtures retain same-process persistence/interruption and metadata requests; original invalid history oracle is preserved.
- Smallest discriminating decision/test: Pin selected interface; crash owner with a pending question and queued steer, then require durable admission/rebind semantics or explicit unknown. Enumerate helper/metadata traffic.
- Conforming rival: Snapshot-bound recovery records versus query reconstruction from canonical events around the same exact real Hermes route. Both retain the same real-agent persistence path, current grants, request/waiter identities, independent observations, metadata/helper accounting and declared recovery boundary; neither substitutes a mock-agent seam.
- Negative controls, not eligible rivals: Synthetic mock-agent persistence seam used as proof of real-agent durable history.
- Previous comparison preserved: Direct same Hermes interface; synthetic mock-agent seam is an invalid substitute for real persistence.
- Comparison sources: ../rl/recommendation-register.json (C04); ../rf/report.md (Hermes profile and recovery limitations)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: Reconnect replay is promoted to crash-safe waiter state, row IDs survive destructive rewind by assumption, or helper fallback widens scope.
- Non-proof: Old same-process fixture is not fresh-process/live-provider qualification; Hermes repository executive role remains retired by D-017.
- Dependencies: D-017, A-25, A-28, A-33, A-46, G-32
- Packet links: R-F, R-E, R-D, R-G

### H-08 — OpenCode v1
Status: **v1_source_documented_unqualified**. Leverage rank 7 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:32`.
- Current evidence: R-B §3.7 and pinned generated types support server/events/abort/fork and cost fields. prompt_async 204 establishes asynchronous submission, not active-turn steering.
- Smallest discriminating decision/test: Pin v1 build; send prompt_async during a blocked turn and map accepted/queued/consumed while exercising pre-command shell-substitution boundary.
- Conforming rival: A qualified explicit-state Recursion adapter versus direct use of the same exact OpenCode v1 route with independently retained delivery, consumption and settlement records. Both use identical route/build/capabilities, task, current authority, full accounting and required evidence; a documented-but-unqualified control remains unknown in both arms. No route is qualified by this comparison.
- Negative controls, not eligible rivals: Assumed steering bridge that promotes asynchronous admission into active-turn steering.
- Previous comparison preserved: Direct OpenCode v1 server/CLI plus explicit queue versus assumed steering bridge.
- Comparison sources: ../rf/report.md (per-route delivery/control qualification); ../rv/recommendations.json (V-R03 / V-R08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: A 204 or pre-command hook becomes a universal effect fence or v2 behavior is attributed to v1.
- Non-proof: Versioned source/types do not prove installed v1 behavior, hook completeness, helper totals or entitlement.
- Dependencies: A-08, A-28, A-33, G-32
- Packet links: R-F, R-G, R-D

### H-09 — OpenCode v2
Status: **generation_unpinned_documentation_partial**. Leverage rank 18 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:33`.
- Current evidence: HARNESS-COVERAGE says v2 has no source pin; ST§4/plugin notes are partial. The R-B nine-route OpenCode profile cannot be assumed to establish v2.
- Smallest discriminating decision/test: Resolve an immutable v2 source/release/interface identity and document generation-specific changes before proposing any conformance trial.
- Competitor/control: Pinned supported v1 profile or no v2 eligibility until evidence exists.
- Falsifier: Claims borrowed from v1 fail on v2 or no stable referent/release can be established.
- Non-proof: A new-generation name, prompt_async mention or previous license does not establish v2 controls/terms.
- Dependencies: A-28, A-32, A-56, G-32
- Packet links: R-F, R-G, R-H

### H-10 — Antigravity
Status: **local_sdk_managed_profiles_documented_unqualified**. Leverage rank 12 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:34`.
- Current evidence: R-B §3.8 distinguishes cached-auth CLI, SDK and managed API. CLI stream-json is text-only, rejects control messages, graceful stdin close waits for turn; cumulative counters and soft-denial exit 0 require care.
- Smallest discriminating decision/test: Pin local CLI profile and feed a denied tool plus graceful close; preserve denied effect, still-running turn and cumulative accounting separately.
- Competitor/control: Direct same local CLI versus SDK/managed routes as separate profiles, never silent fallback.
- Falsifier: Exit 0 becomes successful work, close becomes active cancel or cumulative totals are summed as deltas.
- Non-proof: Local/managed branding does not unify auth, billing, modality, persistence or control guarantees.
- Dependencies: A-28, A-33, A-40, A-46, G-32
- Packet links: R-F, R-D, R-T, R-H

### H-11 — Pi
Status: **documented_rpc_unqualified**. Leverage rank 11 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:35`.
- Current evidence: R-B §3.9 documents steer/follow_up, separate abort controls and agent_settled; documented current session totals include compaction/branch summaries, with custom-handler usage possibly absent.
- Smallest discriminating decision/test: On pinned RPC fixture, allow agent_end before automatic continuation and issue composed abort; use agent_settled and independently reconcile custom-compaction usage.
- Conforming rival: A qualified explicit-state Recursion adapter versus direct use of the same exact Pi route with independently retained delivery, consumption and settlement records. Both use identical route/build/capabilities, task, current authority, full accounting and required evidence; a documented-but-unqualified control remains unknown in both arms. No route is qualified by this comparison.
- Negative controls, not eligible rivals: Generic end-event completion wrapper that equates agent_end with settled.
- Previous comparison preserved: Direct Pi RPC with explicit controls versus generic end-event completion wrapper.
- Comparison sources: ../rf/report.md (per-route delivery/control qualification); ../rv/recommendations.json (V-R03 / V-R08)
- Comparison evidence: inferred, unexecuted and unselected; no accepted capability or gate is removed
- Falsifier: agent_end is treated as idle/settled, a background bash/retry survives claimed full stop or usage exclusions are asserted without current profile evidence.
- Non-proof: Append-only sessions and no built-in sandbox do not prove safe embedding, filesystem rollback or helper completeness.
- Dependencies: A-18, A-28, A-33, A-46, G-32
- Packet links: R-F, R-D, R-U

### H-12 — Meta Muse Code
Status: **referent_documented_embedding_unknown**. Leverage rank 19 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:36`.
- Current evidence: Meta Muse Code referent/msp schema and UI are recorded in ST§4; plugin, legal and accounting cells remain unknown and it is outside R-C nine.
- Smallest discriminating decision/test: Pin official exact product/build and enumerate one submit/observe/cancel interface plus permission model from primary material; keep embedding unavailable if none is documented.
- Competitor/control: Native Muse interaction as UX reference versus supported programmatic integration.
- Falsifier: A terminal beta or schema fragment is presented as a complete embeddable delegation contract.
- Non-proof: Referent resolution and UI evidence do not establish plugin support, terms, quota or runtime qualification.
- Dependencies: A-28, A-29, A-32
- Packet links: R-F, R-G, R-H

### H-13 — DeepSeek Harness / Cordis
Status: **preview_ecosystem_documented_portability_unmeasured**. Leverage rank 10 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:37`.
- Current evidence: DeepSeek Harness/Cordis source and extension model are documented; developer-preview status and partial terms/accounting remain. D-033 explicitly calls for porting hypothesis validation.
- Smallest discriminating decision/test: Select one public representative plugin manifest and produce a loss/cost map for two target harnesses, with lifecycle and cleanup semantics explicitly tested later.
- Competitor/control: Native rewrite of the same plugin versus Cordis import/adapter.
- Falsifier: Port cost exceeds rewrite, required behavior cannot transfer, or disposal is mislabeled external rollback.
- Non-proof: Existing plugin count and shared TypeScript conventions do not establish cheap semantic portability or release readiness.
- Dependencies: D-033, A-30, A-31, A-32, G-32
- Packet links: R-G, R-U

### H-14 — T3 Code
Status: **operator_interface_baseline_not_routed**. Leverage rank 9 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:38`.
- Current evidence: T3 Code is source/UI documented and named comparison standard; route delegation and extension model are unknown in this matrix.
- Smallest discriminating decision/test: Use a pinned T3 workflow as strong user-effort/continuity baseline for one of D-024 journeys; map only observable behavior without inventing a submit API.
- Competitor/control: Direct T3 Code workflow versus Recursion CLI/TUI for same authorized task and artifact.
- Falsifier: Recursion does not improve verified continuity/human effort or baseline capabilities were understated.
- Non-proof: A GUI baseline is not a routed harness, legal entitlement or proof a new dashboard is novel.
- Dependencies: D-024, A-21, A-44, A-50
- Packet links: R-J, R-L, R-W

### H-15 — Goose
Status: **composition_precedent_documented_unqualified**. Leverage rank 13 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:39`.
- Current evidence: Goose source/extension/UI are documented; delegation is partial, accounting unknown and R-C appendix does not qualify a route.
- Smallest discriminating decision/test: Trace one public extension lifecycle and direct task-control flow, then specify a semantic-loss fixture for cross-harness reuse.
- Competitor/control: Direct Goose extension execution versus imported/translated plugin.
- Falsifier: Composition drops tool provenance/authority/lifecycle or adds hidden cost not present in direct execution.
- Non-proof: Composition precedent and source license do not prove interoperability, subscription access or Recursion qualification.
- Dependencies: A-30, A-32, A-46, G-32
- Packet links: R-G, R-F, R-H

### H-16 — Aider
Status: **git_first_baseline_documented_controls_unknown**. Leverage rank 15 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:40`.
- Current evidence: Aider source/route and license are documented; extension/delegation/accounting remain unknown in matrix.
- Smallest discriminating decision/test: Compare one bounded edit/review/source-recovery workflow against direct pinned Aider and catalog concrete control interfaces before considering an adapter.
- Competitor/control: Direct Git-first Aider workflow with explicit human review.
- Falsifier: Recursion overhead adds no accepted outcome/continuity value or assumes unsupported active steering/delegation.
- Non-proof: Git integration and source availability do not supply a general plugin or daemon control contract.
- Dependencies: A-28, A-44, A-50, A-54
- Packet links: R-F, R-W, R-Y

### H-17 — mini-SWE-agent
Status: **minimal_baseline_documented_contradictory_evidence_flagged**. Leverage rank 16 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:41`.
- Current evidence: mini-SWE-agent is a minimal baseline; source/license documented, conflicting evidence is explicitly flagged and plugin/delegation unknown.
- Smallest discriminating decision/test: Resolve the exact pinned variant and disputed claim, then compare one task with complete verification/retry costs rather than agent feature count.
- Competitor/control: Minimal direct mini-SWE-agent loop versus Recursion machinery.
- Falsifier: Claimed Recursion benefit vanishes under a strong minimal baseline or source/version contradiction remains hidden.
- Non-proof: Published benchmark result or minimal implementation does not prove local task fit or inherited adapter controls.
- Dependencies: A-44, A-49, A-50
- Packet links: R-W, R-O

### H-18 — OpenHands
Status: **durability_prior_art_documented_unqualified**. Leverage rank 14 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:42`.
- Current evidence: OpenHands source and delegation/durability prior art are documented; UI partial, plugin/accounting unknown in matrix.
- Smallest discriminating decision/test: Pin one documented session/failure recovery path and contrast artifact/authority/effect semantics against one Recursion lost-machine journey.
- Competitor/control: Direct OpenHands recovery workflow versus Recursion productive continuity.
- Falsifier: Recursion novelty claim duplicates equal/better baseline or source recovery is confused with effect settlement.
- Non-proof: Prior-art durability does not qualify Recursion store, credentials or plugin portability.
- Dependencies: D-024, A-13, A-28, A-50
- Packet links: R-F, R-W, R-X

### H-19 — Devin
Status: **historical_contributor_tool_not_adapter_qualified**. Leverage rank 22 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:43`.
- Current evidence: Devin appears in retired construction/external campaign records; proprietary source is not applicable, most route/control/legal fields unknown.
- Smallest discriminating decision/test: Decide from primary public interface evidence whether Devin is only a comparator/contributor tool or a supported integration candidate; do not reuse retired campaign authority.
- Competitor/control: Human-operated Devin workflow as comparator versus a documented approved API if one exists.
- Falsifier: Historical worker dispatch is cited as current adapter support, entitlement or autonomous fleet authorization.
- Non-proof: Campaign usage does not establish current account permissions, plugin model or route contract.
- Dependencies: D-017, A-28, A-29, G-32
- Packet links: R-F, R-H

### H-20 — Cline
Status: **sampled_excluded_source_partial**. Leverage rank 23 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:44`.
- Current evidence: Cline was sampled/excluded in frontier research; full UI/plugin/delegation/legal/accounting matrix is unknown.
- Smallest discriminating decision/test: Document exclusion rationale against one current relevant accepted workflow and pin any official interface before proposing additional scope.
- Competitor/control: Existing researched launch-critical routes and Cline direct UI as comparator.
- Falsifier: A sampled name is advertised as supported without control/authority/accounting evidence.
- Non-proof: Corpus inclusion/exclusion is not evidence of inferiority or unavailable capabilities.
- Dependencies: A-28, A-50, G-32
- Packet links: R-F, R-G, R-W

### H-21 — Command Code
Status: **name_only_unresolved**. Leverage rank 26 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:45`.
- Current evidence: Command Code appears as a PRODUCT example only; every substantive matrix field is unknown.
- Smallest discriminating decision/test: Resolve exact vendor/project/product and immutable official source from the intended referent before any capability claim; retain unknown if ambiguous.
- Competitor/control: No adapter admission until a concrete referent; known pinned comparator for current evaluation.
- Falsifier: Name similarity is used to infer code, license, auth or controls from another product.
- Non-proof: A product name is not evidence of an executable integration or user entitlement.
- Dependencies: A-28, A-29
- Packet links: R-F, R-H

### H-22 — Grok Bot
Status: **cloud_ux_reference_not_grok_build**. Leverage rank 25 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:46`.
- Current evidence: Grok Bot has source-documented cloud/UI references and partial delegation; source internals/plugin/legal/accounting unknown. It is distinct from Grok Build.
- Smallest discriminating decision/test: Pin one observable cloud UX workflow and disclose inaccessible control/accounting internals; compare only human-facing experience without borrowing CLI claims.
- Competitor/control: Direct Grok Bot interaction versus Grok Build only as explicitly different product.
- Falsifier: Grok Build license, usage or ACP support is attributed to Grok Bot.
- Non-proof: Shared brand or cloud UI does not establish programmable delegation or plugin reuse.
- Dependencies: A-21, A-28, A-50, G-32
- Packet links: R-J, R-F, R-H

### H-23 — SWE-agent
Status: **benchmark_loop_reference_documented**. Leverage rank 17 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:47`.
- Current evidence: SWE-agent source/interface/license documented; UI not applicable, plugin/delegation/accounting unknown.
- Smallest discriminating decision/test: Pin benchmark task corpus, exact agent revision and accepted outcome oracle before using as direct-loop baseline.
- Competitor/control: Direct SWE-agent on identical task/environment with complete retries/review cost.
- Falsifier: Comparison changes task permissions or omits costs/failed attempts and reverses apparent advantage.
- Non-proof: Benchmark-loop source does not prove interactive controls, subscriptions or general agent product parity.
- Dependencies: A-44, A-49, A-50
- Packet links: R-W, R-O

### H-24 — Continue / Roo Code
Status: **combined_sampled_row_requires_identity_split**. Leverage rank 24 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:48`.
- Current evidence: Continue / Roo Code are combined only as sampled/excluded IDE-overlap row; other fields remain unknown. They are distinct products.
- Smallest discriminating decision/test: Split referents into separately pinned source/interface records before any claim, while preserving why the original study excluded each.
- Competitor/control: Each direct IDE workflow separately, not an averaged combined product.
- Falsifier: Capabilities or license of one are transferred to the other.
- Non-proof: Combined matrix label is not a common adapter contract or proof neither can support a workflow.
- Dependencies: A-28, A-32, A-50
- Packet links: R-F, R-G, R-W

### H-25 — BYOK
Status: **native_route_category_not_product_unbuilt**. Leverage rank 20 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:49`.
- Current evidence: BYOK is a native-loop billing/auth category in RCAP/RM, not one harness; route controls partial, accounting unknown.
- Smallest discriminating decision/test: Define one synthetic native route with explicit key-owner boundary, provider/model/pool identity and null-aware usage, without entering real keys.
- Competitor/control: Direct explicitly authorized provider API/native minimal loop versus Recursion native route.
- Falsifier: Category hides provider-specific terms, account authority or separate helper spend.
- Non-proof: BYOK label is not credential authorization, integration implementation or universal provider support.
- Dependencies: A-04, A-28, A-33, A-46, G-32
- Packet links: R-E, R-F, R-H, R-D

### H-26 — ChatGPT sign-in (SiWC)
Status: **restricted_preview_candidate_not_qualified**. Leverage rank 21 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:50`.
- Current evidence: SiWC is separately referenced in ST§4/R-C O5; source/integration/accounting incomplete and preview constraints explicit. It is not interchangeable with existing Codex ChatGPT OAuth.
- Smallest discriminating decision/test: Establish current eligibility, distribution mode and exact auth boundary through public evidence/counsel packet before admitting any route; no login or token handling here.
- Competitor/control: Source-documented Codex managed-auth candidate, subject to its own eligibility and qualification, versus separately restricted sign-in integration.
- Falsifier: Preview assumptions fail eligibility or implementation requires ungranted token custody.
- Non-proof: Brand sign-in, SDK or documentation access does not grant preview enrollment or service entitlement.
- Dependencies: D-021, A-29, A-33, G-32
- Packet links: R-C, R-H, R-E

### H-27 — Perplexity
Status: **prospective_research_comparator_only**. Leverage rank 27 within this ledger. Source: `docs/v3/research-lane/HARNESS-COVERAGE.md:51`.
- Current evidence: Perplexity is only a prospective research-quality comparator in PRODUCT; all other columns unknown. No route or plugin promise follows.
- Smallest discriminating decision/test: Specify one public/synthetic evidence-quality comparison with independently verified sources and identical rights constraints; do not assume a programmable adapter.
- Competitor/control: Direct Perplexity research workflow versus Scientific Research ARM, plus direct-source baseline.
- Falsifier: Recursion does not improve verified evidence/effort or comparator output is treated as authoritative truth.
- Non-proof: A research comparator name is not route legality, API entitlement, plugin support or performance evidence.
- Dependencies: A-43, A-49, A-50, G-32
- Packet links: R-W, R-H
