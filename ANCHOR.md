# Anchor

Reread this when deciding what to work on. If a task doesn't serve something below,
it's not in scope.

Last reviewed: 2026-08-04 · Next review: 2026-11-01

---

## Success criteria (12 month horizon)

**1. Physics foundation.** Cover a physics major's core material in 2–3 years, with
understanding verified by re-explanation, not by grades alone. Arrive at lecture already
stuck on the material so lecture is resolution rather than first contact. Running target:
three weeks ahead of syllabus.

**2. Shipped work.** Cubic Castles client reconstructed, optimized, publicly released.
This is the portfolio artifact — the thing that demonstrates capability to someone deciding
whether to hire or fund.

**3. Employable stack.** Physics + reverse engineering + systems/inference infrastructure.
Rare combination. Mostly a consequence of (1) and (2) done well.

### What these are not

The portfolio is a *long-horizon* goal, not a 12-month one. Tooling spend converts to
income via shipped work and rare skills, not via returns. CSL Labs' near-term deliverable
is research throughput and better-informed decisions — **not alpha**. Any plan that
requires investment returns this year is a plan that fails.

---

## Not this year

Written down so it stops re-entering scope:

- Roblox development — dormant until winter break at the earliest
- Golden Stallion feature work — maintenance only through fall
- Any monetization that extracts from the community. Ruled out on values, and it
  destroys the asset. See `state/DECISIONS.md`.
- New projects. Eight concurrent threads is already over capacity.

---

## Rationing rule

The constraint is review throughput, not tokens. Generated work that isn't verified is
a liability, not an asset.

- **Opus / frontier:** hard multi-file reasoning, physics at the edge of understanding, architecture calls
- **Mid tier:** mechanical passes, refactors, test generation
- **Cheap tier / local:** the supervisor loop, summarization, triage, overnight batch
- **Local (4090 / Qwen):** unattended high-volume mechanical work

If output is accumulating faster than it's being reviewed, the answer is less generation,
not more capacity.

---

## August 2026 proof of concept

Running 2× $200 subscriptions for one month. Highest-availability month of the year;
correct time to test the ceiling. Reversible, month-to-month.

**Deadline: Berkeley starts 2026-08-26.** Realistically one system gets built well before
then. Priority is the learning loop — it's the only one with an external clock that
doesn't move.

### Kill criteria — decide in September, not by feel

| System | Pass condition |
|---|---|
| Learning loop | Produced problem sets actually worked, gap map matched real weak spots |
| Supervisor | Surfaced ≥1 thing that would have been missed; wrong <⅓ of escalations |
| Build loop | Session-resume time measurably dropped |
| Capacity | Hit limits *while shipping*, and the review queue stayed clear |

**Renew the second subscription only if capacity passes AND review queue stayed clear.**
Otherwise drop to one subscription + cheap OpenRouter fallback. Two of three systems
failing means drop back — that is a successful experiment, not a failure.

Measure with `ccusage` weekly. "I felt faster" is not a result.
