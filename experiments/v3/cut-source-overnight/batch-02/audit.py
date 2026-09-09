"""Static evidence overlay; does not execute or promote any original trace."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
CONTRACT="docs/v3/foundation-research/mark2-research/mark3-comparison/comparison-contract.json"
QUESTIONS="docs/v3/construction/cut-source-overnight-20260908/reopen-01/work-inventory.json"
SLICES=("formal-comparison-20260907", "composition-model-20260908", "effect-evidence-20260908",
        "wire-correspondence-20260908", "typed-consultation-20260908", "shared-reservations-20260908",
        "shared-composition-20260908", "coupled-construction-20260908", "coupled-cut-pause-20260908",
        "cut-publication-20260908", "cut-source-overnight-20260908")
INFERRED={"effect-join":["Q1","Q4","Q6"],"epoch-types":["Q2","Q6"],"writer-pool":["Q6"],
          "pause":["Q4","Q6"],"uncertainty":["Q1","Q3","Q6"],"flow-replay":["Q3","Q6"]}


def require(ok,message):
    if not ok: raise ValueError(message)


def read(name):
    return json.loads((ROOT/name).read_text(encoding="utf-8"))


def sha(name):
    return hashlib.sha256((ROOT/name).read_bytes().replace(b"\r\n",b"\n")).hexdigest()


def build():
    original=read(CONTRACT); inventory=read(QUESTIONS)
    ids=[f"comparison.trace.{i:02d}" for i in range(1,28)]
    require([r["id"] for r in original["traces"]]==ids,"exact original27 row IDs")
    require([r["id"] for r in original["obligations"]]==list(INFERRED),"exact six obligation IDs")
    registries=[]; sources={CONTRACT:sha(CONTRACT),QUESTIONS:sha(QUESTIONS)}
    for name in SLICES:
        path=f"docs/v3/construction/{name}/coverage.json"; data=read(path)
        key="traces" if name==SLICES[0] else "slice_traces"
        require([r["id"] for r in data[key]]==ids,"complete unique registry rows")
        require(data["full_comparison_complete"] is False and data["formal_freeze"] is False,"unpromoted registry")
        sources[path]=sha(path)
        registries.append((path,key,data))
    rows=[]
    for i,row in enumerate(original["traces"]):
        refs=[]
        for path,key,data in registries:
            entry=data[key][i]
            result=entry.get("result")
            result_path=None
            if result:
                target=(ROOT/path).parent/result
                require(target.resolve().is_relative_to(ROOT) and target.is_file(),"existing contained result")
                result_path=target.relative_to(ROOT).as_posix();sources[result_path]=sha(result_path)
            refs.append({"path":path,"pointer":f"/{key}/{i}","entry":entry,"result_path":result_path})
        positive=[v for v in refs if v["pointer"].startswith("/slice_traces/") and v["entry"].get("result") and v["entry"].get("status","").startswith("partial")]
        rows.append({"id":row["id"],"contract_pointer":f"/traces/{i}","original":row,
                     "coverage_overlays":refs,"positive_slice_references":[v["path"] for v in positive],
                     "full_trace_complete":False,"new_execution":False})
    unsupported=[v["id"] for v in rows if not v["positive_slice_references"]]
    require(unsupported==[f"comparison.trace.{i:02d}" for i in (4,5,7,8,18,19,20,25,27)],"prospective no-positive-entry finding")
    questions=[q for q in inventory["questions"] if q["id"].startswith("Q")]
    require([q["id"] for q in questions]==[f"Q{i}" for i in range(1,7)],"all deferred questions")
    require(all(q["status"]=="deferred-safeguard" and q["evidence"]==[] for q in questions),"deferred evidence unchanged")
    require(questions[-1]["depends_on"]==[f"Q{i}" for i in range(1,6)],"explicit Q6 dependencies")
    baseline=registries[0][2];transfer=next(data for path,key,data in registries if "shared-reservations" in path)
    chronology={"original_trace_status":original["traces"][21]["status"],
                "original_extension_policy":original["profile_policy"]["conserved_rights_status"],
                "baseline_construction_status":baseline["traces"][21]["construction_status"],
                "baseline_extension":baseline["rights_extension"],"later_extension":transfer["rights_extension"],
                "later_trace_status":transfer["slice_traces"][21]["status"]}
    require(chronology=={"original_trace_status":"constructed-unrun","original_extension_policy":"unselected-unrun",
                        "baseline_construction_status":"not-selected-unrun","baseline_extension":"not-selected-unrun",
                        "later_extension":"selected-bounded-one-transfer","later_trace_status":"partial-modeled-support"},"exact scoped chronology")
    obligations=[]
    for i,o in enumerate(original["obligations"]):
        evidence=[{"path":path,"pointer":f"/slice_obligations/{j}","entry":entry}
                  for path,key,data in registries for j,entry in enumerate(data.get("slice_obligations",[])) if entry["id"]==o["id"]]
        obligations.append({"id":o["id"],"original":o,"contract_pointer":f"/obligations/{i}",
                            "evidence_overlays":evidence,"proposed_responsibility_dependencies":INFERRED[o["id"]],
                            "dependency_classification":"inference from questions, not explicit repository edges",
                            "full_obligation_complete":False})
    return {"status":"STATIC_OBLIGATION_AUDIT_PASS","sources":sources,"obligations":obligations,"traces":rows,
            "questions_preserved":questions,"trace22_chronology":chronology,"positive_slice_trace_count":27-len(unsupported),
            "no_positive_slice_entry":unsupported,"coverage_registries":len(registries),"slice_overlays":10,
            "no_positive_entry_scope":"ten named slice overlays, not absence of all possible evidence",
            "formal_freeze":False,"full_comparison_complete":False,"new_trace_execution":False}
