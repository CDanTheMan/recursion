# R-N: Graphical client architecture over the shared command-and-query model

Date: 2026-10-02 UTC  
Status: research and architecture candidate, not implementation acceptance  
Repository baseline: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Execution: static inspection and artifact generation only; all target fixtures **UNEXECUTED**

## Findings and decision boundary

The GUI can add spatial navigation and richer review while remaining a replaceable, opt-in client. It must consume the same authorized, revision-bound facts as the CLI/TUI and submit the same typed command intents to the same backend admission. A shared label, shared component library or identical screenshot is insufficient evidence of shared semantics.

Three early eliminators matter more than a toolkit benchmark:

1. Any renderer that cannot expose the complete workflow to the selected platform accessibility bridge fails the accessibility gate, even if its frame rate is excellent. The unadapted Dear ImGui embodiment has a source-documented accessibility/internationalization gap; this does not disqualify every immediate-mode architecture
2. Any shell that owns canonical writes, provider credentials or actor lifetime violates the accepted boundary. Closing its last window must not kill or relaunch work
3. Any cache that presents historical authority as current, or silently replays offline commands after reconnect, violates productive continuity

**Scope is comprehensive, sequencing is terminal first.** D-019 includes GUI as built and shipped opt-in at first release and explicitly rejects the smaller-release proposal. Current direction says TUI first, GUI later. PRODUCT, CLI, INTERFACE-STRATEGY and copied R-N context still contain initial-release exclusions. This report treats TUI-first/GUI-later as construction and interface sequencing, preserves the accepted GUI capability, and leaves the exact calendar/release interpretation for explicit Owner reconciliation. It does not decide that GUI is a prerequisite for any core workflow, silently remove GUI from first-release packaging, or declare the older exclusion resolved. No repository text is amended.

No language, framework, UI toolkit, renderer, runtime, transport, encoding, store, package manager, sandbox product or vendor is selected. Named products illustrate mechanisms and real alternatives. No route is qualified. All startup, frame, input, idle, accessibility, security and porting-cost measurements are unknown.

### Evidence classes and inspected substrate

**SD**: public or repository source-documented. **SO**: statically observed source or historical record, not newly executed behavior. **P**: original design inference/candidate. **U**: unknown, unavailable or unmeasured. Mandatory requirements are traced below; proposed mechanisms are associated with recommendations C01–C12 in section 17.

SO: governance, D-017–D-033, the current goal, PRODUCT, INTERFACE-STRATEGY, PLUGINS-AND-EDITIONS, CLI, TERMINAL-RUNTIME, M1B-WIRE-PROFILE, PERFORMANCE-PLAN and the current research maps were inspected. Static `contract_vectors.py` models configuration-fence and receipt-generation races, including a deny-all negative control. The replay-store dossier records bounded synthetic snapshot/receiver results and explicitly distinguishes wire acceptance from application installation. F-M1B-019 rejects unsupported required containment even when PTY and termination capabilities are present. These records demonstrate useful existing test shapes, not an implemented GUI or newly verified behavior. See the repository-relative source register.

R-I is consumed as a completed research deliverable; R-J/R-K/R-L are draft candidates at this report's intake. Their precise shared contracts remain subject to independent integration review. [R-L Q01–Q05](../rl/report.md#r-l-q01) owns the proposed semantic catalog, envelopes, projections and configuration resolution; [R-K Q15–Q17](../rk/report.md) owns terminal accessibility and Stop presentation; [R-J Q03–Q05](../rj/report.md) owns view/input/lifetime distinctions. This lane adds GUI-specific construction constraints, not another backend. For route facts use R-F; for MCP semantics use the protocol-edges supplement; for credential isolation use R-E; for licensing/terms use R-H. Those sources are not restated as GUI evidence.

G-06/G-07/G-11 Owner decisions are closed, while implementation qualification remains open. D-028 floors are Windows 11 25H2 build 26200 Home/Pro, plus 24H2 build 26100 Enterprise, x64 primary; Linux 6.12 LTS primary/6.6 LTS compatibility, cgroup v2 and local ext4. Local NTFS is the Windows canonical-state floor. WSL2 is development/test only, with ext4 and `/mnt/c` distinct. GUI distribution/library/compositor/GPU profiles still require definition within these floors; a kernel version alone does not select a Linux desktop stack. macOS accessibility is compared as an additional portability opportunity, not added to the mandatory release matrix.

<a id="r-n-q01"></a>
## Q01. Requirements and accepted traces

The full machine-readable requirements ledger is `requirements.json`. P/C01 implements the following existing requirements without changing their scope.

| ID | Required capability and concrete GUI expression | Authority trace | Rejecting observation |
|---|---|---|---|
| N01 | Spatial project/workspace/session navigation with typed object identity; a selected session is not the task itself | D-018; INTERFACE division/object graph | Changing selection silently changes command target or canonical membership |
| N02 | Artifact and diff review with exact source/output revision, producing operation, verification status and accessible linear alternative | INTERFACE later GUI; D-024 | Pretty diff binds to mutable branch head or presents generated as accepted |
| N03 | Lineage view with parent/fork/attempt/context links and textual adjacency list | INTERFACE object graph; D-024 | Layout proximity is treated as causation, ownership or authority |
| N04 | Context comparison between named epochs/capsules; accepted instruction references distinguishable from generated summaries | INTERFACE later GUI; D-024 | Comparison fabricates unavailable context or treats summary as instruction |
| N05 | Provenance inspection with source, transformation, evidence and scope; unknown accounting explicit | INTERFACE state facts; D-024/D-031 | Missing count becomes zero; screenshot or stream success becomes verification |
| N06 | Accessible responsive review/navigation/conversation/configuration/control | R-N accessibility target; INTERFACE later GUI | Any required workflow has a mouse-only, image-only or unsupported AT path |
| N07 | One command/query model, schema versions, errors, receipts and projections; deterministic status | INTERFACE; CLI; R-L shared candidate | GUI bypasses admission or changes a refusal into successful queueing |
| N08 | One Stop vocabulary, visible scope/boundary and honest local/remote/effect state | D-022; TERMINAL-RUNTIME | Window close means Stop; interrupt is represented as external rollback |
| N09 | Detachable independent views; zero attach-triggered inference/index/actor launch | TERMINAL-RUNTIME; PERF-010; D-025 | Attaching another window launches work or closes the runtime-owned adapter |
| N10 | Honest synchronized/cached/offline/gap presentation | D-024; M1B; R-N offline requirement | Cached authority enables control or replay loss is filled with invented prose |
| N11 | No canonical-state authority, credential custody or widened credential visibility | D-021/D-029; PLUGINS-AND-EDITIONS | Privileged shell bridge reads auth store or permits arbitrary canonical writes |
| N12 | Opt-in packaging, inert disabled state, no mandatory dashboard; full accepted capability retained | D-019/D-025; PLUGINS-AND-EDITIONS | Core boot depends on GUI, or disabled GUI starts updater/telemetry/model work |
| N13 | Bounded rendering/GPU/window/IME/DPI/animation/idle costs and exact phase measurements | R-N desktop requirement; PERF-010; OR-024 | Unbounded surfaces or queues, blocked writer/control, hidden CPU cost |
| N14 | Incremental TUI migration, transferable meaning, discoverable compatible bindings/layouts | INTERFACE/TERMINAL-RUNTIME; D-018 | User must learn a second meaning for steer, queue, stop, fork or configuration |
| N15 | No unmeasured productivity/savings/porting claim; full review cost | D-024/D-031/D-033; PERFORMANCE-PLAN | Polish, framework choice or source availability is offered as benefit evidence |
| N16 | All ten controls remain representable when the exact route supports them | CLI; INTERFACE all ten controls | A GUI affordance asserts unsupported route capability or removes a required control |

The ten controls are streaming, questions, approvals, queued messages, active steering, interruption, resume, forks, compaction and namespaced custom commands/plugins. Native, upstream-only and combined workflows use the same views; upstream-only status and recovery acquire no hidden native helper inference. No new executive tier is introduced by a window.

<a id="r-n-q02"></a>
## Q02. Reuse means one semantic authority

**P/C01–C03.** A renderer consumes the R-L operation catalog and projection definitions unchanged. GUI widgets may be different from terminal cells, but their canonical objects, target resolution, preconditions, capability explanations, error classes and receipt transitions are not. The backend owns command admission, schema/revision checks, grant/pause/fence verification, durable receipts, canonical writes and effect dispatch. The GUI owns presentation state only.

A query comparison must fix projection/schema version, source cut, authorized audience and filter. A `latest` query returns its actual cut; comparing two different cuts is not evidence of semantic divergence. Store canonical cut, stream cursor, projection generation, authority revision and client receipt identity separately. They cannot be compressed into one generic version. Generated labels or summaries never substitute for source facts.

| Operation | Presentation-only or read projection | Typed mutation, if any |
|---|---|---|
| Pan/zoom lineage, resize panel, reorder visible tabs, collapse row | Local layout only; query bounded neighbors if needed | Persisting shared preferences is the existing configuration operation |
| Select project, filter task list, inspect receipt, compare two context epochs | Read query; viewer cannot invent omitted graph edges | None; changing project membership/accepted context requires its command |
| Open artifact/diff in inert preview | Authorized, revision-bound artifact/read query | Execute/open externally/export/share/edit require distinct admitted operations |
| Type an unsent message, annotate a local review draft | Local draft clearly labeled; no effect implied | Submit, edit accepted queue, answer interaction or record review uses exact typed command |
| Press Steer/Queue/Stop/Resume/Fork | No pure projection can perform these actions | Same catalog operation/version and target revisions as TUI/CLI |
| Toggle configured plugin or change effective settings | Read explain/preview first | Shared validate/compare-and-apply transaction; not an extra GUI settings database |

A diagram drag that reorganizes display does not change task dependencies; an explicit edit command must do that. A review checkbox changes a local draft, not acceptance. Rendering a button is not proof its route supports the action. Show declared, enabled, authorized, exact-route-supported and currently usable facts separately; preserve `unknown`.

Example: TUI queue and GUI queue resolve the same task/attempt/turn and produce the same semantic arguments to `core.message.enqueue@candidate-0` from R-L. Same-ID retry returns the same receipt; changed arguments under that ID conflict. A GUI focus change between pointer-down and submission cannot replace the captured target. Retry after a lost reply queries the old receipt first. Renderer reconnect never creates a new ID to force delivery. Exactly one backend retry owner controls each operation.

**Equivalence falsifiers:** same-cut query mismatch; per-surface authority/refusal difference; a supported GUI action with no catalog operation; a plugin directly mutating a read model; an approval answer accepted for a replacement waiter; a menu/default silently mapping steer to queue. F01/F02/F10/F13 include successful authorized cases so blanket refusal cannot pass.

**Wire boundary:** retain frozen M1B unchanged. Its closed union is HELLO/WELCOME/SNAPSHOT/EVENT/ACK/CREDIT/INPUT/RESIZE/RESET. `GAP` is a visible marker/reason, not a newly invented wire message. Owner Stop is a separately typed control path. R-L's application records and this lane's cache/view state do not add fields to M1B or change its refusal alphabet. Use shared R-L Q04 for exact credit/cursor/RESET rules; GUI conformance also checks atomic application of snapshot content plus cursor, because wire acceptance alone does not prove installation.

<a id="r-n-q03"></a>
## Q03. Stops, scope and ordinary closing

**P/C04.** Keep a persistent keyboard-reachable control showing selected Stop mode and exact target, with expanded ownership scope and current authorization. Stop is available without acquiring a terminal input/resize lease when the principal already has Stop authority. Its dispatch path cannot wait for a diff render, graph layout, modal animation or high-output transcript.

- **Aggressive:** selected agent, immediate forceful interrupt request and dispatch fence; show descendants separately and preserve uncertain in-flight effects
- **Full:** selected agent and its rooted owned subagents, shells, monitors and relaunchers; enumerate local settlement and separate remote receipts, unreachable holders and restart fences
- **Lazy:** close new admission and wait for the named observable boundary; show deadline, waiting/timeout and configured escalation
- `checkpoint`, `interrupt` and `drain` remain distinct mechanisms in the accepted vocabulary, not aliases for three extra Stops

A control receipt displays saved-locally, accepted/refused, delivered/applied, observed and settled/unresolved separately. A disabled control explains why; a stale visible control is still refused server-side. An offline Stop cannot claim an installed fence. Where connection is unavailable, show “not delivered; runtime state unknown” and preserve the pending intent for explicit review, not automatic execution later.

Window close, close tab, renderer crash and detach affect subscriptions and presentation resources only. Escape dismisses a transient view or recovers an unsent draft; it does not become a destructive Stop binding. A separate, explicitly requested daemon exit follows its own command semantics. F06/F11 verify each path. No UI wording says that a socket close, killed process or local stop rolled back an external effect.

<a id="r-n-q04"></a>
## Q04. Six rich-client families, no selection

These axes overlap: a native shell can contain a declarative web renderer, and retained-mode toolkits may custom-paint rather than use OS widgets. The comparison uses six concrete embodiments to expose different dependencies; it is not a claim that each family has uniform performance or security. `candidate-comparison.json` retains each field separately.

Primary mechanism anchors, deliberately brief:

<a id="electron-process-security-facts"></a>
- Electron documents main/renderer/preload separation. The main process is privileged; context isolation and renderer separation do not themselves implement Recursion admission. [S04](https://www.electronjs.org/docs/latest/tutorial/process-model), [S05](https://www.electronjs.org/docs/latest/tutorial/security)
- Tauri documents an OS-webview shell and messaging bridge; Windows uses WebView2, Linux WebKitGTK, macOS WKWebView. Engine parity therefore needs per-profile evidence. [S06](https://v2.tauri.app/concept/architecture/), [S07](https://v2.tauri.app/reference/webview-versions/)
- Qt documents widget accessibility interfaces and supported platform configurations. Custom controls and deployment choices still need qualification. [S08](https://doc.qt.io/qt-6/accessible-qwidget.html), [S09](https://doc.qt.io/qt-6/supported-platforms.html)
- Flutter documents framework/engine/embedder layers with accessibility and input integration. That architecture is not measured Recursion accessibility. [S10](https://docs.flutter.dev/resources/architectural-overview)
- Dear ImGui emits draw data for a host renderer; its inspected README explicitly reports missing accessibility and full internationalization. [S11](https://raw.githubusercontent.com/ocornut/imgui/master/docs/README.md)
- A browser can use a service worker/cache for read availability. That mechanism does not grant current control or make cached records authoritative. [S12](https://www.w3.org/TR/service-workers/)

All remaining cells below are **P tradeoff hypotheses**, not product benchmarks; exact compatibility and measured costs are **U**.

| Family / embodiment | Rendering and accessibility bridge | Platform/DPI and packaging/update | Offline, testability, dependencies and costs |
|---|---|---|---|
| A Bundled web desktop / Electron-style | DOM/layout/compositor plus native window shell; semantic DOM must reach OS AT; custom canvas needs parallel semantic representation | Bundled engine can reduce engine skew, while OS integration/GPU/IME remain profile-specific; engine/application update and signing closure must be owned | Read cache straightforward candidate; test DOM, bridge and native shell, not DOM alone. Engine/runtime/transitive package weight included. Startup, N-window memory, idle wakeups and frame tails U |
| B Web in native shell / Tauri-style | OS webview and narrow shell bridge; accessibility depends on actual webview/platform behavior | Different engine/dependency policies per OS; smaller application download cannot stand for smaller total installed footprint. Record webview owner/version/update policy; offline installer must handle missing dependencies | Cache protocol identical to A. Test each engine, IPC origin and semantic tree. Native bridge/plugins and shared webview count in closure. Startup/idle/frame and first-use dependency costs U |
| C Platform-integrated retained toolkit / Qt Widgets-style or platform-specific frontends | Retained controls/custom painting; accessibility adapter supplies roles, text, actions and events | Cross-platform toolkit or separate OS presentation modules can target Windows/Linux; toolkit support list is not D-028 qualification. Fonts, IME, packaging libraries and scale transitions remain explicit | Typed client and local read cache can be separate modules. Native automation plus independent semantic tree checks. Toolkit/plugins and optional rendering libraries count. No claim of naturally low idle or fast boot; all U |
| D Declarative retained scene / Flutter-style | Declarative tree, layout/render scene and semantic tree; embedder bridges OS input/accessibility | Engine/embedder/graphics artifacts shipped or resolved per profile; test compositor, device loss, text scale and native dialogs independently | Strong visual consistency is possible, not proven. Need semantic-to-visual synchronization tests. Runtime/engine/shader/font closure included; shader/first-use/frame/hidden cost U |
| E Immediate-mode host / Dear ImGui-style | Application regenerates UI descriptions/draw data; accessible tree and stable identities may require explicit adapter | Host selects window/input/graphics backends; portability of triangles does not establish text, IME, AT or desktop packaging parity | Pure projection mapping possible; frame-loop model must sleep on no changes. Snapshot visual tests insufficient. Smaller core can shift cost into accessibility/internationalization adapters. Unadapted cited embodiment fails gate; adapted option remains U |
| F Browser-hosted rich client | DOM and browser compositor/AT; native OS access restricted to admitted backend protocol | No dedicated desktop bundle required, but browser build/update, secure origin, local/remote endpoint and offline assets must be pinned as a profile | Cache can be evicted and tabs suspended; last-synchronized proof essential. Test real browser/AT plus backend. Count browser processes/resources already shared and attributable deltas separately. No installed-app download is not zero cost; metrics U |

**Attack surface by family:** A adds privileged preload/main IPC and bundled engine patch duty; B adds shell commands and OS-webview version skew; C adds native parsing, plugins and toolkit/FFI edges; D adds scene, shader and semantic-bridge synchronization; E adds bespoke text/input/AT code; F adds origin, XSS/CSRF, gateway and service-worker/update/cache edges. The size or memory of a dependency is not a security score. Every family can violate or preserve the same backend boundary depending on implementation.

**Packaging contract, P/C05:** compare a signed self-contained opt-in bundle against platform-managed/shared dependencies without selecting either. Record exact payload/dependency hashes, publisher, licenses/provenance, renderer/protocol ranges, inert-disabled behavior, offline installation prerequisites and downgrade/rollback compatibility. Staged GUI updates cannot update runtime state or widen grants just by reopening a window. Keep old/new projection schemas compatible or fail with an accessible version explanation. R-H owns legal interpretation; no license list here is clearance. Desktop signing/notarization is a deployment constraint, especially if macOS is later added; it is not a security or benignness proof. [S20](https://www.electronjs.org/docs/latest/tutorial/code-signing)

<a id="r-n-q05"></a>
## Q05. Decisive negative traces before benchmarking

| Candidate | Real competitor | Early rejecting trace / later decisive falsifier | Passing would not prove |
|---|---|---|---|
| A bundled web | B OS webview shell | Untrusted iframe/artifact calls privileged bridge or reads denied cache; required native AT action absent; later N20 idle budget breach | Browser isolation is a canonical-state boundary; low memory on every OS |
| B OS webview | A bundled engine | Pinned Linux webview cannot expose approval/diff text or required typed input; missing offline dependency forces an unapproved download; later cross-engine semantic mismatch | “Uses OS webview” means equal engines, zero deployment weight or low cost |
| C retained toolkit | D declarative scene | Custom diff control lacks text/actions in UIA/AT-SPI, or D-028 deployment library floor cannot be met; later focus/DPI corruption | OS-like styling proves accessibility or exact platform parity |
| D declarative scene | C toolkit | Visual approval changes while semantic tree retains old target; device-loss recovery relaunches task; later shader/frame/input tail breach | Smooth animation improves outcomes or rendering choices are universal |
| E immediate-mode | C retained toolkit | Cited unadapted embodiment lacks required accessibility; custom bridge has no stable focused interaction identity; later eventless render loop exceeds idle bound | Every immediate-mode library fails, or small core means cheap remediation |
| F browser-hosted | B packaged shell | Client requires arbitrary local filesystem/shell access outside typed backend, origin confusion admits command, or offline cache promotes authority; later suspension/reconnect loses facts | Browser sandbox protects a same-user host, cache persists, or gateway is safely exposed |

A negative trace eliminates the exact embodiment/profile before resource ranking. Documentation absence is U and a required verification blocker, not proof of failure; an explicit missing required feature can reject that unadapted version. No stack is approved because its competitor fails. Platform packaging/signing constraints may be blockers without being architectural impossibilities; do not “fix” them by weakening permission, trust or release requirements.

<a id="r-n-q06"></a>
## Q06. Lifecycle rendering, input and idle budgets

**P/C06.** A budget is a preregistered vector, not an invented product SLA. `performance-budget-template.json` contains every phase × N-view × load cell, with `limit=null`, `observed=null`, `status=unknown-until-measured`, units, required inputs and decision owner. A future characterization run may estimate costs, but no acceptance result is permitted while a required bound or oracle is missing. Freeze bounds before confirmatory observations; do not fit them around the winning stack.

| Phase | Defined measurement boundaries | Required budget vector and failure screen |
|---|---|---|
| Startup | OS process request to interactive shell, then first verified authorized projection; cold/warm runs separate | p50/p95/p99 launch-to-shell and launch-to-data; CPU/RSS/private memory/GPU memory/handles, disk/network bytes; not “first blank window” |
| First use | Request first diff/lineage/context/AT path to usable verified result | p50/p95/p99 input-to-feedback and input-to-result, decode/layout/paint/present times, dependency activation, shader/font/cache peaks |
| Steady foreground | Frozen idle and high-output event schedules plus typing, scroll, resize, review and Stop | p50/p95/p99 frame-interval and input-to-present; missed presentation deadlines; canonical append/control latency; bounded queues, memory, CPU, GPU and handles |
| Recovery | Wake/crash/reconnect observation to synchronized usable projection | p50/p95/p99 attach-to-interactive and attach-to-current; first-input tails, resync bytes/work, replay gaps, transient peaks, duplicate-work counters |
| Hidden/backgrounded | Hidden/occluded/minimized transition through frozen no-input and high-output windows | CPU time, wakeups/timers, render/present submissions, GPU residency, memory/handles and network; latency to visible/current after foregrounding |
| Disabled/not installed | Lean base boot and explicit no-GUI-work interval | No GUI code activation, watcher, updater, subprocess, timer, provider/model/index call; bounded manifest metadata cost reported separately |

Frame interval and frame work time are different metrics. Input-to-visible response is not input-to-accepted command, fence installation or settled effect. Instrument offered input, actual input receipt, target capture, submission, backend admission, durable append, reply arrival, layout/paint/presentation and AT announcement as separate timestamps. Record clock domain, calibration, sampling loss and instrumentation overhead. True input-to-photon latency requires independent display observation; a render callback is not photons. For static/hidden views with no eligible frames, frame quantiles are **not applicable**, not zero; missed required redraws are failures, not excluded samples.

Report CPU process-group time, wall time, RSS/private/PSS where available, shared memory attribution, GPU resident/committed values with driver/API meaning, handles/file descriptors, queue high-water, cache bytes, network/disk bytes, wakeups and energy only where measured. Do not sum shared RSS across processes as if it were unique memory. Missing GPU or compositor measurements remain U and block claims that need them.

Desktop-specific requirements are falsifiable: move windows between unlike DPI monitors without displaced hit targets; change text scale without clipped Stop/approval; resize while IME composition is active without premature submission or duplicate characters; survive minimized/occluded windows and GPU-device loss without changing canonical task state; keep reduced motion active during reconnect/reflow; bound texture/decoded-image/graph-node work; preserve focus after virtualized rows leave/re-enter view. DWM flip presentation, Wayland surface scaling and browser animation scheduling are distinct mechanisms, so one API's timestamp cannot be treated as identical cross-platform presentation evidence. [S17](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/dxgi-flip-model), [S18](https://wayland.freedesktop.org/docs/html/apa.html#protocol-spec-wl_surface-request-set_buffer_scale), [S19](https://html.spec.whatwg.org/multipage/imagebitmap-and-animations.html#animation-frames), [S16](https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows)

Freeze exact source/build/dependency lock; OS build/kernel/distribution/compositor/session; GPU/driver and hardware acceleration or fallback; CPU/RAM/resource enforcement; display resolution/refresh/scaling; fonts/locale/IME; AT version; browser/webview/toolkit; power policy; event bytes/rate/distribution; diff/artifact size; window geometry/count/visibility; network/loss/delay; cache/retention state; instrumentation; sample/quantile definition; run length; warm-up; randomized/counterbalanced order; abort thresholds; evaluator and independent oracle. Freeze the acceptance margin versus the matched TUI/headless baseline and retain failures/censored observations. A run with too few independent windows/trials for p99 precision reports that uncertainty rather than inventing confidence.

<a id="r-n-q07"></a>
## Q07. Preserve PERF-010 for graphical views

**P/C06–C07.** Run the exact N = 0/1/5/10/20 matrix under idle and high-output loads. Distinguish native windows, tabs, visible panels and subscriptions; freeze a mapping so “20 views” cannot become one active view plus nineteen unevaluated placeholders. Test all visible, one slow view, minimized views, stale/offline view and mixed TUI/GUI clients. N0 is the backend-only control, with frame metrics N/A. All cases retain the same underlying synthetic task/event/effect schedule.

Hard invariants: added passive views cause **zero additional actor/process-work launches, model calls, index jobs or effects**; they may create declared renderer processes. Count renderer-process creation separately from runtime work launches. Canonical events are appended before lossy visual coalescing; a slow renderer cannot block the canonical writer or reserved control path. Each subscription has bounded credit/queue/byte and event limits; whole-client and whole-process aggregate caps prevent N times individually “safe” buffers from exhausting the host. Pending interaction/approval/Stop/effect facts cannot be coalesced into a misleading final success.

P/C07 compares server-shared authorized projections with independent bounded client-side read-model reconstruction. The shared option may reduce duplicate parsing but risks fan-out/cache invalidation coupling; the independent option reduces central presentation coupling but may amplify CPU/memory. Neither changes the canonical writer. The decisive falsifier is loss of control/append progress, mismatch at an identical cut or budget violation. A shared projection cache must be keyed by audience and configuration/schema/source cut, not just task ID.

A disabled GUI performs no executable work. An open idle GUI still has measurable presentation/OS cost; do not call it literally free. Optional rendering/history/image decoding yields to input, Stop and current facts. Visual refresh can be paced/coalesced; command admission and mandatory durable evidence cannot. A bounded deferred redraw is not a replay gap. On pressure, discard re-derivable pixels/history caches and resynchronize honestly rather than retaining unlimited decoded artifacts.

Acceptance uses the full vector and OR-024 ordering: correctness/authority/recoverability/resource/accessibility floors first, responsiveness then subscription efficiency then completion. Do not hide an idle regression behind a scalar “UX score.” All matrix cells remain U until separately admitted local qualification, and no model/provider call is needed for this graphical cost suite.

<a id="r-n-q08"></a>
## Q08. Accessibility target and independent acceptance

**P/C08.** Target WCAG 2.2 Level AA, assessing all 55 A/AA criteria against the complete release workflows. The normative criterion text remains at [WCAG 2.2](https://www.w3.org/TR/2024/REC-WCAG22-20241212/); the report does not reproduce it. The 55-row `accessibility-ledger.md` / `.json` supplies criterion IDs/links, Recursion-specific applicability, synthetic input and independent oracle. Every result is **unknown-until-run**. Conditional media/authentication criteria require a feature inventory; they cannot be marked N/A simply because a demonstration omitted those views.

<a id="wcag-applicability-facts"></a>
For browser/webview content, evaluate WCAG's web conformance requirements and complete processes. For native software, use the informative [WCAG2ICT guidance](https://www.w3.org/TR/wcag2ict-22/) to document an explicit applicability interpretation alongside real OS accessibility testing. WCAG2ICT neither supplies a separate conformance standard nor proves the native bridge works. An automated checker, toolkit declaration or successful screenshot comparison does not establish AA. Criterion 4.1.1 is removed in WCAG 2.2; no obsolete parsing pass is counted toward the 55. Reduced motion remains an additional accepted product requirement; 2.3.3 is AAA, not mislabeled AA.

| Workflow | Representative criterion IDs; complete ledger applies | Independent workflow acceptance |
|---|---|---|
| Project/task navigation and lineage | 1.1.1, 1.3.1–1.3.4, 2.1.1–2.1.2, 2.4.1–2.4.7, 2.4.11, 2.5.7–2.5.8, 4.1.2 | Navigate synthetic parent/fork graph, identify exact selected task and return to prior focus using only keyboard/speech-access path; compare to separately authored object graph |
| Artifact/diff/provenance review | 1.1.1, 1.3.1–1.3.3, 1.4.1/1.4.3/1.4.4/1.4.10–1.4.13, 2.4.4/2.4.6, 4.1.2 | Reviewer finds independently seeded changed line, missing evidence and unresolved outcome in both spatial and sequential presentations |
| Conversation/questions/approvals | 1.3.2, 2.1.4, 2.2.1–2.2.2, 3.2.1–3.2.2, 3.3.1–3.3.3/3.3.7, 4.1.2–4.1.3 | Read target/action/expiry, answer the exact waiter and recover composer focus under streaming output; wrong generation cannot be released |
| Stop/control and recovery | 1.4.1/1.4.3/1.4.11, 2.1.1, 2.4.3/2.4.7/2.4.11, 2.5.2/2.5.3/2.5.8, 4.1.3 | Identify scope/mode, issue authorized Stop and distinguish accepted versus unresolved using AT and keyboard while output saturates |
| Configuration and client connection | 1.3.5 where relevant; 3.1.1–3.1.2, 3.2.3–3.2.4/3.2.6, 3.3.1–3.3.4/3.3.7–3.3.8 | Resolve invalid/stale revision, review effect and apply exact intended change; connection flow offers a usable accessible path without GUI custody of provider secrets |
| Rich media artifacts, if exposed | 1.2.1–1.2.5, 1.4.2, 2.2.2, 2.3.1 | Synthetic prerecorded/live media fixture and independent content transcript establish what is presented and missing; no auto-play or omission can hide the criterion |

**OS bridge acceptance, not a vendor assertion:** Windows needs actual UI Automation names/roles/patterns/text/selection/focus/events for core controls and virtualized reviews. Linux needs an AT-SPI tree, text/actions/relations/states and events on the admitted desktop/compositor/AT combination. Apple NSAccessibility is a comparison point if macOS is later evaluated. Each bridge API provides mechanisms, not a Recursion conformance verdict. [S13](https://learn.microsoft.com/en-us/windows/win32/winauto/entry-uiauto-win32), [S14](https://gnome.pages.gitlab.gnome.org/at-spi2-core/libatspi/), [S15](https://developer.apple.com/library/archive/documentation/Accessibility/Conceptual/AccessibilityMacOSX/)

Proposed first local matrix: Windows Narrator plus an independently selected NVDA profile, and Linux Orca on an explicitly admitted desktop/session; optional Apple VoiceOver comparison only after a macOS profile is authorized. Exact versions, availability and coverage are U. A product must declare its accessibility-supported environment rather than claiming all screen readers. Include knowledgeable independent accessibility review and user task sessions; no paid tool, participant engagement or install is authorized by this research. Test every default and supported high-contrast/theme combination, narrow layout, scale profile, high output, offline recovery and enabled core plugin contribution. Document unsatisfied criteria and limits before any conformance statement.

<a id="r-n-q09"></a>
## Q09. Keyboard, focus, contrast, resizing and announcements

**P/C08–C09.** Actions have stable semantic names and target capture rules. Supply a discoverable palette, region traversal and menu paths, so a captured platform shortcut is not the only route. Keep printable-key shortcuts out of message/IME composition unless explicitly enabled in a named navigation mode. Every visual drag has click/menu and keyboard alternatives; pointer alternatives do not replace keyboard completeness. Selecting a tab never acquires a terminal input lease implicitly.

<a id="apg-focus-facts"></a>
Logical order is project/task navigation → conversation/review region → composer/actions → inspector, with direct region shortcuts and persistent Stop access. Within composites, use appropriate internal navigation while letting users leave normally. Focus identity binds to a durable object or control, not its recycled row number. When a panel closes, return to its invoker if it still exists, otherwise to a declared stable parent location. Incoming output, reordered tasks and expired approvals update without jumping focus to a different action. Modal behavior and focus restoration follow the applicable pattern, verified independently rather than copied blindly. [S03](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/), [S31](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/)

**Visual checks with scoped source interpretation:** test ordinary text at 4.5:1 and qualifying large text at 3:1; control/meaningful graphics contrast at 3:1 where the criterion applies. Use actual computed theme values and normative exceptions, not rounded near-passes. [S21](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html), [S32](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) Changed lines carry insertion/deletion labels and symbols as well as color. Authority and effect states always have readable text. “Unknown” is not represented by low contrast alone.

Text must survive 200% resizing. Narrow/reflow assessment uses the applicable 320-CSS-pixel width or 256-CSS-pixel height equivalent; essential two-dimensional content needs a reasoned exception, not a blanket exemption for the whole app. Offer unified linear diff and lineage adjacency views from the same projection. Native device-independent mapping is explicitly documented in the test profile. [S33](https://www.w3.org/WAI/WCAG22/Understanding/resize-text.html), [S22](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html) The spacing test applies the specified line/paragraph/letter/word overrides to review text without losing action labels or content; do not force those values as the default theme. [S27](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html)

Focus must be visible and not entirely hidden by app-created layers; this candidate additionally aims for fully visible critical Stop/approval controls, without calling that stronger preference an AA requirement. Test overlays, sticky bars, zoom and virtualized scrollers. [S23](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html) Pointer-target checks use the 24-by-24-CSS-pixel rule or a documented allowed exception; the independent test examines adjacent hit regions rather than icon pixels alone. [S24](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)

Reduced motion respects the platform preference and an explicit app setting; a user-requested reduction wins over decorative transitions. Replace animated token arrivals, pane slides, graph fly-throughs, blinking cursors/progress and smooth auto-scroll with stable updates where applicable. No blanket suppression of useful status. Check setting changes during a running stream and after crash/reconnect. CSS preference detection is a mechanism; it does not establish that every animation obeys it. [S28](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html), [S29](https://www.w3.org/TR/mediaqueries-5/#prefers-reduced-motion)

Announcements are a distinct bounded semantic channel: newly pending interaction, authority/input-control change, Stop acceptance/failure, loss of connection, replay gap and unresolved completion. Deduplicate by event/interaction generation; preserve a reviewable history. Group routine progress at a frozen configurable rate and announce counts, not every token. Critical failures cannot be starved by routine progress; repeated copies of the same critical event do not flood speech. Focus/caret remain stable. The rate, maximum backlog and maximum important-event delay are U until a human-checked profile freezes them. Validate status exposure in the actual AT output, not only the API event. [S25](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)

Client connection/authentication must be accessible without turning provider sign-in into a GUI secret store. A required external handoff is named and independently checked end-to-end; automatic paste blocking or cognitive puzzles cannot be waved away as “security.” Any claim is scoped to the authorized connection flow and applicable exceptions. [S26](https://www.w3.org/WAI/WCAG22/Understanding/accessible-authentication-minimum.html)

<a id="r-n-q10"></a>
## Q10. Preserve accessible terminal capability

**P/C09.** Reuse the backend's semantic status, object IDs, interaction IDs, command catalog and receipt fields. Maintain a plain sequential text presentation inside the GUI and retain the scriptable/plain-text terminal route. Graphs, colorized diffs and hover provenance enrich the same facts; their equivalents are searchable lists, labeled changes and explicit inspect actions. GUI features must not require a model-generated description merely to become screen-reader-readable.

Compare full workflows, not only command inventories: finding work; identifying target/scope; reading exact pending action; editing unsent input; steering versus queueing; Stop and uncertainty inspection; configuration explain/apply; source/context review; detach and resume observation. Preserve TUI command naming and exportable binding intent, but translate OS/AT-reserved chords explicitly rather than literally copying every key. The user can reach the same action through the palette even when a chord is unavailable.

A TUI fallback is not an exemption from the GUI's acceptance target. An inaccessible GUI control fails its GUI profile even if an expert can use the CLI instead. Likewise, a GUI semantic tree cannot retroactively qualify raw ANSI output. Independent F04/F09 checks compare task success, target correctness, status availability and focus restoration in the GUI and R-K plain-text/screen-reader surfaces. Failure to expose even one previously available required fact/action is a regression; passing only proves the frozen workflow/profile, not equal accessibility for every user.

<a id="r-n-q11"></a>
## Q11. Honest offline and cached projections

**P/C10.** The candidate cache is a disposable authorized read replica, never a canonical writer. Its envelope binds audience, projection/schema version, source cut, writer incarnation, snapshot identity, relevant authority/configuration revisions, completeness/gap metadata, local receipt time and source synchronization time with clock provenance. Fields are application metadata, not amendments to M1B.

Render explicit states: current synchronized observation; live but lagging; disconnected cached view; resynchronizing; gap/reconstructed from snapshot; permission unavailable; incompatible schema; or no usable cache. A “last synchronized” boundary includes source cut plus a readable timestamp; a local clock alone cannot prove backend freshness. Clock uncertainty is shown. A cached task may be inspected under the authorized local retention policy, but the UI cannot infer the process is running, stopped or still authorized from silence.

The cache is scoped before materialization. It excludes provider credentials, auth environment and raw privileged handles. Audience/scope/schema changes invalidate reuse. A revoked scope cannot fetch new denied bytes; on reconnect, validate scope before installing new projection content. Existing lawful disclosure cannot be retroactively undone on an offline or compromised client. If the threat model forbids persistent offline disclosure, compare memory-only caching with encrypted bounded persistent read caching; encryption at rest alone does not stop a same-user compromised process. Expiry/quota/eviction/delete policy and any local authentication binding are separate unanswered implementation choices.

Unsent drafts may be saved locally with that exact label. They confer no grant, reservation, accepted queue position or guaranteed delivery. They are never auto-submitted when connectivity returns. Reconnection first reconciles existing command IDs and revalidates fresh authority, target revisions, expiry and exact intent. If the user elects to submit a draft afterward, it enters the normal typed admission path. No local-first conflict merge/CRDT is allowed to merge grants, approvals, accepted plans or effect settlement. A view layout can reconcile as a presentation preference under its declared config semantics; that does not authorize work-state merging.

A genuine lost prefix below the replay floor must visibly show its missing interval and verified snapshot boundary. Do not synthesize missing dialogue. A slow locally deferred render is not declared loss. Snapshot content and cursor installation must be atomic at the application level; after a crash, use either the old coherent envelope or the verified new one, never new cursor with old content. A service worker/cache implementation is one option, not a durability/authentication proof. See R-L Q04 and the existing replay-store record for the wire/application distinction.

<a id="r-n-q12"></a>
## Q12. Detach and reattach without relaunch

**P/C10–C11.** The runtime daemon/broker owns actors, adapter sessions, process handles and work lifetime. The graphical host owns windows/renderers. Their independent lifetimes must be visible in source ownership and process topology, not only documentation.

| Interruption | Client behavior | Backend/reattach evidence |
|---|---|---|
| Window/tab close | Release that subscription and view resources; save only authorized draft/layout/cache | Runtime task/process/effect identities unchanged; another client still sees same facts |
| Last window/application close | Close graphical host only, unless a distinct daemon-stop command was explicitly submitted | Zero-view interval retains task; no runtime-owned adapter closes as a side effect |
| Host sleep | Record disconnection upon wake; discard assumed freshness and stale leases | Query same task and old command IDs; a sleeping execution host's actual state remains unknown until observed |
| Network loss | Bounded reconnect policy; cached inspection only; no invented acceptance | Fresh authentication/scope and version checks; replay from cursor or justified RESET/snapshot |
| Renderer/client crash | Unsaved local draft may be lost, and that limitation is explicit | Coherent cache envelope or safe empty view; no command resubmission or inferred effect success |
| Backend restart/failover | Refuse old authority/process/writer assumptions; retain last-known facts as stale | New fenced writer/daemon identity verified by shared service; projection repair does not elect a writer |

Attach flow: identify current backend/protocol → verify read scope → request snapshot/cursor continuity → install verified snapshot/content atomically → establish fresh bounded credit → apply authorized ordered events → resolve outstanding receipts/interactions → restore local focus/layout only where referenced objects remain. Obtain an input lease only through the existing explicit control mechanism; opening or focusing the window is not lease acquisition. D-020 failover remains an opt-in first-party availability plugin, not a browser-tab leader election.

The independent oracle records pre/post runtime actor IDs, launch/model/index/effect counts, ownership handles and canonical command receipts. Renderer process counts may change; actor/effect launch counts may not because of attach. If runtime work legitimately finishes during detachment, the result is shown by replay, not relaunched to match an old screen. A missing process due to an independently modeled execution-host failure must not be hidden by starting it from the GUI. F06 tests positive reattachment, gaps, failures and uncertainty.

<a id="r-n-q13"></a>
## Q13. Security and hostile-view fixtures

**P/C03/C05/C11.** The GUI has no canonical write handle, no provider credential custody and no authority derived from a tab, deep link, cache row or notification. It receives only authorized projections and submits schema-bounded typed intents. Backend admission rechecks current principal, exact scope/action/arguments, target revisions, grants, pause fences and budget independent of any renderer claim.

Separate ordinary authenticated client control from provider credentials. A narrowly scoped client-to-backend session capability may be necessary, but it is not a provider secret and cannot be embedded in artifact URLs, logs or caches. Its provisioning/revocation mechanism remains a security design input; no persistent credential is created here. D-029's operator-provisioned trusted-launch boundary remains outside the GUI's readable domain. Denying direct credential-file reads is insufficient if a powerful delegated CLI/tool can export secret bytes through output; R-E owns that full threat test.

Treat model output, repository documents, Markdown/HTML/SVG, images, diff contents, filenames, links and plugin-rendered widgets as untrusted data. Inert rendering is the candidate default: no script/remote resource load, shell execution, hidden navigation, command URI or credential request caused merely by displaying an artifact. Resource limits cover decompression, images, fonts, graphs, long lines and parsing. Escape misleading control characters and label bidi/invisible characters in security-relevant identities/diffs without corrupting original evidence. External opening/export is an explicit separate operation with recipient/scope checks, not an automatic preview side effect.

For web embodiments, validate IPC sender/origin and deny general native-call bridges; restrict navigation, external links and embedded frames. The documented Electron warning that web frames may send IPC motivates a concrete negative test, not a selection of Electron security settings as sufficient Recursion isolation. [S05](https://www.electronjs.org/docs/latest/tutorial/security) Browser-hosted clients also need authenticated origin-bound endpoints and protection against cross-origin command attempts; do not expose a loopback service publicly to make the UI convenient. Native variants need equivalent narrow IPC and safe parser/plugin boundaries. No same-user or inter-view security guarantee follows from splitting processes.

| Negative fixture | Independent rejection predicate |
|---|---|
| Direct canonical-file/database mutation from renderer | No canonical handle/API or writable mount available; attempted bypass refused by boundary; canonical digest unchanged; successful authorized command positive control still works |
| Fake local receipt or modified cache authority | Backend disregards local accepted/grant claim, rejects stale/forged target and preserves actual receipt history |
| Hostile artifact/plugin bridge call | No shell/network/credential/canonical write side effect; effect sink count unchanged; denied call evidence preserved |
| Synthetic credential sentinel | Sentinel in separately modeled credential domain never appears in GUI projections/cache/logs/crash exports/AT text; disabled-boundary positive control must detect it |
| Deep-link/click/notification target spoof | Displayed target/action and submitted semantic bytes match; command never triggered by passive preview; invalid origin/target refused |
| Revoked view / scope-switch cache reuse | No new denied bytes; cached state marked and handled per declared retention policy; prior disclosure explicitly not undone |
| Browser/desktop update changes operation meaning | Schema/semantic version mismatch fails negotiation; app cannot reinterpret an accepted intent silently |

F02/F08/F10/F13 operationalize these cases with synthetic data. Passing is bounded evidence for the tested boundary, not immunity to malicious OS/kernel/toolkit/AT software, a determined same-user attacker or external exfiltration channels beyond the declared model. Security tools/AT with pre-existing OS permissions are part of the trust profile; accessibility is not weakened by hiding meaningful state as a shortcut to confidentiality.

<a id="r-n-q14"></a>
## Q14. Incremental TUI-to-GUI construction and surface switching

**P/C12.** Build reusable semantics first while implementing the terminal first. Keep the comprehensive capability scope; this is construction ordering, not a new release cut.

1. Freeze shared semantic catalog, target/authority model, query cuts, receipts, configuration resolution, supported capability/loss explanations and conformance vectors through R-L. Stabilize accessible plain-text facts through R-K
2. Add a replaceable read-only GUI client over recorded/synthetic projections: project navigation, lineage, artifact/diff/context/provenance inspectors, plus the semantic accessibility tree. It starts no task, model or indexer. Compare at identical cuts with TUI before adding controls
3. Add typed control widgets by binding the existing operations, including all ten control families, explicit mode/scope, approvals and configuration. Run refusal and receipt-equivalence tests; do not implement GUI-specific effect handlers
4. Add bounded streaming, coherent offline cache and reattach; preserve existing task and command IDs during surface-switch. Implement one view lifecycle adapter per platform, separate from runtime ownership
5. Qualify AT, IME/DPI/rendering/packaging and N-view costs for each admitted floor/profile. Compare graphical reviews with strong TUI/plain-text baselines using matched artifacts and full human effort
6. Ship the accepted GUI capability opt-in with inert disabled paths and removable GUI payload. Resolve the exact “later” timing versus first-release packaging explicitly before claiming release readiness

Reuse layout concepts (navigation, focused task, transcript, composer, inspect panels, event/status view), action names and binding intents rather than preserving terminal pixel geometry. Export keybinding intent with context and conflict explanations; retain a discoverable action path for OS/AT-reserved keys. Surface-switch transfers opaque authorized task/view references and optional local presentation state, never active authority by serialization. Draft transfer is explicit and scope-checked; accepted queued input is queried by durable ID, not copied into a second queue. Deep links resolve objects through current authorization.

Existing TUI/CLI must remain usable if GUI fails or is uninstalled. Compare shared codecs with independently implemented codecs against independent goldens; code reuse alone does not establish no drift. D-033 porting cost is a hypothesis: record adapter/editor/AT/security/packaging/test changes, maintenance and review time before claiming a reuse advantage. R-I's source observations and R-J/R-K prior-art comparisons are useful precedents, not proof that this GUI can be cheaply imported.

<a id="r-n-q15"></a>
## Q15. Value proposition, falsifiers and explicit non-proofs

**P/C12.** The useful hypothesis is narrower than “GUI is better”: for defined lineage, source/context comparison and artifact-review tasks, the graphical arrangement may reduce time and errors in finding evidence and selecting the correct next authorized action, without violating resource/review floors. A strong keyboard-first TUI with an external diff viewer and the same semantic backend is the competitor, not a deliberately crippled terminal.

Freeze representative synthetic continuity tasks: locate the unresolved effect after Full Stop; distinguish an upstream session from persistent task; compare context epochs without losing the accepted instruction; review a forked dirty source artifact without accepting the original; reconnect after a visible gap and identify what is unknown. Counterbalance matched task variants and surface order. Use an independent artifact/evidence oracle and blinded review of final decisions. Measure target-selection errors, false acceptance, omitted uncertainty, task correctness, active human review/correction time, time-to-control, training/binding burden, total local resource cost and accessible task success. Waiting and active effort are separate; resource savings and subscription savings are separate. This provider-free study can measure UI tasks; it cannot establish actual provider quota or end-to-end native/upstream performance.

Decisive falsifiers include: a required workflow needs a divergent command; only GUI can reach an accepted fact; accessibility regression; hidden default inference/indexing; frame/input/idle/cache bound breach; ambiguity mistaken for success; review/correction time offsets navigation gain; an equal-or-better strong TUI baseline; or expensive bridge/security/packaging maintenance erases claimed porting leverage. Withdraw or narrow the specific benefit claim. Such evidence does not autonomously remove an accepted capability or reopen D-019.

**This candidate does not establish:** measured performance or idle footprint; accessibility conformance; entitlement or terms clearance; route qualification; security between views; strong credential isolation; OS process-containment/availability qualification; guaranteed offline secrecy; exactly-once external effects; measured productive-continuity superiority; measured quota savings; measured porting cost; or that any toolkit solves human review burden. It supplies testable requirements, source-grounded mechanisms, competing embodiments and exact handoffs. A rendered screen, valid schema, signed package or passing synthetic fixture is insufficient for those wider claims.

<a id="r-n-q16"></a>
## Q16. Provider-free acceptance fixtures and exact local handoff

All fixtures are **UNEXECUTED**. No verified GUI implementation or GUI test entrypoint exists in the inspected evidence. Accordingly no runnable GUI command is invented. `local-test-handoffs.json` and `UNEXECUTED-local-test-handoffs.md` provide inputs, prerequisites, oracle, actions, evidence, stopping conditions and non-proofs for each case. Repository scripts were neither imported nor run. Historical finite vectors are input-design precedents, not permission to execute them.

Common prerequisites: separately admitted disposable local profile; pinned candidate GUI/TUI/backend builds; synthetic workspaces/artifacts/credentials only; no model/provider/account route configured; independent network/process/effect observer; external synthetic event/authority/effect oracle; finite resource/time bounds; current accessibility matrix and approved local tools; independently authored expected projection/command/AT facts. A positive control must demonstrate allowed work; a negative control must be detected. Stop on unexpected egress, real credentials/content, authority expansion, observer loss, unbounded work, resource/deadline breach or unsafe cleanup. Preserve failed/censored traces. Only terminate fixture-owned resources. An unavailable required oracle yields unknown, never PASS.

| Fixture | Exact accept/reject predicate |
|---|---|
| F01 Cross-surface equality | Equal audience/version/source cut/query produces equal typed facts and completeness; corresponding GUI/TUI commands produce identical semantic arguments/targets/refusals/receipt transitions apart from declared audit IDs; one unequal required field fails |
| F02 Typed-command-only mutation | Every allowed mutation has a canonical admission/receipt; renderer/cache/direct-write/hostile-content paths cause zero unauthorised effects and no canonical change; same-ID exact retry has one effect, conflicting reuse is refused; positive admitted command succeeds |
| F03 Cache staleness and gap | Disconnect immediately changes freshness; visible last-synchronized cut/time survives; no cached grant permits mutation; genuine gap marker matches independent missing interval; snapshot content/cursor remain coherent after each crash cut |
| F04 Keyboard-only complete workflows | Each required navigation/review/conversation/Stop/config workflow completes with correct target and no pointer, trap or hidden focus; panel close restores declared focus; high-output/reordered rows/IME preserve input; any unreachable required action fails |
| F05 Reduced motion | Platform/app reduction removes every declared nonessential transition in frozen scenarios, including reconnect; required statuses remain present/announced; canonical results identical; no forced smooth scroll or flashing progress; missing coverage remains unknown |
| F06 Detach/attach round trip | Close all views, sleep/network-loss/client-crash and reconnect restore same task/projection truth without attach-attributable actor/model/index/effect launch; no old receipt/waiter duplicated; legitimate backend changes/gaps shown honestly |
| F07 N-window soak | All N0/1/5/10/20 idle/high-output cells meet frozen vector bounds; zero mandatory canonical loss, unauthorized commands, input corruption or attach-triggered work; aggregate queues/handles/cache stay bounded; unknown required metric prevents pass |
| F08 Credential and hostile-view boundary | Synthetic sentinel appears in no GUI-readable projection/cache/log/AT/crash artifact; unauthorized origin/IPC/preview cannot read boundary or trigger egress/effect; disabled-boundary control detects sentinel; no strong guarantee inferred |
| F09 Accessibility/AT and TUI parity | Applicable ledger checks pass on every declared profile and complete workflow; semantic tree and actual AT output match independent facts; GUI exposes all required terminal facts/actions; conditional N/A has recorded feature proof |
| F10 Stale control and approval generation | Fresh exact command succeeds once; revoked grant, old fence/config/turn, replacement waiter, expired/changed approval and mismatched route capability are refused server-side with zero unauthorized effect |
| F11 Stop reserve and closure separation | All three modes express correct scope/boundary/uncertainty; authorized Stop meets frozen liveness bound under saturated render/history/subscriptions; close/detach sends no Stop; remote unknown never becomes settled |
| F12 DPI/IME/GPU/window fault | Mixed-scale move/resize/text scaling/composition/device-loss/occlusion preserves target, text and focus; recovery stays within bounds; zero accidental submit, task restart or authority change; missing hardware path U |
| F13 Packaging/plugin/update | Disabled GUI has no executable side effect; offline prerequisites explicit; incompatible schema refused; update cannot widen grant or reinterpret queued intent; uninstall leaves core/TUI/replay usable; artifact-origin bridge blocked |
| F14 Value and review burden | Preregistered matched GUI-versus-TUI decision-task margins and correctness/accessibility/resource floors met with independent blinded scoring; failed/unfinished cases counted; no one-number UX score or quota claim |

F01–F03/F10 are high-information semantic screens before toolkit optimization. F04/F08/F09 can reject a visually excellent embodiment early. F06/F11 must run alongside backend lifetime/control construction. F07/F12 become meaningful only after workload and budgets are frozen. F13 protects opt-in shipping. F14 tests benefit last; a fast wrong or inaccessible UI cannot win. These are qualification priorities, not product-scope deferrals.

## 17. Recommendation and falsification register

Every candidate mechanism recommendation above is bound here. Mandatory accepted requirements remain fixed; an alternative may compete on implementation only, not bypass authority or remove capability.

| ID | Candidate mechanism | Competing option | Decisive falsifier | Passing does not prove |
|---|---|---|---|---|
| C01 | Shared semantic catalog/codecs with independent goldens | Independent surface codecs conforming to same catalog | F01 semantic/refusal mismatch or target substitution | Shared source alone is independent correctness |
| C02 | Backend authorized projection with source-cut envelopes | Client reconstruction from authorized bounded event feed | Same-cut mismatch, cross-audience cache leak or unbounded reconstruction | Production store/snapshot authenticity or lower cost |
| C03 | Narrow typed shell/renderer bridge with inert artifacts | Separate isolated presentation process and protocol gateway | F02/F08 unauthorized native/effect path | Inter-view isolation against all attackers |
| C04 | Persistent mode/scope Stop affordance and separate reserve | Palette/direct-key Stop with equally visible state and reserve | F11 wrong target, unbounded control delay or close-as-Stop | Remote settlement or external rollback |
| C05 | Signed/versioned opt-in GUI bundle with explicit dependencies | Platform-managed shared dependencies plus pinned app artifact | Disabled-path work, unapproved fetch, incompatible rollback or unsupported platform dependency | Benign package, terms clearance or free distribution |
| C06 | Phase/N/load vector budgets and independent presentation telemetry | Independent per-phase/N/load telemetry versus end-to-end traces with externally reconciled phase attribution over the identical required presentation profile; negative/workload control only: Smaller declared supported presentation profile measured with same floors | Any required bound breach or hidden/censored failure | Product-wide performance or p99 beyond sampled profile |
| C07 | Shared authorized projection subscription with bounded per-view delivery | Independent bounded client projections | Slow view blocks writer/control or cross-audience fan-out leak | Better CPU/memory than competitor |
| C08 | Semantic controls plus spatial and sequential views; independent AT audit | Native-first control composition with custom spatial widgets | Any required ledger workflow/AT/focus failure | Universal accessibility or conformance from toolkit claims |
| C09 | Backend semantic announcements and stable focus IDs | Client event-to-announcement reducer under same oracle | Important event lost/starved, speech flood or wrong restored target | Equal usability for every screen reader/user |
| C10 | Coherent scoped read cache; explicit saved drafts and receipt reconciliation | Memory-only read cache with fresh requery | Stale authority, auto-submitted draft, fake gap or torn cursor/content | Offline revocation erases prior disclosure or durable cache persistence |
| C11 | Separate GUI host and runtime lifetime ownership | One package with independently supervised runtime service | Last window affects actor lifetime or attach relaunches work | OS containment or failover qualification |
| C12 | TUI-first semantics, read GUI, typed controls, then profile qualification | Parallel TUI/GUI construction using same frozen corpus | Parallel semantics, measurable review regression or port cost > native rewrite | Release timing resolution or measured productive-continuity advantage |

Stack-specific recommendations retain their own concrete rivals and falsifiers in Q05; none is selected. All current runtime verdicts remain U.

## 18. Completion gate, limitations and artifact hygiene

The coverage register contains all 16 question IDs and all 11 gate IDs with the **exact supplied text**, section/appendix locators and bounded status. Research response completeness is distinct from implementation acceptance. Gates requiring measurements are answered by candidate criteria and explicit UNEXECUTED handoffs, not marked runtime passed.

Open decisions/inputs are bounded: explicit GUI timing interpretation; actual platform/desktop/compositor/AT profiles within D-028; numeric lifecycle/resource budgets and independent measurement availability; cache retention/threat policy; GUI-client authentication boundary; permitted renderer/transport/library choices by the Owner after tests; and legal/distribution conclusions through R-H. No language/toolkit or diminished release scope is inferred to fill these blanks.

Only this lane's artifact folder was written. Protected repository files were read as instructed and not edited; auth files and actual credentials were not read. Artifact text is checked for private capture/workspace paths and credential-like material, with repository-relative provenance retained. The bounded hygiene scan and input hashes are in QA.json; they are not a universal secret-detection proof. No target test, toolkit, model/provider call, install, account action, live host action, spend, publication or merge occurred. Public documentation retrieval and static source reading establish source facts only. Independent review is still required.

## 19. Sources and cross-lane evidence

`source-register.json` / `.md` identify every cited primary URL, retrieval date, observed version or mutable status, claim scope and hash limitations. Public tool-rendered pages were inspected without a full-response byte archive; no excerpt hash is presented as a page hash. Repository input hashes bind exact local bytes at the stated commit. Mutable upstream `master`/latest docs are time-scoped observations, not immutable release certifications.

The report intentionally gives short primary-source mechanism notes and original Recursion design/fixtures. The normative WCAG criterion text and vendor guides are linked, not reproduced. Repeated route/MCP/legal/prior-art facts are cross-referenced to R-F, protocol-edges, R-H and R-I/J/K/L. Package-wide source budgets must be reconciled by source identity across lanes; the source register includes a conservative local summary allocation, not permission to exceed a shared limit.
