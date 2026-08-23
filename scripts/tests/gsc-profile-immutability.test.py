#!/usr/bin/env python3
"""Pin the complete immutable GSC profile set without consulting Git metadata."""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
PROFILE_DIR = SOURCE / "scripts/gates"
EXPECTED_PROFILES = {
    "gsc-shade-tops-v1.json": (
        "8664c1dfb698542032d9dc9d8ce42d8e3eae25b7b498ca3fd326f48f0bcc6aca"
    ),
}


def canonical_profile_bytes(path: Path) -> tuple[bytes | None, str | None]:
    raw = path.read_bytes()
    if b"\r" not in raw:
        return raw, None

    without_crlf = raw.replace(b"\r\n", b"")
    if b"\r" in without_crlf:
        return None, "contains a bare carriage return"
    if b"\n" in without_crlf:
        return None, "mixes LF and CRLF line endings"
    return raw.replace(b"\r\n", b"\n"), None


def profile_errors(profile_dir: Path) -> list[str]:
    actual = {path.name for path in profile_dir.glob("*.json") if path.is_file()}
    expected = set(EXPECTED_PROFILES)
    errors: list[str] = []

    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing:
            errors.append(f"missing immutable profiles: {', '.join(missing)}")
        if unexpected:
            errors.append(f"unexpected immutable profiles: {', '.join(unexpected)}")

    for name in sorted(actual & expected):
        canonical, line_error = canonical_profile_bytes(profile_dir / name)
        if line_error:
            errors.append(f"immutable profile {name} {line_error}")
            continue
        assert canonical is not None
        digest = hashlib.sha256(canonical).hexdigest()
        if digest != EXPECTED_PROFILES[name]:
            errors.append(
                f"immutable canonical profile digest mismatch for {name}: "
                f"expected {EXPECTED_PROFILES[name]}, got {digest}"
            )
    return errors


def require_rejected(profile_dir: Path, label: str) -> int:
    if profile_errors(profile_dir):
        print(f"ok    mutation detected: {label}")
        return 0
    print(f"FAIL  mutation escaped: {label}")
    return 1


def main() -> int:
    live_errors = profile_errors(PROFILE_DIR)
    if live_errors:
        for error in live_errors:
            print(f"FAIL  {error}")
        return 1
    print("ok    immutable GSC profile set and canonical byte digests match")

    failures = 0
    with tempfile.TemporaryDirectory() as raw_temp:
        fixture = Path(raw_temp) / "gates"
        shutil.copytree(PROFILE_DIR, fixture)

        profile = fixture / "gsc-shade-tops-v1.json"
        profile.write_bytes(profile.read_bytes() + b" ")
        failures += require_rejected(fixture, "changed historical profile bytes")

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        profile = fixture / "gsc-shade-tops-v1.json"
        canonical, line_error = canonical_profile_bytes(profile)
        if line_error or canonical is None:
            print(f"FAIL  could not build line-ending controls: {line_error}")
            failures += 1
        else:
            crlf = canonical.replace(b"\n", b"\r\n")
            profile.write_bytes(crlf)
            if profile_errors(fixture):
                print("FAIL  portable CRLF checkout rejected")
                failures += 1
            else:
                print("ok    portable CRLF checkout accepted")

            if canonical.count(b"\n") < 2:
                print("FAIL  immutable profile lacks mutation control line count")
                failures += 1
            else:
                profile.write_bytes(canonical.replace(b"\n", b"\r\n", 1))
                failures += require_rejected(fixture, "mixed profile line endings")

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        shutil.copy2(
            fixture / "gsc-shade-tops-v1.json",
            fixture / "gsc-shade-tops-v2.json",
        )
        failures += require_rejected(fixture, "added profile with copied trusted bytes")

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        (fixture / "gsc-shade-tops-v1.json").rename(
            fixture / "gsc-shade-tops-v2.json"
        )
        failures += require_rejected(fixture, "substituted profile name")

    if failures:
        print(f"gsc-profile-immutability: {failures} FAILED")
        return 1
    print("gsc-profile-immutability: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
