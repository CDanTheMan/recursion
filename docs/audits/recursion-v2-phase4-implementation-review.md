---
title: Recursion v2 Phase 4 implementation review
type: review-artifact
status: pending-human-review
observed: 2026-08-28
related:
  - docs/plans/recursion-v2-execution-fabric.md
  - docs/audits/recursion-v2-infrastructure-audit-2026-08-28.md
  - docs/plans/recursion-v2-phase4-handoff.md
---

# Review boundary

The Phase 4 implementation is intentionally inert. The existing v1 service, provider
allowlist, PAUSE file, cron, credentials, and live host are not changed by this branch. New
provider profiles are `enabled: false`; new service, timer, and logrotate files are `.example`
templates without implicit install targets.

| Area | Review evidence | Live action still required |
|---|---|---|
| Actuator | `state` and `work` scopes; v1 default remains `all`; separate hardened templates | human ownership assignment, side-by-side restart/cutover, rollback |
| Provider egress | exact authority/profile matching and loopback-only proxy injection; disabled defaults | human-owned profile copy, provider credentials, namespace/proxy gate |
| Backup durability | age/SFTP contract, retention and rotation policy, disposable restore drill | destination, secret-store refs, encrypted transfer, PAUSE-held recovery-point drill |
| Sandbox ownership | explicit Linux/root/systemd-aware proof test and existing worker checks | run transient-systemd proof on Hetzner; inspect ownership/capabilities and PAUSE restart |
| Perimeter | no SSH/firewall/inbound bridge changes in this branch | separate human security review before any host deployment |

The implementation test results and commit identity are recorded in the session handoff. Passing
local tests is not production deployment evidence and does not authorize PAUSE removal.
