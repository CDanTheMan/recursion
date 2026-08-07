---
title: "Recursion — autonomous-loops architecture & roadmap (the anti-drift anchor)"
type: spec
status: current
last-verified: 2026-08-07
related:
  - "docs/architecture.md"
  - "CLAUDE.md"
  - "ANCHOR.md"
  - "state/DECISIONS.md"
  - "docs/plans/hermes-project-pilot-phase6-handoff.md"
  - "docs/plans/hermes-project-pilot-phase7-handoff.md"
  - "golden-stallion-client/docs/plans/four-lane-closure-plan-2026-08-05.md"
  - "golden-stallion-client/docs/spec/client-architecture.md"
---

# Autonomous loops — architecture & roadmap

**Why this file exists.** The architecture kept living only in chat, and chat drifts. This is the one
reviewed place that states what the loop system IS, what is BUILT vs UNBUILT, where the human sits,
and the ordered path forward. Every change to the loop system updates this file first. If a claim
here and the running box disagree, the box wins and this file is stale — fix it.

---

<!-- superseded-by: CONTROL_PLANE.md (2026-08-06, D-010) — authority sections only; see §1 and §5 -->

> **AUTHORITY SUPERSEDED 2026-08-06 (D-010).** This document described the supervisor as a
> scheduled, stateless text transform and the Telegram agent as a *reactive* console. That is
> the mailbox shape the rebase replaces: **Hermes is the executive control plane** — it owns the
> portfolio, the goal→task→event lifecycle, dispatch, monitoring, escalation, replanning, and
> review-branch publication, and it takes direct orders from Lucas. See `CONTROL_PLANE.md`.
>
> **What survives, and why it is not a contradiction:** "the supervisor never writes code" is
> still correct and load-bearing. Hermes *decides*; deterministic scripts *execute*. Keeping the
> planner out of implementation is both a correctness boundary (no second implementer) and a cost
> boundary (tool-calling turns fall off the Codex sub onto metered OpenRouter). The lane algebra
> (§3), the gates, the escalation seam, and the guardrails (§8) are all preserved as-is.
>
> Everything below is retained as the record of what was built and why. Read it as history plus
> live mechanics, not as the authority model.

## 1. The two planes (unchanged since v1)

- **Plane 1 — Supervisor.** GPT-5.6 via Codex OAuth ($0 on the ChatGPT sub). cron → `cycle.sh` →
  heartbeat (luna) + daily brief (terra) + reflection (terra). Re-derives a ledger from disk every
  run; owns escalation, git, delivery. Never writes code.
  <!-- superseded-by: CONTROL_PLANE.md (2026-08-06, D-010) -->
  > **PARTLY SUPERSEDED.** "Never writes code" is **retained** — the planner must not become a
  > second implementer, and text-only is also what keeps it on the flat sub (tool-calling turns
  > fall to metered OpenRouter). What is superseded is *stateless*: Hermes now owns durable
  > portfolio/goal/task/event state and drives the lifecycle, rather than re-deriving a read-only
  > ledger every tick and waiting to be asked.
- **Plane 2 — Execution arms.** The thing that actually builds. Today: `claude -p` flat (Max, $0) —
  a competent *file-writer* that turns a spec into code and passes a gate. Metered arms
  (hermes-tools / OpenRouter / DeepSeek) are fenced behind `RECURSION_ALLOW_METERED`.

The load-bearing rule (`delegation-design.md`): **autonomy rests on the acceptance gate, not trust.**
A task with no machine-checkable gate is never auto-integrated — it escalates.

---

## 2. What is BUILT (the spine) — verified 2026-08-07

- **Supervisor tier** — heartbeat/brief/reflection on cron; ledger; INBOX + Telegram escalation.
- **Build-loop v2** — `plan.sh` (roadmap → task) → `work.sh` (arm → acceptance gate → auto-commit
  to `loop/work/<id>`) → `integrate_remote` (publish + **path-scoped ff-only auto-merge**).
  **Proven end-to-end 2026-08-05**: the box planned, built, gated, and **auto-merged a Chiron
  landing page to `main` by itself** (scope `apps/chiron/`, ff-only). A failing build escalates
  after one retry and never merges.
- **Reflection / bounded self-improvement** — `reflect.sh` (daily, $0): proposes ONE improvement to
  `state/PROPOSALS.md` (human-gated, never applied — rule 3) + one durable lesson to
  `state/LESSONS.md` and hermes memory (auto-injected into future arms).
- **Two GSC gates** — `gsc-conformance-gate.sh` (regression; the offline suite stays green) and
  `gsc-nativediff-gate.sh` (**Σ|per-slot triangle error| must strictly decrease; SUM-not-total** —
  the tool's own TOTAL line cancels per-slot over/under; furys TOTAL 14193 hides Σ|slot| 26737).
- **Hermes learning substrate** — curator ARMED (manages agent-created skills; never touches the 70
  bundled); first agent skill `recursion-status` makes the **Telegram gateway self-aware** (answers
  box status from ground truth via the CLI — tested).
- **Parallel loops (capacity)** — the global work lock is now **per-workstream**
  (`state/.locks/ws-<ws>.lock`) and `conduct.sh` runs several workstreams at once (one build each,
  concurrency-capped, same bounds as drain). Tested 2026-08-05: two workstreams built concurrently
  while a same-workstream task serialized behind the first; serial callers unchanged. Design:
  `docs/plans/parallel-loops.md`.
- **Agent ops capacity** — the `recursion-ops` hermes skill teaches the root Telegram agent to
  EXECUTE ops (resolve/requeue/plan/drain/pause/publish) with the loop's guardrails and to defer
  STRUCTURAL changes to a reviewed authoring session (counterpart to read-only `recursion-status`).
  Verified the `hermes-telegram` bundle carries the skills tools, so the gateway can load it. Both
  mirrored in `loop/hermes-skills/` (box `/root/.hermes/skills/` is authoritative).
- **Project-goal reconciliation (Phase 6, merged but not deployed)** — a deterministic
  reconciler observes canonical goal/task/run/process/worktree/ref/event/delivery truth and emits
  only idempotent schema-v1 decisions through the existing durable action queue and sole actuator.
  It admits dependency-ready work under concurrency/token/cost/wall/retry/failure/review budgets;
  reuses the Phase 5 bounded worker, scope, gate, timeout, and exact-commit verifier path; publishes
  only through the existing review-branch publisher; independently verifies the exact final
  candidate; and stops deterministically. PAUSE prevents dispatch, gates, publication, and
  in-flight goal verification. Phase 6 is merged into `origin/master`; production remains
  PAUSE-gated and has not run this loop. See `docs/plans/hermes-project-pilot-phase6-handoff.md`.
- **Reporting and notification fan-out (Phase 7, authored but not deployed)** — the existing
  supervised actuator asks one deterministic outbox observer to enqueue idempotent schema-v1
  decisions. Event reconciliation, exact `(event_id, destination)` fan-out, retry, durable
  transport-evidence acknowledgement, dead-letter escalation, terminal project reporting, the
  one Head Hermes portfolio result, audit-chain refresh, and recovery reconciliation all execute
  through the existing decision/action/actuator path. Human-visible delivery still uses
  `notify.sh`; no second scheduler, sender, state store, or delivery queue exists. Strict policy
  separates the project topic, Head Hermes/explicit portfolio destinations, and explicit Lucas-DM
  attention. PAUSE preserves event/outbox awareness and pending work while preventing sends. The
  Phase 7 review branch is local-only and production has not run it. See
  `docs/plans/hermes-project-pilot-phase7-handoff.md`.
- **Autonomy, human-fenced** — `.env` flags (loop can never self-set them — rule 3):
  `AUTO_REFLECT`, `AUTO_DRAIN`, `AUTO_PLAN`, `ALLOW_PUSH`, `ALLOW_AUTOMERGE`, `CONDUCT` (parallel
  drainer; default off), `PLAN_WORKSTREAMS="chiron"`. `id_deploy` has READ+WRITE (verified).
  ⚠ **Corrected 2026-08-06 — this paragraph was stale.** The **GSC key is WRITE**, not read-only,
  and every registered project now has its own per-repo WRITE deploy key (`~/.ssh/<repo>_deploy`,
  seven added 2026-08-06). Enforcement of "never merge main" moved to **GitHub branch protection**,
  which is the only thing a write key actually respects. `RECURSION_ALLOW_AUTOMERGE` is being
  turned **off** (Lucas, 2026-08-06): every feature ships as a sequential review branch. Read live
  flag values from `.env`; never recall them.

---

## 3. The autonomy model = the LANE ALGEBRA (the core concept)

From `four-lane-closure-plan-2026-08-05`: **every gap belongs to the lane that can answer it, and the
lane decides whether it can be autonomous.** This IS the boundary between what the loop does alone and
what it escalates.

| Lane | Settles | Autonomous? |
|---|---|---|
| **N-off** native decomp offline (10,040 fns + assets) | structure: predicates, layouts, formats | ✅ free, unlimited, **delegable** |
| **W** WASM corpus + captures on disk | the wire; cross-lane confirmation | ✅ offline (⚠ raw `grep`; Grep tool is blind to the gitignored corpus) |
| **N-idle** native live, read-only | ground-truth values, new captures | ❌ needs Lucas present → **escalate** |
| **N-act** native live, active (breakpoints, in-game action) | causation | ❌ needs Lucas driving → **escalate** |
| **B** browser | the deliverable — does it draw right | ❌ human eyeball, one at a time → **escalate** |

**Therefore the recreation is autonomous on N-off + W, and escalates for N-idle / N-act / B.** This
is the correct boundary, not a limitation: **live observation is irreducibly human-gated** — a new
capture or a live-memory read cannot be produced without a live client on a clean alt. The loop
grinds the offline lanes; when it needs a live fact it escalates a *specific, scoped* request to the
human via the supervisor. That is precisely the "loop works hard, escalates for direction" vision.

**The gate is already correct.** The four-lane plan's Phase-2 gate — *"total ratio → 1.000, and the
per-slot table is the gate, not the headline number"* — is exactly `gsc-nativediff-gate.sh`.

---

## 4. Host-model ruling (GSC) — decided 2026-08-05 (Lucas)

**Our own separate client. Goal: 1:1 replication of the native ENGINE's observable behavior +
WASM/browser CLIENT NETWORKING (wss:// + outbound wrap), THEN optimize for the community.**
Engine choice is free — anything that reaches 1:1 parity is acceptable. This is the REIMPLEMENT path
(ADR-0002), *not* WASM-SHELL (running the real `Cubic.exe`; scored 2nd, deliberately rejected for
ban-safety + maintainability). "1:1 first, customize second" = reach native-diff per-slot → 1.000
(the base) before adding any community feature. **We are hard-gated on the 1:1 base.**

---

## 5. Where the human sits (the escalate → direct seam)

- **Escalation:** a failed gate (after retry) or a supervisor decision → `state/INBOX.md` + a
  Telegram ping tagged `[id]`. (There is no reply↔item correlation — reference the tag.)
- **Direction back in:** `recursion resolve/requeue <id>`, editing a roadmap, or a `DECISIONS.md`
  entry. The supervisor reads these next cycle.
- **The Telegram agent** is the human's chat console to the box — reactive, root, **NOT bound by the
  loop's guardrails** (it does what you tell it). It runs OPS (status, resolve/requeue/plan/drain/
  pause). **Structural changes to the loops go through a reviewed authoring session, never the agent
  ad-hoc** — that is how authorship stays singular and drift stays out.

  <!-- superseded-by: CONTROL_PLANE.md (2026-08-06, D-010) -->
  > **SUPERSEDED 2026-08-06 (D-010).** "Reactive console" is no longer the model. Telegram is the
  > **cockpit**: threaded by project (forum topics), and Hermes leads each thread rather than
  > waiting to be asked. Hermes takes direct orders from Lucas there, dispatches, reports live
  > worker/gate/branch state, and correlates replies to the escalation they answer.
  > *Still true:* the gateway is root and outside the loop's rails — a human drives it — and
  > structural changes still go through a reviewed authoring session.

---

## 6. What is UNBUILT (the honest gaps)

*(Parallel loops + agent-ops capacity — DONE 2026-08-05, see §2.)*

1. **A conductor-grade arm for N-off RE.** `claude -p` cannot do decompilation reasoning. The GSC
   repo ALREADY has the harness — `tools/delegate.py` + `bench/` (DeepSeek via OpenRouter, Opus
   judges, spend-capped, ground-truth scorer). It is not yet wired into the recursion loop.
2. **A GSC autonomous workstream — and the GSC-REPO PREP that makes GSC loop-drivable first.** The
   loop has a READ-ONLY key to GSC, so these land on GSC `main` via normal review FIRST, then the
   recursion side wires up: (i) a machine-readable **gap register** (gaps tagged by lane/world/
   target-slot/gate) so the planner reads it and queues only N-off/W; (ii) `native-diff.cjs
   --metric` JSON (per-slot Σ|err|, sumAbs, vecDigest, buildDefaultsHash) so the gate consumes
   structured output; (iii) a **BUILD_DEFAULTS drift signal** so a defaults change forces a
   baseline re-pin instead of a silently-stale compare; (iv) a **seed manifest** of gitignored-
   but-required paths; (v) a **loop-callable conductor arm** over `delegate.py` (reads spend fresh,
   `provider.sort=price`, DeepSeek-generate → scanner → apply; NEVER sets `ANTHROPIC_API_KEY`);
   (vi) a **protected-path contract** (tests/tools/fixtures/data arm-forbidden); (vii) reuse
   `bench/context-pack/` as per-gap boot context. Then a recursion `gsc` workstream drives it,
   gated by `gsc-nativediff-gate.sh`, green = reviewable branch (NO auto-merge — read-only key),
   N-idle/N-act/B → escalate. Do NOT widen `PLAN_WORKSTREAMS` to `gsc` until the prep lands.
   **STATUS 2026-08-05:** GSC-repo prep is BUILT on two review branches (`prep/loop-drivable-gate` =
   gap register + `native-diff --metric` + seed manifest; `prep/loop-conductor-arm` = `loop-arm.sh` +
   protected-path gate + contract). Safety machinery proven in `--dry-run` (no spend). REMAINING, in
   order: (a) Lucas merges both branches to GSC main; (b) a supervised REAL-SPEND shakedown of
   `loop-arm.sh` on one gap (G1b) proving generation quality vs the gate; (c) recursion-side wiring
   (gate → `--metric`; a metered-fenced work.sh conductor engine; a gap-register-driven roadmap).
   Only THEN widen `PLAN_WORKSTREAMS`. A lane without a proven acceptance layer just manufactures
   review backlog — the chiron lesson.
3. **A live-access escalation protocol** — a structured "I need capture #2 (water realm)" / "I need
   a live read of seed provenance" that reaches the human.
4. **Metrics feedback (Item 21).** The supervisor is blind to Golden Stallion fleet/app health.
   Needs the **GS side to PUSH** a health snapshot (bots online, crawls/hr, op=54, last-seen); the
   box has no fleet API and `state/projects/*` is read-only to it. Cross-repo contract: GS
   publishes → recursion reads → ledger.

## 7. Roadmap sequence — decided 2026-08-05 (Lucas)

Build the CAPACITY before loading heavy work onto it.

1. **Hermes agent + parallel loops.** ✅ DONE 2026-08-05 — `recursion-ops` skill shipped +
   curator-adopted, and parallel-loop infra (per-workstream locks + `conduct.sh` conductor) shipped
   and tested (see §2). The subs are under-loaded ($0), so capacity was the constraint, not cost.
2. **GSC autonomous loop.** Wire the existing delegation/bench/gates into a recursion workstream that
   drives the four-lane gap register, gated by native-diff, escalating the live lanes. Close the
   remaining "what's needed to run it autonomously" gap (#2–#4 above).
3. **Metrics feedback (Item 21).** GS health → supervisor ledger.

---

## 8. Guardrails (inherit CLAUDE.md; these are load-bearing here)

- Never `main` / never `--force` / never merge EXCEPT the env-fenced path-scoped ff-only auto-merge.
- The loop NEVER edits its own config/auth/model/cron (self-improvement PROPOSES; human approves).
- Every autonomous task needs a machine-checkable gate. **SUM-not-total** on any renderer metric.
- Live game access (captures, live-memory reads) is human-gated on a throwaway alt + clean proxy —
  never the main account or home IP. The loop requests it via escalation; it never drives the client.
- Metered arms fenced. The Telegram gateway is root and outside these rails — humans drive it.
- The FLEET session is separate — this program does not touch it; Item 21 is a published contract.
