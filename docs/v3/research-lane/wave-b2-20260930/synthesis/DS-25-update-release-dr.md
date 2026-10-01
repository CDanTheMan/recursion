# DS-25 — Update, release, rollback and DR (synthesis)

## Provenance

- Raw report: `raw/ds-DS-25-update-release-dr.md`.
- Labelled a self-contained handoff for Wave B Deep Research, run 2; retrieved 2026-09-30.
- The report states its own research cut-off as 2026-10-01.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun performed.
- The report treats the supplied DS-25 directive as the controlling requirements baseline and triangulates against "the report's sources": primary standards, official security guidance, current supply-chain specifications, industry architecture guidance and peer-reviewed work.
- Evidence classes mirror the report: **locally observed** (in the supplied brief, not running software), **source-documented**, **inferred**, and **unverified**.

## The question

The DS-25 brief covers update modes, release identity, activation receipts, migration, rollback,
backup/restore and disaster recovery for Recursion v3. The report's framing question is what
contract makes update and recovery claims falsifiable and keeps software rollback, state
recovery, history readability, newest-work preservation and task resumability from collapsing
into a single "recovered" status.

## Key findings

- **Five different propositions.** The central finding is that a working executable, readable
  history, preserved newest work and resumable tasks are separate outcomes and must never share
  one "recovered" bit; restoring an old executable does not reverse an already accepted external
  effect. The brief is classified as locally observed; public sources corroborate the separation.
- **Release identity is multidimensional.** SemVer is **source-documented** as encoding declared
  public-API compatibility only, so it cannot carry protocol, schema, policy, build-provenance,
  dependency-lock, SBOM or edition-manifest compatibility. The report proposes a structured
  `ReleaseId`.
- **Reference security properties, not selections.** The report uses TUF-style metadata
  (no version regression, no trusting expired metadata), SLSA v1.2 provenance verification, and
  deterministic SPDX 3.0.1 canonical serialization as properties to require. It does not select a
  signing stack, updater or channel. This is source-documented plus design inference.
- **Reproducible builds have a bounded claim.** Bit-for-bit reproducibility is
  **source-documented** as source/build-input-to-artifact correspondence; it does not establish
  semantic safety, migration correctness, effect reversibility or task recovery.
- **Configuration publication should be compare-and-set.** Expected-revision writes, with a
  rejection that mutates nothing on a stale revision, model RFC 9110 `If-Match` lost-update
  protection. Two receipts are required: `ConfigAcceptedReceipt` proves canonical acceptance only,
  `ConfigAppliedReceipt` proves a specific runtime or session adopted the revision. The split is
  an inferred specification.
- **Six update modes must be observably different.** Mode 2 stops the tasks current at admission
  but may reopen ordinary post-landing scheduling; Mode 6 maintains a global hold after landing
  until a separate authorized release-of-hold. That distinction is **inferred** (medium-high) and,
  in the report, not yet demonstrated by a fault trial.
- **Lifecycle receipts and per-host landing.** Candidate received, staged, eligible/quarantined,
  promoted, activated, landing-observed is proposed as a non-skippable lifecycle; an
  `ActivationReceipt` without a matching `LandingObservation` is `activation_unlanded`, and a host
  bearing an unreachable release identity is `unknown_release`. Partially activated fleets are
  represented as an explicit per-host map rather than rounded up.
- **Migration uses expand/contract.** Additive expand, dual-read, frozen legacy import, backfill,
  shadow comparison, atomic cutover and contraction, with exactly one canonical writer. Forward-only
  boundaries are real/ambiguous external effects, destructive contraction without a verified
  reverse migration, an N+1-only checkpoint/event an older release cannot decode, and a
  policy/constitution change that removes authority. Schema guidance is source-documented; the
  protocol is locally observed plus inferred.
- **A backup is not consistent merely because files copied.** The report requires a
  `SnapshotReceipt` binding state/event high-water, checkpoint digest, schema epoch, immutable
  artifact set and consistency evidence. With an active writer the exact mechanism is
  **unverified until a storage engine is selected**. CISA's offline/encrypted, regularly tested
  backup posture is source-documented and used as corroboration only.
- **Key exclusion and fresh-host restore.** The backup may carry public trust roots and credential
  references, not live provider tokens, private signing keys or runtime credentials; restore
  grants canonical writer authority only after verification. The report supplies a restore
  procedure specification, not a performed restore.
- **Fault injection at every boundary.** Torn write, disk full, process death, duplicate delivery
  and stale lease/fence are given expected dispositions across staging, activation, backup and
  restore; empirical pass/fail remains unknown.
- **No numeric recovery objectives.** The report invents no RPO/RTO, support window or emergency
  deadline; these remain unknown until measured or Owner-decided. RPO is framed in event-space
  high-water terms to avoid equating unknown work with zero.
- **Nothing was executed.** No implementation, rollback or restore trial was authorized or run;
  the six-mode by four-outcome matrix is deliberately `unknown` in every cell. A "full recovery"
  report from process startup alone fails the contract.

## Recommendation and falsifier

The report recommends, as an **inferred** starting disposition, verified compatible executable
rollback while retaining the newest canonical state/history, followed by either verified task
resume or an explicit hold. This is conditional, not universal. The principal competing option is
**repair-forward**; **separate-instance restoration** is preferred when the original host or state
environment is suspect, and must remain noncanonical until parity and fencing are proven.

The decisive falsifier: a controlled trial in which the retained release is authentically valid
and executable but cannot reproduce the newest canonical state/history, cannot interpret a current
task checkpoint, would discard accepted work, or would duplicate/contradict an already
real-or-ambiguous external effect. Such a result removes that release/state pair from the
compatible-rollback class; a successfully starting process does not defeat the falsifier.

## What this does not prove

- No implementation, migration, rollback or restore trial was run; the four-outcome matrix is
  entirely `unknown`.
- No storage engine, packaging format, signing/trust stack, update channel or SBOM tool is
  selected, so engine-specific snapshot and fencing behavior is unverified.
- Bit-level reproducibility is not evidence of semantic safety, migration correctness or recovery.
- The Mode 2 versus Mode 6 distinction, the expected-revision rejection behavior, and the receipt
  model are proposals, not runtime-verified properties.
- No numeric RPO, RTO, support window or emergency deadline is established.
- Public-source claims are documentation-qualified, not observed against a live Recursion system.

## Open Owner decisions

The report explicitly leaves these to the Owner: storage engine; packaging format; signing/trust
stack; update channel; SBOM-generation tool; default configuration propagation policy
(`outstanding_sessions` versus `new_or_isolated_only`); exact semantics and scopes of the three
referenced Stop modes; release-promotion authorization/quorum; normal support windows; emergency
update deadlines; retained-slot count/retention policy; and numeric RPO/RTO objectives after
empirical measurements.

## Relevance to later waves

- Supplies a candidate update/release/DR contract against which later implementation can be
  falsified, without ratifying any component choice.
- Establishes that acceptance must measure history readability, newest-work preservation and task
  resumability independently of executable startup — a reusable gate pattern for later work.
- Reinforces the separation between source/build authenticity and state recovery, and between
  local software movement and external-effect reality, for any later recovery or rollback design.
- Flags receipt/landing observation and expand/contract migration invariants as preconditions that
  later architecture must satisfy or explicitly amend.
