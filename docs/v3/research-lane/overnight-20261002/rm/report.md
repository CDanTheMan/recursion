# R-M — Claude Code terminal mods: adopt concepts, gate ports, avoid authority substitution

Research cut: 2026-10-02 UTC. Recursion baseline: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`. Public source pin: `anthropics/claude-code@52c76441cae91f6891e4712306bffb057ff6fec5`. Status: **research findings, independently unaccepted; no runtime qualification**.

## Decision summary

The useful prior art is typed interception, inspectable contributions, reactive projections and model-free controls. None requires Recursion to adopt Claude's module runtime, format, renderer or vendor. Keep an upstream mod behind a replaceable, opt-in adapter if a later authorized qualification establishes its value. There is **no code artifact cleared for porting** in this study. The competing baseline is a clean-room contribution implemented against Recursion's shared command/query contracts; an ordinary documented harness interface is the competing integration path.

The [chronology](#r-m-q01) corrects both intake assumptions; the [version record](#mods-version-facts) distinguishes current documentation from older declarations. Neither an old declaration nor an attractive tutorial is proof of the current binary’s behavior.

The central failure case is an extension acting with host privileges, changing the request or its apparent origin, then bypassing the independent effect gate. A guard or a frozen event object does not establish D-029's credential boundary or D-022's Stop authority. Dispositions D01–D18 below are research recommendations with alternatives, reversal conditions and non-proofs, not component selections.

## Evidence and scope

**SD** means source-documented by the linked primary source, not tested locally. **SO** means a static observation of bytes or records. **INF** means an explicit Recursion inference/proposal. **U** means unknown or unmeasured. Report and appendices use these classes separately.

Read-only public retrieval and static local inspection were performed. No Claude binary, mod, plugin, marketplace, provider or model was installed, built, invoked, imported, run or benchmarked. No credentials, account, live host, publication, merge or repository edit was involved. The acceptance handoffs are **UNEXECUTED** and contain no invented runnable entrypoint. Artifact hashing/format checks are not mod tests.

The operative local inputs are the committed governance, decisions D-017–D-033, active v3 goal, product, architecture, interface, terminal, CLI, plugin and performance specifications, research coverage/gaps, and bounded historical evidence. Recursion remains a native harness and orchestrator; Hermes has no executive authority. Codex App Server remains the first qualification priority, not a qualified route. G-06/G-07/G-11's Owner decisions are closed, while implementation qualification remains open. The old GAPS wording cannot reopen them.

The copied lane brief says GUI is unnecessary; current instruction says TUI first, GUI later, while D-019 retains GUI as built/opt-in at first release. This study addresses construction sequencing and shared semantics only. It does not resolve that exact release-timing interpretation by silently removing GUI.

Static reading of `experiments/v3/interface-probes/contract_vectors.py` found explicit mutants for coalesced revocation, ACK-as-effective state and missing receiver fences. Its observer tests reject truncated or reordered traces. The committed FU-03 summary records a reduced-bound model result. These records motivate our negative fixtures; none ran here, qualifies mods, or substitutes for the integrated gate. See the package's gaps report for their fuller limits.

<a id="r-m-q01"></a>

## R-M-Q01 — Pinned capability, chronology and lifecycle

### Chronology: correct the premise before comparing

| Claim | Finding and evidence class | Primary pin |
|---|---|---|
| Public launch/GA date | SD: announcement dated 2026-10-01 says available that day in CLI and Desktop; official v2.1.287 release published `2026-10-01T18:00:22Z`. “GA” here denotes this announced availability, not a stability promise | [Announcement](https://claude.com/blog/claude-code-mods), [release](https://github.com/anthropics/claude-code/releases/tag/v2.1.287) |
| Minimum/default | SD: [canonical current overview](../rl/report.md#claude-mods-overview-facts) | [Overview](https://code.claude.com/docs/en/plugins/mods/overview#turn-mods-on-or-off) |
| Early access/naming | SD: publisher-linked design issue created September 3; its dated September 9 update names Claude Mods, invites use of `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`, and references v267/v268. Exact first internal/gated availability remains U | [Design issue #91870](https://github.com/anthropics/claude-code/issues/91870) |
| First published built-ins | SD/SO: September 9 commit adds `sec-default`, `diff`, `telemetry`. Earliest production rollout to every customer remains U | [Initial source commit](https://github.com/anthropics/claude-code/commit/d9c456d7dba722727cc06146ca45580eaa18b914) |
| `agents-md` | SD: v2.1.277 release published `2026-09-18T18:06:32Z`; release text originally excludes some third-party API routes. This pins that feature, not first-mod status or current entitlement | [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.277) |
| Adjacent terminal output | SD: `terminalSequence` added in v2.1.141, published `2026-05-13T23:19:16Z` | [Release](https://github.com/anthropics/claude-code/releases/tag/v2.1.141) |

All primary sources above were retrieved 2026-10-02; exact public file hashes, release timestamps and limitations are in the source register. Mutable issue headings are the publisher's dating, not a historical edit-log proof. The public declaration header and repository README are older early-access material even at the latest repository commit.

### Package and continuation contract

<a id="mods-package-facts"></a>
SD: the package has a manifest and `hooks/hooks.json` naming one module with `register(on, options)`; options contain declared user configuration. [Create a mod](https://code.claude.com/docs/en/plugins/mods/create)

<a id="mods-events-facts"></a>
SD: `on` binds an event, optional matcher and `($, e, next)` handler. Continuing unchanged, forwarding a changed copy and returning an answer are different outcomes. Inputs are immutable; results can also be rewritten. Answering stops later handlers. INF: these outcomes need distinct receipts. [Event guide](https://code.claude.com/docs/en/plugins/mods/events)

<a id="mods-reload-facts"></a>
SD: directory development loads can reload in-session. Generated session mods require approval; approved edits load at turn-end. `register` reruns and ordinary module variables reset. Session state and persistent store have different lifetimes, detailed under Q02. An event hook is not a fresh external shell per invocation. Hook execution in a host-controlled module environment is not a security sandbox. [Create guide](https://code.claude.com/docs/en/plugins/mods/create), [tutorial](https://claude.dev/blog/getting-started-with-claude-code-mods/)

SD: surface-specific availability is recorded in the [canonical overview](../rl/report.md#claude-mods-overview-facts). Those product limits do not change Recursion’s platform requirements.

<a id="r-m-q02"></a>

## R-M-Q02 — Surface map and limits

<a id="mods-reference-facts"></a>
The following is a compact current-reference inventory, not a reproduced SDK. Each row is SD for the retrieved **2.1.287 reference**, with individual machine rows and source anchors in `surface-map.json`.

| Surface | Named coverage |
|---|---|
| <a id="mods-surface-tools"></a>Tools | `tool.call`, `tool.check`, `tool.describe` |
| <a id="mods-surface-prompts"></a>Prompts | `prompt.submit/fill/suggest/edit/compose/section/context/attachment`, `skill.prompt`, `attribution.text` |
| <a id="mods-surface-commands"></a>Commands/configuration | `command.run/describe`, `config.set/describe` |
| <a id="mods-surface-turns"></a>Turns | `turn.start/step/complete`; streaming interception |
| <a id="mods-surface-sessions"></a>Sessions | `session.start/end/compact/receive/send/append/attach/detach/measure` |
| <a id="mods-surface-subagents"></a>Subagents | `agent.offer/spawn` |
| <a id="mods-surface-ui"></a>UI | `ui.render/resolve/press/input/select/focus/scroll/close/message` |
| <a id="mods-surface-composition"></a>Composition | `plugin.register`, `engine.create`, `classic.<Event>`; API-method interception |
| <a id="mods-surface-telemetry"></a>Telemetry | `telemetry.log/mark`, collector filtering |
| `$` namespaces | `plugin`, `ui`, `command`, `tool`, `agent`, `model`, `prompt`, `turn`, `session`, `config`, `settings`, `env`, `fs`, `store`, `state`, `clock`, `http`, `process`, `mcp`, `audio`, `telemetry` |
| Render sites | `Pane`, `AbovePrompt`, message/tool/command rows, `AskUserQuestion`, spinner, progress, mode and hint sites |

[Current reference](https://code.claude.com/docs/en/plugins/mods/reference)

<a id="mods-api-facts"></a>
SD: command registration can produce an immediate deterministic reply; a tool registration carries an input schema and a plugin-qualified name. Model helpers can consume the user's plan/API usage. `prompt.submit` may start a turn and `asUser:true` removes the mod-sender introduction. `session.send` returns `isDelivered:true` on queueing, which is not recipient consumption. [API guide](https://code.claude.com/docs/en/plugins/mods/api)

<a id="mods-interface-facts"></a>
SD: UI trees contain layout, text and controls; terminal-only raster/image and Desktop-only SVG are differentiated. Prop changes and invalidation redraw; a state read subscribes that site. Module variables reset on reload; `$.state` survives reload but resets at session-ending/clear/resume/branch boundaries; `$.store` persists separately. A render hook cannot write reactive state. Keyboard dispatch remains host-owned. Loading fires the module-start hook; clearing/resuming/branching requires the separate settings-hook lifecycle when rehydrating cleared state. [Interface guide](https://code.claude.com/docs/en/plugins/mods/interface)

SD: the [canonical overview](../rl/report.md#claude-mods-overview-facts) records the exact rendering exclusion; qualify earlier decision influence separately.

<a id="mods-old-types-facts"></a>
SD/SO, **older 2.1.277 declarations only**: modules have neither Node nor DOM globals; dynamic string-code evaluation and WebAssembly are excluded. The declared `turn.step` chunk contract allows forwarded/rewritten chunks and synthetic chunks. This establishes historical expressiveness, not permission to rely on an undocumented GA stream field. Exact current stream-rewrite guarantees, complete renderer internals and isolation implementation are U. [Pinned declarations](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/types/claude-code.d.ts)

INF: reading session state is observation; changing a model, sending a prompt/message, registering an executable callback, reading files, network access and spawning processes are separate effect classes. No `$` namespace is a Recursion grant. A terminal-only drawing cannot silently claim GUI or headless parity.

<a id="r-m-q03"></a>

## R-M-Q03 — Stability, versioning and validation

<a id="mods-types-generation-facts"></a>
SD: current documentation defers to declarations generated for the actual build in `.claude-plugin/types/`. [Create guide](https://code.claude.com/docs/en/plugins/mods/create#get-type-definitions-for-your-version)

INF: plugin distribution/cache version is not a stable host contract. Record host build, module digest, dependency closure, generated schema digest, surface and configuration together. This specifies evidence, not a packaging mechanism.

<a id="mods-version-facts"></a>
SD/SO: pinned `mods/README.md` still labels the interface early access and warns of change without notice; its declarations identify 2.1.277 and `/plugin-types`. Current docs describe generated directory layouts and expanded features instead. A notable conflict is old `mcp.call` documentation describing no prompt, whereas current admin docs describe calls under session permission rules. Neither wins for an untested target binary merely because one looks more detailed. [Pinned README](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/README.md), [pinned types](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/types/claude-code.d.ts), [admin guide](https://code.claude.com/docs/en/plugins/mods/admin)

<a id="mods-validation-facts"></a>
SD: `claude plugin validate` statically reads the package and reports hooks/API calls; `claude plugin test` executes mod tests with stubbed host answers, advertised without session/sign-in/network. These are **documented commands, not instructions executed here**. Even static validation requires running the upstream binary, outside this brief. Its test runner is excluded even if provider-free. A passing synthetic hook test would not prove permission enforcement, terminal behavior or credential isolation. [Create guide](https://code.claude.com/docs/en/plugins/mods/create#check-what-claude-code-reads-from-your-mod), [test guide](https://code.claude.com/docs/en/plugins/mods/test)

INF: until exact-build evidence exists, compatibility state is unknown and execution is ineligible. Re-pinning and declaring a semantic loss is preferable to guessing a renamed event. D10 and fixtures F01/F02 make this falsifiable.

<a id="r-m-q04"></a>

## R-M-Q04 — Concepts worth adopting, with alternatives

“Adopt” below means retain a design requirement or comparison candidate. It never chooses a mechanism. The full D01–D18 ledger gives a competitor, decisive negative trace, reversal condition, check and non-proof for each row.

| ID | Concept/disposition | Real competing design | Decisive counterexample |
|---|---|---|---|
| D01 | Adopt typed event observations as prior art | Query snapshots plus explicit observer subscriptions | Observer order changes an admitted effect or canonical result |
| D02 | Adopt explicit observe/rewrite/answer categories | Separate typed transformation and command handlers | “Answer” becomes permission; original request/provenance disappears |
| D03 | Adopt bounded declarative view contributions | Fixed built-in panels plus external read-only projections | A render callback admits an effect or owns durable task state |
| D04 | Adopt reactive projection invalidation as a candidate | Bounded polling of versioned snapshots | Coalescing loses a receipt, fence, gap or pending question |
| D05 | Adopt inspectable package identity/dependencies | Native capabilities with separately declared manifests | Disabled inventory imports code or activates a dependency |
| D06 | Adopt pre-load effect inventory as a comparison | Manifest-only requested-capability review | Scanner misses an indirect effect and review treats absence as proof |

For R-L, the benefit is a typed distinction between contribution, request and committed effect. For R-K, it is controlled drawing over existing observations. The benefit is not “more hooks” or a vendor's purported latency. A no-extension implementation providing the same accepted capabilities remains an honest baseline; it is not a smaller release proposal.

<a id="r-m-q05"></a>

## R-M-Q05 — Port candidates, cost and clean-room competitor

SO: the full, non-truncated pinned Git tree contains four built-in mod directories. Their static inventory is: `agents-md` 75 files/58,994 bytes; `diff` 821/506,662; `sec-default` 116/89,899; `telemetry` 275/163,969. Counts include tests, helpers and small index files, not just executable logic. They are **not** person-day estimates. Selected entrypoints, manifests, READMEs and type declarations were read and blob-verified; the entire dependency graph was not semantically audited.

| Artifact family | Disposition and bounded opportunity | Competing option and blockers |
|---|---|---|
| Diff layout/fixture ideas | D13 watch: possible port only after rights and dependency gates | Clean-room layout/escaping against R-K; no reuse rights cleared, host UI/state/telemetry coupling |
| Instruction-file ordering cases | D14 watch: useful test requirements, no source copied | Native context adapter from Recursion's authority/provenance specification; host prompt framing and nesting differ |
| `sec-default` | D09/D11 avoid as Recursion authority | Independent admission/fencing enforcement; code is tied to host tiers, policy and error semantics |
| Telemetry implementation | D15 avoid direct reuse of host-credential pipeline | Recursion's scoped telemetry receipts/exporter; provider-specific schema, credential and accounting assumptions |
| Type declarations and test kit | D10 watch as pinned compatibility evidence | Native versioned adapter contract with independently authored fixtures; generated types are not a portable SDK license |

<a id="mods-diff-facts"></a>
SO: `diff`'s registration file combines pane, command, prompt, store, process and telemetry concerns. A port is not just a view tree. The static sanitizer drops control/format/default-ignorable characters, including joiner/variation-selector classes. Blind reuse can conflict with R-K's grapheme fidelity and source-byte preservation. Test both display safety and semantic loss rather than calling one strip operation “Unicode support.” [Diff entrypoint](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/diff/hooks/register.ts), [sanitizer](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/diff/hooks/views/layout/sanitize-line/sanitize-line.ts)

INF cost model: compare total accepted effort, not copied lines. Port cost = rights/provenance review + dependency extraction + host-semantic replacement + authority/isolation adaptation + accessibility/rendering verification + independent review + future API-drift maintenance. Clean-room cost has the same acceptance/maintenance floor plus fresh implementation. D-033 is supported only if matched candidates preserve the same capabilities and the port's total cost is lower at an Owner-approved margin. No numeric cost or savings can be inferred from this static inspection; all cost cells are U. A single necessary non-portable credential dependency, unresolved license, failed Unicode fixture, or port cost exceeding the clean-room comparator defeats the proposed port. See F10 and `port-candidates.json`.

<a id="r-m-q06"></a>

## R-M-Q06 — Behaviors to avoid

D07 avoids unreviewed in-session production replacement; the competitor is revision-bound staged activation, with an explicitly disposable development loop treated separately. D08 avoids host-privilege execution as a containment claim. D09 avoids substituting a guard response for the common permission gate. D10 avoids making the native product depend on a mutable host API. D11 avoids mapping host abort/reload/close to Aggressive, Full or Lazy completion. D12 avoids a callback, slash command, model tool or prompt submission that enters effects outside the command schema. D15 avoids transplanting credential-coupled telemetry. These are scoped exclusions, not rejection of rich opt-in capability. Each avoidance row D07–D12/D15 in the disposition ledger now compares two conforming enforcement remedies under identical accepted floors; the named avoided behavior is a separate negative control. The original decisive falsifiers, reversal restrictions, non-proofs and fixture IDs remain applicable.

A disabled Recursion contribution must remain inert: no import, active registration, dependency activation, process/network/model work or credential access. Metadata inventory may cost CPU/disk and must be measured separately. Host flags are not evidence of this invariant; compare the [upstream disable limits](../rl/report.md#claude-mods-overview-facts).

<a id="r-m-q07"></a>

## R-M-Q07 — No lock-in, launch boundary and negative traces

INF architecture constraint: Recursion owns task identity, canonical history, grants, budgets, current revision and effect receipts. An upstream mod may supply an observation or implement an already-admitted adapter operation; it may not supply their authority. The native loop remains first-class and must start, recover and explain state without loading Claude modules. Removing the adapter must leave a truthful missing-capability result, not corrupted canonical state or hidden fallback inference.

For D-029, placing code inside the authenticated harness is especially sensitive: direct access to credential locations, indirect export by a permitted process, environment-derived output and unconstrained tool/network exfiltration all matter. “Recursion never calls the credential API” cannot prove non-access. No Recursion-controlled mod may be smuggled into the credential-bearing boundary as if it were harmless presentation. The required trusted launcher is operator-provisioned outside Recursion's readable domain; admissible output is independently bounded. This is a design constraint, not a demonstrated enclosure. R-E owns qualification of that boundary.

Decisive negative traces are D08's synthetic secret reaching output; D10's native boot needing the upstream module; D12's UI action executing with an old epoch; D11's closed pane reported as settled external work; D15's exporter borrowing an upstream credential. These traces reject a candidate even if every normal-path screenshot looks correct. A source-only check can identify a documented path or a missing mediation requirement; it cannot prove absence of all runtime escapes.

<a id="r-m-q08"></a>

## R-M-Q08 — Licensing, plugin terms and counsel boundary

<a id="mods-license-inventory"></a>
SO: at the source pin, root `LICENSE.md` reserves rights to Anthropic and points to its Commercial Terms. It is not an MIT/Apache/BSD grant. No nested LICENSE/LICENCE/COPYING/NOTICE file appears under `mods/`, and the four inspected plugin manifests omit a license field. A helper named `held-notice.ts` is code, not a license notice. This is exact inventory evidence, not a legal judgment that no other permission can exist. [Pinned license](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/LICENSE.md), [pinned source tree](https://github.com/anthropics/claude-code/tree/52c76441cae91f6891e4712306bffb057ff6fec5/mods)

SD: use [R-H’s Claude legal note](../rh/report.md#claude-legal-facts) and [sole legal evidence appendix](../rh/report.md#appendix-b-public-evidence-register) for RM-S24. This lane adds no legal excerpt or route clearance. Public readability, instructional examples, a plugin listing and Recursion’s Apache-2.0 direction do not establish adaptation, redistribution, sublicensing, compatibility or use entitlement.

<a id="mods-publishing-facts"></a>
SD: publishing guidance describes own-marketplace and directory distribution, version handling and validation. That is a technical distribution path, not permission to redistribute someone else's code. [Publishing guide](https://code.claude.com/docs/en/plugins/publish)

<a id="mods-directory-facts"></a>
SD: Software Directory Terms dated March 16, 2026 cover rights/privacy representations, indemnity, documentation/branding permissions, review and removal, maintenance and changing terms. They do not grant a submitter Anthropic IP rights. Directory Policy dated April 15 adds safety, privacy, collection and instructional-software restrictions. Its context/history restrictions need route-specific interpretation against the mod capabilities advertised elsewhere. Do not resolve that apparent tension by technical inference. [Directory Terms](https://support.claude.com/en/articles/13145338-anthropic-software-directory-terms), [Directory Policy](https://support.claude.com/en/articles/13145358-anthropic-software-directory-policy)

Counsel questions L01–L08 in `license-terms-ledger.json`: applicability of linked terms to each source artifact and research/reuse activity; actual grant for modification/redistribution and notices; generated declarations/examples; independent implementation versus adaptation; marketplace/directory obligations; service/subscription restrictions; branding/trademark; and compatibility with Recursion's chosen distribution direction. G-32 stays open. No code, license body or test implementation is reproduced in this packet. No counsel contact occurred.

<a id="r-m-q09"></a>

## R-M-Q09 — Security properties and known-safe refusal

<a id="mods-security-facts"></a>
SD: mods have user-level access, are not sandboxed, and can launch processes outside the host's Bash sandbox. They can access sensitive environment/settings data. This is negative prior art for Recursion's stronger boundary, not a finding of an exploited vulnerability. [Announcement](https://claude.com/blog/claude-code-mods), [plugin security](https://code.claude.com/docs/en/plugins/security), [admin inventory](https://code.claude.com/docs/en/plugins/mods/admin#review-what-a-mod-can-do)

<a id="mods-publisher-trust-facts"></a>
SD: plugin provenance does not certify behavior; plugin code and updates require publisher trust. Permission rules for model-invoked tools do not cover all code a plugin independently runs. [Plugin security](https://code.claude.com/docs/en/plugins/security)

<a id="mods-failure-facts"></a>
SD: normal handler failure before continuation can skip the handler; after continuation, the downstream result stands. A `.catch` handler can return refusal but has a separate time bound. SD: managed guards have narrower fail-closed behaviors and load/order conditions, not universal isolation. [Event errors](https://code.claude.com/docs/en/plugins/mods/events#handle-a-hook-that-fails), [admin guide](https://code.claude.com/docs/en/plugins/mods/admin)

<a id="mods-permission-facts"></a>
SD: `tool.check` may replace ask/non-managed-hook decisions and bypass the auto classifier on approval. Deny-rule protection depends on managed/organizational context; managed pre-tool blocks and certain mandatory interactive tools retain separate protections. Therefore neither “all deny rules can be bypassed” nor “deny always wins” is an accurate blanket statement. [Permission documentation](https://code.claude.com/docs/en/permissions#extend-permissions-with-hooks)

<a id="mods-guard-facts"></a>
SO: pinned `sec-default` uses tier-aware continuation, settings reads and explicit error handling; it does not become an OS sandbox. [Guard registration source](https://github.com/anthropics/claude-code/blob/52c76441cae91f6891e4712306bffb057ff6fec5/mods/sec-default/hooks/register.ts)

INF refusal design: unknown build/schema, unavailable dependency, changed artifact, expired authority or insufficient containment yields an explicit incompatible/no-effect receipt before activation. A failure after an effect began yields failed/cancelled/uncertain with retained effect identity. It cannot reuse `attempted=false`. Observer failure must not admit effects; required policy failure must not silently continue. Preserve operator Stop independently of redraws, hooks, timers and the extension's own error path. F03–F08 specify counterexamples; `security-ledger.json` distinguishes each observed/source risk from the proposed defense.

<a id="r-m-q10"></a>

## R-M-Q10 — What this study does not prove

No API stability, source-license fitness, legal permission, entitlement, account/subscription eligibility, measured performance, latency, accessibility, sandboxing, credential non-access, security completeness, binary/source parity, portable mod runtime, successful port, productive-continuity gain or measured savings is established. An API without a mandatory model call is not evidence of zero total inference or zero bill. A documented feature is not a qualified Recursion route. Absence of a source file is not absence of a binary feature. Hash equality binds inspected bytes, not their safety.

No final language, store, framework, runtime, extension mechanism, plugin format, transport, toolkit, renderer, sandbox product or vendor is selected. No accepted decision is reopened and no new executive tier is proposed.

<a id="r-m-q11"></a>

## R-M-Q11 — Relationship to R-L

The model is **complementary prior art** for contribution identity and typed input/result distinctions, **a different trust tier** when executing inside a credential-bearing host, and **a competing mechanism** if offered as Recursion's native extension substrate. The third role is rejected pending D10's conditions; it is not required for the first two.

R-L contributions should name component/version/schema, request scope and provenance; views query projections and controls submit the same admitted command as CLI/GUI. A mod's `answer` means intercepted computation, not an authorized effect or accepted decision. Preserve both original and rewritten request identities; bind authority to the actual admitted action. A prompt formatted “as user” remains attributable to its producing component in Recursion's records. Keep upstream queue acknowledgement below consumed/adopted/settled semantics.

Cross-lane handoff: R-L Q03 (contribution identity/inert disabled state), Q12 (adapters), Q13 (no UI-origin authority), C03/F02; R-J's delivery-boundary receipts. Their reports are research drafts pending independent review. No command registry, settings database, authorization plane or executive is duplicated by this proposal. D01/D02/D05/D12/D18 and F03/F04/F06/F13/F14 express the comparative gates.

<a id="r-m-q12"></a>

## R-M-Q12 — Relationship to R-K and existing affordances

Panes, above-prompt bands and redraw subscription are existing UI affordances, not Recursion novelty. Treat them as **complementary presentation candidates**. They compete with fixed built-in views and versioned snapshot observers, not with canonical task ownership. A subscription should refresh a bounded projection without moving a reader's semantic scroll anchor; if the user has scrolled back, show pending output and preserve their location. Rendering is a snapshot, not proof every intermediate event was retained. Important receipt transitions need an independent durable path.

<a id="claude-accessibility-facts"></a>
SD: the upstream screen-reader mode uses linear labeled text and static progress, but attached background sessions and some announcements have documented limitations. No mod-specific accessibility equivalence follows. [Accessibility guide](https://code.claude.com/docs/en/accessibility)

<a id="claude-terminal-notification-facts"></a>
SD: `terminalSequence` is a settings-hook output, not new mod UI. It delegates selected BEL/OSC title/notification sequences to the host terminal writer, rejects other sequences, and is ignored for headless/SDK output. This is **existing terminal mediation prior art**, not permission for raw untrusted control bytes. [Hooks reference](https://code.claude.com/docs/en/hooks#emit-terminal-notifications)

INF R-K requirements remain stronger: sole terminal-writer coordination, partial-write/resize correctness, semantic follow-mode, grapheme/IME fidelity, scoped keyboard commands, control progress under saturation, non-color-only labels, reduced motion and equivalent text access. The sanitizer counterexample in Q05 demands separate source bytes and safe display representation. Neither a vendor animation nor a redraw-rate cap proves non-flicker behavior, accessible task completion or latency.

Cross-lane handoff: R-K Q06/Q07 rendering; Q08 anchors/follow; Q09 Unicode/OSC; Q15–17 accessibility/Stop. Its F07–F10/F13 complement R-M F08/F09/F11. Test meaning and owner control, not pixel resemblance. D03/D04/D16/D17 include alternatives, falsifiers and non-proofs.

<a id="r-m-q13"></a>

## R-M-Q13 — Complete disposition and negative-trace rule

The authoritative machine ledger is `disposition-ledger.json`; the readable full ledger is `disposition-ledger.md`. D01–D18 each includes: scope, adopt/port/avoid/watch, evidence IDs, competing option, decisive falsifier, what could change the research disposition, provider-free check, and non-proof. A port designation means a conditional investigation candidate, never clearance. Among the four source families inspected, zero candidates were qualified for porting by this research. Actual feasible/acceptable port count and port cost remain unknown: no port, rights clearance or matched-cost gate was executed.

For every entry, the independent verifier first confirms the source fact, then checks the proposed invariant against a deliberately failing synthetic trace and a useful permitted control. Refusing everything is not a passing design. For an avoid row, the listed future evidence can narrow that research exclusion only while preserving accepted decisions. Evidence cannot authorize reopening D-018/D-021/D-022/D-029. If a change removes the risky behavior, it is a new scoped candidate, not proof the old one was safe.

<a id="r-m-q14"></a>

## R-M-Q14 — Provider-free evidence acceptance

`UNEXECUTED-acceptance-handoffs.md` and `acceptance-handoffs.json` specify fourteen bounded checks. Each has inputs, prerequisites, independent oracle, expected records, stop conditions, negative control and non-proof. They require only source reading and synthetic trace/table reasoning; no mod or Claude binary is run. There is no verified executable acceptance entrypoint for R-M. These handoffs accept/reject the **study's evidence and disposition rationale**, not an implementation. Runtime and legal qualification remain separate blocked gates.

The verifier must reproduce full-file Git blob hashes from approved read-only retrieval, keep old/current contracts separate, check official date/version claims, challenge each disposition with its named counterexample, and ensure every recommendation maps to an independent check. Unknown fields stay null/unknown. At least one useful allowed operation must remain in the authority fixtures. Reject the report if it repeats a marketing benchmark, treats the older declaration as GA behavior, treats a built-in source listing as an open-source license, equates a hook denial with Full Stop, or marks an unexecuted fixture passed.

### Bounded unknown register

| ID | Unknown | Next evidence/decision; stopping boundary |
|---|---|---|
| U01 | Exact first pre-public availability and rollout breadth | Historical official release/announcement records; retain unknown if absent, never infer from user bug reports |
| U02 | Exact 2.1.287 generated declarations/binary equivalence | Later separately authorized installed-build export and read-only comparison; no binary operation in this lane |
| U03 | Stable API/support/deprecation guarantee | Explicit publisher commitment; until then keep compatibility unqualified |
| U04 | Reuse/distribution and account/route rights | Per-artifact counsel ruling under G-32/D-027; no technical proxy |
| U05 | Whole dependency closure and portable subset | Complete selected-artifact static graph plus licensed extraction scope; stop at hidden host dependency |
| U06 | Port/rewrite cost and maintenance benefit | Matched accepted candidates and total-work receipts under a new engineering admission; no estimate fabricated |
| U07 | Boundary enforcement and external effect mediation | R-E/R-U qualification at D-028 floors; no mod or source-only test can close it |
| U08 | Accessibility, rendering and productive continuity | R-K/R-L accepted fixtures on explicitly admitted targets; screenshot/source evidence is insufficient |
| U09 | Directory-policy applicability to proposed mod behavior | Counsel/publisher clarification tied to exact artifact and distribution route; no submission here |

<a id="completion-and-integrity"></a>

### Completion and integrity

All fourteen questions and all nine completion-gate bullets have exact text/IDs and section locators in `coverage.json`. Source retrieval, file-blob verification and deliverable-format/privacy checks are recorded separately from unexecuted acceptance. Protected repository paths were never written. Delivery artifacts contain authored analysis and metadata, not raw source bodies, credentials or private capture paths. Independent review remains pending; the author's checks do not confer acceptance.
