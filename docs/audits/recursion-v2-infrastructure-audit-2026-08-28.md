---
title: Recursion v2 infrastructure audit
type: audit
status: complete
observed: 2026-08-28
scope:
  - local Recursion repository
  - live gs-recursion Hetzner host
  - registered project clones and publication topology
  - engine, sandbox, routing, evidence, and capacity implementation
  - Cursor CLI, Cursor Cloud Agents, and Grok Bot integration surfaces
related:
  - CONTROL_PLANE.md
  - ANCHOR.md
  - docs/architecture.md
  - docs/plans/engine-plugin-architecture.md
  - docs/plans/recursion-v2-execution-fabric.md
---
# Recursion v2 infrastructure audit — 2026-08-28

This is the read-only baseline for the v2 execution-fabric plan. Three parallel audit arms
inspected the live Hetzner host, the worker/routing implementation, and repository topology.
No production file, service, credential, ref, cron entry, routing flag, or runtime state was
changed.

Every completed live audit batch ended with the exact PAUSE hash:

`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`

All live facts below are observations, not timeless configuration. The executing session must
repeat the named preflight checks before relying on them.

## Executive conclusion

Recursion has a strong single-host control-plane and worker-safety foundation. It does not yet
have the configuration and protocols required to be the provider-neutral, multi-repository,
multi-host basis for all development.

The existing implementation should be extended rather than replaced. The missing layer is a
declarative execution fabric joining:

- engines and models;
- provider accounts and subscription/quota pools;
- hosts and sandbox profiles;
- immutable task assignments;
- repository branch and publication policies;
- remote result reconciliation and canonical evidence.

Hetzner should remain the authoritative coordinator and a light Linux worker. Cursor Cloud should
provide disposable isolated workers. Grok Bot should provide persistent supervisory arms using
its separate weekly allowance. Specialized Windows, GPU, or live-oracle work remains on registered
machines with the required capabilities.

## Live Hetzner baseline

Observed host capacity:

| Item | Observation |
|---|---|
| CPU | 2 vCPU |
| RAM | 3.7 GiB |
| Swap | 2 GiB |
| Free disk | approximately 18 GiB |
| Uptime | approximately 23 days |
| Active workers | none |

The box is appropriately sized for durable state, scheduling, reconciliation, messaging,
verification, publication, and light worker processes. It should not become the universal build
host.

Queue state at audit time:

| State | Count |
|---|---:|
| pending | 0 |
| running | 0 |
| succeeded | 76 |
| failed | 25 |
| legacy | 6 |

Cron retained the expected awareness cadence: health/awareness and fallback checks every three
hours, decisions every six hours, and a forced daily brief. `cycle.sh` preserved local awareness
under PAUSE. No active project worktrees were present.

### Deployment drift

The live `/opt/recursion` checkout was dirty on `loop/auto` at `03c8fa4`. Relative to the fetched
`origin/master`, it was 129 commits ahead and 8 behind. The live local `master` was 36 commits
behind `origin/master`.

This is material drift. The next session must not deploy from either side by assumption. It must
capture the dirty state, identify which live commits and state changes are canonical, and construct
an immutable reconciliation candidate on a review branch.

### Services and containment

- `hermes-gateway`, `hermes-actuator`, cron, provider-network, and provider-proxy were active and
  enabled with no observed worker processes.
- The gateway ran as a dedicated user with `ProtectSystem=strict`, `ProtectHome`, and no retained
  capabilities. Its systemd exposure score was 3.6.
- The provider proxy was similarly contained. Its live probe negotiated TLS 1.3 to Anthropic and
  rejected direct and unauthorized egress.
- `hermes-actuator` ran as root without `ProtectSystem`, `ProtectHome`, or `PrivateNetwork`; its
  systemd exposure score was 7.0 MEDIUM. It is a high-authority seam that must be split or narrowed
  before broader autonomy.

### Host perimeter and durability

Only SSH was publicly listening, but UFW was inactive and the default iptables policies accepted
traffic. SSH allowed password authentication, X11 forwarding, and TCP forwarding. These settings
must be reviewed before adding any inbound control surface.

`/var/backups/recursion` was root-owned mode `0700`, approximately 1.1 GiB, and contained recent
runtime snapshots, bundles, transaction logs, and rollback scripts. No off-host backup schedule or
dedicated Recursion log rotation rule was found. The controller therefore still has one storage
failure domain.

## Repository topology

`state/portfolio.tsv` registered eight active/reference repositories and one pending repository.
Santa Clara was registered pending; `/opt/santa-clara-construction` did not exist.

Authenticated remote reads succeeded for the active repositories using their designated deploy
keys. The live clones were clean but mostly behind their fetched default branches:

| Repository | Behind fetched default |
|---|---:|
| ai-investment-cockpit | 133 |
| chiron | 14 |
| edgar-morning-brew | 2 |
| golden-stallion | 107 |
| golden-stallion-client | 151 |
| golden-stallion-extension | 66 |
| guerra-construction-group | 0 |

The GSC v2 pilot source pin was also stale. PAUSE prevented execution, but the pilot cannot simply
resume. It must be superseded, rebound to a new immutable source snapshot, or explicitly closed.

### Chiron split

Chiron is already canonical in `NotSkittlz/chiron` and `/opt/chiron`. The split was recorded and
byte-verified under D-013, and its active roadmap targets `/opt/chiron`.

The frozen product tree still exists at `apps/chiron` inside Recursion. This is deliberate legacy
residue, not the canonical product. Removal is ready to plan but must preserve completed task
records that truthfully reference the old path. New task generation must never emit
`apps/chiron`.

### Branch and publication model

The existing publisher is intentionally safe:

- only `loop/work/<task-id>` review refs are accepted;
- the registered default branch is rejected as a destination;
- a passed canonical task record is required;
- publication is serialized through `scripts/publish.sh`.

The model lacks:

- a per-project integration branch;
- immutable source SHAs for every task class;
- implementation versus integration branch semantics;
- remote-generated branch reconciliation;
- cross-repository candidate sets;
- stale-but-reviewable outcomes;
- vendor-cloud evidence.

No current Recursion-generated `loop/work/<task-id>` refs were found on active project remotes.
Chiron did contain Cursor-generated branches, proving that external development is already
occurring outside Recursion's publication protocol.

## Engine and sandbox implementation

The low-level v2 worker foundation already exists:

- declarative engine manifests and a fail-closed resolver;
- model aliases qualified by engine and role;
- argv-safe generic plugin execution;
- non-root systemd sandboxing with worktree-only writes;
- project, worktree, engine-slot, and heavy-gate locks;
- durable task leases and run evidence;
- exact candidate commit and seed-manifest verification;
- independent verifier worktrees;
- usage reconciliation and engine scorecards;
- review-only publication.

The targeted manifest, resolver, alias, cross-engine contract, usage reconciliation, scorecard,
provider proxy, and branch-protection tests passed locally. The Linux plugin sandbox test skipped
on the Windows audit host and still needs real Hetzner coverage.

### Missing execution-fabric contracts

The current engine schema records executable, argv, roles, billing basis/provider, network
endpoints, probe, concurrency cap, and environment passthrough. It does not record:

- provider account or subscription pool;
- quota and reset period;
- credential reference;
- model capability registry;
- compatible hosts and sandbox profiles;
- assignment identity and digest;
- remote session/result protocol;
- structured resume/cancellation behavior.

Run evidence does not directly persist the fully resolved assignment. Some reporting reconstructs
the engine from mutable task headers. Routing also remains duplicated between YAML, shell logic,
Hermes configuration, decision validation, and task generation. Several task creation paths still
default to Claude and legacy model aliases.

Parallelism is same-host and workstream-oriented. There is no host registry, distributed lease,
heartbeat, placement scheduler, or remote recovery protocol.

## Cursor CLI findings

`cursor-agent` was installed on Hetzner at version `2026.08.25-3e8eec8`; `cursor` was absent.
Neither root nor `recursion-runner` was authenticated. No Cursor worker service or cron entry was
configured, plugin enablement flags were absent, and the Cursor model alias was unset.

The installed launcher was a small shell wrapper beside an approximately 245 MiB runtime tree.
The generic plugin sandbox copies only the selected executable. A Cursor sandbox run would likely
copy the wrapper without its sibling `node` and `index.js`, then fail. Runtime packaging or a
read-only runtime-tree mount must be implemented and tested before enablement.

The provider-only namespace had loopback, no route, and an allowlist containing only
`api.anthropic.com:443`. Cursor, Gemini, OpenRouter, and DeepSeek endpoints were not provisioned.
The plugin path also did not inject a usable proxy configuration for non-Claude engines.

Cursor's personal My Machines worker mode was present without requiring Enterprise. Shared worker
pools require Enterprise and a service-account key. These are deployment capabilities, not proof
that either mode is authenticated or ready.

## Cursor Cloud Agents

Cursor Cloud Agents are a distinct remote execution backend, not a local engine and not Grok Bot.
The public API supports:

- programmatic agent and run creation;
- Cursor-hosted cloud environments or self-hosted machine/pool selection;
- explicit repository URLs and an immutable `startingRef`;
- isolated generated branches by default;
- artifacts, run status, cancellation, and token-usage retrieval;
- up to 20 repositories in a run, with product limitations for long-running multi-repo work.

Recursion should submit exact source SHAs, keep `workOnCurrentBranch=false`, record every returned
branch and commit, and independently verify the candidate. Vendor-reported tests and artifacts are
inputs to evidence, not canonical proof.

Cloud jobs must consume Cursor pool quota, not Hetzner CPU slots. Cursor source-control credentials
must remain separate from Recursion deploy keys.

## Grok Bot

Grok Bot is a separate Cursor-account product and quota pool. Cursor Ultra supplies the highest
weekly included usage. It is not the Grok model alias and does not draw from the ordinary Cursor
Models or Other Models pool in the same way.

Bots are persistent named supervisory agents with memory, plugins, browser, filesystem, terminal,
and routines. They can coordinate and run in parallel. Routines can run on a schedule or on
supported events. Current product builds also expose signed webhook-triggered routines, but the
surface is new and is not a general Bot-control API.

All Bots belonging to a user share one account-scoped cloud computer, including files, browser
sessions, application logins, and command-line credentials. Separate screens do not create
separate security boundaries.

Consequences for Recursion:

- model Grok Bot as a supervisory capacity pool and an account-shared host class;
- initially allow planning, project leadership, review, triage, and browser QA;
- use one account-level code-changing lease until safe concurrency is measured;
- never place Recursion deploy keys or controller credentials on the shared computer;
- send narrow assignments through a vendor-hosted signed routine webhook;
- use durable dispatch IDs and retry deduplication;
- return code through an external review branch and independently verify it on Hetzner;
- treat transcripts, screenshots, and Bot statements as evidence inputs only;
- keep on-demand spend disabled unless Lucas explicitly enables it.

Grok Bot can reduce the need for persistent supervisory VPS sessions. It does not replace
per-session isolated VMs. Cursor Cloud Agents or registered isolated workers remain the proper
backend for disposable tests and untrusted implementation work.

## Risks ordered by execution priority

1. Live Recursion deployment drift and dirty controller state.
2. Stale project clones and stale GSC pilot source authority.
3. Broad root actuator authority and incomplete host perimeter hardening.
4. No off-host backup or restore proof.
5. Missing project integration/publication contracts.
6. Missing immutable assignment and direct assignment evidence.
7. Broken Cursor runtime-tree treatment in the generic sandbox.
8. Anthropic-only provider egress.
9. No account/subscription pool or quota-aware routing model.
10. No remote host, Cursor Cloud, or Grok Bot adapter.

## Audit sources

Repository sources include:

- `CONTROL_PLANE.md`
- `ANCHOR.md`
- `docs/architecture.md`
- `docs/plans/engine-plugin-architecture.md`
- `scripts/work.sh`
- `scripts/worker-sandbox.sh`
- `scripts/resolve-engine.py`
- `scripts/resolve-model-alias.py`
- `scripts/publish.sh`
- `scripts/capacity.sh`
- `scripts/project-reconcile.py`
- `state/portfolio.tsv`
- `state/project-config/*.json`
- `state/DECISIONS.md`

External product references:

- <https://cursor.com/docs/cli/headless>
- <https://cursor.com/docs/cloud-agent>
- <https://cursor.com/docs/cloud-agent/api/endpoints>
- <https://cursor.com/help/grok-bot/plans>
- <https://docs.x.ai/grok-bot/overview>
- <https://docs.x.ai/grok-bot/skills-routines-and-automations>
- <https://docs.x.ai/grok-bot/approvals-security-and-privacy>
