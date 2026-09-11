# Native WSL construction pipeline

Parent: `goal-recursion-v2-execution-fabric`. This is a construction facility for
researching, testing and developing Recursion. It does not replace Hermes or
change operational autonomy. Lucas reviews and merges branches.

Every SWE-2, Cursor and OpenCode process runs as a native Linux binary inside a
Bubblewrap filesystem and PID namespace in Ubuntu-24.04. Runtime files, source
clones, campaign state and proposed changes live in WSL's ext4 filesystem, whose
VHDX is on D:. Windows only launches WSL and holds the existing provider admission
mutex. Existing credential files are mounted read-only into the trusted client;
they are never copied into research packets, tool workspaces or tracked files.

The qualified arrangement is:

| Layer | Responsibility | Bound |
|---|---|---|
| Astra, current owner session | Scope, task packets, independent review, publication | Existing selected settings |
| Cursor Grok 4.5 High, non-fast | Synthesize worker findings and propose follow-up | Exact `cursor-grok-4.5-high`; 20 workers per packet |
| Explicit OpenCode alternative | Same synthesis contract | Exact `opencode-go/muse-spark-1.3-contributor`, including small_model |
| Native Devin workers | Inspect, research, propose edits and exercise gates | Exact `swe-2-max`; at most 100 reserved provider slots |
| Command tool queue | Execute code in independent offline Linux namespaces | Four machine-wide slots, each 2 GiB, 64 PIDs, two CPU cores |
| Independent verifier and Lucas | Check proposed files, review branches, merge | Model-written PASS has no authority |

The worker tools are `list_files`, `read_file`, literal `search`, `write_file`,
`run_command` and `fetch_source`. They are actual MCP tool calls from SWE-2.
Native filesystem/shell tools, ambient MCP servers and recursive delegation are
disabled in the client. The broker is the only development execution interface.
This distinction matters: enabling arbitrary host shell tools would expose the
inference client's credentials and defeat isolation.

`write_file` persists only exact allowed paths and requires the previous content
digest, preventing stale edits. At most 30 changed files can be proposed. Every
command receives a disposable copy of the current file map. Commands can edit,
compile and test that copy; persistent proposals must go through `write_file`.
No command receives a host writable mount, host home, Windows drive, credential,
controller ledger, Docker socket or network interface with external access.
Each command has a 60-second maximum, a 1 MiB raw output cap, and 64 MiB scratch
mounts. The tool response records actual exit, output and descendant cleanup.
Large escaped output is retained as an artifact with a digest and an explicit
output-limit response; it does not silently become a successful test.

Research uses pinned repository inputs and a reviewed public-source corpus.
`fetch_source` retrieves an exact URL from that frozen corpus, including its
digest and retrieval time. It does not provide unrestricted live web browsing.
The lead supplies or expands the corpus for a new research packet. This keeps
source selection and network authority reviewable.

Native clients share a 24 GiB aggregate cgroup, with 2 GiB per-client ceilings
and a 16-core aggregate CPU limit. Command cgroups are separate. A 100-worker
plan means 100 logical jobs; prior uncertain reservations reduce simultaneous
new admission. It does not mean 100 simultaneous builds. WSL's configured memory
ceiling still applies, independently of free Windows RAM.

Prepare a bounded campaign from committed input files. Each job uses the existing
`id`, `domain`, `kind`, `brief`, `inputs`, `depends_on`, and `allowed_paths` schema.
Keep packets small enough to review; split large architectural questions into
specific falsifiable claims and known-answer gates.

```powershell
python -m tools.construction_swarm.foundry_prepare --repo C:/path/to/review-checkout --jobs D:/RecursionSwarm/jobs.json --output D:/RecursionSwarm/plan.json --run-id research-packet --authorization "Lucas-approved bounded construction packet" --slots 100 --minutes 30
wsl -d Ubuntu-24.04 --cd /opt/recursion-foundry/source -- python3 -m tools.construction_swarm.foundry init --repo /opt/recursion-foundry/repo --plan /mnt/d/RecursionSwarm/plan.json --root /var/lib/recursion-foundry/runs/research-packet
python -m tools.construction_swarm.foundry_wsl --root /var/lib/recursion-foundry/runs/research-packet
```

The native source clone must already contain the plan's exact source commit.
The runtime source directory is a trusted, reviewed copy of this Python package;
freeze it before launch and do not modify it during a campaign. Provisioning is
separate from model work: install official native binaries with checked archive
digests, and verify Bubblewrap plus delegated cgroup memory/PID/CPU controllers.
The runner changes only its own new cgroups, not host controller configuration.

After collection, choose a coordinator explicitly. There is no automatic
provider fallback. These commands produce at most five batches for 100 jobs;
`--batch-index` selects one batch. Each route/batch gets one immutable charged
attempt directory, so repeating the command cannot silently re-spend quota.

```powershell
wsl -d Ubuntu-24.04 --cd /opt/recursion-foundry/source -- python3 -m tools.construction_swarm.foundry_coordinator --root /var/lib/recursion-foundry/runs/research-packet --provider cursor --runtime /opt/recursion-foundry/runtime/cursor-2026.08.25/dist-package --credential /mnt/c/Users/Lucas/AppData/Roaming/Cursor/auth.json
wsl -d Ubuntu-24.04 --cd /opt/recursion-foundry/source -- python3 -m tools.construction_swarm.foundry_coordinator --root /var/lib/recursion-foundry/runs/research-packet --provider opencode --runtime /opt/recursion-foundry/runtime/opencode-1.18.30 --credential /mnt/c/Users/Lucas/.local/share/opencode/auth.json
```

Coordinator output must cover each worker exactly once and preserve its exact
filing reference. Missing, unknown or corrupted evidence cannot advance. All
original dissent and tool-receipt references are retained alongside synthesis,
even if the coordinator paraphrases poorly. `review` is a recommendation for
independent review; it is not acceptance. Neither coordinators nor workers can
publish, merge or create new operational goals.

Place `STOP` in the native run directory to cancel a campaign. The controller
stops admission, cancels clients and tools, and checks cgroup quiescence. On
controller interruption, a shared abort event reaches workers before the thread
pool waits for shutdown. Unknown outcomes retain slots and dispatch charges.
An abandoned tool cgroup blocks its own tool slot; an abandoned aggregate model
cgroup blocks a new model campaign. Do not delete those groups or claims to make
the status appear clean. Inspect retained receipts and exact owned processes.

The Windows pool holds an immutable native reservation before Linux dispatch.
A settlement can reduce it only after the native ledger and cleanup have been
observed. This covers bridge loss and prevents the older Windows packet adapter
from overlapping a native fleet. MSIX may virtualize AppData away from WSL, so
small admission records are shared through `D:/RecursionSwarm/foundry-admission`.
Agent execution and campaign artifacts remain on WSL ext4.

Retain failed and unknown attempt directories and both pool registries. A normal
provider exit with unusable final prose is a failed task when transport and
model identity are positively established. A timeout, lost broker completion,
unverified model or missing cleanup remains unknown. No automatic retry or
expiry refunds it. Follow-up work requires another reviewed packet within the
remaining budget. Publication remains a separate lead action after verification.

Run the dependency-free gates on both systems:

```text
python -m unittest discover -s tools/construction_swarm -t . -p "test*.py"
python -m ruff check tools/construction_swarm
```

Linux tests include actual isolation, cancellation, detached descendant cleanup
and 100 jobs sharing four command slots. Provider qualification and measured
limits are recorded separately in `TOOL-VALIDATION.md`; synthetic and live model
results must not be conflated with a long research campaign.
