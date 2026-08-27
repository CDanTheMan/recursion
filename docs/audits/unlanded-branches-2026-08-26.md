# Unlanded branch audit — 2026-08-26

Reference point: `origin/master` = `0edeacb` (2026-08-25, "Merge pull request #76 from
NotSkittlz/agent/gateway-shutdown-regression"). No fetch was performed; this is the main
clone's current ref as of this audit.

Checkouts scanned (all are worktrees of one repo — `C:\Users\Lucas\Documents\GitHub\recursion`
— sharing one object store and refs, confirmed via `git worktree list`; none are independent
clones):

- `recursion` (main clone) — HEAD on `agent/model-alias-resolver-mode` at `81ffa37` (already
  merged into origin/master); local `master` = `origin/master` = `0edeacb`
- `recursion\.claude\worktrees\project-recursion-status-5e5ca5` — `claude/project-recursion-status-5e5ca5`, **ACTIVE, this session's own work** (7 commits ahead of origin/master, not audited as stale)
- `recursion-agent-contract` — `review/gate-socket-hardening`
- `recursion-agent-lifecycle` — `review/gsc-invalid-lifecycle`
- `recursion-agent-lifecycle-fix` — `review/gsc-lifecycle-race-hardening` (already merged)
- `recursion-agent-lifecycle-v2` — `review/gsc-lifecycle-race-hardening-v2`
- `recursion-agent-notify` — `review/gsc-notification-hardening`
- `recursion-agent-seed` — `review/gsc-terminal-hardening`
- `recursion-authority-descendant` — `agent/phase8-authority-descendant` (already merged)
- `recursion-exact-instruction-turn` — `agent/phase8-exact-instruction-hermetic` (already merged)
- `recursion-gateway-shutdown` — `agent/gateway-graceful-shutdown` (already merged)
- `recursion-gateway-shutdown-regression` — `agent/gateway-shutdown-regression` (already merged)
- `recursion-gsc-conformance-node24` — `agent/gsc-conformance-node24-reporter` (already merged)
- `recursion-gsc-v3-profile` — `agent/gsc-v3-profile-promotion` (already merged)

Local refs total 37 branches. 23 are ancestors of `origin/master` (already merged, incl. the
6 worktrees marked "already merged" above). 14 are not: this session's active branch plus the
13 unlanded ones audited here, all dated 2026-08-12/13. The 2026-08-12 audit apparently only
counted the 6 that had dedicated worktrees; 7 more unlanded branches exist as refs only,
checked out nowhere.

Method: for each unlanded branch, `git patch-id --stable` on every `origin/master..branch`
commit, compared against patch-ids of all `origin/master` commits since 2026-08-01. Non-exact
matches were checked by hand (author, author-date, subject, diffstat) against same-titled
master commits.

## Disposition

| branch | where | ahead | disposition |
|---|---|---|---|
| review/gsc-contract-core | main clone only (no worktree) | 1 | LANDED — safe to delete |
| review/gsc-terminal-hardening | recursion-agent-seed | 1 | LANDED — safe to delete |
| review/hermes-prompt-quote-guard | main clone only | 1 | LANDED — safe to delete |
| review/instruction-noop-evidence-recovery | main clone only | 1 | LANDED — safe to delete |
| review/phase8-routing-recovery | main clone only | 5 | LANDED — safe to delete |
| review/phase8-routing-recovery-handoff | main clone only | 1 | LANDED — safe to delete |
| review/provider-network-nsfs | main clone only | 1 | LANDED — safe to delete |
| review/gate-socket-hardening | recursion-agent-contract | 1 | SUPERSEDED — safe to delete |
| review/gsc-invalid-lifecycle | recursion-agent-lifecycle | 2 | SUPERSEDED — safe to delete |
| review/gsc-lifecycle-race-hardening-v2 | recursion-agent-lifecycle-v2 | 1 | SUPERSEDED — safe to delete |
| review/gsc-notification-hardening | recursion-agent-notify | 1 | SUPERSEDED — safe to delete |
| review/gsc-seed-verification | main clone only | 2 | SUPERSEDED — safe to delete |
| review/provider-only-capability | main clone only | 1 | SUPERSEDED — safe to delete |

No STILL WANTED branches and no genuine ambiguity: every unlanded branch's content is already
on `origin/master`. Dates for all 13: commits range 2026-08-12 08:36 to 2026-08-13 18:17
(local); one-liners below.

**LANDED** (exact `patch-id` match, commit-for-commit, safe to delete):
- `gsc-contract-core` (d0896f7, "Harden Phase 8 plan contracts") → landed as `84c6db5`
- `gsc-terminal-hardening` (ef195f7, "harden terminal goal grading and heavy-gate lock lifecycle") → landed as `737af9b`
- `hermes-prompt-quote-guard` (b29cded, "Fix Hermes prompt quote regression") → landed as `2521f71`
- `instruction-noop-evidence-recovery` (f5ec09e, "Guard instruction noops with refusal evidence") → landed as `1e89410`
- `phase8-routing-recovery` (6d2dab1…dddfed4, 5 commits, routing-hijack repro + fix + review) → landed as `ac8199a`/`43eb60b`/`2e45bbb`/`477748b`/`c4a8bcb`
- `phase8-routing-recovery-handoff` (6d2dab1, "docs: hand off Phase 8 routing recovery") → landed as `ac8199a`
- `provider-network-nsfs` (c5bdb12, "Fix provider namespace provisioning under bounded capabilities") → landed as `25ec98a`

**SUPERSEDED** (same author, same author-timestamp, same subject line, near-identical diff —
rebased directly onto master's mainline instead of through this branch, so `patch-id` differs
only by shifted diff context; content is on master):
- `gate-socket-hardening` (0f43f74, "Harden Phase-8 gate, path, sandbox, and proxy boundaries") → superseded by `56f929f`
- `gsc-invalid-lifecycle` (73ca551 exact-matches `b63b123`; tip 2916e6c, "control: authenticate invalid-contract terminal evidence") → superseded by `84f771b`
- `gsc-lifecycle-race-hardening-v2` (2f05a55, "Harden Phase 8 window races, reject rc, and instruction parsing") → superseded by `8651555`
- `gsc-notification-hardening` (2b86587, "Authenticate Phase 8 notification projections fail-closed") → superseded by `d587b54`
- `gsc-seed-verification` (69162a1, "Bind Phase 8 ignored seed evidence"; 3b081c8 exact-matches `3ac2382`) → superseded by `f461de3`
- `provider-only-capability` (9260076, "Add fail-closed provider-only network capability") → superseded by `aab3764`

## Suggested actions for Lucas

1. Delete all 13 unlanded `review/*` branches — every one has its content on `origin/master` already; none need a PR.
2. Removing the 5 worktrees still checked out to them (`recursion-agent-contract`, `-lifecycle`, `-lifecycle-v2`, `-notify`, `-seed`) needs `git worktree remove`, which this read-only audit did not run.
3. Also prune the 7 worktrees sitting on already-merged branches (`recursion-agent-lifecycle-fix`, `-authority-descendant`, `-exact-instruction-turn`, `-gateway-shutdown`, `-gateway-shutdown-regression`, `-gsc-conformance-node24`, `-gsc-v3-profile`) — same cleanup, different cause.
4. Root cause worth a `DECISIONS.md` entry: on 2026-08-12/13 every review-branch commit was re-committed straight onto master (same author/timestamp/subject) instead of merged via PR — the review-branch workflow was bypassed for ~a day. Confirm that's no longer happening.
5. No branch here needs rescue work or a new PR — this list is pure hygiene.
