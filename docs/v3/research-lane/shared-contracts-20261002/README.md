# Recursion shared contracts and extensibility research

Research handoff for Lucas and the local Recursion sessions, 2026-10-02.

This packet contains the requested single R-SC reconciliation report and the two subsequently requested research companions. All three build on merged PR 147, commit `5b55e55a103fad2d82d625983080b39f2db21c0e`. The three files in the supplied research brief ZIP matched that repository snapshot exactly. This is a research handoff, not a repository patch.

## Read in this order

1. [Shared contract reconciliation](Recursion_Shared_Contract_Reconciliation.md): all 21 R-SC questions, exact field ownership and joins, competing readings, synthetic falsifiers and explicit non-proofs. “Accepted candidate” means the proposed coherent candidate for Owner consideration, not an adopted wire contract.
2. [Harness orchestration performance](Recursion_Harness_Orchestration_Performance.md): ACP, structured harness interfaces and CLI topologies; route-specific adapters versus ACP-first normalization; a provider-free local benchmark design. No universal speed winner is established.
3. [Prompt plugin and skill architecture](Recursion_Prompt_Plugin_Skill_Architecture.md): bounded instruction compilation, plugin capability states, selective discovery, mandatory dependencies, skill retention and compaction. It includes the local handoff for the [inert synthetic corpus](synthetic_benchmark_corpus.json).

## What local sessions need to do

- Reconcile these proposals against any commits after the pin above; retain the exact source and candidate identities used for each result
- Review the proposed contract choices before adopting or implementing them; preserve accepted Owner decisions and frozen M1 contracts
- Build independently checked positive controls and adversarial vectors for the shared joins before treating structural agreement as behavior
- Implement and run the bounded synthetic orchestration and skill-discovery experiments under a separately admitted local task, recording missing observations and failed controls honestly
- Keep real upstream qualification, native-platform fault tests and any provider/model/account work behind their existing separate approvals
- Return the resulting repository commit and exact observed evidence, including failures and unknowns, for the next research reconciliation

## Evidence boundary

Repository source and public documentation were read; the reports and inert corpus received static consistency and coverage checks. No target code, target tests, model/provider calls or Work/Codex sessions were launched. All proposed runtime and performance vectors remain **UNEXECUTED**. No technology stack, route, privacy guarantee, runtime behavior, token saving or subscription benefit is qualified by this packet.

The corpus is data, not an executable runner. Its synthetic instructions and adversarial cases are fixtures for later controlled testing, not instructions to the reader or permission to perform actions. Review all controls and finite budgets before execution.

`SHA256SUMS.txt` identifies the delivered files. Repository citations are pinned external links; no stale source checkout, raw captures, private working notes or generation scripts are included.
