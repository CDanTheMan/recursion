# Changelog

## Unreleased

### Added

- `scripts/install.sh` and `scripts/install.ps1` create a virtualenv, install
  this checkout, run `recursion doctor`, and print the next commands. CI runs
  the Linux script and the Windows script, then checks `recursion --help`.
  The package depends on `jsonschema` 4.23.0 so that install can validate
  `config/harness.json`.
- Fake-only tests cover thin harness branches in stream parsing, config
  rejection, doctor sign-in probes, cooldown files, and run records. They
  do not start a provider CLI.

### Changed

- `recursion cancel` stops a live provider process that is still running, and a
  provider `timeout_seconds` stops it the same way. Children started by that
  process are stopped too: a process group on Linux and a job object on
  Windows. Resume still continues tasks that were cancelled.
- `recursion clean` leaves a run in place when it is `running`, `pending`, or
  resumable, and records the reason under `skipped`. An unlanded run branch
  (no `land.status` of `merged`, and not already in the current or default
  branch) and a worktree with uncommitted changes are skipped unless
  `--include-unlanded` is set. `--dry-run` prints the same removed and skipped
  lists.
- `recursion land` refuses a target branch that is checked out in another
  worktree. The merge commit uses the repository's git identity when one is
  configured, and the recursion identity otherwise.

## 0.2.0 — 2026-10-14

This is the standalone fork [CDanTheMan/recursion](https://github.com/CDanTheMan/recursion).
The v1/v2 trunk was removed on 2026-09-28 and remains at tag
`pre-v3-clean-cut-20260928`. The notes below are what landed on this fork
after that cut.

### Added

- `recursion` console script, installed with `python -m pip install -e .`.
  Subcommands: `plan`, `run`, `status`, `resume`, `cancel`, `providers`, `doctor`,
  `init`, `config validate`, and `logs`.
- Provider adapters `fixture`, `claude`, `codex`, and `grok`. Live CLIs start
  only with `--allow-live`. The config refuses secret-shaped keys.
- Provider adapters `gemini`, `cursor` (`cursor-agent`), and `opencode`,
  disabled in the default config. `recursion doctor` checks git, PATH
  (including Windows `.cmd` and `.exe` shims), version, and a cheap sign-in
  without printing secrets. `recursion init` writes a starter config and
  enables the providers whose commands resolve. Opt-in live smokes stay off
  unless `RECURSION_LIVE=1` and the CLI is present, and they stay off in CI.
- Capability routing, retries, fallback, per-task git worktrees, cross-provider
  review, run reports, usage figures, and budgets.
- Saved runs under `.recursion/runs`, with resume and cancel.
- Orientation gate that compares a work branch with the merge-base of `master`,
  and still accepts `--baseline` for the historical pin.
- GitHub Actions CI on pull requests and on pushes to `master`: Ubuntu and
  Windows, Python 3.11 and 3.12. The job runs the orientation contracts, the
  scope tests, and pytest with coverage.
- Pytest suite under `tests/` that wraps those v3 checks.
- User guide in `docs/USER-GUIDE.md`, a drift test that keeps it aligned with
  `recursion --help` and `config/harness.json`, and a release workflow that
  builds an sdist and a wheel on `v*` tags.
- Accepted task branches merge into `recursion/run/<run-id>`. A provider
  plans `--goal` into a dependency graph, and a missing reviewer is
  `unreviewed` unless `review.accept_unreviewed` is true.
- Capability weights, distinct rate-limit, quota, and auth failures, and
  automatic fallback to the next eligible provider. Cooldowns persist in
  the run state directory. `recursion providers` shows CLI presence,
  capabilities, and cooldown status. The planner prompt asks for
  `depends_on`, and a fixture goal that starts with `graph` emits a real
  dependency list.
- Sample goal and config in `examples/`, and a console end-to-end test that
  installs `recursion` and drives `plan`, `run`, `status`, `cancel`, `resume`,
  and the report through fake `claude`, `codex`, and `grok` executables.
- `config/harness.schema.json` is checked when a config is loaded.
  `recursion config validate` reports the field and the schema error.
- Event logs, run records, and reports replace token-shaped text with
  `[REDACTED]`. `recursion logs RUN-...` prints a run's JSONL and can filter
  by task, provider, and level.
- `run` and `resume` accept `--concurrency N` (integer `>= 1`) to override
  `orchestration.concurrency` for that invocation. The effective value is
  stored on the run. Resume without the flag keeps the stored value. When
  stderr is a terminal, or when `--progress` is set, those commands print
  plain progress lines on stderr. JSONL stays on `--log`, and on stderr when
  progress lines are off.
- A dependent task's prompt includes a size-capped summary, commit, and diff
  for each dependency. The planner prompt includes a size-capped repository
  map of tracked files and key docs.
- `recursion land <run-id>` merges a finished run branch into the current
  branch, or `--into`, with a normal non-fast-forward merge. A dirty tree or
  a conflict is refused and recorded in the report. `recursion clean` prunes
  old run state, worktrees, and task branches, with `--older-than` and
  `--dry-run`.
- `docs/ARCHITECTURE.md` diagrams plan, schedule, worktree, provider,
  review, landing, and report. The README and user guide cover the landed
  providers and commands, with Linux and Windows troubleshooting. The docs
  drift test checks subcommands, flags, provider names, config keys, and
  that diagram.
