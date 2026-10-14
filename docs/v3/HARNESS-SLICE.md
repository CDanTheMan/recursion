---
title: Recursion harness slice
status: implemented
last-updated: 2026-10-14
---

# Recursion harness slice

This fork implements the harness in Python 3.11 or newer under [scripts/v3/harness](../../scripts/v3/harness/run.py). That is the host language. The harness modules use the standard library and call the M1A kernel already in the tree. Route admission loads the M1B checker, which imports `jsonschema` 4.23.0.

Upstream [D-039](../../state/DECISIONS.md) leaves the host language open and points at a language-agnostic outline (open upstream PR 161, not merged here). The M1A and M1B JSON records stay the boundary a later host would reconstruct. The running code in this repository is Python.

## What the existing records already fix

[ARCHITECTURE](ARCHITECTURE.md) ratifies one small deterministic kernel and typed fail-closed adapters (OR-018). Provider sampling, process launch, and frontends stay outside the kernel. Commit and dispatch are separate: a command receipt is not a settled provider effect.

[EXECUTION-FABRIC](EXECUTION-FABRIC.md) keeps kernel admission, broker ownership, and recipient settlement apart. A process exit is one observation. Missing usage is not zero. This slice does not claim settlement.

[ROUTE-CAPABILITIES](ROUTE-CAPABILITIES.md) keeps the route matrix. No live account is certified by the matrix. Claude Code print mode is `claude -p` with JSON or stream-json output. This slice binds that one CLI.

[DECISION-REGISTER](DECISION-REGISTER.md) OR-022 requires a native path and an upstream path, with no hidden API key for ordinary upstream use. OR-024 ranks responsiveness, then subscription efficiency, then completion, under correctness and authorization. This slice has no measurement of those rankings.

## Shape

1. **Plan.** [planning.py](../../scripts/v3/harness/planning.py) admits one task through the M1A kernel: owner intent, goal, ARM run, plan, capacity, budget, work packet. The task text is the intent and the goal outcome, and its digest is the task semantic definition. A different task yields a different projection. Record ids are the closed single-task vocabulary; each run is a fresh stream.
2. **Route.** [routing.py](../../scripts/v3/harness/routing.py) loads frozen fixture `F-M1B-001`, validates it, and runs the M1B reference oracle. Execution continues only when the decision status is `selected`. The selected id on that fixture is `route-a`.
3. **Run.** [providers.py](../../scripts/v3/harness/providers.py) is the adapter interface. `fixture` returns a deterministic transcript and starts no process. `claude` argv is `claude -p --output-format stream-json`; the task goes to stdin; the process starts only with `--allow-live`.

The planning route id `ROUTE-INCLUDED` and the M1B id `route-a` are different namespaces. This slice does not alias them. The adapter runs only after M1B selection succeeds.

## Gate

`python -X utf8 -B tools/check_v3_orientation.py --contracts` runs the original 23 M1 programs and [harness.test.py](../../scripts/tests/v3/harness/harness.test.py). The 2026-09-13 path freeze no longer describes this tree, so the gate keeps that commit as an ancestor, checks orientation invariants, and rejects untracked files outside this slice. It does not fail the repository for later research paths already on the branch.

## Out of this slice

Worker-result and gate-result admission, a second CLI, durable projection storage, and any live provider call in tests or CI.
