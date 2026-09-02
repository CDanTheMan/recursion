schema_version: 1
version: 3
id: task-gsc-0x6c-shadetops-underemission-v2
project_id: golden-stallion-client
project: golden-stallion-client
workstream: golden-stallion-client
pilot_id: pilot-golden-stallion-client
goal_id: goal-gsc-0x6c-shadetops-underemission-v2
plan_id: gsc-0x6c-shadetops-underemission-v2
plan_digest: 7bc21268452add838f75e8ef40e466e074e6c9c977b6261bd5aaf9f7a6a22b3a
dependencies:
goal: Adjust only renderer implementation to reduce verified 0x6c shade-tops under-emission under the required forced-on native-diff gate.
allowed_paths: user-client/render
non_goals: tests,fixtures,oracles,baselines,corpus,live-game-access,portfolio-policy,credentials,merge,deploy
worker_class: renderer-implementation
engine: claude
model_alias: sonnet-routine
verifier_model_alias: opus-review
deadline_seconds: 1500
verifier_deadline_seconds: 900
network_policy: provider-only
evidence_contract: worker-result-v1
verification: independent
expected_change: required
gate_class: heavy
gate_contract: {"acceptance_sha256":"0d24c2beee089999bfeb9a6031a68c71b8a4127f87ea7b08db898b584699c30d","controller_gate_files":{"scripts/gates/gsc-shade-tops-v1.json":"8664c1dfb698542032d9dc9d8ce42d8e3eae25b7b498ca3fd326f48f0bcc6aca","scripts/gsc-shade-tops-gate.py":"f3db1da4f631b1e8c6eccf2fc1a5d638775c972817bbe7dea869b2cf931a2f4b"},"gate_files":{"user-client/render/tools/native-diff.cjs":"14f4bdfa620b521f2d1dfc08ca180f9622be8ade637be7f2d37eff6ea6ea1a77"}}
gate_files: user-client/render/tools/native-diff.cjs
acceptance: /opt/recursion/scripts/gsc-shade-tops-gate.py --repo . --profile /opt/recursion/scripts/gates/gsc-shade-tops-v1.json
controller_gate_files: scripts/gsc-shade-tops-gate.py,scripts/gates/gsc-shade-tops-v1.json
source_head: ad4bb39a8cf3a9f3ad7e17b21dd89fcdf4252b39
source_branch: main
charter_sha256: 006bef38a57a453b25ec56fb7c76bb8e0f4782fe4f7a8655881c58cc3fc547ed
repo: /opt/golden-stallion-client
workdir: .
autonomy: auto
status: stale
seed_manifest: .seedlist
seed_manifest_sha256: 924ff916e705ba96689fe3ebc901c63c40d89c273ed10858e2109ab7c7630dc4
seed: user-client/render/data/models
seed_digest: fe5df2007ef8b345c7218a26c72e0f30510a05213c389b1465853643d3ee62dd
event_seq: 4
last_transition_id: transition-04d2903b15ded8dc6425b83b1c813ab3
lease_expires: 0
transition_reason: phase0-source-head-stale
transition_at: 2026-08-28T21:36:39Z
resolution: Phase 0 invalidated this ready task because its exact source_head is stale. A future retry requires a new task and immutable assignment.

Adjust only renderer implementation to reduce verified 0x6c shade-tops under-emission under the required forced-on native-diff gate.
