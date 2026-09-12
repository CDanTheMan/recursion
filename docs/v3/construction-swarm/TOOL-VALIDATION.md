# Native tool pipeline qualification — 2026-09-11

Parent: `goal-recursion-v2-execution-fabric`. Scope and gates are in
`TOOL-CHARTER.md`; operating commands are in `TOOL-PIPELINE.md`.

## Storage and execution

Windows registered `Ubuntu-24.04` as WSL2 with `BasePath=D:\WSL` and
`VhdFileName=ext4.vhdx`. Both `/opt/recursion-foundry/repo` and
`/var/lib/recursion-foundry/runs` resolve to `/dev/sdd`, ext4 mounted at `/`.
Native clients, coordinators, tool processes, workspaces and campaign artifacts
therefore execute on the added D: SSD. The review checkout remains on Windows.
Small cross-platform admission records use `D:\RecursionSwarm\foundry-admission`.

Qualification used native Devin 3000.10.21, exact `swe-2-max`. The executable
SHA-256 is `ba1956450c0e0bf95f477ccd442a0b45b14765402b2377d6737ae758126d70cd`.
Official native model listing identified SWE-2 Max as Free. This is an observed
route listing, not a contractual promise of permanent unlimited capacity.

## Live tool capacity

These were real provider calls with exported model identity, MCP tool calls,
durable broker requests/receipts, actual Python command gates and cgroup cleanup.
The contract probes exercise six known-answer groups; repetition measures the
pipeline rather than adding independent research coverage.

| Native campaign | Returned qualification jobs | Successful command gates | Peak live clients | Peak command scopes | Client latency min / median / max |
|---|---:|---:|---:|---:|---|
| `native-capacity-8` | 8 / 8 | 8 | 8 | 2 | 20.61 / 29.09 / 35.38 s |
| `native-capacity-30` | 30 / 30 | 30 | 30 | 2 | 20.52 / 27.67 / 77.53 s |
| `native-capacity-100` | 100 / 100 | 100 | 77 | 4 | 14.60 / 30.99 / 60.38 s |

The eight-case campaign also contained a separate review job whose malformed
filing remains unknown; it is excluded from the qualification-job counts above.
Four inherited unknown reservations limited the 100-job campaign to at most 96
new admitted clients. Staggered client startup and completion produced a measured
77-client peak, confirmed independently by elapsed receipts and 0.5-second
cgroup samples. This is **100 completed jobs, not 100 simultaneous clients**.

For the 100-job campaign, aggregate client memory peaked at 3,464,937,472 bytes
(3.23 GiB), with 1,941 sampled PIDs/threads and zero cgroup OOM/max events.
Largest individual client peak was 53,043,200 bytes; largest command scope peak
was 14,036,992 bytes. These small, short packets do not predict memory use for
large repositories, compilation or long model conversations.

The final campaign contained 98 contract probes and one developer→verifier pair.
The developer wrote a new allowed Python module through `write_file`, then ran
its two known-answer assertions. A separate dependent worker read the proposed
bytes from its own workspace and executed the same module successfully. Both
observed `HANDOFF_GATE_PASS`; the proposal stayed external to the repository.
This verifies the handoff mechanism, not useful product functionality.

Provider exports reported 5,397,486 prompt tokens, 4,406,603 cached tokens and
131,399 completion tokens across those 100 workers. These are provider counters,
not measured billing or proof of incremental subscription charges. No Codex
reset was consumed and the owner's current model/settings were unchanged.

## Useful work and adversarial review

An actual native SWE-2 worker contributed `test_foundry_swe.py` through a broker
write: 11 tests covering tool scope, output limits, stale writes, Unicode and
isolation. The lead reviewed the source and corrected two portable mocks and
lint before integration. The original contribution attempt remains unknown
because its final response did not satisfy the then-current collector; its
independently retained source was still reviewable. It was not silently accepted.

SWE-2's focused adversarial review identified an execution-exception path that
could lose failed-cleanup evidence. The fix retains both errors, latches broker
uncertainty and blocks later tool calls; an injected-failure regression verifies
that behavior. The review also prompted explicit argument-object validation.
Its runtime-tree integrity concern requires host write access: installation must
verify official archives and keep the trusted runtime frozen. A pinned binary
alone does not attest every runtime dependency against a hostile host writer.

A separate lead-model review found malformed final output could be classified
as completed failure before per-step model/tool qualification. Collection now
checks transport, exact model and tool/receipt correspondence first. Regression
cases preserve unknown status for changed models, unreceipted/native tools and
uncertain cleanup. Reporting also rechecks bound packet, transport, export and
tool-request bytes before presenting a filing to coordinators.

## Coordinators and final gates

Native credential/identity probes each made one call with tools denied:

- Cursor `cursor-grok-4.5-high`, observed `Cursor Grok 4.5 High`: 15.46 s,
  490,303,488-byte peak; correct missing-evidence disposition and clean exit.
- OpenCode Go `opencode-go/muse-spark-1.3-contributor`: 8.42 s,
  926,261,248-byte peak; exact exported provider/model, correct disposition,
  no tool calls and clean exit. There was no fallback between these providers.

On the actual 100-job output, Grok completed five batches of 20, each with exact
filing-reference coverage. All 100 dispositions were `review`, never acceptance.
Batch durations were 37.71–43.07 seconds; the largest coordinator memory peak
was 935,436,288 bytes. Combined Cursor counters were 62,344 input and 12,559
output tokens. Original worker dissent, limitations and tool references remain
beside each synthesis.

The explicitly tested OpenCode alternative then covered the actual eight-case
campaign plus its uncertain review: eight `review`, one `blocked`, in 20.95
seconds with a 924,893,184-byte peak. It preserved the missing-evidence barrier.
This was an alternative-route qualification call, not a fallback after failure.

Those six historical receipts contain `local_quiescent=false` from the underlying
POSIX process transport, alongside `scope.quiescent=true` from the authoritative
cgroup cleanup. Acceptance used the latter. A final receipt consistency fix
normalizes the top-level field after cgroup cleanup and requires both an exited
direct process and an empty scope. Historical receipts remain unchanged; focused
regression covers clean completion, failed cleanup and a non-exited process.

The complete regression command is
`python -m unittest discover -s tools/construction_swarm -t . -p "test*.py"`.
Final implementation `c4f1796` passed all 61 discovered tests: Windows had 54
passes and seven platform skips (7.63 seconds); WSL had 60 passes and one
Windows-only skip (12.45 seconds). `python -m ruff check tools/construction_swarm`
passed. The first Linux invocation
discovered only 28 tests because its copy omitted the legacy tests directory;
that incomplete run was retained and superseded by the complete 60-test run.
Final gate logs and hashes are retained in `tool-qualification-evidence.json`.

## Retained evidence and limits

Canonical campaign roots are under `/var/lib/recursion-foundry/runs/` using the
names above. Each contains the frozen plan/inputs, ledger, per-attempt packet,
export, transport, filing and tool receipts. `qualification-audit.json` records
independently checked gates and receipt hashes. The 100-job root also retains
`resource-samples.jsonl` and `collector-requalification.json`.

The 30/100-job provider executions used source `8b0e43c`; the eight-case run used
`0436b29`. Collector/evidence fixes are in `9c026a7`, followed by the coordinator
receipt correction in `c4f1796`. All 100 retained final
exports were requalified through that updated collector without new inference;
each filing digest matched. Host helper scripts and earlier evidence are under
`D:\RecursionSwarm\tool-foundry-20260911`; native coordinator probes are under
`/var/lib/recursion-foundry/coordinator-probes`.

Four reservations remain held: one earlier Windows timeout, two native review
attempts with unusable final/protocol evidence, and one focused review with a
string where the schema required a dissent array. None was retried or refunded.
The unrelated prelaunch MSIX path failure had zero provider attempts and was
settled only after verifying that fact. No native reconciliation command yet
automates investigation or release of unknown holds.

This qualifies bounded research/development packets on this machine. Research
retrieval is a frozen reviewed corpus; commands are offline, have four slots,
60-second ceilings and 64 MiB scratch mounts. Long builds, arbitrary live browsing,
200–300 concurrent clients, sustained overnight research quality and automatic
follow-up task generation remain unqualified. The lead must provide new scoped
packets and independent acceptance gates; coordinators advise and Lucas merges.

## Continuation — 2026-09-12

PR 125 (`d6d8f19`) records owner-authorized settlement of quiescent unknowns as
completed failures. That supersedes the “four reservations remain held” close
of the 2026-09-11 qualification write-up above; dispatch charges from those
holds were not refunded.

The next native Devin campaign used the same probe + collector methods. Census
and limits: [`NIGHT-RDT-20260912.md`](NIGHT-RDT-20260912.md). Wave18 re-hit
Cognition `overall message rate limit` (13/30 stderr hits). Overnight Devin
admits stop; next width after the org window is 8.

