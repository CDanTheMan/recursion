# INBOX — questions and escalations requiring a human decision

(reset 2026-08-12 for first production launch on Lucas's instruction; pre-Hermes content archived at /var/backups/recursion/pre-launch-scrape-20260812T075324Z)

## [esc-0004] 2026-08-12 12:15 — Supply the first Fall 2026 physics lecture block so the lead can be scheduled
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: Fall 2026 table contains only the `_fill from actual syllabus once posted_` placeholder; ANCHOR sets Berkeley start at 2026-08-26 and a three-week lead target
**Blocked on:** the course/topic and first lecture date from the actual syllabus
**Context:** lead, target dates, and the pause-new-blocks rule cannot be evaluated without a real lecture block
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available

## [esc-0005] 2026-08-12 15:15 — Supply the first Fall 2026 physics lecture block
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; ANCHOR sets Berkeley start at 2026-08-26 and a three-week lead target.
**Blocked on:** the course, topic, and first lecture date from the actual syllabus.
**Context:** lead, target dates, and the pause-new-blocks rule cannot be evaluated without a real lecture block.
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available.

## [esc-0006] 2026-08-13 09:15 — Supply the first Fall 2026 physics lecture block or defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; CURRENT INBOX `esc-0004` and `esc-0005` identify the same unresolved blocker.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead; syllabus rules require pausing new blocks if lead falls below one week. Neither can be evaluated without the first block.
**Options:** provide the official syllabus; provide the first course/topic/date only; explicitly defer physics scheduling until the syllabus is available.

## [esc-0008] 2026-08-14 15:15 — Supply the first Fall 2026 physics lecture block or explicitly defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; CURRENT INBOX esc-0004 through esc-0006 record the same unresolved blocker.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead; syllabus rules require pausing new blocks below one week. Neither can be evaluated without the first block.
**Options:** provide the official syllabus; provide the first course/topic/date only; explicitly defer physics scheduling until the syllabus is available.

## [esc-0009] 2026-08-15 18:15 — Provide the first Fall 2026 physics lecture block or explicitly defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice: the Fall 2026 table contains only `_fill from actual syllabus once posted_`; CURRENT INBOX esc-0004, esc-0005, esc-0006, and esc-0008 are duplicate unresolved instances.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead; the syllabus rule requires pausing new blocks below one week. Neither can be evaluated without the first block.
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available.

## [esc-0010] 2026-08-18 06:15 — Provide the first Fall 2026 physics lecture block or defer scheduling
**Workstream:** physics-coursework
**Pointer:** SYLLABUS LEAD ledger slice contains only `_fill from actual syllabus once posted_`; CURRENT INBOX esc-0004, esc-0005, esc-0006, esc-0008, and esc-0009 are duplicate unresolved instances.
**Blocked on:** the course, first topic block, and first lecture date from the actual syllabus.
**Context:** ANCHOR requires a three-week lecture lead, and the syllabus rules require pausing new blocks below one week. Neither can be evaluated from the current ledger.
**Options:** provide the official syllabus; provide only the first course/topic/date; explicitly defer physics scheduling until the syllabus is available.

## [esc-0002] 2026-08-29 — May a v2 acceptance gate have side effects?
**Workstream:** recursion-v2 execution fabric
**Pointer:** `scripts/validate-gate.py` (Phase 2, `codex/v2-adapters` @ `33fb08c`);
`scripts/tests/hermes-pilot-phase5-red.test.sh:411` (Phase 5, `codex/v2-cursor-runtime`);
measurement `tmp/integ-p2c` = `8056ace`.
**Blocked on:** a decision on whether an acceptance gate may mutate state, which is not recorded in
`DECISIONS.md`. D-009 governs the GSC native-diff gate and does not speak to this.

**Context.** Phase 2 closed a reviewed blocker by deleting four non-strict relaxations, so direct commands
now run one validator and one grammar in both modes. That closure is correct on its own terms — the same
relaxations were admitting `bash -c true`, `python3 -c true`, `env test -s app/a` and `../outside.sh`.

It also refuses one acceptance command that bare WIP accepted. Phase 5's heavy-contention arm declares:

```
mktask heavy-contention "test -s app/heavy.txt && touch $HEAVY_GATE_MARKER"
```

Measured, each validator run inside its own checkout:

```
bare WIP a84525d   default (non-strict)   rc=0  ACCEPTED
bare WIP a84525d   --strict-direct        rc=2  refused
Phase 2  33fb08c   --legacy-compound      rc=2  refused
Phase 2  33fb08c   --strict-direct        rc=2  refused
```

`touch` was never in the strict grammar; the non-strict relaxation is what admitted it. Consequence at
`tmp/integ-p2c`: `phase5-red` and `phase5-green` each fail one assertion, `contended heavy gate did not fail
closed (rc=0 status=escalated gate=held)`. Serial repeat, n=10: `pass=0 fail=10`. Deterministic, not a race.
Phase 2 is otherwise 10/12 with all three of its own suites green.

**Why this is not mine to choose.** The command is not vacuous — its decisive element is `test -s
app/heavy.txt`, and the `touch` is the harness's probe for whether the gate body executed. So the vacuity
argument that justifies refusing bare `touch` does not reach this compound. Deciding it sets the contract for
what an acceptance gate *is*, which is the central safety mechanism of the fabric. I already made one wrong
unilateral call on this exact surface: I required `test -s app/result.txt && touch C:/phase5-marker` to keep
passing, a writer widened the grammar to obey, and bare `touch` became an admissible gate. I am not
repeating that.

**Options.**
- **A — gates are predicates.** Keep the refusal. Phase 5's fixture stops using the gate as instrumentation
  and observes execution another way. Cleanest contract; requires editing another phase's red fixture.
- **B — constrained mutation.** Re-admit `touch` only as a non-leading element of a compound whose leading
  element is a real test, operand required and confined to declared paths, never absolute. Phase 5's marker
  moves inside the workspace. Preserves both intents; re-opens a side-effect surface.
- **C — leave it.** Phase 2 and Phase 5 cannot both be accepted, and the ordered integration stalls at
  step 2.

**Recommendation: B**, because it satisfies the vacuity argument in full (bare and absolute `touch` stay
refused) without asserting a gate-contract change that nothing in the control plane records. But B still
touches both phases, so it wants a human yes.

**Not blocking other work.** Phases 3, 4, 5, 6/7 and 8 continue; this surfaces only when Phase 2 and Phase 5
integrate together.

### Update 2026-08-29 — independent confirmation, and one misleading label

An independent adjudicator was asked the bounded question "is this a Phase 2 defect or the gate
contract?", explicitly forbidden from resolving this escalation. It returned the contract reading,
with evidence I then re-verified myself.

```
base a84525d and 33fb08c^   `test -s app/heavy.txt && touch <marker>`   exit 0
33fb08c                     same command    exit 2  ERR bare acceptance launcher is not admitted: touch
base a84525d and 33fb08c    `test -s app/heavy.txt`  (pure predicate)   exit 0, identical acceptance_sha256
git diff 33fb08c^ 33fb08c -- scripts/work.sh scripts/capacity.sh   -> no heavy-lock change
```

**The failure line is misleading and should not be read literally.** The fixture prints

```
gate=$([ -e "$HEAVY_GATE_MARKER" ] && echo ran || echo held)
```

so `gate=held` means the marker was NOT created, which is the desired outcome. It says nothing
about the capacity lock. In the observed failure `rc=0 status=escalated gate=held`, only `rc` and
`status` are wrong: validation refuses the gate terminally before a worktree is leased, so
contention is never reached. Phase 2's contention path is untouched and sound.

This does not change the options or the recommendation. It removes the possibility that B is
being recommended to paper over a real fail-closed defect: there is no such defect.

Still needs a human yes. Phase 5 is now at 15/15 with its race suite at 10/10, so A and B both
cost real rework on an otherwise-clean phase.

### Update 2026-08-29 (late) â€” the discriminating arm ran, and it changes what option A costs

The experiment the previous update marked pending has now executed on the Linux lane. Same
fixture, same ref, everything identical except the one gate command:

```
P2PURE ref=origin/tmp/integ-p2c sha=8056ace
--- arm A: unmodified fixture ---
    gate: mktask heavy-contention "test -s app/heavy.txt && touch $HEAVY_GATE_MARKER"
    FAIL  contended heavy gate did not fail closed (rc=0 status=escalated gate=held)
--- arm B: pure predicate, everything else identical ---
    gate: mktask heavy-contention "test -s app/heavy.txt"
    ok    contended heavy gate defers without executing unlocked
```

This confirms the contract reading by execution rather than by argument: with a pure predicate,
Phase 2's heavy-contention deferral works. The gate command is the whole difference.

**The causal chain, stated exactly.** Arm A does not fail on the marker. It fails on the other
three conditions in the assertion:

```
[ "$heavy_rc" = 75 ] && [ status = running ] && [ -d worktree ] && [ ! -e "$HEAVY_GATE_MARKER" ]
        arm A: rc=0, status=escalated      -> two conditions false
        arm B: rc=75, status=running       -> all true
```

Phase 2 refuses the side-effecting gate at admission, so the task escalates instead of deferring,
and the deferral behaviour never gets a chance to be observed. The marker was never the issue.

**What this newly reveals, and it argues against a naive option A.** Under a pure predicate,
nothing in the fixture creates `$HEAVY_GATE_MARKER`, so `[ ! -e "$HEAVY_GATE_MARKER" ]` is
trivially true. Arm B passes partly on a condition that can no longer fail. Deleting the `touch`
therefore does not preserve the assertion â€” it silently converts the non-execution witness into a
tautology, which is the fabricated-value vacuity form this effort exists to eliminate.

So option A is not "edit one fixture line". It is "re-engineer how the harness witnesses that a
contended gate body did not execute, without using the gate to instrument itself" â€” plausibly from
controller run state or the worker log rather than a gate-created file. That is real work in
another phase, and it is the kind of change that can quietly weaken a red suite if done casually.

**Recommendation unchanged: B**, and the new evidence raises my confidence. B keeps the witness
mechanism intact while satisfying the vacuity argument in full â€” bare `touch` and absolute paths
stay refused. Option A remains legitimate but now carries a visible cost that should be priced in
before it is chosen, not discovered afterward.

**Still not mine to decide.** The evidence now says clearly *what each option costs*. It does not
say which contract the fabric should have, and that is not recorded in `DECISIONS.md`. Phase 2
stays blocked and the ordered integration still stalls at step 2 until a human answers.

Everything else continues to move: Phase 6/7 is 15/15 with both mutation proofs holding, Phase 8's
race rates are 10/10 and 10/10, Phase 5's are 10/10 and 10/10, and Phases 3 and 4 have fresh
remediations under gate.


## [esc-0003] 2026-08-29 — Are non-Git controller deployments supported?
**Workstream:** recursion-v2 execution fabric
**Pointer:** `scripts/provider-proxy-service.py:24-33`, `scripts/provider-network.sh:21-25`,
`scripts/worker-sandbox.sh:824-831` (Phase 5, `codex/v2-cursor-runtime` @ `da5e687`).
**Blocked on:** whether a controller that is not a Git checkout is a supported deployment. Not
recorded in `DECISIONS.md`.
**Not blocking Phase 5.** Failing closed is the defensible default and the documented deployment
satisfies it. This wants a decision, not a hold.

**What changed and why.** An independent review found that the builtin provider path invoked
`provider-egress.py` with no controller provenance, so egress read the live registry and a
changed-but-valid registry chose a different namespace and proxy port at rc=0:

```
baseline rc=0  namespace=recursion-provider-anthropic  proxy_port=18080
mutated  rc=0  namespace=attacker-netns                proxy_port=1234
```

The fix derives provenance from the controller checkout when no resolver plan carries it, and
passes it unconditionally. A second independent review confirmed by execution that this works —
egress genuinely honours the pin rather than merely accepting it:

```
pinned baseline                       rc=0  namespace=pinned-a proxy_port=19080
live registry mutated, pin unchanged  rc=2  "provider profile registry differs from controller commit"
registry restored                     rc=0  committed namespace/port
```

**The cost.** Deriving provenance means running `git -C "$ROOT" rev-parse --verify HEAD`. Where
that cannot answer, the path now refuses at rc=96 instead of using the local registry:

```
non-Git controller root      rc=96   (parent resolved the local registry without Git)
git absent from PATH         rc=96
unborn HEAD                  rc=96
detached HEAD                works
shallow / grafted checkout   works when HEAD and the tracked registry object are present
```

**The question.** If a packaged, non-Git controller is a supported deployment, this is an
availability regression and needs a supported authenticated packaging path instead. If the
controller is always a Git checkout — the documented systemd service uses a root-owned
`/opt/recursion` — then failing closed is correct and this note only needs recording.

I am not choosing. Refusing to route provider traffic under unauthenticated policy is the right
default and I have left it in place, but "the previous behaviour was more available" is not
something I should silently trade away on a security seam.

**Related, recorded not escalated.** The same review notes the fix relocates trust rather than
eliminating it: `RECURSION_ROOT` is caller-selectable, so a party who controls the root controls
the commit and the registry together. Under the documented threat model — root-owned checkout,
`/etc/recursion/provider-egress.env`, unprivileged workers — that party is already privileged, so
the original live-registry drift is closed. Independently authenticating the root choice is a
larger change than this phase, and it is called out here so it is a known limit rather than an
assumption.

### esc-0002 RESOLVED 2026-08-29 by Lucas — option A, gates are pure predicates

Decision received: **an acceptance gate evaluates, it does not mutate.** Phase 2's refusal stands.

`state/DECISIONS.md` is a protected path and this executor does not write it. A formal D-entry
recording the gate contract is a human action and is still outstanding; this note is the record of
the decision as given, not a substitute for it.

**What changes.** Phase 5's heavy-contention arm stops using its own acceptance gate as
instrumentation:

```
before  mktask heavy-contention "test -s app/heavy.txt && touch $HEAVY_GATE_MARKER"
after   mktask heavy-contention "test -s app/heavy.txt"
```

**The witness must move, not disappear.** Under a pure predicate nothing creates
`$HEAVY_GATE_MARKER`, so `[ ! -e "$HEAVY_GATE_MARKER" ]` becomes trivially true and the
non-execution check silently becomes a tautology — the fabricated-value vacuity form. Deleting the
`touch` alone is NOT the fix.

The replacement already exists in the same fixture, twice. `heavy-retry` and `pause-after-terminal`
both witness execution from the **worker body**, which is not a gate and is not subject to the gate
grammar:

```
RETRY_LAUNCHES="$TMP/heavy-retry-launches"
run_case heavy-retry "n=$(wc -l < $RETRY_LAUNCHES 2>/dev/null || echo 0); n=$((n+1));
                      echo \"launch $n\" >> $RETRY_LAUNCHES; ..."
...
heavy_retry_launches="$(wc -l < "$RETRY_LAUNCHES" 2>/dev/null || echo 0)"
```

So the heavy-contention witness becomes a launch count from the worker body rather than a marker
written by the gate. That is arguably a stronger assertion: under contention the controller should
defer *before* launching the worker at all, so `launches=0` states the intended invariant more
directly than "the gate body did not run".

**Where the change lands: Phase 2's branch, not Phase 5's.** Phase 2 integrates first, and its
grammar change is what makes the current fixture unadmissible. If the fixture fix lived on Phase
5's branch the cumulative gate would fail at integration steps 2, 3 and 4 and only recover at step
5. The grammar change and the fixture that depends on it belong in the same commit.
`hermes-pilot-phase5-red.test.sh` is on the P3/P5 merge surface, so both later merges must carry
this forward — recorded as a post-merge assertion.

**This reverses my earlier recommendation, on evidence.** I recommended option B twice, on the
grounds that A required re-engineering the non-execution witness. That cost was real but I had not
checked whether the mechanism already existed. It does, in the same file, in two places. With the
cost gone, B's only advantage went with it — and B would have reopened the exact surface where I
previously made a wrong unilateral call, requiring `touch C:/phase5-marker` to keep passing until a
writer widened the grammar and bare `touch` became an admissible gate.

**esc-0003 remains open** and does not block: whether a packaged non-Git controller is a supported
deployment. Failing closed stays in place meanwhile.

## esc-0004 â€” an active project with a paused pilot fails the Phase 4 audit (2026-08-30)

**Status:** open, human decision required. Does not block the v2 integration.

`scripts/audit/hermes-pilot-phase4-green.sh` exits 4 before its first assertion, on line 28:

```
RECURSION_ROOT="$SRC" python3 "$SRC/scripts/project-pilot.py" verify-registry
project-pilot: project pilot golden-stallion-client is not active
```

The state it is reporting:

- `state/project-config/golden-stallion-client.json` -> `"status": "active"`
- `state/pilots/pilot-golden-stallion-client.json`   -> `"status": "paused"`, with

```
"pause_reason": "Phase 0: the source-bound GSC pilot is stale and must be explicitly
                 rebound through a new immutable assignment before any resume."
```

`verify-registry` requires every tracked active project to have an active pilot, so it refuses. The
audit is correct; the repository is internally inconsistent.

I previously carried this as an inherited environment condition because it reproduces at `a84525d`.
That was wrong: reproducing at the base only establishes that no phase introduced it, not that it is
benign. The failure is a true statement about control state.

**Two resolutions exist and both are control-plane decisions:**

- **A.** Set `state/project-config/golden-stallion-client.json` to `paused` so the project matches
  its pilot. Consistent, but it changes the recorded status of a live project.
- **B.** Change `verify-registry` to accept a paused pilot for an active project, on the grounds
  that pausing a pilot is a normal operational state rather than a registry defect.

I am not choosing. A is a control-plane state edit; B changes what the registry invariant means.

**Not in scope to fix here, and specifically must not be "fixed" by the merge.** Phase 5's branch
predates the pause and still carries that pilot as active. I verified the merge outcome rather than
assuming it:

```
merge-tree(tmp/integ-all, codex/v2-cursor-runtime):state/pilots/pilot-golden-stallion-client.json
  -> 2a7268f828   (paused)
```

Phase 5's blob is identical to the phases' common ancestor `9c7a42c`, so the pause is a one-sided
change and survives the merge without a conflict. Any future merge that resumes this pilot as a side
effect is a defect, not a resolution of this escalation.

Until this is answered, `hermes-pilot-phase4-green.sh` is expected to fail on this line and stays
visible in every gate summary rather than being suppressed.

