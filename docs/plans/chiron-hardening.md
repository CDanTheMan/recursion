---
title: "Chiron lane hardening — review of the Hermes agent's findings + plan"
type: plan
status: current
last-verified: 2026-08-05
related:
  - "docs/autonomous-loops-architecture-and-roadmap.md"
  - "state/roadmaps/chiron.md"
  - "golden-stallion-client/docs/loop-arm-contract.md"
---

# Chiron lane hardening

The Telegram/Hermes agent proposed 6 steps to harden the Chiron lane before turning autonomous
continuation loose. **Its diagnosis is correct and matches our discipline** (autonomy rests on the
acceptance gate, not trust). Chiron is at 2/5 roadmap items; the 3 remaining are trivial static pages
gated only by `npm install && npm run build` — i.e. "it compiles", not "it works". Continuing like
that manufactures review backlog, exactly as the agent said.

## ★ The key insight: Chiron hardening IS the GSC prep pattern

What we just built to make **GSC** loop-drivable is the same shape Chiron needs. Reuse it:

| GSC (built) | Chiron equivalent (to build) |
|---|---|
| four-lane plan (narrative source of truth) | **PRODUCT.md** (product contract) — *point 1* |
| `docs/gaps.json` + `tools/gaps.cjs` (machine-readable, dependency-aware, lane-tagged) | **feature ledger** (`features.json` + query CLI; vertical slices, non-goals, deps) — *point 2* |
| `native-diff --metric` (a REAL gate, sum-not-total) | **browser-level acceptance** (render + key elements), not just `npm run build` — *point 3* |
| the gate judges, arm never self-scores | **independent reviewer lane** (2nd agent checks diff/coverage/UI) — *point 4* |
| green = reviewable branch, no auto-merge | **merge policy**: trivial-scoped-green → auto-merge; subjective/arch → compact review packet — *point 5* |
| conduct.sh concurrency cap + per-workstream locks | **WIP cap** (1 implementer + 1 reviewer + 1 audit) — *point 6, mostly DONE* |
| "don't widen PLAN_WORKSTREAMS until a proven shakedown" | same: don't re-arm chiron auto-plan until the layer is proven |

## Point-by-point status

| # | Point | Status | Effort | Notes |
|---|---|---|---|---|
| 1 | Product contract (PRODUCT.md) | **NEW** | S | The missing task-definition layer that let chiron-002 reinvent the app. Highest leverage. |
| 2 | Feature ledger (slices + non-goals + deps) | **NEW** | M | Reuse the `gaps.cjs` pattern. Dependency-aware ⇒ a slice bases on merged deps (fixes the base-branch failure). |
| 3 | Executable acceptance (browser-level) | **PARTIAL** | M–L | Biggest lift. Headless check (Playwright/Puppeteer) asserting the built page renders + key elements. ⚠ capacity: chromium ~300MB disk + ~200–400MB RAM/run. |
| 4 | Independent reviewer lane | **NEW** | M | A cheap `claude -p` reviewer arm as a 2nd gate stage (reads diff, coverage, UI). Light on resources (no build). |
| 5 | Merge policy (trivial→merge / subjective→packet) | **PARTIAL** | S | Have path-scoped ff-only auto-merge; add the trivial-vs-subjective classifier + a review-packet escalation. |
| 6 | Capacity control (cap WIP) | **DONE** | — | conduct.sh concurrency cap + per-workstream locks (shipped today) + 2G swap added. The stage pipeline (impl→review→audit) is the remaining bit, folded into points 3–4. |

## VPS capacity verdict (Lucas's concern)

Box: **2 cores, 3.7 GB RAM, +2 GB swap (added today, swappiness=10), 28 GB free disk, load ~0.5.**

**Yes, the box can run the proposed model** — but the constraint is GATE weight, not agent count:
- **Arms are remote-API-bound** (`claude -p`, `delegate.py` call remote models and mostly WAIT). "1
  implementer + 1 reviewer + 1 audit" is ~zero local CPU while they wait; agent *count* is not the
  limit. The reviewer + audit do no build — they are light.
- **The heavy part is the gate**: `npm install && npm run build` (RAM-heavy, ~1–1.5 GB), a browser
  check (chromium ~200–400 MB), `node --test` (CPU). Only ~1 heavy gate runs per workstream at a
  time. Two workstreams (chiron + gsc) could overlap two heavy gates ≈ 2–2.7 GB — tight but under
  3.7 GB, and **swap now cushions any OOM** (the real prior risk: 0 swap ⇒ OOM-kill, not slowdown).

**Guardrails to keep it safe:**
- Keep `RECURSION_CONDUCT_CONCURRENCY=2` (default). Agents are cheap; don't chase more.
- If browser gates + npm builds start overlapping, add a **gate-concurrency lock** (serialize heavy
  gates independent of arm concurrency) rather than raising RAM.
- Watch `free -m` / OOM logs during the first browser-gate runs; the swap is insurance, not a plan.

## Recommended sequence (harden before re-arming chiron auto-plan)

- **Phase A — task-definition layer:** PRODUCT.md (1) + feature ledger (2). Unblocks coherent tasks.
- **Phase B — acceptance layer:** browser-level acceptance (3) + merge-policy classifier (5).
  Unblocks trust (build≠works closes).
- **Phase C — review layer:** reviewer arm (4) as a second gate stage. Unblocks autonomy.
- **Phase D — re-arm:** WIP cap (6, mostly done) + a supervised shakedown (one slice end-to-end with
  the new gate + reviewer) before letting the chain run unattended — exactly the GSC shakedown rule.

## Recommendation on chiron auto-plan NOW

`AUTO_PLAN=1` + `PLAN_WORKSTREAMS="chiron"` is armed; the next tick would queue the `/learn` page with
a build-only gate. Options:
- **(a) Pause chiron planning** (narrow `PLAN_WORKSTREAMS` to empty, or `AUTO_PLAN=0`) until at least
  Phase B lands, so no more build-only-verified pages ship. **Recommended** — matches the agent's
  advice and "develop properly".
- (b) Let the 3 trivial static pages finish (harmless, scoped auto-merge) then harden before adding
  any NEW slices.
Either is a human flag change (rule 3) — I will not flip it unilaterally.
