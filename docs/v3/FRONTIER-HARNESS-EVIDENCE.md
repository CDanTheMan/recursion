---
title: Recursion v3 frontier harness evidence and gap matrix
status: active-research-synthesis
last-updated: 2026-09-03
campaign-id: FHAR-20260903
---

# Frontier harness evidence and gap matrix

This is the persistent evidence product for
[FHAR-20260903](FRONTIER-HARNESS-RESEARCH-CAMPAIGN.md). It compares exact public source
revisions and primary specifications with Recursion's repository-local contracts. It is a
documentation and static-source result. It does not establish runtime behavior, performance,
resource savings, frontier superiority or production fitness.

## Evidence types and review boundary

| Type | Meaning |
|---|---|
| `direct-source` | Sol opened the cited primary specification, paper or exact source revision and checked the stated locator. |
| `repository-fact` | Direct inspection of the Recursion tree at the campaign base; deployment behavior is not inferred. |
| `owner-direction` | Lucas's accepted product direction; not automatically operative constitutional text. |
| `adaptation` | Recursion design inference from bounded evidence; must carry a competitor and falsifier. |
| `unverified` | Plausible claim that needs a controlled local experiment or missing denominator. |
| `rejected` | Evidence is insufficient, contradicted or outside its applicability boundary. |

All eight Luna packets were produced with `gpt-5.6-luna` at `xhigh`. The two Terra reviews,
when complete, use `gpt-5.6-terra` at `xhigh`. Sol, Luna and Terra are GPT-5.6-family routes;
their agreement is same-family adjudication, not cross-family independence. Workers were
read-only and returned sources, conclusions, contradictions and concise rationale rather than
private reasoning transcripts.

The canonical versions, licenses, locators and expiry rules for this campaign are
[SRC-V3-052–SRC-V3-086](SOURCE-REGISTER.md#frontier-harness-campaign-sources). The trace is:

| Area | Consequential source records |
|---|---|
| harness code | `SRC-V3-052`–`SRC-V3-059` |
| durable histories and recovery | `SRC-V3-013`, `SRC-V3-060`–`SRC-V3-062` |
| cache/context | `SRC-V3-034`–`SRC-V3-036`, `SRC-V3-040`, `SRC-V3-052`–`SRC-V3-054`, `SRC-V3-059` |
| terminal and multi-view | `SRC-V3-020`–`SRC-V3-025`, `SRC-V3-063`–`SRC-V3-068` |
| plugins and future clients | `SRC-V3-004`, `SRC-V3-005`, `SRC-V3-052`–`SRC-V3-054`, `SRC-V3-069`, `SRC-V3-070` |
| autonomy and evaluation | `SRC-V3-056`, `SRC-V3-071`–`SRC-V3-081` |
| systems performance | `SRC-V3-001`–`SRC-V3-003`, `SRC-V3-022`–`SRC-V3-024`, `SRC-V3-082`–`SRC-V3-086` |

## Recursion baseline inspected

At campaign base `a97d5181ee413b87597ea58523708bb9a53f750b`, the production-oriented v2
inventory contains 58 Python files/46,109 lines, 47 shell files/12,647 lines and 30 schema
files/1,823 lines; tests contain another 79 Python files/37,307 lines and 32 shell
files/7,817 lines. Large files and repeated terms such as digest, lock, validation, atomic
write and JSONL append are structural signals for boundary research, not proof of bloat or
duplication. V2 dispatch adapters are mostly one-shot; only the Hermes route receives the
current usage-file integration, and missing provider receipts are correctly treated as
unknown rather than zero. No v2-native resumable provider session, turn loop, context
compactor, prompt cache or multi-view terminal protocol was found. These are
`repository-fact` observations, not deployed-state claims.

## Harness corpus and code paths

The selected eight repositories cover provider-native CLI, HTTP/event server, local/remote
SDK, finite benchmark agent, Git-first editing, explicit effect state machine and an
experimental durable session harness. Continue, Cline and Roo Code were sampled during
discovery but excluded after their strongest IDE/presentation evidence overlapped the selected
execution/session mechanisms. OpenHands' `software-agent-sdk` was selected instead of its
UI-heavy application repository because it exposes the actual conversation/server code path.

| Harness and exact source | Entry to effects and recovery | What transfers / what does not |
|---|---|---|
| OpenAI Codex [`280ae8b`](https://github.com/openai/codex/tree/280ae8b9fcd35a54704dc2c78027b89bd51369fd), Apache-2.0 | `codex-rs/cli` → thread/session turn → model stream → tool futures → rollout/state and app-server events → compaction, resume, fork, interrupt and approval. `app-server/README.md` specifies bounded ingress queues, overload refusal, version-specific schemas and thread/turn/item lifecycle. | Adapt stream/tool/approval, reconstruction, typed protocol and bounded queue behavior. Its thread/session/account is not Recursion Owner, GoalSpec, budget or publication authority. |
| Gemini CLI [`86b461e`](https://github.com/google-gemini/gemini-cli/tree/86b461ea2cdb1c847775433b820ce6b6ada0e63c), Apache-2.0 | CLI/noninteractive entry → `GeminiClient.processTurn`/`sendMessageStream` → `Turn.run` → scheduler/tool executor → chat history/recording → confirmation bus, compression, loop detection, cancellation and retry/fallback. | Adapt context estimation, loop recovery, tool scheduling and confirmation observations. Provider/project/session state is not durable cross-provider authority. |
| OpenCode [`8a6cf2c`](https://github.com/anomalyco/opencode/tree/8a6cf2c9aa1aa407129efc4e875a6ce6ab32ef72), MIT | run command/server → session prompt/processor → AI SDK → tool registry → session/effect/storage/event APIs → permission reply, compaction, revert and fork. | Adapt client/server and event/session graph. Engine permissions and events are not Recursion grants, effect receipts or verification. |
| OpenHands SDK [`07307cb`](https://github.com/OpenHands/software-agent-sdk/tree/07307cb8edfcd9b4675be2761df0646d075a9c36), MIT | conversation API → local conversation → agent step → tools → state/event store → server fanout/replay and conversation lease. | Adapt append log, sequence/replay, local/remote boundary and lease-guarded writes. Conversation-local state lacks Recursion's cross-run GoalSpec, grants, budget and publication chain. |
| SWE-agent [`3ea751c`](https://github.com/SWE-agent/SWE-agent/tree/3ea751c087f32b16e039a2233dd6eefecef325d5), MIT | `run_single` → agent action loop → model → tools/environment → trajectory/patch/evaluator hooks → parser, retry, time/cost and environment failure paths. | Adapt bounded action/observation and benchmark adapter patterns. One-process trajectories do not provide durable approval, lease or sovereign evidence. |
| Aider [`5dc9490`](https://github.com/Aider-AI/aider/tree/5dc9490bb35f9729ef2c95d00a19ccd30c26339c), Apache-2.0 | main → coder loop → model → apply updates/Git → history and commits → malformed-edit reflection, lint/test and undo/confirmation. | Adapt Git edit/undo, context and deterministic test hooks. Git/history alone is not owner authority or cross-engine orchestration evidence. |
| Goose [`c59e45d`](https://github.com/aaif-goose/goose/tree/c59e45d0eefa68aac6f11bacc58123bfcfa3d000), Apache-2.0 | CLI session → `machine.rs` state machine → inference → tool/effect pipeline → SQLite session/usage state → confirmation, cancellation and yield. | Adapt explicit procedures and effect-before-publish shape. Its database, recipes and permission store are engine-local, not Recursion authority. |
| pi-mono [`6aedd10`](https://github.com/badlogic/pi-mono/tree/6aedd1066e540642165aa30fa7b4a1b863778aa7), MIT | experimental session worker → harness `drive` state dispatch → generation/assistant → tools/effect gate → serialized JSONL session/mutation line → recovery, snapshots and watches. | Strongly adapt transaction sequence, lanes, effect-pending recovery and snapshot/event replication. The harness is experimental and has no Owner/GoalSpec/ARM/grant/publication contract; use as interface evidence, not a dependency decision. |

The common successful unit is an engine-local loop: render context, sample/stream, parse tool
calls, execute tools, update a transcript and recover/retry. No inspected member demonstrates
cross-provider replay of one owner-governed logical operation while preserving authority,
budgets, PAUSE, effect fencing, verification and publication provenance. This bounded negative
finding may be falsified by a complete code path outside the inspected revisions.

## Durable execution findings

| Finding | Evidence and limits | Recursion disposition | Competing option / failure mode / decisive test |
|---|---|---|---|
| Canonical commands and event replay must be pure. | Temporal/Durable Task replay histories, Restate log-first epochs, Akka event-handler separation and the existing M1A reducer support the mechanism. Workflow products do not supply Recursion authority. | `adaptation`: authenticated command with expected version/digests → one reducer → append → rebuildable projection. Replay never repeats an external effect. | Database CRUD/projection-first is simpler but permits divergent truths. Crash/tamper/gap/duplicate replay must reproduce one digest or fail closed. |
| A lease is not a fence. | Kubernetes Lease expresses holder/renewal/TTL; Restate rejects stale attempts with epochs. Expiry does not prove an already-running process or effect stopped. | `adaptation`: bind monotonically increasing fence epoch to WorkPacket, effect intent, actuator and result; stale observations are quarantined. | TTL-only admission risks late writes. Force takeover and delayed result; any accepted stale epoch falsifies the design. |
| Correctness-affecting timers/retries are history. | Workflow engines distinguish durable timers/reminders from activation-local or matching-only behavior. | `adaptation`: durable timer identity, schedule/fire events, attempt, failure fingerprint and retry novelty. | Scheduler-only retry is lighter but cannot replay why another effect occurred. Restart before/after fire; event and terminal digest must match. |
| Cancellation is a state machine, not a kill signal. | Temporal cancellation/heartbeats, cooperative task cancellation and OS primitives show propagation and termination are distinct. | `adaptation`: `requested → propagating → acknowledged/compensating → terminal`, bound to identity and epoch. | Process-kill-as-success loses remote/partial effects. Crash and kill at every effect boundary; ambiguity must never become success. |
| Exactly-once is not a safe external-effect claim. | Temporal, DBOS, Restate and actor systems bound their guarantees; external calls can remain ambiguous. | Preserve `PREPARED/EXECUTING/RECEIPT/AMBIGUOUS`, idempotency and reconciliation. | Vendor exactly-once label is shorter but overclaims. Inject crash after remote acceptance before receipt; the system must quarantine/reconcile rather than replay blindly. |
| Backpressure needs typed refusal and protected recovery capacity. | Temporal worker capacity, Prefect/Dagster pools, bounded actor stashes and Codex bounded app-server queues demonstrate distinct policies. | Bounded queues with `capacity`, `budget`, `dependency`, `paused` and `recovery-required` deferrals; reserve admission for verification/recovery. | Unbounded buffering improves short bursts but can exhaust coordinator memory and hide review debt. Saturation test must bound memory and preserve control latency. |

Use Temporal, Restate, DBOS, Durable Task, Orleans, Akka, Prefect and Dagster as comparison
sources, not production dependencies. Their server/database/language/licensing costs and replay
constraints are counterevidence against importing a workflow platform into the privileged v3
kernel. A small TLA+/PlusCal model is appropriate for lease, duplicate-command, replay,
cancellation and ambiguity invariants, but model checking cannot prove implementation
refinement without explicit I/O assumptions and conformance tests.

## Context, token and cache findings

| Mechanism | Classification and exact boundary | Disposition and falsifier |
|---|---|---|
| Recursion event/context lineage | `adaptation`: canonical session events and content-addressed `RepositoryMap`, `EvidenceBundle`, `DecisionSlice` and `CheckpointSummary` are provider-neutral; no runtime exists yet. | Adopt contract. Falsify if replay loses an active directive/digest or cross-route rehydration changes accepted state. |
| Deterministic compaction transaction | DeepSeek Harness records start/summary/end, shadowed sequence IDs and validation; Codex/Gemini/pi expose engine-native compaction paths. | Adapt: old epoch stays authoritative until fidelity validation admits the replacement; keep rehydration locators. Compare deterministic capsule, native compaction and hybrid. |
| OpenAI API prompt caching/compaction | Official API exposes route/model-specific caching controls/counters and opaque native compaction. It does not establish Codex OAuth CLI behavior, subscription debit or portable cache state. | Adapter-only. Opaque compact output may accelerate continuation but cannot be the only owner-intent copy. Any claim without exact endpoint/model/account/SDK and observed counters is rejected. |
| Anthropic API prompt caching | Official API exposes hierarchy/breakpoints, TTL choices and read/write counters. No evidence establishes equivalent Claude CLI control. | Adapter-only; tool/system changes invalidate downstream cache. Falsify savings through direct counters on the exact admitted route. |
| Gemini API context caching | Official API distinguishes implicit and explicit cached content and reports cached-token usage for supported routes. CLI behavior and savings remain unknown. | Adapter-only; pin endpoint/model and TTL. Missing counter is unknown, never zero. |
| vLLM/SGLang prefix/session caches | Exact local-runtime source exposes hash/cache/session mechanics; cache identity is model/template/token/tool-schema/runtime/tenant scoped. | Optional local adapter. Provider KV portability is rejected. Test tenant salt, stale session, eviction and cold/warm behavior. |
| Provider session affinity | Disposable routing hint or native continuation, not canonical actor state. | Prefer when measured, but a fresh route plus validated capsule must remain a recovery path. Falsify if churn loses authority/evidence or same-session benefit is not observed. |

Stable prompt prefixes should place invariant instructions and schemas before volatile task data,
but cache optimization must never freeze stale repository instructions or cross a privacy
boundary. Semantic cache identity must bind project/privacy domain, GoalSpec and policy digests,
source commit/file digests, tool/schema version, engine/provider/model/template and permission
scope. Cache membership/timing may itself leak information, so raw digests or artifacts cannot
be shared across trust domains.

## Terminal, TUI and multi-view findings

| Concern | Direct-source evidence | Proposed contract / falsifier |
|---|---|---|
| Process lifetime and views | tmux and Zellij separate session processes from clients; Recursion's owner direction requires closing a terminal not to end work. | One durable broker owns PTY/process lifetime; views never create actor identity. Attach must not issue another model call or relaunch an ambiguous process. |
| Render stability | Ratatui double-buffers and diffs cells, including wide-glyph cleanup; Textual uses dirty regions; Bubble Tea and Ink batch changed frames/lines; xterm.js schedules dirty-row rendering. | Renderer is replaceable presentation. Golden tests cover wide/combining glyphs, resize, alternate screen, cursor and malformed UTF-8; p99 frame/input targets are measured, not asserted. |
| Slow-client control | tmux tracks consumer offsets and stops PTY reads; Zellij bounds native client queues/disconnects full clients; xterm.js documents its watermark is not backend flow control. OpenCode has bounded retained PTY text but an unbounded per-client path. | Protocol uses monotonically increasing byte/event cursors plus `ACK/CREDIT`; bounded per-view queues end in replay or explicit `RESET+GAP`. A stopped reader must not grow broker memory or block canonical append. |
| Input/resize authority | Terminal libraries assume one input reader; multiple views create conflicts that cell renderers do not solve. | One fenced, expiring input lease and one resize policy; passive watchers cannot write. Simultaneous inputs under stale leases must be refused deterministically. |
| OS portability | POSIX PTY/session/groups+cgroup v2 and Windows ConPTY+Job Objects provide different transport/containment primitives with documented escape/race cases. | Separate adapters behind one process contract. Child/grandchild, breakaway, host-death, resize/output-race and restart reconciliation fixtures are mandatory. |
| Accessibility | xterm.js implements ARIA rows/live-region behavior; Ink has a screen-reader mode; terminal color/cursor support varies. | Provide semantic plain-text/event views, reduced motion and non-color authority cues. Test NVDA/Narrator/AT-SPI rather than claiming compliance from a library. |

Ratatui+crossterm is the leading native-renderer candidate and xterm.js the browser-terminal
candidate; Zellij is the strongest inspected multi-client/flow-control pattern. These are
research recommendations, not selected dependencies. tmux/Zellij may be optional adapters but
cannot be canonical actor or replay storage.

## Autonomy, evaluation and owner-review science

Static code review does not identify whether a result came from the model, action/observation
interface, planner, delegation topology, verifier, retry policy or harness. SWE-agent supplies a
useful fixed-model interface ablation; SWE-bench, tau-bench, METR's time-horizon method, the
Agentic Benchmark Checklist, contamination research and variance research supply complementary
controls. Their results are method precedents, not Recursion outcome evidence.

The required comparison is a matched, preregistered component ladder: minimal deterministic loop;
action/observation interface; planner without delegation; bounded DAG delegation; verifier; then
novel retry/replan. Model version, task, environment, tool schema, route and total budget stay fixed
within each contrast and the matrix repeats across at least two model versions and task families.
Report deterministic hidden-test/state/effect outcomes, pass-at-one, pass-at-k and all-k reliability,
authority violations, intervention count, review minutes, retries, model calls, tokens, latency,
CPU/RSS/I/O and every failure. A Pareto frontier preserves trade-offs; it does not hide them in a
single score.

LLM judges are calibrated secondary evidence only. Deterministic state/effect checks come first,
followed by condition-blind human review for semantic residuals. Owner-review debt is its own
outcome: time to accept, reject or repair a correctly classified package, clarification/rework,
escaped defects and presentation burden. A contract can improve evidence quality while correctness
saturates and tokens, time or tool calls rise. Agentless is direct counterevidence to the claim that
more elaborate agent loops always improve results.

Fresh, rotating or sealed tasks, clean environments, frozen evaluator/source hashes and overlap
audits reduce contamination; none proves its absence. Results must use hierarchical task-family,
task and attempt uncertainty, a preregistered practical margin, and a hard rejection on any
unauthorized effect, stale commit, policy widening, private-data leak or ambiguous-effect success.

## Adversarial minimum and disabled-path contract

The smallest defensible privileged kernel performs strict schema/canonicalization, authenticated
command admission, pure reduction/event sequencing, authority/budget/privacy/fence checks,
deterministic WorkPacket derivation, effect admission/receipt classification, replay and publication
gating. Provider selection and sampling, context construction/compaction, plugin dependency
resolution, source retrieval, terminal rendering, telemetry and process implementation remain
typed proposals or adapters.

A disabled provider, plugin, cache, indexer, frontend or engine may expose bounded manifest
identity, digest and capability metadata and participate in static validation. It must not import or
initialize implementation code, read credentials, open a network connection, spawn a process,
thread, timer or watcher, reserve quota, register an executing background callback, subscribe to an
unbounded stream or change startup resources beyond a preregistered metadata budget. Import tracing,
handle/thread/network observation and cold/warm trials at 0, 10 and 100 disabled capabilities are the
decisive test.

OpenCode's 99 declared direct package dependencies demonstrate feature breadth and maintenance
surface, not measured runtime bloat. Gemini CLI's large UI hook and static-message segmentation
show a useful anti-flicker technique and the risk of UI-owned lifecycle logic. Codex's bounded
queues protect the coordinator but can disconnect a slow client, so canonical events must exist
before any lossy presentation queue. Pi's interrupted-stream recovery correctly preserves
`effect_pending` and reports an unknown result rather than inferring success.

## Plugins, capabilities and future frontends

Capability discovery is itself a resource and authority boundary. Codex's typed immutable
contributor registry and capability-scoped plugin loading, Gemini CLI's extension lifecycle and
most-restrictive MCP tool filters, OpenCode's server/client split, MCP capability negotiation and
MCP Apps' sandboxed view bridge supply complementary mechanisms. None supplies Recursion's
canonical GoalSpec, lease, effect or publication authority.

The proposed plugin path is: inspect a bounded manifest without importing code; validate exact
artifact/dependency digests, protocol version, supplied/required capabilities, isolation, resource
envelope, effect verbs, privacy/egress/credential/model/account bindings, lifecycle, license and
provenance; then intersect it with Owner policy, GoalSpec, route and budget. Unknown fields,
versions or digests fail closed. Trusted first-party contributors may use an immutable typed native
registry. Third-party or changeable plugins default to an isolated, bounded subprocess or remote
MCP-like adapter and receive only an immutable WorkPacket/capability token.

Plugin failure becomes typed unavailable/quarantined state and cannot disable unrelated work.
Reload is `discover -> verify -> stage -> drain/fence old version -> activate`: old packets, leases
and subscriptions become stale while prior evidence remains replayable. Discovery is lazy and
budgeted; manifest summaries do not imply loading complete tool schemas into model context.

CLI, web, desktop and MCP-App-style clients consume cursor/digest-bound redacted projections and
submit authenticated idempotent commands through one daemon gate. Sandboxed iframes, CSP and
postMessage capability negotiation are useful presentation isolation, but UI actions remain
proposals. OpenCode's broad mutating server API is therefore an integration reference, not an
authority model. Gemini's signed installation metadata does not hash extension payload bytes, and
a shortened source hash is display data rather than artifact identity.

## Systems performance and implementation candidates

The strongest static evidence favors one serialized admission/reducer path, bounded event-driven
queues with reserved control/recovery/verification capacity, versioned length-delimited local IPC,
content-addressed evidence and sampled traces joining command, event, lease, effect and receipt.
It does not select an implementation language, store or binary encoding.

Rust is the leading candidate for a privileged kernel because ownership and bounded async
primitives match the failure model; Go is a credible simpler alternative, and Python remains useful
for migration and low-rate adapters. This is an unverified comparison hypothesis. After M1A, the
same deterministic replay workload must compare CPython, Rust and Go under identical schema,
fault, platform and measurement profiles. Compiler memory rules, the GIL, goroutines or ecosystem
reputation are not end-to-end performance evidence.

SQLite WAL is an optional metadata/projection candidate, not canonical authority and not part of
M1A. Compare it with the existing JSONL approach plus content-addressed blobs using synthetic replay,
read contention, checkpoint pressure, restart, corruption and disk-full faults. JSON/JSONL is the
inspectable first IPC encoding; binary framing must earn its complexity with measured benefits while
preserving schema validation, fencing, portability and debuggability.

The repository should remain one small monorepo with dependency direction from protocol/schema and
kernel into adapters and surfaces, not premature microservices. Static v2 file sizes, repeated
durability helpers, Codex workspace breadth and OpenCode dependencies are coupling signals only.
No refactor may delete hardened behavior until replay and conformance establish semantic equivalence.

## Minimum defensible boundary after discovery

```text
Recursion Head + ARM semantic proposals
  -> small deterministic admission/event kernel
       identity | GoalSpec | authority | budgets | PAUSE | fences | effects | evidence
  -> versioned engine adapter
       model stream | native tools | provider retry/compaction | normalized observations
  -> managed process broker
       PTY/job/cgroup | attach/detach | bounded fanout | input/resize lease
  -> thin CLI/TUI, Telegram and future frontend views
```

`owner-direction`: Recursion's versioned release owns the Head, ARM, actor protocol and
canonical state. `adaptation`: Hermes becomes an optional migration/engine adapter rather than
a permanent authority dependency. The operative repository constitution remains unchanged
until Lucas separately reviews an amendment. External engines may optimize sampling, native
tool syntax, streaming, compaction and provider retries; they may not own GoalSpec acceptance,
Recursion actor identity, permission/grant widening, budgets, PAUSE/fence epochs, canonical
effect/evidence state or publication.

The competing full-native-loop architecture offers tighter control but initially duplicates
mature engine code and expands security/maintenance surface. A thin-wrapper architecture is
smaller but cannot guarantee canonical authority or recovery through opaque sessions. The
recommended boundary is falsified if thin typed adapters cannot preserve identity, effect and
evidence invariants across two materially different engines, or if a native spike wins a
preregistered quality/continuity/security/resource metric without a hard-floor regression.

## Open contradiction and gap ledger

| Gap or tempting claim | Disposition |
|---|---|
| “Use Hermes as Head forever because the current constitution names it.” | `rejected` as product destination by `OWN-FHAR-001`; still true for current operative authority until amendment. Migration compatibility is retained. |
| “Reimplement every inner loop to be a real harness.” | `rejected` as a prerequisite. Harness ownership is defined by Recursion's versioned authority/orchestration contract; native-loop scope must earn itself. |
| “A durable workflow product gives exactly-once effects.” | `rejected`; durable internal history does not eliminate external acceptance ambiguity. |
| “SQLite/WAL supplies single-writer authority.” | `rejected`; it supplies a database concurrency primitive. Recursion still defines writer identity, lease fence and effect protocol, and must pin build/VFS/filesystem/checkpoint settings. |
| “Provider cache state is a portable context layer.” | `rejected`; caching is endpoint/model/account/runtime specific and often opaque or non-controllable. |
| “Stable session ID is durable agent identity.” | `rejected`; session affinity is replaceable optimization metadata. |
| “More parallel agents means frontier performance.” | `rejected`; agent count without accepted-quality, quota, latency, resource and review-debt denominators is activity, not performance. |
| “More planning, delegation and retry always improve correctness.” | `rejected`; simple staged repair is competitive evidence, while contracts and hierarchy can add cost or only improve reviewability. Isolate every component. |
| “An LLM judge can be the authoritative verifier.” | `rejected`; documented position, verbosity and self-preference biases require deterministic oracles and calibrated independent review. |
| “Fresh public tasks prove there is no contamination.” | `rejected`; task rotation and overlap checks mitigate exposure but cannot prove training absence. |
| “A large dependency manifest proves runtime bloat.” | `rejected`; imports, startup, resident resources and disabled-path behavior require measurement. |
| “Rust is necessarily the fastest or safest end-to-end choice.” | `unverified`; language mechanisms are relevant, but only a matched implementation/fault comparison can select a default. |
| “SQLite WAL should replace JSONL because it is faster.” | `unverified`; one-writer, checkpoint, filesystem and recovery trade-offs require a complete-store comparison. |
| “MCP or a plugin signature grants Recursion authority.” | `rejected`; protocol negotiation and artifact/metadata integrity do not grant GoalSpec, budget, effect or publication rights. |
| “A future GUI needs direct access to canonical state.” | `rejected`; detachable clients can consume projections and send typed commands without becoming supervisors. |
| “Diff rendering eliminates flicker.” | `rejected`; resize, alternate-screen, Unicode width, terminal support, output races and backpressure remain. |
| “ConPTY or a PTY owns the process tree.” | `rejected`; transport and process containment are separate and platform-specific. |
| “A TUI session server is the canonical control plane.” | `rejected`; tmux/Zellij/OpenCode sessions do not carry Recursion owner authority or evidence. |
| “Static source inspection proves crash consistency or speed.” | `rejected`; fault injection and measurements are required. |
| Cross-provider owner-governed replay with exact effect/evidence continuity | No inspected harness closes it; this is Recursion's strongest plausible differentiator and highest-risk integration hypothesis. |

## Preregistered experiment queue

| ID | Frozen comparison | Measures and hard falsifier |
|---|---|---|
| `EXP-FHAR-01` | Minimal native loop vs typed adapters over two materially different engines on the same public tasks/source and policy | Accepted gate quality, escapes, continuity, owner review, tokens/quota, latency, CPU/RSS/I/O, code/dependency surface. Any authority/effect/evidence hard-floor failure rejects the candidate. |
| `EXP-FHAR-02` | Crash matrix at command append, stream frame, tool intent, external acceptance, receipt, approval and lease transfer | Exact logical operation/sequence, replay digest, duplicate/ambiguous effects, budget and approval continuity. Accepted stale epoch or blind ambiguous retry is a hard failure. |
| `EXP-FHAR-03` | Raw rescan vs deterministic capsule vs native compaction vs hybrid; cold/warm and same/fresh session | Gate quality, directive/evidence recall, rehydration misses, token/cache counters, latency and resources. Missing counters remain unavailable; any fidelity/privacy loss rejects the treatment. |
| `EXP-FHAR-04` | 0/1/5/10/20 terminal views under idle/high-output/slow-reader workloads | Model-call count, p50/p95/p99 input/frame/canonical-append latency, CPU/RSS/wakeups/IPC, queue high-water and gaps. Views may not multiply model work, corrupt input or grow memory without bound. |
| `EXP-FHAR-05` | Linux PTY/cgroup and Windows ConPTY/Job fixtures across child/grandchild, breakaway, resize, host death and restart | Process reconciliation, containment, cursor continuity and ambiguity. Any descendant/effect silently treated as stopped or successfully relaunched fails. |
| `EXP-FHAR-06` | TLA+/PlusCal model of duplicate command, lease takeover, cancel propagation, timer/retry and ambiguous effect | No stale commit, divergent replay, lost cancel or success from ambiguity. Counterexample blocks implementation until model/contract is repaired; passing TLC is not runtime proof. |
| `EXP-FHAR-07` | Fixed-model component ladder: minimal loop, ACI, planner, DAG delegation, verifier, then bounded novel retry/replan | Hidden state/effect correctness, reliability, authority violations, interventions, owner-review minutes, tokens/calls, latency/resources and all failures. A component claim fails if its paired interval crosses the preregistered practical margin or any hard floor regresses. |
| `EXP-FHAR-08` | Fresh/rotating held-out corpus with frozen environment/evaluator hashes, clean state, task-family/task/attempt hierarchy and overlap audits | Report practical effect and interval, not leaderboard rank. Leakage, residual state, incomplete oracle coverage or successful-only reporting invalidates the result. |
| `EXP-FHAR-09` | Zero-cost disabled path at 0/10/100 installed-but-disabled capabilities | Static import graph, startup, CPU/RSS, threads/handles/watchers, network, disk and quota receipts. Any implementation initialization, credential access, background work or undeclared resource growth is a hard failure. |
| `EXP-FHAR-10` | Same M1A-derived deterministic reducer/replay/fault workload in CPython, Rust and Go on frozen Windows/Linux hosts | Full optimization vector, build/install/dependency surface and review burden. A hard-floor regression rejects; non-dominated material choices return to Lucas. |
| `EXP-FHAR-11` | JSONL plus content-addressed blobs vs single-writer SQLite WAL metadata plus blobs under 1M synthetic events/four readers | Append/read/rebuild tails, CPU/RSS/I/O/wakeups, total bytes, checkpoint growth and recovery. Lost evidence, divergent authority or unbounded WAL rejects. |
| `EXP-FHAR-12` | Trusted built-in, isolated third-party plugin and sandboxed view across disable, crash, reload and protocol mismatch | Zero disabled work, bounded failure, exact stale fence, preserved replay and unchanged authority digest. Any plugin/UI plan mutation or payload-integrity overclaim rejects. |

All discovery recommendations remain provisional until Terra adjudication.
