---
name: recursion-status
description: "Answer 'what is the Recursion box doing?' from ground truth via the recursion CLI — never guess."
version: 1.0.0
author: Recursion (agent-created)
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [Recursion, Status, Supervision, Ground-Truth, Ops]
    related_skills: []
---

# Recursion box status

This agent runs as root **on the Recursion control-plane box** (`/opt/recursion`), a meta-supervisor
that runs a build-loop, a daily brief, and a self-reflection tier. When the user (Lucas) asks
anything like *"what's the box doing?"*, *"status"*, *"how's chiron / the golden-stallion-client
renderer going?"*, *"any escalations?"*, *"what did you build?"* — you answer from **live CLI output,
never from memory and never a guess.** A wrong status costs trust; an honest "the command returned X"
never does.

## When to Use

- Lucas asks for the status of the Recursion box, the build-loop, chiron, or the GSC renderer.
- Lucas asks what's queued, what's building, what needs a decision, or what was recently learned.
- Any "is it still running / did it work / what happened overnight" question about this box.

## How (run these with the terminal tool, then REPORT THE ACTUAL OUTPUT)

The `recursion` CLI is on PATH. Run what the question needs; do not run all of them blindly:

- `recursion board` — the live build-loop registry: what's running now, needs a decision, awaiting review.
- `recursion inbox` — escalations waiting on Lucas (the "needs a decision" queue).
- `recursion proposals` — the self-improvement queue (things reflection proposed; a human applies).
- `recursion lessons` — durable operational lessons the box has learned.
- `recursion brief` — the latest daily brief (one page).
- `recursion tasks` — the task queue, optionally `recursion tasks <status>`.
- `recursion pilot status <project>` — scoped live task/run/git evidence for any registered project.

Project-specific legacy details (use only after the scoped pilot status above):
- **Chiron** (a Next.js app the build-loop is building): its progress is the checklist in
  `state/roadmaps/chiron.md` — run `grep -n "^- \[" /opt/recursion/state/roadmaps/chiron.md`
  (`[x]` done, `[~]` planned/in-flight, `[ ]` not started). The built branch is `loop/work/chiron-001`.
- **golden-stallion-client (GSC) renderer**: two gates. Conformance (regression) — genuine passing
  count is `wc -l < /opt/recursion/state/gsc/baseline-pass.txt`. Quality (native-diff) — per-world
  Σ|per-slot triangle error| baselines in `/opt/recursion/state/gsc/nativediff-baseline.tsv` (lower
  is closer to native). Frontier queue: `state/roadmaps/gsc-renderer.md` (geometry axis only).

## Rules

- **Report the command's real output.** If a command errors or is empty, say exactly that.
- Is the box paused? `ls /opt/recursion/state/PAUSE` (present = halted). Mention it if so.
- Keep it short — a few lines, like the brief. Lead with anything that needs Lucas's decision.
- Do **not** run `recursion pause/resume/work/drain/reflect/dispatch` or edit any file when merely
  **reporting** status. Reporting is read-only. Acting is a separate, explicit request.
