---
title: Hermes Phase 8 routing recovery handoff
type: handoff
status: blocked
last-verified: 2026-08-13
related:
  - CONTROL_PLANE.md
  - CLAUDE.md
  - docs/plans/hermes-project-pilot-phase8-handoff.md
  - docs/plans/hermes-phase8-preflight-operational-nuances.md
---
# Hermes Phase 8 routing recovery handoff

## Authority and stop condition

Lucas authorized documentation of the current stopped state and a fresh-session handoff.
This is not authorization to deploy another change, run another Hermes decision turn, edit
runtime records, or remove PAUSE.

The production control plane is `/opt/recursion` on `ssh gs-recursion`. Preserve these rules:

- never push, force-push, or merge a protected branch from a shell;
- make fixes on a review branch with red-to-green tests and adversarial review, then submit
  a PR for Lucas to merge;
- never edit `.env`, model selection, capacity, autonomy flags, cron, credentials, or auth;
- never manually edit/delete instructions, decisions, actions, plans, goals, tasks, windows,
  events, outboxes, or deliveries;
- instructions close only through succeeded coupled actions;
- never repair instruction 618; and
- never remove `state/PAUSE` without a fresh, exact Gate-6 authorization from Lucas after a
  fresh preflight. No such authorization is active.

Every production read or operation must verify the exact PAUSE file before and after. Its
required SHA-256 is
`919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db`.

## Fresh measured production state

The final read-only snapshot on 2026-08-13 found:

| Item | Exact state |
|---|---|
| deployed branch / HEAD | `loop/auto` / `0561bca6294a1eae2b3d31765ac3a3f7fb248c5b` |
| reviewed `origin/master` | `73bfc402822c1b43841e8b715fe8f8c446ad709f` (PR #56 merge) |
| PAUSE | exact hash above; `root:root`; `0644`; 189 bytes |
| tracked production dirt | 3 paths, all under `state/`; zero non-state tracked dirt |
| services | actuator, gateway, cron, provider network, provider proxy active/enabled; all `NRestarts=0` |
| decision queues | pending 0; running 0 |
| workers | zero running `recursion-worker-*` units; zero matching processes |
| GSC checkout | `/opt/golden-stallion-client`, `main`, clean at `ad4bb39a8cf3a9f3ad7e17b21dd89fcdf4252b39` |
| old GSC window | `window-gsc-pilot-1` closed at `2026-08-13T22:04:13Z` by instruction 699 |
| current pilot activity | none; Gate 6 has not started |

The merged/deployed hardening includes the Phase-8 seed/scope/gate contracts and provider-only
capability. Post-deployment provider integration and the complete Phase-8 Linux audit passed.
The evidence bundle is `/var/backups/recursion/pr56-deploy-20260813T202056Z`, manifest root
`d5ec7a7eaaa5bae8c0818afb85730b7a89fe93449a36638732f121a22fb4d538`.

## Routing incident and durable evidence

Instruction 699 lawfully closed the expired v1 window:

- decision `decision-6a55bbccb922dc90c52c091e`;
- succeeded action `action-69f96a0bba296ffcb1675710`; and
- exactly one `pilot-window-closed` event.

Lucas then sent a fresh-plan request. The text included the incidental word `deployed`, which
matched the intake routing expression `deploy\w*`. The request became instruction 707 with
`routing_target: head-hermes`, although only `pilot-golden-stallion-client` can lawfully emit
the required `pilot-plan-propose` action.

Two separately authorized, supervised Head Hermes turns were attempted. Both emitted `noop`
instead of escalation because the Head Hermes brief did not contain the project-pilot contract
surface. The hardened same-instruction noop evidence guard rejected both with `rc=4` and
`cannot-bind noop evidence is absent`:

- failed action `action-bb38398a6e0e3859a1a7d263`; and
- failed action `action-4a90005df9c9dfe6cbb7fbad`.

Instruction 707 remains open. Instruction 732, routed to
`pilot-golden-stallion-client`, also remains open with no action. The conditional project-pilot
turn for 732 was correctly not run because escalation of 707 did not succeed.

Do not retry the same Head Hermes turn. It has now failed the same way twice and another model
sample is not a recovery mechanism.

## Next reviewed implementation target

Build one coherent routing/recovery patch on a fresh review branch. Before editing, reproduce
the failure against the exact merged bytes and preserve red tests. The patch should:

1. Replace broad substring routing with intent-aware, boundary-safe routing so descriptive
   words such as `deployed` cannot hijack an otherwise canonical project-pilot proposal.
2. Add a deterministic actor/verb admission check before model execution. When an instruction's
   requested verb cannot be emitted by its routed actor, the controller must fail closed through
   a lawful, receipt-backed escalation/refusal path rather than asking a model to infer recovery.
3. Provide a lawful coupled recovery for already-misrouted instruction 707 and the follow-up
   instruction 732. Do not rewrite, delete, reopen, or fabricate either historical record.
4. Preserve exact-once instruction/action/event/outbox behavior across replay, PAUSE, crash
   boundaries, and actuator restart.
5. Keep unrelated Head Hermes deployment/policy routing intact.

Minimum red-to-green coverage:

- the exact 707 wording routes to `pilot-golden-stallion-client` after the fix;
- true deployment/policy commands still route to Head Hermes;
- actor/verb mismatch produces one authenticated escalation/refusal without a model call;
- replay does not duplicate the action, event, attention, or delivery;
- PAUSE appearing at every mutation boundary prevents new actuation or completes only the
  reviewed recovery transaction;
- 707 and 732 can reach lawful terminal states through coupled actions without manual file edits;
- queues remain empty and no plan/goal/task/window/worker is created by the recovery; and
- historical instruction 618 and its retained incident evidence remain untouched.

Run focused tests first, then the complete Linux Phase-5 through Phase-8 matrix in a new
root-owned mode-0700 disposable `/var/tmp` clone. Production may be read for evidence only,
with the exact PAUSE hash asserted before and after. Stop if code/config is dirty or any measured
state contradicts this handoff.

## Development agent staffing

For the next authoring session, Lucas prefers OpenCode Go DeepSeek agents to conserve limited
Codex quota:

- DeepSeek V4 Pro: primary implementation analysis and adversarial control-plane review;
- DeepSeek V4 Flash: mechanical test expansion, fixture inspection, and diff auditing; and
- the primary Codex session: authority decisions, production measurements, integration, and
  final evidence synthesis.

These are development-session roles only. Verify the exact OpenCode Go model identifiers and
CLI availability before invoking them. Do not encode them in `.env`, Recursion model selection,
pilot tasks, or production configuration, and do not expose credentials or prompts containing
secrets. Agent output is advisory until independently verified against repository bytes and tests.

## Recovery sequence after Lucas merges a fix

After red-to-green proof, adversarial review, PR review, Lucas merge, and a separately authorized
PAUSE-held deployment:

1. Re-measure production and prove the deployed executable bytes equal the reviewed commit.
2. Use only the reviewed coupled recovery path to terminalize instruction 707.
3. Only after 707 succeeds, lawfully terminalize instruction 732.
4. Ask Lucas to send a new project-topic instruction whose wording avoids control-plane verbs.
5. Poll intake and require routing to `pilot-golden-stallion-client` before any decide turn.
6. Require a fresh v2 plan, goal, and task with the deployed required non-goals, tracked seed
   contract, provider-only model network, heavy forced-on shade-tops gate, immutable gate files,
   source HEAD, and publication disabled.
7. Present the exact canonical plan digest to Lucas for a separate approval instruction.
8. Use a new window identity such as `window-gsc-pilot-2`; never reuse v1.
9. Perform the complete Gate-6 preflight, snapshot/restore drill, rollback arming, and live
   observation setup. Request a separate exact PAUSE-lift authorization only then.

The recommended future project-topic request, after 707 and 732 are closed, is:

> Propose one fresh bounded offline renderer plan for golden-stallion-client: reduce the
> verified 0x6c shade-tops under-emission through the required forced-on native-diff gate,
> with all implementation changes confined to user-client/render, one task, independent
> verification, and new v2 plan, goal, and task IDs. Do not reuse the v1 identities or the
> closed window.

## Remaining promotion gates

Resolving this routing incident does not promote Recursion. The remaining program is:

1. fresh GSC v2 plan, digest approval, new window, Gate-6 observed PAUSE lift, and Gate-7 closure;
2. a distinct Chiron success pilot;
3. a Chiron ambiguity/assist pilot proving exact-once same-task resumption;
4. a two-project parallel isolation pilot;
5. a 24-hour soak covering scheduler ticks, gateway restart, host reboot, PAUSE during a worker,
   notification retry, and usage/cost reconciliation; and
6. final evidence review plus a separate Lucas production-promotion authorization.

Keep PAUSE asserted between every observed window.

## Copyable next-session prompt

```text
You are continuing the Recursion Phase-8 production-control-plane hardening on
ssh gs-recursion, repository /opt/recursion, deployed branch loop/auto, operator Lucas.

Read CLAUDE.md, CONTROL_PLANE.md, ANCHOR.md,
docs/plans/hermes-project-pilot-phase8-handoff.md,
docs/plans/hermes-phase8-preflight-operational-nuances.md, and
docs/plans/hermes-phase8-routing-recovery-handoff.md. The routing-recovery handoff is the
latest state and supersedes older point-in-time state blocks.

Boot by measuring. Verify PAUSE SHA-256
919371834778def8b6b79bb640d44933296a0e912f606e0738a23c166f4ee0db before and after every
production operation. Do not deploy, lift PAUSE, change config/model/capacity/cron/auth, or
manually edit runtime records. Do not run another Head Hermes turn for instruction 707.

Implement the routing/recovery correction described in the latest handoff on a fresh review
branch. Prove red-to-green, obtain independent adversarial review, and prepare a PR for Lucas.
Use OpenCode Go DeepSeek V4 Pro/Flash agents for bounded development/review work if their exact
CLI model identifiers are available; never place those choices in production configuration.
Stop and report if any fresh measurement contradicts the handoff.
```
