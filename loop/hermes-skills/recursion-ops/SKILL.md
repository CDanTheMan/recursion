---
name: recursion-ops
description: "EXECUTE Lucas's operational requests on the Recursion box (resolve/requeue/plan/drain/pause/publish) with the loop's safety discipline — act on ops, defer structural changes to an authoring session."
version: 1.0.0
author: Recursion (authored)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Recursion, Ops, Supervision, Guardrails, Conductor]
    related_skills: [recursion-status]
---

# Recursion box — operations (acting)

This agent runs as root **on the Recursion control-plane box** (`/opt/recursion`). When Lucas asks you
to *do* something to the loop — not just report it — this skill is how you act **with the same
discipline the autonomous loop follows**. You are root and technically unfenced, so the safety here is
JUDGEMENT, not a cage. The rule that keeps trust: **run the OPS verbs freely; never make STRUCTURAL
changes ad-hoc.**

The read-only counterpart is `recursion-status` — use that to *report*. Use THIS to *act*. Acting is
always a separate, explicit request from Lucas; never act while merely answering "status".

## When to Use

Lucas asks you to change the box's state, e.g.:
- "resolve chiron-003 — the page looks good" / "requeue that failed task"
- "pause the box" / "resume"
- "queue the next chiron page" / "plan chiron"
- "drain the queue" / "run the next task"
- "publish the review branch so I can merge it"

## The OPS verbs (safe to run when asked — the `recursion` CLI is on PATH)

- `recursion resolve <id> "<decision>"` — close an escalation. **Always capture Lucas's actual
  decision** in the note; that note is the record. If he didn't give a reason, ask for one.
- `recursion requeue <id> ["note"]` — re-open a task for another arm run. Costs Max quota — fine when
  asked, but say so if he's requeuing the same failing task repeatedly (the approach may be wrong).
- `recursion plan <workstream>` — emit the next task from `state/roadmaps/<ws>.md`.
- `recursion drain` — run queued tasks under bounds (max/failstop/deadline/PAUSE). The continuation
  engine. Report the outcome from the log.
- `recursion work <id>` — build one specific task now.
- `recursion publish [--branch <name>]` — push review branches to origin for Lucas to merge (gated by
  RECURSION_ALLOW_PUSH). This pushes REVIEW branches only; it does **not** merge to a default branch.
- `recursion pause "<reason>"` / `recursion resume` — the kill switch. **`pause` is always the safe
  move** if anything looks wrong or ambiguous.

Chain them like a conductor when it helps: `recursion inbox` → identify the blocker → get Lucas's
decision → `resolve`/`requeue` → `drain`. But every link that changes state is Lucas's call.

## Guardrails (load-bearing — this is why the loop is trusted)

- **Never `main` / never `--force` / never hand-merge.** Merges to a default branch happen ONLY via
  the box's own env-fenced, path-scoped, ff-only auto-merge (chiron), or by a human on GitHub. You
  publish review branches; you do **not** merge them yourself, and never `git push --force`.
- **Never make STRUCTURAL changes ad-hoc.** Editing loop code/scripts, gates, roadmaps' structure,
  auth/deploy keys, cron, models, or the `.env` autonomy flags (`RECURSION_AUTO_*`,
  `RECURSION_ALLOW_*`, `RECURSION_PLAN_WORKSTREAMS`) is NOT an ops task — it causes drift. If Lucas
  asks for one, record the request (append to `state/INBOX.md` and/or tell him plainly) and say **"this
  needs an authoring session"** (Claude Code + Lucas), then stop. The loop itself is forbidden from
  self-setting those flags (CLAUDE.md rule 3); you hold the same line unless Lucas is explicitly and
  knowingly directing a one-off change and understands it bypasses review.
- **Confirm before anything destructive or costly** — `pause` (halts all autonomy), `resolve`
  (closes an escalation for good), repeated `requeue` (burns quota). One-line confirm, then do it.
- **Ambiguity → ask, never guess.** If the task id, workstream, or decision isn't unambiguous, ask
  Lucas which one. A wrong `resolve <id>` closes the wrong escalation.
- **Never touch the FLEET.** The gs-worker fleet is a separate system; this box does not operate it.
- **Never delete `state/tasks/*` or `state/*` files** to "clean up" — requeue/resolve instead.
- **Report what you did**: echo the command and its real output. If it errored, say exactly that.
