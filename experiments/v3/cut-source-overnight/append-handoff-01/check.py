"""Reproduce preserved packets, then compare the two new sealed handoff policies."""
import importlib.util
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[4]
DOC = ROOT / "docs/v3/construction/cut-source-overnight-20260908/append-handoff-01"
prior_dir = ROOT / "experiments/v3/cut-source-overnight/counterexample-assumptions-01"
sys.path.insert(0, str(prior_dir))
spec = importlib.util.spec_from_file_location("prior_ca_check", prior_dir / "check.py")
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
import h_encoding as encoding
import h_unified as unified
import h_separated as separated
import h_relation as relation
import h_experiment as experiment


def replay(n, word, expected):
    state = encoding.initial(n)
    relation.initial_valid(state, n)
    histories, rows = [[], []], []
    for index, action in enumerate(word, 1):
        after = unified.step(state, action, n)
        relation.require(after == separated.step(state, action, n), "independent manual transition")
        relation.transition(state, action, after, n)
        for i in range(2):
            if after[3+i][7] > state[3+i][7]:
                histories[i].append(after[3+i][1])
        measured = encoding.metrics(after)
        relation.metric_valid(after, measured)
        rows.append({"step": index, "action": action, "state": after, "metrics": measured})
        state = after
    relation.complete(state, n)
    reads = [sum(p[6]) for p in state[3:]]
    relation.require(reads == expected, "preregistered completed read work")
    return {"records": n, "actions": word, "length": len(word), "read_work": reads,
            "capture_histories": histories, "completed_waits": [p[12] for p in state[3:]], "trace": rows}


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    prior.main(output / "predecessor")
    original = ROOT / "docs/v3/construction/cut-source-overnight-20260908/counterexample-assumptions-01/results.json"
    relation.require(json.loads((output / "predecessor/result.json").read_text()) == json.loads(original.read_text()), "complete counterexample predecessor reproduction")
    graph_dir = output / "handoff"
    graph_dir.mkdir()
    finite = experiment.explore(graph_dir)
    witnesses = [replay(2, "OCACCACCCC", [3, 2]), replay(3, "OCACCOCCAACCCCC", [4, 5]),
                 replay(3, "OCACCAOACCACCCCC", [4, 5])]
    waits = witnesses[2]["completed_waits"]
    relation.require(waits[0][1] > waits[1][1] and waits[0][2] < waits[1][2], "opposite matched-record waiting orders")
    result = {"status": "APPEND_HANDOFF_PACKET_PASS", "predecessors_reproduced": True,
              "finite": finite, "manual_witnesses": witnesses, "policy_order": ["one", "drain"],
              "source_validity_proven": False, "deferred_questions_resolved": [], "formal_freeze": False,
              "runtime_integration_support": False, "broader_campaign_complete": False}
    prior.write(output / "result.json", result)
    accepted = DOC / "results.json"
    if accepted.exists():
        relation.require(json.loads((output / "result.json").read_text()) == json.loads(accepted.read_text()), "exact accepted result reproduction")
    print(json.dumps({"status": result["status"], "states": finite["states_per_representation"],
                      "witnesses": [w["read_work"] for w in witnesses]}), flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
