# Recursion iOS language design and optimization recommendation

2026-10-02 UTC · iOS advisory companion · Parent goal `goal-recursion-v3-harness-orchestrator`  
Repository source pin `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`  
Shared UI reference `recursion.ui-contract@candidate-2` · Mobile reference R-MOB dated 2026-10-02  
Status: reviewed research candidate for Owner consideration; documentary review does not establish runtime acceptance. All app prototypes, device tests and performance experiments **UNEXECUTED**

## Recommendation and scope

**Recommend Swift for the iOS app, SwiftUI for the native application shell and ordinary state-driven screens, and a deliberately small UIKit integration boundary for any transcript, text-selection, terminal or interaction hotspot that measurements show needs it.** This is the strongest starting point for the user's separately optimized iOS app and glassmorphic direction. Use Apple's actual system materials and controls where available, with readable content surfaces and a fully usable opaque/reduced-motion presentation. Do not build a custom glass renderer merely to resemble Apple's screenshots.

The recommendation is about platform fit and controllable engineering risk. It is **not** a measured claim that Swift, SwiftUI or UIKit beats every React Native implementation. No Recursion mobile implementation has been benchmarked. Start native because the desired differentiation is specifically iOS behavior, accessibility, materials, lifecycle and input integration, while the backend already supplies shared product semantics. Let representative workload evidence decide whether particular screens need UIKit, rather than requiring every screen to use one framework.

The later user clarification explicitly authorizes language and UI-stack advice and expresses reduced interest in React Native. It supersedes the earlier no-language-selection constraint for this advisory comparison only. It does not ratify a repository architecture, authorize application construction, choose deployment floors, or select authentication, transport, storage, provider, distribution or a final rendering implementation. D-018 through D-034 remain intact. D-019's comprehensive opt-in capability surface is preserved; older terminal-first prose does not silently remove accepted GUI/mobile obligations.

**Two apps, one product contract:** iOS and Android may differ in navigation, typography, material, density, input conventions and rendering strategy. They must not differ in command meaning, authority, receipt facts, source-cut honesty or effect accounting. A shared backend and parity corpus are mandatory; a shared UI implementation is not. An always-running backend is an intended deployment shape, not evidence of phone reachability or permission for idle inference.

Evidence classes used here: **SD** public/source-documented behavior; **LO** inspection of supplied source bytes or this report's static checks; **IN** Recursion-specific recommendation or test design; **U** unknown/unmeasured runtime result. Unless explicitly marked SD or LO, design statements are IN. A source's published performance claim is never transferred to Recursion.

Only public documentation research, read-only inspection and self-authored report QA occurred. No app was created, built, signed, installed or launched; no account, store, device, provider/model, push, live host, credential, counsel, paid, deployment or Work/Codex/cloud-session operation occurred. Future experiment instructions are a handoff, not executed work.

## Language and implementation choices

| Approach | Advisory disposition for this iOS app | Genuine advantage to test | Main uncertainty and falsifier |
|---|---|---|---|
| Swift with SwiftUI shell and targeted UIKit | Recommended starting baseline | Direct platform surface; isolate ordinary forms/navigation from specialized rendering; small, explicit interop seam | Reject the proposed split if bridge lifetime/focus/state bugs or complexity outweigh measured benefits |
| Swift with predominantly UIKit | Strong conforming rival | Explicit control over reusable views, text systems, layout and input ownership may suit demanding transcript/terminal surfaces | Prefer it if it materially improves qualified journeys or total maintenance; do not assume imperative code is faster |
| SwiftUI throughout | First implementation candidate within the recommended baseline | Fewer interop boundaries and one UI dataflow model | Retain it if it meets all gates; reject a hotspot only after profiling demonstrates a material miss |
| Current React Native with native components where needed | Legitimate comparator, not the preferred starting point for this request | Shared UI/application code could reduce some changes across platforms | Native integrations, iOS fidelity, resource overhead and maintenance must be measured on the same current profile; a slow legacy demo is not evidence |
| Native iOS UI with a separately shared non-UI library | Optional later comparison | Reuse pure codecs, schema validation or deterministic projection transforms | Additional bindings, build chains, debugging and security review may cost more than duplicated small pure modules; no shared language selected |
| Objective-C or C/C++ in narrow existing components | Compatibility or measured-specialist option | Reuse a qualified existing component when its boundary is worthwhile | No reason established to make these the greenfield application language; low-level access does not automatically improve whole-app responsiveness |

**SD A15.** Apple supports integrating SwiftUI into UIKit with hosting controllers and wrapping UIKit views/controllers for SwiftUI. This establishes a supported mixed-framework route, not cost-free integration or performance equivalence. [UIKit integration][A15]

**SD A16.** Apple's TextKit 2 material exposes text-layout and viewport management, selection and custom text elements. It is relevant prior art for a specialized text surface; the sample does not establish Recursion terminal semantics, streaming throughput or accessibility at scale. [TextKit 2][A16]

**SD RN1.** React Native 0.82 made the New Architecture the only runtime option. Older opt-out guidance does not describe that release. [0.82 release][RN1]
**SD RN2.** React Native 0.84 made Hermes V1 the default. Freeze the actual version and engine in comparisons. [0.84 release][RN2]
**SD RN3.** The New Architecture replaces the old asynchronous bridge with JSI and supports concurrent rendering. Its documentation explicitly declines an automatic performance improvement guarantee. [Architecture][RN3]
**SD RN4.** React Native's performance guide distinguishes JavaScript and UI-thread work and recommends release-build testing. [Performance guide][RN4]

**The correct comparison unit is the whole workload.** This is a thin authenticated remote-control client: inference and execution remain on the backend. Its likely local bottlenecks are event coalescing, text layout, scrolling, blur/compositing, network/reconnect handling and lifecycle transitions, not model execution on the phone. Language, UI toolkit, text renderer, dataflow, batching, transport framing, allocation behavior and glass compositing are separate variables. A native app can still block its UI with decoding or repeatedly relayout an entire transcript. An optimized cross-platform app can use native scrolling and native custom components. Compare equivalent semantics and visual requirements, not a polished native build against a debug cross-platform straw man.

AI-assisted implementation can lower some authoring effort, but the relevant hypothesis is **reviewed end-to-end cost**, including requirement interpretation, parity regressions, debugging, accessibility, device/OS coverage, signing preparation, dependencies, tooling and annual platform changes. Two generated apps can diverge twice as quickly if review is the bottleneck. Record engineer review/correction time and defect escape alongside code-generation time. Share contracts, generated fixtures and test data first; only share executable client code when a measured benefit survives those costs. No productivity multiplier is assumed.

## Platform evidence and the glass direction

All cited public sources were retrieved on 2026-10-02. Apple documentation is mutable; source URLs and dated WWDC sessions are observation pins, not cryptographic snapshots or installed-build qualifications. Current documentation includes the 27-generation design refinements. An SDK's existence, a session demonstration or API listing does not select a minimum OS or establish a required API's status on a future qualified build.

**SD A01.** Standard SwiftUI/UIKit components acquire system Liquid Glass appearance and adaptive behavior. Apple's adoption guide warns that custom navigation/control backgrounds can interfere, and calls for testing custom elements under display and accessibility settings. [Adopting Liquid Glass][A01]
**SD A02.** HIG Materials distinguishes regular and clear variants, limits clear glass to visually rich backgrounds, and recommends sparse custom use. Appearance responds to system preferences including reduced transparency and increased contrast. [Materials][A02]
**SD A03.** Apple's WWDC26 platform session describes revised glass diffusion, edge definition and user-adjustable tint, with supported components adapting to accessibility settings. These are documented platform refinements, not proof that a chosen Recursion palette remains readable. [Platforms State of the Union 2026][A03]
**SD A04.** The custom-glass guide recommends combining related effects in `GlassEffectContainer`, warns against excessive containers/effects, and describes standard controls' touch/pointer response. Grouping is an optimization opportunity, not permission for unlimited effects. [Custom Liquid Glass][A04]
**SD A05.** Apple's rendering guide warns that updates behind glass cause additional calculations, overlapping layers can cause redraw work, and grouping distant controls can enlarge affected regions. It recommends inspecting actual updated regions. [Rendering efficiency][A05]
**SD A34.** Apple's original Liquid Glass design session places it in navigation and controls, discourages glass content tables, and warns against stacking glass on glass. [Meet Liquid Glass 2025][A34]

**SD A35.** Apple introduced the Liquid Glass system design with iOS 26 and iPadOS 26. [Platform release announcement][A35]

That availability boundary does not select Recursion's minimum OS. An approved older target needs a conventional readable material fallback; newer 27-generation refinements remain profile-specific. Pin exact API availability and SDK behavior during later implementation qualification.

### Candidate visual system

Use a calm, highly legible content canvas for task text, evidence, diffs, queue entries, exact approval arguments and receipts. Reserve glass for the OS navigation/control layer and selected compact controls. Glassmorphism here means depth, separation and familiar system interaction; it is not a requirement to refract every row or keep an animated wallpaper running.

- Use regular system material as the initial control-layer candidate. Clear glass is a poor default experiment for dense, unpredictable terminal/text backgrounds; consider it only for a distinct visually rich surface that passes readability tests
- Never place essential approval facts, an unresolved-effect count or the selected Stop scope behind a competing translucent layer. Content can extend visually under bars while its readable region and scroll positions keep required facts unobscured
- Avoid custom glass on both a container and its children. Do not put glass on every message bubble or stream row. A sheet's system material is not a reason to give each form field another blur layer
- Keep status meaning in words and symbols. Glass tint, red, animation, haptic feedback and material brightness supplement meaning; none establishes backend truth
- Preserve the user's display preference. A solid, high-contrast control background and restrained transitions are first-class presentations, with identical controls and state. Do not label them a degraded product
- Pin design behavior by OS/SDK profile. Use availability-aware system components or a readable conventional-material fallback on an approved older profile; do not emulate an unavailable Liquid Glass shader as a compatibility requirement

The strongest rival is a mostly opaque system-control style with a smaller glass footprint. It can satisfy the user's direction through a limited navigation treatment if the fuller candidate fails readability, energy or control access. The falsifier is not a subjective screenshot preference alone: require wrong-target/approval errors, inaccessible content, materially worse control reach, or measured resource regression under the agreed visual brief. Neither appearance establishes security or performance.

## Screen and navigation candidate

**Compact iPhone:** use a small stable set of destinations for work, attention and connection/settings, with task navigation below them. Exact destination names/order remain a usability decision. A task screen shows the target identity, backend connection/freshness, an accessible Stop affordance, the authorized timeline and a context-bound composer. Do not make a horizontally panning desktop dashboard the phone's default.

**Expanded iPad:** the same information architecture can become a sidebar, task list/detail and optional inspector. An additional window is another authorized view, not another executive or input holder. Collapsing columns must preserve selected task identity and unsent draft scope. Use available size and window traits rather than assuming every iPad has room for three columns. A phone presentation in a resizable environment also needs narrow and wide-window tests.

**SD A06.** Apple's Layout guidance, updated 2026-09-09, calls for adaptation to actual size classes, orientation, text size, localization and multitasking. Safe areas account for obscuring hardware and system UI; larger text can require stacking and growing rows. [Layout][A06]
**SD A07.** HIG Sheets reserves sheets for contextual tasks, recommends alternatives for complex flows, discourages nested sheet stacks, and distinguishes cancel/close from saving. It describes expandable detents and form/page-sheet presentation on iPad. [Sheets][A07]

| Screen | Proposed behavior | Required safety and continuity detail |
|---|---|---|
| Backend connection and enrollment | Show intended backend/domain, device enrollment, trust/identity confirmation and connection diagnostics separately | A tunnel icon is not authentication; pairing grants no task authority, node role, provider access or spending |
| Work overview | Bounded authorized task rows, last source cut and useful attention state; lazy details | Historical rows never imply running-now; unavailable inventory does not become an empty account |
| Task detail and transcript | Stable speaker/role/route/task attribution; bounded visible history; follow-latest toggle; jump-to-latest marker | User reading position and selection survive append. Missing history and render lag are different. No invented hidden reasoning |
| Attention list | Separate questions, approvals and blockers with exact target and expiry | Count is scoped to authorized projection; opening a row neither answers nor approves |
| Approval review | Full-height detail for long exact arguments/data/recipient/scope; readable explicit decision controls | Freeze reviewed immutable identity/revision. If changed, require a fresh review; never submit against the newly focused task |
| Question form | Schema-driven inputs, validation, expiry and explicit answer/cancel operations | Dismissing a sheet leaves waiter unanswered. Replacement waiter cannot inherit old text as an answer |
| Stop view | Visible target, selected mode, scope and mode-specific boundary/deadline; receipts below | Accessible from task/attention review even with keyboard or sheet present; no destructive swipe-only shortcut |
| Queue and steering | Explicit local drafts versus accepted backend queue; a separate current-turn steering action | Queue edit/remove race yields typed result; steering cannot silently become enqueue |
| Continuity and receipts | Inspect independent facts and observers, coherent snapshot/cut and unresolved effects | A spinner, socket recovery, saved draft or successful view transition is not admission, delivery or settlement |
| Fork and compaction review | Exact source/context revision, loss and allowed budget/lineage preview | Preserve both fork versions; inspection is deterministic and model-free; transformation requires ordinary admission |
| Capability/settings inspection | Host-owned typed controls with supplying namespace/version and capability states | Viewing settings does not load/activate operational plugins, invoke models or change authority |

A short mode selection can use a sheet; a long approval should expand or navigate to a full-height review before submission. Keep one contextual sheet at a time. The host safety shell must provide an accessible route to the selected task's Stop while an approval is open, without submitting, discarding or reinterpreting that approval. One candidate is a named Stop action inside the review's host toolbar that switches to a control view while preserving the inert draft. Test a nonmodal inspector on wide iPad as a genuine rival. Do not rely on a modal underneath being tappable.

System Back, a dismissal gesture, Home, lock, app switch or last-window close changes presentation lifetime. It never means Stop, approval, waiter cancellation or execution resume. If a local draft would be lost, use the established draft/discard policy; do not invent an automatic outbound queue to protect it.

## Exact shared controls and authority

The following is a presentation mapping, not a new operation catalog. R-L/R-UI own operation identities and support facts. All ten controls remain discoverable with supported, blocked, unavailable or unknown reasons safely disclosed. Rendering an affordance does not qualify any route.

| Required control | iOS expression | Exact same-gate obligation |
|---|---|---|
| Streaming output | Bounded semantic transcript with source identity, cut, cursor and gap marker | No fabricated content; display only currently authorized projections |
| Questions | Accessible current waiter form | Exact interaction ID/generation/revision/turn/schema/expiry; stale answer refuses without retargeting |
| Approvals | Trusted full disclosure and explicit decision | Exact action digest, arguments, data, recipient, scope, principal and revision; no local optimistic approval |
| Queued messages | Accepted queue list with edit/remove; unsent draft shown separately | Expected queue revision and actual delivery boundary; accepted is not delivered |
| Active steering | Explicit current attempt/turn action | Captured target and supported delivery policy; unsupported steer is not silently queue |
| Interruption | Persistent host-owned Stop route | Selected Aggressive/Full/Lazy mode, exact scope and admission fence; no focus-derived target substitution |
| Resume | Explicit inspected checkpoint continuation | Current route/config/grants and unresolved-effect validation; attach is not effect resume |
| Forks | Coherent source/context/candidate review | Preserve source and fork, lineage and conserving allowance split; no copied active grants/reservations |
| Compaction controls | Inspect/request/tune supported mechanism | Current context epoch/governor and loss/rehydration references; no model call just to inspect |
| Commands/plugins | Typed command discovery and forms | Exact namespace/component/version/schema and seven independent capability facts; disabled means no hidden activation |

### The three Stops

- **Aggressive:** selected agent, fence further dispatch and force interruption without waiting; list descendants separately; in-flight effects may remain uncertain
- **Full:** selected agent plus owned subagents, shells, monitors and relaunchers; fence return/restart paths; expose per-host/process results, unreachable recipients and unresolved external effects
- **Lazy:** close admission and stop at the named observable operation boundary; show deadline, waiting/timeout and configured escalation

**Disconnected Stop is unavailable:** display that fact persistently beside the selected target; refuse submission and never queue a deferred Stop for reconnection. If a Stop was sent while online and its response was lost, preserve its uncertain status and reconcile the original command identity, without a new dispatch or a fresh ID.

`checkpoint`, `interrupt` and `drain` remain mechanisms, not extra modes. Socket close, a killed process and source interruption never establish external rollback. Show the truthful result, for example: Full Stop accepted; local dispatch fenced; remote node unconfirmed; one effect unresolved. Never collapse that into everything stopped.

**Current permissions are checked, not remembered as a UI boolean.** Viewer, controller and per-target input holder are separate facts. Stop rights are separate from terminal input/resize ownership. A passive reader may reflow locally but cannot send upstream INPUT/RESIZE. Focus, keyboard appearance, window activation and reconnection transfer no lease. Preserve separate typed `input_lease` and `resize_lease` references and target/daemon/process incarnation.

Every protected read validates current principal, object, privacy domain, audience, purpose and retention restrictions before sensitive metadata lookup/disclosure. Every effect command additionally validates exact action/arguments, captured task/attempt/turn, route/config revision, grant/work/pause/writer bindings, resource limits, any required lease and a currently authenticated connected backend session. If required facts are unknown, refuse safely and explain only authorized metadata. Device enrollment and OS biometric success are not work authorization.

Command identity remains `(admitted_authority_domain, command_id)`. Same key and immutable content recovers the authorized historical disposition with zero new dispatch; changed immutable content conflicts. A missing receipt cannot be repaired by minting a fresh effect ID. Preserve R-L typed error fields and retryability `never|same-id|after-refresh|reconcile`; do not extend M1B's closed refusal vocabulary to express a screen design.

Keep the shared eight receipt dimensions **saved_locally, received, delivered, admitted, started, observed, settled, verified**, with subject/observer/cut/evidence. R-L's own labels and mappings remain intact. They are independent facts, not a universally ordered progress bar. A local tap can be shown immediately as local input recognition, but must not be styled as backend acceptance.

## Accessibility and input acceptance

**SD A08.** Apple's accessibility guidance calls for labeled controls and testing with assistive technologies including VoiceOver, Switch Control, Voice Control, Pointer Control and Full Keyboard Access. [Accessibility][A08]
**SD A09.** SwiftUI exposes Reduce Transparency; Apple's guidance for that value requires opaque rather than semitransparent UI backgrounds. [Reduce Transparency][A09]
**SD A10.** Reduce Motion guidance discourages large animations, especially simulated three-dimensional movement. [Reduce Motion][A10]
**SD A11.** HIG Keyboards distinguishes normal content focus from Full Keyboard Access to controls and warns against overriding system shortcuts. Custom directional navigation for every button is not the platform rule. [Keyboards][A11]
**SD A12.** HIG Pointing Devices favors familiar system pointer effects, comfortable hit regions and useful rather than decorative hover behavior. [Pointing devices][A12]
**SD A13.** Apple recommends matching virtual keyboard type to input and using keyboard layout guidance to keep important interface parts visible. [Virtual keyboards][A13]
**SD A14.** Accessibility announcements support priorities that influence interruption and queuing of speech. An announcement mechanism is not a guarantee that a person heard it. [Announcements][A14]
**SD A33.** Apple's UI design tips recommend touch controls at least 44 by 44 points. This is a design floor for the candidate, not a measured error-rate guarantee. [Design tips][A33]

**Candidate requirements:**

1. Stop, approve/deny, waiter answer/cancel and retry/reconcile all have visible text, semantic names, role, state and exact target. Expand targets beyond icon artwork. No required gesture depends on drag, long-press duration, hover or color alone
2. Dynamic Type and Bold Text can enlarge every safety-relevant label and argument. Reflow control rows vertically; permit multiple lines; never truncate the recipient, destructive scope or unknown-state explanation to preserve a glass pill
3. Test normal, increased-contrast, reduced-transparency, reduced-motion, light/dark and user tint presentations in combination. Contrast is evaluated against actual composited backgrounds, including fast-changing text. Do not select a decorative brand color as a safety color without testing
4. VoiceOver focus follows a stable semantic item identity, not array position. Incoming tokens do not steal focus or restart every utterance. Offer bounded, optional progress summaries and an explicit read-latest action; urgent permission/Stop-state changes need a measured announcement policy. The full details remain navigable
5. When a review opens, focus starts at its title/context; on close it returns to a meaningful origin. If the target becomes invalid while focused, announce the invalidation and disable submission without moving to a replacement target
6. Full Keyboard Access must complete all required journeys; normal text/list navigation and shortcuts follow iOS/iPadOS conventions. A shortcut uses the same captured target and gate as touch. Command-period or Escape is not silently repurposed as an unknown Stop mode
7. Pointer hover may expose supplemental help, never unique approval facts or the only Stop action. Switch/Voice Control names must distinguish repeated task buttons. External keyboard, floating/split keyboard, dictation and composition input must not submit on an intermediate IME state
8. The software keyboard and safe-area changes cannot cover the primary decision controls or target. Landscape and narrow windows still complete the review. iPad multiwindow focus changes must not redirect an unsent command

A checklist or automated audit alone is not accessibility conformance. Include users of relevant assistive technologies in later authorized usability qualification; count wrong-target actions, abandoned journeys, comprehension errors and time to reach/inspect Stop, not just pixel overlap.

## Streaming backpressure and rendering

The backend preserves canonical facts; the phone maintains a bounded read projection. A stream burst must not monopolize decoding, layout, assistive announcements or input handling. Reserve control progress end to end, including ingress framing, scheduling, canonical append and receipt delivery. A separate button or two local queues is insufficient evidence.

**Candidate pipeline:** qualified read ingress with explicit bounds; off-UI decode/validation and scoped model update; immutable/coherent projection update; frame-coalesced visible-row rendering; independently reachable host control shell. Coalesce presentation only after mandatory facts are retained at the proper durable boundary. Local render delay is not a canonical GAP. Bound markdown parsing, syntax highlighting, enormous lines, nested markup, attachments, bidi/control characters and image decode; untrusted output remains inert data.

Use stable row identities and narrow dependencies. Update the current partial text block without reconstructing the full conversation. Keep only a bounded active layout window plus explicitly paged historical data under the selected retention policy. When the user scrolls up or selects text, stop forced autoscroll and show a meaningful pending-new-content indicator. Terminal-like content needs a separate measured representation and accessible semantic alternative; do not assume a pixel terminal is suitable for all ten controls.

**SD A17.** Apple's Swift concurrency guidance distinguishes asynchronous work from work actually moved off the main actor and recommends separating long-running non-UI logic from UI state. Compiler mode and isolation annotations matter. [Explore concurrency in SwiftUI][A17]
**SD A18.** The SwiftUI instrument identifies long view-body and representable updates and their causes. Apple's example shows how broad state dependencies cause unnecessary updates. This is diagnostic technique, not a Recursion speedup estimate. [SwiftUI Instruments][A18]

Do not create a task per token or assume `async` makes parsing nonblocking. Freeze compiler/SDK/concurrency settings and inspect actual execution. Bound workers and cancellation checks; avoid synchronous waits from the UI thread on decode/storage/network work. UI cancellation cancels disposable projection work; it cannot erase a possibly submitted backend command or mean task Stop.

Glass adds a second variable: changing content near controls can cause compositing work even when the control label does not change. Compare system glass at limited navigation surfaces against the equivalent opaque treatment and an otherwise identical layout. Inspect overdraw, offscreen rendering, updated-region extent, frame misses and GPU time. Avoid perpetually moving decorative gradients, pulse animations, independent blur layers or a display-link tick when no visual state changed. Group nearby effects only when profiling supports the chosen bounds; one screen-wide container is not automatically better.

Rendering quality may reduce animation or batch visual updates under thermal/power pressure, but cannot drop canonical facts, hide uncertainty, delay current authorization checks or omit the control shell. A frame-rate target is profile-dependent: report refresh rate, frame deadlines and missed-frame/hitch distribution rather than promising universal 60/120 fps. All numeric Recursion budgets remain unknown until measured and preregistered.

## Foreground background and reconnect

**SD A19.** Apple describes background entry as preparation for suspension, with resource release and minimal work. UIKit captures an app-switcher image after background transition; sensitive views should be removed before that snapshot, also avoiding sensitive restoration archives. [Background UI preparation][A19]
**SD A20.** Background runtime strategies have different purposes and limits. Short finishing work has an expiration path; scheduled refresh/processing is system-managed. They do not establish an indefinitely running foreground-equivalent app. [Background strategies][A20]
**SD A21.** Continued processing tasks start from a person's foreground action, can continue eligible work after backgrounding, expose progress, and are cancellable. Apple's examples concern finite local work. [Long-running tasks][A21]

| Lifecycle observation | Candidate behavior | Forbidden inference |
|---|---|---|
| Active qualified session | Read/control permitted only by current backend gate | A path monitor or tunnel alone proves authority |
| Inactive or background transition | Stop decorative work; preserve only permitted inert state and existing command correlation; prepare privacy-safe view | Backgrounding is Stop or a new work grant |
| Suspended or terminated | Assume connection/freshness may be lost; backend retains already-authorized ownership | The app keeps a realtime socket alive or the actor is dead |
| Foreground return | Show validation/reconnecting state before protected reuse; authenticate and reconcile | Restored pixels, credentials or a cached control lease are current |
| Lost response after online submission | Query original command identity under current reader rights; retain uncertain liability | Timeout proves refusal, or retry with a new ID is safe |
| New unsent text while disconnected | Local draft only if its retention policy permits; explicit later submission | Reconnect automatically submits it |
| Replay below retained floor | Exact GAP/RESET recovery and coherent snapshot installation | Accepted RESET alone establishes reconstructed history |

Do not claim a background timer, silent push, VPN or continued-processing entitlement can turn Recursion into an always-on phone daemon. No audio/location/background-mode misuse is proposed. A legitimate future finite export or local transform would require its own scope, exposure and budget; it is not a keepalive pretext for backend control. Background UI work stopping is separate from Aggressive/Full/Lazy semantics.

**Initialized-profile attachment invariant:** for an already admitted and initialized client/backend/connection-plugin profile, attach, additional views, notification opening and foreground return produce zero new model/inference, indexing, task/actor work or operational plugin activation attributable to that event. Authorized read synchronization has finite, measured CPU/network/storage costs; it is not free. Explicit first activation of an optional client or connection plugin is a separately admitted and budgeted lifecycle treatment, not hidden work charged to an ordinary attachment. Neither case grants new backend work authority.

Frozen M1B retains `HELLO/WELCOME/SNAPSHOT/EVENT/ACK/CREDIT/INPUT/RESIZE/RESET`; GAP is a marker/reason, not an added wire arm. After a replay gap the required next same-stream continuation is RESET. Install validated snapshot bytes and matching cursor atomically before claiming recovery, and obey fresh-credit rules. Reconnect preserves task/actor/operation identity, rechecks enrollment/session/read scope/config/route and leases, and does not start inference, indexing, a second executive or hidden operational plugin activation.

## Pairing protected data and privacy

The app is a remote client, not a provider-account wallet. Enrollment binds the intended authority domain, device/client identity, principal and transaction; current authentication permits reaching the backend gate. A QR code or deep link can carry an inert locator/challenge, not command authority. The original R-MOB mechanism comparison remains open; this report does not select passkeys, OAuth, mTLS, proof keys, an overlay or SSH.

**SD A22.** Apple documents different Keychain unlock, synchronization and backup classes. The passcode-set device-only class is not synchronized or backed up; other device-only classes have different restoration properties. Class selection cannot be replaced by a generic encrypted-storage claim. [Keychain protection][A22]
**SD A23.** Apple's Security-framework Secure Enclave guide describes hardware-held private-key operations, supported key constraints and no plaintext import/export for that interface. It can reduce extraction exposure but is not evidence that an authorized compromised process cannot invoke a key. [Secure Enclave keys][A23]
**SD A24.** Complete file protection makes protected files unavailable for reading/writing while locked or booting. This differs from first-unlock or already-open protection classes. [Complete file protection][A24]
**SD A25.** Backup exclusion is intended for recreatable cache/support files; Apple warns that some document operations reset the property. A flag is therefore not a complete tested backup policy. [Backup exclusion][A25]
**SD A26.** The screenshot notification arrives after a screenshot is taken. It cannot prevent that screenshot from disclosing already-visible content. [Screenshot notification][A26]

**Candidate storage boundary:** keep backend-authentication material in a separately qualified OS-protected store; separate it from content caches, logs and UI state. Device keys are sensitive but are not provider credentials. Prefer a narrow device-bound protected-key candidate where compatible with the eventual protocol, and compare its recovery/unlock/usability against other qualified mechanisms. Do not infer universal clone rejection, anti-phishing success or hardware uniqueness.

Choose the required unlock/biometric semantics explicitly. A key requiring unlocked use will not support unattended locked-background private refresh; that can be the correct privacy outcome. Do not weaken its class just to make a notification badge fresher. A local biometric dialog is neither backend enrollment approval nor an authorization to execute an action. For declared biometric-protected operations, cancellation and changed enrollment need safe fallback/re-enrollment rules, not bypass.

**Private offline retention remains undecided.** Compare online-only private views with an expressly authorized bounded historical snapshot. Even minimal task metadata may be sensitive. Either policy must preserve the exact R-MOB cache identity and separate principal/device generation/audience/purpose/privacy domain/grants/source cuts, not a generic timestamp. Unseen remote revocation cannot instantly invalidate bytes on a disconnected recipient. A restored database cannot resurrect enrollment, grants, input leases, outbound commands or offline-reading permission. Reboot/clock/restore uncertainty closes protected reuse or forces online validation.

Test all derivatives: database journals, temporary decode files, thumbnails, restoration state, local search indexes, clipboard, drag/share previews, screenshots, app-switcher images, crash reports and diagnostic logs. Redact the app-switcher scene before the OS snapshot boundary, restore only after current policy checks, and test multiwindow scenes separately. Screen-recording/capture-aware redaction can be a defense-in-depth candidate only on a qualified API/profile; there is no claim to stop all screenshots, external cameras or compromised-OS capture. Do not repurpose secure text-field behavior as undocumented whole-screen capture prevention.

Logout or observed revocation invalidates the affected sessions and purges/quarantines governed local derivatives with cleanup coverage recorded. Backend device revocation fences new reads/actions and invalidates relevant leases; it is not Full Stop, remote physical wipe or proof of client erasure. Already-admitted tasks and unresolved external effects retain their own authority and liability.

## Notifications Live Activities and links

**SD A27.** Universal links use an app/website association and can route a URL into app context; browser fallback and user navigation context affect opening behavior. Routing is not Recursion authorization. [Universal links][A27]
**SD A28.** Background notifications are low priority, can be delayed/throttled and are not guaranteed. Apple advises against more than a few per hour; delivery can replace an older pending hint. [Background push][A28]
**SD A29.** Live Activities expose glanceable data in highly visible system surfaces, may appear on paired devices, use SwiftUI/WidgetKit, and update through the app or ActivityKit push. Their sandbox cannot independently access the network; combined content is bounded, and stale-state handling is supported. [Live Activities][A29]

**Recommendation:** foreground-only correctness is the baseline; optional generic attention hints are the first notification experiment. A hint can mean an authorized attention item may be available. It must not contain private task titles, source text, arguments, provider names, keys, action-bearing URLs or internal digest identities by default. Even timing and identifiers can leak; bound/deduplicate subscriptions and state the residual observation model.

A tap or universal link opens an inert location, validates the intended domain/route shape, establishes the current session and reads a bounded authorized projection. It never approves, stops, resumes, enrolls a device, activates a plugin or reserves a model budget. Unknown/malformed/cross-principal links refuse safely. Treat all parameters as untrusted. Do not put credentials, approval tokens or private content in URLs. A successful universal-link association does not replace backend identity verification.

Live Activities are worth evaluating only for an explicitly chosen, bounded active task whose status is useful outside the app and whose disclosure policy covers lock screen and paired surfaces. Prefer a coarse last-observed state with freshness/unknown semantics; do not stream tokens or put approval/Stop buttons there in this candidate. They are not a continuously connected control plane. Ending or dismissing the Live Activity does not stop backend work; a stale display cannot say running-now or fully-stopped without current evidence. No native extension or APNs integration is authorized here.

## Measurement plan and budget unknowns

PERF-010 and OR-024 govern the comparison: correctness, authorization, privacy, effect accounting, quality and recoverability are nontradeable floors; then evaluate responsiveness, subscription efficiency and completion. Do not combine a prettier animation or lower phone CPU score with a backend admission regression into a favorable scalar score.

**SD A30.** Power Profiler records device/process power-related measurements. Apple warns that per-process power-impact values are not comparable across device models, charging can report overall power as zero, and Xcode pairing affects sleep observation. [Power Profiler][A30]
**SD A31.** MetricKit supplies device-generated performance/diagnostic reports, including launch/resume, hangs/hitches, CPU and memory categories. Periodic field reports complement local instrumentation; they are not an immediate complete trace of every interaction. [MetricKit][A31]
**SD A32.** Accessibility Inspector and automated application audits can find common label, contrast, hit-region, clipping and Dynamic Type issues. Apple explicitly says clearing audits does not guarantee full accessibility and calls for assistive-technology testing. [Accessibility audits][A32]

| Dimension | Proposed observation | Current budget and result |
|---|---|---|
| Launch/resume | Time to privacy-safe shell, authenticated state, first correct projection, interactive controls; cache/network phases separate | Unknown until approved preregistration and measurement |
| Control progress | Offered event, local recognition, submission, canonical admission, receiver fence and rendered receipt timestamps; missed/refused/censored cases retained | Unknown; no invented Stop SLA |
| Rendering | Frame/hitch distribution, long body/representable updates, GPU time, updated regions and compositing work while streaming/scrolling | Unknown; compare exact screen/refresh profiles |
| Memory | Peak/resident/allocated growth, retained history, layout caches, images, per-view state and memory-pressure response | Unknown; finite proposed caps must be frozen before run |
| Power | Same-device paired trials; CPU/GPU/display/network impact, thermal state, brightness, battery/charging and idle wakeups | Unknown; missing meter is not zero |
| Network/storage | Payload/framing bytes, reconnect attempts, replay/snapshot bytes, writes and retained derivatives | Unknown; include encrypted sensitive data in exposure accounting |
| Backend overhead | Read/query/append/control cost with zero, one and multiple views; installed-disabled versus active client/connection plugin | Unknown; attachment cannot hide new operational work |
| Human outcome | Correct scope selection, approval comprehension, Stop reach, uncertainty comprehension and assistive journey completion | Unknown; failures cannot be averaged away |
| Engineering cost | Review/debug hours, native integration count, OS upgrade regression work, shared-code savings and escaped parity defects | Unknown; AI speedup remains a hypothesis |

Freeze supported OS/device classes, exact SDK/compiler/build flags, material preferences, accessibility settings, renderer, route/config/graph revisions, source cuts, thermal/power/network states, data corpus, instrumentation overhead, semantic oracle, caps, trial order and practical improvement margins. Select oldest-supported and representative constrained devices only after the floor is approved; include a high-refresh profile rather than extrapolating across refresh rates. Simulator timing is not phone battery/GPU/radio evidence. Use Instruments' SwiftUI, CPU, memory, hangs/hitches and relevant graphics/network traces with purpose-scoped signposts; keep private content out of telemetry.

## Bounded local prototype handoff

This section is **unexecuted**. It proposes later local/synthetic work requiring its own reviewed build/device authorization. The smallest useful comparison is a fake-backend client slice with exact fixtures, not a store-ready app. Do not connect it to any account, live backend, provider, real notification service or private content.

Compare two iOS candidates first: SwiftUI controls plus a bounded transcript, and the same shell with a targeted UIKit text/collection surface. Keep the backend fixture and all semantic outcomes identical. A third current React Native candidate is useful if the decision would actually change with equal performance and lower reviewed maintenance; pin its exact version/engine/native components. Do not implement every framework merely to accumulate comparisons.

### Shared semantic scenario matrix

The IDs below coordinate with the Android companion; platforms may use different stimuli but the same semantic oracle. Every outcome remains **UNEXECUTED**.

| ID | iOS-specific scenario | Required positive and negative observations |
|---|---|---|
| MP01 Same-cut parity | Render and invoke all ten controls from exact shared catalog/cut with touch and keyboard | Valid request matches the independent oracle; changed target/scope/revision/mandatory version refuses |
| MP02 Back and gesture detach | Navigate back, dismiss sheet, Home/lock, close final scene, swipe away | Zero new Stop/resume/approval/cancel; backend identities and already-authorized lifetime preserved |
| MP03 Connectivity and ambiguous receipt | Lose connection before send, after admission and before receipt; reconnect with stale credentials | Offline new action=0; uncertain original ID reconciles without dispatch; new-ID bypass mutation fails |
| MP04 Accessible controls and Stops | VoiceOver, largest supported accessibility text, reduced transparency/motion, contrast, Switch/Voice Control and Full Keyboard Access | All ten controls/three modes are discoverable and correctly targeted; inaccessible, hidden or wrong-target mutants fail |
| MP05 Stream flood and control reserve | Fast synthetic text, huge lines, slow reader, parser load, blocked render and zero credit | Caps hold; mandatory facts preserved; admitted control progresses within frozen bounds or explicitly refuses due to qualified limitation |
| MP06 Lifecycle and restoration | Interrupt background transition, memory pressure, process death, state restore, multiple iPad scenes | Privacy-safe snapshot/state; foreground revalidates; restored view never restores authority or automatically submits |
| MP07 Enrollment and backup | Synthetic wrong-domain enrollment, revoked generation, copied cache/key manifest, reboot/clock rollback | Current valid proof/profile succeeds; stale/cross-scope/ambiguous restoration refuses; no universal-clone or wipe claim |
| MP08 Notifications and deep links | Forged/duplicated/expired hint, unauthorized locator, tap with no live session | Zero effect/model/index/activation/budget calls; authorized tap only retrieves bounded projection |
| MP09 Adaptive input | Rotate/rescale window, change Dynamic Type/locale/RTL, show floating keyboard and pointer, switch focus mid-review | Target/draft preserved; no lease transfer from geometry/focus; required facts and decision path remain reachable |
| MP10 Energy and background | Identical visible workload with glass/opaque candidate, idle foreground, background, thermal/low-power states | Report same-device resource vector and failures; no ongoing decorative render/keepalive entitlement assumption |
| MP11 Contribution failure | Unknown, duplicate, disabled/revoked or hostile contribution and extreme descriptor | Host Stop/attention/gap shell remains usable; precise safe loss; no operational registration/activation on drawing |

Add iOS subcases: rapid content moving underneath glass; optical extremes of approved materials; approval sheet with keyboard at maximum text size; voice announcement flood while reading exact arguments; full Stop with one unreachable node; Lazy timeout/escalation; a physical-capture residual demonstration if later separately authorized; and two scenes attempting the same per-target input lease.

Use finite replay schedules, literal expected receipts and an independent oracle. Retain R-MOB's proposed 10,000-event/1,000-control-opportunity soak as an optional finite common fixture, not a product target or statistical-power claim. Declare queue/memory/time bounds before execution; unset thresholds are not evaluable. Stop on completed vectors or a preregistered safety/resource bound; preserve censored results. Include useful authorized success paths so deny-all cannot pass. Mutate target capture, stale waiter, offline-submit gate, GAP order, scope checks, queue caps, receipt identity and opacity/focus behavior to show observers detect the intended failures.

Deliver later: exact source/build/profile digests; fixture input and offered schedule; independent expected/actual semantic trace; no-private-data native screenshots/accessibility trees; Instruments traces; physical-device limitations; failed/censored runs; and a written decision against preregistered margins. Synthetic semantics can reject inconsistent state machines; they cannot certify actual networking, secure storage, OS scheduling, battery life, cryptography, store eligibility or external effects.

## Recommendations rivals and evidence that could change them

| Recommendation | Conforming rival | Decisive falsifier | Passing would not prove |
|---|---|---|---|
| Swift native baseline | Current RN/native-component implementation with same requirements | Rival meets all semantic/OS/design floors with materially lower reviewed lifecycle cost and no relevant resource regression | Universal language superiority or all future OS behavior |
| SwiftUI shell with optional UIKit hotspot | SwiftUI-only or UIKit-first | Interop cost/focus defects exceed measured hotspot benefit; or pure SwiftUI already meets every margin | UIKit is always faster or SwiftUI always simpler |
| System glass in navigation/control layer | Smaller mostly opaque system-material treatment | Required content/control comprehension, access or resource margin regresses | A screenshot proves accessibility or battery efficiency |
| Bounded incremental transcript | Another bounded renderer with identical semantics | Retained memory grows past cap, appends destabilize selection/focus, or control progress fails | Production terminal compatibility or arbitrary input safety |
| Foreground correctness with optional hints | No push/Live Activity at all | Lifecycle correctness depends on delivery, or hints disclose prohibited data | Guaranteed wake/delivery or permanent background runtime |
| Protected device-specific key candidate | Another independently qualified current enrollment mechanism | Needed algorithm/recovery/access policy cannot fit; misuse/restore violates profile | Universal clone prevention, authorized use or uncompromised OS |
| Native OS accessibility path | Custom semantic bridge with equivalent journeys | A required assistive/input path cannot complete or announces wrong subject | Full conformance from an automated audit |
| Two native clients with shared contracts/tests | Shared implementation where it preserves per-OS behavior | Review/upgrade/parity burden overwhelms any measured fit benefit | AI eliminates second-app maintenance |

## Inherited distribution and counsel gate

R-MOB's counsel packet and D-027/G-32 remain unresolved release gates. Native Swift and Apple-provided UI do not clear a distribution channel, provider route or entitlement. Carry these iOS-specific questions into that existing packet, with the final app behavior and current official rules for the intended storefront/region:

- How should a thin authenticated remote-control app with typed plugin contributions be classified, and where is the boundary between displayed remote output, remote desktop behavior and downloaded/executed code?
- Do the exact provider-login/delegation flows, paid backend features, subscriptions or purchase links trigger additional requirements, and can they remain compatible with the no-ungranted-provider-credential-custody boundary?
- What disclosures and permissions cover task content, diagnostics, notification metadata, local retention, lock-screen/paired-device exposure and deletion?
- Which encryption/export declarations, background or networking entitlements, extension capabilities and signing arrangements apply to the chosen profile?
- Which App Store, organizational or alternative distribution paths are actually eligible in the intended regions, and what review/ongoing obligations follow?

These are review questions inherited from the supplied product research, not newly interpreted policy answers or legal advice. No counsel was contacted and no agreement accepted, entitlement requested, account created, signing asset used or submission made.

## Shared contract preservation and remaining decisions

Reuse the four fields `ArtifactRef=(object_type,id,version,content_digest)` and the exact eighteen `ContentEnvelope` base fields: `schema_revision`, `unit_ref`, `source_kind`, `authenticated_origin_or_unknown`, `claimed_author`, `source_revision`, `source_locator`, `integrity_class`, `confidentiality_class`, `allowed_readers`, `project_and_audience`, `privacy_domain_id`, `retention_rights`, `parent_units`, `observed_input_set`, `transform_identity_version_config`, `coverage_and_loss`, `authority_carried_none`. No iOS field becomes a nineteenth base field; imported/model content retains `authority_carried_none=true`.

Preserve one immutable loss record, exact identity/epoch domains, current read checks before existence lookup, audience/purpose-scoped opaque locators, and precommitted `ExposureIntent` before private metadata/chunk release. Current rights/fences are checked at release and protected publication; uncertain copies stay obligations. No iOS restore, backgrounding, reconnect, fork or new view renews a reservation. Keep the shared conserving resource algebra and original operation/reservation lineage; unknown usage is not zero. R-UI qualified contribution/binding identity and complete materialization inputs remain authoritative for this candidate.

Decisions still required before implementation: supported iPhone/iPad and OS floors; whether/how iPad multiwindow ships in the qualified profile; exact private offline policy; authentication and key/recovery profile; transport and optional connection-adapter profiles; notification disclosure/subscription budget; resource and usability margins; any later prototype/build/device authorization. The language/UI-stack recommendation is ready for consideration, not a repository ratification or a reason to reopen accepted backend semantics.

**Not established:** an implemented app; benchmark results; accessibility conformance; actual secure backup/restore; physical erase; instant offline revocation; universally clone-proof credentials; route qualification; remote Stop settlement; exact-once external effects; battery or performance superiority; easier/faster two-app delivery; store/legal/export/entitlement clearance; provider terms compliance; release readiness or Owner adoption.

## Source links

[A01]: https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass
[A02]: https://developer.apple.com/design/human-interface-guidelines/materials
[A03]: https://developer.apple.com/videos/play/wwdc2026/102/
[A04]: https://developer.apple.com/documentation/SwiftUI/Applying-Liquid-Glass-to-custom-views
[A05]: https://developer.apple.com/documentation/xcode/improving-your-app-s-rendering-efficiency
[A06]: https://developer.apple.com/design/human-interface-guidelines/layout
[A07]: https://developer.apple.com/design/human-interface-guidelines/sheets
[A08]: https://developer.apple.com/design/human-interface-guidelines/accessibility
[A09]: https://developer.apple.com/documentation/swiftui/environmentvalues/accessibilityreducetransparency
[A10]: https://developer.apple.com/documentation/SwiftUI/EnvironmentValues/accessibilityReduceMotion
[A11]: https://developer.apple.com/design/human-interface-guidelines/keyboards
[A12]: https://developer.apple.com/design/human-interface-guidelines/pointing-devices
[A13]: https://developer.apple.com/design/human-interface-guidelines/virtual-keyboards
[A14]: https://developer.apple.com/documentation/accessibility/accessibilitynotification/announcement
[A15]: https://developer.apple.com/documentation/SwiftUI/UIKit-integration
[A16]: https://developer.apple.com/documentation/UIKit/using-textkit-2-to-interact-with-text
[A17]: https://developer.apple.com/videos/play/wwdc2025/266/
[A18]: https://developer.apple.com/videos/play/wwdc2025/306/
[A19]: https://developer.apple.com/documentation/uikit/preparing-your-ui-to-run-in-the-background
[A20]: https://developer.apple.com/documentation/backgroundtasks/choosing-background-strategies-for-your-app
[A21]: https://developer.apple.com/documentation/BackgroundTasks/performing-long-running-tasks-on-ios-and-ipados
[A22]: https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
[A23]: https://developer.apple.com/documentation/Security/protecting-keys-with-the-secure-enclave
[A24]: https://developer.apple.com/documentation/foundation/fileprotectiontype/complete
[A25]: https://developer.apple.com/documentation/foundation/urlresourcevalues/isexcludedfrombackup
[A26]: https://developer.apple.com/documentation/uikit/uiapplication/userdidtakescreenshotnotification
[A27]: https://developer.apple.com/documentation/xcode/allowing-apps-and-websites-to-link-to-your-content
[A28]: https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app
[A29]: https://developer.apple.com/documentation/activitykit/displaying-live-data-with-live-activities
[A30]: https://developer.apple.com/documentation/Xcode/measuring-your-app-s-power-use-with-power-profiler
[A31]: https://developer.apple.com/documentation/metrickit
[A32]: https://developer.apple.com/documentation/accessibility/performing-accessibility-audits-for-your-app
[A33]: https://developer.apple.com/design/tips/
[A34]: https://developer.apple.com/videos/play/wwdc2025/219/
[A35]: https://www.apple.com/newsroom/2025/09/new-versions-of-apples-software-platforms-are-available-today/
[RN1]: https://reactnative.dev/blog/2025/10/08/react-native-0.82
[RN2]: https://reactnative.dev/blog/2026/02/11/react-native-0.84
[RN3]: https://reactnative.dev/architecture/landing-page
[RN4]: https://reactnative.dev/docs/performance

## Repository and prior report references

- [Governance at the source pin](https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/CONTROL_PLANE.md)
- [Accepted D-018 through D-034](https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/state/DECISIONS.md)
- [Interface strategy](https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/INTERFACE-STRATEGY.md)
- [Frozen M1B wire profile](https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/M1B-WIRE-PROFILE.md)
- [Performance plan](https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/PERFORMANCE-PLAN.md)
- [Shared contract reconciliation](https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Shared_Contract_Reconciliation.md)
- R-UI final candidate-2 and R-MOB final connected-control reports from the supplied 2026-10-02 composition packet; their inspected byte hashes are recorded in the companion source ledger. These later reports are not represented as committed contents of the earlier source pin
