# Integration progress — 2026-09-14

Parent: goal-recursion-v2-execution-fabric. Product target: Recursion v3.
TASK_BASE: be3ee96353f16cf84df38397120e324c7204b8f3.
Branch: codex/p2-foundry-lifecycle-integration-20260914.
Worktree: /opt/recursion-foundry/worktrees/p2-foundry-lifecycle-integration-20260914.

The reviewed host and observation commits were combined with a local non-default merge.
No imported file changed. Source Windows/native component worktrees remain preserved.
SPEC freezes scope and required outcomes before integration implementation.
Original component exact-candidate gates and review evidence were verified in the parent task:
host 58 tests, observation 55 tests, 49 specifications and exact allowed additions.
The current integration gates and independent review remain pending.
No provider, scientific, fleet, production service, configuration or publication effects.

## Initial composition evidence

First focused run: 13 tests in 6.216 seconds, five assertion/interface errors retained
in the parent task command output (2026-09-14). The implementation's prior-binding,
election, disconnect, missing-data and ownership cases passed. New test assertions had
used nonexistent content_base64, a string freshness instead of freshness.state, and
snapshot_required as the error code instead of the actual replay_unsupported code plus
snapshot_required=true. A direct load_config call passed Path instead of its declared
string. Corrected against the unchanged inherited source interfaces, with no protocol
changes or dropped behavioral outcomes. Added actual-service restart-exhaustion case.

Second focused run: 14 tests passed in 7.414 seconds. Gate construction and exact-candidate
independent review pending. The source and protocol distinctions remain explicit.

## Independent review and correction

Candidate b2e08737b181f5a331e0306bf358a7ba453aad91 passed its first union gate:
14 composition tests, 75 preserved behavioral tests, handoff and complete source binding.
Root receipt: /var/lib/recursion-foundry/reviews/p2-foundry-lifecycle-integration-20260914/root-b2e0873/receipt.json.

Independent Astra review REQUEST_CHANGES despite those passing gates:
the command-session guard could report quiescence while an escaped adopted child remained
a zombie after cgroup.kill. Its actual probe found escaped PID 1409 in state Z after
quiescent=true, and the probe itself reaped it. No service-composition findings were reported.
Review: /var/lib/recursion-foundry/reviews/p2-foundry-lifecycle-integration-20260914/astra-b2e0873-review/independent-review.md.
Counterexample: /var/lib/recursion-foundry/reviews/p2-foundry-lifecycle-integration-20260914/astra-b2e0873-guard-probe/independent-probe.json.
Those receipts remain failed-review evidence, not final acceptance.

The new guard now observes start-bound direct adopted children of its single-command
subreaper, excludes the still-unreaped command leader, performs bounded waitpid reaping,
and refuses quiescence if an adopted child remains. Controls require a waitpid receipt and
actual absence of the known escaped PID, including when test teardown already removed its
cgroup. No inherited guard file changed. Outer integration validation also explicitly
rejects a boolean inner configuration version; inherited source remains untouched.
Manual invocation and the unrun application/production boundaries are documented in SPEC.
Corrected exact-candidate gates and review are pending.