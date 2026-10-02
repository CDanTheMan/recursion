# R-F — Harness-native headless delegation and high-volume fan-out

Research report · 2026-10-02 UTC · static source research only

Parent goal: `goal-recursion-v3-harness-orchestrator`  
Repository basis: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Disposition: decision-ready research and an **unexecuted** deterministic qualification handoff. No route is qualified.

## 0. Findings and decision boundary

The accepted caller-not-proxy model is technically expressible, but a headless process and a JSON stream are insufficient to establish complete authority enforcement, accurate fan-out totals, or settled effects. A bounded launch, native protocol completion, canonical acceptance and external settlement are different events.

The important findings are:

1. The nine named harnesses all have source-documented programmatic entry points. Their control semantics differ materially. A source-native fork is history duplication, not a new grant; native cancellation often leaves queues, child work or already-issued effects to reconcile. The map below explicitly preserves unknowns.
2. Claude invocation and accounting must be qualified together against the canonical facts in §§1.3–1.4 and 6. This is a qualification and counsel seam, not permission to change authentication.
3. Codex App Server remains the D-023 first-qualification direction. The [canonical technical facts](#codex-app-server-facts) establish neither production readiness, containment nor compatibility with an unpinned binary. Their version conflict remains a qualification blocker.
4. A native fan-out may conceal or aggregate child consumption. It is acceptable to report a known subtotal plus an unknown residual. It is unacceptable to turn missing fields into zero, sum overlapping cumulative totals, or claim subscription savings from token estimates.
5. A provider-free stub can falsify authority attenuation, lifecycle accounting and effect reconciliation. It cannot measure actual harness timing, credential isolation, account entitlement, quota, native cancellation, provider costs or model quality.

**Accepted premises, not reopened questions.** D-021/D-030 fix delegation through the user's own authenticated harness, with no credential custody or provider API proxy. D-022 fixes Aggressive / Full / Lazy plus `checkpoint`, `interrupt`, `drain`. D-023 fixes qualification order; D-024 fixes productive continuity as the measurable differentiator. D-029 requires a trusted launch boundary for a strong non-access claim. D-027/R-H/counsel retain route/legal clearance. D-028 supplies later platform floors. No language, store, framework, protocol, transport or vendor is selected here. No implementation, model/provider/harness invocation, login, credential read, install, spend, account action, live-host operation, counsel contact, repository edit was performed.

### Evidence convention and freshness

- **D — source-documented:** the cited public documentation or immutable source says this; not an observed runtime guarantee
- **O — locally observed:** confined here to retrieved document bytes, file hashes and static artifact checks; **zero harness behavior was observed by this research session**
- **I — inferred:** proposed contract/design implication, governed by the recommendation register in §12
- **U — unknown/unverified:** not established in the reviewed public material, or requiring installed-build/runtime/entitlement evidence

Every capability cell below uses D/I/U. Unknown means unknown, not unsupported, false, zero, or a negative runtime test. Public documents were re-retrieved on 2026-10-02; exact timestamps, redirects, content hashes and immutable revisions are in `source-register.md` and `sources.json`. Mutable documentation is pinned by retrieval and hash, not silently treated as a release. No named target binary was installed or inspected.

Historical observations are preserved rather than erased. The current repository's `ROUTE-CAPABILITIES.md` records 2026-09-07 provider-free installed fixtures: Codex 0.149.0 on Windows build 26200, release-tag source `758ef40f50c1a458425c7cfbf1eb12cbc07af0b0`; and Hermes 0.21.0/source `693641aa8b4359c602283bdbbc14041e03bc47bc` in isolated WSL2. They used scripted loopback responses, no real model/account billing and simulated counters. Hermes recovery was same-process close/resume; fresh-process recovery remained untested. The first synthetic-agent persistence oracle failed and was retained. Metadata/detection HTTP requests remained even with model-facing helpers disabled. These are **historical locally observed fixture claims recorded by the repository**, not rerun here, not evidence about current pinned upstream versions, and not authenticated route qualification. Their detailed raw evidence is a later review input, not silently inherited as a PASS.

The current-branch R-A–R-D reports and coverage/gap registers were read as prior analysis. Fresh primary sources below support the external facts. The old orientation prose that still mentions the retired Hermes constitution is subordinate to CONTROL_PLANE, ANCHOR and D-017/D-032 and supplies no current authority.

## 1. R-F.Q01 — Per-harness headless/exec capability map

Each six-cell list is a complete map for (a) submit, (b) steer/queue, (c) interrupt/cancel/stop, (d) resume/fork/rewind, (e) machine-readable output, (f) usage/accounting. Version and authentication are separately mapped in §§2–3. No cell claims external rollback, durable admission across a crash, or complete helper accounting unless explicitly established.

### 1.1 Codex exec

- **Submit — D:** `codex exec`, with prompt and optional piped context; noninteractive execution [RF-S47]
- **Steer/queue — U:** this one-shot reference does not document a bidirectional active-turn steering/queue API for exec. App Server's verbs must not be attributed to exec
- **Interrupt/cancel/stop — U:** no qualified signal-to-terminal/result or whole-owned-tree settlement contract in this reference
- **Resume/fork/rewind — D:** `codex exec resume` by session ID or latest session. **U:** exec-specific fork/rewind parity [RF-S47]
- **Output — D:** `--json` JSONL events, separate stderr progress; `--output-schema` constrains final output, not the event envelope [RF-S47]
- **Accounting — D:** `turn.completed.usage` token fields. **U:** complete subagent/helper coverage, interrupted-run totals and native allowance attribution [RF-S47]

### 1.2 Codex App Server

<a id="codex-app-server-facts"></a>
**D — canonical technical facts:** Initialize before `thread/start`/resume and `turn/start`. `turn/steer` uses `expectedTurnId`; `turn/interrupt` produces interrupted status; resume/fork exist. JSONL stdio carries correlated turn/item, approval/question and token-usage notifications, rate-limit windows and token-activity summaries. Initialization advertises capabilities; `experimentalApi` is opt-in; generated schemas follow the binary. TCP WebSocket is experimental/unsupported; a broader command warning has ambiguous remote Code Mode scope. `thread/shellCommand` and experimental `process/*` bypass the thread sandbox; `command/exec` differs. Losing the last subscriber can unload a thread after grace. Experimental background-terminal controls and session-compaction notifications exist. Web `thread/rollback` is deprecated; pinned README replaces it with `thread/revert`. Fork attachments copy best-effort; shared references do not duplicate resource ownership. Authentication distinguishes Codex-managed saved-account, supplied-key and experimental external-token profiles. [RF-S01, RF-S02]

**U — six-cell map limits:** submit/steer/interrupt/resume-fork/output/accounting are documented above, but crash-durable delivery, descendant/effect settlement, installed rewind availability, complete replay, child quota attribution and general deprecation guarantees remain unqualified. **I:** qualify lifetime/recovery and method-specific containment; transport structure alone is no boundary. Legal scope and the sole S08 quotation are in [R-H §3.2 and Appendix B](../rh/report.md#32-codex-and-chatgpt).

### 1.3 Claude Code print mode

<a id="claude-headless-facts"></a>

- **Submit — D:** `claude -p`; `--input-format stream-json` is listed in the CLI reference [RF-S03, RF-S05]
- **Steer/queue — D:** streaming-input mode supports sequential queued messages through the SDK/control surface; **U:** treating arbitrary one-shot stdin as active steering or assuming crash-durable queues [RF-S04]
- **Interrupt/cancel/stop — D:** current docs distinguish SIGTERM's unfinished turn/no result from SIGINT/SDK interruption. **U:** external rollback or a verified cross-platform whole-tree contract [RF-S03]
- **Resume/fork/rewind — D:** continue/resume/fork-session; checkpoint rewind has file/tool limitations. Bash and outside edits are not universally undone [RF-S05, RF-S07]
- **Output — D:** JSON/stream-json, result and init/capability events; subagent event coverage is version-dependent [RF-S03, RF-S05]
- **Accounting — D:** see the [canonical cost note](#claude-accounting-facts). **U:** subscription allowance conversion or absent-result totals

**D — invocation/authentication supplement:** `--bare` changes discovery and excludes subscription login; the page describes a future default change. Non-bare operation can use the CLI’s existing account authentication. Init/capability and subagent events have version constraints. Client cost estimates are not invoice evidence; continued sessions include earlier spend. [RF-S03] **I:** default changes invalidate the reviewed profile; detailed accounting rules are centralized below.

### 1.4 Claude Agent SDK, separately scoped

<a id="claude-sdk-facts"></a>

- **Submit — D:** `query()` launches a bundled or explicitly selected native Claude Code executable; streaming input accepts a sequence of user messages [RF-S48, RF-S04]
- **Steer/queue — D:** streaming input; interrupt receipts identify pending messages. A receipt is a snapshot, not a durable delivery guarantee [RF-S48]
- **Interrupt/cancel/stop — D:** streaming `interrupt()`; current direct control protocol can advertise `interrupt_cancel_queued_v1`. The SDK method does **not** itself send `cancel_queued` [RF-S48]
- **Resume/fork/rewind — D:** resume/fork options; file checkpoint rewind is narrower than general effect rollback [RF-S48, RF-S07]
- **Output — D:** typed SDK messages correspond to the native subprocess/control stream; nesting correlations exist [RF-S48, RF-S49]
- **Accounting — D:** see the [canonical cost note](#claude-accounting-facts); native subagent depth/concurrency/spend options are version-dependent [RF-S49]

**D — SDK profile supplement:** bundled CLI correspondence tracks the SDK patch line; feature minima and init capabilities are documented. Full `getContextUsage` issues token-count requests outside the message stream; summary mode estimates locally [RF-S48]. **I:** qualify the environment, binary and helper envelope; an interface alone proves neither subscription entitlement nor permission for embedding.

### 1.5 Cursor (`cursor-agent` brief name; current docs use `agent`)

<a id="cursor-headless-facts"></a>

- **Submit — D:** print/headless `agent -p`; `agent acp` offers session/new and session/prompt [RF-S09, RF-S38]. **U:** binary alias equivalence on an uninspected installation
- **Steer/queue — U:** active headless/ACP steering and crash-durable queuing are not established by the reviewed print/ACP pages; do not copy interactive editor behavior into this cell
- **Interrupt/cancel/stop — D:** ACP `session/cancel`. **U:** print-mode signal contract and independent effect settlement [RF-S38]
- **Resume/fork/rewind — D:** CLI resume/continue and ACP session/load. **U:** print/ACP generic fork/rewind parity [RF-S11, RF-S38]
- **Output — D:** JSON/NDJSON and ACP JSON-RPC; failure may end without a terminal JSON result [RF-S10, RF-S38]
- **Accounting — D:** printed duration fields. **U:** token/cost counters in the reviewed print schema, helper totals and per-child billed allowance [RF-S10]

The ACP page describes `cursor/task` as a fire-and-forget notification while also presenting response types. **U:** that mixed documentation is not a reliable host-executed spawn contract. Treat it as observed native-task metadata until a version-specific contract is qualified [RF-S38].

### 1.6 Gemini CLI

<a id="gemini-headless-facts"></a>

- **Submit — D:** non-TTY/headless or `-p`; ACP stdio request/session methods [RF-S14, RF-S15]
- **Steer/queue — D:** experimental interactive model-steering hints; **U:** headless/ACP same-turn parity and durable queue. The hint acknowledgement uses a small model, so helper accounting cannot be assumed absent [RF-S43]
- **Interrupt/cancel/stop — D:** ACP cancel. **U:** external settlement [RF-S15]
- **Resume/fork/rewind — D:** CLI resume/session management and file checkpoints; ACP loadSession. **U:** a universally equivalent cross-interface fork/rewind contract [RF-S15, RF-S16, RF-S18]
- **Output — D:** JSON or JSONL init/message/tool_use/tool_result/error/result events [RF-S14]
- **Accounting — D:** result aggregate and per-model token statistics. **U:** complete helper inclusion and subscription attribution [RF-S14]

The ACP guide and CLI reference show different flag spellings (`--acp` versus `--experimental-acp`). Record the exact installed profile; neither spelling is silently assumed to work on every release [RF-S15, RF-S39].

### 1.7 Grok Build

<a id="grok-headless-facts"></a>

- **Submit — D:** `grok -p`; `grok agent … stdio`; ACP prompts [RF-S19, RF-S55]
- **Steer/queue — D/source:** pinned `x.ai/interject` handler queues a command and returns `queued`; **U:** actual consumption, release exposure and durable delivery without a qualified trace [RF-S56]
- **Interrupt/cancel/stop — D/source:** pinned session actor has cancel/shutdown command paths; interactive cancel controls are documented. **U:** exact public cancel-to-settlement contract on the installed release [RF-S58, RF-S21]
- **Resume/fork/rewind — D:** continue/resume/session-id/fork-session; rewind and source-specific session extensions. Rewind is not general filesystem rollback [RF-S20, RF-S57]
- **Output — D:** `json` and `streaming-json`; ACP updates plus x.ai extension notifications [RF-S19, RF-S55]
- **Accounting — D:** process-scoped status-line cost restarts on resume; source contains subagent/background accounting machinery. **U:** full machine-output accounting coverage from the reviewed external schema [RF-S23, RF-S58]

**D — headless auth premise:** the headless guide permits an existing local authentication context or `XAI_API_KEY` [RF-S19]. Detailed enterprise modes are centralized in [R-H §3.5](../rh/report.md#grok-enterprise-facts).

A handler's successful queue response does not prove its receiver consumed the command. The public extension guide calls its list non-exhaustive and requires availability discovery; source presence is not a release/entitlement claim [RF-S55, RF-S56].

### 1.8 Hermes

<a id="hermes-integration-facts"></a>

- **Submit — D:** `hermes acp`; gateway `prompt.submit`; separately documented HTTP run interfaces [RF-S34, RF-S35]
- **Steer/queue — D:** `session.steer` and busy-input handling; HTTP steer acknowledgement means queued and can return undelivered `pending_steer`. **U:** durable prompt admission across owner restart [RF-S34]
- **Interrupt/cancel/stop — D:** ACP cancel/agent interrupt, gateway session.interrupt, HTTP run stop. **U:** external settlement [RF-S34, RF-S35]
- **Resume/fork/rewind — D:** persisted ACP sessions, resume/load/fork; gateway branch and explicitly confirmed truncating rewind [RF-S34, RF-S35]
- **Output — D:** ACP/gateway JSON-RPC, lifecycle/tool events, replay of still-open correlated questions. **U:** a globally versioned durable event log [RF-S34, RF-S35]
- **Accounting — D:** gateway session.usage and run status/events. **U:** complete child/helper inclusion and per-subscription debit [RF-S34]

**D — compatibility/auth facts:** `gateway.capabilities`/`client.capabilities` include a breaking server-request change; ACP has unstable protocol support. Provider resolution stays with Hermes; ACP adds no credential store. Active attachment is process-local despite persisted transcripts; durable restart admission is not promised. Secret/sudo/vault gateway requests exist [RF-S34, RF-S35]. **I:** exclude those callbacks, qualify restart admission separately, and do not infer global semver guarantees.

### 1.9 OpenCode

<a id="opencode-server-facts"></a>

- **Submit — D:** `opencode run`; local server session/message and prompt_async; separate ACP mode [RF-S27, RF-S28]
- **Steer/queue — D:** prompt_async returns HTTP 204 without waiting. **U:** that proves neither active steering nor durable admission/queue [RF-S27]
- **Interrupt/cancel/stop — D:** session abort endpoint. **U:** descendant/effect settlement [RF-S27]
- **Resume/fork/rewind — D:** CLI continuation/fork, server fork/revert/unrevert [RF-S27, RF-S28]
- **Output — D:** run `--format json`, server SSE, ACP nd-JSON [RF-S27, RF-S28]
- **Accounting — D:** statistics command and pinned assistant-message token/cost types. **U:** exhaustive helper coverage or quota conversion [RF-S28, RF-S37]

**D — server profile supplement:** the server exposes OpenAPI/version identity, session listing, multiple clients and optional basic authentication; provider-auth mutation is a separate surface [RF-S27]. CLI startup/auth-store facts remain [RF-S28]. **I:** this is a legacy profile, not v2 qualification; abort/revert cannot establish external rollback.

<a id="opencode-v2-facts"></a>

**Current v2 delta — D:** global client subscriptions share a connection, await subscriber consumption, provide live updates only, and neither reconnect automatically nor replay history. Separately, experimental `session.log` is durable: `after` is an exclusive aggregate-sequence cursor; `follow=true` continues live. The API durably admits prompts to an ordered inbox. Cancel affects undelivered items; unavailable items are no-ops. Update changes delivery mode, not documented text editing. Interrupt affects process-owned execution; optional resume restarts steering/control items while queued prompts stay parked. Fork copies projected history before a selected message, or all history if omitted. Worktree operations and session-directory concepts are exposed. [RF-S62, RF-S63]

**U/I:** exact installed v2 conformance, retention, privacy/gap signaling, effect settlement and Grok-style dispatch parity remain unqualified. A live-stream gap cannot establish absence of durable replay; a log cannot establish execution or rollback.

### 1.10 Antigravity local CLI

<a id="antigravity-headless-facts"></a>

- **Submit — D:** `agy -p`, or persistent stream-json stdin user messages [RF-S29]
- **Steer/queue — D:** successive turns, one result each. **U:** active-turn steering or crash-durable queue [RF-S29]
- **Interrupt/cancel/stop — D:** stdin close waits for current turn; INTERRUPTED status includes SIGINT as an example. **U:** a bidirectional control cancellation or all-effect settlement guarantee [RF-S29]
- **Resume/fork/rewind — D:** continue/conversation ID. **U:** programmatic fork/rewind in this profile [RF-S29]
- **Output — D:** JSON and stream-json step_update/result [RF-S29]
- **Accounting — D:** session-cumulative usage/duration/turn counters. **U:** exhaustive helper cost/allowance attribution [RF-S29]

**D — framing limit:** unknown input events may be skipped; `control_request`/`control_response` are rejected [RF-S29]. **I:** managed API/credential-bearing SDK routes are separate profiles, never implicitly authorized fallbacks. Auth-mode facts are centralized in [R-H §3.8](../rh/report.md#antigravity-auth-facts).

### 1.11 Pi

- **Submit — D:** `pi --mode rpc` long-lived subprocess, JSONL `prompt` [RF-S31]
- **Steer/queue — D:** `steer` versus `follow_up`, explicit disposition and delivery boundaries [RF-S32]
- **Interrupt/cancel/stop — D:** `abort` waits for idle but queued messages continue unless cleared; `abort_bash` and `abort_retry` are distinct [RF-S32]
- **Resume/fork/rewind — D:** switch_session, fork/clone and append-only entry history. **U:** filesystem/external rollback [RF-S32]
- **Output — D:** strict LF-framed JSONL; command response is not completion; `agent_settled`, rather than `agent_end`, signals no automatic continuation [RF-S31, RF-S60]
- **Accounting — D:** session stats include assistant, tool-reported, compaction and branch-summary usage; custom compaction can omit usage. **U:** complete hidden/provider usage [RF-S32]

The inspected Pi source pin labels its package 1.0.0, but this is not an installed-binary observation [RF-S61]. Queue clearing plus abort is a distinct control sequence, not interchangeable with a generic signal.

## 2. R-F.Q02 — Streams, stability, negotiation and deprecation

All entries are **D** unless marked **U**. “JSON” is syntax, not a common lifecycle schema. A final-output schema does not negotiate event semantics. **I / RF-R1:** retain raw bounded protocol evidence, parse into a versioned adapter profile, preserve unknown event kinds as non-authorizing evidence, and fail closed when a missing/changed field affects authority, completion or accounting.

| Profile | Parseable surface | Version/negotiation evidence | Deprecation/stability limit |
|---|---|---|---|
| Codex exec | JSONL event envelope | Binary-specific schema/profile; final output-schema is separate | **U:** universal exec event compatibility SLA [RF-S47] |
| Codex App Server | [Canonical surface/profile facts](#codex-app-server-facts) | Use the exact reviewed binary/schema/capability tuple | **U:** removal notice, installed correspondence and transport qualification |
| Claude print / SDK | [Print](#claude-headless-facts) and [SDK facts](#claude-sdk-facts) | **I:** capability evidence outranks guessed version comparison | **U:** blanket raw-wire deprecation SLA |
| Cursor print / ACP | NDJSON / JSON-RPC stdio | ACP initialization and implementation identity | **U:** print-schema version handshake or fixed deprecation window; vendor extensions need separate evidence [RF-S10, RF-S38] |
| Gemini headless / ACP | [Canonical headless facts](#gemini-headless-facts) | ACP identity and flag discrepancy: §1.6 | **U:** headless compatibility SLA, extension lifecycle and binary correspondence |
| Grok headless / ACP | [Canonical route facts](#grok-headless-facts) | Discover source-specific extensions as described in §1.7 | **U:** removal window and uniform schema version |
| Hermes ACP / gateway | [Canonical route/profile facts](#hermes-integration-facts) | Qualify the named capability transition and ACP profile | **U:** general semver/deprecation promise |
| OpenCode legacy run / server / ACP; separate v2 | [Legacy facts](#opencode-server-facts); [v2 facts](#opencode-v2-facts) | Pin generation, API and exact types separately | **U:** cross-generation compatibility/removal timetable |
| Antigravity | [Canonical framing/control facts](#antigravity-headless-facts) | Qualify the exact event/profile interpretation | **U:** negotiation, semantic-version guarantee and removal period |
| Pi RPC | Strict LF JSONL | Exact source/package pin; installed help authoritative | **U:** protocol-major handshake or guaranteed deprecation period [RF-S31, RF-S61] |

**ACP is not a capability guarantee.** ACP v1 initialization negotiates a major integer, capability sets and implementation identity. A client that cannot support the returned major should disconnect. `usage_update` is optional; its context-window used/size is not lifetime provider consumption, and optional cumulative cost is not necessarily billing. Cancelled prompt completion is prescribed only after ongoing operations abort and pending updates are sent; late updates before completion remain valid. None proves irreversible remote effects were undone [RF-S51, RF-S52]. The nonexistent `protocol/session-resume` URL returned 404; no claim relies on that guessed page (RF-S53).

**Codex maturity caveat.** Resolve the [canonical source ambiguity](#codex-app-server-facts) against the exact intended transport. Neither method classification nor documentation establishes an accepted production profile.

## 3. R-F.Q03 — Credential and outbound-connection ownership per profile

The **D** facts below identify documented auth paths. Connection-owner columns are **I** architectural attribution based on those process interfaces; the actual executable/process and network peer set remain **U** until authorized measurement. None proves the same-user caller cannot read credentials. No source's token-injection example is adopted.

| Harness/profile | Candidate delegated credential owner | Outbound model connection owner in this lane | Excluded caller-supplied/custody path |
|---|---|---|---|
| Codex exec/App Server | **D:** [App Server modes](#codex-app-server-facts); exec saved-auth behavior [RF-S47] | **I:** Codex runtime and declared helpers | **I:** exclude caller-owned credentials and auth mutation |
| Claude non-bare print | **D:** [Canonical invocation/auth facts](#claude-headless-facts) | **I:** native subprocess and declared helpers | **D:** key/helper/cloud-provider alternatives [RF-S06]. **U:** SDK invocation entitlement |
| Cursor CLI/ACP | <a id="cursor-auth-facts"></a>**D:** browser login stores credentials locally; API-key environment/flags are documented for automation [RF-S08] | **I:** local Cursor runtime | **I:** exclude caller-supplied keys; qualify remote/SDK and ACP separately [RF-S38] |
| Gemini CLI | **D:** cached existing CLI authentication | **I:** Gemini CLI runtime | **D:** caller key/Vertex/ADC injection or copying outside the tool owner [RF-S17] |
| Grok Build | **D:** [Headless premise](#grok-headless-facts); [enterprise modes](../rh/report.md#grok-enterprise-facts); pinned resolver details [RF-S59] | **I:** Grok agent and declared native helpers | **I:** exclude caller-managed credentials and secret relay; profile native topology [RF-S55] |
| Hermes ACP/gateway | **D:** [Canonical auth/profile facts](#hermes-integration-facts) | **I:** Hermes runtime | **D:** external API-server bearer authenticates control [RF-S26]. **I:** that does not exempt provider authentication |
| OpenCode | **D:** auth store and startup environment/project `.env` sources [RF-S28] | **I:** OpenCode runtime/server | **D:** [Canonical server-auth surface](#opencode-server-facts). **I:** exclude credential writes/injection |
| Antigravity local CLI | **D:** [Canonical auth-mode note](../rh/report.md#antigravity-auth-facts) | **I:** Antigravity runtime/shared harness chain | **I:** exclude alternate credential-bearing profiles |
| Pi RPC | **D:** Pi auth store/login/resolver | **I:** Pi subprocess and configured provider module | **D:** caller raw-key env, resolver output interception, or in-process secret-bearing SDK embedding [RF-S33] |

No fallback reads home auth files, exports a token, invokes login, mounts a secret store into Recursion, adds a provider base-URL proxy, or changes an auth mode. A missing native login becomes `authentication_required`; preserved task state can wait. Whether the user's provider permits a particular subscription-backed automation or volume remains **U/counsel-gated**, even when technical delegation is possible.

## 4. R-F.Q04 — Precise caller-not-proxy test

**I / RF-R2**, applying accepted D-021/D-029/D-030 rather than re-deciding them:

A candidate profile passes the technical delegation test only when all of the following are established for its **exact binary, auth mode, helper topology, configuration, transport and platform**:

1. Recursion sends bounded task/control messages to an operator-provisioned harness endpoint. It does not construct or forward provider HTTP requests on the user's account.
2. Provider sockets and authenticated provider requests originate in the harness's declared trusted execution domain, including its declared native helpers. Recursion's domain has no route that can silently become the provider client. A harness-internal gateway is disclosed; it does not make Recursion a proxy by itself.
3. Authentication storage, refresh, account selection and all credential-bearing requests remain with the harness/operator boundary. Recursion receives only non-secret identity/status references, never token material or a credential-bearing environment value.
4. No credential appears in argv, inherited caller environment, IPC, stdio, errors, telemetry, artifacts or restored sessions. Record environment **names/policy**, not values. Token hashes are not a safe substitute for never receiving the token.
5. The enforcement boundary must prevent both **direct access** and **induced disclosure**: Recursion/plugins/untrusted tasks cannot read or regain access to secret files, keyring, memory, handles or environment, and cannot cause the credential-bearing harness or its tools to export secrets through permitted prompts, configuration, helpers, logs or artifacts. OS read denial plus output masking is insufficient when an allowed tool or configuration can induce export. Same-user process separation does not establish either obligation.
6. Secret/account/login/configuration mutation methods and endpoint/auth overrides are outside the admitted adapter control set. Correlated approvals convey permission for a named action; they are not authority to acquire or relay credentials.
7. Local read/control channel authentication is separately authorized and isolated. Calling a bearer “only a server token” does not remove its sensitivity or machine-control consequences.
8. Before a strong profile is eligible, establish that the **exact unmodified upstream binary and supported invocation/configuration** expose credential-bearing runtime C versus tool-execution T separation, or an equivalently enforced protection against direct and induced flows. The launch boundary cannot manufacture this support around a CLI whose credential-capable identity also executes unrestricted tools. No binary patch, authentication shim, token relay or provider proxy is proposed to create it. Unknown/unsupported compatibility leaves the upstream route unqualified even if a synthetic boundary fixture passes.
9. Failure of a required strong preflight refuses admission as `boundary_unqualified`. A policy-only description is an evidence **claim ceiling**, not proof that a weaker deployment is installed or authorization to continue in it. Policy-only execution requires separate operator admission; there is no silent downgrade for strong-required work.

**Crossing the line:** Recursion reading/exporting a refresh token, accepting an OAuth callback for the provider, forwarding a provider Authorization header, receiving a raw key in an SDK option, hosting a provider-compatible proxy for the user's credential, or copying auth storage to a new node fails this lane's no-custody model. A third-party tool's documented support for these paths does not authorize them. This is an architectural boundary test, not a legal conclusion.

**Necessary evidence, not collected:** process identities and loaded helper topology; externally observed network ownership without payload capture; direct-access and induced-export canary tests; exact unmodified-binary C/T support evidence; sanitized launch receipts; protocol-message allowlist; output-redaction coverage; adversarial file/env/memory/handle reads; approved platform qualification. Public documentation alone cannot prove these conditions.

## 5. R-F.Q05 — Minimal DelegationRecord

**I / RF-R3.** One durable record precedes a spawn/submit; later facts append receipts. The record references secrets by an operator-owned boundary identifier and never stores a secret or secret-derived value. Each factual field is `{value, evidence_class, evidence_ref, observed_at, validity}`; `value:null` requires an unknown reason. Proposed fields are schema design, not observations.

| Required group | Minimal fields and meaning |
|---|---|
| Identity | schema revision; delegation_id; goal_id; work_unit_id; attempt_id; parent_attempt_id; spawn_intent_id; fanout_group_id; role; retry_of; branch lineage |
| Authority | issuer/principal reference; grant_id/digest; parent grant; epoch/fence; expiry; action/resource allowlist; denied capabilities; onward-delegation depth; approval bindings; acceptance gate |
| Binary/profile | resolved executable identity, digest, version source, adapter version, native protocol/schema pin, auth-mode class, enabled extensions, transport, platform profile; unknown installed values remain null |
| Invocation | argv **class** and nonsecret argument manifest; prompt/artifact manifest hashes; no shell interpolation; stdin shape; flags affecting discovery, sandbox, tools, resume, permissions, auth or endpoints |
| Environment | explicit permitted-name policy; whether SDK replaces/merges/inherits; forbidden secret-bearing names; trusted harness-only injection policy reference; locale/framing/working-directory policy; no values |
| Scope | canonical working-directory identity; input snapshots; writable artifact scope; output bounds; tool/egress allowlists; privacy classifications/destinations; process ownership root; remote node only if separately admitted |
| Credential/connection ownership | harness-owned credential boundary reference; expected process/helper owners; no-custody test status; policy-only vs enforced; source/observed/unknown evidence per assertion |
| Limits | parent reservation and child allocation by meter; concurrency permit; deadline; maximum spawn count/depth/retries; unknown-meter policy; graceful-boundary and escalation policy |
| Correlation/lifecycle | native session/turn/task IDs when known; submit correlation; event cursor/digest; phase; queue disposition; cancel receipt; terminal result; process-tree observation; unresolved children/effects |
| Result/settlement | artifact manifest; independent verifier result; effect intents/receipts; accounting record; durable checkpoint; late-output disposition; exact source/observed limitations |

Do not record a human-readable binary version as locally observed merely because its documentation says so. Binding the actual executable digest and effective launch policy is a later qualification operation. An argv class such as `preauthenticated-local-print/read-only/new-session` is insufficient unless its exact expansion is frozen and verified; it is a useful review summary, not a hidden free-form command.

## 6. R-F.Q06 and R-F.Q08 — Honest Accounting and ownership

**I / RF-R4.** Three owners have different responsibilities:

- **Canonical parent/goal ledger:** owns the conserved reservation and all-attempt attribution, including native children, retries, verification and recovery
- **Child harness invocation:** produces native counters and lifecycle evidence for its declared scope; cannot establish billing truth merely by returning a cost field
- **User's provider account/subscription:** is the commercial resource pool; its account-window counters can cover other concurrent work and cannot automatically be allocated to one child

A native parent total and its child totals can describe overlapping work. Use a coverage graph/set of attempt IDs and meter epochs; aggregate a disjoint cover once. Keep a parent-inclusive aggregate as the authoritative observation for that covered set when per-child detail is absent; per-child values then remain unknown. Never distribute an aggregate proportionally by tokens or elapsed time unless explicitly reporting a separate, named modelled estimate.

### Minimal HonestAccountingRecord

- Identity: goal/work/attempt/parent/fanout/spawn IDs, route profile, binary/schema, role and native IDs
- Lifecycle: intent, launch, admission-known/unknown, running, upstream-completed, interrupted/cancelled/failed/unknown, independently accepted, settlement state; timestamps plus causal ordering basis
- Meter list: meter name; numeric value or null; unit; epistemic state `measured | modelled | unknown`; evidence class; source; lower bound and unknown residual; scope `request | turn | invocation | session | process | account_window`; cumulative/delta; reset epoch; included attempt set
- Coverage: discovered children; discovery complete/partial/unknown; included/excluded helpers; exact counter exclusions; invisible helper possibility; retries/background work; missing-report reason
- Reconciliation: event/request deduplication keys; overlapping aggregates; corrected/reset counters; late receipts; billing/allowance reconciliation status; accounting completeness separate from honesty

A missing value is `{"value":null,"epistemic":"unknown","reason":"stream_ended_without_result"}`. A zero counts as valid consumption evidence only when the field's scope, coverage and lifecycle validity establish a real measured zero, or a complete pre-dispatch trace proves no relevant request escaped. Presence of a numeric zero alone is insufficient; neither absent text nor process failure establishes it. Known placeholder or crash-zeroed fields retain their raw reported 0 and provenance but normalize actual consumption as unknown, preserving earlier valid observations and any defensible lower bound. Synthetic fixture ticks are labelled synthetic measured units, not provider tokens or currency.

### Concrete source-specific hazards

<a id="claude-accounting-facts"></a>
**D — Claude accounting:** result `usage` covers the main loop; `modelUsage` and estimated cost include subagents. Resume totals became cumulative in v2.1.277; earlier versions reset. `/clear` resets counters/budget. Per-step output may be placeholder data; repeated message IDs require deduplication. At `error_max_budget_usd`, `usage` may exclude the threshold-crossing response although model/cost totals include it. Final crash results may zero usage/cost; recovered main-loop input/cache counters do not establish missing output, helper or whole-tree totals. [RF-S50]

**I:** retain raw invalid zeros without overwriting prior valid totals; preserve defensible subtotals and unknown residuals. Positivity alone does not establish completeness. Helper visibility is in the [SDK facts](#claude-sdk-facts); these documented requests do not themselves establish paid consumption.

- **Grok:** status-line cost covers the process and starts anew on resume. A hidden/small/omitted field is not zero lifetime consumption [RF-S23].
- **Pi:** current pinned session statistics include reported compaction/branch-summary usage. Custom handlers may omit it. The obsolete blanket assumption “Pi excludes all helpers” is rejected [RF-S32].
- **Antigravity — I:** apply the [canonical counter scope](#antigravity-headless-facts) using compatible snapshots, never an overlapping sum.
- **Cursor:** an error can end without terminal JSON; register the attempt before launch and retain an unknown residual [RF-S10].
- **ACP:** optional usage updates concern current context and cumulative cost; absence is unknown, and context size is not billable token total [RF-S52].

The ledger can pass honesty while failing completeness. An unbounded unknown residual prevents a total-cost/savings claim. No token-to-subscription conversion or universal fan-out efficiency follows from these fields.

## 7. R-F.Q07 — External-session authority and attenuation

**I / RF-R3/RF-R5.** A `/goal`, transcript or parent model's instruction is an input request, not self-authenticating authority. A currently authorized principal must have granted this goal the right to create the named kind of child, within finite resources and data boundaries. The canonical kernel verifies that grant and creates each child permit. The external session remains a controller/client; it does not become a second canonical writer.

For every child c, derive:

- capabilities/resources/destinations(c) = parent allowance ∩ goal scope ∩ explicit child scope ∩ route capability ∩ current policy
- expiry(c) ≤ parent expiry; authority epoch(c) bound to current canonical epoch; delegated depth decreases; no grant-administration or scope-widening authority inherited implicitly
- privacy classification and recipient rules retain the most restrictive applicable requirement; a new harness/provider destination requires authorization already present or a new human decision
- unspent child reservations + consumed/settlement-uncertain reservations + retained parent capacity never exceed the parent's authorized vector. Conserved units remain distinct: token estimate, spend, native allowance, wall time, process slots and review debt are not interchangeable

The protected launch/effect boundary enforces these values. Prompt text, environment variables, native tool lists and model obedience are not sufficient enforcement. A child discovering “more work needed” emits an amendment proposal; it cannot grant itself another path, provider, model, tool, sibling scope or budget.

A native subagent whose spawn cannot be intercepted or bounded belongs inside one already-reserved native subtree. If that subtree cannot expose/enforce the required scope, isolation and quota bounds, it is **unqualified for effectful fan-out**. An isolated proposal-only workspace can be an admissible narrower profile after its own qualification. No arbitrary shell-created child is silently reclassified as authorized harness-native delegation.

Each child receives goal/grant reference, explicit task, allowed artifacts, evidence requirements, acceptance gate, current epoch, budget allocation and stop policy. It receives neither parent secrets nor unrestricted transcript history. Resume, fork, compaction and machine change must revalidate the current grant; preserved history is evidence only. A fork may copy context but cannot copy an exclusive write permit or full remaining budget.

Native cap caveat: Claude's documented subagent limits include an ultracode exception to concurrency refusal; SDK environment inheritance also differs by implementation. Recursion's envelope therefore cannot rely solely on an upstream default or a prompt telling the model to spawn fewer children [RF-S49].

## 8. R-F.Q09 — Spawn and effect settlement

**I / RF-R5.** Settlement answers what happened to every admitted effect and child, not whether a process printed “done.” Proposed state names below are contract vocabulary, not selected storage technology.

### Spawn lifecycle

1. **Intent/reservation:** canonical writer commits spawn_intent_id, attempt_id, parent grant/epoch, profile, budget reservation and ownership root before dispatch
2. **Dispatch:** launch boundary atomically claims the intent or returns its existing receipt. Persist `dispatch_started`; bind an opaque launch-incarnation token to a process identity, not PID alone
3. **Admission:** record native correlation/receipt separately from started/running. A broken connection between dispatch and native acknowledgement yields `admission_unknown`
4. **Run:** record streamed evidence and children; each native child is linked if discoverable, otherwise mark subtree discovery partial/unknown
5. **Terminal:** native completion/failure/interrupt and process exit are separate receipts
6. **Settle:** reconcile descendant ownership, external-effect receipts, artifacts, queues and resource reservations; independent acceptance is a separate final gate

Exactly-once native spawn is **not promised**. If the harness lacks idempotent admission/queryable identity, a lost acknowledgement cannot be solved by resubmitting. Freeze the reservation, reconcile against durable launch/native evidence, or mark an unresolved attempt. Duplicate intent delivery deduplicates at the canonical/launch boundary; duplicate upstream work remains detectable through incarnation/native IDs or explicitly unknown if the route hides them.

### Effect lifecycle and commit points

- An effect intent records stable effect_id, payload digest, target/version precondition, grant/epoch, approval and idempotency key **before** dispatch
- Local isolated artifacts commit as immutable candidate manifests; promotion into accepted shared state is a separate authorized compare-and-apply step
- An external operation commits when its actual receiver commits it. A local intention, transport ACK, native tool result or child death does not redefine that boundary
- Receiver receipt, observed target version or independently verified side effect establishes `committed`, `not_committed`, `compensated`, or `outcome_unknown`
- Retry only when idempotency or reconciliation establishes safety. Unknown non-idempotent effects block overlapping replay; compensation is a new authorized effect, never fictional rollback

Parallel children use disjoint artifact scopes or explicit conflict/version predicates. Same-target conflicting writes are serialized at the canonical promotion/effect boundary. Losing proposals remain evidence and charged work. Source-native rewind changes history or selected files only to its documented extent; it never erases an external receipt.

A child with unmediated tools cannot promise per-effect fencing. Either qualify complete mediation or confine it to bounded proposal generation and apply effects through an independently checked boundary. A Full Stop can settle local ownership while remote effects remain unresolved; both states must be reported.

## 9. R-F.Q10 — D-022 Stop and pause vocabulary

**I / RF-R6**, preserving the definitions in D-022 and TERMINAL-RUNTIME. Stop mode, scope and execution policy are separate fields; do not invent a total ordering between Aggressive and Full.

| Term | Fan-out behavior | Required observable receipt |
|---|---|---|
| **Aggressive** | Fence further selected-agent dispatch and interrupt it without waiting for the current operation. Descendants are identified separately; they are not silently assumed in scope | Selected incarnation control/exit evidence; unresolved operations and descendant list |
| **Full** | Fence the rooted owned set, including children, shells, monitors, relaunchers and return paths; stop/reconcile all of it | Every owned local member settled or unresolved; separate remote receipts; no automatic relaunch |
| **Lazy** | Close new admission and stop at the next observable allowed current-operation boundary | Boundary ID, deadline, pending queue disposition and explicit escalation policy; no claim about hidden reasoning |
| `checkpoint` | Request a validated durable capture of goal/grant/epoch, attempts, pending waiters, queues, evidence, accounting, artifacts and unsettled effects | Checkpoint manifest plus replay reference; partial/unknown effects remain visible |
| `interrupt` | Request the native active-operation cancellation primitive and record response/terminal/exit separately | Request, acknowledgement and resulting state; no rollback claim |
| `drain` | Close new root/child admission, allow only the declared already-admitted operations needed to finish/reconcile, continue reading streams/receipts | Finite allowlist, owned set, deadline and final settled/unresolved inventory |

`drain` is not permission for open-ended autonomous continuation, new scope, quota reset or more inference to “finish cleanly.” The exact allowed already-admitted operations and whether a new inference request is permitted must be frozen in the task's admission. A checkpoint is not permission to issue a new model summarization call.

Implementation-sensitive cases for the later fixture and qualification:

- Pi's queue requires clear/retain disposition before abort [RF-S32]. For Claude, qualify the [canonical queue-control distinction](#claude-sdk-facts) rather than treating an interrupt as queue settlement
- Antigravity: map [documented input-close behavior](#antigravity-headless-facts) to the intended control outcome; do not infer active interruption
- ACP permits updates after cancel until the cancelled prompt response, so the collector keeps reading [RF-S52]
- Codex: test [documented subscriber lifetime](#codex-app-server-facts); UI detach must not blindly become unsubscribe
- Shared servers may own unrelated sessions. Full Stop uses session-scoped controls and a rooted ownership set; killing a shared server requires separate scope and must not stop unrelated work
- A killed PID does not retract a published message, external transaction, committed file or remote job. PID reuse, child escape, detached helpers and supervisor restart require separate evidence

At a deadline, report `stopped_with_unresolved_effects` where necessary; do not report clean rollback or success. Deadline expiration never supplies new authority. Later physical-process validation belongs on D-028's accepted Windows/Linux floors; source semantics and stub traces do not qualify that containment.

## 10. R-F.Q11 — Fan-in, bounded parallelism and convergence

**I / RF-R7.** The canonical parent owns one goal and one acceptance rule. A child returns a candidate manifest, cited evidence, declared losses, accounting and settlement receipts. A reducer can combine evidence deterministically; a model's synthesis is a proposed artifact, not a new authority or acceptance vote.

- Freeze a dependency DAG/work-unit set and result schema at admission. Child-added tasks are proposals requiring a new admitted work unit
- Each result binds task, attempt, branch, input manifest, grant/epoch and native event cursor. A late old-epoch result can be retained as evidence but cannot commit work
- Fan-in completes when every required unit is independently accepted, explicitly superseded/cancelled with settled effects, or reported blocked/unknown. “Most workers finished” is not a completion gate
- Compare conflicting outputs by the agreed oracle, provenance and authorized artifact/version rules. No majority vote upgrades missing verification. Irreconcilable results stop promotion and ask the existing authority to decide
- Cancel redundant children only when their reserved purpose has been superseded under the same grant. Cancellation savings count only if later measured; preserve already-used resources and uncertain residuals
- Admit work using the minimum of owner ceiling, reserved budget, native/account documented limit, process/memory capacity and review throughput. Unknown account headroom cannot become infinite capacity
- Bound tree depth, queued intents, active roots, total discovered/possible native descendants, per-child retries, stream bytes, timers and review backlog. A process count alone cannot bound hidden native helper calls
- Backpressure never stops receipt collection for already-admitted work. Spill or bound evidence retention under an explicit policy, recording gaps; do not silently discard cancellation/accounting/effect receipts
- Rate-limit responses reduce or suspend further admission according to frozen policy. No account switching, purchased top-up, reset or alternate paid route is automatic

A practical outcome may be honest partial completion: artifacts verified, one remote effect unresolved and one child's usage unknown. Preserve that vector; a dashboard's single green status would be a false claim.

## 11. R-F.Q12 — Competing fan-out designs and decisive falsifiers

This comparison is **I**, not a selection or reconsideration of D-030.

| Design | When it could fit | Decisive falsifier for the proposed fit | What it does not prove |
|---|---|---|---|
| Single sequential delegate | Strong matched baseline; smallest overlap and simplest settlement | Cannot meet an Owner-frozen responsiveness/completion bound despite best eligible native reuse, or loses required continuity | Simplicity does not establish isolation, legal permission or lower allowance |
| Harness-native fan-out | Use native child scheduling/context/tools inside one reserved subtree | A required child can widen scope, exceed enforceable envelope, escape stop, or remain unaccounted for without truthful uncertainty | Native spawning does not guarantee unlimited subscription capacity, independent verification or complete mediation |
| Recursion-orchestrated parallel native launches | Heterogeneous isolated attempts with per-launch identity/reservation | Duplicate/unknown admission is blindly retried; concurrent effects bypass fences; child reservations exceed parent; route terms forbid this driver | More process control does not guarantee secret isolation, native task equivalence or efficiency |
| Queue-only | Serialize admitted work while preserving responsiveness through explicit queue state | Required deadlines cannot be met, or a supposedly stopped queue dispatches after revocation/restart | Queue acceptance is not execution, durable admission or fairness |

No design wins merely by spawning the largest number of workers. Native fan-out and orchestration may coexist only if each ownership layer and overlap in accounting is explicit. A prohibited or unqualified route stays unrun rather than becoming an artificially poor performance result.

## 12. Recommendation register: competitor, falsifier, non-proof

Every design recommendation in §§2–10 and the handoff is keyed below. **All are I/proposed contracts**, subject to existing Owner decisions and independent verification.

| ID | Recommendation | Competing option | Decisive falsifier | Does not prove | Negative control (not an admissible rival) |
|---|---|---|---|---|---|
| RF-R1 | Pin binary, transport, method, schema, maturity and auth profile; expose degraded/unknown semantics | Pinned text/PTY adapter with explicit semantic loss/refusal versus structured adapter; same exact version/auth profile and required evidence | Required semantics depend on an undocumented field or upgrade silently changes authority/completion/accounting | Runtime compatibility, production readiness or vendor selection | Universal text/PTY or unversioned JSON wrapper |
| RF-R2 | Keep caller/proxy and credential domains separate; require R-E boundary for strong non-access | Externally confined all-R/T domain versus separate credential principal; same strong D-029 direct/induced non-access and unmodified-binary qualification | Caller/plugin can directly read or induce secret export, required unmodified-binary support is absent, or a failed strong preflight silently runs weaker | Trust in the harness itself, privileged-host security, or legal clearance | Policy-only same-user caller, labelled honestly |
| RF-R3 | Record each spawn and derive attenuated grants/reservations externally | Pre-reserved attenuated whole-subtree envelope with independently qualified descendant gates versus external per-child admission; same scope and conserved budget | A child/fork/resume enlarges scope, recipient set, expiry or conserved budget | Model compliance or inability to escape an unqualified sandbox | Native transcript/parent prompt as sole authority |
| RF-R4 | All-attempt scoped accounting with null unknowns and disjoint coverage | Retained aggregate-native reconciliation versus event-level disjoint accounting; identical all-attempt coverage, native units, overlap detection and null unknowns | Missing/invalid crash-zero→measured zero, helper omission presented as complete, overlap double-counted, or reset loses history | Exact bills, allowance conversion or quota savings | Successful-result totals or estimated equal per-child allocation |
| RF-R5 | Durable spawn/effect intent and receiver reconciliation; isolate proposals when mediation is absent | Synchronous durable-intent RPC versus outbox dispatch; same receiver operation identity, ambiguity/query ledger and proposal-only refusal when mediation is absent | One ambiguous non-idempotent effect repeats, a lost spawn disappears, or a stale permit commits | Exactly-once remote execution or rollback | Blind retry or direct native effects with hook/prompt policy |
| RF-R6 | Bind Stop mode/scope/policy, queue disposition and rooted ownership | Generation-fenced admission plus bounded rooted-ownership reconciliation versus eager rooted-inventory fencing; same D-022 scopes and receipts | Queued work/relauncher escapes the stop, unrelated work is killed, or unresolved effects become “rolled back” | Actual D-028 process containment or provider cancellation | Kill PID/socket then mark stopped |
| RF-R7 | Canonical fan-in, independent oracle and bounded admission/review backlog | Independently authored outcome adjudication versus reference-state oracle; same canonical fan-in, bounded review/admission and authority floors | Unverified/conflicting output commits, a child becomes canonical writer, or cap violation escapes accounting | Better quality/latency/resource use than strong baselines | First-result-wins or majority vote; unbounded parallelism |
| RF-R8 | Run the provider-free deterministic falsification suite before separately authorized live qualification | Property/metamorphic provider-free campaign versus scripted deterministic suite; same prerequisites, hard floors, planted-control sensitivity and separate live admission | Any hard-floor violation; fixture falsely passes a planted negative control; replay differs for same trace | Harness conformance, physical crash survival, entitlement, model quality, production scale | Source review alone or jump directly to provider workloads |

## 13. R-F.Q13 — Provider-free deterministic experiment design

The complete unexecuted handoff is `unexecuted-local-test-handoff.md`. This section fixes its claim boundary and acceptance logic; it is not an execution report.

### Test object and synthetic endpoints

A deterministic stub reads bounded request records and emits scripted stdout/JSON records, stderr noise, receipts and synthetic usage. It does not invoke any named harness, provider, model, plugin, shell tool, network endpoint or credential path. Separate synthetic components model: canonical writer, trusted launch boundary, native harness/child graph, receiver/effect sink, evidence stream and verifier. These are logical roles, not selected runtime technologies.

Endpoints are logical message names: `admit`, `spawn`, `submit`, `steer`, `queue`, `interrupt`, `checkpoint`, `drain`, `observe`, `effect.prepare`, `effect.commit`, `effect.query`, `settle`, `fan_in`. Test records carry IDs and hashes; they carry no bearer tokens. Delay is measured in virtual ticks with explicit barriers, not nondeterministic sleeps.

The suite varies sequential, native-fanout, parallel-launch and queue-only designs under the same synthetic work/effect oracle. Native-fanout includes both fully observable children and opaque inclusive aggregates. Strong baselines receive the same native resume, checkpoint, artifact backup, grants, effect guard and verifier budget. No crippled baseline is used to manufacture a benefit.

### Primary endpoints and hard floors

| Endpoint | Measure | Hard floor / decision rule |
|---|---|---|
| Authority | unauthorized/stale commits; child scope and reservation conservation | Exactly zero unauthorized/stale effects or widened grants; conserved budget at every transition |
| Spawn reconciliation | each intent's receipt/incarnation/terminal/unknown state | No lost attempt; no blind retry after ambiguous admission; planted duplicates detected |
| Effect settlement | receiver truth versus reported state | No false settled/rolled-back label; each committed/unknown effect retained |
| Accounting | known meter coverage, overlap, resets, unknown residual | No missing→zero, dropped attempt or double counting; opaque attribution remains unknown |
| Stop conformance | scope fence, queue disposition, owned-tree state, deadline | No forbidden post-fence dispatch; each mode preserves its exact scope; unrelated work survives |
| Evidence/privacy | source hashes, context labels, canaries, egress | Zero synthetic-secret leaks or unapproved egress; original evidence lineage retained |
| Fan-in | exact oracle artifacts, conflicts, acceptance and late output | No acceptance without oracle/independent verifier; one canonical writer |
| Resource/performance | synthetic ticks, maxima, queue depth, bytes and review backlog | Prespecified finite bounds; report comparative results only after every safety floor passes |

### Confounders, controls and stopping

Hold total authorized work, evidence, result oracle, allowed tools, helper costs, retry policy and simulated quota constant. Vary one source of failure at a time, then pairwise and chained cases. Include warm/cold reuse, inclusive/exclusive counters, unknown counters, partial streams, empty success, duplicate frames, queue-before-interrupt races, native child nesting, scope mismatch and post-commit receipt loss. Label source-inspired scenarios as simulations, not replicas of actual vendor internals.

Stop a case immediately on a floor breach; preserve its complete trace and fail it. Stop the run on any network/provider/harness process attempt, access outside synthetic paths, credential-like data outside the canary sink, malformed authority proof or exceeded resource ceiling. Inconclusive settlement stays unknown; it does not time out into success. Negative controls must produce failures; a fixture that lets a known violation pass invalidates the suite.

**Unrun:** no endpoint values, latency gains, cost savings, operating-system behavior or native capability has been measured. An independent verifier must later rerun the exact candidate/fixtures and hashes before a provider-free gate can pass. Actual harness qualification, D-028 containment and R-E credential isolation remain separate, explicitly authorized tasks.

## 14. Completion gate and open blockers

| Gate | Report result | Evidence/remaining blocker |
|---|---|---|
| Every named harness mapped, each cell D/I/U | Covered | §1; version/auth distinctions in §§2–3 |
| Caller-not-proxy ownership unambiguous | Contract covered; live ownership unverified | §§3–4; R-E isolation and exact process/helper/network observation unrun |
| Delegation and Honest Accounting defined; unknown never zero | Covered | §§5–6; synthetic representation and missingness reasons |
| Authority, ownership, settlement and canonical fan-in | Covered as inferred design | §§7–8, 10; no physical or vendor guarantee claimed |
| D-022 vocabulary; no PID rollback | Covered | §9; source-specific queue/control caveats |
| Provider-free deterministic experiment, endpoints/confounders/floors/stops/falsifiers | Covered; **unexecuted** | §13 and separate full handoff |
| Every recommendation has competitor/falsifier/non-proof | Covered | §12 and design comparison §11 |
| Protected paths untouched; privacy/secret scan clean | Static artifact checks only | `artifact-validation.json`; no repository write was issued; not a live security audit |

Open qualification blockers: exact installed binaries/schema and flag profiles; endpoint/helper ownership and R-E strong isolation; route-specific stop/queue/effect mediation; counter inclusion and native allowance attribution; counsel/automation entitlement; D-028 physical containment/recovery; independent runtime verification. These are named unknowns, not missing research answers.

The official Hermes documentation was retrieved as public-source evidence. The failed ACP URL is retained as a failed retrieval, not evidence of missing product support.


## Primary-source links

[RF-S01]: https://learn.chatgpt.com/docs/app-server "Codex App Server"
[RF-S02]: https://raw.githubusercontent.com/openai/codex/d25c114d494ddb693290b76bf5e5f64ecbdb38fc/codex-rs/app-server/README.md "Codex pinned App Server README"
[RF-S03]: https://code.claude.com/docs/en/headless "Claude Code headless"
[RF-S04]: https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode "Claude Agent SDK streaming input"
[RF-S05]: https://code.claude.com/docs/en/cli-reference "Claude Code CLI reference"
[RF-S06]: https://code.claude.com/docs/en/authentication "Claude Code authentication"
[RF-S07]: https://code.claude.com/docs/en/checkpointing "Claude Code checkpointing"
[RF-S08]: https://cursor.com/docs/cli/reference/authentication "Cursor CLI authentication"
[RF-S09]: https://cursor.com/docs/cli/headless "Cursor headless CLI"
[RF-S10]: https://cursor.com/docs/cli/reference/output-format "Cursor CLI output formats"
[RF-S11]: https://cursor.com/docs/cli/using "Cursor CLI usage/history"
[RF-S14]: https://geminicli.com/docs/cli/headless/ "Gemini CLI headless"
[RF-S15]: https://geminicli.com/docs/cli/acp-mode/ "Gemini CLI ACP mode"
[RF-S16]: https://geminicli.com/docs/cli/session-management/ "Gemini CLI session management"
[RF-S17]: https://geminicli.com/docs/get-started/authentication/ "Gemini CLI authentication"
[RF-S18]: https://geminicli.com/docs/cli/checkpointing/ "Gemini CLI checkpointing"
[RF-S19]: https://docs.x.ai/build/cli/headless-scripting "Grok Build headless scripting"
[RF-S20]: https://docs.x.ai/build/cli/reference "Grok Build CLI reference"
[RF-S21]: https://docs.x.ai/build/keyboard-shortcuts "Grok Build keyboard shortcuts"
[RF-S22]: https://docs.x.ai/build/enterprise "Grok Build enterprise"
[RF-S23]: https://docs.x.ai/build/features/status-line "Grok Build status line"
[RF-S24]: https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration/ "Hermes programmatic integration"
[RF-S25]: https://hermes-agent.nousresearch.com/docs/developer-guide/acp-internals "Hermes ACP internals"
[RF-S26]: https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server "Hermes API-server documentation"
[RF-S27]: https://opencode.ai/docs/server/ "OpenCode server reference"
[RF-S28]: https://opencode.ai/docs/cli/ "OpenCode CLI reference"
[RF-S29]: https://antigravity.google/docs/cli/headless/ "Antigravity CLI headless"
[RF-S30]: https://www.antigravity.google/docs/cli/install/ "Antigravity CLI installation/authentication"
[RF-S31]: https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/docs/rpc.md "Pi pinned RPC guide"
[RF-S32]: https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/docs/rpc-commands.md "Pi pinned RPC commands"
[RF-S33]: https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/docs/providers.md "Pi pinned providers/authentication"
[RF-S34]: https://raw.githubusercontent.com/NousResearch/hermes-agent/5bba024d8ddd388f56f354c1f789be825e3d8a3c/website/docs/developer-guide/programmatic-integration.md "Hermes pinned programmatic integration"
[RF-S35]: https://raw.githubusercontent.com/NousResearch/hermes-agent/5bba024d8ddd388f56f354c1f789be825e3d8a3c/website/docs/developer-guide/acp-internals.md "Hermes pinned ACP internals"
[RF-S37]: https://raw.githubusercontent.com/anomalyco/opencode/1ddb0873aee50d209d1a8d7f91b89c5daf692d49/packages/sdk/js/src/gen/types.gen.ts "OpenCode pinned generated SDK types"
[RF-S38]: https://cursor.com/docs/cli/acp "Cursor ACP reference"
[RF-S39]: https://geminicli.com/docs/cli/cli-reference/ "Gemini CLI reference"
[RF-S40]: https://docs.x.ai/build/modes-and-commands "Grok Build modes/commands"
[RF-S43]: https://geminicli.com/docs/cli/model-steering/ "Gemini CLI model steering"
[RF-S47]: https://learn.chatgpt.com/docs/non-interactive-mode "Codex noninteractive mode"
[RF-S48]: https://code.claude.com/docs/en/agent-sdk/typescript "Claude Agent SDK TypeScript reference"
[RF-S49]: https://code.claude.com/docs/en/agent-sdk/subagents "Claude Agent SDK subagents"
[RF-S50]: https://code.claude.com/docs/en/agent-sdk/cost-tracking "Claude Agent SDK cost and usage"
[RF-S51]: https://agentclientprotocol.com/protocol/v1/initialization "ACP v1 initialization"
[RF-S52]: https://agentclientprotocol.com/protocol/v1/prompt-turn "ACP v1 prompt turn"
[RF-S53]: https://agentclientprotocol.com/protocol/session-resume "ACP session-resume candidate URL (404)"
[RF-S54]: https://agentclientprotocol.com/protocol/v1/schema "ACP schema reference"
[RF-S55]: https://raw.githubusercontent.com/xai-org/grok-build/72a61251fcffb464bcc687aeb5a998e5a98ec0c9/crates/codegen/xai-grok-pager/docs/user-guide/15-agent-mode.md "Grok pinned ACP guide"
[RF-S56]: https://raw.githubusercontent.com/xai-org/grok-build/72a61251fcffb464bcc687aeb5a998e5a98ec0c9/crates/codegen/xai-grok-shell/src/extensions/interject.rs "Grok pinned interject handler"
[RF-S57]: https://raw.githubusercontent.com/xai-org/grok-build/72a61251fcffb464bcc687aeb5a998e5a98ec0c9/crates/codegen/xai-grok-pager/docs/user-guide/17-sessions.md "Grok pinned sessions guide"
[RF-S58]: https://raw.githubusercontent.com/xai-org/grok-build/72a61251fcffb464bcc687aeb5a998e5a98ec0c9/crates/codegen/xai-grok-shell/src/session/acp_session.rs "Grok pinned ACP session actor"
[RF-S59]: https://raw.githubusercontent.com/xai-org/grok-build/72a61251fcffb464bcc687aeb5a998e5a98ec0c9/crates/codegen/xai-grok-pager/docs/user-guide/02-authentication.md "Grok pinned authentication guide"
[RF-S60]: https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/docs/json.md "Pi pinned JSON event stream"
[RF-S61]: https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/package.json "Pi pinned package manifest"

[RF-S62]: https://opencode.ai/v2/docs/build/client/ "OpenCode v2 client events"
[RF-S63]: https://opencode.ai/v2/docs/api "OpenCode v2 API session.log"
