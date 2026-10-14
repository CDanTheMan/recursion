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
5. **Entry point.** [scripts/recursion](../../scripts/recursion) is the terminal command. `plan` admits the task and the route. `run` then executes. `status` prints the config, a JSONL log summary, and saved runs. `resume` continues a saved run. `cancel` stops unfinished tasks. [log.py](../../scripts/v3/harness/log.py) writes one JSON object per event.
6. **Several tasks.** [orchestrate.py](../../scripts/v3/harness/orchestrate.py) splits a goal on non-empty lines. Each line is a separate M1A admission, so one task cannot widen another task's projection. Independent tasks run in parallel up to `orchestration.concurrency` in [config/harness.json](../../config/harness.json). Task ``i`` starts at the ``i``-th capable provider, then falls back. Run records live under `.recursion/runs` ([state.py](../../scripts/v3/harness/state.py)).
7. **Provider limits.** Each provider has `timeout_seconds`. A missing executable names the command and does not dump stderr. A rate limit waits `backoff_seconds * (attempt + 1)` before the next try of that provider.
8. **Install.** [pyproject.toml](../../pyproject.toml) exposes the `recursion` console script. `python -m pip install -e .` works on Windows and Linux. The checkout command `python -X utf8 -B scripts/recursion` still runs without install.
9. **Isolation.** [isolation.py](../../scripts/v3/harness/isolation.py) gives each task its own git worktree and branch, `recursion/run/<run-id>/task-<index>`. The CLI removes the worktree and deletes the branch when the task finishes, including after a failure. Parallel adds and removes take one lock per repository so two providers do not collide. Library tests use a null isolator and do not touch the checkout.
10. **Review.** [review.py](../../scripts/v3/harness/review.py) asks a different capable provider to read the diff and the output. The first non-empty line must be `VERDICT approve` or `VERDICT revise`. A revise sends the notes back to the same worker, for at most `review.max_rounds` rounds in [config/harness.json](../../config/harness.json). Verdicts are stored on the task. An unreadable review is a revise and the raw body is not stored. If no other provider finishes a review, the worker result stands.
11. **Report.** [report.py](../../scripts/v3/harness/report.py) writes `<run-id>.report.json` and `<run-id>.report.md` next to the run record. Each task lists its diff, provider, attempts, review verdicts, and duration.
12. **Usage and budgets.** [usage.py](../../scripts/v3/harness/usage.py) reads token and cost figures when a provider stream includes them. A missing figure stays unknown. `budgets.max_input_tokens`, `budgets.max_output_tokens`, and `budgets.max_cost` stop the run when a known figure is above its ceiling. `null` means no ceiling.

The planning route id `ROUTE-INCLUDED` and the M1B id `route-a` are different namespaces. This slice does not alias them. The adapter runs only after M1B selection succeeds.

## Gate

`python -X utf8 -B tools/check_v3_orientation.py --contracts` runs the original 23 M1 programs, [harness.test.py](../../scripts/tests/v3/harness/harness.test.py), [adapters.test.py](../../scripts/tests/v3/harness/adapters.test.py), [orchestration.test.py](../../scripts/tests/v3/harness/orchestration.test.py), and [review.test.py](../../scripts/tests/v3/harness/review.test.py). The 2026-09-13 path freeze no longer describes this tree, so the gate keeps that commit as an ancestor, checks orientation invariants, and rejects untracked files outside this slice. It does not fail the repository for later research paths already on the branch.

## Out of this slice

Worker-result and gate-result admission, durable projection storage, and any live provider call in tests or CI.
