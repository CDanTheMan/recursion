# Operating system platform conformance fixtures

FU04 research report and local qualification handoff

Sources checked 1 and 2 October 2026 | Report prepared 2 October 2026 | Recursion v3 | G04 and DS19 follow up

## 1 Findings and decision boundary

Every platform case in this report is Unqualified. The report supplies a proposed, machine readable qualification contract and a preregistered negative trace catalog; it supplies no measured platform result. Native Windows and native Linux have exactly the same evidence burden as compatibility layers. No operating system, kernel, filesystem, terminal, runtime, store, process library or product configuration is selected or certified.

The central finding is that qualification must attach to an exact behavioral envelope, not to a brand name. The envelope includes the operating system and updates, creation and containment method, privileges and namespace boundaries, terminal and shell path, supervisor policy, storage stack and failure domain. The result that a broker or writer consumes must carry that envelope's fingerprint. A result obtained through a different terminal host, mount route, supervisor policy or storage server is a different result.

The latest Owner direction defines v3 as a standalone harness and an orchestrator or wrapper of other harnesses; Hermes is retired. Therefore an upstream harness is an explicit execution route with its own process, terminal, service and possibly remote-work boundaries. A native child wrapper cannot inherit qualification for work delegated by that harness to another service or host. The schema and fixture scope cover both native and wrapped execution without selecting an upstream implementation.

Five distinctions determine whether later experiments can support acceptance:

1. Managed scope membership and complete capture of causally created work are separate claims. Killing members cannot establish that escaped or externally created work was captured
2. Closing transport, disconnecting a client, observing an empty containment scope, observing a process exit and settling an execution are independent predicates
3. An atomic namespace operation is not a promise that acknowledged state survives a crash. Process death, virtual machine reset, host reset and physical power interruption have different failure domains
4. Resource exhaustion is a family of observations. Throttling, allocation refusal, individual process death and group death must not be collapsed into a portable OOM result
5. Missing evidence yields unknown. Neither a successful API call, an absent notification, an unrun fixture nor an implementer's own PASS can qualify a profile

The most consequential newly verified documentation boundary is ConPTY shutdown. Microsoft documents that ClosePseudoConsole returns immediately starting with Windows 11 24H2 build 26100; earlier versions can block indefinitely if output is not closed or drained. This forces a build specific trace rather than one generic Windows teardown expectation. A return from ClosePseudoConsole is never the suite's execution completion oracle. [S04]

Microsoft also explicitly warns that delivery of most Job completion port notifications is not guaranteed. This makes notification loss a mandatory negative control rather than an unusual instrumentation problem. [S01]

The result is a usable specification for local agent sessions to implement and execute after Owner choices and independent preregistration review. Those sessions still have to collect the exact inventories, instantiate the cut points, run every applicable variant on disposable targets, return evidence and obtain independent acceptance. Section 11 gives the concrete execution handoff.

## 2 Evidence classes and source precision

Every consequential statement belongs to one of four classes:

- Source documented: a named primary source states the mechanism or limit. This does not show that the target build, adapter or device implements it correctly
- Locally observed: an authorized execution produced an independently inspectable trace for the exact pinned target. There are no such platform observations in this report
- Inferred: a proposed contract, oracle, risk consequence or test design derived from the cited mechanisms and the brief. All schemas, qualification rules and fixture designs below have this class
- Unverified: a target pin, deployment behavior, measured threshold, acceptance decision or open question lacks the required evidence

The source register records exact URLs, named standards or release tags, visible revision dates when available and retrieval date. POSIX references use Issue 8, IEEE Std 1003.1 2024. Kernel documentation is anchored to 6.12 for the documented semantics; systemd source is anchored to release tag v256. These are research reference editions, not recommended minimums or claims about the newest versions on 1 October 2026. Microsoft Learn and Linux man pages are live pages retrieved on that date; a visible page revision is not an immutable build pin. No unverified commit hash or host version is invented.

A future execution evidence bundle must preserve the exact source excerpts used, their capture dates and content digests, together with the exact tested binaries and configuration. The report's source register is sufficient to inspect the research propositions, but live documentation alone cannot retire a target unknown. The source register distinguishes the version pinned sources from retrieval pinned pages. POSIX pages that did not open directly were inspected through the official publisher's indexed text; their propositions are constrained to that visible text. This limitation is recorded rather than silently substituted with an older POSIX edition.

The report does not use vendor marketing or agreement among models as qualification evidence. A public issue report can motivate a trace but cannot replace normative API documentation or observed target evidence. The fixture catalog is deliberately a proposed behavioral specification, not executable product code.

## 3 The qualification object

### 3.1 Exact identity and fingerprint

The machine readable files accompanying this report are platform-manifest.schema.json, platform-manifest.json, negative-traces.json, profile-fields.json and source-register.json. Appendix A gives the normative schema. Every object rejects undeclared properties. Each identity field is an explicit fact with state known, unknown or not_applicable. Known facts carry a nonempty value and evidence references; unknown facts carry a reason and named retirement evidence; not_applicable facts carry justification and evidence. An empty value, null, zero, empty collection or omitted field never means unknown.

A pending row has a target_id such as pending:native_windows:01, pin_state pending, profile_key null and qualification unknown. The identifier is a synthetic manifest address, not a machine identity. The supplied rows deliberately contain no discovered host data. They are mandatory research cases awaiting inventory and an Owner scope decision.

For a pinned row, first project its identity by replacing each known fact with its exact value and each justified not_applicable fact with the literal object {"not_applicable":true}. Reject any remaining unknown fact. Wrap the projected object exactly as {"domain":"fu04-profile-identity-v1","identity":projected_identity}. Canonicalize this wrapper with RFC 8785 JCS, encode UTF8 and compute SHA256. The profile key is fu04-p1:sha256: followed by 64 lowercase hexadecimal digits. Provenance references and mutable review status are excluded from this fingerprint. A change to a value in the behavioral envelope creates a new key even when the old result looks relevant. JCS is an Informational RFC and is used here as a proposed deterministic encoding, not as a security certification. [S29]

All quantities in identity values use decimal strings plus the unit fixed by their field name or the documented value grammar. This avoids silent floating point truncation. Configurations too complex for one value are represented by a content digest of a separately retained normalized configuration artifact. That artifact's canonicalization and exclusions are part of the evidence. Do not store secrets, account identifiers, host names or actual workspace paths in the public manifest. A local private evidence index can map synthetic scope IDs to local resources without exporting that mapping.

For fields ending in _canonical, known.value is a string containing a JSON array serialized with JCS after UTF16 code-unit lexicographic sorting and duplicate rejection. The fingerprint preserves that string; it does not parse it into an array. Ordered policies, such as a Job nesting chain or storage stack, retain order in their separately digested configuration artifacts. Mount option defaults must be expanded to effective values. A word such as default, recent, latest, local or native is not an exact pin.

The physical profile key excludes fixture implementation, because the same target may be tested by several harnesses. Adapter artifact and adapter configuration are included because the adapter is part of the claimed behavioral envelope. Each execution result separately pins fixture version, harness digest, contract digest, adapter digest, variant, cut point, failure domain, repetition and seed. Comparing results across harness versions requires an explicit review, not a shared profile key alone.

### 3.2 What must be pinned

The schema enumerates the full identity rather than accepting a free form environment string:

- OS: family, edition, release, build, update revision, kernel release and binary digest, distribution and release, user space API or libc ABI
- Architecture: host, guest and process architecture, ABI, emulation, CPU model and microcode or firmware
- Execution layer: native or virtualized route, product and version, host and guest pins, virtual machine configuration, WSL package and distribution and configuration, compatibility runtime and version
- Filesystem: type, implementation version, format features, effective mount options and namespace, case mode, symbolic link or reparse policy, block and atomic write units, quotas and path route class
- Storage: locality, protocol and dialect, client and server versions, server filesystem and policy, transport options, caches, lease and lock policy, device/controller firmware, virtual disk and backing filesystem, write cache and flush/FUA contract, power loss protection and failure domain topology
- Terminal: host and backend names and versions, shell and version, console or termios modes, encoding, line discipline, dimensions, handle inheritance and embedded host version
- Supervisor: kind, version, effective configuration digest, restart and kill policies, stop timeout, startup gate, activation sources and identity policy
- Security: privilege class, token or capability set, MAC and seccomp policy, FIPS state, integrity or LSM mode, namespace configuration, policy engine and filesystem filter versions
- Containment: mechanism, version, scope type, creation membership method, Job nesting/flags and handle ownership, cgroup mode/controllers/delegation, namespace floor, migration and external service policies, resource limits
- Clock: deadline semantics, API, resolution, suspend accounting, reboot epoch policy and virtualized clock contract
- Adapter: native or wrapped execution route, upstream harness product/version/configuration and delegated-work boundary, contract and artifact/configuration digest, stable process identity method, lock and publication primitive, flush sequence

A security field describes the effective policy; it does not claim that FIPS mode improves process containment or qualifies storage. A package version cannot substitute for a kernel configuration or a seccomp allowlist. Missing introspection permission is an unknown observation capability, not proof the target lacks a feature.

### 3.3 Mandatory cases and expansion rule

The initial manifest contains eleven separate pending rows:

| Case | Required distinction | Initial outcome |
| --- | --- | --- |
| native_windows | Native Windows, exact edition/build/update and local storage stack | Unqualified |
| native_linux | Native Linux, exact distribution/kernel/config and local storage stack | Unqualified |
| wsl2_ext4 | WSL2 distribution filesystem on native ext4 virtual disk and its host backing stack | Unqualified |
| wsl2_mntc | WSL2 Windows mounted path route represented by /mnt/c, including host filesystem and translation | Unqualified |
| msys2 | MSYS2 runtime, shell/terminal and transition to native Windows children | Unqualified |
| git_bash | Git for Windows bundled runtime and terminal path, independently pinned | Unqualified |
| embedded_windows | Embedded terminal host on Windows, exact backend and lifetime ownership | Unqualified |
| embedded_linux | Embedded terminal host on Linux, exact PTY and host lifecycle | Unqualified |
| smb_windows | Windows SMB client, exact dialect/server/filesystem/cache/lease policies | Unqualified |
| smb_linux | Linux SMB client, exact client module/mount/server stack | Unqualified |
| nfs_linux | Linux NFS client, exact protocol/client/server/export/cache/lock settings | Unqualified |

These are coverage categories, not a supported product matrix. Other proposed clients, including an NFS client on Windows, require their own rows if brought into scope. A combination, such as an embedded Windows terminal launching WSL2 while using SMB storage, gets an additional composite profile; none of the component rows automatically qualifies it. Each selected architecture, filesystem, terminal route, supervisor policy or security mode expands the relevant case into a distinct profile. The Owner may explicitly exclude a category, but its mandatory row remains with the recorded exclusion and a rejected/unsupported policy outcome; it is never quietly removed.

Microsoft distinguishes Windows and Linux filesystem routes and exposes WSL configuration affecting automount behavior. MSYS2 identifies its compatibility environment separately from native Windows toolchains. Git for Windows is a separate packaged product. These documented distinctions justify asking for precise profiles; they do not establish any tested behavioral equivalence or superiority. [S24, S25, S26, S36]

### 3.4 Structural schema and semantic validation

JSON Schema checks shape, explicit states, required fields and result vocabulary. The following semantic checks are equally normative and must run before any acceptance decision:

1. All eleven mandatory case categories are present; every in scope composite route has its own row
2. pending requires null profile_key and unknown qualification unless Owner-excluded; pinned requires resolved identity and a matching recomputed fingerprint
3. Qualified implies candidate_in_scope, every applicable obligation accepted with the same profile key and contract digest, no unresolved contradiction, and independent accepted review
4. owner_excluded requires a nonempty owner_decision_ref and rejected/Rejected; pending pins and null profile_key are permitted because this rejects scope, not behavior. Other rejections require a witnessed violation or conclusive unsupported capability; missing access alone is unknown
5. Unknown implies display_status Unqualified; qualified and rejected map to Qualified and Rejected respectively
6. Every result reference resolves to a retained artifact whose bytes match its digest. A local evidence reference is not a public URL and does not authorize uploading the artifact
7. No skipped fixture silently satisfies an obligation. A not applicable fixture needs a reviewed applicability argument; a needed but unavailable mechanism is unsupported or unknown, depending on the evidence
8. Quantities, sampling windows, repeat counts, timeout budgets, error allowances and destructive fault domains are fixed before execution; changing them produces a new preregistration digest
9. No effective configuration drift occurs between inventory, execution and recovery. Drift invalidates the result for qualification and creates an unknown requiring a new pin
10. A result stating execution_settled true cannot contain unknown or false mandatory settlement predicates under the selected contract

The manifest stage advances from proposed_unexecuted through preregistered and executed_pending_review to accepted. The initial manifest is valid as a pending research manifest; proposed_unexecuted structurally requires an empty results array. Its empty results array means no local fixture was run. It must never be rendered as a zero failure result or a zero duration run.

## 4 Observation and recovery contract

### 4.1 Evidence envelope

Every trace produces an append only observation stream with a synthetic run ID, execution epoch, observer epoch, fixture and cut point IDs, event source, monotonic sequence number, clock identity and timestamp, native operation/result/error, stable process identity where relevant, and evidence artifact digest. Sequence gaps, buffer overrun, observer restart, inaccessible state and clock discontinuity are explicit records. When an observer dies before it can report a gap, the independently observed observer death makes completeness unknown.

The ledger is an evidence format proposal, not a selected persistence backend. An independent witness outside the target fault domain records barrier arrivals, injection request and confirmation, externally observed acknowledgments and watchdog stop. When physical power is interrupted, a witness sharing the interrupted power supply is not independent. When the network is cut, a witness communicating only through that network cannot establish the far side's last durable point. Witness placement is part of the failure topology pin.

Every important time point has a semantic label: request received, native operation begun, native operation returned, effect observed, commit claimed, commit externally acknowledged, crash injected, crash confirmed, recovery begun and recovery observation complete. A timestamp is evidence of order only within the named clock/epoch and uncertainty bounds. If ordering matters across hosts, use explicit causal barriers or a documented uncertainty interval; wall time alone is insufficient.

### 4.2 Five predicates that must not collapse

transport_closed means an identified transport endpoint returned its documented end of stream or terminal error, with the source and direction recorded. Local voluntary close is a different cause from peer close. The predicate says nothing by itself about remaining writers, a shell, a Job or a cgroup.

client_disconnected means a specific client session no longer has the connection identified by its connection epoch. The terminal host and the worker can outlive it. For ConPTY, output closure caused by the pseudoconsole can support the documented all clients disconnected condition, provided unrelated duplicated handles and local closure are ruled out. A ClosePseudoConsole return alone does not support it. [S04, S37]

containment_empty means an authoritative native query for the exact scope finds no live member under the scope's documented semantics, after admission is closed or fenced. A poll is a snapshot, not a proof of future emptiness. Linux cgroup.events populated concerns live processes in the subtree; a separate population query and stable identity evidence are needed to interpret it correctly. A successful cgroup.kill write requests scope termination; it is not a bounded time completion certificate. A Job active process count and associated native enumeration must be reconciled, not inferred from a missing completion packet. [S01, S05]

process_exited means the held native identity's terminal state was observed, and an exit status was collected when the platform and relationship permit it. A PID reused by another process must not satisfy or negate this predicate. A readable pidfd can establish terminal state under its documented semantics; collecting wait status for a nonchild has separate restrictions. On Windows, preserve the original process handle through exit observation rather than reacquiring a process solely by numeric PID. [S07]

execution_settled is the application contract's conjunction: admission fenced; all required captured work terminal or a reviewed explicit scope exception; target scope empty; terminal output either completely drained or explicitly truncated under the selected policy; stable accounting finalized with completeness status; resource ownership reconciled; canonical outcome committed under the chosen durability domain; and recovery policy unable to reanimate a stale execution. It is not an operating system primitive. This conjunction is an inferred acceptance rule. If one required predicate is unknown, settled remains unknown, even when the user interface has disappeared.

### 4.3 Recovery oracle

Recovery starts in a fresh observer epoch with the target namespace and admission path fenced. The recovery record resolves the intended execution identity, native handles or surviving scope, current canonical generation, pending/committed operations, retained output boundary and current supervisor state. It explicitly compares the recovered state with independently witnessed acknowledgments. A successful restart is not a recovery oracle.

For each acknowledged operation, the oracle identifies one authoritative outcome under the selected durability contract. For unacknowledged operations, it may identify committed, not committed or unresolved, without inventing a retry. A crash after an effect but before a response is a possible ambiguous outcome. Reconciliation precedes retry when repeating an effect could duplicate work. A failure of evidence collection produces unknown rather than permission to delete an ambiguous artifact or kill an unverified PID.

### 4.4 Common stop rules

Every fixture inherits three stop classes. Safety stop halts injection and quarantines the disposable target when a boundary is crossed, an unrelated process/storage object is affected, the independent observer loses safe control, or physical apparatus is unsafe. Witnessed contract violation stops that cell as rejected and preserves the minimal failing trace. An observation deadline with missing evidence stops the run as unknown, unless the contract itself requires completion within that deadline and the independent watchdog proves a genuine deadline violation, in which case it is rejected.

A successful cell stops only after every preregistered cut point, variant and repetition is complete, both observation and recovery oracles pass, cleanup is verified and independent review accepts the evidence. Cleanups are logged as actions after the observation boundary; they cannot retroactively improve a failed recovery state. All time and volume budgets are named preregistration parameters, not arbitrary values chosen after a hang.

## 5 Primary mechanisms and their limits

### 5.1 Windows process containment and identity

PROC_THREAD_ATTRIBUTE_JOB_LIST assigns the requested Job list during process creation; Microsoft documents support from Windows 10 and Windows Server 2016. Microsoft's explanation states that assignment occurs before the initial thread runs. This removes the child running before a later assignment window, but does not make the control plane's registration durable. A creator can die after native creation and before recording the result. Both facts are independently tested. [S02, S03]

Default CreateProcess inheritance, breakaway flags, nested Jobs, last handle closure and service created processes must be represented explicitly. The Job documentation specifically excludes Win32_Process.Create spawned children from normal inheritance. Kill on last Job handle close is conditional on the actual last handle, so leaked or inherited handles are a required negative control. A Job is a native management scope, not proof of every causal descendant. [S01, S32]

The candidate contract therefore separates stable native process identity, membership at first runnable instruction, registration evidence and recovery ownership. The competing option is creation suspended followed by assignment and controlled release; its decisive test is the parent death window with an independent witness. This report chooses neither a process library nor an implementation route.

### 5.2 Linux creation and containment

clone3 with CLONE_INTO_CGROUP can place a new process into a specified cgroup v2 at creation; its documented introduction is Linux 5.7 and the ordinary permission and membership restrictions still apply. A capability's introduction is not a support floor. seccomp, delegation, cgroup type and namespace policies can prevent its use on a later kernel. [S06]

The 6.12 cgroup v2 documentation states that cgroup.kill targets processes in the affected cgroup subtree with SIGKILL, handles concurrent forks and protects the operation against migrations; it does not operate on a threaded cgroup. These properties do not capture a process that escaped before the operation or work requested from an external service. Pending fatal signals and uninterruptible operations can delay exit, so the suite observes emptiness separately. memory.high, memory.max and memory.events have different meanings; their use is addressed in Section 8. [S05]

A process group, session or parent PID walk is a competing membership mechanism for a weaker contract, not an interchangeable substitute for cgroup membership. pidfds address stable reference and exit observation for a process. The pidfd_open documentation qualifies when acquiring a descriptor after fork remains safe against PID recycling; CLONE_PIDFD is the alternative when those conditions do not hold. The fixture includes both acquisition and recovery races. [S07]

### 5.3 PTY and ConPTY

A Linux PTY consists of an asynchronously interacting manager/subsidiary pair with terminal processing on the subsidiary side. Terminal characters can cause signals to its foreground process group under configured line discipline. Neither PTY closure nor a terminal hangup is a complete work termination mechanism. The profile therefore pins session leadership, foreground group and termios state and observes native process and scope state separately. [S20]

ConPTY uses synchronous communication channels. Microsoft's creation guidance warns that serving channels on a single thread can deadlock and calls for careful reference ownership so broken channels can be detected. The close behavior changes at the documented build boundary noted above. The design obligation is independent drain/close and observation progress, not a choice of threading library. [S37, S04]

GenerateConsoleCtrlEvent targets processes sharing the caller's console; CTRL_C_EVENT cannot be limited to a nonzero process group in the way its signature might suggest. CTRL_BREAK_EVENT and the console sharing rules must be tested explicitly. A reported successful call is not confirmation that a particular process exited. [S16]

### 5.4 Publication and flushing

POSIX rename specifies namespace behavior; Issue 8 separately describes cache transfer and crash behavior. Atomic directory operations are not automatically durable. The Issue 8 rationale explicitly distinguishes synchronizing a replacement file from synchronizing its directory and notes that multi directory operations complicate crash states. The normative cache text permits partial transfer of multi unit operations before a crash. Therefore a same directory single file replacement is a different claim from a multi file commit or cross directory transaction. [S13, S14, S15]

Linux fsync documents that flushing a file does not necessarily persist the containing directory entry; an explicit directory fsync is needed. renameat2 introduces optional behaviors such as NOREPLACE and EXCHANGE with filesystem dependent support. Neither flag creates a portable multi file durable transaction. Cross filesystem rename can fail with EXDEV and is a required negative trace, not a cue to silently replace the contract with copy plus delete. [S11, S12]

ReplaceFileW requires the replacement, original and backup to be on the same volume and documents several failure states that can leave names or attributes changed. Its REPLACEFILE_WRITE_THROUGH flag is explicitly unsupported. FlushFileBuffers documents file buffer flushing and handle requirements; it does not supply a universal POSIX directory fsync equivalent or a universal power loss proof for every Windows filesystem. The Windows publication sequence and recovery states remain target obligations. [S08, S09]

### 5.5 Locks and supervision

LockFileEx does not prevent reading or writing through a mapped view. Its documentation says locks are released on termination or close but that release may be delayed by resource availability. Linux process associated record locks and open file description locks have different lifetime rules; an unrelated close within a process can release its process associated locks, while open file description locks follow the last reference. The chosen primitive must be pinned and tested, rather than hidden behind the word lock. [S10, S21]

In systemd v256, KillMode changes whether termination affects the control group, only the main process or nothing, and SendSIGKILL and stop timeouts modify completion. The service restart policy has separate triggers and exceptions. Windows SCM documentation warns that an already queued restart cannot be canceled and can restart a manually started then stopped service; explicit disabling is required to prevent that documented race. These are sources for fixture variants, not authorization to modify real services. [S27, S28, S23]

## 6 Preregistered negative trace catalog

### 6.1 Shared fixture protocol

Every fixture below is an unexecuted design, classified inferred. A local session must supply a fixture implementation with the same barriers, a reviewed adapter mapping to native calls, and a digest of the resulting executable and configuration. The word execute in this section describes that future local session, not work performed for this report.

The common actors are an independent controller C, a broker or writer under test B, a root worker W, bounded children D1 and D2, and an observation witness E outside the injected fault domain. A fixture creates only synthetic work and synthetic content in an explicitly disposable scope. All actors use stable run and process identities. Content records carry an integer generation, length and digest; generation A and generation B have distinct nonuniform byte patterns so zeros, torn writes and stale content cannot pass accidentally. The witness stores exact expected bytes or their verified digests before injection.

The common barriers are prepared, native_begin, native_return, effect_observed, registration_begin, registration_committed, acknowledgment_observed, injection_confirmed and recovery_observed. Fixture specific barriers below extend this set. A barrier used to position injection must be independently confirmed; merely sleeping for a duration does not demonstrate the intended race. If a cut point cannot be reached or distinguished, that cell is unknown rather than counted as a pass at a nearby point.

Before running, freeze the finite variant list, cut point list, seeds, repetitions, maximum resource allocations, watchdog timeout, drain limit, recovery horizon, observation cadence and allowed outcome set. These numeric choices are Owner or experiment protocol inputs, not measured values supplied by this report. Every named cut point needs at least one confirmed injection; repetition counts and confidence goals require explicit preregistration. Random stress supplements, but cannot replace, deterministic barrier coverage. Each catalog entry inherits the evidence envelope, common stop rules and independent review gate in Section 4.

### PF01 Descendant escape and causal work completeness

Prerequisites: a disposable native scope, direct launch plus one nested child, stable process identities, independent actor registration, and a declaration of which privileges and external services the worker may use.

Injected fault: after W reaches first runnable instruction, D1 repeatedly creates D2 while C requests termination. Separate variants attempt explicit and silent Windows breakaway, a Linux migration out of the delegated subtree before kill, setsid or a new process group, nested Job/cgroup creation, and a synthetic external service creating work on request. The privileged migration variant runs only in a disposable privileged test target; it must not grant those privileges to a production worker. A denied attempt is an observed outcome, not a skipped variant.

Observation oracle: E records every actor's requested creation, native identity, first execution and observed scope membership. C records effective permissions and actual result codes. The negative control deliberately permits an escape or external-service launch and must cause descendant_capture_complete to become false or unknown while scope_membership_complete may remain true. Killing a scope cannot make those two values equal by definition.

Recovery oracle: close or fence admission, enumerate the exact managed scope, reconcile all registered actors and service receipts, and establish which actors terminated, survived or cannot be located. Preserve surviving out of scope actors as a contract failure when their capture was promised; clean them only through the separately approved harness cleanup identity.

Stop condition: any actor running outside a promised captured boundary rejects that completeness claim. Any unrelated process affected triggers safety stop. Loss of actor or scope visibility yields unknown. Native mechanisms: S01, S05, S06, S32.

### PF02 Parent death before registration

Prerequisites: C independently observes native creation and durable registration barriers; W cannot perform external work before the admission gate is released.

Injected fault: kill B separately before native creation; after creation begins but before it returns; after creation returns but before registration; during registration; after registration commits but before acknowledgment; and after acknowledgment but before normal supervision starts. For a proposed suspended creation sequence, add death before assignment and before resume. For creation-time membership, confirm W's first execution occurs within the scope even if B dies.

Observation oracle: native creation result, stable process handle or pidfd, first instruction membership witness, registration commit witness and external acknowledgment must be separable. A missing response is not proof no child was created. The negative control intentionally opens the create-then-register gap and confirms that the oracle can see the orphan or unresolved launch.

Recovery oracle: a new B epoch reconciles registered intent, actual scope contents and live process identities, then either adopts a still authorized execution or terminates it under the selected policy. It must not release two workers for one intent, launch a replacement before resolving the first launch, or report not_started solely because the registration record is absent.

Stop condition: an unfenced worker performs work, two active executions are admitted, or the recovery policy loses a witnessed child: rejected. Unobservable creation/commit order: unknown. Failure to restore safe admission control: safety stop. Mechanisms: S02, S03, S06, S07.

### PF03 Last handle and scope lifetime

Prerequisites: explicit ownership inventory for Job handles, pidfds, inherited descriptors and any monitor references; a test process deliberately retains one extra reference.

Injected fault: crash B while another actor retains a duplicated or inherited Job handle. Compare with a variant in which B holds the last Job handle under kill-on-close. On Linux, kill the manager without explicitly killing the cgroup, then compare with the selected supervisor cleanup path. Hold a terminal descriptor open after W exits in another variant.

Observation oracle: E captures reference ownership transfers, native member state and termination events. Broker death must not be inferred to mean last-handle closure or cgroup destruction. The intentionally retained reference must remain visible to the oracle and prevent premature settled status.

Recovery oracle: determine whether the scope survived, whether its identity can be reattached safely, and whether cleanup killed only owned members. Releasing observer references happens after the evidence window so the observer itself does not cause an apparent successful kill-on-close result.

Stop condition: settlement while a required actor survives rejects; inability to distinguish which handle kept the scope alive yields unknown. Harness cleanup causing an effect before it was observed invalidates that cell. Mechanisms: S01, S32, S05, S37.

### PF04 Undrained terminal teardown

Prerequisites: W writes numbered output records faster than the consumer drains; C confirms actual backpressure rather than assuming a pipe capacity. An independent watchdog and independent exit observer remain responsive.

Injected fault: stop the output consumer at output_blocked, then close the terminal host or invoke the native terminal teardown. Run separate policies that continue draining, deliberately truncate by closing output, and crash the terminal client. Run distinct Windows pre26100 and 26100-or-later profiles only if the Owner includes them; distinguish each supported embedded host and PTY route.

Observation oracle: record the teardown call begin/return, each endpoint's close cause, last complete output sequence and count, process exit evidence and scope emptiness. The consumer cannot be the only observer of the call that can block it. Intentionally retain a duplicated output writer in a negative control. Output closure caused by the harness is labeled local_close, never promoted to all_clients_disconnected.

Recovery oracle: reconcile bounded output retention with the selected loss policy and current scope/process state. A drained terminal has no missing acknowledged records; a deliberately truncated terminal has an explicit loss boundary and reason. Either may still have unsettled process work.

Stop condition: watchdog-confirmed violation of the chosen bounded teardown contract rejects; lost watchdog or uncertain blocking point yields unknown. Unbounded memory growth while buffering triggers safety stop. Mechanisms: S04, S20, S37.

### PF05 Signals and console event scope

Prerequisites: W, D1 and an unrelated sentinel have distinguishable signal handlers and independent heartbeat evidence. Pin terminal foreground group/session and console sharing.

Injected fault: send the chosen graceful cancellation signal/event while D1 ignores it; place D2 in a different process group or console; separately close the terminal transport. Test CTRL_C_EVENT with a nonzero group as an explicit Windows misuse negative control, CTRL_BREAK_EVENT under correct console scope, and Linux foreground/background groups with configured terminal modes.

Observation oracle: record API return, handler receipt, continuation heartbeat, native exit and final forced termination as distinct events. The unrelated sentinel must remain unaffected. A successful signal request cannot stand in for recipient acknowledgment or process exit.

Recovery oracle: after the graceful deadline, the selected escalation policy targets stable owned identities or scope membership, then verifies emptiness and terminal retention. Any actor beyond the declared signal scope is explicitly accounted for rather than silently treated as signaled.

Stop condition: wrong-target delivery or unrelated sentinel death is a safety stop and failed contract. Failure to exit within a promised escalation horizon rejects only when observer completeness is proven; otherwise unknown. Mechanisms: S16, S20, S05.

### PF06 Atomic replacement crash cuts

Prerequisites: preexisting generation A, prepared generation B of different size and digest, observer reads that reopen the authoritative name, and complete same-filesystem/volume route evidence.

Injected fault: crash the writer before file flush, after file flush, immediately before replacement, during replacement, after replacement returns, before directory or selected metadata durability step, and after that step before acknowledgment. Include same-directory, cross-directory, cross-filesystem, existing-reader handle, permission-denied and antivirus/filter interference variants where in scope. Windows failure codes with documented partial name states have explicit expected reconciliation branches.

Observation oracle: live reopening readers see only states permitted by the selected namespace contract. Preserve native return/error and all relevant names, file IDs, contents, attributes and generations. Readers holding the old file open are interpreted separately from readers reopening the name. No copy-plus-delete fallback may impersonate a successful atomic operation.

Recovery oracle: before repairing anything, inventory the original, replacement and backup names and contents, then select or quarantine according to the preregistered algorithm. The witness's acknowledged generation must be recoverable if the selected failure domain promises it. An unacknowledged operation may have completed; recovery must not equate a lost response with no effect.

Stop condition: torn/mixed canonical content, a forbidden live namespace gap, or loss of an acknowledged required generation rejects. A documented partial error state handled safely may pass its explicit error contract. Unknown crash ordering remains unknown. Mechanisms: S08, S09, S11, S12, S13, S14, S15.

### PF07 Failure domain and power interruption

Prerequisites: a disposable target; separately powered witness; exact virtual/physical storage/cache topology; approved interruption apparatus; a recoverable test image and written safety procedure.

Injected fault: repeat PF06's durability-relevant cuts separately for abrupt process death, guest reset, host reset and actual physical power interruption of the named devices. A graceful shutdown is a control, never the injected crash. For network storage, separately interrupt client power, server power and the declared shared power domain.

Observation oracle: E records which power/reset domain actually failed, the last externally witnessed acknowledgment, and evidence that the interruption occurred without a graceful flush path. Device/controller protection and cache behavior are recorded as pins or unknowns. A simulated controller flush failure is a separate synthetic fault, not a physical-power result.

Recovery oracle: boot or remount through the frozen recovery procedure, retain the first observed bytes before repair, verify generation and digest, and check application consistency and namespace state. A filesystem checking clean does not establish that the application's acknowledged state survived.

Stop condition: any promised acknowledged generation lost or application invariant broken rejects that exact domain. Apparatus uncertainty or inability to inspect the first recovery state yields unknown. An unsafe device, shared production volume or unapproved destructive boundary triggers safety stop. Mechanisms: S11, S14, S30, S33, S34, S35.

### PF08 Lock lifetime and mapped bypass

Prerequisites: two cooperating writers, an independent collision detector, the exact lock primitive/range, and a separate mapped-view actor for the Windows bypass control.

Injected fault: terminate the lock owner; close a different descriptor to the same Linux file; retain a duplicate open-file-description reference; request a conflicting lock while release is delayed; and perform mapped-view access while LockFileEx protects the corresponding range. Network variants also interrupt lock ownership/reclamation.

Observation oracle: record acquisition completion rather than mere asynchronous submission, the native result/error, competing write attempts, actual overlapping writes and owner identity. A stale lock file's existence is recorded separately from a currently enforced native lock. The mapped bypass control must be detected as outside the primitive's protection.

Recovery oracle: a new owner attempts real lock acquisition under a bounded policy, verifies fencing epoch and canonical consistency, and only then resumes. It must not delete a lock marker or assume authority merely because a PID is absent or an elapsed timeout expired. A retained valid reference prevents a premature ownership transfer.

Stop condition: two admitted writers or a false exclusivity claim rejects. Release latency beyond a promised bound rejects when proven; no visibility of current server lock ownership yields unknown. Mechanisms: S10, S21, S33.

### PF09 PID reuse and stale process identity

Prerequisites: a disposable process namespace or equivalent safe harness, a stale identity record, a new unrelated sentinel and held original native identity references.

Injected fault: let the original process exit and be reaped, then obtain a reuse of its numeric PID through controlled bounded churn or a permitted deterministic namespace facility. Deliver delayed exit, cancellation and recovery messages carrying the stale execution epoch. Also test acquiring pidfd after an unsafe reaping window.

Observation oracle: distinguish original process handle/pidfd and creation epoch from numeric PID. The oracle requires proof that reuse actually occurred; exhaustion of the churn budget without reuse is an untriggered cell, not a pass. The negative control uses PID-only targeting and must identify the wrong-target hazard without affecting real processes.

Recovery oracle: stale messages cannot affect or settle the new process. Recovery reattaches only when stable identity matches or records unknown and quarantines admission. No broad kill by name or PID enumeration is an acceptable cleanup shortcut.

Stop condition: stale cancellation reaches the unrelated sentinel or stale exit settles a new execution: rejected and safety stop. Failure to trigger reuse or resolve identity: unknown. Mechanism: S07; Windows handle preservation is a proposed identity requirement subject to native adapter verification.

### PF10 Disk full quota and delayed write failure

Prerequisites: a disposable bounded filesystem or quota domain that cannot fill the host's system disk, old generation A, independent error logging capacity and a frozen publication sequence.

Injected fault: exhaust byte space, inode space or quota independently between content write and flush; inject a short write; surface delayed EIO at flush; deny metadata update during replacement. Windows variants separately capture disk-full, quota and native flush/replacement errors rather than guessing a POSIX mapping.

Observation oracle: every write has requested and actual lengths; every flush and rename/replace has its own result. The acknowledgment witness must show no success claimed merely from a completed buffered write. Capture whether error reporting itself failed because its storage was full.

Recovery oracle: preserve A or a fully validated B under the selected contract; never accept a truncated B because a name exists. Reconcile pending intent without duplicating externally visible work. Restore space only after recording the failing state and distinguish restored capacity from successful recovery.

Stop condition: false durable acknowledgment, torn canonical data or unbounded retry rejects. Loss of independent error evidence produces unknown; spillover to nondisposable storage triggers safety stop. Mechanisms: S31, S11, S08, S09.

### PF11 Memory throttling without automatic death inference

Prerequisites: bounded synthetic allocation workload, a private Linux memory controller domain, baseline hierarchical and local counters, pinned swap/reclaim policy, and controller/witness headroom.

Injected fault: drive the workload across memory.high while keeping the hard cap and independent host limits safe; separately impose CPU or I/O throttling to check that the classifier does not confuse stalled progress with memory failure.

Observation oracle: correlate native throttle counters, progress cadence, allocation outcomes and live process/scope observations. Report throttle even if the execution later exits normally. A counter delta is interpreted against baseline and hierarchy, not as an event unique to W merely because it was read nearby in time.

Recovery oracle: after removing only the test pressure according to the preregistration, determine whether work resumes, remains throttled, fails allocation or requires cancellation. Do not respawn an execution still running under pressure and do not bill throttled wall time as CPU consumption.

Stop condition: a portable OOM classification without supporting subtype evidence rejects the classifier. Host pressure escaping the disposable domain is a safety stop. Counter or clock coverage loss yields unknown. Windows has no assumed memory.high equivalent; any substitute is a separately scoped experiment. Mechanisms: S05, S32.

### PF12 Memory refusal process kill and group kill

Prerequisites: safe headroom outside the target scope, native counter snapshots, selected per-process/group limits and explicit OOM group policy. Pin protections/exemptions and external OOM policy agents.

Injected fault: hit Linux memory.max under individual and group policies; provoke a bounded allocation refusal path; hit Windows per-process and Job committed-memory limits. A separate harness policy may terminate after a refusal, but its kill must be labeled harness-policy termination rather than native limit behavior.

Observation oracle: record allocation API outcomes, native memory events and process identities, which members died, surviving members and whether the controller caused the death. The classifier can emit multiple chronological outcomes, such as throttle then process_kill. It cannot infer group kill from one exit or infer an allocation success from missing notifications.

Recovery oracle: account for survivor state and incomplete work before replay; an isolated killed child cannot leave a parent silently committing a partial result. A refusal that was handled successfully does not automatically require replay. Group cleanup and canonical settlement are verified separately.

Stop condition: incorrect subtype, unexplained lost members or duplicate retry while survivors run rejects. Global OOM outside the authorized scope is a safety stop. Ambiguous cause of death remains unknown. Mechanisms: S05, S22, S32.

### PF13 Supervisor restart and stale owner race

Prerequisites: isolated test service/unit, frozen restart policy and activation sources, synthetic writer authority epoch and independent supervisor logs.

Injected fault: crash B just before and after ownership registration, race automatic restart with manual start/stop, and deliver an old owner's delayed completion after a new owner starts. For Windows include the documented queued SCM restart sequence. For systemd include selected KillMode, timeout and restart policies, plus another activation source if configured.

Observation oracle: record every supervisor launch request, execution epoch, stable process identity and admitted writer authority. Service state stopped or active cannot replace native scope evidence. Deliberately retain an old child as a negative control so a new service process cannot make it disappear from accounting.

Recovery oracle: exactly one authorized owner may admit work for the intended generation, old epochs remain fenced and all pending restart/activation sources are reconciled. If a restart cannot be prevented under the selected policy, the startup gate must refuse stale work rather than claiming the supervisor is quiescent.

Stop condition: dual ownership, stale completion accepted or uncontrolled resurrection rejects. Editing an unrelated service is a safety stop. Missing activation or queued-action visibility produces unknown, not quiescence. Mechanisms: S23, S27, S28.

### PF14 Suspend resume and deadline semantics

Prerequisites: Owner choice between elapsed-time and active-time deadline semantics, identified clocks, external elapsed-time witness, boot epoch and explicit suspend/hibernate/VM pause variants.

Injected fault: suspend across a deadline; resume after it; change wall time separately; reboot with a persisted deadline; pause/resume a guest separately from host suspend. Capture each supported sleep state as a distinct variant.

Observation oracle: compare pre/post readings and explicit suspend/resume events, accounting for clock resolution and measurement uncertainty. Linux CLOCK_MONOTONIC excludes suspended time while CLOCK_BOOTTIME includes it. Windows unbiased interrupt time excludes sleep/hibernation; other chosen clock behavior must be pinned rather than assumed equivalent. Record the deadline's intended semantics before running. [S19, S17, S18]

Recovery oracle: expire once when elapsed semantics require it, or retain the correct remaining active budget when active semantics require it; after reboot reconcile the deadline using the approved epoch policy. A persisted monotonic number from an old boot cannot be treated as a current deadline without conversion evidence.

Stop condition: missed or duplicate expiration outside preregistered tolerance rejects; a wrong clock or uncertain pause domain yields unknown. Any action on the real system clock outside the disposable target triggers safety stop.

### PF15 Network storage interruption and ambiguous commit

Prerequisites: isolated client/server test share/export, exact protocol and cache/lease configuration, independent client and server witnesses, no production traffic on the fault path.

Injected fault: drop request before server receipt; drop response after server effect; cut connectivity during write, flush, replacement and lock renewal; restart server; recover with both retained and lost server volatile state. Distinguish SMB durable/persistent handle reconnect from ordinary reopen, and NFS verifier/COMMIT and lease recovery variants.

Observation oracle: capture request identity, protocol result when available, server evidence, client error and first authoritative post-reconnect state. A timeout is neither not_committed nor committed. A client page-cache read after reconnect is not automatically a server recovery observation.

Recovery oracle: verify generation/content against independent acknowledgment; detect changed server identity/verifier or lost locks; reacquire authority through the approved fencing protocol before writes resume. Reissue only when the application's operation identity and semantics make repetition safe. A durable handle is not by itself proof of durable application content.

Stop condition: conflicting writers, duplicate nonidempotent publication, false durability claim or forbidden acknowledged data loss rejects. No independent server observation or unconfirmed partition point yields unknown. Mechanisms: S33, S34, S35, S10, S12.

### PF16 Lost duplicated and reordered notifications

Prerequisites: an observation transport where the harness can drop, delay, duplicate and reorder only synthetic notifications, while independent native queries remain available.

Injected fault: remove a process exit notification; deliver it twice or after the next execution epoch; overrun an observation buffer; restart the observer while a worker exits; delay Job completion packets and cgroup event reads.

Observation oracle: sequence/epoch checks detect duplicates and gaps; authoritative native state resolves what it can; loss of observation coverage is explicit. The negative control removes a notification and must not produce the claim that the event never happened.

Recovery oracle: reconcile native identities, canonical record and final accounting. If the event's exact time or cause cannot be reconstructed, retain that unknown even when eventual process death is established. Do not manufacture a timestamp or attribute a counter delta to the wrong execution.

Stop condition: silent gap, false success, stale event accepted or unknown converted to zero rejects. Recovery deadline with genuinely insufficient evidence yields unknown. Mechanisms: S01, S05, S07.

### PF17 Compatibility path and embedded host boundary

Prerequisites: a separate instance of every selected MSYS2, Git Bash, WSL and embedded-terminal profile; synthetic filenames and arguments; native child probes with exact expected bytes.

Injected fault: launch native children through the compatibility shell; use spaces, Unicode, leading dashes and case collisions in synthetic names; cross a WSL native/Windows mount boundary; terminate the embedded host while retaining the broker. Include environment/path translation and terminal reconnect variants only where the selected adapter uses them.

Observation oracle: compare exact arguments, path identities, resulting filesystem route, terminal ownership, process scope and exit evidence. A successful shell command is not proof that the intended native binary or storage route was exercised.

Recovery oracle: preserve the same execution identity and canonical data route or reject unsupported reconnect. Host closure must not silently change cancellation, output loss or persistence policy. Qualification belongs to the composite path actually observed.

Stop condition: unintended binary/path, accidental profile substitution, lost work hidden by terminal closure or inherited native qualification rejects. Unknown translation or inaccessible host lifecycle remains unknown. Mechanisms: S24, S25, S26, S36, S37.

### PF18 Permission and feature denial

Prerequisites: disposable policy variants with exact security/configuration digests; explicit authorization for every local privilege or policy change.

Injected fault: deny Job assignment, cgroup creation/delegation, clone3, pidfd access, lock acquisition, replacement or flush. Provide an unavailable kernel/API feature variant and a present-but-policy-denied variant. No test disables production protections.

Observation oracle: native denial code, effective policy and absence or presence of partially created work are recorded. The adapter must not silently fall back to a weaker containment, identity or durability guarantee while preserving the stronger profile label.

Recovery oracle: reconcile partial resources, keep admission closed where the promised guarantee is unavailable, and report unsupported for a demonstrably unavailable required feature or unknown for insufficient access to establish capability. The original failing evidence is retained even if a later approved profile change resolves it.

Stop condition: undeclared fallback or work released outside the promised policy rejects. Unapproved privilege escalation is a safety stop. Mechanisms: S02, S06, S07, S08, S09.

### PF19 Resource accounting completeness

Prerequisites: W and short lived children have bounded known synthetic workloads, native cumulative counter baselines, stable scope identity and independent observation of child creation/exit.

Injected fault: let a child run and exit between sampling intervals, kill the parent first, migrate a process where authorized, lose one counter sample and reset/recreate the scope. Separately retain output after process exit so transport lifetime exceeds compute lifetime.

Observation oracle: report counter source, units, aggregation boundary, sampling interval and reset semantics. Distinguish native scope cumulative accounting from samples summed across PIDs. The sum of individual lifetime memory peaks is not a simultaneous group memory peak. Scope membership completeness and descendant capture completeness remain independent tri-state fields.

Recovery oracle: return bounded or unknown accounting where a delta cannot be recovered, preserve terminal costs separately from compute, and prevent zero substitution for a missing counter. Reusing a scope name cannot splice two counter epochs into one charge.

Stop condition: double count, counter reset read as negative usage, incomplete capture represented as exact or missing value represented as zero rejects. Unavailable native metrics remain unknown and block only claims requiring them. Mechanisms: S01, S05, S22.

### PF20 Combined failures and oracle controls

Prerequisites: all component fixtures have independent evidence and the combined variant list is preregistered. The combined target uses its own exact composite profile.

Injected fault: combine output backpressure with supervisor crash; disk-full with writer death; memory pressure with observer restart; network response loss with lock-owner restart; and suspend/resume with cancellation at the deadline. Also run no-fault controls and intentionally faulty adapters for false settlement, omitted flush, PID-only identity and notification-only completion.

Observation oracle: each combined fault has its own confirmation and causal order. The intentionally faulty controls must fail the corresponding oracle. A detector that never flags its known-bad control cannot qualify a good-looking run.

Recovery oracle: settlement requires all relevant terminal, containment, ownership, accounting and durability predicates, without letting one recovered component mask another unresolved component. Preserve the first failure rather than averaging success and failure repetitions.

Stop condition: any violated mandatory invariant rejects; an ineffective fault or insensitive oracle invalidates the cell as unknown. Combined testing does not prove all possible interleavings or substitute for component coverage. Mechanisms: the sources for the component fixtures; the combination design is inferred.

## 7 Containment and durability assertions

### 7.1 Permitted containment statement

The maximum statement supported by a successful native scope termination fixture is: all processes remaining within the named managed scope, under the pinned admission and migration policy, reached the required terminal state within the verified observation horizon. This statement is narrower than complete descendant-tree capture. It does not cover earlier escape, privileged migration outside the scope, service-created work, remote work, a separately scheduled task or a process never observed at creation.

Complete descendant capture is a separate product claim needing a declared causal boundary. A genealogy model based on parent PID alone cannot describe work submitted to a service. A complete capture claim therefore needs the allowed service routes and identity receipts or an enforced prohibition on such routes. Unrestricted administrator authority or an unrestricted external service creates a boundary the proposed local scope contract cannot honestly contain. The Owner can choose a weaker declared contract, a restricted worker policy or an additional external-work accounting contract; this report chooses none.

A proof of membership at one moment is not proof of membership since creation. A proof of emptiness at one moment is not proof that the scope cannot be repopulated. Admission fencing and observer completeness are necessary parts of the claim. A scope-level kill primitive can correctly operate while the product's descendant-completeness promise still fails.

### 7.2 Atomicity is an observation contract

Atomicity must identify object, observers and operation: for example, fresh opens of one canonical filename during a successful same-directory replacement observe an allowed whole generation. It does not imply that readers holding the old handle switch generations, that all files switch together, that attributes are preserved, that another directory's update is synchronized, or that a crash leaves the new generation durable.

The publication fixture records content, length, digest, generation, names and required metadata independently. For Windows, all documented partial failure states of the selected replacement API belong in the recovery model. For Linux, unsupported flags, cross-filesystem requests and errors on directory synchronization belong in the evidence, not in a hidden fallback path. A store benchmark can use this contract as a prerequisite, but the choice of store remains elsewhere.

### 7.3 Durability is an acknowledged outcome within a named failure domain

The contract phrase survives power loss is forbidden without these fields: what lost power, what remained powered, whether caches were volatile, which flush/FUA boundary was acknowledged, whether the witness survived, the recovery procedure and the exact state invariant asserted. The following domains are separate cells, not an implication ladder:

| Domain | What fails | What a passing cell may establish | What it cannot establish |
| --- | --- | --- | --- |
| process_crash | Writer/broker address space ends abruptly | Recovery after process failure with OS/device state still running | Guest, host or power loss behavior |
| guest_reset | Guest abruptly resets; host may retain dirty cache | Application consistency after that guest reset mechanism | Host crash or physical media persistence |
| host_reset | Host kernel resets without graceful shutdown | Recovery under that exact reset/cache topology | Actual power removal or controller failure |
| physical_power_loss | Named physical power domain interrupted | Survival under observed apparatus, cache and hardware topology | All power failures, all hardware faults or failed storage media |
| network_partition | Named client/server path becomes unavailable | Correct handling of ambiguity and recovery under that partition | Server persistence or server power failure |
| server_restart | Named storage server restarts | Recovery under that server state/cache/restart policy | Unperformed client/host/physical faults |

A passing physical-power experiment is a finite observation, not a universal hardware guarantee. A device that acknowledges flush incorrectly may defeat a correctly ordered application protocol. Linux's block cache documentation explains why volatile caches and propagation of flush/FUA matter. NFS explicitly defines stable storage and differentiates stable from unstable writes and COMMIT; those protocol semantics still require a pinned implementation and observed server behavior. [S30, S33]

The durable acknowledgment oracle is strict: any generation externally acknowledged as durable under the selected domain must be present in the allowed application-consistent recovered state. A generation not acknowledged may be present or absent according to the recovery contract. It must not be assumed absent and retried blindly. Application consistency, filesystem consistency, namespace atomicity and content integrity are four separately recorded properties.

## 8 Resource fault taxonomy and downstream consequences

The resource_outcomes array is chronological evidence with zero or more confirmed subtypes. It does not force one final OOM code:

| Subtype | Required observation | Recovery and accounting consequence |
| --- | --- | --- |
| throttle | Native throttling/pressure evidence plus continued identity and progress observations | Work may still be alive; extending or canceling follows policy. Wall delay is not CPU consumption |
| allocation_refusal | Failed allocation or native limit result correlated to the executing identity | The application may recover or fail. Refusal alone does not justify respawn or assumed group death |
| process_kill | A particular stable identity exited, with supported cause attribution | Surviving peers and partial outputs must be reconciled before replay |
| group_kill | Evidence that the defined group policy killed the relevant members, with exceptions and survivors accounted for | Scope emptiness and canonical settlement still need separate proof |
| unknown | Missing/contradictory cause, coverage or native state | Preserve the uncertainty; do not choose a cheaper charge or an automatic replay based on guessed OOM |

Windows Job committed-memory ceilings document refusal of an excessive commit. An application's reaction may subsequently terminate it, but the ceiling must not be described as inherently equivalent to a Linux group OOM kill. Linux memory event counters distinguish several conditions, and the baseline/hierarchy/protection configuration changes interpretation. The profile records these native differences rather than manufacturing one portable status. [S32, S05]

For PF11 and PF12, collect memory.events and memory.events.local with the low, high, max, oom, oom_kill and oom_group_kill keys, baseline values and hierarchy settings; an unavailable key remains unknown. The Linux v6.12 source exposes those counters separately. Pin memory.oom.group and include its protected-task exception in the expected survivor set: oom_score_adj equal to -1000 is not overridden by group OOM policy. Group OOM evidence must therefore remain separate from containment_empty. [S38, S05]

The proposed terminal outcome contains both execution outcome and resource evidence. For example, execution can fail after allocation_refusal, or succeed after throttle. Cause attribution needs native evidence and must permit unknown when a process could have been killed by a controller, global policy or unrelated fault. Multiple causes are not compressed by precedence without an explicit rule.

Disk exhaustion, inode exhaustion, quota refusal, descriptor exhaustion, process-count limits and observer buffer exhaustion are also resource faults, although resource_outcomes specifically names the requested memory/pressure family. Their native errors and affected subsystem are retained in native_errors and the trace's evidence artifacts. A product-wide generalized fault enum can extend the versioned schema later; it must not reinterpret existing records silently.

Accounting uses a counter's actual aggregation boundary. Native cumulative group CPU can capture short-lived members better than sparse PID samples, but it still cannot charge external work it never included. Memory peak metrics have different definitions across systems. A local session must return source, unit, observation interval, counter epoch, missingness and scope completeness with every metric. Unknown and zero have different serialized states. Billing, retry, backoff and user-facing explanation must not depend on replacing the former with the latter.

## 9 Qualification and retirement of unknowns

### 9.1 Exhaustive outcome rule

Qualified at a pinned configuration is allowed only when the Owner has included the profile and approved the relevant claim set; all identity pins are resolved; the exact contract and harness are frozen; every required applicable variant and cut point has confirmed fault injection and complete evidence; observation and recovery oracles pass; no contradictory mandatory result remains; and an independent reviewer accepts the evidence. The acceptance record identifies profile, claim set, failure domains, fixture versions and bounded observation conditions. It is not general platform certification.

Rejected or unsupported applies when a witnessed trace violates a mandatory selected contract, a required capability is conclusively unavailable under the pinned configuration, or the Owner explicitly excludes the case. The record distinguishes behavioral failure, documented unsupported capability and policy exclusion. A rejected profile may still satisfy a weaker future contract, but that requires a new scoped decision and does not rewrite the historical failure.

Unknown pending named evidence applies in every remaining state: unexecuted profile, unresolved identity, missing Owner decision, unconfirmed injection, incomplete oracle, lost witness, inaccessible state, ambiguous cause, conflicting evidence or pending independent review. Unknown is the initial state of all eleven supplied cases. A successful API invocation and a clean document/schema validation do not change it.

For one claim cell, a conclusive violation takes precedence over an incomplete pass record. For profile aggregation, one mandatory rejected cell rejects the selected claim set; otherwise any mandatory unknown leaves the profile unknown; only complete accepted cells permit qualified. Optional exploratory claims cannot silently become mandatory or conceal a failed mandatory claim. Independent review can reject the harness itself, requiring all dependent cells to return to unknown until the evidence is trustworthy.

### 9.2 Named unknown retirement evidence

| Unknown | Evidence required to retire it | Evidence that does not retire it |
| --- | --- | --- |
| Target identity | Authorized inventory, effective configuration artifacts and recomputed fingerprint | Product name or release-family label |
| Scope choice | Explicit Owner decision naming supported/excluded cases and claims | Researcher's preferred platform |
| Creation membership | First execution witness plus native membership and parent-death cut coverage | Assignment call success after execution began |
| Descendant completeness | Actor creation evidence, escape controls and declared external-work boundary | Empty Job/cgroup alone |
| Terminal teardown | Backpressure-confirmed trace, independent close/exit/drain evidence per build | Window disappeared or ClosePseudoConsole returned |
| Durable publication | Confirmed fault domain, external ACK witness and first recovered content/namespace evidence | Filesystem clean, process-kill pass or API documentation |
| Lock ownership | Actual lock acquisition/release/fencing observations under exact primitive | Stale PID file removed |
| Resource cause | Native events/errors, stable identity exits and observer completeness | Generic OOM log line or absent notification |
| Supervisor quiescence | Launch/activation policy, epoch fencing and full restart horizon evidence | One stopped status query |
| Suspend semantics | Chosen semantics, explicit sleep/pause evidence and clock comparison | Monotonic label alone |
| Network commit | Correlated request/server/recovery evidence and authority reconciliation | Timeout or client cache read |
| Acceptance | Independent reviewer decision against retained evidence | Implementer PASS or consensus |

Retirement can produce qualified or rejected; it does not inherently mean success. Newly discovered drift or contrary evidence reopens the relevant cell and invalidates dependent acceptance for that new configuration. Do not erase the old result; retain the precise historical scope and the reason it no longer applies.

## 10 Recommendations with competing options and falsifiers

Every item below is a proposed contract recommendation, classified inferred. None is a library, runtime, store or platform selection.

R01 Use exact behavioral fingerprints. Competing option: a coarse OS-version support matrix with manually documented exceptions. Decisive falsifier: two configurations with the same proposed fingerprint differ in a mandatory observed behavior because an omitted dimension matters. Then the schema must add that dimension and the old equivalence claim is invalid. Does not prove: that the enumerated dimensions are exhaustive forever or that a pinned target passes.

R02 Preserve five independent state predicates. Competing option: one terminal/connection completion flag. Decisive falsifier: a preregistered case can satisfy the proposed settled conjunction while required work remains live, unfenced or uncommitted. Does not prove: liveness or bounded completion on all targets.

R03 Require creation-time membership or an independently qualified gated alternative. Competing option: create, suspend/hold, assign and release with recovery safeguards. Decisive falsifier: PF02 finds first runnable work outside scope or an unrecoverable registration gap despite the claimed mechanism. Does not prove: durable registration, full descendant capture or capture of service-created work.

R04 Treat native queries and identity references as authoritative alongside notifications. Competing option: notification-only event sourcing. Decisive falsifier: PF16 drops an event and the proposed reconciliation yields false settlement, loses identity or cannot detect its own incomplete evidence. Does not prove: that querying is race free or reconstructs exact lost timing.

R05 Separate storage claims by failure domain. Competing option: one generic crash-safe or power-safe label. Decisive falsifier: the same accepted domain descriptor admits materially different failed cache/power components, or PF07 loses a witnessed acknowledged generation. Does not prove: immunity to all hardware faults or honest device firmware.

R06 Preregister publication cuts and first-recovery inspection. Competing option: only random kill/reboot stress. Decisive falsifier: the deterministic protocol cannot distinguish a required cut or its repair step masks the initial recovered state. Does not prove: exhaustive interleaving coverage or multi-file transaction semantics.

R07 Keep resource faults as a family. Competing option: a single resource_exhausted/OOM outcome. Decisive falsifier: the proposed event schema cannot represent a witnessed refusal-with-survivors or throttle-then-kill sequence without losing a fact required for retry/accounting. Does not prove: a universal comparable memory metric.

R08 Require independent acceptance and sensitive-oracle controls. Competing option: the implementer's CI PASS as acceptance. Decisive falsifier: a known-bad control passes, or the reviewer cannot reconstruct the outcome from retained artifacts. Does not prove: reviewer infallibility or absence of untested bugs.

R09 Make compatibility and network routes explicit mandatory cases. Competing option: inherit native qualification except for known exceptions. Decisive falsifier: an in-scope composite route is admitted by the matrix without its own pin and trace coverage. Does not prove: that any route should be supported or that exclusion is permanent.

R10 Keep unknown distinct from rejected and from zero. Competing option: fail closed by labeling all unverified cases unsupported and all missing metrics zero. Decisive falsifier: a downstream consumer treats unknown as acceptance, confirmed absence or a billable exact measurement. Does not prove: the ability to retire every unknown or the appropriateness of a particular business policy.

R11 Fence recovery before automatic retry. Competing option: immediately restart on apparent process/transport death. Decisive falsifier: PF02, PF13 or PF15 admits duplicate work or accepts a stale owner after the proposed fence. Does not prove: exactly-once effects outside the declared causal boundary.

R12 Run destructive evidence only in isolated disposable targets. Competing option: collect convenient failure data on an everyday development workstation or live shared storage. Decisive falsifier: the safety review cannot demonstrate that fault injection and cleanup are confined to the approved target and power/network domain. Does not prove: zero risk to disposable hardware or authorization to perform the tests.

## 11 Local execution handoff

### 11.1 What remains unexecuted

The user's local agent sessions need to implement and execute PF01 through PF20 for every selected profile and applicable variant. They must also perform inventory, preregistration, evidence collection and independent acceptance. No result in this document substitutes for that work. The following is the precise execution queue; completing it is separate from reading this report.

1. Obtain O01 through O12 decisions in Section 12. Record candidate_in_scope or explicit owner_excluded for every mandatory category, exact claims and accepted failure domains. Do not fill unresolved choices with a researcher's preference
2. Inventory each authorized disposable host and every selected composite route. Populate all profile facts with source artifacts. Record effective configurations, not just installed package labels. Resolve unsupported versus permission-denied capabilities without changing security policy implicitly
3. Implement the platform adapters and fixture actors in a separately authorized local engineering session. Preserve native return/error data, stable identity handles, barriers, side-channel witnesses and safe cleanup ownership. This report does not select the implementation language or library
4. Freeze a run specification with profile key, contract digest, harness/adapter digests, numeric budgets, finite cut list, repetitions, seeds, allowed outcomes, independent witness placement and safety approvals. Have a reviewer other than the implementer approve it before execution
5. Run no-fault and known-bad oracle controls first. PF16 and PF20 must demonstrate detection of missing evidence and intentionally false settlement. An insensitive oracle blocks all dependent runs
6. Run PF01, PF02, PF03, PF05, PF08, PF09 and PF18 for process identity, membership, permissions and locks. Stop if admission fencing or isolation fails. Run PF04 and PF17 for each terminal/compatibility route
7. Run PF10, PF11, PF12 and PF19 for resource failure and accounting with independent headroom. Do not exhaust the host's shared disk, process table or memory
8. Run PF06 with process_crash first. After reviewing recovery evidence, separately run PF07 for each additionally authorized guest_reset, host_reset and physical_power_loss domain. A VM result must retain that domain label
9. Run PF13 and PF14 for exact supervisor, activation and time policies. Run PF15 on isolated shares/exports for each selected SMB/NFS client/server profile. No production share or service is a valid convenience substitute
10. Run the preregistered combined cases in PF20. Return the initial recovery observations before any cleanup or repair, all failures and unknowns, and the independent review record. Reruns must preserve earlier failures rather than replacing them

### 11.2 Required run specification

Before a fixture runs, the local session must supply exact values for: case/profile key; claim IDs; fixture/version; variants and ordered cut points; harness/adapter digests; actor topology and privileges; payload byte generator version and sizes; maximum processes, bytes, memory, output and open handles; observer sampling and buffer bounds; watchdog, graceful-stop, drain and recovery horizons; sleep-state/power/network fault domain; repetitions and seeds; trigger confirmation rule; expected outcomes per cut; cleanup identities; evidence destinations; and reviewer/safety approval references.

All numeric budgets are positive finite values with units. The protocol explicitly permits not_applicable only for a reviewed irrelevant parameter. No universal latency threshold is invented here because the Owner's platform floor and product deadline semantics are unresolved. If a local session cannot bind the budget or safety scope, that cell remains unknown before execution. This is an execution prerequisite, not permission to replace a missing test with a narrative pass.

### 11.3 Destructive test prerequisites

Resource faults require a disposable bounded volume/quota and containment boundary, with observer resources reserved outside it. Process churn requires a private controlled target and a preapproved cap. Service experiments require a uniquely identified synthetic service/unit; no real supervisor policy is edited. MAC, token, seccomp or namespace variations require explicit local authorization and a separate profile for every change.

Guest resets require a disposable guest and known host backing storage; snapshots used for restoration are distinguished from the crash mechanism. Host resets and physical interruption require dedicated hardware or an explicitly approved isolated target, a tested restore path, no unrelated mounted data, independent witness power and a human-approved safe interruption procedure. The local session must not improvise electrical switching or damage hardware. If those prerequisites cannot be met, leave physical_power_loss unknown and state precisely which weaker domains were actually observed.

Network interruption requires a test-only share/export and a fault path that cannot affect unrelated users. The controller must be able to restore connectivity and safely stop the test independently. Real secrets and personal files are never fixture payloads. Local detailed inventory and infrastructure identifiers stay in the user's local evidence store; a shareable result uses synthetic IDs and sanitized configuration summaries.

### 11.4 Evidence bundle and acceptance return

Return the pinned manifest; exact preregistration; fixture/harness/adapter identities; raw native observations and error records; independent fault and acknowledgment witness; sequence-gap and clock-epoch records; before/first-after recovery content and metadata digests; actor/scope inventory; resource counter baselines/finals; cleanup log; per-cell pass/fail/unknown reasoning; and independent reviewer decision. Every artifact needs a digest and an evidence reference. Raw logs should be retained locally and shared only after explicit scope/privacy review.

Each cell's final summary must say which fault was confirmed, which expected state was observed, what remains unknown, whether the observation and recovery oracles passed, and why execution stopped. A local agent's own completion message is not acceptance. A reviewer must independently examine evidence and known-bad controls. A failed mandatory cell rejects the claimed profile; a missing or untriggered cell leaves it unknown.

The report's machine-readable schema, catalog and pending manifest can be validated as documents without executing a fixture. Such validation establishes only artifact structure. It is not an OS, containment, durability or recovery test.

## 12 Owner inputs that remain decisions

O01 Platform floor: supported Windows editions/builds/update policy; Linux distributions/kernel/configuration and architectures; whether support means specific pins or a separately governed requalification policy.

O02 Compatibility scope: whether WSL2, native ext4, Windows mounted paths, MSYS2, Git Bash and each embedded terminal route are in scope. Composite routes must be named.

O03 Storage scope: local filesystems and features; SMB and NFS clients/servers/protocols; cross-directory/volume publication requirements; local versus network authority boundaries.

O04 Durability promise: exact allowed loss after acknowledgment and failure domains, including whether physical power loss is actually required, at what hardware boundary and with which protection assumptions.

O05 Causal containment boundary: privileges, breakaway/migration policy, external service routes, remote work and whether full descendant/causal capture is promised or membership-limited management is sufficient.

O06 Terminal semantics: detach versus cancel; drain versus explicit truncation; output retention/loss policy; supported terminal hosts, shell paths and console signal behavior.

O07 Deadline semantics: elapsed versus active time; suspend, hibernate, reboot and virtual-machine pause policy; timeout tolerances and clock uncertainty.

O08 Resource policy: limits, permitted refusal/throttle outcomes, group kill policy, swap/reclaim behavior, retry rules and accounting completeness requirements.

O09 Supervision and recovery: supported service manager/activation policies, startup/ownership fencing and when an interrupted execution may be adopted, canceled or retried.

O10 Experimental budgets: finite workloads, repetitions, cut coverage, resource safety caps, observation horizons and acceptance confidence claims. Research proposes the structure but does not pick product thresholds.

O11 Evidence and independent acceptance: reviewer role, artifact retention, permissible private inventory, public redaction and who may accept or reject each claim set.

O12 Destructive authorization: which disposable hosts, virtual machines, test shares and power/network domains may be interrupted; who can approve privilege/configuration changes and physical apparatus.

These inputs are required facts in the manifest rather than implied choices. Lucas remains the final Owner. The latest Owner direction retires Hermes and defines v3 as a standalone harness that can both execute natively and wrap or orchestrate other harnesses. Historical authority wording in the supplied brief does not override that direction. This report edits no protected product document.

## 13 Claim ledger

The ledger maps every material claim family to its class, evidence and retirement burden. Detailed proposed fields and fixture steps inherit the inferred classification of their listed family.

| ID | Consequential claim | Class | Evidence or retirement requirement |
| --- | --- | --- | --- |
| C01 | Jobs manage associated processes; most completion notifications are not guaranteed | Source documented | S01 |
| C02 | Creation-time Job list is available on documented Windows families | Source documented | S02; actual capability requires PF18 |
| C03 | Creation-time Job assignment precedes initial thread execution | Source documented | S03; target observation PF02 |
| C04 | ConPTY close behavior changes at build 26100 | Source documented | S04; exact build/host PF04 |
| C05 | cgroup kill is subtree membership based and protects its operation against concurrent creation/migration | Source documented | S05; complete causal capture remains a different claim |
| C06 | CLONE_INTO_CGROUP is cgroup v2 creation placement with restrictions | Source documented | S06; target policy availability unknown |
| C07 | pidfd provides stable process reference subject to acquisition/relationship semantics | Source documented | S07; PF09 |
| C08 | ReplaceFileW has same-volume restrictions, unsupported write-through flag and partial failure states | Source documented | S08; PF06/PF07 |
| C09 | File buffer flush is not a general cross-platform directory durability proof | Inferred from documented scope | S09/S11; target sequence and PF07 needed |
| C10 | LockFileEx permits mapped-view bypass and release timing may vary | Source documented | S10; PF08 |
| C11 | File fsync alone need not persist containing directory entry | Source documented | S11 |
| C12 | renameat2 flags and filesystem support are distinct from durable multi-file commit | Source documented and scoped inference | S12; PF06 |
| C13 | POSIX namespace semantics and crash/cache semantics are distinct | Source documented | S13/S14/S15 |
| C14 | Console control events have console/group-specific limits | Source documented | S16; PF05 |
| C15 | Active-time versus suspend-inclusive clocks differ | Source documented | S17/S18/S19; product policy O07 |
| C16 | PTY is a terminal transport with configured signal semantics | Source documented | S20; PF04/PF05 |
| C17 | Linux record-lock and open-file-description lifetimes differ | Source documented | S21; PF08 |
| C18 | Windows Job memory metrics/ceilings are committed-memory based | Source documented | S22/S32; PF12/PF19 |
| C19 | SCM queued restart can survive a manual restart/stop sequence | Source documented | S23; PF13 |
| C20 | WSL mount routes and compatibility products require distinct pins | Inferred from documented differences | S24/S25/S26/S36; PF17 |
| C21 | systemd kill and restart behavior depends on effective unit policy | Source documented | S27/S28 pinned v256; actual selected version unverified |
| C22 | JCS supplies a deterministic serialization definition | Source documented | S29; fingerprint scheme itself inferred |
| C23 | Volatile device caches and flush/FUA propagation affect persistence | Source documented | S30; hardware behavior unverified |
| C24 | Successful write may be short or followed by delayed failure | Source documented | S31; PF10 |
| C25 | NFS stable/unstable writes and COMMIT have distinct semantics | Source documented | S33; PF15 |
| C26 | SMB FLUSH specifies server-side persistence behavior with protocol conditions | Source documented | S34/S35; pinned implementation unverified |
| C27 | ConPTY channel ownership and synchronous I/O can create deadlocks | Source documented | S37; PF04 |
| C28 | Five independent state predicates and recovery conjunction prevent unsafe conflation | Inferred design | Sections 4/6; falsify via PF16/PF20 |
| C29 | All initial target rows have no local qualification evidence | Unverified target state | Empty result set; local handoff required |
| C30 | Exact profile hashing and no inheritance are necessary acceptance controls | Inferred design | Section 3; R01/R09 falsifiers |
| C31 | Membership-limited termination cannot prove full causal capture | Inferred from mechanism scope | Sections 5/7; PF01 |
| C32 | Reset domains do not establish physical power-loss survival by analogy | Inferred experimental boundary | Section 7; PF07 |
| C33 | Resource subtypes alter retry and accounting decisions | Inferred design | Section 8; PF11/PF12/PF19 |
| C34 | Exhaustive outcome rule and unknown retirement prevent missing verification from passing | Inferred governance | Section 9; independent review |
| C35 | Proposed catalog is runnable-level specification once local preregistration inputs are bound | Inferred deliverable claim | Section 6/11; implementation and all runs remain unexecuted |
| C36 | No actual platform certification or measured performance is established | Unverified target claims expressly withheld | All mandatory profiles remain Unqualified |

## Appendix A Complete platform manifest schema

This is the full JSON Schema 2020 12 definition. It is the same JSON object as platform-manifest.schema.json; line wrapping is presentation only. Section 3.4 defines the additional mandatory semantic checks. No sample target inventory is implied.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "FU04 Platform Manifest Version 1",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "schema_version": {"const": "fu04-platform-manifest-v1"},
    "as_of": {
      "type": "string",
      "format": "date"
    },
    "contract_status": {
      "enum": [
        "proposed_unexecuted",
        "preregistered",
        "executed_pending_review",
        "accepted"
      ]
    },
    "contract_digest": {
      "type": [
        "string",
        "null"
      ]
    },
    "profiles": {
      "type": "array",
      "items": {"$ref": "#/$defs/profile"},
      "minItems": 1
    },
    "results": {
      "type": "array",
      "items": {"$ref": "#/$defs/result"},
      "minItems": 0
    }
  },
  "required": [
    "schema_version",
    "as_of",
    "contract_status",
    "contract_digest",
    "profiles",
    "results"
  ],
  "$defs": {
    "fact": {
      "oneOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "state": {"const": "known"},
            "value": {"type": "string", "minLength": 1},
            "evidence_refs": {
              "type": "array",
              "items": {"type": "string", "minLength": 1},
              "minItems": 1
            }
          },
          "required": [
            "state",
            "value",
            "evidence_refs"
          ]
        },
        {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "state": {"const": "unknown"},
            "reason": {"type": "string", "minLength": 1},
            "retirement_evidence": {
              "type": "array",
              "items": {"type": "string", "minLength": 1},
              "minItems": 1
            }
          },
          "required": [
            "state",
            "reason",
            "retirement_evidence"
          ]
        },
        {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "state": {"const": "not_applicable"},
            "reason": {"type": "string", "minLength": 1},
            "evidence_refs": {
              "type": "array",
              "items": {"type": "string", "minLength": 1},
              "minItems": 1
            }
          },
          "required": [
            "state",
            "reason",
            "evidence_refs"
          ]
        }
      ]
    },
    "tri": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "value": {
          "enum": [
            "true",
            "false",
            "unknown"
          ]
        },
        "evidence_refs": {
          "type": "array",
          "items": {"type": "string", "minLength": 1},
          "minItems": 0
        },
        "reason": {"type": "string", "minLength": 1}
      },
      "required": [
        "value",
        "evidence_refs",
        "reason"
      ],
      "allOf": [
        {
          "if": {
            "properties": {
              "value": {
                "enum": [
                  "true",
                  "false"
                ]
              }
            },
            "required": [
              "value"
            ]
          },
          "then": {
            "properties": {
              "evidence_refs": {
                "minItems": 1
              }
            }
          }
        }
      ]
    },
    "profile": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "target_id": {"type": "string", "minLength": 1},
        "case_id": {"type": "string", "minLength": 1},
        "case_variant": {"type": "string", "minLength": 1},
        "scope_decision": {
          "enum": [
            "pending_owner",
            "candidate_in_scope",
            "owner_excluded"
          ]
        },
        "owner_decision_ref": {
          "type": [
            "string",
            "null"
          ]
        },
        "pin_state": {
          "enum": [
            "pending",
            "pinned"
          ]
        },
        "profile_key": {
          "type": [
            "string",
            "null"
          ],
          "pattern": "^fu04-p1:sha256:[0-9a-f]{64}$"
        },
        "identity": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "os": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "family": {"$ref": "#/$defs/fact"},
                "edition": {"$ref": "#/$defs/fact"},
                "release": {"$ref": "#/$defs/fact"},
                "build": {"$ref": "#/$defs/fact"},
                "update_revision": {"$ref": "#/$defs/fact"},
                "kernel_release": {"$ref": "#/$defs/fact"},
                "kernel_build_digest": {"$ref": "#/$defs/fact"},
                "distribution": {"$ref": "#/$defs/fact"},
                "distribution_release": {"$ref": "#/$defs/fact"},
                "libc_or_api_abi": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "family",
                "edition",
                "release",
                "build",
                "update_revision",
                "kernel_release",
                "kernel_build_digest",
                "distribution",
                "distribution_release",
                "libc_or_api_abi"
              ]
            },
            "architecture": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "host_arch": {"$ref": "#/$defs/fact"},
                "guest_arch": {"$ref": "#/$defs/fact"},
                "process_arch": {"$ref": "#/$defs/fact"},
                "abi": {"$ref": "#/$defs/fact"},
                "emulation": {"$ref": "#/$defs/fact"},
                "cpu_model": {"$ref": "#/$defs/fact"},
                "microcode_or_firmware": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "host_arch",
                "guest_arch",
                "process_arch",
                "abi",
                "emulation",
                "cpu_model",
                "microcode_or_firmware"
              ]
            },
            "execution_layer": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "kind": {"$ref": "#/$defs/fact"},
                "product": {"$ref": "#/$defs/fact"},
                "version": {"$ref": "#/$defs/fact"},
                "host_os_build": {"$ref": "#/$defs/fact"},
                "guest_kernel": {"$ref": "#/$defs/fact"},
                "vm_configuration_digest": {"$ref": "#/$defs/fact"},
                "wsl_package": {"$ref": "#/$defs/fact"},
                "wsl_distribution": {"$ref": "#/$defs/fact"},
                "wsl_configuration_digest": {"$ref": "#/$defs/fact"},
                "compatibility_runtime": {"$ref": "#/$defs/fact"},
                "compatibility_runtime_version": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "kind",
                "product",
                "version",
                "host_os_build",
                "guest_kernel",
                "vm_configuration_digest",
                "wsl_package",
                "wsl_distribution",
                "wsl_configuration_digest",
                "compatibility_runtime",
                "compatibility_runtime_version"
              ]
            },
            "filesystem": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "type": {"$ref": "#/$defs/fact"},
                "implementation_version": {"$ref": "#/$defs/fact"},
                "format_features": {"$ref": "#/$defs/fact"},
                "mount_options_canonical": {"$ref": "#/$defs/fact"},
                "mount_namespace": {"$ref": "#/$defs/fact"},
                "case_mode": {"$ref": "#/$defs/fact"},
                "symlink_reparse_policy": {"$ref": "#/$defs/fact"},
                "block_size_bytes": {"$ref": "#/$defs/fact"},
                "atomic_write_unit_bytes": {"$ref": "#/$defs/fact"},
                "quota_configuration_digest": {"$ref": "#/$defs/fact"},
                "path_route_class": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "type",
                "implementation_version",
                "format_features",
                "mount_options_canonical",
                "mount_namespace",
                "case_mode",
                "symlink_reparse_policy",
                "block_size_bytes",
                "atomic_write_unit_bytes",
                "quota_configuration_digest",
                "path_route_class"
              ]
            },
            "storage": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "locality": {"$ref": "#/$defs/fact"},
                "protocol": {"$ref": "#/$defs/fact"},
                "protocol_version": {"$ref": "#/$defs/fact"},
                "client_version": {"$ref": "#/$defs/fact"},
                "server_version": {"$ref": "#/$defs/fact"},
                "server_configuration_digest": {"$ref": "#/$defs/fact"},
                "server_filesystem": {"$ref": "#/$defs/fact"},
                "transport_options_canonical": {"$ref": "#/$defs/fact"},
                "cache_configuration_digest": {"$ref": "#/$defs/fact"},
                "lease_lock_configuration_digest": {"$ref": "#/$defs/fact"},
                "device_model": {"$ref": "#/$defs/fact"},
                "device_firmware": {"$ref": "#/$defs/fact"},
                "controller_model_firmware": {"$ref": "#/$defs/fact"},
                "virtual_disk_format": {"$ref": "#/$defs/fact"},
                "virtual_disk_host_filesystem": {"$ref": "#/$defs/fact"},
                "write_cache_policy": {"$ref": "#/$defs/fact"},
                "flush_fua_contract": {"$ref": "#/$defs/fact"},
                "power_loss_protection": {"$ref": "#/$defs/fact"},
                "failure_domain_topology_digest": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "locality",
                "protocol",
                "protocol_version",
                "client_version",
                "server_version",
                "server_configuration_digest",
                "server_filesystem",
                "transport_options_canonical",
                "cache_configuration_digest",
                "lease_lock_configuration_digest",
                "device_model",
                "device_firmware",
                "controller_model_firmware",
                "virtual_disk_format",
                "virtual_disk_host_filesystem",
                "write_cache_policy",
                "flush_fua_contract",
                "power_loss_protection",
                "failure_domain_topology_digest"
              ]
            },
            "terminal": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "kind": {"$ref": "#/$defs/fact"},
                "host_product": {"$ref": "#/$defs/fact"},
                "host_version": {"$ref": "#/$defs/fact"},
                "backend_product": {"$ref": "#/$defs/fact"},
                "backend_version": {"$ref": "#/$defs/fact"},
                "shell_product": {"$ref": "#/$defs/fact"},
                "shell_version": {"$ref": "#/$defs/fact"},
                "console_mode_digest": {"$ref": "#/$defs/fact"},
                "encoding": {"$ref": "#/$defs/fact"},
                "line_discipline": {"$ref": "#/$defs/fact"},
                "dimensions": {"$ref": "#/$defs/fact"},
                "handle_inheritance_policy_digest": {"$ref": "#/$defs/fact"},
                "embedded_host_version": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "kind",
                "host_product",
                "host_version",
                "backend_product",
                "backend_version",
                "shell_product",
                "shell_version",
                "console_mode_digest",
                "encoding",
                "line_discipline",
                "dimensions",
                "handle_inheritance_policy_digest",
                "embedded_host_version"
              ]
            },
            "supervisor": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "kind": {"$ref": "#/$defs/fact"},
                "version": {"$ref": "#/$defs/fact"},
                "configuration_digest": {"$ref": "#/$defs/fact"},
                "restart_policy": {"$ref": "#/$defs/fact"},
                "kill_policy": {"$ref": "#/$defs/fact"},
                "stop_timeout_ns": {"$ref": "#/$defs/fact"},
                "startup_gate": {"$ref": "#/$defs/fact"},
                "activation_sources_canonical": {"$ref": "#/$defs/fact"},
                "service_identity_policy": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "kind",
                "version",
                "configuration_digest",
                "restart_policy",
                "kill_policy",
                "stop_timeout_ns",
                "startup_gate",
                "activation_sources_canonical",
                "service_identity_policy"
              ]
            },
            "security": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "principal_privilege_class": {"$ref": "#/$defs/fact"},
                "token_or_capabilities_digest": {"$ref": "#/$defs/fact"},
                "mac_policy_digest": {"$ref": "#/$defs/fact"},
                "seccomp_policy_digest": {"$ref": "#/$defs/fact"},
                "fips_mode": {"$ref": "#/$defs/fact"},
                "integrity_or_lsm_mode": {"$ref": "#/$defs/fact"},
                "namespace_configuration_digest": {"$ref": "#/$defs/fact"},
                "policy_engine_versions": {"$ref": "#/$defs/fact"},
                "antimalware_filter_versions": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "principal_privilege_class",
                "token_or_capabilities_digest",
                "mac_policy_digest",
                "seccomp_policy_digest",
                "fips_mode",
                "integrity_or_lsm_mode",
                "namespace_configuration_digest",
                "policy_engine_versions",
                "antimalware_filter_versions"
              ]
            },
            "containment": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "mechanism": {"$ref": "#/$defs/fact"},
                "version": {"$ref": "#/$defs/fact"},
                "scope_type": {"$ref": "#/$defs/fact"},
                "creation_membership_method": {"$ref": "#/$defs/fact"},
                "job_chain_flags_digest": {"$ref": "#/$defs/fact"},
                "job_handle_ownership_digest": {"$ref": "#/$defs/fact"},
                "cgroup_mode": {"$ref": "#/$defs/fact"},
                "cgroup_controllers_canonical": {"$ref": "#/$defs/fact"},
                "cgroup_delegation_digest": {"$ref": "#/$defs/fact"},
                "namespace_floor": {"$ref": "#/$defs/fact"},
                "migration_policy": {"$ref": "#/$defs/fact"},
                "external_service_policy": {"$ref": "#/$defs/fact"},
                "resource_limits_digest": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "mechanism",
                "version",
                "scope_type",
                "creation_membership_method",
                "job_chain_flags_digest",
                "job_handle_ownership_digest",
                "cgroup_mode",
                "cgroup_controllers_canonical",
                "cgroup_delegation_digest",
                "namespace_floor",
                "migration_policy",
                "external_service_policy",
                "resource_limits_digest"
              ]
            },
            "clock": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "deadline_semantics": {"$ref": "#/$defs/fact"},
                "clock_api": {"$ref": "#/$defs/fact"},
                "clock_resolution_ns": {"$ref": "#/$defs/fact"},
                "suspend_accounting": {"$ref": "#/$defs/fact"},
                "reboot_epoch_policy": {"$ref": "#/$defs/fact"},
                "virtualization_clock_contract": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "deadline_semantics",
                "clock_api",
                "clock_resolution_ns",
                "suspend_accounting",
                "reboot_epoch_policy",
                "virtualization_clock_contract"
              ]
            },
            "adapter": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "execution_route_kind": {"$ref": "#/$defs/fact"},
                "upstream_harness_product": {"$ref": "#/$defs/fact"},
                "upstream_harness_version": {"$ref": "#/$defs/fact"},
                "upstream_harness_configuration_digest": {"$ref": "#/$defs/fact"},
                "delegated_work_boundary": {"$ref": "#/$defs/fact"},
                "contract_version": {"$ref": "#/$defs/fact"},
                "artifact_digest": {"$ref": "#/$defs/fact"},
                "configuration_digest": {"$ref": "#/$defs/fact"},
                "process_identity_method": {"$ref": "#/$defs/fact"},
                "lock_primitive": {"$ref": "#/$defs/fact"},
                "publish_primitive": {"$ref": "#/$defs/fact"},
                "flush_sequence_digest": {"$ref": "#/$defs/fact"}
              },
              "required": [
                "execution_route_kind",
                "upstream_harness_product",
                "upstream_harness_version",
                "upstream_harness_configuration_digest",
                "delegated_work_boundary",
                "contract_version",
                "artifact_digest",
                "configuration_digest",
                "process_identity_method",
                "lock_primitive",
                "publish_primitive",
                "flush_sequence_digest"
              ]
            }
          },
          "required": [
            "os",
            "architecture",
            "execution_layer",
            "filesystem",
            "storage",
            "terminal",
            "supervisor",
            "security",
            "containment",
            "clock",
            "adapter"
          ]
        },
        "qualification": {
          "enum": [
            "qualified",
            "rejected",
            "unknown"
          ]
        },
        "display_status": {
          "enum": [
            "Qualified",
            "Rejected",
            "Unqualified"
          ]
        },
        "required_fixture_ids": {
          "type": "array",
          "items": {"type": "string", "minLength": 1},
          "minItems": 1
        },
        "required_owner_inputs": {
          "type": "array",
          "items": {"type": "string", "minLength": 1},
          "minItems": 0
        },
        "evidence_refs": {
          "type": "array",
          "items": {"type": "string", "minLength": 1},
          "minItems": 0
        },
        "unknowns": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "id": {"type": "string", "minLength": 1},
              "reason": {"type": "string", "minLength": 1},
              "retirement_evidence": {
                "type": "array",
                "items": {"type": "string", "minLength": 1},
                "minItems": 1
              },
              "owner_role": {"type": "string", "minLength": 1}
            },
            "required": [
              "id",
              "reason",
              "retirement_evidence",
              "owner_role"
            ]
          },
          "minItems": 0
        }
      },
      "required": [
        "target_id",
        "case_id",
        "case_variant",
        "scope_decision",
        "owner_decision_ref",
        "pin_state",
        "profile_key",
        "identity",
        "qualification",
        "display_status",
        "required_fixture_ids",
        "required_owner_inputs",
        "evidence_refs",
        "unknowns"
      ],
      "allOf": [
        {
          "if": {
            "properties": {
              "scope_decision": {"const": "owner_excluded"}
            },
            "required": [
              "scope_decision"
            ]
          },
          "then": {
            "properties": {
              "owner_decision_ref": {"type": "string", "minLength": 1},
              "qualification": {"const": "rejected"},
              "display_status": {"const": "Rejected"}
            }
          }
        },
        {
          "if": {
            "properties": {
              "pin_state": {"const": "pending"}
            },
            "required": [
              "pin_state"
            ]
          },
          "then": {
            "properties": {
              "profile_key": {
                "const": null
              }
            }
          }
        },
        {
          "if": {
            "allOf": [
              {
                "properties": {
                  "pin_state": {"const": "pending"}
                },
                "required": [
                  "pin_state"
                ]
              },
              {
                "not": {
                  "properties": {
                    "scope_decision": {"const": "owner_excluded"}
                  },
                  "required": [
                    "scope_decision"
                  ]
                }
              }
            ]
          },
          "then": {
            "properties": {
              "qualification": {"const": "unknown"},
              "display_status": {"const": "Unqualified"}
            }
          }
        },
        {
          "if": {
            "properties": {
              "pin_state": {"const": "pinned"}
            },
            "required": [
              "pin_state"
            ]
          },
          "then": {
            "properties": {
              "profile_key": {
                "type": "string",
                "pattern": "^fu04-p1:sha256:[0-9a-f]{64}$"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "qualification": {"const": "qualified"}
            },
            "required": [
              "qualification"
            ]
          },
          "then": {
            "properties": {
              "scope_decision": {"const": "candidate_in_scope"},
              "pin_state": {"const": "pinned"},
              "display_status": {"const": "Qualified"},
              "owner_decision_ref": {"type": "string", "minLength": 1}
            }
          }
        },
        {
          "if": {
            "properties": {
              "qualification": {"const": "rejected"}
            },
            "required": [
              "qualification"
            ]
          },
          "then": {
            "properties": {
              "display_status": {"const": "Rejected"}
            }
          }
        },
        {
          "if": {
            "properties": {
              "qualification": {"const": "unknown"}
            },
            "required": [
              "qualification"
            ]
          },
          "then": {
            "properties": {
              "display_status": {"const": "Unqualified"}
            }
          }
        }
      ]
    },
    "result": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "result_id": {"type": "string", "minLength": 1},
        "profile_key": {
          "type": "string",
          "pattern": "^fu04-p1:sha256:[0-9a-f]{64}$"
        },
        "fixture_id": {"type": "string", "minLength": 1},
        "fixture_version": {"type": "string", "minLength": 1},
        "variant_id": {"type": "string", "minLength": 1},
        "cutpoint": {"type": "string", "minLength": 1},
        "failure_domain": {
          "enum": [
            "process_crash",
            "guest_reset",
            "host_reset",
            "physical_power_loss",
            "network_partition",
            "server_restart",
            "none"
          ]
        },
        "contract_digest": {"type": "string", "minLength": 1},
        "harness_digest": {"type": "string", "minLength": 1},
        "adapter_digest": {"type": "string", "minLength": 1},
        "run_id": {"type": "string", "minLength": 1},
        "execution_epoch": {"type": "string", "minLength": 1},
        "observer_epoch": {"type": "string", "minLength": 1},
        "repetition": {
          "type": "integer",
          "minimum": 1
        },
        "seed": {"type": "string", "minLength": 1},
        "fault_confirmed": {"$ref": "#/$defs/tri"},
        "trace_complete": {"$ref": "#/$defs/tri"},
        "observation_oracle": {
          "enum": [
            "pass",
            "fail",
            "unknown"
          ]
        },
        "recovery_oracle": {
          "enum": [
            "pass",
            "fail",
            "unknown"
          ]
        },
        "state": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "transport_closed": {"$ref": "#/$defs/tri"},
            "client_disconnected": {"$ref": "#/$defs/tri"},
            "containment_empty": {"$ref": "#/$defs/tri"},
            "process_exited": {"$ref": "#/$defs/tri"},
            "execution_settled": {"$ref": "#/$defs/tri"},
            "scope_membership_complete": {"$ref": "#/$defs/tri"},
            "descendant_capture_complete": {"$ref": "#/$defs/tri"}
          },
          "required": [
            "transport_closed",
            "client_disconnected",
            "containment_empty",
            "process_exited",
            "execution_settled",
            "scope_membership_complete",
            "descendant_capture_complete"
          ]
        },
        "resource_outcomes": {
          "type": "array",
          "items": {
            "enum": [
              "throttle",
              "allocation_refusal",
              "process_kill",
              "group_kill",
              "unknown"
            ]
          },
          "minItems": 0
        },
        "native_errors": {
          "type": "array",
          "items": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "api": {"type": "string", "minLength": 1},
              "code": {"type": "string", "minLength": 1},
              "phase": {"type": "string", "minLength": 1},
              "evidence_ref": {"type": "string", "minLength": 1}
            },
            "required": [
              "api",
              "code",
              "phase",
              "evidence_ref"
            ]
          },
          "minItems": 0
        },
        "evidence_refs": {
          "type": "array",
          "items": {"type": "string", "minLength": 1},
          "minItems": 0
        },
        "stop_reason": {"type": "string", "minLength": 1},
        "qualification": {
          "enum": [
            "qualified",
            "rejected",
            "unknown"
          ]
        },
        "independent_review": {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "status": {
              "enum": [
                "pending",
                "accepted",
                "rejected"
              ]
            },
            "reviewer_role_id": {
              "type": [
                "string",
                "null"
              ]
            },
            "decision_ref": {
              "type": [
                "string",
                "null"
              ]
            }
          },
          "required": [
            "status",
            "reviewer_role_id",
            "decision_ref"
          ]
        }
      },
      "required": [
        "result_id",
        "profile_key",
        "fixture_id",
        "fixture_version",
        "variant_id",
        "cutpoint",
        "failure_domain",
        "contract_digest",
        "harness_digest",
        "adapter_digest",
        "run_id",
        "execution_epoch",
        "observer_epoch",
        "repetition",
        "seed",
        "fault_confirmed",
        "trace_complete",
        "observation_oracle",
        "recovery_oracle",
        "state",
        "resource_outcomes",
        "native_errors",
        "evidence_refs",
        "stop_reason",
        "qualification",
        "independent_review"
      ],
      "allOf": [
        {
          "if": {
            "properties": {
              "qualification": {"const": "qualified"}
            },
            "required": [
              "qualification"
            ]
          },
          "then": {
            "properties": {
              "fault_confirmed": {
                "properties": {
                  "value": {"const": "true"}
                }
              },
              "trace_complete": {
                "properties": {
                  "value": {"const": "true"}
                }
              },
              "observation_oracle": {"const": "pass"},
              "recovery_oracle": {"const": "pass"},
              "independent_review": {
                "properties": {
                  "status": {"const": "accepted"},
                  "reviewer_role_id": {"type": "string", "minLength": 1},
                  "decision_ref": {"type": "string", "minLength": 1}
                }
              }
            }
          }
        }
      ]
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {
          "contract_status": {"const": "proposed_unexecuted"}
        },
        "required": [
          "contract_status"
        ]
      },
      "then": {
        "properties": {
          "results": {
            "maxItems": 0
          }
        }
      }
    }
  ]
}
```

## Appendix B Source register

All sources below are primary public documentation or standards. Retrieval date is 1 October 2026, except the explicitly noted 2 October source check. A release tag or standard edition is a reference pin; a live documentation page is retrieval pinned and not an immutable target build. Reference editions do not select a supported platform floor. The POSIX official indexed excerpts were used where direct retrieval failed.

### S01 Job Objects

Microsoft Learn revision 2025-07-14. [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)

### S02 UpdateProcThreadAttribute

Microsoft Learn live API documentation. [UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)

### S03 Creation time Job assignment

Microsoft The Old New Thing 2023-02-09. [Creation time Job assignment](https://devblogs.microsoft.com/oldnewthing/20230209-00/?p=107812)

### S04 ClosePseudoConsole

Microsoft Learn revision 2025-07-09. [ClosePseudoConsole](https://learn.microsoft.com/en-us/windows/console/closepseudoconsole)

### S05 cgroup v2

Linux kernel documentation 6.12. [cgroup v2](https://docs.kernel.org/6.12/admin-guide/cgroup-v2.html)

### S06 clone

Linux man-pages current page as retrieved. [clone](https://man7.org/linux/man-pages/man2/clone.2.html)

### S07 pidfd open

Linux man-pages current page as retrieved. [pidfd_open](https://man7.org/linux/man-pages/man2/pidfd_open.2.html)

### S08 ReplaceFileW

Microsoft Learn revision 2023-06-01. [ReplaceFileW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew)

### S09 FlushFileBuffers

Microsoft Learn revision 2021-10-13. [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers)

### S10 LockFileEx

Microsoft Learn revision 2021-10-13. [LockFileEx](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-lockfileex)

### S11 fsync

Linux man-pages current page as retrieved. [fsync](https://man7.org/linux/man-pages/man2/fsync.2.html)

### S12 rename and renameat2

Linux man-pages current page as retrieved. [rename and renameat2](https://man7.org/linux/man-pages/man2/rename.2.html)

### S13 POSIX rename

POSIX Issue 8 IEEE 1003.1-2024. [POSIX rename](https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html)

### S14 POSIX file system cache

POSIX Issue 8 section 4.11. [POSIX file system cache](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap04.html)

### S15 POSIX cache rationale

POSIX Issue 8 rationale A.4.11. [POSIX cache rationale](https://pubs.opengroup.org/onlinepubs/9799919799/xrat/V4_xbd_chap01.html)

### S16 GenerateConsoleCtrlEvent

Microsoft Learn revision 2021-08-26. [GenerateConsoleCtrlEvent](https://learn.microsoft.com/en-us/windows/console/generateconsolectrlevent)

### S17 QueryUnbiasedInterruptTime

Microsoft Learn revision 2024-09-26. [QueryUnbiasedInterruptTime](https://learn.microsoft.com/en-us/windows/win32/api/realtimeapiset/nf-realtimeapiset-queryunbiasedinterrupttime)

### S18 High resolution time stamps

Microsoft Learn live documentation. [High resolution time stamps](https://learn.microsoft.com/en-us/windows/win32/sysinfo/acquiring-high-resolution-time-stamps)

### S19 clock gettime

Linux man-pages current page as retrieved. [clock_gettime](https://man7.org/linux/man-pages/man2/clock_gettime.2.html)

### S20 pty

Linux man-pages current page as retrieved. [pty](https://man7.org/linux/man-pages/man7/pty.7.html)

### S21 fcntl locking

Linux man-pages current page as retrieved. [fcntl locking](https://man7.org/linux/man-pages/man2/fcntl_locking.2.html)

### S22 Job extended limits

Microsoft Learn live API documentation. [Job extended limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information)

### S23 ChangeServiceConfig2W

Microsoft Learn revision 2024-11-20. [ChangeServiceConfig2W](https://learn.microsoft.com/en-us/windows/win32/api/winsvc/nf-winsvc-changeserviceconfig2w)

### S24 WSL filesystems

Microsoft Learn live documentation. [WSL filesystems](https://learn.microsoft.com/en-us/windows/wsl/filesystems)

### S25 WSL configuration

Microsoft Learn live documentation. [WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)

### S26 MSYS2 overview

MSYS2 official documentation. [MSYS2 overview](https://www.msys2.org/docs/what-is-msys2/)

### S27 systemd kill procedure

systemd release tag v256. [systemd kill procedure](https://raw.githubusercontent.com/systemd/systemd/v256/man/systemd.kill.xml)

### S28 systemd service

systemd release tag v256. [systemd service](https://raw.githubusercontent.com/systemd/systemd/v256/man/systemd.service.xml)

### S29 JSON Canonicalization Scheme

RFC8785 June2020 Informational. [JSON Canonicalization Scheme](https://www.rfc-editor.org/rfc/rfc8785.html)

### S30 Writeback cache control

Linux source release tag v6.12. [Writeback cache control](https://raw.githubusercontent.com/torvalds/linux/v6.12/Documentation/block/writeback_cache_control.rst)

### S31 write

Linux man-pages current page as retrieved. [write](https://man7.org/linux/man-pages/man2/write.2.html)

### S32 Job basic limits

Microsoft Learn live API documentation. [Job basic limits](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information)

### S33 NFSv4 1 protocol

RFC8881 August2020. [NFSv4.1 protocol](https://www.rfc-editor.org/rfc/rfc8881.html)

### S34 SMB2 FLUSH request

MS-SMB2 section2.2.17 revision2025-04-07. [SMB2 FLUSH request](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/e494678b-b1fc-44a0-b86e-8195acf74ad7)

### S35 SMB2 receiving FLUSH

MS-SMB2 section3.3.5.11 revision2026-01-14. [SMB2 receiving FLUSH](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2/026984f6-38af-4408-8200-50557eb0a286)

### S36 Git for Windows

Official project site. [Git for Windows](https://gitforwindows.org/)

### S37 Creating a pseudoconsole session

Microsoft Learn live documentation. [Creating a pseudoconsole session](https://learn.microsoft.com/en-us/windows/console/creating-a-pseudoconsole-session)

### S38 Linux memory controller source

Linux source release tag v6.12, functions __memory_events_show, memory_events_show and memory_events_local_show; checked 2 October 2026. [Linux memory controller source](https://raw.githubusercontent.com/torvalds/linux/v6.12/mm/memcontrol.c)

## Appendix C Machine readable package

The separate JSON files preserve editable schema, pending profiles, complete negative traces and source metadata. platform-manifest.json contains eleven pending profiles and no execution results. negative-traces.json contains the complete PF01 through PF20 texts, including every fault and oracle. Their JSON schemas define structural validation. profile-fields.json is a field index, not an additional source of truth. source-register.json records the citations and retrieval pins. All files are proposed specification artifacts; no profile qualification follows from successfully parsing or validating them.
