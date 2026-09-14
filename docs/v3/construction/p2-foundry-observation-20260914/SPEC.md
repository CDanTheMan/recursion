# P2 foundry observation contract

Date: 2026-09-14

Parent: `goal-recursion-v2-execution-fabric`. Product target: Recursion v3. The legacy
goal identifier preserves lineage. External Devin/SWE-2 workers research, develop and
test on Recursion; they are not product-runtime agents.

## Source and scope binding

`TASK_BASE` is `e627cd93bac473094bc99e8fa29c8d62bae526a2`, the required head of
`codex/v3-integration-20260914`. Only the four packet files named in `NEXT.md` may differ
from that commit. The focused unittest contains the additive source/scope check and pins
these reader dependencies at `TASK_BASE`:

| Dependency | Git blob |
|---|---|
| `tools/construction_swarm/foundry.py` | `650a2871c912c20f37d2e822e911ae42ddfd24b6` |
| `tools/construction_swarm/ledger.py` | `6cc4b25466f99bf8a0e406db0eefb4b385a1ecaa` |
| `tools/construction_swarm/runner.py` | `16c69e6c3aad4b2a9b97910a751594f8d2b01678` |
| `tools/construction_swarm/contracts.py` | `aff5cc8f443272be3315e4f8bfba6734990eb50e` |
| `tools/construction_swarm/p2_access.py` | `6d41f0195b74d103269133c4279c1b002e3c8669` |
| `tools/construction_swarm/foundry_tools.py` | `523766a6600d779259baee5973e3a9ae3464e87e` |
| `tools/construction_swarm/foundry_client.py` | `b7ba82058dd6d4ee39fbe8f458bac8e6a68d2c87` |

The existing integration and handoff gates are unchanged. This successor adds no
canonical registry and edits neither foundry nor P2.

## Actual source schema

The adapter observes one configured foundry run directory per project. It reads the
schema created by `Ledger` and consumed by `foundry.report`:

- `ledger.sqlite` tables `meta(key,value)`, `jobs(id,spec,state,attempts,result_hash)`,
  `attempts(job,number,state,started,ended,receipt)` and
  `events(seq,at,event,detail)`;
- `meta.plan` plus `meta.plan_hash`, with each `jobs.spec` equal to the corresponding
  immutable plan job;
- `attempts/<job>/<number>/filing.json`, bound by `jobs.result_hash`;
- the current ledger receipt and matching `receipt.json`;
- receipt-bound `packet.json`, `transport.json`, `client-output/export.json`, and each
  `tools/<number>/receipt.json` plus its request digest.

This is the same digest chain checked by `foundry.report`, with additional read and
aggregate byte ceilings. A worker return is the current attempt's durable `returned`
state. Independently accepted output additionally requires the job's `accepted` state
and a matching durable `head-decision` event whose reference is retained. Neither fact
is canonical Hermes acceptance. Job/current-attempt combinations must be reachable through
the bound `Ledger` reserve, finish, retry, recovery, reconciliation and decision transitions;
contradictory combinations refuse the snapshot rather than asserting acceptance or releasing
an unknown hold. Legitimate failed-attempt retry and unknown-attempt reconciliation remain
observable.

## Read projection

`FoundryObservationAdapter` implements the existing `AccessService` adapter interface for
`status`, `tasks`, `task`, `events`, and `artifact`. `main(... serve ...)` explicitly
constructs that adapter, the existing grant store and `AccessService`, then calls the
existing foreground `serve` function. Construction performs no service activation by
itself.

- P2 transport authentication and grant-scoped project checks remain authoritative.
- A project maps to exactly one absolute run directory; aliases are refused.
- Status and task views identify the foundry run/source, observed work, current attempt,
  returned state, foundry-local review state, holds, result availability and unavailable
  fields. Route quota, spend, leases outside this ledger, goal progress, canonical task
  state, canonical acceptance, canonical revision and Hermes authority remain unavailable.
- `running` and `unknown` current attempts remain visible as held. Missing terminal
  evidence never becomes failure, return or release. A malformed job/attempt state conflict
  refuses the observation; it cannot turn an `unknown` job into a known effect or make an
  `accepted` job independent of a returned current attempt.
- Freshness is based on the latest durable foundry event timestamp. P2 marks an old or
  absent timestamp stale/unavailable; the adapter does not refresh it to wall-clock time.
- SQLite `events.seq` and the latest event are observation facts, but unchanged P2 replay
  accepts only an integer and cannot bind that integer to a run across service restart.
  Therefore this adapter exposes no `last_event_cursor` and refuses every `events` replay
  request with `snapshot_required`. No cross-run or canonical cursor is invented.
- Artifact handles are derived, never caller paths. A handle is exposed only after the
  original ledger result digest, retained receipt, receipt file and all receipt manifest
  digests verify. Missing, malformed or mismatched evidence is unavailable/refused.
  The artifact read reopens the fixed file, verifies its full original digest and returns
  only a bounded base64 slice.

## Bounds and refusal

Each read uses a read-only SQLite transaction and checks the database identity before and
afterward. The first coherent observation pins device/inode, plan digest, run id and source
commit for that project; later replacement refuses. Symlink roots/databases/artifacts,
missing paths, malformed or partial SQLite/JSON, schema drift, inconsistent plan rows and
oversized evidence refuse or appear explicitly unavailable. Valid in-flight absence is not
treated as corruption.

Limits are 32 MiB per database, 64 MiB aggregate evidence verification per request,
32 MiB per evidence file (matching the foundry export ceiling), 1 MiB returned artifact
slices, 3 MiB tool receipts (matching `Broker.call`), 256 jobs, 2,048 attempts,
4,096 events, 100 projects, and the inherited P2 request/response, reader and timeout
bounds. Tests use temporary fixtures under 32 MiB, no child over 15 seconds, a focused
gate ceiling of 120 seconds and zero inference/provider calls.

## Frozen acceptance outcomes

The focused gate must prove:

1. coherent completed and in-flight work/attempt/result views;
2. returned output is not accepted until a matching independent decision exists;
3. running and unknown attempts remain held and observable;
4. missing, malformed, partial and replaced records refuse or remain explicitly
   unavailable without changing input bytes;
5. transport grants and adapter mappings preserve project isolation;
6. old durable event timestamps produce stale envelopes;
7. actual `events.seq` remains observable only as a non-cursor fact and all unbound P2
   integer replay requests refuse across both current and restarted adapters;
8. verified digest-bound artifacts read correctly, and missing/tampered digests refuse;
9. the explicit entry point reaches only the existing read service, never foundry
   initialization/run, schedulers, workers or providers;
10. contradictory accepted/unknown and unknown/failed job/current-attempt pairs, plus a
    missing current attempt, refuse without mutating input; valid retry, recovery and
    reconciliation states remain observable; and
11. the exact `TASK_BASE`, seven dependency blobs, clean tree and four-path scope hold.

Required commands:

```text
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_foundry_observation
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p1_core
python -X utf8 -B -m unittest -v tools.construction_swarm.test_p2_access
python -X utf8 -B docs/v3/construction/next-work-20260914/check_handoff.py
git diff --check e627cd93bac473094bc99e8fa29c8d62bae526a2 HEAD
```

An existing completed-run smoke is optional, read-only and must be labelled observed or
unrun. It cannot activate a service or extend access. This packet does not authorize
production/fleet/service activation, providers, configuration/auth/model/cron/autonomy
changes, publication, merge, or a claim of completed canonical integration.
