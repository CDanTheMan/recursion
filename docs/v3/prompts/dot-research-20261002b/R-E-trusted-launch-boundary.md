---
title: R-E — Operator-provisioned trusted launch boundary
status: ready-for-explicit-invocation
last-updated: 2026-10-02
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# R-E — Operator-provisioned trusted launch boundary

This is a design-research handoff for accepted Owner decision D-029, with D-021 and D-028 as
constraints, and the gap register in [GAPS.md](../../research-lane/GAPS.md).

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone agent harness and a harness
orchestrator that delegates through other harnesses. Hermes-led control was retired on
2026-09-28 (state/DECISIONS.md D-017); Hermes is an optional upstream integration, not the
executive control plane. Workers are bounded executors. An implementer's own PASS is never
acceptance; independent review is required, and missing verification is never a pass.
`CONTROL_PLANE.md` is the operative constitution; a research session may propose amendments
but must never edit it. No research session performs implementation,
provider/model/authentication/configuration changes, spending, deployment, publication or
merge.

Scope: this repository is the Recursion product only. Unrelated repositories, curricula,
captures and datasets are out of scope. Do not reopen accepted Owner decisions.

Evidence discipline: prefer primary public sources (standards, official product/API docs,
pinned source, licenses, peer-reviewed work). Classify every consequential claim as
source-documented, locally observed, inferred or unverified; keep `unknown` distinct from
zero. Model consensus and vendor marketing are not evidence. Every recommendation needs a
competing option and a decisive falsifier, and must name what it does not prove. Do not
request or display hidden chain-of-thought.

Privacy: a public Deep Research session receives only public or synthetic briefs — never
secrets, credentials, personal data, private repository content, local paths, or
account/infrastructure identifiers.

### Lane context

- D-021 accepts delegation over credential intermediation: Recursion must not hold, copy or
  relay provider credentials it was not explicitly granted; where possible it delegates a request
  to a user-authenticated local tool or harness rather than intermediating login, because driving
  the user's already-authenticated CLI is the preferred route over capturing OAuth tokens.
- D-029 chooses option B over policy-only non-intermediation: Recursion invests in an
  operator-provisioned trusted launch boundary outside Recursion's readable domain so that the
  strong "never holds or reads provider credentials" claim is real, not aspirational. Recursion
  is a trusted orchestrator the user leans on to define and operate their own space. If a
  supported platform profile cannot enforce the boundary, that profile must be labeled
  "non-intermediation-by-policy only" rather than claiming the strong property.
- D-021's prior analysis (carried as R-B section 6) found that same-user processes can still read
  home directories, environment variables, OS keychains and process memory, so simply spawning the
  user's CLI yields only policy-level non-intermediation, not a provable absence of credential
  access.
- D-028 pins the platform floors this lane must respect: Windows 11 25H2 (build 26200) Home/Pro
  and 24H2 (build 26100) Enterprise, x64 primary with Arm64 a later case; Linux kernel 6.12 LTS
  primary with 6.6 LTS a compatibility minimum, cgroup v2 required, ext4; WSL2 development/test
  only, never production; canonical state on local NTFS or local ext4 only, SMB/NFS out of scope
  for the first release. A design must state which floor it assumes and what it does below it.
- D-022 adopts one pause/stop vocabulary across configuration, the formal model and the broker:
  three Stop modes — Aggressive / Full / Lazy — plus `checkpoint`, `interrupt` and `drain`. Any
  boundary design must express how the boundary process is checkpointed, interrupted and drained
  with that vocabulary; a source interrupt, socket close or killed PID is not external rollback.
- Evidence status: no trusted-launch-boundary prototype exists. All enforcement claims below are
  hypotheses with falsifiers, not measured facts.

## Purpose

Produce the decision-ready evidence pack that determines whether, and by what platform-specific
primitives, Recursion can uphold a strong "never holds or reads provider credentials" claim
through an operator-provisioned trusted launch boundary. The lane defines the threat model, maps
the available Windows and Linux isolation primitives, proposes per-platform boundary design
candidates, compares the strong boundary against "non-intermediation-by-policy only", and
specifies a provider-free conformance test that proves zero secret bytes appear in any
Recursion-readable data. It does not select a language, store, framework, sandbox product or
vendor, does not implement the boundary, and does not call any provider.

## Authority and boundaries

The authority, scope and privacy constraints in `## Baked context` are the operative limits.
Recursion is a standalone agent harness and a harness orchestrator that delegates through other
harnesses; Hermes-led control was retired on 2026-09-28 and Hermes is an optional upstream
integration, not the executive control plane. Propose amendments to the operative constitution;
never edit it. Public Deep Research receives only public or synthetic briefs. **DO NOT select a
language, package manager, sandbox, isolation product, store or vendor.** Do not claim any
primitive provides a guarantee that is not documented by its vendor or standard. No credential is
collected, displayed, copied, relayed, decrypted or attempted; no login, provider or paid route
call occurs. Do not decide an Owner question recorded in D-021, D-022, D-028 or D-029. Treat
every named OS primitive (AppContainer, Job Objects, DPAPI, Linux user namespaces, cgroup v2,
kernel keyring) as prior art to be cited from public sources, not as endorsed or selected
components.

## Inputs to read

None. This handoff is self-contained; the rescope and prior conclusions are summarized in
`## Baked context` above. Do not assume repository, connector or private-source access.

## Research questions

### Threat model and the claim to prove

1. What exactly must "Recursion never holds or reads provider credentials" mean as a testable
   property, stated as an adversary model: which principal runs Recursion, which principal owns
   the credential, and what can a compromised, buggy or merely curious Recursion process attempt
   — home-directory reads, environment inspection, keychain/secret-service queries, process-memory
   reads, debugger attach, file-handle inheritance, IPC snooping, log capture — with a documented
   source for each capability?
2. What is the documented distinction between (a) a boundary that structurally denies Recursion
   access to credential bytes and (b) policy-level non-intermediation in which Recursion chooses
   not to read them but could? Which assurance does each actually provide, and what does neither
   provide (for example a compromised kernel, a malicious CLI, or a credential presented directly
   to the provider by the CLI)?
3. What is the operator's part of the contract — what does the user provision, authorise and
   revoke, and what residual trust must the user place in Recursion under each model?

### Windows primitives

4. For Windows at the D-028 floor, what do documented primitives offer for launching the
   user-authenticated CLI/tool under a boundary Recursion cannot read across: a separate principal
   or SID, AppContainer and low-integrity tokens, Windows Job Objects, DPAPI and Credential
   Manager scope isolation, DACLs and mandatory integrity labels, restricted tokens, and
   privileged-service launch? For each, what is documented, what is inferred, and where is the
   honest `unknown`?
5. Which Windows designs can hold an opaque launch handle/token or named-pipe handle so that
   Recursion starts the CLI and observes only its stdout/JSON, without the credential-bearing
   environment or filesystem being readable in Recursion's security context?
6. What are the documented limits: same-session assumptions, shared desktop, handle inheritance
   mistakes, debug-privilege attach (SeDebugPrivilege), accessibility/injection surfaces, Win32
   API gaps, and anything that makes a strong boundary unachievable on the stated floor?

### Linux primitives

7. For Linux at the D-028 floor, what do documented primitives offer: unprivileged and privileged
   user namespaces, mount and PID namespaces, cgroup v2 resource and process control, DACLs,
   capability dropping, seccomp filters, the kernel keyring and Secret Service, and
   ptrace/yama/`/proc/<pid>/mem` memory-read restrictions? For each, what is documented, inferred
   or `unknown`?
8. Which Linux designs can launch the user CLI in a distinct security context, deliver the secret
   to that context without exposing it to Recursion, and let Recursion read only the CLI's own
   stdout/JSON — including secret-stripped environments, scoped artifact and control channels,
   and a one-way or handle-passed launch token?
9. What are the documented limits on a local-only, no-root, ext4, cgroup v2 host: user-namespace
   restrictions on the target distributions, keyring session scope, Secret Service daemon trust,
   ptrace exceptions, and container/namespace escapes or information leaks that undermine the
   claim?

### Competing options, falsifiers and conformance

10. What is the honest comparison between the strong boundary and "non-intermediation-by-policy
    only": for each platform, what does the strong boundary buy, what does it cost in complexity,
    operability and failure modes, and which profile must fall back to policy-only labeling?
11. What are the competing option sets (separate OS principal; container/namespace; handle-passed
    opaque token; broker with no shared address space; policy-only) and what decisive falsifier
    would reject each design?
12. What provider-free, deterministic conformance test proves zero secret bytes appear in
    Recursion-readable data — a synthetic sentinel-secret fixture planted where the real
    credential would live, a hostile scan of Recursion's readable filesystem, environment, logs,
    artifacts, memory snapshot and IPC, and explicit pass/fail oracles, with the boundary disabled
    and enabled as the required contrast?

## Deliverable

A source-pinned report containing: a testable threat model that states the adversary, the
capabilities and the precise claim; a per-platform primitive matrix (Windows and Linux) whose
cells are source-documented, inferred or `unknown`; per-platform design candidates with competing
options, costs and decisive falsifiers; an explicit disposition for each supported profile —
strong boundary or "non-intermediation-by-policy only"; a mapping of the boundary lifecycle onto
the D-022 vocabulary (`checkpoint`, `interrupt`, `drain`, Aggressive / Full / Lazy Stops); and a
provider-free conformance-test design using a synthetic sentinel to prove zero secret bytes appear
in Recursion-readable data, with enabled/disabled contrast, oracles and stop conditions. Each
recommendation names a competing option, a decisive falsifier and what it does not prove. No
language, store, framework, sandbox product or vendor is selected.

## Non-goals

- No selection of a language, package manager, sandbox, isolation product, store or vendor.
- No boundary implemented, no privilege used, no credential collected, decrypted or displayed.
- No claim of a guarantee beyond what a vendor or standard documents; unproven cells stay
  `unknown`.
- No provider, model, network, login or paid route call.
- No legal conclusion about whether any boundary satisfies provider terms (that belongs to R-H and
  counsel).
- No reopening of D-021, D-022, D-028 or D-029.
- No modification of a protected path or of any accepted Owner decision.

## Completion gate

- The claim is restated as a testable property with an explicit adversary model and named
  capabilities, each with a source.
- Windows and Linux primitive matrices are complete for the named primitives, with every cell
  source-documented, inferred or `unknown`.
- Each supported platform profile has a disposition: strong boundary or
  "non-intermediation-by-policy only".
- At least two competing designs per platform are compared with cost, failure modes and a
  decisive falsifier.
- The boundary lifecycle is expressed in the D-022 vocabulary (`checkpoint`, `interrupt`,
  `drain`, Aggressive / Full / Lazy Stops), and no interrupt is described as external rollback.
- The conformance test is provider-free, uses a synthetic sentinel, scans all
  Recursion-readable surfaces, and defines pass/fail oracles and stop conditions.
- Every recommendation names a competing option and what it does not prove.
- Protected paths are untouched; privacy and secret scan are clean.
