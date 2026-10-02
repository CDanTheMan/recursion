# Recursion overnight research handoff

Research date: 2 October 2026 UTC  
Authoritative repository snapshot: `73d70505b8c266fbb08d820d304ebd2e68ac7f1b`  
Branch at research time: `loop/work/orchestrator-reconciliation-20261002`

This is an extractable research packet for review and later, separately authorized local sessions. It contains findings, candidate contracts, source references, exact unresolved questions and unexecuted acceptance designs. It is not a patch, executable test runner, implementation, route qualification or authorization to change the repository or run a target.

## Start here

1. Read [DECISION-READOUT.md](DECISION-READOUT.md) for the findings that change the next step
2. Read the [integrated model architecture](synthesis/MODEL-ARCHITECTURE.md), then its [ownership and field map](synthesis/OWNERSHIP-AND-FIELD-MAP.md). These reconcile the lane proposals; they do not ratify them
3. Use [LOCAL-SESSION-HANDOFF.md](LOCAL-SESSION-HANDOFF.md) to scope the next local session and the [joined acceptance handoff](synthesis/INTEGRATION-TEST-HANDOFF.md) for cross-boundary tests
4. Use the [117-row ledger](gaps/complete-ledger.md) and [evidence reconciliation](gaps/report.md) when deciding what is still open
5. Follow the relevant lane report and machine appendix for details. [COVERAGE.json](COVERAGE.json) indexes the original 580 research obligations. [FIXTURE-INDEX.json](FIXTURE-INDEX.json) points to acceptance designs without deleting their distinct cases

Extract the entire ZIP into one folder. Preserve its relative paths. Markdown can be read in an editor; JSON/CSV files are editable data. There are no supplied execution scripts. Repository-relative locators in prose identify files in the pinned repository and are not promises that the repository is bundled.

## Checkpoint2: reviewed kernel and M1B additions

Read [CHANGELOG.md](CHANGELOG.md) before using earlier supplemental test recipes. The original 21 reports, 580 research obligations and 425-case index remain frozen. These additional catalogs are separate:

- [Qualified SK01–SK05 audit](additional-kernel-research/SUPPLEMENTAL-KERNEL-AUDIT.md): five static/inferred kernel/model candidates, with the post-delivery SK02 setup qualification
- [Semantic-guard audit](semantic-guard-research/SEMANTIC-GUARD-COVERAGE.md) and [matrix](semantic-guard-research/coverage-matrix.json): eight additional SG01–SG08 source-level candidates, alongside existing enforced guards
- [Local reproduction handoff](kernel-local-handoff/LOCAL-KERNEL-REPRODUCTION-HANDOFF.md) and [13-case catalog](kernel-local-handoff/cases.json): a dependency-ordered SK/SG synthesis; all reproduction cases remain UNEXECUTED
- [Semantic-validation hardening](semantic-validation-hardening/SEMANTIC-VALIDATION-HARDENING.md): a comparison of two conforming designs for maintaining semantic obligations, not an accepted repair or technology choice
- [M1B audit](m1b-semantic-research/M1B-SEMANTIC-COVERAGE.md): two useful test additions for RESIZE semantics and split multibyte payloads. The queue-byte absence lead was withdrawn because later calibration already covers it. No new M1B implementation defect was established

**Setup qualification:** earlier packet-dependent seeds, including SK02's stored prefix, are producer diagnostics rather than independently whole-contract-valid controls. Shared packet-correlation metadata and F005's separate effect mismatch require a separately identified and reviewed whole-prefix-valid source/fixture regime before an isolated conformance claim. Resealing bytes alone cannot repair a hardcoded constructor. Preserve historical source, fixtures and oracles; do not silently edit them to force a test through.

These additions are reviewed static/inferred research, not executed counterexamples, accepted bugs, authorized fixes or runtime qualification. Both earlier ZIPs remain separate unchanged checkpoints. This consolidated archive is a checkpoint, not a declaration that overnight research has ended.

## Checkpoint3: bounded M1C test strengthening

The [M1C pure-classifier review](m1c-classifier-research/M1C-CLASSIFIER-REVIEW.md) establishes **no new mandatory classifier defect**. Its [11-row guard/witness map](m1c-classifier-research/semantic-matrix.json) and [seven complete UNEXECUTED vectors](m1c-classifier-research/future-synthetic-vectors.json) propose a small evidence-relation check, particularly retention of qualifying evidence through refusal. Historical receipt precedence and later-start-only behavior are intentional, previously covered semantics, not new bugs.

The [source pins](m1c-classifier-research/source-pins.json) retain bounded repository-byte provenance. This prepared addition is pure-classifier evidence/test strengthening, not runtime qualification, a new accepted fix or permission to execute. It stays separate from all original and earlier additive counts. Earlier checkpoints remain unchanged; [CHANGELOG.md](CHANGELOG.md) records the progression.

## What each layer means

- `synthesis/`: final integrated research interpretation and field reconciliation for this packet; still a proposal, with unresolved conflicts and qualification gates
- `re/` through `ry/`: 21 specialist reports and detailed candidate appendices. A lane's `MUST`, JSON field, threshold example or recommended design is not an accepted product decision
- `model-architecture/`: supporting earlier architecture comparison and canonical public-source notes. Kept because later reports cite its facts and test lineage. Where its integration state differs, read the final `synthesis/` interpretation and the pinned governance first
- `gaps/`: 57 architecture edges, 33 gap rows and 27 harness/product/category rows, totaling 117. Closed Owner decisions and open implementation qualification are distinct
- `protocol-edges/`: supplemental version-specific MCP edge analysis and ten unexecuted cases
- `shared-evidence/`: navigation to canonical public factual passages. Source registers retain source/version/retrieval and hash limitations; raw captures and public code archives are not included
- Root navigation, coverage, fixture index and quality files: packet-level reading and verification aids, not product evidence

## Authority and evidence rules

The latest explicit Owner instruction and the current authoritative repository governance take precedence over this packet. At the research pin, start with `CONTROL_PLANE.md`, `ANCHOR.md`, `state/DECISIONS.md` and the active v3 goal. If your checkout is newer, reconcile its changes before using these findings. Do not silently apply this packet to another revision.

The final integrated synthesis is the preferred reading order among these research proposals. It cannot override governance, manufacture acceptance or erase a lane's specific falsifier. Do not blind-merge the candidate schemas or collect every proposed mechanism into one implementation. Preserve the existing contract version until a separately authorized decision changes it. In particular, do not expand the frozen M1B wire union while borrowing higher-level interface ideas.

Evidence labels vary slightly by report but have four meanings:

- **Source-documented**: an authoritative project requirement or cited primary source states it. Public documentation is not runtime evidence
- **Locally observed / static observation**: inspected bytes, hashes or historical receipt contents. Reading an old result is not a new run
- **Inferred / proposed**: architectural reasoning, a candidate schema, comparison or test predicate
- **Unknown / unverified**: evidence is absent, incomplete, conflicting or not qualified. Unknown is never zero, false or pass by substitution

The 381 numbered questions and 199 completion bullets are research-coverage obligations. Addressing all 580 does **not** mean 199 runtime passes or 580 proved claims. A gate demanding measurement can have a complete bounded-unknown answer and remain open. All new target tests and benchmarks in this packet are **UNEXECUTED**. Document parsing, digest checks and link checks establish only artifact properties described in [QUALITY-NOTES.md](QUALITY-NOTES.md).

## Boundaries preserved

D018–D033 remain accepted constraints. Recursion is a native harness and an orchestrator; upstream-only use cannot secretly depend on native helper inference. The comprehensive capability set remains built and opt-in under D019. D020 retains a single-node core with fencing/availability seams and a required user-toggleable first-party takeover capability for remote/full; it does not mandate default consensus. D022 keeps Aggressive / Full / Lazy and checkpoint / interrupt / drain distinct. Codex-first qualification is an order, not a passed route.

Exact native platform floors remain in the authoritative D028 decision; WSL is development/test evidence. D029's strong credential claim requires direct and induced-flow protection, not just denied file reads. Productive-continuity and cheap-porting advantages remain hypotheses. No language, store, framework, runtime, renderer, transport, sandbox product, model or vendor is selected. No legal route is cleared and G32 is not closed.

TUI-first construction and a shared backend are retained. The precise relationship between “GUI later” and D019's built-and-opt-in release scope needs explicit Owner interpretation; this packet does not choose a smaller release.

## Before a local agent acts

Reading this ZIP is authorized research handoff. Execution is a separate decision. Bind the exact source/candidate, allowed paths, disposable environment, fixture/oracle identity, finite resource/time limits, evidence destination and stop conditions. Keep real credentials, accounts, providers, live hosts, spending, installs and counsel contact outside a provider-free session. If no verified entrypoint exists, design or implement it only under that session's authorization; do not invent a command or run a repository script merely because it is named here.
