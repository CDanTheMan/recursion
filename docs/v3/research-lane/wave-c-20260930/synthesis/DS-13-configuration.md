# DS-13 — configuration architecture and operator control (synthesis)

## Provenance

- Raw: `raw/ds-DS-13-configuration.md`.
- Source-prompt: DS-13 — configuration architecture and operator control.
- Session: Wave C Deep Research (self-contained handoff); retrieved 2026-09-30.
- Status: research evidence, not a decision. Not independently verified by Recursion; no rerun.
- Architecture research only: no repository, runtime, provider, model, authentication, credential, deployment, spending, publication, or configuration changes were made.
- Evidence classes preserved from the report: **[Source-documented]** (a cited primary source states it), **[Inferred]** (architectural conclusion derived from those sources and the brief), and **[Unverified]** (implementation evidence still needed). There are **no "locally observed" claims** because no repository was inspected.
- Claims are attributed to "the report's sources"; no URLs are added.

## The question

Can Recursion v3 use **one versioned, typed configuration architecture** to make files, interactive CLI, Telegram, editions, goals, tasks, plugins, routes, nodes, PAUSE, Full Access, and terminal layouts predictable, transactional, portable, explainable, and rollback-safe? The report treats the brief's accepted decisions as constraints and separates the structural schema, canonical representation, human syntax, and transaction protocol as different problems.

## Key findings

- **One schema, not one parser.** [Inferred] A single typed data model and metadata vocabulary can cover every named surface, but "one schema" must not collapse into one parser, file syntax, or validation mechanism. The strongest candidate is **JSON Schema 2020-12 + a mandatory Recursion vocabulary → restricted I-JSON instance model → RFC 8785/JCS canonical bytes → a deterministic non-model resolver for merging, authority, provenance, and invariants → multiple editors emitting the same typed edit command.**
- **Schema and canonical bytes.** [Source-documented] JSON Schema 2020-12 remains current in 2026 and supports vocabularies/meta-schemas; RFC 8785 JCS constrains inputs to I-JSON values, rejects duplicate names, requires IEEE-754-compatible numbers, and **does not normalize Unicode strings** (it is Informational, not Standards-Track).
- **JCS consequences.** [Inferred] Money/quotas/large counters must not be arbitrary floating point (use bounded integers or tagged decimal strings); security-sensitive identifiers need a narrow ASCII grammar; duplicate-key rejection must occur **before** object construction.
- **Human syntax stays provisional.** [Source-documented/Inferred] TOML 1.1.0 leads because it is small and rejects duplicate table definitions, but it permits `inf`/`nan`, native dates/times, and large integers outside the I-JSON/JCS model, so a strict profile is required. YAML 1.2.2 is a conditional comparator behind a tighter JSON-shaped subset; direct canonical JSON is the fallback. The report recommends **freezing the architecture but not the human syntax**.
- **Smallest orthogonal field set.** [Inferred] **18 setting domains / 55 first-order persisted leaves** (excluding repeated records and transaction envelopes), across **seven scopes** (`built-in defaults < edition preset < installation/authority-domain < project < parent goal < task < ephemeral operator override`). Editions are presets, goals/tasks are scopes, CLI/Telegram are command producers — not duplicate configuration systems.
- **Full Access, PAUSE, credentials.** [Inferred from DS-13] No `full_access: true` field exists; Full Access is an editor macro expanding to an explicit capability vector, and `sovereign` is separately requested and acknowledged. PAUSE exposes `checkpoint`/`interrupt`/`drain` modes but the emergency stop sits outside configuration and current immediate-halt behavior cannot be displaced by a config value. Credentials are opaque typed references; validation sees only metadata (e.g. availability, non-secret fingerprint), never secret material.
- **Merge algebra.** [Inferred] Four operator families replace universal "most specific wins": `keyed-override` (preferences), `meet` (authority/egress/budget ceilings: intersection, min, conjunction, or lattice meet), `stable-id` (plugins: union distinct IDs, conflict rejects), and `explicit-binding` (credentials only through an authorized typed operation). Requested and effective states are distinct; a child cannot override an ancestor ceiling; deletion is a typed "unset" mutation rather than `null`.
- **Defaults and provenance.** [Inferred] Schema `default` is an annotation/editor hint only; effective defaults enter via the explicit built-in-defaults scope. The resolver emits typed provenance and reason codes **with zero model tokens**, listing **all causally relevant contributors** because an intersection can be jointly determined, and preserving `unknown` distinctly from empty/zero.
- **Narrowing/widening and acknowledgment.** [Inferred] Widening compares effective-before with effective-after, not the text, catching preset/edition changes that unblock stored requests. Six authority-edge classes (capability, egress/network, privacy exposure, spending/billing, publication, credential binding) require acknowledgment; a receipt binds principal, session, scope, schema version, command ID, before/after digests, widened paths, reason code, expiry/one-use semantics, the authority decision, and **what the operation does not grant**.
- **Cross-field constraints.** [Inferred] At least **16 named constraint families** (engine availability, tool capability, context/resource fit, memory privacy, default route existence, route target validity, delegation ceiling, verification feasibility, schedule capacity, placement feasibility, resource ceiling, node reference validity, PAUSE mode validity, plugin identity validity, transport binding validity, feature availability) with stable reason codes, sitting above **silent invariants** rechecked after every resolution and migration.
- **Transactions.** [Source-documented/Inferred] HTTP `If-Match` is the optimistic-concurrency precedent: an edit names the exact revision+digest and mismatch means "stale; recompute," not last-write-wins. A deterministic ledger `(scope_id, command_id) → {request_digest, result, committed_revision}` makes replay idempotent (same ID + same digest returns the original result; same ID + different digest is a hard conflict). Desired state commits atomically, but each target applies a **complete effective revision** with per-target receipts (`applied`/`pending`/`blocked`/`failed`/`superseded`); rollback is a new authorized transaction, not an invisible pointer rewind.
- **Lifecycle and migration.** [Inferred] Four lifecycle classes are application contracts: `goal-frozen` (authority ceilings, verification minimums, critical credential identities — only via GoalSpec amendment), `checkpoint-applied`, `live`, `restart-required`. Runtime states are `committed → pending | applied | blocked` and `pending → applied | failed | superseded`; "committed" means accepted desired state, not that every worker runs it. Migration is pure, staged before commit, lossless where declared reversible (`down(up(x))` canonically equal to `x`), and blocks rather than silently dropping unrepresentable values.
- **Portability and editors.** [Source-documented/Inferred] Portable paths are logical roots plus relative segments (`project`, `config`, `state`, `cache`, `runtime`, `node-local`), mapped through XDG roots on Linux and Windows Known Folders at application time — never host-expanded strings inside the digest. The round-trip invariant is semantic canonical equality, not comment/key-order preservation; file, CLI, and Telegram editors must compile to the same edit envelope and yield identical canonical digests.
- **Competitor and testing.** [Source-documented] CUE is the credible challenger (data, schema, and constraints unified with order-independent conjunction), but that model does not naturally express the ordered seven-scope preference resolution; it stays in a conformance bake-off. NIST's 2024 combinatorial-testing work supports low-order coverage with large suite reductions but does not make pairwise coverage sufficient for authority-sensitive paths.
- **Silent invariant.** [Inferred from DS-13] The central safety property is architectural, not configurable: no schema value, edition, feature flag, task override, transport command, plugin, or Full Access expansion may disable the integrity, authority, privacy, or verification checks that decide whether a configuration becomes effective.

## Recommendation and falsifier

**Freeze the configuration architecture but not the final human file syntax.** Each recommendation carries a competing option and a decisive falsifier:

1. **Freeze JSON Schema 2020-12 + required Recursion vocabulary** (vs. CUE as authoritative) — falsified if independent implementations cannot agree on schema acceptance, vocabulary behavior, typed output, and reason codes, or schema/resolver duplication grows materially larger.
2. **Freeze restricted I-JSON + JCS** (vs. a bespoke format) — falsified if cross-language output is not byte-identical for the supported corpus or exact values need pervasive string encoding.
3. **Do not yet freeze human syntax; lead with restricted TOML 1.1, keep JSON fallback** (vs. JSON only, or restricted YAML) — falsified if parsers cannot identically reject the restricted fixtures or normal nesting becomes excessively ambiguous.
4. **Explicit merge operators** (vs. generalized field ownership or single overwrite) — falsified if a formal model reproduces every case with fewer ambiguous states and identical provenance.
5. **Optimistic CAS + command ledger** (vs. last-write-wins or pessimistic locks) — falsified if stress/property tests show CAS cannot meet UX/recovery needs without pathological conflicts.
6. **Atomic desired-state commit with per-target whole-revision receipts** (vs. global 2PC) — falsified only by a bounded deployment proving equivalent failure-safe atomic commit with a smaller failure surface.
7. **Opaque credentials with separately authorized binding** (vs. inline values or generic reference override) — falsified only if an essential provider cannot expose a safe opaque-reference API and a safer alternative still prevents values entering config/logs/diffs.
8. **Pure, staged, lossless-where-reversible migrations with rollback as new intent** (vs. forward-only destructive migrations) — falsified only by a formally specified, independently reviewed recovery mechanism proven equivalent without snapshots.
9. **Preserve blocked feature intent across editions** (vs. delete/silently disable on downgrade) — falsified only by analysis showing reactivation risk that explicit acknowledgment cannot remove.
10. **Logical-root paths plus segments** (vs. persisted absolute paths/URIs) — falsified only if required workloads depend on host-native path semantics that cannot be represented losslessly.

The decisive gate: independent Windows and Linux implementations must pass the same adversarial corpus with **identical accept/reject decisions, identical canonical digests, identical effective values, and identical provenance/reason codes**; failure reopens the architecture, notably toward CUE.

## What this does not prove

- No implementation was inspected; the completion gate is satisfied for the **research deliverable**, not the product.
- No human file syntax, parser implementation, or serialization library is selected or frozen.
- The exact authority lattices for privacy exposure and publication remain unresolved and may be partially ordered or incomparable.
- Provider/engine identifier and cost-class semantics, plugin schema trust, schedule grammar, symlink/junction containment, adapter restart boundaries, terminal-layout extension grammar, remote-node attestation, and cross-transport authentication assurance are all **[Unverified]**.
- The configuration-complexity vector (18/55/7/4/16/4/6/6/12 and the 100% round-trip/equivalence targets) is a **candidate design metric, not an implementation measurement**.
- No secret values appear in the report and no file/config/path was edited, but a repository secret scan was neither possible nor authorized.

## Open Owner decisions

- The exact ordered lattices for `privacy_exposure` and `publication`.
- Which of the six authority edges require step-up authentication versus ordinary acknowledgment.
- Whether a blocked authority-bearing request may ever auto-activate after an upgrade (recommended answer: no; Owner confirmation needed).
- Whether credential binding identities are always goal-frozen or may rotate checkpoint-wise.
- The minimum independent-verification invariant configuration may never reduce.
- Which identifier classes must be ASCII-constrained.
- What counts as a billing widening when engine choice changes without a numeric budget change.
- Whether retained unsupported edition requests are visible by default.
- The authentication-assurance mapping for Telegram versus local terminal commands.
- The supported reversible-migration window.
- Whether plugin configuration may introduce a bounded plugin vocabulary or only product-standard JSON Schema keywords.
- Which adapter-defined properties may legitimately be `restart-required`.
- Whether, after a future constitutional PAUSE amendment, `checkpoint` is a default or a goal-frozen value.

## Relevance to later waves

This lane is a blocking prerequisite for the configuration schema, the authority/resolution engine, the transactional edit protocol, editor surfaces, edition gating, and migration tooling. Later waves should consume the report as a **candidate specification**: build the canonical conformance corpus (duplicate keys, TOML redefinitions, `-0`, exponent/precision boundaries, NaN/infinity, Unicode composition, line endings/BOM, YAML tags/aliases, migration round-trips), run Windows and Linux implementations against identical accept/reject, digest, effective-value, and reason-code expectations, and keep CUE alive as the competing bake-off until the schema/resolver split proves smaller and more auditable. Nothing here selects a parser, freezes human syntax, or resolves the open authority lattices.
