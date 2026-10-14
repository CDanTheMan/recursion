# Recursion

This fork, [CDanTheMan/recursion](https://github.com/CDanTheMan/recursion), is standalone
development. Product orientation is [docs/v3/START-HERE.md](docs/v3/START-HERE.md). It does
not use the CSL Laboratories issue tracker, review bot, search MCPs, CI service, or Discord
bot. `AGENTS.md` and `CLAUDE.md` stay byte-identical.

## What this is

Recursion v3 is a provider-neutral agent harness: a client, a local execution kernel, a
context and compaction engine, and a multi-node fabric, plus typed adapters for other
harnesses. A person should be able to drive it on the models they already use, without
locking the workflow to one provider.

The tree is specifications, contract schemas, and provider-free checks. There is no
application binary to compile.

V1/v2 were removed from the trunk on 2026-09-28. That tree is at tag
`pre-v3-clean-cut-20260928`.

## Layout

| Path | What it is |
|---|---|
| `docs/v3/` | Product specifications, research, and evidence. Start with `START-HERE.md` and `PRODUCT.md`. |
| `experiments/v3/` | Provider-free experiments and checks |
| `schemas/control-plane/v3/` | Planning, execution, and integrity schemas |
| `scripts/v3/` | Planning replay and validation |
| `scripts/tests/v3/` | M1 test programs and fixtures (planning, execution, integrity) |
| `tools/` | Frozen orientation and scope checks |
| `state/` | Decision log and goal records |

## Build and test

Python 3.11+ and Git, from the repository root. Install the pinned dependencies
in `requirements.txt` first. Tests import `jsonschema` (Draft 2020-12; 4.23.0 is
the version this suite was run with). Nothing else is built.

```bash
set -euo pipefail
python -m pip install -r requirements.txt
python -X utf8 -B -m pytest
python -X utf8 -B tools/check_v3_orientation.py --contracts
python -X utf8 -B tools/test_check_v3_orientation_scope.py
python -X utf8 -B schemas/control-plane/v3/planning/materialize.py --check
python -X utf8 -B schemas/control-plane/v3/execution/materialize.py --check
python -X utf8 -B schemas/control-plane/v3/integrity/materialize.py --check
python -X utf8 -B scripts/tests/v3/planning/materialize_fixtures.py --check
python -X utf8 -B scripts/tests/v3/execution/materialize_fixtures.py --check
python -X utf8 -B scripts/tests/v3/integrity/materialize_fixtures.py --check
find scripts/tests/v3 -name '*.test.py' -print | sort | while IFS= read -r f; do
  python -X utf8 -B "$f"
done
python -X utf8 -B experiments/v3/recovery-ledger-20260914/test_ledger.py
```

That is the suite: six materialize checks, every `scripts/tests/v3/**/*.test.py` program,
and the recovery-ledger tests. Keep it green. Fix the cause of a failure. Do not delete,
skip, or weaken a check to make the run pass.

`tests/` is the pytest suite CI runs. It wraps the orientation contracts, the
scope tests, and the schema and fixture validators, and it prints coverage.
GitHub Actions (`.github/workflows/ci.yml`) runs that suite, plus the orientation
`--contracts` check and the scope tests directly, on pull requests and on
pushes to `master`, for `ubuntu-latest` and `windows-latest` and Python 3.11
and 3.12.
The orientation gate diffs the worktree against the merge-base with master.
Paths outside its allowlist fail. Do not delete product files to satisfy it.
It still requires this file and `CLAUDE.md` to match, and the text
`docs/v3/START-HERE.md` in the first 2200 characters of each.

## Coding conventions

- Checks and experiments are Python 3.11+. Runtime code stays on the standard library.
  `jsonschema` is for tests and schema validation.
- `from __future__ import annotations`, `pathlib`, and `unittest`. Run with
  `python -X utf8 -B`.
- Schemas are closed JSON Schema objects. Fixture ids stay contiguous (`F-M1A-001`, and
  the same pattern for M1B and M1C).
- Markdown is plain. Dates are `YYYY-MM-DD`.
- No secrets, tokens, or credentials in tracked files.
- Checks stay provider-free. Do not call a live provider, host, or paid API from a test.

## Branch and pull request

Work on this fork.

1. Branch from up-to-date `master`.
2. Commit on that branch. Do not commit to `master`.
3. Push the branch and open a pull request against `master`.
4. Never `git push --force`.

Dan reviews and merges. Open the pull request with the suite green.
