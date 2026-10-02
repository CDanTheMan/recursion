# R-F provider-free delegation/fan-out falsification handoff

**Status: UNEXECUTED.** This is a test specification, not an implemented adapter, installed harness, test run or authorization to start one.

Parent goal: `goal-recursion-v3-harness-orchestrator`  
Source basis: repository `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Evidence date: 2026-10-02 UTC  
Recommendation binding: RF-R1 through RF-R8 in `report.md` apply; each has a competing option, decisive falsifier and explicit non-proof.

## 1. Claim, scope and prerequisites

Claim under test: a deterministic canonical controller can delegate to a synthetic headless harness, fan out within a fixed parent grant, preserve all attempts/uncertainty, stop within the requested D-022 scope, and settle simulated effects without creating another canonical writer.

The test may falsify that contract. It cannot prove real provider/harness correctness, high-volume subscription entitlement, credential isolation, network ownership, model quality, quota savings, installed-binary conformance or D-028 physical process/crash guarantees.

Before any future execution, the Owner-approved task must name a candidate commit/digest, allowed implementation/artifact paths, disposable provider-free environment, finite runtime/resource budget, exact gate entrypoint and an independent verifier. Implementation must not edit protected repository paths. Do not improvise a test command against current software from this document. No language, framework, store, sandbox or transport is selected.

Excluded: actual Codex, Claude, Cursor, Gemini, Grok, Hermes, OpenCode, Antigravity or Pi process; network listener/egress; provider/model request; real plugin or MCP/ACP server; credential files/environment/keychain; destructive host operation; package installation; account login; VM reset; paid route. A subprocess-based mock is optional later, not required for the first state-machine suite and not permission to run a real CLI.

## 2. Synthetic components and logical endpoints

Use deterministic, independently authored components with explicit inputs:

1. Canonical writer: admits a frozen grant, reservations and attempt lineage; applies only canonical events
2. Trusted launch stub: claims stable spawn_intent IDs, issues incarnation receipts, and enforces the synthetic process/egress/secret boundary
3. Harness stub: accepts input records; emits deterministic native-like JSON, stderr, control receipts and synthetic child events; no model logic
4. Effect receiver: records target versions and non-idempotent counters separately from harness state; supports receipt loss without loss of the actual effect
5. Collector: bounds/decodes input, records raw evidence and correlation, separates stdout from stderr
6. Independent oracle/verifier: derives expected state from fixtures and receiver truth, not from candidate reducer output

Logical endpoints: admit, spawn, submit, steer, queue, interrupt, checkpoint, drain, observe, effect.prepare, effect.commit, effect.query, settle, fan_in. These are message labels inside the synthetic experiment. None is an HTTP URL or a product API selection.

Inputs and outputs are records with schema_revision, logical_operation_id, wire_attempt_id, parent/child attempt IDs, grant reference, epoch, native correlation, virtual_tick, event_sequence and a bounded payload. Request IDs are unique per wire attempt; logical IDs persist across safe retries. No secret or credential-derived hash appears.

Scripted output record types: launch_receipt, admission_ack, admission_rejected, queued, delivered, child_spawn, child_end, message_delta, tool_start, effect_intent, effect_receipt, usage_snapshot, usage_delta, usage_reset, interrupt_receipt, terminal_result, process_exit, checkpoint_receipt, replay_gap, protocol_error. Native-inspired scenarios must label their profile and documentary source; they do not claim byte-for-byte vendor fidelity.

## 3. Determinism and finite dimensions

Use virtual time and explicit barriers. Wall-clock sleeps and random live scheduling cannot choose the acceptance outcome. A seeded schedule may enumerate interleavings, but every generated trace must be retained with its seed and exact schedule, and critical boundary schedules must also be explicit fixtures.

Proposed **fixture values only**, not product defaults or evidence of capacity:

- 1 canonical writer, 1 primary parent, 4 required work units
- active launch limits of 1, 2 and 4 across comparator arms
- tree-depth values 0, 1 and 3; maximum total admitted child intents 16
- parent synthetic resource allowance 100 units; explicit child reservations whose sum cannot exceed 100
- maximum 2 safe retries per logical operation; ambiguous admission is not automatically retryable
- maximum queue 16, outstanding waiters 8, frame size 8192 bytes, JSON nesting 16, retained raw-output budget 262144 bytes, virtual lifetime 1000 ticks
- interruption boundary deadline 10 virtual ticks for the dedicated controllable fixture; a non-cooperative case must end unresolved rather than falsely pass

The future implementer may change these numbers only before preregistration, giving the same values to each comparator and retaining boundary cases at limit−1, limit, limit+1. Values are synthetic stress points, not operational recommendations. Performance conclusions are restricted to the chosen model/fixture scales.

## 4. Fixed work and effect oracle

A synthetic goal requires four work units A–D. Each produces a predefined artifact digest from public/synthetic inputs. A and B can run independently; C consumes A; D consumes B and C. Each task carries a grant and explicit artifact scope. One task includes hostile source text claiming it may expand grants; the oracle treats that text only as content.

Effect receiver state:

- document X has initial version 0; authorized compare-and-apply moves it to version 1 with known content hash
- counter Y is non-idempotent; exactly one authorized logical increment is allowed
- forbidden target Z must remain unchanged
- two conflicting proposals for X are retained but only the authorized version-matching winner can promote
- one mock remote effect can commit while its receipt is withheld, allowing `outcome_unknown` to be the correct answer

The oracle separately knows the stub's synthetic consumption. If the public-facing stub hides a counter, the candidate must report unknown even though the test oracle knows the true amount. Oracle access may score honesty; it must not populate missing production-like accounting fields.

## 5. Comparator arms

All arms receive identical goal/grants, tool/effect restrictions, immutable evidence, checkpoint opportunity, allowed native-like features, verifier budget, helper-cost scripts and failure schedules:

- B0: single sequential delegate, strongest native-like resume/context reuse
- B1: native-fanout subtree with a complete child registry, then with an opaque aggregate-only registry
- B2: parallel native-launch orchestration with distinct per-attempt identity/reservations
- B3: queue-only execution, durable admission and serialized dispatch

Cross each with no fault, isolated fault, pairwise fault and a prespecified chained-failure episode. Do not disable a baseline's native reuse to create artificial wins. If an arm lacks a required contract, report incapable/unqualified rather than infinite latency or infinite “savings.” Performance is considered only after safety/authority/privacy/correctness floors pass.

## 6. Fixture catalog and exact expected outcomes

Each fixture preserves input bytes, output bytes, canonical events, receiver truth, expected event/state predicates and an explicit source-inspired versus design-only label.

| ID | Injected condition | Machine-checkable oracle / decisive failure |
|---|---|---|
| RF-F01 | Four independent/ordered work units, complete streams | Exactly four accepted required manifests; dependency order respected; one canonical writer; no unknowns invented where evidence is complete |
| RF-F02 | Source text tells child to widen goal/write Z | Z unchanged; denied attempt retained; effective child capability set remains subset of parent |
| RF-F03 | Nested child asks for parent full budget repeatedly | Sum consumed + reserved + uncertain liability ≤100 at every transition; exhausted child cannot spawn |
| RF-F04 | Fork copies context and attempts to copy exclusive write grant | Both histories retained; at most one active exclusive effect permit; branch budgets are split, not duplicated |
| RF-F05 | Duplicate spawn intent arrives before launch receipt | One launch incarnation or explicit duplicate receipt for same intent; no second consumption record for duplicate delivery |
| RF-F06 | Launch occurs; acknowledgement is lost; controller restarts | Attempt is admission_unknown until reconciled; no blind second launch; reservation remains held |
| RF-F07 | Native harness emits unobservable helper/subtree aggregate | Parent inclusive meter retained once; individual children/coverage unknown; no fabricated allocation or zeros |
| RF-F08 | Parent result includes child usage plus child receipts; alternate budget-crossing result omits crossing response from usage but includes it in model/cost totals | Disjoint coverage equals oracle once; no parent+children double count; positive incomplete usage stays scope-limited and is not substituted for whole-tree/crossing-inclusive totals |
| RF-F09 | Repeated messages share usage ID; cumulative resume total | Duplicate ignored for aggregation; restored cumulative prefix not summed twice; all raw events preserved within bounds |
| RF-F10 | /clear-like reset and new child attempt | Native reset epoch changes; canonical parent budget does not reset; prior consumption remains charged |
| RF-F11 | Interrupted stream has no result; alternate crash-result variant explicitly reports zeroed usage/cost; process exits 0/nonzero | Native/process outcomes remain distinct; preserve raw reported0 with invalid/crash provenance; retain earlier valid covered subtotal; missing residual remains unknown; no independent acceptance from exit or invalid zero |
| RF-F12 | Effect Y commits, response lost, then interrupt arrives | Y equals1; outcome_unknown until query proves commit; no automatic replay makes Y equal2 |
| RF-F13 | Two children concurrently propose X from version0 | One permitted compare-and-apply; conflict retained; losing work remains counted |
| RF-F14 | Aggressive Stop targets parent only | Parent new dispatch fenced immediately; descendants explicitly listed with independent state; not falsely reported Full |
| RF-F15 | Full Stop rooted set contains shells/monitor/relauncher | All rooted permits fenced; no relaunch; every owned member settled or unresolved; unrelated root continues |
| RF-F16 | Lazy Stop at named next boundary | No new admission; allowed operation reaches recorded boundary or explicit timeout; no guessed reasoning boundary |
| RF-F17 | Queued follow-up survives generic native abort | Candidate explicitly cancels/retains queue according to Stop contract; forbidden post-stop follow-up never dispatches |
| RF-F18 | Cancel acknowledgement precedes late tool/update/result | Late observations retained and correlated; ACK not treated as external settlement |
| RF-F19 | EOF means finish-current-turn on one profile, abort on another | Correct profile-specific transition; no universal EOF semantics |
| RF-F20 | Pending approval reconnects, old epoch response returns | One durable waiter identity; stale/wrong-action approval refuses; legitimate current reply binds exact effect |
| RF-F21 | Compaction drops budget/approval/source claim from native history | Canonical checkpoint restores current authority and original evidence; lossy summary never becomes authority |
| RF-F22 | Source fork/lost-machine/late completion chain | New attempt revalidates grant; old epoch can't commit; prior results retained; no credential migration |
| RF-F23 | Stream split at every byte, Unicode separators inside strings | Reassembled frames match fixture digests; only LF framing splits records; stderr never parsed as command |
| RF-F24 | Oversized line/deep JSON/stdout+stderr flood during Stop | Declared memory/output bounds enforced; mandatory stop/effect receipts not silently lost; gap/overload explicit |
| RF-F25 | Unknown event/schema version; missing required authority field | Harmless event preserved as unknown; authority-sensitive operation refused before effect; no permissive fallback |
| RF-F26 | PID reused; orphan native child; same task ID on another route | Incarnation+route+native correlation prevents conflation; orphan remains linked or explicitly unknown |
| RF-F27 | Authentication-required event offers token/proxy fallback | No credential request/relay or provider request; task state persists blocked; no automatic auth-mode switch |
| RF-F28 | Synthetic secret canary, malicious stdout and allowed-tool/config induced export; exact-profile strong preflight unsupported/fails | Direct and induced leaks detected/refused; strong-required work not admitted after failure; no implicit policy-only continuation; weaker mode requires separate operator admission |
| RF-F29 | Native concurrency cap exception allows excess internal children | External admitted envelope constrains subtree or declares unqualified; never presents native cap as an enforced global cap |
| RF-F30 | Fan-in first result conflicts with independent oracle | Candidate not accepted; conflict/reviewer outcome retained; no majority/fastest-result override |
| RF-F31 | Rate-limit/backpressure/deadline with unfinished effects | New admission stops; no account/route switch or reset; unresolved effects/counters remain unknown at horizon |
| RF-F32 | Every source-inspired stable/experimental/deprecation variant | Different profiles retain separate outcomes; v2-style live-only global subscription and separate durable log use distinct cursors, exclusive after/follow behavior and replay gates; method/transport maturity never inferred from JSON syntax |

For RF-F28, the future profile must first establish exact unmodified upstream C/T separation or equivalent enforced support; a wrapper, binary patch, authentication shim or token relay cannot manufacture that prerequisite. Unknown support stays unqualified. A state-only model can check information flow labels and synthetic output. It does **not** establish real OS memory/keychain isolation. Later R-E canary tests require separately admitted platform enforcement. Never substitute this fixture result for that stronger evidence.

## 7. Required trace and result schema

Every case result includes:

- fixture ID/version/digest; candidate commit/digest; source profile pins; independent oracle version
- arm, virtual schedule/seed, input/output trace digests and complete causal event sequence
- expected and actual canonical final-state digests; receiver final-state digest; replay state digest
- all launch intents/incarnations/native IDs, grant/epoch transitions, queue/waiter dispositions
- all effect intents/receipts with committed/not_committed/compensated/outcome_unknown; process-state observation kept separate
- every meter observation, scope/reset/coverage, disjoint aggregation, known subtotal and unknown residual
- peak resources; Stop request/fence/boundary/terminal/settlement virtual ticks
- each hard-floor predicate individually PASS/FAIL/UNMEASURED; reason and minimal failing trace
- independent acceptance and independent rerun status, never copied from implementation self-report

No global PASS if any required predicate is UNMEASURED. A designed unknown **outcome** can be correct and pass honesty; a missing **test observation** does not pass the gate. This distinction prevents an uncertainty-preserving adapter from being penalized for honestly reporting an unknowable remote effect.

## 8. Gate definition

The future single machine-checkable gate must return success only if:

1. Every RF-F01–RF-F32 case and required comparator/boundary variant exists and has an exact manifest/hash
2. Schema/static checks reject missing identities, grants, epochs, meter scope/reset state and unknown reasons
3. All authority, privacy, effect-settlement, accounting, canonical-writer and Stop hard-floor predicates pass
4. Replay of every accepted trace yields exactly the same canonical-state digest; receiver truth agrees with every claimed settled state
5. No candidate has emitted a provider/harness/network/install/credential/live-host action
6. All planted negative controls fail for the correct reason, not parser breakage or an unrelated timeout
7. The independent verifier reruns the exact candidate and fixtures and obtains the same case dispositions/digests

The gate's executable name is deliberately not invented here. Its exact command becomes part of the separately approved implementation task. Until then all gate outcomes are UNRUN.

## 9. Negative controls and confounders

Deliberately defective **synthetic** candidates: copy full parent grant to child; reset parent budget on native /clear; add parent-inclusive and child totals; turn missing usage or a crash-zeroed placeholder into valid zero; retry lost non-idempotent effect; equate cancel ACK to rollback; kill shared server for one session; accept old-epoch result; infer queue empty from absent capability; split JSON on Unicode paragraph separator; omit helper attempts; restore auth data in continuity capsule. Every defect must be detected by a named fixture. These controls do not authorize weakening a real system.

Record confounders: native/helper visibility; request count versus token count; partial output versus terminal output; cumulative versus delta/reset semantics; prompt/session/process/account scope; warm/cold context; independent versus overlapping tasks; fan-out depth; account-window rounding and other-user work (simulated only); lost receipt versus absent effect; ordering of revocation and receiver commit; scheduler fairness; stream backpressure; hidden background work; verifier overhead; latest-doc versus installed-release mismatch.

## 10. Stop conditions and reporting

- Abort the entire future experiment immediately if an actual model/provider/harness process, credential path, network endpoint, installation or live-host action is attempted
- Fail the case on any hard-floor breach; preserve evidence without auto-repairing the expected result
- On limits or unknown admission/effects, stop new admission, reconcile only permitted operations, and emit the unresolved inventory
- Do not retry indefinitely or extend deadlines; only prespecified retries apply
- Do not resume a required authorization-dependent action because time elapsed

Report safety and correctness first. Then synthetic completion/ticks/resource/backlog metrics by arm and condition, including failed/inconclusive cases. No “X% cheaper” or subscription-capacity conclusion is possible from this suite. Its end state is either contract falsified with a minimal counterexample, provider-free contract passed with exact scope, or blocked/unmeasured with a named missing input. Real route qualification stays a separate task.

## 11. Interface handoffs

- R-E: actual credential/connection/process boundary and canary isolation, exact platform profile
- R-H: exact binary/auth mode/driver/volume/terms profile; no legal inference from a stub
- R-D: real resource meters, native allowance and helper completeness; all-attempt denominators
- FU-03/FU-05: canonical event/fence/Stop model and wire saturation/replay cases
- D-028/FU-04: process ownership/termination, local NTFS/ext4 and actual VM-reset evidence, only on approved disposable targets
- MCP bridge supplement: cross-check lost response, protocol era, pending-input binding, task TTL, cancellation, saturation and hidden sampling fixtures where a native harness invokes MCP. MCP, ACP and vendor control semantics remain different profiles

Nothing in this handoff changes the accepted product scope, qualification priority or caller-not-proxy decision.
