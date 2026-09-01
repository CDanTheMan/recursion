import copy, gc, hashlib, importlib.util, math, sys, unittest, weakref
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).parents[2];sys.path.insert(0,str(ROOT/"scripts"))
import mvp_adapters as a
import mvp_contracts as c
import mvp_kernel as k
NOW="2026-08-31T12:00:00Z"
def packet():
    sp=importlib.util.spec_from_file_location("kernel_fixture",ROOT/"scripts/tests/mvp-kernel.test.py");m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m.packet()
def snapshots(**changes):
    out={}
    for n,s in a.REGISTRY.items():
        refs=[{"id":"endpoint-evidence","sha256":"a"*64,"kind":"endpoint","adapter":n,"observed_at":NOW,"version":"v1","model":s.models[0],"endpoint_ref":"endpoint-evidence"},{"id":"health-evidence","sha256":"b"*64,"kind":"health","adapter":n,"observed_at":NOW,"version":"v1","health":"healthy","endpoint_ref":"endpoint-evidence"},{"id":"model-evidence","sha256":"c"*64,"kind":"model","adapter":n,"observed_at":NOW,"version":"v1","model":s.models[0],"endpoint_ref":"endpoint-evidence"},{"id":"executable-evidence","sha256":"d"*64,"kind":"executable","adapter":n,"observed_at":NOW,"version":"v1","executable":s.executable},{"id":"sandbox-evidence","sha256":"e"*64,"kind":"sandbox","adapter":n,"observed_at":NOW,"version":"v1","sandbox":s.sandbox,"worktree":"<validated-worktree>"}]
        if n in {"hermes-api","opencode-openrouter"}:refs.append({"id":"credential-evidence","sha256":"f"*64,"kind":"credential","adapter":n,"observed_at":NOW,"endpoint_ref":"endpoint-evidence"})
        v=dict(adapter=n,available=True,enabled=True,auth_proven=True,observed_at=NOW,freshness_seconds=0,quota_remaining=2,concurrency_available=1,capabilities=s.capabilities,roles=s.roles,models=s.models,network=s.network,provider=s.provider,billing=s.billing,version="v1",health="healthy",executable=s.executable,sandbox=s.sandbox,host=s.host,auth=s.auth,measured_health=n=="qwen-local",evidence_refs=refs,endpoint_ref="endpoint-evidence",credential_ref="credential-evidence" if n=="hermes-api" else None,health_evidence_ref="health-evidence",model_evidence_ref="model-evidence",executable_evidence_ref="executable-evidence",sandbox_evidence_ref="sandbox-evidence",sandbox_proof={"kind":"enclosing-sandbox","worktree":"<validated-worktree>","method":"host-enclosure","evidence_ref":"sandbox-evidence"})
        v.update(changes.get(n,{}));out[n]=a.CapabilitySnapshot(**v)
    return out
def metered_budget(p):
    b=dict(p["budget"]);b.update(metered_spend_allowed=True,approval_digest="a"*64,cost_limit_cents=100,calendar_month_ceiling_cents=100,remaining_cost_cents=100,budget_digest="")
    b["budget_digest"]=c.canonical_digest(b);body=p.to_dict();body["budget"]=b;body["packet_digest"]=hashlib.sha256(c.canonical_json({x:y for x,y in body.items() if x!="packet_digest"})).hexdigest();return b,k.TaskPacket(body,body["packet_digest"])
def hermetic_plan(p, adapter):
    caps={"codex-cli":("workspace-edit","jsonl"),"cursor-cli":("workspace-edit","structured-output")} [adapter]
    changes={"cursor-cli":{"billing":"subscription","included_pool_proven":True}} if adapter=="cursor-cli" else {}
    r=a.negotiate(a.NegotiationRequest("implementer",caps,execution_mode="hermetic"),snapshots(**changes),reference_time=NOW)
    return a.build_dispatch_plan(p,r,execution_mode="hermetic")
def fake(p, adapter):
    return a.fake_completion(p,hermetic_plan(p,adapter))
class AdapterTest(unittest.TestCase):
    def test_build_dispatch_plan_rejects_malformed_public_inputs_with_adapter_error(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer"),snapshots(),reference_time=NOW)
        for bad in (None,object(),{},"x"):
            with self.assertRaises(a.AdapterError):a.build_dispatch_plan(p,bad)
        for bad_packet in (None,object(),{},"x"):
            with self.assertRaises(a.AdapterError):a.build_dispatch_plan(bad_packet,r)

    def test_fake_completion_requires_hermetic_authority(self):
        p=packet()
        for bare in ("codex-cli","cursor-cli","hermes-api","opencode-openrouter","qwen-local"):
            with self.assertRaises(a.AdapterError):a.fake_completion(p,bare)
        live=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW)
        with self.assertRaises(a.AdapterError):a.fake_completion(p,live)

    def test_direct_plan_mutations_cannot_escape_packet_authority(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW);plan=a.build_dispatch_plan(p,r)
        for field,value in (("budget_digest","0"*64),("grant_digest","0"*64),("source_sha","b"*40),("execution_mode","hermetic")):
            with self.assertRaises(a.AdapterError):replace(plan,**{field:value})
        b,p=metered_budget(packet());r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","api"),network="provider-only",model="hermes",metered_spend_cents=1,approval_digest="a"*64),snapshots(),reference_time=NOW,budget=b);plan=a.build_dispatch_plan(p,r,endpoint_ref="endpoint-evidence",credential_ref="credential-evidence")
        for field in ("endpoint_ref","credential_ref"):
            with self.assertRaises(a.AdapterError):replace(plan,**{field:"other-ref"})
        with self.assertRaises(a.AdapterError):replace(plan,packet_authority={**a._plain(plan.packet_authority),"context_digest":"0"*64,"authority_digest":"0"*64})

    def test_plan_seal_reconstruction_cannot_substitute_packet_or_negotiation(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW);plan=a.build_dispatch_plan(p,r)
        rebuilt_packet=replace(p)
        self.assertIsNot(rebuilt_packet,p)
        with self.assertRaises(a.AdapterError):a._PlanSeal(rebuilt_packet,plan.negotiation,a._plain(plan.packet_authority))
        with self.assertRaises(a.AdapterError):a._PlanSeal(rebuilt_packet,plan.negotiation,a._plain(plan.packet_authority),None)
        with self.assertRaises(a.AdapterError):a._validate_plan_for_packet(rebuilt_packet,plan)
        with self.assertRaises(a.AdapterError):replace(plan,_seal=copy.copy(plan._seal))
        rebuilt_negotiation=replace(plan.negotiation)
        self.assertIsNot(rebuilt_negotiation,plan.negotiation)
        with self.assertRaises(a.AdapterError):replace(plan,negotiation=rebuilt_negotiation)

    def test_replaced_packet_cannot_mint_anchor_or_forged_plan(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW);plan=a.build_dispatch_plan(p,r)
        replaced_packet=replace(p)
        self.assertIsNot(replaced_packet,p)
        self.assertFalse(hasattr(p,"_adapter_packet_anchor"))
        with self.assertRaises(a.AdapterError):a._packet_anchor(replaced_packet,create=True)
        with self.assertRaises(a.AdapterError):a._PlanSeal(replaced_packet,r,a._plain(plan.packet_authority),None)
        with self.assertRaises(a.AdapterError):replace(plan,_seal=object())
        with self.assertRaises(a.AdapterError):a._validate_plan_for_packet(replaced_packet,plan)

    def test_plan_issuance_is_not_module_enumerable_and_rejects_raw_copy_forms(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW);plan=a.build_dispatch_plan(p,r)
        self.assertFalse(hasattr(a,"_PLAN_ISSUANCE"))
        self.assertFalse(isinstance(a.REGISTRY,dict))
        self.assertFalse(hasattr(a,"_PLAN_TRUST"))
        with self.assertRaises(AttributeError):
            setattr(a.DispatchPlan,"_factory_check",lambda plan,packet: None)
        for candidate in vars(a).values():
            if type(candidate) is object:
                with self.assertRaises(a.AdapterError):
                    a._PlanSeal(p,r,a._plain(plan.packet_authority),candidate)
        raw=object.__new__(a.DispatchPlan)
        for name in a.DispatchPlan.__dataclass_fields__:
            object.__setattr__(raw,name,getattr(plan,name))
        with self.assertRaises(a.AdapterError):a._validate_plan_for_packet(p,raw)
        for copier in (copy.copy,copy.deepcopy):
            try:copied=copier(plan)
            except Exception:continue
            with self.assertRaises(a.AdapterError):a._validate_plan_for_packet(p,copied)
        with self.assertRaises((AttributeError,TypeError)):
            setattr(plan,"adapter","cursor-cli")

    def test_plan_issuance_ledger_releases_dead_plans(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW);plan=a.build_dispatch_plan(p,r)
        plan_ref=weakref.ref(plan)
        del plan;gc.collect()
        self.assertIsNone(plan_ref())
        fresh=a.build_dispatch_plan(p,r)
        self.assertIsNotNone(weakref.ref(fresh)())

    def test_duplicate_requires_exact_external_packet_and_plan_anchors(self):
        p=packet();pl=hermetic_plan(p,"codex-cli");b=a.fake_completion(p,pl)
        for kwargs in ({},{"packet":packet(),"plan":pl},{"packet":p,"plan":None}):
            with self.assertRaises(a.AdapterError):a.deduplicate_result(b,[],**kwargs)
        altered=copy.deepcopy(a._plain(b));altered["result_envelope"]["context"]=[{"id":"other-context","summary":"public summary","evidence_refs":[]}]
        with self.assertRaises(a.AdapterError):a.deduplicate_result(altered,[],p,pl)

    def test_resigned_checkpoint_anchor_tampering_is_rejected(self):
        p=packet();pl=hermetic_plan(p,"codex-cli");base=a.fake_completion(p,pl);x=copy.deepcopy(a._plain(base));cp=x["checkpoints"][0];cp["packet_digest"]="0"*64;cp["checkpoint_digest"]=c.canonical_digest(cp)
        x["result_envelope"]["checkpoints"]=[cp];x["candidate"]["result_envelope"]=x["result_envelope"];rd=hashlib.sha256(c.canonical_json(x["result_envelope"])).hexdigest();x["result_digest"]=rd;x["candidate"]["result_digest"]=rd;x["evidence"]["result_digest"]=rd;x["evidence"]["result_envelope_digest"]=rd;x["receipt"]["result_digest"]=rd;x["receipt"]["checkpoint_digests"]=[cp["checkpoint_digest"]]
        for row in (x["candidate"],x["evidence"],x["receipt"]):row[c.DIGEST_FIELD[row["kind"]]]=c.canonical_digest(row)
        x["records"]=[cp if row.get("kind")=="checkpoint" else x[row["kind"]] if row.get("kind") in {"candidate","evidence","receipt"} else row for row in x["records"]];x["bundle_digest"]=hashlib.sha256(c.canonical_json(x["records"])).hexdigest()
        with self.assertRaises(a.AdapterError):a.deduplicate_result(x,[],p,pl)

    def test_resigned_context_substitution_is_rejected_by_packet_authority(self):
        p=packet();pl=hermetic_plan(p,"codex-cli");base=a.fake_completion(p,pl);x=copy.deepcopy(a._plain(base));env=x["result_envelope"]
        env["context"]=[{"id":"context-substitute","summary":"substituted context","evidence_refs":[]}]
        env["context_digest"]=hashlib.sha256(c.canonical_json(env["context"])).hexdigest()
        env["checkpoints"][0]["context_digest"]=env["context_digest"]
        env["checkpoints"][0]["checkpoint_digest"]=c.canonical_digest(env["checkpoints"][0])
        x["candidate"]["result_envelope"]=env
        x["result_digest"]=hashlib.sha256(c.canonical_json(env)).hexdigest();x["candidate"]["result_digest"]=x["result_digest"]
        x["evidence"]["result_digest"]=x["result_digest"];x["evidence"]["result_envelope_digest"]=x["result_digest"];x["receipt"]["result_digest"]=x["result_digest"]
        x["receipt"]["checkpoint_digests"]=[env["checkpoints"][0]["checkpoint_digest"]]
        for row in (x["candidate"],x["evidence"],x["receipt"]):row[c.DIGEST_FIELD[row["kind"]]]=c.canonical_digest(row)
        x["records"]=[env["checkpoints"][0] if row.get("kind")=="checkpoint" else x[row["kind"]] if row.get("kind") in {"candidate","evidence","receipt"} else row for row in x["records"]]
        x["bundle_digest"]=hashlib.sha256(c.canonical_json(x["records"])).hexdigest()
        with self.assertRaises(a.AdapterError):a.deduplicate_result(x,[],p,pl)

    def test_duplicate_evidence_id_with_different_hash_is_rejected(self):
        refs=list(snapshots()["codex-cli"].evidence_refs);dup=dict(refs[0]);dup["sha256"]="f"*64
        with self.assertRaises(a.AdapterError):
            a.CapabilitySnapshot(**{**snapshots()["codex-cli"].__dict__,"evidence_refs":refs+[dup]})

    def test_cli_evidence_is_fresh_versioned_and_snapshot_bound(self):
        cases=(("stale",{"observed_at":"2026-08-31T11:54:59Z"},a.RejectionReason.STALE),
               ("future",{"observed_at":"2026-08-31T12:00:01Z"},a.RejectionReason.FUTURE),
               ("version",{"version":"v999"},a.RejectionReason.CAPABILITY),
               ("binding",{"adapter":"cursor-cli"},a.RejectionReason.CAPABILITY))
        for _name,change,reason in cases:
            ss=snapshots();snap=ss["codex-cli"];rows=[dict(row) for row in snap.evidence_refs];rows[0].update(change)
            ss["codex-cli"]=a.CapabilitySnapshot(**{**snap.__dict__,"evidence_refs":rows})
            got=dict(a.negotiate(a.NegotiationRequest("implementer"),ss,reference_time=NOW).rejected)["codex-cli"]
            self.assertEqual(got,reason)

    def test_registry_exact_and_frozen(self):
        self.assertEqual(tuple(a.REGISTRY),a.NAMES)
        with self.assertRaises(Exception):a.REGISTRY["x"]=None
        with self.assertRaises(a.AdapterError):a.NegotiationRequest("worker")

    def test_dispatch_is_exact_and_scans_public_material(self):
        with self.assertRaises(a.AdapterError):
            a.DispatchPlan("evil","0"*64,"1"*64,"a"*40,"2"*64,"3"*64,"<validated-worktree>",("evil",),{"model":"x","packet_digest":"0"*64,"assignment_digest":"1"*64,"summary":"public"},"public")
        with self.assertRaises(a.AdapterError):
            a.DispatchPlan("codex-cli","0"*64,"1"*64,"a"*40,"2"*64,"3"*64,"<validated-worktree>",("codex",),{"model":"codex","packet_digest":"0"*64,"assignment_digest":"1"*64,"summary":"sk-test-secret-value"},"sk-test-secret-value")

    def test_public_records_are_recursively_immutable(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer"),snapshots(),reference_time=NOW)
        with self.assertRaises(TypeError):r.snapshot.evidence_refs[0]["id"]="changed"
        plan=a.build_dispatch_plan(p,r)
        with self.assertRaises(TypeError):plan.request["summary"]="changed"
        with self.assertRaises(TypeError):plan.evidence_refs[0]["id"]="changed"

    def test_hermes_api_is_empty_argv_but_requires_refs(self):
        p=packet();b,p=metered_budget(p);q=a.NegotiationRequest("implementer",("workspace-edit","api"),network="provider-only",model="hermes",metered_spend_cents=1,approval_digest="a"*64)
        r=a.negotiate(q,snapshots(),reference_time=NOW,budget=b)
        plan=a.build_dispatch_plan(p,r,endpoint_ref="endpoint-evidence",credential_ref="credential-evidence")
        self.assertEqual(plan.argv,());self.assertEqual(plan.request["endpoint_ref"],"endpoint-evidence")
        with self.assertRaises(a.AdapterError):a.build_dispatch_plan(p,r,endpoint_ref="unknown-endpoint",credential_ref="credential-evidence")

    def test_qwen_requires_provenance_not_boolean(self):
        x=snapshots(**{"qwen-local":{"measured_health":True,"health_evidence_ref":None}})
        r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","local")),x,reference_time=NOW)
        self.assertEqual(dict(r.rejected)["qwen-local"],a.RejectionReason.LOCAL_UNAVAILABLE)

    def test_result_window_envelope_and_duplicate_revalidation(self):
        p=packet();pl=hermetic_plan(p,"codex-cli");b=a.fake_completion(p,pl);self.assertEqual(b["candidate"]["result_digest"],b["result_digest"])
        with self.assertRaises(a.AdapterError):a.deduplicate_result(dict(b,bundle_digest="0"*64),[b],p,pl)
        with self.assertRaises(a.AdapterError):
            a.record_result(p,delivery_id="late",run_id="late-run",adapter="codex-cli",execution_mode="hermetic",started_at="2026-08-30T12:00:00Z",finished_at="2026-08-30T12:00:00Z",reference_time=NOW,current_source_sha=p["task"]["source_sha"],candidate_commit="a"*40,output={"summary":"ok"},usage={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0},checkpoint_records=b["checkpoints"],result_digest=b["result_digest"])

    def test_record_result_requires_exact_plan_execution_mode_live_to_hermetic(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl"),execution_mode="live"),snapshots(),reference_time=NOW);plan=a.build_dispatch_plan(p,r,execution_mode="live")
        with self.assertRaises(a.AdapterError) as cm:
            a.record_result(p,delivery_id="mode-live-hermetic",run_id="mode-live-hermetic",adapter="codex-cli",execution_mode="hermetic",started_at=NOW,finished_at=NOW,reference_time=NOW,current_source_sha=p["task"]["source_sha"],candidate_commit="a"*40,output={"adapter":"codex-cli","summary":"bounded public summary","execution_mode":"hermetic"},usage={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0},checkpoint_records=[a.fake_completion(p,hermetic_plan(p,"codex-cli"))["checkpoints"][0]],plan=plan)
        self.assertEqual(cm.exception.code,"binding")

    def test_record_result_requires_exact_plan_execution_mode_hermetic_to_live(self):
        p=packet();plan=hermetic_plan(p,"codex-cli")
        with self.assertRaises(a.AdapterError) as cm:
            a.record_result(p,delivery_id="mode-hermetic-live",run_id="mode-hermetic-live",adapter="codex-cli",execution_mode="live",started_at=NOW,finished_at=NOW,reference_time=NOW,current_source_sha=p["task"]["source_sha"],candidate_commit="a"*40,output={"adapter":"codex-cli","summary":"bounded public summary","execution_mode":"live"},usage={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0},checkpoint_records=[a.fake_completion(p,plan)["checkpoints"][0]],plan=plan)
        self.assertEqual(cm.exception.code,"binding")

    def test_result_output_depth_is_typed(self):
        p=packet();b=fake(p,"codex-cli");deep="x"
        for _ in range(30):deep={"x":deep}
        with self.assertRaises(a.AdapterError):
            a.record_result(p,delivery_id="deep",run_id="deep-run",adapter="codex-cli",execution_mode="hermetic",started_at=NOW,finished_at=NOW,reference_time=NOW,current_source_sha=p["task"]["source_sha"],candidate_commit="a"*40,output=deep,usage={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0},checkpoint_records=b["checkpoints"],result_digest=b["result_digest"])
    def test_dataclasses_reject_bool_int(self):
        with self.assertRaises(a.AdapterError):a.CapabilitySnapshot("codex-cli",True,True,True,NOW,quota_remaining=True)
        with self.assertRaises(a.AdapterError):a.NegotiationRequest("worker",metered_spend_cents=True)
    def test_dataclasses_reject_nonfinite_and_unknown(self):
        with self.assertRaises(TypeError):a.NegotiationRequest("worker",nope=1)
        with self.assertRaises(c.ContractError):c.canonical_json({"x":math.nan})
    def test_codex_deterministic(self):
        r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW)
        self.assertTrue(r.accepted);self.assertEqual(r.adapter.name,"codex-cli");self.assertEqual(r.rejected[0],("codex-cli",None))
    def test_affinity_only_eligible(self):
        r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit",),affinity="cursor-cli"),snapshots(),reference_time=NOW);self.assertFalse(r.accepted);self.assertEqual(r.reason,a.RejectionReason.AFFINITY_UNAVAILABLE)
    def test_absent_and_unknown_snapshot_trace(self):
        r=a.negotiate(a.NegotiationRequest("implementer"),{},reference_time=NOW);self.assertEqual(len(r.rejected),5);self.assertEqual(r.reason,a.RejectionReason.ABSENT)
        r=a.negotiate(a.NegotiationRequest("implementer"),{"unknown":{}},reference_time=NOW);self.assertEqual(r.rejected[-1],("unknown",a.RejectionReason.MALFORMED))
    def test_mismatched_snapshot_key_is_typed(self):
        x=snapshots();x["codex-cli"]=copy.copy(x["cursor-cli"]);r=a.negotiate(a.NegotiationRequest("implementer"),x,reference_time=NOW);self.assertEqual(dict(r.rejected)["codex-cli"],a.RejectionReason.MALFORMED)
    def test_pause_has_all_five_pause_reasons(self):
        r=a.negotiate(a.NegotiationRequest("implementer"),snapshots(),reference_time=NOW,pause=True);self.assertFalse(r.accepted);self.assertEqual([x[1] for x in r.rejected],[a.RejectionReason.PAUSE]*5)
    def test_reference_time_required(self):
        self.assertEqual(a.negotiate(a.NegotiationRequest("implementer"),snapshots()).reason,a.RejectionReason.MALFORMED)
    def test_stale_future_expired(self):
        for ch,reason in (({"freshness_seconds":301},a.RejectionReason.STALE),({"observed_at":"2030-01-01T00:00:00Z"},a.RejectionReason.FUTURE),({"observed_at":"2026-08-31T11:00:00Z","expires_at":"2026-08-31T11:59:59Z"},a.RejectionReason.EXPIRED)):
            r=a.negotiate(a.NegotiationRequest("implementer"),snapshots(**{"codex-cli":ch}),reference_time=NOW);self.assertEqual(dict(r.rejected)["codex-cli"],reason)
    def test_exact_runtime_binding(self):
        for field in ("provider","network","sandbox","executable","host","auth","version"):
            x=snapshots();v="bad" if field not in {"network"} else "other";v="" if field=="version" else v
            try:x["codex-cli"]=a.CapabilitySnapshot(**{**x["codex-cli"].__dict__,field:v})
            except a.AdapterError:continue
            r=a.negotiate(a.NegotiationRequest("implementer"),x,reference_time=NOW);self.assertIn(dict(r.rejected)["codex-cli"],set(a.RejectionReason))
    def test_role_capability_model_binding(self):
        x=snapshots();x["codex-cli"]=a.CapabilitySnapshot(**{**x["codex-cli"].__dict__,"roles":("implementer",)});r=a.negotiate(a.NegotiationRequest("implementer"),x,reference_time=NOW);self.assertEqual(dict(r.rejected)["codex-cli"],a.RejectionReason.ROLE)
    def test_qwen_requires_measured_health(self):
        x=snapshots(**{"qwen-local":{"measured_health":False}});r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","local")),x,reference_time=NOW);self.assertEqual(dict(r.rejected)["qwen-local"],a.RejectionReason.LOCAL_UNAVAILABLE)
    def test_subscription_requires_zero(self):
        r=a.negotiate(a.NegotiationRequest("implementer",metered_spend_cents=1),snapshots(),reference_time=NOW);self.assertEqual(dict(r.rejected)["codex-cli"],a.RejectionReason.METERED_NOT_APPROVED)
    def test_plan_codex_exact_and_safe(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW);plan=a.build_dispatch_plan(p,r)
        self.assertEqual(plan.argv,("codex","exec","--json","--strict-config","--sandbox","workspace-write","--ask-for-approval","never","--ephemeral","-C","<validated-worktree>","-"));self.assertNotIn("prompt",str(plan).lower())
    def test_plan_cursor_exact(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","structured-output")),snapshots(**{"cursor-cli":{"billing":"subscription","included_pool_proven":True}}),reference_time=NOW);self.assertEqual(a.build_dispatch_plan(p,r).argv[0],"cursor-agent");self.assertNotIn("--yolo",a.build_dispatch_plan(p,r).argv)
    def test_plan_opencode_no_invented_sandbox(self):
        p=packet();b,p=metered_budget(p);r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","api"),model="opencode",network="provider-only",metered_spend_cents=1,approval_digest="a"*64),snapshots(),reference_time=NOW,budget=b);self.assertNotIn("--sandbox",a.build_dispatch_plan(p,r,credential_ref="credential-evidence").argv)
    def test_plan_rejects_unsafe_worktree_and_model(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","jsonl")),snapshots(),reference_time=NOW)
        with self.assertRaises(a.AdapterError):a.build_dispatch_plan(p,r,worktree=r"C:\x\..\y")
        with self.assertRaises(a.AdapterError):a.build_dispatch_plan(p,r,model="other")
    def test_private_and_nonfinite_result_rejected(self):
        p=packet();base=fake(p,"codex-cli");cp=base["checkpoints"];out={"summary":"ok"};kw=dict(delivery_id="d-test",run_id="r-test",adapter="codex-cli",execution_mode="hermetic",started_at=NOW,finished_at=NOW,reference_time=NOW,current_source_sha=p["task"]["source_sha"],candidate_commit="a"*40,usage={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0},checkpoint_records=cp,result_digest=hashlib.sha256(c.canonical_json(out)).hexdigest())
        with self.assertRaises(a.AdapterError):a.record_result(p,output={"private_output":"x"},**kw)
        with self.assertRaises(a.AdapterError):a.record_result(p,output={"x":float("nan")},**kw)
    def test_result_digest_and_source_binding(self):
        p=packet();out={"summary":"ok"};cp=fake(p,"codex-cli")["checkpoints"];kw=dict(delivery_id="d2",run_id="r2",adapter="codex-cli",execution_mode="hermetic",started_at=NOW,finished_at=NOW,reference_time=NOW,current_source_sha=p["task"]["source_sha"],candidate_commit="a"*40,output=out,usage={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0},checkpoint_records=cp)
        with self.assertRaises(a.AdapterError):a.record_result(p,result_digest="0"*64,**kw)
        bad=dict(kw,current_source_sha="b"*40,result_digest=hashlib.sha256(c.canonical_json(out)).hexdigest())
        with self.assertRaises(a.AdapterError):a.record_result(p,**bad)
    def test_hermetic_fakes_distinct(self):
        p=packet();x=fake(p,"codex-cli");y=fake(p,"cursor-cli");self.assertNotEqual(x["delivery_id"],y["delivery_id"]);self.assertNotEqual(x["result_digest"],y["result_digest"])
    def test_duplicate_identical_and_conflict(self):
        p=packet();pl=hermetic_plan(p,"codex-cli");b=a.fake_completion(p,pl);self.assertIs(a.deduplicate_result(b,[b],p,pl),b)
        with self.assertRaises(a.AdapterError) as cm:a.deduplicate_result(dict(b,bundle_digest="0"*64),[b],p,pl)
        self.assertEqual(cm.exception.code,"duplicate-conflict")
    def test_metered_requires_full_approval(self):
        p=packet();q=a.NegotiationRequest("implementer",("workspace-edit","api"),network="provider-only",model="opencode",metered_spend_cents=1,approval_digest="a"*64)
        r=a.negotiate(q,snapshots(),reference_time=NOW);self.assertEqual(dict(r.rejected)["opencode-openrouter"],a.RejectionReason.METERED_NOT_APPROVED)
    def test_metered_overspend_and_on_demand_reject(self):
        p=packet();b,p=metered_budget(p);q=a.NegotiationRequest("implementer",("workspace-edit","api"),network="provider-only",model="opencode",metered_spend_cents=101,approval_digest="a"*64)
        r=a.negotiate(q,snapshots(),reference_time=NOW,budget=b);self.assertEqual(dict(r.rejected)["opencode-openrouter"],a.RejectionReason.OVERSHOOT)
        q=a.NegotiationRequest("implementer",("workspace-edit","api"),network="provider-only",model="opencode",metered_spend_cents=1,approval_digest="a"*64,on_demand=True);r=a.negotiate(q,snapshots(),reference_time=NOW,budget=b);self.assertEqual(dict(r.rejected)["opencode-openrouter"],a.RejectionReason.METERED_NOT_APPROVED)
    def test_direct_plan_rejects_dangerous_flag(self):
        with self.assertRaises(a.AdapterError):a.DispatchPlan("codex-cli","0"*64,"1"*64,"a"*40,"2"*64,"3"*64,"<validated-worktree>",("codex","--yolo"),{"model":"codex","packet_digest":"0"*64,"assignment_digest":"1"*64,"summary":"public"},"public")
    def test_direct_negotiation_result_requires_authority(self):
        with self.assertRaises(a.AdapterError):a.NegotiationResult(a.REGISTRY["codex-cli"],True,snapshot=snapshots()["codex-cli"],request=a.NegotiationRequest("implementer"))
        with self.assertRaises(a.AdapterError):a.NegotiationResult(a.REGISTRY["codex-cli"],True,snapshot=snapshots()["codex-cli"],request=a.NegotiationRequest("implementer"),authority_snapshots=snapshots(),reference_time=NOW)
    def test_unknown_snapshot_key_fails_closed(self):
        x=snapshots();x["forged"]={};r=a.negotiate(a.NegotiationRequest("implementer"),x,reference_time=NOW);self.assertFalse(r.accepted)
    def test_placeholder_proof_cannot_authorize_concrete_worktree(self):
        p=packet();r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","api"),model="opencode",network="provider-only",metered_spend_cents=1,approval_digest="a"*64),snapshots(),reference_time=NOW,budget=metered_budget(p)[0])
        with self.assertRaises(a.AdapterError):a.build_dispatch_plan(p,r,worktree=r"C:\one",credential_ref="credential-evidence")
    def test_public_scanner_handles_unicode_separators(self):
        with self.assertRaises(a.AdapterError):a.DispatchPlan("codex-cli","0"*64,"1"*64,"a"*40,"2"*64,"3"*64,"<validated-worktree>",("codex","exec"),{"model":"codex","packet_digest":"0"*64,"assignment_digest":"1"*64,"summary":"raw\u2060prompt: hello"},"public")
    def test_qwen_claims_are_distinct_and_typed(self):
        x=snapshots();q=x["qwen-local"];d=dict(q.__dict__);d["model_evidence_ref"]="endpoint-evidence";x["qwen-local"]=a.CapabilitySnapshot(**d);r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","local")),x,reference_time=NOW);self.assertEqual(dict(r.rejected)["qwen-local"],a.RejectionReason.LOCAL_UNAVAILABLE)
    def test_task_other_budget_cannot_build_plan(self):
        p=packet();b,p2=metered_budget(p);r=a.negotiate(a.NegotiationRequest("implementer",("workspace-edit","api"),model="opencode",network="provider-only",metered_spend_cents=1,approval_digest="a"*64),snapshots(),reference_time=NOW,budget=b)
        with self.assertRaises(a.AdapterError):a.build_dispatch_plan(packet(),r,credential_ref="credential-evidence")
    def test_live_record_requires_accepted_plan(self):
        p=packet();
        with self.assertRaises(a.AdapterError):a.record_result(p,delivery_id="live-run",run_id="live-run",adapter="codex-cli",execution_mode="live",started_at=NOW,finished_at=NOW,reference_time=NOW,current_source_sha=p["task"]["source_sha"],candidate_commit="a"*40,output={"summary":"ok"},usage={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0},checkpoint_records=[])
    def test_resigned_candidate_envelope_conflict_rejected(self):
        p=packet();pl=hermetic_plan(p,"codex-cli");b=a.fake_completion(p,pl);x=copy.deepcopy(a._plain(b));x["candidate"]["result_envelope"]["run_id"]="other-run";x["candidate"]["candidate_digest"]=c.canonical_digest(x["candidate"]);x["bundle_digest"]=hashlib.sha256(c.canonical_json(x["records"])).hexdigest()
        with self.assertRaises(a.AdapterError):a.deduplicate_result(x,[],p,pl)
if __name__=="__main__":unittest.main()
