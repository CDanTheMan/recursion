engine: claude
repo: /opt/golden-stallion-client
sshkey: ~/.ssh/gsc_deploy
seed: user-client/render/data/models
acceptance: bash /opt/recursion/scripts/gsc-nativediff-gate.sh
workdir: .

- [ ] Reduce furys_storage slot 0x68 (inline) triangle over-count — measured +19926 tris, the single biggest per-slot GEOMETRY error across the four baselined worlds
- [ ] Reduce vikings_collection net triangle under-count — measured Σ|per-slot err| 16412, signed -16336 (mostly MISSING geometry)
- [ ] Reduce chickenlips_resources Σ|per-slot triangle error| (baseline 4453) without worsening any other world
- [ ] Reduce watersigns_realm Σ|per-slot triangle error| (baseline 3186) without worsening any other world

<!--
FRONTIER ROADMAP — golden-stallion-client renderer, GEOMETRY axis only.

★ WHAT THIS GATE MEASURES. The acceptance is gsc-nativediff-gate.sh: Σ|per-slot TRIANGLE error|
must strictly decrease for at least one baselined world and NO world may get worse (empty
GSC_NATIVEDIFF_TARGET => "any-improves / none-worsens" mode, which is also the control — a shared-
code fix that legitimately improves several worlds passes; a change that worsens a bystander world
fails). Conformance stays green and the measurement tools may not be edited. Baseline lives at
state/gsc/nativediff-baseline.tsv (re-pin with `gsc-nativediff-gate.sh --regen` on a known-good tree
ONLY when BUILD_DEFAULTS change; a re-pin prints old-beside-new so it is never silent).

⚠ AXIS SPLIT — this gate is NOT the whole renderer. It sees triangle COUNTS, so it drives GEOMETRY
work (missing/extra faces, joining, occlusion). It is BLIND to:
  - vertex colour / ALPHA  (north-star #1 = water renders ~2.5x too opaque; α=0x66=0.4 exactly). That
    fix widens aColor vec3->vec4 and changes NO triangle counts — gate it by the shade/alpha oracle
    (capture-reader.cjs / live vertex-buffer reads), never by native-diff.
  - UV / atlas-page selection, tint, translucent OVERLAY passes.
Do NOT queue a shading item under this roadmap; the gate would pass it green having measured nothing.

⚠ SCOPE OF THE ARM. A build-loop arm (claude -p) is a mechanical file-writer. The items above are
NOVEL geometry RE (why is furys inline +19926 over?), which needs the vault + a conductor session,
not a cheap arm. This roadmap is the objective CONTRACT + the measured frontier queue; it is NOT
armed for overnight auto-drain. GSC's deploy key is READ-ONLY, so nothing here can auto-merge
regardless — a green result is a reviewable loop/work/<id> branch, no more.

Order the checklist largest-honest-win-first (§3 of docs/spec/RENDERER-NORTH-STAR.md). Joining
(CLUSTER role 3 39.3% + SUPERJOINER 11.4%) already SHIPPED 2026-08-04 — do not re-open it.
-->
