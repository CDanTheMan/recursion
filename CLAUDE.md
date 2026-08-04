# Operating rules — Recursion

This repo supervises other work. Agents operating here have write access to state that
other systems read. Treat mistakes as expensive.

Read `ANCHOR.md` before any planning task.

## Hard rules

1. **Never `git push --force`.** Under any circumstance, in any script, for any reason.
2. **Automated runs commit to `loop/auto` only.** Never to `main`. Never merge.
3. **Never modify your own config, auth, model selection, or cron entries.** If something
   looks misconfigured, write the finding to `state/INBOX.md` and stop.
4. **No secrets in tracked files.** Credentials live in `.env` (gitignored). If you find a
   secret committed, stop and report — do not attempt to rewrite history.
5. **Never modify files under `state/projects/`.** Those are copies pushed from product
   repos. Read only.

## Escalate, don't guess

An agent proceeding confidently past ambiguity is the main failure mode here. Stop and
write to `state/INBOX.md` instead of choosing when:

- A task could be interpreted two materially different ways
- Completing it requires a decision not recorded in `DECISIONS.md`
- A source conflicts with something in `research/`
- A physics answer can't be verified against a known-solution source

A stopped job with a clear question beats four hours of plausible wrong work.

## Bounded output

The morning brief is **one page**. Hard cap.

Generating more material than can be reviewed creates a backlog, not progress. When there's
more to say, prioritize and drop the rest — do not append.

Problem sets: 3–6 problems, targeting current gaps. Not comprehensive coverage.

## Physics-specific

- **Ground on verified problems.** Source from real problem sets with known solutions.
  Generate *sequencing*, not problems, unless explicitly asked.
- **Do not deliver solutions on request.** The struggle is the point. Hints escalate in
  stages; full solutions only after a genuine attempt exists in the log.
- Run dimensional analysis and limiting-case checks on any derivation before presenting it.
- If confidence in a physics claim is low, say so in-line. Confident wrong physics is the
  worst possible output of this system.

## Style

Plain markdown. No decorative headers. Dates as `YYYY-MM-DD`. Keep files skimmable —
anything not reread is dead weight.
