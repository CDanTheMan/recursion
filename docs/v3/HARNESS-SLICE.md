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

[ROUTE-CAPABILITIES](ROUTE-CAPABILITIES.md) keeps the route matrix. No live account is certified by the matrix. This slice binds three headless commands: Claude Code print mode `claude -p` with stream-json, Codex `codex exec --json`, and Grok Build `grok -p` with streaming-json.

[DECISION-REGISTER](DECISION-REGISTER.md) OR-022 requires a native path and an upstream path, with no hidden API key for ordinary upstream use. OR-024 ranks responsiveness, then subscription efficiency, then completion, under correctness and authorization. This slice has no measurement of those rankings.

## Shape

1. **Plan.** [planning.py](../../scripts/v3/harness/planning.py) admits one task through the M1A kernel: owner intent, goal, ARM run, plan, capacity, budget, work packet. The task text is the intent and the goal outcome, and its digest is the task semantic definition. A different task yields a different projection. Record ids are the closed single-task vocabulary; each run is a fresh stream.
2. **Route.** [routing.py](../../scripts/v3/harness/routing.py) loads frozen fixture `F-M1B-001`, validates it, and runs the M1B reference oracle. Execution continues only when the decision status is `selected`. The selected id on that fixture is `route-a`.
3. **Run.** [providers.py](../../scripts/v3/harness/providers.py) is the adapter interface. `fixture` returns a deterministic transcript and starts no process. `claude` argv is `claude -p --output-format stream-json`; the task goes to stdin. `codex` argv is `codex exec --json` plus the task as the prompt argument. `grok` argv is `grok -p`, the task, and `--output-format streaming-json`. A headless process starts only with `--allow-live`.
4. **Choose a provider.** [config/harness.json](../../config/harness.json) lists each provider's command and capabilities. [capabilities.py](../../scripts/v3/harness/capabilities.py) keeps providers that are enabled and hold every required capability, in preference order. That choice is not an M1B route id. [dispatch.py](../../scripts/v3/harness/dispatch.py) retries the current provider, then tries the next capable one. A failed attempt records the error class. Provider stderr is not copied into the error or the log.
5. **Entry point.** [scripts/recursion](../../scripts/recursion) is the terminal command. `plan` admits the task and the route. `run` then executes. `status` prints the config and a JSONL log summary. [log.py](../../scripts/v3/harness/log.py) writes one JSON object per event.

The planning route id `ROUTE-INCLUDED` and the M1B id `route-a` are different namespaces. This slice does not alias them. The adapter runs only after M1B selection succeeds.

## Gate

`python -X utf8 -B tools/check_v3_orientation.py --contracts` runs the original 23 M1 programs, [harness.test.py](../../scripts/tests/v3/harness/harness.test.py), and [adapters.test.py](../../scripts/tests/v3/harness/adapters.test.py). The 2026-09-13 path freeze no longer describes this tree, so the gate keeps that commit as an ancestor, checks orientation invariants, and rejects untracked files outside this slice. It does not fail the repository for later research paths already on the branch.

## Out of this slice

Worker-result and gate-result admission, durable projection storage, and any live provider call in tests or CI.
