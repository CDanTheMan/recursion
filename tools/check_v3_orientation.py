#!/usr/bin/env python3
"""Provider-free gate for the 2026-09-13 v3 orientation repair, plus the harness slice.

The default scope diff is the merge-base of HEAD and master, so a clean
master checkout passes and a work branch is judged only on its own changes.
``--baseline COMMIT`` compares against another ancestor. The repair pin is
``797be4f18edf3f9e0f2dbac9432f190dbe1ed969``.

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
HISTORICAL_BASELINE = "797be4f18edf3f9e0f2dbac9432f190dbe1ed969"
# Kept so older callers that imported the pin still see the same commit.
BASELINE = HISTORICAL_BASELINE
MASTER_REFS = ("master", "origin/master")
ALLOWED = {
    "README.md", "AGENTS.md", "CLAUDE.md", "docs/v3/README.md",
    "docs/v3/VALIDATION.md", "docs/v3/ROADMAP.md", "docs/v3/START-HERE.md",
    "state/tasks/v3-orientation-20260913.md", "tools/check_v3_orientation.py",
    "tools/test_check_v3_orientation_scope.py",
    ".gitattributes", ".github/workflows/ci.yml", ".github/workflows/release.yml",
    "requirements.txt", "pyproject.toml", "tests/conftest.py", "tests/test_v3_checks.py",
    "tests/test_docs_drift.py", "tests/test_adapter_streams.py", "tests/test_e2e_console.py",
    "tests/test_process_lifecycle.py", "tests/.gitignore", "docs/USER-GUIDE.md", "CHANGELOG.md",
    "examples/sample-goal.txt", "examples/harness.json", "examples/stubs/provider_stub.py",
    "tests/test_config_logs.py", "docs/ARCHITECTURE.md",
    "scripts/install.sh", "scripts/install.ps1",
    "tests/test_install_scripts.py", "tests/test_harness_gaps.py",
}
PRODUCT_SLICE = {
    ".gitignore",
    "config/harness.json",
    "config/harness.schema.json",
    "docs/v3/HARNESS-SLICE.md",
    "pyproject.toml",
    "scripts/__init__.py",
    "scripts/recursion",
    "scripts/tests/v3/harness/adapters.test.py",
    "scripts/tests/v3/harness/doctor.test.py",
    "scripts/tests/v3/harness/fixtures/claude-stream.jsonl",
    "scripts/tests/v3/harness/fixtures/codex-stream.jsonl",
    "scripts/tests/v3/harness/fixtures/cursor-stream-no-usage.jsonl",
    "scripts/tests/v3/harness/fixtures/cursor-stream.jsonl",
    "scripts/tests/v3/harness/fixtures/gemini-stream-no-usage.jsonl",
    "scripts/tests/v3/harness/fixtures/gemini-stream.jsonl",
    "scripts/tests/v3/harness/fixtures/grok-stream.jsonl",
    "scripts/tests/v3/harness/fixtures/opencode-stream-captured.jsonl",
    "scripts/tests/v3/harness/fixtures/opencode-stream-no-usage.jsonl",
    "scripts/tests/v3/harness/fixtures/opencode-stream.jsonl",
    "scripts/tests/v3/harness/harness.test.py",
    "scripts/tests/v3/harness/landing.test.py",
    "scripts/tests/v3/harness/live.test.py",
    "scripts/tests/v3/harness/ops.test.py",
    "scripts/tests/v3/harness/orchestration.test.py",
    "scripts/tests/v3/harness/progress.test.py",
    "scripts/tests/v3/harness/review.test.py",
    "scripts/tests/v3/harness/routing.test.py",
    "scripts/tests/v3/harness/smoke.test.py",
    "scripts/tests/v3/harness/streams.test.py",
    "scripts/v3/__init__.py",
    "scripts/v3/harness/__init__.py",
    "scripts/v3/harness/__main__.py",
    "scripts/v3/harness/availability.py",
    "scripts/v3/harness/capabilities.py",
    "scripts/v3/harness/clean.py",
    "scripts/v3/harness/cli.py",
    "scripts/v3/harness/cooldowns.py",
    "scripts/v3/harness/config.py",
    "scripts/v3/harness/context.py",
    "scripts/v3/harness/dag.py",
    "scripts/v3/harness/dispatch.py",
    "scripts/v3/harness/doctor.py",
    "scripts/v3/harness/errors.py",
    "scripts/v3/harness/isolation.py",
    "scripts/v3/harness/land.py",
    "scripts/v3/harness/log.py",
    "scripts/v3/harness/orchestrate.py",
    "scripts/v3/harness/planning.py",
    "scripts/v3/harness/providers.py",
    "scripts/v3/harness/redact.py",
    "scripts/v3/harness/report.py",
    "scripts/v3/harness/review.py",
    "scripts/v3/harness/routing.py",
    "scripts/v3/harness/run.py",
    "scripts/v3/harness/smoke.py",
    "scripts/v3/harness/state.py",
    "scripts/v3/harness/streams.py",
    "scripts/v3/harness/usage.py",
    "scripts/v3/planning/__init__.py",
    "scripts/v3/proc/__init__.py",
    "scripts/v3/proc/lifecycle.py",
    "scripts/v3/planning/replay/__init__.py",
    "scripts/v3/planning/validation/__init__.py",
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
        programs.extend((p.relative_to(ROOT).as_posix(),) for p in sorted(
            (ROOT / "scripts/tests/v3" / area).glob("*.test.py")
        ))
    return programs


def m1_programs() -> list[tuple[str, ...]]:
    programs = contract_programs()
    require(len(programs) == 23, "M1 check inventory changed; inspect instead of reducing coverage")
    return programs


def harness_programs() -> list[tuple[str, ...]]:
    return [
        ("scripts/tests/v3/harness/adapters.test.py",),
        ("scripts/tests/v3/harness/doctor.test.py",),
        ("scripts/tests/v3/harness/harness.test.py",),
        ("scripts/tests/v3/harness/landing.test.py",),
        ("scripts/tests/v3/harness/live.test.py",),
        ("scripts/tests/v3/harness/ops.test.py",),
        ("scripts/tests/v3/harness/orchestration.test.py",),
        ("scripts/tests/v3/harness/progress.test.py",),
        ("scripts/tests/v3/harness/review.test.py",),
        ("scripts/tests/v3/harness/routing.test.py",),
        ("scripts/tests/v3/harness/smoke.test.py",),
        ("scripts/tests/v3/harness/streams.test.py",),
    ]


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
    tracked = set(git("ls-files").splitlines())
    permitted = ALLOWED | PRODUCT_SLICE
    outside = out_of_scope(changed, untracked, permitted)
    require(not outside, f"out-of-scope changes: {outside}")
    require(PRODUCT_SLICE <= (tracked | untracked),
            f"missing product-slice paths: {sorted(PRODUCT_SLICE - (tracked | untracked))}")
    check_whitespace(ROOT, base)
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
    print(f"SCOPE_PASS baseline={base} historical={HISTORICAL_BASELINE} "
          f"changed={len(changed)} preserved_other_paths=true product_slice={len(PRODUCT_SLICE)}")
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
