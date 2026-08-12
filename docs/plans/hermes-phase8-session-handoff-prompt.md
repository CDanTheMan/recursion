# Recursion / Hermes Phase 8 — continuation prompt

Paste this whole file as the opening message of a new session.

---

You are continuing work on the **Recursion control plane** (`recursion` repo, deployed at
`/opt/recursion` on the box reachable as `ssh gs-recursion`). Lucas is the operator.

**This prompt contains no state on purpose.** Every count, hash, branch name and "current gate"
would be wrong within a day, and a stale number reads exactly like a working one. A previous
handoff baked in a state block and every line of it was false within four sessions. Boot by
measuring.

## Read first, in this order

1. `CLAUDE.md` at the repo root — the operating rules. Rules 1–3 are load-bearing and Lucas
   enforces them: never force-push, never merge to a protected branch, and **never modify config,
   auth, model selection, cron entries, or `.env` autonomy flags** — those are his, including
   turning autonomy *down*.
2. `docs/plans/hermes-project-pilot-phase8-handoff.md` — the running record. **Newest sections are
   at the end.** Read backwards from the end until you have the current picture.
3. `docs/plans/hermes-phase8-preflight-operational-nuances.md` — the trap list. Every entry cost a
   real failure, several of them in production. Read all of it. It is short.

## Boot — measure, never assume

```sh
ssh gs-recursion

R=/opt/recursion
git -C $R rev-parse --abbrev-ref HEAD && git -C $R log --oneline -1
git -C $R fetch origin --quiet && git -C $R log --oneline -1 origin/master
# ^^ PRODUCTION IS FREQUENTLY BEHIND origin/master. A merged fix is not a deployed fix.
#    Production tracks loop/auto; master reaches it by an explicit gated merge, never a pull.

sha256sum $R/state/PAUSE            # file ABSENT means execution is LIVE. Check before anything.
systemctl is-active hermes-actuator hermes-gateway cron
systemctl show hermes-actuator -p NRestarts --value
crontab -l | grep recursion-

for d in pending running legacy succeeded failed; do
  printf '%-10s %s\n' "$d" "$(ls $R/state/decision-queue/$d 2>/dev/null | wc -l)"
done
wc -l $R/state/decisions.jsonl $R/state/events.jsonl
ls $R/state/plans $R/state/pilot-windows 2>/dev/null
grep -l '^status: open' $R/state/instructions/*.md
python3 -c "
import json, glob
for f in sorted(glob.glob('$R/state/pilots/*.json')):
    v = json.load(open(f))
    print(v['id'], v['concurrency_limit'], v['budget']['max_inflight_workers'])"

# Is anything wedged? This exact shape is the signature: an identical line repeating on a
# fixed interval. It has happened three times and each time it ran until stopped by hand.
grep -c 'recovery failed' $R/loop/logs/$(date -u +%F)-conduct-hermes.log
tail -20 $R/loop/logs/$(date -u +%F)-decide.log
git -C $R status --porcelain
```

A dirty worktree in `state/` is normal — the loop writes there. Compare it against what the
handoff records as the expected dirty set rather than treating any diff as an incident.

## The work

The project is an **ordered gate sequence**, defined in the handoff doc under *"Remaining gates
after hardening deployment"*: deploy hardening → resume cron → install the actuator → configure
model/capacity limits → synthesize and approve one pilot plan and window → remove PAUSE for that
one soak → observe, close, reassert safe state.

**Do not collapse two gates into one authorization.** Determine which gate is open by reading the
doc's newest sections and then measuring — never by trusting a summary, including this one.

Gate 6 removes PAUSE. It is the first step where a mistake actually runs something. Do not start
it without Lucas present and unhurried.

## Only Lucas can do these

- Push and merge. You publish review branches; he merges on GitHub. Never `git push` from a
  session shell.
- Cron entries, `.env`, autonomy flags, model selection, credentials.
- The three authenticated Telegram instructions gate 5 needs. `require_lucas_instruction` checks
  `principal` and requires `routing_target: head-hermes`, so **approval and window instructions
  go to Head Hermes / #general**, not a project topic. The *goal* instruction goes to the project
  topic so it routes to that project's pilot — but `route_for` forwards a message to head-hermes
  if it contains words like merge, deploy, policy, priority, pause, or "approve plan", and a
  head-routed turn cannot emit `actor=pilot-*`.
- Anything in-game, and anything that spends money.

## Working discipline that has repeatedly paid for itself

**Every production mutation gets:** a compare-and-swap gate asserting the exact pre-state, a
root-owned `0700` backup taken *before* the first write, an armed `ROLLBACK.sh`, and a
post-condition that checks **exact values**, not shapes. A malformed cron line passed three
structural checks — "one line changed", "no longer shares a minute", "still five lines" — and
only full-value equality caught it. Back up each mutated object separately so a partial failure
can be partially reverted.

**Simulate first.** Merges are rehearsed in a throwaway clone and compared by **blob OID**, not
file hash, so no line-ending filter can launder a mismatch.

**Contain before diagnosing.** A wedged retry loop gets the service stopped first; it mutates
nothing and buys unlimited thinking time. Under PAUSE, a stopped actuator costs nothing.

**Prove isolation before the first write.** A copied directory is not a sandbox: `.env` re-exports
`RECURSION_ROOT`, and "sandbox" runs enqueued ten decisions into production. Verify `ROOT` and
`RECURSION_ROOT` agree before writing anything. There is now an audit assertion for this, but the
discipline is the point.

**Every new assertion must be run against the pre-fix bytes and observed to FAIL.** One check
passed vacuously because the string it searched for wrapped across two `echo` lines. Checkers that
spell out the pattern they search for match their own file — this bit `pgrep`, the `$HOME` audit,
and nearly the `.env` audit.

**Do not publish a guessed mechanism.** "This is broken" and "here is why" are separate claims
with separate evidence bars. Two confident root causes this session were wrong — lock contention
that was actually an unset `HOME`, and a self-deadlock that did not exist. Both were labelled
inferred, which is the only reason they did no damage. `bash -x` answered in one line what an hour
of reading the code did not.

**Replay the real failing artifact** rather than building a fixture for it; a fixture carries
whatever the author thought was normal and usually passes. And when a replay fails, check whether
the *harness* or the *subject* failed before quoting the error.

## The shape of nearly every defect found here

The machinery is exact and the prompt that drives it is approximate. Repeatedly: a validator
enforced a literal the prompt never stated, and the rejection happened downstream, silently, long
after the model finished — presenting to Lucas as "Hermes ignored me". `phase8-green` now reads
required keys and enum values out of `validate_plan`'s own AST and fails if the prompt omits them.
**When you change a validator, grep the prompts.** When something "ignores" an instruction,
suspect a silent downstream refusal before suspecting the model.

Also: a *service* environment is not a login environment. systemd supplies no `HOME`, and under
`set -u` that killed a script entirely — invisible to every test, because no test ran without it.

## Open items to check, not to trust

- Whether the newest review branch is merged, and whether **production has been deployed to it**.
- The last regression suite result — it runs ~28 minutes; confirm `DONE` and all phases `RC=0`
  rather than assuming.
- Four autonomy flags in `.env` (`ALLOW_PUSH`, `AUTO_DRAIN`, `AUTO_PLAN`, `AUTO_REFLECT`). They
  are PAUSE-gated today but resume the full autonomous loop the moment PAUSE lifts. Lucas has been
  asked several times and has not given an explicit answer. **Do not flip them.**
- `hermes-actuator` boot persistence — check `systemctl is-enabled`.
- A permanent stub-model test for the decide retry exists only as a manual proof in a commit
  message. Making it a real test is the top open follow-up.

## How Lucas works

He merges on GitHub Desktop and will tell you when it is done. He wants findings stated plainly,
including your own mistakes, and he will keep going for a long time — say so if a step should wait
for a fresh session rather than proceeding because he asked. When he authorizes something, the
authorization is for that thing, not the category.
