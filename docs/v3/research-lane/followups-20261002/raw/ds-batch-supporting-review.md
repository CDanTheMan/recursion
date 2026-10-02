---
title: Recursion followup research batch
source-prompt: follow-up batch supporting review
session: Codex Dot follow-up research — specification only, target experiments NOT run
retrieved: 2026-10-02
status: research-evidence-not-a-decision
verification: not independently verified by Recursion; target experiments not run
---

# Recursion followup research batch

Supporting document review and local execution handoff

Prepared for Lucas | Uploaded packet dated 1 October 2026

## Purpose and conclusion

The uploaded archive contains five research briefs, a README, and a Python structural checker. The five research reports address 60 numbered questions in total. This companion reviews the two supporting files and provides a cross-report execution sequence. It does not replace any individual research report or certify a runtime, database, operating system, model, or broker.

The central distinction is between completed research specifications and unperformed experimental validation. The briefs expressly prohibit running their target experiments in these research sessions. Their requests for measured conformance cannot therefore be truthfully marked passed here. Local agents must collect the evidence listed in each report, using Owner-approved scope and isolated test environments. Owner decisions remain distinct from test results.

## Archive inventory

| Input | Role | Numbered questions |
| --- | --- | --- |
| FU-01-language-runtime-experiment.md | Runtime experiment and no-selection rule | 14 |
| FU-02-canonical-store-crash-replay.md | Store crash and replay benchmark | 13 |
| FU-03-formal-model-and-conformance-vectors.md | Finite model, mutants, and byte conformance | 12 |
| FU-04-os-platform-conformance-fixtures.md | Native and compatibility platform qualification | 10 |
| FU-05-broker-protocol-chaos.md | Broker freeze blockers and chaos matrix | 11 |
| README.md | Research-wave index, dependencies, and gate instructions | Not a separate research brief |
| check_followups.py | Structural and pattern-based checks | Not a research or conformance test |

These counts and the presence of all seven files were observed by reading the uploaded archive. They are not claims that all scientific requirements have been experimentally satisfied. The five reports retain the uploaded briefs as their research inputs. A separately requested repository audit examines the current committed tree and maps integration differences; it is not retroactive evidence that these experiments ran.

## Review of the README

The README describes a deliberately bounded five-brief follow-up wave. It identifies FU-03 as a prerequisite for FU-01: the runtime experiment consumes a common byte-level corpus, refusal vocabulary, and trace-validity contract. FU-04 supplies the platform-specific facts needed by FU-02 and FU-05. This supports researching independent source questions in parallel while holding downstream experimental admission until the dependency artifacts are accepted and pinned.

The README also references a gap register, constitution, anchor, agent instructions, and prior syntheses that are not included in this archive. Those references explain the intended repository context. They do not establish that this research has read their contents or recovered their exact accepted definitions. Each brief says it is self-contained, so its supplied context is the boundary of available prior-state evidence. A local agent should reconcile proposed completions against the actual authoritative records before implementation.

The phrase executable specification is treated as a requirement for concrete contracts, inputs, transitions, expected results, and rejection rules. It does not authorize the research session to perform the experiments that the same brief prohibits. A proposed deterministic format is not evidence that two implementations produce its bytes, and a finite model definition is not evidence that TLC explored it.

## Review of the structural checker

The checker was read statically. It was not executed, imported, or modified. This review concerns the uploaded source only.

The script searches upward from its own directory for tools/check_public_scope.py and imports that module's PATTERN. The archive does not include that dependency. Its relative-link checks also require files outside the uploaded folder. The later, separately requested repository snapshot provides that context for static audit, but the checker remains unexecuted here; this companion does not manufacture a substitute dependency or claim a gate result.

The declared checks are internally consistent with a structural gate: the five expected FU filenames, required front-matter keys, allowed status, unique titles, eight required section headings, the research directive marker, README references, relative Markdown link existence, reused forbidden-identifier pattern, and several obvious-secret patterns. Unexpected FU filenames are rejected. Both README and FU documents receive link and pattern checks.

Several limits matter when interpreting a future PASS:

- Front matter is parsed with a small line-and-colon routine rather than a general YAML validator. Presence of a date or goal key does not validate its meaning or authority
- Heading and directive checks use substring presence. They cannot establish that the sections contain complete or correct research
- The Markdown-link regular expression checks simple links and filesystem existence. It does not validate anchors, HTTP destinations, source quality, or all possible Markdown syntax
- Secret detection is pattern-based and limited to listed token forms and literals. A clean scan is not proof that every secret or sensitive datum is absent
- A failure can print part of a matched suspected secret. Treat raw checker output as potentially sensitive until reviewed; redact before sharing logs
- Importing the scope-check module executes its top-level Python code. A local agent should inspect the expected dependency before running the provided checker, rather than treating the script's descriptive no-network claim as a transitive guarantee
- No check evaluates benchmark design, statistical inference, model coverage, mutation reachability, byte correctness, platform qualification, or Owner acceptance

These are static observations and bounded inferences from the uploaded script, not observed failures in its intended repository. There is no recommendation to replace the checker or change its policy in this research task.

## Current authority clarification

Lucas explicitly confirmed that Hermes is retired and Recursion v3 is a standalone harness that also wraps and orchestrates other harnesses. The older operative-Hermes language in the supplied packet must not be carried into new execution instructions as current authority. Preserve native, upstream-only, and combined workflows while resolving exact implementation and scope questions through the current Owner-controlled records. This clarification does not select a runtime or authorize live operations.

## Cross report local execution sequence

### Stage 1 Reconcile authority and pins

Local sessions first read the actual operative instructions and accepted gap decisions. Reconcile each report's candidate fields with those records. Keep unsupported prior-state details explicitly unknown until resolved. Record a precise experiment identity, versions, host profile, dependency closure, and source digests. Preserve historical freeze pins separately from newly proposed current versions.

Required evidence: an Owner-approved scope record and immutable input manifest, plus a list of unresolved decision inputs. Stop if an input would require silently selecting a product default, changing an accepted decision, or assigning an unsupported durability or availability guarantee.

### Stage 2 Establish the two prerequisite lanes

FU-03 local sessions supply the specified finite-model modules, baseline run, reachable-mutant classification and retained counterexamples, independently specified byte corpus, and two independent implementation results. They must not count an unexecuted mutant as killed or an equivalent/unreachable case as a successful detection. The report's model bounds remain part of every conclusion.

FU-04 local sessions inventory exact native and compatibility profiles and execute the approved negative traces. Required observations distinguish process membership, process exit, transport closure, and settled execution. Disk exhaustion, forced termination, and interruption experiments belong on disposable, explicitly approved test systems, with recovery and stop conditions in place. A production workstation is not an implied destructive-test target.

The two prerequisite lanes may progress in parallel where independent. Downstream consumers remain held for whichever prerequisite they need. Passing one profile does not qualify a different filesystem, terminal, compatibility layer, or security configuration.

### Stage 3 Run dependent experiments

FU-01 uses the accepted FU-03 corpus and pinned host conditions. It tests hard floors before collecting or comparing resource results. Any correctness, authority, replay, or reproducibility-floor failure rejects that arm for this experiment, regardless of speed. The comparison must include helper processes and dependency closure rather than hiding costs in another process.

FU-02 uses the accepted platform profiles and identical canonical workload and CAS assumptions for both finalists. Local evidence must separately establish replay parity, stale-writer exclusion, duplicate-command reuse, consistent backup/restore, and the precise claimed durability failure class. A process-kill pass is not a power-loss pass. A database writer lock is not an authority lease.

FU-05 requires actual resolution or approved narrowing of all four freeze blockers and accepted platform observations. It then runs its interoperability and chaos cases, including slow readers, replay gaps, ACK/credit edge cases, rollover/incarnation, and containment escape paths. A transport acknowledgment does not settle a tool effect or authorize a new action.

### Stage 4 Independent acceptance

Collect immutable receipts from the local runs and have an independent reviewer compare them against the preregistered oracles. Report qualified, rejected, held, or unknown using each report's defined vocabulary; do not map unknown to success. Resolve cross-report discrepancies before any Owner decision. Choosing a language, store, durability promise, protocol revision, or product default remains an explicit Owner act.

## Required local result packet

Every local handoff should return the report and requirement identifiers, exact input and source identities, host/profile identity, time and failure class, raw evidence references, observed versus expected result, uncertainty, stop reason if any, and independent reviewer disposition. Preserve failed and incomplete attempts alongside successful reruns. A changed source, host, dependency, timeout policy, or experimental condition creates a distinct run that cannot overwrite the failed one.

The following states remain distinct: research finished; specification proposed; specification accepted; local experiment not run; experiment inconclusive; floor failed; qualified within a named scope; and Owner selection made. No report delivery alone advances the later states.

## Completion status of this companion

The archive inventory and static supporting-file review are complete. The uploaded structural checker was not run. Its repository dependency and external relative-link targets were absent from the zip and later available only through the separate static repository audit. Target experiments and implementation acceptance remain tasks for the user's local sessions. This companion introduces no product selection and no new executive authority.

## Source record

Primary inputs for this companion are the seven files in followups-20261001.zip uploaded by Lucas on 1 October 2026. Findings about the checker and README come from direct static inspection; execution-sequence recommendations are proposals derived from their declared dependencies. Detailed public citations, candidate-specific falsifiers, and individual completion gates are in the five accompanying research reports.
