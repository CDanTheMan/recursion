# SC-CUT-SOURCE-01 findings — 2026-09-08

Registration must advance source authority even when the record head stays unchanged.
The constructed protocol captures registry, revision, incarnation and exact ordinal count,
collects every admitted record, and checks that boundary at attestation, fresh publication
and reconciliation. A pending attempt without its start prevents a complete attestation.
Exact retained retries return the previous receipt without appending again. Atomic
registration/start is an alternative transition with an explicit AttemptStarted guard.

Accepted run-10 at source commit 9110065c3b393de3259abfbd3f487c552fb43294 contains
51 profiles / 104 environments, 17966 states and 31140 edges per representation, zero
frontier, 36 distinguishing guard mutations and 4 calibrations. Inclusive and split reducers
and the separate relation agree. These totals sum declared environments; they do not
represent the full original Cartesian product. All results are modeled, not measured
runtime support or formal freeze.

The eight-action scaling core reaches 6823 states/12740 edges per cursor unit and applies
its ordered consumer suffix to every terminal. Scaling increases pending registrations,
retry and restart multiplicity to four, while preserving original attempts 1/2, A6/B6 pool 10,
and the full four-event 1, 2, 1, 2 schedule. Pending entries 3/4 are not extra literal admissions
or external executions. Explicit maximum-four mutations distinguish pending completeness,
stale-source fresh retry, and success overridden by a later start.

Independent challenge exposed a real common-mode fresh retry-conflict publication bypass:
without an existing receipt it could publish stale source bytes. Run-02 records its failing
positive assertion. Further guards now refuse a receipt used as an atomic start, negative
collection ordinals, and incomplete original intent registration. Run-03 records a separate
positive-test fixture failure caused by occupied delivery; the corrected direct foreign
attempt delivery is exercised by passing runs. No failed or superseded evidence was erased.

All ten admitted discovery runs retain exact source snapshots, admission and execution
receipts, stdout/stderr and any counterexample artifact. Run-06's stale usage observation
is explicitly superseded. Two failed process controls retain the Windows exit-accounting
race; bounded idle waiting fixes it. Accepted controls demonstrate normal exit, termination
of an owned parent plus descendant, and enforcement of a 64MiB test memory ceiling.
The model itself uses an owned 2GiB job, 600-second and 256MiB artifact limits. This process
containment does not turn Python's audit refusal into an operating-system sandbox.

Discovery stops early on evidence convergence. Both complete final gates and two independent
exact-candidate reviews remain publication conditions, with actual receipts stored externally
under the exact candidate. Each gate must rerun the combined model, containment controls,
16 frozen historical gates, 25 unchanged regressions and 16 adversarial gate corruptions.

Truthful registration outside this admitted boundary, physical durability and recovery,
orphan-reader reclamation, real external-effect outcomes, general authentication, runtime
or common-writer integration, and the complete original comparison remain open. All six
obligations and 27 trace rows preserve their complete prior support and residuals. The next
probe document is a proposal only. No additional campaign or operational change is active.
