id: cubic-castles-002
workstream: cubic-castles
goal: Implement HSR side-culling so hsr.conformance tests pass
engine: claude
repo: /opt/golden-stallion-client
acceptance: bash /opt/recursion/scripts/gsc-conformance-gate.sh
workdir: .
autonomy: auto
status: running

Make the failing tests in user-client/render/hsr.conformance.test.cjs pass: "block 516 matches
§5.3 exactly", "HSR culls exactly 10 of 46 with all five neighbours occluding, 0 with none",
"HSR removes THE CORRECT boundary group per neighbour (catches a transposed axis)", "a model
UNDERSIDE is never culled — §5.3 has no +z test", "HSR only applies to DFLAG_HIDESIDES carriers".

Spec: docs/spec/RENDERER-NORTH-STAR.md §5.3. Source: user-client/render/shade-sides.js,
mesh-cubes.js, occluder.js, block-flags.js. NOTE the vertical axis is axis 1 with sign -1 (see
user-client/render/axis.js); a model UNDERSIDE must never be culled. Read the tests + §5.3 first.

Hard rules:
- Do NOT edit any *.test.cjs, truth fixture, or file under user-client/render/data — fix the
  implementation. The gate rejects any change to those.
- Do NOT regress currently-passing tests. The gate runs the FULL suite: fails on ANY regression,
  requires at least one previously-failing test to flip green.
- You may run `node --test user-client/render/hsr.conformance.test.cjs` to iterate.
