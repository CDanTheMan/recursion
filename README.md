# Recursion

The meta layer. This repo does not build products — it supervises the repos that do,
tracks decisions, and runs the learning loop.

**Not** part of Golden Stallion or CSL Labs. Those push status *into* here; this repo
never reaches into them.

## Layout

| Path | Churn | What it is |
|---|---|---|
| `ANCHOR.md` | Yearly | Success criteria, what's explicitly not happening, kill criteria |
| `CLAUDE.md` | Rare | Operating rules for any agent session in this repo |
| `research/` | Stable | Deep research reports + "what this changes" notes. Git history here is valuable |
| `state/` | Nightly | Decision log, gap map, per-project status. Snapshotted once daily, not per-change |
| `curriculum/` | Weekly | Syllabus map, generated problem sets |
| `loop/` | Rare | Supervisor scripts, prompts, routing config |
| `scripts/` | Rare | Setup and maintenance |

## The three modes

1. **Build** — Claude Code in the product repos. Each writes its own `STATE.md`; a copy lands in `state/projects/`.
2. **Decide** — `state/DECISIONS.md`. Every call gets a falsifier. Reviewed on a cadence.
3. **Learn** — `curriculum/`. Ingest → solve → re-explain. The re-explain checkpoint is the gate.

## Running the loop

```bash
# one-time
cp .env.example .env        # fill in, never commit
bash scripts/install-cron.sh

# manual run
bash loop/supervisor/run.sh morning
```

The supervisor commits to `loop/auto`. You merge to `main`. A bad night is a branch
you delete.

## Status

Proof of concept, August 2026. Kill criteria in `ANCHOR.md`. Decision due start of September.
