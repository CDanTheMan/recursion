---
title: "Recursion — autonomous-loops architecture & roadmap (the anti-drift anchor)"
type: spec
status: current
last-verified: 2026-08-05
related:
  - "docs/architecture.md"
  - "CLAUDE.md"
  - "ANCHOR.md"
  - "state/DECISIONS.md"
  - "golden-stallion-client/docs/plans/four-lane-closure-plan-2026-08-05.md"
  - "golden-stallion-client/docs/spec/client-architecture.md"
---

# Autonomous loops — architecture & roadmap

**Why this file exists.** The architecture kept living only in chat, and chat drifts. This is the one
reviewed place that states what the loop system IS, what is BUILT vs UNBUILT, where the human sits,
and the ordered path forward. Every change to the loop system updates this file first. If a claim
here and the running box disagree, the box wins and this file is stale — fix it.

---

## 1. The two planes (unchanged since v1)

- **Plane 1 — Supervisor.** GPT-5.6 via Codex OAuth ($0 on the ChatGPT sub). cron → `cycle.sh` →
  heartbeat (luna) + daily brief (terra) + reflection (terra). Re-derives a ledger from disk every
  run; owns escalation, git, delivery. Never writes code.
- **Plane 2 — Execution arms.** The thing that actually builds. Today: `claude -p` flat (Max, $0) —
  a competent *file-writer* that turns a spec into code and passes a gate. Metered arms
  (hermes-tools / OpenRouter / DeepSeek) are fenced behind `RECURSION_ALLOW_METERED`.

The load-bearing rule (`delegation-design.md`): **autonomy rests on the acceptance gate, not trust.**
A task with no machine-checkable gate is never auto-integrated — it escalates.

---

## 2. What is BUILT (the spine) — verified 2026-08-05

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
- **Autonomy, human-fenced** — `.env` flags (loop can never self-set them — rule 3):
  `AUTO_REFLECT`, `AUTO_DRAIN`, `AUTO_PLAN`, `ALLOW_PUSH`, `ALLOW_AUTOMERGE`,
  `PLAN_WORKSTREAMS="chiron"`. `id_deploy` has READ+WRITE (verified). GSC key is READ-ONLY.

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

---

## 6. What is UNBUILT (the honest gaps)

1. **Parallel loops.** Today execution is SERIAL — one `work.sh` at a time (single
   `state/.work.lock`), drainer runs tasks one after another. Parallelism needs per-workstream
   queues/locks, concurrent worktrees, and a concurrency cap.
2. **A conductor-grade arm for N-off RE.** `claude -p` cannot do decompilation reasoning. The GSC
   repo ALREADY has the harness for this — `tools/delegate.py` + `bench/` (DeepSeek via OpenRouter,
   Opus judges, spend-capped, ground-truth scorer). It is not yet wired into the recursion loop.
3. **A GSC autonomous workstream.** A roadmap that drives the four-lane **gap register** continuously,
   labels each gap by lane, queues only N-off/W for the arm, and escalates N-idle/N-act/B.
4. **A live-access escalation protocol** — a structured "I need capture #2 (water realm)" / "I need a
   live read of seed provenance" that reaches the human.
5. **Metrics feedback (Item 21).** The supervisor is blind to Golden Stallion fleet/app health. Needs
   the **GS side to PUSH** a health snapshot (bots online, crawls/hr, op=54, last-seen); the box has
   no fleet API and `state/projects/*` is read-only to it. Cross-repo contract: GS publishes →
   recursion reads → ledger.

---

## 7. Roadmap sequence — decided 2026-08-05 (Lucas)

Build the CAPACITY before loading heavy work onto it.

1. **Hermes agent + parallel loops.** Develop the agent so it can support what we load onto it
   (ops discipline via a `recursion-ops` skill; possibly a conductor role), AND build parallel-loop
   infrastructure (per-workstream queues/locks, concurrent worktrees, concurrency cap). The subs are
   under-loaded ($0, lightly used), so capacity is the constraint, not cost.
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
