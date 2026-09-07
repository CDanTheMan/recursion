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

Second: Which assistant decision classes, if any, may amend GoalSpec?

- **Recommended: retain Owner-only amendments.** Persistent assistants can consult and make
  already-granted routine decisions; their identities may span sessions and goals.
- **Alternative: propose a bounded amendment whitelist.** Specify exact classes, ceilings,
  receipts and revocation semantics in a separately authorized contract/amendment task.

No new permission is needed for an assistant's already-authorized routine choice. A consultant's
message is advice until the current lease holder records an admissible decision.

Other unknowns are evidence work: exact account/distribution eligibility, all ten controls on
critical routes, auxiliary quota bounds, recovery compatibility and numerical performance
presets. [The eight experiment families](experiments.json) identify the next tests. A missing
critical route can become an Owner release decision after the richer supported paths have been
tested; it is not permission to drop a name now.
