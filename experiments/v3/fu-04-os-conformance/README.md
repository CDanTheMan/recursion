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

## Next increments

1. Owner fixes G-11 platform floors, then `pin_state` and `profile_key` are populated with exact
   pins (no analogy).
2. Add each native profile as a distinct mandatory case; WSL2, compatibility shells, embedded
   terminals, SMB and NFS remain separate cases, never inherited.
3. Execute negative traces only on disposable approved targets, recording the observation and
   recovery oracles per trace.
4. Independent verifier reruns the exact candidate; a locally observed host probe is not
   acceptance.
