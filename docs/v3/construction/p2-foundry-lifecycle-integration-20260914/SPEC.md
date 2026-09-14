# Foundry observation lifecycle integration — 2026-09-14

Parent: goal-recursion-v2-execution-fabric. Target: Recursion v3.
Lucas authorized bounded implementation, tests, slice commits and independent Astra review.
External Devin/SWE-2 contributors research, develop and test ON v3, including custom kernels.
No v1/v2 product work, product-runtime workers, providers, scientific execution or fleet activation.

## Exact inputs and allowed scope

Common ancestor e627cd93bac473094bc99e8fa29c8d62bae526a2.
Reviewed lifecycle 3b4865a19516abd6289d3509077743f65233ca80.
Reviewed observation 881e3252ee21564da02beba5990fcaf4bfb60b14.
Combined TASK_BASE be3ee96353f16cf84df38397120e324c7204b8f3 contains both unmodified.
DQ controller ed8db0e stays separate; no scientific admission is implied.

Only five new files:
- tools/construction_swarm/p2_foundry_lifecycle.py
- tools/construction_swarm/test_p2_foundry_lifecycle.py
- docs/v3/construction/p2-foundry-lifecycle-integration-20260914/SPEC.md
- docs/v3/construction/p2-foundry-lifecycle-integration-20260914/PROGRESS.md
- docs/v3/construction/p2-foundry-lifecycle-integration-20260914/check.py

All inherited files, 49 top-level v3 specifications, component gates and policy stay unchanged.
Each original component source gate belongs to its original reviewed branch, not this union.
The new gate checks exact union provenance, clean candidate, actual tracked bytes, five additions
and behavioral regressions without relabeling the old scope gates as combined-candidate gates.

## Integration contract

A new fixed-purpose controller subclasses the reviewed lifecycle Controller, changing only
the fixed observation-service argv and adding durable observation-binding metadata/refusal.
It reuses the original lock, cgroup ownership, restart/backoff, fences, PAUSE, stop and cleanup.
It accepts no arbitrary executable/module/command or provider/worker launch route.
It takes strict bounded outer JSON:
version=1; lifecycle_config=absolute path to the inherited lifecycle JSON;
project_runs=nonempty project-to-absolute-run mapping (at most 100).
The inherited lifecycle JSON supplies its existing exact configuration schema. Both are
operator-owned inputs; this packet provisions only disposable test files. No application
settings, credentials, cron, startup or persistent cgroup delegation are installed.

Project identifiers, normalized absolute paths and duplicate aliases are validated with the
existing adapter contract. The normalized mapping digest is persisted in every state and must
match before inherited takeover can arm any domain cleanup/write. A prior generic controller
or different mapping is refused. Missing run data remains an explicit observation failure.
Mapping source paths are arguments; plaintext client tokens never enter controller/service argv.

The child is exactly p2_foundry_observation serve with the inherited source, socket, grant,
instance and fence arguments plus the validated mappings. Service-instance identity is unique
to this controller/incarnation. Client exit does not own or stop it.
Lifecycle running means process/socket readiness, not proof that every foundry record is
readable/current. Authenticated read responses supply application freshness/unavailability.
No acceptance promotion, canonical Hermes authority, replay cursor, or live-client claim is added.

## Frozen required outcomes

1. Real service returns correct status/tasks/task/artifact through separate authenticated CLI
   and stdio MCP processes; canonical authority remains unavailable.
2. Missing/incorrect credentials and cross-project requests refuse.
3. Returned output is not accepted; foundry-local decision, stale data, retained unknown holds
   and unsupported event replay remain explicit.
4. Closing clients preserves service PID/incarnation; reconnect sees the same records.
5. Killing only the identity-bound test service causes a bounded restart, higher fence and
   a changed service instance; a persistent MCP client reconnects successfully.
6. Stop returns a quiescent receipt, the owned cgroup is empty, and unrelated canary survives.
7. Retrying a controller at the same source/mapping preserves incarnation monotonicity.
8. Invalid/aliased/injection-shaped mappings refuse before launch; mismatched prior mapping
   refuses without signaling its owned canary or changing inherited domain controls/state.
9. PAUSE/disabled prevents start; a competing controller starts/signals no service.
10. Every read preserves source run bytes; malformed/missing data produces unavailable instead
    of a fabricated success, without changing lifecycle process-readiness semantics.
11. Imported source and frozen scope/behavior contracts remain intact.

## Gates and bounds

NEW gate: python3 -X utf8 -B docs/v3/construction/p2-foundry-lifecycle-integration-20260914/check.py
--candidate FULL_SHA --output FRESH_EXTERNAL_DIRECTORY

Focused behavior: python3 -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_foundry_lifecycle

The combined gate also runs unmodified P1, P2 access, host lifecycle and observation behavioral
tests plus the existing handoff-preservation command. The observation standalone SourceScopeTests
are deliberately excluded from the union behavior invocation because their frozen branch/scope
describes the original candidate; equivalent stronger union preservation is required by this gate.
Zero providers/scientific calls; 120 seconds per gate command, 15 seconds per owned test child,
32 MiB fixture data, bounded outputs and complete owned cleanup. Tests use native WSL fixture
cgroups only. Retain failure logs and exact-candidate review externally.
Independent Astra approval must name the exact final candidate.

## Qualification boundary

This delivers an operator-invoked read-service integration tested with temporary real-schema
records, not actual Cursor/Codex app installation, remote transport, canonical acceptance,
standing worker scheduling, quota/reset handling, installed startup, or 24/7 operation.
Real completed-run smoke, production grants/delegation and disruptive host trials remain unrun.
No pushes, publication, protected-branch merges or operational configuration changes in this slice.