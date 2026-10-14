# Recursion user guide

This guide is for the `recursion` command in this checkout. The product map is
[docs/v3/START-HERE.md](v3/START-HERE.md). How one run moves from plan to
report is [ARCHITECTURE.md](ARCHITECTURE.md). The slice notes are
[docs/v3/HARNESS-SLICE.md](v3/HARNESS-SLICE.md). The shipped config is
[config/harness.json](../config/harness.json). The schema checked at startup
is [config/harness.schema.json](../config/harness.schema.json).

`recursion` plans a task through the M1A kernel, admits frozen route fixture
`F-M1B-001`, and then runs a provider. The selected route id on that fixture
is `route-a`. Planning also records the separate ids `ROUTE-INCLUDED` and
`ROUTE-ZERO`. Those are not provider names, and a capability match does not
rename them.

## Install

Python 3.11 or 3.12 and Git. From the repository root, one script creates a
virtualenv, installs this checkout, and runs `recursion doctor`.

Linux:

```bash
bash scripts/install.sh
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/install.ps1
```

The script prints the next commands. It installs with `python -m pip install -e .`
inside `.venv`. That editable install registers the `recursion` console script
from `pyproject.toml` and pulls `jsonschema` 4.23.0, which config validation
needs. Commands that plan or run read `config/harness.json` and the
M1 fixtures from this checkout, so install from the repository, not from a
bare wheel.

The same install without the script:

Linux:

```bash
python -m pip install -e .
```

Windows PowerShell:

```powershell
python -m pip install -e .
```

Without installing, from the repository root:

Linux:

```bash
python -X utf8 -B scripts/recursion --help
```

Windows PowerShell:

```powershell
python -X utf8 -B scripts/recursion --help
```

`requirements.txt` pins the test tools, including pytest and the same
`jsonschema` 4.23.0. Install it before `pytest`:

```bash
python -m pip install -r requirements.txt
```

## Quickstart

The shipped config enables `fixture` and `fixture-b`. Both return a
deterministic transcript and start no process. Neither needs an account or
`--allow-live`. Their weights are equal, and `fixture` is first in
`routing.preference`, so a run that does not pin one provider uses `fixture`
as the worker and `fixture-b` as the reviewer. A later task in the same run
starts at the next candidate, so `fixture-b` can be the worker and `fixture`
the reviewer.

Linux:

```bash
recursion run --task "Say hello"
```

Windows PowerShell:

```powershell
recursion run --task "Say hello"
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

`fixture-b` answers the review with `VERDICT approve`, unless the task
contains the line `fixture: revise once` (one revise, then approve). The
fixture also writes `.recursion-fixture/hello.txt` in the task worktree, so
the run branch has a commit to merge. The task status is
`completed` and the command exits `0`. `review.accept_unreviewed` stays
false. `recursion land <run-id>` can merge that finished run, and
`recursion clean` can prune it later, without flipping `accept_unreviewed`.

`recursion run --task "Say hello" --provider fixture` pins one provider.
Review is `skipped` (`no distinct reviewer`), the task is `unreviewed`, and
the command exits `2`. The same happens when the config leaves only one
fixture enabled. The JSON result is still printed. Set `accept_unreviewed`
to true when a missing reviewer should leave the worker result accepted.
Exit code `0` means the run completed. Exit code `2` means the command
refused the request or the run ended `budget-exceeded`, `cancelled`,
`conflict`, `failed`, `review-rejected`, `skipped`, or `unreviewed`.

### Through land and clean

The [README](../README.md) quickstart continues through `doctor`, `init`,
`plan`, `status`, `logs`, `land`, and `clean`. Write the starter config
outside this checkout. A file created inside it makes `git status` dirty,
and `land` then refuses with `working tree is dirty`. `init` enables
`fixture` and `fixture-b` and leaves `review.accept_unreviewed` false.
The run does not pin one provider, so `fixture-b` reviews, the task is
`completed`, and the command exits `0`. `land` needs a current branch. A
detached HEAD needs `--into`, or check out a branch first. A fixture task
that edits no files leaves the run branch at the same commit as the target.
`land` still records `land.status` `merged` and the current HEAD, and git
does not add a commit. `clean --older-than 0` then removes that finished
run. An `unreviewed` run is skipped as `resumable`.

## Commands and flags

`recursion --help` lists these subcommands and no others:

```text
usage: recursion [-h]
                 {plan,run,status,resume,cancel,providers,doctor,init,config,logs,land,clean}
                 ...
```

`-h` and `--help` show that text and exit. `plan`, `run`, `status`,
`resume`, `cancel`, `providers`, `land`, and `clean` also accept `--config`
and `--state-dir`.
`doctor` accepts `--config` and `--live`, and does not accept `--state-dir`. `init` accepts
a path and `--force`, and does not accept `--config` or `--state-dir`.
`config validate` accepts `--config`. `logs` accepts `--state-dir` and does
not read the config.

| Flag | Help text | Where |
|---|---|---|
| `-h`, `--help` | show this help message and exit | every command |
| `--config CONFIG` | provider config JSON (default: config/harness.json) | `plan`, `run`, `status`, `resume`, `cancel`, `providers`, `doctor`, `config validate`, `land`, `clean` |
| `--state-dir STATE_DIR` | directory for resumable run records | `plan`, `run`, `status`, `resume`, `cancel`, `providers`, `logs`, `land`, `clean` |

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

`cli_found` is true for `fixture` and `fixture-b` without looking them up.
For every other provider it is true when `doctor`'s PATH search finds the
command, including Windows `.exe`, `.cmd`, `.bat`, and `.ps1` shims. The
command does not start the CLI and does not probe sign-in. Active cooldowns come from
`<state-dir>/cooldowns.json`.

### doctor

```text
usage: recursion doctor [-h] [--config CONFIG] [--live]
```

Help: check git and each configured provider executable.

| Flag | Help text |
|---|---|
| `--config CONFIG` | provider config JSON (default: config/harness.json) |
| `--live` | send one tiny prompt to each enabled, signed-in provider |

Stdout is one JSON object with `git`, `ok`, and `providers`. `ok` is true
when at least one enabled provider is usable. The process exits `0` when
`ok` is true and `1` when it is false. A bad config still exits `2`.

`--live` is off unless you pass it. It sends one prompt, `Reply with the
single word pong. Do not use tools and do not change any files.`, to each
enabled provider that is installed and signed in. Each prompt runs in a
throwaway git repository. The report then also has `live` and `live_ok`.
`live` is one row per provider, with `status` (`skipped` or `ran`),
`reason`, `ok`, `text`, and `error`. `text` is the parsed assistant reply,
truncated. `live_ok` is true when every attempted prompt passed, and also
when none were attempted. The process exits `1` when `ok` is false or
`live_ok` is false. `doctor --live` refuses, before any prompt, when `CI`
or `GITHUB_ACTIONS` is set. Tests and CI do not pass `--live`.

`git.available` is whether `git --version` succeeds. `git.version` is the
first line of that output. On Windows, `git.longpaths` is true when
`git config --get core.longpaths` prints `true`, `1`, or `yes`, and false
when it is unset or another value. On other systems `git.longpaths` is
null. A missing git does not by itself make `ok` false.

Each provider row has `name`, `command`, `enabled`, `installed`, `resolved`,
`version`, `signed_in`, `auth_method`, and `usable`. `fixture` and
`fixture-b` are installed without a PATH lookup. Each is usable when it is
enabled, and `signed_in` is `not-applicable`. Another provider is installed
when its command resolves on `PATH`. On Windows the search also tries
`PATHEXT` and always tries `.exe`, `.cmd`, `.bat`, and `.ps1`, ignoring case. A `.cmd` or `.bat` shim is
started through `cmd.exe /d /c`. A generated provider stub is started with
Python directly. A `.ps1` shim is started with `powershell.exe -NoProfile
-NonInteractive -ExecutionPolicy Bypass -File`, or with `pwsh` when that
is the PowerShell found on `PATH`. A `.exe` is started directly. A provider
is usable when it is enabled and installed. `version` is the first line of
`<command> --version` when that exits 0.

Sign-in checks are local and do not start a billed prompt. The report never
includes the variable's value, a credential file's contents, or the probe's
stdout.

| Provider | Check |
|---|---|
| `claude` | `claude auth status`. Exit 0 is signed in. The reported method is `authMethod` when it is one of `none`, `claude.ai`, `oauth_token`, `api_key`, `api_key_helper`, or `third_party`. |
| `codex` | `codex login status`. Exit 0 is signed in. |
| `grok` | `XAI_API_KEY` is set, or `~/.grok/auth.json` exists and is non-empty. The file is not read. |
| `gemini` | `GEMINI_API_KEY`, `GOOGLE_API_KEY`, or `GOOGLE_APPLICATION_CREDENTIALS` is set, or `~/.gemini/oauth_creds.json` exists and is non-empty. The file is not read. `GOOGLE_GENAI_USE_VERTEXAI` and `GOOGLE_GENAI_USE_GCA` alone are not treated as signed in. |
| `cursor` | `CURSOR_API_KEY` is set, otherwise `cursor-agent status --format json`. A boolean `isAuthenticated` is read before the `status` word. `unauthenticated` is signed out. The command exits 0 when signed out. |
| `opencode` | `~/.local/share/opencode/auth.json` exists and is non-empty (the file is not read), otherwise `opencode auth list`. An empty JSON list, the text `0 credentials`, or `No authenticated integrations`, is signed out. ANSI color codes are ignored. |

A disabled provider can be installed and still not usable. The shipped config
leaves `gemini`, `cursor`, and `opencode` disabled. `fixture` and `fixture-b`
are enabled, so `ok` is true with no CLI installed. A machine with only
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

`init` writes a version-1 file. It enables `fixture`, `fixture-b`, and every
other registered provider whose command resolves on PATH. Sign-in is not required.
The other providers are present and disabled. Budgets, review rounds,
`review.accept_unreviewed`, `landing.base_ref`, `landing.conflict_retries`,
concurrency, retries, `cooldown_seconds`, `weights`, and the capability
preference match the shipped defaults, with preference and weights listing
every registered provider once.

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

### land

```text
usage: recursion land [-h] [--config CONFIG] [--state-dir STATE_DIR]
                      [--into INTO]
                      run_id
```

Help: merge a finished run branch into a target branch.

| Flag | Help text |
|---|---|
| `run_id` | saved run id |
| `--into INTO` | branch that receives the run (default: the current branch) |

`land` merges `recursion/run/<run-id>` into the current branch, or into
`--into`, with `git merge --no-ff`. The run must be `completed` and the run
branch must exist. A dirty worktree is refused before any merge. A conflict
aborts the merge and leaves the target branch where it was. `land` also
refuses when the target branch is checked out in a worktree other than the
one it is running in, so that checkout is not left stale. The message starts
with `target branch is checked out in another worktree`. These refusals are
stored on the run as `land.status` `refused` or `conflict`, and the report
is rewritten. A merge stores `land.status` `merged` and the commit that
is checked out afterward. When the run branch is already contained in the
target, git reports that the branch is already up to date, no commit is
added, and the recorded commit is the current HEAD. A fixture task that
edits no files does that. The merge commit uses this repository's `user.name` and `user.email` when
they are configured. A missing name falls back to `recursion`, and a missing
email falls back to `recursion@localhost`. Exit code `0` means the merge
landed. Exit code `2` means it did not.

### clean

```text
usage: recursion clean [-h] [--config CONFIG] [--state-dir STATE_DIR]
                       [--older-than OLDER_THAN] [--dry-run]
                       [--include-unlanded]
```

Help: prune old run state, worktrees, and task branches.

| Flag | Help text |
|---|---|
| `--older-than OLDER_THAN` | prune runs older than this many days |
| `--dry-run` | list what would be removed or skipped |
| `--include-unlanded` | also remove unlanded run branches and worktrees with uncommitted changes |

The default is 7 days. `0` selects every run created before now. A selected
run loses its record, report, JSONL log, task branches
`recursion/task/<run-id>/`, run branch `recursion/run/<run-id>`, and any
worktree checked out on those branches. The main worktree is not removed.
These runs and checkouts are listed under `skipped` and are not deleted:

| Reason | What stays |
|---|---|
| `running` | The run status is `running`, or a task is still `running`. |
| `pending` | The run status is `pending`, or a task is still `pending`. |
| `resumable` | `resume` can continue the run (`failed`, `cancelled`, `unreviewed`, and the other unfinished statuses). |
| `checked out` | One of the run's branches is checked out in the main worktree. The run record stays. |
| `unlanded` | The run branch has no `land.status` of `merged`, and that branch is not already contained in the current branch or the default branch. Task branches, clean worktrees, and the state files are still removed. |
| `dirty worktree` | The worktree has uncommitted changes. The branch checked out there stays too. |

`--include-unlanded` removes an `unlanded` run branch and a `dirty worktree`.
It does not remove a `running`, `pending`, or `resumable` run, and it does
not remove a branch `checked out` in the main worktree. `--dry-run` prints
the same `removed` and `skipped` lists and deletes nothing. Stdout is JSON
with `dry_run`, `include_unlanded`, `older_than_days`, `removed`, and
`skipped`.

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
| `conflict_retries` | `1` | Integer `>= 0`. After a task branch conflicts while merging into the run branch, how many times the harness may ask a provider to reconcile that task on a fresh worktree cut from the run branch. `0` records the conflict and skips dependents. |

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
| `preference` | `["fixture", "fixture-b", "claude", "codex", "grok", "gemini", "cursor", "opencode"]` | Tie-break when weights are equal. Each configured provider once. |
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
| `fixture-b` | `true` | `execute`, `deterministic` | `fixture-b-provider --output-format json` | `120` |
| `claude` | `true` | `execute`, `stream-json`, `subscription` | `claude -p --output-format stream-json --verbose --dangerously-skip-permissions` | `120` |
| `codex` | `true` | `execute`, `jsonl`, `subscription` | `codex exec --json --approve-for-me` | `120` |
| `grok` | `true` | `execute`, `streaming-json`, `subscription` | `grok --output-format streaming-json --always-approve --no-auto-update` | `120` |
| `gemini` | `false` | `execute`, `stream-json`, `subscription` | `gemini -p --output-format stream-json --approval-mode yolo --skip-trust` | `120` |
| `cursor` | `false` | `execute`, `stream-json`, `subscription` | `cursor-agent -p --output-format stream-json --force --trust` | `120` |
| `opencode` | `false` | `execute`, `json` | `opencode run --format json --auto` | `120` |

`enabled` is a boolean. A disabled provider is skipped. Naming it with
`--provider` is an error. `timeout_seconds` is an integer `>= 1`. A live
process that exceeds it fails as a timeout. The `fixture` and `fixture-b`
adapters never start a process, including when their argv names
`fixture-provider` or `fixture-b-provider`.

## Providers

Live CLIs start only with `--allow-live`. Tests and CI omit that flag. The
executable must be on `PATH` and already signed in with that product's own
login. Recursion does not run a login command, does not pass a key, and does
not store one.

### Fixture

No install and no sign-in. `fixture` and `fixture-b` are both enabled in
[config/harness.json](../config/harness.json). An execute transcript names the
provider, the route, the packet, and the task. An execute also writes
`.recursion-fixture/hello.txt` in the task worktree (`hello` and the
provider name), so the task commit advances the run branch. A review
transcript is `VERDICT approve` followed by `fixture review` or
`fixture-b review`, unless the task contains the line `fixture: revise once`.
That line asks for one `VERDICT revise`, and the next review approves. A plan
whose goal starts with a line `graph` is a dependency list. Each following
line is `id: description`, then optional ` requires cap,cap`, then optional
` depends id,id`. Any other goal is still one independent task per
non-empty line. An invalid graph falls back to that line split. `fixture-b`
uses the same plan and execute behavior with its own provider name. It exists
so review can pick a provider other than the worker without a live CLI.

`examples/harness.json` is a live-CLI sample. It lists both fixtures and
leaves them disabled. The shipped config is the one that reviews offline.

### Claude Code

Install Claude Code so `claude` is on `PATH`, and sign in with Claude Code
itself. With `--allow-live`, the harness runs
`claude -p --output-format stream-json --verbose --dangerously-skip-permissions`
and writes the task to the process stdin. `stream-json` requires `--verbose`.
`--dangerously-skip-permissions` lets a headless tool call proceed. There is
no working-directory flag; the process cwd is the task directory. The model
flag is left unset, so the signed-in CLI default is used. Assistant text is
the `result` string. An `is_api_error_message` assistant event is not that
text. Usage comes from the result event.

Verified against Claude Code 2.1.299 on 2026-10-14, from `claude --help` and
a signed-out `stream-json` run. That run exits 1 with an empty stderr. The
stdout result has `is_error` true, `terminal_reason` `api_error`, and the
text `Not logged in · Please run /login`. A signed-in completion was not
run here. A live rate-limit body was not produced; the `rate_limit` category
is the name in the Claude docs.

### Codex

Install the Codex CLI so `codex` is on `PATH`, and sign in with that CLI.
With `--allow-live`, the harness runs `codex exec --json --approve-for-me`.
The task is written to stdin and the prompt argument is `-`. When the task
has a directory, `--cd` is that directory. `exec` accepts `--approve-for-me`
for unattended workspace writes. The model flag is left unset. Assistant
text is each completed `agent_message`. Usage comes from `turn.completed`.

Verified against Codex CLI 0.162.1 on 2026-10-14, from `codex exec --help`
and a signed-out run inside a fresh git repository. That run reached
`401 Unauthorized` on stdout and stderr. A directory that is not a git repo
stops with `Not inside a trusted directory` unless the CLI is given
`--skip-git-repo-check`; the harness leaves that flag off because task
worktrees are git repos. A signed-in completion was not run here.

### Grok Build

Install Grok Build so `grok` is on `PATH`, and sign in with that CLI. With
`--allow-live`, the harness runs
`grok --output-format streaming-json --always-approve --no-auto-update --prompt-file <file>`.
The task is the prompt file. Headless Grok reads that file, and it reads
`--cwd` when the task has a directory. `--always-approve` lets tool calls
proceed. The model flag is left unset. Assistant text is the `text` events'
`data`. Thoughts and tool output are not that text. Usage is the last
`usage` object in the stream.

Verified against Grok 1.0.52 (`0920c8169e27`) on 2026-10-14, from `grok --help`
and the headless guide shipped with that install. A signed-out run exits 1
with stderr `Not signed in` and a stdout `{"type":"error","message":...}`.
`--prompt-file`, `--cwd`, `--always-approve`, and `--no-auto-update` were
accepted at the flag layer. A signed-in completion was not run here. The
streaming event sample in the tests is the shape from that shipped guide.

### Gemini CLI

Disabled in the shipped config. Install Gemini CLI so `gemini` is on `PATH`,
set `enabled` to true, and sign in with Gemini CLI itself. With
`--allow-live`, the harness runs
`gemini -p <task> --output-format stream-json --approval-mode yolo --skip-trust`.
`--approval-mode yolo` approves tool calls. `--skip-trust` accepts the
workspace for the session. A task longer than 7000 characters is written to
stdin, and the `-p` value is a single space so the flag still has a value.
There is no working-directory flag; the process cwd is the task directory.
The model flag is left unset. `stream-json` events are newline-delimited
JSON. The assistant text is the `message` events whose role is `assistant`.
Token figures come from `result.stats` (`input_tokens`, `output_tokens`).
That object has no dollar cost, so cost stays unknown.

Verified against Gemini CLI 0.64.0 on 2026-10-14, from `gemini --help` and a
signed-out run. That run exits 41 and asks to set an auth method. The same
exit happened for a prompt on stdin and for `-p` pointing at a file, so
those paths were accepted at the flag layer. Whether a signed-in run
concatenates stdin with `-p` was not observed. A signed-in completion was
not run here.

### Cursor CLI

Disabled in the shipped config. The install links `agent` and `cursor-agent`
to the same binary. This harness calls `cursor-agent`. Set `enabled` to true
and sign in with Cursor. With `--allow-live`, the harness runs
`cursor-agent -p --output-format stream-json --force --trust`. `--force`
approves tool calls. `--trust` accepts the workspace. `--workspace` is the
task directory when one is set. A short task is the positional prompt after
`--`. A task longer than 7000 characters is written to stdin and the
positional prompt is omitted. The model flag is left unset. The assistant
text is the terminal `result` string. When that event includes
`usage.inputTokens` and `usage.outputTokens`, those figures are kept. The
documented result object has no dollar cost, so cost stays unknown.

Verified against Cursor Agent `2026.10.14-0f9edde` on 2026-10-14, from
`cursor-agent --help` and `status --help`. A signed-out print run exits 1
with stderr `Authentication required`. `status --format json` exits 0 and
reports `isAuthenticated` false. A signed-in completion was not run here,
so a signed-in stdin prompt was not observed.

### OpenCode

Disabled in the shipped config. Install OpenCode so `opencode` is on `PATH`
and set `enabled` to true. With `--allow-live`, the harness runs
`opencode run --format json --auto`. `--auto` approves permissions that are
not explicitly denied. `--dir` is the task directory when one is set. The
short task is the positional message. `-p` on this command is a password
flag and is not used. This CLI has no stdin prompt. A task longer than 7000
characters is written to a file in the task directory and passed with
`--file`, plus a short message that points at that file. The model flag is
left unset. Assistant text is the `text` events. Each `step_finish` event
contributes `part.tokens.input`, `part.tokens.output`, and `part.cost`, and
those steps are added. A stream with no `step_finish` leaves usage unknown.
A reported cost of zero stays zero.

Verified against OpenCode 1.19.0 on 2026-10-14, from `opencode run --help`
and `opencode auth list`. The auth command takes no `--format` or
`--standalone` flag in this version. Signed out, it prints `0 credentials`
and exits 0. One headless run of `opencode run --format json --auto` with
the prompt `Reply with the single word pong.` completed and returned
`pong`, with `step_finish` cost 0. A second run that attaches `--file` was
not made. A live rate-limit body was not produced.

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
ids, and cycles. The same prompt includes a size-capped repository map:
tracked file paths, plus the opening text of `README.md`,
`docs/USER-GUIDE.md`, and `docs/v3/START-HERE.md` when they exist. Invalid
output, or no planning provider, falls back to one task per non-empty line
and logs `plan.fallback` with a fixed reason. The raw planner body is not
stored. Each description is still its own M1A admission. A task's
`required_capabilities` further filters its candidates. Task `i` starts at
the `i`-th remaining candidate, then continues in order. A task starts only
after every dependency is `completed` and landed, and its worktree is cut
from the run branch so it sees that work. The worker prompt also includes a
size-capped summary, commit, and diff for each dependency. Token-shaped
text in that context is redacted. A failed, rejected, conflicted, or
unreviewed dependency marks dependents `skipped` with
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
review body is not stored. The shipped config keeps `fixture` and `fixture-b`
enabled, so an offline run has a distinct reviewer and does not need
`accept_unreviewed`. If no other provider exists, the verdict is `skipped`
(`no distinct reviewer`). If every reviewer fails, the verdict is `skipped`
(`no reviewer completed`) and the failed attempts are stored on that review.
Reviewer writes made before the failure are removed too. A config that
leaves only one fixture enabled still ends `unreviewed` when no other
reviewer finishes.
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
into the run branch. A merge conflict aborts that merge and records the
paths. When `landing.conflict_retries` is greater than `0`, the harness
checks out a new worktree from the run branch, gives the provider the
original task, the conflicting paths, and a short note of what already
landed, then runs the normal review step and tries the merge again. Each
attempt is stored on the task, in the JSONL log, in the progress line, and
in the report. `resume` continues a recovery that was interrupted. `cancel`
stops the recovery provider the same way it stops any other provider call.
If recovery fails or the retries are used up, the task stays `conflict`,
dependents are skipped, and the conflicted task branch is kept. The checkout
you started from is not changed. Unreviewed branches are
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
| `older-than must be an integer >= 0` | `--older-than` was negative or not an integer. Exit code 2. |
| `run is not finished` | `land` was asked to merge a run whose status is not `completed`. |
| `run branch is missing` | The finished run has no `recursion/run/<run-id>` branch. |
| `working tree is dirty` | `land` refused because `git status --porcelain` was not empty. The report records `land.status` `refused`. |
| `merge conflict` | `land` aborted the merge. The target branch is unchanged. The report records `land.status` `conflict` and the paths. |
| `unknown branch` | `--into` names a branch that is not in this repository. |
| `invalid branch name` | `--into` is not a branch name. |
| `pass --into when HEAD is detached` | `land` has no current branch to receive the run. |
| `target branch is checked out in another worktree` | `land` refused because that branch is checked out in a different worktree. The target branch is unchanged. The report records `land.status` `refused`. |
| `missing provider config` | `--config` or `config/harness.json` is not a file. |
| `provider config is not JSON` | The file does not parse. |
| `config keys mismatch` | A required key is missing or an unknown key is present. |
| `routing.retries:` (and other field paths) | The JSON Schema rejected that field. The text after the path says what is wrong. |
| `config key '...' is not allowed` | The key looks like a secret. |
| `provider config version must be 1` | `version` is not the integer `1`. |
| `unknown provider` | The name is not `fixture`, `fixture-b`, `claude`, `codex`, `grok`, `gemini`, `cursor`, or `opencode`. |
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

### Linux

Install from this checkout with `python -m pip install -e .`, then
`python -m pip install -r requirements.txt`, so `jsonschema` is present and
`config/harness.json` resolves. Invoke `scripts/recursion` as
`python -X utf8 -B scripts/recursion` when the console script is not on
`PATH`.

`claude`, `codex`, `grok`, `gemini`, and `opencode` must be executable files
on `PATH`. Cursor's command is `cursor-agent`. `recursion doctor` and
`recursion providers` report whether that command resolves. They do not start
a billed prompt. A live run still needs `--allow-live` and that product's
own login. A missing command is `CLI was not found on PATH`.

Git is required for task worktrees. `git <subcommand> failed` means the
worktree could not be added or removed. `git worktree prune` drops a
checkout left behind by an interrupted run. A cancel or a provider timeout
stops the running process and its process group. Text files in this repository
are LF (`.gitattributes`). Leave `core.autocrlf` false so a checkout does
not rewrite fixtures the checkers compare byte for byte.

If the locale is not UTF-8, set `PYTHONIOENCODING=utf-8`. Config, JSONL,
run records, and provider output are read and written as UTF-8.

### Windows

Use PowerShell for the install and quickstart above. The harness reads and
writes config, logs, run records, and provider output as UTF-8. When you use
`scripts/recursion` instead of the console script, start it with
`python -X utf8` so the Windows console uses UTF-8 too.

`doctor` and `providers` resolve a command with `PATHEXT` and also try
`.exe`, `.cmd`, and `.bat`, ignoring case. `cursor-agent` is the Cursor
command this harness calls. A `.cmd` shim that is only a name on `PATH` is
still reported as installed when that search finds it.

Task worktrees are created with `git -c core.longpaths=true`. Turn on
Windows long paths if a worktree path still exceeds the legacy path limit.
A cancel or a provider timeout stops the running process and the job object
that contains it.
`doctor` reports `git.longpaths` from `git config --get core.longpaths`.
This repository stores text as LF (`.gitattributes`). Leave `core.autocrlf`
off so a checkout does not rewrite the fixtures the checkers compare byte
for byte.
