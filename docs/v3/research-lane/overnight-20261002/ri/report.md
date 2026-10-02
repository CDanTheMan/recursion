# R-I: Grok Build source study

Decision evidence pack • 2026-10-02 • Static public-source research only

## 0. Executive result and basis

**The strongest reuse candidates are explicit input-disposition, actor/transport separation, scoped child presentation, and declarative extension discovery patterns. This study does not validate a reusable crate, cheap port, language choice, or Grok route.** The concrete adoption alternatives and rejection criteria are in §15; the tests that could discriminate them are in §16 and `local-test-handoffs.json`.

Three findings change the starting brief:

1. **D:** the [dashboard guide](#grok-dashboard-guide-facts) and [state implementation](#grok-dashboard-state-facts) distinguish the current topology from legacy row identities. Use that version-bound evidence rather than describing an unqualified nested child tree.
2. **D:** the [interjection fact note](#grok-interjection-facts) separates an optimistic response from subsequent admission/delivery. The source evidence does not establish model adoption.
3. **D/O:** the [provenance findings](#grok-provenance-facts) bound source transparency; the public tree alone cannot establish complete release provenance or platform qualification.

### Pin and observation scope

- **O:** Public `main` resolved on 2026-10-02 to `2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8`, commit date 2026-09-29, Git tree `d7f2fa79787169d549eee97c8c2dbf9fbe3a43d3`. The old `72a61251fcffb464bcc687aeb5a998e5a98ec0c9` pin is historical and is not substituted for this study. [GB-PIN] [GB-TREE]
- **O:** All 4,487 archived file blobs matched the Git blob identities in the independently fetched, non-truncated recursive tree. Archive SHA-256: `5c536ade62ca11f7ef3f5ef4f113799e8b1fa63a3df9efbc9dad1c5f0404584d`. This verifies retrieved bytes against GitHub's tree, not a signed author identity, reproducible build, malicious-content absence, or installed binary.
- **D:** `SOURCE_REV` records internal monorepo revision `559751fdcec02d413e4c57c8832ab275e4f44980`. **U:** Its unpublished tree and correspondence to any distributed binary were not independently verified. [GB-SOURCE-REV]
- **O:** Manifest parsing found 107 workspace members and 1,357 locked packages: 107 path/workspace packages, 1,246 registry packages with checksums, and four Git packages at two resolved revisions. `workspace-inventory.json` includes every member, description when declared, license, features, direct/build/dev/target dependencies and pinned manifest URL. `dependency-lock-ledger.json` preserves all lock entries as metadata, not dependency source bodies.

Labels throughout: **D**, source-documented from pinned code or dated primary documentation; **O**, locally observed byte identity or static parsing; **I**, inference or proposed Recursion contract; **U**, unknown or unmeasured. A test definition in source is D, never a local test pass. “Reusable pattern” is an I-class candidate abstraction, not a claim that the original crate is safe or directly portable. Unreviewed crate reuse remains U.

The authoritative Recursion input is commit `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`, including CONTROL_PLANE, ANCHOR, D-017–D-033, the current goal, PRODUCT, INTERFACE-STRATEGY, PLUGINS-AND-EDITIONS, research coverage/gaps/synthesis and this lane's directive. R-G's current draft is used only for contract alignment, not as ratified implementation. Native-loop ownership, comprehensive build/lean opt-in release, first Codex App Server qualification, D-022 Stop vocabulary, D-028 floors, D-029 trusted launch and D-033's unmeasured porting hypothesis remain intact. No source, decision, route, account, installed system or configuration was changed.

## 1. R-I-Q01: Workspace and ownership map

<a id="grok-workspace-facts"></a>

All path-based source rows below are at the fresh Grok commit; each row separates the D ownership observation from its I/U reuse assessment. This is a component map, not a complete dynamic call graph.

| Component / owning crate(s) | Source-documented boundary and key dependencies | Pattern classification and limit |
|---|---|---|
| <a id="ri-01-01"></a>Composition root: `xai-grok-pager-bin` | D: executable assembles pager and shell entrypoints; `main` constructs a multithread Tokio runtime; allocator/release features are conditional. [GB-BIN] [GB-MANIFEST] | I: reusable composition-root pattern; Grok-specific startup, login/update and product wiring should remain adapter-local |
| <a id="ri-01-02"></a>TUI: `xai-grok-pager`, render/minimal/diff/PTY-harness crates, `xai-ratatui-*` | D: app state, actions, effects, views and terminal rendering are separately organized; manifests name ratatui/crossterm/terminal helpers. [GB-ROOT] [GB-MANIFEST] [GB-PAGER-EFFECTS] | I: reusable state/action/effect/view split; U: direct renderer portability and accessibility |
| <a id="ri-01-03"></a>Agent definition: `xai-grok-agent` | D: definition parsing, builder, tools, prompt assembly, reminders and compaction policy. It is not by itself the owning conversation loop. [GB-AGENT] | I: reusable descriptor/builder split; Grok-specific prompt templates, toolset presets and policy defaults |
| <a id="ri-01-04"></a>Active loop: `xai-grok-shell` | D: `SessionActor`, `run_session`, conversation-turn processing, command queues, sampling/tool handling; `MvpAgent` dispatches ACP. [GB-SESSION] [GB-LOOP] [GB-TURN] [GB-ACP] | I: reusable session actor abstraction; porting entire loop would import large product/telemetry/auth policy closure |
| <a id="ri-01-05"></a>ACP transport: `xai-acp-lib`, shell agent and leader modules | D: typed ACP gateway and agent implementations; `agent-client-protocol` is declared 0.10.4 with unstable features. [GB-MANIFEST] [GB-ACP] | I: portable protocol pattern; Grok extensions require an exact adapter; U: stable public ABI |
| <a id="ri-01-06"></a>Conversation state and compaction: `xai-chat-state`, `xai-grok-compaction`, `xai-compaction-transcript`, shell session storage | D: distinct workspace members; session log/replay and compaction checkpoints described in guide. [GB-MANIFEST] [GB-SESSION] [GB-SESSIONS] | I: reusable state/projection/checkpoint separation; U: Recursion canonical replay/authority preservation |
| <a id="ri-01-07"></a>Sampling: `xai-grok-sampler`, sampling-types, models and proxy types | D: sampling types/backend closure separate from session and tool crates; manifests include async-openai, HTTP/TLS and protocol dependencies. [GB-MANIFEST] [GB-SESSION] | I: generic typed sampling seam; Grok-specific endpoint/auth/model policies are not neutral defaults |
| <a id="ri-01-08"></a>Tools: `xai-grok-tools`, tools-api; common tool types/protocol/runtime | D: tool implementations and typed invocation layer; explicit Codex/OpenCode source-port notices. [GB-ROOT] [GB-MANIFEST] [GB-TOOLS-NOTICE] | I: narrow reviewed tool semantics are port candidates; U: behavioral equivalence, rights closure and cost |
| <a id="ri-01-09"></a>Processes and terminals: `xai-grok-shell-terminal`, `ptyctl`, tty-utils | D: local, ACP and PTY runner variants; output recorder, background registry and exit watcher. [GB-TERMINAL] [GB-PIPE] [GB-PTY] | I: reusable runner/output identity pattern; OS and effect settlement remain separate |
| <a id="ri-01-10"></a>Workspace: workspace/client/daemon/types, fast-worktree and Git helpers | D: filesystem/VCS/execution/checkpoint closure; worktree extension invokes create/apply/remove/resume/rehydrate functions. [GB-ROOT] [GB-MANIFEST] [GB-WORKTREE] | I: useful workspace-process separation; U: complete sandbox or cross-machine snapshot semantics |
| <a id="ri-01-11"></a>Extensions: hooks, plugin-marketplace, agent discovery and subagent-resolution | D: metadata/plugin registry, hook execution and resolution are distinct modules. [GB-PLUGIN-MANIFEST] [GB-DISCOVERY] [GB-HOOK-DISPATCH] | I: declarative inventory useful; permission and lifecycle translation mandatory |
| <a id="ri-01-12"></a>Dashboard persistence: dashboard-store, active-sessions, session-events/search | D: named storage/session crates and stable session-keyed row state. [GB-MANIFEST] [GB-DASH-STATE] | I: session identity separate from view slot; U: replicated canonical authority |
| <a id="ri-01-13"></a>Auth, login, secrets, cloud config, telemetry, update | D: dedicated product crates are in the workspace. [GB-MANIFEST] [GB-BIN] | Grok-specific; I: avoid importing as neutral core; no actual auth data was read |
| <a id="ri-01-14"></a>Mermaid/layout/font assets | D: first-party mermaid wrapper plus four in-tree upstream crates and font license. [GB-VENDOR] [GB-MERMAID] [GB-FONT] | I: isolated rendering is a candidate; U: safe parsing of hostile output and total license closure |
| <a id="ri-01-15"></a>Remaining workspace members | D: exact names/dependency declarations in machine inventory, including build/proto and common utility leaves. [GB-MANIFEST] | U: semantic reuse until individual implementation review; a generic crate name is not portability evidence |

**I:** Crate granularity is evidence of modular organization, not a minimal dependency closure. A narrow vendoring decision needs an actual selected feature/target graph, build-script and native-library inventory, an independently reviewed API and fixtures. Merely depending on `xai-grok-agent` imports tools/hooks/config/telemetry dependencies; its small public type surface is not proof of small runtime or build cost.

## 2. R-I-Q02: Runtime, channels and cancellation

<a id="grok-runtime-facts"></a>

**D:** The binary's outer runtime is multithreaded. Session bring-up has a dedicated OS-thread path, an 8 MiB configured stack, a current-thread Tokio runtime with a bounded blocking pool, and `LocalSet`. Both top-level agent operations and subagent code call that path. `SessionActor` receives typed commands, emits client updates through a gateway, and uses mpsc, oneshot, locks and task handles. Its spawn code creates several unbounded channels, including command, question, session-event and sampling-event channels. These are concrete implementation facts, not a claim that every historical/leader path has identical scheduling. [GB-BIN] [GB-SPAWN] [GB-SESSION]

**D:** The session loop dispatches commands and timer arms, uses local tasks, explicit cancellation tokens, abort-on-drop handles and a bounded deferred-start join. Cancellation aborts running turn tasks, cancels sampling/compaction and handles foreground terminals/children according to options. Distinct queues and wake barriers protect some stale-turn races; the code names turn epochs and prompt IDs. [GB-LOOP] [GB-CANCEL]

**I, reusable patterns:** separate actor ownership from transport; correlate completions to exact turn/epoch; keep control responsiveness independent of long-running tool work; restore drained inputs when cancellation interrupts preparation; make teardown waits bounded; cap blocking pools separately from async task counts. **U:** scheduling fairness, maximum queue growth, leak freedom, race freedom and responsiveness under real load. An unbounded channel is a reason to measure/admit capacity, not proof of a present denial of service.

**I, Grok-specific:** default timers, inference-based auxiliary work, retries/model policies, telemetry/feedback uploads, remote feature configuration and product wake behavior are not Recursion defaults. Native core boot and upstream-only operation must not silently start helper inference by importing those paths. R1/R2/R10 and T01/T03/T10 discriminate reuse from a native implementation; no runtime is selected.

## 3. R-I-Q03: Turns, streams, questions, permissions, compaction and resume

<a id="grok-session-surfaces"></a>

| Surface | What the inspected source establishes | Portability and honest limitation |
|---|---|---|
| Turn | D: ACP `prompt` enters session command/delivery machinery; turn result/completion carries prompt/turn correlation; cancel is a separate operation. [GB-ACP] [GB-TURN] | I: map canonical operation, attempt, session and turn separately; do not use transport request ID as all four |
| Stream | D: ACP notifications include user/assistant/tool updates; session has replay/buffering and persistence machinery; `updates.jsonl` drives conversation restore. [GB-SESSION] [GB-SESSIONS] | I: portable event/projection pattern; U: externally stable ordering, reconnect cursor coverage and every crash window |
| Permission | D: workspace permission layer and ACP request-permission support are wired into session construction. [GB-PERMISSION] [GB-SPAWN] | I: map exact request/tool/session and grant scope; permission presentation does not issue Recursion authority |
| Questions | D: `x.ai/ask_user_question` data carries session ID, tool-call ID, question set, default/plan mode; response union includes accepted, chat-about-this, skip-interview and cancelled paths. [GB-QUESTION] | Grok-specific wire union; I: preserve outcome/partial answers rather than collapse to yes/no; U: fully durable pending-question lifecycle |
| Interjection | D: [canonical facts](#grok-interjection-facts) | I: reusable disposition/state machine; specific `x.ai/*` API remains adapter-bound |
| Queue edits | D: extension notifications parse remove/reorder/clear/edit/interject/hold-edit/release-edit; owner/client attribution and versioned/idempotent commands appear in parser and queue implementation. [GB-QUEUE-PARSE] [GB-QUEUE] | I: maintain canonical edit operation and observe authoritative queue-change outcome; sending a notification has no response proof |
| Compaction | D: explicit `x.ai/compact_conversation*` dispatch and persisted compaction checkpoints; manual and automatic compaction documented. [GB-ACP] [GB-SESSIONS] | I: preserve original evidence, context transformation and accounting; U: semantic sufficiency or quota benefit |
| Resume / fork | D: ACP new/load/list/resume/close methods; namespaced state/import/history/fork/rehydrate operations; disk log and parent lineage metadata. [GB-ACP] [GB-ADMIN] [GB-SESSIONS] | I: retain origin/profile/source/workspace bindings; U: all-process, cross-host or authority-equivalent continuation |
| Service/account extensions | D: billing, auth, cloud environment, sharing and privacy methods share the dispatch namespace. [GB-ACP] | Grok-specific; I: do not expose by wildcard forwarding or infer permission from namespace membership |

**I:** A Recursion adapter must publish an allowlisted, version-bound subset of this surface. `x.ai/*` denotes product extensions, not ACP-standard behavior. SDK dependency version, source commit, runtime binary, negotiated capability and route qualification are different identifiers. A newer schema alone cannot upgrade a qualified profile. In particular, because queue edits are notifications, the canonical input ledger needs subsequent revision/outcome observation or an explicit uncertainty disposition; retry cannot blindly assume a lost edit was never applied.

## 4. R-I-Q04: Process/effect and conversation continuity

<a id="grok-continuity-facts"></a>

**D:** The terminal crate exposes local, ACP and PTY backends with terminal IDs, status, cwd, output offset, exit code and separate create/input/resize/output/wait/kill/release functions. Streaming local execution includes output recording and background-task tracking. Unix and Windows code paths differ; inspected Windows piped setup uses process-wrap creation flags, JobObject and KillOnDrop, while PTY code explicitly distinguishes Unix foreground-process-group inspection from ConPTY limitations. [GB-TERMINAL] [GB-PIPE] [GB-PTY]

**D:** Send-now is a special turn cancellation: it preserves background work/children; foreground handling differs from ordinary stop. The source comments even name a narrow spawn-versus-abort race. Bounded reap avoids hanging forever on a process stuck in kernel I/O. These admissions are useful prior art for explicit uncertainty, not evidence that escaped descendants are impossible. [GB-CANCEL] [GB-PIPE]

**D:** Worktree extension code has typed create/create-from-worktree/apply/remove/list/GC/status and session resume/rehydrate operations, with progress notifications and asynchronous creation. **I:** the presence of an apply operation is a separate mutation boundary, not automatic permission to merge. **U:** complete capture of dirty index, untracked/ignored files, symlinks, submodules, filesystem case/line-ending behavior and concurrent mutation across Recursion floors. [GB-WORKTREE]

<a id="grok-sessions-facts"></a>
**D — session guide:** `/rewind` changes history while leaving files unchanged; forks can request or decline a worktree. `/exit` retains history; `/delete` removes it. [GB-SESSIONS] **I:** conversation lineage, checkout isolation and all-world recovery are separate claims.

**I:** Recursion should retain at least four separate facts: conversation position; workspace/source identity; process/terminal lifetime; external-effect settlement. A copied transcript must not assert the same files or a terminated tool; a closed view must not settle a process; a killed process must not claim external rollback. D-022's Aggressive / Full / Lazy plus checkpoint / interrupt / drain remain canonical. Mapping any Grok stop requires effect-specific scope and receipts; the mode names cannot be inferred from an upstream cancel boolean. T04/T05/T09 are the handoff.

## 5. R-I-Q05: Dashboard and the ranking claim

<a id="grok-dashboard-guide-facts"></a>
**D — dashboard guide:** rows are local top-level sessions and forks, not subagents; child activity stays under parents. The dashboard supports selected-agent peek/reply, retained history, worktree-enabled dispatch and visible new-agent destination/mode. Busy replies normally queue; pending questions/permissions have separate choices. New-agent dispatch and selected-agent reply differ. Esc returns from detail; `/exit` retains history; the guide describes confirmed deletion as permanent. Navigation, grouping, attention states and background activity are documented. These are guide claims at the fresh pin; the source-specific archive branch below limits any universal deletion claim. [GB-DASHBOARD]

<a id="grok-dashboard-state-facts"></a>

**D:** The dashboard's local top-level/fork rows can be grouped by state or directory, pinned/reordered by stable session ID, renamed, peeked, attached and stopped. Needs-input/working/idle/inactive/completed/failed distinctions avoid making quietness mean completion. Background tasks/monitors/loops can retain a working indication after a foreground turn ends. Inactive roster entries from other pager processes start collapsed; session picker/history and agent-definition modal are separate surfaces. [GB-DASH-ROW] [GB-DASH-STATE] [GB-DASH-ACTIVITY]

**D — state/source refinement:** parent activity and child-count badges are separate; child transcripts use tasks/dock/framed views. The state parser discards legacy `sub:` row keys [GB-DASH-ACTIVITY, GB-DASH-STATE, GB-SUBAGENTS]. The [guide topology](#grok-dashboard-guide-facts) and source implementation must not be merged with older versions.

**D:** The location header and worktree toggle describe the next new agent's destination. Dispatch and peek reply have different targets. Search mode is explicitly entered rather than interpreting arbitrary prompt text as a filter. Navigation key meaning depends on list/input focus and whether the draft is empty. Peek displays recent response type/time, a bounded preview, model/approval-mode information and an agent-specific reply composer. Questions/permissions replace reply text with options; the peek stores the permission request ID to reject stale answers, while full-view handling remains distinct. [GB-DASH-PEEK] [GB-DASH-SEARCH] [GB-DASH-DISPATCH]

**I:** These are credible hypotheses for lower target confusion and interruption cost: a visible destination, stable row ordering, distinct new-agent versus selected-agent composer, a recent-output peek, and task-state cues. **U:** “Best-in-class” is not an established ranking. No timed usability study, competitor-matched task trial, error-rate measurement, assistive-technology trial or terminal-accessibility certification was performed. Source comments and demo polish cannot supply that evidence. T06 compares these patterns against a conventional flat session list without selecting a toolkit.

## 6. R-I-Q06: Five different input operations

<a id="grok-input-operations"></a>

<a id="grok-keyboard-facts"></a>
**D — keyboard guide:** nonempty Enter during work normally queues a follow-up; the default is `follow_up_behavior=queue`. Configured steering promotes input at a safe gap. Send-now cancels the current turn and submits a new prompt while other queued/background work can survive. During blocked waits, plain Enter can instead cancel that blocked turn and run the new message next, without necessarily draining already-held follow-ups. Key meanings depend on focus, draft, state and terminal; send-now chords can be remapped. [GB-KEYS]


| Operation | D: implementation/documentation | I: disposition Recursion must preserve |
|---|---|---|
| <a id="ri-06-01"></a>Normal queue | See [keyboard facts](#grok-keyboard-facts); source queue rows may be held during blocked background/subagent waits [GB-QUEUE] | Accepted for later execution, not delivered to active turn |
| <a id="ri-06-02"></a>Configurable steer | D: [canonical facts](#grok-interjection-facts) | Accepted → queued → injected at a known boundary; adoption remains unverified |
| <a id="ri-06-03"></a>Send now | See [keyboard facts](#grok-keyboard-facts) and source-specific cancellation paths [GB-CANCEL, GB-PAGER-PROMPT] | Two linked operations, interrupt plus next-turn submission, not active steering |
| <a id="ri-06-04"></a>Peek reply | D: [canonical facts](#grok-dispatch-lifecycle-facts) | Target/session and intended mode must be explicit; a UI row selection is not authority |
| <a id="ri-06-05"></a>Queue edit | Source has remove/reorder/edit/hold/release and queue interject operations; optimistic UI and authoritative queue paths coexist. [GB-QUEUE-PARSE] [GB-PAGER-QUEUE] | Edit/retract is race-sensitive until acknowledged by state; accepted edit is not proof original input was never consumed |

**I:** the [keyboard exceptions](#grok-keyboard-facts) must remain explicit in the disposition map; a generic busy-state rule is insufficient.

<a id="grok-interjection-facts"></a>
**D:** `x.ai/interject` itself is a mid-turn buffer path, whereas user-facing send-now can go through prompt/cancel orchestration and older-shell fallback paths. Method names and UI action enums contain historical “interject” terminology; do not infer identical semantics from that spelling. The wire handler returns `status: queued` after a channel-send attempt whose result is discarded; optimistic UI echo is separate from actor admission and delivery. Safe-point drain uses a restore-on-cancel guard, prepares messages, submits a batch to chat state, then persists; on actor submission failure it returns without falsely consuming the buffer. A final missed drain can create a hidden fallback prompt in order. [GB-INTERJECT] [GB-DRAIN] [GB-PAGER-INTERJECT] [GB-PAGER-EFFECTS]

**I, R2:** Canonical input record: stable message/operation ID, immutable content digest and revision, principal, exact target session/turn/epoch, requested disposition, effective disposition, accepted evidence, delivered boundary, supersedes/retract relation, unresolved/fallback reason and accounting lineage. UI states may be accepted, pending, injected, reclaimed, replaced, failed or uncertain; model “adoption” must stay a separately attributed statement, never inferred from a successful RPC. T01/T02/T03 specify falsification races.

## 7. R-I-Q07: Worktree dispatch and cross-harness comparison

<a id="muse-interactive-facts"></a>
**D — Muse interactive:** Enter steers at the next step; Alt+Enter queues. Empty-composer Esc can reclaim the newest eligible queued instruction. Interruption ends the turn without necessarily stopping background terminals/subagents. Session commands, side conversation, tasks, question/workflow monitoring, command palette are documented. A conversation fork preserves the source session; workspace equivalence remains unverified. [MUSE-INTERACTIVE]


**D/source:** dispatch has separate launch-only and launch-and-attach actions; shell creation progress is distinct from final results [GB-DASH-DISPATCH, GB-WORKTREE]. The [guide](#grok-dashboard-guide-facts) supplies the visible worktree/destination premise. **I:** until creation and launch both succeed, display partial progress rather than an already isolated agent.

<a id="grok-dispatch-lifecycle-facts"></a>
**D — dispatch source:** `dispatch_dashboard_overlay_exit` returns no effects. Peek binds the selected row and rejects absent/unloaded sessions. With `workspace_dashboard_enabled`, eligible confirmed rows call `archive_dashboard_row`, request membership removal using `RemovalCause::Archive`, and close local views; busy rows must stop first. Legacy/local confirmation can emit `DeleteSession`. [GB-DASH-DISPATCH] (lines 483–565, 1767–1842, 2019–2131)

**U/I:** effective feature selection and every storage consequence were not run or fully traced. Compare the [guide claims](#grok-dashboard-guide-facts) and [session commands](#grok-sessions-facts); view close, stop, archive and history deletion remain distinct. Ctrl+X is not universally permanent deletion at this pin.

All comparator docs were re-opened on 2026-10-02. OpenCode V2 documentation is date-pinned only; no installed binary was identified. V1 v1.18.34 resolved to `aec0b9a6d8898f68f923aaf08b7306d931fd9d76`; inspected facade/source files are pinned, but absent cells are not negative capability claims. Muse's official SDK schema is pinned at `bb44be3d36de46d2411bd9eaa4aee99006092546`, while interactive docs are mutable. [opencode-session-prompt.ts] [opencode-acp-agent.ts] [muse-code-sdk-msp-msp.d.ts]

| Behavior | Grok current pin | Meta Muse Code | OpenCode V1 inspected profile | OpenCode V2 dated docs |
|---|---|---|---|---|
| <a id="ri-07-01"></a>Active steer / next-turn queue | D: [Grok evidence](#grok-keyboard-facts) | D: [canonical facts](#muse-interactive-facts) | U: distinct active-steer/queue external contract not established by reviewed V1 facade and prompt service; T07 | D: [canonical facts](../rj/report.md#opencode-v2-tui-facts) |
| <a id="ri-07-02"></a>Admission meaning | D: [Grok evidence](#grok-interjection-facts) | D: SDK command ack is admission only; turn terminal is separate [muse-code-sdk-msp-msp.d.ts] | D: prompt/loop/cancel services exist; U: same disposition semantics | D: [canonical facts](../rf/report.md#opencode-v2-facts) |
| <a id="ri-07-03"></a>Retract / pending cancel | D: [Grok evidence](#grok-input-operations) | D: [canonical facts](#muse-interactive-facts), [canonical facts](../rk/report.md#muse-lifecycle-facts) | U: equivalent durable reclaim guarantee in inspected subset | D: [canonical facts](../rf/report.md#opencode-v2-facts) |
| <a id="ri-07-04"></a>Interrupt scope | D: [Grok evidence](#grok-continuity-facts) | D: [canonical facts](../rk/report.md#muse-lifecycle-facts) | D: explicit cancel API; U: descendant/external settlement | D: [canonical facts](../rf/report.md#opencode-v2-facts) |
| <a id="ri-07-05"></a>Fork semantics | D: [Grok evidence](#grok-sessions-facts) | D: SDK has session/turn identities and fork interface; U: Recursion workspace/authority equivalence | D: ACP facade exposes unstable-named fork; U: projected-history equivalence and filesystem isolation | D: [canonical facts](../rf/report.md#opencode-v2-facts) |
| <a id="ri-07-06"></a>Worktree dashboard dispatch | D: [Grok evidence](#grok-dashboard-guide-facts) | U: identical dashboard workflow not established by reviewed interactive sources | U: same flow not established | D: [canonical facts](../rf/report.md#opencode-v2-facts); U: identical Grok dispatch flow [OC-API] |
| <a id="ri-07-07"></a>Close view versus delete | D: [Grok evidence](#grok-dispatch-lifecycle-facts) | U: exact parity in reviewed subset | D: [canonical facts](../rj/report.md#opencode-v1-tui-facts); U: identical close semantics [OC-V1-TUI] | D: tab close/reopen and session delete are distinct keybind commands; U: all runtime lifecycle implications [OC-V2-KEYS] |
| <a id="ri-07-08"></a>Reconnect / evidence | D: [Grok evidence](#grok-session-surfaces) | D: SDK explicit lifecycle; U: target binary conformance | U: complete tested recovery | D: [canonical facts](../rf/report.md#opencode-v2-facts) |

**I:** A shared Recursion UI should advertise effective semantics from exact profile capabilities, not render four “Send” buttons identically. V2 claims must not be backported onto V1, and an SDK schema must not certify a proprietary host. T07's provider-free scripted trace comparison can establish mapping behavior; real adoption by a model remains outside that fixture.

## 8. R-I-Q08: Extension contributions and lifecycle

| Surface | D: declaration / discovery / lifecycle | Permission implication and classification |
|---|---|---|
| <a id="ri-08-01"></a>Agents | Markdown/frontmatter plus tools/model/permission-related fields; project/user/bundled/plugin discovery; plugin namespace qualification and ambiguous-name refusal. [GB-DISCOVERY] [GB-SUBAGENTS] | I: portable instruction/tool-declaration pattern; semantic host mapping required; definition is not a grant |
| <a id="ri-08-02"></a>Personas / roles | TOML instruction overlays, input/output hints, model/effort and isolation defaults; inline config beats files; resolved at child spawn. [GB-SUBAGENTS] | I: model/effort/isolation fields are operational choices, not merely tone. Introductory persona prose must not erase the documented override fields |
| <a id="ri-08-03"></a>Subagents | Spawn/resume/stop and bounded type selection; context/MCP inheritance and worktree options; plugin agents cannot declare MCP servers or bypass-permission mode. [GB-SUBAGENTS] | I: parent-child lineage useful; shared connected MCP does not prove attenuated credentials, billing or egress |
| <a id="ri-08-04"></a>Skills / commands | SKILL.md and legacy command Markdown; name/description, invocation flags, allowed-tools, model/effort and metadata; multiple roots, override precedence and reload; .gitignore is not a skill-exclusion policy. [GB-SKILLS] | I: inert content plus explicit invocation flags maps well; model overrides and helper scripts require admission; arbitrary prose is untrusted |
| <a id="ri-08-05"></a>MCP | Configured stdio, HTTP/SSE and streamable HTTP; project/plugin sources, runtime toggles and tool discovery; policy allow/deny gates exist. [GB-MCP] [GB-PLUGINS] | I: useful protocol realization; transport/auth/version/tools must be profiled separately; server access is not inherited authority |
| <a id="ri-08-06"></a>Plugins | Optional root manifest with fallback locations; convention-based skills/commands/agents/hooks/MCP/LSP; install, enable, trust, reload/update states; component containment checks. [GB-PLUGIN-MANIFEST] [GB-PLUGINS] | I: static descriptor candidate; unknown manifest fields are silently ignored upstream, which cannot establish required-field preservation |
| <a id="ri-08-07"></a>Hooks | Config/plugin/local command or HTTP handlers, event matching, sequential gates, timeout and output interpretation. Lifecycle events cover prompts, tools, stop/children and session transitions. [GB-HOOK-EVENTS] [GB-HOOK-RUNNER] [GB-HOOKS] | I: extension callbacks only; fail-open behavior is unsuitable as sole authority boundary |
| <a id="ri-08-08"></a>LSP declaration | Plugin manifest/docs include `.lsp.json` contribution. [GB-PLUGIN-MANIFEST] [GB-PLUGINS] | D: declaration exists; U: full runtime feature parity/reuse not studied; no executable portability inferred |

**D:** Project plugin trust is per canonical plugin-root path, not per-worktree or content digest. Untrusted plugins can expose metadata while hooks/MCP/scripts are blocked. User/session/process-supplied directories can be auto-trusted by documented discovery context. A source-pinned install policy is available, but that does not make all default trust digest-bound. [GB-PLUGIN-TRUST] [GB-PLUGINS]

**I:** These contextual trust defaults must not be copied into Recursion. An adapter receiving `pluginDirs` is not authorized to grant execution simply because it is a caller. Reload/update needs a new artifact identity, dependency closure and reviewed grants; changed bytes at the same path are not the same admitted plugin. Installed-but-disabled must satisfy Recursion's stronger inertness contract, including no import, hooks, watcher, context enumeration, background model use or update scan. Upstream “disabled” labels alone do not prove that property.

## 9. R-I-Q09: Exact R-G handoff and required translation additions

This is an **I-class extension of R-G's draft contract**, using its direct/mechanical/annotation/none vocabulary and its independent translation, availability, installation, activation and qualification axes. It does not duplicate or ratify the general schema.

| Foreign contribution | Mapping | Exact target obligation / loss record |
|---|---|---|
| Plugin name/version/description/license claim | Direct data plus mechanical namespace | Populate `identity`, provenance and dependencies from inspected bytes; missing version stays unknown; declared license is not clearance |
| Skills/commands and literal schemas | Direct content; mechanical invocation names | Contribution ID, content digest, source priority, model/user invocation flags and parameter syntax; keep non-instruction metadata separate from prompt body |
| Agent/persona prompts and model/tool presets | Annotation | Separate instruction contribution from route/model/effort/isolation requests; add `ROUTE_OVERRIDE_REQUIRES_GRANT`, `TOOLSET_TRANSLATION_LOSS`, `PERSONA_RESOLUTION_DIFFERENCE` as applicable |
| MCP config | Mechanical transport/config map plus annotation | Exact protocol revision, endpoint/process principal, tool namespace, auth audience, result schemas, resource bounds and capability loss; `UNDECLARED_EGRESS` or `CREDENTIAL_BOUNDARY_UNKNOWN` blocks required use |
| Hooks | Annotation | Event point, order, input mutation, output replacement, failure behavior and cleanup; record `FAIL_OPEN_HOOK`, never map “allow” to an AuthorityGrant |
| LSP / TUI / dashboard actions | Annotation or none | Host-specific UI realization; missing UI recorded `HOST_UI_UNAVAILABLE`; if sole approval surface, loss is required and admission fails |
| Path trust / auto-trusted pluginDirs | None as authority | Preserve as source fact only; Recursion supplies detached digest-bound AuthorityGrant and installation record |
| Timers, side inference, auto-update, subprocess helpers | Annotation | Separately admitted lifecycle effects and billing/egress; no auto-enable or silent fallback |
| Imported release/account entitlement | None | Independent RouteProfile, legal gates and operator-provisioned launch; no inference from license or source availability |

Required additions are fields/constraints in existing R-G records, not a new competing manifest:

1. `compatibility` binds Grok source commit, host executable identity when available, ACP revision, adapter digest and selected extensions. Required extension unknown means refusal.
2. `contributions[]` identifies input dispositions, safe-point semantics, question-outcome unions and all translated/lost fields. Unknown foreign fields are retained inertly; a critical unknown is not silently discarded like Grok's forward-compatible parser.
3. `attenuation` is intersected with parent/GoalSpec/current grants. Instructions, inherited MCP and role presets cannot expand it.
4. `privacy` names data classes, workspace compartments, egress recipients and retention; hooks/HTTP/telemetry need explicit data-flow treatment. Absence is unknown, not unrestricted.
5. `bounds` separates resource, model-launch, route/account, quota and spend; helper inference is attributed to its actual role and route. Upstream-only has no hidden native helper.
6. `evidence_contract` records transport acknowledgement, actor admission, delivery, effective disposition, execution result and effect settlement separately, with source receipt and uncertainty.
7. Installation/activation/reload are fenced transitions with immutable content/dependency digests and stale-epoch rejection. Source path trust is not migrated as a grant.
8. D-029's launch boundary additionally must prevent credential export via an unconstrained CLI/output, not merely deny direct file reads. A Grok-auth crate is not that boundary.

**I:** Required losses cause pre-admission incompatibility with `attempted=false, effect=none`; after any admitted effect, record failed/cancelled/uncertain/settling instead. Preserve all four accepted incompatibility responses; recommendations cannot self-install, reroute, authenticate or spend. R3/R4/R7 and T08/T09 test this handoff.

## 10. R-I-Q10: Fail-open hooks and effect admission

**D:** Hook documentation explicitly says timeout, crash, malformed output and missing required environment variables are recorded but do not block tool use. In the actual sequential gate dispatcher, `HookRunnerResult::Failed` is logged and accumulated without producing denial. Only a successfully interpreted blocking/denial path blocks the corresponding operation. This is not merely a README warning. [GB-HOOKS] [GB-HOOK-DISPATCH] [GB-HOOK-RUNNER]

**D:** Failure semantics are event-specific: stop gates may request continuation and have a bounded continuation cap; errors allow normal stopping. Prompt and post-tool gates are not interchangeable with pre-tool permission gates. A post-tool hook runs after effects and may change displayed/model-visible output, not roll the external world back. Hook notices and result provenance therefore matter. [GB-HOOKS] [GB-HOOK-EVENTS]

**I, R4:** Recursion must enforce authorization at its own admitted effect boundary, independent of successful hook execution: revalidate principal and parent attenuation, goal/config/route/plugin epoch, exact operation and arguments, workspace scope, egress, credential visibility, reservations and current Stop/revocation state immediately before launch/commit. If an advisory hook rewrites arguments, the rewritten operation requires revalidation. A post-tool output replacement must retain the original result/effect receipt and mark the transformation; it cannot turn failure into accepted success.

A hook timeout must never convert lack of authority into permission. Hook “deny” can further restrict an admitted operation but “allow” cannot enlarge a grant. Aggressive / Full / Lazy choose already-ratified cancellation/drain behavior for in-flight work; none turns an upstream process stop into external rollback. Irreversible/ambiguous effects remain in settlement/reconciliation, and new admissions stay fenced after revocation. The Grok hook named `Stop` is a turn-finalization extension point, not Recursion's entire D-022 Stop contract. T08/T09 provide failure and race cases.

## 11. R-I-Q11: License rights and obligations, without legal conclusion

<a id="grok-license-facts"></a>

**D:** The root license is Apache License 2.0 for first-party source; third-party material retains its own terms. Reading source is authorized by those published terms, but copying any selected portion requires its own provenance/notice review. [GB-LICENSE] [GB-ROOT]

**D, license-text summary:** Apache 2.0 grants copyright permissions to use, reproduce, modify and distribute the work and derivatives, and a bounded contributor patent license. Redistribution conditions include giving recipients a license copy, prominent notices of modified files, retaining applicable copyright/patent/trademark/attribution notices, and carrying applicable NOTICE attributions when a NOTICE accompanies the work. The patent grant has a patent-litigation termination condition; it is not all-patents clearance. Trademark permission is limited to customary origin description and notice reproduction. Warranty and liability are disclaimed; offering one's own additional warranty requires taking responsibility for it. [GB-LICENSE] [APACHE]

**I:** A reuse packet should record the exact copied files, upstream/derived ancestry, chosen license alternatives, modifications and retained notices; counsel determines distribution compatibility and any unresolved obligations. This report makes no compatibility, redistribution-clearance or provider-terms legal conclusion.

**D:** Tool-crate notices identify modified ports from OpenAI Codex under Apache 2.0 and OpenCode under MIT, and describe modification marking. Vendored Mermaid stack includes MIT and Apache files with further JS-ecosystem ancestry notices; font and theme materials have distinct notices. **I:** “The root says Apache” is insufficient for those boundaries. [GB-TOOLS-NOTICE] [GB-VENDOR] [GB-MERMAID-NOTICE] [GB-FONT] [GB-NOTICES]

**U/out of scope:** The source license grants no demonstrated account/subscription entitlement, route automation eligibility, paid service access, trademark endorsement, CVE clearance, warranty of correctness or fitness, or permission to reuse credentials. Service contracts and credential-reliant releases remain R-H/counsel-gated. No counsel was contacted.

## 12. R-I-Q12: Dependency security, artifacts and provenance

<a id="grok-provenance-facts"></a>

### Deterministically inspectable here

**O/D:** declared dependency edges, target/features and workspace patching remain material [GB-MANIFEST].

**O/D:** locked versions, checksums and Git resolutions are retained in the inventory. The four Git packages are async-openai/async-openai-macros at `95b52ebdedf42143083cf3d6f0e0be7c84e9c808`, and nucleo/nucleo-matcher at `5b74652e482f7c07d827f18c6d21e7540c242c69` [GB-LOCK]. No dependency was built, imported or fetched for execution.

**D:** THIRD-PARTY-NOTICES records alternatives such as MIT OR Apache elections, as well as materially different license families including MPL and libgit2's GPL/linking-exception bundle. Its release-oriented omissions are documented in the vendor index. **I:** Do not turn upstream's election or “dropped from release” assertion into a decision for Recursion's different closure. Build/dev/optional/target dependencies and copied assets need separate treatment. [GB-NOTICES] [GB-VENDOR]

**O:** Actual vendored directories are mermaid-to-svg, dagre_rust, graphlib_rust and ordered_hashmap. **D/O discrepancy:** vendor README/NOTICE additionally names nfsserve and fuser, whose directories are absent from this public tree. This is a traceability discrepancy, not proof of illicit distribution or a vulnerable binary. It demonstrates why a notice index cannot substitute for a source or binary inventory. [GB-VENDOR] [GB-VENDOR-README]

**D:** `bin/protoc` is a DotSlash descriptor with platform archive sizes and SHA-256 values, not the compiler binary [GB-PROTOC].

**D:** the README requires external build tools [GB-ROOT].

**D:** `xai-grok-tools/build.rs` embeds/searches for external binaries and can download release assets. The fd path compares a pinned archive hash. In the inspected ripgrep path, HTTPS bytes are unpacked and the executable is hashed for runtime integrity, without comparison against an independently expected archive digest. The override path hashes supplied bytes [GB-TOOLS-BUILD]. **I:** a self-computed digest detects later change, not provenance. No build/download was executed.

**D/O:** Prompt templates have explicit reversible XOR encoding with in-repository seeds and source comments saying it is obfuscation, not security. A fresh analysis-only parser decoded the three static numeric arrays and compared them byte-for-byte to their plaintext templates: all three match. This was data parsing, not importing repository code, running its test or executing instructions. The record carries lengths and full plaintext hashes without reproducing bodies. Compile-time string obfuscation is separately declared in pager code/manifests. **I:** neither proves maliciousness nor secrecy; both enlarge provenance review if opaque output is shipped. [GB-XOR] [GB-XOR-DATA] [GB-OBF]

**D:** Mermaid's in-tree layout stack is Rust source; additional ancestry notices still matter. **U:** A repository-wide proof that no other minified, encoded or generated artifact can affect a distribution was not established. Scope of the completed encoded-artifact check is exactly the three named templates; avoid global “no obfuscation” or “all artifacts verified” claims.

**D:** public source is periodically synchronized from a monorepo; external patches are not accepted [GB-ROOT, GB-CONTRIBUTING].

**D:** SECURITY names a vulnerability-reporting program [GB-SECURITY]. Target-specific build hardening flags exist [GB-CARGO-CONFIG]. **U:** their use in an actual release, response SLA, signed provenance, independent audit and security guarantees remain unestablished.

### Remaining unknowns

**U:** Target/feature-resolved release SBOM; all transitive source license expressions and election correctness; current vulnerability matching including native libraries; release signing/attestation verification; reproducible build equality; build-cache provenance; update-delivery integrity; actual binary-to-source correspondence; complete imported third-party ancestry; exploitability and supply-chain response quality. T11 closes only the chosen source-slice provenance question, T12 the approved build closure; neither is a security audit. A pinned Git SHA, package checksum, SBOM or signature cannot alone establish benign semantics.

## 13. R-I-Q13: Rust evidence for FU-01 / DS-18

<a id="grok-build-facts"></a>

**D:** the generated root manifest declares Rust 2024; platform/configuration distinguishes GNU/musl targets [GB-MANIFEST]; the checked-in toolchain is Rust 1.94.0 [GB-TOOLCHAIN]. Runtime architecture is documented in §2 [GB-SPAWN].

**D — README build guidance:** target individual crates because full-workspace builds are slow; check/test/clippy/fmt and external build tools are part of the documented source workflow. Linux build hosts and Windows binaries are documented; Windows source builds are best-effort and untested [GB-ROOT].

**I:** the concrete implementation and packaging graph establish neither comparative language ergonomics nor Recursion operating cost. The matrix below maps those existing facts to unchanged qualification obligations.

| FU-01 dimension | D evidence from this project | U / required Recursion comparison |
|---|---|---|
| Build/test ergonomics | D: [canonical evidence](#grok-build-facts) | Cold/warm wall time, reviewer labor, diagnosis time, CI reliability, clean offline closure |
| Async/concurrency | D: [runtime facts](#grok-runtime-facts) and [restore guards](#grok-interjection-facts) | Tail control latency, resource ceilings, queue overflow, cancellation correctness and deterministic replay against the common oracle |
| Linux | D: [canonical evidence](#grok-build-facts) | Kernel 6.12 primary / 6.6 compatibility, cgroup v2, ext4, process containment, pressure and abrupt-VM-reset receipts |
| Windows | D: [canonical evidence](#grok-build-facts) | Windows 11 25H2 build 26200 Home/Pro and 24H2 build 26100 Enterprise x64, NTFS, terminal families and cancellation traces |
| Distribution | D: [canonical evidence](#grok-provenance-facts) | Size/startup/memory/maintainability, binary provenance, install/update/rollback closure; no one-executable simplicity inferred |
| Reuse | D: [canonical evidence](#grok-workspace-facts) | Accepted-equivalent port versus native rewrite cost; second host binding maintenance; zero acceptable imports remains possible |

D-028 WSL2 is development/test only, with ext4 and `/mnt/c` separate mandatory cases; it cannot stand in for Windows or production Linux qualification. Canonical state remains local NTFS/ext4, not network storage. Grok's support wording does not establish any Recursion platform floor.

**I:** Carry source examples into FU-01's fixed corpus and competing-language prototypes without selecting a language, runtime, framework, store, package manager, renderer or vendor. The Grok toolchain pin differs from the existing FU-01 experiment's candidate pin; record both, do not silently replace the experiment version. Common correctness/authority/recovery floors precede resource comparison. T10/T12 give inputs/oracles; no candidate has measured winning status here.

## 14. R-I-Q14: Explicit non-establishments and bounded gaps

| Claim not established | Status | What would establish a narrower claim |
|---|---|---|
| Grok route qualification | Out of this lane's scope; U | Approved exact binary/interface/auth/account/profile, independent positive and negative route traces, authority/usage/resume/effect evidence; Codex App Server remains first priority |
| Account/subscription entitlement | Out of scope; U | Current exact account/service contract and counsel-reviewed route applicability; source license is insufficient |
| UI conformance / accessibility / best-in-class | Certification/ranking out of scope; local performance unmeasured | Declared terminal/input/assistive-tech matrix, task success/error metrics, matched baselines and independent evaluation |
| Porting cost or savings | Unmeasured, not assumed | Paired accepted-equivalent port/native rewrite with labor, maintenance, defects, loss and resource accounting per R-G |
| Security audit / CVE-free distribution | Out of scope; U | Threat model, complete selected closure, vulnerability/provenance review, hostile tests and appropriately scoped independent security assessment |
| Release source correspondence | U | Verified source-to-binary build/attestation and target/feature/native-tool closure |
| D-024 productive continuity | Unmeasured | Approved continuity journeys across harness, compaction, fork and machine loss preserving authority/evidence/accounting and outperforming declared baseline |
| Grok crate drop-in portability | U | Dependency-isolated candidate build and semantic fixtures on accepted floors; license review; second realization without widened authority |
| Complete teardown/rollback | U and generally stronger than upstream mechanisms | Effect-specific receipts and reconciliation; external rollback only where an actual compensation protocol proves it |

**I:** Dashboard construction can inform TUI-first sequencing with one shared backend/projection/command contract. The current “GUI later” instruction and D-019's built opt-in GUI release wording have a timing interpretation requiring Owner clarification at scheduling, not permission for this research to shrink release scope. This study neither schedules a GUI deferral nor substitutes UI polish for the D-024 continuity gate.

## 15. R-I-Q15: Adoption / port / avoid ledger

All recommendations are conditional **I**, source-pinned prior-art evaluations, not final component selections. Each names a real alternative, decisive falsifier and explicit non-proof. The machine version is `adoption-ledger.json`. Each recommendation refers to a behavior or boundary; no upstream code is accepted for incorporation.

| ID / proposed disposition | Competing option | Decisive falsifier | Does not prove / evidence |
|---|---|---|---|
| R1: adopt actor/transport ownership pattern in contract; reimplement against Recursion invariants | Vendor a narrow session core, or a shared-loop service design | Under common fault corpus, control starvation, stale completion or resource cost exceeds the competing accepted implementation | No Rust/Tokio selection or concurrency safety; [GB-SESSION] [GB-SPAWN], T03/T10 |
| R2: adopt explicit queue/steer/cancel-and-send dispositions; adapter translates wire details | Upstream-native presentation translated through the same complete canonical queue/steer/cancel dispositions | Any accepted trace loses/reorders/duplicates input, falsely reports consumption, or targets a successor turn | No model adoption, upstream reliability or public API stability; T01/T02. Source premise: [canonical facts](#grok-interjection-facts) |
| R3: port declarative skill/agent metadata through R-G's translation/loss contract | Keep complete Grok host as route adapter, or native equivalents | Required semantics or authority cannot be preserved, or accepted total port cost exceeds matched native rewrite | No universal importer or cheap-port claim; [GB-PLUGIN-MANIFEST] [GB-SKILLS], T08/T11 |
| R4: avoid hooks/path-trust as authorization boundary; retain advisory hooks behind kernel admission | Mediated declarative hooks versus qualified isolated hook executors under identical grants and final sink checks. Blind upstream trust is a negative control; a disabled profile retains the shipped hook capability | Rewritten input, hook failure or stale epoch can create an unauthorized effect; if advisory hook cannot be contained, omit that binding | No sandbox/security certification; [GB-HOOK-DISPATCH] [GB-PLUGIN-TRUST], T08/T09 |
| R5: adopt target-explicit peek/new-dispatch and session-keyed projection patterns | Flat list plus full-screen switching, or nested dashboard tree | Matched tasks show no benefit or more wrong-target submissions, missed approvals or inaccessible controls | No best-in-class ranking/toolkit choice; T06. Source premises: [dashboard guide](#grok-dashboard-guide-facts), [dashboard state](#grok-dashboard-state-facts) |
| R6: port worktree dispatch through separate workspace/session transactions | Enforced single-mutator checkout with isolated reader generations versus private clones under the same scope and source-fidelity contract | Partial creation misreports isolation, source provenance diverges, or concurrent effects leak between admitted workspaces | No snapshot completeness or effect rollback; [GB-WORKTREE] [GB-SESSIONS], T04/T05 |
| R7: use narrow allowlisted Grok ACP adapter for optional supported subset | Reimplement native capability, or adapt whole SDK/loop | Exact required input/question/resume/authority/accounting semantics cannot be represented or independently verified | No route/account entitlement; no replacement for native loop; [GB-ACP] [GB-QUESTION], T07/T09 |
| R8: evaluate narrow vendoring only after provenance/closure review | Native rewrite or existing independently reviewed dependency | Missing required license/provenance, unacceptable transitive/native closure or higher accepted maintenance cost | No quality/security from Apache alone; [GB-NOTICES] [GB-TOOLS-BUILD], T11/T12 |
| R9: avoid copying encoded prompt packaging as a secrecy boundary | Plain inspectable templates or independently justified asset packaging | Any claimed confidentiality depends on in-repository reversible encoding; or encoding prevents complete provenance review | No allegation of malice; no prompt-quality conclusion; [GB-XOR], T11 |
| R10: retain Grok Rust implementation as one FU-01 comparator, not selection | Other already-specified candidate implementations on same corpus | It fails a mandatory floor, or accepted alternative dominates declared tradeoff without violating floors | No language win, resource saving or delivery forecast; [GB-ROOT] [GB-TOOLCHAIN], T10/T12 |

**D-033 hypothesis only:** “Porting is cheap” is falsified for the declared candidate population if accepted-equivalent total cost exceeds native rewrite, or no clean import preserves required semantics. Counting source ports inside Grok demonstrates that ports exist; it does not reveal their cost, defect rate, licensing effort or suitability for Recursion.

## 16. Exact local handoffs and completion gate

All T01–T12 are **UNEXECUTED** proposals, not runnable command promises. No verified Recursion entrypoint currently exists for these new fixtures. The later implementer must add a reviewed provider-free harness in an explicitly authorized session, link it to the fixed oracle and obtain independent review. No target binary, repository test, package script, model or account was invoked in this study.

`local-test-handoffs.json` specifies each test's inputs, prerequisites, independent oracle, required evidence, expected pass/fail condition, stopping condition and non-proofs. `coverage.json` maps every exact question and gate to report sections. `architecture-map.json`, `input-disposition-ledger.json`, `extension-mapping.json`, `ui-comparison.json`, `licensing-provenance-ledger.json`, `adoption-ledger.json` and the full inventories are the machine appendices.

- G01: claims carry D/O/I/U and source locators; full-file source hashes and mutable-document limitations are explicit (§0, source register)
- G02: crates, async, ACP and process ownership/classification are covered (§§1–4; full inventory includes unreviewed-member unknowns)
- G03: dashboard, queue/steer/send-now, peek, worktrees and three comparison profiles are covered without inheriting stale subagent rows (§§5–7)
- G04: R-G mapping and fail-open hook boundary are explicit (§§8–10)
- G05: first-party versus third-party licenses, provenance discrepancies and no-execution dependency checks are separated; no legal conclusion (§§11–12)
- G06: Rust is only one project's evidence, with exact D-028 qualification gaps (§13)
- G07: route, entitlement, UI, cost and security non-establishments are explicit (§14)
- G08: all ten proposals have alternatives, falsifiers and non-proofs; no implementation technology or vendor selected (§15)
- G09: only research artifacts created; protected inputs unchanged by this lane; final artifact privacy/secret scan described in QA, with its scope and limitations

A covered research question is not a passed implementation gate. Independent acceptance of this report remains pending.


## Public source locators

References resolve to the complete source register. Grok paths all carry the fresh immutable pin; comparator pages are date-pinned where no executable pin exists.

[GB-ROOT]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/README.md
[GB-MANIFEST]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/Cargo.toml
[GB-LOCK]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/Cargo.lock
[GB-LICENSE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/LICENSE
[GB-NOTICES]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/THIRD-PARTY-NOTICES
[GB-VENDOR]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/third_party/NOTICE
[GB-VENDOR-README]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/third_party/README.md
[GB-SOURCE-REV]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/SOURCE_REV
[GB-SECURITY]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/SECURITY.md
[GB-CONTRIBUTING]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/CONTRIBUTING.md
[GB-TOOLCHAIN]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/rust-toolchain.toml
[GB-CARGO-CONFIG]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/.cargo/config.toml
[GB-PROTOC]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/bin/protoc
[GB-BIN]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager-bin/src/main.rs
[GB-AGENT]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-agent/src/lib.rs
[GB-SESSION]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session.rs
[GB-SPAWN]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session_impl/spawn.rs
[GB-LOOP]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session_impl/run_loop.rs
[GB-TURN]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session_impl/turn.rs
[GB-ACP]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/agent/mvp_agent/acp_agent.rs
[GB-INTERJECT]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/extensions/interject.rs
[GB-DRAIN]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session_impl/interjection.rs
[GB-CANCEL]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session_impl/cancel.rs
[GB-QUEUE-PARSE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/agent/ext_parsers.rs
[GB-QUEUE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/session/acp_session_impl/prompt_queue.rs
[GB-QUESTION]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-tools/src/implementations/grok_build/ask_user_question/types.rs
[GB-WORKTREE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/extensions/worktree.rs
[GB-ADMIN]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell/src/extensions/session_admin.rs
[GB-TERMINAL]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell-terminal/src/lib.rs
[GB-PIPE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell-terminal/src/streaming_local_terminal.rs
[GB-PTY]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-shell-terminal/src/pty_session.rs
[GB-DASHBOARD]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/23-dashboard.md
[GB-KEYS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/03-keyboard-shortcuts.md
[GB-SESSIONS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/17-sessions.md
[GB-DASH-STATE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/views/dashboard/state.rs
[GB-DASH-DISPATCH]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/app/dispatch/dashboard.rs
[GB-DASH-ACTIVITY]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/views/dashboard/row_activity.rs
[GB-PAGER-PROMPT]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/app/dispatch/prompt.rs
[GB-PAGER-INTERJECT]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/app/dispatch/interject.rs
[GB-PAGER-QUEUE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/app/dispatch/queue.rs
[GB-PAGER-EFFECTS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/app/effects/mod.rs
[GB-PLUGINS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/09-plugins.md
[GB-SKILLS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/08-skills.md
[GB-SUBAGENTS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/16-subagents.md
[GB-MCP]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/07-mcp-servers.md
[GB-HOOKS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/10-hooks.md
[GB-PLUGIN-MANIFEST]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-agent/src/plugins/manifest.rs
[GB-PLUGIN-TRUST]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-agent/src/plugins/trust.rs
[GB-DISCOVERY]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-agent/src/discovery.rs
[GB-HOOK-DISPATCH]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-hooks/src/dispatcher.rs
[GB-HOOK-RUNNER]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-hooks/src/runner/mod.rs
[GB-HOOK-EVENTS]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-hooks/src/event.rs
[GB-TOOLS-NOTICE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-tools/THIRD_PARTY_NOTICES.md
[GB-TOOLS-BUILD]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-tools/build.rs
[GB-XOR]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-agent/src/prompt/template.rs
[GB-XOR-DATA]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-agent/src/prompt/prompt_encrypted.rs
[GB-OBF]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/obf.rs
[GB-MERMAID]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/third_party/mermaid-to-svg/Cargo.toml
[GB-MERMAID-NOTICE]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/third_party/mermaid-to-svg/THIRD_PARTY_NOTICES
[GB-FONT]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-mermaid/assets/Roboto-LICENSE.txt
[GB-PERMISSION]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-workspace/src/permission/mod.rs
[OC-API]: https://opencode.ai/v2/docs/api
[OC-CLIENT]: https://opencode.ai/v2/docs/build/client/
[OC-V2-TUI]: https://opencode.ai/v2/docs/cli/tui/
[OC-V1-TUI]: https://opencode.ai/docs/tui/
[OC-V2-PLUGINS]: https://opencode.ai/v2/docs/build/plugins/
[MUSE-INTERACTIVE]: https://dev.meta.ai/docs/muse-code/interactive
[MUSE-TURNS]: https://meta-models.github.io/muse-code-sdk/next/guides/msp-concepts/sessions-and-turns/
[APACHE]: https://www.apache.org/licenses/LICENSE-2.0
[opencode-session-prompt.ts]: https://raw.githubusercontent.com/anomalyco/opencode/aec0b9a6d8898f68f923aaf08b7306d931fd9d76/packages/opencode/src/session/prompt.ts
[opencode-acp-agent.ts]: https://raw.githubusercontent.com/anomalyco/opencode/aec0b9a6d8898f68f923aaf08b7306d931fd9d76/packages/opencode/src/acp/agent.ts
[opencode-session-index.ts]: https://raw.githubusercontent.com/anomalyco/opencode/aec0b9a6d8898f68f923aaf08b7306d931fd9d76/packages/opencode/src/session/index.ts
[muse-code-sdk-msp-msp.d.ts]: https://raw.githubusercontent.com/meta-models/muse-code-sdk/bb44be3d36de46d2411bd9eaa4aee99006092546/schema/msp/msp.d.ts
[OC-V2-KEYS]: https://opencode.ai/v2/docs/cli/keybinds

[GB-DASH-PEEK]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/views/dashboard/peek.rs
[GB-DASH-ROW]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/views/dashboard/row.rs
[GB-DASH-SEARCH]: https://github.com/xai-org/grok-build/blob/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/src/views/dashboard/search.rs

[GB-PIN]: https://api.github.com/repos/xai-org/grok-build/commits/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8
[GB-TREE]: https://api.github.com/repos/xai-org/grok-build/git/trees/d7f2fa79787169d549eee97c8c2dbf9fbe3a43d3?recursive=1
