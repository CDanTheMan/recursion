schema_version: 1
id: gsc-0x68-cloud
workstream: gsc
goal_id: goal-gsc-client-reconstruction
dependencies:
goal: Reduce furys_storage slot 0x68 (inline/Cloud) triangle OVER-emission (+19926, ratio 1.037) toward native, WITHOUT overshooting into under-emission and WITHOUT worsening any other world.
engine: claude
worker_class: claude
repo: /opt/golden-stallion-client
sshkey: ~/.ssh/gsc_deploy
seed: user-client/render/data/models
acceptance: bash /opt/recursion/scripts/gsc-nativediff-gate.sh
workdir: .
allowed_paths: user-client/render
non_goals: tests fixtures oracle baselines live-game automation
autonomy: auto
automerge: no
status: proposed
planned_from: live-re-derived (0x68 is the dominant furys error; register gap G1b/0x74 already CLOSED at 1.000)

CONTEXT — this is the single biggest geometry error on the board. MEASURE FIRST, then fix minimally.

WHAT: furys_storage slot 0x68 ("inline", opaque cube faces) over-emits by +19,926 triangles
(ours 554,583 vs native 534,657; ratio 1.037). The slot is dominated by CLOUD (id 306,
DFLAG_HIDESIDES + DFLAG_HOMOGENOUS) and Chest (id 177).

ROOT (already reverse-engineered — READ THESE THREE DOCS before touching code):
- docs/verify/the-general-occluder-is-a-BINARY-relation-and-ours-is-unary-2026-08-05.md
- docs/verify/furys-0x68-is-cloud-and-the-union-arm-is-41pct-worse-2026-08-04.md
- docs/verify/cloud-union-halves-the-error-and-overshoots-2026-08-04.md
Native occlusion is a BINARY relation: neighbour.occludes(self) (FUN_004dcf78 is a THISCALL on the
NEIGHBOUR, self passed as the argument). OUR isOccluderNeighbor(x,y,z) is UNARY — it only looks at
the neighbour position, never at self — so it cannot express the relation and we emit shared faces
native culls.

CRITICAL — DO NOT just flip hsrGeneralOcclude ON. That was MEASURED to make 0x68 41% WORSE
(+19,926 -> -28,154, an overshoot). The correct fix makes the occluder BINARY (consider BOTH self
and the neighbour flags for the shared face), not cull more universally.

FILES to read + edit (implementation only): user-client/render/mesh-chunked.js (the 0x68/inline
cube-face emission + where occlusion is decided) and user-client/render/block-flags.js. Grep the
render dir for isOccluderNeighbor / hsrGeneralOcclude / HIDESIDES to find the exact site.

HOW TO CHECK YOURSELF (run node as you go — network is off but node works):
- node user-client/render/tools/native-diff.cjs --world=furys_storage --slot-blocks=0x68
  (the 0x68 delta must move toward 0 from +19,926; do NOT overshoot to negative)
- node user-client/render/tools/native-diff.cjs --world=furys_storage
  (whole-world Sum|per-slot| must DECREASE from 26,737; the TOTAL line is SIGNED and is NOT the metric)
- Repeat for vikings_collection, chickenlips_resources, watersigns_realm — NONE may get worse.
- node --test user-client/render/*.test.cjs   (conformance must stay green)

The gate (your acceptance) enforces: at least one world Sum|per-slot triangle error| strictly
DECREASES, AND no world worsens, AND conformance is green, AND you did not touch tools/tests/
fixtures/data. Minimal-and-correct beats broad-and-broken. If you CANNOT make it strictly better
without overshooting or worsening another world, make NO change — a no-op is correctly rejected as
"no progress", and that is the honest result, not a failure to hide.
