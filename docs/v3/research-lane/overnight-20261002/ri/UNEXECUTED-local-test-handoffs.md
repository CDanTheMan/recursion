# R-I unexecuted local handoffs

No target or fixture was executed. No runnable entrypoint is verified. A later authorized local session must implement the described harness and pin it before running.

## T01 Interject acknowledgement is not delivery

**Inputs:** {"traces": ["actor alive and waiting", "command receiver closed after session lookup", "active turn ends before next safe gap", "chat-state batch rejected", "cancellation during image/skill preparation"], "messages": ["m1", "m2"], "turns": ["t1", "t2"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test"]

**Independent Oracle:** ["Independent state-transition table: transport reply, actor admission, context insertion and model adoption are distinct", "Fake actor records received IDs; fake context store records inserted IDs; no model"]

**Pass Fail Predicate:** Never label an RPC queued response as delivered/adopted. On closed channel or missing insertion receipt, expose uncertain/not delivered. Successful insertions appear exactly once; stranded fallback is explicit and bound to its effective turn.

**Required Evidence:** ["Ordered fake transport/actor/context receipts", "Message identity/content revision ledger", "Race schedule and terminal queue contents"]

**Stopping Condition:** Stop on first false-consumption assertion or duplicate/lost message; otherwise finish every fixed interleaving and publish complete denominator

**Does Not Prove:** No real Grok binary conformance; no human intent adoption, model behavior or future source stability


## T02 Versioned queue mutation and wrong-target races

**Inputs:** {"operations": ["edit", "remove", "reorder", "hold_edit", "release_edit", "send_now"], "races": ["target consumed before edit", "stale revision", "duplicate operation", "missing owner", "turn advances", "notification lost before/after apply"], "sessions": ["sA", "sB"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test"]

**Independent Oracle:** ["Independent queue revision model with one legal winner for each race", "Target/content ledger separate from client UI projection"]

**Pass Fail Predicate:** Only valid owner/version mutations commit. Stale or already-delivered edits cannot falsely reclaim input. Duplicate IDs do not reapply; uncertain notification outcomes trigger observation/reconciliation rather than blind retry. No action crosses sA/sB.

**Required Evidence:** ["Canonical queue revisions and client projection diffs", "Refusal reasons and unresolved state", "Exact effective target"]

**Stopping Condition:** First mutation outside authority or stale target fails; stop after all operation/race pairs settle or become explicitly uncertain

**Does Not Prove:** No upstream transport reliability or complete durable queue implementation


## T03 Cancellation-safe draining and bounded control response

**Inputs:** {"load": ["synthetic event bursts", "blocked fake tool", "saturated data queue", "shutdown during deferred start", "stranded human and parent messages"], "limits": "Prespecify queue count/byte limits and control-latency ceiling"}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Independent control-latency/resource thresholds chosen before run"]

**Independent Oracle:** ["Reference input conservation invariant: accepted = pending + delivered + explicitly reclaimed + failed/uncertain, without duplication", "Monotonic fake clock and externally observed scheduling trace"]

**Pass Fail Predicate:** Cancellation never loses ownership of drained inputs. Stop/revocation is processed within declared bound under admitted load; overload rejects or backpressures explicitly. Stale completion cannot finish successor turn.

**Required Evidence:** ["Per-ID state conservation report", "Maximum queue bytes/count", "Control latency distribution and timed-out joins"]

**Stopping Condition:** Fail immediately on lost input/stale completion; otherwise exhaust declared stress envelope and fault schedule

**Does Not Prove:** No Rust/Tokio superiority, arbitrary-load guarantee or external effect termination


## T04 Conversation fork and filesystem effects remain separate

**Inputs:** {"workspace": "Synthetic Git repository with committed file, dirty tracked change, staged change, untracked file and ignored file", "events": ["conversation fork without worktree", "fork with worktree", "rewind after fake irreversible write", "source checkout moves"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Disposable filesystem only; file mutation authorized in later session"]

**Independent Oracle:** ["Independent byte manifests for original/fork plus conversation lineage oracle", "Fake external-effect ledger cannot be rewritten by conversation operations"]

**Pass Fail Predicate:** Conversation-only rewind leaves original effect record and expected file bytes; worktree fork exposes exactly its declared capture scope and never calls it full-world rollback. Original workspace identity and mutations remain attributable.

**Required Evidence:** ["Before/after source and workspace identities", "Per-file capture/exclusion ledger", "Conversation/effect lineage diffs"]

**Stopping Condition:** First hidden file revert, original-source mutation or omitted required capture fails; otherwise all declared cases resolved

**Does Not Prove:** No full host snapshot or external rollback; no all-filesystem portability


## T05 Dashboard worktree dispatch partial failure

**Inputs:** {"faults": ["creation fails", "creation succeeds but session start fails", "session starts while attach fails", "duplicate dispatch", "worktree deleted/moved before start", "user changes destination during pending request"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test"]

**Independent Oracle:** ["Two-phase logical state table independently distinguishes workspace preparation, session admission, running and attached", "Synthetic workspace creator/session broker return controlled receipts"]

**Pass Fail Predicate:** UI never claims isolated running work before both prerequisites; original request pins destination; retries do not duplicate workspace/session; partial resources and cleanup status remain visible.

**Required Evidence:** ["Dispatch ID and bound workspace/source revision", "Creation/session/view receipts", "No-effect versus partial-effect failure classification"]

**Stopping Condition:** Stop on incorrect running/isolation display or unauthorized cleanup; otherwise all failures produce named terminal/uncertain state

**Does Not Prove:** No performance, destructive cleanup policy or real Git worktree correctness


## T06 Target-explicit TUI against flat-list baseline

**Inputs:** {"prototype_A": "Grok-inspired peek/dispatch distinction implemented over synthetic backend", "prototype_B": "Flat list plus full-session switching", "tasks": ["reply to busy selected session", "answer stale approval", "dispatch new worktree", "close view", "interrupt foreground while child runs", "delete only named history"], "terminal_cases": ["small viewport", "keyboard only", "mouse", "Windows integrated terminal chords", "screen-reader/assistive-tech scenario when available"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Prespecified participant/task sampling and success/latency/accessibility rubric; no claim from insufficient sample"]

**Independent Oracle:** ["Blinded observer scores intended versus effective target and outcome from immutable synthetic trace", "Separate UI evaluator; no model needed"]

**Pass Fail Predicate:** Zero unauthorized/wrong-target destructive effects in safety cases; task success/error/latency and accessibility meet predeclared thresholds relative to baseline. Missing assistive-tech case stays unmeasured.

**Required Evidence:** ["Target-confusion counts with denominators", "Task times and intervals", "Accessibility observations", "Exact frontend/terminal builds"]

**Stopping Condition:** Terminate hazardous misrouting scenario; complete prespecified study or mark incomplete with exact missing cases

**Does Not Prove:** No best-in-class universal ranking, toolkit selection or production route conformance


## T07 Cross-harness disposition translation

**Inputs:** {"profiles": ["Grok current source subset", "Muse pinned MSP schema", "OpenCode V1 pinned facade subset", "OpenCode V2 dated docs subset"], "vectors": ["busy steer", "busy queue", "pending cancel after delivery", "interrupt with pending successor", "fork history at boundary", "question partially answered"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Independent exact schema/semantic profile for each source; runtime-unknown entries cannot be promoted"]

**Independent Oracle:** ["Canonical expected trace prepared by verifier; profile-local scripted fake servers", "Unsupported cells require typed incompatibility, never simulated support"]

**Pass Fail Predicate:** Each profile preserves required identity/disposition/outcome or refuses before effects. V1 never inherits V2 semantics. Experimental log replay is separate from live-only generic events. Adoption remains unknown.

**Required Evidence:** ["Profile digests and source locators", "Per-vector semantic losses/refusals", "Canonical/foreign paired traces"]

**Stopping Condition:** Stop each profile at unsupported required semantics; finish fixed profile/vector matrix with explicit unknowns

**Does Not Prove:** No real upstream qualification, account access or provider-supported stability


## T08 Imported plugin authority and disabled inertness

**Inputs:** {"synthetic_plugins": ["unknown critical manifest field", "same path changed digest", "auto-trusted pluginDirs", "skill model override", "persona worktree/model override", "inherited MCP", "hook timeout/crash/malformed/deny/argument rewrite"], "trap_channels": ["process", "network", "credential-read", "model", "timer", "watcher", "context enumeration", "quota/spend"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Trap implementations independently audited; all credentials replaced by canaries"]

**Independent Oracle:** ["Independent grant-intersection oracle", "Trap counters observe forbidden starts without running foreign plugin code"]

**Pass Fail Predicate:** Disabled/import-only produces zero trapped effects. Missing required metadata/loss refuses. Changed artifact invalidates grant. Hook allow/error or inherited MCP never expands authority; rewritten args are revalidated.

**Required Evidence:** ["Per-dimension effective grants", "Loss and incompatibility records", "Trap counters and canary egress results", "Fenced reload/revocation timeline"]

**Stopping Condition:** First forbidden effect/canary disclosure fails immediately; otherwise all fixtures assessed

**Does Not Prove:** No complete OS isolation or safety of arbitrary native extensions


## T09 D-022 stop and admitted effect boundary

**Inputs:** {"effects": ["not admitted", "admitted but not started", "local fake tool running", "remote fake effect committed", "settlement unknown"], "controls": ["Aggressive", "Full", "Lazy", "checkpoint", "interrupt", "drain", "grant revocation"], "races": ["rewritten hook arguments", "stale epoch", "child spawn between stop and process abort"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Use accepted D-022/FU-03 transition semantics; Owner resolves any remaining ambiguity before harness authoring"]

**Independent Oracle:** ["Frozen authority/effect-state oracle from accepted deterministic corpus", "Fake irreversible sink is independently observed and cannot be undone by cancellation"]

**Pass Fail Predicate:** New admissions are fenced immediately; every control has its declared scope. Committed/ambiguous effects remain committed/uncertain pending reconciliation. No process cancel or hook Stop is reported as rollback. Credential-export output path must be denied, not only direct read.

**Required Evidence:** ["Admission/grant/epoch records", "Independent effect sink receipts", "Stop disposition and unsettled obligations", "D-029 launch/output denial canary"]

**Stopping Condition:** Any unauthorized effect or false rollback fails; otherwise every effect/control/race combination has an honest outcome

**Does Not Prove:** No live-host containment, actual credential security or distributed rollback


## T10 FU-01 common-corpus language comparison

**Inputs:** {"candidates": "Existing authorized FU-01 candidates, each exact compiler/runtime pin; Grok pin only prior art", "workloads": ["decode/admit/reduce/derive WorkPacket corpus", "input-disposition races", "cold boot with adapters absent", "disabled plugin idleness", "concurrency/resource pressure"], "metrics": ["correctness floors", "tail latency", "CPU/RAM/disk", "build/test/review labor", "dependency closure"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "FU-03 frozen oracle and current FU-04 floor manifest", "No selection until independent common-corpus results and Owner decision"]

**Independent Oracle:** ["Independent language-neutral expected canonical bytes/refusals", "External resource measurement with common workloads and declared environments"]

**Pass Fail Predicate:** All mandatory vectors and authority/recovery floors first; only passing candidates enter measured tradeoff comparison. No missing metric becomes zero; no weighted score masks failed floor.

**Required Evidence:** ["Raw measurements and uncertainty", "Exact targets/toolchains/config", "Verification and developer labor logs", "Failure/refusal corpus outputs"]

**Stopping Condition:** Disqualify arm at mandatory failure; otherwise complete predeclared measurement matrix and leave selection to Owner

**Does Not Prove:** No Grok quality-to-Recursion transfer, production performance forecast or language selection


## T11 Narrow candidate provenance and matched port cost

**Inputs:** {"candidates": ["one declarative skill", "one bounded tool implementation", "one queue/actor pattern", "one render asset"], "reference": "Frozen source slice and complete dependency/assets inventory", "alternatives": ["port/adapter", "narrow vendor", "native rewrite", "avoid"]}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Rights/notice review with counsel gate when distribution matters", "Fixed acceptance behavior and labor accounting rubric before competing implementations"]

**Independent Oracle:** ["Independent source/notice correspondence review; separate acceptance reviewer for behavior", "Matched native baseline performs same required behavior; maintenance change applied to both"]

**Pass Fail Predicate:** Every included byte has provenance and applicable notice disposition. Required behavior/grant/evidence preserved. Report labor, rework, dependency/resource cost and maintenance delta; reject cheap-port claim if cost exceeds native or no acceptable port.

**Required Evidence:** ["Source/lock/asset digests", "Notice/election/modification ledger", "Accepted/rejected candidates including zero outcomes", "Complete labor and maintenance evidence"]

**Stopping Condition:** Reject candidate on unresolved required provenance/authority gap; otherwise fixed candidates and paired change complete

**Does Not Prove:** No universal license compatibility, security audit or ecosystem-wide savings


## T12 Build closure and D-028 platform handoff

**Inputs:** {"profiles": ["Windows 11 25H2 26200 Home/Pro x64 NTFS", "Windows 11 24H2 26100 Enterprise x64 NTFS", "Linux 6.12 cgroup v2 ext4", "Linux 6.6 cgroup v2 ext4", "WSL2-ext4 dev/test", "WSL2 /mnt/c dev/test"], "artifacts": ["selected feature/target dependency closure", "native tool archive expected digests", "release binary source mapping"], "fault": "approved abrupt VM reset only in disposable target"}

**Prerequisites:** ["Separate Owner-approved implementation/test session", "Exact fixture and adapter revision plus synthetic identities; no credentials or provider/network calls", "Independent verifier distinct from implementer; fixed expected outputs before test", "Separate explicit authorization for builds/installs and disposable reset target; none granted by this research", "Hermetic cache/registry and no provider credentials; source commands are not authorized execution"]

**Independent Oracle:** ["Independent target/feature SBOM and expected archive digests", "FU-04 crash/replay oracle and byte-identical canonical state", "External build/resource observer"]

**Pass Fail Predicate:** Record build/test/packaging results per exact profile; no WSL substitute for production. Reject unpinned acquisition or mismatch. Passing reset trace reproduces canonical state, while external effects retain uncertainty.

**Required Evidence:** ["Compiler/OS/filesystem identities", "Offline/build acquisition receipt", "Native dependency notices", "Reset boundary and replay digests", "Failures and skipped cases"]

**Stopping Condition:** Stop on provenance/floor/authority failure; complete declared profile matrix or name exact blocked profile

**Does Not Prove:** No physical power-loss proof, broad OS support, reproducible release or CVE freedom without corresponding evidence

