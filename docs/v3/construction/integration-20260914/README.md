# Combined v3 construction review â€” 2026-09-14

Parent: goal-recursion-v2-execution-fabric. Product target: Recursion v3. This integration session reconciles the three handoffs Lucas returned for PR synthesis and the next external fleet work. External agents research, develop and test ON the product.

Working branch: codex/v3-integration-20260914, separate worktree C:/r3i. TASK_BASE is 0c908f6833e715af0eaa01b6f6788120eb577efd. The manifest pins the three reviewed candidate commits, their trees and exact file inventories. Their 18 additions are disjoint and were combined without editing any imported file. Only the five files in this integration directory are newly authored.

The original scoped gates remain unchanged. In particular, the recovery gate requires its original branch and five-path diff, and the delegated-Q gate requires its original seven-path diff. They intentionally reject a combined tree. Intake reran their gates on the exact original candidates and retrieved the independent reviewers' final verdicts directly. The manifest binds archived intake evidence by SHA-256; this is provenance for reviewed local work, not a canonical acceptance seal or scientific grant.

Run the new composition gate from a clean native Linux clone of the exact integration commit, inside the D: WSL VHDX. A Windows worktree's absolute Git administrative pointers are not a Linux clone. Transport a bundle without changing its refs or candidate bytes; retain original Windows worktrees.

```text
python3 -X utf8 -B docs/v3/construction/integration-20260914/check.py --candidate FULL_SHA --evidence-root EXTERNAL_INTAKE_DIRECTORY --output FRESH_EXTERNAL_DIRECTORY
```

The local intake directory is D:/RecursionSwarm/integration-v3-20260914/combined-inputs-1789416331147, accessible as /mnt/d/RecursionSwarm/integration-v3-20260914/combined-inputs-1789416331147 in WSL. Copy its eleven manifest-pinned files together for another host; missing or altered evidence fails. Preserve Git history, including all three original candidates and the ledger's frozen-expectation commit. Keep the native clone under <repo>-foundry and gate outputs under /var/lib/recursion-foundry; exported evidence may be copied to D: outside the VHDX. The observed Ubuntu-24.04 distro is installed at D:/WSL.

The gate requires exact HEAD, clean checkout, unchanged baseline, original ancestry/tree pins, the exact additive union and matching actual source bytes, including files hidden by Git index flags. It tests four synthetic composition refusals. It reruns the preservation check, 18 P1 cases, 19 WSL P2 cases, the ledger's independent prefix/mutation/component/reset audits and test subprocess, and DQ's exact prospective plan/fake controls. All source/evidence bindings are checked again afterward. No original gate is monkeypatched or reclassified.

Only source composition and the selected inert behavior are covered. The new gate's two component-only modes emit COMPONENT_CHECK_PASS, never integration acceptance. Original standalone gate evidence does not approve a changed combined SHA. Obtain independent review of the final composed commit and preserve that verdict externally.

Draft d5536be was rejected in code review before a full combined run: its direct subprocess timeout could leave descendants and lose partial output. That draft remains in history. The correction requires native Linux ownership, streaming output bounds, partial failure logs and a short descendant cleanup control; no prior successful source or component receipt is relabelled as approval of that draft.

Each P2 command remains bounded to 120 seconds; each other selected command to 60 seconds, retaining the packets' local fixture limits. Run under Linux so the integration runner owns the command sessions, can retain bounded partial output and can verify cleanup, including children that create another process group. A short inert timeout control must retain failure and descendant-cleanup evidence. These test boundaries are not scientific accounting admission or actual-host lifecycle qualification. No inference or inherited scientific state exploration is introduced.

Read [PR-PLAN](PR-PLAN.md) for prerequisite publication order and [NEXT](NEXT.md) for the next parallel assignments. GitHub master was freshly observed at 8568b8a on 2026-09-14, with no open PRs; TASK_BASE contains 20 unpublished prerequisite commits. Do not silently omit them or reinterpret this dated observation as future live status.

P1 remains a fake canonical-boundary candidate; P2 has a read-only fixture adapter; the recovery ledger is inert product accounting; DQ-16 is unexecuted. Their composition does not activate a service, implement a live canonical adapter, demonstrate real consumption admission or finish P2â€“P8. No configuration, credentials, model routing, startup policy, PAUSE, publication or default-branch merge is changed by this integration.
