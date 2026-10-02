# R-U local acceptance handoffs — UNEXECUTED

These are specifications for a later separately authorized local engineering session. No provider/model/account call, installation, live host action or security test was run. No verified runnable Recursion runtime-security entrypoint exists for this lane; no commands are invented. Tests use synthetic artifacts, local processes and disposable profiles only. Existing repository fixture/checker scripts were not imported or run.

## Common prerequisites, exact outcomes and safety stops

Native matrix: Windows 11 25H2 build 26200 Home x64/local NTFS; separate Pro row; Windows 11 24H2 build 26100 Enterprise x64/local NTFS; Linux 6.12 LTS and 6.6 LTS, each exact patch/config with cgroup v2/local ext4. WSL2-ext4 and WSL2 /mnt/c are separate dev/test-only rows and cannot qualify native production. Every patch, policy, runtime, helper, observer and fixture has its own digest/fingerprint.

Before execution, an independent reviewer freezes the complete corpus, expected-result manifest, grant/policy/artifact identity, observer placement, all fault cut points/repetitions/seeds, resource caps and units, allowed enforcement overshoot, observation window and stop deadlines. Missing preregistration means UNEXECUTED. Each mandatory hard bound requires external enforcement or admission refusal. No target/kernel/runtime is already qualified.

A positive useful-operation control and a deliberately unsafe sensor-sensitivity control are mandatory. Missing observations, sequence gaps, untriggered faults, unavailable primitives or a missed positive control cannot pass. Report unknown/unsupported rather than filling zero. Zero-effect predicates permit exactly zero forbidden events. Resource predicates require observed use <= frozen cap B + frozen tolerance epsilon; epsilon=0 for forbidden effects. Proposed local control-receipt experiment bound is 1,000 ms, not a production SLA. Disabled soak is 24 hours over 0/10/100 plugins. Proposed parser corpus boundaries are 1 MiB, depth 32 and 10,000 nodes, expressly experimental.

Independent observers/writer/Stop reserve remain outside guest budgets and failure domain. Stop immediately on an unauthorized effect/synthetic leak, lost observer integrity or approach to the separate safety ceiling; fence guest, retain first evidence and perform only bounded preauthorized cleanup. Otherwise complete the declared corpus/window, or return exact failed/unknown/unsupported outcome. No retry changes acceptance criteria after results.

Each evidence bundle contains immutable inputs and expected results; profile/enforcement/fixture/observer digests; stable process/object identities; sequence/clock/gap records; raw synthetic observations; admission/refusal/fence/control/effect receipts; dimensional resource baselines/peaks/finals; before/first-after recovery state where applicable; cleanup/unresolved-effect ledger and independent reviewer disposition. A successful schema check is artifact QA, not a security result. All measurements in the JSON appendix are null.


## RU-H01 — Default-deny capability probe

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: One inert plugin with empty requested grants; one approved read of a 16-byte synthetic file as positive control; requests covering file, network, process, env, device, IPC, clock, entropy and service verbs.

Additional prerequisites: Known isolated endpoints and canary objects; independent syscall/service observer.

Procedure: Try each ungranted verb, then the narrow granted control. Repeat undeclared, unknown and unsupported capability names.

Independent oracle: Independent object/canary state plus endpoint observer and receiver decision, not guest exit status.

Exact pass: Every ungranted operation refused with missing dimension before effect; forbidden-effect count=0; exactly the allowed positive control succeeds.

Fail: Any denied effect occurs; silent unsandboxed fallback; deny-all implementation fails positive control.

Evidence: Grant/request matrix, sorted refusals, independent effect counts and positive-control receipt. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not establish every syscall or malicious-kernel escape resistance.

## RU-H02 — Attenuation and budget escalation

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Parent allows only read on root A, no egress, budget B. Children request write, sibling root B, longer expiry, deeper delegation and repeated/sibling budget claims.

Additional prerequisites: Atomic parent reservation oracle and pinned typed lattice definitions.

Procedure: Derive child grants; attempt union/replay/stale epoch; concurrently reserve more than parent remaining budget.

Independent oracle: Independent reference meet/reservation calculator plus receiver effect receipts.

Exact pass: All effective dimensions are subsets; total reservations never exceed parent remaining; stale/union/escalation denied; valid narrow child useful read succeeds.

Fail: One widened verb/scope/expiry/audience/budget or duplicate reservation accepted.

Evidence: Parent-child chain, reservation transitions, independently computed expected grants. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove all future capability types or arithmetic implementations.

## RU-H03 — Linux path and mount traversal

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic allowed tree A and denied tree B; symlink/magic-link/hard-link/rename/bind-mount cases; concurrent path exchange.

Additional prerequisites: Disposable Linux profile; test-only namespace/mount setup separately authorized; no host mounts/private paths.

Procedure: Attempt .., absolute and component-swap traversal and rename across A/B with read/write/execute variants; use object identities.

Independent oracle: Independent file-open/effect observer and before/after B canary; separate allowed A read/write.

Exact pass: No B byte returned/modified or denied object executed; crossing denied; A positive control works; complete race trace.

Fail: Any outside-root success, unobserved race admitted as pass, or textual prefix bypass.

Evidence: Object IDs, resolver policy flags, race schedule, denied-canary digests. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove arbitrary filesystem/kernel behavior or physical durability.

## RU-H04 — NTFS junction and reparse abuse

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Local NTFS A/B trees; synthetic junction/reparse swaps, alternate data streams, case aliases, device and UNC-shaped inputs.

Additional prerequisites: Disposable exact Windows target; only test objects; supported tag inventory and protected handle resolver.

Procedure: Probe all declared forms while switching path components; exercise source and destination rename grants and unsupported tags.

Independent oracle: Independent object-handle/file identity observer and denied canary state; no outside network destination.

Exact pass: No outside object/stream reached; unsupported paths/tags typed-refused; authorized NTFS operations succeed.

Fail: Any object scope escape or fallback through alternate path syntax.

Evidence: Reparse tags, object identities, exact input corpus and refusal/output traces. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not certify every NTFS feature or network storage.

## RU-H05 — Inherited handles descriptors and environment

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Supervisor holds synthetic secret file, directory, process/debug handle, IPC/socket and loader/env decoys; explicit safe output/control endpoint list.

Additional prerequisites: Test identities and handles only; no actual auth files, real tokens or service credentials.

Procedure: Spawn through candidate; enumerate observed child handle/FD inventory; request passing/duplication; inject env/home/proxy/loader decoys.

Independent oracle: Independent handle-rights inventory and synthetic sentinel reader/listener; deliberately leaky negative-control launcher.

Exact pass: Only approved endpoint rights cross; denied sentinel/output count=0; no executable substitution; leaky control detected.

Fail: Any inherited/minted host right or ambient config changes closure; positive leak control missed.

Evidence: Inherited-object rights, environment names with synthetic values, executable closure and leak-control receipt. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove absence of undiscovered OS handle types.

## RU-H06 — Direct and induced credential boundary

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic credential C domain, credential-free T domain and R-controlled requests; requests try file/env/process/store access and instruct C/T to export canary via tool/output.

Additional prerequisites: Use only synthetic shim with declared behavior; separately obtain exact documented unmodified upstream C/T support before extrapolating to that route.

Procedure: Probe direct access and confused-deputy paths, including allowed output channels; leak-permitted control demonstrates sensor sensitivity.

Independent oracle: Independent C/T/R object and byte-flow observers; two distinct synthetic secret values across otherwise identical runs.

Exact pass: Zero forbidden credential canary bytes/rights reach R/T; induced export denied; allowed nonsecret result delivered; missing upstream split remains route unknown.

Fail: Direct or induced leak; shim success promoted to real route; filtered display hides raw leaked bytes.

Evidence: Principal/scope diagram, all released raw-channel canary counts, compatibility evidence reference or explicit unknown. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not establish actual CLI behavior, global noninterference, real credentials or entitlement.

## RU-H07 — Birth-to-exit ownership and escape

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic child/grandchild, double-fork/setsid, breakaway request, alternate-launch broker and bounded relauncher; crash cuts before/after creation, association, registration.

Additional prerequisites: Exact native Job/cgroup supervisor and stable process identities; all alternate launchers are test-only and scoped.

Procedure: Exercise finite cut schedule with immediate spawning; attempt migration/breakaway and service-mediated child; apply explicit Full ownership fence.

Independent oracle: Independent process-start inventory joined to at-birth membership and stable handles/IDs, plus intentional escaped control.

Exact pass: Every runnable owned identity captured at birth or launch denied; no guest can create outside scope; Full leaves no live owned identity/relauncher; control detects escape.

Fail: Any first-runnable escape, uncontrolled helper, stale restart or incomplete identity ledger labeled complete.

Evidence: Birth/membership timestamps, job/cgroup config, owned-service list, exit/wait observations. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove all possible races, kernel-stuck liveness or external rollback.

## RU-H08 — Resource saturation and aggregate budgets

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Two parties each try CPU, wall, memory, address, FD/handle, process/thread, disk/temp/inodes, network bytes/connections and output at B-1, B and B+1 units; safe outer envelope.

Additional prerequisites: Numeric caps/units/epsilon and hard vs soft class frozen; each mandatory hard resource has qualified external enforcement or admission refuses.

Procedure: Saturate each dimension singly then selected combinations; attempt sibling exhaustion; keep writer and independent Stop control active.

Independent oracle: OS/runtime external counters plus broker reservations and independent writer/Stop witness.

Exact pass: Every hard observed usage <= B+epsilon; correct throttle/refusal/kill class; aggregate task cap respected; no mandatory observed-only limit advertised hard; control receipt <=1000ms in this experimental profile.

Fail: Cap breach beyond frozen epsilon; guest self-report accepted; hidden unbounded resource or writer starvation.

Evidence: Baselines/peaks/finals, limit configuration, dimensional units, event/receipt timeline and cleanup. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not establish portable unit equivalence or real workload performance.

## RU-H09 — Forbidden egress and network pivot

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Isolated local network with allowed service A and forbidden B; IPv4/IPv6, TCP/UDP, DNS, redirect, proxy, rebinding, loopback and IPC-relay cases.

Additional prerequisites: No public/provider egress; isolated listener/packet observers outside guest; synthetic DNS/proxy only.

Procedure: Try direct socket bypass and every pivot; update epoch mid-connection; perform one permitted A request.

Independent oracle: Independent packet/listener counts and mediator peer identity, including DNS and retries.

Exact pass: Forbidden B receives zero connection/payload bytes; denied direct socket paths blocked; redirect/rebind rechecked; A useful request succeeds; post-revoke new effects zero.

Fail: Any forbidden packet/connection, host-service pivot or unchecked redirected peer.

Evidence: Address resolution/peer bindings, packet counts and per-request grant receipts. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prevent an authorized recipient from redisclosing allowed data or all covert channels.

## RU-H10 — Cross-party and channel smuggling

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Parties A/B with distinct storage/output/IPC identities; synthetic memory/shared-object probes, signals, pipe/socket impersonation and command-looking output.

Additional prerequisites: Independent observer can attribute all test objects and receiver commands; no real desktop/service interaction.

Procedure: Attempt B reads/writes/debug/handle duplication, IPC spoofing, signals and output-as-control; perform explicitly shared read control.

Independent oracle: Object access and receiver command ledger, not rendered UI alone.

Exact pass: Zero unauthorized B data/effects; zero output-to-command promotion; authenticated shared control works.

Fail: Any cross-party byte, action or spoofed principal accepted.

Evidence: Object rights, raw-output digest, accepted/rejected command identities and canary counts. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove microarchitectural isolation or prompt-injection detection.

## RU-H11 — Running-party revocation

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Granted open file/connection/service handle; queued and in-flight operations; next epoch revokes write/egress while preserving another party.

Additional prerequisites: Receiver linearization point and pre-fence drain policy frozen; supported revocable mediation or scoped replacement.

Procedure: Fence epoch; try new operations through existing handles and queued old packets; observe replacement/cleanup if used.

Independent oracle: Independent receiver commit sequence, raw resource effects and unaffected-party progress.

Exact pass: New post-fence effects=0; pre-fence accepted effects explicitly accounted; old handle invalidated or party observed stopped/replaced; unrelated party continues.

Fail: Old connection/FD admits a new effect, revocation receipt precedes effective fence without honest state, or whole task silently restarted.

Evidence: Fence, close/replacement, in-flight settlement and unaffected-party receipts. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not undo bytes already sent/written or prove bounded remote revocation.

## RU-H12 — D022 Stop scope matrix

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Selected agent A, owned descendants B/C, relauncher D and unrelated party E; Aggressive, Full, Lazy with observable operation boundary/deadline.

Additional prerequisites: Mode/scope frozen to current contract; guest processes test-only; escalation preauthorized; stable identity/wait and mount/socket ownership observers.

Procedure: Issue each mode; Full targets rooted A/B/C/D; Aggressive records descendant dispositions; Lazy stops at boundary or reports deadline/escalation.

Independent oracle: Independent ownership set, exit/wait and resource observations plus E heartbeat.

Exact pass: Full reports complete only if all owned identities terminal and no revival; Aggressive does not imply descendants gone; Lazy boundary/deadline truthful; E unaffected; mounts/handles/sockets reconciled.

Fail: False whole-tree claim; unrelated E killed; boundary invented; restart after fence or indefinite wait called success.

Evidence: Requested/delivered/fenced/observed states, mode-specific ownership and resources ledger. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove every mode kills all descendants or any external rollback.

## RU-H13 — Supervisor crash and recovery

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic active party, queued packet, one accepted-but-unsettled side effect and duplicated delayed receipt; cuts around birth, fence and canonical commit.

Additional prerequisites: Disposable process-crash target only by default; separate approved VM-reset cut if D028 durability is being tested.

Procedure: Crash supervisor at frozen cuts; recover with new epoch; deliver stale packets/receipts; reconcile identities and effects before retry.

Independent oracle: Independent observer surviving crash plus first-recovery state digest and canonical event replay.

Exact pass: No stale reanimation/double dispatch; every observed effect retained as settled or unknown; owned resources reconciled; replay deterministic for named failure domain.

Fail: Missing receipt becomes not-executed/zero cost, stale epoch admitted, or duplicate effect/revival.

Evidence: Before/first-after state, observer causal ledger, replay digest and cleanup. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Process crash does not prove VM-reset durability; VM reset does not prove physical-platter resilience.

## RU-H14 — Disabled-path 24-hour soak

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: 0/10/100 synthetic plugins, absent/installed-disabled cold/warm and explicit-enable arms; booby-trapped import/compile/callback/network entrypoints; malformed bounded metadata.

Additional prerequisites: Independent process/module/IO/network/registration observers; baseline and inventory-cost attribution; planned restarts/idle/discovery triggers.

Procedure: Observe full 24-hour interval including restart, discovery and trigger corpus; explicit enable exercises canary entrypoint outside disabled interval.

Independent oracle: Independent action counters, entrypoint canaries, allowed inventory manifest reads and resource records.

Exact pass: All forbidden disabled-event counts exactly zero; no payload scans/cache writes/model/quota work; metadata within frozen caps and cost reported; enable control detected.

Fail: One prohibited event or metadata exhaustion; missing observer coverage or enable control cannot pass.

Evidence: Per-arm forbidden vector, manifest/payload read distinction, resource distributions and complete time coverage. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove universal zero CPU/disk usage, infinite-time inertness or real plugin behavior.

## RU-H15 — Artifact signature SBOM and provenance set

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic artifacts A/Aprime, dependency graph with missing leaf, wrong subject/signature/issuer/builder/source/parameter, unknown license, malformed types and a valid baseline bundle.

Additional prerequisites: Offline test roots and synthetic signatures created only in later authorized session; pinned verifier and policy; no real credentials.

Procedure: Verify each case without loading artifact; strict-release profile and explicitly authorized unsigned-local profile evaluated separately.

Independent oracle: Independent expected-result manifest and alternate verification/calculation of signature and digests.

Exact pass: Valid baseline accepted as evidence only; every wrong required binding rejected; incomplete closure/rights unknown cannot become verified; unsigned never called publisher-verified.

Fail: Any invalid binding admitted, parser execution, or evidence acceptance widens task grant.

Evidence: Per-case reason list, verifier/policy/root IDs and exact signed-byte digests. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove publisher honesty, benign source, complete SBOM or license permission.

## RU-H16 — Malicious metadata parser confinement

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic duplicate keys, depth33, >1MiB payload, >10000 nodes, cyclic references, decompression bomb, external entity/URL and instruction-looking text.

Additional prerequisites: Parser isolated from writer with hard CPU/memory/output caps; no network; format-specific expected errors frozen.

Procedure: Feed corpus at limit and one over; block parser response while writer processes Stop; try external reference fetch.

Independent oracle: Independent parser-resource/network/process observer and writer receipts.

Exact pass: Over-limit/ambiguous input refused before privileged use; zero network/code activation; limits hold; benign at-limit control accepted; writer control <=1000ms for proposed profile.

Fail: Unexpected fetch/code run, canonical writer blockage, cap breach or ambiguous field admitted.

Evidence: Input hashes, parser result/classification and independent resource/control trace. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove absence of all parser bugs or define production parser budgets.

## RU-H17 — Offline trust expiry rotation inclusion and revocation

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic root R1/R2 sequence, valid/invalid cross-signature/threshold, expired/future cert/time, promise-only and invalid/valid inclusion proofs, stale advisory/deny snapshots and clock rollback.

Additional prerequisites: No network; protected independent root and monotonic metadata state; recorded evaluation time T; required policy freshness frozen.

Procedure: Verify same immutable inputs twice; rotate roots in authorized sequence; test attacker-supplied root and rolled-back trust state.

Independent oracle: Independent expected verification result and Merkle/digest calculations; separate test time oracle.

Exact pass: Identical inputs yield identical result; self-root/bad proof/stale current admission rejected; valid historical decision labeled snapshot/time scoped; unknown latest revocation never called clear.

Fail: Bundle supplies its own trust anchor; SET treated as proof where inclusion required; stale snapshot called globally current; replay differs.

Evidence: Root transitions, version floors, time basis, proof/checkpoint IDs and reason lists. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not reveal unseen revocation or prove globally consistent logs.

## RU-H18 — Advisory and pinned resolution semantics

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic ecosystems with nonlexicographic versions, aliases, affected ranges, withdrawal/revision and a pinned transitive dependency graph; stale/no-coverage cases.

Additional prerequisites: Feed and matching policy snapshot pinned; maintenance opt-in state fixed; no actual vulnerable code or network fetching.

Procedure: Match at range boundaries; update advisory snapshot; resolve dependencies offline; attempt substituted name/source/digest and disabled polling.

Independent oracle: Independent hand-computed expected affected/not-affected/unknown matrix and lock digest.

Exact pass: Exact expected matches; unknown coverage/freshness explicit; substitutions rejected; disabled service makes zero fetch/activation; no automatic capability expansion.

Fail: False clear at a boundary, unpinned dependency admitted or disabled fetch occurs.

Evidence: Matching inputs, alias/revision logic, closure digest and maintenance activity counts. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not detect unpublished vulnerability or validate a real package.

## RU-H19 — Verify-to-execute identity and cache race

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Artifact A verified, A substituted at path/cache, dependency DLL/helper changed, symlink swap and stale verified-cache entry.

Additional prerequisites: Protected immutable storage candidate and identity-bound loader; no actual external binary execution in current research.

Procedure: At frozen cuts replace candidate path or dependency; execute later authorized synthetic entrypoint only if exact identity holds.

Independent oracle: Independent opened/executed-object digest plus verifier receipt, not filename.

Exact pass: Only exact admitted closure runs; every mismatch refuses/reverifies; cached evidence binds policy/root/epoch/closure and never skips current grant.

Fail: Different bytes execute or cache key omits an authority/evidence dependency.

Evidence: Open/execute identities, immutable-object state and cache-key fields. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove immutable storage against privileged host attacker.

## RU-H20 — Origin signature cache metamorphic authority

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Same operation and grant with first-party/third-party labels, signed/unsigned/invalid-signature evidence, cached/fresh, previously approved and renamed artifacts.

Additional prerequisites: Evidence admission result separated from runtime allowed-set oracle; approved local unsigned policy used only where authorized.

Procedure: Compare allowed capability sets after evidence eligibility; attempt same forbidden verb under each label and valid narrow control.

Independent oracle: Independent typed meet and receiver effect ledger.

Exact pass: No case widens effective authority; invalid evidence may block admission, never increase privilege; same eligible grants yield same allowed operations.

Fail: Origin, signature, cache or prior success admits an otherwise denied effect.

Evidence: Metamorphic input pairs and differential allowed/denied sets. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not prove every runtime receiver implementation or publisher safety.

## RU-H21 — Updated dependency capability expansion

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: A v1 read-only local artifact; v2 dependency requires egress/write/model/quota; both synthetic signed variants plus unchanged-capability update.

Additional prerequisites: Update authority separated from capability authority; epoch-bound staging and explicit consent fixture.

Procedure: Stage v2; try autoactivation on old grant; then separately supply exact new grant for a positive control; replay v1 packets.

Independent oracle: Independent grant diff, activation and receiver effect timeline.

Exact pass: No new capability/activation before required consent; old epoch fenced; unchanged update follows configured authority; stale packets rejected.

Fail: Update permission alone supplies new capabilities or hidden inference.

Evidence: Dependency/manifest deltas, consent/grant identity and activation receipts. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not authorize any real update, model call or spending.

## RU-H22 — Quarantine rollback and forward recovery

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: A accepted artifact, bad B with synthetic incident, revoked previous A variant, compatible good C and incompatible state schema.

Additional prerequisites: Incident policy, retention limits, compatible rollback rules and already authorized emergency response fixed.

Procedure: Quarantine B during work; try stale B relaunch; rollback to valid A case then attempt revoked/incompatible A; use C forward-recovery case.

Independent oracle: Independent admission/fence ledger and state/artifact compatibility oracle.

Exact pass: B blocked under new epoch; history retained; safe compatible rollback possible; revoked/incompatible rollback refused; C only after independent evidence/grant admission; unresolved effects preserved.

Fail: Bad/revoked digest revives, downgrade expands grants, evidence erased or incompatible state silently opened.

Evidence: Incident scope, artifact/state schema versions, quarantine/recovery receipts and effect ledger. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not recover leaked confidentiality or reverse external effects.

## RU-H23 — Exact platform parity and unsupported admission

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Same semantic capability corpus on every exact native matrix row; separate WSL2-ext4 and /mnt/c rows; disabled Linux controller/LSM and unavailable Windows primitive mutants.

Additional prerequisites: Approved disposable targets for each profile; exact patch/config fingerprint; no substitution of WSL for production.

Procedure: Run mandatory semantic cells and unsupported mutants; compare allowed effect set, refusal class, Stop scope and dimensional resource semantics.

Independent oracle: Independent common expected semantics plus native observers, never one platform adapter self-report.

Exact pass: Each native row meets mandatory semantics or explicit unsupported admission; no best-effort downgrade with strong label; WSL remains dev/test; units not conflated.

Fail: Broader platform grant, missing primitive accepted, WSL promoted or one profile used as proof for another.

Evidence: Per-profile cell matrix, feature/delegation inventory, unknown/refusal records and hashes. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not qualify other editions/builds/architectures or select a technology.

## RU-H24 — Local remote-host protocol simulation

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Two isolated local synthetic supervisors with distinct host IDs; packet loss, duplication, delayed receipt, expired lease and stale epoch; synthetic artifact transfer.

Additional prerequisites: Loopback/isolated local transport only; no live remote account/host; receiver grant and fence implementation pinned.

Procedure: Partition simulated receiver during Stop; replay old work; reconnect and reconcile; try unauthorized artifact/audience transfer.

Independent oracle: Independent sender/receiver event and object ledger with adversarial channel schedule.

Exact pass: Stale/unauthorized requests refused; no duplicate effect; partition reports remote cessation unknown until qualified receiver receipt; artifact audience enforced.

Fail: Local ack/EOF called remote stopped, stale receiver effect or private-scope cross-host transfer.

Evidence: Both causal histories, transport schedule, receipt identity and reconciliation state. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not qualify actual remote OS/network or prove local plugin requirement fulfilled remotely.

## RU-H25 — Executable closure and rights inventory

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic package with nested helper, runtime library, build/download hook, undeclared native extension, incomplete SBOM and conflicting/unknown license metadata.

Additional prerequisites: Independent manually enumerated expected closure and review-status matrix; no external source imported or license decision fabricated.

Procedure: Compare lock/SBOM/provenance/runtime manifest closure; stage bytes without executing hooks; require evidence for each rights disposition.

Independent oracle: Independent expected dependency graph and exact artifact-byte inventory.

Exact pass: All executable/loadable inputs represented or admission blocked; unknown rights remain unknown; no install hook executes at discovery; scope of approved use explicit.

Fail: Omitted helper runs, unknown license becomes cleared, public-readability implies reuse or signature supplies rights.

Evidence: Expected/actual closure diff and rights status references without raw proprietary source. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not substitute for counsel or establish a real source license.

## RU-H26 — Blocked guest cannot block writer Stop or recovery

Status: UNEXECUTED. Entrypoint: unavailable; implement only in a separately authorized session.

Inputs: Synthetic guest floods output, never replies, stalls host callback, saturates reserved budget and crashes parser; unrelated task submits control; reopen after supervisor crash.

Additional prerequisites: Writer/Stop/observer independently scheduled/reserved; frozen proposed 1000ms local receipt bound; bounded raw queues before parse.

Procedure: Apply each blockage and allowed combinations while committing idempotent Stop/fence/status; recover and reconcile without guest cooperation.

Independent oracle: Independent control client and canonical commit observer with monotonic timeline; known-bad inline callback control.

Exact pass: Every admitted local control receipt <=1000ms in proposed envelope; canonical fence recorded without guest reply; queues bounded; recovery retains unknown effects; known-bad starvation detected.

Fail: Guest blockage suppresses fence/control beyond bound, queue grows unbounded, or recovery invents settlement.

Evidence: Control ingress/accept/commit/output times, queue peaks, crash recovery digest and starvation control. Plus the common evidence bundle.

Stop/inconclusive: Common safety stops and missing-observation rule apply to every case.

Passing does not prove: Does not promise a shipped SLA or liveness under host/kernel failure.
