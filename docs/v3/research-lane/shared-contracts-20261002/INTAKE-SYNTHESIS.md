---
title: Shared contracts + extensibility intake synthesis (2026-10-02)
status: research-evidence-not-a-decision
last-updated: 2026-10-02
---

# Shared contracts + extensibility intake synthesis

Research evidence only — not adoption, not execution. Source: the hash-verified intake here
(`check_intake.py`). The Dot delivered the requested **R-SC reconciliation** plus two proactive
companions, all pinned to repo commit `5b55e55…` (merged PR 147). All proposed runtime/performance
vectors are **UNEXECUTED**.

## What landed

| File | What |
|---|---|
| `Recursion_Shared_Contract_Reconciliation.md` | answers the 21 R-SC questions: one candidate field map + joins + falsifiers |
| `Recursion_Harness_Orchestration_Performance.md` | ACP vs structured vs CLI topologies; route-adapter vs ACP-first; a provider-free benchmark design |
| `Recursion_Prompt_Plugin_Skill_Architecture.md` | bounded instruction compilation; capability states; discovery; skill retention/compaction |
| `synthetic_benchmark_corpus.json` | inert, unexecuted fixtures for later controlled testing |

## Shared-contract reconciliation (key content)

- **Candidate, not adopted.** Identity domains that must never collapse (writer/work/pause fences,
  incarnations, route vs route-descriptor epochs, context/config/release epochs, command/operation/
  attempt ids, workspace/repository/instance/snapshot/materialization ids, grant epoch). No
  unqualified scalar `epoch` is admissible.
- **Canonical command key:** `(admitted_authority_domain, command_id)`; `content_digest` is the
  equality/conflict predicate, **not** a third key component.
- **Artifact/ContentEnvelope:** `ArtifactRef = (object_type, id, version, content_digest)`;
  `ContentEnvelope` = 18 base names; `authority_carried_none`; one loss record; digest-domain binding
  belongs to the containing interpretation.
- **Receipt stages:** eight independent facts (saved_locally / received / delivered / admitted /
  started / observed / settled / verified) — never flattened to one boolean.
- **Publication ordering:** P0 private staging → P1 durable disclosure intent → P2 first check →
  P3 release → P4 verify/register → P5 second check → P6 publish → P7 reconcile; receiver-fence
  installation is a distinct serial barrier.
- **Resource invariants:** one conserving algebra (`S + O + H + P ≤ L`); uncertainty annotates,
  never adds; settlement atomic; retry/fork/session/node change never reduces settled or duplicates
  outstanding. Decisive vectors ID/C/P/R/D/RF/Y/F series, all unexecuted.

## Orchestration performance (key content)

- Five distinct layers (semantic contract / control interface / transport-codec / topology /
  qualified route); **ACP is not a cost label** — "ACP vs JSON/API" is a false dichotomy.
- Tradeoff table across direct structured, first-party ACP, bridges, persistent CLI, one-shot CLI,
  PTY (compatibility only). **No universal speed winner.**
- Three discriminators: same boundary, same route/different residency, same semantics under pressure.
- Provider-free benchmark: arms H-A…H-E; endpoints (cold launch, warm admission, first-event,
  control/fence, retention, verified outcome, p50/p95, resources, recovery); planted-violation
  oracle; workloads W1–W3; stop conditions; immutable identity bundle. All **unexecuted**.

## Prompt/plugin/skill architecture (key content)

- **Mechanism for the D-034 thesis:** a small versioned behavioral core + a **task-scoped context
  compiler** (eight passes: read cut → resolve graph → mandated contributions → retrieve optional
  with recorded omission → admit disclosures → render with span map → fit/applicability → dispatch
  through existing admission). Immutable per context epoch; stable prefixes are an optimization
  only within authority.
- **Injection safety:** separate trusted-control and untrusted-content paths; imported metadata and
  claimed approvals are requests/data until resolved against canonical policy; prompt-only defense
  is an intentionally inadequate negative control.
- **Seven capability states** (Installed/Enabled/Authorized/Available/Selected/Loaded/Executed) are
  independent; disabled-path metadata stays out of the prompt.
- **Discovery:** mandatory closure + bounded optional retrieval; completeness contract; zero-match
  ≠ absent capability.
- **Skill retention/compaction:** three retention classes + the seven-step rehydration transition;
  a rehydrated instruction is loaded again, not newly approved.
- **It explicitly does NOT establish scale** — no token/cache/latency/subscription saving is proven.

## Relation to the thesis (D-034)

The two companions supply the *mechanism* the thesis depends on (deterministic, injection-safe
composition; per-workflow-qualified performance), and both are explicit that **scale and savings are
unproven**. That is exactly right: D-034 is a claim to earn. Notable open item: the delivered
reconciliation scopes its authority to D-018…D-033 and **does not reconcile D-034** — the new packet
`dot-research-20261002d` bakes D-034 in so the next pass can.

## Next

- Commissioned packet `docs/v3/prompts/dot-research-20261002d/` (R-PC prompt/context composition;
  R-UI capability-driven UI projection; R-MOB mobile/remote clients) extends these.
- The synthetic corpus and all vectors remain unexecuted; the benchmark/compiler/discovery runs stay
  behind their own admitted local sessions.
- No technology, route, privacy guarantee, saving or entitlement is qualified by this packet.
