# First formal construction packet

Read CONTROL_PLANE.md, applicable CLAUDE/AGENTS instructions and ANCHOR.md first. The Owner
authorized next bounded testing/construction campaigns, setup when needed, read-only delegation,
commits and normal review-branch publication. Production activation, PAUSE or active-assistant
configuration/auth/routing changes, paid usage, resets, merges and force pushes remain outside scope.

## Repository and evidence

- Branch: `codex/v3-formal-comparison-20260907`.
- Frozen start: `a497bae10dddc3adf176242aed878f83b4519316`, published as PR #94 with two full gates
  and two independent exact-candidate approvals. Its worktree remains frozen for validation.
- Parent: `goal-recursion-v2-execution-fabric`; predecessor: `recursion.v3.interface-probes.20260907`.
- Scope commit: `466b080`; first model commit: `443bd6a`; loss-semantics refinement: `a06eb4d`.
- The shared outer envelope started `2026-09-07T22:39:28Z` and ends `2026-09-08T04:39:28Z`.
  This packet began `2026-09-07T23:59:08Z`; preserve the final 90-minute review reserve.

Find the actual candidate in Git; listed hashes are provenance, never reset targets. Final
publication requires two complete gates and two independent reviews of that identical clean
candidate. Receipts live under the Git common directory
`research-attestations/formal-comparison/<candidate>/`. Missing local receipts require validation.
The preceding interface campaign's completion is independently recorded under `interface-probes/`.

`research-attestations/formal-comparison/discovery/index.json` identifies both retained full model
runs. Each has a pre-run admission, exact executed source/configuration snapshot, output log and
result. The later run is accepted for this specification. The earlier run remains scoped to its
earlier handling of a new loss during existing flow recovery. Source snapshots, not a possibly
incomplete working-tree HEAD, identify executed bytes; the second launch helper was new/untracked
at admission and retained explicitly. Semantic model modules were committed.

## Scope and findings

Canonical decisions and limitations live in ARCHITECTURE, TERMINAL-RUNTIME, EXECUTION-FABRIC,
ACCEPTANCE and ROADMAP. This directory owns the [domain declarations](domains.json),
[frozen input manifest](manifest.json), [complete coverage ledger](coverage.json),
[execution bindings](evidence.json) and [model results](results.json).

The result is a conditional preventive flow/control subsystem pass. Separate abstract, split and
inclusive transition implementations share declarations but do not call one common reducer.
They have the same author; independent review and immutable-oracle controls caught four shared
initial mistakes before the first exhaustive run. Graph agreement alone is not correctness.

The accepted small graph has 444,834 reachable states and 2,644,215 transitions per concrete
boundary, empty frontiers, twelve constructive witnesses and twenty-two mutant counterexamples.
Maximum discovered depth is 35; no depth-20 cutoff erased internal cycles. A named weak-fairness
check excludes indefinitely pending local Stop. Hidden-choice and fairness calibrations test the
checking method's limitations. Exact internal graph isomorphism is a stronger construction gate
than visible trace inclusion; its failure alone is not a semantic architecture fault.

The small environment has three one-slot data stages, two total in-flight messages, two total
CREDIT offers, two event identities and unit frame/event costs. This permits a blocked upstream
pump while its downstream stage is full. The full core/cross profiles keep their original
cardinalities and new explicit domain proposals, but are unimplemented and unrun.

Important assumptions: Stop has an independent direct logical path; a dropped SDK token produces
an immediate trustworthy loss signal; external outcome starts unknown and stays unknown.
The model establishes none of their physical implementations. Rejected message candidates do not
advance the admitted cursor; M1B's posthoc audit retains rejected EVENT facts differently.
The retained RESET counterexample shows why omitting a prevented EVENT does not by itself create
a valid recovery cause on the wire. Full admission/emission/audit mapping is unimplemented.

## Reproduce and continue

1. `python -X utf8 -B experiments/v3/formal-comparison/check.py --working` checks retained evidence,
   scope, claims, coverage and positive/adversarial bindings. It is not final acceptance.
2. The exact clean candidate uses the same command with `--candidate FULL_HASH`. Final mode
   reruns model exploration/calibrations, all 25 unchanged regressions on that candidate, and
   historical checks on the two named frozen worktrees. It writes receipts externally.
3. A new exploratory model run uses `run_packet.py` under a fresh bounded campaign/packet with
   sufficient remaining reserve. Old deadlines are not reusable launch authorization.
4. The next construction request is the preventive/emitted/audit RESET mapping. Specify a
   supported resynchronization sequence and preserve rejection, snapshot and cursor evidence;
   validate it against unchanged M1B rules before claiming a real adapter.
5. Extend both models with typed epochs and recipient installation, process birth/registration,
   receiver records, shared writer/pool conservation, GoalSpec/consultation and literal M1A/M1C
   joins. Run all required corpus witnesses and the full standalone profiles. Traces 01/02/26
   currently have partial coverage only; 22 remains not-selected/unrun; other rows remain
   unimplemented. All six obligations remain required. Formal freeze stays false.
6. Physical control reserve, ingress loss detection, fresh-connection/fresh-process recovery,
   configuration/plugin and remote probes proceed alongside formal construction. Language then
   full storage comparison follow the complete formal gate, with every accepted capability retained.

No new consequential Owner decision is established. First new GRILLME decision: none.
