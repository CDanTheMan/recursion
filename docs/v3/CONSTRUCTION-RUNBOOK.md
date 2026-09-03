---
title: Recursion v3 construction runbook
status: proposed-procedure-not-authorization
last-updated: 2026-09-03
---

# Recursion v3 construction runbook

This is temporary construction procedure, separate from the product specification. It does not
authorize implementation, provider changes, deployment or control-plane amendments.

## Recommended first autonomous milestone

The broad former “Milestone 1 contract skeleton” is split. The first candidate is
[M1A — Autonomous Planning Contract and Replay Baseline](M1A-AUTONOMOUS-PLANNING.md). It contains
only strict planning schemas, pure cross-record/DAG validation, deterministic WorkPacket
derivation, typed gate/retry/replan/escalation behavior and in-memory replay over sanitized
fixtures.

The canonical contract is [AUTONOMOUS-PLANNING.md](AUTONOMOUS-PLANNING.md), the closed fixture
grammar/oracle blueprint is [M1A-FIXTURE-ORACLES.md](M1A-FIXTURE-ORACLES.md), and the standalone
handoff is [prompts/m1a-autonomous-planning-contract.md](prompts/m1a-autonomous-planning-contract.md).
No part of M1A is executed in this research campaign.

**Future allowed paths:**

- `schemas/control-plane/v3/planning/**`
- `scripts/v3/planning/**`
- `scripts/tests/v3/planning/**`
- `docs/v3/**`

**Non-goals:** providers/models/network; terminals/subprocesses; plugins; SQLite/database/migration;
Git calls or ref/worktree mutation by the code/tests; publication/merge/deploy/service effects;
credentials/config/account changes; live PAUSE; external effects; UI; native loop; scientific
adapters; performance/superiority claims. A future task may make its own bounded local commit only
when separately authorized.

## Exact task graph and acceptance

The canonical sequential DAG is M1A-01 vocabulary/fixture freeze → M1A-02 strict schemas and
canonicalization → M1A-03 cross-record/DAG validator → M1A-04 pure decider/reducer/packet
derivation → M1A-05 all conformance fixtures → M1A-06 exact-candidate independent rerun.

The 23 mandatory fixtures and twelve machine-checkable gates in
[M1A-AUTONOMOUS-PLANNING.md](M1A-AUTONOMOUS-PLANNING.md), together with the closed command/event/
error/digest oracles in [M1A-FIXTURE-ORACLES.md](M1A-FIXTURE-ORACLES.md), are the acceptance
blueprint. M1A-01 freezes their literal strict-JSON red bundles before reducer code. In summary,
they fail closed on unauthenticated/incomplete/widened goals, bad DAGs, stale packets/leases,
non-novel/exhausted retries, missing/downgraded verifiers, quota/provider blocks, route replacement,
current/future PAUSE separation, ambiguous effects, duplicate commands, replay divergence,
unauthorized parent mutation, unknown fields/policies, ownership conflicts and incomplete
amendment disposition.

Missing verification is never pass. Sol/Luna/Terra review is same-family. A future verifier binds
the exact candidate, commands, fixtures and evidence and records any missing independence.

## Why the former broad milestone was split

The former schema list combined autonomous planning with routes, plugins, scientific records,
terminal protocol, persistence and publication. That made the first construction step too large
to falsify and obscured privileged-code ownership. M1A keeps only pure planning behavior. Inert
route/budget/lease/PAUSE/effect references remain solely to test the mandatory failure states;
they do not implement those subsystems.

- **M1B** may later add inert route, plugin and process requirement contracts, still without a
  provider call, process launch or plugin execution.
- **M1C** may later add inert source/effect/persistence requirement contracts. SQLite, scientific
  adapters, Git, publication, external effects and migration remain later separately authorized
  work.

The broad OR-015 migration rehearsal remains blocked by multiple writers without one proven
fence. No M1A fixture may be called a migration rehearsal or runtime proof.

## Handoff, stop and rollback

A future M1A task freezes literal red fixture inputs/expected receipts/events/errors/state/digests
and obtains review of that exact red commit before green behavior. Stop on an authority term with
two owners, current/future PAUSE conflation, a child
widening, nondeterministic replay, semantic-model judgment in the reducer, required I/O/external
subsystem, out-of-scope path or missing verifier. Return the smallest conflicting fixture to
Lucas rather than encoding a policy choice.

M1A has no runtime cutover. If separately authorized construction fails, its unreferenced local
candidate can be abandoned without changing v1/v2 behavior. Never rewrite history, push, publish,
merge or deploy from this runbook.
