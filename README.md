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
(Draft 2020-12) and pytest.

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
| `docs/v3/` | Product specifications, research, and evidence |
| `experiments/v3/` | Provider-free experiments and checks |
| `schemas/control-plane/v3/` | Planning, execution, and integrity schemas |
| `scripts/v3/` | Planning replay and validation |
| `scripts/tests/v3/` | M1 test programs and fixtures |
| `tests/` | Pytest suite that wraps those v3 checks |
| `tools/` | Orientation gate and scope tests |
| `state/` | Decision log and goal records |

## Harness

Harness usage is recorded in [docs/v3/HARNESS-SLICE.md](docs/v3/HARNESS-SLICE.md).

## Retired

The v1/v2 Hermes supervisor, decision queue, execution fabric, and remote
adapters were removed from the trunk on 2026-09-28. The prior tree is at tag
`pre-v3-clean-cut-20260928`.
