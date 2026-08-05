# Decision log

Every decision gets a falsifier — the specific thing that, if observed, means this was
wrong. Without it, review is hindsight.

**Review cadence:** first of the month. Pull decisions ≥60 days old, check whether the
falsifier fired, mark `HELD` / `FAILED` / `UNCLEAR`. Do not edit the original entry.

---

## Template

```
## D-00N — <the call>
Date: YYYY-MM-DD · Status: OPEN
**Options considered:** A / B / C
**Chose:** X
**Because:** one or two sentences
**Falsifier:** if <specific observable> by <date>, this was wrong
**Review:** YYYY-MM-DD
```

---

## D-001 — Single harness; Claude Code + cron, no Hermes or OpenClaw supervisor
Date: 2026-08-04 · Status: OPEN

**Options considered:** Hermes on the VPS as supervisor / OpenClaw / `claude -p` on cron /
two harnesses coordinating quotas

**Chose:** One harness. Claude Code for build, `claude -p` on cron for the supervisor.
OpenClaw already removed from the Windows machine.

**Because:** Anthropic blocks third-party harnesses on subscription auth, but headless
`claude -p` is first-party and subscription-covered — so the original reason for a separate
harness disappeared. Two frameworks means two configs, two auth stores, two silent failure
modes. Cross-harness quota negotiation depends on undocumented internals and fails silently.

**Falsifier:** if by 2026-09-15 cron + `claude -p` can't do scheduled supervision reliably
— missed runs, no usable state handoff between runs, brittle scripting eating more time
than it saves — a real harness was the right call.

**Review:** 2026-09-15

---

## D-002 — Add ChatGPT Pro for August; single-month proof of concept
Date: 2026-08-04 · Status: OPEN

**Options considered:** Max only / Max + cheap OpenRouter leg (~$25) / Max + ChatGPT Pro
($400 total)

**Chose:** Max + ChatGPT Pro, month-to-month, for August only.

**Because:** August is the highest-available-hours month before Berkeley starts — the
correct window to test the parallel-development ceiling. A week of "held up fine" without
fully leaning in is not a ceiling test. Reversible in both directions.

**Falsifier:** if by 2026-09-01 `ccusage` shows nowhere near capped while running full
parallel, the constraint was never tokens — it was review throughput, and the second
subscription bought nothing. Equally wrong if limits were hit but merged-and-verified
output didn't track generated output: that's a purchased backlog.

**Review:** 2026-09-01 — see kill criteria in `ANCHOR.md`

---

## D-003 — Projects push status into Recursion; Recursion does not read product repos
Date: 2026-08-04 · Status: OPEN

**Options considered:** supervisor gets read access to golden-stallion and CSL Labs repos /
each project writes `STATE.md` and pushes a copy here

**Chose:** Push model.

**Because:** keeps blast radius small if the loop misbehaves, and adding a fifth project
is one file rather than new credentials and permissions.

**Falsifier:** if by 2026-10-01 the pushed state is routinely stale enough that the
supervisor's briefs are wrong, the copy step is too much friction and direct read access
was correct.

**Review:** 2026-10-01

---

## D-004 — No community-extractive monetization for Golden Stallion
Date: 2026-08-04 · Status: OPEN

**Options considered:** in-game market manipulation / sponsorship + premium client tier +
Gilded Republic subscription ladder

**Chose:** Non-extractive paths only.

**Because:** ruled out on Republic values. Separately: a community project that extracts
from its own community has a ceiling measured in months and destroys the asset that
actually has value — the reconstructed client and the reputation around it.

**Falsifier:** none accepted. This is a values constraint, not an optimization.

**Review:** n/a

---

## D-005 — GSC-first sequencing, driven by the August game-update clock
Date: 2026-08-04 · Status: OPEN

**Options considered:** learning-loop first (ANCHOR's original priority — Berkeley 2026-08-26) /
GSC engine first / fleet-first

**Chose:** GSC (client reconstruction) first.

**Because:** ANCHOR treated the learning loop as the only external clock. There's a second, sharper
one — the CC devs' planned August update. An update drifts WASM indices / offsets / struct layouts
(the vault is full of "18 stale indices", "a stale export = the wrong fn under a trusted name") and
can make version-differentiation harder — invalidating hard-won RE and the current full-item captures
as ground truth. Berkeley learning is absorbable alongside classes (interactive, foreground), so it
doesn't need the 3-weeks-ahead lead ANCHOR assumed. GSC is background/autonomous (oracle-gated), so
the two parallelize rather than compete for attention.

**Falsifier:** if the update lands and the reconstruction wasn't at a usable checkpoint against the
stable binary, we mis-sequenced (should have started sooner / raced harder). Equally wrong if
GSC-first let the learning loop slip behind Lucas's actual classes.

**Review:** 2026-09-01 (with the other kill criteria).

**Note:** amends ANCHOR's "priority is the learning loop" premise. ANCHOR's next scheduled review is
2026-11-01, but this is a same-day amendment — carry it into the 2026-09-01 review.

---

## D-006 — Adopt Hermes on the loop box, running on the ChatGPT sub via Codex OAuth (amends D-001)
Date: 2026-08-04 · Status: OPEN

**Options considered:** `claude -p` on cron (D-001's choice) / thin custom dispatcher + OpenRouter /
Hermes (`NousResearch/hermes-agent`) with OpenAI Codex OAuth + OpenRouter fallback

**Chose:** Hermes on `gs-recursion`, primary = ChatGPT Pro via Codex OAuth, fallback = OpenRouter.

**Because:** D-001 rejected a third-party harness on the premise "subscription auth is blocked" —
which is true for **Anthropic**, but **not** for OpenAI. Verified 2026-08-04: Hermes runs on the
ChatGPT subscription via **Codex OAuth** (GPT-5.x, not metered API) with an automated
`fallback_providers` swap to OpenRouter on quota/rate-limit/error. This runs the 24/7 loop on the
$200 sub without burning the soon-halved Claude weekly limit, and Hermes' management surface is the
single control front Lucas wanted. Claude `claude -p` stays an optional heavy tier, off the 24/7 path.

**Falsifier:** if OpenAI restricts Codex OAuth in third-party harnesses (or rate-limits it below
usefulness), Hermes-on-subscription stops working — but the fallback chain already degrades it to
OpenRouter, so the failure is absorbed, not fatal. Equally wrong if silent auto-fallback runs up a
metered OpenRouter bill unnoticed → mitigated by `fallback_threshold_per_day: 3 → notify`.

**Review:** 2026-09-01 (with the capacity kill criteria).

**Note:** supersedes D-001's "no Hermes" conclusion *for the OpenAI side only*. D-001's core point —
never run two harnesses fighting over one auth store — still holds: Hermes owns the loop, `claude -p`
is invoked as a tool, not a second supervisor.

---

## D-007 — Confirm ChatGPT Pro (Codex OAuth) + Claude Max for the August PoC; SuperGrok/Cursor set aside
Date: 2026-08-04 · Status: OPEN

**Options considered (since D-006):** dual SuperGrok Heavy (verified OAuth via OpenCode/Hermes) /
Cursor Ultra ($200 → $400 credits, Grok incl.) / stay on ChatGPT Pro (Codex OAuth) + Claude Max

**Chose:** ChatGPT Pro via Codex OAuth (loop) + Claude Max (interactive) — one-month August PoC,
reassess Sept 1. Confirms D-006.

**Because:** SuperGrok Heavy was genuinely strong (official xAI↔OpenCode integration, subscription
OAuth, Grok 4.3 / 1M ctx) but the $100 promo expired → $300/mo, no longer worth it. Cursor Ultra is
good value but its credits lock to Cursor's own tools (cursor-agent), forcing a harness switch off
OpenCode/Hermes and unable to reach the local GSC oracle. ChatGPT Pro via Codex OAuth already runs
headless in the Hermes we stood up, is exactly $200, and matches ANCHOR's August-PoC budget. Lucas
chose to run it this month on the increased budget, then make a reformed decision.

**Falsifier:** if the Sept-1 `ccusage` review shows the loop never approached ChatGPT-Pro limits (a
$20 Plus or OpenRouter-only would have sufficed), the $200 was over-bought. Equally wrong if
merged/verified output didn't track generation — a purchased backlog (ANCHOR).

**Review:** 2026-09-01 (with the capacity kill criteria).

**Note:** OpenCode stays installed as an available coding agent (auth with Codex, or revisit Grok if
pricing changes) — not on the PoC critical path. Preserve this "why we set them aside" so a future
session doesn't re-shop SuperGrok/Cursor without new pricing.
