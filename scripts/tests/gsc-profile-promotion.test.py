#!/usr/bin/env python3
"""Phase 8 controls for explicit immutable project gate-profile promotion."""

from __future__ import annotations

import hashlib
import json
import os
import runpy
import shutil
import subprocess
import time
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
PHASE8 = runpy.run_path(str(SOURCE / "scripts/tests/hermes-pilot-phase8-red.py"))
Fixture = PHASE8["Fixture"]
canonical_digest = PHASE8["canonical_digest"]
fields = PHASE8["fields"]
PILOT = runpy.run_path(str(SOURCE / "scripts/project-pilot.py"))
AUTHORITY = runpy.run_path(str(SOURCE / "scripts/project_authority.py"))
AuthorityError = AUTHORITY["AuthorityError"]

SELECTION_SCHEMA = "recursion-project-gate-profile-selection/v1"
PROMOTION_SCHEMA = "recursion-project-gate-profile-promotion/v1"
PROMOTION_ID = "chiron-shade-tops-v3"
AUTHORITY_V2_SCHEMA = "recursion-project-authority-contract/v2"
AUTHORITY_V2_RELATIONSHIP = "remote-descends-from-source"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def byte_tree_fingerprint(root: Path) -> dict[str, tuple[int, str]]:
    return {
        str(path.relative_to(root)): (path.stat().st_mode & 0o777, file_sha256(path))
        for path in sorted(root.rglob("*")) if path.is_file() and not path.is_symlink()
    }


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
    subprocess.run(
        ["git", "-C", str(fixture.root), "config", "core.autocrlf", "false"], check=True,
    )
    subprocess.run(["git", "-C", str(fixture.root), "add", "scripts"], check=True)
    subprocess.run(
        ["git", "-C", str(fixture.root), "commit", "-qm", "controller fixture"], check=True,
    )


def git_output(repository: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *args], text=True, capture_output=True, check=True,
    ).stdout.strip()


def configure_project_remote(fixture: Fixture, remote: Path) -> None:
    config_path = fixture.root / "state/project-config/chiron.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["remote"] = str(remote)
    fixture.write_json("state/project-config/chiron.json", config)


def install_descendant_bare_remote(
    fixture: Fixture, *, retain_remote_object_locally: bool = True,
) -> tuple[Path, str, str]:
    """Create source < remote/main while leaving the project checkout at exact source."""
    source_head = git_output(fixture.repo, "rev-parse", "HEAD")
    remote = fixture.temp / (
        "chiron-descendant.git" if retain_remote_object_locally else "chiron-missing-object.git"
    )
    if retain_remote_object_locally:
        marker = fixture.repo / "user-client/render/remote-descendant.js"
        marker.write_text("export const remoteDescendant = true;\n", encoding="utf-8")
        subprocess.run(
            ["git", "-C", str(fixture.repo), "add", "user-client/render/remote-descendant.js"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(fixture.repo), "commit", "-qm", "remote descendant"],
            check=True,
        )
        remote_head = git_output(fixture.repo, "rev-parse", "HEAD")
        subprocess.run(["git", "clone", "-q", "--bare", str(fixture.repo), str(remote)], check=True)
        subprocess.run(["git", "-C", str(fixture.repo), "reset", "--hard", source_head],
                       stdout=subprocess.DEVNULL, check=True)
    else:
        subprocess.run(["git", "clone", "-q", "--bare", str(fixture.repo), str(remote)], check=True)
        publisher = fixture.temp / "remote-publisher"
        subprocess.run(["git", "clone", "-q", str(remote), str(publisher)], check=True)
        subprocess.run(["git", "-C", str(publisher), "config", "user.name", "Phase 8 Test"],
                       check=True)
        subprocess.run(
            ["git", "-C", str(publisher), "config", "user.email", "phase8@example.invalid"],
            check=True,
        )
        marker = publisher / "user-client/render/remote-descendant.js"
        marker.write_text("export const remoteDescendant = true;\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(publisher), "add", str(marker.relative_to(publisher))],
                       check=True)
        subprocess.run(["git", "-C", str(publisher), "commit", "-qm", "remote descendant"],
                       check=True)
        remote_head = git_output(publisher, "rev-parse", "HEAD")
        subprocess.run(["git", "-C", str(publisher), "push", "-q", "origin", "HEAD:main"],
                       check=True)
    configure_project_remote(fixture, remote)
    return remote, source_head, remote_head


def install_divergent_bare_remote(fixture: Fixture) -> tuple[Path, str, str]:
    """Create a locally present remote tip that has no ancestry relationship to source."""
    source_head = git_output(fixture.repo, "rev-parse", "HEAD")
    empty_tree = subprocess.run(
        ["git", "-C", str(fixture.repo), "mktree"], input="", text=True,
        capture_output=True, check=True,
    ).stdout.strip()
    divergent_head = subprocess.run(
        ["git", "-C", str(fixture.repo), "commit-tree", empty_tree, "-m", "divergent root"],
        text=True, capture_output=True, check=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", str(fixture.repo), "update-ref", "refs/heads/divergent", divergent_head],
        check=True,
    )
    remote = fixture.temp / "chiron-divergent.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(fixture.repo), str(remote)], check=True)
    subprocess.run(
        ["git", "--git-dir", str(remote), "update-ref", "refs/heads/main", divergent_head],
        check=True,
    )
    configure_project_remote(fixture, remote)
    return remote, source_head, divergent_head


def advance_bare_remote_with_local_object(fixture: Fixture, remote: Path, parent: str) -> str:
    """Advance remote/main without moving the exact checked-out source branch."""
    tree = git_output(fixture.repo, "rev-parse", f"{parent}^{{tree}}")
    advanced = subprocess.run(
        ["git", "-C", str(fixture.repo), "commit-tree", tree, "-p", parent,
         "-m", "later authenticated remote descendant"],
        text=True, capture_output=True, check=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "-C", str(fixture.repo), "push", "-q", str(remote),
         f"{advanced}:refs/heads/main"],
        check=True,
    )
    return advanced


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
        fixture.write_json(
            "state/pilot-windows/chiron-historical-window.json",
            {
                "schema_version": 1, "id": "chiron-historical-window",
                "project_id": "chiron", "pilot_id": "pilot-chiron",
                "goal_id": fixture.plan["goal"]["id"], "plan_id": fixture.plan_id,
                "plan_digest": historical_record["plan_digest"], "status": "armed",
                "expires_at_epoch": int(time.time()) + 3600,
            },
        )
        historical_pin_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        if historical_pin_result.returncode:
            return False
        historical_pin = json.loads(historical_pin_result.stdout)

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
            and historical_pin.get("source_head")
            == historical_record["plan"]["authority_contract"]["source_head"]
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


def test_promoted_descendant_remote_binds_explicit_v2_authority() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        remote, source_head, remote_head = install_descendant_bare_remote(fixture)
        if source_head != installed["live_head"]:
            return False
        if git_output(remote, "rev-parse", "--is-bare-repository") != "true":
            return False
        promoted = v3_plan(fixture, installed["required"], suffix="remote-descendant")
        result = propose(fixture, promoted, "411")
        if result.returncode:
            return False
        record = json.loads(
            (fixture.root / f"state/plans/chiron/{promoted['id']}.json").read_text(
                encoding="utf-8"
            )
        )
        expected_authority = {
            "schema": AUTHORITY_V2_SCHEMA,
            "charter_sha256": hashlib.sha256(
                "Build-verifiable Chiron application changes only.".encode()
            ).hexdigest(),
            "default_branch": "main",
            "required_non_goals": json.loads(
                (fixture.root / "state/project-config/chiron.json").read_text(encoding="utf-8")
            )["required_non_goals"],
            "source_head": source_head,
            "remote_head": remote_head,
            "remote_relationship": AUTHORITY_V2_RELATIONSHIP,
        }
        return (
            record["plan"].get("authority_contract") == expected_authority
            and record["plan"]["gate_profile_selection"]["promotion_id"] == PROMOTION_ID
            and record["plan_digest"] == canonical_digest(record["plan"])
            and git_output(fixture.repo, "rev-parse", "HEAD") == source_head
            and git_output(fixture.repo, "rev-parse", "refs/heads/main") == source_head
            and not git_output(fixture.repo, "status", "--porcelain", "--untracked-files=all")
        )
    finally:
        fixture.close()


def test_selectorless_legacy_authority_remains_exact_tip_only() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        install_promotion(fixture)
        _, source_head, _ = install_descendant_bare_remote(fixture)
        historical = json.loads(json.dumps(fixture.planner_plan))
        result = propose(fixture, historical, "421")
        return (
            result.returncode != 0
            and git_output(fixture.repo, "rev-parse", "HEAD") == source_head
            and not (fixture.root / f"state/plans/chiron/{historical['id']}.json").exists()
        )
    finally:
        fixture.close()


def test_promoted_remote_divergence_fails_and_missing_object_uses_read_only_scratch() -> bool:
    divergence = Fixture()
    missing = Fixture()
    try:
        configure_historical_profile(divergence)
        divergent_install = install_promotion(divergence)
        _, divergent_source, _ = install_divergent_bare_remote(divergence)
        divergent_plan = v3_plan(
            divergence, divergent_install["required"], suffix="remote-divergence",
        )
        divergent_result = propose(divergence, divergent_plan, "431")

        configure_historical_profile(missing)
        missing_install = install_promotion(missing)
        _, missing_source, missing_remote = install_descendant_bare_remote(
            missing, retain_remote_object_locally=False,
        )
        refs_before = git_output(
            missing.repo, "for-each-ref", "--format=%(refname) %(objectname)",
        )
        git_dir = Path(git_output(missing.repo, "rev-parse", "--absolute-git-dir"))
        git_bytes_before = byte_tree_fingerprint(git_dir)
        fetch_head_path = missing.repo / ".git/FETCH_HEAD"
        fetch_head_before = fetch_head_path.read_bytes() if fetch_head_path.is_file() else None
        missing_plan = v3_plan(missing, missing_install["required"], suffix="missing-object")
        missing_result = propose(missing, missing_plan, "432")
        missing_object = subprocess.run(
            ["git", "-C", str(missing.repo), "cat-file", "-e", f"{missing_remote}^{{commit}}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False,
        )
        return (
            divergent_source == divergent_install["live_head"]
            and divergent_result.returncode != 0
            and "does not contain the exact source" in divergent_result.stderr
            and not (
                divergence.root / f"state/plans/chiron/{divergent_plan['id']}.json"
            ).exists()
            and missing_source == missing_install["live_head"]
            and missing_object.returncode != 0
            and missing_result.returncode == 0
            and (missing.root / f"state/plans/chiron/{missing_plan['id']}.json").is_file()
            and git_output(
                missing.repo, "for-each-ref", "--format=%(refname) %(objectname)",
            ) == refs_before
            and byte_tree_fingerprint(git_dir) == git_bytes_before
            and (fetch_head_path.read_bytes() if fetch_head_path.is_file() else None)
            == fetch_head_before
            and git_output(missing.repo, "rev-parse", "refs/heads/main") == missing_source
            and not git_output(
                missing.repo, "status", "--porcelain", "--untracked-files=all",
            )
        )
    finally:
        divergence.close()
        missing.close()


def test_promoted_remote_rollback_fails_closed() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        remote, source_head, remote_head = install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="remote-rollback")
        proposed = propose(fixture, promoted, "441")
        if proposed.returncode:
            return False
        record_path = fixture.root / f"state/plans/chiron/{promoted['id']}.json"
        record = json.loads(record_path.read_text(encoding="utf-8"))
        if record["plan"].get("authority_contract", {}).get("remote_head") != remote_head:
            return False
        subprocess.run(
            ["git", "--git-dir", str(remote), "update-ref", "refs/heads/main", source_head],
            check=True,
        )
        result = approve(fixture, str(promoted["id"]), str(promoted["goal"]["id"]), "442")
        return (
            result.returncode == 4
            and "no longer contains its anchored tip" in result.stderr
            and not (fixture.root / f"state/goals/{promoted['goal']['id']}.md").exists()
            and not (fixture.root / f"state/tasks/{promoted['tasks'][0]['id']}.md").exists()
        )
    finally:
        fixture.close()


def test_remote_proof_unavailability_is_typed_and_state_preserving() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        remote, source_head, _ = install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="remote-unavailable")
        if propose(fixture, promoted, "447").returncode or approve(
            fixture, str(promoted["id"]), str(promoted["goal"]["id"]), "448",
        ).returncode:
            return False
        state_before = {
            path.relative_to(fixture.root): path.read_bytes()
            for path in (fixture.root / "state").rglob("*") if path.is_file()
        }
        refs_before = git_output(
            fixture.repo, "for-each-ref", "--format=%(refname) %(objectname)",
        )
        unavailable = remote.with_name(remote.name + ".offline")
        remote.rename(unavailable)
        result = fixture.run(
            "python3", "scripts/project-pilot.py", "verify-approved-goal",
            "chiron", str(promoted["goal"]["id"]), "--check-remote",
        )
        state_after = {
            path.relative_to(fixture.root): path.read_bytes()
            for path in (fixture.root / "state").rglob("*") if path.is_file()
        }
        return (
            result.returncode == 74
            and "remote freshness" in result.stderr
            and state_after == state_before
            and git_output(
                fixture.repo, "for-each-ref", "--format=%(refname) %(objectname)",
            ) == refs_before
            and git_output(fixture.repo, "rev-parse", "refs/heads/main") == source_head
            and not git_output(
                fixture.repo, "status", "--porcelain", "--untracked-files=all",
            )
        )
    finally:
        fixture.close()


def test_proved_repository_dirt_is_invalid_not_unavailable() -> bool:
    fixture = Fixture()
    try:
        config = json.loads(
            (fixture.root / "state/project-config/chiron.json").read_text(encoding="utf-8")
        )
        implementation = fixture.repo / "user-client/render/shade-tops.js"
        exact = implementation.read_bytes()
        implementation.write_bytes(exact + b"// tracked dirt\n")
        tracked: tuple[int, str] | None = None
        try:
            AUTHORITY["observe_clean_source"](config)
        except AuthorityError as exc:
            tracked = (exc.code, str(exc))
        implementation.write_bytes(exact)
        untracked_path = fixture.repo / "user-client/render/untracked-dirt.js"
        untracked_path.write_text("export const dirt = true;\n", encoding="utf-8")
        untracked: tuple[int, str] | None = None
        try:
            AUTHORITY["observe_clean_source"](config)
        except AuthorityError as exc:
            untracked = (exc.code, str(exc))
        untracked_path.unlink()
        relative = str(implementation.relative_to(fixture.repo))
        subprocess.run(
            ["git", "-C", str(fixture.repo), "update-index", "--assume-unchanged", relative],
            check=True,
        )
        implementation.write_bytes(exact + b"// assume-unchanged dirt\n")
        hidden: tuple[int, str] | None = None
        try:
            AUTHORITY["observe_clean_source"](config)
        except AuthorityError as exc:
            hidden = (exc.code, str(exc))
        finally:
            subprocess.run(
                ["git", "-C", str(fixture.repo), "update-index", "--no-assume-unchanged", relative],
                check=True,
            )
            implementation.write_bytes(exact)
        return tracked == (4, "project repository must be exactly clean before authority is proven") \
            and untracked == tracked \
            and hidden == (4, "project repository index hides tracked worktree changes")
    finally:
        fixture.close()


def test_empty_authenticated_remote_is_unavailable_not_stale() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        empty = fixture.temp / "empty-authenticated.git"
        subprocess.run(["git", "init", "-q", "--bare", str(empty)], check=True)
        configure_project_remote(fixture, empty)
        promoted = v3_plan(fixture, installed["required"], suffix="empty-remote")
        fixture._write_instruction("439", "pilot-chiron")
        decision = fixture.decision(
            verb="pilot-plan-propose", args=["chiron", str(promoted["id"])], iid="439",
            actor="pilot-chiron", goal=str(promoted["goal"]["id"]),
            text="Propose one explicitly promoted immutable gate-profile plan.",
            extra={"plan": promoted},
        )
        state_before = byte_tree_fingerprint(fixture.root / "state")
        refs_before = git_output(
            fixture.repo, "for-each-ref", "--format=%(refname) %(objectname)",
        )
        index_before = file_sha256(fixture.repo / ".git/index")
        result = fixture.run("python3", "scripts/project-pilot.py", "execute", str(decision))
        return (
            result.returncode == 74
            and "no branch evidence" in result.stderr
            and not (fixture.root / f"state/plans/chiron/{promoted['id']}.json").exists()
            and byte_tree_fingerprint(fixture.root / "state") == state_before
            and git_output(
                fixture.repo, "for-each-ref", "--format=%(refname) %(objectname)",
            ) == refs_before
            and file_sha256(fixture.repo / ".git/index") == index_before
            and not git_output(
                fixture.repo, "status", "--porcelain", "--untracked-files=all",
            )
        )
    finally:
        fixture.close()


def test_promoted_remote_advancement_approves_and_exports_exact_source_pin() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        remote, source_head, bound_remote = install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="remote-advancement")
        if propose(fixture, promoted, "443").returncode:
            return False
        current_remote = advance_bare_remote_with_local_object(fixture, remote, bound_remote)
        if current_remote == bound_remote:
            return False
        if approve(
            fixture, str(promoted["id"]), str(promoted["goal"]["id"]), "444",
        ).returncode:
            return False
        verified = fixture.run(
            "python3", "scripts/project-pilot.py", "verify-approved-goal",
            "chiron", str(promoted["goal"]["id"]), "--check-remote",
        )
        if verified.returncode:
            return False
        contract = json.loads(verified.stdout)
        record = json.loads(
            (fixture.root / f"state/plans/chiron/{promoted['id']}.json").read_text(
                encoding="utf-8"
            )
        )
        fixture.write_json(
            "state/pilot-windows/chiron-promoted-window.json",
            {
                "schema_version": 1,
                "id": "chiron-promoted-window",
                "project_id": "chiron",
                "pilot_id": "pilot-chiron",
                "goal_id": promoted["goal"]["id"],
                "plan_id": promoted["id"],
                "plan_digest": record["plan_digest"],
                "status": "armed",
                "expires_at_epoch": int(time.time()) + 3600,
            },
        )
        pin_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        if pin_result.returncode:
            return False
        pin = json.loads(pin_result.stdout)
        window_path = fixture.root / "state/pilot-windows/chiron-promoted-window.json"
        goal_path = fixture.root / f"state/goals/{promoted['goal']['id']}.md"
        original_read_text = Path.read_text

        def deny_goal(self, *args, **kwargs):
            if self == goal_path:
                raise PermissionError("simulated transient pinned-goal read failure")
            return original_read_text(self, *args, **kwargs)

        pin_unavailable = 0
        Path.read_text = deny_goal
        try:
            PILOT["active_source_pin"](fixture.root, "chiron")
        except SystemExit as exc:
            pin_unavailable = int(exc.code)
        finally:
            Path.read_text = original_read_text
        fixture.write_json(
            "state/pilot-windows/other-project-window.json",
            {"project_id": "other-project", "status": "armed", "expires_at_epoch": "bad"},
        )
        other_project_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        mismatched = json.loads(window_path.read_text(encoding="utf-8"))
        mismatched["plan_id"] = "wrong-plan"
        write_json(window_path, mismatched)
        mismatch_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        mismatched["plan_id"] = promoted["id"]
        write_json(window_path, mismatched)
        goal_text = goal_path.read_text(encoding="utf-8")
        goal_path.write_text(
            goal_text.replace("status: active", "status: verifying", 1), encoding="utf-8",
        )
        verifying_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        if verifying_result.returncode:
            return False
        verifying_pin = json.loads(verifying_result.stdout)
        paused_bytes = goal_path.read_bytes()
        goal_path.write_text(
            paused_bytes.decode("utf-8").replace("status: verifying", "status: paused", 1),
            encoding="utf-8",
        )
        paused_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        if paused_result.returncode:
            return False
        paused_pin = json.loads(paused_result.stdout)
        second = json.loads(window_path.read_text(encoding="utf-8"))
        second["id"] = "chiron-competing-window"
        write_json(fixture.root / "state/pilot-windows/chiron-competing-window.json", second)
        competing_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        (fixture.root / "state/pilot-windows/chiron-competing-window.json").unlink()
        expired = json.loads(window_path.read_text(encoding="utf-8"))
        expired["expires_at_epoch"] = int(time.time()) - 1
        write_json(window_path, expired)
        expired_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        # Terminal-receipt authentication is independent of elapsed-window release. Restore
        # a live record and the verifying goal before proving a forged terminal status still
        # cannot drop the pin.
        expired["expires_at_epoch"] = int(time.time()) + 3600
        write_json(window_path, expired)
        goal_path.write_bytes(paused_bytes)
        verifying_goal_bytes = goal_path.read_bytes()
        goal_path.write_text(
            verifying_goal_bytes.decode("utf-8").replace(
                "status: verifying", "status: blocked", 1,
            ),
            encoding="utf-8",
        )
        forged_terminal = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        goal_path.write_bytes(verifying_goal_bytes)
        reconcile = runpy.run_path(str(SOURCE / "scripts/project-reconcile.py"))
        reconcile["transition_goal"](
            fixture.root, "chiron", str(promoted["goal"]["id"]),
            "verifying", "blocked", "verifier-disagreement",
        )
        terminal_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        return (
            contract["source_head"] == source_head
            and contract["authority_contract"]["remote_head"] == bound_remote
            and pin["source_head"] == source_head
            and pin["remote_head"] == bound_remote
            and pin_unavailable == 74
            and other_project_result.returncode == 0
            and json.loads(other_project_result.stdout)["source_head"] == source_head
            and mismatch_result.returncode == 4
            and "does not match its approved plan" in mismatch_result.stderr
            and verifying_pin["source_head"] == source_head
            and paused_pin["source_head"] == source_head
            and competing_result.returncode == 4
            and "exactly one armed/open project window" in competing_result.stderr
            and expired_result.returncode == 0
            and json.loads(expired_result.stdout)["source_head"] == "-"
            and forged_terminal.returncode == 4
            and "terminal source-pin" in forged_terminal.stderr
            and terminal_result.returncode == 0
            and json.loads(terminal_result.stdout)["source_head"] == "-"
            and git_output(remote, "rev-parse", "refs/heads/main") == current_remote
            and git_output(fixture.repo, "rev-parse", "refs/heads/main") == source_head
            and not git_output(fixture.repo, "status", "--porcelain", "--untracked-files=all")
        )
    finally:
        fixture.close()


def test_source_fast_forward_before_window_commit_fails_closed() -> bool:
    """The locked arm precondition must catch resync winning the race first."""
    fixture = Fixture()
    window_id = "chiron-window-source-race"
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        _, source_head, remote_head = install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="arm-source-race")
        goal_id = str(promoted["goal"]["id"])
        if propose(fixture, promoted, "451").returncode or approve(
            fixture, str(promoted["id"]), goal_id, "452",
        ).returncode:
            return False

        instruction_id = "453"
        body = (
            f"Open pilot window {window_id} for chiron, goal {goal_id}, "
            "for 900 seconds."
        )
        fixture._write_instruction(instruction_id, "head-hermes", body)
        instruction_path = fixture.root / f"state/instructions/{int(instruction_id):08d}.md"
        decision_path = fixture.decision(
            verb="pilot-window-open",
            args=["chiron", goal_id, window_id, "900"],
            iid=instruction_id,
            actor="head-hermes",
            goal=goal_id,
            text="Authorize only the exact source-race control window.",
        )
        (fixture.root / "state/PAUSE").write_text("phase8-preflight\n", encoding="utf-8")
        cfg, pilot, _ = PILOT["records"](fixture.root, "chiron", active=True)
        window_action = PILOT["window_action"]
        globals_ = window_action.__globals__
        original_commit = globals_["commit_pilot_transition"]
        moved = False

        def move_source_then_commit(*args, **kwargs):
            nonlocal moved
            subprocess.run(
                ["git", "-C", str(fixture.repo), "reset", "--hard", remote_head],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
            )
            moved = True
            return original_commit(*args, **kwargs)

        globals_["commit_pilot_transition"] = move_source_then_commit
        result_code = 0
        try:
            window_action(
                fixture.root, cfg, pilot,
                json.loads(decision_path.read_text(encoding="utf-8")), instruction_id,
                instruction_path, fields(instruction_path),
            )
        except SystemExit as exc:
            result_code = int(exc.code)
        finally:
            globals_["commit_pilot_transition"] = original_commit

        window_path = fixture.root / f"state/pilot-windows/{window_id}.json"
        events_path = fixture.root / "state/events.jsonl"
        events = events_path.read_text(encoding="utf-8") if events_path.is_file() else ""
        return (
            source_head == installed["live_head"]
            and moved
            and result_code != 0
            and git_output(fixture.repo, "rev-parse", "HEAD") == remote_head
            and not window_path.exists()
            and "pilot-window-armed" not in events
        )
    finally:
        fixture.close()


def test_window_lock_contention_defers_exact_action() -> bool:
    fixture = Fixture()
    window_id = "chiron-window-lock-contention"
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="lock-contention")
        goal_id = str(promoted["goal"]["id"])
        if propose(fixture, promoted, "454").returncode or approve(
            fixture, str(promoted["id"]), goal_id, "455",
        ).returncode:
            return False
        instruction_id = "456"
        fixture._write_instruction(
            instruction_id, "head-hermes",
            f"Open pilot window {window_id} for chiron, goal {goal_id}, for 900 seconds.",
        )
        decision = fixture.decision(
            verb="pilot-window-open",
            args=["chiron", goal_id, window_id, "900"],
            iid=instruction_id,
            actor="head-hermes",
            goal=goal_id,
            text="Authorize only the exact lock-contention control window.",
        )
        (fixture.root / "state/PAUSE").write_text("phase8-preflight\n", encoding="utf-8")
        with PILOT["phase8_lock"](fixture.root, "window-chiron"):
            state_before = byte_tree_fingerprint(fixture.root / "state")
            result = fixture.run("python3", "scripts/project-pilot.py", "execute", str(decision))
            state_after = byte_tree_fingerprint(fixture.root / "state")
        return (
            result.returncode == 75
            and "state lock is contended" in result.stderr
            and state_after == state_before
            and not (fixture.root / f"state/pilot-windows/{window_id}.json").exists()
        )
    finally:
        fixture.close()


def test_source_pin_window_inventory_is_bounded_and_fail_closed() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        _, _, _ = install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="window-inventory")
        if propose(fixture, promoted, "449").returncode or approve(
            fixture, str(promoted["id"]), str(promoted["goal"]["id"]), "450",
        ).returncode:
            return False
        record = json.loads(
            (fixture.root / f"state/plans/chiron/{promoted['id']}.json").read_text(
                encoding="utf-8"
            )
        )
        window_path = fixture.root / "state/pilot-windows/chiron-window-inventory.json"
        write_json(
            window_path,
            {
                "schema_version": 1, "id": window_path.stem, "project_id": "chiron",
                "pilot_id": "pilot-chiron", "goal_id": promoted["goal"]["id"],
                "plan_id": promoted["id"], "plan_digest": record["plan_digest"],
                "status": "armed", "expires_at_epoch": int(time.time()) + 3600,
            },
        )
        link = fixture.root / "state/pilot-windows/symlink-window.json"
        link.symlink_to(window_path)
        symlinked = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        link.unlink()
        original_read_text = Path.read_text

        def deny_window(self, *args, **kwargs):
            if self == window_path:
                raise PermissionError("simulated transient window record read failure")
            return original_read_text(self, *args, **kwargs)

        transient_code = 0
        Path.read_text = deny_window
        try:
            PILOT["active_source_pin"](fixture.root, "chiron")
        except SystemExit as exc:
            transient_code = int(exc.code)
        finally:
            Path.read_text = original_read_text
        malformed = fixture.root / "state/pilot-windows/unattributable.json"
        malformed.write_text("{malformed\n", encoding="utf-8")
        malformed_result = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        malformed.unlink()
        invalid = json.loads(window_path.read_text(encoding="utf-8"))
        invalid["expires_at_epoch"] = "never"
        write_json(window_path, invalid)
        contradictory = fixture.run(
            "python3", "scripts/project-pilot.py", "active-source-pin", "chiron",
        )
        return (
            symlinked.returncode == 74
            and "symlink" in symlinked.stderr
            and transient_code == 74
            and malformed_result.returncode == 4
            and "cannot read validated state" in malformed_result.stderr
            and contradictory.returncode == 4
            and "invalid expiry" in contradictory.stderr
        )
    finally:
        fixture.close()


def test_named_remote_resolution_and_credential_symlink_fail_closed() -> bool:
    named = Fixture()
    credential = Fixture()
    try:
        configure_historical_profile(named)
        named_install = install_promotion(named)
        remote, _, _ = install_descendant_bare_remote(named)
        subprocess.run(
            ["git", "-C", str(named.repo), "remote", "add", "origin", str(remote)],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(named.repo), "config",
             "url.file:///definitely-absent/.insteadOf", str(remote)],
            check=True,
        )
        named_config_path = named.root / "state/project-config/chiron.json"
        named_config = json.loads(named_config_path.read_text(encoding="utf-8"))
        named_config["remote"] = "origin"
        write_json(named_config_path, named_config)
        named_plan = v3_plan(named, named_install["required"], suffix="named-remote")
        named_result = propose(named, named_plan, "445")

        configure_historical_profile(credential)
        credential_install = install_promotion(credential)
        key_target = credential.temp / "deploy-key-target"
        key_target.write_text("not-a-real-key\n", encoding="utf-8")
        key_link = credential.temp / "deploy-key-link"
        key_link.symlink_to(key_target)
        credential_config_path = credential.root / "state/project-config/chiron.json"
        credential_config = json.loads(credential_config_path.read_text(encoding="utf-8"))
        credential_config["remote"] = "ssh://git@example.invalid/chiron.git"
        credential_config["deploy_key_ref"] = str(key_link)
        write_json(credential_config_path, credential_config)
        credential_plan = v3_plan(
            credential, credential_install["required"], suffix="credential-symlink",
        )
        credential_result = propose(credential, credential_plan, "446")
        return (
            named_result.returncode == 0
            and credential_result.returncode == 74
            and "remote freshness credential is absent" in credential_result.stderr
            and not (
                credential.root / f"state/plans/chiron/{credential_plan['id']}.json"
            ).exists()
        )
    finally:
        named.close()
        credential.close()


def test_ambient_git_redirects_cannot_fabricate_authority() -> bool:
    fixture = Fixture()
    poisoned = {
        "GIT_DIR": str(fixture.temp / "fabricated.git"),
        "GIT_WORK_TREE": str(fixture.temp / "fabricated-worktree"),
        "GIT_OBJECT_DIRECTORY": str(fixture.temp / "fabricated-objects"),
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(fixture.temp / "fabricated-alternates"),
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "url.file:///definitely-absent/.insteadOf",
        "GIT_CONFIG_VALUE_0": str(fixture.temp),
        "GIT_SSH_COMMAND": "false",
        "GIT_ASKPASS": "false",
        "SSH_ASKPASS": "false",
        "TEMP": str(fixture.repo),
        "TMP": str(fixture.repo),
        "TMPDIR": str(fixture.repo),
    }
    prior = {key: os.environ.get(key) for key in poisoned}
    try:
        configure_historical_profile(fixture)
        install_promotion(fixture)
        remote, source_head, remote_head = install_descendant_bare_remote(fixture)
        config = json.loads(
            (fixture.root / "state/project-config/chiron.json").read_text(encoding="utf-8")
        )
        authority = runpy.run_path(str(SOURCE / "scripts/project_authority.py"))
        nested = fixture.repo / "not-a-project-checkout"
        nested.mkdir()
        nested_config = dict(config)
        nested_config["repo"] = str(nested)
        nested_refused = False
        try:
            authority["observe_clean_source"](nested_config)
        except authority["AuthorityError"] as exc:
            nested_refused = exc.code == 74 and "root marker" in str(exc)
        finally:
            nested.rmdir()
        _, windows_protocol, windows_env = authority["_remote_access"](
            {"remote": r"C:\authority\repository.git"}, fixture.repo,
        )
        os.environ.update(poisoned)
        current, relationship = authority["prove_current_remote_lineage"](
            config, source_head,
        )
        for key, value in prior.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        return (
            current == remote_head
            and relationship == AUTHORITY_V2_RELATIONSHIP
            and nested_refused
            and windows_protocol == "file"
            and "GIT_SSH_COMMAND" not in windows_env
            and git_output(remote, "rev-parse", "refs/heads/main") == remote_head
            and git_output(fixture.repo, "rev-parse", "refs/heads/main") == source_head
            and not git_output(
                fixture.repo, "status", "--porcelain", "--untracked-files=all",
            )
        )
    finally:
        for key, value in prior.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        fixture.close()


def test_scratch_ancestor_git_config_cannot_redirect_remote_authority() -> bool:
    fixture = Fixture()
    module_globals: dict | None = None
    original_scratch_parent = None
    original_git_env = None
    try:
        configure_historical_profile(fixture)
        install_promotion(fixture)
        real_remote, source_head, remote_head = install_descendant_bare_remote(fixture)
        attacker_remote = fixture.temp / "attacker-authority.git"
        subprocess.run(
            ["git", "clone", "-q", "--bare", str(fixture.repo), str(attacker_remote)],
            check=True,
        )
        ancestor = fixture.temp / "scratch-ancestor"
        scratch_root = ancestor / "scratch-root"
        scratch_root.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(ancestor)], check=True)
        subprocess.run(
            ["git", "-C", str(ancestor), "config", "--local",
             f"url.{attacker_remote}.insteadOf", str(real_remote)],
            check=True,
        )
        config = json.loads(
            (fixture.root / "state/project-config/chiron.json").read_text(encoding="utf-8")
        )
        authority = runpy.run_path(str(SOURCE / "scripts/project_authority.py"))
        module_globals = authority["_authenticated_remote_observation"].__globals__
        original_scratch_parent = module_globals["_scratch_parent"]
        original_git_env = module_globals["_git_env"]
        scratch_calls: list[Path] = []

        def controlled_scratch_parent() -> Path:
            scratch_calls.append(scratch_root)
            return scratch_root

        def without_ceiling(*, ceiling=None):
            isolated = original_git_env(ceiling=ceiling)
            isolated.pop("GIT_CEILING_DIRECTORIES", None)
            return isolated

        module_globals["_scratch_parent"] = controlled_scratch_parent
        module_globals["_git_env"] = without_ceiling
        redirected, _, _, _ = authority["_authenticated_remote_observation"](config, "main")
        module_globals["_git_env"] = original_git_env
        observed, _, _, _ = authority["_authenticated_remote_observation"](config, "main")
        return (
            redirected == source_head
            and observed == remote_head
            and observed != source_head
            and len(scratch_calls) == 2
            and git_output(attacker_remote, "rev-parse", "refs/heads/main") == source_head
        )
    finally:
        if module_globals is not None:
            if original_scratch_parent is not None:
                module_globals["_scratch_parent"] = original_scratch_parent
            if original_git_env is not None:
                module_globals["_git_env"] = original_git_env
        fixture.close()


def test_authenticated_graph_is_complete_without_lazy_fetch() -> bool:
    fixture = Fixture()
    try:
        configure_historical_profile(fixture)
        install_promotion(fixture)
        remote, _, remote_head = install_descendant_bare_remote(fixture)
        config = json.loads(
            (fixture.root / "state/project-config/chiron.json").read_text(encoding="utf-8")
        )
        authority = runpy.run_path(str(SOURCE / "scripts/project_authority.py"))
        observed, transport, protocol, env = authority["_authenticated_remote_observation"](
            config, "main",
        )
        proof = fixture.temp / "complete-authority-proof.git"
        subprocess.run(
            ["git", "init", "--bare", "--quiet", str(proof)], check=True,
        )
        authority["_fetch_authority_graph"](
            proof, "main", observed, transport, protocol, env,
        )
        blob = git_output(
            remote, "rev-parse", "refs/heads/main:user-client/render/remote-descendant.js",
        )
        offline = fixture.temp / "authenticated-remote.offline"
        remote.rename(offline)
        materialized = subprocess.run(
            ["git", "-C", str(proof), "cat-file", "-e", f"{blob}^{{blob}}"],
            stdin=subprocess.DEVNULL, text=True, capture_output=True, check=False,
        )
        local_config = subprocess.run(
            ["git", "-C", str(proof), "config", "--local", "--list"],
            stdin=subprocess.DEVNULL, text=True, capture_output=True, check=True,
        ).stdout.lower()
        promisor_markers = list((proof / "objects/pack").glob("*.promisor"))
        return (
            observed == remote_head
            and materialized.returncode == 0
            and "promisor" not in local_config
            and "partialclone" not in local_config
            and not promisor_markers
        )
    finally:
        fixture.close()


def test_malformed_or_mutated_promoted_authority_fails_closed() -> bool:
    malformed = Fixture()
    try:
        configure_historical_profile(malformed)
        installed = install_promotion(malformed)
        install_descendant_bare_remote(malformed)
        malformed_plan = v3_plan(malformed, installed["required"], suffix="malformed-authority")
        malformed_plan["authority_contract"] = {
            "schema": AUTHORITY_V2_SCHEMA,
            "source_head": installed["live_head"],
        }
        malformed_result = propose(malformed, malformed_plan, "451")
        if malformed_result.returncode == 0 or (
            malformed.root / f"state/plans/chiron/{malformed_plan['id']}.json"
        ).exists():
            return False
    finally:
        malformed.close()

    for index, (field, value) in enumerate((
        ("schema", "recursion-project-authority-contract/v1"),
        ("remote_relationship", "equal"),
        ("remote_relationship", "source-descends-from-remote"),
        ("remote_head", "not-an-object-id"),
    ), start=1):
        fixture = Fixture()
        try:
            configure_historical_profile(fixture)
            installed = install_promotion(fixture)
            install_descendant_bare_remote(fixture)
            promoted = v3_plan(fixture, installed["required"], suffix=f"authority-mutation-{index}")
            if propose(fixture, promoted, f"45{index + 1}").returncode:
                return False
            record_path = fixture.root / f"state/plans/chiron/{promoted['id']}.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["plan"]["authority_contract"][field] = value
            record["plan_digest"] = canonical_digest(record["plan"])
            write_json(record_path, record)
            result = approve(
                fixture, str(promoted["id"]), str(promoted["goal"]["id"]), f"46{index}",
            )
            if result.returncode == 0:
                return False
        finally:
            fixture.close()
    return True


def test_authority_record_io_is_typed_without_mutation() -> bool:
    fixture = Fixture()
    original_read_text = Path.read_text
    try:
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="typed-record-io")
        if propose(fixture, promoted, "471").returncode or approve(
            fixture, str(promoted["id"]), str(promoted["goal"]["id"]), "472",
        ).returncode:
            return False
        targets = (
            fixture.root / "state/project-config/chiron.json",
            fixture.root / "state/pilots/pilot-chiron.json",
            fixture.root / f"state/plans/chiron/{promoted['id']}.json",
            fixture.root / f"state/goals/{promoted['goal']['id']}.md",
            fixture.root / f"state/tasks/{promoted['tasks'][0]['id']}.md",
        )
        state_before = byte_tree_fingerprint(fixture.root / "state")
        observed: list[tuple[int, int, int, int]] = []
        verify = PILOT["verify_approved_goal"]
        for target in targets:
            exact = target.read_bytes()
            exact_mode = target.stat().st_mode & 0o777

            def denied(self, *args, **kwargs):
                if self == target:
                    raise PermissionError("simulated transient authority read failure")
                return original_read_text(self, *args, **kwargs)

            Path.read_text = denied
            unavailable = 0
            try:
                verify(
                    fixture.root, "chiron", str(promoted["goal"]["id"]),
                    check_remote=True,
                )
            except SystemExit as exc:
                unavailable = int(exc.code)
            local_unavailable = 0
            try:
                verify(
                    fixture.root, "chiron", str(promoted["goal"]["id"]),
                    state_unavailable_code=74,
                )
            except SystemExit as exc:
                local_unavailable = int(exc.code)
            finally:
                Path.read_text = original_read_text

            target.write_text("[]\n", encoding="utf-8")
            malformed = 0
            try:
                verify(
                    fixture.root, "chiron", str(promoted["goal"]["id"]),
                    check_remote=True,
                )
            except SystemExit as exc:
                malformed = int(exc.code)
            target.unlink()
            absent = 0
            try:
                verify(
                    fixture.root, "chiron", str(promoted["goal"]["id"]),
                    check_remote=True,
                )
            except SystemExit as exc:
                absent = int(exc.code)
            target.write_bytes(exact)
            target.chmod(exact_mode)
            observed.append((unavailable, local_unavailable, malformed, absent))
        state_after = byte_tree_fingerprint(fixture.root / "state")
        if observed != [(74, 74, 4, 4)] * len(targets) or state_after != state_before:
            changed = sorted(
                path for path in set(state_before) | set(state_after)
                if state_before.get(path) != state_after.get(path)
            )
            print(f"typed-record-io diag observed={observed} changed={changed}")
            return False
        return True
    finally:
        Path.read_text = original_read_text
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


def test_transport_classifier_and_git_floor_fail_closed() -> bool:
    fixture = Fixture()
    original_path = os.environ.get("PATH", "")
    try:
        classify = AUTHORITY["_transport_shape"]
        valid = {
            "../relative.git": "file",
            str(fixture.temp / "absolute.git"): "file",
            "file:///var/tmp/fixture.git": "file",
            "https://example.invalid/repo.git": "https",
            "ssh://git@example.invalid/repo.git": "ssh",
            "git@example.invalid:repo.git": "ssh",
            "example.invalid:repo.git": "ssh",
            "Z:/fixture/repo.git": "file",
        }
        if any(classify(value, fixture.repo)[1] != protocol
               for value, protocol in valid.items()):
            return False
        invalid = (
            "ext::bash", "transport::helper", "git://example.invalid/repo.git",
            "http://example.invalid/repo.git", "https://[::1",
            "https:///missing-host.git", "ssh:///missing-host.git",
            "file://remote-host/share/repo.git", "https://user:secret@example.invalid/repo.git",
            "https://example.invalid/repo.git?redirect=yes", "bad\0transport",
        )
        for value in invalid:
            try:
                classify(value, fixture.repo)
            except AuthorityError as exc:
                if exc.code != 4:
                    return False
            else:
                return False

        real_git = shutil.which("git")
        if not real_git:
            return False
        wrapper_dir = fixture.temp / "old-git"
        wrapper_dir.mkdir()
        wrapper = wrapper_dir / "git"
        wrapper.write_text(
            "#!/usr/bin/env bash\n"
            "if [ \"${1:-}\" = --version ]; then echo 'git version 2.35.1'; exit 0; fi\n"
            f"exec {json.dumps(real_git)} \"$@\"\n",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)
        os.environ["PATH"] = str(wrapper_dir) + os.pathsep + original_path
        try:
            AUTHORITY["_require_git_version"]()
        except AuthorityError as exc:
            return exc.code == 74
        return False
    finally:
        os.environ["PATH"] = original_path
        fixture.close()


def test_sha256_authority_uses_matching_disposable_object_format() -> bool:
    fixture = Fixture()
    try:
        shutil.rmtree(fixture.repo / ".git")
        initialized = subprocess.run(
            ["git", "init", "-q", "--object-format=sha256", str(fixture.repo)],
            text=True, capture_output=True, check=False,
        )
        if initialized.returncode:
            return False
        subprocess.run(
            ["git", "-C", str(fixture.repo), "config", "user.name", "Phase 8 Test"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(fixture.repo), "config", "user.email", "phase8@example.invalid"],
            check=True,
        )
        subprocess.run(["git", "-C", str(fixture.repo), "add", "."], check=True)
        subprocess.run(
            ["git", "-C", str(fixture.repo), "commit", "-qm", "sha256 fixture"], check=True,
        )
        subprocess.run(["git", "-C", str(fixture.repo), "branch", "-M", "main"], check=True)
        configure_historical_profile(fixture)
        installed = install_promotion(fixture)
        _, source_head, remote_head = install_descendant_bare_remote(fixture)
        promoted = v3_plan(fixture, installed["required"], suffix="sha256-authority")
        result = propose(fixture, promoted, "455")
        if result.returncode:
            return False
        record = json.loads(
            (fixture.root / f"state/plans/chiron/{promoted['id']}.json").read_text(
                encoding="utf-8",
            )
        )
        authority = record["plan"]["authority_contract"]
        return (
            len(source_head) == len(remote_head) == 64
            and authority["source_head"] == source_head
            and authority["remote_head"] == remote_head
            and authority["remote_relationship"] == AUTHORITY_V2_RELATIONSHIP
            and not git_output(
                fixture.repo, "status", "--porcelain", "--untracked-files=all",
            )
        )
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
            "a promoted plan binds explicit v2 authority while an authenticated bare remote is ahead",
            test_promoted_descendant_remote_binds_explicit_v2_authority,
        ),
        (
            "selector-less historical authority still requires exact local and remote tips",
            test_selectorless_legacy_authority_remains_exact_tip_only,
        ),
        (
            "promoted authority rejects divergence and proves missing objects in read-only scratch",
            test_promoted_remote_divergence_fails_and_missing_object_uses_read_only_scratch,
        ),
        (
            "promoted authority rejects an authenticated remote rollback",
            test_promoted_remote_rollback_fails_closed,
        ),
        (
            "remote proof unavailability returns 74 without mutating controller or source state",
            test_remote_proof_unavailability_is_typed_and_state_preserving,
        ),
        (
            "proved tracked or untracked repository dirt remains a hard authority failure",
            test_proved_repository_dirt_is_invalid_not_unavailable,
        ),
        (
            "an empty authenticated remote defers instead of terminally declaring stale authority",
            test_empty_authenticated_remote_is_unavailable_not_stale,
        ),
        (
            "later authenticated descendants preserve approval and export the exact source pin",
            test_promoted_remote_advancement_approves_and_exports_exact_source_pin,
        ),
        (
            "a source fast-forward before the arm commit cannot create a stale window",
            test_source_fast_forward_before_window_commit_fails_closed,
        ),
        (
            "shared source-window lock contention defers the exact human action",
            test_window_lock_contention_defers_exact_action,
        ),
        (
            "source-pin window inventory rejects symlinks, unreadable ownership, and contradictions",
            test_source_pin_window_inventory_is_bounded_and_fail_closed,
        ),
        (
            "named remotes resolve in-project while symlinked SSH credentials fail closed",
            test_named_remote_resolution_and_credential_symlink_fail_closed,
        ),
        (
            "ambient Git redirects cannot fabricate local or authenticated remote authority",
            test_ambient_git_redirects_cannot_fabricate_authority,
        ),
        (
            "a scratch ancestor repository cannot redirect authenticated authority",
            test_scratch_ancestor_git_config_cannot_redirect_remote_authority,
        ),
        (
            "authenticated authority materializes a complete graph without lazy fetch",
            test_authenticated_graph_is_complete_without_lazy_fetch,
        ),
        (
            "transport parsing and the isolated Git version floor fail closed before evidence",
            test_transport_classifier_and_git_floor_fail_closed,
        ),
        (
            "SHA-256 authority uses a matching disposable proof object format",
            test_sha256_authority_uses_matching_disposable_object_format,
        ),
        (
            "malformed, schema-mutated, and relationship-mutated v2 authority fails closed",
            test_malformed_or_mutated_promoted_authority_fails_closed,
        ),
        (
            "authority record I/O defers while absence and malformed bytes stay invalid",
            test_authority_record_io_is_typed_without_mutation,
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
