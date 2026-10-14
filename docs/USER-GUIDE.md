# Recursion user guide

This guide is for the `recursion` command in this checkout. The product map is
[docs/v3/START-HERE.md](v3/START-HERE.md). The slice notes are
[docs/v3/HARNESS-SLICE.md](v3/HARNESS-SLICE.md). The shipped config is
[config/harness.json](../config/harness.json).

`recursion` plans a task through the M1A kernel, admits frozen route fixture
`F-M1B-001`, and then runs a provider. The selected route id on that fixture
is `route-a`. Planning also records the separate ids `ROUTE-INCLUDED` and
`ROUTE-ZERO`. Those are not provider names, and a capability match does not
rename them.

## Install

Python 3.11 or 3.12 and Git. From the repository root.

Linux:

```bash
python -m pip install -e .
```

Windows PowerShell:

```powershell
python -m pip install -e .
```

The editable install registers the `recursion` console script from
`pyproject.toml`. Commands that plan or run read `config/harness.json` and the
M1 fixtures from this checkout, so install from the repository, not from a
bare wheel.

Without installing, from the repository root:

Linux:

```bash
python -X utf8 -B scripts/recursion --help
```

Windows PowerShell:

```powershell
python -X utf8 -B scripts/recursion --help
```

`requirements.txt` is the test pin, including `jsonschema` 4.23.0. Planning
and routing load that checker. Install it before `plan` or `run`:

```bash
python -m pip install -r requirements.txt
```

## Quickstart

The `fixture` provider returns a deterministic transcript and starts no
process. It does not need `--allow-live`.

Linux:

```bash
recursion run --task "Say hello" --provider fixture
```

Windows PowerShell:

```powershell
recursion run --task "Say hello" --provider fixture
```

Stdout is one JSON object. Stderr is JSONL events (`plan.admitted`,
`route.selected`, `provider.candidates`, `task.started`, `provider.attempt`,
`provider.result`, `task.completed`). A successful single task includes
`status` `completed`, `run_id`, `execution.text`, and `report` paths. The
fixture text is:

```text
provider=fixture
route=route-a
packet=<packet id>
Say hello
```

With only `fixture` as a candidate, review is `skipped` because there is no
second provider. The default `review.accept_unreviewed` is false, so the task
is `unreviewed` and the command exits `2`. The JSON result is still printed.
Set `accept_unreviewed` to true when a missing reviewer should leave the
worker result accepted. Exit code `0` means the run completed. Exit code `2`
means the command refused the request or the run ended `budget-exceeded`,
`cancelled`, `conflict`, `failed`, `review-rejected`, `skipped`, or
`unreviewed`.

## Commands and flags

`recursion --help` lists these subcommands and no others:

```text
usage: recursion [-h] {plan,run,status,resume,cancel,providers} ...
```

`-h` and `--help` show that text and exit. Every subcommand also accepts
`-h` / `--help`, `--config`, and `--state-dir`.

| Flag | Help text | Where |
|---|---|---|
| `-h`, `--help` | show this help message and exit | every command |
| `--config CONFIG` | provider config JSON (default: config/harness.json) | every command |
| `--state-dir STATE_DIR` | directory for resumable run records | every command |

The default state directory is `.recursion/runs` in the repository root.
One run is `RUN-` plus 16 hex characters, stored as `<run-id>.json`.

### plan

```text
usage: recursion plan [-h] [--config CONFIG] [--state-dir STATE_DIR]
                      [--task TASK] [--goal GOAL] [--log LOG]
```

Help: admit tasks and the M1B route; do not start a provider.

| Flag | Help text |
|---|---|
| `--task TASK` | one task admitted through M1A |
| `--goal GOAL` | plan a task graph, or one task per line when planning falls back |
| `--log LOG` | append JSONL events to this file as well as stderr |

Pass exactly one of `--task` or `--goal`. `--task` returns `planning`,
`route`, and `task`. `--goal` asks a provider for a task graph and returns
`goal`, `plan_source`, `plan_fallback`, `route`, and `tasks`. Each task has
`id`, `depends_on`, `required_capabilities`, and its own M1A admission.
`plan` does not take `--provider`, `--capability`, `--fallback`,
`--allow-live`, or `--run`. Planning uses the configured preference order
and does not start a live CLI.

### run

```text
usage: recursion run [-h] [--config CONFIG] [--state-dir STATE_DIR]
                     [--task TASK] [--goal GOAL] [--provider PROVIDER]
                     [--capability CAPABILITY] [--fallback] [--allow-live]
                     [--base-ref BASE_REF] [--keep-worktrees] [--log LOG]
```

Help: plan, admit a route, and execute capable providers.

| Flag | Help text |
|---|---|
| `--task TASK` | one task admitted through M1A |
| `--goal GOAL` | plan a task graph and run it; line splitting is the fallback |
| `--provider PROVIDER` | use this provider instead of capability order |
| `--capability CAPABILITY` | extra capability the provider must have |
| `--fallback` | after an explicit provider fails, try the next capable provider |
| `--allow-live` | start a headless CLI; omitted in tests and CI |
| `--base-ref BASE_REF` | git ref the run branch is cut from (default: config landing.base_ref) |
| `--keep-worktrees` | keep worktrees and branches for failed tasks |
| `--log LOG` | append JSONL events to this file as well as stderr |

Pass exactly one of `--task` or `--goal`. `--capability` may be repeated.
`--fallback` is refused unless `--provider` is set. `--task` prints one task
result when the status is `completed` or `unreviewed`. `--goal` prints the
saved run record. A single task that fails prints the error on stderr and
does not print the JSON result.

### status

```text
usage: recursion status [-h] [--config CONFIG] [--state-dir STATE_DIR]
                        [--log LOG] [--run RUN]
```

Help: show providers, log summary, and saved runs.

| Flag | Help text |
|---|---|
| `--log LOG` | JSONL file to summarize |
| `--run RUN` | print one saved run |

`--log` reads a file. It does not append. The payload has `config_version`,
`log` (`events`, `last_event`, `path`), `providers`, `routing`, and `runs`.
`--run` adds the full record under `run`. Each listed run has `completed`,
`goal`, `run_id`, `status`, and `tasks`.

### resume

```text
usage: recursion resume [-h] [--config CONFIG] [--state-dir STATE_DIR] --run
                        RUN [--allow-live] [--base-ref BASE_REF]
                        [--keep-worktrees] [--log LOG]
```

Help: continue unfinished tasks from a saved run.

| Flag | Help text |
|---|---|
| `--run RUN` | required; `--help` prints no description |
| `--allow-live` | `--help` prints no description |
| `--base-ref BASE_REF` | git ref used when the run branch does not exist yet |
| `--keep-worktrees` | keep worktrees and branches for failed tasks |
| `--log LOG` | append JSONL events to this file as well as stderr |

`--allow-live` has the same effect as on `run`: a headless CLI starts only
when it is set. Resume clears a stored cancel, marks the run `running`, and
sets tasks in `failed`, `cancelled`, `running`, `budget-exceeded`,
`review-rejected`, `skipped`, `conflict`, or `unreviewed` back to `pending`.
Tasks already `completed` stay completed. The saved `depends_on` list is kept,
so a retried dependency can unblock the tasks that were waiting on it.

### cancel

```text
usage: recursion cancel [-h] [--config CONFIG] [--state-dir STATE_DIR] --run
                        RUN
```

Help: cancel unfinished tasks in a saved run.

| Flag | Help text |
|---|---|
| `--run RUN` | required; `--help` prints no description |

`cancel` does not take `--allow-live` or `--log`. It sets `cancel_requested`
and marks `pending` and `running` tasks `cancelled` with error `run cancelled`.
A run whose tasks are all `completed` stays `completed`. Any other mix is
`cancelled`. A live driver checks the flag between attempts and stops.

### providers

```text
usage: recursion providers [-h] [--config CONFIG] [--state-dir STATE_DIR]
```

Help: show each provider, whether its CLI is found, its capabilities, and cooldown status.

`providers` prints one JSON object. `providers` is a list, in config order.
Each row has `name`, `enabled`, `command` (the first argv entry),
`capabilities`, `weight`, `cli_found`, and `cooldown`. `cooldown` is `null`
or `{reason, until}`. `until` is UTC, `YYYY-MM-DDTHH:MM:SSZ`.

`cli_found` is true for `fixture` without looking it up. For every other
provider it is true when the command resolves on `PATH`. The command does
not start the CLI and does not probe sign-in. Active cooldowns come from
`<state-dir>/cooldowns.json`.

## Config reference

`config/harness.json` is the default file. The loader requires version `1`
and exactly these top-level keys: `version`, `review`, `landing`, `budgets`,
`orchestration`, `providers`, `routing`. A missing or extra key is refused.
There is no second default object: the values below are the file's values.

Secret-shaped keys are refused anywhere in the file, in any letter case:
`api_key`, `apikey`, `api-key`, `token`, `secret`, `password`,
`authorization`, `credential`, and `xai_api_key`. The harness does not read
environment credentials and does not store keys.

### version

Default `1`. Must be the integer `1`.

### review

| Key | Default | Meaning |
|---|---|---|
| `max_rounds` | `2` | Integer `>= 1`. How many times a different provider may review one task. |
| `accept_unreviewed` | `false` | Boolean. When false, a task with no finished reviewer is `unreviewed`. When true, that task is accepted. |

### landing

| Key | Default | Meaning |
|---|---|---|
| `base_ref` | `HEAD` | Non-empty git ref, without a newline, from which `recursion/run/<run-id>` is cut. `--base-ref` overrides it. |

### budgets

A ceiling stops the run when a known usage figure is greater than that
ceiling. A figure the provider did not report stays unknown and does not
count as zero. `null` means no ceiling.

| Key | Default | Meaning |
|---|---|---|
| `max_input_tokens` | `1000000` | `null` or an integer `>= 0`. Input-token ceiling. |
| `max_output_tokens` | `1000000` | `null` or an integer `>= 0`. Output-token ceiling. |
| `max_cost` | `null` | `null` or a number `>= 0`. Cost ceiling. |

### orchestration

| Key | Default | Meaning |
|---|---|---|
| `concurrency` | `2` | Integer `>= 1`. How many ready tasks run at once. |

### routing

| Key | Default | Meaning |
|---|---|---|
| `required_capabilities` | `["execute"]` | Every selected provider must have each of these. |
| `preference` | `["fixture", "claude", "codex", "grok"]` | Order of capable providers. Each configured provider once. |
| `retries` | `1` | Integer `>= 0`. Extra tries of the same provider after the first. |
| `backoff_seconds` | `1` | Integer `>= 0`. On a transient error or a timeout, wait `backoff_seconds * (attempt + 1)` before the next try of that provider. |
| `cooldown_seconds` | `60` | Integer `>= 0`. How long a provider stays unavailable when the CLI does not report a reset time. |
| `weights` | `1` for each provider | Object naming each provider once. Integer `>= 1`. Higher weight is tried first. Equal weights keep `preference` order. |

### providers

A non-empty list. Every registered provider appears once. Each object has
exactly `name`, `enabled`, `capabilities`, `argv`, and `timeout_seconds`.
`argv` and `capabilities` must match the adapter. They cannot be edited into
a different command.

| name | enabled | capabilities | argv | timeout_seconds |
|---|---|---|---|---|
| `fixture` | `true` | `execute`, `deterministic` | `fixture-provider --output-format json` | `120` |
| `claude` | `true` | `execute`, `stream-json`, `subscription` | `claude -p --output-format stream-json` | `120` |
| `codex` | `true` | `execute`, `jsonl`, `subscription` | `codex exec --json` | `120` |
| `grok` | `true` | `execute`, `streaming-json`, `subscription` | `grok -p --output-format streaming-json` | `120` |

`enabled` is a boolean. A disabled provider is skipped. Naming it with
`--provider` is an error. `timeout_seconds` is an integer `>= 1`. A live
process that exceeds it fails as a timeout. The `fixture` adapter never
starts a process, including when its argv names `fixture-provider`.

## Providers

Live CLIs start only with `--allow-live`. Tests and CI omit that flag. The
executable must be on `PATH` and already signed in with that product's own
login. Recursion does not run a login command, does not pass a key, and does
not store one.

### Fixture

No install and no sign-in. `recursion run --provider fixture` is the local
path. An execute transcript names the provider, the route, the packet, and
the task. A review transcript is `VERDICT approve` followed by `fixture review`.
A plan whose goal starts with a line `graph` is a dependency list. Each
following line is `id: description`, then optional ` requires cap,cap`, then
optional ` depends id,id`. Any other goal is still one independent task per
non-empty line. An invalid graph falls back to that line split.

### Claude Code

Install Claude Code so `claude` is on `PATH`, and sign in with Claude Code
itself. With `--allow-live`, the harness runs `claude -p --output-format stream-json`
and writes the task to the process stdin.

### Codex

Install the Codex CLI so `codex` is on `PATH`, and sign in with that CLI.
With `--allow-live`, the harness runs `codex exec --json` and passes the task
as the prompt argument. Stdin is not attached.

### Grok Build

Install Grok Build so `grok` is on `PATH`, and sign in with that CLI. With
`--allow-live`, the harness runs `grok -p <task> --output-format streaming-json`.
Stdin is not attached.

If the executable is missing, the error names the command and does not copy
stderr. Provider stderr is not written into the run record or the JSONL log.

## Capability routing, retries, and fallback

Routing keeps providers that are `enabled` and that hold every required
capability. Higher `weights` run first. Equal weights keep `preference`
order. `--capability` adds to that required set. This choice is not the M1B
route id.

`--provider` must be enabled and capable. Without `--fallback` it is the only
candidate. With `--fallback` it runs first, then the other capable providers
in weight order.

A provider already in cooldown is skipped. The attempt is `cooldown` plus
the stored reason, and the CLI is not started. An explicit `--provider`
without `--fallback` fails while it is cooling. With `--fallback`, the next
capable provider runs.

Availability failures are not task failures. Exit code `401` or an auth
phrase (`auth expired`, `not logged in`, `please log in`, `unauthorized`,
`invalid api key`, and the same family) is `auth-expired`. Exit code `402`
or a quota phrase (`quota`, `resource_exhausted`, `out of credits`,
`billing`, and the same family) is `quota-exhausted`. Exit code `429` or a
rate phrase (`rate limit`, `too many requests`, `overloaded`) is
`rate-limited`. The harness records a cooldown and moves to the next
eligible provider. It does not retry that provider in place. A reset time
in the output (`retry-after: 30`, `try again in 2 minutes`, or an ISO time
such as `2026-10-14T08:35:00Z`) sets `until`. Otherwise `until` is now plus
`cooldown_seconds`. The output itself is not stored.

A timeout, exit `500`/`502`/`503`/`504`, or a transient phrase
(`temporarily unavailable`, `connection reset`, `connection refused`,
`timed out`) retries the same provider with backoff, up to `retries`. Any
other non-zero exit is a task failure: it is retried without waiting, then
the next candidate runs. `RunCancelled` stops immediately. The recorded
error is the exception class, not the process output.

Cooldowns live in `<state-dir>/cooldowns.json` (by default
`.recursion/runs/cooldowns.json`). Later tasks and later runs skip a
provider until `until`. The same snapshot is copied onto the run record as
`cooldowns`.

`recursion plan --goal` and `recursion run --goal` ask the first capable
provider for one JSON object whose only key is `tasks`. The prompt includes
a `depends_on` example: `test` depends on `build`, and independent tasks use
`[]`. Each task has `id`, `description`, `required_capabilities`, and
`depends_on`. The harness checks the shape, unique ids, known dependency
ids, and cycles. Invalid output, or
no planning provider, falls back to one task per non-empty line and logs
`plan.fallback` with a fixed reason. The raw planner body is not stored.
Each description is still its own M1A admission. A task's
`required_capabilities` further filters its candidates. Task `i` starts at
the `i`-th remaining candidate, then continues in order. A task starts only
after every dependency is `completed` and landed, and its worktree is cut
from the run branch so it sees that work. A failed, rejected, conflicted,
or unreviewed dependency marks dependents `skipped` with
`dependency <id> is <status>`.

## Cross-provider review

After a worker finishes, a different candidate reviews the task, the output,
and the diff. The reviewer is asked to put `VERDICT approve` or
`VERDICT revise` on the first non-empty line.

| First line | Result |
|---|---|
| `VERDICT approve` | The task is accepted. Notes may follow. |
| `VERDICT revise` | Notes go back to the same worker, until `review.max_rounds`. |
| anything else | Treated as revise. The raw body is not stored. |
| empty | Treated as revise. The note is `reviewer returned no verdict`. |

Notes stored on the task are at most 1000 characters. The prompt clips the
output and the diff at 2000 characters. The reviewer can read the worktree.
Edits it makes are removed, the verdict is `rejected-write`, and the raw
review body is not stored. If no other provider exists, the verdict is
`skipped` (`no distinct reviewer`). If every reviewer fails, the verdict is
`skipped` (`no reviewer completed`) and the failed attempts are stored on
that review. Reviewer writes made before the failure are removed too.
With `accept_unreviewed` false, either skip leaves the task `unreviewed`
and does not merge it. With `accept_unreviewed` true, the worker result is
accepted. A revise on the last round, or a rejected write on the last round,
sets the task to `review-rejected`.

## Worktrees

A run branch `recursion/run/<run-id>` is cut from `landing.base_ref`
(default `HEAD`, overridable with `--base-ref`). Each task gets a worktree
and branch `recursion/task/<run-id>/task-<index>`, cut from the run branch.
The two namespaces stay separate so git can store both refs. The provider's
working directory is that worktree. If the provider leaves uncommitted
edits, the harness commits them as `recursion: land <id>`. A commit the
provider already made is kept. Accepted branches are merged with `--no-ff`
into the run branch. A merge conflict aborts that merge, records the
conflict paths, and sets the task to `conflict`. Unreviewed branches are
kept and are not merged. Failed and rejected branches are deleted unless
`--keep-worktrees` is set. A run that lands nothing deletes the empty run
branch. Parallel git operations take one lock per repository. The stored
diff is the commits, the patch, and `git status`, and it is cut at 8000
characters with a `[diff truncated]` suffix. The commits on the branch are
the full result.

## Reports, usage, and budgets

When a run finishes, the state directory gains `<run-id>.report.json` and
`<run-id>.report.md`. The report lists the run status, stop reason, duration,
and usage, plus `run_branch`, `base_ref`, and `plan_source`. Each task lists
its text, id, dependencies, provider, attempts, review verdicts, branch,
commit, merge status, duration, and diff.

Usage is read from provider stdout when a JSON line carries it. The last such
object wins. Recognized fields are `input_tokens` or `prompt_tokens`,
`output_tokens` or `completion_tokens`, and `cost` or `total_cost_usd`. A
missing figure stays unknown. Known figures from the worker and from reviews
are added. Crossing a budget sets `stop_reason` to `budget`, asks the run to
stop, and marks unfinished tasks `budget-exceeded`.

## Run state, resume, and cancel

Run records live under `.recursion/runs` unless `--state-dir` is set. The
directory is gitignored. Status values include `running`, `completed`,
`failed`, `cancelled`, `review-rejected`, `budget-exceeded`, `conflict`,
`unreviewed`, and `skipped`. The task graph (`id`, `depends_on`,
`required_capabilities`) is stored on the run, so `resume` continues it.

`recursion status` lists saved runs. `recursion status --run RUN-...` prints
one record. `recursion resume --run RUN-...` continues tasks that are not
`completed`. `recursion cancel --run RUN-...` cancels tasks that are still
`pending` or `running`. A driver that is already inside a provider call
notices the cancel before the next attempt.

## Troubleshooting

| Message | What it means |
|---|---|
| `pass one of --task or --goal` | `plan` and `run` need exactly one of those flags. |
| `--fallback applies to an explicit --provider` | `--fallback` was set alone. |
| `unrecognized arguments` | The flag is not on that subcommand. Exit code 2. |
| `missing provider config` | `--config` or `config/harness.json` is not a file. |
| `provider config is not JSON` | The file does not parse. |
| `config keys mismatch` | A required key is missing or an unknown key is present. |
| `config key '...' is not allowed` | The key looks like a secret. |
| `provider config version must be 1` | `version` is not the integer `1`. |
| `unknown provider` | The name is not `fixture`, `claude`, `codex`, or `grok`. |
| `provider '...' is disabled` | `--provider` names an entry with `enabled` false. |
| `does not satisfy capabilities` | The provider lacks a required capability. |
| `no enabled provider satisfies capabilities` | Nothing enabled matches. |
| `M1B route was not selected` | Fixture `F-M1B-001` did not select a route. |
| `task text is empty` | Blank `--task`. |
| `task text contains a NUL` | The task contains a NUL. |
| `task text is not UTF-8` | The task does not encode as UTF-8. |
| `task text exceeds the M1A text bound` | The task is longer than 4096 characters or 4096 UTF-8 bytes. |
| `goal text is empty` | `--goal` has no non-empty line. |
| `headless CLI is not started unless --allow-live is set` | A live provider was selected without `--allow-live`. |
| `CLI was not found on PATH` | Install that CLI or pick another provider. |
| `timed out after N seconds` | The process exceeded that provider's `timeout_seconds`. |
| `was rate-limited` | The process exited 429 or its stderr said it was rate limited. The log does not keep that stderr. |
| `exited N` | The process failed for another reason. Stderr is not stored. |
| `budget exceeded` | A known usage figure is above its ceiling. |
| `no provider completed the task` | Every candidate failed. |
| `unknown run` | `--run` does not match a file in the state directory. |
| `not a run id` | The id is not `RUN-` plus 16 hex characters. |
| `malformed log` | A `--log` line is not a JSON object with an `event` string. |
| `git <subcommand> failed (N)` | Git could not add or remove the task worktree. Stderr is not stored. |
| `merge conflict` | An accepted task branch did not merge into the run branch. The conflicting paths are named when git reports them. |
| `review did not complete` | No reviewer finished, and `accept_unreviewed` is false. |
| `dependency <id> is <status>` | A task did not start because a dependency was not accepted. |
| `no provider has the required capabilities` | The task's `required_capabilities` matched no candidate. |
| `planner returned invalid JSON` | The planner's text was not the required object, so the goal fell back to lines. |

`plan`, `run`, and `resume` also emit a `run.refused` JSONL event when they
raise one of these errors.

## Windows

Use PowerShell for the install and quickstart above. The harness reads and
writes config, logs, run records, and provider output as UTF-8. When you use
`scripts/recursion` instead of the console script, start it with
`python -X utf8` so the Windows console uses UTF-8 too.

Task worktrees are created with `git -c core.longpaths=true`. Turn on Windows
long paths if a worktree path still exceeds the legacy path limit. This
repository stores text as LF (`.gitattributes`). Leave `core.autocrlf` off so
a checkout does not rewrite the fixtures the checkers compare byte for byte.
