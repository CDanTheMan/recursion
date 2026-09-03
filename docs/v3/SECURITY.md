---
title: Recursion v3 security and sovereignty hypothesis
status: hypothesis
last-updated: 2026-09-03
---

# Recursion v3 security and sovereignty hypothesis

## Security objective

Protect owner identity, privacy, source, data, credentials, machines, and publication authority without turning open-source software into a service that can lock its owner out. Security controls become mandatory where one identity, process, plugin, or node crosses into another trust domain. Local owners retain the ability to configure and run their own software.

## Owner Sovereignty guarantee

V3 should preserve:

- local and self-hosted operation;
- bring-your-own subscriptions, accounts, APIs, and models;
- inspectable and portable configuration;
- offline-capable operation where configured capabilities permit it;
- custom builds and federated plugin sources;
- owner-selectable permission profiles, including full-access modes;
- no mandatory vendor authorization or central marketplace;
- no telemetry export without explicit opt-in.

Sovereignty does not cause one component to inherit every owner privilege. An owner may choose broad profiles after clear warnings; delegated agents and remote nodes still receive explicit attributable grants so compromise and mistakes can be contained.

## Permission profiles

Candidate profiles include:

- `observe-only`;
- `sandboxed`;
- `workspace-write`;
- `trusted-autonomous`;
- `control-plane-authoring`;
- `absolute-full-access`.

Adapters may map these to provider-native options, including dangerous skip-permission flags when the owner explicitly selects them. V3 must display the effective capabilities and blast radius, record the acknowledgement, and avoid implying that a provider-native flag overrides Recursion's budget, privacy, identity, or publication contracts.

`absolute-full-access` widens the selected actor's tool, process, filesystem, and network surface only to the extent named by its grant. It does not implicitly confer control-plane authoring, credential enumeration, new provider enrollment, metered spending, protected-branch merge, publication, deployment, or the right to weaken PAUSE, privacy, identity, and audit invariants. Those are separate attributable grants or human seams. The name and exact composition remain subject to Lucas's decision because a misleading "absolute" label is itself a safety defect.

Lower scopes may narrow permissions freely. Widening network, credential, spending, deployment, or control-plane access requires an explicit owner action at the affected scope. Ordinary model, cache, quality, and concurrency preferences may override normally within inherited bounds.

## Local versus remote boundary

Remote execution requires non-disableable identity, integrity, replay protection, and authorization invariants. These protect connections between nodes; they do not gate local use of the open-source program.

A lightweight, zero-model preflight runs at enrollment or when trust-relevant inputs change. Its result is cached against runtime hash, configuration hash, trust-bundle and protocol versions, certificate state, and relevant permission snapshot. It should complete in seconds on the target class of hardware.

The full conformance suite is mandatory for official v3 release evidence and optional for an individual owner's ordinary installation. A failure quarantines the affected remote capability instead of globally disabling local Recursion.

## Node identity and authorization

- Installation trust root is separate from everyday operator credentials.
- Device enrollment requires proof of possession and explicit owner approval.
- Controller, executor, observer, and verifier privileges are granted separately.
- Parent-goal envelopes and work packets are signed, scoped, expiring, and replay protected.
- Risk-based step-up confirmation applies to authority expansion, high-impact commands, new egress, credentials, updates, and destructive actions.
- Revocation prevents new admission immediately and causes in-flight work to checkpoint or terminate according to the versioned revocation policy.
- PAUSE and emergency kill outrank ordinary checkpoint completion. Their exact treatment of an already-started external effect is an unresolved owner decision; until resolved, recovered output is quarantined and cannot authorize a new effect.
- A disconnected node may finish only the local bounded operation explicitly permitted by its last valid grant and spool signed evidence. After reconnection, the controller revalidates the GoalSpec version, fencing token, lease, and PAUSE/revocation state before admitting that evidence or any derived action. It cannot widen scope or publish while disconnected.

An owner authenticated on both devices may execute commands remotely when both devices, the goal, and the requested capability are authorized.

## Credentials

`recursiond` is hypothesized as the sole credential broker. Secrets remain in provider-native auth homes, an OS secret store, or another configured vault—not Git, SQLite, prompts, worktrees, telemetry, context artifacts, or plugin manifests.

Workers receive:

- an opaque account/credential reference;
- a temporary environment or home overlay exposing only the selected route;
- the minimum lifetime and filesystem visibility required;
- no enumeration of unrelated accounts.

Model-visible output must never contain credential values. Logs and evidence pass a secret scanner before durable storage or publication.

## Project privacy and egress

Every admitted project declares data classification and egress policy. Defaults are `private` and deny-by-default.

A local egress broker validates:

- destination and resolved provider route;
- project classification and provider data-use policy;
- exact GoalSpec and network grant;
- secret-exposure scan;
- artifact classification;
- owner authorization for provider training or contributor-tier routes.

Cheap or contributor routes default to prohibited for private projects unless the owner explicitly enables their data terms. Enabling a contributor route requires a route-specific acknowledgement and an egress broker that captures and classifies the exact outbound bytes before launch; prompt scanning alone is defense in depth, not the boundary. Project configuration and prompt content cannot widen contributor eligibility. Private cache and evidence artifacts remain project scoped; content addressing never implies public or cross-project sharing.

## Provider refusals and safety policy

Refusal handling exists for continuity and compatibility, not for evading provider or legal safeguards. A refusal is recorded and may trigger an explicitly configured alternate route only when the underlying task remains authorized by the GoalSpec, local policy, law, privacy boundary, and provider terms. Repeated or material refusal escalates to the operator.

Recursion may advise that a model/route is a poor fit for an authorized workflow based on observed continuity. The owner may ignore advisory recommendations within valid authority. Hard local boundaries—credentials, privacy, egress, budgets, node identity, and publication—remain enforced independently of model behavior.

## Plugin trust

Plugins declare capabilities, dependencies, event permissions, filesystem/network access, secret references, resource budgets, and isolation needs. Trust modes are:

- `sandboxed`;
- `trusted`;
- owner-authorized `full-access`.

Untrusted plugins never modify the authority kernel, read canonical storage directly, or call another plugin through hidden global state. A `full-access` plugin still cannot replace kernel authority checks. Privileged plugin installation and update require a pinned digest, attributable provenance, staged verification, and the owner-selected signature policy; whether unsigned local code may ever receive privileged capability remains an explicit owner decision. Update signing, provenance, and rollback are separate from agent execution authority.

## Threats the design must test

- stolen node credential or replayed work packet;
- malicious project configuration widening egress or permissions;
- prompt/tool output attempting to exfiltrate credentials;
- plugin dependency confusion or update compromise;
- symlink/reparse/path traversal across worktrees;
- stale route/GoalSpec used after revocation;
- provider response forging evidence or completion;
- split-brain executive leases;
- disconnected node publishing stale work;
- public event sizes, timing, identifiers, or raw content revealing private project membership;
- owner-hostile defaults that make local recovery impossible.
