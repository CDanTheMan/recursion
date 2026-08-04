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
