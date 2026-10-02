# Recursion mobile and remote control client candidate

2026-10-02 UTC · R-MOB · Parent goal `goal-recursion-v3-harness-orchestrator`  
Status: research candidate for independent review and Owner decision  
Source pin: `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`  
Target fixtures: **UNEXECUTED** · No mobile implementation or route qualified

## Decision summary

A mobile client can fit Recursion as an optional, replaceable authorized projection and typed control surface. It must connect to the current backend before any remote action. Pairing identifies a client; it does not delegate an executive role, enroll an execution node, transfer a provider account or grant permission to spend. An always-running Linux backend can preserve already-authorized work while a phone is absent, but does not make the phone continuously connected.

The viable contract is stronger than a secure socket: current read and effect authorization, one input holder per target, durable command identity, separately evidenced receipt facts, bounded delivery, and detach-independent backend ownership must survive every reconnect. The phone neither owns actor lifetime nor silently submits an offline queue. A command sent while connected whose result became uncertain remains subject to receipt reconciliation, not automatic duplication.

Two impossibility boundaries are explicit. A disconnected device cannot instantly learn an unseen revocation, and no protocol can retract bytes already disclosed to an offline or compromised recipient. A stolen software-held private key can also be indistinguishable from its original when used correctly. The candidate therefore distinguishes immediate backend fencing, observed client invalidation, qualified key-protection profiles and residual disclosure. It never reports universal clone prevention, instant remote erasure or remote Stop completion without evidence.

**Product choice still open:** propose a minimal, explicitly authorized last-synchronization/status view when disconnected, with private content online-only unless an independently approved retention policy permits a bounded offline snapshot. Even minimal task metadata can be sensitive. The latest user instruction fixes connected-only remote actions; it does not choose private-content retention, an authentication mechanism, transport, push vendor, toolkit, distribution route or numeric device budgets.

## Evidence and source boundary

**SD** denotes source-documented requirements or platform behavior; **LO** denotes local static observation; **IN** denotes this candidate's inference/proposal; **U** denotes unknown or unmeasured runtime behavior. All contracts, recommended defaults, threat mitigations and fixture outcomes below are IN unless marked otherwise. An expected outcome is not an observed pass.

LO: the supplied read-only export identifies 1,401 verified tracked blobs and 196 verified trees, root `a866969c9346372dcf74c2f05a7f9d648c766494`. Its pin contains merged PR149 and the following PR148. The attached README and R-MOB brief match the exported repository bytes. This report inspected text and source metadata only. Public documentation retrieval and self-authored artifact checks are the only active research operations. No target script, test or import ran. No provider/model/account/store/device/push/live-host call, credential read or creation, app build/sign/install, repository edit, deployment, publication, counsel contact, spending or Work/Codex/cloud session occurred.

The current user's two clarifications are incorporated as request context: remote control requires a connected mobile client; optional connection-method plugins may include Tailscale, SSH or other supported methods. These authorize research, not connection setup. The Owner remains final authority under [CONTROL_PLANE][R01]. [ANCHOR][R02], [AGENTS][R03] and [D-018 through D-034][R04] retain their force. Hermes is an optional upstream integration. D-019's comprehensive opt-in surface is preserved; historical graphical-release exclusions in older prose are not silently used to remove mobile/GUI capabilities. Construction sequencing and exact packaging reconciliation remain Owner matters.

### Source inputs and inherited contracts

| Input at the current pin | Binding used here |
|---|---|
| [Exact R-MOB directive][R05] and packet README | All 23 questions and 11 completion gates; no technology selection or live qualification |
| [PRODUCT][R06] and [EXECUTION-FABRIC][R07] | Client, authority coordinator, execution host, engine, inference provider and billing pool are separate; remote/node fabric is backend capability |
| [INTERFACE-STRATEGY][R08] | One semantic catalog, ten controls, Aggressive/Full/Lazy, separately evidenced continuity |
| [TERMINAL-RUNTIME][R09] and [M1B-WIRE-PROFILE][R10] | Backend owns actors/processes; bounded per-view delivery; frozen wire vocabulary and GAP recovery |
| [PERFORMANCE-PLAN][R11] | PERF-010 and OR-024; hard floors before responsiveness, subscription efficiency and completion; full vector |
| [R-L][R12], [R-N][R13], [R-K][R14], [R-X][R15] | Shared commands/receipts; authorized offline views; single input/resize holder; enrollment, separate fences, disclosure and remote effect uncertainty |
| [Prompt Plugin Skill Architecture][R16] | Installed, enabled, authorized, available, selected, loaded, executed are independent facts |
| [Shared Contract Reconciliation][R17] | Four-field ArtifactRef, eighteen-field ContentEnvelope, separate identity domains, canonical command key, one loss record, exposure-intent ordering and conserving accounting |
| [GAPS][R18] | G-05 protocol/qualification work remains open; G-32 counsel gate remains open |

The prior reports' embedded `73d70505…` and `5b55e55…` pins are historical provenance. The links above identify the current inspected bytes. Their candidates and reported historical checks are not newly ratified or rerun here.

## Public primary evidence capsules

All sources below were retrieved on **2026-10-02 UTC**. RFC numbers are fixed document identities; WebAuthn Level 3 and vendor pages are mutable publications observed on that date. Their current contents are not a claim about any installed build. Sources are prior art, not selected components. No external source is quoted verbatim. Repeated source-derived material, including the counsel rows, is accounted for in the accompanying source ledger.

- **S01** [RFC 8252][S01]: Native-app OAuth uses an external user agent and public-client PKCE. This constrains an OAuth alternative; it does not authenticate a physical device or grant Recursion work rights
- **S02** [RFC 9700][S02]: OAuth security guidance addresses redirect validation, replay, token audience and sender constraints. Token possession alone is not a sufficient design for the proposed protected control path
- **S03** [RFC 9449][S03]: DPoP binds token use to key proofs and request properties, with replay and nonce considerations. It does not guarantee safety when an attacker can invoke the legitimate key or erase every application-level replay risk
- **S04** [RFC 8705][S04]: Mutual-TLS client authentication and certificate-bound tokens are distinguishable mechanisms. Their certificate lifecycle and endpoint/proxy handling remain deployment obligations
- **S05** [RFC 8628][S05]: Device authorization includes user-code phishing and remote-phishing risks. A displayed code or QR scan alone does not establish that the user intended this backend, device key and authority scope
- **S06** [WebAuthn Level 3][S06]: Credentials are scoped to relying parties; backup eligibility/state can distinguish single-device and multi-device credentials. Successful authentication is not proof that one particular phone exclusively possesses a credential
- **S07** [Apple Keychain protection][S07]: Protection classes have different unlock, synchronization and backup properties; a passcode-bound device-only class is neither synchronized nor backed up. Profile-specific configuration matters
- **S08** [Android Keystore][S08]: Keys may be non-exportable and hardware-backed where supported. A compromised app or OS may still invoke keys on-device, so extraction resistance does not imply authorized use
- **S09** [Android Auto Backup][S09]: Backup and device-transfer rules vary by platform/profile. On some manufacturers' devices, disabling cloud backup does not disable device-to-device transfer. Restored app files cannot be assumed to preserve trustworthy enrollment
- **S10** [Apple passkeys][S10] and **S11** [Android Credential Manager][S11]: Both document platform passkey integration. These are possible account-authentication surfaces, not a replacement for Recursion's per-device enrollment and current authorization
- **S12** [APNs background updates][S12]: Background notification delivery is not guaranteed and may be throttled. Correctness cannot depend on a wake arriving
- **S13** [Apple notification payload guide][S13]: The archived guide advises minimal payloads and avoiding sensitive content. Its archival status is explicit; it is not evidence of current delivery guarantees
- **S14** [FCM message types][S14]: Notification and data messages have different handling; transport encryption is not end-to-end encryption. A delivery service therefore cannot be presumed blind to payload content
- **S15** [WCAG 2.2][S15]: Keyboard access, focus visibility, non-drag alternatives, target sizing and accessible authentication supply testable criteria. Web criteria do not by themselves certify a native mobile application
- **S16** [Apple accessibility guidance][S16] and **S17** [Android accessibility principles][S17]: Platform accessibility features and semantic UI support require deliberate design and testing. A rendered control or screenshot is not accessibility evidence
- **S18** [Apple review guidelines][S18]: Sections 2.5, 3.1, 4.2.3, 4.2.7, 4.7, 4.8 and 5.1 raise distinct questions about software behavior, purchase flows, remote desktop classification, plugins, login and privacy
- **S19** [Google Play Payments][S19], **S20** [Device and Network Abuse][S20], **S21** [User Data][S21]: Payments, remote/code behavior and data disclosures have separate policies. Applicable exceptions, storefronts and exact app behavior need counsel review
- **S22** [Apache License 2.0][S22]: The license contains redistribution/notice conditions, a patent grant and limits on trademark permission. It does not itself clear an app's dependencies, provider routes or store agreements
- **S23** [Apple Enterprise Program][S23] and **S24** [Managed Google Play custom apps][S24]: Organizational distribution has eligibility and administration constraints. Enterprise distribution is not an unrestricted public-store substitute
- **S25** [Apple export compliance][S25]: Encryption use can require export-compliance information in submission. The applicable classification and declarations need a product-specific review
- **S26** [Apple alternative web distribution][S26]: Availability depends on region and approval/notarization requirements. Website distribution cannot be treated as universally available iOS sideloading
- **S27** [Android alternative distribution][S27], **S28** [Android signing][S28], **S29** [Android developer verification][S29]: Distribution outside Play still has platform/install requirements. Signing and the current region/device-specific verification rollout are separate from app review
- **S30** [PWA capabilities][S30] and **S31** [WebKit web push][S31]: Browser capabilities differ by implementation and installation context. The WebKit article documents Home Screen web push support beginning with iOS/iPadOS 16.4, not present-day universal equivalence
- **S32** [Apple universal links][S32] and **S33** [Android App Links][S33]: Website/app association can route links to an app. Such routing is not user approval or Recursion command authority

## Pairing and device authentication

### Q01 Trust root and enrollment without provider credentials

**IN, M01.** Separate six identities: user/principal; Recursion authority domain and trust root; client installation/device enrollment; protected client key; authenticated session; provider account. The last is outside the mobile client's custody. The user client is not an execution node. Backend-held provider references may be redacted labels, never tokens, cookies, passwords, environment dumps or secret-bearing locators.

A candidate ceremony has these invariant steps, independent of mechanism:

1. An already-authorized operator initiates a bounded enrollment request at the intended backend. The phone does not nominate itself as administrator
2. The backend and phone authenticate the intended service domain/trust root and exchange fresh challenges plus a candidate public device-key binding through the eventual qualified mechanism
3. Both review surfaces show the same backend identity, account/domain, requested device role, expiration, enrollment transaction and a transcript-bound key/channel confirmation. Friendly device names are explicitly untrusted labels
4. The operator approves the exact enrollment binding through existing canonical admission; the transaction is consumed once with a durable receipt. Changed key, domain or role conflicts rather than inheriting consent
5. The enrollment creates an inactive/read-eligible client identity according to explicit policy. Read grants, control grants, input lease and work admission remain separate. A valid authorized enrollment is required as the positive fixture

The trust root must be provisioned or recognized through an independently trustworthy channel and have an explicit rotation/recovery process. A root presented only by the untrusted QR code cannot authenticate that same code. A generic push/deep link may open an enrollment screen but cannot approve enrollment. No real key, credential or trust bundle is provisioned in this research.

### Q02 Mechanism comparison without selecting one

**IN, M02.** The required property is a revocable, scoped, short-lived backend session bound to a qualified authenticator and current authorization. It is not a preference for a particular OAuth, certificate or passkey stack.

| Genuine candidate | Genuine rival and decision leverage | Decisive falsifier | Non-proof |
|---|---|---|---|
| External-agent OAuth with PKCE plus application key-bound session/token use | Operator-approved mutual authentication/certificate-bound session; compare lifecycle, renewal and proxy complexity | Captured session credential works from a different unbound presenter, wrong audience or expired enrollment | RFC compliance, key compromise resistance or implementation security is unmeasured |
| User-verified pairing to a per-installation protected key | Account authentication followed by a distinct device-enrollment approval; compare recovery friction and ceremony confusion | Approval of A enrolls B's key, or mere account login enrolls a controller | Human comparison is not cryptographic proximity or resistance to all social engineering |
| Non-exportable qualified device-key profile | Explicitly classified software-key profile with accepted clone risk; compare supported hardware and recoverability | Profile claims hardware protection without evidence, or silently falls back to exportable material | Protected keys can still be misused on a compromised device; neither detects every clone |
| Account passkey plus distinct device-bound session key | Device-key enrollment rooted in another independently authenticated operator session | Synced account credential is treated as unique physical-device identity | Account recovery and per-device revocation are separate; authentication success is not work authorization |

The source capsules S01–S11 motivate these choices; this table proposes Recursion-specific tests. A long-lived provider credential on the phone, unscoped bearer session, unrevokeable client or pairing-grants-work design is a rejected negative control, not a conforming rival. Long-lived renewal material, if a future profile requires it, needs separately qualified protected storage, rotation, revocation and bounded scope; it cannot quietly replace the short-lived control session.

### Q03 Scope and current admission

**IN, M03.** An additive application contract `MobileSessionBinding@candidate-1` records domain, principal reference, device-enrollment reference/generation, device-key reference, session instance, intended backend audience, allowed purposes, read/control scope references, issued/expiry observations and clock interpretation, authentication assurance, negotiated protocol/security-profile revisions, revocation revision and evidence. These are semantic requirements, not a wire encoding, executable schema or new canonical store. Raw private keys and session secrets are excluded from logs, projections, URLs and ordinary content envelopes.

A current authenticated session allows a request to reach the common gate. Every protected read checks current principal, object, privacy domain, audience, purpose and retention restrictions before metadata lookup and disclosure. Every control command additionally checks exact action/arguments, task/attempt/turn, route/config revision, relevant grant/work/pause/writer references, required input lease, resource bounds and current connected session. Session scope is an upper bound, never a self-contained authorization snapshot that bypasses current revocation. Device possession does not mint canonical writes, node enrollment, child grants, provider visibility or budget.

Connection methods are separately optional adapters. Authenticated reachability cannot be substituted for Recursion identity or grants. The integrated connection-method comparison below belongs to this boundary and selects no transport.

### Q04 Revocation and device loss

**IN, M04.** An authorized backend revocation commits the device's enrollment/session generation change and immediately fences new backend admissions, renewals and protected disclosures using that identity. It cancels pending unconsumed enrollment and notification subscriptions and invalidates input/resize ownership through the same broker contract. Trust-root/key compromise requires separate recovery and replacement enrollment rather than reviving a revoked record.

Connected conforming clients purge affected views and local session material when they observe the revocation; acknowledgments identify the device/session and cleanup coverage. A lost, offline or hostile phone remains `revocation-not-observed-by-client` and possible previously disclosed copies remain outstanding. Remote deregistration is backend state, not proof of physical deletion. Expiry is enforced by the backend's qualified clock at admission; a phone's wall clock cannot extend it.

This is device-session revocation, not a Full Stop. Already-admitted backend tasks continue under their own current grants unless separately stopped/revoked. An already-dispatched external effect can remain unresolved. Receiver fence installation, process termination, external settlement and physical erasure remain independent facts, preserving R-X and the shared reconciliation barrier.

### Q05 Threat and negative fixture model

**IN, M05.** The attacker may control a network/relay, send phishing links or QR codes, reorder/replay traffic, run another client, restore old app files, supply hostile projection content, steal an unlocked phone or compromise an ordinary client process. The canonical trust root and correctly enforced backend gate are baseline assumptions, not proved secure. Root compromise, a malicious OS and an external effect sink that ignores its contract require explicit higher-risk profiles or refusal.

| Attack | Required binding/refusal | Honest residual |
|---|---|---|
| Unknown client | No enrollment receipt or approved key binding: no private inventory/control; narrow enrollment diagnostics only | Discovery may reveal service reachability under declared public metadata policy |
| QR/code relay or phishing | Bind domain, enrollment transaction, intended principal, key and role; require independent authenticated approval; expire/consume challenge once | A deceived authorized operator can approve the attacker's exact device; proximity must not be inferred |
| Replay or concurrency | Challenge/proof uniqueness, audience/request binding and atomic consumption; durable command dedup survives new connections | Request-proof checking is not a substitute for logical-effect dedup |
| Downgrade or stripping | Authenticated negotiation covers offered/required/selected versions and assurance; unsupported required semantics fail before disclosure | Version agreement does not prove implementation conformance |
| Clone from backup | Restored enrollment without its current protected key fails proof; conflicting observed incarnations quarantine pending review | An exported key correctly replaying the complete protocol may be indistinguishable; report unsupported clone exclusion |
| Local attacker | Inert projection rendering; narrow IPC; no credential export, arbitrary command URI, provider login webview or secret clipboard | Non-exportability does not prevent authorized-process misuse or already-seen plaintext capture |
| Confused deputy | Wrong backend audience, principal, privacy domain, purpose, target or stale authority independently fails | A signed malicious statement is still merely a statement |

No mutating request, grant, lease, enrollment or protected disclosure uses replayable early-data semantics. The actual cryptographic realization and anti-phishing usability need independent qualification, not synthetic security certification.

## Remote session control

### Q06 Viewer and controller roles and the single input lease

**IN, M06.** Read-only attachment is the initial role. A viewer may inspect authorized facts and maintain local layout/drafts. A controller has separately granted typed control rights; an input holder additionally owns the one current per-target interactive input slot. These are three different facts. Multiple targets may each have a holder; there is no one global keyboard lease.

An explicit request-control operation names the target, current holder/lease revision and intended scope. The common broker validates current rights, arbitrates cooperative release, authorized takeover or expiry, atomically transfers input/resize ownership and returns fresh opaque references. Focus, attach, notification, keyboard appearance and reconnect cannot transfer it. M1B retains separate `input_lease` and `resize_lease` fields. A passive reader may resize its own viewport but not the upstream terminal.

Stop authority is separate: an authorized user must not acquire or steal terminal input to stop work. Other separately granted addressed messages use their own catalog operation, never an INPUT-lease bypass. A returning phone rechecks current lease, target/process/daemon incarnation and rights before sending anything. Offline buffered keystrokes are discarded as executable input; optionally retained text remains an unsent draft.

### Q07 Ten controls and identical command semantics

**IN, M07.** Mobile consumes R-L's versioned catalog and R-UI `recursion.ui-contract@candidate-2` projection/materialization candidate. It adds mobile presentation bindings, not operation meanings. Every gesture resolves to a named existing semantic operation or a presentation-only action. No swipe can mean a new implicit approval, resume or Stop.

| Required control | Mobile expression and same-gate obligation | Decisive parity check |
|---|---|---|
| Streaming output | Bounded accessible task/turn stream with source identity and gap markers | Same authorized cut yields same facts as CLI/TUI/GUI; no hidden reasoning invented |
| Questions | Show exact waiter ID/revision/expiry; answer/cancel via catalog | Delayed answer cannot target replacement question |
| Approvals | Review exact action, recipient, data, arguments, scope and expiry | Changed payload or recipient invalidates old approval |
| Queued messages | List/edit/remove accepted items before delivery boundary | Local draft, accepted queue and actual delivery remain distinct |
| Active steering | Explicit current attempt/turn and supported route delivery | Unsupported steer is not silently queue |
| Interruption | Persistent selected mode and scope, common admission fence | All three modes preserve exact ownership and uncertainty |
| Resume | Explicit command after current checkpoint/route/config/grants/effect checks | Opening the app or tapping notification cannot resume effects |
| Forks | Preview coherent source/context/evidence cut and allowance partition | Both versions preserved; no copied active grant/reservation |
| Compaction | Inspect/request/tune supported mechanism under one governor | Inspection is deterministic; model-backed transform needs ordinary admission |
| Commands/plugins | Exact namespace/component/version/schema plus present capability facts | Rendering an unavailable command never activates its plugin |

Command identity is `(admitted_authority_domain, command_id)`. Complete immutable content/digest includes historical actor/grant, operation meaning, target and arguments; digest is a conflict predicate, not a third key. Principal-local client IDs require a durable injective ingress map before lookup. Same key/same content returns authorized historical disposition with zero new dispatch. Changed content conflicts. Current reader authorization precedes receipt existence lookup; old accepted authority never becomes current authority.

Use R-L `TypedError` fields: code, failed precondition, target/revision, effect-attempted `no|yes|unknown`, retryability `never|same-id|after-refresh|reconcile`, evidence and bounded explanation. Mobile errors do not extend M1B's closed refusal alphabet. Seven capability states remain independent; unsupported and unknown have different labels. R-UI supplies the graph/config/materializer/schema/source-cut projection bindings; no additional authority store is introduced.

### Q08 Persistent Stop and truthful unresolved effects

**IN, M08.** Provide a continuously discoverable Stop control with selected target and mode visible, accessible through touch, keyboard, switch/voice or screen-reader actions. It must work without precision swipes, long-press timing or mouse use. A compact screen may expose an explicit mode/scope sheet, but cannot hide the current selection or let overlays/stream rendering indefinitely block access. Labels and status use text, not color alone; focus and large text must preserve the complete review/submit path.

| Mode | Common meaning | Required mobile facts |
|---|---|---|
| Aggressive | Fence selected-agent dispatch and request forceful interruption without waiting for its operation | Descendants listed separately; in-flight effects may remain unresolved |
| Full | Selected agent and owned subagents, shells, monitors and relaunchers; fence return/restart | Per-host/per-process observations; unreachable nodes and unresolved effects remain visible |
| Lazy | Close admission and wait for a named observable operation boundary | Boundary, deadline, waiting/timeout and configured escalation |

`checkpoint`, `interrupt` and `drain` remain mechanisms, not extra Stop modes. Display request saved, accepted, local fence, remote fence observation, interrupt delivery, owned-process exit/containment, effect settlement and independent verification separately. Suggested truthful summary: “Full Stop accepted; local dispatch fenced; remote node unconfirmed; one effect unresolved.” Never shorten that to “everything stopped.” If the phone is disconnected, Stop cannot be submitted; show that fact persistently and do not queue a future surprise Stop. A previously sent online Stop with lost response remains uncertain until its receipt is reconciled.

Accessibility targets draw on S15–S17. Native assistive-technology journeys on exact OS/build profiles remain U, as do error rates, reach time and comprehension. A standards checklist is not conformance.

### Q09 Bounded operation under hostile mobile conditions

**IN, M09.** Freeze finite global and per-device/view ceilings for enrollment/session count, query work, filter complexity, replay range, snapshot bytes, framing, outstanding credit, queued presentation data, reconnect attempts/backoff, cache bytes/age, notification volume and receipts retained. Per-device caps alone do not bound an N-device adversary. Canonical append precedes lossy presentation coalescing. Mandatory facts stay durable; withholding a slow client's delivery is not deleting history.

Reserve authenticated control capacity through ingress, framing, pumps, scheduler, admission, canonical writer, dispatch and receipt projection. Compare independent reserved control channels with demonstrably reserved scheduling on a shared channel; neither is chosen without saturation evidence. A mobile client cannot own a global lock, force unbounded replay or block Stop/recovery while rendering. Full disk or failed canonical storage is an explicit availability limitation, not evidence that a queue can guarantee progress under arbitrary faults.

For the no-extra-work comparison, freeze an already admitted and initialized client/backend/connection-plugin profile. Attach, resume-from-background, notification and additional views must produce zero model/inference, indexing, new operational plugin activation, node enrollment or new task/actor work attributable to that event. Explicitly requested first activation of an optional client or connection plugin is a separate bounded lifecycle/cold-start treatment; ordinary client rendering code and that measured initialization are not falsely claimed to execute zero instructions. Initial activation still grants no work authority and cannot introduce hidden inference. Authorized read synchronization has its own finite resource budget; it is not “free.” Always-on backend operation refers only to already-authorized backend lifetime. It grants neither fresh work nor an unlimited idle-inference entitlement.

## Connection method plugins for Q03 and Q09

The following integrated comparison responds to the user's optional Tailscale/SSH connection-plugin request. It is research only; all local connectivity simulations remain unexecuted. These alternatives add no mobile-only authority or offline control queue.

### Connection authority boundary

**Proposed:** add an optional, transport-neutral connection adapter boundary beneath the existing authenticated observer/control protocol. Keep direct backend access as a conforming rival. An operator-provisioned overlay or forwarding endpoint can be a connectivity input, never a substitute for current Recursion device authentication, actor authorization, scope, input lease, epoch/fence or common command admission. Do not reuse a tailnet identity, SSH account or source IP as the Recursion principal. No adapter may acquire provider credentials, forward an authentication agent, enroll an execution node, launch work, write canonical state or convert reconnect into authority.

A connection may be reachable while Recursion authorization is refused. A valid device session may exist while its transport is unreachable. Present these independently. A path change, mobile backgrounding, app termination or last-window close is detach, never Aggressive/Full/Lazy Stop. Stop remains an explicit typed command with the same modes, scope and receipts as other clients. Unreachable recipients and unresolved external effects stay unknown; tunnel shutdown is not rollback.

### Conforming options and their tradeoffs

#### Direct authenticated backend endpoint

**Proposed comparator:** the operator provisions a reachable backend endpoint, its verified server identity, ingress restrictions and the existing Recursion device-enrollment path. The app connects without a separate overlay account or SSH session. Operator tasks include selecting the allowed network exposure, managing endpoint/DNS identity where used, maintaining the backend and validating reachability from intended phone networks. No public endpoint, certificate scheme or application transport is chosen here. Where neither the host nor an approved ingress is reachable, this option is blocked; encryption alone is not NAT traversal.

**Genuine rival:** an externally managed overlay when exposing ingress is undesirable. **Decisive falsifier:** the direct candidate cannot connect from a required network under the operator's exposure policy, or passes a command whose device/session authority is invalid. **Nonproof:** direct topology does not prove lower latency, simpler setup, safe public exposure, phone background availability or cheaper operation. Backend application authentication and revocation remain required.

#### Operator provisioned Tailscale overlay

<!-- source:C01:start -->
**Source-documented:** the quickstart creates a tailnet through an identity-provider login, installs/authenticates clients on two devices and manages them in an admin console. **Proposed operator checklist:** provision the phone and host externally; restrict permitted destinations to the intended backend; provide its endpoint to Recursion; then perform separate Recursion enrollment. Existing operator infrastructure may reduce incremental work, but a new installation adds account, app and policy management. No setup-time saving has been observed. [Tailscale quickstart](https://tailscale.com/docs/how-to/quickstart)
<!-- source:C01:end -->

<!-- source:C02:start -->
**Source-documented:** Tailscale distinguishes direct UDP, DERP relay and tailnet peer-relay paths. Connections start through DERP and attempt to upgrade; NAT conditions or blocked UDP can prevent a direct path, and network changes can cause fallback. Its documentation describes direct paths as usually lower-latency and higher-throughput than relays. That comparison is vendor documentation, not a measurement against Recursion's direct endpoint. Expose observed path type and freshness, including unknown, rather than promising peer-to-peer performance. [Connection types](https://tailscale.com/docs/reference/connection-types)
<!-- source:C02:end -->

<!-- source:C03:start -->
**Source-documented:** the firewall guide describes NAT traversal with little manual intervention in many environments, but coordination/DERP access needs permitted outbound connectivity, and direct tunnels use UDP. Restrictive egress can break contact; relay availability is not universal connectivity. **Inferred:** this can reduce manual ingress configuration for some operators while moving troubleshooting to endpoint, policy, DNS and relay reachability. No firewall, router or network configuration was changed. [Firewall requirements](https://tailscale.com/docs/reference/faq/firewall-ports)
<!-- source:C03:end -->

**Genuine rival:** direct authenticated access, or the manually provisioned WireGuard comparator below. **Decisive falsifier:** a paired evaluation finds no reduction in operator effort at equivalent isolation, or a mandatory mobile VPN/egress policy prevents the overlay, or relay-path performance fails the agreed workload target. **Nonproof:** an overlay ping or admitted tailnet membership proves neither Recursion command authority nor task continuity, store eligibility, availability or savings.

#### OpenSSH forwarding

<!-- source:C04:start -->
**Source-documented:** OpenSSH supports local forwarding, reverse forwarding and jump-host forwarding; its no-command mode can carry forwarded ports without executing a remote command. **Proposed:** the operator, outside Recursion, provisions a reachable SSH endpoint, verifies host identity and configures a narrowly bound forward to the authenticated backend. A reverse-forward/bastion design adds a reachable intermediary and listener-exposure decisions; it is not automatic peer NAT traversal. Loopback arrival at the backend must not bypass Recursion authentication. [OpenSSH ssh manual](https://man.openbsd.org/ssh.1)
<!-- source:C04:end -->

<!-- source:C05:start -->
**Source-documented:** OpenSSH's server-alive controls detect an unresponsive session and can disconnect it. Forward-establishment success does not prove the ultimate backend is reachable: ExitOnForwardFailure excludes downstream forwarding failures. **Proposed:** keep credentials and the forwarding process operator-owned; do not grant shell, agent forwarding or broad proxy access for this client integration. Application reconnect and receipt reconciliation are separate from SSH liveness. A mobile implementation must establish that its chosen permitted integration survives the required lifecycle; a stock phone SSH daemon or persistent shell is not assumed. [OpenSSH configuration manual](https://man.openbsd.org/ssh_config.5)
<!-- source:C05:end -->

**Genuine rival:** an externally managed overlay or direct endpoint where no SSH administration is needed. **Decisive falsifier:** the only usable mobile path requires unsupported background execution, excessive host access, credential custody or an unbounded reconnect helper; alternatively the endpoint-forward is healthy but Recursion cannot authenticate or reconcile correctly. **Nonproof:** a working shell/forward is not an authenticated Recursion actor, an input lease, a Stop receipt or a durable task session. End-to-end latency and throughput under loss remain unmeasured.

#### Tailscale SSH is a separate SSH access option

<!-- source:C06:start -->
**Source-documented:** Tailscale SSH changes SSH authentication and authorization, takes tailnet traffic on port 22 into Tailscale's SSH server, and differs from ordinary OpenSSH carried over a tailnet. Its server is documented for Linux and the open-source macOS CLI variant; clients can originate from other Tailscale platforms. Restarting the daemon stops existing SSH sessions. SSH access policy changes can terminate sessions, but alternative access paths require separate revocation. **Proposed:** evaluate it only if operator-managed SSH access is actually needed. Recursion endpoint traffic over a tailnet need not enable SSH. **Genuine rival:** ordinary constrained SSH forwarding or direct backend protocol over the overlay. **Decisive falsifier:** required server/platform/forwarding behavior is unavailable, or the integration grants host-account privileges exceeding the connectivity purpose. **Nonproof:** this documentation does not qualify a mobile forwarding library, forwarding feature parity or Recursion authority. [Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh)
<!-- source:C06:end -->

#### Manually provisioned WireGuard as one additional rival

<!-- source:C07:start -->
**Source-documented:** WireGuard encapsulates IP over UDP with configured peer keys and allowed addresses; key distribution and pushed configuration are outside its protocol. It updates a peer's endpoint from authenticated incoming packets. **Proposed comparator:** operator-managed peer configuration avoids reliance on a selected hosted overlay control plane but requires an explicit plan for reachable endpoints, key distribution, revocation and support. It does not by itself supply a discovery/relay service. [WireGuard conceptual overview](https://www.wireguard.com/)
<!-- source:C07:end -->

<!-- source:C08:start -->
**Source-documented:** WireGuard's optional persistent keepalive maintains NAT/firewall mappings; it is off by default and increases background packets. **Genuine rival:** managed overlay discovery and relays. **Decisive falsifier:** required carrier/NAT reachability cannot be achieved within the permitted topology, or manual peer/key lifecycle burden exceeds the agreed operator target. **Nonproof:** protocol simplicity and silence while idle do not quantify phone battery, throughput or setup time for this application. [WireGuard quickstart](https://www.wireguard.com/quickstart/)
<!-- source:C08:end -->

### Revocation outages and mobile constraints

<!-- source:C09:start -->
**Source-documented:** Tailscale describes a coordination outage as allowing pre-established communication with cached policies, while new connections, key changes and policy updates are unavailable. **Required interpretation:** cached overlay permission must never keep a revoked Recursion device authorized. Backend admission independently checks its current fence and session policy; if required authority cannot be established, fail closed. Do not promise global revocation propagation to unreachable devices or infer remote termination from revocation acceptance. [Control and data planes](https://tailscale.com/docs/concepts/control-data-planes)
<!-- source:C09:end -->

<!-- source:C10:start -->
**Source-documented:** Tailscale's device-removal guide describes disconnection on removal, warns that uninstalling alone does not remove registration, and notes that rejoining can occur without administrator approval when device approval is disabled. **Proposed:** separately record network-device removal, Recursion device/session revocation, input-lease invalidation and installed recipient fences. Connectivity revocation is not the sole enforcement boundary. Do not translate the documented removal behavior into a measured worst-case revocation SLA. [Device removal](https://tailscale.com/docs/features/access-control/device-management/how-to/remove)
<!-- source:C10:end -->

<!-- source:C11:start -->
**Source-documented:** Tailscale identifies routing/address conflicts and mobile VPN coexistence limits; its guide says iOS and Android cannot run multiple active VPNs. **Proposed:** treat mandatory corporate VPN coexistence as an admission question, not a problem the adapter silently works around. An externally managed VPN may be a prerequisite of an optional connection profile, never a prerequisite for Recursion core. [Other VPNs](https://tailscale.com/docs/reference/faq/other-vpns)
<!-- source:C11:end -->

<!-- source:C12:start -->
**Source-documented:** Tailscale's iOS/macOS VPN On Demand applies connection policies by network conditions, and conflicting rules can prevent connection. Only one VPN app can have On Demand enabled at a time. **Required interpretation:** an automatic tunnel policy is not guaranteed mobile application execution, continuous backend reachability, current Recursion authentication or command delivery. Reattach and revalidate after foregrounding; show disconnected/stale state until evidence changes. [VPN On Demand](https://tailscale.com/docs/features/client/ios-vpn-on-demand)
<!-- source:C12:end -->

**Proposed operational comparison:** direct access depends on its backend/ingress and any selected DNS/identity services; forwarding adds the SSH host and any intermediary; an overlay adds its operator-managed client and control/data-path dependencies. Record actual dependencies instead of collapsing them into a connected indicator. Network-key removal, host-account removal and Recursion grant revocation are different operations. None retroactively settles work already sent. No numerical latency, throughput, battery, outage or revocation bound has been established for any candidate.

### Candidate adapter boundary

These are **proposed fields**, not a new M1 schema or an authentication choice. Reuse existing R-MOB/R-X shared records through references rather than creating a second authority system.

- Identity/configuration: adapter ID and version, explicit opt-in, compatibility range, configuration digest, non-secret operator-profile reference, allowed destination, endpoint identity expectation and credential-custody owner; no credential values or shell command templates
- Observation: connection generation, transport state/reason, observed path class (`direct`, `relay`, `forwarded`, `unknown`), observation time, bounded diagnostic evidence reference and measured values only when present
- Application binding: verified backend identity, negotiated observer/control version, Recursion device/session reference, audience/scope/expiry and current authorization/fence revision; these are validated by the backend, never minted by the connectivity adapter
- Continuity: canonical task/attempt and operation references, last acknowledged cursor and snapshot boundary, explicit replay-gap status, bounded online in-flight queries/commands and receipt-reconciliation records, never an offline autoexecution queue and common flow-control accounting
- Retry ownership: one bounded connection retry owner distinct from command/effect recovery, connection-attempt allowance, backoff and cancellation; changing network paths cannot generate new command identities or repeat ambiguous effects
- Lifecycle: detach reason, authentication revalidation required, prohibited implicit activation/dispatch, no input-lease acquisition on connect; current command admission and truthful Stop receipts remain outside transport health

**Competing boundary:** an adapter that only exposes a configured endpoint and generic connection status, with path diagnostics left entirely to operator tooling. **Decisive falsifier for richer diagnostics:** they require privileged credential access, leak topology beyond the authorized audience, create a second retry owner or add more measurable view/setup cost than their troubleshooting benefit. **Nonproof:** field completeness is neither a working adapter nor security verification.

### Licensing and distribution questions for G 32

<!-- source:C13:start -->
**Source-documented:** Tailscale distinguishes its open-source core/DERP code from its proprietary hosted coordination service and some platform GUI wrappers. **Counsel question:** for the exact intended dependency and platform, are we merely interoperating with an operator-installed service, distributing code, embedding a library, or redistributing a branded client? Those scenarios require separate license/notice, trademark, service-term and platform-entitlement review; open-source core availability cannot answer them collectively. [Open source at Tailscale](https://tailscale.com/opensource)
<!-- source:C13:end -->

<!-- source:C14:start -->
**Source-documented:** Tailscale publishes hosted-service terms dated 2026-08-25. **Counsel question:** identify the applicable account/service agreement and plan for the proposed deployment, including commercial use and support expectations; do not infer entitlement from a free development setup. This research created no account and accepted no service agreement. [Tailscale terms](https://tailscale.com/terms)
<!-- source:C14:end -->

Additional G-32 questions: does external-app interoperability versus embedding a VPN/tunnel change entitlements, disclosures or review obligations; can any connection module be updated separately; what exact source/binary notices and export/trademark obligations apply; and can each distribution path remain optional? No store eligibility or legal conclusion follows from this comparison. A selected SSH/WireGuard implementation would require its own pinned license/dependency review; protocol support is not a distribution license.

### Smallest provider free simulation handoff

**Proposed, not executed:** use the existing synthetic R-MOB admission fixture with two opaque byte-path stubs, no network stack, sockets, shell, credentials, provider, host or app process. Do not install or import a candidate transport. Run identical logical inputs with only path labels changed.

1. Begin with one synthetic writer/fence, an authenticated controller, one passive viewer, a task and a known projection cursor. The path alone has no device or work authority
2. Submit one typed command with stable operation identity; simulate backend acceptance, then drop its receipt and lose the path. Assert no duplicate effect, no completed/settled claim, no implicit Stop and no new work on disconnect
3. Reconnect through the other path/generation. Require current device authorization and version/cursor reconciliation. Query the same operation; duplicate delivery returns the same canonical receipt or remains ambiguous under the existing effect guard, never a fresh attempt
4. Revoke the device and advance the fence while the path still reports reachable. Attempt commands with cached overlay membership, SSH-account access, stale session, passive-client input and old input lease. Every attempt is refused; no writer/input-lease/node authority appears
5. Drop replay history to force GAP. Refuse invented continuity. Delay/duplicate health and data observations without blocking canonical append, independent Stop admission or recovery
6. Submit an explicit Stop through a currently authorized connection while a simulated execution recipient is unreachable. Separate accepted, delivered, fence-installed, owned-process observation and unresolved effects. Reconnection does not relaunch work

**Acceptance oracle:** identical canonical command/receipt/fence outcomes across path stubs; zero authority derived from path labels; bounded buffers/retries; no duplicate external-effect claim; unknown effects stay unknown. **Falsifier:** changing path, replaying receipt/command, or presenting connectivity identity changes authority or launches work. **Nonproof:** this handoff is not an executed fixture, a live NAT/relay/mobile-roaming test, cryptographic verification or performance evidence.

Actual comparison requires a separately authorized experiment with specified phone/OS/client builds, mobile lifecycle states, direct versus relayed paths, carrier/Wi-Fi restrictions, equivalent workloads and isolation. Measure operator steps/time/errors, connection/recovery latency, command-to-ack versus command-to-observed-effect latency, throughput, CPU/memory, bytes/wakeups and battery. Include control-plane/relay loss and revocation during partition. Agree thresholds before measurement; report failures and unknowns rather than an aggregate score. No such account, installation, network change, tunnel, live host, model/provider call or benchmark occurred here. Local work was source reading, research-artifact writing and artifact QA only.

## Offline read views and synchronization honesty

### Q10 Last synchronized boundary and honest gaps

**IN, M10.** “Connected” means a currently authenticated, qualified backend session with fresh checks; network link or tunnel status alone is insufficient. Read presentation states distinguish synchronized-at-cut, live-but-lagging, disconnected-cached, resynchronizing, GAP/reconstructed, permission-unavailable, schema-incompatible and empty. Show source cut, stream/incarnation/cursor unit, snapshot identity, backend synchronization observation and readable time with clock uncertainty. Do not label a historical task “running now” from its last known event.

Use M1B's unchanged HELLO/WELCOME/SNAPSHOT/EVENT/ACK/CREDIT/INPUT/RESIZE/RESET vocabulary. `GAP` is a marker/reason, not a tenth message. After a detected replay gap, RESET is the only permitted next same-stream continuation; `replay-gap-continuation`, `credit-exhausted`, `stale-lease` and `passive-client-input` keep their literal meanings. Snapshot bytes plus cursor must be validated and installed coherently before the UI claims reconstruction. WELCOME or accepted RESET alone does not prove the snapshot exists. Locally deferred rendering must not manufacture a retention gap.

### Q11 Exact cache identity and the revocation boundary

**IN, M11.** Proposed `MobileReadCacheBinding@candidate-1` is an additive scoped projection binding. Its cache identity is the complete tuple:

`(authority_domain, principal_ref, device_enrollment_ref_and_generation, privacy_domain_id, project_and_audience, purpose_and_retention_policy_ref, projection_schema_revision, projection_query_and_filter_digest, UiMaterializationManifest_ref, resolved_capability_graph_digest, configuration_revision, configuration_epoch, route_epoch, route_descriptor_epoch, context_epoch_or_not_applicable, current_read_grant_refs_and_revocation_generations, applicable_writer_work_pause_refs, source_writer_domain_and_fence, stream_id_and_incarnation_and_cursor_unit, contiguous_source_cut, receipt_cut, snapshot_ref, content_and_loss_refs)`.

Every element has a declared issuer/type; `unknown` and `not_applicable` are explicit and never zero. A generic `epoch`, maximum epoch or cache timestamp cannot replace these domains. A security-significant unknown prevents protected reuse. The tuple names identity and provenance; it is not a bearer capability and a cache hit never establishes current authorization, freshness or equal bytes across privacy domains.

Validate the principal/domain before lookup, then current scope before new backend disclosure. On known logout, scope change, revocation, audience change, identity switch or incompatible security/schema revision, purge/quarantine corresponding materializations, indexes, thumbnails, drafts and restoration state; do not rekey old bytes into the new audience. Restrictive updates take effect at the backend gate independently of ordinary preference propagation. Receipt history is disclosed only to currently authorized readers.

**The literal conflict:** the brief asks for a cache that never serves across revocation while also allowing disconnected cached views. Instantaneous unseen remote revocation cannot satisfy that absolute wording. No design here claims otherwise. Two conforming policies require an explicit interpretation/Owner decision:

| Policy candidate | Allowed offline display | Residual and decisive falsifier |
|---|---|---|
| Online-only private view; minimal authorized status proposal | Only the exact metadata approved for offline retention; optionally no task metadata at all. Private views close on loss of qualified freshness | Previously seen pixels/copies remain unretractable. Fails if private content is loaded/reopened offline or metadata exceeds its disclosure policy |
| Explicit bounded offline snapshot | Previously authorized snapshot, local unlock and finite retention/freshness policy, conspicuous historical cut; no control | Unseen revocation cannot be learned during the window. Fails if advertised as immediate revocation, shown past a trusted bound, or reused across principal/audience |

Neither is adopted here. Even online-only is a prospective access rule for a conforming client, not a promise to erase prior disclosure. If the requirement means that an adversarial offline device can never read already-received bytes after revocation, the requirement is unsatisfiable; no cache mechanism should be approved under that claim.

### Q12 Local protection and backup restoration

**IN, M12.** Separate a protected authentication-key/session store from the content cache. “No secrets in cache” means provider credentials, private keys, session/renewal tokens, recovery codes and credential-bearing links never enter content, logs, notification payloads, crash telemetry, thumbnails or ordinary backups. A device's protected backend-authentication key is itself sensitive key material, but it is not a provider credential; using it does not contradict the narrower no-provider-custody rule.

For an approved private cache profile, require OS protected file storage, least-privilege process access, a profile-specific encryption/key-lifetime design and explicit backup/device-transfer exclusions. Encrypted cache and its decrypting keys must not be restored together into a newly trusted client without current enrollment/read revalidation. Avoid raw private content beyond the named retention policy; encrypted content remains sensitive disclosed data. Lock-screen previews, screenshots/app-switcher snapshots, clipboard, share sheets, search indexes and accessibility output all need their own exposure policy and tests.

S07–S09 establish why a generic “encrypted by OS” claim is insufficient. On logout or observed revocation, invalidate sessions/keys as applicable and purge authorized local data; record best-effort cleanup coverage. Backend lost-device revocation fences future use but cannot guarantee physical wipe. Restore/reinstall creates an untrusted local state until authenticated and re-enrolled; no restored database may resurrect grants, active input leases, outbound commands or private cache permission.

Expiry also requires a qualified clock profile. Backend validity uses backend current authority and time. For offline display, wall-clock rollback, suspend, reboot, backup rollback or uncertain elapsed-time provenance must close protected display or force online revalidation; a monotonic timer across an unqualified reboot is not a trusted expiry proof. No secure timer implementation is selected or certified. An attacker controlling the OS or retained plaintext remains outside any claim of enforceable local expiry.

### Q13 Reconnect and receipt reconciliation

**IN, M13.** Reconnect authenticates the intended current backend, rechecks device enrollment/session/protocol/read scope, reconciles the old coherent source cut, resolves current authority and fetches only authorized receipt/projection deltas. It restores the same task identity and local presentation state, not the old control lease. It does not create new work epochs, actors, effects or model sessions merely to match a cached screen.

The visible receipt projection preserves R-L/shared names and their actual observers:

| Fact | Evidence boundary | Must not imply |
|---|---|---|
| `saved_locally` | Exact local draft/outbox persistence and qualified local profile | Accepted queue position, authority or submission |
| `accepted_or_refused` | Canonical disposition and separately evidenced durability | Dispatch, remote receipt or effect |
| `delivered_applied` | Exact recipient/incarnation and acknowledgment's declared coverage | Model adoption, full effect, independent verification |
| `outcome_observed` | Named operation/attempt and attributable observer/cut | Completeness beyond that observer |
| `effect_settlement` | Original liability/effect and valid canonical reconciliation | Task acceptance, unrelated settlement or rollback |
| `verification` | Named gate, exact candidate and independent review | Universal safety or platform qualification |

Transport receipt, local start and partial byte acknowledgments remain additional subject-specific facts from shared contracts. This is a fact vector with partial ordering, not a mobile stage enum. Reordered delayed acknowledgments cannot force facts into a fabricated chronology.

Unsent text stays a local draft; explicit foreground submission after current validation is a new command. A possibly submitted online command is looked up under its original canonical identity. Same-ID historical receipt recovery never dispatches again. If receipt/dedup history is unavailable, hold `receipt-history-unavailable`, retain original unresolved liabilities and delegate reconciliation to the one existing retry owner. A fresh ID is not a workaround. Reconnection alone is never a retry authorization or budget renewal.

## Push and notifications

### Q14 Minimal notification contract

**IN, M14.** Proposed `NotificationHint@candidate-1` permits only a bounded, expiring, audience/device-scoped, non-authorizing hint identifier, collapse/dedup class and schema version, plus an optional generic text/category specifically allowed by the notification disclosure policy. Avoid canonical task IDs, titles, source paths, participant names, prompt/output text, diffs, budgets, grant references, digests/equality fingerprints, session credentials and provider secrets. Even a category such as “approval needed” can reveal activity and must be explicitly classified.

The provider delivery address/token is held only in a separate minimal subscription record with device/principal binding, current opt-in, revocation generation and expiry; it is not a work grant. No token is copied into the content envelope. Payload validation rejects unrecognized action-bearing or privileged fields. End-to-end encryption, if a later design adds it, would not itself hide timing, device routing or ciphertext size and would not make notifications authoritative.

### Q15 Tap and deep link do not admit work

**IN, M15.** A push arrives: validate bounded syntax, dedup/expiry and local display policy; optionally display the generic hint. A tap opens an inert app route or authenticated sign-in shell. It then performs a current-authorized read against the backend if connected. It never executes embedded commands, accepts approvals, acquires input, starts research, activates a capability/plugin/node, resumes work, launches inference or spends. Subsequent user intent must use the ordinary typed command path and existing confirmation/admission policy.

A deep link identifies at most a scoped navigation locator. Validate scheme, exact allowed destination/route and decoded parameters; reject redirects, script/command URIs, traversal, ambiguous encoding and secret-bearing parameters. Association mechanisms in S32–S33 help route a link but grant no authority. Linking to a nonexistent/unauthorized task must not leak its existence. Link/notification replay can reopen a view, never replay an action. Push accepted, delivered, displayed, tapped, read refreshed and command admitted are separate observations; no delivery success implies an effect.

### Q16 Bounded subscriptions and delivery

**IN, M16.** Notification delivery is optional and off until consent/configuration. Freeze per-device and global rate limits, burst cap, dedup window, maximum pending hints, expiry, fan-out count, backoff and quiet-hour policy. Preferences bind current principal/device, time-zone interpretation and revision. Invalid/stale device delivery addresses are removed from future sends. Revocation closes new sends immediately at the sender; already-submitted notifications may still arrive, so their content must already meet the safe payload policy and clients recheck current rights before resolution.

Compare event-driven minimal hints plus explicit foreground refresh against no push with foreground-only reads. Neither supports a correctness dependency on notification delivery. Multi-device hints share notification-event identity for dedup but do not share session tokens or input ownership. One device's tap does not mark all other devices as having observed a command receipt. Quiet hours and dedup are presentation policy, not admission or task-stop semantics. Expired backlogs collapse to a bounded refresh hint rather than flooding on reconnect.

### Q17 Privacy beyond payload text

**IN, M17.** Audit observers separately: delivery provider, network observer, device OS/lock screen, another app, shared-device user and backend operator. Record whether each can see sender/app identity, routing token, IP/network, send time, cadence, size, collapse keys, device count, subscription associations, delivery/failure logs, locale and notification category. Unlinkable-looking IDs do not establish noninterference.

A synthetic observer comparison holds public inputs constant while varying one private task event; distinguishability of visible payload/category/size/timing is a falsifier for any claimed no-leakage policy. Candidates include no push for sensitive domains, fixed generic categories, coarse batching and padded bounded messages. Genuine alternatives trade responsiveness, data/wakeup costs and residual traffic leakage; none is selected as anonymous communication. A stable app-level subscription still reveals participation. Any claim of reduced human effort or improved productivity requires a separate measured task study.

## Detach continuity and client lifetime

### Q18 Closing backgrounding and lost sockets

**IN, M18.** Closing the last view, backgrounding, OS app termination, network loss and failed push cause client detach/freshness loss only. They must not synthesize `checkpoint`, `interrupt`, `drain`, any Stop or a new work command. The daemon/broker retains actor/task/process ownership and admitted execution policy. Release or eventual expiry of a phone's input lease is distinct from termination of work.

A synthetic trace captures task/actor/process/logical-operation identities and launch counters, detaches all clients, lets an already-admitted bounded synthetic task progress, and reattaches after events or a genuine retention gap. Pass requires the same task history and zero attach-attributable model/index/actor/effect starts. If work finished while absent, show its actual result. If the execution host failed, show current unknown/recovery facts; do not silently relaunch from the phone. This is a test specification, not a claim the invariant has been proved in Recursion.

Always-on Linux changes backend availability expectations only. Host power, sleep, network, service health, authority validity and the phone's connectivity are independent observations. No service configuration or deployment is authorized by this report.

### Q19 Coexistence without a second executive

**IN, M19.** CLI/TUI/GUI/mobile clients share the same canonical task IDs, commands, grants, operation retry ownership and receipts. Each view has its own authorized projection/cursor and local layout. R-UI's materialization manifest pins the effective graph/configuration, schema/client profile, source/receipt cut, locale/accessibility interpretation and loss/omissions. Same-cut parity is tested; differing cuts are labeled rather than mistaken for contradictions.

No mobile leader election, app-owned scheduler, notification worker or background refresh becomes Head, ARM, writer or work coordinator. D-020's optional backend failover uses the kernel's writer-fencing seam; a newly authenticated phone cannot select a writer. On authority-coordinator failover, reject old session/fence assumptions until the common backend contract establishes current bindings. Concurrent controls use exact expected revisions and one admission outcome; losing clients receive typed conflicts, not last-tap-wins authority.

### Q20 Lifecycle resource vector and freeze rules

**IN, M20.** All measured cells are presently **unknown-until-measured**. PERF-010 applies to mobile view cost without substituting phone responsiveness for backend control progress. OR-024's nontradeable correctness/authorization/privacy/effect/quality/recoverability floors precede responsiveness, subscription efficiency and completion. No scalar score can hide a regression.

| Phase or dimension | Observation to freeze and report | Current result |
|---|---|---|
| Cold start | Launch to safe shell, authenticated connection, first correct authorized projection; installation/cache state and network separate | unknown-until-measured |
| Resume/background | Wake to explicit stale state, validation completion, first correct frame; stale-control exposure window | unknown-until-measured |
| First use | Enrollment completion/errors, canceled/failed ceremony, user active time, accessibility completion, support steps | unknown-until-measured |
| Steady state | Offered input, admission, append, acknowledgment and render p50/p95/p99; generator lateness/refusals retained | unknown-until-measured |
| Recovery | Reconnect/re-auth/snapshot/GAP/receipt reconciliation time and bytes; task continuity, unresolved effects | unknown-until-measured |
| Battery/wakeups | Energy with method/uncertainty, wakeups, background duration, radio activity, thermal state | unknown-until-measured |
| Memory/handles | Peak and steady private/resident memory, process/handle/socket counts, cache and allocation growth | unknown-until-measured |
| Network/storage | Up/down payload and framing bytes, reconnect/push/snapshot overhead, writes and retained bytes | unknown-until-measured |
| Backend cost | CPU/memory/I/O, append/control latency, global queue bounds, view fan-out and disabled-path work | unknown-until-measured |
| Human/quality | Time to understand current state, wrong-scope/duplicate controls, review/correction burden and task success | unknown-until-measured |
| Maintenance/portability | Dependencies, privileged code, install size, update work, device/OS/accessibility coverage | unknown-until-measured |

Before outcomes, freeze client/backend builds, OS/hardware, key/storage profile, connection method, radio/network impairment, thermal/power state, task/evaluator corpus, route/config/graph revisions, source cuts, offered load, instrumentation overhead, N-device/N-view topology, limits, trial duration, stopping rules and practical margins. Randomize matched order; preserve failed/censored trials. Report client and backend separately, with no summation of shared memory and no missing meter converted to zero.

Compare headless backend, connected foreground clients, detached clients, optional push, cold/warm caches and installed-disabled plugins at fixed total budgets. A local synthetic harness can establish only its modeled queue/counter behavior; actual phone battery, push delivery, secure storage, network latency and accessibility require separately authorized physical-profile tests. A larger N cannot substitute for representative faults. Numeric limits are experimental preregistration fields, not invented product minima.

## Distribution and counsel under G32

### Q21 Questions for counsel

**IN, M21.** This is a counsel-input checklist, not legal advice, release clearance, store eligibility or a determination that any policy applies. D-026's Apache-2.0 direction remains subject to D-027/G-32. Lucas engages counsel; no contact, acceptance of terms or spend occurs here. Freeze territory, distributor entity, monetization, backend ownership, exact capabilities, data flows, dependencies and intended audience before asking for a determination.

| Topic | Exact question and evidence counsel needs |
|---|---|
| iOS classification and review | Which remote-desktop, plugin/chatbot, LAN/host, external-app dependency (4.2.3), account, privacy and review-access rules apply? Supply exact screens and control/data flows; do not infer an exemption from the app's name [S18] |
| Android remote and plugin behavior | Do typed remote execution, optional plugins or updates implicate Device and Network Abuse rules, and what proof of authorized use is needed? Supply manifests and executable-versus-inert content boundaries [S20] |
| BYOK and subscriptions | For free BYOK/provider-subscription access, paid Recursion features, hosting and upgrades, which billing, purchase-link or entitlement rules apply in each region/storefront? Does BYOK change the answer? [S18][S19] |
| Data and accounts | Which consent, deletion, SDK and data disclosures cover keys, routing, notifications, caches and accounts? Does accountless operation change the answer? [S18][S21] |
| Apache-2.0 and dependencies | Are LICENSE/NOTICE, modified-file attribution, dependency licenses, patent terms, contribution provenance and any CLA complete? Can the selected store terms, EULA, binary protections and redistribution model coexist with every shipped component's obligations? [S22] |
| Signing and notarization | Who controls release/upload keys, rotation, revocation and recovery? Which signing, provisioning, review/notarization and update obligations apply to each iOS/Android channel? Are cross-store update identities compatible with the intended ownership model? [S26][S28] |
| Encryption/export | What classifications, declarations, exemptions, filings or regional restrictions apply to the actual cryptography and distribution entities? Do OS-provided crypto and an optional tunnel change the answer? Do not assume “uses standard TLS” settles it [S25] |
| Branding and third-party accounts | May Recursion use each provider/store name, logo or compatibility claim? Does an upstream route's license grant the proposed automation and subscription use? Keep app distribution, third-party entitlement and trademark questions separate [S22] |
| Enterprise/MDM | Is the audience eligible for the proposed employee/private-custom channel? What MDM contracts, managed/unmanaged separation, privacy notices, key custody and offboarding obligations apply? Is it permissible for external community users? [S23][S24] |
| Developer/self distribution/PWA | What geography/device/profile restrictions, verification and account conditions apply to testing, sideloading, web distribution and browser delivery? Which obligations survive outside a public store? [S26][S27][S29][S30] |

Counsel dispositions must be signed off against exact dated policies and architecture, with conditions, territories and re-review triggers. A checked row means the question/evidence is ready, not that the route legally passes. Store rejection, a new policy, dependency change, monetization change or new disclosure triggers re-review.

### Q22 Genuine distribution alternatives

**IN, M22.** Backend semantics, identity, receipts, grants and continuity remain channel-neutral. Store availability, mobile installation, push registration or a vendor account cannot be a backend boot/recovery prerequisite.

| Option | Documented constraint to investigate | Rival and decisive falsifier | What it does not prove |
|---|---|---|---|
| Public native stores | Product behavior and commercial/data policies need exact review [S18][S19][S20][S21] | Private organizational distribution; fail if mandatory approved functionality cannot be represented or counsel finds incompatible terms | Approval of one version is not future eligibility or route entitlement |
| Enterprise/MDM/private custom app | Audience, program and administration eligibility [S23][S24] | Public distribution; fail if intended community audience is ineligible or management boundaries leak data | MDM enrollment is not Recursion grant, wipe proof or broad public distribution permission |
| Developer/test/self-hosted/sideloaded binary | Per-platform region/account/install, signing and verification requirements [S26][S27][S28][S29] | Browser client; fail if target audience cannot lawfully/reliably install or maintain updates within the accepted support budget | Easier testing is not production reach, security or lower maintenance cost |
| Progressive web client | Browser/installation capability matrix and background/key/storage limits [S30][S31] | Native client; fail if required connected controls, safe authentication, offline policy or assistive-tech journeys cannot satisfy the profile | Web availability is not native-equivalent latency, key protection, notifications or store-law exemption |

No winner is selected. A thin native shell and a browser client can both implement one protocol without sharing identical key assurance or offline guarantees. Unsupported profiles refuse/explain the affected capability rather than degrading authorization. D-033's low-porting-cost hypothesis needs measured migration/maintenance work against a native rewrite; source availability alone proves nothing.

## Q23 Provider free acceptance fixture handoff

**IN, M23.** This is a bounded specification for a future separately authorized local harness, not implemented software and not an executed test report. Use only synthetic principals, public fixture text, inert key identifiers and an in-memory model. Model cryptographic decisions as explicit supplied outcomes; never label such a model a cryptographic test. No network, live host, device, account, store, push service, model/provider, credential store, target import or repository test is required.

Each vector includes a useful authorized positive control, a targeted invalid variant, exact expected facts, independently observed mutation/disclosure counters and a deliberately broken gate that the observer must detect. A parser rejection before the intended gate is not a successful security test. A deny-all system fails its positive control.

| Fixture | Exact pass predicate and rejecting observation |
|---|---|
| MOB-F01 Enrollment | Approved exact domain/key/principal/role/challenge consumes once and creates one client identity; unknown/changed/replayed binding creates none. Any provider-secret field or work grant from pairing fails |
| MOB-F02 Clone boundary | Backup copy lacking qualified key proof is denied; observed conflicting incarnations quarantine. Exported-key-equivalent case is reported indistinguishable/unsupported, never falsely “detected.” Claiming universal clone rejection fails |
| MOB-F03 Phishing/relay/downgrade | Wrong domain, transcript key, role, expired challenge or removed mandatory security capability yields zero enrollment/disclosure/control; valid bound ceremony succeeds |
| MOB-F04 Scope and connected-only | Viewer, wrong audience/purpose, revoked/expired device or disconnected client produces zero new effect; current authorized connected operation succeeds exactly once |
| MOB-F05 Lease race | Two clients request one target; exactly one current input/resize holder. Focus, attach, sleep return and passive resize produce zero unauthorized input; authorized Stop succeeds independently of holder |
| MOB-F06 Ten-control parity | Same-cut CLI/TUI/GUI/mobile intents produce equivalent canonical semantic arguments/dispositions for all ten controls; altered target, stale waiter, unsupported steer and collision are refused without alternate meaning |
| MOB-F07 Stop uncertainty | Aggressive/Full/Lazy preserve exact mode/scope. With unreachable node and accepted external effect, local fence may be true while remote Stop/settlement remains unknown; no global stopped/rollback badge |
| MOB-F08 Lost online acknowledgment | Original accepted ID reconciles to historical receipt, zero new dispatch. Changed immutable body conflicts. Missing history holds unresolved liability; reconnect never emits a fresh effect ID |
| MOB-F09 Offline honesty | Disconnected screen shows exact last synchronized cut and unknown-current state, with every remote action disabled/refused; no background submission on reconnect |
| MOB-F10 Cache cross-scope | Change principal/device/audience/privacy domain/purpose/schema/grant independently; old private bytes and existence metadata never cross into the new scope. Authorized same-scope read remains useful |
| MOB-F11 Offline revocation impossibility | Backend revokes while client isolated: backend new reads/actions=0; client reports last-known state and policy residual. Online-only private view is closed; bounded snapshot remains explicitly historical only under approved bound. Fake instant erasure or unseen-revocation knowledge fails |
| MOB-F12 Expiry and restore | Wall-clock rollback, reboot/elapsed-time uncertainty or restored enrollment/cache forces protected-view hold/revalidation; no grant/token/lease resurrection. Current online renewal under explicit policy succeeds |
| MOB-F13 Storage and backup | Synthetic backup/transfer manifest excludes key/session/provider material and disallowed private derivatives; restore cannot decrypt/reuse without qualified current enrollment. Log/thumbnail/index/clipboard leakage fails |
| MOB-F14 GAP | Genuine requested cursor below replay floor demands RESET next; ACK/CREDIT/INPUT/SNAPSHOT before RESET fails. Snapshot/cursor installation is atomic; missing snapshot never displays invented history |
| MOB-F15 Notification no authority | Duplicate/forged/expired/action-bearing hint or tap/deep link causes zero commands, effects, activations, model/index calls and budget reservations. Valid tap can retrieve one authorized bounded projection only |
| MOB-F16 Notification limits/privacy | Per-device/global cap, dedup, quiet-hour and revocation predicates hold; unauthorized sensitive categories/identifiers absent. Any claimed traffic noninterference fails when private-event variants remain distinguishable under its stated observer |
| MOB-F17 Detach and reattach | Last-window-close, background, killed app, failed push and socket loss generate no Stop/launch; actor/task/logical-operation identity unchanged; reattach reconstructs actual bounded synthetic progress |
| MOB-F18 N-device N-view soak | Retain the baseline PERF-010 view axis V={0,1,5,10,20}; add device N={0,1,4,16} and supplemental V={4,32} stress cells. Freeze finite selected topology cells, 10,000 synthetic events and 1,000 control opportunities, caps and scheduler bounds before run. Queues never exceed caps; every admitted control within bound; append/recovery unblocked; zero attach-triggered model/index/plugin/actor starts |
| MOB-F19 Saturation and fairness | Slow reader, zero credit, partial frame, reconnect storm and full modeled storage cannot steal reserved capacity; valid control progresses within qualified model bounds, or explicit persistence-unavailable refusal occurs. Dropped canonical fact or fabricated receipt fails |
| MOB-F20 Source/contract integrity | Four ArtifactRef and eighteen ContentEnvelope base fields unchanged; unknown mandatory revision refuses; authority_carried_none true for imported/model content; content/loss aliases agree; distinct epoch domains retained |
| MOB-F21 Disclosure ordering | Expected-copy ExposureIntent and resource/lineage binding committed before private metadata/chunk release; current checks at release and task publication; race preserves possible copies/unknowns, never publishes revoked content |
| MOB-F22 Resource conservation | Same pool/unit/window obeys S+O+H+P≤L for disjoint withheld headroom; each liability counted once; retries/reconnect/fork do not renew limits; unknown actual use never zero |
| MOB-F23 Accessible model journeys | Semantic model exposes mode, target, stale state, exact action and all ten controls without gesture-only path; deliberately missing labels/focus fail. Native device accessibility result remains unknown |
| MOB-F24 Counsel readiness | Every Q21 item has exact architecture evidence, dated official source, owner/question and unresolved disposition. Any “cleared,” “eligible” or “legal pass” without counsel evidence fails |

The soak numbers are finite proposed fixture parameters, not product targets or statistical power. Threshold variables for timing, memory, energy and native reliability remain unset until an approved preregistration; an unset threshold makes that performance predicate **not evaluable**, not passed. Record source/build/profile digests, actual offered schedule, full adverse/positive traces, observation coverage and mutation sensitivity. End a run on completed finite vectors or a safety/resource bound; retain censored data and explain the stop. The local harness can reject contradictory contracts; it cannot qualify phone hardware, network crypto, store policy, battery life or external effects.

## Recommendation register with genuine rivals

All recommendations are IN. They add tests and candidate bindings while preserving accepted invariants; none selects a stack or waives a requirement. Unsafe controls in Q05/Q23 are not counted as viable rivals.

| Recommendation | Conforming rival | Decisive falsifier | What passing does not establish |
|---|---|---|---|
| M01–M05 Transaction-bound user-verified device enrollment with revocable protected sessions | Account-authenticated separate enrollment using another qualified key-binding mechanism | Wrong-device enrollment, replayed use, provider custody, work authority from identity | Cryptographic security, anti-phishing human success or universal clone prevention |
| M06 Explicit broker-mediated control transfer | Exclusive controller session grant with explicit handoff mapped to the same lease semantics | Concurrent current holders, focus stealing, Stop waiting for input lease | Actual backend liveness under arbitrary faults |
| M07 Shared catalog-generated mobile forms | Independently implemented codecs validated by common semantic corpus | Same intent yields different admission/refusal/target | Generator correctness, full route parity or UI quality |
| M08 Persistent accessible compact Stop control | Dedicated always-reachable control view with equivalent mode/scope visibility and navigation bounds | Required journey hides mode/scope, needs timing gesture, or lies about unresolved effects | Native accessibility conformance or measured response time |
| M09 Reserved control channel | Reserved end-to-end logical scheduling on shared transport | Bulk or hostile reader blocks canonical append/Stop/recovery | Progress under unavailable canonical storage or arbitrary network partitions |
| M10–M12 Online-only private content with policy-scoped minimal offline status proposal | Explicit bounded offline snapshot under approved disclosure/clock/retention policy | Post-disconnect display exceeds chosen policy or claims unseen revocation knowledge | Retroactive erasure or confidentiality against compromised OS |
| M13 Receipt-first recovery and immutable IDs | Server-owned queryable command journal with client retaining only safe correlation handle | New dispatch from reconnect, fresh ID bypass or settlement from missing ACK | Exactly-once at arbitrary external sinks |
| M14–M17 Optional generic push hints with bounded refresh | Foreground-only reads and no push for sensitive domains | Tap admits work, payload leaks prohibited metadata, or delivery becomes correctness dependency | Anonymity, reliable delivery or less human effort |
| M18–M19 Thin disposable views over common backend | Multiple independently built clients over identical contracts and parity corpus | Client close stops actor or attachment starts a second executive/writer | Process containment or availability-plugin correctness |
| M20 Phase-separated resource vector at fixed total budget | Matched sequential workflow trials plus component traces | Hidden scalar improvement, censored failures or unknown charged as zero | Performance superiority, savings or cheap porting |
| M21–M22 Channel-neutral backend and independently gated client distributions | Narrower qualified initial client profiles without removing accepted capabilities | Backend depends on store/push availability or channel changes authority | Release eligibility, entitlement or legal clearance |
| M23 Independent literal model oracle with positive/adverse/mutant controls | Two independently implemented local semantic models with shared vectors | Deny-all passes, blind observer misses mutant, or unrun vector marked pass | Production security, implementation acceptance or exhaustive proof |

## Shared contract integration and explicit non proofs

Use the unchanged `ArtifactRef=(object_type,id,version,content_digest)` and all eighteen `ContentEnvelope` fields by reference. New mobile/session/cache/hint information is a versioned additive application binding, never a nineteenth base field. Preserve `project_and_audience`, `privacy_domain_id`, `retention_rights`, full influence/provenance and `authority_carried_none=true`; do not substitute `project_id`. Loss facets refer to one immutable shared record. Outward handles are audience/purpose-scoped locators with current authorization before existence lookup, not serialized internal digest identities or bearer permissions.

Private projection delivery is an actual disclosure. Shared `ExposureIntent` registration precedes private metadata/chunks; current rights/fences are checked at release and again before protected publication. A receipt of cached bytes cannot make current rights true. Potential copies survive uncertain transfer and revocation as explicit obligations. Resource accounting retains one original reservation/operation lineage, the declared disjoint or tagged representation and independent cumulative-versus-instantaneous dimensions. Mobile reconnect is not an accounting reset.

R-UI owns contribution/projection materialization and its loss/disabled-capability behavior. R-PC owns deterministic composition and its manifest; mobile may inspect only authorized projections. It does not load skills, compile new model prompts or activate tools merely to draw a settings panel. Restrictive authority changes fence current backend use regardless of preference application phase. Writer, work, pause, route, descriptor, configuration content/application, context, device enrollment, session, input lease, process and stream identities stay distinct.

**Not established:** a built mobile app; qualified pairing/authentication/transport; cryptographic security; hardware uniqueness; anti-phishing usability; accessibility conformance; actual Stop/containment on phones or nodes; instantaneous offline revocation; remote erasure; global exactly-once effects; production backup safety; privacy noninterference; measured latency, battery, resource, productivity, savings or porting cost; store eligibility; provider/subscription entitlement; Apache/dependency clearance; export classification; legal conclusion; Owner adoption. Missing evidence remains unknown. No language, package manager, mobile toolkit, framework, store, runtime, transport, push provider, authentication mechanism, encoding or vendor is selected.

## Completion gate audit

This is coverage/self-check, not independent acceptance. The functional proofs requested by the brief remain unexecuted obligations; the offline absolute claim is expressly unresolved rather than marked proved.

| Gate | Report coverage | Disposition |
|---|---|---|
| G01 Pairing identity/trust/session/revocation/phishing without provider custody | Q01–Q05, F01–F04 | Candidate specified; security unverified |
| G02 Viewer/controller/lease/commands/errors/Stop/boundedness | Q06–Q09, F05–F08/F19 | Candidate specified; runtime unverified |
| G03 Honest offline/cache key/invalidation/protection/GAP | Q10–Q13, F09–F14 | Two policies explicit; instant unseen revocation cannot be guaranteed |
| G04 Minimal no-authority push and privacy | Q14–Q17, F15–F16 | Candidate specified; delivery/privacy unverified |
| G05 Detach lifetime and same-task reattach | Q18–Q19, F17 | Exact proof obligation specified; not executed |
| G06 Lifecycle budgets and freeze tied to PERF-010/OR-024 | Q20, F18–F19/F22 | All measured cells unknown; no scalar score |
| G07 Counsel questions and distribution rivals | Q21–Q22, F24 | Counsel input only; G-32 open |
| G08 Provider-free suite with exact pass/fail predicates | Q23, F01–F24 | Designed/unexecuted; no provider/store needed |
| G09 Every recommendation has rival/falsifier/non-proof; no selection | Mechanism/distribution/recommendation registers | Covered as candidate comparisons |
| G10 Explicit non-proofs | Evidence boundary and non-proofs section | Covered |
| G11 Protected paths untouched and artifact hygiene | Read-only source export; artifact-only checks receipt | Verified only to the recorded static-check scope |

Question coverage is one-to-one: Q01–Q05 pairing; Q06–Q09 control; Q10–Q13 offline; Q14–Q17 push; Q18–Q20 lifetime/resources; Q21–Q22 counsel/distribution; Q23 fixtures. No question is closed by a source's existence or a document structure pass.

## Source links

[R01]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/CONTROL_PLANE.md
[R02]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/ANCHOR.md
[R03]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/AGENTS.md
[R04]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/state/DECISIONS.md
[R05]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/prompts/dot-research-20261002d/R-MOB-mobile-and-remote-control-clients.md
[R06]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/PRODUCT.md
[R07]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/EXECUTION-FABRIC.md
[R08]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/INTERFACE-STRATEGY.md
[R09]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/TERMINAL-RUNTIME.md
[R10]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/M1B-WIRE-PROFILE.md
[R11]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/PERFORMANCE-PLAN.md
[R12]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rl/report.md
[R13]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rn/report.md
[R14]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rk/report.md
[R15]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/overnight-20261002/rx/report.md
[R16]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Prompt_Plugin_Skill_Architecture.md
[R17]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/shared-contracts-20261002/Recursion_Shared_Contract_Reconciliation.md
[R18]: https://github.com/NotSkittlz/recursion/blob/b696f6ece243b48c94fc0bbc7ee1d4b284c46f97/docs/v3/research-lane/GAPS.md
[S01]: https://www.rfc-editor.org/rfc/rfc8252
[S02]: https://www.rfc-editor.org/rfc/rfc9700
[S03]: https://www.rfc-editor.org/rfc/rfc9449
[S04]: https://www.rfc-editor.org/rfc/rfc8705
[S05]: https://www.rfc-editor.org/rfc/rfc8628
[S06]: https://www.w3.org/TR/webauthn-3/
[S07]: https://support.apple.com/guide/security/keychain-data-protection-secb0694df1a/web
[S08]: https://developer.android.com/privacy-and-security/keystore
[S09]: https://developer.android.com/identity/data/autobackup
[S10]: https://developer.apple.com/documentation/authenticationservices/supporting-passkeys
[S11]: https://developer.android.com/identity/credential-manager
[S12]: https://developer.apple.com/documentation/usernotifications/pushing-background-updates-to-your-app
[S13]: https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/CreatingtheNotificationPayload.html
[S14]: https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type
[S15]: https://www.w3.org/TR/WCAG22/
[S16]: https://developer.apple.com/design/human-interface-guidelines/accessibility
[S17]: https://developer.android.com/guide/topics/ui/accessibility/principles
[S18]: https://developer.apple.com/app-store/review/guidelines/
[S19]: https://support.google.com/googleplay/android-developer/answer/9858738
[S20]: https://support.google.com/googleplay/android-developer/answer/16559646?hl=en
[S21]: https://support.google.com/googleplay/android-developer/answer/10144311
[S22]: https://www.apache.org/licenses/LICENSE-2.0
[S23]: https://developer.apple.com/programs/enterprise/
[S24]: https://developers.google.com/android/work/play/custom-app-api/get-started
[S25]: https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance/
[S26]: https://developer.apple.com/documentation/marketplacekit/distributing-your-app-from-your-website
[S27]: https://developer.android.com/distribute/marketing-tools/alternative-distribution
[S28]: https://developer.android.com/studio/publish/app-signing
[S29]: https://developer.android.com/developer-verification
[S30]: https://web.dev/learn/pwa/capabilities
[S31]: https://webkit.org/blog/13878/web-push-for-web-apps-on-ios-and-ipados/
[S32]: https://developer.apple.com/documentation/xcode/supporting-universal-links-in-your-app
[S33]: https://developer.android.com/training/app-links/about
