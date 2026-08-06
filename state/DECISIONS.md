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

> **ID note (2026-08-06):** a second entry was mistakenly also filed as `D-002` (the
> native-diff gate, 2026-08-06). It has been renumbered to **D-009**. This entry — the
> ChatGPT Pro subscription call — is the original D-002 and is unchanged.

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

> **FALSIFIER FIRED — superseded by D-011 (2026-08-06).** All four `state/projects/*.md`
> were still dated 2026-08-04 two days later, having never been updated, while the
> supervisor quoted them as current status. That is exactly the observable this decision
> named. Reversed to a git-native read. The original reasoning — small blast radius, one
> file to add a project — is preserved above and was not wrong; it was outweighed once
> the loop needed to *act* on project state rather than merely report it.

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

---

## D-008 — Engine config deployed on gs-recursion: local terminal, system service, luna→gemini fallback
Date: 2026-08-05 · Status: OPEN

**Options considered (fallback model):** anthropic/claude-haiku-4.5 (first pick) / deepseek-chat-v3.1 /
openai/gpt-5.6-luna / a luna→non-OpenAI chain

**Chose:** Primary `gpt-5.6-terra` (Codex OAuth). Fallback chain via OpenRouter, `sort: price`:
leg 1 `openai/gpt-5.6-luna`, leg 2 `google/gemini-2.5-flash-lite`. Terminal backend `local`;
gateway installed as a systemd **system** service run as root (boot-persistent).

**Because:** luna is the cheapest current-gen model on OpenRouter ($0.10/$0.60 per Mtok) — beats
DeepSeek ($0.25/$0.95) on both axes and stays in the primary's family. haiku-4.5 (first pick,
$1.00/$5.00) was ~10x too dear for a leg that only fires on primary outage. Leg 2 is a non-OpenAI
backstop: if the fallback trigger is an OpenAI-wide outage, an openai/* leg is also down, so a
different vendor covers it. `local` backend because the box is a dedicated single-tenant disposable
sandbox (Docker's isolation is defeated once you mount in the auth/keys it must use). System-service-
as-root because auth/keys/repo all live under /root and the box must survive reboots (D-I).

**Falsifier:** if the Sept-1 review shows the fallback fired often enough that metered OpenRouter
spend was material, the primary sub was undersized or the loop is too chatty — revisit tiering.
Equally wrong if luna proved too weak for fallback decisions and the loop made bad calls during an
outage window unnoticed — then leg 1 should be terra, not luna.

**Review:** 2026-09-01 (with the capacity kill criteria).

**Note:** implements D-006/D-007. Config lives in `/root/.hermes/config.yaml` on gs-recursion
(backup `config.yaml.bak-20260805`); verify live with the `fallback_providers` block + `hermes model`.
STILL TODO, and NOT a Hermes toggle: (1) a fallback-spend ALERT — must be a Recursion-side monitor
(cron checks OpenRouter usage / greps gateway logs for fallback events → Telegram); (2) per-tier model
routing (Lua→luna, decisions→terra, escalate→sol) is Recursion dispatcher logic, built when the loop
lands, not a global Hermes setting.

## D-009 — GSC/cubic-castles native-diff gate: approved as the metric; planner integration DEFERRED
Date: 2026-08-06 · Status: RESOLVED (Lucas, via session)

**Correction 2026-08-06:** originally filed as `D-002`, colliding with the 2026-08-04
ChatGPT Pro decision. Renumbered to D-009 with Lucas's approval. Any earlier reference to
"D-002" that concerns the native-diff gate means THIS entry. The original D-002 above is
unchanged.

**Options considered:** A) approve gate + planner integration / B) approve gate, DEFER planner integration / C) defer/reject, leave GSC idle
**Chose:** B
**Because:** The strict-decrease Sum|per-slot| native-diff gate is a sound regression/quality metric (SUM-not-total; byte-identical untargeted worlds = the control) — approved in that role; it is Tier-2 of the two-tier gate. But DEFER letting it auto-drive overnight planning: proven 2026-08-06 that the pure count ratchet REJECTS decomp-exact correct fixes that couple across worlds — two conductor runs (0x68 Cloud, 0x6c overlay) each found a correct fix and correctly NO-OPd, because a fix that helps one world while an unrelated defect in another makes it score worse fails "no world worsens". Auto-planning on the count gate manufactures no-op branches, not merges. Also the gap register is STALE (0x74/0x88 already measure 1.000 = closed), so a planner would queue dead gaps. The real driver is Tier-1 = a decomp-DECISION ledger (correctness vs the decompiled predicate), now being built.
**Falsifier:** if the FIRST two-tier-gated autonomous cubic-castles run still produces only no-ops (the decomp-decision ledger does not make correct coupled fixes landable either), then the blocker was not the gate and deferring-for-the-ledger was the wrong remedy.
**Lift condition:** two-tier gate merged + gap register de-staled from live measurement + 1 supervised shakedown passes -> add cubic-castles/gsc to RECURSION_PLAN_WORKSTREAMS.
**Review:** 2026-09-06

---

## D-010 — Rebase Recursion onto a Hermes-led control plane; Claude becomes a bounded executor
Date: 2026-08-06 · Status: OPEN

**Options considered:** (A) keep the current shape — cron-driven stateless supervisor,
Claude sessions doing architecture ad hoc / (B) rewrite the orchestrator on a new
framework (Hermes Kanban as the canonical store) / (C) keep the proven execution layer and
move only AUTHORITY up to Hermes, behind adapters

**Chose:** C.

**Because:** the execution layer is not what is failing. `work.sh` (worktrees, gates,
retry-once, no-op skip), `conduct.sh` (per-workstream locks), the PAUSE switch,
`publish.sh`, and the gates are proven and were re-verified on the box. What is missing is
above them: nothing owns a durable goal→task→event lifecycle, so blockers have no identity
(the same escalation was appended to `state/INBOX.md` four times in nine hours), a killed
worker leaves a permanent `running` row, and "status" is four stores pretending to be one.
Rewriting the queue on a new framework would put the working safety machinery at risk to
fix a layer above it, and would run two sources of truth during migration — the failure
this rebase exists to end. Hermes becomes the executive: it holds the portfolio, takes
direct orders from Lucas, decides what runs next, and monitors it. Claude receives one
bounded task with allowed paths, explicit non-goals, and a machine-checkable gate.

Hermes decides in TEXT and a deterministic actuator executes through the existing scripts.
That is not only a correctness boundary (the planner never becomes a second implementer) —
it is a cost boundary: tool-calling turns fall off the Codex subscription onto metered
OpenRouter, so an executive that *acts* through tool calls would quietly convert a flat
subscription into a metered bill.

**Falsifier:** if by 2026-09-15 Lucas still cannot ask Telegram "what is running and why"
and get an answer grounded in live task/process/git state — or if escalations still
duplicate, or a stale `running` row still survives a killed worker — then moving authority
without replacing the store was insufficient and (B) was the right call. Equally wrong if
the constitution is in place but Claude sessions keep making architecture calls anyway:
that would mean the boundary needs mechanical enforcement beyond protected paths.

**Review:** 2026-09-15

---

## D-011 — Git is the transport: every project is a live clone; reverses D-003
Date: 2026-08-06 · Status: OPEN

**Options considered:** (A) keep the push model and add a freshness SLA so stale copies at
least render as STALE / (B) reverse to a git-native read — clone every registered project
on the box, derive status from git

**Chose:** B (Lucas's instruction: "everything is going to be connected with git and not
be statically updated via porting").

**Because:** D-003's falsifier fired. Copied state goes stale silently and reads exactly
like working state; a fetch cannot. (A) would have made staleness visible but kept the
copy step as the source of truth, and a control plane that must *act* on project state
needs the repo, not a summary of it — it has to read the charter, run the gates, and push
the review branch. Seven repos are now cloned on the box behind per-repo deploy keys, so
blast radius stays scoped per repo without an account-level credential.

**The honest exception, recorded so it is not quietly violated:** data that cannot live in
git — the gitignored GSC block-model corpus, raw captures, and secrets — is still carried
by an explicit seed manifest. That manifest must be checksummed and must fail loudly when
a path is absent; the 2026-08-05 corpus incident (48 conformance tests unpassable because
a gitignored corpus was silently absent) is what that rule is paying for.

**Falsifier:** if by 2026-10-01 the clones are routinely stale because nothing fetches
them, or disk/IO on the box becomes a real constraint, or a write key on a cloned repo
enables an incident that the push model would have prevented, this was wrong.

**Review:** 2026-10-01

---

## D-012 — PAUSE halts execution and preserves awareness
Date: 2026-08-06 · Status: OPEN

**Options considered:** (A) keep the code's behaviour — PAUSE exits before everything,
including the heartbeat / (B) implement the documented behaviour — halt execution, keep
monitoring, status, and escalation alive

**Chose:** B. The docs were right and the code had drifted.

**Because:** three documents and `pause.sh`'s own message all promise "heartbeat +
escalation still reach you", while `cycle.sh` and `run.sh` both exited before the
heartbeat. A paused box that cannot tell you it is paused, or deliver the escalation that
made you pause it, is a blind spot dressed as a safety feature — and PAUSE is exactly the
state you are in when you most need to see what the box thinks. Execution (arms, planning,
drain, conduct, reflection, pushes, merges) still halts hard; those keep their own guards.

**Falsifier:** if a paused box now performs any action that changes a repo, a branch, or
external state, the split was drawn in the wrong place and (A)'s blunt exit was safer.

**Review:** 2026-09-15
