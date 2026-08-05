id: cubic-castles-000
workstream: cubic-castles
goal: Wiring control — validate the external-repo worktree + conformance gate (no arm, zero cost)
engine: none
repo: /opt/golden-stallion-client
acceptance: bash /opt/recursion/scripts/gsc-conformance-gate.sh --no-progress
workdir: .
autonomy: auto
status: queued

Control task. engine=none writes nothing; it just proves the build-loop can create a worktree
in the golden-stallion-client repo, run the conformance gate there, and pass on a clean HEAD
(no tampering, no regression, progress not required). If this passes, the plumbing is sound.
