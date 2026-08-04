# Recursion — architecture

Last updated: 2026-08-04. Read `ANCHOR.md` first — that's WHY/WHAT; this is HOW.

## Purpose

One control plane over several workstreams that each move at a different tempo and need a different
amount of Lucas. The bottleneck being solved is **context-switching**: juggling a separate
session/terminal per project is itself what slows development and learning. Recursion is the single
front + shared brain; the workstreams report into it, it routes work out.

## Workstreams and interaction intensity

| Workstream | Runs on | Interaction | Autonomy ceiling | Why |
|---|---|---|---|---|
| GSC engine (client reconstruction) | **local Windows** (needs live `cubic.exe` + CheatEngine oracle) | background | **high** | machine oracle: native mesh @0x006FA210 scores its own output |
| Fleet ops (vend/disco/holla) | gs-worker-nbg + operator API | background | medium | auto-fix reversible; escalate costly/risky; mining = DO-NOT-DEPLOY |
| Learning loop | interactive, anywhere; state in Recursion | **foreground** | low (by design) | the value is the live Socratic loop |
| Supervision + routing | gs-recursion-nbg (always-on) | background | — | the dispatcher + ledger + alerting |

**Key principle: autonomy scales with machine-verifiability.** GSC has a ground-truth oracle, so
autonomous iteration there is self-reviewing and can't create the unreviewable backlog ANCHOR warns
about. Fleet work is partially checkable → auto the safe part, escalate the rest. Learning is
interactive by nature. Because GSC + fleet are background and learning is foreground, they
parallelize: Lucas lives in the tutoring while the renderer grinds and the fleet self-heals, all
reporting into one ledger.

## Engine: a thin escalation-tiered dispatcher (NOT a heavyweight harness)

The always-on component is deliberately light and event-driven — mostly idle, wakes on a trigger
(cron, fleet alert, a message from Lucas). It does not run a big model non-stop; it ROUTES work to
the right engine on demand. **This is what makes a 24/7 brain fit the quota.**

Tiers (names are a skin over the function — rename freely):

- **Lua — routine heartbeat.** Cheap, frequent health/status checkins (fleet alive? queue draining?
  GSC loop progressing? anything new in the ledger?). Runs on the cheapest tier (local rules /
  OpenRouter). Escalates up only on a real signal.
- **Terra & Sol — decision agents (mid-tier reasoning).** Fire only when Lua surfaces something.
  - **Terra** — infrastructure/fleet: keep workers alive, refill queues, replace jailed accounts
    within guardrails, "build/repair infra" moves.
  - **Sol** — keep the productive loop going: GSC iteration direction, learning-loop scheduling.
  - Run on `claude -p` (Claude subscription, flat) for hard reasoning, or GPT/Codex, or cheap
    OpenRouter per `routing.yaml`.
- **Hermes — the front/router.** The single interface Lucas talks to + the message bus between tiers
  and Lucas. Async (INBOX/Telegram) and sync (a conductor session).
- **Lucas — top of the escalation chain.** Sees only what genuinely needs him (below).

### Engines in scope + control (Claude · GPT · OpenRouter — all first-class)

All three are in scope; the loop routes among them by cost and task:

- **Claude** (`claude -p`) — subscription-covered workhorse for hard reasoning/dev. Spends the Claude
  limit, so heavy use competes with interactive sessions.
- **GPT / ChatGPT Pro ($200)** — Lucas's, and **stays under Lucas's control.** Default role: a
  human-driven parallel *interactive* seat (Codex/ChatGPT). The autonomous loop may call GPT only as
  a **metered API within an explicit spend cap Lucas sets**, escalation-gated for anything expensive
  — it never burns the subscription unsupervised.
- **OpenRouter** — cheap routine tier (heartbeat, triage, summarization) + the graceful-degrade
  fallback so the loop never hard-stops on a quota.

**Control invariants (load-bearing):**
- `routing.yaml` is the single control surface for which engine does what. **Lucas edits it to
  rebalance; the loop never edits its own routing/auth/budget** (CLAUDE.md hard rule 3). So Lucas
  always has the wheel on how much of each subscription gets spent.
- GPT usage is Lucas-controlled by construction: interactive seat by default, automated GPT only
  within a budget cap + escalation gate.
- Calling `claude -p` still spends the Claude limit, so the Claude+GPT+OpenRouter mix conserves Claude
  quota only insofar as GPT/OpenRouter carry load — a routing-budget knob Lucas owns, not free
  headroom.

## Escalation: auto / notify / escalate

Every proposed action is scored on **reversibility × cost × ambiguity × verifiability.** Higher on
any axis → higher it escalates.

- **Auto (act, log only)** — reversible, cheap, machine-verifiable. GSC iterations that pass the
  oracle. Fleet: kick a wedged bot, restart a crashed worker, refill a queue.
- **Notify (act, then tell Lucas async)** — worth knowing, didn't need approval. Committed a branch;
  auto-replaced an account within the jail-plague guardrail. → daily digest + Telegram.
- **Escalate (block on Lucas)** — irreversible / expensive / ambiguous / unverifiable. Provisioning
  accounts (spends money + proxies), major reconfig, merging GSC to `main`, ANYTHING mining
  (DO-NOT-DEPLOY), a decision not in `DECISIONS.md`, a physics claim unverifiable against a known
  solution. → `state/INBOX.md` + Telegram ping, and WAIT.

This is the scaffold's "escalate, don't guess" made mechanical.

## How Lucas fits in — the three questions

**1. Escalation to you.** Telegram push (you're often mobile) → the item lives in `state/INBOX.md`
(durable queue). You clear it by answering; the loop reads your answer next cycle. One-page briefs,
prioritized, drop rather than append.

**2. Direct access + changing things.** Four levers:
- **Async (pull, low-attention default):** read INBOX/briefs/state; answer escalations.
- **Sync (drop-in):** open a **conductor session** — interactive Claude Code with full read/write to
  `state/` + dispatch rights. Steer directly: redirect the GSC loop, pause a fleet action.
- **Declarative steering (the wheel):** the loops READ `DECISIONS.md` + `ANCHOR.md`. Change a
  decision → the loops pick it up next cycle. Config as control.
- **Kill switch:** a `state/PAUSE` flag every loop checks first. Present ⇒ autonomous action halts
  instantly; only heartbeat + escalation remain. The safety valve.

**3. Context management (for optimized work)** — the vault already paid for these lessons:
- **The ledger is the shared brain.** `state/` (projects, DECISIONS, gap-map, briefs, INBOX) is the
  durable, compact, cross-agent memory. Agents boot from it, not from a giant transcript.
- **Carry no state.** Every scheduled run RE-DERIVES current state from the ledger + ground truth
  (oracle / fleet-status / DB) at run time. A state block baked into a prompt rots in days and reads
  as working (memory: `handoff-prompts-must-carry-no-state`).
- **Per-workstream working set.** Each loop keeps its own small state (GSC: current gap + last oracle
  scores; fleet: health snapshot; learning: gap-map) — not one bloated shared context.
- **Route context depth by tier**, like compute: Lua gets the check only; Terra/Sol get the relevant
  slice; the conductor gets the full ledger on demand.
- **Guard the digest.** Summaries drop quiet-but-important facts (memory: `digests-miss-inert`).
  Periodic full refresh against ground truth, not just rolling summaries.

## Where everything runs

- **Windows (Lucas's box):** GSC oracle loop (live `cubic.exe` + CheatEngine MCP + client code). GSC
  autonomy is local.
- **gs-worker-nbg (Hetzner):** fleet workers (vend/disco/holla) via German residential proxy.
- **gs-recursion-nbg (Hetzner, always-on):** dispatcher (Lua/Terra/Sol/Hermes), state ledger, cron,
  fleet monitor, alerting.
- **Railway (app layer only):** API, Discord bot, dashboard, renderer, Postgres.

## Open naming check

Lua / Terra / Sol / Hermes are a PROPOSED mapping onto the functional tiers above — confirm or
rename. The function is fixed; the skin is yours.
