# Follow-up batch supporting review (synthesis)

## Provenance

This synthesis summarizes `raw/ds-batch-supporting-review.md` (its own title: "Recursion followup research batch"). It reviews two supporting files plus a cross-report execution sequence, is research and static inspection only, read the structural checker without executing it, and ran no target experiment, platform qualification or benchmark. "The report's sources" are the uploaded archive files and the reports' cited public sources.

## What it reviews

The companion reviews the two supporting files and gives a cross-report execution handoff; it
does not replace any research report or certify a runtime, database, OS, model or broker.

- **README** — a deliberately bounded five-brief wave. It makes FU-03 a prerequisite for FU-01 (a common byte corpus, refusal vocabulary and trace-validity contract) and FU-04 the source of platform facts for FU-02 and FU-05, so source questions can be researched in parallel while downstream experiments stay held until dependency artifacts are accepted and pinned. Its referenced gap register, constitution, anchor, agent instructions and prior syntheses are not in the archive, so their exact definitions were not read.
- **Structural checker** (`check_followups.py`) — read statically, not executed. It imports a `tools/check_public_scope.py` dependency absent from the archive, as are some relative-link targets. Its checks match a structural gate (expected FU filenames, front-matter keys, allowed status, unique titles, eight required headings, directive marker, README references, link existence, forbidden-identifier reuse, secret patterns), but they are substring/pattern checks and cannot establish research completeness.

The central distinction is between completed specifications and unperformed experimental validation: the briefs prohibit running their target experiments, so measured conformance cannot truthfully be marked passed here. The five reports address 60 numbered questions in total, observed from the archive rather than experimental satisfaction, and a checker PASS would remain structural only.

## The four execution stages

The companion proposes a dependency-derived cross-report sequence, not an observed result.

1. **Stage 1 — reconcile authority and pins.** Local sessions read the actual operative
   instructions and accepted gap decisions, reconcile each report's candidate fields with them,
   keep unsupported prior-state details explicitly unknown, and record exact experiment
   identity, versions, host profile, dependency closure and source digests. Historical freeze
   pins are kept separate from current proposals. Required evidence is an Owner-approved scope
   record and immutable input manifest plus unresolved decision inputs. Stop if an input would
   require silently selecting a product default, changing an accepted decision, or assigning an
   unsupported durability or availability guarantee.
2. **Stage 2 — establish the two prerequisite lanes.** FU-03 supplies finite-model modules,
   baseline run, reachable-mutant classification, retained counterexamples, a byte corpus and
   two independent implementation results; an unexecuted mutant is not killed and an
   equivalent/unreachable case is not a detection. FU-04 inventories exact native and
   compatibility profiles and runs approved negative traces, distinguishing process membership,
   process exit, transport closure and settled execution, with destructive work only on
   disposable approved systems. The lanes may run in parallel where independent; downstream
   consumers stay held for whichever prerequisite they need, and passing one profile does not
   qualify a different filesystem, terminal, compatibility layer or security configuration.
3. **Stage 3 — run dependent experiments.** FU-01 uses the accepted FU-03 corpus and pinned
   hosts, tests hard floors before comparing resources, and includes helper processes and
   dependency closure in cost. FU-02 uses accepted FU-04 profiles with identical canonical
   workload and CAS assumptions, separately establishing replay parity, stale-writer exclusion,
   duplicate-command reuse, consistent backup/restore and the precise durability failure class
   (a process-kill pass is not a power-loss pass; a database writer lock is not an authority
   lease). FU-05 requires resolution or approved narrowing of all four freeze blockers and
   accepted platform observations, then runs its interoperability and chaos cases including
   slow readers, replay gaps, ACK/credit edge cases, rollover/incarnation and containment
   escape paths. A transport acknowledgment does not settle a tool effect or authorize action.
4. **Stage 4 — independent acceptance.** Immutable receipts from local runs are compared by an
   independent reviewer against the preregistered oracles and reported as qualified, rejected,
   held or unknown using each report's vocabulary, with unknown never mapped to success.
   Cross-report discrepancies are resolved before any Owner decision, and choosing a language,
   store, durability promise, protocol revision or product default remains an explicit Owner act.

## Authority clarification

The companion records Lucas's explicit confirmation that **Hermes is retired** and that
Recursion v3 is a standalone harness that also wraps and orchestrates other harnesses. Older
"operative-Hermes" language in the supplied packet must not be carried into new execution
instructions as current authority. Native, upstream-only and combined workflows are preserved,
and exact implementation and scope questions are resolved through current Owner-controlled
records. This clarification does **not** select a runtime or authorize live operations.

## Required local result packet

Every local handoff should return: report and requirement identifiers; exact input and source
identities; host/profile identity; time and failure class; raw evidence references; observed
versus expected result; uncertainty; stop reason if any; and independent reviewer disposition.
Failed and incomplete attempts are preserved alongside successful reruns, and a changed source,
host, dependency, timeout policy or experimental condition creates a distinct run that cannot
overwrite the failed one. The companion insists on distinct states that must not be collapsed:

- research finished;
- specification proposed;
- specification accepted;
- local experiment not run;
- experiment inconclusive;
- floor failed;
- qualified within a named scope;
- Owner selection made.

No report delivery alone advances the later states: research finished does not mean a
specification was accepted, and a specification accepted does not mean an experiment ran.

## What this does not prove

This companion is a static review and handoff, not a research brief, conformance test or
product decision, and it introduces no product selection or new executive authority. The
structural checker was not executed, so it yields no gate result; the archive lacks its
scope-check dependency and some link targets. No target experiment, benchmark, model-checker
run or platform qualification was performed, and the stages, state vocabulary and result-packet
fields are proposals derived from the reports' declared dependencies. A deterministic format in
a report is not evidence that two implementations produce its bytes, and a finite model
definition is not evidence that a model checker explored it.

## Relevance

This is the entry-point document for the follow-up wave: read it first for dependencies, then reconcile authority, contract versions and candidate definitions before any implementation. It defines the ordering in which FU-03 and FU-04 prerequisite artifacts gate FU-01, FU-02 and FU-05, and supplies the result-packet and independent-acceptance discipline later waves must follow, keeping explicit the boundary between proposed specifications, accepted contracts, unrun experiments and future Owner decisions.
