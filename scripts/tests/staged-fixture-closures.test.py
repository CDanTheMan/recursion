#!/usr/bin/env python3
"""Run the staged-dependency guard against every shell fixture copy list.

The fixtures deliberately stage partial ``scripts/`` trees.  Keep this check
independent from their runtime assertions: extract both loops and individual
``cp`` commands that copy from ``$SRC/scripts``, reproduce each destination's
exact list, and run the dependency guard on the result.  A list edit therefore
fails locally even when the edited runtime branch is not reached by a fixture.
"""

from __future__ import annotations

import ast
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
COMMAND = re.compile(
    r"\b(?P<program>cp|install|rsync)\s+"
    r"(?P<args>.*?)(?=\s*(?:&&|\|\||;|$))"
)
SOURCE = re.compile(r"^\$SRC/scripts/(?P<name>[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)$")
LOOP_SOURCE = re.compile(r"^\$SRC/scripts/\$(?P<variable>[A-Za-z_]\w*)$")


def logical_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    pending = ""
    start = 0
    for number, line in enumerate(text.splitlines(), 1):
        if not pending:
            start = number
        value = line.rstrip()
        if value.endswith("\\"):
            pending += value[:-1] + " "
            continue
        pending += value
        lines.append((start, pending))
        pending = ""
    if pending:
        lines.append((start, pending))
    return lines


def target_group(tokens: list[str], source_indexes: list[int]) -> str:
    for token in tokens[max(source_indexes) + 1:]:
        if token.startswith((">", "<", "2>")):
            continue
        if "/scripts" in token:
            return token.split("/scripts", 1)[0] + "/scripts"
        return token
    raise AssertionError("cp command has no destination")


def python_path_parts(node: ast.AST) -> list[str] | None:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.BinOp) and isinstance(current.op, ast.Div):
        if not isinstance(current.right, (ast.Constant, ast.Name)):
            return None
        value = current.right.value if isinstance(current.right, ast.Constant) else current.right.id
        parts.append(value)
        current = current.left
    if not isinstance(current, ast.Name) or current.id != "SOURCE":
        return None
    return list(reversed(parts))


def python_fixture_lists(path: Path, text: str) -> list[tuple[str, list[str]]]:
    try:
        tree = ast.parse(text, filename=str(path))
    except (SyntaxError, UnicodeError) as exc:
        raise AssertionError(f"{path.name}: cannot parse fixture: {exc}") from exc

    found: list[tuple[str, list[str]]] = []
    has_partial_copy = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.For) or not isinstance(node.target, ast.Name):
            continue
        if not isinstance(node.iter, (ast.Tuple, ast.List)):
            continue
        try:
            names = [value for value in ast.literal_eval(node.iter) if isinstance(value, str)]
        except (ValueError, TypeError):
            continue
        if not names:
            continue
        variable = node.target.id
        for call in (candidate for child in node.body for candidate in ast.walk(child)):
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute) \
                    or call.func.attr != "copy2" or not call.args:
                continue
            parts = python_path_parts(call.args[0])
            if parts == ["scripts", variable]:
                found.append((f"python-for-{variable}", names))
                has_partial_copy = True
                break

    for call in (node for node in ast.walk(tree) if isinstance(node, ast.Call)):
        if not isinstance(call.func, ast.Attribute) or call.func.attr != "copy2" or not call.args:
            continue
        parts = python_path_parts(call.args[0])
        if parts and parts[0] == "scripts":
            if not has_partial_copy:
                raise AssertionError(f"{path.name}: unrecognised Python script staging form")
            break
    return found


def fixture_lists(path: Path) -> list[tuple[str, list[str]]]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".py":
        return python_fixture_lists(path, text)
    found: list[tuple[str, list[str]]] = []
    loop_variables: set[str] = set()
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
        loop_variables.add(variable)

    direct: dict[str, list[str]] = {}
    direct_line: dict[str, int] = {}
    saw_staging_command = False
    for line_number, line in logical_lines(text):
        if line.lstrip().startswith("#"):
            continue
        for command in COMMAND.finditer(line):
            args = command.group("args")
            if "$SRC/scripts/" not in args:
                continue
            saw_staging_command = True
            if command.group("program") != "cp":
                raise AssertionError(
                    f"{path.name}:{line_number}: unsupported staging command "
                    f"{command.group('program')}"
                )
            try:
                tokens = shlex.split(args, comments=True)
            except ValueError as exc:
                raise AssertionError(
                    f"{path.name}:{line_number}: cannot parse staging command: {exc}"
                ) from exc
            source_indexes: list[int] = []
            names: list[str] = []
            for index, token in enumerate(tokens):
                literal = SOURCE.fullmatch(token)
                if literal:
                    source_indexes.append(index)
                    names.append(literal.group("name"))
                    continue
                loop_source = LOOP_SOURCE.fullmatch(token)
                if loop_source and loop_source.group("variable") in loop_variables:
                    continue
                if "$SRC/scripts/" in token:
                    raise AssertionError(
                        f"{path.name}:{line_number}: unrecognised staging source {token}"
                    )
            if not names:
                continue
            group = target_group(tokens, source_indexes)
            direct.setdefault(group, []).extend(names)
            direct_line.setdefault(group, line_number)
    if found and len(found) == 1 and direct:
        # A fixture may restore one file later after replacing it with a test stub.  It
        # is still the same staged tree, not a second closure to check independently.
        variable, names = found[0]
        for direct_names in direct.values():
            names.extend(direct_names)
        found[0] = (variable, names)
    else:
        found.extend(
            (f"cp@{direct_line[group]}", names)
            for group, names in direct.items()
        )

    # phase2/3/6 define one reusable full controller-closure function and may also
    # use small, intentionally incomplete worker lists later in the scenario.  The
    # guard-bearing closure is the list this self-check must reproduce.
    if "stage_controller_closure()" in text or "copy_controller()" in text:
        found = found[:1]
    if not found and saw_staging_command:
        raise AssertionError(f"{path.name}: staging form was not recognised")
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
    fixtures = sorted(
        path for path in (repo / "scripts/tests").iterdir()
        if path.is_file() and path.suffix in {".py", ".sh"}
    )
    if not fixtures:
        raise AssertionError("no shell fixtures found")
    override = os.environ.get("STAGED_FIXTURE_SCRATCH", "").strip()
    temporary_context = nullcontext(override) if override else tempfile.TemporaryDirectory(
        prefix="staged-fixture-closures-"
    )
    with temporary_context as temporary:
        scratch = Path(temporary)
        if not scratch.is_dir():
            raise AssertionError(f"staging scratch directory does not exist: {scratch}")
        checked: list[str] = []
        skipped: list[str] = []
        for fixture in fixtures:
            lists = fixture_lists(fixture)
            if not lists:
                skipped.append(fixture.name)
                continue
            check_fixture(source_scripts, fixture, scratch)
            checked.append(fixture.name)
    checked_text = ", ".join(checked) or "none"
    skipped_text = ", ".join(skipped) or "none"
    print(
        "staged-fixture-closures: ALL PASS "
        f"(checked {len(checked)}: {checked_text}; "
        f"skipped {len(skipped)} with no recognised partial scripts staging: {skipped_text})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
