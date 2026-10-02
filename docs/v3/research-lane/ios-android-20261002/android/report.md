# Recursion Android client design and optimization recommendation

2026-10-02 UTC · Android companion · Research candidate 1  
Parent goal: `goal-recursion-v3-harness-orchestrator`  
Repository source: `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`  
Target implementation, prototype, device journeys and benchmarks: **UNEXECUTED**

## Recommendation and its limits

Recommend **Kotlin with Jetpack Compose for the Android application shell, ordinary controls and state-driven screens**, using a distinct Recursion design system. Keep **Kotlin with Views** as a genuine whole-screen comparator and permit a narrowly isolated Views or custom-rendered transcript/terminal surface only if an equivalent, accessible prototype demonstrates a useful improvement. Compose does not require the app to adopt Material's appearance. A custom Android identity can use Android's navigation, input, accessibility and lifecycle behavior while choosing its own visual language. [A01][A02][A03]

The reason for this starting recommendation is direct platform integration and the user's preference for two individually optimized applications. It is an advisory hypothesis, not evidence that Kotlin or Compose is always faster. Backend latency, parser work, unbounded transcripts, layout invalidation, radios and background activity can dominate language choice. A second, independent native app also adds review, test, release and maintenance obligations.

Modern **React Native with TypeScript, its New Architecture and qualified native integrations** remains a serious rival. Comparing only its historical asynchronous bridge would be misleading: the current architecture removes that bridge, and the 0.82 release made the New Architecture mandatory. There is no measured Recursion result establishing whether a native implementation's benefits outweigh shared-client development savings. [A04][A05][A06]

The later user instruction explicitly permits advisory language and UI-stack recommendations. It supersedes the earlier no-selection constraint only for this comparison. No repository decision is ratified; no app is built; no backend language, renderer implementation, transport, authentication mechanism, push provider, distribution route, minimum Android version or private offline retention policy is selected.

## Authority and evidence boundary

**SD** means source-documented platform behavior; **LO** means local static observation; **IN** means Recursion-specific proposal or inference; **U** means unknown until measured. Recommendations, proposed screens, test oracles and experiment budgets are IN. Expected test outcomes are not passes.

LO: this report inspected the read-only repository export and D-018 through D-034 in `state/DECISIONS.md`, together with CONTROL_PLANE, ANCHOR, AGENTS and START-HERE. Existing inputs remain unchanged:

- R-MOB `report.md`: SHA-256 `b44826c1e46bd64c7e8e710a5258dfa34a4a810a9d962f672b3d60c34c29c65e`
- R-UI `report.md`: SHA-256 `23fa223bc92fd53b6f5f82d27ea7bf7d4082f3e82f0653f190efd2e734efa931`, `recursion.ui-contract@candidate-2`
- Repository input commit: `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`; prior candidate pins remain historical provenance

The current user requests separate OS designs over the same backend. This companion adds Android treatment to the prior mobile/UI candidates; it does not revise operation meaning or introduce another canonical store. D-019's comprehensive opt-in capability surface remains intact. D-022's vocabulary is unchanged. D-028 specifies backend platform floors, not an Android minimum. D-029's trusted provider launch boundary remains a backend obligation. D-031 forbids unmeasured savings claims. D-033's cheap-port proposition remains falsifiable. D-034 makes mobile an optional client and remote execution an independent backend capability.

Only public documentation retrieval, local source reading and self-authored artifact QA occurred. No target script/import/test, app prototype, device/account/store/provider/model call, installation, credentials, network setting, live host, counsel contact, spending, publication, repository mutation or Work/Codex/cloud session was undertaken. Public source URLs were inspected on 2026-10-02 UTC. Mutable documentation snapshots are not installed-version evidence.

## Shared backend contract with separate Android presentation

IN, inherited from R-MOB and R-UI candidate-2:

1. Enrollment, authenticated session, read rights, control rights, input lease and work admission are separate. The mobile app is not an execution node or a provider-credential container
2. Protected controls require a **currently connected, authenticated client and current backend authorization**. A network indicator alone is insufficient. Every submit checks the exact operation, domain, target, argument content, relevant revisions, expiry and scope through the common gate
3. **Detach is not Stop**. Back, Home, activity destruction, force-stop, radio loss, lock, notification dismissal and app removal do not prove or request backend task termination. Mobile lifetime never owns backend actors
4. There is **no automatic offline action queue**. Offline text may be an unsent draft only under a chosen retention policy. Queue is a distinct accepted backend operation. Reconnect cannot turn a draft into a message, approval, steering command or Stop
5. A command sent online with a lost response remains ambiguous. Reconcile its canonical `(admitted_authority_domain, command_id)` and immutable content under current disclosure rights; never mint a fresh ID merely to make a spinner disappear
6. Private offline retention remains undecided. Even task names and last-seen metadata may be private. This report neither promises a cache nor treats online-only as a ratified choice
7. Receipt facts stay separate: intent saved, accepted, admission fenced, remote fence observed, interrupt delivered, owned process contained/exited, external effect settled, independently verified. No animation, push or socket close collapses them into success
8. Seven capability states remain independent: installed, enabled, authorized, available, selected, loaded and executed. UI support/render disposition is separate. Viewing an inert contribution never activates its plugin
9. Input and resize leases are per-target and distinct. Attach, focus, keyboard appearance and reconnect cannot claim either. Stop authority does not require stealing terminal input
10. Host-owned controls, continuity and attention remain available when an extension fails. Rich content gets a bounded inert representation and equivalent accessible fallback, or the affected action is unavailable with a reason

Model inference, task execution and canonical authorization remain on the backend; local projection parsing and rendering do not turn the Android client into an inference or execution host. Share semantic fixtures, versioned catalogs, refusal meanings, source-cut verification and command receipts across the two apps. For an initialized profile, attaching, viewing and opening a notification must cause zero new inference, task execution or plugin activation; authorized read synchronization has its own finite network/CPU budget. Any first activation is a separate explicit admitted operation. Share source code only where it reduces total verified cost. Do not force a common visual tree, gesture map, app lifecycle or system-permission abstraction that hides OS differences.

## Android design identity

### Candidate visual systems

IN: evaluate two deliberate Android visual candidates using the same semantic payloads.

| Candidate | Visual and interaction identity | Likely benefit to test | Cost or falsifier |
|---|---|---|---|
| A Opaque workspace | Solid light/dark surfaces, strong typographic hierarchy, thin separators, restrained elevation, labeled status strip, compact but spacious list rows; bottom destinations on compact windows and side navigation on wider windows | Stable contrast, clear scopes, low visual interference during long streaming work | Fails if density slows comprehension, critical actions need excessive navigation, or measured rendering/energy advantage is absent |
| B Layered panels | Opaque main workspace with a restrained tonal layer for contextual tools, progressive detail and an optional movable secondary pane on large windows | Faster comparison of task, attention and evidence without leaving the current context | Fails if layers obscure keyboard focus, confuse selected target, or add enough compositing/layout cost to miss budgets |

Candidate A is the preferred design probe. Candidate B is a real rival for complex work, not a deliberately poor negative control. Neither copies iOS glass. Translucency is not needed to establish the Android app's identity; decorative effects remain removable without losing meaning. System authentication/permissions remain recognizable system surfaces, not brand-skinned imitations. Light and dark themes must each pass contrast and focus checks. Optional system-derived accent colors cannot redefine semantic warning/Stop colors or become the only way to recognize state.

The design system owns a small set of explicit tokens: surfaces, primary/secondary text, separators, focus outline, warning/error/unknown states, control spacing, hit areas, text roles and motion settings. It must define pressed, focused, disabled, unavailable and disconnected appearances independently. A disabled action still needs a readable explanation. Custom appearance cannot delete platform semantics, selection, cursor, keyboard, magnification or accessibility support.

### Navigation and predictive Back

SD: Android's supported predictive Back path is version-sensitive; targeting/running Android 16 changes default system animations and legacy Back interception. Edge-to-edge behavior also depends on target and runtime. [A07][A08][A09]

IN: Android navigation is a location/state model, never a backend action shortcut. The visible destination hierarchy should be Workspace → task → attention/artifact/receipt detail, with Connection and Settings independently reachable. A search result may open a task but cannot silently switch control ownership. A scope strip names backend/domain, selected task/attempt and connection freshness whenever controls are visible.

Back behavior is specified per state:

- With IME visible, preserve normal keyboard dismissal behavior and leave the draft unsent
- From a transient panel, return to the underlying screen; do not approve, reject, resume or stop work
- From an unsent edited form, preserve only permitted draft state or ask about discard; cancellation restores the same state
- From a task detail, return to the prior list/filter/scroll context; existing backend work continues
- At the root, return control to system navigation. A predictive gesture canceled part-way changes neither destination nor backend state
- A deep-linked screen has an explicit return path. Back never follows a hidden command URI

A back-preview frame must not reveal a private previous screen before current disclosure is re-established. Navigation bookkeeping must be idempotent across canceled gestures, rotation and process recreation. The app must not consume every Back event just to log departure. OS Back and toolbar Up may differ in destination history, but both preserve the same no-effect invariant.

### Edge to edge and the keyboard

IN: let backgrounds extend beneath system bars while placing meaningful content and touch/focus targets within the actual safe geometry. Account separately for status/navigation/caption bars, display cutouts, system gesture regions and IME, including landscape and freeform windows. Avoid hard-coded bottom padding and double-applying overlapping insets. [A08][A10]

The task control strip must remain reachable when the IME opens, when a hardware keyboard disconnects, and when the taskbar/caption bar appears. Reflow the strip into labeled rows rather than squeezing scope text into an ellipsis that hides which agent will stop. A full-width bottom Stop strip is only a candidate: compare it against a stable top scope/control row under one-handed, large-font and keyboard workloads.

Terminal input requires an explicit Input mode with target and lease holder visible. Ordinary text selection and scroll do not imply terminal input. IME composition, autocorrect, paste and enter-key behavior must be tested separately from raw terminal key events. A keyboard shortcut must use the currently focused, explicitly scoped control context; focus change while a key is held cannot redirect a repeat to another task. Clipboard insertion is draft/input according to the exact reviewed operation, never an approval bypass.

### Adaptive windows and foldables

SD: window size classes describe available app space rather than device marketing categories. Fold posture and separation introduce additional geometry. For apps targeting Android 16, the documented large-display behavior removes several orientation/resizability restrictions under specified conditions. [A09][A11][A12]

IN: derive layout from current window geometry, usable space, font scale, input method and hinge/posture, not a phone/tablet flag. Use one pane when the actual content cannot support two readable panes. On wider windows use a task list plus detail; add evidence/attention as a third pane only when all remain usable. Large type can deliberately collapse a wide window to fewer panes.

A hinge/separating fold must not split an approval's consequential content from its submit control, cut through text, or hide the task scope. A tabletop posture can separate reading from controls, but its orientation is a layout convenience and grants no extra control rights. Preserve stable selected object, scroll anchor and focus when folding, unfolding, resizing or entering split screen. The canonical task identity does not change when its pane changes position.

Multi-window instances must not maintain independent optimistic input ownership. The app and backend still arbitrate one current input holder per target. Both windows may view the same task; only a fresh granted lease permits input. Window closure detaches that viewer, and a narrow remaining window must still expose Stop and continuity facts.

## Screen and control specification

IN: each screen is an Android materialization of candidate-2 semantics. All source-derived accessibility mechanisms are summarized later; the following behavior is Recursion-specific.

| Screen | Compact Android treatment | Expanded or foldable treatment | Required safety and accessibility facts |
|---|---|---|---|
| Backend and enrollment | Plain backend identity and role preview; distinct Connect, Authenticate and Enrollment status | Same sequence in a centered bounded panel; no multi-column security ceremony | Trust root, enrollment binding and exact intended backend; no QR-only trust or provider secret entry |
| Workspace | Bounded task list with stable row identity, unread/attention facts and explicit filter | Navigation rail/list plus selected task detail | Current read scope, last cut, gaps, unknown status; task names follow privacy policy |
| Task and stream | Single transcript with a pinned scope/control region and labeled jump-to-latest | Transcript and optional continuity/evidence pane | Source/attempt/turn, live versus stale, input holder, route capability and same-cut coverage |
| Attention | Ordered questions and approvals; full-screen review for consequential detail | Master/detail with review pane; no tiny approval popover | Waiter identity/revision, exact action/recipient/data/arguments, expiry and changed-content conflict |
| Queue and steering | Separate accepted Queue list and explicit Steer composer mode | Side-by-side draft and accepted items if readable | Unsent draft versus accepted versus delivered; exact active turn and route support |
| Stop and continuity | Visible selected target/mode plus accessible mode/scope review; receipt facts expand linearly | Owner/dependency scope tree with linear alternative and per-node evidence | Aggressive/Full/Lazy meaning, unreachable nodes and unresolved external effects |
| Artifacts and forks | Bounded text/diff first, explicit representation selector | Two-version compare with synchronized source identities | Authorized ArtifactRef/ContentEnvelope, source cut and evidence; neither side silently overwritten |
| Context and compaction | Inspectable context summary, limits and proposed transformation preview | Context/source evidence plus before/after comparison | Deterministic inspection versus admitted model-backed work, loss and allowance accounting |
| Commands and plugins | Search plus directly reachable mandatory controls; typed argument form | Capability/command list and explanation pane | Exact namespace/component/version/schema; seven states; unavailable and unknown differ |
| Settings and connections | Requested/effective settings, permission and connection method explanations | Two-pane categories/details with stable focus | Config revision, scope, preview/apply semantics; OS permission ≠ backend grant |

### All ten required controls

| Control | Android expression | Never infer | Decisive unexecuted oracle |
|---|---|---|---|
| 1 Streaming output | Virtualized/paged stream, pause visual follow, jump-to-latest and readable source/gap header | A visual animation is new canonical output; hidden reasoning exists | Same authorized cut matches the canonical projection, and mandatory facts survive coalescing |
| 2 Questions | Labeled form with waiter identity, options, expiry and cancel action | A restored draft answers a replacement waiter | Old waiter/generation is refused with zero new dispatch |
| 3 Approvals | Host-owned review of exact action, recipient, data and scope, explicit submit | System biometric success authorizes the displayed backend action by itself | Changing one consequential field invalidates the old approval |
| 4 Queued messages | Accepted queue with supported edit/remove operations, separately labeled local draft | Offline text is queued or delivered | No offline mutation; edit after delivery boundary refuses or reconciles honestly |
| 5 Active steering | Explicit Steer selection, active attempt/turn and route support | Queue fallback is equivalent to steer | Unsupported route cannot silently turn steering into delayed delivery |
| 6 Interruption | Persistent scoped Stop with three named modes and an evidence view | Back, disconnect or an OS task kill is Stop | Exact selected scope/mode reaches the same common gate as other clients |
| 7 Resume | Explicit current checkpoint/config/route review and resume command | Notification tap, unlock or reconnect resumes effects | Stale checkpoint/authorization prevents new admission |
| 8 Forks | Two preserved versions, source/context cut and allowance preview | A new screen inherits active grants or reservations | Both versions remain inspectable; inherited authority does not appear |
| 9 Compaction | Inspect/request/tune supported mechanisms with preview and receipts | A UI summary silently spends inference or discards evidence | Inspection is deterministic; model work needs ordinary admission and loss remains visible |
| 10 Commands and plugins | Typed catalog-bound forms and capability explanations | Viewing a widget installs/loads/executes a plugin | Unknown required semantics disable affected actions while core Stop survives |

### Three Stops with visible scope

**Aggressive:** selected agent, new dispatch fenced and forceful interruption requested without waiting for its current operation. Show descendants separately so the operator cannot mistake agent-only scope for all owned work.

**Full:** selected agent plus owned subagents, shells, monitors and relaunchers; fence return and restart. Display the included ownership set/revision and per-host/process observations. An unreachable host stays unconfirmed; an already-dispatched external effect can remain unresolved.

**Lazy:** close new admission and wait at a named observable operation boundary. Show boundary, deadline, waiting/timeout and configured escalation. A spinner alone cannot explain whether the boundary was reached.

`checkpoint`, `interrupt` and `drain` remain mechanisms, not fourth, fifth and sixth Stop modes. The mode selector and target are reviewable together. A one-tap action, if later chosen, must still expose its configured mode/scope before activation and preserve the shared command contract; this report does not impose an extra confirmation on every Stop. Offline, show **Stop unavailable while disconnected** and preserve the last observed state. Do not enqueue a surprise Stop for later. An online Stop with a lost reply becomes receipt reconciliation, not a claimed failure or automatic new command.

## Accessibility and inclusive control

SD capsules A13–A17 cover platform semantics, target sizes, contrast, font scaling, testing and keyboard behavior. Native widgets provide useful defaults, but a custom design still needs semantic and end-to-end tests. [A13][A14][A15][A16][A17]

IN: require complete journeys through all ten controls and every Stop mode using TalkBack, Switch Access, hardware keyboard and touch. Voice Access and magnification are additional profiles. Short accessible labels identify action and target; expanded descriptions expose scope and state. Repeated task/queue rows have stable identities and useful distinguishing information. A custom-rendered terminal must supply a semantic linear transcript and a separate accessible control path, not one enormous unlabeled drawing node.

The proposed touch floor is 48 × 48 dp; visible icon size may be smaller but overlapping invisible hit areas are unacceptable. Small text should achieve at least 4.5:1 contrast and qualifying large text at least 3:1, following the source's text-size qualifications. All states use text/shape as well as color. Test contrast on actual rendered backgrounds in light/dark themes, with any accent adaptation, disabled state and focus overlay. [A14]

Support maximum system font settings, including Android 14's documented nonlinear scaling up to 200%, without reducing the user's text choice to make controls fit. Use platform scaling; do not multiply every dimension by one assumed scalar. Long IDs can have separate expandable detail, but the meaningful target, action and consequence cannot be ellipsized beyond recognition. [A15]

The reading position and accessibility focus remain stable during streaming. Batch nonurgent announcements at semantic boundaries, expose new-output counts and an explicit read-latest action, and prioritize a new actionable waiter without repeatedly interrupting the user. Focus moves into a modal/pane predictably and returns to its trigger after dismissal. A receipt update announces the fact that changed, not all historical output.

Respect available system animation settings and offer a local reduced-motion mode for app-owned effects. Disable decorative parallax, pulsing, unnecessary auto-scroll and animated layout churn. The product must remain intelligible with zero app animation and with haptics disabled. That is a proposed product requirement, not a claim that every Android version exposes one uniform reduced-motion API. Timeouts, focus order and Stop availability must not depend on animation duration.

Switch scanning must not traverse thousands of stream tokens before reaching controls. Provide headings, panes and bounded groups plus an explicit content-navigation mode. Keyboard users need visible, unobscured focus, predictable tab/arrow order, an escape path from nested content and non-conflicting named shortcuts. No essential function requires drag, long press, precise gesture timing or simultaneous keys that cannot be replaced with an accessible action.

An automated accessibility scanner passing is not TalkBack usability, and TalkBack on one phone is not Switch Access, large-font or keyboard conformance. Human testing with disabled users remains an independently budgeted future qualification activity.

## Rendering and performance architecture

### Streams and bounded work

IN: distinguish four rates: canonical event production, authorized transport delivery, client presentation materialization and display refresh. They need not match. A 120 Hz display is not a requirement to emit 120 backend updates per second or reparse the transcript every frame.

Pipeline candidate: receive bounded authorized frames → validate identity/revision/limits → append or reconcile the allowed projection slice → perform bounded parsing/materialization off the critical input path → publish narrow view changes → render visible rows and controls. This describes responsibilities, not a selected transport, thread API or store. The independent control path must retain scheduling and memory capacity when presentation is flooded.

Bound the event count and bytes, maximum row/span size, parse nesting, image/decode size, rich-contribution count, in-flight work and per-view plus global credits. Virtualization reduces visible UI work; it does not itself bound the underlying retained history. A single giant text row or malicious unbroken token can defeat ordinary list virtualization. Use finite chunks with stable source identities, page old history and preserve explicit GAP/replay information.

Coalesce superseded presentation updates only after canonical facts are durable. Never coalesce away an approval change, revocation, scope change, gap, error, Stop receipt or effect uncertainty. If a stream outruns presentation, withdraw credit or reduce optional visual frequency. Do not move the backlog into an unbounded worker/channel/flow that merely hides it from the UI thread. Backend global caps must also bound many slow clients.

### Compose recommendation and escape hatches

SD: Compose separates composition, layout and drawing work; official guidance calls for stable list keys, narrow state reads and avoiding repeated expensive work. Its published scrolling comparison is a particular benchmark, not every app. Release optimization and measurement matter. [A03][A18]

IN: use stable immutable display identities, narrow state ownership and small independently updating subtrees. A new token should not invalidate the whole workspace, recalculate every task filter or rebuild all accessibility labels. Keep rich parsing, sort/filter work and cryptographic operations outside a render body. A monotonic event cursor and source identity are not the list index. Measure invalidations, allocations, layout and drawing independently rather than optimizing only recomposition counts.

A Views-heavy rival may offer a simpler bounded recycled transcript surface for a particular workload. A mixed surface is justified only when the measured benefit survives interoperability costs, semantic-tree bridging, focus restoration, IME behavior and maintenance. The availability of interoperability APIs is documented; its benefit here is unmeasured. [A35] A custom GPU/canvas path can be worse overall if text selection, TalkBack, Unicode layout and editing must be recreated. Render fidelity must include bidirectional text, combining marks, emoji, very long lines and hostile terminal/control sequences, not just English monospace output.

### Frame time and responsiveness

SD: Android's rendering guidance ties frame opportunities to refresh rate. The arithmetic intervals are approximately 16.67 ms at 60 Hz, 11.11 ms at 90 Hz and 8.33 ms at 120 Hz; those are display intervals, not an app-only CPU allowance. [A19]

IN: establish profile-specific thresholds only after baselines. Measure actual frame deadline overruns, p50/p95/p99 frame duration, freezes/ANRs, input-to-visible acknowledgement and input-to-backend admission separately. A quick pressed-state animation must not masquerade as backend acceptance. A slow remote link must not make local controls freeze. A renderer that meets median frame time but starves Stop during a burst fails.

Metrics also include cold/warm startup to usable authorized content, reconnect to honest current cut, stream-to-visible delay, scroll-anchor stability, peak/steady memory, allocation/GC behavior, CPU/GPU time, task completion, control mistakes and human repair effort. Capture display rate, thermal state, battery condition, compilation/profile mode and release configuration. Emulator smoothness is not physical-device battery or jank evidence. Macrobenchmark is a candidate harness, not a measurement already performed. [A20]

### Power and network cost

SD: Doze/App Standby constrain background activity, while manufacturer/user restrictions vary. Official connectivity guidance recommends avoiding unnecessary regular network work. [A21][A22][A23]

IN: the default client must not hold a wake lock, foreground service, exact alarm or tight polling loop solely to look permanently connected. Rendering and subscriptions follow actual visibility and permitted work. Stop decorative animations, expensive parsing and rapid freshness timers when hidden. Coordinate subscriptions for multiple panes/windows instead of multiplying them blindly. Battery saver may reduce optional visual refresh without hiding control facts.

Compare bounded foreground streaming, adaptive/coalesced presentation, and permitted hint-driven refresh. A push is only an invitation to revalidate state; correctness cannot require timely delivery. Disconnected retry uses finite backoff and jitter with visible connection state. Network availability does not imply backend authentication or reachability. Resubscribe with authorized cursors and explicit gaps, not full-history retransmission on every small interruption.

Power tests must account for radio wakeups, transferred bytes, keepalives, reconnects, wake-lock duration, screen brightness and display refresh as well as CPU. Continuous low CPU can still cost battery through radio activity. Report energy per representative completed journey and background idle delta against a no-client baseline. No claimed battery advantage is available yet.

## Activity lifecycle and recovery

SD: activity recreation, system process death and user dismissal have different state-survival behavior; ViewModel is not process-death persistence, and saved state is intended for small reconstruction data. [A24][A25]

IN: restore presentation locations and permitted drafts independently from current backend truth. Restored waiter IDs, grant references, selected Stop scope, lease or route revision are historical hints until revalidated. Never serialize bearer sessions, raw keys, approval authority or executable input into general saved state. Even reconstruction IDs need privacy classification.

| Transition | Android client behavior | Backend truth and oracle |
|---|---|---|
| Rotation, resize, fold | Preserve selected identity, allowed draft, scroll anchor and focus; avoid duplicate subscription | No new command, lease or duplicate admission |
| Home, lock, another app | Mark visibility; stop optional work; reconnect/revalidate when active | Already admitted backend work remains independent |
| System process death | Recreate minimal permitted navigation; authenticate and fetch current cut | Old state cannot authorize; online uncertain command reconciles same identity |
| User force-stop or app dismissal | No reliance on an exit callback; next launch has explicit freshness status | No claim that backend stopped or received detach |
| Reboot, reinstall, restore | Enrollment/session proof must be current; classify missing/invalid key | Restored files do not silently regain controller identity |
| Auth cancellation, lockout, key invalidation | Remain noncontrolling; show recoverable reason and explicit next path | No fallback to weaker assurance without approved profile |
| Network change in foreground | Suspend protected submit unless live authenticated; preserve uncertainty | Lost response is not new-command permission |

The client must be correct if Android kills it between any two UI events. No `onDestroy`/background callback is the sole place for essential command durability, authority revocation or backend termination. Offline draft loss is a separate user-experience failure from duplicate command dispatch. Private draft persistence cannot be silently chosen to fix lifecycle convenience.

## Device trust and local privacy

SD: Android Keystore's protection is key/device/profile-dependent; StrongBox is optional and has supported-operation/performance limits. Non-exportability does not prevent on-device misuse. Backup rules distinguish cloud backup, device-to-device transfer and newer cross-platform transfer behavior. [A26][A27]

IN: enrollment records the qualified protection profile instead of advertising every Android installation as equivalent. At least distinguish required hardware-backed profile, accepted lower-assurance profile and unsupported/unknown. Absence of StrongBox, unsupported algorithm or key invalidation must not silently degrade a required profile. Any fallback requires an explicitly accepted security profile, a truthful UI and fresh enrollment binding where necessary.

An account authenticator, device-bound installation key, unlock gesture and command approval solve different problems. An OS biometric prompt may gate a cryptographic operation in a qualified design, but does not know Recursion's operation/recipient/arguments unless the application protocol binds them. A successful local biometric event cannot refresh stale backend rights. Authentication timeout/fallback, changed biometric enrollment, no secure screen lock and lockout need separate fixtures. [A28]

Before any future implementation, classify enrollment handles, renewal/session material, private projection bytes, receipts, drafts, logs and diagnostic attachments. Configure and test explicit cloud-backup, Android device-transfer and applicable cross-platform-transfer exclusions independently; a manifest flag alone is insufficient evidence. Restored settings may be harmless while restored controller identity is not. A migrated phone must not acquire the old installation's control rights just because its files arrived.

Lock-screen notification redaction, recent-task snapshots, screenshots/recording, clipboard, keyboard suggestions, crash reports and accessibility exposure require an explicit privacy policy. Screen-capture restrictions can reduce accidental exposure but cannot prove protection against an already-compromised OS or another camera. Avoid credential-bearing URLs and any private data in diagnostics by default. Private offline content and retention duration remain Owner decisions.

Backend device revocation immediately fences new admissions according to the shared contract; an offline stolen phone may retain previously disclosed bytes. Client cleanup acknowledgements name exactly what was observed and removed. No universal remote-erasure, clone-proof or hardware-trust claim is made.

## Notifications and deep links

SD: Android 13 introduced runtime permission for nonexempt notifications; channel behavior is separately user-controlled. Verified App Links establish a routing association, not command authority. [A29][A30][A31]

IN: offer notification setup in context after the user sees its benefit. Denial, dismissal, channel silence or unsupported delivery is an ordinary operating state with an in-app attention inbox. Separate a small finite set of user-meaningful channels, such as questions/approvals, task status and connection/security notices; do not create one channel per task or evade a user's blocked channel by inventing a new one.

Use minimal, authorized, expiring notification references with redacted lock-screen text. Full prompts, source code, recipient data and approval arguments should not be notification payloads by default. Profile notification mirroring and recent-history exposure as separate disclosure paths. Dismissal means dismissal of a notice, not rejection of an approval or cancellation of a task. [A32]

A tap opens a bounded app route, establishes the intended backend/account, then authenticates and checks current read rights before showing private object details. It never approves, resumes, acquires an input lease, enrolls a device or sends a queued message. Wrong-backend, stale, revoked, replayed, modified, unverified and oversized links are distinct negative fixtures. Domain verification does not validate every path/query/argument. Treat all extras as untrusted input and use exact known routes, not arbitrary plugin command dispatch.

The first candidate provides **Open in app**, with consequential action review inside the authenticated app. A future notification action would require its own complete current-gate semantics and tests; no direct offline approval/Stop action is assumed. Receipt reconciliation happens before a stale notification becomes a live control. Delivery, display, user viewing and command acceptance remain distinct facts.

## Connection methods and VPN conflicts

SD: Android documents one active VPN service per user/profile; starting another replaces the existing service. User/profile boundaries and always-on behavior matter. [A33]

IN: represent connection methods as optional adapters, separate from Recursion identity and authorization. A direct qualified connection, existing overlay network, SSH-based tunnel or separately qualified relay are alternatives. Naming Tailscale or SSH as candidates does not install, authenticate, configure or select them. A UI can explain required existing setup without handling provider or administrator secrets.

Prefer a compatibility probe design that discovers current state without changing it. If a method depends on a VPN slot already used by a work VPN, firewall/privacy app or another overlay, explain the exact conflict and require an explicit user decision. Do not disconnect the current VPN, alter always-on/lockdown policy, bypass a work-profile restriction or silently switch transport. Work and personal profiles may have different network visibility and enrollment identities.

Show connection method, intended backend, current authenticated status, last successful synchronization and failure class separately. A VPN's connected badge is not a Recursion session. An SSH tunnel's existence is not a current task grant. A captive portal, split DNS problem, IPv6-only route, metered network, certificate/trust failure or network handover must not become an insecure fallback. Connection repair cannot automatically resend old intents.

An embedded VPN implementation has its own service, notification, battery and security burden; an external already-configured overlay has dependency and usability costs. Compare these costs without choosing a transport or vendor. No real network-change test was performed.

## Genuine technology alternatives

| Candidate | Why it can win | What must be measured or qualified | Falsifier and nonproof |
|---|---|---|---|
| Kotlin plus Compose, targeted Views where justified | Direct Android APIs, platform-oriented tooling, custom design tokens and coherent state-driven UI | Recomposition/layout allocation under floods; text/IME/accessibility; startup; interoperability cost | Reject preferred status if an equivalent rival meets safety/usability with materially better total cost; official endorsement is not Recursion performance |
| Kotlin plus Views for most UI | Mature explicit view lifecycle and controlled recycled/text surfaces; potentially simpler hot-path tuning for a given team | State complexity, adapter updates, layout depth, large-type/adaptive behavior, focus restoration | Reject if maintenance or state bugs offset any rendering benefit; a single fast scroll is not whole-app superiority |
| React Native plus TypeScript and current New Architecture | Shared application logic/components, experienced-team leverage and native integration where needed; independent OS styling is still possible | JS/UI scheduling, module availability, native integration/upgrade burden, list behavior, memory/energy and platform parity | Reject only on equivalent measured gates or unacceptable integration cost; old-bridge anecdotes and debug-build comparisons are nonproofs |
| Kotlin native UI with a separately shared non-UI core | Potentially reuse parsing, schemas and pure state logic while preserving OS UI | FFI/build/tooling/debugging cost, code-generation correctness, binary size and upgrade ownership | Do not choose a shared-core language until total verified cost is better; code percentage shared is not a benefit metric |
| Java plus Views | Existing expertise/components may beat a rewrite; Android APIs remain supported | Actual development and maintenance cost against Kotlin; equal runtime pipeline and tooling | No assumption that Java is intrinsically slow or Kotlin source is automatically faster |

A web-based wrapper is a useful accessible text baseline, but this request favors two OS-specific optimized applications and the wrapper must not be used to avoid native lifecycle/input/security qualification. A fully custom cross-platform renderer likewise owes the full text, semantics, input and OS integration surface; it is not selected merely because a graphics demo is smooth. These are scope-aware alternatives, not claims of measured ranking.

Native UI removes some abstraction seams, but it does not remove backend network round-trips or guarantee low memory/energy. TypeScript types do not replace runtime validation; Kotlin types do not replace current authorization. Both implementations need bounded queues, version negotiation, lifecycle handling and independent verification. The strongest shared asset initially is the protocol/fixture corpus, not a common screen implementation.

## AI assisted development hypothesis

IN: AI assistance can make separate codebases more plausible, but its speedup must be measured as **verified change throughput**, not generated lines or time to first compiling screen. No model/provider work was run for this research.

Use equivalent bounded work items in a future authorized trial: add one typed attention control, fix one adaptive/IME defect, repair one reconnect race, integrate one OS permission, and update one shared semantic contract in both applications. Record initial authoring time, review time, failed builds, debugging, rework, security/accessibility defects, regression coverage, dependency updates, OS-specific fixes and parity drift. Count human effort and allowed tool/inference cost across the entire accepted change, including repair after review.

A genuine rival is one shared implementation with platform adapters and distinct designs. Another is two native apps with shared generated models/fixtures. Compare against the team's actual ability to review Kotlin and Swift. AI-generated Kotlin that reviewers cannot confidently audit is not cheap because it arrived quickly. At least one maintenance-cycle or deliberately staged OS/contract change is needed before a two-app lifecycle-cost claim. A synthetic short trial supports only that trial.

Freeze task definitions and acceptance tests before assignment. Blind review where practical, preserve failed attempts, counterbalance order, and do not let one candidate omit security, accessibility or difficult terminal behavior. AI productivity is supported only if total reviewed delivery and defect outcomes improve without violating the same gates. If two-app parity failures consume the savings, the hypothesis is falsified for that scope.

## Test profiles and shared fixtures

IN: shared mobile fixture IDs below are aligned with the iOS companion. They specify outcomes, not pixel equality. Every entry is **UNEXECUTED**.

| Fixture | Android-specific stress | Oracle |
|---|---|---|
| MP01 Same cut and control parity | Different pane layouts and custom contribution renderings | Same authorized facts, ten operation meanings and typed refusals; unknown required semantics fail closed |
| MP02 Navigation and detach | Gesture Back commit/cancel, 3-button Back, Home, Recents, task dismissal | No implicit Stop, approval, resume or input takeover; correct local navigation |
| MP03 Connectivity and uncertain receipt | Metered/roaming/handover, VPN conflict, reconnect after send-before-receipt | No offline queue; reconcile exact identity; no duplicate effect or authority extension |
| MP04 Accessible controls and Stops | TalkBack, Switch Access, keyboard, font/display scale, zero motion | All ten controls and three modes usable with full scope visible; focus and reading stable |
| MP05 Stream flood and control reserve | Long history, hostile spans, rapid edits, extension flood, multiple views | Finite buffers and work; explicit gaps; Stop/attention responsive; no mandatory fact lost |
| MP06 Lifecycle restoration | Rotation, fold, resize, background kill, force-stop, reboot/restore | Historical presentation never becomes current grant; no duplicate or unsent-input replay |
| MP07 Device trust and backup | Qualified key profiles, no StrongBox, invalidated key, cloud/D2D/cross-platform restore | No restore-only controller enrollment or silent assurance downgrade; report unsupported clone exclusion and truthful recovery |
| MP08 Notifications and links | Permission denied/channel blocked/lock-screen; wrong/stale/forged link | No private disclosure before current read gate, no command from navigation, no dependence on delivery |
| MP09 Adaptive input | Fold hinge, freeform caption/taskbar, IME, hardware keyboard, multi-window | Scope and submit stay together; no obscured controls; single input/resize ownership |
| MP10 Power and background | Doze, battery saver, restricted app, low-memory and thermal stress | Backend continues independently; bounded client activity and honest staleness |
| MP11 Contribution failure | Unknown schema, duplicate identity, unsupported rich representation, renderer failure | Core Stop/attention/continuity survive; inert rendering never activates capability |

### Android profile matrix

The eventual platform floor remains open. Qualify runtime **and target SDK** separately. Include the chosen minimum, relevant behavior boundaries such as API 31 backup rules, API 33 notifications, API 34 font scaling and API 35/36 window/Back behavior, and the current intended shipping release. Later/preview APIs seen in mutable documentation are not automatically supported. Select exact OS build/security patch and library/compiler versions before running.

| Axis | Required representatives or contrasts | Why one device is insufficient |
|---|---|---|
| Hardware and OEM | Lower-memory supported phone, midrange and high-refresh phone, at least two OEM families; thermal-normal/throttled | Scheduling, key capabilities, power policy and display behavior differ |
| Geometry | Narrow portrait, landscape, small split window, tablet, foldable closed/open/tabletop, freeform if supported | Device class does not determine available app space |
| Input and navigation | Gestures and 3-button system navigation, IME variants, hardware keyboard/mouse, touch/stylus | Back, focus, composition and hit-target risks differ |
| Accessibility | TalkBack/Switch versions, max font/display scale, RTL/complex scripts, dark/light, high contrast where available, reduced motion | A screenshot or one semantic tree does not establish usability |
| Trust and restore | Supported hardware-key types, absent/invalidated key, lock settings, cloud/D2D/cross-platform restore profile | One successful biometric unlock does not prove enrollment/recovery |
| Network | Offline, constrained/latent/flapping, metered, captive portal, IPv4/IPv6, VPN/work-profile/lockdown cases | A Wi-Fi success does not establish connectivity correctness |
| Workload | One/ many task views, long transcript, bursty terminal updates, approval while parsing, plugin contribution flood | Average chat traffic hides control starvation and memory growth |
| Lifecycle and policy | Rotation, process kill, user force-stop, reboot, background restriction, Doze, permission denial | Visible foreground success is not persistence or background correctness |

Do not explode every axis into an unaffordable full Cartesian product. Use a risk-based pairwise suite plus mandatory high-risk combinations: stream flood + Stop + TalkBack; keyboard + large type + small split window; pending approval + process death + link reopen; wrong-key restore + revoked enrollment; VPN loss immediately after online send. Record excluded combinations explicitly. Device lab access and human participant testing require a later approved scope.

## Unknown budgets and bounded prototype handoff

No numeric product budget is qualified. The following registers prevent unknowns from turning into implied acceptance thresholds.

| Budget | Measurement needed | Decision withheld |
|---|---|---|
| Frame/input/Stop reserve | Deadline overruns and tail latency while flooding, with assistive services enabled | Per-profile response thresholds and reserve allocation |
| Memory/history | Steady/peak process memory, retention slope, huge-row and image limits, post-trim recovery | Transcript/cache ceilings and supported low-memory floor |
| Network | Bytes/event and completed journey, reconnect/replay bytes, credit occupancy | Framing/credit/batch/backoff values and keepalive policy |
| Energy | Idle delta, radio wakeups, CPU/GPU, wakelocks and energy per completed journey | Background/foreground battery targets and visual refresh defaults |
| Lifecycle | Restore time, same-ID reconciliation, draft recovery/disclosure | Private retention policy, saved-state payload and allowed offline view |
| Human use | Scope comprehension, error rate, time to reachable Stop/approval review | Layout density, default pane arrangement and shortcut choices |
| Engineering | Reviewed hours/change, parity defects, dependency/OS update cost | Final UI-stack adoption and amount of shared code |

**Future prototype packet, not execution authorization:** propose at most three Android variants: Kotlin/Compose, Kotlin/Views and modern RN/TypeScript. Use a finite synthetic local corpus with no account, real backend, provider calls, credentials or private content. Freeze exact dependencies, app package IDs, schemas and fixture manifests; no dependency or device setup occurs under this report. A mock backend can return inert recorded receipts, but cannot stand in for real admission proof.

The initial experiment scope is one task screen, attention review, all three Stops, connection loss/reconciliation and an adaptive layout transition. All ten control meanings are represented in the semantic fixture set even if some use simple accessible forms. Compare the same recorded event corpus, equivalent visual complexity and identical operation/content fidelity. Begin with normal data, long history and adversarial burst traces; exact finite event/byte counts and device-time ceilings must be frozen before approval.

The proposed bounded run envelope is no more than three candidate apps, two initial approved physical-device profiles, five journey types and three measured repetitions per candidate/profile/journey, after a separately specified warm-up. Cap each trace at five minutes and total instrumented runtime at 7.5 hours before exclusions/warm-up; setup, builds, warm-up and human review need their own explicit limits. These are planning caps, not statistical sufficiency or measured requirements. A failed hard gate stops that candidate's performance comparison pending diagnosis; do not keep spending to rescue a desired winner. Broader profile qualification is a separate packet.

Record cold/warm and compilation states, randomized run order, display/thermal/network conditions, corpus hash and exact app build. Compare confidence/variability honestly; three repetitions provide limited evidence and may require a separately approved follow-on design. Store traces and failures, not just averages. Measure instrumentation overhead and avoid declaring emulator power readings to be device energy.

Hard oracles precede optimization: no unauthorized effect, no offline action replay, exact command identity, bounded memory/work, same-cut facts, accessible core controls, truthful uncertainty, no lease theft, no private pre-auth disclosure. Then apply the inherited ordering of responsiveness, subscription/resource efficiency and completion with the complete cost vector. A quicker screen that hides an unresolved effect fails before it can win a benchmark.

## Inherited legal and distribution gate

The existing R-MOB counsel checklist and G-32 remain open. A custom native Android UI does not clear Play remote/code behavior, payments, privacy, signing, export or distribution obligations. Exact app behavior, supported routes and distribution profiles still need the prior product-specific review; no legal advice, store acceptance, terms clearance or publication authority is asserted. No counsel, store or account was contacted.

## Decision questions that remain

The next Owner decision can accept or reject the **Kotlin/Compose advisory baseline and opaque Android design probe** without accepting a final build or platform floor. Before implementation, settle supported Android profiles, private offline retention, device-assurance fallback policy, notification disclosure, allowed prototype environments and finite experiment budgets. Authentication, transport, push vendor and distribution remain separate decisions.

The decisive outcome is not that one toolkit is fashionable or that AI produced more code. It is an independently verified Android application that preserves Recursion's authority and continuity while making frequent controls clear, responsive and accessible on the intended devices, at an accepted total development and operating cost.

## Primary public source capsules

All retrieved 2026-10-02 UTC. Unless a release/API version is named, these are mutable official documentation snapshots, not immutable source-code pins. No external prose is quoted. Capsules contain the narrow documented facts; proposed Recursion behavior above is synthesis. The companion source ledger counts repeat motifs and canonical redirects conservatively, including overlap with prior R-MOB and coordinated iOS/RN use.

- **A01** Android Kotlin-first guidance: Android recommends Kotlin for new apps while retaining Java API support; Compose is Kotlin-oriented. This supports an integration recommendation, not a universal speed or productivity claim
- **A02** Compose custom design systems: Material theming can be extended, partly replaced or replaced entirely through public APIs. Choosing Compose does not force a Material-branded visual identity
- **A03** Compose performance: its published Pokedex hero comparison reports scrolling-jank parity with Views from Compose 1.9; release/R8 and profile configuration matter. The result is workload-specific
- **A04** React Native architecture overview: JSI replaces the historical asynchronous bridge; concurrent rendering and batching are supported. Enabling the architecture alone need not improve an application's performance
- **A05** React Native 0.82 release, 2025-10-08: the release runs only on the New Architecture. Older overview opt-out instructions are not applicable to that release
- **A06** React Native performance overview, updated 2026-08-12: JavaScript and main-thread work have different responsiveness effects, and release builds are required for meaningful comparison. It is guidance, not a native-versus-RN benchmark
- **A07** Predictive Back guidance, updated 2026-10-01: supported callbacks participate in system navigation; interception should follow UI state. Android 15 exposes supported system predictive animations without the earlier developer-option gate
- **A08** Edge-to-edge Views guidance: targeting API 35+ on Android 15+ extends content behind system bars; meaningful tappable content requires appropriate insets. Gesture, cutout and bar insets address different overlaps
- **A09** Android 16 target changes: target/runtime API 36 affects Back and edge-to-edge opt-out; targeted large displays of smallest width at least 600 dp ignore specified orientation/resizability/aspect restrictions. Exceptions and profiles matter
- **A10** Software keyboard guidance: keyboard visibility and geometry are represented through window insets; animation handling is version-dependent. The mutable page also describes newer API 37.2 behavior, which this report does not adopt
- **A11** Window size classes: decisions should follow current available application-window space, which can change during execution, rather than assuming a device always has one fixed layout
- **A12** Fold-aware guidance: folding features and posture can influence how panes are arranged. A large window and a physical fold are separate layout inputs
- **A13** Android accessibility principles: meaningful labels/actions, semantic grouping and alternatives to gesture-only operations support TalkBack and Switch Access. Existing control defaults still require correct application semantics
- **A14** Make apps accessible, updated 2026-09-22: guidance recommends 48 dp touch targets, 4.5:1 for smaller text and 3:1 for qualifying larger text; custom controls require deliberate semantics and testing
- **A15** Android 14 features: nonlinear font scaling reaches 200%; text uses platform-scaled units and should be tested at the maximum. A single hard-coded scale factor does not model it accurately
- **A16** Accessibility testing: combine manual assistive-service use, analysis tools, automated checks and user testing. No one technique is a complete substitute for the others
- **A17** Keyboard navigation: focusable controls and predictable focus traversal are needed for non-touch navigation. Keyboard operation requires deliberate verification rather than assuming a touch UI transfers intact
- **A18** Compose performance practices: stable lazy-list keys, limited unnecessary recomposition and moving expensive calculations out of repeated UI work can reduce avoidable cost; actual gains need profiling
- **A19** Android slow rendering, updated 2026-09-21: higher refresh rates shorten frame intervals; tracing and release-like configurations help diagnose jank. Visual inspection alone gives limited causal evidence
- **A20** Macrobenchmark guide: whole-app journeys can be benchmarked with controlled startup/compilation and measurement configuration. The harness itself does not establish a fair corpus or acceptable threshold
- **A21** Doze and App Standby: background CPU/network/alarm behavior is constrained and work may be deferred. An application cannot treat an inactive phone as a continuously available foreground connection
- **A22** Background restrictions: user restrictions and manufacturer behavior can constrain jobs, alarms and network work. Foreground success does not establish reliable background execution
- **A23** Regular network updates: unnecessary periodic traffic and radio activity can consume power; the source discusses reducing regular-update costs. It does not select a Recursion streaming or push transport
- **A24** Save UI state: configuration recreation and process death differ; ViewModel does not survive system process death; small saved reconstruction state and durable storage serve different purposes
- **A25** Process lifecycle: Android can reclaim app processes according to lifecycle importance. Application correctness cannot require indefinite background process survival
- **A26** Keystore: secure-hardware support varies by key operation and device; StrongBox is optional, constrained and not equivalent to invulnerable key use. Extractability and authorized invocation are distinct
- **A27** Auto Backup: cloud, device-transfer and newer cross-platform-transfer rules are distinct. Some manufacturers do not disable device transfer through allowBackup=false alone. Rule omission and restore behavior need profile testing
- **A28** Biometric authentication: system prompts can gate supported cryptographic operations, with authenticator/fallback and key-invalidation details depending on configuration. A local authentication result is not an application authorization protocol
- **A29** Notification permission: Android 13+ applies runtime permission to nonexempt notifications; allow, deny and dismiss have distinct behavior. A user denying permission is an expected state
- **A30** Notification channels: channel behaviors are separately user-controlled; once created, the app cannot freely rewrite importance and behavior to override those choices
- **A31** App Link verification: app/domain association affects routing and verification state can differ. Verification does not validate Recursion object scope, freshness or action authority
- **A32** Notification construction: lock-screen visibility and public alternatives can control displayed content. They do not make the whole delivery/mirroring/history path private by themselves
- **A33** Android VPN guidance: one active VPN service is supported per user/profile, and activating another stops the current service. An adapter must consider existing VPN and profile policy
- **A34** React Native 0.84 release, 2026-02-11: Hermes V1 became the default JavaScript engine on Android and iOS. This is a version landmark, not a claim that 0.84 is today's newest release
- **A35** Compose interoperability: Compose and Views can coexist through supported interoperability APIs. Interoperability availability is not evidence that mixed surfaces are free of lifecycle, focus or performance cost

[A01]: https://developer.android.com/kotlin/first
[A02]: https://developer.android.com/develop/ui/compose/designsystems/custom
[A03]: https://developer.android.com/develop/ui/compose/performance
[A04]: https://reactnative.dev/architecture/landing-page
[A05]: https://reactnative.dev/blog/2025/10/08/react-native-0.82
[A06]: https://reactnative.dev/docs/performance
[A07]: https://developer.android.com/guide/navigation/custom-back/predictive-back-gesture
[A08]: https://developer.android.com/develop/ui/views/layout/edge-to-edge
[A09]: https://developer.android.com/about/versions/16/behavior-changes-16
[A10]: https://developer.android.com/develop/ui/views/layout/sw-keyboard
[A11]: https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes
[A12]: https://developer.android.com/develop/ui/compose/layouts/adaptive/foldables/make-your-app-fold-aware
[A13]: https://developer.android.com/guide/topics/ui/accessibility/principles
[A14]: https://developer.android.com/guide/topics/ui/accessibility/apps
[A15]: https://developer.android.com/about/versions/14/features
[A16]: https://developer.android.com/guide/topics/ui/accessibility/testing
[A17]: https://developer.android.com/develop/ui/views/touch-and-input/keyboard-input/navigation
[A18]: https://developer.android.com/develop/ui/compose/performance/bestpractices
[A19]: https://developer.android.com/topic/performance/issues/render
[A20]: https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview
[A21]: https://developer.android.com/training/monitoring-device-state/doze-standby
[A22]: https://developer.android.com/develop/background-work/background-tasks/bg-work-restrictions
[A23]: https://developer.android.com/develop/connectivity/minimize-effect-regular-updates
[A24]: https://developer.android.com/topic/libraries/architecture/saving-states
[A25]: https://developer.android.com/guide/components/activities/process-lifecycle
[A26]: https://developer.android.com/privacy-and-security/keystore
[A27]: https://developer.android.com/identity/data/autobackup
[A28]: https://developer.android.com/identity/sign-in/biometric-auth
[A29]: https://developer.android.com/develop/ui/compose/notifications/notification-permission
[A30]: https://developer.android.com/develop/ui/compose/notifications/channels
[A31]: https://developer.android.com/training/app-links/verify-applinks
[A32]: https://developer.android.com/develop/ui/compose/notifications/create-notification
[A33]: https://developer.android.com/develop/connectivity/vpn
[A34]: https://reactnative.dev/blog/2026/02/11/react-native-0.84
[A35]: https://developer.android.com/develop/ui/compose/migrate/interoperability-apis
