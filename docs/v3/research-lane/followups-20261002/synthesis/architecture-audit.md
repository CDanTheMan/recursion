# Architecture audit (synthesis)

This synthesis aggregates the read-only architecture audit in
`../raw/ds-architecture-audit.md`. It preserves the audit's findings, severity, evidence
classes and proposed packets. It is a research synthesis, not a decision, and it adopts no
technology, authorization or scope change.

## Provenance and method

- **Source:** one static architecture audit of the pinned commit
  `3a542c6bbd88351e6f6c5eceffd317bc2450fcad`, retrieved 2026-10-02.
- **Method:** the audit enumerated all 910 tracked files, recomputed their Git blob hashes against
  the supplied tree (all matched), and read authority/entry documents, specification slices, the
  three planning modules, representative tests/oracles, selected experimental evidence and the
  current research layer plus the five follow-up reports.
- **Static snapshot only.** Nothing in the audit executed Recursion code: no script, test, model
  checker, provider, service, host-control action or deployment was run, and no snapshot or
  remote file was modified. This is not retroactive proof that any experiment, gate or receipt
  actually ran.
- **Evidence classes used throughout:** *source-observed* (visible in this exact tree),
  *repository-reported* (a historical run/outcome recorded but not rerun here), *specified* (a
  product obligation or proposed mechanism, not working software), *inference* (an architectural
  consequence drawn from inspected evidence), and *unmeasured/unverified* (required evidence is
  absent from the audit).
- **Severity scope:** “high” concerns consequence to construction or release. No deployed system
  was inspected, so it does not mean an exploitable live vulnerability.

## What actually exists

The audit's headline: the tree is a substantive, carefully defended **contract-and-experiment
foundation**, not yet a usable v3 harness.

- **Implemented product substrate:** three pure Python planning modules — `canonical.py`,
  `contracts.py` and `kernel.py` — providing strict decode/schema/scope admission and pure
  reduction with replay over fixture authority/policy and an in-memory receipt journal.
- **M1B/M1C:** schemas, literal fixture bundles and test-only reference oracles. The audit counts
  71 fixture bundles (23 planning, 24 execution, 24 integrity) and 17 `*.test.py` programs
  (7/5/5); these are distinct denominators, not “71 tests passed.”
- **Experiments:** 220 files (219 Python) of prototypes, finite models, mechanism probes and an
  inert recovery ledger — experimental support material, not the product runtime.
- **Inventory and limits:** 562 docs, 102 scripts, 9 schemas, 6 state files and 11 root/tool
  files; no `pyproject.toml`, `setup.py`, `package.json`, `Cargo.toml` or `go.mod`. M1A's AST gate
  forbids filesystem/network/process/storage imports and calls; replay consumes fixture authority
  and an in-memory journal; M1B's oracle is test-only; M1C performs no represented effect.

The audit states this is a construction-stage finding, not evidence the product direction is
wrong. Missing from this snapshot: the durable kernel service, native sampling/tool loop,
qualified upstream adapters, operator CLI, plugin runtime, context governor and node fabric.

### Requirements-to-evidence gaps (audit map)

| Requirement | Evidenced here | Missing proof |
|---|---|---|
| Decode, validation, plan/scope admission | `canonical.py`, `contracts.py` | production authentication, future-epoch coverage |
| Pure reduction/replay | `kernel.py` | durable atomic writer, lifecycle, real effects |
| Routes/plugins/process | M1B schema, fixtures, test-only oracle | real adapters, plugin containment, broker |
| Evidence/effect/publication/state | M1C schema, fixtures, pure evaluators | authentication, effect mediation, physical storage, actuator |
| Composition/recovery models and recovery allowance | finite models, inert ledger, historical review | integrated model, real counters, physical crash durability |
| Native, upstream-only, combined execution | required and architecturally placed | working loops, qualified adapters, no-hidden-connection trial |
| CLI, context/compaction, plugins, node tethering | detailed proposals | implementations and real qualification |

## Key findings (by severity)

The audit records nine findings; severity is reproduced as recorded.

- **A-01 — High: current-looking documents disagree on retired authority and migration.** README,
  START-HERE, ARCHITECTURE, STATE and the new follow-up README still describe pre-v3/Hermes
  governance or prescribe v2 migration, contradicting D-017 and the supersession banner.
- **A-02 — High: research-to-repository reconciliation is missing.** The master synthesis looked
  at public/synthetic material, so “missing” claims hold only when scoped to the new corpus and
  unqualified profiles; literal M1 vectors and a ten-control table already exist.
- **A-03 — High: canonical-byte epochs need an explicit compatibility boundary.** M1A rejects
  floats/lexical `-0` and sorts by UTF-16; M1B/M1C have their own profiles; newer research
  explores float-capable JCS and a CBOR test envelope.
- **A-04 — High: durable authority and real effect enforcement remain integration premises.** The
  planner does not commit state, and a signed record, callback, canceled process or broker ACK
  cannot become authenticated admission, revocation or a settled effect.
- **A-05 — High for release: native/upstream role closure is not implemented.** Required
  independent native and upstream-only workflows and the full role matrix have no qualified
  runtime; a native path cannot be deferred and upstream cannot hide direct inference.
- **A-06 — High for release: plugins need semantic conformance and actual disabled-path proof.**
  The disabled-path oracle zeroes counters without instrumenting a runtime; manifest equivalence
  is not portability and signature verification is not authority.
- **A-07 — High for release: smart compaction is a specification, not a demonstrated
  optimizer.** Structural integrity and semantic quality are separate; savings, quality and cache
  economics are unmeasured.
- **A-08 — High for release: node tethering must qualify the accepting endpoint, not just
  transport.** Connected is not eligible and disconnected is not stopped; Windows/Linux
  recorded-work recovery is required, live process migration is not promised.
- **A-09 — Medium: structural gates are useful but cannot accept semantic research.**
  `check_followups.py`/`check_synthesis.py` check inventory, front matter, headings, links and
  secrets, not cited sources, false claims or gap closure.

## Authority and scope drift

The audit's central non-technical finding (A-01/A-02) is that current-looking guidance and the
research layer can send an agent into retired or out-of-scope work.

- September 28 governance and **D-017** retire v1/v2 and the Hermes-led repository control plane;
  v3 is greenfield and retired, not migrated, yet several entry points and specifications still
  present the old constitution as operative or prescribe v2 strangler migration, and the new
  follow-up README repeats operative-Hermes language.
- The audit distinguishes Hermes the optional upstream engine from the retired Hermes-led
  repository executive; upstream use remains in scope where accepted product scope requires it.
- Research claims must be bound to an exact scope and predecessor: the master synthesis looked at
  public/synthetic material, so GAPS statements such as “vectors do not exist” and “zero OS cells”
  hold only for the new proposed corpus, not the whole repository.
- Structural document gates can pass while stale authority text and “unknown” cells persist, so
  the audit does not treat a green gate as scientific acceptance.

The audit's proposed resolution is reconciliation, not rewriting protected decisions: a
non-protected documentation patch and supersession map that preserves historical source, reason
and explicit supersession, and does not delete required future v3 schema migration/update/rollback
obligations along with obsolete v2 cutover text.

## Evidence-to-implementation seams

The audit frames the gap as an **evidence-to-implementation seam**, not a knowledge gap. Its five
headline conclusions are:

1. **Preserve the full product.** Native-only, upstream-only and combined execution are equally
   real release requirements; a thin wrapper, an exclusively native harness, or an upstream-only
   system with a hidden native planner/compactor would each miss accepted scope.
2. **Repair authority and scope drift before admitting construction.** v1/v2 and Hermes-led
   repository control are retired; repeated contradiction defeats the “one trustworthy
   specification” goal.
3. **The five follow-up reports are decision inputs, not gap closure.** FU-01/02/04 do not run
   experiments; FU-03 does not run the model checker or implement the stacks; FU-05 does not
   implement its protocol. They can close specification/design questions but cannot turn G-01–05
   into measured or independently accepted results.
4. **Do not retrofit the frozen M1 wire contracts to match newer research.** M1A, M1B, M1C and the
   prospective FU-01/FU-03 formats are distinct layers/epochs; a typed, tested bridge is required,
   not an M1 mutation.
5. **Build evidence across seams before optimizing components.** Cross-implementation equality,
   large state counts and a green document gate are useful but insufficient; demand independent
   invariants, seeded failures, current-authority checks at the effect boundary and honest
   unresolved outcomes.

The audit notes what the existing tests do well (literal receipt/state/digest conformance,
replay/decode checks, purity, attenuation, graph conflict, stale bindings) while stating they do
not show authenticated principals, adversarial containment, power-loss durability, actual upstream
control or independent human acceptance. Supplied fixture facts are premises; integration must
prove each fact where it is supplied and enforced.

## Proposed next construction packets

The audit proposes a finite first hardening cycle of seven bounded packets — a proposal for
report intake, not an instruction to run them, and no open-ended swarm, new broad research wave,
production service or live provider trial. Each packet uses one task/worktree, exact
source/candidate, allowed paths, finite resources, a machine gate and an independent verifier.

- **LP-0 — Reconcile authority and evidence trace.** Eliminate A-01/A-02/A-09 before
  implementation consumes stale premises; produce a requirement-to-source/code/test/gap crosswalk,
  current/historical/superseded classification and evidence manifests. Preserve frozen gates and
  protected logs.
- **LP-1 — Build the model/vector compatibility bridge.** Make FU-03 executable without mutating
  frozen M1: finite model, mutant manifest, typed canonical-byte corpus, refusal taxonomy,
  trace-validity checker and mapping to existing obligations and M1 literals.
- **LP-2 — Qualify minimal native OS primitives.** Turn FU-04 into observed per-profile facts for
  store, broker and nodes using synthetic owned-child fixtures and temporary files only.
- **LP-3 — Compare canonical writer crash/replay candidates.** Executable FU-02 evidence against a
  candidate-neutral state/effect oracle; no product default selection.
- **LP-4 — Run equivalent runtime candidates.** Decision-producing FU-01 evidence: equivalent
  experimental stacks, independent conformance, full accounting and hard floors before
  performance comparison.
- **LP-5 — Exercise the broker contract under native chaos.** Executable FU-05 evidence at the
  process/view boundary with fixture children, synthetic streams and temporary broker state.
- **LP-6 — Compose one inert product seam.** Synthetic goal spanning fake route/plugin, capsule,
  fake node attempt, compaction loss, revocation and reconnect, with seeded adversarial traces.

The audit sequences them: LP-0 can run while LP-1/LP-2 are drafted; LP-3/LP-4 consume admitted
outputs; LP-5 consumes platform/command contracts; LP-6 composes accepted seams. Independent
review capacity is a real dependency. Every result carries exact input/candidate hashes, scope
evidence, pins, finite bounds, author/reviewer identities, raw attempts (including failed,
aborted and censored runs), controls, oracle version, measured denominators, limitations and an
explicit accepted/repaired/blocked disposition.

## What this does not prove

- The audit is a **static snapshot at the pinned commit**; no code was run and it is not
  retroactive proof the experiments ran, nor a claim that all tests pass on this commit.
- No historical gate or receipt was rerun, and no exhaustive semantic audit of all 266 Python
  files, all research reports, every schema field or all 910 files was performed.
- No external primary-source revalidation, route entitlement/legal review, live upstream
  qualification, performance measurement, power-loss trial, vulnerability scan or supply-chain
  clearance was done; no current machine, account, session or consumption state was inspected.
- The findings describe construction/release consequence, not exploitable live vulnerabilities.
- The proposed packets are not authority to select a technology, modify protected paths, enroll
  nodes, use credentials, deploy, or run destructive fault injection outside a separately
  approved isolated environment.

## Owner decisions

The audit leaves these to the Owner and records none as decided here:

- Whether to accept the reconciliation (LP-0) and the finite hardening cycle, in what order,
  subject to independent review capacity, and the exact current-authority/supersession wording
  for non-protected guidance without editing protected decisions or reviving deleted infrastructure.
- Any technology or default choice the research explicitly does not make: language, store,
  renderer, plugin sandbox, universal compaction policy, consensus model, transport topology or
  support window.
- Revalidation of exact product/route/version eligibility and entitlement; absence of a
  launch-critical integration requires an Owner release decision.
- Whether an unresolved non-dominated tradeoff (e.g. LP-3 store, LP-4 runtime) returns for
  selection rather than being silently chosen; any protected-path change, credential use, node
  enrollment or destructive fault-injection environment remains human-gated.

## Relevance to next steps

The audit's productive sequence is **reconcile current truth → preserve/version the contracts →
execute the finite model/platform/store/runtime/broker comparisons → compose one adversarial seam
→ build required product slices → run complete workflow/recovery acceptance**, keeping plugins,
smart compaction and node tethering first-class throughout rather than deferring their contracts
behind a supposedly complete kernel.

Its bottom line: the strongest asset is discipline around literal contracts, explicit
uncertainty, bounded evidence and retained reviewer counterexamples; the major weakness is the
missing bridge between the research/specification layer and the implementation boundary,
compounded by stale authority and migration language. The audit is therefore an input to intake
and reconciliation — not a design authority, a decision, or proof any proposed experiment has run.
