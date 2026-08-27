# Notification connectors (Component 6 — scaffolding, inert)

One `<name>.json` per notification transport, validated by `scripts/resolve-connector.py`
against `schemas/control-plane/v1/connector-manifest.schema.json`. A manifest declares an
absolute transport executable, its argv template, the acknowledgement shape it produces,
the env var names it may receive, and a timeout.

**This directory ships with no loadable manifest, deliberately.** The only files here are
this README and `examples/telegram-alt.json.example`. `resolve-connector.py --validate`
globs `*.json` at the top level only, and `--name X` looks for exactly `X.json`, so the
`.example` extension is what keeps the example unloadable — copying it to
`telegram-alt.json` is a human act, not a default.

## Reserved names

`telegram` and `hermes`. `notify.sh` implements both natively; a manifest using either
name is refused (exit 2) so a connector can never shadow the built-in path.

## Enablement chain — five links, every one human-owned

The loop never writes any of these. Nothing executes until all five hold:

1. `.env`: `RECURSION_CONNECTORS=1`
2. `.env`: `RECURSION_CONNECTOR_<NAME>_ENABLED=1` (name uppercased, dashes → underscores)
3. a valid `<name>.json` in this directory
4. `.env`: `RECURSION_CONNECTOR_ACTIVE=<name>`
5. `.env`: `RECURSION_NOTIFY_TRANSPORT=/opt/recursion/scripts/connector-transport.py`

Link 5 is the real switch. It is an existing, currently-unset hook in `notify.sh`; while
it is unset, `notify.sh` uses its built-in Telegram path and no connector can run —
regardless of links 1–4. The adapter also ships without the executable bit, so a box
deployment must `chmod +x scripts/connector-transport.py` before `notify.sh` can exec it.

`RECURSION_CONNECTOR_DIR` overrides this directory. It is a control-only hook for the
hermetic tests and is never set on the box.

## Token hygiene

`env_passthrough` refuses any name containing `TOKEN`, `SECRET`, `KEY`, or `PASSWORD`,
with **no allowlist**. This is stricter than the engine manifest, which permits provider
API keys because the worker sandbox carries them on a root-owned 0600 `EnvironmentFile`.
A connector has no such carrier. `TELEGRAM_BOT_TOKEN` in particular cannot ride a
manifest: `notify.sh`'s contract is that the token never leaves that file. The match is a
deliberately over-broad substring test; a false positive costs a rename.

## What the adapter does not do

`scripts/connector-transport.py` substitutes `{{DESTINATION}}` and `{{MESSAGE}}` as exact
argv elements (no shell, no interpolation), filters the environment, enforces the timeout,
and passes the child's stdout through byte-exact. It never parses, edits, or fabricates an
acknowledgement. `notify.sh` remains the sole ack validator, and a zero exit from the
adapter is not delivery evidence.

## Gated on D-014 closing

While D-014 is OPEN, `notify.sh`'s validator accepts only a Telegram-shaped acknowledgement
(`transport == "telegram"`, a `message_id`, and a chat/thread echo), so `ack_contract` has
exactly one legal value. Widening that validator, adding non-Telegram destination kinds to
the Phase 7 outbox, and enabling any of this on the box are separate follow-on tasks; the
durable-outbox/PAUSE-interlock surface is promotion-critical and its evidence must not be
invalidated by a change made ahead of that.
