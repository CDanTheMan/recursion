---
title: Recursion v2 Phase 4 hardening handoff
type: implementation-handoff
status: review-only
authorized: 2026-08-28
---

# Scope

This branch implements only the code and review artifacts for Phase 4 of
`docs/plans/recursion-v2-execution-fabric.md`. It does not deploy, publish, remove PAUSE,
change credentials, alter SSH/firewall policy, install a service or timer, or contact an
off-host destination.

## Delivered boundaries

- `hermes-actuator.sh` retains its v1 `all` mode. Optional `state` and `work` scopes let a
  human deploy a non-root state actuator alongside a narrowly scoped root worker dispatcher.
- Provider profiles are strict, provider-specific, endpoint-exact, and disabled in the tree.
  The shared Phase 4 proxy admits only signed per-assignment capabilities, maps each capability
  to exactly one provider profile, and rejects missing, forged, or cross-provider transport
  authorization. A sandbox plan can request proxy injection only through `provider-egress.py`;
  disabled or mismatched profiles return a typed refusal. Existing plans without `egress_profile`
  retain their v1 shape and behavior.
- `deploy/backup/recursion-offsite.json` is a disabled age/SFTP contract with explicit
  retention, log-rotation, and restore-drill requirements. `backup-offsite.py` has explicit
  `--execute` backup/restore/reconcile commands, HMAC-authenticated configuration, argv-only age
  and SFTP calls, PAUSE admission held across every remote transfer, strict archive file/byte
  limits, bounded deletion of safely named nonconforming remote artifacts, durable encrypted
  snapshots in the configured canonical snapshot directory, atomic evidence, and tmpfs/runtime-
  dir plaintext cleanup. The local restore drill is labeled prepared; off-host restore remains
  pending live evidence.
- `.example` systemd and logrotate artifacts are review templates, not units installed by this
  checkout. No artifact has a `WantedBy` target that could enable it implicitly.
- `phase4-linux-proof.test.py` is an explicit Linux/root/systemd-aware proof boundary. It never
  starts a service or changes a namespace; the transient systemd proof is a human-only gate.

## Human-only deployment sequence

1. Re-read `CONTROL_PLANE.md`, PAUSE, the dated infrastructure audit, and this handoff on the
   target host. Capture the dirty checkout, exact ref, service state, and PAUSE hash.
2. Review SSH, forwarding, firewall, and inbound-service policy independently. Do not add an
   inbound Grok bridge; the initial bridge is outbound-only.
3. Install `recursion-actuator` and assign only the state paths required by the state template.
   Install the state/work templates side-by-side, first with the existing actuator stopped and
   a rollback copy available. Verify `RECURSION_ACTUATOR_SCOPE=state|work` and PAUSE behavior.
4. Copy provider profiles to a human-owned `/etc/recursion/providers` directory. Keep every
   profile disabled until endpoint ownership, proxy namespace, credentials, and provider billing
   approval are separately recorded. Enable only the reviewed profile and run the Linux proxy
   gate; do not broaden the allowlist to make a probe pass.
5. Provision an encrypted age recipient/identity and HMAC policy key through the secret store,
   create the off-host destination, authenticate the human-owned policy, and set its `enabled`
   flag. Use `backup-offsite.py plan` as the review record, then explicitly execute one PAUSE-held
   backup and a restore drill into a disposable root. Verify the manifest, PAUSE hash, retention
   result, atomic evidence, and recovery point before scheduling anything. Do not call local
   evidence an off-host restore; that remains pending live evidence.
6. Install logrotate and, only after the preceding receipts are reviewed, install and enable a
   separately reviewed backup schedule. The checked-in `.example` files are never sufficient
   authorization for those operations.
7. Preserve the existing v1 actuator as the rollback path until the new units, provider profile,
   backup, restore, and PAUSE-across-restart evidence are independently accepted. Lucas performs
   any cutover, merge, PAUSE change, or production deployment.
