schema_version: 1
version: 2
id: task-gsc-0x6c-shadetops-underemission
project_id: golden-stallion-client
project: golden-stallion-client
workstream: golden-stallion-client
pilot_id: pilot-golden-stallion-client
goal_id: goal-gsc-0x6c-shadetops-underemission
plan_id: gsc-0x6c-shadetops-underemission-v1
plan_digest: 67fe16acff0c638df28ee86e5003fccd2e5905d7570d84ad638588a4e06bf8c3
dependencies:
goal: Adjust renderer implementation to reduce verified 0x6c shade-tops overlay under-emission while preserving conformance behavior.
allowed_paths: user-client/render
non_goals: credentials,merge,deploy
worker_class: renderer-implementation
engine: claude
model_alias: sonnet-routine
verifier_model_alias: opus-review
deadline_seconds: 1500
verifier_deadline_seconds: 900
network_policy: none
evidence_contract: worker-result-v1
verification: independent
expected_change: required
gate_files: user-client/render/shade-tops.js,user-client/render/mesh-chunked.js
acceptance: node user-client/render/tools/native-diff.cjs --metric
repo: /opt/golden-stallion-client
workdir: .
autonomy: auto
status: stale
event_seq: 3
last_transition_id: transition-7ef2808676e3bdf2c1b242cdc9efe7f8
transition_reason: phase0-superseded-unpinned-source
transition_at: 2026-08-28T21:36:40Z
resolution: Closed during Recursion v2 Phase 0 because the legacy task has no immutable source assignment and was superseded by a later source-bound attempt.

Adjust renderer implementation to reduce verified 0x6c shade-tops overlay under-emission while preserving conformance behavior.
