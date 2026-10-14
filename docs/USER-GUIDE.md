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

Stdout is one JSON object. When stderr is not a terminal, it is JSONL
events (`plan.admitted`, `route.selected`, `provider.candidates`,
`task.started`, `provider.attempt`, `provider.result`, `task.completed`).
When stderr is a terminal, or when `run` or `resume` is passed `--progress`,
stderr is short plain lines for those events instead. `--log` keeps the
JSONL stream in a file either way. A successful single task includes
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
usage: recursion [-h]
                 {plan,run,status,resume,cancel,providers,doctor,init,config,logs}
                 ...
```

`-h` and `--help` show that text and exit. `plan`, `run`, `status`,
`resume`, `cancel`, and `providers` also accept `--config` and `--state-dir`.
`doctor` accepts `--config` and does not accept `--state-dir`. `init` accepts
a path and `--force`, and does not accept `--config` or `--state-dir`.
`config validate` accepts `--config`. `logs` accepts `--state-dir` and does
not read the config.

| Flag | Help text | Where |
|---|---|---|
| `-h`, `--help` | show this help message and exit | every command |
| `--config CONFIG` | provider config JSON (default: config/harness.json) | `plan`, `run`, `status`, `resume`, `cancel`, `providers`, `doctor`, `config validate` |
| `--state-dir STATE_DIR` | directory for resumable run records | `plan`, `run`, `status`, `resume`, `cancel`, `providers`, `logs` |

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
| `--log LOG` | append JSONL events to this file, and to stderr when progress lines are off |

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
                     [--base-ref BASE_REF] [--keep-worktrees]
                     [--concurrency CONCURRENCY] [--progress] [--log LOG]
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
| `--concurrency CONCURRENCY` | override orchestration.concurrency for this invocation |
| `--progress` | print plain progress lines on stderr instead of JSONL |
| `--log LOG` | append JSONL events to this file, and to stderr when progress lines are off |

Pass exactly one of `--task` or `--goal`. `--capability` may be repeated.
`--fallback` is refused unless `--provider` is set. `--task` prints one task
result when the status is `completed` or `unreviewed`. `--goal` prints the
saved run record. A single task that fails prints the error on stderr and
does not print the JSON result.

`--concurrency N` overrides `orchestration.concurrency` for this invocation.
`N` is an integer `>= 1`. The run record stores that value, and the scheduler
uses the stored value. Omit the flag to use the config value.

`--progress` prints plain progress lines on stderr instead of JSONL. A
terminal does the same without the flag. `--log` still receives JSONL.
Lines name the outcome (`task 0 started`, `provider fixture attempt 0`,
`task 0 completed provider=fixture`) and do not include error text.

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
                        [--keep-worktrees] [--concurrency CONCURRENCY]
                        [--progress] [--log LOG]
```

Help: continue unfinished tasks from a saved run.

| Flag | Help text |
|---|---|
| `--run RUN` | required; `--help` prints no description |
| `--allow-live` | `--help` prints no description |
| `--base-ref BASE_REF` | git ref used when the run branch does not exist yet |
| `--keep-worktrees` | keep worktrees and branches for failed tasks |
| `--concurrency CONCURRENCY` | override orchestration.concurrency for this invocation |
| `--progress` | print plain progress lines on stderr instead of JSONL |
| `--log LOG` | append JSONL events to this file, and to stderr when progress lines are off |

`--allow-live` has the same effect as on `run`: a headless CLI starts only
when it is set. Resume clears a stored cancel, marks the run `running`, and
sets tasks in `failed`, `cancelled`, `running`, `budget-exceeded`,
`review-rejected`, `skipped`, `conflict`, or `unreviewed` back to `pending`.
Tasks already `completed` stay completed. The saved `depends_on` list is kept,
so a retried dependency can unblock the tasks that were waiting on it.
`--concurrency` replaces the stored concurrency before the run continues.
Omit it to keep the value already on the record. `--progress` matches `run`.

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
`cancelled`. A live driver terminates the provider process that is still
running, and the children that process started, and does not begin another
attempt. Resume clears that cancel and can run the unfinished tasks again.

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
provider it is true when `doctor`'s PATH search finds the command, including
Windows `.exe`, `.cmd`, and `.bat` shims. The command does not start the CLI
and does not probe sign-in. Active cooldowns come from
`<state-dir>/cooldowns.json`.

### doctor

```text
usage: recursion doctor [-h] [--config CONFIG]
```

Help: check git and each configured provider executable.

| Flag | Help text |
|---|---|
| `--config CONFIG` | provider config JSON (default: config/harness.json) |

Stdout is one JSON object with `git`, `ok`, and `providers`. `ok` is true
when at least one enabled provider is usable. The process exits `0` when
`ok` is true and `1` when it is false. A bad config still exits `2`.

`git.available` is whether `git --version` succeeds. `git.version` is the
first line of that output. On Windows, `git.longpaths` is true when
`git config --get core.longpaths` prints `true`, `1`, or `yes`, and false
when it is unset or another value. On other systems `git.longpaths` is
null. A missing git does not by itself make `ok` false.

Each provider row has `name`, `command`, `enabled`, `installed`, `resolved`,
`version`, `signed_in`, `auth_method`, and `usable`. `fixture` is installed
without a PATH lookup. It is usable when it is enabled, and `signed_in` is
`not-applicable`. Another provider is installed when its command resolves on
`PATH`. On Windows the search also tries `PATHEXT` and always tries `.exe`,
`.cmd`, and `.bat`, ignoring case. It is usable when it is enabled and
installed. `version` is the first line of `<command> --version` when that
exits 0.

Sign-in checks are local and do not start a billed prompt. The report never
includes the variable's value, a credential file's contents, or the probe's
stdout.

| Provider | Check |
|---|---|
| `claude` | `claude auth status`. Exit 0 is signed in. The reported method is `authMethod` when it is one of `none`, `claude.ai`, `oauth_token`, `api_key`, `api_key_helper`, or `third_party`. |
| `codex` | `codex login status`. Exit 0 is signed in. |
| `grok` | `XAI_API_KEY` is set, or `~/.grok/auth.json` exists and is non-empty. The file is not read. |
| `gemini` | `GEMINI_API_KEY`, `GOOGLE_API_KEY`, or `GOOGLE_APPLICATION_CREDENTIALS` is set, or `~/.gemini/oauth_creds.json` exists and is non-empty. The file is not read. `GOOGLE_GENAI_USE_VERTEXAI` and `GOOGLE_GENAI_USE_GCA` alone are not treated as signed in. |
| `cursor` | `CURSOR_API_KEY` is set, otherwise `cursor-agent status --format json`. |
| `opencode` | `~/.local/share/opencode/auth.json` exists and is non-empty (the file is not read), otherwise `opencode auth list --format json --standalone`. An empty list, or the text `No authenticated integrations`, is signed out. `--standalone` keeps the check from attaching to a background server. |

A disabled provider can be installed and still not usable. The shipped config
leaves `gemini`, `cursor`, and `opencode` disabled, so a machine with only
`fixture` enabled still has `ok` true.

### init

```text
usage: recursion init [-h] [--force] path
```

Help: write a starter config that enables providers doctor can see.

| Flag | Help text |
|---|---|
| `path` | config path to create |
| `--force` | overwrite an existing file |

`init` writes a version-1 file. It enables `fixture` and every other
registered provider whose command resolves on PATH. Sign-in is not required.
The other providers are present and disabled. Budgets, review rounds,
`review.accept_unreviewed`, `landing.base_ref`, concurrency, retries,
`cooldown_seconds`, `weights`, and the capability preference match the
shipped defaults, with preference and weights listing every registered
provider once.

An existing file is left unchanged unless `--force` is set. A directory is
refused even with `--force`. Both cases exit `2`. Parent directories are
created. The file is UTF-8 with LF newlines.

### config validate

```text
usage: recursion config validate [-h] [--config CONFIG]
```

Help: check the config against the schema and the adapters.

| Flag | Help text |
|---|---|
| `--config CONFIG` | provider config JSON (default: config/harness.json) |

`recursion config validate` reads the file, checks it against
[config/harness.schema.json](../config/harness.schema.json), then applies the
same adapter checks as startup. `plan`, `run`, `status`, `resume`, `doctor`,
and `init` load the config through that same check. A schema failure names
the field, for example `routing.retries: -1 is less than the minimum of 0`.
Success prints `ok`, `path`, and `version`. Exit code `0` means the file is
valid. Exit code `2` means it is not.

### logs

```text
usage: recursion logs [-h] [--state-dir STATE_DIR] [--task TASK]
                      [--provider PROVIDER] [--level {info,warning,error}]
                      [--tail TAIL]
                      run_id
```

Help: show JSONL events for one saved run.

| Flag | Help text |
|---|---|
| `run_id` | saved run id |
| `--state-dir STATE_DIR` | directory for resumable run records |
| `--task TASK` | task index or task id |
| `--provider PROVIDER` | provider name |
| `--level {info,warning,error}` | minimum level: info, warning, or error |
| `--tail TAIL` | print only the last N matching events |

`run` and `resume` append events to `<state-dir>/<run-id>.jsonl` as well as
stderr. Each object has `event`, `ts`, and `level` (`info`, `warning`, or
`error`). Task events include `index` and `run_id`. `--task` keeps one task.
`--provider` keeps one provider. `--level warning` keeps warnings and errors.
`--level error` keeps errors. `--tail` is applied after those filters. Stdout
is JSONL, one event per line. A missing run or a missing log exits `2`.

## Config reference

`config/harness.json` is the default file. The loader requires version `1`
and exactly these top-level keys: `version`, `review`, `landing`, `budgets`,
`orchestration`, `providers`, `routing`. A missing or extra key is refused.
There is no second default object: the values below are the file's values.

Secret-shaped keys are refused anywhere in the file, in any letter case:
`api_key`, `apikey`, `api-key`, `token`, `secret`, `password`,
`authorization`, `credential`, and `xai_api_key`. The config loader does not
read environment credentials and does not store keys. `doctor` can see that a
sign-in variable is set, and it does not print the value.

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
| `concurrency` | `2` | Integer `>= 1`. How many ready tasks run at once. `--concurrency` on `run` and `resume` overrides it for that invocation and stores the effective value. Resume without the flag keeps the stored value. |

### routing

| Key | Default | Meaning |
|---|---|---|
| `required_capabilities` | `["execute"]` | Every selected provider must have each of these. |
| `preference` | `["fixture", "claude", "codex", "grok", "gemini", "cursor", "opencode"]` | Tie-break when weights are equal. Each configured provider once. |
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
| `gemini` | `false` | `execute`, `stream-json`, `subscription` | `gemini -p --output-format stream-json` | `120` |
| `cursor` | `false` | `execute`, `stream-json`, `subscription` | `cursor-agent -p --output-format stream-json` | `120` |
| `opencode` | `false` | `execute`, `json` | `opencode run --format json` | `120` |

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

### Gemini CLI

Disabled in the shipped config. Install Gemini CLI so `gemini` is on `PATH`,
set `enabled` to true, and sign in with Gemini CLI itself. With
`--allow-live`, the harness runs `gemini -p <task> --output-format stream-json`.
Stdin is not attached. `stream-json` events are newline-delimited JSON. The
assistant text is the `message` events whose role is `assistant`. Token
figures come from `result.stats` (`input_tokens`, `output_tokens`). That
object has no dollar cost, so cost stays unknown.

### Cursor CLI

Disabled in the shipped config. The install links `agent` and `cursor-agent`
to the same binary. This harness calls `cursor-agent`. Set `enabled` to true
and sign in with Cursor. With `--allow-live`, the harness runs
`cursor-agent -p --output-format stream-json <task>`. Stdin is not attached.
The assistant text is the terminal `result` string. When that event includes
`usage.inputTokens` and `usage.outputTokens`, those figures are kept. The
documented result object has no dollar cost, so cost stays unknown.

### OpenCode

Disabled in the shipped config. Install OpenCode so `opencode` is on `PATH`
and set `enabled` to true. With `--allow-live`, the harness runs
`opencode run --format json <task>`. The task is the positional message.
`-p` on this command is a password flag and is not used. Stdin is not
attached. Assistant text is the `text` events. Each `step_finish` event
contributes `part.tokens.input`, `part.tokens.output`, and `part.cost`, and
those steps are added. A stream with no `step_finish` leaves usage unknown.

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

Usage is read from provider stdout when a JSON line carries it. Claude,
Codex, Grok, Gemini, and Cursor keep the last aggregate object. OpenCode
`step_finish` events are summed, one cost and token object per step.
Recognized fields are `input_tokens`, `prompt_tokens`, or `inputTokens`;
`output_tokens`, `completion_tokens`, or `outputTokens`; and `cost` or
`total_cost_usd`. OpenCode reads those figures from `part.tokens` (`input`,
`output`) and `part.cost`. A missing figure stays unknown. A reported zero
stays zero. Known figures from the worker and from reviews are added.
Crossing a budget sets `stop_reason` to `budget`, asks the run to stop, and
marks unfinished tasks `budget-exceeded`.

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
terminates that process. A provider timeout terminates it the same way.
On Linux the call stops the process group. On Windows it stops the job
object that contains the process.

`recursion logs RUN-...` prints the JSONL file for that run. Tokens and
API-key-looking strings are replaced with `[REDACTED]` before they are
written to the event log, the run record, or the report. A secret-shaped
key in a stored object is replaced entirely.

## Troubleshooting

| Message | What it means |
|---|---|
| `pass one of --task or --goal` | `plan` and `run` need exactly one of those flags. |
| `--fallback applies to an explicit --provider` | `--fallback` was set alone. |
| `unrecognized arguments` | The flag is not on that subcommand. Exit code 2. |
| `concurrency must be an integer >= 1` | `--concurrency` was `0` or not an integer. Exit code 2. |
| `missing provider config` | `--config` or `config/harness.json` is not a file. |
| `provider config is not JSON` | The file does not parse. |
| `config keys mismatch` | A required key is missing or an unknown key is present. |
| `routing.retries:` (and other field paths) | The JSON Schema rejected that field. The text after the path says what is wrong. |
| `config key '...' is not allowed` | The key looks like a secret. |
| `provider config version must be 1` | `version` is not the integer `1`. |
| `unknown provider` | The name is not `fixture`, `claude`, `codex`, `grok`, `gemini`, `cursor`, or `opencode`. |
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
| `timed out after N seconds` | The process exceeded that provider's `timeout_seconds`. The process and the children it started are stopped. |
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

`plan`, `run`, and `resume` also emit a `run.refused` event when they
raise one of these errors. It is a JSONL line on stderr unless progress
lines are on, in which case stderr shows `run refused` and the error class.

## Windows

Use PowerShell for the install and quickstart above. The harness reads and
writes config, logs, run records, and provider output as UTF-8. When you use
`scripts/recursion` instead of the console script, start it with
`python -X utf8` so the Windows console uses UTF-8 too.

Task worktrees are created with `git -c core.longpaths=true`. Turn on Windows
long paths if a worktree path still exceeds the legacy path limit. This
repository stores text as LF (`.gitattributes`). Leave `core.autocrlf` off so
a checkout does not rewrite the fixtures the checkers compare byte for byte.
