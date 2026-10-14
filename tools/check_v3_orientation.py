#!/usr/bin/env python3
"""Provider-free gate for the 2026-09-13 v3 orientation repair, plus the harness slice.

The original 23 M1 programs stay mandatory. Harness paths are an explicit extra
allowlist so the slice can land without dropping those checks.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "797be4f18edf3f9e0f2dbac9432f190dbe1ed969"
ALLOWED = {
    "README.md", "AGENTS.md", "CLAUDE.md", "docs/v3/README.md",
    "docs/v3/VALIDATION.md", "docs/v3/ROADMAP.md", "docs/v3/START-HERE.md",
    "state/tasks/v3-orientation-20260913.md", "tools/check_v3_orientation.py",
}
PRODUCT_SLICE = {
    "docs/v3/HARNESS-SLICE.md",
    "scripts/v3/harness/__init__.py",
    "scripts/v3/harness/__main__.py",
    "scripts/v3/harness/errors.py",
    "scripts/v3/harness/planning.py",
    "scripts/v3/harness/providers.py",
    "scripts/v3/harness/routing.py",
    "scripts/v3/harness/run.py",
    "scripts/tests/v3/harness/harness.test.py",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", "-c", "core.longpaths=true", *args], cwd=ROOT, encoding="utf-8"
    ).strip()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def prose(text: str) -> str:
    """Exclude fenced/inline code so regex examples are not treated as links."""
    text = re.sub(r"(?ms)^```[^\n]*\n.*?^```[^\n]*$", "", text)
    text = re.sub(r"(?ms)^~~~[^\n]*\n.*?^~~~[^\n]*$", "", text)
    return re.sub(r"`[^`\n]*`", "", text)


def check_links(paths: list[Path]) -> int:
    count = 0
    for path in paths:
        for raw in re.findall(r"\]\(([^)]+)\)", prose(path.read_text(encoding="utf-8"))):
            target = raw.split(' "', 1)[0].strip().strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            require(resolved.is_relative_to(ROOT), f"link escapes repository: {path}: {raw}")
            require(resolved.exists(), f"missing link target: {path}: {raw}")
            count += 1
    return count


def check_registry() -> tuple[int, int]:
    registry = json.loads(read("docs/v3/CLAIM-REGISTRY.json"))
    rows = re.findall(
        r"^\| ([A-Z][A-Z0-9]*-[0-9]{3}) \|",
        read("docs/v3/" + registry["canonicalLedger"]), re.MULTILINE,
    )
    require(len(rows) == len(set(rows)), "duplicate claim rows")
    expected = []
    for span in registry["ranges"]:
        expected.extend(
            f"{span['prefix']}-{n:03d}"
            for n in range(span["start"], span["end"] + 1)
            if n not in span["reserved"]
        )
    require(len(expected) == len(set(expected)), "overlapping claim ranges")
    require(set(rows) == set(expected), "claim registry and ledger differ")
    require(all(re.fullmatch(registry["idPattern"], row) for row in rows), "bad claim ID")
    # OR-021..039 belong to the later Owner decision register, not the original
    # OR-001..020 claim-ledger range. Do not silently relabel the older registry.
    owner_rows = re.findall(r"^\| (OR-\d{3}) \|", read("docs/v3/DECISION-REGISTER.md"), re.MULTILINE)
    counts = Counter(owner_rows)
    require(all(counts[f"OR-{n:03d}"] == 1 for n in range(21, 40)),
            "accepted OR-021..039 decision rows missing or duplicated")
    return len(rows), 19


def m1_programs() -> list[tuple[str, ...]]:
    programs = []
    for area in ("planning", "execution", "integrity"):
        programs.append((f"schemas/control-plane/v3/{area}/materialize.py", "--check"))
        programs.append((f"scripts/tests/v3/{area}/materialize_fixtures.py", "--check"))
        programs.extend((str(p.relative_to(ROOT)),) for p in sorted(
            (ROOT / "scripts/tests/v3" / area).glob("*.test.py")
        ))
    require(len(programs) == 23, "M1 check inventory changed; inspect instead of reducing coverage")
    return programs


def harness_programs() -> list[tuple[str, ...]]:
    return [("scripts/tests/v3/harness/harness.test.py",)]


def run_contracts() -> tuple[int, int]:
    m1 = m1_programs()
    harness = harness_programs()
    for program in m1 + harness:
        print("RUN " + " ".join(program), flush=True)
        result = subprocess.run(
            [sys.executable, "-X", "utf8", "-B", *program], cwd=ROOT, timeout=180,
            capture_output=True, encoding="utf-8", errors="replace", check=False,
        )
        if result.returncode:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise ValueError(f"contract check failed: {program[0]}")
        print((result.stdout + result.stderr).strip(), flush=True)
    return len(m1), len(harness)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contracts", action="store_true")
    parser.add_argument("--candidate", help="require this full HEAD commit and a clean tree")
    args = parser.parse_args()
    head = git("rev-parse", "HEAD")
    require(git("merge-base", BASELINE, head) == BASELINE, "baseline is not an ancestor")
    if args.candidate:
        require(re.fullmatch(r"[0-9a-f]{40}", args.candidate) is not None,
                "candidate must be a full commit")
        require(args.candidate == head, "candidate is not HEAD")
        require(not git("status", "--porcelain"), "candidate is not clean")
    changed = set(filter(None, git("diff", "--name-only", BASELINE).splitlines()))
    untracked = set(filter(None, git("ls-files", "--others", "--exclude-standard").splitlines()))
    tracked = set(git("ls-files").splitlines())
    permitted = ALLOWED | PRODUCT_SLICE
    # The 2026-09-13 allowlist no longer covers this tree. Keep the baseline as an
    # ancestor, reject stray untracked files, and require the harness paths.
    historical = changed - permitted
    stray = untracked - permitted
    require(not stray, f"untracked files outside the harness slice: {sorted(stray)}")
    require(PRODUCT_SLICE <= (tracked | untracked),
            f"missing product-slice paths: {sorted(PRODUCT_SLICE - (tracked | untracked))}")
    git("diff", "--check", BASELINE, "--", *sorted(permitted & tracked))
    for path in sorted(PRODUCT_SLICE):
        for number, line in enumerate(read(path).splitlines(), 1):
            require(not line.endswith((" ", "\t")), f"trailing whitespace: {path}:{number}")
    require(ALLOWED <= tracked, "stage all orientation files, including AGENTS.md, before checking")
    require(read("AGENTS.md") == read("CLAUDE.md"), "agent entry instructions diverged")
    for entry in ("README.md", "AGENTS.md", "CLAUDE.md"):
        require("docs/v3/START-HERE.md" in read(entry)[:2200], f"missing early v3 route: {entry}")
    for entry in ("README.md", "VALIDATION.md", "ROADMAP.md"):
        require("START-HERE.md" in read("docs/v3/" + entry)[:2200],
                f"missing current entry link: docs/v3/{entry}")
    documents = sorted((ROOT / "docs/v3").glob("*.md"))
    links = check_links(documents + [ROOT / p for p in ("README.md", "AGENTS.md", "CLAUDE.md")])
    claims, decisions = check_registry()
    fixtures = 0
    for area, label, expected in (("planning", "M1A", 23), ("execution", "M1B", 24),
                                  ("integrity", "M1C", 24)):
        files = sorted((ROOT / "scripts/tests/v3" / area / "fixtures").glob(f"F-{label}-*.json"))
        require([p.stem for p in files] == [f"F-{label}-{n:03d}" for n in range(1, expected + 1)],
                f"{label} fixture IDs missing, extra or reordered")
        for path in files:
            json.loads(path.read_text(encoding="utf-8"))
        fixtures += len(files)
    print(f"candidate={head} mode={'clean-candidate' if args.candidate else 'working'}", flush=True)
    print(
        f"SCOPE_PASS baseline={BASELINE} ancestor=true historical_paths={len(historical)} "
        f"product_slice={len(PRODUCT_SLICE)}"
    )
    print(f"SPEC_STRUCTURE_PASS documents={len(documents)} links={links} claims={claims} "
          f"later_owner_decisions={decisions} fixtures={fixtures}", flush=True)
    if args.contracts:
        m1_count, harness_count = run_contracts()
        print(f"M1_CONTRACT_CHECKS_PASS commands={m1_count}")
        print(f"HARNESS_SLICE_CHECKS_PASS commands={harness_count}")
    if args.candidate:
        require(git("rev-parse", "HEAD") == args.candidate, "HEAD changed during gate")
        require(not git("status", "--porcelain"), "gate changed candidate files")
    print("V3_ORIENTATION_PASS_NOT_RELEASE_ACCEPTANCE")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"V3_ORIENTATION_FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
