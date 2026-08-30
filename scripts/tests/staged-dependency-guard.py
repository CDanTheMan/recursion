#!/usr/bin/env python3
"""Check that a subset-staged controller contains every first-party dependency it invokes.

The red fixtures intentionally copy only part of ``scripts/`` into a disposable controller.
This guard follows ordinary imports, literal dynamic imports, and explicit shell invocations,
including files below subdirectories.  It compares dependencies with the staged tree rather
than assuming that the source checkout will be present at runtime.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


CODE_SUFFIXES = frozenset({".py", ".sh"})
SHELL_PATH_RE = re.compile(
    r"(?:^|[\s\"'`()])(?:[^\s\"'`()]+/)?scripts/"
    r"([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.(?:py|sh))(?:$|[\s\"'`()])"
)
SHELL_COMMAND_RE = re.compile(
    r"(?:python(?:3)?|bash|sh|source|\.)\s+"
    r"(?:[^\s\"'`()]+/)?([A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*\.(?:py|sh))"
)
SHELL_INVOCATION_RE = re.compile(r"\b(?:python(?:3)?|bash|sh|source)\s+|(?:^|\s)\.\s+")


def dependency_names(source: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in source.rglob("*"):
        if not path.is_file() or path.suffix not in CODE_SUFFIXES:
            continue
        relative = path.relative_to(source).as_posix()
        if relative.endswith("/__init__.py"):
            module = relative[:-len("/__init__.py")].replace("/", ".")
        else:
            module = relative.rsplit(".", 1)[0].replace("/", ".")
        result[module] = path
    return result


def python_dependencies(path: Path, names: dict[str, Path], source: Path,
                        staged: Path | None = None) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    staged = source if staged is None else staged
    relative_paths = {
        dependency_path.relative_to(source).as_posix(): module
        for module, dependency_path in names.items()
    }

    def add_module(module: str | None) -> None:
        if not module:
            return
        pieces = module.split(".")
        for end in range(len(pieces), 0, -1):
            candidate = ".".join(pieces[:end])
            if candidate in names:
                found.add(candidate)
                return

    relative = path.relative_to(staged).with_suffix("").as_posix().split("/")
    current_package = relative[:-1] if relative[-1] != "__init__" else relative[:-1]

    def add_relative(module: str | None, level: int) -> None:
        base = current_package[:max(0, len(current_package) - level + 1)]
        target = ".".join([*base, *(module.split(".") if module else [])])
        add_module(target)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                add_module(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                add_relative(node.module, node.level)
                if node.module is None:
                    for alias in node.names:
                        add_relative(alias.name, node.level)
            else:
                add_module(node.module)
        elif isinstance(node, ast.Call):
            function = node.func
            dynamic = (
                isinstance(function, ast.Name)
                and function.id in {"__import__", "import_module", "run_module"}
            ) or (
                isinstance(function, ast.Attribute)
                and function.attr in {"import_module", "run_module"}
            )
            if dynamic and node.args and isinstance(node.args[0], ast.Constant) \
                    and isinstance(node.args[0].value, str):
                add_module(node.args[0].value)
            if ((isinstance(function, ast.Name) and function.id == "spec_from_file_location")
                    or (isinstance(function, ast.Attribute)
                        and function.attr == "spec_from_file_location")):
                for argument in node.args[1:]:
                    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                        candidate = argument.value.replace("\\", "/")
                        if candidate.endswith((".py", ".sh")):
                            relative = candidate.lstrip("./")
                            module = relative_paths.get(relative)
                            if module is None:
                                module = relative.rsplit("/", 1)[-1].rsplit(".", 1)[0]
                            if module in names:
                                found.add(module)
    return found


def shell_dependencies(path: Path, names: dict[str, Path], source: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    found: set[str] = set()
    relative_paths = {
        dependency_path.relative_to(source).as_posix(): module
        for module, dependency_path in names.items()
    }

    def add_path(relative: str) -> None:
        # The guard is invoked from the fixture scripts using the source checkout as
        # its tool path; it is not part of the staged controller runtime.
        if relative == "tests/staged-dependency-guard.py":
            return
        module = relative_paths.get(relative)
        if module is None:
            basename = relative.rsplit("/", 1)[-1].rsplit(".", 1)[0]
            candidates = [
                candidate_path.relative_to(source).as_posix()
                for candidate_path in names.values()
                if candidate_path.name.rsplit(".", 1)[0] == basename
            ]
            relative = candidates[0] if len(candidates) == 1 else relative
            module = relative_paths.get(relative)
        if module is not None:
            found.add("@path:" + relative)

    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        if not SHELL_INVOCATION_RE.search(line):
            continue
        for match in SHELL_PATH_RE.finditer(line):
            add_path(match.group(1))
        for match in SHELL_COMMAND_RE.finditer(line):
            add_path(match.group(1))
    return found


def staged_module_path(staged: Path, module: str) -> Path:
    if module.startswith("@path:"):
        return staged / module[len("@path:"):]
    parts = module.split(".")
    package = staged.joinpath(*parts)
    if package.with_suffix(".py").is_file():
        return package.with_suffix(".py")
    return package / "__init__.py"


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: staged-dependency-guard.py SOURCE_SCRIPTS STAGED_SCRIPTS", file=sys.stderr)
        return 2
    source, staged = Path(argv[1]), Path(argv[2])
    if not source.is_dir() or not staged.is_dir():
        print("dependency guard: source and staged script directories are required", file=sys.stderr)
        return 2
    names = dependency_names(source)
    missing: list[tuple[str, str]] = []
    found: set[tuple[str, str]] = set()
    for path in sorted(staged.rglob("*")):
        if not path.is_file() or path.suffix not in CODE_SUFFIXES:
            continue
        try:
            dependencies = (python_dependencies(path, names, source, staged) if path.suffix == ".py"
                            else shell_dependencies(path, names, source))
        except (OSError, SyntaxError, UnicodeError, ValueError):
            missing.append((path.relative_to(staged).as_posix(), "<parse>"))
            continue
        for dependency in sorted(dependencies):
            display_dependency = dependency[len("@path:"):] if dependency.startswith("@path:") else dependency
            found.add((path.relative_to(staged).as_posix(), display_dependency))
            if not staged_module_path(staged, dependency).is_file():
                missing.append((path.relative_to(staged).as_posix(), dependency))
    print("dependency guard: first-party dependencies " + (
        ", ".join(f"{script}->{dependency}" for script, dependency in sorted(found))
        or "none"
    ))
    if missing:
        for script, dependency in sorted(set(missing)):
            print(f"dependency guard: missing {dependency} required by {script}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
