# R-U — Capability-scoped execution and supply-chain admission

Research design candidate · 2026-10-02 · baseline `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`

## Decision summary

The decision-ready result is a **two-stage admission contract**: evidence determines whether exact bytes may be considered for execution; the current task's attenuated grant and qualified enforcement profile determine what those bytes may do. Neither stage replaces the other. Signed is not authorized. No runtime, sandbox, language, framework, packaging format or vendor is selected.

1. A Job, cgroup, process boundary or namespace alone cannot support the complete security claim. Resource containment, capability authorization, confidentiality, code identity/provenance/license, publisher trust and execution qualification require separate evidence.
2. D-028 requires native Windows and Linux parity at exact floors; use the [Landlock delta](../re/report.md#landlock-floor-facts). Unsupported enforcement must refuse admission or use an independently qualified conforming composition, never silently weaken the grant.
3. D-029 requires both direct credential denial and prevention of induced credential export through tools/output. Unmodified upstream binaries must actually support the necessary credential/tool separation or equivalent protection. A wrapper cannot invent that support.
4. Whole-owned-tree cessation is a Full Stop or explicitly tree-scoped obligation. Aggressive and Lazy retain their accepted scope and timing. No shared server's unrelated work may be killed merely to obtain an empty process container.
5. Installed-disabled paths prohibit plugin execution and effects; bounded metadata discovery still has attributable CPU/disk cost. A universal zero-resource promise conflicts with current product specifications and is not adopted.
6. Offline verification can reproduce a decision against a dated trust/advisory snapshot. It cannot know an undisclosed revocation or advisory published after that snapshot. Stale evidence blocks profiles requiring current evidence.

All runtime, isolation, supply-chain-consumer and performance fixtures in this packet are **UNEXECUTED**. It supplies 26 precise handoffs, not an escape-resistance result. Independent review remains pending.

## Authority, evidence and reconciled premises

**LO-record** means static inspection of committed files, never a newly executed experiment. **SD** means a retrieved primary source describes a mechanism. **INF** means an original candidate design or inference. **U** means unverified, unmeasured or missing. All proposed contracts, recommendations and fixture predicates below are INF unless explicitly marked otherwise.

Current governance, D-017–D-033, the active v3 goal, PRODUCT, INTERFACE-STRATEGY, PLUGINS-AND-EDITIONS, the research index/coverage/gaps/synthesis and the actual R-U brief were inspected at the baseline. Accepted decisions are retained: native harness plus orchestrator; comprehensive opt-in capabilities; one fenced canonical writer and optional availability plugin; D-022 controls; Codex first qualification priority; productive continuity; optional bounded autonomy; no vendor-intent claims. Upstream-only operation acquires no hidden native inference dependency.

| Brief premise | Current authoritative reading | Consequence here |
|---|---|---|
| Zero resource consumption for a disabled capability | PLUGINS-AND-EDITIONS explicitly permits bounded metadata discovery and says it costs CPU/disk | Q09/Q18/G03 distinguish exact zero prohibited actions from measured metadata cost; no universal zero-byte/zero-cycle promise |
| Q08/Q20 imply all Stops reap every descendant | Current interface and terminal contracts distinguish Aggressive, Full and Lazy | Full or explicit rooted-tree Stop must capture the complete owned set; other modes keep their actual scope; no unrelated shared work is terminated |
| Every executable must have a publisher signature | Product distribution contract preserves acknowledged unsigned local plugins | Strict verified-release profile requires the full signed evidence set; explicit local-artifact policy preserves unsigned use with truthful missing-evidence status and identical authority/isolation requirements |
| No containment evidence exists anywhere | M1B is synthetic; later FU04 and terminal records retain bounded observations | Preserve those records at their actual scope, without extrapolating them to hostile native containment or current profile qualification |
| Graphical frontend not required | Current user says TUI first, GUI later; D-019 retains comprehensive built opt-in capability | Sequence shared isolation/command backend before frontends; this report neither reduces release scope nor resolves remaining GUI timing interpretation |

**LO-record:** `reference_oracle.py::evaluate_disabled` sets activity counters to zero; F-M1B-015 contains one manifest read and constructed zero activity. These are synthetic oracle contracts, not measured inertness. FU04's retained WSL process-group case detects a `setsid` escape and separately cleans it up; that is evidence against process-group-only hostile containment, not proof of native cgroup tree capture. FU04 still declares no qualified OS/profile; the reduced FU03 result is not the integrated gate. Terminal records describe bounded Windows birth-association observations with explicit exclusions. None was rerun.

Shared upstream facts stay in [R-F](../rf/report.md), [R-G](../rg/report.md), [protocol edges](../protocol-edges/report.md), [R-E](../re/report.md), [R-M](../rm/report.md), [R-P](../rp/report.md) and [R-Q](../rq/report.md), all used as draft cross-lane inputs. In particular, R-M’s [security note](../rm/report.md#mods-security-facts) is negative prior art; source reuse rights remain uncleared.

## Threat model and trusted computing base

The adversary controls an admitted plugin's implementation, tool arguments, output, dependency metadata, manifest claims and child processes; can race revocation, consume its allowed resources and cooperate with another malicious plugin. A compromised publisher, registry, build worker or cached artifact is separately modeled. The adversary does not gain authority merely because its code is first-party or previously accepted.

Assets: task grants, credential domains, canonical state and writer progress, other parties' data, operator control, artifact integrity, evidence and complete accounting. Principals: kernel/admission writer K; independently provisioned credential launcher B and credential-bearing upstream C; credential-free tool/plugin domains T_i; runtime supervisor S; read-only evidence verifier V; separately scoped local/remote host supervisors. R-E defines the exact R/B/C/T relationship and direct plus induced-flow requirement.

TCB inventory is explicit per profile: host kernel and security configuration; boot/admin boundary; supervisor and all reachable privileged helpers; capability compiler and receiver checks; runtime/engine/JIT and host imports where used; filesystem/network mediators; cryptographic verifier, parser, trusted roots and time/freshness source; canonical writer/fence; credential launcher and upstream code authorized to handle secrets. Dynamic loaders, native extensions, install hooks, diagnostic uploaders and service managers belong in that inventory when reachable. A plugin is not in the trusted set merely because it passes the verifier.

A credential-bearing C that is itself malicious can deliberately export or encode credentials through permitted outputs. It is therefore part of the credential TCB, not interchangeable with an arbitrary hostile T plugin. To host an untrusted upstream harness while retaining D-029, the admitted unmodified architecture must separate credential use from attacker-controlled execution/output or provide an equivalent enforceable boundary. If it cannot, strong qualification is refused or the profile is honestly policy-only; a wrapper, signature or output string filter cannot manufacture the missing property.

Out-of-claim conditions: malicious credential-bearing C, host administrator/kernel/hypervisor; arbitrary microarchitectural covert channels; authorized recipients redisclosing data; provider-side rollback; remote host honesty without separate evidence; universal absence of vulnerabilities; universal bounded termination of kernel-stuck processes. A required workflow exposed to an excluded adversary needs a different admitted threat profile, not stronger wording. Resource isolation does not establish confidentiality; isolated address spaces do not establish authorized effects; artifact hashes do not establish rights.

## R-U-Q01 — Typed authority lattice

A proposed `ExecutionGrant` binds goal/task/attempt/party IDs; exact artifact, dependency-lock and manifest digests; policy and GoalSpec digests; parent grant; platform/enforcement fingerprint; epoch; validity interval; allowed operations; budget reservations; delegation depth; audience and privacy labels. A holder cannot edit these bindings. Receiver-authenticated references or authenticated tokens are alternative encodings; neither is selected (RU-R01).

The partial order is **no more authority in any dimension**. Effective grant is the meet of parent task grant, explicit Owner grant, manifest declaration, constitutional/policy restrictions, current lifecycle/Stop state, host enforcement ability, route/account bounds and remaining reserved budget. Absent or unknown required dimensions deny. Deny reasons survive the meet. Sibling grants are not unioned; a party cannot accumulate two delegations into a broader capability. Consumable budgets use a shared atomic reservation ledger, so repeated child issuance cannot mint spend or CPU allowances. Re-delegation can only narrow resource sets, verbs, time, audience, recipients and remaining budget.

| Dimension | Typed scope and attenuation |
|---|---|
| Filesystem | Object-root identity plus relative resolution policy, read/list/create/write/append/truncate/rename/delete/execute as separate verbs; source and destination grants for rename; no textual prefix authorization; special files and alternate streams explicit |
| Network | Endpoint identity, destination address set and ports, transport/application protocol, method, direction, byte/connection caps, DNS/redirect/proxy rules; every redirect and resolved peer rechecked; a hostname never means arbitrary port 443 |
| Process | Approved executable/dependency digest, argument/environment policy, workdir root, child count/depth, parent scope, no breakaway or external launcher without a separately admitted owned operation |
| Environment | Named nonsecret values or opaque service references; no inherited ambient environment, home directory, proxy or loader path; reading an allowed name does not authorize changing executable resolution |
| Device | Named device/object and operation set; raw disks, camera, microphone, desktop/control and kernel/device interfaces deny absent exact grants |
| IPC | Endpoint object, authenticated peer, method, message bound, allowed direction and handle-transfer policy; no ambient user-session bus, control socket or arbitrary named-pipe authority |
| Clock/entropy | Explicit wall/monotonic/virtual clock and precision; bounded entropy source; neither implies determinism or absence of timing channels |
| Services | Method-level service capability, object scope, audience, idempotency key and effect class; calling a broker does not grant that broker's own privileges |

Capabilities are typed requests, not magic names. Platform-specific impossibility remains visible. Memory retrieval and attachment parsing are read capabilities with audience boundaries (R-Q/R-T), not reasons to expose whole host directories. Native and delegated loops use the same admission contract; no upstream SDK owns K's authority.

## R-U-Q02 — Default deny and receiver enforcement

Before the first guest instruction, S verifies the protected executable closure and effective grant, closes ambient handles, establishes filesystem/process/network policy, reserves resources and installs the current epoch. A guest receives only admitted endpoints. Loader/import/compile/start hooks are execution and cannot occur during discovery. Dynamic dependencies cannot be fetched or loaded beyond the approved closure.

A receiver validates each operation's principal, task, digest, epoch, verb, scope, expiry and remaining budget at the commit/effect boundary. Brokered access competes with OS-enforced direct access plus a narrowly exposed capability API (RU-R02); every direct bypass must be denied. The chosen composition is evaluated as a whole. Security hooks inside a hostile guest are advisory at most.

Refusals carry operation ID, missing capability type, redacted requested resource, decision/policy revision, enforcement profile, and reason such as `undeclared`, `outside_parent`, `expired`, `revoked_epoch`, `unsupported_primitive`, `budget_exhausted`, `evidence_stale`, or `effect_unresolved`. No fallback to unsandboxed execution, inherited credentials, hidden helper model or broader route is allowed. Error detail must not reveal the names/contents of resources the caller lacks permission to enumerate. Positive controls prove the boundary still permits the intended narrow operation; deny-all success is not useful compatibility.

## R-U-Q03 — Resource limits outside the guest

Limits have units, scope, enforcement class (`hard`, `rate`, `deadline`, `observed-only`), observation granularity, allowed overshoot and consequence. A mandatory hard bound unsupported by a placement rejects that profile. Per-party ceilings are nested inside task ceilings; aggregate reservation prevents N individually compliant plugins from exhausting the task. Kernel/writer/Stop/observer reserves are outside hostile-party budgets. No numeric performance advantage is asserted.

| Resource | Linux candidate | Windows candidate | Qualification gap / honest semantics |
|---|---|---|---|
| CPU bandwidth and total CPU | [Linux CPU premise](../re/report.md#linux-resource-limit-facts) plus external total-time accounting/termination; no unauthorized realtime policy | [Windows CPU premise](../re/report.md#windows-resource-limit-facts) plus external supervisor | Rate and total time differ; overshoot/timer granularity measured; guest counters insufficient |
| Wall time | Supervisor monotonic deadline independent of guest, host suspend semantics pinned | Same with exact clock/suspend policy | Timeout request is not observed exit; clock discontinuity unknown blocks expiry claim |
| Resident/committed memory | [Linux memory premise](../re/report.md#linux-resource-limit-facts) and separately controlled swap/OOM policy | [Windows memory premise](../re/report.md#windows-resource-limit-facts) | Linux charged memory, Windows commit and RSS are not interchangeable; OOM outcome separately recorded |
| Virtual address space | Qualified process limit or runtime linear-memory/allocator bound | Qualified runtime/OS-specific bound, otherwise unsupported | Use the [Windows bound distinction](../re/report.md#windows-resource-limit-facts) |
| FDs/handles | Process FD limit plus task aggregate broker allocation cap | Brokered/runtime handle cap; arbitrary native handle-count hard cap unestablished | If native raw handles evade mandatory cap, reject that profile; polling is not hard enforcement |
| Processes/threads | [Linux process premise](../re/report.md#linux-resource-limit-facts) plus broker child admission | [Windows process premise](../re/report.md#windows-resource-limit-facts) plus qualified thread/runtime policy | Process and thread counts differ; supervisor-created work must also be charged |
| Disk/temp bytes and inodes | Dedicated bounded ext4 allocation/quota or mediated storage | Dedicated bounded local NTFS allocation/quota or mediated storage | Use the [Linux rate/capacity distinction](../re/report.md#linux-resource-limit-facts); per-user quotas need correct principal granularity; journal/metadata/retained artifacts charged |
| I/O rate | [Linux I/O premise](../re/report.md#linux-resource-limit-facts), conditional on device-stack qualification | Qualified I/O rate mechanism or mediated service | Buffered writes and shared-device cost need attribution; unsupported is not zero |
| Network bytes/connections | Deny direct sockets; count/reserve at network mediator, or qualified external network enforcement | Same, with qualified WFP/OS composition | Include DNS, retries, reconnects and both directions; guest self-report cannot enforce |
| Output volume/queues | Bounded OS/runtime channel, independent drain, byte/event credits and truncation/refusal policy | Same | Bound raw bytes before parse/decompress; logs cannot block control or fill canonical storage |

SD premises: [Linux resource controls](../re/report.md#linux-resource-limit-facts), [Job lifecycle](../re/report.md#windows-job-facts) and [Windows resource controls](../re/report.md#windows-resource-limit-facts). These document mechanisms, not this composition’s behavior. RU-R03 compares nested OS envelopes plus mediated exceptional resources against fully mediated runtime resource handles backed by an outer OS envelope.

## R-U-Q04 — Revocation and the D-022 lifecycle

Revocation first durably advances/fences the selected grant epoch and stops new admission. Each receiver rejects stale use; S then closes/invalidates broker-owned capabilities and applies the accepted Stop policy. A guest-held open file/connection may outlive an ACL change, so in-place narrowing requires mediated revocable handles or stopping and recreating **that party** under a narrower grant. The whole task need not restart. An OS API's success is not proof that the guest lost an already-open resource. RU-R04 compares per-call revocable brokers with party replacement at an epoch boundary, both fail-closed.

| Control | Scope, resources and required observations |
|---|---|
| Aggressive | Immediately interrupt selected agent and fence further selected dispatch; record each separately owned descendant's disposition. Close admitted selected endpoints as policy requires. Do not imply all descendants or external work stopped |
| Full | Fence selected rooted ownership set including shells, subagents, monitors, service restart rules and remote delegations; terminate/reconcile every owned local scope, then independently observe emptiness/exit and resource cleanup. Remote receipts stay separate |
| Lazy | Fence new admission; permit only the predeclared current operation/drain allowlist until named observable boundary and deadline; report waiting or timeout; escalation must already be authorized |
| checkpoint | Validate credential-free state/artifact/cursor identity; do not save a credential-bearing memory image or infer unseen model state |
| interrupt | Request source-specific interruption and record delivery/result; it is neither guaranteed process exit nor external rollback |
| drain | Only pre-admitted effect-specific operations may finish; bounded output/settlement drain cannot acquire new authority |

Record `requested`, `fence_committed`, `receiver_fence_observed`, `control_delivered`, `process_exited`, `containment_empty`, `resources_reconciled` and `external_effect_state` separately with causal IDs. Closing sockets/mount views does not undo sent packets or committed writes. Retained output/artifacts remain under retention grants, not silently deleted. On crash, recovery fences old identities before reconnecting/retrying; unresolved effects are never fabricated as success, zero cost or rollback.

## R-U-Q05 — Exact floor parity

| Profile | Fixed disposition | Required qualification |
|---|---|---|
| Windows 11 25H2 build 26200 Home/Pro, x64 | Native primary floor; local NTFS | Exact edition/build/patch, token/ACL/AppContainer policy, Jobs, handles, network mediator, limits and supervisor privileges |
| Windows 11 24H2 build 26100 Enterprise, x64 | Additional native qualification case | Independent same corpus; no inference from 25H2 or another edition |
| Linux 6.12 LTS, x64, cgroup v2, local ext4 | Native primary | Exact patch/config/LSM ABI/controllers/delegation, process birth, filesystem and network policy |
| Linux 6.6 LTS, cgroup v2, local ext4 | Compatibility minimum | Independent corpus; required features must have a conforming alternative composition |
| WSL2-ext4; WSL2 `/mnt/c` | Two distinct mandatory dev/test-only cases | No production qualification and no inheritance of Windows Job closure into Linux process cessation |
| Arm64; ReFS/xfs/btrfs; embedded alternatives | Later/deferred | Not quietly used to satisfy current floors |
| SMB/NFS canonical state | Out of first-release scope | Not a passing alternative |

Source delta: use the [exact Landlock floor note](../re/report.md#landlock-floor-facts). Accordingly, a Landlock-only network profile is inadmissible; combine a qualified network mediator/OS boundary or refuse. Runtime ABI/config detection precedes admission, and a best-effort compatibility downgrade cannot retain a stronger security badge. [Seccomp premises](../re/report.md#linux-seccomp-facts) and [WFP premises](../re/report.md#windows-filtering-facts) supply separate mechanism evidence, not qualification.

Semantic parity means the same deny/allow/refusal/Stop/evidence contract, not identical syscalls or counter meanings. Profile keys bind implementation, OS policy, kernel/runtime, principal layout, helpers, filesystem, trust snapshot and fixture revision. Any relevant change invalidates inherited execution qualification (RU-R05). D-028 VM-reset durability is an application-consistent commit/replay question, not a physical-platter or sandbox-escape result.

## R-U-Q06 — Explicit containment claims

| Claim | Provider-free observable | Caveat |
|---|---|---|
| Birth-to-exit process containment | Independent process-start inventory matches admitted stable identities and scope membership from first runnable instruction | Current membership cannot establish past membership or external helper capture |
| Filesystem view/access | Outside-root canaries remain unread/unmodified; expected narrow operations work | Metadata leakage is separately classified; sanitizing a path string is insufficient |
| Egress confinement | Independent listener/packet observer records no prohibited outbound bytes or connections | Allowed endpoint may itself relay data; permitted egress is not confidentiality |
| Credential non-access | Synthetic secret inaccessible directly and through allowed C/T/output routes | Real upstream separation remains an unmodified-binary compatibility prerequisite; no actual secret testing here |
| Kernel/host surface restriction | No denied device, process-debug, namespace-entry, service or privileged IPC operation succeeds | Finite syscall probes are not kernel exploit resistance |
| Inter-party isolation | A cannot read/modify B's memory, storage, handles, output or command channel outside a shared grant | Shared CPU/cache timing and authorized sharing are separate threats |
| Control and recovery independence | Saturated/crashed guest cannot suppress writer fence, Stop receipt or correct recovery state | Host-wide kernel failure is outside guest containment claim |

R-E owns the detailed credential OS facts and C/T qualification dependency. R-P owns injection provenance, authority promotion and receiver checks; R-Q owns memory audience/retention. This lane owns execution of those decisions. A safe prompt does not sandbox a syscall, and a sandbox does not make untrusted output authoritative (RU-R06).

## R-U-Q07 — Escape and abuse matrix

The full runnable-handoff specifications are in `UNEXECUTED-local-test-handoffs.md` and `local-test-handoffs.json`. Here each row states the exact security predicate; U indicates missing observation, never a pass.

| Probe family | Variants | Pass predicate |
|---|---|---|
| H03 paths/mounts | `..`, absolute paths, symlink exchange, bind/mount crossing, hard links, rename source/destination, Linux magic links | No outside-root canary byte read/write, no object substitution, allowed control succeeds; race oracle observes all attempts |
| H04 NTFS | Junctions/reparse points, alternate data streams, case/normalization aliases, device/UNC paths, rename race | Same object-level scope predicate; unsupported tag/path refuses before effect |
| H05 inherited authority | File/dir/process/token/section/socket handles and FDs, descriptor passing, loader/env injection | Only allowlisted endpoint rights cross; no secret or host capability reaches guest; positive leak control detected |
| H06 credentials/deputies | Synthetic direct file/env/memory/store access and induced tool/export/output | Zero synthetic credential bytes across forbidden boundary; no broad C helper reachable; unknown C/T support blocks strong label |
| H07 descendants | Immediate child, grandchild, double-fork/setsid, Job breakaway, alternate launcher/service restart, parent crash and PID reuse | Every admitted owned identity captured at birth or attempt denied; no unowned work killed; no stale revival |
| H08 exhaustion | CPU, memory, address space, handles/FDs, children/threads, disk/inodes, connections/bytes, output | Each hard limit respected under its pinned unit/overshoot contract; expected refusal/throttle/kill observed; writer/Stop reserve survives |
| H09 network pivots | IPv4/IPv6, TCP/UDP, DNS, loopback, redirect, proxy, rebinding, local service/socket relay | Prohibited destination gets zero observed connection/payload; raw bypass denied; allowed control works |
| H10 channels/party crossing | Signals, named pipes, Unix sockets, shared memory, process memory, stdout command-shaped content | No unauthorized object access, authority promotion, receiver action or cross-party byte leak |
| H11 resource revocation | Already-open file/connection, queued request, delayed receiver, in-flight allowed effect | Post-fence newly admitted effects zero; pre-fence effects explicit; revocable handle ceases or party replacement completes |

The [object-resolution premises](../re/report.md#object-resolution-facts) motivate object-bound/race-resistant resolution. An openat2-based resolver competes with a no-direct-path mediated object store; Windows alternatives require equally strict handle-based resolution plus OS access checks. Neither textual canonicalization nor a runtime hook is accepted as the sole adversarial boundary.

## R-U-Q08 — Whole-owned-tree termination, not a schema proof

The brief's all-modes premise is reconciled above. Full Stop acceptance is a conjunction over the rooted ownership set: admission fenced; every owned execution captured or explicitly unresolved; stable identity exits; no live processes in owned containment; zombies/wait handles reconciled; output drained or marked truncated; owned IPC/socket/mount handles closed or assigned explicit retained ownership; relaunchers fenced; external effects settled or explicitly unknown; canonical outcome committed. Only the observed conjunction can support a bounded local termination claim.

For Windows, compare creation-time Job association with a fully gated supervisor creation path that cannot run guest code until association is verified. Use the [creation-attribute premises](../re/report.md#windows-creation-attributes-facts). Neither breakaway nor a service-mediated launch may evade ownership. Use the [Job notification limits](../re/report.md#windows-job-facts); reconcile observations against Job queries and identity-bound process handles. Last-handle closure works only if its ownership and kill-on-close configuration are correct; a leaked duplicate handle invalidates that assumption.

For Linux, compare birth into the delegated cgroup with an independently qualified gated launch path. Use the [birth/lifecycle premises](../re/report.md#linux-resource-limit-facts). Guest cannot migrate itself or cause out-of-scope service creation. Use the same note’s population limit when evaluating the claim. PID numbers alone are not identities. Uninterruptible kernel work yields timeout/unresolved, not false `reaped`.

No finite test proves every possible descendant race. H07/H12/H13 challenge defined cut points and independent observer completeness, including deliberately escaped negative controls. A shared upstream server unable to isolate the selected ownership set must expose an appropriate supported session control or reject Full Stop qualification; killing unrelated sessions is prohibited (RU-R07).

## R-U-Q09 — Disabled-path inertness without fictional zero cost

Define a disabled interval from admission of an installed-disabled configuration through an explicit enable or the end of the declared observation window. During that interval, the forbidden-event vector must remain exactly zero: implementation import/compile/instantiate; payload scan; install/update hook; plugin-created process/thread/timer/watcher; network or credential access; model call; quota reservation/debit/spend; runtime cache write; context injection; tool registration/enumeration; callback; event subscription. No source merely being installed or discovered may trigger activation.

Host-owned bounded manifest inventory is separately attributable: bytes read, CPU time, memory retained and inventory storage. It may occur outside the payload's inert storage and is not universally zero. Metadata parser size/depth/CPU limits prevent a disabled malicious manifest becoming an exhaustion channel. Installed payload footprint, preexisting cache footprint and inventory cost must remain visible; do not report unknown cost as zero. Neither disabled updates nor periodic health probes secretly activate the payload.

H14 compares absent, installed-disabled cold, installed-disabled warm and explicit-enable controls with 0/10/100 synthetic plugins; 24-hour proposed soak includes restart, idle, discovery, malformed metadata and attempted callback triggers. Independent OS/runtime observers plus booby-trapped guest entrypoints must detect a deliberately enabled positive control. Any one forbidden event falsifies inertness, even with negligible resource cost. The metadata cost distribution and bounded inventory limits are separately reported; they cannot falsify a nonexistent universal zero-cycle promise. RU-R08 compares prebuilt bounded catalog discovery with bounded on-demand manifest parsing under the same no-execution invariant.

## R-U-Q10 — Classification and falsification thresholds

Every `ClaimRecord` carries statement, adversary/exclusions, exact profile, source and revision, evidence class, observation completeness, test ID/seed/cut, independent oracle, result, uncertainty and reviewer disposition. SD never automatically becomes LO. A retained test receipt is LO-record; authoring JSON is not execution. U remains U if a sensor dropped events, the positive control did not fire, a required primitive is absent or the exact profile differs.

Security categorical threshold is **one unauthorized successful operation, one secret byte, one escaped owned identity, one unauthorized activation or one stale-epoch acceptance**. Allowed failures/refusals are not leaks. Resource thresholds use the frozen cap plus declared measurement/OS enforcement tolerance; a mandatory hard zero-effect counter has no nonzero tolerance. Proposed H26 control budget is 1,000 ms per local control receipt while hostile output is saturated, with separate durable fence and process-stop observations; this is an experimental threshold, not a shipped SLA. Exceedance refutes that latency candidate only, not an authorization invariant. Missing timing evidence means U.

Qualification is `unqualified`, `qualified-for-this-envelope`, `rejected` or `unknown`; no numerical safety score blends a confidentiality failure into better throughput. Passing finite fixtures establishes only their bounded predicates. RU-R09 compares independent event tracing plus object-state reconciliation with a separately isolated observer and challenge/response canaries; each must detect its known-bad control.

## R-U-Q11 — Supply-chain admission object

Proposed `ArtifactEvidenceBundle` includes exact artifact and closure digests; immutable dependency resolution/lockfile; SBOM with transitive component identities, versions, relationships and completeness statement; platform/runtime/ABI range; license/notice/provenance references and review disposition; publisher identity evidence; artifact signature and builder attestation; source/build inputs; capability manifest; expected executable entrypoints; verifier/policy/root snapshot IDs; advisory snapshot and expiry; distribution/update provenance; parser limits. Runtime-loaded native libraries, plugins, shell helpers and install-time scripts are part of the closure, not invisible additions.

<a id="supply-chain-format-facts"></a>
The release-profile verifier separately answers: bytes match? signer/builder accepted? expected source/build parameters? closure accounted? known risk accepted under current policy? license/reuse/distribution reviewed? requested capability set supported? The final execution admission still requires Q01. [SPDX 2.3 package information](https://spdx.github.io/spdx-spec/v2.3/package-information/) and [CycloneDX 1.6 schema](https://github.com/CycloneDX/specification/blob/1.6/schema/bom-1.6.schema.json) are alternative exchange formats, not selected tooling or proof of completeness. Missing dependencies and `NOASSERTION`/unknown license fields are preserved; an SBOM alone does not clear rights.

<a id="provenance-attestation-facts"></a>
[in-toto Statement v1](https://github.com/in-toto/attestation/blob/main/spec/v1/statement.md) binds a typed predicate to subject digests. [SLSA provenance](https://slsa.dev/spec/v1.2/build-provenance) records build context. The consumer adds expectations and evidence policy; it does not trust a self-asserted security level. A locally authored unsigned plugin remains possible under the product's explicit digest-aware local-artifact policy. Its unsigned/unattested fields stay missing, any authorized exception is narrow and dated, and it cannot claim verified-publisher status or bypass runtime constraints. Strict release admission rejects missing mandatory evidence. RU-R10 compares consumer verification of bundled attestations against a locally approved immutable evidence manifest plus independent reconstruction checks, with the same required evidence and runtime grant floor.

## R-U-Q12 — Offline deterministic verification and freshness limits

Verification is a pure decision over immutable artifact bytes, evidence bundle, pinned verifier, independently provisioned trust roots/identity expectations, stored minimum metadata versions, advisory/revocation snapshot and a recorded trusted evaluation time. The result and reason list must reproduce exactly for those inputs. Verification does not fetch arbitrary SBOM URLs, execute scripts, import the artifact, discover roots from it or contact a vendor. A separate, explicitly enabled update path may refresh signed trust/advisory bundles; it cannot silently widen execution authority.

Checks: bounded parse with duplicate/ambiguous fields rejected; digest and detached/signature-envelope binding; expected signer identity and issuer/key; certificate chain to an independently trusted root; trusted signing-time evidence within certificate validity; allowed algorithm; attestation type and subject; expected builder/source/parameters; complete dependency evidence or explicit blocker; inclusion proof/checkpoint where required; version/expiry/rollback policy; current deny/quarantine entries; license disposition; manifest-grant fit. Preserve exact signed bytes; do not normalize them into a different signature message.

<a id="sigstore-evidence-facts"></a>
The [Sigstore bundle schema](https://raw.githubusercontent.com/sigstore/protobuf-specs/main/protos/sigstore_bundle.proto) distinguishes modern proof material and older promise-compatible bundles. A signed entry promise is not interchangeable with a verified Merkle inclusion path to a trusted signed checkpoint. A current-proof policy rejects promise-only evidence rather than weakening its claim. A checkpoint snapshot proves the bounded recorded log claim, not global consistency with all observers or future absence of misissuance. The [Sigstore security model](https://docs.sigstore.dev/about/security/) uses short-lived certificates; current artifact quarantine/identity compromise response remains a separate consumer policy, not an invented universal certificate-revocation API.

**SD — Sigstore bundle guide:** bundles can carry signature/identity verification material and optional timestamp/log evidence; version and consumer policy determine required evidence. [Bundle guide](https://docs.sigstore.dev/about/bundle/)

<a id="tuf-version-facts"></a>
[TUF 1.0.36](https://theupdateframework.github.io/specification/v1.0.36/) supplies versioned-role/threshold/expiry/root-rotation concepts. Competing offline designs are a provisioned signed release bundle with sequential root updates versus an independently administered signed local approval catalog with equivalent version/freshness checks (RU-R11). Both need an out-of-band initial root and protected monotonic trust state. An artifact cannot authenticate its own root. If trusted time is unavailable or metadata stale, current admission is blocked; historical replay may still say “valid against snapshot S at time T.” Offline cannot establish the latest global revocation. Missing freshness never becomes “not revoked.”

## R-U-Q13 — Dependency security, quarantine and rollback

<a id="osv-advisory-facts"></a>
An opted-in security-maintenance capability imports bounded, dated public advisory snapshots into a separate service. [OSV's schema](https://ossf.github.io/osv-schema/) supports ecosystem/version/range, aliases, revisions and withdrawal information; matching must respect ecosystem semantics, not lexicographic version comparison. Publisher advisories and independent ecosystem feeds are inputs with origin/freshness retained. This research did not obtain usable CISA/NVD content, so it makes no current-vulnerability or KEV completeness claim. A local mirror snapshot competes with operator-supplied signed offline snapshots (RU-R12); neither runs hidden work when disabled.

At each candidate update: lock exact artifact and dependency digests; verify resolution and all build/download hooks under separate authority; compare closure, license, signer/builder, ABI and capability deltas; verify evidence; stage immutable bytes without activation; execute only later-authorized qualification; request explicit consent for newly required capability dimensions; fence old epoch; drain/stop under policy; activate new identity. Automatic update permission does not imply permission for new egress, credentials, model calls, spending or grant administration. Reproducibility is an independently compared build-output property, not a lockfile label; hermetic resolution and reproducible outputs are distinct.

Quarantine revokes new admissions for exact bad digests/closure/affected profiles, records cause and evidence, fences active use according to already granted emergency policy, preserves forensic material under bounded retention and marks unsettled effects. It never erases history or becomes a mandatory centralized remote kill switch. Rollback points to an independently reverified previously allowed artifact compatible with current state schema and grant; no automatic rollback to a revoked/vulnerable version. Forward recovery is the conforming rival when old state or artifact is unsafe (RU-R13). A deliberate code downgrade can be authorized while update metadata remains monotonic; do not disable rollback-attack defenses. Recovery does not undo published effects or restore credentials by copying them.

## R-U-Q14 — Supply-chain attacks and residual trust

| Adversary/action | Detectable/rejectable condition | Recorded or residual risk |
|---|---|---|
| Compromised legitimate publisher signs malicious bytes | Unexpected digest, capability delta, denied signer snapshot, independent tests or review find violation | Valid signature on harmful expected content can pass identity checks; signer intent cannot be inferred |
| Typosquat/substituted dependency | Exact ecosystem/name/source/digest binding disagrees with approved lock/expectations | An initially approved wrong package is not fixed by valid provenance; identity enrollment needs independent review |
| Build worker compromise | Provenance/source/parameters or independent reconstruction mismatch | A compromised trusted build platform may forge internally consistent attestations; SLSA does not universally eliminate that TCB |
| Silent capability expansion | Manifest diff, runtime import/endpoint request or binary behavior exceeds current grant | Undeclared malicious attempts may be prevented; signature does not reveal all behavior |
| Malicious SBOM/provenance/parser payload | Size/depth/duplicate/type limits, no remote references followed, isolated parser failure, digest mismatch | Well-formed incomplete or dishonest inventory needs corroboration; parser/library compromise remains TCB risk |
| Cache substitution or verify/execute race | Protected immutable content plus execution-time identity mismatch | “Cache hit” is not validation; writable DLL/search path can invalidate closure |
| Stale/replayed trust or advisory data | Protected minimum version, expiry and freshness check fails | Offline absence of a newer revocation remains unknown |
| Local maintainer signs unsafe release | Grant and sandbox still deny unapproved effects | Runtime bugs and authorized data misuse remain; license/signature cannot prove suitability |

<a id="slsa-verification-facts"></a>
[SLSA verification guidance](https://slsa.dev/spec/v1.2/verifying-artifacts) explicitly limits what provenance checking establishes. RU-R14 compares independent reproducible reconstruction plus policy checks with separated builder/reviewer attestations and the same behavioral gate; neither is assumed to detect malicious but faithfully built source. Quarantine receipts describe observations and impact, not a claim about vendor motives.

## R-U-Q15 — Origin never supplies authority

Admission is the conjunction of separate results, not a “trusted” boolean. `identity_verified`, `provenance_valid`, `license_reviewed`, `publisher_policy_accepted`, `execution_profile_qualified`, `task_grant_valid`, `resource_reserved` and `current_epoch` are independent fields. First-party packages obey exactly the same functional/OS/egress/model/quota/spend authorization rules; privileged built-ins have specifically enumerated kernel roles, not blanket rights bestowed by a signature.

For the same requested operation and current grant, changing only publisher label, signature validity, cache source or previous acceptance must never enlarge the effective capability set. It may change whether artifact evidence permits admission; it may not change allowed operations after admission. H20's metamorphic cases prove this finite oracle. A signature valid for artifact A cannot authorize altered A', a renamed package or a changed dependency lock. License review permits specified uses, not runtime actions. The [R-M source and trust findings](../rm/report.md#mods-security-facts) supply neither porting rights nor isolation. RU-R15 compares a central typed meet compiler with independently checking receivers consuming a minimal grant IR; both enforce the fixed invariant.

## R-U-Q16 — Placement comparison, no selection

Costs below are **qualitative design hypotheses**; all startup, throughput, memory, maintenance and compatibility measurements are U. All conforming untrusted placements keep K's writer and control reserve outside the guest failure domain. An in-process evaluator in a separate host is not “in-process in K.”

| Placement | Containment/capabilities and TCB | Platform, cost and debuggability hypothesis | Real conforming competitor |
|---|---|---|---|
| P1 trusted immutable in-process contributor / restricted module | Trusted code can use typed interfaces; arbitrary native code sharing K's address space is not an adversarial isolation boundary. A verified restricted evaluator with no FFI must separately prove memory/capability/preemption properties | Direct calls may reduce transport work, but a fault can share host fate; per-party native hard caps and interruption difficult. Only trusted immutable registry is currently an admissible plain in-process scope | Same trusted contributor in bounded OS-sandboxed worker; for untrusted restricted evaluator, P2 or P3 with independent host/writer |
| P2 Wasm/WASI capability imports | Guest has no ambient host IO in the core model; actual import functions, runtime/JIT, memory, compilation/cache/deserialization and native libraries become TCB | Potentially common ABI across floors, but host import availability and syscall/resource behavior differ; compilation/start/cache cost U; debugging needs guest/host correlation | P3 OS-sandboxed process with method-scoped broker and equivalent limits |
| P3 supervised child plus OS security | Distinct protected address space plus qualified filesystem/IPC/network restrictions; supervisor, policy compiler and kernel trusted; Job/cgroup supplies lifecycle/resources only | Native CLI compatibility plausible, integration differs sharply by OS; process startup and broker cost U; native debugger must be separately admitted | P2 in independent bounded runtime host, or P4 where qualified |
| P4 container-style namespace boundary | On Linux, OCI configuration composes namespaces, mounts, identity/capabilities, resources and seccomp; shared kernel is still trusted; no daemon/host socket grant | Image layers/runtime/update closure increase inventory; namespace/loader compatibility and warm/cold cost U. Native Windows support must be qualified separately; production WSL substitution forbidden | P3 native sandbox composition with immutable executable closure |
| P5 remote/host boundary | Moves code to separately enrolled execution host; local host exposure reduced only if transport/artifact ingress is bounded; remote supervisor/OS now trusted; network partition complicates Stop | Cold transfer/queue/handshake cost, data residency, dependency inventory and remote debugging overhead U; each execution host keeps its own floor and grants | Dedicated local P3/P4 execution host with equivalent receiver grants and privacy policy |

<a id="runtime-placement-facts"></a>
SD: [WebAssembly core](https://webassembly.github.io/spec/core/intro/introduction.html) places environment access at imports; [WASI v0.2.0](https://github.com/WebAssembly/WASI/blob/v0.2.0/README.md) describes capability-oriented APIs. [Wasmtime security](https://docs.wasmtime.dev/security.html) is implementation prior art only, including output/host-boundary concerns. [OCI v1.2.1 Linux configuration](https://github.com/opencontainers/runtime-spec/blob/v1.2.1/config-linux.md) describes composition fields, not an escape-proof isolation tier. Versions cited are research references, not selected Recursion dependencies.

Per-placement recommendations RU-R16–R20 preserve these competitors, negative traces and non-proofs in `recommendations.json`. No weighted score can trade away mandatory safety or D-019 local functionality. Remote execution cannot silently replace a required local-plugin workflow; selection awaits matched useful-task acceptance under fixed invariants.

## R-U-Q17 — Pre-benchmark elimination traces

| Placement | Negative trace that eliminates the claimed profile | Separate unsafe negative control |
|---|---|---|
| P1 | Required hostile plugin can address K memory, invoke FFI or block K's writer; no independently enforceable preemption/resource bound | Arbitrary native shared-memory plugin with “trusted publisher” exemption |
| P2 | Required import exposes host root/raw socket/ambient credential or host callback cannot be revoked/bounded; required floor runtime support absent | Unrestricted WASI preopens/host `exec` import |
| P3 | First runnable instruction outside scope; inherited privileged handle; required FS/network policy missing on exact floor | Same-user child plus clean environment and Job/process-group only |
| P4 | Host/daemon socket reachable; namespace join or mount exposes denied objects; Windows composition depends on production WSL | Privileged/host-network container with host filesystem mounts |
| P5 | Remote receiver accepts stale epoch, cannot enforce grant, releases secrets, or reports local Stop as remote cessation after partition | SSH command treated as a complete remote security/settlement contract |

These reject a specific composition/claim, not every implementation of a category. A missing primitive can prompt a conforming alternative composition, not a benchmark to excuse it. Runtime revocation can use scoped party replacement; unsupported in-place revocation does not eliminate a placement if replacement meets the actual revocation contract without reviving stale work. A true required primitive absence remains unsupported, not “pending performance.”

## R-U-Q18 — Preference reversal rules

One forbidden disabled-path activation/effect reverses any preference relying on inertness. One escaped owned identity, unauthorized effect, direct or induced credential leak, cross-party disclosure, unauthorized widened grant or stale receiver acceptance rejects the proposed untrusted profile before cost comparisons. A hard resource-cap breach, writer/Stop starvation beyond the frozen experimental bound, or semantically divergent platform result also rejects that profile's claimed envelope.

A conforming placement preference can reverse only through matched evidence: same task/grants/inputs/output quality and independent security floors, then measured cold/warm startup, steady-state resources, control tails, recovery correctness and maintenance surface. If a candidate cannot perform useful authorized work, passing denial tests is insufficient. Metadata overhead may reverse a performance preference when measured against an approved budget, but is not a violation of the corrected no-execution invariant. RU-R21 compares a hard-gate-then-Pareto evaluation with a hard-gate-then-preregistered-priority ranking; no product is selected and no favorable measurement exists.

## R-U-Q19 — Provider-free acceptance suite

The 26 handoffs include exact synthetic inputs, prerequisites, independent oracles, evidence, pass/fail predicates, stops and non-proofs. No verified runnable Recursion security entrypoint exists for this lane; no command is invented. They require a later authorized engineering session and disposable local targets, not account/provider calls.

| IDs | Coverage |
|---|---|
| H01–H02 | Default-deny positive/negative probes; meet/attenuation/sibling-budget escalation |
| H03–H06 | Filesystem/NTFS races, inherited handles/environment, direct and induced synthetic credentials |
| H07–H13 | Birth capture, saturation, egress, inter-party/channel abuse, revocation, Stop scope, crash/recovery |
| H14 | Disabled-path soak and separately measured metadata cost |
| H15–H19 | Signature/SBOM/provenance negative set, parser confinement, offline time/root/rotation, advisory matching, verify/execute race |
| H20–H22 | Origin/cache metamorphic invariance, capability-expanding update, quarantine/rollback/forward recovery |
| H23–H26 | Floor parity and unsupported admission; bounded local remote-host simulation; closure/rights inventory; writer/Stop under blocked guest |

Run specification must pin all exact floor variants, artifact/runtime/helper/observer digests, synthetic corpus, cap units, observation window, control deadlines, fault cut points, repetitions, seed, trusted evaluation time, evidence snapshots and expected outcomes before execution. Invalid or incomplete preregistration yields `UNEXECUTED`, not an adaptable success criterion. Known-bad controls are required to demonstrate sensor sensitivity. All measured fields remain null in this report.

## R-U-Q20 — Authority, complete ownership and independent control proofs

Three independent evidence joins are necessary:

- **Authority:** H02 and H20 compare identical request/grant pairs across valid signature, first-party label, prior acceptance and cache hit; receiver decisions never admit a capability beyond the meet. H21 changes a dependency/manifest and must block new capability until a fresh scoped grant.
- **Ownership:** H07/H12/H13 join creation-time identity traces, scope queries, process exit/wait observations, owned-service restart fences and recovery epochs. Full Stop cannot report complete while any owned identity is live/unresolved; Aggressive/Lazy cannot imply broader cessation. No unrelated control process is killed to make counts zero.
- **Control:** H08/H16/H26 saturate guest output/parser/CPU/storage or block its response while K accepts and durably records a Stop/fence through reserved independent paths. A guest callback cannot run inline on canonical commit or Stop; bounded queues and independently supervised parsers compete with isolated ingress workers plus a reserved control scheduler (RU-R22). Neither design is presumed implemented.

Local remote-host simulation establishes protocol behavior under loss/duplication/stale epochs, not actual network/remote OS security. A partition leaves receiver cessation unknown unless an independent qualified receipt exists. Canonical writer fencing remains in core; availability takeover is optional D-020 machinery, not an automatic distributed-consensus dependency for every sandbox. Productive continuity requires preserving authorized work, retained evidence and honest accounting after a party crash or switch, not replaying an unknown effect until something succeeds.

## Completion-gate disposition

| ID | Research disposition | Execution/acceptance ceiling |
|---|---|---|
| R-U-G01 | Q01/Q02/Q04/Q05 specify typed, attenuated, default-deny and revocable authority | Cross-platform enforcement U |
| R-U-G02 | Q03 and H08 specify per-party/task external resource enforcement and gaps | Caps/overshoot/control measurements U |
| R-U-G03 | Q06–Q10 enumerate claims and exact oracles; prompt conflict explicitly reconciled | Whole-tree/zero-effect proof NOT ESTABLISHED; no universal zero-resource assertion |
| R-U-G04 | Q11–Q14/H15–H19/H22 specify offline evidence, freshness, threats and recovery | Latest unseen revocation and determined-attacker guarantee impossible from offline snapshot alone |
| R-U-G05 | Q01/Q15/H20 retain non-origin authority invariant | Finite metamorphic runtime suite UNEXECUTED |
| R-U-G06 | Q16–Q18 compare five placements with conforming rivals and rejection traces | No selection |
| R-U-G07 | Q19 and complete handoff appendix specify every mandatory fixture family | All 26 UNEXECUTED |
| R-U-G08 | Recommendation ledger gives conforming option, falsifier and non-proof for each proposal | No route or runtime qualified |
| R-U-G09 | Explicit non-results below | No measured claims or entitlement |
| R-U-G10 | Artifact-only authoring, input hashes, bounded privacy/secret-pattern QA recorded | Independent review pending; scan is not a universal secret detector |

## Explicit non-results and bounded next evidence

No measured escape resistance; no measured containment/performance advantage; no guarantee against a determined supply-chain attacker; no route qualification, authentication approval, entitlement or license clearance; no sandbox/runtime/vendor choice. No model/provider/credential/account call, installation, security test, benchmark, live-host action, counsel contact, repository edit, merge, publication or deployment occurred.

Unknowns have precise owners of evidence: profile execution session supplies H01–H14/H23/H26; isolated verifier implementation session supplies H15–H22; upstream compatibility review supplies unmodified C/T evidence before H06 may support a strong route claim; per-artifact rights review supplies H25's license/reuse decision; remote-fabric session supplies real-host confirmation beyond H24 simulation. These are unexecuted handoffs, not requests to reopen D-028/D-029 or hide comprehensive capabilities behind deferrals.

See `coverage.json` for exact question/gate text and locators, `recommendations.json` for every rival/falsifier/non-proof, `candidate-contracts.json` for machine-readable field obligations, and `source-register.md`/`.json` for public revision/retrieval/hash limitations.
