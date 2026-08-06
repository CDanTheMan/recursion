<!-- Authored by the Codex checker arm (gpt-5.6-terra, $0) 2026-08-06; reviewed by the session.
     ANCHORS (verified): our cull decision = user-client/render/mesh-chunked.js hsrProbeFor L919 ->
     makeCellIsCube L839 (same-id branch L865) + isOccluderNeighbor L371; stateCullIdSet block-flags.js:88.
     Decomp = re-corpus/decomp/render/FUN_4cf8db.c (823B). Build is a REVIEWED authoring session
     (the arm cannot self-gate building its own gate); GSC key read-only => reviewable branch, human commits.
     The +6/+198 Tier-2 override for the same-id fix needs Lucas explicit approval. -->

# Two-tier renderer decision gate

**Goal:** Accept decomp-exact renderer corrections by their audited face decisions, while retaining native triangle-count telemetry as a mandatory regression bound.

**First scope:** `FUN_004cf8db`, the four existing offline fixtures, and the `HIDESIDES` same-id arm only. World names in reports are `furys_storage`, `vikings_collection`, `chickenlips_resources`, and `watersigns_realm`.

## 1. Offline decision ledger

### Inputs and ownership

Add a deterministic offline command:

```text
node user-client/render/tools/decision-ledger.cjs --fixtures=decision-ledger/v1/fixtures.json --out=<temporary-jsonl>
```

It loads only committed fixture cells, block flags, model/state metadata, and the renderer's normal candidate-face enumeration. It must not start the game, read a network resource, or require a raw live capture. It must enumerate the same candidate face immediately before the renderer applies the hidden-surface cull; it is not a post-mesh triangle heuristic.

Add these protected, versioned inputs:

```text
user-client/render/tools/decision-ledger.cjs
user-client/render/tools/reference/fun-004cf8db-v1.cjs
user-client/render/data/decision-ledger/v1/fixtures.json
user-client/render/data/decision-ledger/v1/coverage.json
user-client/render/data/decision-ledger/v1/oracle.jsonl
user-client/render/data/decision-ledger/v1/geometry-availability.json
```

`fun-004cf8db-v1.cjs` is a literal transcription of the decompiled control flow, including `join_tag_guard`, the `nb.id <= 99` early return, the pinned `general_occlude(nb,self)` adapter, `HIDESIDES`, same-id comparison, and `ROTATE` state comparison. It returns `{ cull: 0|1, path: string }`. The renderer adapter returns the same shape. `1` always means cull the shared face.

`oracle.jsonl` is the pinned reference output; the gate generates a separate temporary *current* ledger and never rewrites the oracle during an arm run. `fixtures.json` names the four fixture revisions and their SHA-256 values. `coverage.json` declares the exact predicate/path scope and expected covered-candidate count per fixture.

### One record per candidate face

JSON Lines, canonically key-sorted and sorted by `(world, section, cell, direction, slot)`. Each record is one candidate face, never an aggregate:

```json
{
  "schema": 1,
  "ledger_version": "fun-004cf8db-v1",
  "fixture_version": "four-worlds-v1",
  "world": "furys_storage",
  "section": "0x0123",
  "cell": [41, 73, 12],
  "slot": "0x68",
  "direction": "+z",
  "self": {"id": 253, "packed": 65789, "dflag": 131074, "join_tag": 0},
  "neighbour": {"id": 253, "packed": 65789, "dflag": 131074},
  "state": {"self_low12": 253, "neighbour_low12": 253, "xor_low12": 0, "xor_high_state": 0},
  "reference": {"cull": 1, "path": "same-id"},
  "renderer": {"cull": 0, "path": "same-id"},
  "scope": "same-id-reachable",
  "covered": true
}
```

`section` uses the native-diff section identity. `cell` is mandatory because several faces can otherwise have the same requested tuple `(block id, neighbour id, state, direction, section, slot)`. `packed`, dflags, and join-tag are retained so the result is reproducible and the comparison does not silently substitute a lossy state key.

For this first predicate, `scope == "same-id-reachable"` iff all are true: join-tag guard is false; `neighbour.id & 0xfff > 99`; the pinned general-occlude adapter returns false; `self.dflag & 0x20000 != 0`; and `(self.packed ^ neighbour.packed) & 0xfff == 0`. This is the only intended-mismatch population in v1. The ledger nevertheless emits every renderer candidate face in the four fixtures, with `scope: "out-of-scope"` where appropriate, so absence cannot be hidden by filtering before enumeration.

### Coverage contract

A candidate is **covered** only when all of these hold:

1. it is enumerated by the renderer candidate-face hook;
2. its fixture/world/section/slot is in the pinned fixture manifest;
3. all inputs consumed by the reference predicate are present, including join-tag and the pinned general-occlude result; and
4. it has exactly one reference decision and exactly one renderer decision.

It is **uncovered** if a fixture cannot load, an expected candidate is absent, state cannot be decoded, a duplicate key is emitted, reference evaluation throws, a slot/section changes unexpectedly, or an expected count differs from `coverage.json`. The command exits nonzero and prints the first 20 canonical keys plus per-world counts. It must never drop an unsupported entry and report a green comparison.

The coverage report prints, per world: `all candidates`, `same-id-reachable expected`, `covered`, `uncovered`, `reference-cull`, `renderer-cull`, and `mismatches`. Gate input is invalid unless `uncovered == 0` for every expected scope count. New candidates outside v1 scope are reported, not scored; a new candidate that matches an expected scope selector is an uncovered failure until an explicit re-pin updates the expected count.

## 2. Tier 1: decision correctness gate

Let `I` be the pinned set of covered `same-id-reachable` keys in the oracle. For a tree `T`:

```text
m_T(k) = 1 if renderer.cull_T(k) != reference.cull(k), else 0
M_T    = sum(k in I) m_T(k)
```

A Tier-1 correction passes only if:

- protected-path/tamper checks and `node --test user-client/render/*.test.cjs` pass;
- the reference and oracle hashes equal the pinned versions;
- coverage is complete as defined above; and
- `M_after < M_before`.

The report must print `fixed = |{k: m_before=1, m_after=0}|`, `introduced = |{k: m_before=0, m_after=1}|`, `persisting`, and `M_before -> M_after`. Fixing some records while introducing others is allowed only when the fully covered, pinned intended mismatch count strictly decreases; it is not allowed to hide introduced records. Any introduction outside `I`, or any change to an out-of-scope reference/renderer decision, is reported as `scope escape` and fails v1. This makes the first build narrow: it cannot use this gate to justify unrelated culling changes.

### Native-backed per-block geometry non-worsen guard

Where native geometry ownership is available, maintain a pinned availability map keyed by `(world, section, slot, block_id)`. For each available key `g`:

```text
E_T(g) = abs(renderer_triangles_T(g) - native_triangles(g))
```

Tier 1 requires `E_after(g) <= E_before(g)` for every available key touched by a changed intended ledger record. It prints the complete touched-key table. A greater value is a hard failure, even if `M` falls.

`geometry-availability.json` must explicitly list both `available` keys and each unavailable reason. For the smallest build, raw native per-cell geometry is absent in this worktree, so the map is expected to contain no `available` keys and to print `geometry guard: 0 applicable; raw native ownership unavailable`. That is not a fabricated geometry pass; Tier 2 remains the mandatory protection until this map is populated.

## 3. Composition with Tier 2

Run both tiers, every time, after the existing no-edit and conformance checks. Tier 2 still runs `native-diff.cjs --world=W` for all four worlds; it validates its signed-total parse cross-check and records per-slot vector digest and `A_T(W) = sum_slots abs(ours-native)`.

Normal pass:

```text
Tier 1 passes
AND Tier 2 has at least one A_after(W) < A_before(W)
AND no A_after(W) > A_before(W)
```

Tier-1 override pass (the only exception to Tier 2's historical no-worsen rule):

```text
Tier 1 passes
AND every Tier-2 parse/digest/fixture check succeeds
AND every changed decision is in I
AND each world delta A_after(W)-A_before(W) <= reviewed_budget(W)
AND the change has an approved override record for this exact ledger/reference/fixture hash triple
```

An override does not suppress Tier 2: its complete four-world table is printed and persisted with the arm result. It is a bounded, reviewed exception, not a rebaseline.

Store reviewed override records outside arm-editable paths, for example `/opt/recursion/state/gsc/decision-gate-overrides.json`. An entry must contain: immutable `id`; predicate; ledger/reference/fixture SHA-256 values; allowed source paths; `M_before`, expected `M_after_max`; each world’s maximum permitted `A` increase; expiry; RE evidence/reviewer; and approval commit or task id. For the known same-id correction, the reviewer must consciously approve any allowance such as `furys: 0, vikings: 6, chickenlips: 198, watersigns: 0`; these are limits, not defaults inferred by the gate.

If an `A` increase exceeds its approved value, has no matching override, the override is expired, a non-target world moves unexpectedly, or any parsing/coverage check fails, the composite gate fails with `TIER2_BUDGET_EXCEEDED` and emits an escalation containing the world/slot deltas and decision keys. There is no automatic re-pin and no automatic budget increase.

## 4. Versioning, tamper resistance, and trust

The gate pins and prints SHA-256 for the renderer commit, fixture manifest, reference transcription, oracle ledger, coverage manifest, geometry-availability map, and any override record. The initial gate’s protected-path list includes all `tools/`, `*.test.cjs`, `render/data/`, the reference transcription, oracle, ledger manifests, and baseline data. It checks both unstaged/staged changes and the arm diff against its merge base. An arm may change renderer implementation only; it may never alter the reference, oracle, fixture, tool, tests, or override record.

A maintainer-only re-pin command is required:

```text
node user-client/render/tools/decision-ledger.cjs --re-pin --reason=<ticket> --reviewer=<name>
```

It refuses a dirty tree, runs conformance and the full four-world ledger, writes a new version directory, and prints old beside new: hashes, expected-covered counts, reference-cull counts, mismatch totals, added/removed keys, and every changed reference decision. The re-pin diff and reason are reviewed/committed before it becomes a gate input. Re-pin is forbidden during an arm result.

A transcription can be wrong and can make `M` falsely reach zero. Therefore Tier 1 is a correctness signal only for the exact pinned predicate, never proof that the emitted mesh is native-correct; Tier 2 remains mandatory telemetry and a hard bounded-regression guard.

Promote a transcription to override-eligible only after all are recorded in its version directory:

1. two independent reviewers map every return/branch and operand direction to the decompilation, specifically `general_occlude(nb,self)` rather than a unary substitute;
2. a boundary-vector test suite covers every early return and both same-id outcomes: join-tag set, neighbour id 99/100, general true/false, no HIDESIDES, different id, same id/no rotate, same id/rotate with equal high state, and same id/rotate with different high state;
3. an independent second implementation produces identical decisions for the pinned four-fixture ledger; and
4. when an offline native witness becomes available, its isolated shared-face observations agree with the predicted cull/keep outcomes. Until (4), the version may gate engineering progress but cannot authorize a Tier-2 override without explicit human exception noted in the override record.

## 5. Smallest first build

1. Add the protected v1 reference transcription and exhaustive boundary-vector tests for `FUN_004cf8db`; call the already-pinned general-occlude adapter but do not alter it.
2. Hook candidate-face enumeration at the existing HSR decision point and emit canonical JSONL for the four seeded fixtures.
3. Build and commit the v1 oracle/coverage manifests from the unmodified baseline; fail on any uncovered expected tuple.
4. Implement Tier 1 for only `same-id-reachable`. Add a regression test proving a HIDESIDES, non-HOMOGENOUS same-id pair is `reference.cull=1` and current renderer decision is `0` before the renderer fix.
5. Move the renderer same-id test out of the HOMOGENOUS-only path, using existing packed/state helpers; do not change general occlusion or any other HSR arm.
6. Run the four-world Tier-1 report, conformance, and Tier-2 telemetry. Expect the known correction to reduce `M`; do not accept it if it has uncovered records or scope escape.
7. Require a separate reviewer to create an exact, expiry-bounded Tier-2 override record before accepting the known `+6`/`+198` count movement. Without that record, report the Tier-1 success and fail the composite gate.

**Likely implementation files:** `user-client/render/mesh-chunked.js` (same-id arm and decision hook); new protected tooling/data paths above; `/opt/recursion/scripts/gsc-decision-gate.sh`; and a small wrapper/update to `/opt/recursion/scripts/gsc-nativediff-gate.sh` so Tier 2 is always invoked, never bypassed.

**Verification:** `node --test user-client/render/*.test.cjs`; decision-ledger coverage report for all four fixtures; composite gate on unchanged baseline (no progress) and on the known same-id fix (Tier 1 passes; Tier 2 either normal-passes or requires the exact reviewed override); tamper tests for each protected path; malformed/missing fixture and oracle tests that fail loudly.
