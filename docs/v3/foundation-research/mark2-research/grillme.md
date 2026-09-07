# Mark 2 consequential Owner decisions

2026-09-07. Both answers remain pending in [decisions.json](decisions.json). These proposals
do not reopen the completed questionnaire or alter current authority.

First GRILLME: Which proof boundary should the first formal model use?

- **Recommended: smallest aggregate plus explicit bounded broker refinement.** Keep the six
  existing M1 obligations in the aggregate; require executable bounded traces for process
  ownership, consultation, queue saturation, RESET/replay, relaunch, configuration and
  update/Stop ordering. Move an obligation into the model if its refinement cannot be stated
  or independently tested.
- **Alternative: include a bounded broker in the first model.** Prove the cross-boundary races
  in one state space, accepting higher model complexity and potentially slower exploration.

The decisive test is `experiment.mark2.simulation`, informed by small interface probes before
freeze. The recommendation is not an Owner selection. Neither option chooses a language,
store or framework, changes M1, resolves OR-015 or changes operational PAUSE.

This is an unproved construction boundary, not a conflict with the accepted platform scope.
The current rule preserves six M1 obligations and requires an explicit proof-boundary choice.
MKR-011/MKR-018/MKR-022 and their primary evidence in [evidence.json](evidence.json) explain
why protocol cancellation and process ownership cannot be assumed equivalent. The affected
contracts are [ARCHITECTURE](../../ARCHITECTURE.md), [EXECUTION-FABRIC](../../EXECUTION-FABRIC.md),
[ACCEPTANCE](../../ACCEPTANCE.md) and [ROADMAP](../../ROADMAP.md). Formal-model freeze remains
blocked on this choice and the preceding bounded probes. Falsifier: a necessary broker
obligation cannot be stated or independently checked as a refinement, or a bounded interleaving
violates an aggregate obligation. Then include that state in the model. The recommendation is
about proof organization; the product's configurable behavior is unchanged.

Second: Which assistant decision classes, if any, may amend GoalSpec?

- **Recommended: retain Owner-only amendments.** Persistent assistants can consult and make
  already-granted routine decisions; their identities may span sessions and goals.
- **Alternative: propose a bounded amendment whitelist.** Specify exact classes, ceilings,
  receipts and revocation semantics in a separately authorized contract/amendment task.

No new permission is needed for an assistant's already-authorized routine choice. A consultant's
message is advice until the current lease holder records an admissible decision.

OR-027 requires configurable assistant decision rights while current GoalSpec amendment
ownership stays with the Owner. This is a possible future authority change, not permission
granted by a persistent identity. MKR-008/MKR-009/MKR-010 and the linked primary evidence
support separating identity, consultation and authority; they cannot select the Owner's
delegation policy. Affected contracts are [EXECUTIVES](../../EXECUTIVES.md),
[EXECUTION-FABRIC](../../EXECUTION-FABRIC.md), [PLANNING](../../PLANNING.md) and
[DECISION-REGISTER](../../DECISION-REGISTER.md). The assistant experiment tests whether a
representative authorized workflow needs actual amendments rather than routine decisions.
Repeated avoidable Owner intervention would falsify the recommendation's usability premise.
Any whitelist remains blocked pending an exact answer and separate amendment/revocation
fixtures; current routine delegation and consultation can proceed under existing grants.

A later Owner session records each exact answer in the pending decision record, checks it
against OR-021 through OR-035 and current authority, updates the affected canonical documents,
then compiles the accepted versioned GoalSpec and construction DAG. Silence changes no status.

Other unknowns are evidence work: exact account/distribution eligibility, all ten controls on
critical routes, auxiliary quota bounds, recovery compatibility and numerical performance
presets. [The eight experiment families](experiments.json) identify the next tests. A missing
critical route can become an Owner release decision after the richer supported paths have been
tested; it is not permission to drop a name now.
