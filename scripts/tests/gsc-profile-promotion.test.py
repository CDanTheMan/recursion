#!/usr/bin/env python3
"""Phase 8 controls for explicit immutable project gate-profile promotion."""

from __future__ import annotations

import hashlib
import json
import runpy
import subprocess
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
PHASE8 = runpy.run_path(str(SOURCE / "scripts/tests/hermes-pilot-phase8-red.py"))
Fixture = PHASE8["Fixture"]
canonical_digest = PHASE8["canonical_digest"]
fields = PHASE8["fields"]

SELECTION_SCHEMA = "recursion-project-gate-profile-selection/v1"
PROMOTION_SCHEMA = "recursion-project-gate-profile-promotion/v1"
PROMOTION_ID = "chiron-shade-tops-v3"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def configure_historical_profile(fixture: Fixture) -> dict:
    required = {
        "acceptance": fixture.plan["goal"]["acceptance_suite"],
        "gate_class": fixture.plan["goal"]["gate_class"],
        "gate_files": fixture.plan["goal"]["gate_files"],
        "controller_gate_files": fixture.plan["goal"]["controller_gate_files"],
    }
    config_path = fixture.root / "state/project-config/chiron.json"
    pilot_path = fixture.root / "state/pilots/pilot-chiron.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    pilot = json.loads(pilot_path.read_text(encoding="utf-8"))
    config["required_gate_profile"] = required
    pilot["required_gate_profile"] = required
    fixture.write_json("state/project-config/chiron.json", config)
    fixture.write_json("state/pilots/pilot-chiron.json", pilot)
    return required


def initialize_controller_repository(fixture: Fixture) -> None:
    subprocess.run(["git", "init", "-q", str(fixture.root)], check=True)
    subprocess.run(
        ["git", "-C", str(fixture.root), "config", "user.name", "Phase 8 Test"], check=True,
    )
    subprocess.run(
        ["git", "-C", str(fixture.root), "config", "user.email", "phase8@example.invalid"],
        check=True,
    )
    subprocess.run(["git", "-C", str(fixture.root), "add", "scripts"], check=True)
    subprocess.run(
        ["git", "-C", str(fixture.root), "commit", "-qm", "controller fixture"], check=True,
    )


def install_promotion(fixture: Fixture, *, source_head: str | None = None) -> dict:
    fixture.install_seed_contract()
    live_head = subprocess.run(
        ["git", "-C", str(fixture.repo), "rev-parse", "HEAD"],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    seed = json.loads(
        fixture.run(
            "python3", "scripts/seed_contract.py", "inspect", "--repo", str(fixture.repo),
        ).stdout
    )
    profile_path = fixture.root / "scripts/gates/chiron-shade-tops-v3.json"
    profile = json.loads(
        (fixture.root / "scripts/gates/gsc-shade-tops-v3.json").read_text(encoding="utf-8")
    )
    profile["profile_id"] = "chiron-shade-tops-0x6c-v3"
    profile["base_commit"] = source_head or live_head
    profile["seed_contract"] = seed
    profile["controller_gate"]["sha256"] = file_sha256(
        fixture.root / "scripts/gsc-shade-tops-gate.py"
    )
    write_json(profile_path, profile)

    relative_binding = f"scripts/gates/promotions/{PROMOTION_ID}.json"
    relative_profile = "scripts/gates/chiron-shade-tops-v3.json"
    acceptance = (
        f"{fixture.root / 'scripts/gsc-shade-tops-gate.py'} --repo . "
        f"--profile {fixture.root / relative_profile}"
    )
    required = {
        "acceptance": acceptance,
        "gate_class": "heavy",
        "gate_files": ["user-client/render/tools/native-diff.cjs"],
        "controller_gate_files": [
            "scripts/gsc-shade-tops-gate.py",
            relative_profile,
            relative_binding,
        ],
    }
    binding = {
        "schema": PROMOTION_SCHEMA,
        "promotion_id": PROMOTION_ID,
        "project_id": "chiron",
        "source_head": source_head or live_head,
        "profile": {
            "profile_id": profile["profile_id"],
            "path": relative_profile,
            "sha256": file_sha256(profile_path),
        },
        "required_gate_profile": required,
    }
    write_json(fixture.root / relative_binding, binding)
    initialize_controller_repository(fixture)
    return {"binding": binding, "required": required, "live_head": live_head}


def v3_plan(fixture: Fixture, required: dict, *, suffix: str = "v3") -> dict:
    plan = json.loads(json.dumps(fixture.planner_plan))
    plan["id"] = f"chiron-phase8-plan-{suffix}"
    plan["goal"]["id"] = f"goal-chiron-phase8-smoke-{suffix}"
    plan["tasks"][0]["id"] = f"chiron-phase8-smoke-{suffix}"
    plan["goal"]["acceptance_suite"] = required["acceptance"]
    plan["goal"]["gate_class"] = required["gate_class"]
    plan["goal"]["gate_files"] = list(required["gate_files"])
    plan["goal"]["controller_gate_files"] = list(required["controller_gate_files"])
    plan["tasks"][0]["acceptance"] = required["acceptance"]
    plan["tasks"][0]["gate_class"] = required["gate_class"]
    plan["tasks"][0]["gate_files"] = list(required["gate_files"])
    plan["tasks"][0]["controller_gate_files"] = list(required["controller_gate_files"])
    plan["gate_profile_selection"] = {
        "schema": SELECTION_SCHEMA,
        "promotion_id": PROMOTION_ID,
    }
    return plan


def propose(fixture: Fixture, plan: dict, iid: str) -> subprocess.CompletedProcess[str]:
    fixture._write_instruction(iid, "pilot-chiron")
    decision = fixture.decision(
        verb="pilot-plan-propose",
        args=["chiron", str(plan["id"])],
        iid=iid,
        actor="pilot-chiron",
        goal=str(plan["goal"]["id"]),
        text="Propose one explicitly promoted immutable gate-profile plan.",
        extra={"plan": plan},
    )
    return fixture.run("python3", "scripts/project-pilot.py", "execute", str(decision))


def approve(fixture: Fixture, plan_id: str, goal_id: str, iid: str) -> subprocess.CompletedProcess[str]:
    record_path = fixture.root / f"state/plans/chiron/{plan_id}.json"
    record = json.loads(record_path.read_text(encoding="utf-8"))
    digest = str(record["plan_digest"])
    fixture._write_instruction(iid, "head-hermes", f"approve {plan_id} {digest}")
    decision = fixture.decision(
        verb="pilot-plan-approve",
        args=["chiron", plan_id, digest],
        iid=iid,
        actor="head-hermes",
        goal=goal_id,
        text="Approve only this exact promoted plan digest.",
    )
    return fixture.run("python3", "scripts/project-pilot.py", "execute", str(decision))


def test_explicit_promotion_preserves_historical_authority() -> bool:
    fixture = Fixture()
    try:
        historical = configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        status = fixture.run("python3", "scripts/project-pilot.py", "status", "chiron")
        if status.returncode:
            return False
        advertised = json.loads(status.stdout).get("gate_profile_promotions") or []
        if [item.get("promotion_id") for item in advertised] != [PROMOTION_ID]:
            return False

        # Materialize the selector-less historical plan first. It must retain the project v1
        # default even after the v3 promotion descriptor exists.
        if not PHASE8["test_fresh_plan"](fixture) or not PHASE8["test_approval"](fixture):
            return False
        historical_paths = [
            fixture.root / "state/project-config/chiron.json",
            fixture.root / "state/pilots/pilot-chiron.json",
            fixture.root / f"state/plans/chiron/{fixture.plan_id}.json",
            fixture.root / "state/goals/goal-chiron-phase8-smoke.md",
            fixture.root / "state/tasks/chiron-phase8-smoke.md",
        ]
        historical_bytes = {path: path.read_bytes() for path in historical_paths}
        historical_record = json.loads(historical_paths[2].read_text(encoding="utf-8"))
        if historical_record["plan"].get("gate_profile_selection") is not None:
            return False
        if historical_record["plan"]["goal"]["acceptance_suite"] != historical["acceptance"]:
            return False

        promoted = v3_plan(fixture, installed["required"])
        proposed = propose(fixture, promoted, "201")
        if proposed.returncode:
            return False
        promoted_path = fixture.root / f"state/plans/chiron/{promoted['id']}.json"
        record = json.loads(promoted_path.read_text(encoding="utf-8"))
        selection = record["plan"].get("gate_profile_selection")
        expected_binding_path = f"scripts/gates/promotions/{PROMOTION_ID}.json"
        expected_selection = {
            "schema": SELECTION_SCHEMA,
            "promotion_id": PROMOTION_ID,
            "binding_path": expected_binding_path,
            "binding_sha256": file_sha256(fixture.root / expected_binding_path),
        }
        if selection != expected_selection or record["plan_digest"] != canonical_digest(record["plan"]):
            return False
        approved = approve(
            fixture, str(promoted["id"]), str(promoted["goal"]["id"]), "202",
        )
        goal = fields(fixture.root / f"state/goals/{promoted['goal']['id']}.md")
        task = fields(fixture.root / f"state/tasks/{promoted['tasks'][0]['id']}.md")
        selection_text = json.dumps(expected_selection, sort_keys=True, separators=(",", ":"))
        reconcile = runpy.run_path(str(SOURCE / "scripts/project-reconcile.py"))
        config = json.loads(
            (fixture.root / "state/project-config/chiron.json").read_text(encoding="utf-8")
        )
        pilot = json.loads(
            (fixture.root / "state/pilots/pilot-chiron.json").read_text(encoding="utf-8")
        )
        independent_task = reconcile["_phase8_expected_task_values"](
            config, pilot, record["plan"], str(promoted["id"]),
            str(record["plan_digest"]), str(promoted["goal"]["id"]),
            record["plan"]["tasks"][0],
        )
        return (
            approved.returncode == 0
            and goal.get("gate_profile_selection") == selection_text
            and task.get("gate_profile_selection") == selection_text
            and independent_task.get("gate_profile_selection") == selection_text
            and all(path.read_bytes() == historical_bytes[path] for path in historical_paths)
        )
    finally:
        fixture.close()


def test_implicit_latest_and_substitution_fail_closed() -> bool:
    fixture = Fixture()
    try:
        historical = configure_historical_profile(fixture)
        installed = install_promotion(fixture)

        implicit = v3_plan(fixture, installed["required"], suffix="implicit")
        implicit.pop("gate_profile_selection")
        implicit_refused = propose(fixture, implicit, "301").returncode != 0

        latest = v3_plan(fixture, installed["required"], suffix="latest")
        latest["gate_profile_selection"]["promotion_id"] = "latest"
        latest_refused = propose(fixture, latest, "302").returncode != 0

        substituted = v3_plan(fixture, installed["required"], suffix="substitution")
        for gate in (substituted["goal"], substituted["tasks"][0]):
            gate["acceptance_suite" if gate is substituted["goal"] else "acceptance"] = historical["acceptance"]
            gate["gate_class"] = historical["gate_class"]
            gate["gate_files"] = list(historical["gate_files"])
            gate["controller_gate_files"] = list(historical["controller_gate_files"])
        substitution_refused = propose(fixture, substituted, "303").returncode != 0

        unmeasured_profile = fixture.root / "scripts/gates/chiron-shade-tops-v4.json"
        unmeasured_profile.write_bytes(
            (fixture.root / "scripts/gates/chiron-shade-tops-v3.json").read_bytes()
        )
        subprocess.run(
            ["git", "-C", str(fixture.root), "add", "scripts/gates/chiron-shade-tops-v4.json"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(fixture.root), "commit", "-qm", "tracked unmeasured profile"],
            check=True,
        )
        unmeasured = v3_plan(fixture, installed["required"], suffix="unmeasured")
        unmeasured["gate_profile_selection"]["promotion_id"] = "chiron-shade-tops-v4"
        unmeasured_refused = propose(fixture, unmeasured, "304").returncode != 0

        return all((implicit_refused, latest_refused, substitution_refused, unmeasured_refused))
    finally:
        fixture.close()


def test_promoted_source_head_mismatch_fails_closed() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture, source_head="0" * 40)
        promoted = v3_plan(fixture, installed["required"], suffix="wrong-source")
        result = propose(fixture, promoted, "401")
        return (
            result.returncode != 0
            and not (fixture.root / f"state/plans/chiron/{promoted['id']}.json").exists()
        )
    finally:
        fixture.close()


def test_promotion_inventory_is_project_scoped_and_current_project_stays_strict() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        install_promotion(fixture)
        promotions = fixture.root / "scripts/gates/promotions"

        # A malformed committed descriptor cannot be attributed to this project, and a
        # descriptor that explicitly belongs to another project must not couple that
        # project's dirt or schema errors into Chiron's status path.
        (promotions / "unattributed.json").write_text("{malformed\n", encoding="utf-8")
        write_json(
            promotions / "other-project.json",
            {
                "schema": "intentionally-invalid-other-project-schema",
                "promotion_id": "wrong-other-project-id",
                "project_id": "other-project",
            },
        )
        subprocess.run(
            ["git", "-C", str(fixture.root), "add", "scripts/gates/promotions"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(fixture.root), "commit", "-qm", "other project inventory"],
            check=True,
        )
        (promotions / "other-project.json").write_text("{dirty\n", encoding="utf-8")
        (promotions / "editor-scratch.json").write_text("{untracked\n", encoding="utf-8")
        status = fixture.run("python3", "scripts/project-pilot.py", "status", "chiron")
        if status.returncode:
            return False
        advertised = json.loads(status.stdout).get("gate_profile_promotions") or []
        if [item.get("promotion_id") for item in advertised] != [PROMOTION_ID]:
            return False

        # A dirty descriptor that claims this project is still a hard failure.
        (promotions / f"{PROMOTION_ID}.json").write_text("{dirty\n", encoding="utf-8")
        current_status = fixture.run("python3", "scripts/project-pilot.py", "status", "chiron")
        return current_status.returncode != 0
    finally:
        fixture.close()


def test_stale_instruction_930_cannot_gain_v3_authority() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        if not PHASE8["test_fresh_plan"](fixture) or not PHASE8["test_approval"](fixture):
            return False
        implementation = fixture.repo / "user-client/render/shade-tops.js"
        implementation.write_text("export const shadeTops = true;\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(fixture.repo), "add", "user-client/render/shade-tops.js"],
            check=True,
        )
        subprocess.run(
            [
                "git", "-C", str(fixture.repo), "-c", "user.name=fixture", "-c",
                "user.email=fixture@example.invalid", "commit", "-qm", "v3 source head",
            ],
            check=True,
        )
        fixture._write_instruction(
            "930", "head-hermes",
            "Open pilot window window-gsc-pilot-7 for chiron, "
            "goal goal-chiron-phase8-smoke, for 14400 seconds.",
        )
        decision = fixture.decision(
            verb="pilot-window-open",
            args=["chiron", "goal-chiron-phase8-smoke", "window-gsc-pilot-7", "14400"],
            iid="930",
            actor="head-hermes",
            goal="goal-chiron-phase8-smoke",
            text="Replay the stale v2 window request after the source moved.",
        )
        result = fixture.run("python3", "scripts/project-pilot.py", "execute", str(decision))
        return (
            result.returncode != 0
            and not (fixture.root / "state/pilot-windows/window-gsc-pilot-7.json").exists()
        )
    finally:
        fixture.close()


def main() -> int:
    controls = [
        (
            "an explicit v3 promotion materializes its immutable selector while historical v2 "
            "authority stays byte-identical",
            test_explicit_promotion_preserves_historical_authority,
        ),
        (
            "implicit latest, v1/v3 substitution, and tracked-but-unmeasured profiles fail closed",
            test_implicit_latest_and_substitution_fail_closed,
        ),
        (
            "a promoted profile cannot bind a different source HEAD",
            test_promoted_source_head_mismatch_fails_closed,
        ),
        (
            "promotion inventory is project-scoped while current-project bindings stay strict",
            test_promotion_inventory_is_project_scoped_and_current_project_stays_strict,
        ),
        (
            "stale instruction 930 cannot gain authority after the project source advances",
            test_stale_instruction_930_cannot_gain_v3_authority,
        ),
    ]
    failures = 0
    for label, control in controls:
        try:
            passed = bool(control())
        except Exception as exc:
            print(f"diag  {label}: {exc}")
            passed = False
        if passed:
            print(f"ok    {label}")
        else:
            print(f"FAIL  {label}")
            failures += 1
    if failures:
        print(f"gsc-profile-promotion: {failures} FAILED")
        return 1
    print("gsc-profile-promotion: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
