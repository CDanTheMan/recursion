"""Focused A/B or A/B/C acceptance; all model execution remains owned by the enclosing runner."""
import argparse
import json
from pathlib import Path
import audit
import workloads as w
ROOT=Path(__file__).resolve().parents[4]
DOC=ROOT/"docs/v3/construction/cut-source-overnight-20260908/batch-02"


def write(path,x):path.write_text(json.dumps(x,indent=2)+"\n",encoding="utf-8")
def normalize(x):return json.loads(json.dumps(x))


def controls():
    rows=w.old_experiment.controls()
    enc,step,relation=w.b_encoding,w.b_unified.step,w.b_relation
    start=enc.initial(4)
    bad=list(start[5]);bad[13]=0
    try:relation.initial_valid((*start[:5],tuple(bad)),4)
    except ValueError as error:rows.append({"control":"initial-budget-zero","detected":True,"reason":str(error)})
    else:raise ValueError("initial budget control undetected")
    offered=step(start,"O",4);serviced=step(offered,"A",4)
    bad=list(serviced[5]);bad[13]=offered[5][13]
    missing_decrement=(*serviced[:5],tuple(bad))
    opened=step(start,"C",4);read=step(opened,"C",4);finished=step(read,"C",4)
    bad=list(finished[5]);bad[13]=0;missing_reset=(*finished[:5],tuple(bad))
    after=step(offered,"C",4);early=(*after[:5],after[3])
    for label,before,action,after in (("missing-budget-decrement",offered,"A",missing_decrement),
                                      ("missing-release-refill",read,"C",missing_reset),
                                      ("premature-two-service-reseal",offered,"C",early)):
        relation.state_valid(after,4)
        try:relation.transition(before,action,after,4)
        except ValueError as error:rows.append({"control":label,"detected":True,"reason":str(error)})
        else:raise ValueError("control undetected: "+label)
    return rows


def main(output,packet):
    output.mkdir(parents=True,exist_ok=False)
    overlay=audit.build();write(output/"A-audit.json",overlay)
    inputs={row["path"]:row["git_blob_sha256"] for row in json.loads((DOC/"manifest.json").read_text())["inputs"]}
    w.require(all(inputs.get(path)==digest for path,digest in overlay["sources"].items()),"registered immutable audit input bytes")
    if (DOC/"A-audit.json").exists():w.require(overlay==json.loads((DOC/"A-audit.json").read_text()),"exact static evidence overlay")
    b,graphs=w.explore(output/"B")
    b["matched_prefix_comparisons"]=w.matched_prefixes(graphs)
    b["controls"]=w.old_experiment.controls()
    write(output/"B-result.json",b)
    if (DOC/"B-results.json").exists():w.require(normalize(b)==json.loads((DOC/"B-results.json").read_text()),"exact accepted B reproduction")
    if packet=="B":
        result={"status":"BATCH02_A_B_PACKET_PASS","audit_summary":{"positive_slice_traces":overlay["positive_slice_trace_count"],"no_positive_entry":overlay["no_positive_slice_entry"]},"B":b}
    else:
        w.require((DOC/"B-results.json").exists() and (DOC/"A-audit.json").exists(),"accepted A/B required before C")
        c,cgraphs=w.explore(output/"C",three=True,baseline=graphs,used=b["states_per_representation"])
        c["controls"]=controls();state=w.b_encoding.initial(4);trace=[]
        for action in "OOOAAC":
            after=w.b_unified.step(state,action,4);w.require(after==w.b_separated.step(state,action,4),"independent threshold witness")
            w.b_relation.transition(state,action,after,4);state=after;trace.append(state)
        w.require(state[5][3] and not state[4][3] and state[5][0]==3 and state[1]==4,"meaningful N4 guard distinction")
        w.require(("prefix",6,state) in cgraphs[(4,"AC")][0],"witness belongs to registered domain")
        c["threshold_witness"]={"records":4,"actions":"OOOAAC","states":trace}
        differences={sum(g[0][i][2][5][6])-sum(g[0][i][2][4][6]) for g in cgraphs.values() for i in g[3]}
        w.require(differences=={0,3},"both completed difference outcomes attained")
        result={"status":"BATCH02_A_B_C_PACKET_PASS","A_audit_sha256":w.sha(w.encoded(overlay)),"B":b,"C":c,
                "formal_freeze":False,"full_comparison_complete":False,"deferred_questions_resolved":[],"runtime_selection":None}
        if (DOC/"results.json").exists():w.require(normalize(result)==json.loads((DOC/"results.json").read_text()),"exact accepted final batch result")
    write(output/"result.json",result)
    print(json.dumps({"status":result["status"],"B_states":b["states_per_representation"],"C_states":result.get("C",{}).get("states_per_representation"),"audit_partial_traces":overlay["positive_slice_trace_count"]}),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("output",type=Path);parser.add_argument("--packet",choices=("B","C"),required=True)
    args=parser.parse_args();main(args.output,args.packet)
