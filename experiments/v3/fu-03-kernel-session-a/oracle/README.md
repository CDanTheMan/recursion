# FU-03 kernel reference oracle (session A)

An **independent reference oracle + bounded trace-validity checker** for the FU-03 kernel,
authored from the prose specification in
`docs/v3/research-lane/followups-20261002/raw/ds-FU-03-formal-model-vectors.md`
(sections 3, 4, 5, 8 and 9). Pure Python 3.12 stdlib, deterministic, provider-free, no network.
It does **not** import, call or consult any TLA model, live reducer, provider or host action.

Evidence class: reference implementation / inference and locally observed. This is not
acceptance, not the integrated-bound TLC gate and not a kernel freeze.

## Files

| Path | Role |
|---|---|
| `refstate.py` | `RefState(log)`, `RefValid(log)`, `RefProject(log)`; explicit command/event/state records; deterministic CBOR and the domain-separated SHA-256 preimage `D(domain, epoch, value)`. |
| `trace_checker.py` | Bounded bridge: replay a finite trace (events, observed states/projections, or explicit admissions) against `RefState`; report the **first divergence index**. |
| `vectors/vectors.json` | Language-neutral normative corpus: canonical bytes/ordering, duplicate command id, lease/authority fencing, PAUSE/epoch race, effect safety, replay determinism/refusal, trace controls, digest domains. |
| `check_oracle.py` | Gate: runs every vector and the trace controls, asserts determinism and projection binding, fails loudly. |

## Run

```text
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/oracle/check_oracle.py
python -X utf8 -B tools/check_public_scope.py
```

Both must pass. The trace checker can also be run directly on a trace JSON file:

```text
python -X utf8 -B experiments/v3/fu-03-kernel-session-a/oracle/trace_checker.py path/to/trace.json
```

## What the oracle implements

- **State** exactly as the section 8 state map (schema epoch, aggregate, ordinal, tail, goal, plan,
  lease, writer, pause epoch, paused, status, owner, attempt, effect, timer, result, cancelled,
  receipts, outbox, retry ready).
- **Admission** in the section 4 ordered precedence: duplicate id (cached on equal digest,
  `COMMAND_CONFLICT` on unequal), expected ordinal/digest, aggregate/task/principal/capability,
  goal, plan, writer, worker lease/owner, verifier, pause epoch, paused, cancelled, then the
  per-kind semantic, timer, effect and capacity guards.
- **Reduction** of one event per admitted command, except `PrepareEffect`, which is one atomic
  two-event batch (`EffectPrepared`, `OutboxEnqueued`) with a single receipt.
- **Refusal taxonomy** codes 0–17 and the stable detail enums from section 9.
- **Digests** `D(domain, 1, C(x)) = SHA-256("RCV1/" || domain || 00 || U16(epoch) || U64(len) ||
  C(x))` for the seven declared domains over canonical CBOR.

`RefProject` returns the fixed 16-field tuple `(aggregate, ordinal, tail, status, goal, plan,
lease, owner, attempt, paused, pause epoch, cancelled, result value, verifier result, effect
status, timer status)`.

## Vectors

Each vector has a typed input and an expected result. Categories:

- `canonical_bytes` / `canonical_decode` — canonical CBOR heads, map ordering, duplicate keys,
  nonshortest, tags, undefined, bad UTF-8, truncation, trailing bytes, canonical roundtrip.
- `admission` — duplicate id equal vs unequal digest, lease/owner/writer/goal/plan/aggregate/
  principal/capability fencing, PAUSE and pause-epoch races, cancel, retry/timer, effect token
  and state safety.
- `log_reduction` — folding accepted commands, atomic `PrepareEffect`, effect reconciliation,
  retry token reset, plus tamper controls (flipped digest, wrong predecessor, ordinal gap,
  removal, duplication, unknown schema) that must yield the exact first divergence index.
- `trace` — bounded trace-bridge controls for accepted and refused steps.
- `digest_domains` — the same typed value under all seven domains and two epochs must not collide.

`check_oracle.py` additionally builds observed-state traces and proves the checker catches a
corrupted observed digest at the exact first index.

## What this does NOT prove

- Not a machine-checked refinement. It checks **one finite observed behaviour** against the
  declared abstraction, assuming the supplied observations are faithful and complete.
- Not the integrated-bound TLC run, not 36/36 mutant classification, not the Alloy cross check.
- No quantification over all executions, no fairness/liveness, no exactly-once external effect,
  no storage durability, no OS containment, no provider trust.
- The reference equations themselves are independently authored but **not proven**; the
  specification is a candidate (`CAND RCV1 20261001`) with several details explicitly recorded
  as candidate completions. Sharing a mistaken requirement is not excluded by authorship.
- Digests are concrete SHA-256. The specification's symbolic injective `DigestOf` is stronger;
  a matching digest here is not a collision-resistance or authentication claim.

## Recorded local assumptions (candidate completions)

The source leaves some encodings unspecified. This oracle fixes them explicitly and documents
them so a reviewer can compare rather than infer:

1. The event-specific payload `payload[1]` for both `EffectPrepared` and `OutboxEnqueued` is the
   captured token/fence map (token, aggregate, task, goal, plan, lease, writer, pause epoch,
   attempt, effect id, issuing command id, owner).
2. An outbox entry uses that same fence map layout, ordered by first enqueue ordinal.
3. `Reduce`/`RefState` re-checks the command's expected-state binding (in addition to schema,
   aggregate, writer epoch, ordinal, predecessor and digest) so a committed event must carry the
   pre-state it was admitted against. A duplicate command id committed as a second event is
   `FIELD_INVALID/BAD_TRANSITION` on equal digest and `COMMAND_CONFLICT` on unequal digest.
4. The effect token is `D("effecttoken", 1, [aggregate, effect id, attempt, issuing command id])`
   per section 5.
5. `Verify` is a worker-kind for lease purposes (current numeric lease, no owner equality), and
   all verifier actor/binding failures use `VERIFIER_INVALID`.
