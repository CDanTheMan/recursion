# Recursion

**Recursion v3** is a provider-neutral agent platform: a harness with its own client,
execution kernel, context/compaction engine and multi-node fabric, plus adapters for
supported upstream harnesses. The current development target and single source of truth is
[docs/v3/START-HERE.md](docs/v3/START-HERE.md).

V1/v2 — the previous Hermes-based supervisor and control plane — are **retired**. They were
removed from the trunk on 2026-09-28 and remain recoverable from the
`pre-v3-clean-cut-20260928` tag.

Start here:

- [docs/v3/START-HERE.md](docs/v3/START-HERE.md) — orientation and specification map
- [docs/v3/RESEARCH-SCOPE.md](docs/v3/RESEARCH-SCOPE.md) — research goals and the gates that pass
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute
- [ANCHOR.md](ANCHOR.md) — why the work exists; [CONTROL_PLANE.md](CONTROL_PLANE.md) — who decides

> Governance note: `CONTROL_PLANE.md` and `ANCHOR.md` are the operative authority and scope
> records. They still describe the pre-v3 control plane and will be rewritten in an
> Owner-authoring session, not edited as part of a cleanup.

## Layout

| Path | What it is |
|---|---|
| `docs/v3/` | v3 product specifications, research and evidence |
| `experiments/v3/` | v3 research experiments and provider-free evidence checks |
| `schemas/control-plane/v3/` | v3 contract schemas (planning, execution, integrity) |
| `scripts/v3/` | v3 planning replay and validation |
| `scripts/v3/harness/` | harness slice: plan a task, admit one route, run one provider |
| `scripts/tests/v3/` | v3 M1 test programs and fixtures |
| `tools/check_v3_orientation.py` | the frozen 2026-09-13 orientation-repair gate |
| `state/` | decision log and v3 goal/task records |

## Run the harness

The harness plans one task with the M1A kernel, admits a route with the M1B reference checker, and runs one provider adapter. The default provider is a local fixture. It does not call a live CLI and does not read credentials.

From the repository root, with Python 3.11 or newer. Route admission uses the M1B schema checker, which imports `jsonschema` 4.23.0:

```text
python -m pip install "jsonschema==4.23.0"
python -X utf8 -B -m scripts.v3.harness --task "Summarize the harness slice" --provider fixture
```

On Windows, if `python` is not the 3.11+ launcher, use `py -3` with the same flags. Paths in this repository exceed 260 characters. Prefix git commands with `git -c core.longpaths=true` for clone, checkout, status, and diff. That flag is per command. The Python command above does not change.

`--provider claude` is the headless CLI adapter. Its argv is `claude -p --output-format stream-json`, and the task is written to that process's stdin. The process is not started unless you also pass `--allow-live`. Leave that flag off in tests and CI.

The contracts gate runs the existing M1 checks and the harness test:

```text
python -X utf8 -B tools/check_v3_orientation.py --contracts
```

The shape of this slice is recorded in [docs/v3/HARNESS-SLICE.md](docs/v3/HARNESS-SLICE.md).

## Retired

The v1/v2 custom harness — the Hermes executive, supervisor loop, decision queue, project
pilot and reconciler, `work.sh`/`publish.sh`, the MVP contract kernel, execution fabric,
remote adapters, and their configs and deployment units — was removed from the trunk on
2026-09-28 because it contributed no dependency to v3.
Nothing is lost: the complete prior tree is at tag `pre-v3-clean-cut-20260928` and in git
history.
