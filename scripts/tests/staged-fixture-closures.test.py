#!/usr/bin/env python3
"""Run the staged-dependency guard against every pilot red-fixture copy list.

The red fixtures deliberately stage a partial ``scripts/`` tree.  Keep this check
independent from their runtime assertions: extract each loop that copies
``$SRC/scripts/$variable``, reproduce that exact list, and run the guard on the
result.  A list edit therefore fails locally even when the edited runtime branch
is not reached by a particular fixture invocation.
"""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path


LOOP = re.compile(
    r"for\s+(?P<variable>[A-Za-z_]\w*)\s+in\s+(?P<items>.*?)\s*;\s*do"
    r"(?P<body>.*?)\n\s*done",
    re.DOTALL,
)
def fixture_lists(path: Path) -> list[tuple[str, list[str]]]:
    text = path.read_text(encoding="utf-8")
    found: list[tuple[str, list[str]]] = []
    for match in LOOP.finditer(text):
        variable = match.group("variable")
        if not re.search(
            rf'cp\s+"\$SRC/scripts/\${re.escape(variable)}"', match.group("body")
        ):
            continue
        items = match.group("items").replace("\\\r\n", "").replace("\\\n", "")
        names = [name for name in shlex.split(items) if name]
        if not names:
            raise AssertionError(f"{path.name}: empty staged copy list")
        found.append((variable, names))
    # phase2/3/6 define one reusable full controller-closure function and may also
    # use small, intentionally incomplete worker lists later in the scenario.  The
    # guard-bearing closure is the list this self-check must reproduce.
    if "stage_controller_closure()" in text or "copy_controller()" in text:
        found = found[:1]
    if found and "staged-dependency-guard.py" not in text:
        raise AssertionError(f"{path.name}: no staged-dependency-guard invocation")
    if not found:
        return []
    return found


def check_fixture(source_scripts: Path, fixture: Path, root: Path) -> None:
    for index, (variable, names) in enumerate(fixture_lists(fixture), 1):
        staged = root / f"{fixture.stem}-{index}" / "scripts"
        staged.mkdir(parents=True)
        for name in names:
            source = source_scripts / name
            if not source.is_file():
                raise AssertionError(f"{fixture.name}: staged source is absent: {name}")
            shutil.copy2(source, staged / name)
        result = subprocess.run(
            [sys.executable, str(source_scripts / "tests/staged-dependency-guard.py"),
             str(source_scripts), str(staged)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            details = (result.stdout + result.stderr).strip()
            raise AssertionError(
                f"{fixture.name} list {index} ({variable}) failed guard:\n{details}"
            )
        print(f"ok    {fixture.name} staged list {index} ({len(names)} files)")


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    source_scripts = repo / "scripts"
    fixtures = sorted((repo / "scripts/tests").glob("hermes-pilot-phase*-red.test.sh"))
    if not fixtures:
        raise AssertionError("no pilot red fixtures found")
    override = os.environ.get("STAGED_FIXTURE_SCRATCH", "").strip()
    temporary_context = nullcontext(override) if override else tempfile.TemporaryDirectory(
        prefix="staged-fixture-closures-"
    )
    with temporary_context as temporary:
        scratch = Path(temporary)
        if not scratch.is_dir():
            raise AssertionError(f"staging scratch directory does not exist: {scratch}")
        checked = 0
        for fixture in fixtures:
            lists = fixture_lists(fixture)
            if not lists:
                continue
            check_fixture(source_scripts, fixture, scratch)
            checked += 1
    print(f"staged-fixture-closures: ALL PASS ({checked} fixtures with staged lists)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
