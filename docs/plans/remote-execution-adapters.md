---
title: Remote execution adapters — Cursor Cloud (Phase 6) and Grok Bot (Phase 7)
type: implementation-plan
status: shipped-inert
authorized: 2026-08-28
last-verified: 2026-08-28
execution_state: foundations-landed-disabled
related:
  - CONTROL_PLANE.md
  - docs/plans/recursion-v2-execution-fabric.md
  - docs/plans/engine-plugin-architecture.md
  - docs/audits/recursion-v2-infrastructure-audit-2026-08-28.md
  - schemas/control-plane/v1/remote-backend.schema.json
  - scripts/remote/README.md
  - state/DECISIONS.md#d-016
---
# Remote execution adapters — Phase 6 and Phase 7 foundations

This is the adapter layer of `docs/plans/recursion-v2-execution-fabric.md`: the Phase 6
Cursor Cloud client contract and the Phase 7 Grok Bot outbound dispatcher.

**Everything described here is inert.** No credential, no PAUSE change, no service, no cron
entry, no deployment, no publication, and no live state was touched. Nothing runs until a
human sets flags in the box `.env`, and the loop never writes those flags (CLAUDE.md rule 3).
Both adapters are constructed with an *injected* transport; the production transport refuses to
be constructed at all without a third, separate flag. The whole control suite therefore runs
against fakes and cannot reach the network.

## What landed

| Path | Role |
|---|---|
| `scripts/remote_assignment.py` | Immutable assignment contract, canonical digest, secret-reference contract, secret-material screen, typed error taxonomy. Pure. |
| `scripts/remote_backend.py` | Manifest resolution, transport seam, durable attempts, account-shared lease, PAUSE gate. `--validate` CLI. |
| `scripts/cursor-cloud-adapter.py` | Phase 6 client contract: models, create, status, stream, cancel, artifacts, usage, returned-ref reconciliation, restart recovery. |
| `scripts/grok-bot-dispatcher.py` | Phase 7 outbound signed-routine dispatcher: immutable redacted envelope, idempotent dispatch, retry reconciliation, proposal-only result channel. |
| `scripts/remote/` | Manifest directory. Ships a README and two `.json.example` files; **no loadable manifest**. |
| `schemas/control-plane/v1/remote-backend.schema.json` | Documentation/editor schema. The self-contained validator in `remote_backend.py` is authoritative. |
| `scripts/tests/remote-assignment.test.py` | Assignment, digest, secret screen, error taxonomy. |
| `scripts/tests/remote-backend.test.py` | Manifests, enablement chain, transport gating, attempts, lease, PAUSE. |
| `scripts/tests/cursor-cloud-adapter.test.py` | The Phase 6 gate properties, driven by a fake transport. |
| `scripts/tests/grok-bot-dispatcher.test.py` | The Phase 7 gate properties, driven by a fake transport. |

`state/remote/` (gitignored) holds the durable attempt journals, session projections and
proposals at runtime.

## What this is not

This is **not** Phase 1. The Phase 1 canonical registries — engine, provider, capacity pool,
model, host, sandbox, routing policy, project publication — and their v1 compatibility readers
are not built here. `remote_assignment.py` carries only the assignment subset the two adapters
must agree on, so they do not each grow their own digest and their own idea of what an
assignment is. When Phase 1 lands, the assignment contract should move to the canonical
registry and this module should become a reader of it.

It is also not Phase 2 (candidate import and serialized integration), not Phase 3 (assignment-
native evidence across the whole loop), and not Phase 8 (placement). Nothing in `work.sh`,
`publish.sh`, `notify.sh`, the outbox, or the engine plugin path was modified. Existing
evidence for D-014 and D-015 is untouched.

## Design decisions and the reasons behind them

### Secret references, never secret values

Every credential-bearing manifest field is `secret:<ENV_NAME>`. `validate_secret_ref` refuses a
reference naming a controller or deploy credential (`GITHUB_TOKEN`, `TELEGRAM_BOT_TOKEN`,
`OPENROUTER_API_KEY`, or any name starting `RECURSION_`, `SSH_`, `GIT_SSH`, `AWS_`, `HERMES_`).
A remote backend may hold exactly one credential: its own.

A Grok routine webhook URL is itself bearer-grade — anyone holding it can post to the routine —
so it lives behind `endpoint_ref`, and durable records store the reference, never the resolved
value. The refusal messages are written so they cannot echo a resolved value.

`screen_for_secret_material` runs over every manifest, envelope, attempt record and session
projection. It refuses credential-shaped **key names** and credential-shaped **values**, and it
reports a *label* (`github-token`) rather than the matched text — a screen that prints the
secret it caught is a leak with good intentions. The value patterns are anchored so ordinary
text does not trip them (`risk-register` contains `sk-`), and the key-name screen exempts any
name ending `_ref`, because that is the reference form and it has already been validated.

### The exact starting SHA

`source_sha` must be 40 lowercase hex. A branch, a tag, `HEAD`, an abbreviated sha and an
uppercase sha are each refused. A run bound to a moving ref cannot be reconciled against what it
actually built, and the Cursor Cloud create request puts this value — and only this value — in
`startingRef`.

### Isolated branch enforcement, twice

`build_create_request` derives the target branch from the project's `task_branch_pattern`,
forces `workOnCurrentBranch: false` and `autoCreatePr: false`, and refuses a target equal to the
default or integration branch or unmatched by `allowed_result_branch_patterns`. Then
`assert_isolated_branch_request` re-checks the **finished body**.

The post-check is not redundant. Construction can be reasoned about today; a post-check over the
exact bytes about to be sent is what survives a future edit to construction. The plan's Phase 6
gate asks for both ("impossible by request construction and post-check"), and the same predicate
runs a third time when a returned ref is reconciled.

### The independent-verification boundary

`reconciliation_input` records every returned branch and commit **per repository** and always
emits `verification_state = requires-independent-verification`. There is no branch, no flag and
no vendor payload that produces `verified`; that word belongs to the independent gate on
Hetzner. `gate_evidence` is `null` and `vendor_self_report_is_evidence` is `false`.

The vendor's own claims are kept as a *digest plus a key inventory*, not ingested verbatim.
Recording them verbatim would put unvetted vendor prose into canonical evidence; recording
nothing would lose attributability when the two later disagree. Downloaded artifacts carry
`evidence_class: advisory` and a sha256.

An unrecognised vendor status is a `malformed-response`, not a guess. Guessing that an unknown
string means "finished" is how a half-built candidate gets imported.

### Durable attempts, and what an open attempt means

An attempt record is committed **before** any request and closed after. That ordering is the
whole contract:

- a prior **succeeded** attempt with the same idempotency key → **replay** the stored result;
  a second POST would be a second vendor run and a second branch;
- a prior **open** attempt → `unreconciled-attempt`, a hard refusal. A process died between
  commit and close, so the request may already have landed. That is a question for a human, not
  a licence to re-send.

`reconcile_attempt` consumes an observation (`landed` / `not-landed` / `unknown`) and records
*who* observed it. `unknown` is **terminal** — it becomes `unreconciled` and needs a human.
Deciding "probably didn't land" is exactly how a duplicate dispatch happens.

The idempotency key is `sha256(backend, operation, assignment_digest, dispatch_id,
request_digest)`. It includes the assignment digest so a retry that quietly rebound the source,
pool or model cannot deduplicate against the original run. For the Grok envelope the request
digest deliberately **excludes `issued_at`**: the timestamp is inside the signed body so a
captured envelope cannot be replayed with a fresh header, but if it were inside the idempotency
key then the same logical dispatch retried one second later would be a different key and would
be sent twice.

Reads (status, artifacts, usage) do not consume attempts. A durable row per status poll would
drown the journal that exists to answer one question — "did a request that may have changed
remote state actually land?" — and a poll cannot change remote state. Reads update the session
projection instead.

### PAUSE

Every outbound path calls `assert_not_paused` **first**, before building anything, before
committing an attempt, before resolving a credential. Local awareness stays available: `recover`
enumerates open attempts and non-terminal sessions under PAUSE and reports
`provider_queried: false` rather than pretending the remote state is known. A paused box that
cannot tell you what it was doing is a failure, not a safety feature (D-012).

### The account-shared lease

Concurrency is leased per **capacity pool**, using `runtime-state.py`'s proven witnessed
mkdir/PID lock rather than a second implementation. Grok Bot ships with one slot because every
Bot on the account shares one cloud computer — one filesystem, one browser session, one set of
logins. Two Bots editing code are one writer with two screens. Cursor Cloud uses the same
mechanism to keep vendor runs inside the pool's measured concurrency rather than Hetzner's CPU
slots.

Exhaustion raises `lease-unavailable`, which is a **defer** (exit 75), the established requeue
disposition. The task stays queued; it is not a failure and it never escalates.

### Quota is not permission to spend

HTTP 402 maps to `quota-exhausted` (defer, 75); HTTP 429 maps to `rate-limited` (retryable, 10).
They are separated on purpose. No handler can set `on_demand`, and a metered or on-demand
manifest additionally requires `RECURSION_ALLOW_METERED=1` — the same rule the `hermes` engine
and the metered plugin engines already follow. A usage record derives `spend_state` from the
manifest's billing basis and never from the vendor payload, so an unreconciled metered run
cannot report itself as included usage.

### The Grok result channel

Results arrive as a **proposal**. `record_proposal` writes to
`state/remote/<backend>/proposals/` and nowhere else — no task, no board, no ledger, no
`state/DECISIONS.md`, no branch. The record carries `authority: advisory`,
`requires_human_review: true` and `self_reported_evidence_is_advisory: true`.

A proposal carrying an imperative key (`merge`, `deploy`, `publish`, `push`, `force_push`,
`delete_branch`, `pause`, `credentials`, `autonomy`, `cron`, `approve`, `execute`) is refused
**whole**, at any nesting depth — a partially-obeyed instruction is worse than a rejected one.

Code comes back on a review branch that Recursion fetches and verifies itself. The envelope says
so, in `verification_note` and `capabilities_withheld`, so the boundary travels with the
assignment instead of living only in a document the Bot never reads.

### The transport seam

`Transport` is the only path to the network. `RefusingTransport` is the default, so an adapter
constructed without one fails loudly rather than silently acquiring one. `HttpsTransport`
raises unless `RECURSION_REMOTE_LIVE=1`.

That third flag exists to make "this cannot reach the internet" a structural property rather
than a claim: the control suite asserts that constructing `HttpsTransport` without the flag
raises, so a regression that started opening sockets would fail the suite instead of quietly
succeeding.

### The typed error taxonomy

One table maps each code to one retryable flag and one exit code, so a caller never string-
matches a message to decide what to do. `0` ok, `2` present-but-invalid, `3` absent-or-disabled
(the house codes from `resolve-engine.py` / `resolve-connector.py`), `4` refused by policy,
`10` retryable, `75` defer. An error code outside the table cannot be constructed.

## Enablement chain (human-owned; none of it performed)

1. `.env`: `RECURSION_REMOTE_ADAPTERS=1`
2. `.env`: `RECURSION_REMOTE_<NAME>_ENABLED=1`
3. a valid `<name>.json` copied into `scripts/remote/`
4. `.env`: real values for the env vars its `*_ref` fields name
5. `.env`: `RECURSION_REMOTE_LIVE=1`

Plus `RECURSION_ALLOW_METERED=1` for a metered or on-demand backend.

## Human seams this work does not cross

Unchanged and still required before anything here runs:

- **Credentials.** A Cursor Cloud API key and a Grok routine webhook + sender key must be
  created and installed by a human. Cursor's source-control credentials must stay separate
  from Recursion's deploy keys.
- **The routine itself.** Lucas creates and tests a narrowly scoped routine in the Grok Bot
  desktop app on safe test inputs, per the plan. Nothing here automates the Bot's consumer UI,
  copies a login cookie, or gives a Bot SSH access to `gs-recursion`.
- **Live verification of the vendor API surface.** The Cursor Cloud request and response field
  names follow the vocabulary recorded in the 2026-08-28 audit and are **provisional** until
  verified against the live API — the same discipline the engine manifests shipped under
  (measure, don't assume). Shipping provisional names is safe because the adapter is inert.
- **Deployment, PAUSE removal, merge.** All still Lucas's.

## Known follow-ons

- **`runtime-state.py` does not back up `state/remote/`.** Its `RUNTIME_DIRECTORY_PATHS` was
  deliberately not modified here: changing the backup manifest alters proven restore behaviour
  and belongs with the Phase 4 backup/restore work, not with an inert adapter. Until then, a
  restore does not reconstruct the attempt journals. Recorded rather than silently fixed.
- **Wiring into routing and `work.sh`.** Nothing selects these backends yet. That is Phase 8
  placement plus the Phase 1 registries; a task cannot currently be routed to a remote backend
  at all, which is the intended state for an inert foundation.
- **Cursor Cloud artifact retention / session archiving.** The plan lists "archive completed
  sessions according to retention policy". Retention is a policy decision and a state-lifecycle
  change; not implemented.
- **Grok status polling.** A signed routine webhook is fire-and-forget: there is no vendor
  endpoint that will say whether a lost POST landed. Reconciliation therefore consumes an
  external observation. If a narrow result endpoint appears later, it slots in behind the same
  reconciliation call.
