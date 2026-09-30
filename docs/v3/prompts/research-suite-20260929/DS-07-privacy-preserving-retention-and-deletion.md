---
title: DS-07 — Privacy-preserving retention and deletion
status: proposed-inert
last-updated: 2026-09-29
parent-goal: goal-recursion-v2-execution-fabric
invocation: only after Lucas explicitly invokes this file in a new session
---

# DS-07 — Privacy-preserving retention and deletion

Run as a single Deep Research session (the Deep Research plugin only; no repository or GitHub connector). This handoff is fully self-contained. This file is inert until Lucas invokes it; reading or creating it launches nothing and authorizes no provider call, write, or effect.

## Baked context

### Shared Recursion context

Recursion is a provider-neutral agent platform. The development target is Recursion v3: a
small deterministic kernel with typed adapters; native and upstream execution; persistent,
goal-scoped assistants organized as Head -> ARM executives -> bounded workers (no separate
AI "ARM manager"); configurable context and compaction; plugins and editions; an
interactive detachable terminal (CLI, optional Telegram); and Windows/Linux operation and
recovery. A graphical frontend is not required for v3.

Authority: Lucas is the final owner. Hermes is the executive control plane. Workers are
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

- **Focus.** This lane specifies how raw private artifacts expire while durable lineage remains auditable, using scoped encryption, verified blob and key deletion, cache/backup propagation and a minimal signed non-sensitive tombstone. It is research lane R9 of the Recursion v3 agenda.
- **Ratified direction.** `OR-009` ratifies: encrypt raw private artifacts with project- or retention-class-scoped data-encryption keys; on expiry delete the artifact and its scoped key; propagate physical deletion through caches, replicas, backups and disconnected-node spools; append a minimal signed tombstone. This lane refines mechanics and must not reopen the owner-selected direction.
- **Owner-selected retention defaults.** Successful raw sessions 30 days; failed or disputed raw sessions 90 days; compact metadata, lineage, decisions, receipts and accepted evidence are indefinite or project-policy governed; explicit pinning for important sessions; project-specific shorter or longer policies within legal and storage constraints.
- **Deletion proof-state machine.** requested -> local-content-deleted -> key-destroyed -> propagation-pending -> verified-complete | partial | blocked | legal-hold | expiry-bound. Completion requires either evidence from every recoverable copy or a recorded backup-expiry boundary.
- **Tombstone.** Records artifact class, governing policy/version, deletion request and completion times, responsible component and disposition, and non-sensitive copy dispositions. It must not retain raw content or an unnecessarily equality-revealing global digest.
- **Cryptographic erasure.** Defense in depth, not proof that every copy disappeared. Content addressing, deduplication and shared keys can defeat deletion isolation if scoped incorrectly. NIST SP 800-88 media-sanitization guidance does not prove that logical or provider-held copies are gone.
- **Copy classes to enumerate.** Active store, CAS replicas, caches, backups, provider-side copies and disconnected spools, each with its own proof state.
- **Boundary.** No encryption, key management or deletion is performed; no legal advice is given, and legal hold remains an owner and legal decision.

## Purpose

Specify how raw private artifacts expire while durable lineage remains auditable, using scoped encryption, verified blob and key deletion, cache/backup propagation and a minimal signed non-sensitive tombstone. Agenda lane R9 blocks a defensible deletion contract until proof states for disconnected nodes, backup expiry and key granularity exist; deletion must never be reported complete while an unexpired recoverable copy remains.

## Authority and boundaries

The authority, scope and privacy constraints are restated in `## Baked context`; read nothing else in preparation. Preserve the current Hermes constitution; write proposed amendments, never edit it. Public Deep Research receives only public or synthetic briefs — never unpublished v3 drafts verbatim, private project content, transcripts, local paths, credentials, or account/infrastructure identifiers. No runtime, provider, auth, config, cron, PAUSE, spending, deployment, publication or merge is authorized. The owner-selected retention direction is fixed; refine mechanics, do not reopen it. No encryption, key management or deletion is performed.

## Inputs to read

None. This handoff is self-contained; the context is baked in above and below.

## Research questions

1. What key granularity (per project, per retention class, per artifact, per epoch) allows cryptographic erasure without breaking content-addressed deduplication or artifact identity?
2. How is key destruction verified when the key lives in an OS store, a KMS or a disconnected node, and what evidence distinguishes proven destruction from assertion?
3. Which recoverable copies must be enumerated (active store, CAS replicas, caches, backups, provider-side copies, disconnected spools), and what is the proof state for each?
4. How is a backup-expiry boundary recorded, audited and surfaced, and what happens when a copy outlives its recorded boundary?
5. What is the minimal signed tombstone that proves deletion without retaining raw content or an unnecessarily equality-revealing global digest?
6. How do content addressing, deduplication and shared keys create deletion-isolation failures, and which negative fixtures expose them?
7. What size, timing or access-pattern leakage lets a public observer infer private project membership, and how is that bounded?
8. How do legal hold and pin or retention overrides interact with the deletion proof-state machine without silently claiming completion?
9. What should the proof-state machine be, relative to `requested -> local-content-deleted -> key-destroyed -> propagation-pending -> verified-complete | partial | blocked | legal-hold | expiry-bound`?
10. What independent evidence is required before any node may report `verified-complete`, and what blocks that claim?
11. Where does NIST SP 800-88-style media sanitization guidance stop applying to logical and provider-held copies?
12. Which retention defaults (for example 30 days successful, 90 days failed or disputed) remain owner-selected and outside this lane's decisions?
13. What stop conditions prevent publishing a deletion claim while any recoverable copy lacks evidence or a recorded expiry boundary?

## Deliverable

A source-pinned report with: a claim table (claim, source, version/date, classification, confidence, expiry trigger); a deletion proof-state machine; key-granularity and propagation options with tradeoffs; negative fixtures; a recommendation tied to a named competing option and decisive falsifier; and open Owner questions.

## Non-goals

- No key management, encryption or deletion implementation.
- No provider cache or backup deletion performed or requested.
- No claim that cryptographic erasure proves every copy is gone.
- No reopening of the ratified retention direction or default durations.
- No legal advice; legal hold remains an owner and legal decision.
- No secrets, keys, real digests or real artifact content in any output.
- No private project identity or content in public or synthetic briefs.

## Completion gate

- Every proof state maps to an observable predicate or is explicitly `unavailable`.
- No completion claim is allowed while a recoverable copy lacks evidence or a recorded expiry boundary.
- Key-granularity options each name a tradeoff and a falsifier.
- Content-address and deduplication leakage negative fixtures are specified.
- Owner retention direction is not reopened and no mechanism is promoted to a default.
- Disconnected-node and backup-expiry proof states have explicit stop conditions.
- Protected paths are untouched; privacy and secret scan are clean.
