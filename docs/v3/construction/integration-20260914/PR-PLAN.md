# Review-branch publication order

Fresh observation: GitHub master 8568b8a4e95171803cf126ce417cdfd775a71eb4, zero open PRs. The common source 0c908f6833e715af0eaa01b6f6788120eb577efd is 20 commits ahead and contains 29 new files. These prerequisite commits must be included before the three handoffs can be merged.

Prepare these requirement-sized review changes:

| Order | Existing local source | Proposed title | Scope |
|---|---|---|---|
| 1 | codex/v3-next-packets-20260914 at 0c908f6 | Establish repaired P1 and verified v3 construction baseline | P1 implementation/repairs, completed external wave evidence and v3-preserving handoffs; 29 additions against observed master. |
| 2, parallel after 1 | codex/p1-readonly-service-20260914 at 7111669 | Add authenticated read access for external v3 construction | Six access/CLI/MCP/test/document files. |
| 3, parallel after 1 | codex/v3-recovery-reservation-ledger-20260914 at f64c5bd | Model cumulative recovery reservations and reset reconciliation | Five inert product experiment/test/document files. |
| 4, parallel after 1 | codex/v3-delegated-q-coupling-20260914 at 8fa7e2c | Add prospective delegated-Q coupling checker and auditor | Seven source/fake experiment files; DQ-16 explicitly unexecuted. |
| 5, after 2–4 | codex/v3-integration-20260914 at final reviewed HEAD | Validate composition and record the next v3 fleet work | Five integration files after predecessor diffs are present. |

The last source includes local merge commits retaining every reviewed origin. Those are review-branch merges only. Lucas performs GitHub/default-branch merges. Re-fetch and compare the actual base before opening or retargeting each PR; if the base moves, rerun relevant composed checks and review. Do not assume a squash preserves original ancestry: the pinned source candidates and receipts must remain available, while the current acceptance gate remains tied to the reviewed local composition.

Description drafts:

1. The reviewed P1 fixes and completed external research wave existed only in local worktrees, leaving later tasks based on unpublished prerequisites. This change publishes that source/evidence baseline while preserving the v3 specifications and explicit limits on service readiness. Validation: prior exact-candidate P1 and external-wave receipts plus the specification-preservation audit; it establishes neither a live canonical integration nor unattended operation.
2. Independent clients can inspect bounded project-scoped construction views through an authenticated Unix-socket service, CLI and stdio MCP bridge. Reads preserve freshness, replay-gap, artifact-integrity and disconnected-cache boundaries. Validation: 19 WSL process/socket cases, 18 P1 regressions and independent Astra review; actual application interoperability and host lifecycle remain unqualified.
3. The recovery experiment preserves cumulative charges and unknown reservations across successor boundaries and reset reconciliation. Literal outcomes and independent mutation/component/reset checks cover the selected inert domain. Validation: 16 test methods, 21 prefixes, six behavioral mutations, three component and three reset guards; no physical durability or live spending claim.
4. The candidate defines DQ-16's sixteen histories/560 paired prefixes and implements a checker, independent auditor and falsifying controls. Validation: exact source preflight, 40 negative controls, three valid fixtures and two independent reviews. Scientific execution remains disabled pending controller/accounting integration and a fresh finite admission.
5. The integration binds unchanged bytes from all three reviewed candidates, preserves their original scoped gates and reruns selected behavior in one clean source tree. The accompanying roadmap separates external construction-service work from v3 product experiments. Validation must cite the final combined SHA and its external gate/review receipt.

Publishing uses the repository's existing approved publisher route. scripts/publish.sh requires a canonical loop/work task ref, an active registered clone, a passed canonical task, configured publisher key, push permission and no PAUSE. This document does not create registry state or satisfy those operational conditions. Existing codex/ refs are source references, not an exception to the publisher rule. The earlier Windows exception covered one different branch only.

Read-only SSH observation on 2026-09-14 confirmed that gs-recursion's /opt/recursion/state/PAUSE exists and its publisher script is present. Publication is therefore blocked through that route; this session has not changed PAUSE or push flags. The prior branch-specific Windows exception does not cover these five refs. A new explicit bounded exception or an authorized publisher-state change is required before publication. Do not infer either from a review PASS.

No PR has been opened by this local integration. Prepare exact review refs/bundles and descriptions before any publication approval or publisher action; never bypass the route, change autonomy flags, raw-push or merge on Lucas's behalf.
