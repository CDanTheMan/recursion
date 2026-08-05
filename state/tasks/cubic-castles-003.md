id: cubic-castles-003
workstream: cubic-castles
goal: Implement multiPart block splitting so multipart.conformance tests pass
engine: claude
repo: /opt/golden-stallion-client
acceptance: bash /opt/recursion/scripts/gsc-conformance-gate.sh
workdir: .
autonomy: auto
status: blocked
blocked_on: model corpus absent on box (user-client/render/data/models/blocks ~12MB, gitignored + PC-local); all target conformance tests need it — scp the corpus to unblock

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
