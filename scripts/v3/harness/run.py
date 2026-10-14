"""Plan one task, admit one M1B route, and run one provider adapter."""

from __future__ import annotations

import argparse
import json
import sys

from scripts.v3.harness.errors import HarnessError
from scripts.v3.harness.planning import plan_task
from scripts.v3.harness.providers import ProviderRequest, open_provider
from scripts.v3.harness.routing import require_selected, select_route


def run_task(task: str, *, provider: str = "fixture", allow_live: bool = False) -> dict:
    """Execute the slice and return a JSON-ready result.

    Planning uses the M1A kernel. Route admission uses the M1B reference oracle
    on ``F-M1B-001``. The adapter runs only after that oracle selects a route.
    """

    planned = plan_task(task)
    route = select_route()
    route_id = require_selected(route["decision"])
    adapter = open_provider(provider)
    request = ProviderRequest(task=planned["intent_text"], packet_id=planned["packet_id"], route_id=route_id)
    result = adapter.execute(request, allow_live=allow_live)
    return {
        "execution": result.to_dict(),
        "planning": planned,
        "route": {
            "fixture_id": route["fixture_id"],
            "selected_route_id": route_id,
            "status": route["status"],
        },
        "task": planned["intent_text"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan a task and run it through one provider adapter.")
    parser.add_argument("--task", required=True, help="task text admitted as the M1A owner intent and goal outcome")
    parser.add_argument("--provider", default="fixture", help="adapter name: fixture or claude")
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="start the headless CLI; omitted in tests and CI",
    )
    args = parser.parse_args(argv)
    try:
        result = run_task(args.task, provider=args.provider, allow_live=args.allow_live)
    except HarnessError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
