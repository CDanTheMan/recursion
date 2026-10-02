# Model architecture: discriminating test handovers

Status: **UNEXECUTED DESIGNS**. These are specifications for separately admitted work. No command below launches a test, and no result is implied. Source snapshot: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Preserve frozen M1 profiles; new illustrative names require explicit mapping rather than silent schema edits.

## Shared admission and result contract

Each execution packet must bind: parent v3 goal; exact candidate commit and artifact digests; selected architecture arm; schema/byte profiles; required platform/build/filesystem; threat/failure model; exact allowed paths and effects; finite budgets/time/retry/stop envelope; data classification; authorized routes; independent verifier; literal oracle identity; required positive/negative controls; checkpoint/evidence retention and stopping conditions.

Each test result is one of `not_run`, `blocked`, `pass_within_declared_scope`, `fail`, `unknown`, or `inconclusive`, with evidence, scope and reason. These are handover-report labels, not changes to M1 enums. No mutable test can rewrite its expected output. `unknown` is not zero. An implementer's pass is not independent acceptance. Crash/containment actions need an explicitly approved disposable target. Live harness/model/provider work requires separate fresh authorization and route/legal prerequisites.

## H-MA-01: canonical command-to-effect join

Question: can the existing M1A/M1B/M1C identities be joined without losing an original key, target or complete admission binding?

- Build an explicit field provenance map from exact frozen profiles, preserving every opaque digest and original source
- Inputs: literal admitted command, goal/plan/policy, work packet, effect intent/admission, source/target/payload and receipt; add an authenticated supplemental join if the existing projection cannot carry all fields
- Negative controls: swapped target, same digest with wrong domain/profile, mismatched original idempotency key, wrong lease/epoch, stale approval, independently changed payload, missing original source
- Positive control: authorized exact join reaches one valid operation and later a matching settled outcome
- Oracle: independent literal relation checker; reject reconstructing absent inputs by “inverting” a digest
- Pass boundary: every required field has one owner, provenance and explicit compatibility mapping; refused cases cause no dispatch
- Falsifier: a false join is accepted or a required legitimate join cannot be represented without violating frozen bytes
- Non-proof: does not validate real authentication or effect truth

## H-MA-02: matched split/inclusive proof experiment

Question: does kernel-plus-broker refinement expose the same required failures as the inclusive model at identical scope?

Prerequisite reconciliation: use the [gap audit](../gaps/report.md#3-fu-03-what-the-committed-evidence-does-establish)'s actual four-ID diagnostic bound and mutation-site distinctions. The [seven-step enlarged-bound witness](../gaps/fu03-candidate-witness.json) is an unexecuted source-level hypothesis, not an executed counterexample or authorization to run it. Reproduce/refute and reconcile timer/effect invariant meaning before promoting a larger diagnostic run into full-gate evidence.

- Pin common observations, integrated bounds, scheduler fairness, fault order and invariant set before implementations
- Include all six preserved M1 obligations, recipient permit installation, process birth/ownership, relaunchers, rooms, fork reservations, queue saturation, RESET, configuration and update/Stop races
- Retain abstract model plus two separately authored concrete models and independently authored mapping/monitors
- Every concrete step must be mapped or proven observationally stuttering; no composite revoke-plus-deliver or answer-plus-adopt shortcut
- Controls: remove each guard at one exact site; retain exposure witness, reachable/non-equivalent justification, first divergence and minimized/full counterexample
- Report all required mutants with dispositions; syntax error, timeout and checker crash are inconclusive; equivalent/unreachable rows are not kills
- Compare state space, runtime/resources, mapping size, review defects and covered behaviors without using speed to waive behavior
- Stopping: declared envelope or first safety violation; do not reduce agreed bounds to create a pass
- Non-proof: finite model agreement is not an unbounded theorem, OS conformance or production freeze

## H-MA-03: commit/dispatch/receipt crash matrix

Question: can each architecture preserve one operation and honest uncertainty across every dual-write window?

Cutpoints: before command commit; after reservation/intent commit; before delivery; recipient accepts before local acknowledgment; effect occurs before receipt; receipt exists before canonical persistence; canonical persistence before client acknowledgment.

For every cut, resume from the last acknowledged durable state. Assert command deduplication, unchanged OperationId/target/payload, one retry owner, retained reservation while ambiguous and refusal of dependent effects. Distinguish a proven no-dispatch state from possible dispatch. Positive path must complete useful synthetic work rather than only refuse everything. Compare A receiver records and C helper journal at identical residency/fault history. Later physical trials require D-028 target identity and approved reset; an in-memory simulated cut proves only state-machine behavior.

## H-MA-04: native loop control and partial-stream corpus

Question: does the native implementation actually own the loop and mediate tools?

- Use a deterministic synthetic model-stream source, not a provider call, for malformed/truncated/duplicate/out-of-order data
- Cases: text-only final; one permitted tool; conflicting tool batch; independent parallel tools; partial arguments that parse but are incomplete; duplicated final event; stream error after usage; steering before/after tool preflight; revoked grant during sampling; late tool result after Full Stop; pressure-triggered compaction; exhausted role reservation
- Assert every sampling and tool attempt uses its own admitted identity; partial output is never authoritative; completion order and transcript order remain distinguishable; cancellation never erases completed siblings
- Instrument the call graph: Recursion owns next-turn choice, tool proposal ordering and stop/continuation decisions; no upstream SDK controls the hidden loop
- Negative controls: execute partial JSON, call tool before canonical admission, accept late grant, sum cumulative usage twice, continue after missing role path
- Positive path: complete a bounded multi-turn synthetic task, recover after crash and produce a reviewable candidate
- Non-proof: synthetic stream correctness does not prove model quality or provider billing behavior

## H-MA-05: upstream-only reasoning-role closure

Question: can an upstream-only installation perform the accepted workflow without native helper inference?

List every reasoning role, including setup assistance, planning, routing, research, compaction, review, recovery and notification drafting. For the tested workflow each is bound to qualified upstream execution or a stated deterministic alternative with honest capability loss. Remove/disable direct model credentials and native inference implementations in the test closure; trap attempted calls, imports and network destinations rather than setting counters to zero.

Negative cases: session lost during compaction; verifier unavailable; adaptive scorer disabled; upstream refusal; helper error; unknown usage; route exhausted. Expected: current work held or uses only a previously authorized equivalent route; no hidden model call, new account, paid fallback or allowance reset. Positive control: a supported upstream-only workflow completes and all-role consumption is attributed or explicitly unavailable. Later live runs need exact route entitlement/consent and approved inference budget. This test does not prove every possible upstream workflow is supported.

## H-MA-06: strong non-intermediation profile

Question: what exact non-access claim holds at each accepted platform floor?

Threat-model inputs: Recursion principal; trusted launcher principal; trusted harness binary; generated-code sandbox; plugin principals; administrative operator; filesystem/registry/keychain/environment/process-memory/handle/log/dump/IPC access; permitted egress and returned stream. Classify every opaque locator or launch handle by actual authority: possession that enables invocation/use is sensitive bearer-like authority, not harmless metadata or evidence of provider-secret non-access. Test principal binding, attenuation, expiry, revocation and replay using synthetic handles.

Preflight prerequisite: identify documented support in the exact unmodified upstream build for separating credential-facing C from untrusted tools T, or a specifically evidenced equivalent enforceable profile capability. Map the actual enforcing boundary and test it. A wrapper or launch broker cannot supply upstream separation merely by declaration; absent or unverified support blocks the strong profile rather than assuming transparent compatibility.

Negative cases: arbitrary launcher argv; environment override; directory traversal/symlink into credential roots; inherited secret-bearing handles; process inspection; child asks harness tool to read provider-auth files; printable encoded secret returned through nominal JSON; alternate executable substitution; stale route digest. Use synthetic sentinel credentials only under separate authorization. No real secret extraction is authorized.

Pass is claim-specific: policy-only, OS-protected against orchestrator, and tool/output-channel resistance are separate. A failed strong preflight closes execution admission and refuses tasks requiring the strong property. Record the weaker assurance label without running it; policy-only execution requires separate operator admission of that exact weaker mode for an eligible task. Add a negative control that attempts automatic downgrade/continuation after failure and require deterministic refusal. No fallback may evade the failed boundary. Native Windows and Linux profiles qualify separately; WSL does not inherit production status. Independent verifier must observe the accepting boundary, not only orchestrator log refusal.

## H-MA-07: context reconstruction and repeated compaction

Question: does context management preserve productive continuity rather than only references?

- Synthetic corpus with exact accepted directives, revoked/superseded instructions, contradictions, pending approval/question, unresolved operation, dirty source cut, evidence/version changes and private cross-project distractors
- Arms: route-native only; deterministic artifact selection; coordinated hybrid; cold full reconstruction; warm session; no-future-work counterfactual
- Structural oracle checks exact bindings, non-droppable references, rehydration, audiences and single governor/epoch
- Independent task oracle checks continuation choices, temporal correction, abstention, escaped defects and owner re-explanation/correction burden
- Inject lost provider session, late old compactor, spontaneous upstream compaction, stale repository index and revoked artifact audience
- Count every transform/retrieval/index/cache/refresh/retry/verifier cost; missing subscription meters remain null
- Falsifier: structural pass accompanies semantic harm over the owner-set noninferiority margin, or full-workflow benefit disappears
- Non-proof: a tested query set does not imply universally lossless compression

## H-MA-08: room and consultation race corpus

Question: do direct coordination and Head-mediated commitments preserve identical authority with different burden?

Cases: duplicate/reordered message; expired coordinator lease; room membership revoked; question replaced; answer forwarded without original author evidence; proposed wording quoted as accepted; cross-goal evidence leak; room consensus contradicts owner intent; no-progress ping-pong; Stop during protected commitment; participant route/session migration.

Each message/decision binds exact room/goal/role epochs and original QuestionId. Test accepted/delivered/adopted separately. Protected effects always use canonical admission. Compare owner time, semantic correction, completed task value, total inference and coordination traffic. An inability to reach acceptance may be correct safety behavior but cannot by itself prove useful collaboration.

## H-MA-09: durable schedule and adaptation boundary

Question: can bounded autonomy survive crash and learn without expanding authority?

Schedule cases: due tick during downtime; restart after occurrence claim; duplicate wake; backward wall-clock observation; end condition reached; revoked goal; exhausted shared pool; route unavailable; child continues after parent stop; catch-up storm. Assert stable occurrence identity, explicit lateness disposition, fresh admission, no reset allowance and no model keepalive for status.

Adaptation cases: corrupt/missing labels; absent counters; biased workload mix; cache warmness confounder; stale model/price/config; user pin; learned route violating privacy; exploratory attempt outside budget. Assert candidate policies remain proposals until permitted promotion; kernel eligibility is never bypassed; rollback preserves historical effects. Compare against static owner policy with preregistered floor/margin and independent labels. Offline score alone cannot pass live value.

## H-MA-10: client overload and common semantics

Question: does terminal-first presentation share one backend and keep control responsive?

Use multiple independently implemented clients against one command/query contract. Exercise all ten controls, attach/detach, queued edits, stale questions, repeated approval responses, current-turn steering, resume, preserved forks, compaction and engine extensions. Slow the render sink and saturate byte/event credit. Stop must retain bounded service; clients receive explicit gap/RESET, exact-cut snapshot and incarnation validation. A view cannot start/stop a model/process by attachment lifecycle alone.

Assertions distinguish locally saved, canonically accepted, delivered, adopted and settled. Compare deterministic CLI JSON projection with TUI semantic view; later GUI must reproduce the same object ids and command receipts. Accessibility acceptance needs separately approved concrete clients/assistive technologies. A headless event transcript alone is not UI accessibility proof.

## H-MA-11: plugin inertness, translation and update

Question: does comprehensive optionality remain lean and behaviorally honest?

Inventory known/uninstalled, installed-disabled, enabled-inactive and active states separately. Instrument import/compile/instantiate, filesystem payload reads, threads/processes/timers/watchers, model/network/auth, schema/context registration, subscriptions, quota and spend. Test 0/10/100 installed-disabled entries, plus incompatible invocation under all four response modes. No counter may be fabricated by the resolver itself.

For selected port candidates compare unchanged declarative reuse, schema translation, protocol bridge, isolated host reuse and native rewrite at matched behavior. Include lifecycle disposal failure, dependency conflicts, hook timing, loss of typed result metadata, stale plugin digest, hot reload and downgrade. Update all six modes against executable/history/newest-work/resumable outcomes. Record negative acceptable-port counts and full ongoing maintenance cost. Passing metadata validation is not a successful port.

## H-MA-12: availability and six continuity journeys

Question: can the complete arrangement meet productive continuity under the accepted release scope?

Use exact native platform/failure profiles and separately admitted disposable targets. The [FU-04 receipt audit](../gaps/report.md#4-fu-04-raw-counts-actual-mechanisms-and-oracle-limits) is a prerequisite oracle review: 13 historical run rows are not 13 qualified mechanisms, and file-size/manual-epoch checks do not establish durable replay or receiver fencing. Automatic takeover tests must expose real writer/store/effect-receiver fences, partitioned old writer return, offline nodes, unavailable availability plugin, stale checkpoints and ambiguous prior effects. Core must still boot/replay/status without optional adapters; it must not fall back to an unfenced writer.

Then execute the six D-024 journeys: native/upstream/native; explainable compaction after session loss; Full Stop with unreachable node/unresolved effect; dirty unfinished-source fork; disconnect/detach/reconnect; honest subscription-quality tradeoff. Each needs useful authorized completion, rejected invalid behavior, exact source/evidence continuity and full accounting/human effort. Baselines must include strong direct upstream and minimal native workflows, not only weak or uncontrolled swarms.

Acceptance margins, budgets, deadlines and exact targets are Owner inputs; this packet invents none. Stop after any safety-floor violation, exhausted authorized envelope or missing authority. Preserve evidence for independent review rather than weakening the scenario. Even a complete passing corpus proves its declared scope, not arbitrary external effects or every future upstream build.

## Handover dependency map

`identity/byte reconciliation -> matched formal corpus -> platform/store/broker evidence -> native/upstream role closure -> context/room/schedule/plugin integration -> six end-to-end journeys -> comparative value + release review`

Documentation and synthetic fixture authoring may progress before live prerequisites. Executable qualification and decision-producing ranking cannot silently skip them. No live target, installed binary or experimental run was selected or executed in this packet.
