---
title: DS-20 — Linux service topology and enterprise scaling
status: ready-for-explicit-invocation
last-updated: 2026-09-30
parent-goal: goal-recursion-v3-harness-orchestrator
invocation: self-contained; supplying this document launches the research
---

**Research directive.** You are the lead researcher. This document is your complete brief and your explicit authorization to research; it is not inert. Conduct the investigation described below and produce the deliverable, then check every item of the completion gate. Do not ask which topic to research, do not request further approval, and do not return a scoping plan, research plan, methodology, timeline, outline, or clarification request — those are not acceptable outputs. Execute the research now and return the final report with findings and citations; if you catch yourself planning, convert the plan into the research immediately.

# DS-20 — Linux service topology and enterprise scaling

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. Supplying this document is the invocation; it makes no repository or provider call on its own.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Recursion is a standalone harness and harness orchestrator; Hermes is a retired control plane and an optional upstream integration. Workers are
bounded executors. An implementer's own PASS is never acceptance; independent review is
required, and missing verification is never a pass. `CONTROL_PLANE.md` is the operative
constitution; a research session may propose amendments but must never edit it. No research
session performs implementation, provider/model/authentication/configuration changes,
spending, deployment, publication or merge.

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

- Recursion v3's design target is one daemon per authority domain/OS account with one serialized canonical admission path and exactly one fenced writer per aggregate; read-only projections are disposable.
- The privileged kernel is four pure functions (`decode`/`admit`/`reduce`/`derive_work_packet`) with no filesystem, network, process, provider or wall-clock access; storage, IPC, engines and views call the boundary.
- `esc-0013` is a recorded open escalation: a lock directory created root-first at mode 0700 permanently excludes a non-root participant while a root-run backup and a non-root actuator contend for one lock. It is cited as input only and is not resolved here.
- `E-FHAR2-103` is the log/projection/artifact/IPC profile: JSONL/JSON-Sequence plus a content-addressed store versus single-writer SQLite WAL metadata plus the same store, with all store bytes counted and storage explicitly not authority.
- `E-FHAR2-104` is the terminal/process broker contract; the broker owns process identity, containment, cursors, leases and recovery.
- The security direction specifies a zero-model enrollment preflight cached against runtime hash, configuration hash, trust-bundle and protocol versions, certificate state and permission snapshot; the full conformance suite is mandatory for official release evidence but optional for an individual install, and a failure quarantines only the affected remote capability.
- Milestone 7 delivers the authenticated node fabric (enrollment, trust-root/operator separation, signed envelopes, replay protection, disconnect spooling, capability quarantine and cached preflight); Milestone 8 delivers adaptive optimization; Milestone 9 delivers integration, editions and private soak.
- Coordinator-small is a 2-vCPU/4-GiB class target; single-authority multi-node operation is distinct from hosted multi-tenant isolation, and a disconnected node may finish only its last valid bounded local operation and spool signed evidence for revalidation.
- `OR-018` ratifies Option 2 (a native deterministic kernel with typed adapters); `OR-019` keeps canonical authority/recovery with Recursion and forbids an external account/session/harness from owning canonical identity.
- **UNRESOLVED, Owner-owned:** the implementation language, store, consensus library, container runtime, backup tool and observability stack are unselected; no deployment is authorized.

## Purpose

Produce the evidence needed for the Owner to decide how Recursion v3 is provisioned and scaled on Linux — daemon topology, systemd unit/users/groups, resource budgets, single-authority multi-node operation, and enterprise deployment — before Milestones 2, 7, 8 and 9 commit to a deployment shape. This is blocking because the current deployment already runs several processes as different users that contend for one lock (`esc-0013` in the open-escalation register), because the ratified architecture target expects one daemon per authority domain/OS account, and because multi-node enrollment, split-brain and offline revocation must be designed before any node fabric is built. Nothing here selects a runtime, store, consensus library, container runtime or cloud. This is research only with an explicit no-deployment rule; procurement/compliance research carries no certification claim.

## Authority and boundaries

The authority, scope and privacy constraints that govern this lane are restated in `## Baked context`; treat them as the operative limits. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. **DO NOT select a language, store, framework, renderer or plugin runtime.** The Owner decides. No claim that a distro, kernel, systemd version, SELinux policy or FIPS module is certified follows from this file. The open-escalation and decision registers are read-only here and may not be edited; existing escalations are cited, never resolved by this lane.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

### Daemon topology, units and ownership

1. What daemon topology implements "one daemon per authority domain/OS account" (the ratified architecture target): one unit, one unit per role, or one unit per account/domain — and how does it keep exactly one canonical writer?
2. How should the deployment units define their users/groups and directories — what users/groups, `RuntimeDirectory`, `StateDirectory`, `LogsDirectory`, and what directory modes — so the documented root-run backup and the non-root actuator can both be correct rather than in conflict?
3. Given the open escalation `esc-0013` (a lock directory created root-first at mode 0700 permanently locks out non-root participants; a root-run backup contends with a non-root actuator and no shared group exists), what are the competing resolutions — a shared group with `2770`, a differently-owned-but-safe lock directory, or running the backup non-root — and what does each cost to the trust model?
4. Where do canonical state, code, logs and XDG-style locations belong for a root-owned system checkout, and how is the code/config/state/credential split kept from silently collapsing into one writable tree?

### Scaling and topology

5. Vertical vs horizontal scaling for the coordinator: what exactly scales with CPU/RAM (event append, projections, observers), what does not (the single-writer admission path), and where does the 2-vCPU/4-GiB coordinator-small profile become the limit?
6. Single-authority multi-node operation vs hosted multi-tenancy: what changes in the authority plane, privacy/egress and isolation when one authority spans several nodes versus several tenants share one service?
7. How are enrollment, trust-root/operator separation, signed envelopes and the lightweight preflight (the security direction) sized for an enterprise fleet, and what is the minimum honest preflight that completes in seconds with zero model tokens?

### Coordination and failure

8. Leader election and fencing: what incarnation/fencing-token design guarantees a stale holder cannot authorize a transition, and how do `etcd`/Raft, an embedded consensus library, or a single durable lock each fail under partition and clock skew?
9. Split brain with a sleeping laptop or a network partition: what is the required behavior for a node that wakes holding a stale lease, and how is "finish only the last bounded local operation and spool signed evidence" enforced without allowing a disconnected publish?
10. Offline revocation, duplicate delivery and spool/spool-reconcile: what protocol makes re-admission after reconnect revalidate GoalSpec/fence/lease/PAUSE before accepting spooled evidence or any derived action?
11. Consensus necessity: when is consensus genuinely required (multi-writer coordination, membership) versus avoidable (single-writer authority + outbox), and what is the failure mode of adopting consensus where it is not needed?

### Enterprise install and security

12. Enterprise distros (RHEL/Ubuntu/Debian), SELinux vs AppArmor policy, FIPS-mode crypto constraints, and air-gapped installs — what breaks, and how is each denial made visible rather than swallowed?
13. Proxies, DNS/TLS, and certificate management for node and provider egress: what must be configurable per site, and where does a corporate TLS-inspection proxy silently break pinning or mTLS?
14. Observability in an enterprise: `journald` vs OpenTelemetry vs Prometheus for the required telemetry signals, and how is telemetry kept local/minimal without leaking private membership?
15. Backup and restore operations: `restic` vs `borg` vs ZFS snapshots for the state+artifact set, consistency of a snapshot taken during a live append, and key/credential exclusion?

### Containers and orchestration

16. Containers (`podman`/`docker`) and Kubernetes: when is the daemon a `StatefulSet` vs a custom operator, how are PVs and network policy used for one-authority state, and where does secrets injection conflict with the "no secrets in state/logs" rule?
17. Rollout/rollback in an orchestrated environment versus the ratified update-mode table (`interrupt_save_update_resume` etc.): what does the platform do that the update contract forbids, and how is that fenced?

### Capacity and SLO

18. Capacity, queueing and SLO modelling: what is the admission equation (from the performance plan) on a real Linux host, what load-shedding order is safe (analytics/indexing first, integrity last), and what watchdog and bounded-downtime behavior is acceptable?
19. Procurement/compliance as research only: which claims (auditability, data residency, deletion proof) can be supported by the design, and which must be explicitly `unknown` or `requires-certification` with no claim made here?

## Deliverable

A source-pinned report containing: a claim table (claim, source, version/date, classification, confidence, expiry trigger); a topology and ownership matrix (units, users/groups, directories, modes) with every cell measured, modelled, or `unknown`; a fault matrix for partition, sleeping laptop, duplicate delivery, offline revocation and split brain; explicit cost/scale estimates with denominators (per node, per 100 identities, per event/sec); an enterprise-install feasibility table with no certification claim; a recommendation tied to a named competing option and decisive falsifier; and open Owner questions. No implementation is selected as a product default and nothing is deployed.

## Non-goals

- No deployment, install, container build or cluster creation.
- No systemd unit, `sysusers.d`/`tmpfiles.d` or inventory change.
- No selection of an orchestrator, consensus library, container runtime, backup tool or observability stack.
- No provisioning decision written into the open-escalation or decision registers or any protected path.
- No resolution of `esc-0013` or any other open escalation; they are cited as inputs only.
- No procurement, compliance or certification claim.
- No provider, model, DNS, registry or paid network calls.
- No numeric SLO, budget or resource ceiling invented before measurement.
- No modification of protected paths, the open-escalation register or construction scripts.

## Completion gate

- Every systemd, `sysusers.d`, `tmpfiles.d` and directory-mode claim is pinned to a specific version/date or marked `unverified`.
- The lock-directory multi-user problem from `esc-0013` is analysed against the recorded deployment roles (a root-run backup service, a non-root actuator service and the declared users/groups) with the competing resolutions and their trust costs.
- Split brain, sleeping laptop, duplicate delivery and offline revocation each have a specified behavior and a falsifier.
- Consensus is justified only where required, with the no-consensus design stated as the competing option.
- Enterprise install claims (SELinux/AppArmor, FIPS, air-gap, proxy/TLS) carry no certification claim and name their failure mode.
- Every recommendation names a competing option and a decisive falsifier, and preserves an explicit no-selection/no-deployment outcome.
- Observability, backup/restore and container/Kubernetes sections tie to the telemetry contract, the canonical-state contract and the ratified update modes.
- Protected paths are untouched; privacy and secret scan are clean.
