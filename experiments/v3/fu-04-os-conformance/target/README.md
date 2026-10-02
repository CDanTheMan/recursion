# FU-04 target model — disposable OS-conformance targets

Date: 2026-10-01
Status: scaffold. Evidence class: `locally_observed` where stated; otherwise `unmeasured`.
Nothing here qualifies any OS build — qualification requires the negative traces to pass on an
approved target (`../platform-floors.json`, D-028).

## What the targets are

| Target | Disposable? | Reset | Used for |
| --- | --- | --- | --- |
| WSL2 distro `Debian` | yes — unregister + reinstall | `target-reset.ps1` | destructive Linux traces (`wsl2_ext4`) |
| Windows Sandbox guest | yes — fresh guest per launch | close the window | destructive Windows traces |
| Hyper-V gen-2 VM (fallback) | yes — revert checkpoint | checkpoint revert | destructive Windows traces if Sandbox is unavailable |
| This Windows host | **no** | n/a | safe, non-destructive probes only |

The host is not disposable. Destructive faults run only in a disposable target, never on the
host.

## What is disposable

- **WSL2 `Debian`** — the ext4 rootfs lives inside the `Debian` distro only. `wsl --unregister
  Debian` destroys that rootfs and frees its disk; Windows, other distros and host drives are
  untouched. `/mnt/c` is a convenience mount and is **not** disposable: a fault that writes
  there writes to the host.
- **Windows Sandbox** — every launch is a fresh guest. In-guest mutations (registry, disk,
  services) are discarded when the window closes, so crash/exhaustion faults cannot outlive the
  trace.
- **Hyper-V VM** — mutations are bounded by a checkpoint/undo disk; revert to the checkpoint.

## How to reset the Linux target

```powershell
# dry run (prints the commands, changes nothing)
pwsh -File experiments/v3/fu-04-os-conformance/target/target-reset.ps1 -DryRun

# real reset of the disposable distro only
pwsh -File experiments/v3/fu-04-os-conformance/target/target-reset.ps1
```

`target-reset.ps1` runs `wsl --unregister Debian` then `wsl --install -d Debian --no-launch`.
It is idempotent (skips unregister when `Debian` is absent) and supports `-WhatIf`.
**Warning:** unregister destroys the disposable `Debian` distro and its contents. Do not point it
at any other distro.

## How the runner reaches each target

- **Host / Windows Sandbox** — the runner executes directly on Windows (`probe_windows.py`).
  For destructive Windows traces, launch a Sandbox guest from a `.wsb` config and run the trace
  inside it.
- **WSL2 `Debian`** — the runner shells in per command (no persistent session):
  `wsl.exe -d Debian -- <command>`. Stdout of the child is UTF-8; `wsl.exe`'s own console output
  is UTF-16, so `capture-identity.py` decodes both.
- **Identity** — `capture-identity.py` pins host OS/volumes and the `Debian`
  `PRETTY_NAME`/`uname`/cgroup-v2/page-size/`ulimit -n`, writing `target/identity.json`
  (deterministic, no network, no secrets).

```powershell
python -X utf8 -B experiments/v3/fu-04-os-conformance/target/capture-identity.py
```

## Windows Sandbox elevation step (human-gated)

`enable-windows-sandbox.ps1` contains the exact elevated command:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM -All
```

**REQUIRES ELEVATION + REBOOT; not executed by any agent.** Run it from an Administrator
PowerShell, then reboot. Launch disposable guests with `Start-SandboxTrace` in the same file.
If Windows Sandbox is unavailable, the fallback is a **Hyper-V gen-2 VM** with a checkpoint/undo
disk (also requires elevation + reboot).

## Safety rules

1. Destructive faults run **only** in a disposable target (`Debian`, Windows Sandbox, or a
   checkpointed Hyper-V VM). Never on the host.
2. Keep destructive faults **bounded**: a time limit and a resource limit, with a defined
   cleanup/reset (`target-reset.ps1`).
3. `/mnt/c` and any network (SMB/NFS) mount are **out of the disposable boundary**; never fault
   against them.
4. Live provider/game/host actions, spending and quota resets are human-gated. Ask; never do
   them.
5. An implementer's PASS is not acceptance; an independent verifier reruns the exact candidate.

## Files

- `capture-identity.py` — capture host + `Debian` identity to `identity.json`.
- `target-reset.ps1` — idempotent reset of the disposable `Debian` target.
- `enable-windows-sandbox.ps1` — elevated Windows Sandbox enablement + disposable launcher.
- `README.md` — this target model.
