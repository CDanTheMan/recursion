# DS-20 — Linux service topology and enterprise scaling (synthesis)

## Provenance

- Raw: `raw/ds-5-DS-20-linux-scaling.md`
- Handoff: `docs/v3/prompts/research-suite-20260929/DS-20-linux-service-topology-and-enterprise-scaling.md`
- Session: Wave A Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- The report's evidence labels — **strong/source-documented**, **inferred**, **unverified/modelled** — are preserved below. Claims are attributed to "the report's sources"; no new facts or URLs are added.
- Scope: one self-contained handoff (DS-20) with no repository inspection and no machine telemetry; the original prompt left the topic unspecified, so the report scoped itself to the handoff.
- Source base: the report's Sources section lists public standards bodies, upstream project documentation, and distribution documentation reviewed through 2026-09-30.

## The question

How should Recursion v3 be provisioned and scaled on Linux so the one-writer authority invariant survives multi-user service ownership, multi-node execution, enterprise controls, failures, backup/restore, and orchestration — without selecting a store, language, consensus library, container runtime, backup tool, observability stack, or cloud? The handoff frames four linked areas: daemon/user/directory topology, fencing and reconnect, enterprise constraints, and capacity/SLO measurement. It explicitly forbids deployment, escalation resolution, and any certification claim.

## Key findings

- **Daemon topology (strong).** "One daemon per authority domain/OS account" is best read as **one logical canonical-writer service boundary**, not one independently authoritative process per role. Helpers (projection, backup, telemetry, broker) may exist but must not independently acquire canonical-write authority. Running "one unit per role" risks moving the authority problem into the filesystem. systemd can recursively correct `StateDirectory=` ownership when the top-level owner differs, so differently owned units must not share one managed canonical state tree.
- **esc-0013 (inferred recommendation; not resolved).** The root `0700` lock hierarchy versus the non-root actuator is a trust/ownership conflict, not merely a mode question. The preferred direction is to **remove backup from the writer-lock trust domain**: the authority/storage boundary exposes a read-only, consistency-defined snapshot/export that a separately constrained backup identity copies. Shared group + `2770` is a **fallback**, not the preferred architecture, because it widens the set of principals with write capability. This does not resolve esc-0013; the Owner retains it.
- **Fencing over leases (strong).** A lease or distributed lock alone is insufficient as the final safety mechanism; a stale holder can keep acting after its lease expires. A writer incarnation needs a **monotonically ordered fencing epoch/token**, and every canonical transition — or its final side-effect sink — must reject stale epochs. etcd/Raft partitions let the majority continue while the minority loses write availability; quorum loss stops writes rather than permitting two authoritative partitions.
- **Disconnected-node rule (strong).** A sleeping or partitioned node never treats its old lease as authoritative. It may finish only the already-admitted bounded local operation, may durably spool signed evidence, and may not originate a new admission or publish an authoritative transition. Reconnect revalidates enrollment, cert/trust state, protocol compatibility, current fencing epoch, GoalSpec, lease state, and `PAUSE`; spooled evidence is deduplicated and retained as historical evidence, and every derived action is re-admitted under the current fence.
- **No consensus for worker fan-out (strong).** Consensus should not be introduced merely because there are multiple workers. One canonical writer plus signed outboxes/spools and deterministic re-admission supports multi-node execution. A linearizable fencing/consensus service becomes necessary only when the Owner requires automatic writer failover or a replicated authority plane that keeps accepting canonical writes after coordinator loss. Consensus is the competing option, not the baseline.
- **Coordinator-small (unverified).** The 2-vCPU/4-GiB profile is a **target, not a demonstrated capacity point**. No host measurements were supplied, and DS-20 forbids inventing a resource ceiling. More cores help parallel boundary work but cannot parallelize a deliberately serialized authority path. The break point must come from a synthetic, zero-model benchmark sweeping admission rate, event size, projection fan-out, artifact bandwidth, fsync behavior, disconnect/spool pressure, and enterprise security overhead.
- **Enterprise MAC/FIPS (strong feasibility; certification unknown).** Deployment on SELinux/AppArmor and FIPS-enabled distros is technically feasible, but "runs on a FIPS-enabled or MAC-enforcing OS" is **not** certification. NIST validation is tied to specific cryptographic modules and operating environments. MAC denials should become explicit startup/readiness/preflight failures rather than silent degradation. Recursion compliance remains `requires-certification`.
- **Kubernetes is packaging, not a fence (strong).** StatefulSets provide persistent identity/storage lifecycle, and `ReadWriteOncePod` constrains a CSI-backed volume to one Pod, but storage attachment exclusivity does not fence stale external side effects. Kubernetes self-heals by replacing workloads, so a replacement writer must start non-authoritative and reacquire a fresh Recursion epoch before readiness. A custom Operator is justified only when Kubernetes must automate Recursion-specific transitions.
- **Observability (moderate).** Local structured evidence is the mandatory lowest-common-denominator; OpenTelemetry and Prometheus-style metrics are optional projection/export choices, not required core operation. Exported telemetry must avoid stable user names, GoalSpec text, prompts, artifact contents, provider secrets, and unnecessary membership identifiers.
- **Backup/restore (strong architectural inference).** Split the decision into "how a consistent source point is obtained" and "which tool moves and deduplicates it." Prefer a consistency-defined snapshot/export; exclude credentials, private keys, transient locks, caches, and journal noise; restore should be quarantined and must re-verify manifests and acquire a fresh fence before resuming authority. No tool (Borg/restic/ZFS) is selected.
- **Fleet preflight (unverified on latency).** A deterministic, capability-scoped, zero-model preflight should check runtime/config hashes, ownership and writability, trust-bundle/protocol versions, cert/key state, enrolled identity, and current fence/`PAUSE`/revocation. A failure quarantines that capability rather than declaring the whole daemon corrupt. The "seconds" property is not established.
- **Single-authority multi-node is not hosted multi-tenancy (inferred).** One authority across several nodes shares trust roots and a failure blast radius; it does not establish tenant isolation, tenant-separated credentials, residency, or deletion boundaries. Hosted tenancy needs a separate threat model.
- **Load shedding and watchdog (inferred).** Under pressure, preserve fencing, signature/authentication checks, canonical durability, revocation/`PAUSE`, and recovery metadata; defer optional analytics/projections/export; only then reject or backpressure new admissions. A process restart is not recovery correctness — a replacement must start quarantined and reacquire authority.
- **Enterprise networking (inferred from the report's sources).** Node/operator trust roots, public/provider TLS roots, and any corporate TLS-inspection CA should be separate trust domains. A proxy that terminates TLS and substitutes its certificate breaks end-to-end mTLS/pinning; Recursion should fail visibly instead of silently importing an egress CA into its node-authority trust root.
- **Container runtime deferred.** A container changes packaging and isolation mechanics but not the canonical-writer invariant, so the Podman-versus-Docker runtime question can stay deferred while the authority contract is specified.

## Recommendation and falsifier

The report recommends a **no-selection, no-deployment** outcome: define decision criteria, keep the single-writer/no-consensus design as the baseline, fence every writer incarnation, decouple backup from the writer mutex, treat local structured evidence as mandatory, use StatefulSet only as lifecycle/storage packaging, and treat FIPS/data-residency/deletion/certification claims as `requires-certification`. Each direction names a competing option (separate authoritative service per role, shared writable state/group, lease-only ownership, replicated Raft authority, mandatory OTel/Prometheus core, PVC/Pod as authority lock, Operator from first release, label-inferred compliance).

The decisive falsifiers are explicit: a required privilege/failure boundary that still preserves exactly one writer; a store that formally requires multiple OS principals to write one canonical tree; a storage design that cannot expose a consistent snapshot/export within RPO/RTO; effects proved atomic inside one linearizable transaction; an Owner HA requirement for continued canonical writes after coordinator loss; and a safety-relevant trust/revocation transition that can change without expiring any preflight cache input.

The report's highest-leverage point is that the consequential decision is not "etcd or no etcd", "Borg or restic", or "systemd or Kubernetes" but the **availability and authority contract**: whether one fenced canonical writer may be temporarily unavailable during coordinator failure, or whether automatic write continuation is mandatory. Once that is explicit, consensus, orchestration, and recovery options become falsifiable rather than fashion-driven.

## What this does not prove

- No language, store, consensus library, container runtime, backup tool, observability stack, or cloud is selected.
- No topology or capacity value is measured; every operational mode is labelled modelled or unknown.
- esc-0013 is not resolved and no escalation is modified.
- No FIPS, MAC, OS, container, or Kubernetes certification is claimed.
- The "seconds" preflight duration is unverified until measured.
- Single-authority multi-node operation is not evidence of safe hosted multi-tenancy; tenant isolation needs a separate threat model.
- No numeric SLO, watchdog timeout, or recovery decomposition is established before measurement.
- No unit names, directory modes, default product configuration, or exact install procedure are fixed.
- Nothing is deployed, installed, provisioned, or written into a protected path.

## Open Owner decisions

- Must canonical writes stay available automatically after total loss of the active coordinator? (decides consensus necessity)
- Is an authority boundary always one-to-one with an OS account, or can one service identity host several separately fenced authority instances?
- Can backup be defined entirely around a daemon/storage snapshot/export interface (which would let esc-0013 leave backup outside writer locking)?
- What RPO/RTO, certificate lifetime/revocation freshness, and numeric coordinator-small SLOs apply?
- Is Kubernetes an official deployment target or merely a compatibility target?
- Is hosted multi-tenancy in v3 scope, and if so, under what isolation threat model?
- Is node mTLS required to work through TLS-inspecting corporate proxies?
- Which telemetry may leave an authority domain, and what constitutes deletion proof for artifacts, backups, and telemetry?
- Which combinations need formal certification rather than engineering evidence?

## Relevance to later waves

The report sets prerequisites for later milestones: validate the ownership matrix on a disposable host before the service shape hardens; build a deterministic fault harness (partition, sleep/wake, offline revocation, `PAUSE`, GoalSpec change, duplicate/reordered envelopes, forced writer candidates) before the authenticated node fabric; benchmark coordinator-small before any adaptive optimization; run one enforcing SELinux and one enforcing AppArmor installation before enterprise soak; and treat restore testing as part of backup evidence rather than an optional postscript.

Its no-selection verdict means later waves should consume these criteria and the fault matrix as constraints, not as a chosen deployment. Any wave that would select a store, consensus library, container runtime, backup tool, or observability stack is making an Owner decision this report deliberately left open.
