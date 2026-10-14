# Changelog

## 0.2.0 — 2026-10-14

This is the standalone fork [CDanTheMan/recursion](https://github.com/CDanTheMan/recursion).
The v1/v2 trunk was removed on 2026-09-28 and remains at tag
`pre-v3-clean-cut-20260928`. The notes below are what landed on this fork
after that cut.

### Added

- `recursion` console script, installed with `python -m pip install -e .`.
  Subcommands: `plan`, `run`, `status`, `resume`, `cancel`.
- Provider adapters `fixture`, `claude`, `codex`, and `grok`. Live CLIs start
  only with `--allow-live`. The config refuses secret-shaped keys.
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
