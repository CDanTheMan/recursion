schema_version: 1
id: cubic-castles-000
workstream: cubic-castles
goal_id: goal-gsc-client-reconstruction
dependencies:
goal: Wiring control — validate the external-repo worktree + conformance gate (no arm, zero cost)
engine: none
worker_class: deterministic-gate
repo: /opt/golden-stallion-client
seed: user-client/render/data/models
acceptance: bash /opt/recursion/scripts/gsc-conformance-gate.sh --no-progress
workdir: .
allowed_paths: .
non_goals: tests fixtures oracle baselines live-game automation
autonomy: auto
status: passed

Control task. engine=none writes nothing; it just proves the build-loop can create a worktree
in the golden-stallion-client repo, run the conformance gate there, and pass on a clean HEAD
(no tampering, no regression, progress not required). If this passes, the plumbing is sound.
