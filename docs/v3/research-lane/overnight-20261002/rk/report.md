# Terminal multiplexer and transformative TUI design candidate

R-K research report · 2026-10-02 UTC · Repository basis `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`

## Findings and decision boundary

The viable design space is a broker-owned runtime with disposable, authorized projections. The unanswered choice is how to host and render those projections, not whether a pane owns an agent. tmux, Zellij and terminal panes can host a Recursion client; none of their documented layout or session features substitutes for Recursion's authority, effect ledger, Stop scope or recovery contract.

Five findings materially affect implementation:

1. The exact M1B construction profile already specifies UTF-8 I-JSON, RFC 8785 canonicalization and a closed message union. Production framing/encoding remains an open comparison. Changing the encoding is a separately versioned decision, not a silent change to the existing oracle. `GAP` is a visible reconstruction marker and `replay-gap` a reason; neither is an additional M1B message.
2. A one-client broker trace cannot establish mutual exclusion across N clients. M1B also does not materialize a snapshot, authenticate a retention floor, allocate a physical Stop reserve or implement cursor rollover. Its `requires_reset` result records that recovery was needed, including after an accepted reset; it must not be rendered directly as current unrecovered state.
3. Current Zellij documentation explicitly describes native Windows named pipes and ConPTY. A blanket “Zellij is Linux/WSL-only” comparison is stale. The [resurrection mechanism](#zellij-resurrection-facts) does not establish the no-new-effects reattach required here. [RK-S16]
4. The [Muse lifecycle facts](#muse-lifecycle-facts) give a concrete detach counterexample. **I:** the persistent broker must own its upstream connection independently of terminal views.
5. The [ConPTY lifecycle note](#conpty-lifecycle-facts) distinguishes current accepted floors from older warnings; no return or EOF substitutes for owned-work settlement.

This report answers all 23 questions and nine completion gates. It proposes contracts and unexecuted tests, not a component selection. No language, store, framework, runtime, transport, toolkit, renderer, multiplexer, encoding or vendor is selected. It establishes no measured performance advantage, route qualification, entitlement, accessibility/UI conformance, security boundary between views or measured porting cost. No provider, model, target test, account, credential, installation, live host, counsel, publication, merge or deployment action was performed.

### Evidence and authority

**D** means source-documented, including accepted repository requirements where identified. **O** means locally observed static bytes, hashes or records, never newly observed runtime behavior. **I** means inferred design candidate. **U** means unknown/unmeasured. A source-documentation cell is not a product qualification result. All recommendations are I and map to the competing-option/falsifier/non-proof register in §24. All performance values measured for Recursion are U.

The authority basis is CONTROL_PLANE, ANCHOR, D-017–D-033, the active v3 goal, PRODUCT, PLUGINS-AND-EDITIONS, INTERFACE-STRATEGY, TERMINAL-RUNTIME, M1B-WIRE-PROFILE and PERFORMANCE-PLAN at the stated commit. Relevant research index, architecture/harness coverage, GAPS and SYNTHESIS were inspected. Older Hermes-executive, smaller-release and GUI-exclusion prose cannot reopen current decisions. G-06/G-07/G-11 Owner decisions are closed; qualification remains open. Historical FU-04 and wire records are preserved as bounded records, not rerun or promoted to profile qualification.

R-E and R-F research were read as current draft cross-lane analysis. R-E's credential-domain warning applies to raw terminal output and arbitrary CLI tools; a projection cannot make a credential-facing process safe merely by hiding its window. R-F's receipt/cancellation/accounting distinctions apply unchanged. R-I/R-J draft reports became available during synthesis and were read before completion. R-I confirms the same Grok source pin and warns that a queued interjection reply does not prove actor delivery/adoption; this reinforces Q14 without importing its runtime. R-J supplies addressed-message, room/correlation and separate terminal-versus-workflow lease semantics; Q02/Q11 preserve them. Their findings are draft integration inputs, not independent acceptance.

## R-K-Q01 Server ownership and disposable views

**D requirement; I design R01.** Maintain four explicit roles, without prescribing their process packaging:

- The canonical service owns task/actor identities, admitted commands, writer fencing, authority, effects and durable event order.
- The execution broker owns or delegates a qualified process-containment scope, upstream adapter connections, PTY/ConPTY endpoints, output draining, process epochs and exit observations. A separately provisioned trusted launcher may perform launches; the broker's ownership is logical responsibility, not permission to inherit credential access.
- The projection service derives authorized histories/snapshots and bounded per-view delivery. It has no authority to start inference, resume effects or create executives merely because a subscriber exists.
- A terminal client owns only layout, focus, draft editing, selection, scroll position, render cache and connection state. Those are recoverable view state, not an independent task database.

Opening attaches to existing task/stream identities. Splitting creates a second projection/subscription, or changes layout, without executing a “new task” command. Closing disposes client resources and releases its control lease if held. The broker retains the PTY master/ConPTY and adapter connection. Neither closing the last view nor an external multiplexer pane may close those execution endpoints. New task, fork, resume and Stop remain separate admitted commands.

Multiple actors in one view remain separate target records and contexts; multiple views of one actor share one canonical history. A room can display an R-J conversation but cannot merge task grants or budget reservations. The tmux server/client model is documented prior art, including shared session attachment; its pane/program coupling is not adopted as Recursion authority. [RK-S15]

**U:** process packaging, service installation and authenticated local attachment mechanism. F01/F02/F03/F11 must establish the lifetime invariant on each target profile before claiming it works.

## R-K-Q02 One fenced input and resize lease

**I, R02.** For each interactive target/process incarnation, define one control-lease slot. It is either unheld or has exactly one holder; there are never two active holders. Input and upstream PTY resize transfer atomically as one ownership transaction, although M1B has distinct `input_lease` and `resize_lease` fields. Many independently controlled actors may each have a holder. “One lease” does not mean one global keyboard for all work.

A holder binding includes authenticated client, target, daemon incarnation, process incarnation, lease generation and validity policy. The opaque references are resolved at the broker, not trusted because they were displayed in a pane. Per-target effect/approval authority is checked separately. A passive view may edit an unsent draft, search and scroll, but cannot send terminal input or resize the upstream PTY. It can resize its own local viewport without changing another client's terminal geometry. A passive terminal viewer can separately hold an addressed-message capability under R-J; such a message uses its own admitted command and delivery policy, never an INPUT-lease bypass.

A passive reader explicitly requests control by named action. The broker validates its control capability, arbitrates against the current holder, records transfer, invalidates the old references and returns fresh binding information. Cooperative release, an authorized explicit takeover, or expiry may transfer ownership. Focus, attach, hover, split and network reconnect alone cannot. An old client returning after sleep must revalidate and cannot replay buffered input under its old lease. Clock/expiry behavior across suspension is profile-specific and must be frozen, not inferred from wall-clock timestamps.

M1B contains no acquire/release/renew verb or cross-client lease oracle. Those operations need a separately typed control contract and a composed test, not invented fields in `m1b-broker/1`. Its per-client WELCOME/null-lease representation must map passive readers without distributing a usable holder capability. A lease reference alone is not authentication. Owner Stop uses its own authority path and cannot be denied merely because another client holds terminal input.

**Falsifying trace:** two simultaneously valid INPUT commands from distinct holders, a passive RESIZE accepted, or focus stealing control. Passing F04 proves bounded exclusion in that profile, not confidentiality or role authority.

## R-K-Q03 Cursor snapshot and replay recovery

**D M1B; I materialization R03.** Identify a cursor by stream ID, daemon incarnation, cursor unit and count; retain task identity separately across daemon replacement. Each view tracks last durably folded cursor, last acknowledged cursor, available replay floor, snapshot cursor/digest and last confirmed freshness. A byte position is never a grapheme or cell position. A global task event ID is not silently reused as a filtered view's contiguous sequence: filtered projection streams need their own stable identity and source-event bindings.

For event cursors, each EVENT advances exactly one. For byte cursors, advance by decoded payload bytes as specified, not base64 size or encoded frame size. ACK cannot move backward or acknowledge beyond delivery; it releases acknowledged pending entries and does not grant new credit. Persisting a client bookmark must not falsely imply the canonical writer committed anything new.

When requested cursor is below replay floor, WELCOME establishes the gap condition. The next same-stream message must be RESET; even ACK, CREDIT or SNAPSHOT before RESET permanently refuses that trace. After RESET, validate/install the referenced snapshot through the separately qualified materialization path, grant fresh CREDIT, then accept subsequent EVENTs. Show “history unavailable between these cursors; state reconstructed from snapshot X,” with source and evidence links. No fabricated turns, answers or successful effects fill the interval.

The frozen oracle advances current cursor from WELCOME's snapshot cursor even without snapshot bytes. Therefore a normal WELCOME/SNAPSHOT/replay sequence cannot be guessed from familiar protocols: the handshake/materialization mapping must be separately frozen and tested against the literal oracle. Receipt of WELCOME or `accepted-reset` alone is not convergence. The UI remains reconstructing until a verified snapshot plus its ordered suffix produces the independent expected state.

Missing/corrupt/unauthorized snapshots fail closed for control with a readable recovery explanation. Monotonicity applies within an incarnation; rollover never wraps a Count. The 2,147,483,647 limit particularly constrains high-rate byte streams. F05/F06 include boundary and new-incarnation mapping; version negotiation, materialization, rollover and ACK wording remain freeze blockers.

## R-K-Q04 Slow client isolation and non-droppable facts

**D requirement; I R04.** Canonical append occurs before publication into any lossy presentation queue. Commands, lease transitions, process exits, termination observations and canonical state changes are never discarded to make a renderer smooth. A client may stop receiving when out of credit and later replay durable facts; that is delayed delivery, not deletion. Repetitive live render deltas may be coalesced after their source facts are retained. Never drop an EVENT then jump an event cursor to hide the omission.

Use independently bounded framing, read pumps, subscription queues, scheduling and render queues. Application CREDIT complements, rather than replaces, transport flow control. Reserve capacity for authenticated Stop from ingress through parsing, admission, canonical writing, dispatch and receipt projection; bulk history/snapshot transfer cannot consume it. A single shared writer still needs bounded transaction sizes and fair service. PTY/adapter drains run with zero views and never wait for one client to ACK. Qualify the separate channel-service constraint in the [ConPTY facts](#conpty-lifecycle-facts).

Proposed fixture envelope: per-view unacknowledged queue ≤1 MiB and 4,096 events, outstanding grants no greater than allocated queue capacity, presentation state ≤2 MiB per admitted ordinary viewport, with global admission caps. These are experimental parameters, not ratified limits. M1B permits CREDIT fields up to 16,777,216 bytes and 65,536 events and additive grants; its oracle does not independently cap the accumulated grant total. Production outstanding-credit enforcement and overflow handling must be specified without silently changing that oracle.

On saturation, stop delivery to that client, preserve canonical facts, and use the exact reset/recovery rule if exhaustion was recorded. Do not manufacture a replay loss for locally deferred events. If durable storage itself fills or fails, stop new work admission and report persistence unavailable; finite storage cannot promise complete infinite output. Reserved control storage and out-of-space behavior require F07/F08, not an assertion that a second queue guarantees liveness.

## R-K-Q05 Detach terminal loss and zero views

**I, R01/R03/R04.** Client close, terminal crash and SSH drop remove a projection transport. They do not send upstream EOF, SIGHUP, Ctrl-C, session deletion or Stop. Host sleep changes reachability, not ownership. The UI distinguishes connection lost, actor last observed running, execution host unreachable and canonical writer unavailable. If the broker's machine is actually lost, recovery follows D-020 writer fencing and task/effect reconciliation; it is not the same as reconnecting a terminal.

At zero views the broker continues draining bounded output, retaining canonical facts, applying task budgets/deadlines and executing already-authorized work. It creates no replacement assistant and does no idle inference to maintain status. An optional task policy may stop work on an explicit condition, but that condition cannot be silently substituted for view loss.

Reattach supplies stable task/stream identity and a checkpointed cursor; it reauthenticates current read/control scope, checks incarnation and reconstructs view state. It never automatically reissues a queued effect after an ambiguous send. Unsent local text is labeled saved locally and remains distinct from accepted backend input.

F02/F03 compare process birth identity, actor ID, attempt ID, operation IDs, model/index/plugin activation counters and committed event roots before/after close and reconnect, including a real zero-view interval in later local qualification. A process may legitimately finish while detached; the expected outcome then is the same completion record, not forced liveness. A relaunched PID with a replayed transcript is a failure for the same-process reattach fixture.

The [Muse lifecycle](#muse-lifecycle-facts) and [Zellij evidence](#zellij-resurrection-facts) constrain reattachment designs; neither upstream label establishes Recursion's no-new-effects contract.

## R-K-Q06 Incremental rendering and bounded repaint

**I, R05.** The candidate commits to a non-flicker incremental/diff contract, not a selected renderer. Maintain a desired frame and a last completely emitted frame keyed by geometry, style and width-policy generation. Diff changed grapheme/cell spans, expand changes to cover both halves of wide cells and invalidate overlapping regions. Batch one coherent screen update instead of refreshing each panel independently. ncurses documents the virtual/physical-screen and staged-update pattern as established prior art. [RK-S29]

The competing bounded-full-repaint strategy reconstructs only the current viewport, never the complete log. It is a valid fallback after geometry/style/width invalidation or when a measured cost model predicts that numerous cursor/attribute changes cost more than a contiguous repaint. Compare sparse 1% changes, 50% changes and 100% changes, scrolling regions, very wide Unicode, narrow cells and resize bursts. “Changed cells” alone is not the objective: total encoded bytes, diff CPU, terminal parsing cost, visible tearing and input latency matter.

For a partial write, keep the exact remaining encoded bytes or invalidate the physical-screen baseline. Do not compare the next desired frame against output never emitted. A resize creates a new geometry generation; suppress stale frame completion and redraw a coherent current viewport. Terminal synchronized-update support may be evaluated only when exact capability and timeout behavior are independently documented/verified; it is not assumed universal here.

**Decisive comparison:** reject a purported diff advantage if, at equal correctness, its CPU/tail latency/bytes exceed bounded repaint under the preregistered workload or it corrupts wide-cell cleanup. Reject full repaint as the universal default if sparse streaming causes excess bytes, flicker, reader-announcement churn or breached input budget. No source establishes the winner on Recursion's terminals.

## R-K-Q07 Pacing batching and input priority

**I, R06.** Separate canonical ingestion from frame generation. Batch presentation updates to an experimental 30 Hz ceiling during sustained output and render on meaningful change; stop animation/timers when idle or hidden. Offer lower-rate and reduced-motion profiles. An input echo or explicit control response preempts disposable frame work, not command-order or canonical invariants. Bound a renderer work slice, parse chunk and history page so a nominal input priority cannot sit behind an unbounded callback.

Each frame uses an immutable state/geometry revision. New output arriving mid-frame accumulates for the next frame; partial output never updates the committed render baseline prematurely. A resize storm may coalesce unsent desired geometries, but accepted RESIZE commands and their lease/receipt facts remain durable. The final valid holder geometry must be applied; passive-client dimensions affect only letterboxing/clipping/reflow of that view.

Input decoding is separate from untrusted output parsing. Escape-prefix ambiguity has a documented finite policy and a keyboard-compatible alternative; it must not delay Stop behind paste/output decoding. A full transport output pipe, incomplete oversized frame, stalled renderer and disconnected view must not hold the only execution-control thread.

Measure input receive→visible local echo, command offer→durable acceptance, acceptance→fence installation, source append→visible committed frame and maximum freeze interval separately. A fast echo is not proof of accepted steering. A 30 Hz cadence is a candidate energy/latency tradeoff, not proof that users prefer it. F07/F09 compares event-driven pacing and 30/60 Hz treatments at matched workloads; all frame and tail results remain U.

## R-K-Q08 Stable scrollback and follow mode

**I, R07.** Anchor reading by semantic event/item ID plus grapheme offset, not an absolute wrapped row number. Incoming output appends to history without moving that anchor. Reflow after resize preserves the anchor or explains that retained content is unavailable. Selection, search hits and drafts survive unrelated output; switching tasks preserves each view's local reading state.

Follow mode is explicit: “Following live output” when enabled, or “N new events · Jump to live” while reading older content. A named keyboard action and pointer control re-enable it. Scrolling away disables follow; output, attention notices and pane focus do not re-enable it. The new-event count is computed from authoritative event identity, not number of paint operations. On reconnect, preserve the reading anchor unless it is outside retention, then show the actual gap.

Complete retained scrollback comes from canonical source events/artifact references, not the terminal emulator's visible buffer or coalesced frames. A live spinner/progress line can sample repeated deltas while an exact event view/export retains the unsampled evidence within declared retention. If raw PTY bytes are not retained, state the recording policy and do not claim complete byte history; bounded audit-relevant events and raw terminal transcripts are different products.

Window virtualization/paging bounds memory; retaining all scrollback in every client is the competing option with a finite test cap. F08 verifies exact export hashes and independent anchors after 100× viewport output. Passing establishes fixture retention and navigation, not infinite retention or cross-terminal text extraction fidelity.

## R-K-Q09 Unicode IME paste and control-sequence safety

**D standards; I R08.** Pin segmentation data and width policy in the profile. UAX #29 defines extended grapheme boundaries; UAX #11 explicitly warns that East Asian Width alone is not an off-the-shelf modern-terminal width solution. Retrieved revisions are Unicode 18.0.0, UAX #29 revision 49 and UAX #11 revision 46. This identifies reviewed documents, not a required runtime Unicode selection. [RK-S42, RK-S43]

Incremental UTF-8 decoding preserves incomplete code points between chunks and rejects or visibly replaces malformed sequences according to a declared policy. Cursor editing/deletion, selection and wrapping operate on grapheme clusters, including combining marks, emoji ZWJ sequences, variation selectors and regional-indicator flags. Width policy accounts for wide/ambiguous characters and terminal/font mismatch; a conservative replacement or plain-text fallback must be available. Never normalize signed/canonical evidence bytes in place merely to display them.

IME composition belongs to the user's terminal/input frontend. Where composition events are exposed, retain the preedit buffer and caret through output/resize; where a terminal delivers only committed text, do not invent preedit support. Pin terminal+IME+locale and manually test composition, candidate selection and cancellation. Streaming must not steal focus or submit partially composed text. Bracketed paste is supported when negotiated; paste is inert composer text until explicit submit, with byte/line caps and disclosure of multiline commands. Kitty's protocol supplies enhanced key disambiguation but cannot be assumed through every host/multiplexer. [RK-S26, RK-S27]

Treat all model/tool/PTY payloads as untrusted data. Render structured conversation through a bounded allowlisted formatter; isolate raw-terminal emulation from application commands. Escape title changes, clipboard OSC 52, hyperlinks, device-control strings and cursor/screen controls unless an explicitly scoped terminal-emulation policy permits them. Do not forward raw output to the containing terminal. Approval-looking output cannot create a real approval control. Clipboard access is a user capability, not a payload instruction. F10 includes all byte split points and malicious control sequences; it cannot establish credential confidentiality.

## R-K-Q10 PERF 010 latency budgets and honest unknowns

**I preregistration proposal R09, not ratified SLA or measured result.** Every measured field is currently `null/unmeasured`. The following numbers are candidate thresholds to make later comparisons falsifiable. They require Owner/reviewer approval and minimum-profile calibration before a performance PASS can be asserted; they are not copied from an upstream benchmark.

| Metric and measurement boundary | Candidate p50 / p95 / p99 | Disposition and hard condition |
|---|---|---|
| Local input received to visible echo on active client | 20 / 50 / 100 ms | U; excludes terminal/OS delivery before receipt; separately capture end-to-end key-to-photon where possible |
| Canonical append completed to committed visible frame | 33 / 50 / 100 ms | U; test at 30 Hz pacing and matched output; stalled clients are reported excluded from live-latency SLO, not silently counted as fast |
| Canonical append request to durable completion | 5 / 20 / 50 ms | U; exact persistence boundary and disk profile frozen; proposed p99 added-view regression ≤5 ms versus zero-view paired baseline |
| Owner Stop offer to durable acceptance and local admission fence | 20 / 50 / 100 ms | U; acceptance and fence measured separately; this is not a process-termination or remote-settlement deadline |
| Individual renderer work slice | p99 ≤8 ms; observed maximum recorded | U; compare bounded repaint and diff, with no hiding GC/blocking pauses |
| Coalesced presentation frames | Count and ratio, no universal maximum | Must bind ranges/reasons; acceptable only after retained source facts |
| Dropped canonical/command/lease/exit/termination events | Exactly 0 | Hard failure at any N; presentation omissions never classified as canonical losses |
| Additional inference, actor creation, effect execution, indexing or disabled-plugin activation caused by views | Exactly 0 | Hard failure; process count may grow for thin clients, not for duplicated actors |

Run N=0/1/5/10/20 passive views; where measuring typed-input latency add one designated active controller and report total clients N+1. Also run the requested total-view-count interpretation separately, with one active among N for N>0, to prevent ambiguous denominators. At N=0 input/frame metrics are not applicable, not zero; append/control/resource measurements remain mandatory. Fix OS/build/terminal/font/geometry, workload rate, event size, writer mode and warm/cold state. Proposed ordinary geometry is 120×40 with 80×24 and 240×80 variants; the protocol's 1..1000 dimensions remain intact, with explicit resource admission for extreme geometry.

Candidate memory envelope: daemon additive projection memory ≤2 MiB per admitted view plus a fixed, predeclared shared snapshot/cache budget; client render/history memory ≤16 MiB per ordinary viewport, with queues ≤1 MiB/4,096 events. Report daemon, all clients and terminal-host RSS separately and summed. These are component-budget hypotheses, not total process RSS promises; B0, allocator overhead and extreme-geometry reservations remain measured inputs. Reject unbounded growth after warm-up and retain peak RSS/high-water marks rather than hiding a spike in a steady-state average.

Record CPU, wakeups, IPC bytes, process/handle counts, p50/p95/p99 distributions, maxima, errors, timeouts and missed-frame count. Minimum sample counts, quantile estimator and confidence intervals must be preregistered; repetitions are independent runs, not millions of correlated tokens. Overload beyond the declared source rate is a separate capacity treatment with bounded shedding/admission behavior, not a waived correctness failure. No approved SLA currently exists; F01/F07/F09 yield the evidence for a later decision.

## R-K-Q11 Focused task workspace and composed views

**I, R10.** Work opens to one task's conversation, a compact identity/route/continuity header, a composer whose delivery mode is named, and a persistent Stop/status strip. The five destinations remain Work, Attention, Artifacts, Environment and Settings/recovery. A command palette names deterministic commands, assistant requests and engine extensions distinctly. Layout restoration restores preferences and selected objects only; it does not activate plugins or restart work.

Agent tabs and splits are optional lenses over existing task/assistant records. Each pane labels actor, task, run/turn and passive/control state. Selecting a tab changes focus; it does not change execution route or acquire a lease. Add-view and new-agent are visibly separate actions, with new-agent crossing admission. A graph is an on-demand projection of lineage/ownership, not a second scheduler. A shared room shows R-J membership and attributed messages with accepted/delivered/adopted evidence; one bounded workflow-step coordination lease is shown separately from terminal control and portfolio authority.

Attention lists durable questions, approvals, conflicts, resource blocks and unresolved effects, ordered by declared urgency/expiry and stable user pinning. It shows exactly what action is waiting and for which task. Background activity does not reorder the row being read or steal focus. Answering uses the original interaction ID/revision; closing the inbox never answers or rejects.

Open one inspector at a time by default: Changes (artifact/diff and verification), Context (epoch/compaction/capsule provenance), Route (exact harness/interface/build and capability losses), Usage (observed units, reservations, unknown residual), Details (receipts/effects/ownership). Users may opt into richer layouts. No graph, telemetry stream or evidence wall opens automatically. Hidden inspectors stop presentation work and cannot start indexing. At narrow widths, tabs and inspector labels become an ordered list while Stop and target remain reachable.

CLI, TUI and later GUI consume the same command schemas and read models; geometry is never backend state authority. This construction sequence preserves current TUI-first direction without silently deleting D-019's opt-in GUI release obligation. The precise release-timing conflict remains an Owner interpretation item, not a smaller-release recommendation.

## R-K-Q12 Per-cell prior art comparison

<a id="conpty-lifecycle-facts"></a>
**D — Windows console profile:** ConPTY supplies terminal I/O and resize. Microsoft warns that servicing its blocking channels together can deadlock. `ClosePseudoConsole` returns immediately starting Windows 11 24H2/build 26100; older indefinite-close warnings need a pre-24H2 scope. The accepted Windows floors meet that threshold. Return/EOF does not establish output drainage or owned-process/effect settlement. [RK-S19, RK-S20]


<a id="zellij-resurrection-facts"></a>
**D — Zellij resurrection:** attaching to a live session and restoring serialized session state are distinct; resurrection can re-run commands. This is a documented lifecycle mechanism, not evidence that automatic actor restart is admitted by Recursion. [RK-S17]


<a id="muse-lifecycle-facts"></a>
**D — Muse lifecycle:** MSP v1 permits one client per host; its stdio connection owns host lifetime, and stdin closure drains/exits the host. Sessions persist; command admission and cursor-bearing outcomes are distinct. Stop admission is separate from a terminal event. Turn interruption can pair retract intent but does not stop all background terminals/children, which have other stop operations. [RK-S05]

<a id="codex-tui-command-facts"></a>
**D — Codex TUI commands:** agent/status controls, saved resume, remote TUI connection, conversation fork, contextual persistent keymaps and slash controls are documented. Enter sends an active instruction; Tab queues the next turn. `/stop` targets background terminals. Whole-work-tree/effect settlement, coherent workspace fork and N-view exclusivity/cost remain unqualified. [RK-S39]

<a id="t3-composer-facts"></a>
**D — T3 composer:** Queue/Steer preference, follow-up settings and keybinding remapping are documented. Queued messages can release at a tool boundary or turn end; Stop reclaims queued messages. Those controls do not establish Recursion Full Stop or external-effect settlement. [RK-S11]

<a id="t3-sidebar-facts"></a>
**D — T3 sidebar:** thread/worktree navigation supports new-thread/new-worktree and same-worktree choices. A beta Working section returns decision-needed threads to the active list. Other client/platform claims require their own profile evidence. [RK-S12]


All cells are **D**, **I** or **U**. D is limited to the cited version/source; U is not an assertion that a feature is absent. Product references are comparison baselines, not endorsements or route qualification. Grok and T3 pins are immutable public commits; Muse/OpenCode/Codex web docs are retrieval-pinned and installed-build correspondence is U. T3's command-line entry starts a server/web interface, not a TUI. [RK-S10]

| Affordance | Grok Build Agent Dashboard | Meta Muse Code | OpenCode | Codex TUI | T3 Code |
|---|---|---|---|---|---|
| Focused work and session navigation | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts) | D: [canonical facts](../ri/report.md#muse-interactive-facts) | D: [canonical facts](../rj/report.md#opencode-v1-tui-facts) | D: CLI work loop, resume and subagents [S09] | D: thread/worktree navigation across web/desktop/mobile [S10,S12] |
| Attention organization | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts) | D: [canonical facts](../ri/report.md#muse-interactive-facts); U: equivalent inbox | D: [canonical facts](../rj/report.md#opencode-v1-tui-facts); U: inbox parity | D: [canonical facts](#codex-tui-command-facts); U: unified cross-task inbox | D: [canonical facts](#t3-sidebar-facts) |
| Steer versus queue | D: [canonical facts](../ri/report.md#grok-keyboard-facts) | D: [canonical facts](../ri/report.md#muse-interactive-facts) | D: [canonical facts](../rj/report.md#opencode-v2-tui-facts); U: equivalent v1 semantics | D: [canonical facts](#codex-tui-command-facts) | D: [canonical facts](#t3-composer-facts) |
| Persistence and reconnect | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts); U: Recursion no-effects multi-view semantics | D: [canonical facts](#muse-lifecycle-facts) | D: [canonical facts](../rf/report.md#opencode-server-facts); U: exact no-effects reconnect | D: saved resume and remote TUI connection; U: qualified N-view behavior [S09,S39] | D: cached offline projections and centralized connection runtime [S38] |
| Worktrees and forks | D: [canonical facts](../ri/report.md#grok-dashboard-guide-facts) | D: [canonical facts](../ri/report.md#muse-interactive-facts); U here: workspace fork completeness | U: this retrieved TUI evidence does not establish dirty-tree preservation | D: [canonical facts](#codex-tui-command-facts); U here: complete dirty-source preservation | D: [canonical facts](#t3-sidebar-facts) |
| Truthful receipt/effect separation | U: full accepted/delivered/adopted/settled contract | D: [canonical facts](#muse-lifecycle-facts) | U: equivalent composed contract | U: equivalent composed contract in terminal docs; protocol qualification separate | D: committed intent/receipt precedes effects; turn end differs from checkpoint settlement [S13] |
| Configurable keyboard/workflow surface | D: [canonical facts](../ri/report.md#grok-keyboard-facts) | D: palette/keymap and configuration [S03,S46] | D: configurable keybinds, themes and separate TUI config [S06,S07] | D: [canonical facts](#codex-tui-command-facts) | D: [canonical facts](#t3-composer-facts) |
| N passive views with one fenced terminal lease | U: dashboard sessions do not establish this | D: [canonical lifecycle facts](#muse-lifecycle-facts); U: external projection multiplexer | D: multiple clients; U: one input/resize lease and N-cost bound | U: remote connection alone does not establish exclusion or cost | U: multiple surfaces do not establish the terminal lease contract |
| Full Stop across owned descendants/relaunchers/effects | U: cancel/delete distinctions do not prove it | D: [canonical facts](../ri/report.md#muse-interactive-facts), [canonical facts](#muse-lifecycle-facts); U: Recursion Full equivalence | U: required whole-owned-work contract | D: [canonical facts](#codex-tui-command-facts); U: Full equivalence | D: [canonical facts](#t3-composer-facts); U: all-owned-work/effect settlement |
| Accessibility and PERF-010 qualification | U: no independently verified matrix in reviewed sources | U | U | U | U |

In this table `Sxx` abbreviates `RK-Sxx`. The OpenCode v2 TUI was retrieved separately after reading R-J's draft. That documented interaction does not backfill v1 or qualify a v2 binary. R-J Q18 retains the deeper v1/v2 API, replay and adoption distinctions; those facts are not duplicated here. Task graphs, attention, persistence, worktrees, receipts, configurable workflows and side conversations are existing categories. A combination may be useful without being historically novel.

## R-K-Q13 Differentiation that could survive a strong baseline

**I hypotheses R11.** D-024 already fixes productive continuity as the claim to test. Candidate TUI differentiation is the user-visible joint contract, not another dashboard:

| Candidate claim | Strong competing baseline | Decisive falsifier | Passing evidence would not prove |
|---|---|---|---|
| Reattach/split preserves currently authorized work and exact evidence with no added inference | An upstream server plus thin clients, or T3's durable intent/reconnect model | Any view-triggered effect/relaunch/hidden helper, authority loss, or baseline achieves equal results with less effort | Better model quality, legal permission, general machine-loss recovery |
| Operator can distinguish accepted, delivered, adopted and unresolved quickly during faults | Muse's command/view distinction and T3's effect-state separation | Blinded participants systematically misidentify a delivered message as adopted or an offline effect as settled; baseline equal/better | That backend receipts themselves are correct outside tested profiles |
| One bounded workflow-step coordinator remains legible across many views | Existing agent dashboards/task boards with explicit ownership labels | A split mints another executive/step permit, hides a conflicting holder, or fails stale-step controls | Global optimal coordination or cost savings |
| Many passive views have preregistered bounded cost without blocking control | External multiplexer hosting a thin client and a simple single-view baseline | Any hard floor failure or no practically meaningful benefit at N=20 | Zero marginal CPU/memory, all terminals, any inference savings |
| Users complete the six continuity journeys with fewer errors/review minutes | Best supported direct harness and T3-like workflow, matched configuration | Equivalent or worse verified outcomes or human effort after all setup/recovery cost | Universal category leadership or a novelty claim |

No superiority is established. Each evaluation includes task completion, authority/evidence preservation and honest accounting, not only time-to-first-paint. A design that lowers token cost while worsening safety or comprehension fails the accepted optimization floors. No native helper model may silently support an upstream-only workflow.

## R-K-Q14 Facts rather than one optimistic badge

**I, R12.** Show orthogonal evidence fields with timestamp/source and current/last-known status:

- Command: saved locally → accepted, then delivered/applied where evidenced, observed outcome, and settled/unresolved effects. Failed/refused/unknown are explicit branches, not a progress animation.
- Message: accepted, delivered, adopted each need their own evidence. Rendering the text proves none. If an adapter cannot observe adoption, show unknown rather than infer it from later activity.
- Code: generated, tested (exact test receipt), reviewed (reviewer/candidate binding), accepted (Owner/gate) and published are distinct.
- Configuration: compiled, validated, staged and effective attach to revisions. A view's edited draft is not effective configuration.
- Continuity: task identity, source/route/context epoch, last verified checkpoint, pending approvals, active holder and unresolved operations. A resumed upstream session may be new while the task persists.

A plausible row is “Local turn interrupted; local owned processes observed empty; one node unreachable; one external effect unresolved.” It must not collapse to “Stopped.” Pending Lazy Stop names the operation boundary, deadline and explicit escalation policy. An event gap is a marker plus verified snapshot lineage, not a prose reconstruction. Unknown usage stays null with a reason, never a zero or hidden subtotal.

These read models are shared backend projections, not independent frontend databases. Rendered facts can lag; display their freshness and let users inspect the receipt. Commands use expected revisions and stable idempotency IDs even from cached views. F12 tests delayed, reordered and stale facts; passing demonstrates a reducer/UI mapping, not the underlying remote effect's actual outcome. T3 and Muse already document important pieces of this distinction. [RK-S05,RK-S13,RK-S38]

## R-K-Q15 Keyboard access and focus

**I, R13.** Define commands by stable action names and contextual targets, then map configurable shortcuts to them. Provide a discoverable palette/help listing command name, current binding, target, capability requirement and disabled reason. Every pointer action has a keyboard path. A command may be invoked by a palette name when a host captures its usual chord; do not require Kitty protocol or a particular terminal.

Use logical focus order across task navigation, transcript, composer, inspector and Stop. Within a composite list use arrows; Tab/Shift-Tab enter/leave focus regions consistently. Focus is visible in plain text as well as color, remains onscreen, and returns to its invoking control after an inspector closes. Preserve the draft/caret when opening help or receiving output. An expired interaction updates in place without moving focus onto a different approval.

Bindings have explicit global versus region precedence, collision detection and export/reset. Reserve host, shell, multiplexer and assistive-technology chords through profile-specific compatibility maps. Printable-letter shortcuts apply only in a named navigation mode, not during typing/IME. Prefix sequences can be supported, but a discoverable non-timed palette alternative must always exist. Command meaning cannot change destructively merely because an agent became busy between keypresses.

<a id="wcag-criteria-facts"></a>
**D — WCAG criteria:** WCAG 2.2 covers keyboard access, ordered/visible/unobscured focus, name/role/value, contrast, non-color communication and status messages. It addresses web content rather than certifying arbitrary terminal emulators [RK-S30]. See [R-N’s applicability note](../rn/report.md#wcag-applicability-facts) for the web/native distinction. **I/U:** ARIA fields or screenshots cannot establish terminal accessibility; exact bindings and assistive-technology behavior remain unqualified until F13. Prior-art contextual keymaps are identified in the comparison notes.

## R-K-Q16 Persistent Stop mode and scope

**D vocabulary; I R13.** Keep a named Stop control visible in the work footer/header even when the transcript is scrolled, composer has text or an inspector is open. Display selected mode and actual target, for example “Stop Full · task T · owned scope 6 local / 1 remote unknown.” Provide one direct configurable key/chord and palette action; no mouse-only target or timed double press is required. A compact terminal can expose the same text through a persistent command strip rather than hiding Stop inside an overflow menu.

Aggressive immediately fences further selected-agent dispatch and requests forceful interruption, listing descendants separately. Full traverses the rooted ownership set, including shells, subagents, monitors and relaunchers, with separate local/remote receipts. Lazy closes admission and waits for the named observable operation boundary, showing deadline and any configured escalation. `checkpoint`, `interrupt` and `drain` remain distinct mechanisms, not extra Stop modes.

Stop control authority is independent of input/resize lease and passive observation permission. A read-only user sees the scope/mode and a disabled explanation; an authorized owner need not take the keyboard lease before stopping work. A shared upstream host cannot be killed if it owns unrelated sessions; use qualified session-scoped controls or report inability to isolate the requested scope. No Full badge asserts external rollback.

Escape only dismisses a transient UI layer or cancels an unsubmitted editing action with recoverable draft behavior. It is not a global destructive Stop/quit/delete mapping. Closing a pane remains Detach, clearly separate from Stop and Delete history. An explicit confirmation is appropriate when changing an uncertain/broad scope, but cannot become a universal modal delay for an already-authorized emergency action. F07/F11/F13 test discoverability, execution scope and liveness independently.

## R-K-Q17 Accessible presentation modes

**I, R14.** Provide an ordinary keyboard-first mode, high-contrast mode with textual status labels, reduced-motion mode with stable progress text/no blinking spinner, and a plain-text sequential mode preserving commands, interaction IDs and exact receipts. Do not depend on color, animation, Nerd Font glyphs or a two-dimensional graph. Keep speech notifications separate from the rapidly changing visual transcript.

Semantic announcements summarize durable transitions: a question/approval needs attention; control transferred; Stop accepted/fence observed; connection lost; gap detected; run ended with unresolved effects. Deduplicate by event ID, merge repetitive progress over a configurable interval (candidate 1 second for nonurgent summaries), and provide a reviewable announcement history. Never announce every token or steal focus. Urgent Stop failure/approval expiry should not be buried by a progress rate limit; user control must allow pausing announcements and reading full detail on demand.

A raw ANSI TUI cannot assume browser-style live regions or direct screen-reader semantics. Windows Terminal's accessibility design describes a UI Automation provider and output notifications; a backend's semantic event needs a supported frontend/terminal path or a plain-text accessible view. [RK-S40] Linux terminal/screen-reader combinations need a separately admitted compatibility matrix. Narrator/NVDA/JAWS and representative Linux configurations are test candidates, not claimed supported products; unavailable licensed tools remain untested, not waived.

Use the [canonical accessibility criteria](#wcag-criteria-facts) as review targets, without claiming conformance from textual requirements. F13 requires actual assistive-technology/user inspection, including high-output, small geometry, IME and reconnect. Screenshot correctness or automated text extraction alone cannot pass accessibility.

## R-K-Q18 Multiplexer options without selecting one

All options retain the accepted daemon/broker owner. “In-process” here means a renderer/projection module collocated with a service or thin client; an interactive foreground process that is the sole runtime owner is excluded by requirements, not selected against by benchmark.

| Option | Detach and ownership | Windows/Linux | Accessibility and testability | Dependency/cost uncertainty |
|---|---|---|---|---|
| In-process renderer/projection | I: fewer internal boundaries; still needs detached broker lifetime and client-independent PTY drain. Fatal if UI exit tears down owner | U: native backends at both floors required; shared code is not parity | I: deterministic render fixtures easier to inject; shared scheduler/allocator can couple faults | I: fewer IPC copies but greater crash/jank coupling; measured CPU/RSS and maintenance U |
| Local daemon endpoint with thin clients | I: naturally expresses durable owner plus disposable projections; authenticated local IPC mandatory | I: platform endpoint implementations can differ while semantics stay identical; U: conformance | I: fake client, fuzzing, lease races and disconnect faults can be isolated; accessibility still client-dependent | I: serialization, schema/versioning, service lifecycle and support costs; no automatic performance benefit |
| tmux as view host | D: server/client detach and read-only/ignore-size clients exist; I: panes run Recursion clients, not actors [S14,S15] | D: official supplied builds list Linux/macOS; U: native supported Windows path in these sources [S41]. WSL does not satisfy D028 production | I: adds prefix/focus/TERM/control-mode layers; test both direct and nested clients; screen-reader fit U | D: libevent/ncurses dependencies documented [S47]; I: integration may cost less than bespoke layouts, or more through parity/escape-key maintenance |
| Zellij as view host | D: attach to live sessions and serialized resurrection are distinct; I: only thin-client commands may be restored automatically [S17,S18] | D: current FAQ native Windows named pipes/ConPTY; U: exact D028 build behavior [S16] | D: simplified UI and collision-resistant presets documented [S16]; U: screen-reader/IME conformance | I: layouts/plugins and server protocol add dependency/update surface; savings and porting cost U |
| OS terminal panes as view host | D: Windows Terminal offers split/focus/resize/close UI [S36]; I: each pane runs a disposable client | U: equivalent Linux host matrix differs; no universal OS pane protocol | I: can use familiar host accessibility but loses integrated layout semantics; app accessibility still required | I: low custom pane code, less consistent cross-host behavior; host lifetime cannot own actor lifetime |

S47 is the official tmux installation reference in the source register. Each row has a competing option and elimination test in §24; none is selected. Test local-only attachment without a public listener. An external host may terminate a client on pane close; that is acceptable only if the independently owned runtime survives. It may not restart an actor command during layout restoration.

## R-K-Q19 Framing backpressure cursor and encoding options

**D frozen baseline.** M1B objects have exact fields, UTF-8 I-JSON restrictions, maximum object size 262,144 bytes, depth 64, raw payload cap 65,536 decoded bytes and Count bounds. Preserve its message set HELLO/WELCOME/SNAPSHOT/EVENT/ACK/CREDIT/INPUT/RESIZE/RESET. RFC 8785 canonicalization is a digest representation, not message framing. I-JSON interoperability does not supply authentication, access control or resource admission. [RK-S34,RK-S35]

| Open comparison | Candidate advantages | Competing cost/failure and required falsifier | Non-proof |
|---|---|---|---|
| Length-prefixed bounded records | I: reject oversized declared lengths early; count partial bytes before decode | Bounded JSONL can be easier to inspect. Reject lengths causing unchecked allocation, forever-blocked partial frames or host-endian ambiguity | Framing does not guarantee control scheduling or durable delivery |
| Bounded JSONL records | I: readable stream and common tooling | Length-prefix avoids newline scanning. Require escaped newlines inside JSON, incremental cap/time limit and explicit incomplete-tail policy; one giant line is a hard rejection | A line ending is not durable acceptance |
| RFC 7464 JSON text sequences | D: record separator framing/recovery conventions [S32] | I: less ubiquitous tools than JSONL; recovery must never skip canonical facts silently | Parser recovery does not authorize event-gap invention |
| Application CREDIT plus bounded transport | I: per-view byte/event allocation isolates slow readers | Transport-only flow control is simpler but fails if one blocked client stalls shared writer. Reject cumulative grant overflow or accepting EVENT without credit | Socket write completion is not client fold/ACK |
| Event cursor | I: natural canonical event ordering and structured replay | Byte cursor maps terminal payload offsets. Reject holes from filtered events or rollover; map source identity separately | Event count does not describe visible text width or atomic external effects |
| UTF-8-byte cursor | I: exact raw payload offsets | Event cursor is easier for semantic streams. Reject base64/frame-size counting, dropped-byte concealment or Count wrap | Bytes are not codepoints, graphemes or cells |
| Structured snapshot plus bounded artifact reference | I: rebuild semantics and generate any frontend | Cell snapshot yields fast visual restore. Reject missing object/digest, unauthorized fields, schema/width mismatch or suffix divergence | Digest correctness does not prove source authenticity or complete historical retention |
| Cell/terminal-state snapshot | I: exact emulator state including alternate screen, styles and cursor | Semantic snapshot permits accessibility and other frontends. Reject hidden authority encoded in screen state or cross-width corruption | Pixels/cells do not establish command receipts or agent state |
| JSON/I-JSON object encoding | D: required in existing profile; I: easy inspection and conformance tooling | Binary may reduce envelope/base64 cost. Falsify efficiency claim with matched parse/IPC/tail measurements | Human-readable does not mean safe, small or canonical without validation |
| CBOR or another explicitly versioned binary encoding | D: CBOR defines a typed compact representation and deterministic-encoding considerations [S33]; I: possible new profile | JSON remains existing contract. Reject lossy null/missing/integer/schema mapping or incompatible digest identity; evaluate decoder attack surface and diagnostic cost | Smaller records do not prove faster UI, better security or cheap porting |

No choice is made. A transport may frame existing JSON objects without changing their fields, but framing negotiation itself needs a contract. A binary representation cannot quietly retain the `m1b-broker/1` identity while changing its JSON contract. If evaluated, define a new outer/versioned profile with a total reversible mapping and preserve old digest domains. Snapshot transfer, lease-management/control verbs and Stop stay separately typed; they cannot be smuggled into untrusted EVENT payloads as executable commands.

## R-K-Q20 Ownership OS paths and prebenchmark elimination

**I R15.** Every host/encoding combination must use the same ownership and lease checks before decoding input into effects. A terminal/PTY is an I/O device, not execution authority. **D:** Linux PTYs provide paired terminal endpoints; sessions/process groups are useful signal scopes but are not sufficient descendant containment after escape [RK-S22]. Use the [canonical cgroup premises](../re/report.md#linux-cgroup-facts). **I:** killing contained processes does not undo filesystem/network effects or disable an outside relauncher.

For the [ConPTY profile](#conpty-lifecycle-facts), use the distinct [Job Object premises](../re/report.md#windows-job-facts). **I:** the client must never hold the final authoritative Job handle. Creation-time containment and qualified membership-before-resume remain the accepted candidate from historical research. Breakaway, alternate launchers and unrelated shared-host work remain explicit negative cases. Use the [versioned close facts](#conpty-lifecycle-facts) when checking settlement.

R-E's trusted launcher may own OS containment handles in another principal. In that arrangement the broker receives scoped control/evidence, not raw credential or arbitrary impersonation handles. A Full Stop request cannot enlarge its target to a shared credential host. The thin client's external multiplexer owns only the client's terminal; it cannot bypass the broker by directly attaching to credential-facing raw PTYs.

Eliminate before performance measurement any option showing: pane close kills the actor; holder/focus races admit two INPUTs; passive resize changes upstream geometry; raw output invokes a command/clipboard/approval; reconnect creates an actor or retries an ambiguous effect; output floods delay a required Stop fence indefinitely; malformed framing allocates without cap; daemon restart accepts stale leases; process exit is displayed as external settlement; or a layout restore launches inference/indexing/plugins. Encoding changes cannot repair these authority failures. F04–F07/F10–F12 are correctness prerequisites for PERF-010.

## R-K-Q21 External multiplexer as runtime and reversal conditions

**I, R16.** The decisive falsifier of “simply use an external multiplexer as the runtime” is a single trace where its ordinary pane/session lifecycle produces an unadmitted runtime effect: kill-pane terminates owned work, resurrection re-runs an actor, multiple writable attached clients bypass the broker lease, a full output consumer blocks control, or its session ID replaces canonical task/effect identity. tmux's documented pane destruction [RK-S14] and the [canonical Zellij mechanism](#zellij-resurrection-facts) make these concrete test cases, not accusations of bugs.

A wrapper can keep the broker outside the external multiplexer and run only thin clients in panes. That is still a product-owned semantic view layer, even if pane drawing/hosting is reused. It should be compared fairly against integrated splits and OS panes with identical capabilities, clean configuration and matched terminal profiles.

A tentative preference for product-controlled composition would reverse if an external-host adapter passes every authority/lifetime/accessibility/fault gate on both native platform floors, delivers equal/better measured input and append tails, and has lower total engineering/update/support cost over an agreed interval. Conversely a Windows/IME/accessibility gap, unsupported hostile-key binding, unauditable plugin auto-launch, or parity-maintenance cost above native construction can eliminate that host profile. D-033 requires measured time including licensing review, migration, tests, dependency upgrades and regression support; lines copied or a weekend demo are not cost evidence. No preference or port-cost estimate is adopted here.

## R-K-Q22 Provider free acceptance suite

All fixtures below are **UNEXECUTED**. Full inputs, prerequisites, independent oracles, predicates, evidence and stopping conditions are in `unexecuted-local-handoffs.json` and its readable companion. No provider endpoint is required; provider/auth/network calls are trapped and are immediate failures.

| Fixture | Required stimulus | Exact central predicate |
|---|---|---|
| F01 N-view soak | N=0,1,5,10,20; idle and bounded high output; passive-count and total-count interpretations reported | Zero view-caused work/model/index/plugin activation; exact canonical digest equality with source oracle; queue/memory bounds hold at every sample; adopted latency thresholds met with all failures retained |
| F02 Close/split/zero views | Close each client, then all; reopen/split existing task | Same actor/process birth/attempt and no extra effects; continuing drains; only explicit Stop changes execution lifetime |
| F03 Reconnect and host loss | SSH-style drop, client crash/sleep, broker incarnation change | No duplicate operations; stale leases refused; reconstruct identical canonical state or visible verified gap; no implied resumption |
| F04 Lease races | Concurrent request/transfer/input/resize with stale holders | At most one valid holder per target; exactly one accepted result per identical command ID; conflicting duplicate refused; passive input/resize refused |
| F05 Replay and materialization | Below-floor request, missing/corrupt snapshot, gap continuation, ACK/CREDIT errors | Exact M1B known-answer outcomes plus independent snapshot/suffix state equality; no GAP wire invention or optimistic recovered badge |
| F06 Cursor/decoder limits | Both cursor units, boundary values, repeated credit, partial/oversized/deep frames | No wrap, hidden hole, unlimited outstanding allocation, illegal unit switch or schema bypass; unsupported evolution refused explicitly |
| F07 Saturation and Stop | Zero-credit/stalled readers, blocked rendering, full data queues, writer pressure | Canonical facts retained and local admission fence meets adopted bounded target; no Stop behind bulk frame; unresolved evidence honestly shown |
| F08 Huge output and reading | Output ≥100× viewport and retention-boundary case | Exact retained history export; reading anchor and selection stable; memory bounded; explicit real loss marker only |
| F09 Rendering and resize | Sparse/dense frames, 100 resizes/s synthetic input, partial writes, largest admitted geometry | Final framebuffer equals independent reference; no stale generation commit/wide-cell residue; holder's final geometry applied; tails/resource limits hold |
| F10 Unicode IME and injection | Grapheme corpus split at every UTF-8 boundary; actual later IME matrix; malicious controls/paste | Exact committed text/editing oracle; composition preserved where supported; no output-origin command, clipboard or approval effect |
| F11 Process containment and Stop scopes | Qualified native synthetic process tree, escape/relauncher/shared-host cases | Detach preserves actor; Full covers owned set or explicitly unresolved; unrelated actors unaffected; Aggressive/Lazy semantics exact; no remote rollback inference |
| F12 Shared backend facts | Same commands through headless client and TUI; delayed/stale/conflicting receipts | Identical accepted commands/canonical states; saved/accepted/delivered/adopted/settled remain distinct; no UI-created second executive |
| F13 Keyboard/accessibility | All controls with keyboard, narrow terminal, screen readers, reduced motion | Every action reachable and labeled; visible restored focus; Stop discoverable; no destructive Escape; important announcements deduplicated/rate-limited without lost urgent state |
| F14 Port and encoding comparison | Same frozen workload under eligible host/encoding candidates | Compare only correctness-passing candidates, total-system cost and maintenance effort; no selection from incomplete data |

Before any local run, freeze the target candidate, exact OS/terminal/font/IME, synthetic workload, memory envelope, stopping deadline and adopted thresholds. If those are missing, status is BLOCKED/NOT_RUN, never pass. Destructive OS/process-loss fixtures require a separately approved disposable target and independent containment; this research authorizes none. At least one independent verifier uses literal expected outcomes or a separately implemented renderer/reducer rather than echoing the system-under-test assertions.

## R-K-Q23 What synthetic fixtures can and cannot prove

**I, R17.** The fixture observer is outside the client/projection implementation. It records process creation with birth identities, provider/model invocation traps, indexer entry traps, plugin import/activation counters, canonical append receipts/digests, control grants, input delivery and effect dispatch. Assert zero *increment attributable to view operations* against a matched task baseline; client processes themselves are expected and separately counted. A stub saying its own model count is zero is insufficient.

For close/detach, compare actor and process birth identity across view close while synthetic output continues, then close all clients and verify output drainage and the same effect sequence. For split/no-work, compare the pre/post authority graph and counters; view IDs/layout records may increase, Head/ARM role leases, bounded step permits, work reservations and actor count may not. Multiple contexts remain separately keyed in a combined view.

For slow-client isolation, stop ACK/CREDIT/read progress on one view while another offers authorized Stop and the writer receives synthetic events. Correlate actual acceptance/fence timestamps with queue high-water and source event IDs. Test a hostile partial frame and a blocked pipe, not only a sleeping render loop. A bounded abstract trace does not prove physical liveness; local scheduler/persistence instrumentation is necessary later.

For cursors/history, derive expected byte counts/event counts independently from the synthetic corpus. Track every client fold and compare reconstructed snapshot+suffix state and exact retained export digests. Reject invented gaps for deferred events, arithmetic wrap and stale-incarnation continuation. At every N, enforce the same hard floors and explicitly adopted append/memory bounds; do not hide N=20 failures in aggregate averages.

These fixtures can falsify deterministic wiring, state mapping and bounded platform behavior when later executed. They cannot prove provider-native cancellation, subscription savings, D029 credential isolation, real model quality, whole-internet effect settlement, unbounded fault tolerance or accessibility for every terminal. Productive continuity still requires separately admitted end-to-end route/host journeys and human evaluation. Runtime evidence remains U today.

## 24 Recommendation and falsification register

These are research candidates within accepted requirements. “Competing option” means a real alternative implementation or comparison treatment, not permission to violate an accepted invariant. Every proposed mechanism in Q01–Q23 is governed by the corresponding row. Source primitives are cited where introduced; this register is original design analysis.

| ID and candidate | Real competing option | Decisive falsifier / decision test | What a passing test does not prove |
|---|---|---|---|
| R01 Disposable views over broker-owned actors | Collocated renderer with an independently retained owner; external host with thin clients | F02/F03: any view-close/reconnect work creation, actor loss or downstream EOF; compare eligible alternatives | Broker crash survival, credentials or provider recovery |
| R02 Atomic target-scoped input/resize holder | Explicit separately typed input/resize grants with a transaction preserving one common holder | F04: two valid holders, stale acceptance, passive resize, or refusal of authorized owner Stop solely for lack of input lease | Role/step/effect authorization or confidentiality |
| R03 Verified snapshot plus ordered suffix and explicit gaps | Retain full event replay within a finite declared retention profile | F05/F06: mismatched reconstruction, fake loss, cursor wrap, absent snapshot accepted | Physical durability, source truth, infinite retention |
| R04 Bounded per-view flow isolation and reserved control path | Shared fair queue with independently enforced per-client quotas and end-to-end reserve | F07: stalled view blocks canonical append/Stop, cumulative grant or buffer growth unbounded | Control liveness under an unavailable disk/kernel; all remote termination |
| R05 Incremental/diff contract with measured repaint fallback | Bounded full viewport repaint | F09: wrong pixels/cells or worse tail/bytes/CPU at equal correctness; crossover changes choice | Best renderer/toolkit or universal perceptual quality |
| R06 Bounded pacing/batching and input priority | Event-driven immediate output or 60 Hz pacing with bounded work slices | F07/F09: input/Stop starvation or unacceptable freshness/energy tradeoff | Benefit on unspecified hardware, network or terminal |
| R07 Semantic reading anchors plus virtualized retained history | Finite fully materialized client history | F08: anchor/selection moves, export loses retained facts, unbounded client cache | Infinite raw-output preservation or secure terminal host |
| R08 Pinned grapheme/width profile and inert output/paste | Conservative plain text with visible escaped controls and replacement glyphs | F10: text corruption, accidental submit, IME focus loss or any output-origin authority | Complete Unicode support, D029 security or arbitrary-font parity |
| R09 Preregistered PERF-010 thresholds and resource envelopes | Owner-approved profile-relative regression bounds without absolute UI targets | F01: calibrated minimum profile cannot meet targets or targets do not predict user usability; revise before trials | Measured advantage from proposed numbers, accepted SLA or route efficiency |
| R10 Focused work plus opt-in splits/inbox/inspectors | Per-actor-only views or externally hosted panes with a separate deterministic inspector | F12/F13 and blinded tasks: more wrong-target actions, slower comprehension, hidden plugin activity | Category leadership, accessibility conformance or lower review effort today |
| R11 Joint continuity differentiation | Strong direct-harness/T3/Muse behavior with matched setup and faults | Six journeys show equal/worse outcomes or human effort after total costs | Historical novelty or universal superiority |
| R12 Orthogonal receipt/freshness facts | Compact summary with expandable evidence, retaining the same semantics | F12: user/reducer conflates saved with accepted, adopted with delivered, exit with settlement | Authenticity of an unqualified source's own assertions |
| R13 Named keyboard controls and persistent scoped Stop | Palette-first command interface with always-visible target/mode | F13: inaccessible action, obscured/lost focus, timed-only Stop or destructive Escape | Best default chords on all terminal hosts |
| R14 Semantic announcements plus plain-text fallback | Dedicated accessible linear client over the shared backend | F13: streaming overwhelms speech, important state omitted, focus stolen, unsupported AT mislabeled passed | WCAG/UI conformance or all assistive-technology coverage |
| R15 Distinct terminal I/O and qualified OS ownership boundary | Out-of-process operator-provisioned launcher owning containment and scoped receipts | F11: escaped/restarted child unaccounted, unrelated work killed, final Job handle held by view | Remote rollback, compromised-kernel safety or credential noninterference |
| R16 External host comparison under product semantics | Integrated split composition or OS terminal panes | F14 plus all hard gates: native parity/accessibility/maintenance cost reverses claimed leverage | Cheap porting from source availability or a demo |
| R17 Independent synthetic observers and literal expected outcomes | Differential implementation plus externally captured OS evidence | F01–F14: oracle shares the same defect, counters only self-reported, mutants pass or target is unpinned | Live provider semantics, entitlement, bills or human comprehension |

**Open-option completeness:** Q18's in-process, daemon, tmux, Zellij and OS-pane rows all compare against the other eligible hosts under R01/R16. Q19's framing, credit, cursor, snapshot and encoding rows each contain their own competing option, falsifier and non-proof. Binary versus JSON remains a future versioned experiment; existing M1B JSON conformance remains unchanged.

## 25 Unresolved decisions and local evidence needed

1. **M1B production mapping:** freeze snapshot materialization/handshake, version negotiation, cursor rollover/incarnations, explicit cumulative-credit bounds and ACK-release interpretation. Preserve literal existing tests; add a separate N-client composition oracle and physical pipeline fixtures.
2. **Performance:** adopt an exact minimum hardware/OS/terminal profile and numerical or profile-relative thresholds before measurements. All current proposed values remain unmeasured candidates.
3. **Accessibility:** approve a finite terminal/font/IME/assistive-technology matrix and plain-text fallback requirements. Record untested combinations honestly.
4. **Credential/launch boundary:** require separate qualification of the operator-provisioned boundary and output/tool closure described by R-E; its research report is not qualification. A raw-terminal view may require a narrower profile; do not loosen D029 for convenience.
5. **External host and porting:** resolve source/binary/dependency/license closure and measure implementation, parity and upkeep cost. Current Zellij Windows documentation prevents automatic exclusion but is not qualification.
6. **Release timing:** preserve TUI-first construction and one shared backend. Current direction says GUI later; D019 says accepted GUI built opt-in at first release, while older PRODUCT/INTERFACE prose excludes it. Only the Owner can reconcile calendar/release packaging meaning; this report neither removes GUI nor mandates building it first.

## 26 Completion and artifact scope

The accompanying coverage register maps the exact 23 questions and nine completion gates to these sections and local handoffs. Coverage means substantively answered research, including bounded unknowns; it is not independent acceptance or runtime PASS. All fixture statuses are UNEXECUTED. The existing supplemental wire-test entrypoint is cited in the handoff only because its source and stated scope were inspected; it was not run.

No repository path was edited. Artifact QA records protected-file hashes against the supplied snapshot and scans delivery files for credential-like material, absolute private capture paths and raw public-source bodies. Public documents were fetched without accounts; a Muse terminal URL returned an identity-confirmation interstitial and was not used as evidence or bypassed. Failed public URL attempts remain in the source register as non-supporting records. Full raw captures remain outside the deliverable; their response-body hashes establish retrieved byte identity, not signed provenance or installed behavior.

## 27 Sources

The complete source register supplies exact URLs, retrieval timestamps, available versions/commits, full HTTP-body SHA-256 hashes and limitations. Markdown source links below support the cited public factual claims; local contract/analysis records are separately classified and pinned in the register. No raw source body is reproduced.

- **RK-S01** [Grok Agent Dashboard](https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/23-dashboard.md) · 2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8 · retrieved 2026-10-02
- **RK-S02** [Grok keyboard shortcuts](https://raw.githubusercontent.com/xai-org/grok-build/2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8/crates/codegen/xai-grok-pager/docs/user-guide/03-keyboard-shortcuts.md) · 2bdd1d6a6369de0e8c68132ea4539e9abd9e14a8 · retrieved 2026-10-02
- **RK-S03** [Muse working with the agent](https://dev.meta.ai/docs/muse-code/interactive) · mutable documentation · retrieved 2026-10-02
- **RK-S05** [Muse sessions and turns](https://meta-models.github.io/muse-code-sdk/next/guides/msp-concepts/sessions-and-turns/) · mutable documentation · retrieved 2026-10-02
- **RK-S06** [OpenCode TUI](https://opencode.ai/docs/tui/) · mutable documentation · retrieved 2026-10-02
- **RK-S07** [OpenCode keybinds](https://opencode.ai/docs/keybinds/) · mutable documentation · retrieved 2026-10-02
- **RK-S08** [OpenCode server](https://opencode.ai/docs/server/) · mutable documentation · retrieved 2026-10-02
- **RK-S09** [Codex terminal CLI](https://developers.openai.com/codex/cli/features/) · mutable documentation · retrieved 2026-10-02
- **RK-S10** [T3 README](https://raw.githubusercontent.com/pingdotgg/t3code/b33eda13998b5b0571daaf266c87f6f31af41f7d/README.md) · b33eda13998b5b0571daaf266c87f6f31af41f7d · retrieved 2026-10-02
- **RK-S11** [T3 composer](https://raw.githubusercontent.com/pingdotgg/t3code/b33eda13998b5b0571daaf266c87f6f31af41f7d/docs/user/composer.md) · b33eda13998b5b0571daaf266c87f6f31af41f7d · retrieved 2026-10-02
- **RK-S12** [T3 thread sidebar](https://raw.githubusercontent.com/pingdotgg/t3code/b33eda13998b5b0571daaf266c87f6f31af41f7d/docs/user/thread-sidebar.md) · b33eda13998b5b0571daaf266c87f6f31af41f7d · retrieved 2026-10-02
- **RK-S13** [T3 architecture](https://raw.githubusercontent.com/pingdotgg/t3code/b33eda13998b5b0571daaf266c87f6f31af41f7d/docs/internals/overview.md) · b33eda13998b5b0571daaf266c87f6f31af41f7d · retrieved 2026-10-02
- **RK-S14** [tmux manual](https://man.openbsd.org/tmux.1) · mutable documentation · retrieved 2026-10-02
- **RK-S15** [tmux getting started](https://github.com/tmux/tmux/wiki/Getting-Started) · mutable documentation · retrieved 2026-10-02
- **RK-S16** [Zellij FAQ](https://zellij.dev/documentation/faq) · mutable documentation · retrieved 2026-10-02
- **RK-S17** [Zellij session resurrection](https://zellij.dev/documentation/session-resurrection) · mutable documentation · retrieved 2026-10-02
- **RK-S18** [Zellij commands](https://zellij.dev/documentation/commands) · mutable documentation · retrieved 2026-10-02
- **RK-S19** [Creating a pseudoconsole session](https://learn.microsoft.com/en-us/windows/console/creating-a-pseudoconsole-session) · mutable documentation · retrieved 2026-10-02
- **RK-S20** [ClosePseudoConsole](https://learn.microsoft.com/en-us/windows/console/closepseudoconsole) · mutable documentation · retrieved 2026-10-02
- **RK-S21** [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects) · mutable documentation · retrieved 2026-10-02
- **RK-S22** [Linux PTY manual](https://man7.org/linux/man-pages/man7/pty.7.html) · mutable documentation · retrieved 2026-10-02
- **RK-S23** [Linux cgroup v2](https://docs.kernel.org/6.12/admin-guide/cgroup-v2.html) · Linux 6.12 documentation · retrieved 2026-10-02
- **RK-S24** [Unicode text segmentation](https://www.unicode.org/reports/tr29/) · mutable documentation · retrieved 2026-10-02
- **RK-S25** [Unicode East Asian Width](https://www.unicode.org/reports/tr11/) · mutable documentation · retrieved 2026-10-02
- **RK-S26** [XTerm control sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html) · XTerm Patch 411 documentation dated 2026-08-23 · retrieved 2026-10-02
- **RK-S27** [Kitty keyboard protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/) · mutable documentation · retrieved 2026-10-02
- **RK-S29** [ncurses refresh](https://invisible-island.net/ncurses/man/curs_refresh.3x.html) · ncurses 6.6 manual; page date 2025-01-18 · retrieved 2026-10-02
- **RK-S30** [WCAG 2.2](https://www.w3.org/TR/WCAG22/) · W3C Recommendation WCAG 2.2 · retrieved 2026-10-02
- **RK-S31** [ARIA keyboard interface practice](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) · mutable documentation · retrieved 2026-10-02
- **RK-S32** [RFC 7464 JSON Text Sequences](https://www.rfc-editor.org/rfc/rfc7464) · RFC 7464 · retrieved 2026-10-02
- **RK-S33** [RFC 8949 CBOR](https://www.rfc-editor.org/rfc/rfc8949) · RFC 8949 · retrieved 2026-10-02
- **RK-S34** [RFC 8785 JSON Canonicalization](https://www.rfc-editor.org/rfc/rfc8785) · RFC 8785 · retrieved 2026-10-02
- **RK-S35** [RFC 7493 I-JSON](https://www.rfc-editor.org/rfc/rfc7493) · RFC 7493 · retrieved 2026-10-02
- **RK-S36** [Windows Terminal panes](https://learn.microsoft.com/en-us/windows/terminal/panes) · mutable documentation · retrieved 2026-10-02
- **RK-S38** [T3 connection runtime](https://raw.githubusercontent.com/pingdotgg/t3code/b33eda13998b5b0571daaf266c87f6f31af41f7d/docs/internals/connection-runtime.md) · b33eda13998b5b0571daaf266c87f6f31af41f7d · retrieved 2026-10-02
- **RK-S39** [Codex developer commands](https://learn.chatgpt.com/docs/developer-commands) · mutable documentation · retrieved 2026-10-02
- **RK-S40** [Terminal accessibility design record](https://raw.githubusercontent.com/microsoft/terminal/main/doc/terminal-a11y-2023.md) · Historical 2023 accessibility design record at mutable main; retrieval-pinned only · retrieved 2026-10-02
- **RK-S41** [tmux official build platforms](https://raw.githubusercontent.com/tmux/tmux-builds/main/README.md) · mutable documentation · retrieved 2026-10-02
- **RK-S42** [Unicode segmentation revision 49](https://www.unicode.org/reports/tr29/tr29-49.html) · Unicode 18.0.0 revision 49 · retrieved 2026-10-02
- **RK-S43** [Unicode width revision 46](https://www.unicode.org/reports/tr11/tr11-46.html) · Unicode 18.0.0 revision 46 · retrieved 2026-10-02
- **RK-S46** [Muse configuration and terminal preferences](https://dev.meta.ai/docs/muse-code/configuration) · mutable documentation · retrieved 2026-10-02
- **RK-S47** [tmux official installation and dependencies](https://github.com/tmux/tmux/wiki/Installing) · Official installation wiki; displayed revision 2025-12-22 · retrieved 2026-10-02
- **RK-S48** [OpenCode v2 TUI](https://opencode.ai/v2/docs/cli/tui/) · Mutable OpenCode v2 documentation; installed artifact unknown · retrieved 2026-10-02
