# Recursion: architecture and gap-closure evidence audit

Source snapshot: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Audit date: 2026-10-02 UTC  
Status: read-only evidence reconciliation and proposed discriminating work; not qualification, an accepted architecture change, or permission to execute

## Bottom line

The current tree contains substantially more than empty specifications, but substantially less than a qualified v3 harness. Preserve both sides of that statement.

1. G-03 and G-04's original absence claims are stale. Committed formal models, raw TLC output, OS fixture catalogs and bounded historical observations exist. Neither gap is closed
2. G-06, G-07 and G-11 remain closed Owner decisions. Their implementations and platform profiles remain unqualified; that is a different state
3. FU-03 records five kills among seven diagnostic mutants. The executed baseline is limited to four fresh command IDs. Its current mutation sites are not automatically the exact full FU-03 registry, and the two surviving diagnostics are not accepted reachability/equivalence classifications
4. FU-04's current raw file contains 13 run rows: 12 pass, 0 fail and 1 unknown, plus 10 not-run rows. Those runs cover 10 unique PF IDs. The index's 13 not-run figure is stale. The recorded passes establish narrower mechanisms than several trace titles imply
5. The final R-P…R-Y mapping in ARCHITECTURE-COVERAGE is substantially wrong. Exact titles give P injection, Q memory, R autonomy, S adaptation, T multimodal, U isolation, V replay, W evaluation, X node fabric and Y workspace
6. No accepted D-018…D-033 choice is reopened. No language, store, renderer, framework, sandbox, provider or second stress-test adapter is selected

The complete companion ledger covers **57 architecture edges, 33 gap rows and 27 harness/product rows**. Every row has current evidence, current status, a smallest discriminating decision/test, competitor/control, falsifier, non-proof, dependencies and a relative leverage rank. The machine-readable mapping covers all 21 actual briefs. See `complete-ledger.md`, the three `*-ledger.json` / `*.csv` pairs, and `packet-mapping.json` / `.csv`.

## Scope and evidence rules

The audit read CONTROL_PLANE, ANCHOR, active v3 goal, D-017…D-033, START-HERE, RESEARCH-INDEX, ARCHITECTURE-COVERAGE, HARNESS-COVERAGE, GAPS, SYNTHESIS, PRODUCT, INTERFACE-STRATEGY and PLUGINS-AND-EDITIONS. It inspected the exact current FU-03/FU-04 source and recorded artifacts, the actual titles of the 21 frontier briefs, R-B/reconciliation material and the historical installed-interface overlay. `source-manifest.json` fingerprints 98 relevant source files.

The supplied commit is the authority snapshot. File hashes bind the bytes inspected; they are not signed execution attestations. Original source research is treated as **repository-recorded source documentation**, not freshly reverified public fact. Historical `locally-observed` and `modeled` labels are preserved as recorded evidence and never presented as measurements reproduced by this audit. The proposed tests and dependency rankings are audit interpretations. Eligible rivals must preserve the same accepted capability, authority, safety, accounting, evidence, platform and release gates. The comparison fields distinguish conforming design/evidence alternatives from retained deliberately failing negative controls; neither is selected or executed. Mature E–Y contract proposals ground the repaired alternatives, with separate artifact pins in `comparison-source-manifest.json`.

No repository tests, TLC/model checks, OS probes, harness/model/provider calls, installs, credentials, account actions, host resets, live hosts, spend, counsel contact or repository edits occurred. Small local scripts only parsed, counted, hashed and rendered the already-supplied artifacts into this report directory.

The author's own PASS is not independent acceptance. A candidate can have useful bounded observations while failing qualification. Conversely, an unqualified result must not be rewritten as “nothing exists.”

## 1. Authority, closed decisions and remaining drift

CONTROL_PLANE:14–24 puts the current explicit Owner instruction above repository documents. CONTROL_PLANE:10–12 and ANCHOR retire the Hermes-led repository control plane; the active goal is `goal-recursion-v3-harness-orchestrator`. Product-level Head/ARM concepts are not permission to restore a standing repository executive.

### Preserve closed choices

| Gap | Accepted decision | Closed question | Still requires evidence |
|---|---|---|---|
| G-06 | D-020, DECISIONS:87 onward | Automatic takeover is required/toggleable, through a first-party availability plugin over a single-node fenced core; no default consensus | Store seam, receiver fences, split-brain refusal, election/replication behavior and failover recovery |
| G-07 | D-022, DECISIONS:132 onward | One vocabulary: Aggressive / Full / Lazy plus checkpoint / interrupt / drain | Exact config/model/broker mapping; per-effect observable boundaries; descendant, remote and ambiguous-effect settlement |
| G-11 | D-028, DECISIONS:240 onward | Windows/Linux floors, WSL dev/test, local NTFS/ext4, SMB/NFS exclusion and abrupt-VM-reset durability definition | Exact profile keys, qualified mechanisms and retained native traces |

A new failure against those requirements is implementation evidence or a named feasibility issue. It does not quietly turn a settled scope question back into an open Owner choice.

### Drift that needs a reviewed documentation correction

- **START-HERE:41–43** still says an operative Hermes constitution survives and the amendment remains only a proposal. CONTROL_PLANE and D-017 supersede this. **START-HERE:83–87** may preserve the v2 parent as historical campaign lineage, but it cannot supply the parent goal for current work. **START-HERE:96–99**'s “existing supervisor” language also needs retirement-context labeling
- **SYNTHESIS** correctly describes the original 28-lane freeze. Its “no model check/no measured cells” statements remain historical descriptions of that wave, not a current repository-wide inventory. Its availability/stop/platform question list must link to closed D-020/D-022/D-028 dispositions
- **GAPS:34–35** says formal-model and OS artifacts do not exist. Replace current status with partial recorded evidence, retaining the original statement as dated history. **GAPS:77** says ten controls and Lazy Stop are undefined; INTERFACE-STRATEGY now defines them at design level, although route conformance is open
- **D-031** controls present positioning. D-018's earlier vendor-intent hypothesis is historical reasoning, not a surviving marketing/research claim to establish intent with resource measurements. Workload savings can be measured; sabotage intent cannot be inferred from them
- **GUI construction order and release timing are separate.** The current TUI-first/GUI-later direction sets construction order. D-019 includes GUI among first-release built-opt-in capabilities, while ANCHOR, PRODUCT and INTERFACE-STRATEGY contain later-GUI wording. This audit removes neither GUI capability nor any D-019 first-release opt-in obligation. Preserve the shared command/query design and record the release-timing tension explicitly; obtain Owner clarification if its interpretation would change a release gate. Do not revive the rejected smaller overall release by implication
- PRODUCT:213 retains “current immediate PAUSE remains operative”; present behavior must instead be reconciled with accepted D-022. PRODUCT:219 names SQLite in a performance statement although the store is unselected. PRODUCT:222's v2 comparison can be historical research baseline only, never a greenfield runtime/migration dependency
- `platform-floors.json` uses the misleading key `also_qualified` for Windows Enterprise. The same artifact explicitly says qualification is none and maps native Windows to `in_scope_unqualified`. Read it as an additional qualification target, not certification

One further coverage limit: DS-29 is referenced by ARCHITECTURE-COVERAGE, but this snapshot contains its construction-fleet prompt and no returned DS-29 lane file under research-lane. CONSTRUCTION-RUNBOOK is historical proposed campaign procedure, not evidence of a qualified product worker fleet. The ledger narrows edge 11 accordingly.

No protected or unprotected repository file was edited. The next editing session should preserve lineage and propose narrowly scoped replacements rather than deleting inconvenient prior reasoning.

## 2. Correct research-packet ownership

The titles below come from each actual file's H1. The JSON mapping includes exact path, digest and related edge IDs.

| Brief | Actual subject | Principal architecture edges |
|---|---|---|
| R-E | Operator-provisioned trusted launch boundary | 33; authority/fencing interfaces 4/5/8/35 |
| R-F | Harness-native headless delegation and high-volume fan-out | 28/38; broker/accounting 17/46 |
| R-G | Importing plugin ecosystems and cross-harness reuse | 30/32; isolation/MCP 31/39 |
| R-H | Counsel-ready caller-of-the-CLI operating mode | 29/56 |
| R-I | Open-source Grok Build source study | 28/32/56, source-informed UI comparison |
| R-J | Terminal multi-agent communication and parallel-tab experience | 19/20/24/25 |
| R-K | Terminal multiplexer and transformative TUI | 19/20/23 |
| R-L | Unified CLI/TUI/GUI command-and-query model | 21/22/55 |
| R-M | Claude Code terminal modding: adopt, port or avoid | 20/32 |
| R-N | Graphical client over the same command/query model | 21/23, later timing |
| R-O | Backend performance and configurability | 15/44/46/47/57 |
| R-P | Prompt injection and untrusted-input defense | 34, plus authority/ingress boundaries |
| R-Q | Durable memory and knowledge | 27; context/privacy 26/36 |
| R-R | Long-horizon autonomy and scheduling | 16/42; bounded planning 41 |
| R-S | Adaptive optimization and outcome learning | 45; routing/performance feedback |
| R-T | Multimodal I/O and attachments | 40; context/privacy/accounting |
| R-U | Sandbox runtime isolation and supply chain | 31; containment/launch 18/33 |
| R-V | Observability, introspection and replay debugging | 22/47/48 |
| R-W | Harness evaluation and benchmark science | 49/50; canary 37 |
| R-X | Node fabric and remote execution protocol | 53; leases/fences 5/8/10 |
| R-Y | Workspace and repository graph | 54; source forks 10 |

ARCHITECTURE-COVERAGE:123 onward incorrectly assigns workspace to P, multimodal to Q, replay to S, adaptation to T, accessibility to U, MCP to V, injection to W and quarantine/fencing to Y. R is aligned; X intersects leases but its actual scope is broader node fabric.

Correcting ownership is not closing the edges. Accessibility has R-K/R-N coverage. MCP still lacks a single dedicated R-E…Y lane, though FU-05/R-F/R-G/R-U cover pieces. The overnight `../protocol-edges/report.md` adds an eight-primary-source review and ten **unexecuted** MCP fixtures. Quarantine and per-adapter fencing likewise require explicit cross-lane ownership rather than pretending the workspace packet owns them.

## 3. FU-03: what the committed evidence does establish

### Raw recorded outcome

| Model or mutant | Raw result | Scope |
|---|---|---|
| RKernel | 727 generated / 727 distinct; no error recorded | Reduced diagnostic model |
| Original RMutant M02 | ChainIntegrity violation; 20 generated | First diagnostic mutation |
| RIntegrated | 38,837 generated / 34,625 distinct; no error recorded | Integrated-style, still reduced |
| M02 | ChainIntegrity; 30 generated | Killed diagnostic analogue |
| M03 | **TypeOK**; 2 generated | Killed; README's ChainIntegrity label is wrong |
| M04 | NoDuplicateIds; 30 generated | Killed diagnostic analogue |
| M16 | PauseNoProgress; 786 generated / 750 distinct | Killed diagnostic analogue |
| M26 | VerifierSafety; 14,252 generated / 13,334 distinct | Killed diagnostic analogue |
| M25, M31 | No error; same 38,837 / 34,625 counts as baseline | NOT_KILLED_WITHIN_BOUND, not accepted equivalence/reachability classifications |

The raw outputs and JSON agree on those numbers. All seven current mutant module byte digests match the recorded digests, and static comparison shows each current module equals the current baseline with its recorded one-site textual edit and module rename. This establishes artifact consistency, not faithful implementation of every full-spec mutation.

TLC 2.19 / tla2tools v1.7.4 and the JAR digest are recorded. This audit did not run or independently verify the checker/runtime. Detailed receipts and static comparisons are in `fu03-static-evidence.json`. Its initial run-summary copy is explicitly normalized: personal executable/capture paths are omitted, while repository-relative artifact locators, the original source-record hash and command fingerprints are preserved. It is not presented as a verbatim source record.

### Bound and semantic limitations

`RIntegrated.tla:15–17` says `CmdIds=1..4`, `MaxEvents=6`, `Cap=2`; the header at line 6 saying `1..6`/`16` is stale. Each baseline transition consumes a fresh command ID through `Fresh` and `AppendEvent` (37, 51–57). Thus the baseline cannot take more than four accepted transitions. A nominal six-event cap does not establish six-event reachable behavior. The M04 mutant intentionally changes the fresh-ID rule.

The full candidate requires an integrated 20-event/20-ID state space, independent reference/replay/projection monitors, packet derivation, authority dimensions, complete classified mutation registry, RCV1/JCS corpus and independent implementations. Current code explicitly omits those (RIntegrated:8–10). `CHECK_DEADLOCK FALSE` and no fairness/liveness specification also preclude a progress claim.

Keep three different findings separate:

1. **Incidental/structural detection:** M03 is genuinely killed in this diagnostic model, by TypeOK. That does not establish a full-spec ChainIntegrity or independent replay monitor
2. **Registry-semantic mismatch:** the candidate FU-03 registry (raw specification:252–310) defines M02 as deleting predecessor validation; the diagnostic changes event construction. M03 changes `+1` to `+2` rather than weakening equality to `>=`. Candidate M25 changes recovery requeue, while the diagnostic removes `RetryEffectOK`. These are useful fault analogues, not automatically exact registered instantiations
3. **Insufficient exposure/classification:** M25's Retry cannot be reached under four IDs. GrantLease → Start → SubmitFail → ArmTimer already consumes all four before FireTimer and Retry. M31 never reaches its distinguishing full-queue enqueue in that run. In the simplified model, one effect/at most two attempts also appears to limit dispatch appends to two; that inference needs explicit exposure/equivalence classification, not a blanket “larger bound fixes it” assumption

The candidate acceptance denominator is 36/36 rows classified, with every reachable nonequivalent fault killed and no survivor/inconclusive row. A kill ratio over seven instantiated diagnostics is not that metric. The remaining 29 are uninstantiated here, not passed.

### Candidate seven-step witness, explicitly outside the executed bound

Source-level reasoning suggests a baseline invariant conflict if the existing simplified model is enlarged to at least seven fresh IDs and seven events while preserving all other semantics:

1. GrantLease(w1, id1): owner w1, lease 2
2. Start(id2): Running, attempt 1
3. PrepareEffect(id3): effect Prepared
4. MarkDispatch(id4): effect InFlight, outbox length 1
5. SubmitFail(id5): Failed while effect remains InFlight
6. ArmTimer(id6): Armed; no effect-status guard
7. FireTimer(id7): retryReady true while effect remains InFlight

At step 7, `NoBlindEffectReplay` (RIntegrated:271) requires retryReady false. This is **an inferred candidate in an enlarged state space, not a counterexample to the executed four-ID/six-event run**, and not a claim about the richer candidate specification. No Retry or M25 edit is needed. `fu03-candidate-witness.json` records every precondition, state change and source line so an authorized independent session can reproduce or falsify it.

Do not silently weaken the invariant or unrelated guards to manufacture a kill. First reconcile what the intended contract prohibits: armed/fired retry readiness, actual repeat dispatch, or recovery requeue. Raising limits without this semantic review could expose a baseline defect rather than improve mutation coverage.

### Gate strength

`check_fu03_mutants.py` checks clean-baseline text, reported JAR digest, receipt counts and reported expected/actual invariant names. Its docstring's assertion about exact single-site edits exceeds what the checker itself recomputes. It does not recompute source hashes, compare each mutation, inspect every raw trace, validate complete reference-monitor independence, or rerun TLC. The audit's separate seven-file byte comparison is useful but cannot replace those acceptance obligations.

Smallest next discriminator: reconcile mutation identity and intended timer/effect semantics, add independent monitor/exposure predicates, reproduce the proposed bounded witnesses, then build up the exact full corpus. A new mass benchmark or language choice before that is lower leverage.

## 4. FU-04: raw counts, actual mechanisms and oracle limits

### Count reconciliation

`traces/traces_results.json` currently contains:

- 13 run rows: 3 host and 10 WSL rows
- 12 recorded pass, 0 recorded fail, 1 unknown
- 10 distinct PF IDs exercised: nine have pass outcomes, PF11 remains unknown
- 10 not-run rows: PF03, PF07, PF12, PF14–PF20
- Four separate safe host probes in `results/probes.json`; these overlap mechanisms and must not be added as four new qualified platform cells
- Zero qualified platform profiles

PF04, PF06 and PF08 each have both host and WSL rows, explaining why 13 run rows represent only 10 trace IDs. The index's “13 not_run” at RESEARCH-INDEX:76 is stale. No missing or unknown case is a zero failure. `fu04-static-evidence.json` preserves per-row observed support and limits.

D-028 scope is closed. The historical machine manifest intentionally remains `proposed_unexecuted`, `pending_owner`, with null profile keys; `check_fu04.py` enforces that legacy state. The separate accepted floors file now carries scope dispositions. Treat these as historical proposal versus present chosen scope, not an unanswered Owner platform decision. Missing exact profile qualification remains a real blocker.

### Narrow each recorded pass to its checked mechanism

| Recorded case | Support visible in source/receipt | Claim that remains unproved |
|---|---|---|
| PF01 WSL | Process-group membership, deliberate setsid escape, explicit cleanup | Preventing escape; full cgroup/causal descendant containment |
| PF02 WSL | Live unregistered orphan and explicit cleanup | Canonical new-epoch launch reconciliation; handler's “new epoch” is not implemented as an authority protocol |
| PF04 host | Bounded anonymous-pipe output and eventual child exit | ConPTY; witnessed blocked state; complete terminal scope/loss semantics |
| PF04 WSL | `script`-generated PTY output and group teardown | A stopped consumer at a witnessed output-blocked point; retained endpoint lifetime contract |
| PF05 WSL | TERM-ignoring group, later KILL and surviving separate sentinel | Windows console events; full handler-receipt trace; external settlement |
| PF06 host | Application-visible fsync/replace, B content and non-atomic name-gap control | Any actual writer crash, VM reset or durable application replay |
| PF06 WSL | Forty post-kill file-size observations and gap control | Byte/hash integrity, exact crash-cut witness, VM reset or acknowledged replay |
| PF08 host | Lock contention and explicit release/reacquire | Overlapping/mapped bypass or owner-death release; offset-5 write is outside the locked byte |
| PF08 WSL | Advisory flock, direct-write bypass, owner kill and reacquisition | Monotonic canonical receiver fence or complete storage writer mediation |
| PF09 WSL | Forced numeric PID reuse with different starttimes | A real adapter rejecting a delivered stale cancellation/completion |
| PF10 WSL | Recorded ENOSPC, preserved predecessor, later successful write | Flush/replace error protocol or independently witnessed durable acknowledgment |
| PF11 WSL | Bounded address-space refusal; native throttle unavailable | Native memory.high/OOM qualification; correctly retained unknown |
| PF13 WSL | Sequential mkdir ownership and manually written epoch 2 | Concurrent supervisor race, receiver-side stale epoch rejection, monotonic store |

Important exact anchors:

- `run_traces.py:81–82,654–665`: scripts emit `trace_end=1`; `flag` accepts only “true.” All ten WSL rows therefore have `fault_triggered=false`. This is a telemetry bug, not evidence that no physical condition was triggered. Preserve raw observations and validate fault activation separately
- `run_traces.py:195–227`: PF04 WSL keeps `script` logging and redirects output to `/dev/null`; it does not implement the catalog's blocked-consumer experiment
- `run_traces.py:677–724`: PF04 host uses an anonymous pipe, explicitly records that ConPTY was not exercised, and treats `p.poll() is None` as blocked although that only establishes the child has not exited
- `run_traces.py:254–305`: PF06 WSL reads file size, not bytes/digest. Equal-size corruption/mixed content can pass this oracle; the exact before/after flush/rename cut is not independently evidenced
- `run_traces.py:777–825`: PF08 locks one byte at offset 0 and writes offset 5. That is an allowed out-of-range write, not evidence of overlapping or memory-mapped bypass
- `run_traces.py:418–449,634–650`: PF13 uses `mkdir`, despite catalog bounds saying flock. It calls mere delayed-file existence `delayed_epoch1_fenced=true`, then the handler does not even use that field. No stale command is applied to a receiver that checks an epoch
- PF10 infers refusal from nonempty `dd` stderr, which may include ordinary success statistics. This particular retained receipt contains an ENOSPC message; the general oracle still needs exit/error-code semantics. `no_false_ack=true` is scripted, not an independent acknowledgment witness

### Artifact gate is not trace conformance

`check_traces.py:105–120` verifies that recorded pass rows have non-timeout status, true observation/recovery booleans and nonempty evidence. It does not require a true independently evidenced fault trigger, successful negative-control evidence, the claimed native mechanism, complete causal inventory, or digest-bound source/target identity. `check_fu04.py` checks manifest shape, file existence and safe-probe counts; its “no fabricated result” wording is stronger than such checks can independently establish.

The runner merges old target rows by `(id,target)` while top-level invocation records only the latest run (`run_traces.py:925 onward`). Thus a host/non-destructive invocation header alongside WSL destructive rows is expected merging behavior, not proof of unauthorized activity. It does mean an accepted corpus needs per-row immutable run identity, timestamp, candidate/config/profile hashes and independent verification.

The kickoff probe file's old PF IDs/titles also differ from the normalized catalog. For example its PF08 means disk-full while normalized PF08 means lock lifetime. A versioned catalog/ID crosswalk is required; do not sum or overlay those lists by bare ID.

Smallest next discriminator: fix/review receipt provenance and fault/oracle definitions first; then test the actual native mechanism on an approved disposable exact profile. Keep PF07 scoped to D-028's abrupt VM reset, not an unrequested physical-power program; do not treat excluded SMB/NFS or compatibility-shell variants as newly mandatory production scope.

## 5. Preserve older limited evidence without upgrading it

HARNESS-COVERAGE's “documented, uninstalled” Codex label cannot be a repository-wide current fact. ROUTE-CAPABILITIES:9–34 records historical installed Codex 0.149.0 and Hermes loopback fixtures. Their evidence file contains 15 retained runs, four labeled `accepted-scoped-evidence`, plus failed/invalid/earlier attempts and a retained release-control deviation. The failed initial Hermes history oracle remains failed; it was not erased by later real-agent observations.

Relevant bounded findings include:

- Codex same-connection steering/question/late-answer/fork/idle-server resume fixtures, with scripted provider usage and no post-resume inference/in-flight crash recovery
- Hermes real-agent same-process close/resume persistence; five local detection GETs plus one catalog GET; an interrupted second scripted POST with no final usage report, which remains unknown consumption
- IPR-001's one-build Windows creation-time Job observation and post-creation association orphan hazard; this is useful older containment evidence, not universal Job or FU-04 qualification
- IPR-007's 45,024 finite recipient-fence/consultation schedules and 16 deliberately broken guard variants, explicitly without aggregate/broker refinement or product integration

`historical-interface-evidence.json` retains those source labels and limits. None establishes a currently installed tool, current authenticated route, live provider result, entitlement, full OS qualification or productive-continuity advantage. R-B's October source map is fresher documentation but still does not replace exact-build conformance.

Harness classification matters: BYOK is a category; SiWC is a separate restricted-preview candidate; OpenCode generations must not be mixed; Cursor first-party and third-party paths differ; Grok Bot is not Grok Build; Continue and Roo are two products in one historical row; T3/Perplexity are comparators rather than automatically routed engines. The 27-row ledger preserves all those distinctions.

## 6. Highest-leverage closure sequence

These are dependency/risk recommendations for future bounded sessions, not a new release cut or approval to execute.

1. **Reconcile evidence identity and documentation.** Correct stale row states, exact packet ownership, raw counts and capability-versus-qualification labels. Preserve accepted decisions and older scoped results. This is inexpensive and prevents all later work from consuming false prerequisites
2. **Make the deterministic kernel falsifiable.** Reconcile mutation semantics, independent reference state, reachable controls, the seven-step candidate and byte/refusal corpus. FU-01 cannot turn reputation into a language decision before its shared corpus exists
3. **Qualify actual native OS mechanisms and receiver fences.** D-028 already sets scope. Profile-keyed launch/containment, epoch rejection, crash cuts and VM-reset replay evidence feed store and broker work. WSL remains a separate dev/test case
4. **Compare canonical-store and broker candidates on the same oracle.** No store/runtime winner follows from research. Close the four broker semantic blockers and preserve unknown external effects across ACK/retry/reconnect
5. **Reconcile R-A/R-B shared semantics, then Codex-first conformance.** Admission, current grants, attenuation, operation/attempt IDs, stop vocabulary, profile identity, losses and accounting must compose. Use the provider-free H1 stage before separately authorized real-binary/account stages; do not choose a second vendor here
6. **Measure total productive continuity against strong baselines.** T3/direct harness/minimal orchestrator comparisons need frozen tasks, quality floors, all-role/retry/review costs, missing-counter handling and accepted margins. Savings remain workload-specific; no vendor-intent inference
7. **Validate cheap porting, inert optionality and broader capabilities.** D-019 remains comprehensive/opt-in; D-033 permits a zero-acceptable-port outcome. Every import needs a semantic loss/cost map versus native rewrite. Later UI, memory, multimodal and adaptation work consumes the same authority/evidence contracts rather than inventing parallel state
8. **Keep counsel an independent release gate.** The packet can be made ready; Lucas supplies deployment/tier/entity facts and engages counsel. Source licenses and CLI delegation architecture are not clearance

Every resumed implementation session should bind a source commit, allowed paths, exact experiment/configuration and independent oracle, with its authorized environment, finite budget, stopping conditions and evidence-retention location. It should keep source documentation, recorded local behavior, inference and unknown separate. Neither this report nor its numerical completeness check supplies execution authorization.

## Deliverable index

- `complete-ledger.md`: full human-readable 117-row ledger
- `architecture-ledger.json` / `.csv`: 57 architecture edges
- `gap-ledger.json` / `.csv`: 33 gaps, including the three closed Owner decisions
- `harness-ledger.json` / `.csv`: 27 harness/product/category rows
- `packet-mapping.json` / `.csv`: all 21 exact brief titles, file hashes and corrected edges
- `fu03-static-evidence.json`: raw-count reconciliation, seven source/receipt comparisons and model/gate caveats
- `fu03-candidate-witness.json`: explicitly enlarged, unexecuted seven-step witness with every guard
- `fu04-static-evidence.json`: all 13 recorded runs, 10 not-run rows, scope and oracle limits
- `historical-interface-evidence.json`: preserved older scoped evidence and failed-attempt limits
- `source-manifest.json`: 98 repository file identities for reproduction of this static audit
- `comparison-source-manifest.json`: 18 separately pinned E–Y research artifacts grounding conforming rival proposals; no qualification or selection follows

No DOCX was created. The JSON/CSV/Markdown files are the requested reviewable source deliverables.
