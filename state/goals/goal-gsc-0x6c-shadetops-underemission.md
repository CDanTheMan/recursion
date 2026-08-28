schema_version: 1
version: 2
id: goal-gsc-0x6c-shadetops-underemission
project_id: golden-stallion-client
pilot_id: pilot-golden-stallion-client
plan_id: gsc-0x6c-shadetops-underemission-v1
plan_digest: 67fe16acff0c638df28ee86e5003fccd2e5905d7570d84ad638588a4e06bf8c3
instruction_id: 506
status: abandoned
outcome: Reduce verified shade-tops overlay under-emission in renderer slot 0x6c without changing fixtures or gate machinery.
acceptance_suite: node user-client/render/tools/native-diff.cjs --metric
falsifier: The native-diff metric does not show a reduced 0x6c under-emission or protected paths are modified.
budget: {"max_concurrency":1,"max_cost_usd":0,"max_failures":1,"max_publish_attempts":0,"max_review_queue":1,"max_task_attempts":1,"max_tokens":45000,"max_wall_clock_seconds":1800,"publication_required":false}
started_at_epoch: 1786583004
terminal_reported: 1
event_seq: 3
last_transition_id: transition-9ce1f6b9f77f5764097d06ea09317158
last_transition_at: 2026-08-28T21:36:40Z
last_transition_reason: phase0-superseded-unpinned-source
last_transition_from: active
finished_at: 2026-08-28T21:36:40Z
resolution: Superseded by the v2 source-bound attempt and closed during Recursion v2 Phase 0; this unpinned legacy goal must not resume.
