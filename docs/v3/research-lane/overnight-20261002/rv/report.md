# R-V — Model-free observability, introspection and replay debugging

Research candidate · 2 October 2026 UTC · repository snapshot `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`

## Decision-ready findings

1. Explanation is a deterministic query over an identified, authenticated canonical cut and its retained command/receipt/input evidence. It is not a new inference, a fresh authorization, or a causal story reconstructed from chat. Recorded decisions, received observations, hypotheses and unknowns have different types.
2. Keep three replay promises separate: **state replay** reproduces recorded reductions; **decision re-derivation** checks the historical predicate against retained historical inputs; **external re-execution** performs work again and is outside replay. Only the last needs new execution admission. A matching state digest can coexist with an originally wrong decision or false external report.
3. Canonical events, receipt journals and materialized application snapshots must precede or independently outlive disposable presentation. A live subscription, a valid RESET frame, or a cursor acknowledgement is not durable history or installed state. Slow viewers must be disconnected or served bounded snapshots without becoming a writer/Stop dependency.
4. Preserve both raw meter reports and validated quantities. A crash receipt that reports `0` may be an actual observation of an invalid meter report; actual consumption then remains unknown and its liability remains reserved. Roles, inclusive parent totals, child totals, cumulative updates, resets and recovery segments cannot be summed indiscriminately.
5. Required evidence/status remains model-free with rich tracing, exporters, adaptation and memory disabled. Optional diagnostics have CPU, memory, disk, queue, retention and privacy costs. “Zero model calls” is a narrowly witnessed operation property, not literally zero resource use.
6. Public/support export is a distinct allowlisted compilation, not a scrubbed copy of a local trace. Content, paths, credentials, hidden reasoning, raw digests and stable cross-project identifiers are excluded; rare-event timing and joinability still require threat tests.

This report answers 22 questions and nine completion bullets. All product behavior proposed here is **IN** (inferred design), not implemented acceptance. Every runtime fixture and benchmark is **UNEXECUTED**. No language, store, framework, runtime, tracing library, telemetry backend, query language or vendor is selected; no route is qualified.

<a id="evidence"></a>
## Evidence, authority and inherited boundaries

**SD** means a cited primary source documents a property, not that Recursion implements it. **LO-record** means static inspection of committed source/evidence, without executing it. **IN** means a proposed contract or inference. **U** means unknown/unmeasured. A retained provider statement is evidence that the statement was received; validation and truth remain separate. Optional human/model annotations are never canonical authority and cannot fill required inputs.

Current governance and D018–D033 prevail over stale baked context. Recursion owns a first-class native loop and separately supports independently useful upstream-only execution. Hermes has no executive authority. Status/explain/replay cannot silently invoke a native helper for an upstream-only task. D019's comprehensive built, opt-in release scope is preserved; TUI-first construction and common backend support later GUI work. The exact timing interpretation against older GUI-exclusion text remains an Owner clarification, not a smaller release decision. Core has one fenced writer and the availability seam; automatic takeover is an opt-in first-party remote/full capability, not default consensus. Writer, work, process, route, configuration, release and Stop/pause epochs remain distinct.

### Static observations that narrow the gap

| Repository-relative source at the snapshot | LO-record finding | Consequence and limit |
|---|---|---|
| `scripts/v3/planning/replay/kernel.py`, `genesis`, `_sealed_state`, `_validate_replay_checkpoint`, `replay` (lines 54–102, 608–717) | M1A already constructs deterministic projections, binds a checkpoint to its projection and first checkpoint event, and joins ordered command/receipt records to event groups with before/after digests | Do not claim that Recursion has no replay code. This is frozen M1A behavior, not qualification of the complete R-V layer, production store or first-event diagnostic UX |
| Same file, `admit` (517–590); `scripts/v3/planning/validation/canonical.py` | Refused/conflicting commands can produce journal receipts without changing canonical state; exact duplicate handling precedes fresh admission. The decoder has explicit bounded, integer-only restrictions | Explain must include the receipt journal, not assume every refusal is a state event. R-V does not add fields to or reinterpret frozen M1A. A returned old receipt is not fresh authorization |
| `docs/v3/construction/replay-store-evidence-20260907/dossier.md`; `experiments/v3/replay-store-evidence/reader.py` | Recorded narrow probes distinguish a real retained suffix from a false floor, and emitted RESET from installed application content/cursor. The reader checks a bounded synthetic catalog | Preserve these historical observations. They do not prove arbitrary concurrent snapshots, storage durability, production authentication or external exactly-once effects |
| `docs/v3/TERMINAL-RUNTIME.md`, shared snapshot and reservation sections | Captured/copied/advertised/emitted/installed positions and presentation versus authoritative reservation state are already distinguished | Reconnect cannot restore an old allowance or silently release uncertain effects |
| FU03 `results/summary.json`, FU04 `traces/traces_results.json` | Reduced-bound formal evidence and bounded OS receipts exist; neither is a production-profile qualification | Do not erase evidence with old GAPS wording or promote finite/WSL observations into native-platform guarantees |
| Research index, architecture/harness coverage, synthesis, `STATE.md`, `TELEMETRY.md`, `PERFORMANCE-PLAN.md` | DS10/25/26 and full persistence/telemetry qualification remain open; coverage prose includes dated/stale assignments | R-V owns explain/replay edge 48, not the obsolete lane name. Counter coverage, observer overhead and full recovery fidelity remain U |

Input identities and hashes are in [input-pins.json](input-pins.json). This is a static record audit, not a new target execution. Historical commands are not authorized to run by this report.

### Narrow public-source findings

These capsules are the public-source summaries for this lane; later sections are original Recursion contracts. Versions, retrieval dates and hash limits are in [source-register.json](source-register.json).

<a id="v-s01-facts"></a>
- **V-S01:** W3C Trace Context is a context-propagation Recommendation. Its privacy section prohibits sensitive information in trace headers and recognizes cross-request correlation risks. Correlation identifiers are not authentication or task authority. [Trace Context, 23 November 2021](https://www.w3.org/TR/2021/REC-trace-context-1-20211123/)
<a id="v-s02-facts"></a>
- **V-S02:** OpenTelemetry's stable Logs Data Model separates source occurrence time from observation time and supplies optional trace/span correlation. A mapped log record is not itself a durable decision receipt. [Logs Data Model](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
<a id="v-s03-facts"></a>
- **V-S03:** OpenTelemetry's tracing API supports parent contexts and links, including links between traces. Its timestamps need not establish event order. These are representation primitives, not proof of causation. [Tracing API](https://opentelemetry.io/docs/specs/otel/trace/api/)
<a id="v-s04-facts"></a>
- **V-S04:** The retrieved event semantic conventions are marked **Development**, unlike the stable log data model. They distinguish named occurrences from duration-bearing spans and prohibit dynamic event names. Pin the convention revision separately. [Event conventions](https://opentelemetry.io/docs/specs/semconv/general/events/)
<a id="v-s05-facts"></a>
- **V-S05:** OpenTelemetry explicitly warns that hashing predictable identifiers may fail anonymization. Removing strings alone is therefore an insufficient export claim. [Sensitive-data guidance](https://opentelemetry.io/docs/security/handling-sensitive-data/)
<a id="v-s06-facts"></a>
- **V-S06:** OWASP recommends explicit interaction correlation, exclusion of secrets/sensitive fields, output sanitization and testing logging failures. Its general operational guidance does not authorize dropping Recursion's mandatory receipts. [Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
<a id="v-s07-facts"></a>
- **V-S07:** RFC 5424 defines structured syslog messages and explicit unavailable fields. It supplies an interchange precedent, not canonical writer fencing, application atomicity or recovery. [RFC 5424](https://www.rfc-editor.org/rfc/rfc5424)
<a id="v-s08-facts"></a>
- **V-S08:** Lamport's original work distinguishes causal partial order from a constructed total order. Canonical append order may serialize observations without proving a physical-time order of external events. [Original paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/Time-Clocks-and-the-Ordering-of-Events-in-a-Distributed-System.pdf)
<a id="v-s09-facts"></a>
- **V-S09:** The rr authors' technical report studies recording nondeterministic execution inputs under specific hardware/OS and workload constraints. It motivates explicit input capture; it supplies no Recursion portability or overhead result. [Record/replay report, 2017](https://arxiv.org/abs/1705.05937)
<a id="v-s10-facts"></a>
- **V-S10:** Google's Dapper report uses sampling and common-library instrumentation for its tracing objectives. Sampled performance evidence is useful but cannot replace a complete authoritative decision record. [Dapper, 2010](https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/)
<a id="v-s11-facts"></a>
- **V-S11:** Mozilla Glean documentation describes declared measurements, review, expiry and resolution controls. These are useful design precedents for a bounded telemetry catalog, not a privacy certification of Recursion. [Glean design principles](https://docs.telemetry.mozilla.org/concepts/glean/glean.html)
<a id="v-s12-facts"></a>
- **V-S12:** Honeycomb's first-party engineering guide shows why high-cardinality request/context identifiers help diagnose isolated failures. Its commercial cost claims are not adopted; scoped diagnostic value does not remove retention or disclosure costs. [High-cardinality guide](https://www.honeycomb.io/resources/getting-started/understanding-high-cardinality-role-observability)
<a id="v-s13-facts"></a>
- **V-S13:** At pinned T3 Code commit `b33eda13998b5b0571daaf266c87f6f31af41f7d`, architecture documentation separates committed intent/command receipts from later reactor effects, and production state from test-only runtime receipts. This is a comparison shape, not Recursion qualification. [Pinned architecture](https://raw.githubusercontent.com/pingdotgg/t3code/b33eda13998b5b0571daaf266c87f6f31af41f7d/docs/internals/overview.md)
<a id="v-s14-facts"></a>
- **V-S14:** The identifiable W3C logging document is **Extended Log File Format**, a historical Working Draft, not an “Event Logging Recommendation.” It describes field/version declarations and omitted values. No general W3C Event Logging Recommendation was verified; this report does not invent one. [Working Draft](https://www.w3.org/TR/WD-logfile)

Shared source facts are not repeated: [OpenCode current/legacy and v2 facts](../rf/report.md#opencode-server-facts), [v2 live versus durable log and projected fork](../rf/report.md#opencode-v2-facts), [route accounting](../rf/report.md#claude-accounting-facts), [R-O telemetry and observer tax](../ro/report.md#ro-s12), [R-L projection/application snapshot contracts](../rl/report.md#r-l-q04), [R-Q evidence/authority](../rq/report.md#q03), and [R-S deterministic explanation](../rs/report.md#rs-s16). These companion proposals remain research inputs, not normative acceptance. OpenCode receipts/compaction surfaces and T3 separation are competing evidence designs to test, not interchangeable implementations.

<a id="q01"></a>
## R-V-Q01 — Routing explanation

**IN, recommendation V-R01.** `ExplainRequest` binds domain, decision/operation identity, canonical event cut, receipt-journal cut, query scope/audience, requested explanation version and finite output bounds. The response retains a sorted candidate universe and its discovery completeness, exact descriptor revisions, historical GoalSpec/policy/configuration/authority/reservation inputs, meter freshness, predicate identifier/version/digest, and stable tie-break rule. Each predicate node identifies operands by retained reference, operator, result `true|false|unknown|not_evaluated`, dependency and reason code. Do not reevaluate against today's budget and call that the historical explanation.

The result distinguishes **selected**, **eligible-but-not-selected**, **refused**, **deferred**, **unknown eligibility**, **not evaluated** and **not in the recorded candidate universe**. It is dishonest to call every alternative refused. Short-circuit branches remain `not_evaluated`; an optional counterfactual computes separately under a named hypothetical input set and cannot edit the original record. A model-origin proposal may be recorded as a proposal, but its hidden reasoning is neither requested nor reconstructed.

Synthetic example: at cut 12, route A has current capability/authority and 12 units of headroom before withholding a 3-unit control reserve, leaving 9 for a request bounded at 9; route B fails the recorded privacy-class predicate; route C is eligible but loses the stable preference order. Explain names all three dispositions. If B's descriptor is missing, its historical result may be retained as a reported verdict while independent re-derivation is `unknown`; it cannot be reconstructed from the selected route alone. V-F01 checks both preservation and deliberate missing-input refusal.

<a id="q02"></a>
## R-V-Q02 — Admission and resource explanation

**IN, V-R01/V-R08.** Admission output names worker/plugin/parallel-step identity, parent task and role lease, expected revisions, exact proposed capability/resource vector, policy decision, queue/defer boundary and inputs. A resource predicate records units, collector/source version, observation scope/time/validity, low/high-water thresholds, hysteresis state, outstanding reservations, control/recovery reserves, child allocation, concurrency permits and review debt. Unknown CPU/headroom is not a favorable zero. A queue reason identifies a concrete unmet condition and next permitted observation; it does not promise when capacity will arrive.

For each independent resource dimension, the disjoint-headroom representation checks `settled_consumption + outstanding_reserved_upper_bound + still_unallocated_withheld_control_headroom + proposed_reservation <= approved_limit`. Outstanding reservations already include admitted recovery work and uncertain liabilities; neither is added again. The still-unallocated control headroom is disjoint from outstanding reservations. Admission atomically transfers the relevant allowed headroom into outstanding reservations: ordinary work cannot consume the withheld control share, and an admitted control/recovery operation moves its allocation out of that share into outstanding once. The alternative representation tags the control reserve inside total outstanding reservations and uses `settled_consumption + total_outstanding_including_tagged_control + proposed_reservation <= approved_limit`, with no extra control term. Do not mix the two representations. Thus the synthetic ordinary admission is `3 + 5 + 3 + 9 = 20`; admitted recovery and uncertain liabilities are already within the 5, and the withheld control 3 remains untouched by that ordinary admission. A parent-inclusive meter and child measures require reconciliation before computing consumption. High-water contraction and low-water expansion use recorded samples and predicate versions, so replay cannot invent fresh headroom. Numeric production limits remain U until R-O's profile-specific preregistration is adopted.

M1A refused receipts do not become fabricated canonical events. In production, authenticate the current caller and authorize the current reader/domain/scope before receipt lookup or disclosure, including existence metadata. The proposed canonical operation key is `(admitted_authority_domain, command_id)`. `content_digest` is the immutable equality/conflict check under that key, not an extra namespace that permits another operation with the same ID. `actor_id` and `auth_ref` stay bound inside the immutable command. Any client/principal-local namespace needs an explicit injective durable mapping into canonical IDs before this boundary; transport request IDs remain separate. Same-domain/same-ID/different-payload or changed actor/authentication reference is not an exact duplicate; a caller identity alone is not permission to disclose another domain's receipt. A read-authorized historical receipt keeps its original disposition and state cut even when current effect authority has been revoked; returning it never redispatches the effect, admits new work or revives a grant. Current status may separately display a later canonical change. These are production qualification obligations. Frozen M1A is a pure sanitized in-memory fixture scope with synthetic authority; this report claims no cross-user defect and makes no silent amendment of its duplicate behavior. Invalid requests whose identity cannot bind a receipt get a bounded ingress error with no raw-body logging. The diagnostic layer does not introduce a competing admission writer. V-F02 tests admit/queue/defer/refuse and preservation of Stop/recovery reserve under saturation.

<a id="q03"></a>
## R-V-Q03 — Compaction explanation

**IN, V-R02.** `CompactionReceipt` binds the single governor and its lease for the route/context epoch, trigger measurement/predicate, pre/post manifest references, transform identity/version, admitted resource cost and transition receipt. A disposition map classifies each in-scope artifact revision as exact-retained, transformed-with-parentage, intentionally omitted, expired/deleted, inaccessible, or rehydrated. It includes exact-control retention, unresolved approvals/effects, loss reasons, coverage denominator, source retention/rights and fidelity-gate evidence. “Summary created” is not “epoch safely advanced.”

Epoch advancement requires the declared artifact install/verification boundary and a canonical transition; proposed, generated, checked, installed and effective are separate. Deterministic fidelity checks can compare exact authority-bearing references and required fields. They cannot prove the meaning of an arbitrary natural-language summary. If a model performed original compaction, its output is replay input with original cost/coverage; explaining it now invokes no model and claims no reproduction of hidden cognition. A missing transformed artifact stops semantic re-derivation at that dependency while preserving the known compaction receipt and explicit loss marker.

Compare receipts plus a retained exact control capsule with receipts plus a versioned artifact graph and query-time manifest diff; both retain exact directives and pending approvals outside summaries. V-F03 loses one directive, changes governor identity and omits a fidelity result in negative variants. A smaller context is never itself a fidelity pass. See R-Q's [recoverable-state boundary](../rq/report.md#q04).

<a id="q04"></a>
## R-V-Q04 — Effects and Stop honesty

**IN, V-R03.** An effect is a stable logical operation plus distinct attempts, receiver identity/scope, payload binding, current admission, idempotency owner and causal receipts. Its display is a fact vector, not a linear success enum: `intent`, `saved_locally`, `accepted`, `dispatch_attempted`, `delivered`, `applied`, `observed_outcome`, `verification`, `settlement`. Each has evidence, observer, source cut, time/clock and knowledge state. “Accepted” identifies who accepted what: canonical command, transport, remote job or final artifact are different subjects. `pending`, `unresolved`, `failed` and `settled` are independent from process termination.

Stop has mode **Aggressive/Full/Lazy**, exact target/owned closure and command/Stop epoch. Show requested, canonically accepted, dispatch fenced, source interrupt requested/acknowledged, local processes observed exited/waited, remote fences installed/unreachable, lazy boundary reached/timed out, and remaining external liabilities separately. `checkpoint`, `interrupt` and `drain` remain distinct operations. Full Stop does not claim an unreachable descendant stopped. A killed PID or closed socket cannot prove rollback, delivery failure, refund or absence of a later applied effect.

Late valid historical receipts may classify the original operation under the governing protocol; they do not authorize new work or clear M1A quarantine by UI inference. Compensation is another admitted effect with its own receipt, not erasure of history. V-F04 covers intended-but-never-dispatched, remote-accepted-but-unobserved and applied-but-business-outcome-unverified. V-F11 supplies all three Stops and a late receipt.

<a id="q05"></a>
## R-V-Q05 — Incomplete records

**IN, V-R04.** Every response carries coverage: source cut requested/available, receipt cut, projection freshness, scope completeness and missing dependencies. A `GapMarker` names its class (`canonical_missing`, `receipt_missing`, `artifact_expired`, `presentation_coalesced`, `transport_gap`, `meter_unavailable`, `scope_redacted`, `schema_unsupported`), allowed interval/opaque range, reason, first affected dependency and reconstruction disposition. A coalesced frame is not evidence of missing canonical history. A scope-redacted count may itself be withheld; public viewers need not learn private sequence density.

Typed quantities use `value:null` when unknown/invalid/unavailable/stale, with unit, reason and origin. Known zero requires witnessed coverage. State may be complete through cut 15 while explanation of decision 9 remains incomplete because its predicate input expired. Conversely a complete display transcript may omit an indispensable canonical event. Report these axes independently.

Do not guess a missing step, infer success from silence, fetch today's external state during replay, or silently summarize away a gap. A user can explicitly request a newly admitted diagnostic observation; it becomes a new observation, never a repair to old evidence. Negative variants of V-F06/F07/F09 require exact markers and prohibit later events being labeled successfully replayed past the first required missing input.

<a id="q06"></a>
## R-V-Q06 — Causal model and correlation

**IN, V-R05.** The canonical writer orders admitted events within its authority domain. The causal graph contains typed edges with explicit origin receipts, not edges guessed from timestamps: `command_causes_event`, `attempt_of_operation`, `spawned_under_lease`, `response_to_call`, `consumed_artifact`, `produced_artifact`, `retry_of`, `recovery_from`, `forked_from`, `supersedes`, `observation_of`, and `joined_from`. Fan-in links multiple causes; a single parent tree is insufficient. Imported correlation is an untrusted claim until joined to an authenticated local observation.

Identity namespaces include project/goal, assistant role, task/step, run/attempt, logical operation/effect, command/receipt/event, work lease, writer domain/epoch/sequence, process and node incarnation, route/interface/build/route epoch, model-call ID, source fork, checkpoint/context epoch, configuration/Stop epochs, reservation/meter segment and recovery segment. Nullable upstream session/turn IDs map to opaque scope-local aliases; their disappearance cannot destroy Recursion lineage. Trace/span IDs are optional projection identifiers, never grants.

A received timestamp and source occurrence timestamp are kept separately with clock identity and uncertainty. Canonical order is recording order; independent remote events may remain unordered causally. Negative durations or a missing parent are gaps/clock issues, not silently corrected causality. Graph acyclicity applies to the chosen causal relation; containment and later annotations use separately typed edges so graph cycles do not masquerade as temporal causation. V-F13 checks fan-in, out-of-order arrival, duplicate native IDs and wrong-incarnation joins.

<a id="q07"></a>
## R-V-Q07 — Versioned, bounded schema and retention

**IN, V-R05/V-R10.** [candidate-contracts.json](candidate-contracts.json) defines logical `EventEvidenceEnvelope`, `DecisionRecord`, `ProjectionManifest`, `ExplainResult`, `ReplayDiagnostic`, `MeterObservation` and `ExportManifest` contracts. They are a separately versioned candidate layer, not additions to frozen M1A/M1B payloads. Existing fields are mapped by exact source-schema adapters with an explicit loss/unknown report.

The event envelope identifies schema/profile, immutable event/evidence reference, authenticated producer and canonical admission, event kind, source and receipt cuts, subject/correlation/causal references, separate epochs, occurrence/observation clocks, payload class/reference, policy/retention, integrity/authenticity and availability. Avoid free-form attribute bags. Names/reason codes are finite registered vocabularies. High-cardinality identifiers live in access-controlled local evidence and bounded query indexes, not metric labels. Validation imposes per-record bytes, reference fan-in, nested-depth, page, graph-node/edge, queue and total-scope caps. Production values require adoption; the synthetic profile has explicit illustrative bounds.

Retention follows existing STATE direction: raw successful sessions 30 days, failed/disputed 90 days unless project policy overrides; minimal receipts/lineage are policy-governed, not a promise of unbounded free storage. Pinned evidence, holds, lawful purge and R-Q copy/key deletion states remain distinct. Expired payloads leave the minimum allowed tombstone and a replay limitation. No recoverable content or unnecessary global equality digest is retained merely to preserve an attractive explain badge. Bounded disk pressure sheds optional caches before required evidence; if safe canonical retention cannot continue, new work admission holds visibly. V-F16 checks expiry/purge and downstream cache invalidation.

<a id="q08"></a>
## R-V-Q08 — Timeline and graph views

**IN, V-R06.** The default TUI shows focused task state and current wait/Stop/effect uncertainty; timeline, graph, evidence and telemetry are separately opened views. Opening an absent/disabled plugin's pane renders an inert placeholder, never activates inference, indexing or a component. Minimal CLI status/explain is always available. Shared backend semantics apply to later GUI construction without resolving the release-timing conflict.

A timeline is paged by canonical cut with stable item keys and lanes for task phases, queue/wait boundaries, attempts/retries, route/context changes, Stop receipts and effect settlement. Duration labels include clock/coverage; asynchronous pending tails and gap markers remain visible. It updates only changed visible rows, batches under a view budget and preserves a user's scrolled anchor. A graph expands a bounded causal neighborhood on explicit request, showing edge type, evidence and missing/unavailable nodes. Stable deterministic ordering is separate from a renderer's layout coordinates.

Scope-limited viewer caches key on principal, project/goal, audience/purpose, policy revision, source cut, projection/renderer schema and filter. They contain only disclosed projection data; no broad source cache followed by visual hiding. Revocation or scope change invalidates incompatible cache generations; stale offline data is labeled and not reused after permission denial. Cache presence creates no authority or new continuation. V-F08/F12 cover incremental rendering, zero/slow viewers and cross-scope cache transplantation. This extends [R-K focused views](../rk/report.md#r-k-q11-focused-task-workspace-and-composed-views), not a renderer selection.

<a id="q09"></a>
## R-V-Q09 — Canonical append, snapshots and viewer isolation

**IN, V-R06.** Canonical ingestion/commit and non-droppable command/lease/process-exit/termination/effect facts precede presentation. Required refused-command evidence stays in its authoritative receipt journal. Optional span, frame and profiling queues may coalesce/drop under explicit loss counters. They are never the reconstruction oracle. If mandatory ingestion cannot durably proceed, the originating operation must be held/throttled or safely stopped under its admitted policy; no claim of unlimited absorption is made.

Use bounded per-view credit, finite page and work budgets, timeout/disconnect, and a separate control reserve. The writer never awaits a viewer callback, socket drain, exporter flush or graph query. Snapshot construction reads a pinned consistent canonical cut into a bounded worker; it cannot hold the writer indefinitely. A `ProjectionManifest` binds content bytes/digest, projection/schema/filter/audience/policy revision, source event and receipt cuts, replay floor, generation and completeness. It must exist and be verified before advertised installation. Copied, advertised, received, installed and acknowledged cursors are distinct. Content and installed cursor change atomically in the application envelope; a failed install preserves the prior usable generation. Old pins require bounded policy and safe lifetime release, not timeout-based guesses of reader death.

Keep frozen M1B RESET/CREDIT/replay-floor semantics exact; the application manifest is a separate layer. Different projected streams cannot share an unqualified cursor. Saturating a viewer should cause bounded presentation degradation while append, Stop and recovery satisfy adopted budgets under the declared scheduler/host assumptions. Numerical latency is U, not “cannot ever slow anything.” V-F08, V-F09 and V-F12 establish structural nondependency plus measured bounded impact; total machine failure is outside a viewer-only guarantee.

<a id="q10"></a>
## R-V-Q10 — Reproducible explanation across versions

**IN, V-R07.** Reproducibility is equality for the same event/receipt/artifact cuts, canonicalizer, reducer, predicate, explanation schema, audience policy and formatting profile. `latest` resolves to an explicit returned cut. A current-policy redaction may legitimately differ from yesterday's authorized result; the data and disclosure versions must not be omitted from the equality claim.

Canonical output sorts explicit unordered sets and uses stable codes, typed operands and pinned templates. Locale, wall-clock freshness phrases, terminal width and graph positions are excluded from the comparable object; a renderer derives those separately. Record original schema bytes and interpretation version. A versioned pure migration produces a new derived representation with old/new digests and declared loss; it does not rewrite original evidence. Unknown required fields/version yield `unsupported`, not guessed defaults. Historical re-derivation runs the historical admissibility predicate against retained historical authority facts; it never restores those facts as current grants.

Compare a version-specific replay interpreter with a bounded migration-to-common-intermediate-representation interpreter, both checked against independently authored golden vectors. V-F14 changes locale, map order and ambient time, migrates a known older record, then introduces an unsupported field and missing interpreter. A pass proves deterministic output in this version/domain, not that the recorded decision was sound. Explain rendering may be optional; the typed answer and status must not depend on an optional model-generated explanation.

<a id="q11"></a>
## R-V-Q11 — Checkpoint plus suffix replay

**IN, V-R07.** `ReplayRequest` explicitly chooses `state_replay` or `decision_rederive`, requested source cut, trusted checkpoint/catalog references and finite resource envelope. Read-only output goes to a separate diagnostic artifact, never the live writer. Authenticate the current reader and authorize the admitted domain/read scope before checkpoint, receipt or dedup lookup/disclosure; historical effect authorization is not current read permission. Recheck that scope at disclosure and refuse a revoked reader without revealing receipt existence. First validate source/schema/reducer identity and checkpoint binding; then acquire a coherent event/receipt/artifact cut. A checkpoint contains or references actual reconstructable state, open operation/lease/reservation identities, prior digest and typed dependency coverage. A digest without materialized bytes is not a checkpoint.

Starting at the checkpoint's declared boundary, validate contiguous events and their command/receipt groups, obtain required recorded inputs, apply the pure reducer and compare declared digest boundaries. Decision mode additionally recomputes predicates and compares selected/refused/deferred outcomes. Stop before the first event/group whose necessary input is missing or unsupported. Return the last verified cut and exact dependency marker. If framing corruption prevents assigning a trustworthy sequence, report the byte/container position and unverifiable suffix instead of inventing an event number.

M1A's frozen checkpoint convention includes a first `CheckpointRecorded` event bound to the supplied snapshot; adapters must honor it, not impose an off-by-one “checkpoint already consumed” rule. Its replay input resolves each command ID/digest once, while admission can retain repeated delivery of the original receipt in the journal. Preserve that occurrence evidence and explicitly derive the unique logical command/receipt replay view; do not assume the raw delivery journal is interchangeable with replay input. The proposed production operation key is admitted authority domain plus canonical command ID; the digest checks immutable content equality/conflict and preserves actor/authentication reference binding. A principal-local client ID can enter only through the explicit injective canonical mapping, never a silent alternative namespace. It must not double-count a repeated receipt or discard a conflicting one. Authorized historical disclosure and current effect admission are separate checks: a still-readable old accepted receipt after effect revocation remains old accepted evidence and causes no redispatch. V-F14 tests changed payload, caller/principal/domain and revoked read scope outside the frozen pure M1A fixture boundary. Its whole-input decoding and command-group receipts are not a verified first-event diagnostics implementation. V-F05/F06 define a new independent diagnostic oracle. A replayed effect observation restores the recorded statement and pending state; it never reruns a tool, asks a provider, restores live leases or emits production commands.

<a id="q12"></a>
## R-V-Q12 — Nondeterminism and re-execution

**IN, V-R07.** Capture every input that affects a deterministic boundary, not an entire machine by default: time readings used by admission/deadlines, entropy/allocated IDs, accepted scheduling order and concurrency decisions, relevant config/policy/source revisions, provider/tool response fields actually consumed, and external observation/receipt identity. Source clocks have recorded uncertainty; replay does not resample them. A seed alone is inadequate when generator algorithm/version/draw order differs. Unknown ordering remains unknown.

Prefer bounded integers/fixed-unit rationals for admission/accounting; if a component uses floating point, bind representation, rounding, exceptional-value rejection and numerical implementation/version. Never assume cross-platform floating equality or silently epsilon-compare an authoritative digest. For a model-based score/summary, inject the recorded accepted output and label model behavior opaque; deterministic downstream consumption is replayable while model internal computation is not. Optional explanations cannot become missing reducer inputs.

Three labels are mandatory: `replayed_recorded_input`, `rederived_deterministic_result`, and `reexecuted_new_attempt`. The last is a separately authorized operation with current grants, budget, effect reconciliation and idempotency checks, and is not performed by replay. Sandbox replay has no actuator/network/model capabilities even when original receipts contain tool names. V-F10 supplies hostile command-looking response data and traps every execution entrypoint; V-F14 changes entropy/time/platform settings. This is semantic state-machine replay, not rr-style instruction-level machine replay or reproduction of provider behavior.

<a id="q13"></a>
## R-V-Q13 — Digest verification and first divergence

**IN, V-R07.** Compute an independently specified state digest at each defined event or transaction-group boundary and compare with the recorded expected digest. Include namespace, schema/reducer/canonicalizer and state cut in the digest domain. Distinguish event integrity, authenticated origin, projection parity, command receipt parity and decision-verdict parity. Equal rendered status does not prove equal state, and a hash chain does not authenticate a writer.

`ReplayDiagnostic` contains mode, last verified boundary, first failing event/group or unlocatable position, expected/actual digest, error class, missing-input references, dependency frontier, pinned versions, bounded field-level diff and evidence class. Sensitive values remain references or scoped redacted differences. Missing expected digest yields `unverified`, not match. If only group digests were recorded, failure localization is the first differing group; exact internal event divergence is U unless independent intermediate oracles exist. Do not claim stronger localization than recorded evidence allows.

Positive vectors compare against separately authored expected state bytes, not merely the implementation's own save/load output. Negative vectors mutate a predicate, sequence, checkpoint binding, receipt, same-length value and state-relevant input. Separate incidental parse rejection from detecting the intended semantic fault. A common parser/reducer bug can reproduce itself perfectly; independent decoder/oracle and adversarial controls matter. V-F05/F06/F14 distinguish deterministic repeatability from correctness and evidence authenticity.

<a id="q14"></a>
## R-V-Q14 — Recovery, lost node, harness change and fork

**IN, V-R09.** Record `RecoveryStarted` as the current controller's recovery segment with cause observation, prior verified cut, new node/process/writer incarnation, prior/current route/source/config identities, unresolved effects and liability references. Finish with separate restored-state, replay-verified, reconciliation-complete and productive-continuation evidence. A crash time may be bounded by last observation and first detection; do not invent its exact instant. Historical M1A event types need an adapter/candidate extension, not silent mutation.

After lost-node detection, recovered canonical state does not prove the old worker stopped. A new writer follows existing fencing/takeover rules; execution grants and receiver fences are revalidated before actual continuation. Late old-incarnation results remain attributable historical observations and cannot satisfy a new attempt without an explicit admissible join. A harness change starts a new route epoch and accounting segment while retaining the same task/goal lineage; it does not claim an upstream loop or session is portable. A source fork records the exact preserved source binding and new branch lineage but copies no active spend reservation or permit by default.

V-F15 covers crash after intent/before dispatch, after possible application/before receipt, lost node with late result, harness loss with retained capsule, and dirty-source fork with retained original. Read-only replay displays the two segments and outstanding liabilities; it does not itself demonstrate useful resumed work. A later D024 continuation gate must independently verify the result, authority continuity and total accounting on admitted runtime profiles. D028 abrupt-VM-reset durability remains a separate authorized disposable-rig test, unexecuted here.

<a id="q15"></a>
## R-V-Q15 — Cost and cheaper alternatives

**IN, V-R11.** A plain indexed receipt lookup is the cheaper baseline for “what was chosen/attempted?” Full replay buys a check of recorded transitions and decision-input consistency, differential localization and a reproducible state at an old cut. It is unnecessary for every live status request. Compare bounded materialized projections plus on-demand replay against bounded direct event/receipt folds plus checkpoints, under identical authority/coverage requirements.

Measure model invocation attempts and independently observed inference usage, CPU time, wall time, peak resident/commit memory, logical/physical I/O where available, bytes read/written, artifact hydration, event/reference count, cache state, output bytes, viewer/exporter overhead and human diagnosis time. Parent/history costs are separate from the marginal explain/replay operation. Original model consumption remains in the historical ledger and is not charged again by replay, but not erased either. Additional model-token consumption is expected zero for the operation; unknown historical usage stays unknown.

A streaming fold is approximately O(suffix events + validated referenced bytes + projection work), not a universal complexity guarantee: linear searches, sorted copies, graph fan-in and materialization can dominate. Measure these rather than calling a bounded fixture scalable. Cap replay bytes/events/CPU/wall time and artifact fan-out, expose cancellation, and stop with `budget_exhausted` retaining the last verified cut. Disabled rich views do no view-attributable rendering/indexing/model activation, but core metadata and required evidence still have costs. R-O owns production budget calibration. V-F17 uses required-evidence-only, local metrics, and explicit rich trace/export arms; no numeric production winner exists.

<a id="q16"></a>
## R-V-Q16 — Honest counters and reconciliation

**IN, V-R08.** Counters are typed records, not unqualified numbers. Every raw report has source/collector/schema/version, operation/attempt/role/route/node/session/meter epoch, native unit, interval, cumulative-or-delta semantics, inclusion set, observed time, raw value/presence, coverage and integrity. Validation produces a separate value/status/reason and reconciliation lineage; the raw statement never silently becomes actual usage. A known numeric report may validate as unknown consumption after a crash, meter reset or uncovered helper.

| Counter family | Counting boundary and unknown rule |
|---|---|
| Decisions, admissions, refusals, queues/deferrals | Unique bound decision/command receipt, with duplicate/retry receipts deduplicated; incomplete receipt cut makes the scope incomplete |
| Retries, route switches | New attempt and explicit route-epoch transition, respectively; a reattachment is neither; absent transition evidence stays unknown |
| Compactions, rehydrations | Separately requested/attempted/installed transitions and artifact revisions; failed transforms and missing metrics remain visible |
| Effects | Intended/dispatch-attempted/receiver-accepted/applied/observed-failed/settled/unresolved counted separately; no inferred application from success prose |
| Wasted/recovered work | Named unit and criterion (discarded bytes, superseded attempts, verified reused artifact, recovered accepted output); semantic “waste” is an explicit classification, not all retries automatically |
| Human corrections | Authenticated correction event with subject/revision/class; observing a changed artifact does not prove who corrected it or why |
| Resources and inference | Roles include planner, worker, router, compactor, verifier, retry, recovery, permission/token-count and external-harness helpers where present; missing role coverage is retained |
| Observer failures | Coalesced/dropped optional frames/spans, unavailable meters, export rejects, query truncation, replay gaps and collector coverage; collector death cannot report clean zero |

Cumulative reports 10, 15, 15 for one proved meter epoch yield 15 total, not 40. A parent total 100 explicitly including child 30 stays 100 for that inclusive scope; child 30 is an attribution subview, not another charge. If inclusion semantics are unavailable, totals are unreconciled. A reset starts a new meter segment only with trustworthy reset evidence; a decrease without it is invalid/unknown, not negative consumption. Proved segments 15 and 4 yield 19 across segments; task allowance never renews just because the provider window resets.

A synthetic crash report of raw `0` with incomplete terminal coverage becomes validated `value:null, reason:crash_incomplete_meter`; its bounded liability remains outstanding. A confirmed no-call operation may legitimately have zero inference attempts within a complete independently witnessed boundary. Shared helpers stay explicit parent overhead/unknown; arbitrary proportional allocation cannot become measured child usage. Money, token categories, subscription debit, rate-limit capacity, host resources and human time stay separate. Normal and recovery subtotals roll into one conserved parent ledger exactly once. V-F07/V-F18 cover these exact examples and fresh-session/fork/reset attempts to mint allowance.

<a id="q17"></a>
## R-V-Q17 — Privacy-preserving telemetry contract

**IN, V-R10.** Optional telemetry is off until explicitly enabled; exports are separately off and recipient/purpose scoped. Required canonical evidence and safety/accounting still exist locally with content-minimal receipts. A telemetry catalog declares field type/classification, finite label vocabulary, sensitivity, collection purpose, owner, source, retention, resolution/bucketing, maximum cardinality, maximum bytes/rate, sampling/loss semantics and approved export shape. Unsupported fields are refused. No auto-instrumentation, background indexing or SDK activation merely to explain disabled status.

Local aggregation precedes authorized export. Compile only allowed aggregate fields from a pinned authorized cut; remove raw payloads, identifiers, account/session data, exact private sizes, paths and equality-revealing digests. Bound series, rare buckets, per-window volume and joinability; expose suppressed/unknown coverage without leaking private counts. Per-export aliases, where needed for a requested diagnostic, are scoped to that export and not derived from stable identifiers. Differential privacy could be a separately assessed aggregate option with an explicit privacy budget; this candidate claims neither anonymity nor a formal DP guarantee.

Privacy falsifiers include any forbidden field/canary in bytes, filenames, error messages, dead-letter queues or temporary/export archives; cross-project linkage from a stable handle; unauthorized endpoint attempt; and a predeclared membership/timing/rare-label attack exceeding its accepted risk bound. Passing string-redaction tests proves only the supplied leakage cases. Finite retention and opt-in do not eliminate inference risks. V-F09/V-F19 test content and metadata; production threat model/thresholds remain U pending explicit adoption.

<a id="q18"></a>
## R-V-Q18 — Local explanation versus public/support export

**IN, V-R10.** Local explanation resolves privileged references only after read authorization and carries source taint/rights/retention from R-P/R-Q. A support export is a new disclosure operation with exact recipient, purpose, fields, time window, expiry and reviewable output manifest. It may be an aggregate-only summary or a synthetic minimized reproduction; neither receives an implicit grant to send local evidence. The report itself sends no telemetry or support package.

The compiler begins from an allowlisted export schema, not a full local trace plus regex cleanup. Provenance records transformations without copying the sensitive source. Reject unknown nested fields; tokenize errors into bounded codes; strip URL query strings and secret-bearing headers before persistence into general logs. Scope checks precede query/materialization, not just rendering. Exclude prompts, source/tool output, private paths/repository membership, credentials, stable cross-project IDs, raw private hashes and hidden-reasoning/opaque reasoning payloads. A local protected source may itself require an authorized retention facility; explanation needs only permitted fields, never an excuse to ingest credentials.

An export manifest binds compiled bytes, redaction policy, allowlist version, local evidence cut, exclusions, unresolved risks and approval/destination. Digest verification proves the approved bytes, not their privacy. Signed raw telemetry is still raw telemetry. Error handling must not log the rejected payload. V-F19 uses two synthetic projects with identical private content and deliberately malicious fields to falsify equality/cross-scope leakage. Network delivery is outside the fixture and requires separate authorization.

<a id="q19"></a>
## R-V-Q19 — Deterministic anomaly diagnostics

**IN, V-R12.** A finite declarative rule set consumes authorized local projections: retry count/rate crossing a configured window, reserved-plus-consumed burden near its limit, required evidence gap, repeated containment refusal, overdue unresolved effect or meter staleness. Rules specify version, predicate, window/clock, minimum coverage, severity, cooldown/deduplication key, audience, resource ceiling and expiry. A gap produces an evidence-availability alert, never “healthy” from missing samples.

Output is `DiagnosticRecord`: observed facts, matched predicate/operands, inferred cause hypotheses separately tagged, alternatives, unknowns, exact source cuts and bounded next checks. “Retry threshold exceeded” is a fact about records; “provider intentionally wastes quota” is unsupported and prohibited. No model is required. A rules engine may propose a reviewed next step but cannot launch a worker, create a standing executive, activate adaptation/research, acquire credentials, widen grants, change budget or apply a fix. Safety admission can independently enforce already accepted ceilings; the diagnostic plugin is not their owner.

Compare event-driven threshold rules with on-demand deterministic diagnosis or bounded admitted polling of existing local projections. Both preserve no hidden agent and explicit budgets; an autonomous remedial agent is a negative control. Notifications use an approved destination and bounded delivery policy; suppressed alerts are counted without a notification storm. V-F20 checks threshold crossings, clock jumps, gaps, deduplication, disabled state and attempted self-activation. R-R owns any separately authorized ongoing scheduling, not the observability rules.

<a id="q20"></a>
## R-V-Q20 — Explicit non-proofs

Neither explanation nor replay proves optimal routing, useful work, truthful source reporting, complete hidden helper accounting, model internals, causal optimality, external semantic fidelity, delivery/application/rollback without relevant receipts, security against an arbitrary host, all-platform determinism, production durability, absence of private side channels, route entitlement, legal compliance or comparative efficiency. A trace ordering two events does not prove the first caused the second. A matching digest can preserve a mistake exactly. No anomaly means only no rule fired over available evidence, never correctness.

A deterministic predicate result answers why the implemented policy selected a recorded option; it does not justify that policy. Diagnostic hypotheses remain hypotheses even when plausible or repeated. Unknown or stale required evidence prevents a completeness claim. Passing provider-free fixtures shows behavior only in their finite declared domain and independent observation boundary. Failure or missing preregistration is not a pass. The recommendation register binds each narrower non-proof as well.

<a id="q21"></a>
## R-V-Q21 — Provider-free acceptance fixtures

All fixtures below are **UNEXECUTED local handoffs**. Full inputs, prerequisites, independent oracles, evidence, stopping conditions and non-proofs are in [local-test-handoffs.json](local-test-handoffs.json) and its [readable handoff](UNEXECUTED-local-test-handoffs.md). [synthetic-fixtures.json](synthetic-fixtures.json) contains finite input/oracle examples, including hand-authored expected state bytes/digests; generating those artifacts is not running a reducer or target test.

| Fixture | Exact acceptance obligation |
|---|---|
| V-F01 routing/refusal | A selected, B privacy-refused, C eligible-not-selected at the pinned cut; all operands/versions preserved; missing descriptor yields typed incomplete re-derivation and no invented refusal |
| V-F02 admission/resources | Disjoint `3+5+3+9=20` accounting and atomic headroom transfer produce the expected admit/queue/defer/refuse; the tagged-reserve alternative counts control only once; unknown headroom never permits strict admission; zero implicit plugin activation |
| V-F03 compaction | One governor, complete disposition map, exact directive/approval/effect references and explicit fidelity verdict; mutated/missing exact control fails installation, not merely warns |
| V-F04 effects honesty | Synthetic intended/accepted/applied/observed/settled states remain distinct; no external applied/rolled-back claim from process exit or transport ACK |
| V-F05 replay determinism | Same checkpoint/suffix and independent expected states produce identical canonical bytes/digests at every declared boundary with zero effect/model dispatch attempts |
| V-F06 first divergence/gap | Missing input for event 4 stops before event 4 with last verified cut 3; mutation at event 5 reports 5 when earlier required inputs exist; no continuation labeled verified |
| V-F07 unknown counters | Absent and crash-invalid zero become null validated usage with reasons; proved complete zero stays zero; unknown numerator/denominator produces null ratio |
| V-F08 slow/absent viewer | Queue and query ceilings hold for no viewer, stalled viewer and hostile fan-out; canonical/control path never waits on viewer; adopted append/Stop/recovery budget and loss-marker predicates hold |
| V-F09 export redaction | Export disabled makes no endpoint/activation attempt; allowed export contains only allowlisted synthetic aggregate fields; all content/metadata canaries and forbidden stable IDs absent |
| V-F10 no hidden inference | Independent local/remote-model, plugin-load, actuator and network tripwires detect positive controls; explain/status/replay cause zero attempts within fully covered entrypoints |
| V-F11 Stop/effect boundaries | Aggressive target, Full owned closure and Lazy operation boundary remain distinct; unreachable remote and uncertain effect stay unresolved; requested never displayed as observed |
| V-F12 snapshot/cache isolation | Wrong scope/filter/generation/digest or uninstalled bytes cannot advance installed cursor; crash points preserve prior or fully installed envelope and latest authoritative reservation |
| V-F13 causal joins | Fan-in has both explicit causes; wrong node/attempt ID and untrusted header cannot join authority; wall-clock reversal does not reorder canonical events |
| V-F14 versions/nondeterminism | Recorded time/entropy/schedule and pinned interpretation give exact outputs; reader/domain authorization precedes lookup; changed payload/principal/domain and revoked read scope cannot misuse dedup; historical receipts never redispatch; unsupported versions refuse; group-only digests do not claim event-local localization |
| V-F15 continuity | Crash/lost-node/harness-change/fork segments retain original effects, authority history and accounting; replay launches no continuation or duplicate effect |
| V-F16 retention | Expired artifact yields typed dependency loss; authorized purge invalidates all fixture cache copies and does not claim full replay from metadata alone |
| V-F17 observer tax | Required-only, metrics and rich-trace arms include all declared observer resource costs; missing measurements remain U; resource exhaustion ends at last verified cut |
| V-F18 reconciliation | Cumulative 10/15/15 becomes 15; inclusive parent 100 plus child 30 remains total 100; proved reset 15+4 becomes 19; missing inclusion/reset remains unreconciled |
| V-F19 metadata privacy | Cross-project aliases/caches and deterministic hashes cannot correlate synthetic secrets; unknown fields/error payloads fail closed; rare/timing attack result is evaluated against adopted bounds |
| V-F20 anomaly boundary | Expected deterministic alerts/deduplication appear; unknown coverage is not healthy; zero remedial agent, model, credential, policy or budget mutation attempts |

<a id="q22"></a>
## R-V-Q22 — Independent witnessing and limits of the fixtures

The zero-model claim needs independent sensitivity, not a JSON field prefilled with zero. Before each fixture, the future authorized local runner invokes synthetic positive-control stubs for model/client dispatch, local inference entrypoints, plugin activation, child-process/network attempts and actuator dispatch; each must trip the witness without reaching a live endpoint. During the measured operation all prohibited attempt counts must equal zero. An unobserved path, failed witness or target escape makes the result **UNVERIFIED**, not zero. Required status/explain/replay run with provider integrations absent, installed-disabled and with hostile synthetic descriptors, including upstream-only tasks. These fixtures do not contact a provider or telemetry endpoint.

For writer isolation, use a separate canonical/control observer and storage/snapshot oracle. Saturate view queues and stop their consumers while admitting a known finite canonical/control sequence; compare the complete committed identities/order and Stop receipt/settlement vector, plus queue bytes and adopted tail/deadline budgets. Structural absence of a callback dependency and finite schedule tests complement timing measurements; neither alone proves universal nonblocking. Optional streams may show drop markers; required facts remain durable or work visibly refuses before unsafe loss.

For gaps, independently remove a specified required input at a known cut, including an otherwise valid later suffix; require the exact last verified boundary, unknown and gap marker. For redaction, inspect all synthetic output channels, files, diagnostic errors and compiled export bytes, then attempt cross-scope/rare-label joins. A clean scan only establishes the declared finite corpus and observation scope. Independent verification at the exact candidate pin, on D028 profiles where applicable, is still required. No fixture here is implemented or measured by this research.

<a id="recommendations"></a>
## Competing designs, falsifiers and non-proofs

Every proposal above is covered by this register and [recommendations.json](recommendations.json). All rivals below preserve the accepted invariants; unsafe options appear only as negative controls.

| ID | Design candidate and admissible competitor | Decisive falsifier | What a pass does not prove | Negative control |
|---|---|---|---|---|
| V-R01 | Stored typed decision certificates + independent re-derivation vs complete immutable input snapshots + query-time predicate evaluation | A required historical operand/verdict cannot be reproduced or a refusal becomes selection | Optimal policy or complete discovery | Model-written post-hoc rationale as authority |
| V-R02 | Exact control capsule + compaction receipts vs versioned artifact graph + receipt-bound manifest diff | Lost directive/approval/effect is accepted as fidelity pass | Natural-language semantic equivalence | Summary replaces authoritative controls |
| V-R03 | Effect state vector projected from receipts vs separate per-stage receipt timeline with explicit unknowns | ACK/exit/Stop request becomes applied/rollback/settled | Truth of an unverified receiver | One success badge |
| V-R04 | Inline typed gap/completeness markers vs a separate mandatory coverage record joined by cut | Missing required input silently omitted or zero-filled | Completeness outside declared scope | Best-effort transcript fills gaps |
| V-R05 | Event-first typed causal DAG projected on demand vs bounded persisted edge index derived from the same event/receipt cuts | Unrecorded causal edge or wrong-incarnation join presented as fact | Physical causality or model reasoning | Infer parents from timestamp proximity |
| V-R06 | Bounded pull pages/snapshots plus notifications vs bounded credited push with replay/reset | Stalled viewer blocks canonical/control progress, unlimited queue or wrong-scope install | All-load latency or storage durability | Shared unbounded subscriber queue |
| V-R07 | Version-specific pure replay interpreters vs pure migration to a common versioned representation | Expected state/decision mismatch, hidden input, bad localization or any execution during replay | Original correctness or external reproducibility | Replay reruns tools/model to repair history |
| V-R08 | Event-level disjoint ledger reconciliation vs periodic retained native-unit reconciliation with identical coverage semantics | Child duplication, cumulative double count, false zero or reset renews task allowance | Provider billing completeness | Sum every report; failure is free |
| V-R09 | Unified lineage with explicit recovery segments vs linked immutable segment logs with authenticated cut manifests | New segment loses liability/authority provenance or revives old permits | Useful continuation or failover qualification | Resume session implies resumed authority |
| V-R10 | Aggregate-only allowlisted export vs explicitly approved synthetic minimized reproduction | Any forbidden content/linkability or unapproved egress in declared threat corpus | Universal anonymity/compliance | Upload raw trace then scrub |
| V-R11 | Materialized bounded status + on-demand replay vs indexed direct fold/checkpoints with identical evidence | Budget breach, omitted observer tax or implicit activation in declared profile | Cross-workload advantage | Claim literally zero resources |
| V-R12 | Event-driven bounded deterministic rules vs on-demand diagnosis/bounded approved local polling | Rule self-activates agent, widens policy, or reports healthy from missing coverage | Absence of incidents | Standing autonomous remediation executive |

Structured event records, causal spans/graphs, deterministic re-derivation and sampled profiling are complementary layers, not four replacements for mandatory evidence. A genuine comparison holds mandatory canonical/receipt records fixed: **A** minimal complete records plus on-demand explanations; **B** same records plus bounded causal index/materialized views; **C** same records plus optional sampled profiler. Compare diagnostic fidelity, time-to-first-correct diagnosis, observer resource vector and disclosure surface on identical faults. The sampled arm cannot claim complete event coverage; the index arm must prove rebuild parity; the direct arm must fit bounded query budgets. No telemetry architecture is selected by this proposal.

<a id="handoff"></a>
## Local handoff, unresolved decisions and completion

The highest-leverage next authorized construction is a provider-free explanation/replay adapter at an exact candidate pin, preserving M1A/M1B unchanged and exposing typed evidence/diagnostic seams. Its first independent gate should cover V-F01/F04/F05/F06/F07/F10/F12 before an exporter or rich graph is connected. A compliant alternative is a separate golden-vector interpreter first, then integration. This sequencing is a research proposal, not permission to implement or shrink accepted capability scope.

Open decisions/evidence: adopt finite production event/query/graph/retention/queue/replay budgets and control headroom; bind canonical and refusal-journal cut semantics for the selected store without selecting it here; retain old predicate/schema artifacts under current privacy policy; define approved privacy attack thresholds and export audiences; independently verify the role/meter inclusion maps; implement first-divergence reporting rather than relabel existing exceptions; qualify snapshot installation and Stop under real scheduler/storage faults. Each maps to explicit handoffs in the machine register. If prerequisites are missing, the local run is **BLOCKED**, not an invitation to invent a command.

No general R-V runtime test entrypoint was verified. Existing M1A functions and historical replay-store probes are evidence references, not sufficient commands for this suite. Handoffs therefore specify adapter inputs/outputs and oracles without fabricated runnable commands. Owner-authorized native Windows/Linux and separately labeled WSL dev/test sessions remain necessary for profile evidence. VM-reset/power-loss and live route qualification are outside these synthetic tests.

<a id="completion"></a>
### Completion disposition

- G01: typed routing/admission/compaction/effect explanation and independent lifecycle facts are defined in Q01–Q05
- G02: requested/observed/rollback boundaries, late evidence and gap markers are explicit in Q04/Q05/Q11/Q14
- G03: versioned identities/schema, retention/redaction and bounded views are defined in Q06–Q10
- G04: checkpoint/suffix, recorded nondeterminism, digest/localization and continuity are defined in Q11–Q14
- G05: counters/unknowns and opt-in bounded local-first export are defined in Q16–Q19
- G06: all eight required fixture categories plus twelve composition/negative fixtures have exact UNEXECUTED predicates in Q21–Q22 and the handoff register
- G07: zero additional inference is an expected witnessed property; host costs and non-proofs remain explicit in Q15/Q20/Q22
- G08: every recommendation has a conforming rival, falsifier and non-proof; nothing is selected or qualified
- G09: the research report records artifact-only integrity/privacy checks and protected-source equality against the verified committed snapshot manifest. [Packet quality notes](../QUALITY-NOTES.md) distinguish those historical observations from release checks. Clean finite scans are not proof of universal privacy

The precise 31-item coverage map preserves the brief's exact questions and completion bullets in [coverage.json](coverage.json). Runtime acceptance, performance measurements, privacy certification and independent research review remain pending.
