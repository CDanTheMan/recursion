schema_version: 1
version: 1
id: goal-gsc-0x6c-shadetops-underemission-v2
project_id: golden-stallion-client
pilot_id: pilot-golden-stallion-client
plan_id: gsc-0x6c-shadetops-underemission-v2
plan_digest: 7bc21268452add838f75e8ef40e466e074e6c9c977b6261bd5aaf9f7a6a22b3a
instruction_id: 747
status: active
outcome: Reduce verified 0x6c shade-tops under-emission through renderer-only changes while preserving the forced-on native-diff gate.
acceptance_suite: /opt/recursion/scripts/gsc-shade-tops-gate.py --repo . --profile /opt/recursion/scripts/gates/gsc-shade-tops-v1.json
falsifier: The required forced-on native-diff gate does not show reduced 0x6c under-emission or any protected path is modified.
gate_class: heavy
gate_files: user-client/render/tools/native-diff.cjs
controller_gate_files: scripts/gsc-shade-tops-gate.py,scripts/gates/gsc-shade-tops-v1.json
gate_contract: {"acceptance_sha256":"0d24c2beee089999bfeb9a6031a68c71b8a4127f87ea7b08db898b584699c30d","controller_gate_files":{"scripts/gates/gsc-shade-tops-v1.json":"8664c1dfb698542032d9dc9d8ce42d8e3eae25b7b498ca3fd326f48f0bcc6aca","scripts/gsc-shade-tops-gate.py":"f3db1da4f631b1e8c6eccf2fc1a5d638775c972817bbe7dea869b2cf931a2f4b"},"gate_files":{"user-client/render/tools/native-diff.cjs":"14f4bdfa620b521f2d1dfc08ca180f9622be8ade637be7f2d37eff6ea6ea1a77"}}
source_head: ad4bb39a8cf3a9f3ad7e17b21dd89fcdf4252b39
source_branch: main
charter_sha256: 006bef38a57a453b25ec56fb7c76bb8e0f4782fe4f7a8655881c58cc3fc547ed
budget: {"max_concurrency":1,"max_cost_usd":0,"max_failures":1,"max_publish_attempts":0,"max_review_queue":1,"max_task_attempts":1,"max_tokens":45000,"max_wall_clock_seconds":1800,"publication_required":false}
started_at_epoch: 1786725203
terminal_reported: 0
seed_manifest: .seedlist
seed_manifest_sha256: 924ff916e705ba96689fe3ebc901c63c40d89c273ed10858e2109ab7c7630dc4
seed: user-client/render/data/models
seed_digest: fe5df2007ef8b345c7218a26c72e0f30510a05213c389b1465853643d3ee62dd
event_seq: 2
last_transition_id: transition-136910b065ea601ed6b96a1704148d01
