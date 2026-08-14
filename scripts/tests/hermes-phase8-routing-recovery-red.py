#!/usr/bin/env python3
"""Hermetic routing/admission/recovery controls for the Phase-8 incident."""

from __future__ import annotations

import hashlib
import json
import os
import signal
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[2]
PROJECT = "golden-stallion-client"
PILOT = "pilot-golden-stallion-client"
DIRECT = "lucas-direct:telegram:8913126684"

ACTION_707_FIRST = (
    '{"action_payload_sha256":"2938c7242e7a5f66f06e0703dba76ff1c2556212c36b306984c22585719a9b7e",'
    '"actor":"head-hermes","arguments":[],"attempts":1,"created_at":"2026-08-13T22:12:14Z",'
    '"decision_id":"decision-16801468efbb3ed54a15dcaa","decision_source":"hermes-model",'
    '"event_seq":3,"goal_id":"goal-gsc-0x6c-shadetops-underemission-v2",'
    '"id":"action-bb38398a6e0e3859a1a7d263",'
    '"idempotency_key":"decision:14c7d1bfbc72337c5559a9fcef2a2c807c13671e5dd1822765c14742092b0ee2",'
    '"instruction_id":"707","last_transition_id":"transition-a02ec80d32bb3c84cee9069ce753c46b",'
    '"lease_expires":null,"lease_owner":null,"project":"golden-stallion-client",'
    '"result_evidence":"log=/opt/recursion/loop/logs/2026-08-13-conduct-hermes.log rc=4 | '
    'cannot-bind noop evidence is absent","routed_decider":"head-hermes","schema_version":1,'
    '"status":"failed","updated_at":"2026-08-13T22:12:16Z","verb":"noop"}\n'
)
ACTION_707_SECOND = (
    '{"action_payload_sha256":"04e5f422ed703b4f847fdfb221dae4b792fcc047d655d45c80687fd26c3b18fe",'
    '"actor":"head-hermes","arguments":[],"attempts":1,"created_at":"2026-08-13T22:17:08Z",'
    '"decision_id":"decision-af1cc1dad357bd728b6929ba","decision_source":"hermes-model",'
    '"event_seq":3,"goal_id":"goal-gsc-0x6c-shadetops-underemission-v2",'
    '"id":"action-4a90005df9c9dfe6cbb7fbad",'
    '"idempotency_key":"decision:72ad3205d17e5c2dbbdbcda94dc75db8ed253def295fa0b7d544e7b8106ad7d9",'
    '"instruction_id":"707","last_transition_id":"transition-b2852e1f57bc23c4ad74d4fe9b76abf9",'
    '"lease_expires":null,"lease_owner":null,"project":"golden-stallion-client",'
    '"result_evidence":"log=/opt/recursion/loop/logs/2026-08-13-conduct-hermes.log rc=4 | '
    'cannot-bind noop evidence is absent","routed_decider":"head-hermes","schema_version":1,'
    '"status":"failed","updated_at":"2026-08-13T22:17:10Z","verb":"noop"}\n'
)
INSTRUCTION_707 = """schema_version: 1
id: 707
received: 2026-08-13T22:07:26Z
principal: 8913126684
topic: 6
project_id: golden-stallion-client
pilot_id: pilot-golden-stallion-client
pilot_memory_key: telegram-topic:6
routing_target: head-hermes
reply_correlation: telegram:-1003894008732:6:707
deduplication_key: telegram:-1003894008732:6:707
from: 8913126684
chat: -1003894008732
thread: 6
project: golden-stallion-client
status: open
action_ids: action-4a90005df9c9dfe6cbb7fbad

## INSTRUCTION
Propose a fresh offline golden-stallion-client pilot plan to reduce the verified 0x6c shade-tops under-emission in user-client/render, using new v2 plan, goal, and task identities and the deployed required seed, scope, provider, and forced-on gate contracts. Do not reuse or edit the closed v1 plan, goal, task, or window.


## CONSUMED 2026-08-13T22:12:15Z
resulting actions: action-bb38398a6e0e3859a1a7d263

## OPEN 2026-08-13T22:12:16Z
deferred/failed actions reopened instruction: action-bb38398a6e0e3859a1a7d263 | last failure: log=/opt/recursion/loop/logs/2026-08-13-conduct-hermes.log rc=4 | cannot-bind noop evidence is absent

## CONSUMED 2026-08-13T22:17:09Z
resulting actions: action-4a90005df9c9dfe6cbb7fbad

## OPEN 2026-08-13T22:17:10Z
deferred/failed actions reopened instruction: action-4a90005df9c9dfe6cbb7fbad | last failure: log=/opt/recursion/loop/logs/2026-08-13-conduct-hermes.log rc=4 | cannot-bind noop evidence is absent
"""
INSTRUCTION_732 = """schema_version: 1
id: 732
received: 2026-08-13T22:11:01Z
principal: 8913126684
topic: 6
project_id: golden-stallion-client
pilot_id: pilot-golden-stallion-client
pilot_memory_key: telegram-topic:6
routing_target: pilot-golden-stallion-client
reply_correlation: telegram:-1003894008732:6:732
deduplication_key: telegram:-1003894008732:6:732
from: 8913126684
chat: -1003894008732
thread: 6
project: golden-stallion-client
status: open
action_ids: 

## INSTRUCTION
Authorize one Head Hermes turn to escalate instruction 707 as a routing blocker.
"""


def fields(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            break
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def json_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class Fixture:
    def __init__(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="phase8-routing-recovery-"))
        self.root = self.temp / "root"
        self.root.mkdir()
        shutil.copytree(SOURCE / "scripts", self.root / "scripts")
        shutil.copytree(SOURCE / "schemas", self.root / "schemas")
        for relative in (
            "state/instructions", "state/actions", "state/project-config", "state/pilots",
            "state/decision-queue/pending", "state/decision-queue/running",
            "state/decision-queue/succeeded", "state/decision-queue/failed",
            "state/notification-events", "state/deliveries", "state/transport-evidence",
            "state/recovery", "state/.locks", "state/tasks", "state/goals", "state/plans",
            "state/pilot-windows", "state/reports", "loop/logs", "bin",
        ):
            (self.root / relative).mkdir(parents=True, exist_ok=True)
        (self.root / ".env").write_text("", encoding="utf-8")
        (self.root / "CONTROL_PLANE.md").write_text("fixture authority\n", encoding="utf-8")
        (self.root / "ANCHOR.md").write_text("fixture scope\n", encoding="utf-8")
        (self.root / "state/DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
        (self.root / "state/PAUSE").write_text("fixture pause\n", encoding="utf-8")
        (self.root / "state/portfolio.tsv").write_text(
            "#project\tpath\tremote\tbranch\tsshkey\troadmap\ttopic\tstatus\n"
            f"{PROJECT}\t/opt/golden-stallion-client\tgit@example/repo\tmain\t-\t-\t6\tactive\n",
            encoding="utf-8",
        )
        targets = [
            "project-topic:telegram:-1003894008732:6",
            "head-hermes:telegram:-1003894008732:1",
            DIRECT,
        ]
        self.write_json("state/project-config/golden-stallion-client.json", {
            "schema_version": 1, "id": PROJECT, "repo": "/opt/golden-stallion-client",
            "remote": "origin", "default_branch": "main", "deploy_key_ref": "-",
            "charter": "routing fixture", "allowed_paths": ["user-client/render"], "topic": 6,
            "pilot_id": PILOT, "activation_gate": "fixture", "notification_targets": targets,
            "goal_source": "state/goals", "status": "active",
        })
        self.write_json("state/pilots/pilot-golden-stallion-client.json", {
            "schema_version": 1, "id": PILOT, "project_id": PROJECT, "topic": 6,
            "charter": "routing fixture", "model_policy": "project-pilot", "concurrency_limit": 0,
            "budget": {"max_inflight_workers": 0}, "notification_targets": targets,
            "goal_source": "state/goals", "memory_key": "telegram-topic:6",
            "worktree_root": ".worktrees/gsc", "status": "active",
        })
        (self.root / "state/instructions/00000707.md").write_text(INSTRUCTION_707, encoding="utf-8", newline="\n")
        (self.root / "state/instructions/00000732.md").write_text(INSTRUCTION_732, encoding="utf-8", newline="\n")
        retained = (
            "schema_version: 1\nid: 618\nprincipal: 8913126684\nstatus: acknowledged\n"
            "action_ids: action-retained\n\n## INSTRUCTION\nRetained incident evidence.\n"
        )
        (self.root / "state/instructions/00000618.md").write_text(retained, encoding="utf-8", newline="\n")
        self.retained_618 = hashlib.sha256(retained.encode()).hexdigest()
        self.write_exact_action("action-bb38398a6e0e3859a1a7d263", ACTION_707_FIRST,
                                "6572b4c5115f499258da36663c9c5a697a9a41049758a53cb080a65c35243db7")
        self.write_exact_action("action-4a90005df9c9dfe6cbb7fbad", ACTION_707_SECOND,
                                "b65903d93da048083a255ed647b9e226cc140ebf7cd672bcab3ecb4c62544db4")
        self.model_marker = self.temp / "model-called"
        hermes = self.root / "bin/hermes"
        hermes.write_text(
            "#!/usr/bin/env bash\nprintf called > \"$RECURSION_MODEL_MARKER\"\nexit 99\n",
            encoding="utf-8", newline="\n",
        )
        hermes.chmod(0o755)
        self.visible = self.temp / "visible.jsonl"
        transport = self.root / "bin/inert-telegram"
        transport.write_text(
            """#!/usr/bin/env python3
import json,os,sys
destination,message,delivery,event=sys.argv[1:5]
parts=destination.split(':'); chat=parts[2]; thread=parts[3] if len(parts)>3 else None
with open(os.environ['RECURSION_VISIBLE_LOG'],'a',encoding='utf-8') as out:
    out.write(json.dumps({'destination':destination,'delivery_id':delivery,'event_id':event})+'\\n')
print(json.dumps({'ok':True,'accepted':True,'transport':'telegram',
                  'message_id':'stub-'+delivery,'chat_id':chat,'thread_id':thread}))
""",
            encoding="utf-8", newline="\n",
        )
        transport.chmod(0o755)
        self.env = os.environ.copy()
        self.env.update({
            "RECURSION_ROOT": str(self.root), "RECURSION_INTAKE_ALLOW": "8913126684",
            "RECURSION_DECIDE_QUIET": "1", "RECURSION_NO_NOTIFY": "0",
            "RECURSION_MODEL_MARKER": str(self.model_marker),
            "RECURSION_NOTIFY_TRANSPORT": str(transport),
            "RECURSION_VISIBLE_LOG": str(self.visible),
            "RECURSION_CONTROL_LOCK_WAIT_S": "2",
            "PATH": str(self.root / "bin") + os.pathsep + self.env.get("PATH", ""),
        })

    def close(self) -> None:
        shutil.rmtree(self.temp, ignore_errors=True)

    def write_json(self, relative: str, value: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")

    def write_exact_action(self, action_id: str, content: str, digest: str) -> None:
        observed = hashlib.sha256(content.encode()).hexdigest()
        if observed != digest:
            raise AssertionError(f"fixture action digest mismatch {action_id}: {observed}")
        (self.root / "state/actions" / f"{action_id}.json").write_text(
            content, encoding="utf-8", newline="\n"
        )

    def run(self, command: list[str], *, extra: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = self.env.copy()
        if extra:
            env.update(extra)
        return subprocess.run(command, cwd=self.root, env=env, text=True, capture_output=True, check=False)

    def decide(self) -> subprocess.CompletedProcess[str]:
        return self.run(["bash", "scripts/hermes-decide.sh"])

    def drain(self, *, failpoint: str | None = None) -> subprocess.CompletedProcess[str]:
        extra = {"RECURSION_ROUTING_FAILPOINT": failpoint} if failpoint else None
        return self.run(["bash", "scripts/conduct-hermes.sh", "--paused-safe"], extra=extra)

    def queue(self, state: str, verb: str | None = None) -> list[tuple[Path, dict]]:
        result = []
        for path in sorted((self.root / "state/decision-queue" / state).glob("*.json")):
            value = json.loads(path.read_text(encoding="utf-8"))
            if verb is None or value.get("verb") == verb:
                result.append((path, value))
        return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    fixture = Fixture()
    try:
        # 732 is not independently recoverable: the reviewed ordering requires 707 first.
        blocked = fixture.run([
            "python3", "scripts/instruction_routing.py", "--root", str(fixture.root),
            "admit", "state/instructions/00000732.md", "--enqueue",
        ])
        require(blocked.returncode == 4 and not fixture.queue("pending"),
                f"732 ordering gate failed rc={blocked.returncode}: {blocked.stderr}")
        print("ok    732 recovery refuses until 707 has a succeeded coupled action")

        first = fixture.decide()
        replay = fixture.decide()
        pending = fixture.queue("pending", "routing-refuse")
        require(first.returncode == replay.returncode == 0 and len(pending) == 1,
                f"pre-model admission was not idempotent: {first.stderr} {replay.stderr}")
        require(not fixture.model_marker.exists(), "admission invoked the model")
        require(len(json_rows(fixture.root / "state/decisions.jsonl")) == 1,
                "admission duplicated the decision journal")
        print("ok    actor/verb mismatch queues one deterministic refusal with zero model calls")

        claim = fixture.run([
            "python3", "scripts/decision-queue.py", "claim-pending", "--kind", "non-work",
        ])
        running_path = claim.stdout.strip()
        require(claim.returncode == 0 and running_path, f"707 decision claim failed: {claim.stderr}")
        crash_env = fixture.env.copy()
        crash_env.update({"RECURSION_QUEUE_ACTUATION": "1", "RECURSION_ROUTING_FAILPOINT": "perform-hang"})
        process = subprocess.Popen(
            ["bash", "scripts/conduct-hermes.sh", "--file", running_path], cwd=fixture.root,
            env=crash_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True,
        )
        deadline = time.time() + 15
        while time.time() < deadline:
            action_rows = [json.loads(path.read_text(encoding="utf-8"))
                           for path in (fixture.root / "state/actions").glob("*.json")
                           if json.loads(path.read_text(encoding="utf-8")).get("verb") == "routing-refuse"]
            if action_rows and action_rows[0].get("status") == "running" \
                    and fields(fixture.root / "state/instructions/00000707.md")["status"] == "consumed":
                break
            time.sleep(0.05)
        else:
            os.killpg(process.pid, signal.SIGKILL)
            out, err = process.communicate()
            raise AssertionError(f"routing action never reached running/consumed: {out} {err}")
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        require(fields(fixture.root / "state/instructions/00000707.md")["status"] == "consumed",
                "hard crash did not preserve the consumed instruction")
        print("ok    hard crash leaves one running action for fresh-actuator recovery")

        completed = fixture.drain()
        require(completed.returncode == 0, f"707 recovery did not resume: {completed.stderr}")
        require(fields(fixture.root / "state/instructions/00000707.md")["status"] == "acknowledged",
                "707 did not close through acknowledgement")
        route_actions = [json.loads(path.read_text(encoding="utf-8"))
                         for path in (fixture.root / "state/actions").glob("*.json")
                         if json.loads(path.read_text(encoding="utf-8")).get("verb") == "routing-refuse"]
        require(len(route_actions) == 1 and route_actions[0].get("status") == "succeeded"
                and route_actions[0].get("attempts") == 1,
                "707 did not retain one replayed succeeded action")
        decision_707 = fixture.queue("succeeded", "routing-refuse")[0][0]
        action_replay = fixture.run(
            ["bash", "scripts/conduct-hermes.sh", "--file", str(decision_707)],
            extra={"RECURSION_QUEUE_ACTUATION": "1"},
        )
        require(action_replay.returncode == 0, f"succeeded action replay failed: {action_replay.stderr}")
        print("ok    707 terminalizes through one replay-safe succeeded coupled action")

        second = fixture.decide()
        require(second.returncode == 0 and len(fixture.queue("pending", "routing-refuse")) == 1,
                f"732 admission failed after 707: {second.stderr}")
        interrupted = fixture.drain(failpoint="after-event")
        require(interrupted.returncode == 74, f"routing tail failure was not preserved: {interrupted.stderr}")
        require(fields(fixture.root / "state/instructions/00000732.md")["status"] == "acknowledged",
                "durably succeeded recovery action did not acknowledge 732")
        require(len([row for row in json_rows(fixture.root / "state/events.jsonl")
                     if row.get("event") == "instruction-routing-refused"]) == 2,
                "post-event interruption lost or duplicated refusal evidence")
        print("ok    interruption after refusal receipt preserves one recoverable terminal tail")
        completed_732 = fixture.drain()
        require(completed_732.returncode == 0 
                and fields(fixture.root / "state/instructions/00000732.md")["status"] == "acknowledged",
                f"732 did not terminalize after 707: {completed_732.stderr}")
        route_actions = [json.loads(path.read_text(encoding="utf-8"))
                         for path in (fixture.root / "state/actions").glob("*.json")
                         if json.loads(path.read_text(encoding="utf-8")).get("verb") == "routing-refuse"]
        require(len(route_actions) == 2 and all(row.get("status") == "succeeded" for row in route_actions),
                "707/732 do not have exactly two terminal recovery actions")
        print("ok    732 terminalizes only after 707 through its own coupled refusal action")

        source_events = [row for row in json_rows(fixture.root / "state/events.jsonl")
                         if row.get("event") == "instruction-routing-refused"]
        require(len(source_events) == 2 and len({row["id"] for row in source_events}) == 2,
                "recovery source events are not exact-once")
        paused_schedule = fixture.run([
            "python3", "scripts/notification-outbox.py", "schedule", "--project", PROJECT,
        ])
        require(paused_schedule.returncode == 0 and paused_schedule.stdout.strip() == "0"
                and not any((fixture.root / "state/notification-events").iterdir())
                and not any((fixture.root / "state/deliveries").iterdir()),
                "PAUSE admitted notification reconciliation or delivery")
        (fixture.root / "state/PAUSE").unlink()
        scheduled = fixture.run([
            "python3", "scripts/notification-outbox.py", "schedule", "--project", PROJECT,
        ])
        require(scheduled.returncode == 0 and scheduled.stdout.strip() == "2",
                f"attention reconciliation was not scheduled exactly twice: {scheduled.stderr} {scheduled.stdout}")
        notified = fixture.run(["bash", "scripts/conduct-hermes.sh"])
        require(notified.returncode == 0, f"attention reconciliation failed: {notified.stderr}")
        attention = [json.loads(path.read_text(encoding="utf-8"))
                     for path in (fixture.root / "state/notification-events").glob("*.json")]
        deliveries = [json.loads(path.read_text(encoding="utf-8"))
                      for path in (fixture.root / "state/deliveries").glob("*.json")]
        require(len(attention) == 2 and all(row.get("event_type") == "lucas-attention-required"
                                            for row in attention),
                "refusal evidence did not become exactly two authenticated attention events")
        require(len(deliveries) == 2 and all(row.get("destination") == DIRECT for row in deliveries),
                "attention outbox did not create one direct delivery per refusal")
        delivery_schedule = fixture.run([
            "python3", "scripts/notification-outbox.py", "schedule", "--project", PROJECT,
        ])
        require(delivery_schedule.returncode == 0 and delivery_schedule.stdout.strip() == "2",
                "delivery actions were not scheduled exactly once")
        delivered = fixture.run(["bash", "scripts/conduct-hermes.sh"])
        require(delivered.returncode == 0 and len(json_rows(fixture.visible)) == 2,
                f"inert deliveries were not accepted exactly once: {delivered.stderr}")
        deliveries = [json.loads(path.read_text(encoding="utf-8"))
                      for path in (fixture.root / "state/deliveries").glob("*.json")]
        require(all(row.get("status") == "succeeded" for row in deliveries),
                "delivery records lack durable transport acknowledgement")
        for decision_path, _ in (
            fixture.queue("succeeded", "notification-reconcile")
            + fixture.queue("succeeded", "notification-deliver")
        ):
            replay_notice = fixture.run(
                ["bash", "scripts/conduct-hermes.sh", "--file", str(decision_path)],
                extra={"RECURSION_QUEUE_ACTUATION": "1"},
            )
            require(replay_notice.returncode == 0, "notification action replay failed")
        require(len(list((fixture.root / "state/notification-events").glob("*.json"))) == 2
                and len(list((fixture.root / "state/deliveries").glob("*.json"))) == 2
                and len(json_rows(fixture.visible)) == 2,
                "notification replay duplicated attention, delivery records, or visible sends")
        print("ok    replay does not duplicate refusal events, attention, or delivery records")

        for directory in ("state/plans", "state/goals", "state/tasks", "state/pilot-windows"):
            require(not any((fixture.root / directory).iterdir()), f"recovery created forbidden state in {directory}")
        require(not fixture.queue("pending") and not fixture.queue("running"),
                "recovery left pending/running decisions")
        require(hashlib.sha256((fixture.root / "state/instructions/00000618.md").read_bytes()).hexdigest()
                == fixture.retained_618, "instruction 618 changed")
        require(not fixture.model_marker.exists(), "a model ran during recovery")
        print("ok    queues are empty, execution state is absent, and instruction 618 is byte-identical")
        print("routing-recovery: ALL PASS")
        return 0
    except AssertionError as exc:
        print(f"FAIL  {exc}")
        return 1
    finally:
        fixture.close()


if __name__ == "__main__":
    raise SystemExit(main())
