# DS-08 — private canary methodology (synthesis)

## Provenance

- Raw: `raw/ds-DS-08-canary-methodology.md`.
- Session: Wave B Deep Research, self-contained handoff, run 2; retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Evidence classes preserved from the report: **source-documented** (the supplied DS-08 brief; Git, SLSA, OWASP and NIST documentation; mutation-testing literature), **inferred** (the protocol and boundary design), **locally observed** (only the no-start statement, scoped to the research session), and **unverified** (existence of an independent oracle).
- Privacy boundary: the report is alias-only. Only the alias `CANARY-01` is used; no real project identity, path, content, digest, transcript, private route identifier, or infrastructure identifier is reproduced here. All claims are attributed to "the report's sources"; no new facts or URLs are added.
- Scope: no canary ran; no private route was exercised; no candidate commit was created. No implementation, and no selected runtime, store, framework, or sandbox.

## The question

How should a first private canary be specified so that a passing result is meaningful and its evidence stays inside an alias-only boundary? The report treats `CANARY-01` as a capability-limited experiment against one frozen deterministic rule: it may alter tests and fixtures but not production code, it needs an independent clean rerun and failure injection, and it must not execute during the research campaign.

## Key findings

- **Sealed two-layer protocol (inferred).** A public/tracked layer carries only the alias, policy version, PASS/FAIL/UNKNOWN outcomes, classification, and non-sensitive verification claims. A separate private control layer resolves the alias to the real project, approved path classes, and a pre-existing approved route. The report's sources (SLSA verification-summary guidance) support communicating a verification decision without disclosing all pipeline details.
- **Double-enforced write boundary (inferred; Git source-documented).** Prevention makes the repository read-only except for privately configured test/fixture allowlists and ephemeral scratch space; detection machine-parses every changed, untracked, renamed, and type-changed path against a frozen baseline. Git's `status --porcelain` and NUL-delimited outputs are cited as stable, script-oriented primitives; `git diff --name-status -z` enumerates path/status changes. A post-hoc diff alone is weaker because the requirement concerns what the run was allowed to write, not only surviving version-control differences.
- **`WRITE_BOUNDARY_PASS` predicate (inferred).** Paths must be canonical, repository-relative, inside `ALLOW_TEST ∪ ALLOW_FIXTURE`, and never inside `DENY` (which always wins); only regular-file ADD/MODIFY content is allowed; DELETE/RENAME/COPY/TYPECHANGE/SYMLINK/SUBMODULE candidate operations and any recorded out-of-allowlist write attempt fail the run. Normalization, case-folding, or symlink ambiguity yields FAIL/UNKNOWN, never PASS.
- **Exactly one local candidate commit (inferred; Git source-documented).** After content gates and the independent rerun, the sole permitted non-test/fixture write is version-control metadata: one commit, one parent equal to the frozen baseline, tree equal to the independently verified candidate tree, and zero pushes/merges/publications/deployments. The commit hash stays private as a potential correlator.
- **Three baseline questions (source-documented + inferred).** The report refuses to conflate three separate checks:

  | Check | What a pass establishes | What it does not |
  |---|---|---|
  | Characterization | Frozen input reproduces the frozen observed behavior reproducibly. | That the behavior is correct. |
  | Independent oracle | Agreement with an owner-approved reference fixed before observation. | Correctness outside the tested cases. |
  | Contrastive sensitivity | The assertion can reject at least one deliberately wrong outcome. | Broad fault coverage or absence of overfitting. |

- **Anti-tautology rule (source-documented + inferred).** A characterization pass is not automatically a correctness pass; a golden-master test can faithfully freeze a pre-existing defect. Expected output should be fixed from an independently derived oracle before observing candidate behavior, and a deliberately wrong test-layer expected result must fail.
- **Independent clean rerun (inferred; reproducibility source-documented).** A separate reviewer/executor starts from the same frozen baseline, candidate tree, input, oracle, and environment but fresh mutable state; disagreement is a determinism failure, not an invitation to rerun until a pass appears. The report notes this is weaker than reproduction by independently operated build platforms.
- **Fail-closed route eligibility (inferred).** `ROUTE_ELIGIBLE` requires a pre-existing, active, in-scope private approval whose intended route is already covered, with no new provider/model/auth/config selection and no unapproved fallback. No route was exercised to establish eligibility; it is a policy predicate for a later authorized session.
- **Failure injection means detect and fail safely (inferred).** Malformed input, expected-output mismatch, runner/process crash, missing dependency, and stale state each have explicit expected/failure outcomes; none may be normalized into a successful business-rule result or a candidate commit.
- **Proposed gate sequence (inferred).** The report orders the runbook as private preflight → freeze baseline/input/oracle/policy → isolated writable test/fixture workspace → generate candidate → write-boundary gate → baseline plus contrastive verification → failure-injection matrix → independent clean rerun → independent review → exactly one local candidate commit → final boundary/disclosure check → bounded PASS/FAIL/UNKNOWN record.
- **Machine-readable run record (inferred).** The private control plane instantiates a frozen baseline revision, approved test/fixture prefixes, and a deny set before the run, while the tracked record carries only alias-safe fields: protocol version, baseline/input class, expected-output source, boundary/negative-control/injection/rerun verdicts, review outcome, route eligibility, candidate-commit-created flag, publication flag, and overall result.
- **Narrow boundary exception (inferred).** The only exception to "tests and fixtures only" is version-control metadata needed to create the single local candidate commit after all content gates and the independent rerun pass; it does not authorize modifying project configuration, hooks, remotes, credentials, or production content.
- **Disclosure classes and stop rules (inferred; OWASP source-documented).** Tracked/public, private operational, and private sensitive material are separated; the public form must exclude repository locators, paths, snippets, names, digests, commit IDs, transcripts, provider/model/account identifiers, credentials, and stable private-route handles. The report lists immediate stop conditions spanning disclosure, protected-path contact, ambiguous path classification, missing/ambiguous approval, fallback routing, unprovable oracle provenance, insensitive negative controls, ambiguous execution state, rerun disagreement, unverified PASS evidence, and any push/merge/deploy/publish attempt.
- **Bounded proof statement (inferred).** A pass can support only that the executor operated on one pre-approved deterministic rule under the specified boundary; the candidate was test/fixture-only; defined negative controls and failure conditions were detected; a separate clean execution reproduced the declared result; independent review accepted the evidence; and the final artifact remained local.
- **Session attestation (locally observed, this session only).** `CANARY-01` did not start, no private repository was accessed, no route was exercised, and no candidate commit was created. The report recommends the trusted control plane generate this assertion from session events rather than the canary worker self-certifying it.
- **Preventive stronger than detective (inferred).** A Git-diff-only boundary is weaker than filesystem enforcement because the specification concerns attempted/permitted writes, not merely surviving version-control differences; the detective layer should therefore supplement, not replace, least-privilege prevention.
- **External sources used as references, not proof (source-documented).** NIST's SSDF is used as a general secure-development reference rather than evidence that this particular canary is secure, and the report notes SP 800-218 v1.1 is final while v1.2 is an initial public draft.
- **Logging and secrecy discipline (OWASP source-documented).** Logs and tracked artifacts should avoid source code, tokens, credentials, and higher-classification material; file paths can themselves require special handling, and secrets should be least-privileged and never logged in plaintext.
- **Unknown is not zero (inferred).** Facts deliberately unavailable behind the privacy boundary — for example secrets, flaky dependencies, or protected-path hazards in the private project — must be recorded as `unknown until privately verified`, never as false or absent.
- **Completion-gate assessment (inferred; locally observed for this report).** The report marks its alias-only reference, machine-checkable boundary specification, rerun/failure-injection specification, no-start attestation, route-eligibility statement, and proof/non-proof separation as satisfied, while qualifying that it is not a repository-level secret scan.

## Recommendation and falsifier

The report recommends the sealed two-layer protocol: preventive test/fixture-only filesystem enforcement, a complete machine-readable write audit, an independent-oracle label, a mandatory contrastive sensitivity test, all five failure injections, a separate fresh-state rerun, and independent review before exactly one local candidate commit. The named competing option is a lighter post-hoc Git-diff gate in an ordinary writable checkout; the report argues it answers a materially weaker question because it cannot establish the absence of transient, ignored, out-of-tree, or reverted writes, oracle sensitivity, or clean-state repeatability.

The decisive falsifier is a controlled red-team exercise in which the protocol reports PASS despite any of: a write escaping into a protected path; a real project or route identifier reaching tracked/public output; an intentionally wrong oracle passing; a crash or missing dependency normalized into success; planted stale state changing the result undetected; or an independent fresh rerun disagreeing while the overall verdict still passes. Any such event blocks the canary.

## What this does not prove

- Even a full pass proves only the tested pipeline slice for one frozen rule under one constrained execution context; not correctness of the production rule (absent an independent oracle), general migration correctness, security, exhaustive fault coverage, route reliability, release readiness, or Recursion-wide conformance.
- The existence of an independent authoritative oracle for the chosen private rule is unverified; without one the report can only claim characterization.
- The report is not a secret scan of the unseen private repository; repository-level privacy remains a mandatory canary-time preflight.
- The no-start statement is a locally observed fact about this research session only, not evidence about any other actor.
- No canary was authorized, and the correct state is "not-ready-to-run," not an inferred PASS.

## Open Owner decisions

- Which privately configured logical prefixes instantiate `ALLOW_TEST`, `ALLOW_FIXTURE`, and `DENY` for `CANARY-01`?
- What source is authoritative for the deterministic rule's expected output?
- What operationally qualifies as "independent" for the clean rerun: a distinct bounded worker on the same machine, or an additional isolation requirement?
- What private retention/access policy governs route-approval evidence, sanitized audit events, and the local candidate revision?
- Is the candidate commit retained on an isolated local ref after evaluation, or deleted after acceptance/rejection?

## Relevance to later waves

This lane is a gate-shaping input for the later authorized canary session and for any verifier-independence or migration work: it separates characterization from correctness, supplies a machine-checkable write-boundary predicate, and defines the failure-injection and stop conditions a real run must instantiate with private values. Later waves consume these as criteria and fixtures — not as evidence that any canary has run or passed, and not as authorization to execute.
