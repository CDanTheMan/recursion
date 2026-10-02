# R-B — Cross-harness delegation without credential intermediation

Decision-ready research and qualification design | 2 October 2026

## 1. Findings and decision boundary

Recursion can delegate model work to a user-authenticated local harness while retaining its own authority, evidence and accounting. The defensible design is an external canonical record plus a bounded, version-qualified adapter, with a separately enforced credential boundary. A subprocess alone establishes neither credential isolation nor complete effect mediation. A transcript summary alone establishes neither authority continuity nor evidence continuity.

Recursion is both a harness and a harness orchestrator. Lucas remains final Owner. Hermes is one upstream harness in this report, not an executive control plane. D-021 remains delegation over credential intermediation; D-023 makes Codex App Server the first qualification priority, not an already-qualified route or an exclusive vendor choice; D-024 makes productive continuity the measurable outcome. No additional product default is selected.

Four findings change the qualification work:

- Published interfaces are richer than a single prompt/response wrapper, but admission, consumption, terminal output, independent acceptance and effect settlement are different events
- Source versions matter: current Codex web documentation retains deprecated thread/rollback, while the pinned source README removes it and names thread/revert. The exact installed release must resolve this conflict [S01, S02]
- Fresh Hermes documentation supports reconnect replay of open questions and persisted ACP sessions; that does not establish durable prompt admission across an owner-process restart. Pi now documents compaction and branch-summary usage inclusion; the blanket assertion that these helpers are excluded is not current for that pinned profile [S31–S35]
- A provider-free fixture experiment can falsify the continuity design and its ledgers. It cannot qualify real harness behavior, provider entitlement, model quality, quota savings or production reliability

All actual harness executions, logins, model/provider requests, adapter implementation, credential changes and continuity experiments remain unrun. Legal route clearance belongs to R-C/counsel. Research evidence does not authorize execution or constitute Owner acceptance.

## 2. Evidence rules and source pins

Every map field below uses D = source-documented, I = inferred design consequence, or U = unknown from the cited material. O = locally observed is reserved for executed behavior; no map field is O. Reading or hashing a public document is not observing its described runtime behavior. A D assertion is attached to its surface and version; it is not a guarantee.

Public documents were retrieved on 2026-10-02 UTC. The source register identifies exact URLs and sections; the companion sources.json records retrieval timestamps and SHA-256 of successfully captured public response bytes. Immutable source pins are used for Codex, Hermes, OpenCode types and Pi. Mutable documentation is a dated snapshot; its correspondence to a released binary remains U. A failed capture is marked failed rather than assigned a fabricated hash. No prior Recursion repository, previous report or old memo supplies evidence here.

Important separation: provider credential = authority to consume a model/provider account; caller authentication = authority to reach a local/remote harness control endpoint. A server bearer password can confer substantial machine/tool access even when it is not a provider token. Neither may be assumed harmless, copied out of a user's environment, or silently introduced by an adapter.

## 3. Nine-harness surface map (Q1)

The five labeled fields in each profile are the map cells. Interactive-only controls are explicitly distinguished from programmatic ones. Unless stated otherwise, durable in-flight queues, crash-safe approvals, exact helper accounting, complete mediation and effect settlement are U for every profile.

### 3.1 Codex App Server

- Submit — D: initialize a connection, start/resume a thread, then turn/start [S01, Basic usage]
- Steer/queue — D: turn/steer appends input to an active turn with expectedTurnId; not a new turn. General durable queue survival is U [S01, Steer an active turn]
- Interrupt — D: turn/interrupt; terminal interrupted status is documented. External effect rollback is U [S01, Interrupt a turn]
- Resume/fork/rewind — D: thread/resume and thread/fork. Rewind is version-conflicted: web docs retain deprecated thread/rollback; pinned source removes it and points to thread/revert for paginated threads. Installed behavior U [S01; S02, Thread rollback]
- Observe — D: item events, turn/completed, thread/tokenUsage/updated, contextCompaction items, correlated approvals/questions, review/start. Full settlement and complete billable-use coverage U [S01, Events, Approvals, Review]

### 3.2 Claude Code

- Submit — D: claude -p and programmatic Agent SDK; JSON and stream-json output [S03, Basic usage]
- Steer/queue — D: SDK streaming input supports sequential queued messages and interruption. Exact same-turn steering/queue durability under process loss is U [S04, Streaming input]
- Interrupt — D: streaming-input interrupt capability; claude stop targets background sessions. Headless signal-to-effect settlement is U [S04; S05, CLI commands]
- Resume/fork/rewind — D: --resume/--continue, --fork-session and checkpoint rewind. Rewind has explicitly limited file coverage [S03, Continue conversations; S05, CLI flags; S07, Limitations]
- Observe — D: streamed messages and result with session/cost metadata. A result is not independent correctness acceptance; full hidden/helper coverage and all effects settled are U [S03, Stream responses]

### 3.3 Cursor

- Submit — D: agent -p; agent acp with session/new and session/prompt. TypeScript/Python SDKs also submit local/cloud runs; hosted API is separate [S09; S38; S13; S41–S42]
- Steer/queue — D: interactive CLI Enter steers at a safe boundary; a second Enter interrupts. SDK local run.steer returns complete_delivered or revert_to_followup; cloud/detached handles fall back to follow-up. ACP/headless parity and queue durability U [S12; S38; S41, Steering]
- Interrupt — D: ACP session/cancel; SDK run.cancel for local/cloud. External effect settlement remains U [S38, Request flow; S41, Cancelling]
- Resume/fork/rewind — D: --resume/--continue, ACP session/load and SDK Agent.resume. Programmatic fork/rewind U in reviewed CLI/ACP references; editor checkpoints do not establish CLI parity [S11, History; S38, Sessions; S41, Resuming]
- Observe — D: stream-json tool events and terminal result on success; failure may have no terminal JSON. CLI token/cost fields U in this schema. SDK streams, cumulative run usage and getUsage billed records are D, separately scoped [S10; S41, Usage]

### 3.4 Gemini/Google CLI

- Submit — D: Gemini CLI headless prompt and ACP prompt/newSession. This identifies Gemini CLI, not every Google CLI [S14; S15, Core methods]
- Steer/queue — D: experimental interactive hints reach the next turn; a small model generates acknowledgement. Programmatic ACP/headless parity, durable queues and acknowledgement-helper meter coverage remain U [S43, Using model steering, How it works]
- Interrupt — D: ACP cancel. Process/remote-effect settlement U [S15, Core methods]
- Resume/fork/rewind — D: ACP loadSession, CLI --resume, session checkpoints and file checkpoint restoration. Native cross-harness fork parity U [S15; S16; S18]
- Observe — D: headless init/message/tool_use/tool_result/result events with aggregate/per-model usage, error and exit status. Complete hidden-helper inclusion U [S14]

Version seam: the ACP guide uses --acp while the CLI cheatsheet lists --experimental-acp. Pin the binary and advertised profile; do not silently translate flags or claim both work [S15, Start; S39, Flags].

### 3.5 Grok Build

- Submit — D: grok -p and grok agent stdio; ACP session/prompt and session/update [S19]
- Steer/queue — D: interactive interject and prompt-queue controls. A public, version-specific programmatic steering contract and crash durability remain U [S21, Input, Panels]
- Interrupt — D: interactive cancellation controls. Do not infer complete background-effect settlement from a keypress; programmatic cancel semantics are U in this reviewed surface [S21]
- Resume/fork/rewind — D: --resume/--continue/--session-id, --fork-session; interactive /rewind. Cross-harness authority migration U [S19; S20; S40]
- Observe — D: JSON/streaming-json; changelog 0.2.97 documents per-prompt/session usage and cost. Full helper coverage U. Status-line cost resets on resume, so it is not a lifetime total [S19; S23; S36, 0.2.97]

### 3.6 Hermes

- Submit — D: ACP prompt, TUI-gateway prompt.submit, HTTP run/response surfaces [S34, Protocols]
- Steer/queue — D: session.steer, busy-input policies and HTTP run steer. Acknowledgement means queued; consumption waits for a tool boundary, with pending_steer reported if undelivered [S34, API server]
- Interrupt — D: ACP cancel, session.interrupt, HTTP run stop; independent effect settlement U [S34, Method catalog; S35, Cancellation]
- Resume/fork/rewind — D: saved ACP sessions, resume/load/fork; session.branch and explicitly confirmed destructive rewind. Live activation is process-local; prompt-admission durability across owner restart is not claimed [S34–S35]
- Observe — D: lifecycle/tool events, session.usage, run status/events and reconnect open_requests/inflight. Complete usage coverage U [S34, Requests, Events, Terminal status]

### 3.7 OpenCode

- Submit — D: opencode run; headless server session creation and message endpoint; ACP support is separately documented [S27; S28]
- Steer/queue — D: prompt_async returns 204 without waiting. I: asynchronous admission alone does not prove steering an already-running turn; active steering and durable queue semantics U [S27, Messages]
- Interrupt — D: session/:id/abort. Settlement U [S27, Sessions]
- Resume/fork/rewind — D: session/message retrieval, fork, revert/unrevert and CLI continuation. Exact reconstruction across versions U [S27, Sessions; S28, Run]
- Observe — D: SSE events, session status, message/parts; pinned generated types expose cost/token fields. Helper coverage and post-abort effects U [S27; S37, AssistantMessage]

### 3.8 Antigravity

- Submit — D: agy -p and persistent stream-json stdin; separate Python SDK Agent.chat and managed Gemini Interactions API profiles also exist [S29; S44; S46]
- Steer/queue — D: successive turns in one process; guide says wait for each result. Same-turn steering/durable queue U; control_request/control_response are explicitly unsupported [S29, Drive a session, Unsupported messages]
- Interrupt — D: closing stdin waits for the current turn then exits. This is graceful close, not active cancellation; headless active-stop contract U. SDK/managed cancellation semantics are U in the references reviewed here [S29, End a session; S44–S46]
- Resume/fork/rewind — D: --continue/--conversation; SDK save_dir/conversation_id persist/restore sessions. Programmatic fork/rewind U for these profiles; managed cross-profile resume U [S29, Continue; S45, Persistence]
- Observe — D: step_update/result, token fields and subagent references. Headless counters are cumulative; exit 0 can accompany tool soft-denial. SDK response.usage_metadata is separately documented; full settlement U [S29; S45, Cost auditing]

### 3.9 Pi

- Submit — D: subprocess RPC prompt, CLI and separate SDK integration [S31, Interfaces]
- Steer/queue — D: steer/follow_up with different delivery boundaries; disposition accepted/queued/handled is not completion [S32, Prompting]
- Interrupt — D: abort, abort_bash and abort_retry are separate controls [S32, Abort, Bash, Retry]
- Resume/fork/rewind — D: switch_session, fork/clone, append-only session entries including prior branches. Filesystem rollback does not follow from conversational branching [S32, Session]
- Observe — D: events, get_entries, get_session_stats; agent_end can precede automatic continuation, whereas agent_settled is the documented idle signal. Compaction usage may be absent from custom handlers [S31, Lifecycle; S32, Compaction, Stats]

## 4. Credential ownership and route choice (Q2–Q3)

These are technical boundaries, not permissions to use a subscription or redistribute a client.

- Codex — D: managed ChatGPT authentication is owned/persisted/refreshed by Codex; apiKey and external chatgptAuthTokens modes require caller-supplied secrets. D-021's candidate is already-authenticated managed local use, with auth mutation endpoints outside the adapter. Remote server bearer authentication is a separate credential. Local/open-source versus commercial/hosted constraints need R-C clearance [S01, Auth endpoints]
- Claude Code — D: local account authentication and alternative key/token/helper/cloud-provider paths are documented. Candidate: unmodified, already-authenticated local process; Recursion never invokes setup-token or reads/injects credentials. An SDK surface is not itself permission to transplant subscription auth [S05, Auth commands; S06]
- Cursor — D: login credentials are stored locally; env/flag keys and ACP auth-token alternatives are caller-supplied paths. Candidate: already-authenticated CLI/ACP. Hosted API accepts Basic/Bearer keys. SDK local/cloud uses user/service API-key identity, supplied by the caller or SDK-managed interactive login that mints/stores a key. Local describes the agent loop. Neither path was executed; SDK/hosted routes need separate isolation/authorization and Owner/counsel clearance [S08; S13; S38; S41–S42, Authentication]
- Gemini/Google CLI — D: headless uses existing cached authentication; API key/Vertex/ADC are separate methods. Candidate: authenticated CLI resolves its own existing credential. Copying ADC/key material into Recursion would cross the boundary [S17, Authentication, Headless]
- Grok Build — D: ACP can use an existing cached token; alternatives include API key and external auth-provider command. Candidate: existing local session, not a token-broker integration authored by Recursion [S19, ACP; S22, Authentication]
- Hermes — D: ACP reuses Hermes' configured provider resolver rather than owning another auth store. HTTP API additionally requires API_SERVER_KEY, including loopback. Candidate: preconfigured local harness interface; a new caller bearer is separately authorized and cannot be described as credential-free merely because it is not a provider key [S25, Provider/auth; S26, Configuration]
- OpenCode — D: startup reads its own auth store and may also read environment/project .env; HTTP basic auth is optional server protection; provider auth-setting endpoints exist. Candidate: isolated preconfigured harness; provider-auth writes, broad config writes and project secret discovery are outside this adapter [S27, Authentication, Auth; S28, Auth]
- Antigravity — D: headless uses cached credentials; local CLI can use OS keyring, while configured Gemini API-key mode reads caller environment and has no account session. Candidate: cached local CLI auth. SDK Gemini-key/Vertex-credential and managed API-key routes are separate caller-credential profiles; key entry/relay is outside Recursion and they are not fallback authorization [S29–S30; S44, Quickstart, Enterprise; S46, REST]
- Pi — D: interactive authentication saves keys/tokens in its own auth store; environment keys and key-resolver commands are alternatives. Candidate: RPC process resolves existing Pi-owned authentication; in-process embedding or passing raw keys would enlarge the secret-bearing boundary [S33, Authentication]

Local delegation is the D-021 preference, conditional on capability, isolation and route permission. Hosted APIs are never an automatic fallback. Where a host API was not established in this surface review, its existence and applicable credential contract remain U. Selecting a second adapter, deployment mode, runtime or token-bearing route remains an Owner decision after technical and R-C evidence; this report selects none.

## 5. Capability and loss taxonomy (Q4–Q6)

A capability assertion is a typed tuple: operation + surface/version + preconditions + effect scope + evidence class + source/observation reference + validity interval. A transition records before/after values separately for five axes:

1. Authority: grant identity, scope, revocation epoch, approval waiter binding, single-writer/fork ownership
2. Context/working state: original inputs, selected branch, artifacts, tool state, pending messages, summaries and compaction boundaries
3. Evidence: originals, source identity, content hashes, event ordering, provenance and withheld/redacted parts
4. Accounting: attempt lineage, helpers, meter scope, inclusion/exclusion, missing counters and spend uncertainty
5. Effect control: admission, authorization check, dispatch, execution, interruption and externally verified settlement

On each axis use capability present/degraded/lost/unknown. Keep recovery orthogonal: recoverable from retained canonical evidence; recoverable only after renewed user input; unrecoverable under the available evidence; or unknown. A loss is not automatically irreversible. An upstream's missing verb is not a loss if the product never promised that capability.

### Source-supported losses and non-losses

- Claude rewind cannot undo Bash modifications and ordinarily excludes several subagent/external changes. Lost property: general workspace rollback. Recovery requires independent artifact history; a transcript rewind cannot manufacture it [S07, Limitations]
- Cursor's non-streaming JSON intentionally omits tool/delta history and may emit no result JSON on failure. Lost property: evidence detail or terminal record if this is the only capture. Recursion must record pre-admission and stream/process evidence; past uncaptured bytes are unrecoverable [S10]
- Cursor SDK tool restrictions and systemPrompt do not persist across resume. Lost property: caller-specific restrictions unless deliberately reapplied and externally enforced; this is not CLI/ACP behavior [S41, Caveats]
- Gemini session retention deletes associated plans, trackers, outputs and logs; default retention is documented as 30 days. Lost property: local evidence availability after cleanup without an independent copy [S16, Retention]
- Hermes rewind rewrites durable rows, so cached row IDs become stale. Lost property: old locator validity, recoverable from the supplied survivor mapping. ACP non-text prompt blocks are ignored; lost property: faithful multimodal input on that profile [S34, Rewind; S35, Limitations]
- Hermes reconnect replay preserves live questions; it does not prove restart-safe waiter state or durable prompt admission. Such crash continuity is U, not a demonstrated current loss. An HTTP steer that is accepted but never consumed is explicitly distinguishable via pending_steer [S34]
- Antigravity streaming accepts text only and rejects control messages; lost property when translating a richer route is multimodal/control parity. Cumulative counters treated as deltas create duplicate accounting, not extra usage. Tool soft-denial with successful exit loses the implication that exit 0 means requested work occurred [S29]
- Pi get_entries preserves pre-compaction/abandoned history, so native compaction is not proof of destroyed originals. But a summary-only export loses source detail; that is I, a proposed adapter defect. Custom compaction can omit usage; exact omitted usage then remains U. Current documented totals include compaction and branch summaries [S32]
- Grok process-local displayed cost restarts on resume; carrying it forward as lifetime cost loses past accounting. Headless usage fields now exist, so the old blanket “no counters” claim is rejected [S23; S36]
- Codex removed rollback versus web-document deprecation is a version portability break. A route using the wrong contract loses the requested operation; no actual failure was executed [S01, S02]
- OpenCode prompt_async documents no-wait submission, not active steering. Treating it as steering silently loses an unproven semantic guarantee; actual active-turn behavior remains U [S27]

Authority duplicated by a source fork, unpersisted queues erased by a machine loss, and provenance erased by a summarizer are cross-harness failure hypotheses (I), not observed defects attributed to all nine products. No current source pin here proves every pending question is in-memory, every hook fails open, or every cancel leaves effects running. Those inherited examples are experiment cases, not findings.

A DelegationRecord must preserve original evidence references even when a summary is generated. “Observed on version X” may coexist with “documented on version Y”; neither overwrites the other. Unknown reasons include undocumented, unexercised, unsupported, contradictory, unavailable, omitted and lost. An empty array means known empty only when coverage is complete; otherwise accompany it with coverage unknown.

## 6. Delegation architecture and record (Q7–Q8)

This is a proposed contract (I), not an implemented architecture. Its components specify responsibilities, not a language, store, transport, protocol or runtime.

### Canonical state outside upstream sessions

The small Recursion kernel retains Owner intent and AuthorityGrant references, epoch/revocation state, goal/WorkUnit/Attempt graph, pending approvals/questions, evidence/artifact manifests, transition losses, HonestAccounting and effect receipts. It is not an autonomous executive. Plugins request capabilities and cannot mint grants. Upstream sessions are useful acceleration state and never the sole copy of intent or evidence.

The minimum handoff kernel contains the authorized goal; allowed actions/resources and denied boundaries; grant/epoch references; completion and stop criteria; source/artifact identifiers with provenance and integrity hashes; unsettled-effect identifiers; pending questions with disposition; and accounting obligations. No credential, secret resolver, hidden reasoning, inherited self-approval, or new permission is carried in it. A reference to a grant is not a transferable bearer grant: the effect boundary validates the caller, route and current epoch independently.

### Credential isolation: the strong claim has prerequisites

A source-reviewed wrapper that promises not to read tokens is weaker than a process that cannot read them. Same-user processes can have ambient access through home files, inherited environment, process inspection, keychain interfaces, debugging, crash dumps, shell configuration, or arbitrary subprocesses. Simply calling a logged-in CLI satisfies neither an architectural non-access claim nor complete mediation.

The strong profile requires an operator-provisioned, trusted launch/auth boundary outside Recursion's readable/control domain. Recursion receives an opaque launch handle, not an environment snapshot or home directory. The boundary starts the approved harness with its pre-existing authentication; strips secret-bearing parent environment from Recursion; prevents Recursion and plugins from inspecting the harness's process memory, credential paths/keychain, launch configuration or dumps; and exposes only scoped artifacts and structured control/results. OS-specific mechanisms on Windows/Linux must be separately demonstrated rather than presumed equivalent. No mechanism is selected here.

The trusted authenticated harness is itself a secret-bearing component. Its model tools must be prevented from reading credential stores or exporting them, and its output contract must exclude secret values. If the harness deliberately leaks credentials, a generic output filter cannot prove absence of covert channels. Therefore the claim is conditional on a trusted, pinned auth/harness boundary plus demonstrated isolation, not protection from a malicious credential-owning harness or privileged OS compromise. If the deployment cannot meet this boundary, label it non-intermediation-by-policy only, and reject the stronger “Recursion cannot see credentials” qualification.

A new machine must already have separately user-authorized authentication. Never migrate credentials inside a continuity capsule. If absent, stop at authentication_required; preserving work while awaiting user action is continuity of state, not completed productive continuity.

### Admission, execution and transition protocol

1. Persist Attempt and AuthorityGrant/epoch binding before submission. Verify RouteProfile identity, binary/docs/protocol versions, data boundaries and declared losses. Never add an automatic paid route or weaker permission mode
2. Rehydrate only approved artifacts into a scoped workspace; verify hashes, original source identities and branch ancestry. Derive summaries from originals and label them derivative. Importing external text cannot change authority
3. Submit a bounded request through the local adapter; record an ambiguous admission separately if the connection fails before acknowledgement. Retry only with idempotency/reconciliation, never by guessing that no work began
4. Persist correlated approval/question state outside the upstream: request hash, attempt/turn, epoch, action/target, expiry and response disposition. Reconnect may re-present it; a resumed or forked session must not replay an old approval into a different action
5. Before every effect, the external enforcement point validates live scope/epoch and resource preconditions, then writes an intent with a stable effect ID. For direct upstream effects, complete mediation must be proven. If not provable, permit only proposal/artifact production in an isolated workspace and independently authorize application. Prompt instructions, hooks and approval APIs alone are insufficient
6. Detect compaction through declared events or history markers; Codex's contextCompaction is one example. If the profile offers no reliable signal, compaction observability is U and the adapter reconstructs required canonical state at the next safe boundary. It does not infer preserved facts from lower token counts
7. At handoff fence the prior effect authority, request interrupt, reconcile issued effects and durable admissions, and persist a loss manifest. “Cancel acknowledged” is not “no effects remain.” Unsettled effects block conflicting replay
8. Create a successor Attempt on B with the authorized current branch, narrowed scope and new epoch binding. A source fork does not duplicate authority: both branches may analyze, but only explicitly granted nonconflicting effects proceed. Late A outputs remain evidence, not authority
9. Accept completion only when independent criteria pass and required effects are settled. Preserve partial/failed attempts and uncertainty; an upstream final answer cannot accept itself

### Concrete DelegationRecord fields

- Identity: schema version; delegation, goal, WorkUnit, Attempt and parent IDs; source/target RouteProfile IDs; native session/turn IDs when known
- Authority: AuthorityGrant reference; current epoch; action/resource boundaries; issuer; expiry/revocation checks; effect-policy profile; no bearer secret
- Continuity: source branch and selected successor; canonical event cursor; artifact/evidence manifest; compaction boundary; derivative summary references; pending waiter and queued-input disposition
- Capability/loss: operation-specific assertion IDs, evidence class and source pins; before/after axis states; loss reason, recoverability and required intervention
- Lifecycle: created/admission-unknown/admitted/running/waiting/interrupted/failed/upstream-complete/independently-accepted; timestamps and causal events
- Reconciliation: effect intents/receipts, unsettled IDs, deduplication keys and late-output disposition; HonestAccounting reference; local qualification evidence and independent review outcome

Example: an approval for effect E at epoch 7 remains pending when A disconnects. B receives its description as pending evidence, not permission. After transition to epoch 8, the old reply is stale. E is reconciled against the effect ledger; only a new valid decision bound to the current action may dispatch it. If dispatch happened but its receipt was lost, E stays outcome_unknown and is not blindly repeated.

## 7. Minimal HonestAccounting (Q9)

The smallest honest record must represent absence and scope, not merely a token total. This contract is aligned with R-D's measurement record and R-A's shared IDs.

- Identity and lineage: experiment/block/task/WorkUnit/Attempt/parent IDs; role primary/helper/compaction/verification/retry/recovery; route and version; opaque model/effort/account-window references, with unknown where unavailable
- Lifecycle: recorded before admission; start/end clock plus ordering basis; admission state; completed/interrupted/cancelled/failed/partial/unknown terminal outcome; reason; upstream completion separately from independent acceptance and effect settlement
- Resources: a list of meters, each with value number or null; unit; measured/modelled/unknown; per-attempt/per-turn/session/process/account-window scope; delta or cumulative semantics; timestamp; raw evidence reference; inclusion/exclusion and missing reason
- Coverage: known child-attempt IDs; helper discovery complete/partial/unknown; explicitly excluded helper categories; omitted-meter reason. Unknown helper existence is not zero helpers
- Reconciliation: meter snapshot/reset identity, deduplication cursor, counter corrections, effect-settlement state, accepted output reference and independent acceptance evidence

Zero is valid only when a measured, covered counter explicitly reports zero, or a complete pre-dispatch trace proves no provider request and no helper ran within that meter scope. The latter is proven_not_dispatched, not an imputed missing counter; local compute and human effort still remain in their own meters. Null with unknown is mandatory for missing data. A cumulative counter is differenced only within a stable scope/reset interval with compatible inclusion semantics; otherwise retain snapshots. Overlapping parent/child totals are never blindly summed. Token count, modelled currency, actual billed currency and subscription quota depletion are different meters. A provider-free fixture meter must be labeled synthetic measured; it is not real provider usage or spend.

All admitted and admission-unknown attempts remain in denominators, including failures and interruptions. Count retries, recovery, compaction and verification work even if the upstream reports only successful output. A useful partial ledger may pass honesty while failing completeness; it cannot support a total-cost or savings claim until missing scope is bounded. Pi's documented inclusive session totals and Antigravity's cumulative session counters specifically require overlap-aware accounting [S29, S32].

## 8. Competing designs and decisive falsifiers (Q10)

The following are the recommendations in this report. Each includes a competing option and a bounded claim.

- R1: Keep canonical authority/evidence outside every harness. Competitor: single-harness-native persistence. Reject R1 if required state cannot be reconstructed without undocumented session internals, or transition allows stale authority. It does not prove better model output
- R2: Require an enforceable secret boundary for the strong non-access profile. Competitor: source-reviewed same-user wrapper. Reject strong R2 qualification if synthetic credential canaries are readable by Recursion/plugins or appear in their logs/artifacts. It does not establish security against the trusted harness or privileged OS
- R3: Use typed, version-specific adapters with explicit degraded/unknown states. Competitor: a universal text/PTY wrapper. Reject R3 if a required capability can only be approximated while being reported preserved. It does not choose a protocol or prove an advertised capability works
- R4: Gate effects through externally checked authority and reconciliation. Competitor: upstream tools plus prompt/hook policy. Reject R4 if any effect bypasses the fence, a stale approval executes, or ambiguous effects are replayed. It does not undo already committed external effects
- R5: Retain all-attempt scoped accounting. Competitor: successful-result totals. Reject R5 if known missing counters become zero or cumulative/child totals double count. It does not reveal unobservable provider billing internals
- R6: Evaluate continuity with strong matched baselines before making efficiency claims. Competitors: native-only Recursion, a fully featured single harness, and a credential-intermediating router. Reject the benefit claim if switching gives no prespecified advantage after hard floors and uncertainty. The credential-intermediating router is an analytical comparator under D-021, not an authorized implementation

Native-only offers the smallest upstream dependency and a useful control; single-harness offers richer native semantics with less translation; a credential router can expose uniform provider APIs but moves secrets into a new trust domain and still does not recover evidence or settle tools. Delegation wins only if its continuity benefit survives these controls. No competitor reopens the accepted Owner decisions.

## 9. Falsifiable productive-continuity experiment (Q11–Q12)

### Claim and stages

Hypothesis H1: under a prespecified set of recoverable disruptions, a currently authorized task can complete on B after A becomes unusable, retaining all required authority/evidence invariants and an honest all-attempt ledger, with less repeated accepted work than matched restart controls. This is a conjunctive claim: quality, cost or speed cannot compensate for a floor violation.

Stage P is provider-free and is the precise local handoff below. It uses deterministic harness-behavior fixtures and a synthetic effect sink, not actual Codex/Claude/etc. processes. It can reject the adapter/kernel contract. Stage H would later qualify exact real binaries and auth boundaries, with Codex App Server first and a deliberately different second adapter chosen separately. Stage H requires new explicit authorization, route clearance and applicable budget; it has not been scheduled or executed.

### Synthetic task and injected transitions

Fixture task: from a signed-off synthetic requirement set and two labeled source documents, produce a dependency-ordered change proposal and update a synthetic inventory through a reversible mock effect sink. The deterministic oracle specifies exact accepted artifact hashes, cited source IDs, allowed effect set, forbidden effect set and dependency order. Include conflicting untrusted text that asks to expand permission, an allowed idempotent update, a pending approval and a deliberately non-idempotent mock increment.

At named causal barriers, not wall-clock sleeps:

1. A admits a request, emits a source-derived intermediate artifact and pauses with an unresolved approval and a queued correction
2. Simulate native compaction: provide a lossy derivative summary while retaining originals externally; also test an undeclared compaction/event gap
3. Simulate a source fork: preserve branch ancestry, give two branches competing proposals, and attempt duplicate authority and a late stale approval. Separately vary adapter source version to detect a contract/source fork; this is distinct from conversation branching
4. Simulate lost machine: make A's process-local state inaccessible while leaving the declared external checkpoint available. Include loss immediately before admission acknowledgement and after mock-effect commit but before receipt
5. Fence A and rehydrate on B. A later returns a completion and an effect request; both must be reconciled under the old epoch
6. Complete only the authorized current branch; independently verify artifact/effect/evidence oracles and account for all attempts, including interrupted helpers

Run isolated single-fault cases, pairwise combinations, the full chain, and a no-fault condition. Reverse A/B fixture roles so the result is not an artifact of a richer destination. Vary which capabilities are documented/present/absent and force unknown responses. No fictitious fixture outcome is recorded as measured product performance.

### Strong baselines and ablations

- B0: same single-harness fixture, no disruption, full native context/tools/checkpoints, same task budget and external effect oracle; ceiling and instrumentation overhead
- B1: strong single-harness recovery with its best documented resume/compaction/fork behavior, identical durable artifact backup, authority/effect guard and accounting; grant it the same lost-machine replacement and restore opportunity. It must not be a deliberately crippled transcript-only baseline
- B2: restart on B from original task and canonical evidence, with the same grants/budget; isolates reusable progress benefit
- B3: native-only Recursion contract fixture with the same evidence/guards; isolates extra adapter burden
- Ablations: remove only external waiters, provenance, accounting scope metadata or effect reconciliation, one at a time. These are synthetic fault cases, never permission to weaken real safeguards

For an irrecoverable native-machine-loss condition, report recovery capability separately. Do not turn “baseline unavailable” into an infinite speed/cost win. Match optional features, cold/warm caches, failure injection and operator intervention across methods.

### Endpoints, hard floors and confounders

Hard floors, evaluated first on every trial:

- Authority/safety: zero unauthorized or stale-epoch committed effects; zero duplicated exclusive authority; every approval bound to its exact current action/target; no conflicting replay of outcome_unknown effects
- Privacy: zero synthetic secret-canary bytes entering Recursion-readable data, prompts, logs or artifacts; zero unapproved egress; zero credential transfer between machines
- Correctness: every mandatory oracle assertion passes, including tool-denial visibility and selected branch; successful prose/exit status is insufficient
- Evidence: every required source boundary and accepted artifact is integrity-verifiable; missing originals or false provenance fail the floor, not just a quality score
- Reproducibility: full fixture/version/seed/fault/clock-order record and independently repeatable verdict; a hidden manual repair is a failed reproducibility floor
- Accounting honesty: all admitted/admission-unknown attempts retained; known missing data never zero; no unlabelled estimate or overlapping double count

Then report: independently accepted completion rate over all assigned tasks; retained accepted-work fraction; repeated work/reads; recovery time from injected disruption to accepted continuation; user interventions; lost/recovered waiter count; artifact/evidence coverage; attempted/committed/settled/unknown effects; per-attempt scoped synthetic resource vectors and unknown coverage. Stage P measures no real tokens, quota or money.

Confounders: model quality, provider load/limits, model/effort mismatches, helper fan-out, caches, content-window differences, native retention settings, prompt ordering, source forks, asynchronous background effects, auto-updates, platform permissions, network loss and clock skew, omission/redaction, evaluator leakage, and selective exclusion of failures. Stage P fixes or explicitly varies these as fixture parameters; real behavior remains unmeasured.

Before a later run, freeze task families, disruption matrix, rejection rules and a smallest practically useful continuity gain. For Stage P exhaustively enumerate the finite fault-state fixtures and report exact counts; it is not a statistical sample of production. For Stage H preregister matched repeated tasks, paired uncertainty intervals and a power/precision justification; do not invent confidence from a handful of successes. Unknown cost/coverage makes an efficiency verdict inconclusive even if the safety floors pass.

Immediate stop/falsifier: any floor breach; credential exposure; unresolved authority conflict; unmediated effect; unrecoverable required evidence; ambiguous admission/effect replay; falsely successful denied tool; hidden repair; or route/version drift. Pause that profile, preserve synthetic evidence and obtain independent review. A recoverable wait for an approval is not a failure by itself, but completion stays pending. H1 is rejected for the declared domain if a recoverable fixture cannot finish within the prespecified task budget or retention of accepted progress does not beat B2; the D-024 headline benefit requires prespecified superiority in independently verified outcomes and human effort against strong B1, following R-D's dependency-aware preregistration and uncertainty rules. Reduced repeat work against B2 alone supports only the narrower reuse mechanism. No broad “productive continuity proven” label follows from a fixture pass.

## 10. Precise local execution handoff

Status: design only; every operational outcome below is UNRUN. This section is not permission to launch a harness, install software, log in or call a provider.

Prerequisites before Stage P:

1. Owner separately authorizes implementation/execution in an identified disposable local environment; no production repositories, real credentials, provider network or external effect tools are mounted
2. Independent reviewer freezes the schema, authority/effect invariants, deterministic task oracle, finite fault matrix and baseline budgets before results are generated
3. Fixtures use synthetic credential canaries held outside the Recursion-readable boundary; egress is blocked. Harness A/B are behavioral models with declared capabilities, not actual named product binaries
4. Capture exact fixture hashes, environment/OS isolation configuration, ledger/evidence format, seed, monotonic ordering scheme and artifact manifest. Do not include live user identifiers or auth material

Execution and required evidence:

- Materialize the synthetic sources and expected artifact/effect oracle; verify initial hashes and zero external egress
- Execute B0–B3 and the delegation candidate on the same finite cases; capture immutable chronological admissions, grant checks, waiter state, compaction boundaries, branch ancestry and all resource-meter scopes
- Inject the named barriers, crash/restart, duplicated/out-of-order events, missing usage, helper omission, counter reset, stale approval and after-commit/before-receipt ambiguity; record intended versus actual barrier
- Reconcile the mock sink independently of harness claims; compare all effect IDs, order and hashes against the authority oracle
- Have an independent evaluator replay each case from the frozen evidence and record floor pass/fail plus endpoint values. The implementer's verdict alone is not acceptance

Stop rules: stop a case on any floor violation, attempted live network/auth access, unexpected real data, or fixture drift; stop the profile if isolation cannot be demonstrated. Do not continue by replacing missing counters with zero, disabling a boundary, silently changing a model/route or restoring a lost receipt by assumption.

Expected output contract: cases.jsonl (all assigned cases), attempts ledger, effects ledger, artifact/evidence manifest, capability/loss records, floor verdicts, paired endpoint summary, reproducibility instructions, failure evidence, and independent review disposition. Filenames are proposed deliverables, not an implemented test suite.

UNRUN outcomes: fixture correctness; all floors; candidate/baseline continuity; Windows and Linux isolation; exact installed-harness admission/steering/waiter recovery; native compaction detection; actual effect settlement; helper completeness; quota/cost; legal entitlement; independent acceptance. The present report supplies none of these outcomes as PASS.

## 11. Completion gate and unanswered qualification questions

Research-deliverable gate:

- All nine named harnesses and five map cells: covered in section 3, each D/I/U
- Per-harness credential and caller-token boundaries: section 4; architecture-strength distinction: section 6
- Typed losses with sources, unknowns and recoverability: section 5
- Canonical authority/evidence/control kernel external to every upstream: section 6, proposed and conditional on enforceable isolation
- Missing counters unknown, not zero: section 7
- Falsifiable continuity design, strong baselines, endpoints, confounders/floors/stops: sections 9–10
- Every recommendation has competitor/falsifier/non-proof: section 8
- Protected project paths: untouched; only new research/artifact files created. Public retrievals and synthetic design only; no harness execution, credentials, real account IDs or provider requests

Open qualification questions are deliberately not Owner decisions answered by implication: exact release/profile compatibility; credential-isolation deployment feasibility; complete effect mediation; durable admission/waiter/queue semantics; helper coverage; second stress-test adapter; and route entitlement. They need later evidence/approval, not another summary of unverified capabilities.

## 12. Source register

IDs cite exact source sections in the body. All are primary public sources, accessed 2026-10-02 UTC. Immutable source SHA and captured-response hashes are evidence pins, not installed-version claims. Sources.json contains full capture hashes and timestamps; raw documentation snapshots are research support and need not be distributed with the report.

- S01: [Codex App Server: lifecycle, auth, events, approvals and review](https://developers.openai.com/codex/app-server)
- S02: [Codex source README: Thread rollback, immutable commit d25c114d494ddb693290b76bf5e5f64ecbdb38fc](https://raw.githubusercontent.com/openai/codex/d25c114d494ddb693290b76bf5e5f64ecbdb38fc/codex-rs/app-server/README.md)
- S03: [Claude Code programmatic/headless operation](https://code.claude.com/docs/en/headless)
- S04: [Claude Agent SDK streaming input](https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode)
- S05: [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- S06: [Claude Code authentication](https://code.claude.com/docs/en/authentication)
- S07: [Claude Code checkpoint limitations](https://code.claude.com/docs/en/checkpointing)
- S08: [Cursor CLI authentication](https://cursor.com/docs/cli/reference/authentication)
- S09: [Cursor headless CLI](https://cursor.com/docs/cli/headless)
- S10: [Cursor CLI output schema](https://cursor.com/docs/cli/reference/output-format)
- S11: [Cursor CLI use and session history](https://cursor.com/docs/cli/using)
- S12: [Cursor Agent overview: steering and checkpoints](https://cursor.com/docs/agent/overview)
- S13: [Cursor Cloud Agents API: separate hosted route](https://cursor.com/docs/cloud-agent/api/endpoints)
- S14: [Gemini CLI headless mode](https://geminicli.com/docs/cli/headless/)
- S15: [Gemini CLI ACP mode](https://geminicli.com/docs/cli/acp-mode/)
- S16: [Gemini CLI session management and retention](https://geminicli.com/docs/cli/session-management/)
- S17: [Gemini CLI authentication](https://geminicli.com/docs/get-started/authentication/)
- S18: [Gemini CLI checkpointing](https://geminicli.com/docs/cli/checkpointing/)
- S19: [Grok Build headless/ACP](https://docs.x.ai/build/cli/headless-scripting)
- S20: [Grok Build CLI reference](https://docs.x.ai/build/cli/reference)
- S21: [Grok Build keyboard controls](https://docs.x.ai/build/keyboard-shortcuts)
- S22: [Grok Build enterprise authentication](https://docs.x.ai/build/enterprise)
- S23: [Grok Build status-line accounting](https://docs.x.ai/build/features/status-line)
- S24: [Hermes programmatic integration, mutable documentation](https://hermes-agent.nousresearch.com/docs/developer-guide/programmatic-integration/)
- S25: [Hermes ACP internals, mutable documentation](https://hermes-agent.nousresearch.com/docs/developer-guide/acp-internals)
- S26: [Hermes API server caller authentication](https://hermes-agent.nousresearch.com/docs/user-guide/features/api-server)
- S27: [OpenCode server API](https://opencode.ai/docs/server/)
- S28: [OpenCode CLI and auth](https://opencode.ai/docs/cli/)
- S29: [Antigravity headless control, counters and permissions](https://antigravity.google/docs/cli/headless/)
- S30: [Antigravity authentication](https://www.antigravity.google/docs/cli/install/)
- S31: [Pi RPC lifecycle; immutable commit 7fbbd5f4a1d982bb02d63472dde0774fa639f99b](https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/docs/rpc.md)
- S32: [Pi RPC commands, compaction and accounting; same immutable commit](https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/docs/rpc-commands.md)
- S33: [Pi provider authentication; same immutable commit](https://raw.githubusercontent.com/earendil-works/pi/7fbbd5f4a1d982bb02d63472dde0774fa639f99b/packages/coding-agent/docs/providers.md)
- S34: [Hermes programmatic integration; immutable commit 5bba024d8ddd388f56f354c1f789be825e3d8a3c](https://raw.githubusercontent.com/NousResearch/hermes-agent/5bba024d8ddd388f56f354c1f789be825e3d8a3c/website/docs/developer-guide/programmatic-integration.md)
- S35: [Hermes ACP internals; same immutable commit](https://raw.githubusercontent.com/NousResearch/hermes-agent/5bba024d8ddd388f56f354c1f789be825e3d8a3c/website/docs/developer-guide/acp-internals.md)
- S36: [Grok Build changelog: version 0.2.97](https://x.ai/build/changelog) (Read through web research; direct byte capture unavailable.)
- S37: [OpenCode generated message types; immutable commit 1ddb0873aee50d209d1a8d7f91b89c5daf692d49](https://raw.githubusercontent.com/anomalyco/opencode/1ddb0873aee50d209d1a8d7f91b89c5daf692d49/packages/sdk/js/src/gen/types.gen.ts)
- S38: [Cursor ACP lifecycle and permission requests](https://cursor.com/docs/cli/acp)
- S39: [Gemini CLI cheatsheet: version-sensitive flags](https://geminicli.com/docs/cli/cli-reference/)
- S40: [Grok Build modes and session commands](https://docs.x.ai/build/modes-and-commands)

- S41: [Cursor TypeScript SDK: local/cloud control, steering, resume, usage and caveats](https://cursor.com/docs/sdk/typescript)
- S42: [Cursor Python SDK: caller-key authentication and programmatic surface](https://prod.cursor.com/docs/sdk/python)
- S43: [Gemini CLI experimental interactive model steering](https://geminicli.com/docs/cli/model-steering/)

- S44: [Antigravity Python SDK overview, API-key and Vertex paths](https://antigravity.google/docs/sdk/overview/)
- S45: [Antigravity SDK lifecycle, usage and session persistence](https://antigravity.google/docs/sdk/lifecycle)
- S46: [Managed Antigravity agent through Gemini Interactions API](https://ai.google.dev/gemini-api/docs/antigravity-agent)
