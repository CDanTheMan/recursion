# Recursion

**Recursion v3** is a provider-neutral agent harness: a client, a local execution
kernel, a context and compaction engine, and a multi-node fabric, plus typed
adapters for other harnesses. A person should be able to drive it on the models
they already use.

This repository is the standalone fork
[CDanTheMan/recursion](https://github.com/CDanTheMan/recursion). The product map
is [docs/v3/START-HERE.md](docs/v3/START-HERE.md). Who decides is
[CONTROL_PLANE.md](CONTROL_PLANE.md). Why the work exists is
[ANCHOR.md](ANCHOR.md). V1/v2 were removed from the trunk on 2026-09-28 and
remain at tag `pre-v3-clean-cut-20260928`.

## Install

Python 3.11 or 3.12 and Git. From the repository root:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` pins the test dependencies, including `jsonschema` 4.23.0
(Draft 2020-12) and pytest. `bash scripts/install.sh` on Linux, or
`powershell -ExecutionPolicy Bypass -File scripts/install.ps1` on Windows,
creates a virtualenv, installs this checkout, and runs `recursion doctor`.

## Run tests

```bash
python -X utf8 -B -m pytest
python -X utf8 -B tools/check_v3_orientation.py --contracts
```

`pytest` runs [`tests/`](tests/test_v3_checks.py). That suite runs the orientation
contracts, the scope tests, and the schema and fixture validators under
`scripts/tests/v3` (three schema checks, three fixture checks, and seventeen M1
test programs). It prints a coverage report. The orientation command is the
same gate CI runs on pull requests and on pushes to `master`.

## Layout

| Path | What it is |
|---|---|
| `docs/USER-GUIDE.md` | How to install and run the harness |
| `docs/ARCHITECTURE.md` | How one run moves from plan to report |
| `docs/v3/` | Product specifications, research, and evidence |
| `CHANGELOG.md` | What has landed on this fork |
| `experiments/v3/` | Provider-free experiments and checks |
| `schemas/control-plane/v3/` | Planning, execution, and integrity schemas |
| `scripts/v3/` | Planning replay and validation |
| `scripts/tests/v3/` | M1 test programs and fixtures |
| `tests/` | Pytest suite that wraps those v3 checks |
| `tools/` | Orientation gate and scope tests |
| `state/` | Decision log and goal records |

## Harness

Install the checkout and run one task on the fixture provider. That provider
starts no CLI and needs no account.

Linux:

```bash
python -m pip install -e .
recursion run --task "Say hello" --provider fixture
```

Windows PowerShell:

```powershell
python -m pip install -e .
recursion run --task "Say hello" --provider fixture
```

The command prints a JSON result on stdout. Events are JSONL on stderr.
With only `fixture` as a candidate, review has no second provider, so the
task is `unreviewed` and the command exits `2` unless
`review.accept_unreviewed` is true.

### Commands

`plan`, `run`, `status`, `resume`, `cancel`, `providers`, `doctor`, `init`,
`config validate`, `logs`, `land`, and `clean`. `plan` admits tasks and does
not start a live CLI. `run` schedules them. `--concurrency` overrides how many ready tasks
run at once, and `--progress` prints plain lines on stderr instead of JSONL.
`status`, `resume`, and `cancel` use the saved
run. `cancel` stops a provider that is still running, and the children that
process started. `providers` shows whether each CLI is on `PATH`, its weight, and any
cooldown. `doctor` checks git and sign-in without printing secrets. `init`
writes a starter config. `config validate` checks
[config/harness.schema.json](config/harness.schema.json). `logs` prints one
run's JSONL and can filter by task, provider, and level. `land` merges a
finished run into a branch. `clean` prunes old run state.

### Providers

`fixture` is enabled and starts no process. Live adapters, started only with
`--allow-live`, are `claude`, `codex`, `grok`, `gemini`, `cursor`
(`cursor-agent`), and `opencode`. The shipped config leaves `gemini`,
`cursor`, and `opencode` disabled. The harness does not store API keys.

### What a run does

[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) is the picture. In short: plan a
graph, schedule ready tasks by weight and cooldown, check out a worktree,
call a provider, review with a different provider, land accepted work on
`recursion/run/<run-id>`, and write a JSON and Markdown report. Budgets stop
a run when a known usage figure crosses its ceiling. Sample inputs are
[examples/sample-goal.txt](examples/sample-goal.txt) and
[examples/harness.json](examples/harness.json).

Commands, flags, config, and Windows and Linux troubleshooting are in
[docs/USER-GUIDE.md](docs/USER-GUIDE.md).

## Retired

The v1/v2 Hermes supervisor, decision queue, execution fabric, and remote
adapters were removed from the trunk on 2026-09-28. The prior tree is at tag
`pre-v3-clean-cut-20260928`.
