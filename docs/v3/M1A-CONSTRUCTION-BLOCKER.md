---
title: M1A construction blocker and Wave 1 receipt
status: blocked-owner-decision
last-updated: 2026-09-03
---

# M1A construction blocker and Wave 1 receipt

M1A construction stopped before schema materialization. No schema, fixture or reducer was
created. The accepted documents require incompatible wire values and leave content-addressed
objects in recursive digest cycles. Choosing a spelling, a new type or a digest boundary would
silently change the canonical contract.

## Decisive blocker

The first M1A-01 schema branch cannot be translated one-to-one:

1. [M1A-WIRE-PROFILE.md](M1A-WIRE-PROFILE.md) defines `Token` at line 27 as lowercase ASCII
   matching `^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`.
2. The same file types `PlanningEvent.event_type` as a registered `Token` at line 295.
3. [M1A-FIXTURE-ORACLES.md](M1A-FIXTURE-ORACLES.md) closes the event alphabet at lines 93–109
   with PascalCase values such as `OwnerIntentRecorded`, `GoalSpecAccepted` and `PauseApplied`;
   the wire profile adds five PascalCase disposition events at lines 355–356.
4. `CommandReceipt.related_errors` is a `TokenSet` at wire-profile line 277, while the closed
   error registry uses uppercase `E-*` values at oracle lines 118–147.

A strict schema must either reject every required event/error, add new `EventType`/`ErrorToken`
types, or rename the closed alphabet. The documents authorize none of those choices. A literal
F-M1A-001 that validates while retaining both rules would falsify this blocker.

There is also no documented acyclic construction for the required literal digests. The digest
rule at wire-profile lines 40–45 omits only the object's own `content_digest` and retains nested
digests. `PlanRevision.task_node_refs` includes each TaskNode digest at line 227, while every
`TaskNode.plan_ref` includes the PlanRevision digest at line 229. Similarly, receipts require
`state_after_digest` at lines 270–283 while the resulting projection carries receipt content
digests at lines 302–329. Computing either pair without an added omission, pre-state rule or
identity boundary requires an undocumented fixed-point choice.

These conditions trigger the campaign stop rules: a schema requires an undocumented semantic
choice and the byte-identical fixture oracle cannot be frozen from the accepted owners.

## Other confirmed closure gaps

Wave 1 also found these independently blocking or under-specified wire/oracle seams. They are
recorded so a reviewed correction does not repair only the first symptom:

- no literal genesis projection/digest is defined although F-M1A-002 and F-M1A-018 require it;
- `PauseApplied` requires a DomainRecord primary record, but `apply-pause` carries no record and
  no pause DomainRecord is registered;
- schema-invalid commands are promised receipts without a rule for their command digest, and
  the error registry has no missing-required-field error for F-M1A-002;
- the amendment command cannot introduce the new GoalSpec and PlanTransition that its refs must
  already resolve;
- F-M1A-019 requires executive-lease replacement, but only work-lease replacement is a registered
  command/event;
- the Owner verifier-exception record required by F-M1A-011 has no registered admission command
  or event;
- the assigned verifier identity is not bound by PlanRevision, TaskNode, GateRequirement or a
  separate assignment record;
- TaskNode/WorkPacket omit the GoalSpec-bound egress-policy ref, GoalSpec omits an authority-policy
  ref, and RouteAssignment omits the capacity-pool binding needed for the stated attenuation;
- F-M1A-004 requires a stable sorted refusal witness, but CommandReceipt has no witness field; and
- the profile does not define digest operands for `graph_digest`, `state_delta_digest`,
  `unchanged_binding_digest`, `narrowed_binding_digest` and `event_log_digest`.

## Wave 1 worker receipts

Every worker was read-only, used the exact clean candidate below, ran only inspection commands
such as `Get-Content`, `rg` and read-only Git queries, made no file/config/Git change and spawned
no nested agent. All are GPT-5.6-family routes; this is not cross-family review.

| Worker | Model / effort | Lane | Outcome | Confidence / decisive falsifier |
|---|---|---|---|---|
| LUNA-M1A-01 | `gpt-5.6-luna` / `xhigh` | one-to-one schema inventory | BLOCKED: event Token conflict and plan/node plus receipt/state digest cycles | high; produce strict F-M1A-001 events and finite digests without changing the profile |
| LUNA-M1A-02 | `gpt-5.6-luna` / `xhigh` | literal F-M1A-001–023 plan | BLOCKED: confirmed the decisive conflicts plus genesis, pause, parser-receipt and amendment bootstrap gaps | 0.96–0.99; materialize schema-valid F-M1A-001/F-M1A-005 from current owners |
| LUNA-M1A-03 | `gpt-5.6-luna` / `xhigh` | repository convention audit | PASS for conventions only: stdlib runtime, direct `unittest`, test-only `jsonschema`; existing v2 canonicalizers are not RFC 8785 and do not resolve the blocker | 0.92; any new core import/I/O or code-point rather than UTF-16 key sort falsifies its recommendation |
| LUNA-M1A-04 | `gpt-5.6-luna` / `xhigh` | adversarial authority/policy audit | BLOCKED: F-M1A-019 and F-M1A-011 need unregistered commands/events; multiple attenuation bindings are absent | high; encode either fixture without inventing a union arm |

Candidate inspected: `a256ad2ee7104f7abb1b679fc415afc49291556f` on branch
`codex/v3-m1a-autonomous-planning` in the dedicated local worktree. The workers inspected the
operative constitution, anchor, repository instructions, autonomous-planning semantics, M1A
construction spec, wire profile, fixture oracle and campaign record. The convention reviewer
also inspected existing v1/v2 schemas, Python contracts/kernels, direct test runners and installed
Python test dependencies. No contradictory lower-priority evidence supplies missing aliases,
digest boundaries or union arms.

## Disposition and exact Owner seam

M1A-01 is blocked. M1A-02 through M1A-07 are not admitted. Wave 2 is not launched, and neither
Terra adjudicator is launched, because the required schema-only and literal-red commits do not
exist. Their omission is prerequisite enforcement, not a verifier pass or downgrade.

Lucas must approve an exact canonical revision covering at least:

1. event and error spelling/types;
2. acyclic PlanRevision/TaskNode and CommandReceipt/ProjectionState digest boundaries;
3. genesis state/event-chain literals and every named digest operand;
4. pause, amendment, executive-lease-replacement and verifier-exception command/event carriers;
5. schema-invalid command receipt/error precedence; and
6. verifier, egress, authority, account, capacity-pool and budget-reservation bindings.

Until then, M1A is not ready for construction review. Nothing in this receipt claims a runtime,
replay result, fixture pass, independent verification or production behavior.
