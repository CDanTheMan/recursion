id: cubic-castles-001
workstream: cubic-castles
goal: Implement the water vertex-alpha lane so alpha.conformance tests pass (water alpha = 0.4)
engine: claude
repo: /opt/golden-stallion-client
acceptance: bash /opt/recursion/scripts/gsc-conformance-gate.sh
workdir: .
autonomy: auto
status: running

Make the failing tests in user-client/render/alpha.conformance.test.cjs pass — e.g.
"SILENCE BREAKER: water vertices carry 0.4, not 1.0" and "the alpha lane moves NO triangle and
NO vertex count". The native renderer gives water vertices a vertex alpha of 0.4 (RE finding:
water is ~2.5x too opaque at alpha 1.0). Implement the vertex-alpha lane so water carries 0.4
WITHOUT changing any triangle or vertex COUNT — alpha is a per-vertex channel only.

Where to look: user-client/render/shading.js, palette.js, mesh-cubes.js, mesh-core.js, and
render-options.js (there may be a gated flag). Read the failing tests FIRST to see exactly what
they assert, then implement.

Hard rules:
- Do NOT edit any *.test.cjs, truth fixture, or file under user-client/render/data — fix the
  implementation. The gate rejects any change to those.
- Do NOT regress the currently-passing tests. The gate runs the FULL suite: it fails on ANY
  regression and requires at least one previously-failing test to flip green.
- You may run `node --test user-client/render/alpha.conformance.test.cjs` to iterate.
