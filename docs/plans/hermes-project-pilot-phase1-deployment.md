---
title: Hermes Project Pilot Phase 1 Deployment Runbook
type: runbook
status: proposed
last-verified: 2026-08-06
related:
  - CONTROL_PLANE.md
  - docs/plans/hermes-project-pilot-production-plan.md
  - docs/plans/hermes-project-pilot-phase0-evidence.md
---
# Hermes project pilot Phase 1 deployment runbook

This runbook is deployment evidence, not deployment authorization. Phase 1 authoring must not
apply it until Lucas separately approves a maintenance window and the review branch is merged.
`state/PAUSE` remains present for the entire procedure.

## Preconditions

1. Assert `/opt/recursion/state/PAUSE` exists and record its SHA-256.
2. Record the deployed commit, current unit, service properties, installed Python distribution
   manifest, and OSV result. Back up the existing unit and Hermes venv outside the checkout.
3. Stop `hermes-gateway`. Do not stop heartbeat/status monitoring outside that service.
4. Create the `hermes-gateway` and `recursion-runner` identities with the reviewed sysusers and
   tmpfiles definitions. Neither account receives a shell, sudo, SSH, or deploy-key access.
5. Provision a separate Claude login under `/var/lib/recursion-runner` through Lucas's interactive
   login seam. Do not copy `/root/.ssh`, `/opt/recursion/.env`, or `/root/.hermes` into the runner.

## Staged dependency replacement

Build a new venv beside the current one from the same reviewed Hermes Agent artifact, applying
`deploy/requirements/hermes-gateway-phase1.txt`. Run `pip check`, import the gateway entrypoint,
and query OSV for the complete staged environment. Do not update the live venv in place. Atomically
switch `/usr/local/lib/hermes-agent/venv` only after all checks pass; retain the old venv for rollback.

## Gateway identity migration

Copy only the gateway's required Hermes configuration and Telegram session material into
`/var/lib/hermes-gateway` during the approved secret-handling window. Preserve no secret in git,
logs, or the evidence bundle. Set ownership to `hermes-gateway:hermes-gateway` and mode `0700`.
Install the reviewed unit, run `systemd-analyze verify`, then `daemon-reload` and start the service.

## Acceptance and rollback

Run:

```bash
bash scripts/audit/hermes-pilot-live-phase1-red.sh
systemd-analyze security hermes-gateway
bash scripts/audit/hermes-pilot-phase0-baseline.sh
bash scripts/tests/hermes-pilot-phase1-red.test.sh
```

The live audit and Phase 1 suite must be green; the baseline must remain 17/17. Re-assert PAUSE,
confirm no worker/gate/publisher is active, and record the unit/venv hashes. On any failure, stop the
gateway, restore the previous unit and venv atomically, run `daemon-reload`, restart awareness-only
service, and remain paused. Lifting PAUSE requires a separate explicit Lucas decision.
