#!/usr/bin/env python3
"""Provider-free gate for the 2026-09-13 v3 orientation repair, not v3 release.

The default scope diff is the merge-base of HEAD and master, so a clean
master checkout passes and a work branch is judged only on its own changes.
``--baseline COMMIT`` compares against another ancestor. The repair pin is
``797be4f18edf3f9e0f2dbac9432f190dbe1ed969``.
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
HISTORICAL_BASELINE = "797be4f18edf3f9e0f2dbac9432f190dbe1ed969"
# Kept so older callers that imported the pin still see the same commit.
BASELINE = HISTORICAL_BASELINE
MASTER_REFS = ("master", "origin/master")
ALLOWED = {
    "README.md", "AGENTS.md", "CLAUDE.md", "docs/v3/README.md",
    "docs/v3/VALIDATION.md", "docs/v3/ROADMAP.md", "docs/v3/START-HERE.md",
    "state/tasks/v3-orientation-20260913.md", "tools/check_v3_orientation.py",
    "tools/test_check_v3_orientation_scope.py",
    ".gitattributes", ".github/workflows/ci.yml", "requirements.txt",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(
        ["git", "-c", "core.longpaths=true", "-c", "core.quotepath=false", *args],
        cwd=cwd, encoding="utf-8",
    ).strip()


def normalize_git_path(path: str) -> str:
    """Git on Windows can emit quotes or backslashes; allowlist entries use '/'."""
    return path.strip().strip('"').replace("\\", "/")


def resolve_commit(cwd: Path, rev: str) -> str:
    try:
        return git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", cwd=cwd)
    except subprocess.CalledProcessError as exc:
        raise ValueError(f"commit does not resolve: {rev}") from exc


def require_ancestor(cwd: Path, ancestor: str, head: str, message: str) -> str:
    resolved = resolve_commit(cwd, ancestor)
    require(git("merge-base", resolved, head, cwd=cwd) == resolved, message)
    return resolved


def default_scope_base(cwd: Path, head: str) -> str:
    """Nearest merge-base of HEAD with ``master`` or ``origin/master``.

    The closer base wins, so a stale local master does not classify commits
    already on origin/master as out-of-scope branch work. A clean checkout of
    either tip has an empty diff.
    """
    tips = []
    for ref in MASTER_REFS:
        try:
            tips.append(resolve_commit(cwd, ref))
        except ValueError:
            continue
    if not tips:
        raise ValueError("master ref not found (tried master, origin/master)")
    best: str | None = None
    best_distance: int | None = None
    for tip in tips:
        try:
            base = git("merge-base", tip, head, cwd=cwd)
        except subprocess.CalledProcessError as exc:
            raise ValueError(f"{tip} does not share history with HEAD") from exc
        distance = int(git("rev-list", "--count", f"{base}..{head}", cwd=cwd))
        if best is None or best_distance is None or distance < best_distance:
            best = base
            best_distance = distance
    if best is None:
        raise ValueError("master ref not found (tried master, origin/master)")
    return best


def comparison_base(cwd: Path, head: str, baseline: str | None) -> str:
    """Commit the out-of-scope diff is measured against."""
    if baseline:
        return require_ancestor(cwd, baseline, head, "baseline is not an ancestor")
    return default_scope_base(cwd, head)


def scope_paths(cwd: Path, base: str) -> tuple[set[str], set[str]]:
    changed = {normalize_git_path(p) for p in git("diff", "--name-only", base, cwd=cwd).splitlines() if p.strip()}
    untracked = {normalize_git_path(p) for p in git(
        "ls-files", "--others", "--exclude-standard", cwd=cwd
    ).splitlines() if p.strip()}
    return changed, untracked


def out_of_scope(changed: set[str], untracked: set[str], allowed: set[str]) -> list[str]:
    paths = {normalize_git_path(p) for p in changed | untracked if p.strip()}
    return sorted(paths - allowed)


def check_whitespace(cwd: Path, base: str) -> None:
    result = subprocess.run(
        ["git", "-c", "core.longpaths=true", "-c", "core.quotepath=false", "diff", "--check", base],
        cwd=cwd, capture_output=True, encoding="utf-8", errors="replace", check=False,
    )
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()
        raise ValueError(detail or f"whitespace errors against {base}")


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


def contract_programs() -> list[tuple[str, ...]]:
    programs: list[tuple[str, ...]] = []
    for area in ("planning", "execution", "integrity"):
        programs.append((f"schemas/control-plane/v3/{area}/materialize.py", "--check"))
        programs.append((f"scripts/tests/v3/{area}/materialize_fixtures.py", "--check"))
        programs.extend((str(p.relative_to(ROOT)),) for p in sorted(
            (ROOT / "scripts/tests/v3" / area).glob("*.test.py")
        ))
    return programs


def run_contracts() -> int:
    programs = contract_programs()
    require(len(programs) == 23, "M1 check inventory changed; inspect instead of reducing coverage")
    for program in programs:
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
    return len(programs)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contracts", action="store_true")
    parser.add_argument("--candidate", help="require this full HEAD commit and a clean tree")
    parser.add_argument(
        "--baseline",
        help="ancestor to diff against (default: merge-base of HEAD and master). "
             f"The 2026-09-13 pin is {HISTORICAL_BASELINE}.",
    )
    args = parser.parse_args()
    head = git("rev-parse", "HEAD")
    require_ancestor(ROOT, HISTORICAL_BASELINE, head, "historical baseline is not an ancestor")
    if args.candidate:
        require(re.fullmatch(r"[0-9a-f]{40}", args.candidate) is not None,
                "candidate must be a full commit")
        require(args.candidate == head, "candidate is not HEAD")
        require(not git("status", "--porcelain"), "candidate is not clean")
    base = comparison_base(ROOT, head, args.baseline)
    changed, untracked = scope_paths(ROOT, base)
    outside = out_of_scope(changed, untracked, ALLOWED)
    require(not outside, f"out-of-scope changes: {outside}")
    check_whitespace(ROOT, base)
    tracked = set(git("ls-files").splitlines())
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
    print(f"SCOPE_PASS baseline={base} historical={HISTORICAL_BASELINE} "
          f"changed={len(changed)} preserved_other_paths=true")
    print(f"SPEC_STRUCTURE_PASS documents={len(documents)} links={links} claims={claims} "
          f"later_owner_decisions={decisions} fixtures={fixtures}", flush=True)
    if args.contracts:
        print(f"M1_CONTRACT_CHECKS_PASS commands={run_contracts()}")
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
