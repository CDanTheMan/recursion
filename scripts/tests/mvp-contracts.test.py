import copy, hashlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from mvp_contracts import ContractError, canonical_digest, validate

T="2026-08-31T12:00:00Z"; D="0"*64; C="a"*40
def base(kind):
    if kind=="task": return {"schema_version":2,"kind":"task","id":"task-one","project_id":"project-one","source_repository":"org/repo","source_branch":"main","source_sha":C,"parent_goal":"goal-one","parent_task_id":None,"depth":0,"allowed_paths":["src"],"requested_capabilities":["workspace-edit"],"gate_digest":D,"created_at":T}
    if kind=="budget": return {"schema_version":2,"kind":"budget","id":"budget-one","task_id":"task-one","parent_budget_id":None,"token_limit":100,"wall_seconds":60,"concurrency_limit":1,"cost_limit_usd":0,"metered_spend_allowed":False,"calendar_month_ceiling_usd":0,"remaining_tokens":100,"remaining_wall_seconds":60,"remaining_cost_usd":0}
    if kind=="checkpoint": return {"schema_version":2,"kind":"checkpoint","id":"checkpoint-one","task_id":"task-one","sequence":0,"prev_digest":None,"state_digest":D,"created_at":T,"checkpoint_digest":""}
    if kind=="capability_grant": return {"schema_version":2,"kind":"capability_grant","id":"grant-one","task_id":"task-one","capabilities":["workspace-edit"],"allowed_paths":["src"],"network_policy":"none","endpoints":["none"],"expires_at":T,"grant_digest":""}
    if kind=="recovery": return {"schema_version":2,"kind":"recovery","id":"recovery-one","task_id":"task-one","prior_checkpoint_digest":D,"prior_receipt_digest":D,"action":"resume","state":"queued","created_at":T,"recovery_digest":""}
    if kind=="receipt": return {"schema_version":2,"kind":"receipt","id":"receipt-one","task_id":"task-one","assignment_digest":D,"adapter":"local","candidate_commit":C,"result_digest":D,"usage":{"tokens":1},"checkpoint_digests":[D],"receipt_digest":""}
    if kind=="verification": return {"schema_version":2,"kind":"verification","id":"verification-one","task_id":"task-one","receipt_digest":D,"candidate_digest":D,"gate_digest":D,"evidence_digest":D,"verifier_task_id":"task-two","verified_at":T}
    return {"schema_version":2,"kind":"supervisor","id":"supervisor-one","parent_goal":"goal-one","policy_digest":D,"created_at":T,"expires_at":None}
def signed(x):
    field={"capability_grant":"grant_digest","receipt":"receipt_digest","checkpoint":"checkpoint_digest","recovery":"recovery_digest"}.get(x["kind"])
    if field: x[field]=canonical_digest(x)
    return x
def expect_ok(x): validate(signed(x))
for k in ("supervisor","task","budget","capability_grant","receipt","checkpoint","verification","recovery"): expect_ok(base(k))
for mutation in (lambda x:x.update(extra=1), lambda x:x.update(schema_version=True), lambda x:x.update(allowed_paths=["../secret"])):
    x=base("task"); mutation(x)
    try: validate(x); raise AssertionError("mutation accepted")
    except ContractError: pass
x=base("verification"); x["verifier_task_id"]=x["task_id"]
try: validate(x); raise AssertionError("self verification accepted")
except ContractError: pass
print("mvp-contracts: ok")
