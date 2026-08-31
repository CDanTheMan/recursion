import copy
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import mvp_kernel as k
from execution_fabric import digest_record


def signed(body, field):
    body = dict(body)
    unsigned = dict(body)
    unsigned.pop(field, None)
    body[field] = digest_record(unsigned)
    return body


def records(depth=0):
    task = signed({"id": "task-root", "depth": depth, "project_id": "project-a", "parent_goal": "goal-a", "source_repository": "repo", "source_branch": "main", "source_sha": "a" * 40, "allowed_paths": ["scripts"], "requested_capabilities": ["read"], "parent_task_id": None, "parent_task_digest": None}, "task_digest")
    assignment = signed({"id": "assignment-a", "task_id": task["id"], "source_sha": task["source_sha"]}, "assignment_digest")
    budget = signed({"id": "budget-a", "task_id": task["id"], "task_digest": task["task_digest"], "token_limit": 100}, "budget_digest")
    grant = signed({"id": "grant-a", "task_id": task["id"], "task_digest": task["task_digest"], "capabilities": ["read"], "allowed_paths": ["scripts"]}, "grant_digest")
    return task, assignment, budget, grant


def packet():
    t, a, b, g = records()
    return k.build_packet(task=t, assignment=a, budget=b, grant=g, supervisor_digest="b" * 64,
                         evidence_refs=[{"id": "ev-a", "sha256": "c" * 64}])


def test_deterministic_and_mutation_isolated():
    p = packet()
    assert p.packet_digest == k.build_packet(**{"task": records()[0], "assignment": records()[1], "budget": records()[2], "grant": records()[3], "supervisor_digest": "b" * 64, "evidence_refs": [{"id": "ev-a", "sha256": "c" * 64}]}).packet_digest
    with pytest.raises(TypeError):
        p.value["depth"] = 9
    d = p.to_dict(); d["task"]["id"] = "changed"
    assert p["task"]["id"] == "task-root"


def test_rejects_bad_evidence_secret_unknown_nonfinite_and_pause():
    t, a, b, g = records()
    with pytest.raises(k.KernelError):
        k.build_packet(task=t, assignment=a, budget=b, grant=g, supervisor_digest="b" * 64, evidence_refs=[{"id": "ev", "sha256": "x"}])
    with pytest.raises(k.KernelError):
        k.build_packet(task=t, assignment=a, budget=b, grant=g, supervisor_digest="b" * 64, context=[{"summary": "private chain of thought"}])
    with pytest.raises(k.KernelError):
        k.build_packet(task=t, assignment=a, budget=b, grant=g, supervisor_digest="b" * 64, pause=True)
    with pytest.raises(k.KernelError):
        k.validate_packet(packet(), pause_observed=True)


def test_retention_mandatory_then_priority_and_overflow():
    p = packet()
    kept = k.retain_context(p, [{"id": "low", "summary": "low", "priority": 1}, {"id": "must", "summary": "must", "priority": 0, "mandatory": True}, {"id": "high", "summary": "high", "priority": 4}])
    assert [x["id"] for x in kept["context"]] == ["must", "high", "low"]
    with pytest.raises(k.KernelError):
        k.retain_context(p, [{"summary": "x" * 100, "mandatory": True}], limits=k.KernelLimits(max_tokens=1))


def test_child_depth_and_parent_binding():
    p = packet(); t, a, b, g = records()
    child = dict(t); child.update(depth=1, parent_task_id=t["id"], parent_task_digest=t["task_digest"], id="task-child")
    child["task_digest"] = digest_record({x: y for x, y in child.items() if x != "task_digest"})
    with pytest.raises(k.KernelError):
        k.spawn_child(p, task=child, assignment=a, budget=b, grant=g)


def test_import_is_inert():
    code = "import sys; sys.path.insert(0, 'scripts'); import mvp_kernel"
    result = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0 and result.stdout == "" and result.stderr == ""
