#!/usr/bin/env python3
"""Pin the complete immutable GSC profile set without consulting Git metadata."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
PROFILE_DIR = SOURCE / "scripts/gates"
PROMOTION_DIR = PROFILE_DIR / "promotions"
EXPECTED_PROFILES = {
    "gsc-shade-tops-v1.json": (
        "8664c1dfb698542032d9dc9d8ce42d8e3eae25b7b498ca3fd326f48f0bcc6aca"
    ),
    "gsc-shade-tops-v3.json": (
        "548e598e0687b4009f50060812f5bd5900bc58ed772e89cf3dc28ad2156ed975"
    ),
}
EXPECTED_PROMOTIONS = {
    "gsc-shade-tops-v3.json": (
        "460309744c9ec64464ed5c0f9a8058445f72d6fcf5d5a7406d46e9cac96e5434"
    ),
}
EXPECTED_V3_PROMOTION = {
    "schema": "recursion-project-gate-profile-promotion/v1",
    "promotion_id": "gsc-shade-tops-v3",
    "project_id": "golden-stallion-client",
    "source_head": "19998a79630b2d57c0ed1e99915470b1048ded10",
    "profile": {
        "profile_id": "gsc-shade-tops-0x6c-v3",
        "path": "scripts/gates/gsc-shade-tops-v3.json",
        "sha256": "548e598e0687b4009f50060812f5bd5900bc58ed772e89cf3dc28ad2156ed975",
    },
    "required_gate_profile": {
        "acceptance": (
            "/opt/recursion/scripts/gsc-shade-tops-gate.py --repo . --profile "
            "/opt/recursion/scripts/gates/gsc-shade-tops-v3.json"
        ),
        "gate_class": "heavy",
        "gate_files": ["user-client/render/tools/native-diff.cjs"],
        "controller_gate_files": [
            "scripts/gsc-shade-tops-gate.py",
            "scripts/gates/gsc-shade-tops-v3.json",
            "scripts/gates/promotions/gsc-shade-tops-v3.json",
        ],
    },
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


def promotion_errors(promotion_dir: Path) -> list[str]:
    actual = {path.name for path in promotion_dir.glob("*.json") if path.is_file()}
    expected = set(EXPECTED_PROMOTIONS)
    errors: list[str] = []
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        if missing:
            errors.append(f"missing immutable promotions: {', '.join(missing)}")
        if unexpected:
            errors.append(f"unexpected immutable promotions: {', '.join(unexpected)}")
    for name in sorted(actual & expected):
        canonical, line_error = canonical_profile_bytes(promotion_dir / name)
        if line_error:
            errors.append(f"immutable promotion {name} {line_error}")
            continue
        assert canonical is not None
        digest = hashlib.sha256(canonical).hexdigest()
        if digest != EXPECTED_PROMOTIONS[name]:
            errors.append(
                f"immutable canonical promotion digest mismatch for {name}: "
                f"expected {EXPECTED_PROMOTIONS[name]}, got {digest}"
            )
        try:
            value = json.loads(canonical.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"immutable promotion {name} is malformed: {exc}")
            continue
        if name == "gsc-shade-tops-v3.json" and value != EXPECTED_V3_PROMOTION:
            errors.append("immutable v3 promotion semantic binding differs from the exact contract")
    return errors


def require_rejected(profile_dir: Path, label: str) -> int:
    if profile_errors(profile_dir):
        print(f"ok    mutation detected: {label}")
        return 0
    print(f"FAIL  mutation escaped: {label}")
    return 1


def require_promotion_rejected(promotion_dir: Path, label: str) -> int:
    if promotion_errors(promotion_dir):
        print(f"ok    promotion mutation detected: {label}")
        return 0
    print(f"FAIL  promotion mutation escaped: {label}")
    return 1


def main() -> int:
    live_errors = profile_errors(PROFILE_DIR) + promotion_errors(PROMOTION_DIR)
    if live_errors:
        for error in live_errors:
            print(f"FAIL  {error}")
        return 1
    print("ok    immutable GSC profile/promotion sets and canonical byte digests match")

    failures = 0
    with tempfile.TemporaryDirectory() as raw_temp:
        fixture = Path(raw_temp) / "gates"
        shutil.copytree(PROFILE_DIR, fixture)

        profile = fixture / "gsc-shade-tops-v1.json"
        profile.write_bytes(profile.read_bytes() + b" ")
        failures += require_rejected(fixture, "changed historical profile bytes")

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        profile = fixture / "gsc-shade-tops-v3.json"
        profile.write_bytes(profile.read_bytes() + b" ")
        failures += require_rejected(fixture, "changed measured v3 profile bytes")

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
        profile = fixture / "gsc-shade-tops-v3.json"
        canonical, line_error = canonical_profile_bytes(profile)
        if line_error or canonical is None:
            print(f"FAIL  could not build v3 line-ending controls: {line_error}")
            failures += 1
        else:
            profile.write_bytes(canonical.replace(b"\n", b"\r\n"))
            if profile_errors(fixture):
                print("FAIL  portable v3 CRLF checkout rejected")
                failures += 1
            else:
                print("ok    portable v3 CRLF checkout accepted")

            profile.write_bytes(canonical.replace(b"\n", b"\r\n", 1))
            failures += require_rejected(fixture, "mixed v3 profile line endings")

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

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        v1_bytes = (fixture / "gsc-shade-tops-v1.json").read_bytes()
        v3_bytes = (fixture / "gsc-shade-tops-v3.json").read_bytes()
        (fixture / "gsc-shade-tops-v3.json").write_bytes(v1_bytes)
        failures += require_rejected(fixture, "substituted v1 bytes under the v3 identity")

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        (fixture / "gsc-shade-tops-v1.json").write_bytes(v3_bytes)
        failures += require_rejected(fixture, "substituted v3 bytes under the v1 identity")

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        v3_path = fixture / "gsc-shade-tops-v3.json"
        reordered = json.loads(v3_path.read_text(encoding="utf-8"))
        reordered = dict(reversed(list(reordered.items())))
        v3_path.write_text(json.dumps(reordered, indent=2) + "\n", encoding="utf-8")
        failures += require_rejected(fixture, "reordered v3 profile fields")

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        v3_path = fixture / "gsc-shade-tops-v3.json"
        reordered = json.loads(v3_path.read_text(encoding="utf-8"))
        reordered["worlds"] = list(reversed(reordered["worlds"]))
        v3_path.write_text(json.dumps(reordered, indent=2) + "\n", encoding="utf-8")
        failures += require_rejected(fixture, "reordered v3 measured worlds")

        promotion_dir = fixture / "promotions"
        promotion = promotion_dir / "gsc-shade-tops-v3.json"
        promotion.write_bytes(promotion.read_bytes() + b" ")
        failures += require_promotion_rejected(
            promotion_dir, "changed v3 promotion binding bytes",
        )

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        promotion_dir = fixture / "promotions"
        promotion = promotion_dir / "gsc-shade-tops-v3.json"
        value = json.loads(promotion.read_text(encoding="utf-8"))
        value["profile"]["path"] = "scripts/gates/gsc-shade-tops-v1.json"
        promotion.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
        failures += require_promotion_rejected(
            promotion_dir, "substituted v1 path in v3 promotion binding",
        )

        shutil.rmtree(fixture)
        shutil.copytree(PROFILE_DIR, fixture)
        promotion_dir = fixture / "promotions"
        shutil.copy2(
            promotion_dir / "gsc-shade-tops-v3.json",
            promotion_dir / "gsc-shade-tops-latest.json",
        )
        failures += require_promotion_rejected(
            promotion_dir, "added implicit-latest promotion alias",
        )

    if failures:
        print(f"gsc-profile-immutability: {failures} FAILED")
        return 1
    print("gsc-profile-immutability: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
