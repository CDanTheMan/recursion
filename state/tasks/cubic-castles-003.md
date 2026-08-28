schema_version: 1
id: cubic-castles-003
workstream: cubic-castles
goal_id: goal-gsc-client-reconstruction
dependencies: cubic-castles-000
goal: Implement multiPart block splitting so multipart.conformance tests pass
engine: claude
worker_class: claude
repo: /opt/golden-stallion-client
seed: user-client/render/data/models
acceptance: bash /opt/recursion/scripts/gsc-conformance-gate.sh
workdir: .
allowed_paths: user-client/render
non_goals: tests fixtures oracle baselines live-game automation
autonomy: auto
status: moot
resolved: feature already implemented; corpus absence was the only blocker. With corpus present the target tests pass at baseline (206). No arm work to do.

Make the failing tests in user-client/render/multipart.conformance.test.cjs pass: "parts are
split, and only for blocks that have a suffixed file", "multiPart OFF reproduces the merged mesh
exactly (separability)", "silence breaker: multiPart must CHANGE the fixture".

Spec: docs/spec/RENDERER-NORTH-STAR.md. Source: user-client/render/mesh-model.js,
model-loader.js, modl.js, render-options.js. multiPart is a gated option; OFF must reproduce the
merged mesh byte-for-byte (separability). Read the tests + spec FIRST.

Hard rules:
- Do NOT edit any *.test.cjs, truth fixture, or file under user-client/render/data — fix the
  implementation. The gate rejects any change to those.
- Do NOT regress currently-passing tests. The gate runs the FULL suite: fails on ANY regression,
  requires at least one previously-failing test to flip green.
- You may run `node --test user-client/render/multipart.conformance.test.cjs` to iterate.
