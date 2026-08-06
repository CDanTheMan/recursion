id: gsc-overlay-0x6c
workstream: gsc
goal: Close the 0x6c under-emission (the shadetops/translucent-overlay pass) across worlds by fixing the shadetops APPLICATION PREDICATE, WITHOUT over-emitting on 0x68 and WITHOUT worsening any world.
engine: claude
repo: /opt/golden-stallion-client
sshkey: ~/.ssh/gsc_deploy
seed: user-client/render/data/models
acceptance: bash /opt/recursion/scripts/gsc-nativediff-gate.sh
workdir: .
autonomy: auto
automerge: no
planned_from: live-re-derived (0x6c is the biggest coherent under-emission: vikings -7862, furys -3680, chickenlips -3060)

CONTEXT — the biggest coherent error on the board is 0x6c UNDER-emission. MEASURE FIRST, then fix minimally.

WHAT (measured now): slot 0x6c (TEX2) under-emits vs native on every world:
  furys_storage   -3,680 (0.972)   vikings_collection -7,862 (0.757)   chickenlips -3,060 (0.957)
The missing geometry is the TRANSLUCENT OVERLAY PASS, ~91% of which is the "shade tops" decal.

ROOT (already reverse-engineered — READ THESE before touching code):
- docs/verify/slot-6c-gap-is-the-translucent-overlay-pass-2026-08-03.md
- docs/verify/the-overlay-gap-is-91pct-shadetops-on-0x6c-and-a-new-defect-on-0x68-2026-08-05.md
- docs/verify/shadetops-is-validated-on-0x6c-and-over-emits-on-0x68-2026-08-05.md
- docs/verify/shade-tops-decal-is-half-the-overlay-pass-2026-08-03.md

⚠ CRITICAL COUPLING — this is the whole difficulty. Enabling shadetops CLOSES 0x6c under-emission
but OVER-emits on 0x68 (it currently over-APPLIES). So the task is NOT "turn shadetops on" — it is
"get the shadetops APPLICATION PREDICATE right": which blocks/faces receive the shade-tops decal, so
that 0x6c closes toward native on furys/vikings/chickenlips WITHOUT growing 0x68. A correct predicate
is a NET win across slots; a blunt on-switch fails the gate by worsening 0x68.

FILES: grep the render dir for shadetops / shadeTops / the 0x6c overlay pass to find the emission +
its application predicate (user-client/render/mesh-chunked.js and any shadetops module; there is a
shadetops.conformance.test.cjs whose fixtures encode the intended behaviour — read it, do NOT edit it).

HOW TO CHECK YOURSELF (run node; network off, node works):
- node user-client/render/tools/native-diff.cjs --world=<w> --slot-blocks=0x6c   (0x6c must move toward 0)
- node user-client/render/tools/native-diff.cjs --world=<w> --slot-blocks=0x68   (0x68 must NOT grow)
- node user-client/render/tools/native-diff.cjs --world=<w>   (whole-world Sum|per-slot| must DECREASE;
  TOTAL is signed and is NOT the metric) for ALL of furys/vikings/chickenlips/watersigns — none may worsen.
- node --test user-client/render/*.test.cjs   (conformance stays green)

The gate enforces: >=1 world Sum|per-slot| strictly DECREASES, no world worsens, conformance green, no
edits to tools/tests/fixtures/data. If you cannot close 0x6c without worsening 0x68 or another world,
make NO code change and instead WRITE docs/verify/<dated>.md recording exactly what the application
predicate is, what you tried, and the measured coupling — a no-op with a decode note is the honest
result, not a failure to hide. Do NOT narrow scope just to keep the ratchet green (that is fitting the
metric).
