"""Fresh interactive counterexample packet; no source-admission or provider activity."""
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
PRIOR = ROOT / "experiments/v3/cut-source-overnight/progress-01"
sys.path.insert(0, str(PRIOR))
import pg_encoding as encoding
import pg_unified as unified
import pg_separated as separated
import pg_relation as relation
import pg_experiment as previous
from variant import step as variant_step


def require(value, message):
    if not value:
        raise ValueError(message)


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def replay(n, word):
    state = encoding.initial(n)
    relation.initial_valid(state, n)
    histories = [[], []]
    rows = []
    for index, action in enumerate(word, 1):
        before = state
        a = unified.step(before, action, n)
        b = separated.step(before, action, n)
        require(a == b, "independent exact witness transition")
        relation.transition(before, action, a, n)
        for i in range(2):
            if a[3 + i][7] > before[3 + i][7]:
                histories[i].append(a[3 + i][1])
        state = a
        measured = encoding.metrics(state)
        relation.metric_valid(state, measured)
        rows.append({"step": index, "action": action, "state": state, "metrics": measured})
    relation.complete(state, n)
    require(all(not p[3] for p in state[3:]), "joint completed collector endpoint")
    return {"records": n, "actions": word, "length": len(word), "capture_histories": histories,
            "read_work": [sum(p[6]) for p in state[3:]], "trace": rows}


def history_certificate(n):
    # Necessary increasing-history constraints, a superset of reachable histories.
    # This is not schedule enumeration and does not assert every pair is realizable.
    histories = [tuple(i for i in range(1, n) if mask & (1 << (i - 1))) + (n,)
                 for mask in range(1 << (n - 1))]
    pairs = [(a, b) for a, b in itertools.product(histories, repeat=2)
             if a[0] == b[0] and sum(a) > sum(b)]
    for a, b in pairs:
        require(len(a) >= 3 and sum(a) >= n + 3, "necessary optimistic work lower bound")
        require(sum(a) + 2 * len(a) >= n + 9, "collector opportunity lower bound")
    return {"records": n, "basis": "necessary capture-history pairs, not reachable schedules",
            "histories": histories, "advantage_pairs": pairs,
            "no_advantage_under_necessary_constraints": not pairs,
            "collector_lower_bound": None if not pairs else min(sum(a) + 2 * len(a) for a, b in pairs)}


def changed_assumption(n=3, repetitions=7):
    normal = encoding.initial(n)
    changed = encoding.initial(n)
    word = "O" * (n - 1) + "CCAC" * repetitions
    rows = []
    for index, action in enumerate(word, 1):
        normal_next = unified.step(normal, action, n)
        relation.transition(normal, action, normal_next, n)
        normal = normal_next
        changed = variant_step(changed, action, n)
        require(changed[:3] == normal[:3] and changed[3] == normal[3], "unchanged arrivals and optimistic policy")
        if index > n - 1 and (index - (n - 1)) % 4 == 0:
            count = (index - (n - 1)) // 4
            expected = (1, 1, 1, False, 1, False, (count,) + (0,) * (n - 1),
                        count, count, 0, 0, count, (0,) + (-1,) * (n - 1))
            require(changed[4] == expected, "independent repeated-cycle equation for sealed variant")
        rows.append({"step": index, "action": action, "normal_sealed": normal[4], "variant_sealed": changed[4]})
    relation.complete(normal, n)
    require(changed[4][0] == 1 and sum(changed[4][6]) > n * (n + 1) // 2, "finite witness beyond original read bound")
    return {"assumption_removed": "sealed collector idles at unchanged already checked count",
            "records": n, "actions": word, "repetitions": repetitions,
            "original_completed": True, "variant_visible": changed[4][0],
            "variant_pending": n - changed[4][0], "variant_reads": sum(changed[4][6]),
            "original_read_bound": n * (n + 1) // 2,
            "infinite_claim_basis": "separate induction on CCAC cycles; finite trace alone is insufficient",
            "trace": rows}


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    prepared = output / "predecessor-prepare"
    explored = output / "predecessor-explore"
    prepared.mkdir(); explored.mkdir()
    prepared_result = previous.prepare(prepared)
    write(prepared / "result.json", prepared_result)
    old = previous.explore(explored)
    write(explored / "result.json", old)
    doc = ROOT / "docs/v3/construction/cut-source-overnight-20260908/progress-01"
    require((prepared / "inputs.json").read_bytes().replace(b"\r\n", b"\n") ==
            (doc / "inputs.json").read_bytes().replace(b"\r\n", b"\n"), "original input bytes")
    require(json.loads((explored / "result.json").read_text()) == json.loads((doc / "results.json").read_text()), "complete prior finite JSON result")
    for profile in old["profiles"]:
        require(hashlib.sha256((explored / profile["graph_file"]).read_bytes()).hexdigest() == profile["graph_sha256"], "prior graph bytes")
    witnesses = [replay(4, "COACCOACOACCCAAC" + "C" * 6)]
    require(witnesses[0]["read_work"] == [8, 7], "earlier manual example")
    for n in (3, 4):
        word = "COACCC" + "O" * (n - 2) + "A" * (n - 1) + "C" * (n + 5)
        row = replay(n, word)
        require(row["length"] == 3 * n + 8 and row["read_work"] == [n + 3, n + 1], "shorter construction")
        require(row["capture_histories"] == [[1, 2, n], [1, n]], "batching mechanism")
        witnesses.append(row)
    certificates = [history_certificate(n) for n in (2, 3, 4)]
    require(certificates[0]["no_advantage_under_necessary_constraints"], "N2 necessary exclusion")
    variant = changed_assumption()
    result = {"status": "COUNTEREXAMPLE_ASSUMPTIONS_PACKET_PASS", "witnesses": witnesses,
              "history_certificates": certificates, "assumption_variant": variant,
              "predecessor_reproduced": True, "predecessor_states_per_representation": old["states_per_representation"],
              "schedule_exhaustiveness_claim": False, "formal_freeze": False,
              "source_validity_proven": False, "deferred_questions_resolved": [],
              "publication_ready": False, "broader_campaign_complete": False}
    write(output / "result.json", result)
    print(json.dumps({"status": result["status"], "witnesses": [{k: r[k] for k in ("records", "length", "read_work", "capture_histories")} for r in witnesses], "variant_reads": variant["variant_reads"]}), flush=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
