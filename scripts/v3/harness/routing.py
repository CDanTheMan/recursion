"""Admit one execution route with the frozen M1B reference checker."""

from __future__ import annotations

import importlib.util
import re
from functools import lru_cache
from pathlib import Path
from types import ModuleType

from scripts.v3.harness.errors import HarnessError


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "scripts" / "tests" / "v3" / "execution" / "fixtures"
DEFAULT_FIXTURE_ID = "F-M1B-001"


def require_selected(decision: dict) -> str:
    """Return the selected route id, or refuse execution."""

    route_id = decision.get("selected_route_id")
    if decision.get("status") != "selected" or not isinstance(route_id, str) or not route_id:
        raise HarnessError("M1B route was not selected")
    return route_id


@lru_cache(maxsize=1)
def _execution_modules() -> tuple[ModuleType, ModuleType]:
    oracle = _load(
        "m1b_reference_oracle",
        ROOT / "scripts" / "tests" / "v3" / "execution" / "reference_oracle.py",
    )
    schema = _load(
        "m1b_schema_support",
        ROOT / "scripts" / "tests" / "v3" / "execution" / "schema.test.py",
    )
    return oracle, schema


def _load(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise HarnessError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def select_route(fixture_id: str = DEFAULT_FIXTURE_ID) -> dict:
    """Run the reference oracle on one frozen execution fixture.

    The default fixture is the eligible subscription selection ``F-M1B-001``.
    The returned decision is schema-valid and byte-matches the fixture's
    expected object. A divergent oracle refuses the run.
    """

    if re.fullmatch(r"F-M1B-[0-9]{3}", fixture_id) is None:
        raise HarnessError(f"not an M1B fixture id: {fixture_id}")
    path = FIXTURES / f"{fixture_id}.json"
    if not path.is_file():
        raise HarnessError(f"missing M1B fixture {fixture_id}")
    oracle, schema = _execution_modules()
    bundle = schema.strict_loads(path.read_bytes())
    schema.validate(bundle, "M1BFixtureBundle")
    decision = oracle.decide(bundle)
    schema.validate(decision)
    if decision != bundle["expected"]:
        raise HarnessError(
            f"{fixture_id} reference oracle diverged from the frozen expected decision"
        )
    return {
        "decision": decision,
        "fixture_id": fixture_id,
        "selected_route_id": decision.get("selected_route_id"),
        "status": decision.get("status"),
    }
