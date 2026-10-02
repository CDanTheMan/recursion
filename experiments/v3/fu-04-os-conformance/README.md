# FU-04 experiment — OS platform conformance (kickoff)

Status: **kickoff / unqualified.** Evidence class: `locally_observed` for the safe host probes
(one host); everything else stays `unknown`. No OS build, kernel, terminal, filesystem or
distribution is certified.

Source specification: `docs/v3/research-lane/followups-20261002/raw/ds-FU-04-os-conformance.md`
and `.../machine/` (manifest + traces). Prompt: `docs/v3/prompts/followups-20261001/FU-04-os-platform-conformance-fixtures.md`.

## What ran (safe, non-destructive)

`probe_windows.py` records `results/probes.json`: atomic replace + `fsync` (application-visible,
**not** crash durability), byte-range lock acquire/release, monotonic clock non-decreasing, and
child process exit observation. These are observations about one host, not qualification.

## What did NOT run

Destructive negative traces (descendant escape/containment, parent death, crash durability, disk
exhaustion, OOM, forced-kill supervisor races, suspend/resume, network-storage interruption) are
listed in `results/probes.json` under `destructive_not_run`. They require a disposable,
Owner-approved test system and separate authorization, and are not counted as pass, fail or zero.

## Manifest invariant

`docs/v3/research-lane/followups-20261002/machine/platform-manifest.json` stays
`proposed_unexecuted`; all 11 profiles remain `pending_owner` with `profile_key = null`. The 20
negative traces in `negative-traces.json` remain `unexecuted`. An empty result is never rendered
as zero failures.

## Gate

```text
python -X utf8 -B experiments/v3/fu-04-os-conformance/probe_windows.py
python -X utf8 -B experiments/v3/fu-04-os-conformance/check_fu04.py
```

## Platform floors (G-11 / D-028)

`platform-floors.json` pins the approved floors: Windows 11 **25H2 (26200)** minimum Home/Pro plus
**24H2 (26100) Enterprise**, x64 primary; Linux **6.12 LTS** primary / **6.6 LTS** minimum with
**cgroup v2**; **WSL2 dev/test only**; canonical state on **local NTFS/ext4 only** (SMB/NFS out of
scope); "survives power loss" = application-consistent after an abrupt **VM reset** at the commit
boundary. Every manifest case is mapped to `in_scope_unqualified`, `dev_test_only`, `out_of_scope`
or `later`; **no profile is qualified** and the manifest stays `proposed_unexecuted`.

## Runnable traces and disposable target

- `traces/traces.json` normalizes all 20 fixtures (PF01…PF20) with injected fault, observation
  oracle, recovery oracle, stop condition, negative control and a `runs_now` flag.
- `traces/run_traces.py` executes them against `host` (Windows, non-destructive) or the disposable
  `wsl:Debian` target; destructive runs require `--allow-destructive` and are bounded with hard
  timeouts. `traces/check_traces.py` is the gate.
- `target/capture-identity.py` records run identity (host + WSL target); `target/target-reset.ps1`
  resets the disposable distro; `target/enable-windows-sandbox.ps1` is the **elevated** Windows
  step (not executed by any agent).

**Disposable Linux target:** WSL2 distro `Debian` (Debian GNU/Linux 13 trixie, kernel
6.6.114.1-microsoft-standard-WSL2, cgroup2fs). Reset = `wsl --unregister Debian` then
`wsl --install -d Debian --no-launch`.

**Windows destructive target:** needs Windows Sandbox enabled (elevation + reboot). Until then,
Windows destructive traces stay `not_run`. `PF11` is recorded `unknown` (cgroup v2 is mounted
read-only in this WSL target, so true memory-throttle counters are unavailable — the bounded
`ulimit` substitute is not a native throttle classification).

## Next increments

1. Owner fixes G-11 platform floors, then `pin_state` and `profile_key` are populated with exact
   pins (no analogy).
2. Add each native profile as a distinct mandatory case; WSL2, compatibility shells, embedded
   terminals, SMB and NFS remain separate cases, never inherited.
3. Execute negative traces only on disposable approved targets, recording the observation and
   recovery oracles per trace.
4. Independent verifier reruns the exact candidate; a locally observed host probe is not
   acceptance.
