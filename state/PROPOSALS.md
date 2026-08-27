# Recursion — self-improvement proposals (human-review queue)

Reflect.sh appends; a human applies or rejects. NOTHING here is auto-applied (CLAUDE.md rule 3).
[APPLY-SAFE] = low-risk, likely-approve. [NEEDS-APPROVAL] = touches config/auth/model/cron/gate/spend/mining.

## 2026-08-05 20:28 — [NEEDS-APPROVAL] Add a native-diff numeric acceptance gate for GSC frontier tasks
status: DONE 2026-08-05 — built as scripts/gsc-nativediff-gate.sh (commit 8a6755f); baseline state/gsc/nativediff-baseline.tsv; roadmap state/roadmaps/gsc-renderer.md

[NEEDS-APPROVAL] Add a native-diff numeric acceptance gate for GSC frontier tasks
**Evidence:** “GSC corpus deployed; conformance is COMPLETE” says 211 tests yield 206 pass, 0 FAIL, 5 skip and explicitly identifies native-diff quality as the frontier requiring “a NUMERIC acceptance gate (error must strictly decrease + a control reproducing the old golden).”
**Change:** Human to design and approve a native-mesh error baseline/control and strict-decrease gate, then add its task-planner integration under the GSC overnight workflow.
**Fitness:** Reduces GSC native-diff error and restores productive build-loop work without re-running already-green conformance tasks.
**Risk:** Changes acceptance gates and task selection; baseline design could reward misleading aggregate improvements, so it requires human approval.

## 2026-08-06 — [NEEDS-APPROVAL] Turn OFF autonomous merge to the default branch
status: OPEN — awaiting a human to flip the flag (rule 3: the loop cannot flip its own)

**Evidence:** `RECURSION_ALLOW_AUTOMERGE=1` is live in `.env`. `chiron-001` and `chiron-003`
are `status: passed` with `automerge: yes` / `automerge_scope: apps/chiron`, so
`work.sh integrate_remote` (and `publish.sh`) will ff-push `loop/work/<id>` straight to the
default branch on the next qualifying run.

**Conflict:** this contradicts (a) Lucas's 2026-08-06 directive — the loop may commit and push
branches but never merge to main, everything ships as sequential review branches — and
(b) `CONTROL_PLANE.md` invariant 4, "no autonomous merge to a protected or default branch."

**Change (human):**
1. Set `RECURSION_ALLOW_AUTOMERGE=0` in `/opt/recursion/.env`.
2. Drop `automerge: yes` + `automerge_scope:` from `state/tasks/chiron-00{1,3}.md`.
3. Confirm branch protection on the default branch of every repo the box holds a write key
   for: `recursion` (default is **master**, not main), `golden-stallion-client`, `chiron`,
   `guerra-construction-group`, `santa-clara-construction`.

**Why the flag alone is not enough:** the box now holds WRITE deploy keys for seven repos. A
write key can push anywhere the repo allows, so GitHub branch protection — not an env flag —
is the actual enforcement. The flag stops *our* code path; protection stops *any* path.

**Risk of applying:** none to correctness — it only removes an autonomous write. The chiron
chain will publish review branches instead of self-merging, which is the intended model.

## PROPOSAL 2026-08-06 — point notifications at The Cockpit (two human-only steps)

The routing code is merged and tested; it is INERT until both of these happen, and it fails safe
in the meantime (every message goes to the current chat, exactly as before).

**1. Grant the bot topic rights.** ~~DONE 2026-08-06~~ — Lucas promoted @recursion_manager_bot to
administrator, `topics.sh ensure` created all eight topics (recursion=3, golden-stallion=4,
golden-stallion-extension=5, golden-stallion-client=6, ai-investment-cockpit=7,
edgar-morning-brew=8, guerra-construction-group=9, chiron=10), the ids are in
`state/portfolio.tsv`, a second `ensure` created 0, and `check` verifies all eight.
Routing was confirmed end-to-end on BOTH delivery paths: the API reports the message landing in
`message_thread_id: 10` of "The Cockpit".

**2. Add two lines to `.env`** (a human edits .env — CLAUDE.md rule 3):

    RECURSION_TELEGRAM_CHAT=-1003894008732
    RECURSION_TELEGRAM_HOME_THREAD=1

`TELEGRAM_CHAT_ID` is currently `8913126684`, which `getChat` reports as `type=private` — a DM,
not the supergroup. Leave it: it stays the fallback, so nothing that works today stops working.

**Why not just change .env myself:** it is the one file the loop may never edit, because it holds
the flags that decide what the loop is allowed to do. That rule is worth more than the
convenience of skipping this note.

**Falsifier:** after both steps, a build message from a chiron task should appear in the `chiron`
topic and not in General. If it lands in General, the registry has a topic id that `message_thread_id`
is not receiving.

## 2026-08-26 — [NEEDS-APPROVAL] Declarative engine plugins (Cursor / Gemini / OpenCode / Sentry-local)
status: IN AUTHORING — Lucas approved the scope in-session (D-015 draft); implementation on a review branch

**Evidence:** worker plane supports only `claude` and `hermes`; `deepseek|openrouter` exit 91
("no file tools — needs a file-emission protocol"). Subscriptions are moving; Lucas wants
Cursor + ChatGPT as the drive pair and a toggle-able local Qwen arm on the Sentry PC.
**Change:** engine manifests under `scripts/engines/`, fail-closed `resolve-engine.py`,
generalized model aliases, generic sandbox exec path, availability-probe requeue.
Full plan: `docs/plans/engine-plugin-architecture.md`.
**Fitness:** engines/models become human-owned configuration; September reshuffle needs no code.
**Risk:** touches `work.sh`/`worker-sandbox.sh` (protected paths). Mitigated: builtin paths
byte-identical, plugins inert until `.env` flags a human sets, red controls before green.
**Human steps after merge:** box CLI/flag verification, provider-allowlist entries, `.env`
enable flags + alias values, Sentry server + tunnel (deployment section of the plan).
