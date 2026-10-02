#!/usr/bin/env python3
"""FU-04 target: capture the run identity for the host and the WSL `Debian` target.

Deterministic, provider-free, Python standard library only. No network access. No secrets are
recorded: no usernames, no credentials, no absolute user paths, and the Linux nodename is
deliberately omitted. Output is stable across repeated runs on the same machine.

    python -X utf8 -B experiments/v3/fu-04-os-conformance/target/capture-identity.py

Writes `target/identity.json`. Evidence class: `locally_observed` for this one host + distro.
Nothing here qualifies any OS build; it only pins what the run actually observed.
"""
from __future__ import annotations

import ctypes
import json
import platform
import subprocess
import sys
from ctypes import wintypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "identity.json"

WSL_DISTRO = "Debian"
WINDOWS_KEY = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"

DRIVE_TYPES = {
    0: "unknown",
    1: "no_root_dir",
    2: "removable",
    3: "fixed",
    4: "network",
    5: "cdrom",
    6: "ramdisk",
}


def decode(data: bytes) -> str:
    """Decode process output that may be UTF-16 (wsl.exe's own console) or UTF-8 (child)."""
    if not data:
        return ""
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    if b"\x00" in data:
        return data.decode("utf-16-le", errors="replace").replace("\x00", "")
    return data.decode("utf-8", errors="replace")


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        cp = subprocess.run(cmd, capture_output=True, check=False)
    except OSError as exc:
        return 127, f"{type(exc).__name__}: {exc}"
    return cp.returncode, decode(cp.stdout + cp.stderr).replace("\ufffd", "")


def host_os() -> dict:
    import winreg

    values: dict[str, str] = {}
    for name in ("ProductName", "DisplayVersion", "CurrentBuildNumber", "CurrentBuild",
                 "UBR", "EditionID", "InstallationType"):
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, WINDOWS_KEY) as key:
                value, _ = winreg.QueryValueEx(key, name)
            values[name] = str(value)
        except OSError:
            values[name] = ""

    build_number = values.get("CurrentBuildNumber") or values.get("CurrentBuild") or ""
    ubr = values.get("UBR") or ""
    build = f"{build_number}.{ubr}" if build_number and ubr else build_number

    # The registry ProductName still reads "Windows 10 ..." on Windows 11; the build number is
    # authoritative. Keep the raw value and normalize the caption from the build.
    caption_raw = values.get("ProductName") or platform.platform()
    caption = caption_raw
    if build_number.isdigit() and int(build_number) >= 22000 and caption_raw.startswith("Windows 10"):
        caption = caption_raw.replace("Windows 10", "Windows 11", 1)

    return {
        "caption": caption,
        "caption_raw": caption_raw,
        "build": build,
        "version": values.get("DisplayVersion") or platform.version(),
        "edition_id": values.get("EditionID") or "",
        "installation_type": values.get("InstallationType") or "",
        "architecture": platform.machine(),
        "python": platform.python_version(),
    }


def host_volumes() -> list[dict]:
    k32 = ctypes.windll.kernel32
    k32.GetLogicalDrives.restype = wintypes.DWORD
    mask = k32.GetLogicalDrives()
    fs_buf = ctypes.create_unicode_buffer(261)
    volumes: list[dict] = []
    for index in range(26):
        if not mask & (1 << index):
            continue
        root = f"{chr(65 + index)}:\\"
        drive_type = k32.GetDriveTypeW(root)
        serial = wintypes.DWORD()
        max_len = wintypes.DWORD()
        flags = wintypes.DWORD()
        ok = k32.GetVolumeInformationW(
            root, None, 0, ctypes.byref(serial), ctypes.byref(max_len),
            ctypes.byref(flags), fs_buf, 261,
        )
        free_avail = ctypes.c_ulonglong()
        total = ctypes.c_ulonglong()
        total_free = ctypes.c_ulonglong()
        k32.GetDiskFreeSpaceExW(
            root, ctypes.byref(free_avail), ctypes.byref(total), ctypes.byref(total_free)
        )
        volumes.append({
            "root": root,
            "drive_type": DRIVE_TYPES.get(drive_type, f"type_{drive_type}"),
            "filesystem": fs_buf.value if ok else None,
            "total_bytes": total.value,
        })
    volumes.sort(key=lambda v: v["root"])
    return volumes


def wsl_version() -> dict:
    rc, text = run(["wsl.exe", "--version"])
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    fields["exit_code"] = rc
    fields["available"] = rc == 0
    return fields


def wsl_target(distro: str) -> dict:
    rc, listing = run(["wsl.exe", "--list", "--quiet"])
    installed = [line.strip() for line in listing.splitlines() if line.strip()] if rc == 0 else []
    present = any(name.lower() == distro.lower() for name in installed)

    target: dict = {
        "distro": distro,
        "installed": present,
        "wsl_version": wsl_version(),
    }
    if not present:
        target["error"] = "distro not registered; nothing captured"
        return target

    def in_distro(*argv: str) -> tuple[int, str]:
        return run(["wsl.exe", "-d", distro, "--", *argv])

    _, os_release_text = in_distro("cat", "/etc/os-release")
    os_release: dict[str, str] = {}
    for line in os_release_text.splitlines():
        if "=" not in line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        os_release[key.strip()] = value.strip().strip('"').strip("'")

    _, uname_s = in_distro("uname", "-s")
    _, uname_r = in_distro("uname", "-r")
    _, uname_v = in_distro("uname", "-v")
    _, uname_m = in_distro("uname", "-m")

    _, controllers_text = in_distro("cat", "/sys/fs/cgroup/cgroup.controllers")
    controllers = controllers_text.split()
    _, fs_type = in_distro("stat", "-fc", "%T", "/sys/fs/cgroup")
    fs_type = fs_type.strip()
    _, self_cgroup = in_distro("cat", "/proc/self/cgroup")
    _, page_size = in_distro("getconf", "PAGESIZE")
    _, ulimit_n = in_distro("sh", "-c", "ulimit -n")

    target["os_release"] = os_release
    target["pretty_name"] = os_release.get("PRETTY_NAME", "")
    target["uname"] = {
        "sysname": uname_s.strip(),
        "release": uname_r.strip(),
        "version": uname_v.strip(),
        "machine": uname_m.strip(),
    }
    target["cgroup"] = {
        "controllers": controllers,
        "controllers_present": bool(controllers),
        "fs_type": fs_type,
        "self_cgroup": self_cgroup.strip(),
        "v2_present": fs_type == "cgroup2fs" or bool(controllers),
    }
    target["page_size_bytes"] = _as_int(page_size)
    target["ulimit_n"] = _as_int(ulimit_n)
    return target


def _as_int(text: str) -> int | None:
    text = text.strip()
    return int(text) if text.isdigit() else None


def main() -> int:
    record = {
        "experiment": "fu-04-os-conformance target identity",
        "evidence_class": "locally_observed (this host + distro only)",
        "certification": "none; identity capture is not platform qualification",
        "platform_floors": "experiments/v3/fu-04-os-conformance/platform-floors.json",
        "host": {
            "os": host_os(),
            "volumes": host_volumes(),
        },
        "wsl_target": wsl_target(WSL_DISTRO),
        "notes": [
            "Windows volume identity is local fixed disks; network drives are enumerated but "
            "the canonical scope is local only.",
            "cgroup v2 presence is read from /sys/fs/cgroup; platform floors require it.",
            "Linux nodename is intentionally not recorded.",
        ],
    }
    OUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
