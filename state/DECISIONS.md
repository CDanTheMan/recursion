# Decision log

Every decision gets a falsifier — the specific thing that, if observed, means this was wrong.
Without it, review is hindsight.

**Review cadence:** first of the month. Pull decisions ≥60 days old, check whether the
falsifier fired, mark `HELD` / `FAILED` / `UNCLEAR`. Do not edit the original entry.

---

## D-017 — Recursion v3 is greenfield; v1/v2 are retired, not migrated
Date: 2026-09-28 · Status: OPEN

**Options considered:** A) migrate v2 aggregate-by-aggregate into v3 (the original
`CURRENT-AND-MIGRATION` / OR-019 strangler) / B) keep both versions side by side / C) treat v3 as
a brand-new harness that inherits nothing from v1/v2 and retire the old control plane.

**Chose:** C.

**Because:** v3 is a from-scratch provider-neutral agent harness (its own client, execution
kernel, context/compaction engine and node fabric). The v1/v2 Hermes-based control plane
contributed no dependency to it, and version coexistence caused the drift that blocked
contributors. The complete prior tree is preserved at tag `pre-v3-clean-cut-20260928`.

**Consequence:** the pre-v3 decision log (D-001 through D-016) and the v2 migration framing in
`docs/v3/CURRENT-AND-MIGRATION.md` are historical lineage only and authorize no current work.
`CONTROL_PLANE.md` and `ANCHOR.md` were rewritten for a single-product repository under Lucas
alone, with coding agents as bounded executors and no standing executive.

**Falsifier:** if v3 turns out to require v2 state, schema or a migration path to function, this
was wrong.

**Review:** 2026-12-01
