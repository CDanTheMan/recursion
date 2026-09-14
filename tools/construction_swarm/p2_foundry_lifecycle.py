"""Fixed-purpose lifecycle integration for external v3 foundry observations."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from . import p2_host_lifecycle as host
from .p2_access import AccessRefused
from .p2_foundry_observation import FoundryObservationAdapter

SERVICE_KIND = "foundry-observation-v1"


def load_config(filename):
    outer = host._load_json(host._absolute_path(filename, "config"))
    host._require(
        isinstance(outer, dict)
        and set(outer) == {"version", "lifecycle_config", "project_runs"}
        and type(outer["version"]) is int and outer["version"] == 1,
        "configuration_refused", "foundry lifecycle config fields/version differ",
    )
    mappings = outer["project_runs"]
    host._require(
        isinstance(mappings, dict) and 1 <= len(mappings) <= 100,
        "configuration_refused", "one to 100 explicit project mappings required",
    )
    host._require(
        all(isinstance(value, str) and value and not any(ord(c) < 32 for c in value)
            for value in mappings.values()),
        "configuration_refused", "run paths must be bounded literal strings",
    )
    # The inherited adapter validates project names, absolute paths and aliasing,
    # without reading the run ledgers or starting any process.
    try:
        adapter = FoundryObservationAdapter(mappings)
    except (AccessRefused, ValueError, TypeError) as exc:
        raise host.LifecycleRefused("configuration_refused", "project mapping refused") from exc
    normalized = tuple(sorted((key, str(path)) for key, path in adapter.project_runs.items()))
    config = host.load_config(host._absolute_path(outer["lifecycle_config"], "lifecycle_config"))
    return config, normalized


class FoundryController(host.Controller):
    """Reuse the reviewed ownership controller with a fixed read-service command."""

    def __init__(self, config, project_runs):
        super().__init__(dict(config))
        self.project_runs = tuple(project_runs)
        self.binding = {
            "kind": SERVICE_KIND,
            "source_commit": self.config["source_commit"],
            "repository_root": self.config["repository_root"],
            "python_executable": self.config["python_executable"],
            "socket_path": self.config["socket_path"],
            "grants_file": self.config["grants_file"],
            "project_runs": dict(self.project_runs),
        }
        self.binding_bytes = host._json_bytes(self.binding)
        self.binding_digest = hashlib.sha256(self.binding_bytes).hexdigest()

    def _base_state(self, incarnation, restart_count, health, **detail):
        state = super()._base_state(incarnation, restart_count, health, **detail)
        state["observation_binding"] = json.loads(self.binding_bytes)
        state["observation_binding_sha256"] = self.binding_digest
        state["health_scope"] = "process_and_socket_transition"
        state["application_health"] = "read_response_required"
        return state

    def _reconcile_previous(self, previous):
        # Must precede super(): it can authorize cgroup cleanup/control writes.
        if previous is not None:
            host._require(
                previous.get("observation_binding") == self.binding
                and previous.get("observation_binding_sha256") == self.binding_digest,
                "state_refused", "prior observation binding differs",
            )
        return super()._reconcile_previous(previous)

    def _child_argv(self, incarnation):
        # Build the complete fixed argv rather than accepting a module/command in config.
        return [
            self.config["python_executable"], "-X", "utf8", "-B", "-m",
            "tools.construction_swarm.p2_foundry_observation", "serve",
            "--socket", self.config["socket_path"],
            "--source-commit", self.config["source_commit"],
            "--grants", self.config["grants_file"],
            "--instance-id", f"foundry-{self.controller_id}-{incarnation}",
            "--fence", str(incarnation),
            *[item for project, path in self.project_runs
              for item in ("--project-run", project + "=" + path)],
        ]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="explicitly run the foundry read-service controller")
    run.add_argument("--config", required=True)
    stop = commands.add_parser("stop", help="stop only the recorded owned controller/service")
    stop.add_argument("--state-root", required=True)
    stop.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args(argv)
    try:
        if args.command == "run":
            config, projects = load_config(args.config)
            return FoundryController(config, projects).run()
        host._require(0.1 <= args.timeout <= 15, "stop_refused", "stop timeout is invalid")
        host._print(host.request_stop(host._absolute_path(args.state_root, "state_root"), args.timeout))
        return 0
    except host.LifecycleRefused as exc:
        host._print({"status": "REFUSED", "error": {
            "code": exc.code, "message": exc.message, **exc.detail,
        }})
        return 3


if __name__ == "__main__":
    raise SystemExit(main())