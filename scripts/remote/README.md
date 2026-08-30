# Remote execution backends (v2 Phase 6 / Phase 7 — scaffolding, inert)

One `<name>.json` per remote execution backend, validated by `scripts/remote_backend.py`
against `schemas/control-plane/v1/remote-backend.schema.json`. A manifest declares an
endpoint (or a reference to one), a credential **reference**, a capacity pool, a host id, a
lease width, retry bounds, and a publication policy.

Design: `docs/plans/remote-execution-adapters.md`. Program context:
`docs/plans/recursion-v2-execution-fabric.md` (Phase 6, Phase 7) and D-016.

**This directory ships with no loadable manifest, deliberately.** The only files here are this
README and `examples/*.json.example`. `remote_backend.py --validate` globs `*.json` at the top
level only, and resolution looks for exactly `<name>.json`, so the `.example` extension plus
the `examples/` subdirectory are what keep the examples unloadable. Copying one into place is
a human act, not a default.

## The two backends

| Manifest kind | Adapter | What it is |
|---|---|---|
| `cursor-cloud` | `scripts/cursor-cloud-adapter.py` | An isolated vendor VM and a capacity pool. Disposable implementation and burst parallelism. |
| `grok-routine` | `scripts/grok-bot-dispatcher.py` | A supervisory arm on an **account-shared** cloud computer. Planning, review, triage, browser QA. |

They are not interchangeable and neither is an engine. An engine manifest
(`scripts/engines/*.json`, D-015) describes a CLI this box can exec. A remote backend
describes a service that executes somewhere else, pays from its own pool, and returns a
candidate Recursion must independently verify.

## Enablement chain — every link human-owned

The loop writes none of these (CLAUDE.md rule 3). Nothing dispatches until all of them hold:

1. `.env`: `RECURSION_REMOTE_ADAPTERS=1`
2. `.env`: `RECURSION_REMOTE_<NAME>_ENABLED=1` (name uppercased, dashes → underscores)
3. a valid `<name>.json` in this directory
4. `.env`: the env vars its `*_ref` fields name, with real values
5. `.env`: `RECURSION_REMOTE_LIVE=1` — the third flag, and the real switch

Link 5 gates the *production transport itself*: `HttpsTransport.__init__` raises without it.
Every adapter is constructed with an injected transport, and without link 5 the injected
transport is `RefusingTransport`, which raises `live-transport-disabled` on any call. That is
why the hermetic controls can exercise the whole client contract with fakes and still prove
the suite cannot reach the network.

A metered or on-demand manifest additionally requires `RECURSION_ALLOW_METERED=1`, the same
rule the `hermes` engine and the metered plugin engines already follow.

`RECURSION_REMOTE_DIR` overrides this directory. It is a control-only hook for the hermetic
tests and is never set on the box.

## Secret references, never secret values

Every credential-bearing field is a reference of the form `secret:<ENV_NAME>`:

```json
"credential_ref": "secret:CURSOR_CLOUD_API_KEY"
```

`validate_secret_ref` refuses a reference that names a controller or deploy credential
(`GITHUB_TOKEN`, `TELEGRAM_BOT_TOKEN`, `OPENROUTER_API_KEY`, anything starting `RECURSION_`,
`SSH_`, `AWS_`, `HERMES_`, …). A remote backend may hold exactly one credential: its own.

A Grok routine webhook URL is bearer-grade — anyone holding it can post to the routine — so it
lives behind `endpoint_ref` rather than in the manifest. Durable records store the
*reference*; the resolved URL is never written down.

Manifests, envelopes, attempt records and session projections all pass through
`screen_for_secret_material`, which refuses credential-shaped keys and credential-shaped
values. It is over-broad on purpose: a false positive costs a rename.

## What the adapters will not do

- write a default or integration branch (refused at request construction *and* by a post-check
  over the finished request body, and again when a returned ref is reconciled);
- accept a vendor's or a Bot's self-report as verification — `verification_state` is always
  `requires-independent-verification`, and there is no code path that emits anything else;
- turn quota exhaustion into spending: HTTP 402 is a **defer** (exit 75), and no handler can
  set `on_demand`;
- dispatch under PAUSE — every outbound path checks `state/PAUSE` first, while local awareness
  (recovery listing, durable reads) stays available;
- re-send a request that may already have landed: an attempt left `open` by a dead process is
  a question for a human, not a retry.

## Runtime state

Attempts, sessions and proposals live under `state/remote/<backend>/`, which is gitignored
runtime state — the same class as `state/runs/` and `state/deliveries/`. The append-only
`attempts.jsonl` is the record of truth; the per-attempt and per-dispatch JSON files are
projections of it.
