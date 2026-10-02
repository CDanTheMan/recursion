# Recursion capability composition research

Research handoff for Lucas and the local Recursion sessions, 2026-10-02.

**Revision 2:** replaces the first delivery with the corrected R-UI candidate-2 identity contract and matching R-MOB reference. See [correction notes](CORRECTIONS.md). The separately requested OS-specific design and language expansion is not part of this correction.

This packet serves D-034, “the harness that scales with your workflow,” through three specification candidates. It extends the shared-contract, orchestration and prompt/skill research already incorporated in the repository. It is not an implementation or a patch to accepted decisions.

## Source basis

All three reports use master commit `b696f6ece243b48c94fc0bbc7ee1d4b284c46f97`, tree `a866969c9346372dcf74c2f05a7f9d648c766494`. This includes PR 149's merge `e2e02af1712de8fc388883bc65c150ad1138ee96` and the subsequent PR 148 merge. The read-only tracked-source export verified 1,401 files and 196 Git trees. All five files in the supplied research packet matched this source exactly.

## Reports

1. [R-PC Prompt and context composition](rpc/report.md): exact compiler inputs and read cuts, mandatory closure, immutable prompt and provenance artifacts, current-right checks, conflict handling, cache limits, and fixed-budget capability-increment experiments
2. [R-UI Capability-driven UI projection](rui/report.md): typed contribution points, deterministic semantic materialization, host-owned safety controls, accessible fallback, ten-control and three-Stop parity, and bounded contribution/view experiments
3. [R-MOB Mobile and remote control](rmob/report.md): device pairing and authentication candidates, connected-only controls, offline-view limits, push semantics, detach continuity, distribution questions for counsel, and optional direct/Tailscale/SSH/WireGuard connection comparisons

Each report contains candidate contracts, real competing designs, falsifiers, explicit non-proofs, question/gate coverage and a bounded provider-free handoff. The handoffs specify later tests; they are not runnable scripts or executed results.

## Shared design boundary

The prompt compiler, UI materializer and mobile client consume authorized, versioned projections of the same backend facts. They do not become additional writers or permission sources. Connection plugins change how a client reaches the backend, while current authorization, canonical commands, receipts, accounting and Stop remain Recursion responsibilities.

Mobile remote control requires a live authenticated backend connection. An always-on Linux deployment can preserve backend work through phone detach, but cannot guarantee phone connectivity. Disconnected views never automatically execute queued actions later. A previously submitted command with an uncertain result requires receipt reconciliation, not blind resubmission.

Private offline-content retention is still an explicit policy choice. The reports compare minimal authorized offline status with separately approved bounded private snapshots. Neither can promise that an offline device instantly learns a remote revocation or erases bytes already disclosed.

## Local next steps

- Reconcile any newer repository commit against the pinned inputs before implementation
- Review the candidate contract choices and unresolved policies without treating report completeness as Owner adoption
- Implement independently checked controls and negative vectors for the composition, UI and mobile seams under separate bounded local tasks
- Keep contribution count, client/view count, fixed aggregate resources and complete assigned-task cohorts explicit; do not hide a quality, latency or authority regression behind another improvement
- Separate synthetic accounting/control tests from actual model quality, human review effort, mobile battery, platform isolation, connectivity performance and store-policy qualification
- Bring back exact source/candidate identities, observed results and unresolved evidence for the next reconciliation

## Evidence boundary

Only static source/public-document research and deliverable checks were performed. All target runtime, performance and model-quality tests remain **UNEXECUTED**. No Work/Codex sessions, model/provider calls, credentials, installs, network configuration, account/live-host actions or counsel contact were used. No language, store, framework, renderer, transport, authentication mechanism, push provider or vendor was selected.

The archive contains only these three reports, this reading guide, correction notes and file checksums. It excludes source snapshots, private working records, raw captures and generation or test code. `SHA256SUMS.txt` identifies the delivered bytes.
