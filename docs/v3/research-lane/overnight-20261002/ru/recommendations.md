# R-U recommendation ledger

All candidates are proposals. Competitors preserve accepted invariants; unsafe variants are separate negative controls. No placement or product is selected.

## RU-R01 — Typed meet and budget-preserving delegation

Candidate: Authenticated opaque receiver references plus a central typed meet compiler

Conforming competitor: Authenticated grant tokens plus independent typed receiver checks and a shared reservation ledger

Decisive falsifier: A child or sibling union admits any verb/resource/time/budget unavailable to its parent

Unsafe negative control: String capability names or publisher trust used as authority

Passing does not prove: Does not prove all receiver implementations, confidentiality or complete cost accounting

Handoffs: RU-H01, RU-H02, RU-H20

## RU-R02 — Pre-execution default deny and complete mediation

Candidate: OS-denied ambient access with broker-only typed operations

Conforming competitor: OS-enforced direct object grants plus minimal independently checked broker APIs

Decisive falsifier: Any direct or helper path effects an undeclared operation

Unsafe negative control: Guest-side policy hook only

Passing does not prove: Does not prove kernel/runtime escape resistance

Handoffs: RU-H01, RU-H03, RU-H05, RU-H09

## RU-R03 — Enforce aggregate resource envelopes externally

Candidate: Nested OS task/party envelopes plus mediated exceptional resources

Conforming competitor: Fully mediated runtime resource handles backed by an outer OS envelope

Decisive falsifier: A mandatory hard cap is only guest-reported or is exceeded beyond frozen tolerance

Unsafe negative control: Per-plugin counters with no aggregate task reservation

Passing does not prove: Does not imply identical Windows/Linux accounting units or a performance win

Handoffs: RU-H08, RU-H26

## RU-R04 — Revoke without restarting the whole task

Candidate: Per-operation revocable receiver handles

Conforming competitor: Fence and replace only the affected party with narrower immutable grant

Decisive falsifier: A post-fence operation succeeds through old handle/connection or stale epoch

Unsafe negative control: Change ACL and assume all open handles are revoked

Passing does not prove: Does not roll back an already committed external effect

Handoffs: RU-H11, RU-H13

## RU-R05 — Qualify exact floor semantics

Candidate: Per-floor conformance compiler and independent semantic corpus

Conforming competitor: Common narrow broker IR with per-floor proof obligations and explicit unsupported arms

Decisive falsifier: Same advertised grant permits materially broader effects on one exact floor

Unsafe negative control: Best-effort primitive downgrade retains strong badge

Passing does not prove: Does not qualify other patches, architectures or production WSL

Handoffs: RU-H23

## RU-R06 — Keep containment and content authority separate

Candidate: OS/runtime effect boundary plus receiver grant checks

Conforming competitor: Equivalent independently scoped service boundary plus receiver grant checks

Decisive falsifier: Untrusted output or isolated guest obtains authority through presentation or a deputy

Unsafe negative control: Safe-looking prompt or successful sandbox launch treated as authorization

Passing does not prove: Does not prove injection detection or universal confidentiality

Handoffs: RU-H06, RU-H10

## RU-R07 — Observe complete rooted ownership for Full Stop

Candidate: Birth containment plus independent scope/identity reconciliation

Conforming competitor: Qualified gated launch supervisor plus independent start and ownership inventory

Decisive falsifier: Owned process escapes, restarts after fence or is reported stopped without evidence

Unsafe negative control: Kill PID/process group, or kill unrelated shared server sessions

Passing does not prove: Does not guarantee bounded kernel-stuck process exit or external rollback

Handoffs: RU-H07, RU-H12, RU-H13

## RU-R08 — Disabled runtime is effect-free; metadata cost explicit

Candidate: Prebuilt bounded catalog with no payload loading

Conforming competitor: Bounded on-demand manifest parsing in an isolated inventory service

Decisive falsifier: One forbidden activation/effect occurs, or metadata limit is breached

Unsafe negative control: Hidden initialization to make lazy loading appear ready

Passing does not prove: Does not prove zero CPU/disk cost or all-time inertness

Handoffs: RU-H14, RU-H16

## RU-R09 — Use independent sensitive observations

Candidate: Event tracing plus object-state reconciliation

Conforming competitor: Isolated observer with challenge canaries and stable-identity queries

Decisive falsifier: Known-bad control is missed or incomplete trace becomes pass

Unsafe negative control: Guest self-report or missing log as absence proof

Passing does not prove: Does not prove absence beyond the finite corpus/window

Handoffs: RU-H01, RU-H07, RU-H14, RU-H26

## RU-R10 — Separate evidence admission from execution authority

Candidate: Consumer verifies bundled SBOM/signatures/attestations against pinned expectations

Conforming competitor: Locally approved immutable evidence manifest plus independent reconstruction under same required evidence policy

Decisive falsifier: Artifact with missing mandatory evidence reaches strict execution, or evidence changes grant

Unsafe negative control: Signed means safe/authorized

Passing does not prove: Does not establish publisher honesty, rights or route entitlement

Handoffs: RU-H15, RU-H20, RU-H25

## RU-R11 — Offline decisions bind explicit trust snapshots

Candidate: Provisioned release evidence bundle and sequential root updates

Conforming competitor: Independent signed local approval catalog with equivalent root/version/expiry rules

Decisive falsifier: Artifact-provided root accepted or stale snapshot called globally current

Unsafe negative control: Fetch whatever key URL untrusted metadata supplies

Passing does not prove: Does not discover unseen revocations or establish globally consistent logs

Handoffs: RU-H17

## RU-R12 — Bound advisory maintenance and preserve provenance

Candidate: Opt-in local mirror of dated public advisory snapshots

Conforming competitor: Operator-imported signed offline advisory snapshots

Decisive falsifier: Incorrect ecosystem/version mapping clears a vulnerable fixture or disabled maintenance fetches

Unsafe negative control: Continuous hidden updates or no-findings means safe

Passing does not prove: Does not detect unpublished vulnerabilities

Handoffs: RU-H18, RU-H14

## RU-R13 — Quarantine and recover without reviving bad code

Candidate: Reverified compatible rollback artifact with new grant epoch

Conforming competitor: Forward recovery to independently admitted replacement

Decisive falsifier: Revoked digest reactivates or rollback silently expands authority/state access

Unsafe negative control: Disable anti-rollback protection or erase incident history

Passing does not prove: Does not reverse leaked data or settled external effects

Handoffs: RU-H21, RU-H22

## RU-R14 — Corroborate provenance and publisher claims

Candidate: Independent reproducible reconstruction plus same behavioral gate

Conforming competitor: Separated builder/reviewer attestations plus same behavioral gate

Decisive falsifier: Unexpected build input accepted or complete-looking forged inventory gains privilege

Unsafe negative control: One self-signed provenance document as safety guarantee

Passing does not prove: Does not detect every malicious but faithfully built source or compromised trust platform

Handoffs: RU-H15, RU-H25

## RU-R15 — Prove non-origin authority as a metamorphic invariant

Candidate: Central typed meet compiler and immutable minimal grant IR

Conforming competitor: Independent receivers recompute the same meet from validated bindings

Decisive falsifier: Changing only origin/signature/cache produces a larger allowed operation set

Unsafe negative control: First-party exemption or historical-success grant cache

Passing does not prove: Does not prove every future grant dimension is implemented correctly

Handoffs: RU-H20, RU-H21

## RU-R16 — Evaluate in-process only within admissible scope

Candidate: Immutable trusted contributor registry, or separately verified restricted evaluator outside K

Conforming competitor: Same trusted contributor in P3; untrusted evaluator compared with P2/P3

Decisive falsifier: Guest accesses writer memory/FFI or blocks canonical control

Unsafe negative control: Arbitrary native plugin shares privileged writer process

Passing does not prove: Does not establish untrusted native in-process isolation or per-party resource parity

Handoffs: RU-H01, RU-H08, RU-H26

## RU-R17 — Evaluate Wasm/WASI with scoped imports

Candidate: P2 in independent bounded host with typed imports and outer process envelope

Conforming competitor: P3 OS-sandboxed worker with same broker and grants

Decisive falsifier: Import/native extension bypasses policy or callback cannot be preempted/revoked

Unsafe negative control: Unrestricted preopens/raw host exec

Passing does not prove: Does not establish a specific runtime or performance advantage

Handoffs: RU-H01, RU-H05, RU-H08, RU-H11

## RU-R18 — Evaluate OS-sandboxed process composition

Candidate: P3 with birth containment, protected objects and egress mediation

Conforming competitor: P2 isolated runtime host with equivalent capabilities

Decisive falsifier: First instruction escapes scope or denied FS/network operation succeeds

Unsafe negative control: Plain same-user child plus Job/cgroup only

Passing does not prove: Does not remove kernel/helper TCB or prove arbitrary CLI compatibility

Handoffs: RU-H03, RU-H05, RU-H07, RU-H09

## RU-R19 — Evaluate container composition at actual floors

Candidate: P4 minimal namespace/image/runtime composition without host sockets

Conforming competitor: P3 native process security with immutable dependency closure

Decisive falsifier: Host/daemon access or required Windows support relies on production WSL

Unsafe negative control: Privileged host-mount/host-network container

Passing does not prove: Does not establish VM-strength isolation or native Windows support

Handoffs: RU-H03, RU-H07, RU-H09, RU-H23

## RU-R20 — Evaluate remote boundary with receiver enforcement

Candidate: P5 independently enrolled host validates grants, epochs and receipts

Conforming competitor: Dedicated local P3/P4 host under same privacy/capability contract

Decisive falsifier: Remote stale epoch accepted, data leaks or partition becomes false stopped

Unsafe negative control: SSH delivery treated as settlement

Passing does not prove: Does not qualify real remote host from local simulation or replace required local execution

Handoffs: RU-H24

## RU-R21 — Rank only after hard gates and useful task acceptance

Candidate: Hard-gate then Pareto comparison of matched candidates

Conforming competitor: Hard-gate then preregistered responsiveness/efficiency/completion ranking

Decisive falsifier: Preference survives a hard invariant failure or hides semantic task losses

Unsafe negative control: Weighted safety score trades a leak for speed

Passing does not prove: Does not select a runtime or demonstrate a measured advantage

Handoffs: RU-H23, RU-H26

## RU-R22 — Keep guest work away from writer and Stop

Candidate: Bounded queues and independently supervised parsers

Conforming competitor: Isolated ingress workers plus reserved control scheduler and bounded channels

Decisive falsifier: Blocked guest/output/parser prevents fenced Stop/control within frozen test bound

Unsafe negative control: Inline untrusted callbacks on canonical writer

Passing does not prove: Does not prove liveness under kernel/admin or physical-host failure

Handoffs: RU-H08, RU-H16, RU-H26
