"""Bounded conditional progress study over stipulated valid original record streams."""
import argparse
import ast
from collections import deque
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / "docs/v3/construction/cut-source-overnight-20260908/progress-01"
CASES = ("success", "ambiguous", "prior-unresolved", "later-start-only")


def audit(event, args):
    if event.startswith("socket.") or event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.fork"):
        raise RuntimeError("This local measurement has no network or child-process activity")


sys.addaudithook(audit)

from pg_encoding import initial, opportunities, metrics
import pg_unified
import pg_separated
import pg_relation


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write(path, value):
    path.write_bytes(encoded(value) + b"\n")


def literal(path, name):
    tree = ast.parse((ROOT / path).read_text(encoding="utf-8"))
    matches = [statement.value for statement in tree.body if isinstance(statement, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == name for t in statement.targets)]
    pg_relation.require(len(matches) == 1, "one original constant")
    return ast.literal_eval(matches[0])


def prepare(directory):
    sys.path.insert(0, str(ROOT / "experiments/v3/effect-evidence"))
    from ee_cases import unsigned
    from ee_common import canonical
    streams = []
    for name, size in zip(CASES, (3, 2, 4, 4)):
        original = unsigned(name)
        pg_relation.require(len(original["records"]) == size, "original record inventory")
        records = [canonical(record) for record in original["records"]]
        streams.append({"name": name, "original": original,
                        "canonical_record_hex": [raw.hex() for raw in records],
                        "canonical_record_sha256": [digest(raw) for raw in records]})
    costs = literal("experiments/v3/coupled-construction/c_domain.py", "COSTS")
    requests = literal("experiments/v3/coupled-cut-pause/p_literal.py", "REQUESTS")
    pg_relation.require(costs == (1, 2, 1, 2), "original wire event lengths")
    pg_relation.require(requests == (("pool10", "goalA", "opA", "attemptA", "payloadA", "ownerA", 6),
                                     ("pool10", "goalB", "opB", "attemptB", "payloadB", "ownerB", 6)), "original A6/B6 requests")
    result = {"classification": "stipulated-valid-input-premises", "factory": "ee_cases.unsigned",
              "source_validity_proven": False, "streams": streams, "original_wire_costs": costs,
              "original_pool_requests": requests, "allowance_release_transitions": 0}
    write(directory / "inputs.json", result)
    return {"status": "INPUT_PREPARATION_COMPLETE", "streams": len(streams), "new_progress_graphs": 0,
            "inputs_sha256": digest(encoded(result))}


def explore_graph(size, step, budget):
    first = ("prefix", 0, initial(size))
    pg_relation.initial_valid(first[2], size)
    nodes, ids, edges, parents, terminals = [first], {first: 0}, [], [None], []
    pending = deque([0])
    while pending:
        source_id = pending.popleft()
        source = nodes[source_id]
        choices = opportunities(source, size)
        pg_relation.schedule_valid(source, choices, size)
        if not choices:
            pg_relation.complete(source[2], size)
            terminals.append(source_id)
        for action, phase, index in choices:
            state = step(source[2], action, size)
            pg_relation.transition(source[2], action, state, size)
            target = (phase, index, state)
            if target not in ids:
                pg_relation.require(len(nodes) < budget, "per-representation cumulative state cap")
                ids[target] = len(nodes)
                nodes.append(target)
                parents.append((source_id, action))
                pending.append(ids[target])
            edges.append((source_id, action, ids[target]))
    return nodes, edges, parents, terminals


def witness(graph, node_id):
    nodes, edges, parents, terminals = graph
    word, current = [], node_id
    while parents[current] is not None:
        current, action = parents[current]
        word.append(action)
    measured = metrics(nodes[node_id][2])
    pg_relation.metric_valid(nodes[node_id][2], measured)
    return {"node": node_id, "actions": "".join(reversed(word)), "phase": nodes[node_id][:2],
            "metrics": measured}


def controls():
    start = initial(2)
    opened = pg_unified.step(start, "C", 2)
    read = pg_unified.step(opened, "C", 2)
    bad_policy = list(read[3])
    bad_policy[6] = opened[3][6]
    missing_read = (*read[:3], tuple(bad_policy), read[4])
    offered = pg_unified.step(start, "O", 2)
    serviced = pg_unified.step(offered, "A", 2)
    bad_policy = list(serviced[3])
    bad_policy[12] = offered[3][12]
    missing_wait = (*serviced[:3], tuple(bad_policy), serviced[4])
    wrong_policy = list(serviced[3])
    wrong_policy[12] = (0, serviced[3][12][1] + 1)
    wrong_wait = (*serviced[:3], tuple(wrong_policy), serviced[4])
    pg_relation.state_valid(wrong_wait, 2)
    lost_pending = (offered[0], start[1], start[2], *offered[3:])
    results = []
    for name, before, action, after in (("omitted-read-accounting", opened, "C", missing_read),
                                        ("omitted-serviced-append-wait", offered, "A", missing_wait),
                                        ("incorrect-nonnegative-append-wait", offered, "A", wrong_wait),
                                        ("discarded-pending-offer", start, "O", lost_pending)):
        try:
            pg_relation.transition(before, action, after, 2)
        except ValueError as error:
            results.append({"control": name, "detected": True, "reason": str(error)})
        else:
            raise ValueError("measurement control was not detected: " + name)
    return results


def explore(directory):
    inputs_path = DOC / "inputs.json"
    inputs = json.loads(inputs_path.read_text(encoding="utf-8"))
    pg_relation.require([s["name"] for s in inputs["streams"]] == list(CASES), "exact prepared stream names")
    summaries = []
    total = 0
    for stream in inputs["streams"]:
        size = len(stream["original"]["records"])
        a = explore_graph(size, pg_unified.step, 500000 - total)
        b = explore_graph(size, pg_separated.step, 500000 - total)
        pg_relation.require(a == b, "exact reachable graphs, parents and terminal identities")
        nodes, edges, parents, terminals = a
        total += len(nodes)
        data = {"nodes": nodes, "edges": edges, "parents": parents, "terminals": terminals}
        graph_bytes = encoded(data) + b"\n"
        filename = stream["name"] + "-graph.json"
        (directory / filename).write_bytes(graph_bytes)
        predicates = {
            "optimistic_actual_retry": lambda s: s[3][10] > 0,
            "sealed_postponed_append": lambda s: s[4][11] > 0,
            "optimistic_less_read_work": lambda s: sum(s[3][6]) < sum(s[4][6]),
            "sealed_less_read_work": lambda s: sum(s[4][6]) < sum(s[3][6]),
        }
        witnesses = {}
        for label, predicate in predicates.items():
            # Work comparisons use completed endpoints so unfinished work cannot win.
            domain = terminals if "less_read_work" in label else range(len(nodes))
            found = next((i for i in domain if predicate(nodes[i][2])), None)
            witnesses[label] = None if found is None else witness(a, found)
        witnesses["quiet_completion"] = witness(a, terminals[0])
        pg_relation.require(witnesses["optimistic_actual_retry"] is not None, "actual retry positive witness")
        pg_relation.require(witnesses["sealed_postponed_append"] is not None, "waiting positive witness")
        terminal_metrics = [metrics(nodes[i][2]) for i in terminals]
        for i, measured in zip(terminals, terminal_metrics):
            pg_relation.metric_valid(nodes[i][2], measured)
        pg_relation.require(terminal_metrics == [metrics(b[0][i][2]) for i in b[3]], "all exact terminal measurements")
        summaries.append({"name": stream["name"], "record_count": size, "states_per_representation": len(nodes),
                          "edges_per_representation": len(edges), "terminal_count": len(terminals), "frontier": 0,
                          "graph_file": filename, "graph_sha256": digest(graph_bytes), "exact_graph_equality": True,
                          "independent_relation_all_edges": True, "witnesses": witnesses,
                          "terminal_read_work_ranges": {
                              name: [min(m[name]["read_work"] for m in terminal_metrics), max(m[name]["read_work"] for m in terminal_metrics)]
                              for name in ("optimistic", "sealed")}})
    return {"status": "CONDITIONAL_PROGRESS_FINITE_PASS", "classification": "modeled-conditional-collection-progress",
            "inputs_sha256": digest(encoded(inputs)), "profiles": summaries, "states_per_representation": total,
            "frontier": 0, "prefix_length": 6, "controls": controls(), "source_validity_proven": False,
            "deferred_questions_resolved": [], "campaign_complete": False, "formal_freeze": False,
            "full_comparison_complete": False, "runtime_integration_support": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "explore"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pg_relation.require(args.output.is_dir(), "pre-admitted existing output directory")
    result = prepare(args.output) if args.mode == "prepare" else explore(args.output)
    write(args.output / "result.json", result)
    print(json.dumps({"status": result["status"], "classification": result.get("classification")}), flush=True)
