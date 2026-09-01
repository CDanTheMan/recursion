"""Pure, inert capability-negotiated MVP adapters."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import datetime as _dt, hashlib, re, unicodedata, weakref
from types import MappingProxyType
from typing import Any, Mapping, Sequence
import mvp_contracts as contracts
import mvp_kernel as kernel

class AdapterError(ValueError):
    def __init__(self, code: str, message: str = ""):
        self.code = code; super().__init__(message or code)
class RejectionReason(str, Enum):
    ABSENT="absent"; DISABLED="disabled"; STALE="stale"; FUTURE="future"; EXPIRED="expired"; AUTH_UNPROVEN="auth-unproven"; QUOTA_EXHAUSTED="quota-exhausted"; CAPABILITY="capability"; NETWORK="network"; ROLE="role"; MODEL="model"; PROVIDER="provider"; BILLING="billing-basis"; EXECUTABLE="executable"; SANDBOX="sandbox"; METERED_NOT_APPROVED="metered-not-approved"; PAUSE="PAUSE"; MALFORMED="malformed"; OVERSHOOT="overspend-or-quota"; DUPLICATE_CONFLICT="duplicate-conflict"; LOCAL_UNAVAILABLE="requeue-local-unavailable"; AFFINITY_UNAVAILABLE="affinity-unavailable"
NAMES=("codex-cli","cursor-cli","hermes-api","opencode-openrouter","qwen-local")
ROLES={"implementer","verifier"}; BILLING={"subscription","included","metered","local"}; NETWORK={"none","provider-only","allowlist"}; MODES={"hermetic","live"}; _HERMETIC_PROOF=object(); _NEGOTIATION_TRUST=object()
HEX64=re.compile(r"^[0-9a-f]{64}$"); SHA=re.compile(r"^[0-9a-f]{40,64}$"); TIME=re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$"); ID=re.compile(r"^[a-z][a-z0-9-]{1,63}$"); CONTROL=re.compile(r"[\x00-\x1f\x7f]"); MAX_PUBLIC_DEPTH=16
CLI_EVIDENCE_VERSION="v1"; CLI_EVIDENCE_MAX_AGE_SECONDS=300; CLI_EVIDENCE_MAX_FUTURE_SKEW_SECONDS=0
_PRIVATE_PUBLIC=re.compile(r"\b(?:raw\s+prompt|private\s+(?:transcript|output|reasoning|scratchpad|cot)|(?:conversation|message)\s+(?:dump|transcript)|chain\s+of\s+thought|cot)\b",re.I)

def _s(v: Any,n="value",empty=False)->str:
    if not isinstance(v,str) or (not empty and not v) or CONTROL.search(v) or len(v)>contracts.MAX_STRING: raise AdapterError("malformed",f"{n} must be safe")
    return v
def _i(v: Any,n,minv=0)->int:
    if type(v) is not int or v<minv: raise AdapterError("malformed",f"{n} must be integer")
    return v
def _b(v: Any,n)->bool:
    if type(v) is not bool: raise AdapterError("malformed",f"{n} must be boolean")
    return v
def _ss(v: Any,n,empty=True)->tuple[str,...]:
    if not isinstance(v,(list,tuple)) or len(v)>contracts.MAX_LIST: raise AdapterError("malformed",f"{n} must be bounded")
    r=tuple(_s(x,n) for x in v)
    if not empty and not r or len(set(r))!=len(r): raise AdapterError("malformed",f"{n} invalid")
    return r
def _plain(v: Any,depth=0):
    if depth>MAX_PUBLIC_DEPTH: raise AdapterError("oversized","nesting exceeds bound")
    if isinstance(v,Mapping):
        if any(not isinstance(k,str) for k in v): raise AdapterError("malformed","mapping keys must be strings")
        return {k:_plain(x,depth+1) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [_plain(x,depth+1) for x in v]
    return v
def _freeze(v: Any,depth=0,active=None):
    if depth>MAX_PUBLIC_DEPTH: raise AdapterError("oversized","nesting exceeds bound")
    active=set() if active is None else active
    if isinstance(v,Mapping):
        if id(v) in active: raise AdapterError("malformed","cyclic mapping")
        active.add(id(v))
        try:
            if any(not isinstance(k,str) for k in v): raise AdapterError("malformed","mapping keys must be strings")
            return MappingProxyType({k:_freeze(x,depth+1,active) for k,x in v.items()})
        finally:active.remove(id(v))
    if isinstance(v,(list,tuple)):
        if id(v) in active: raise AdapterError("malformed","cyclic sequence")
        active.add(id(v))
        try:return tuple(_freeze(x,depth+1,active) for x in v)
        finally:active.remove(id(v))
    return v
def _safe(v: Any,n):
    try:
        plain=_plain(v); contracts.canonical_json(plain); _scan_public(plain,n)
    except AdapterError: raise
    except Exception as e: raise AdapterError("secret-or-private-output" if any(x in str(e).lower() for x in ("secret","private")) else "malformed",f"{n} is unsafe") from e
def _obj(v,n):
    if not isinstance(v,Mapping): raise AdapterError("malformed",f"{n} is not object")
    r=_plain(v); _safe(r,n); return r
def _scan_public(v,n):
    if isinstance(v,str):
        normalized=unicodedata.normalize("NFKC",v).casefold()
        folded="".join(" " if c.isspace() or unicodedata.category(c) in {"Cf","Pc","Pd"} else c for c in normalized)
        if _PRIVATE_PUBLIC.search(folded):raise AdapterError("secret-or-private-output",f"{n} contains private material")
    elif isinstance(v,Mapping):
        for k,x in v.items():_scan_public(k,n);_scan_public(x,n)
    elif isinstance(v,(list,tuple)):
        for x in v:_scan_public(x,n)
def _digest(v,n):
    v=_s(v,n)
    if not HEX64.fullmatch(v): raise AdapterError("malformed",f"{n} is not digest")
    return v
def _ref(v,n):
    v=_s(v,n)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*",v): raise AdapterError("malformed",f"{n} is not ref")
    return v
def _time(v,n):
    v=_s(v,n)
    if not TIME.fullmatch(v): raise AdapterError("malformed",f"{n} is not UTC time")
    try:contracts.parse_time(v)
    except Exception as e:raise AdapterError("malformed",f"{n} invalid") from e
    return v
def _argv(v,empty=False):
    if not isinstance(v,(list,tuple)) or (not empty and not v) or len(v)>contracts.MAX_LIST:raise AdapterError("malformed","argv invalid")
    return tuple(_s(x,"argv") for x in v)
def _refs(v):
    if not isinstance(v,(list,tuple)) or len(v)>contracts.MAX_LIST:raise AdapterError("malformed","evidence refs invalid")
    out=[]
    for x in v:
        x=_obj(x,"evidence ref")
        allowed={"id","sha256","kind","adapter","observed_at","version","model","endpoint_ref","credential_ref","executable","sandbox","worktree","health"}
        if not {"id","sha256"}<=set(x) or not set(x)<=allowed or not ID.fullmatch(str(x["id"])):raise AdapterError("malformed","evidence ref invalid")
        _digest(x["sha256"],"evidence sha256");out.append(_freeze(x))
    # IDs are the stable names used by packet context and capability claims.
    # Duplicate IDs are ambiguous even when their hashes differ.
    if len({x["id"] for x in out})!=len(out):raise AdapterError("malformed","duplicate evidence ref")
    return tuple(out)
def _declared(ref,refs,n):
    if not ref or not any(x.get("id")==ref for x in refs):raise AdapterError("malformed",f"{n} evidence missing")
def _claim(ref,refs,kind,snap,*,required=()):
    """Resolve one typed capability claim; a SHA alone is never provenance."""
    matches=[x for x in refs if x.get("id")==ref]
    if len(matches)!=1:raise AdapterError("malformed",f"{kind} evidence missing")
    row=matches[0]
    if row.get("kind")!=kind or row.get("adapter")!=snap.adapter or row.get("observed_at")!=snap.observed_at:
        raise AdapterError("malformed",f"{kind} evidence is not bound")
    for key in required:
        expected=snap.models[0] if key=="model" and snap.models else (snap.sandbox_proof.get("worktree") if key=="worktree" and snap.sandbox_proof else getattr(snap,key,None))
        if row.get(key)!=expected:raise AdapterError("malformed",f"{kind} evidence {key} mismatch")
    return row
def _validate_cli_evidence(snap,reference):
    """Return a typed rejection for CLI evidence, or ``None`` when bound.

    CLI capability claims are deliberately narrow: the five fixture rows are
    the complete snapshot, each row is versioned and bound to this adapter and
    observation, and the observation cannot be stale or from the future.
    """
    required={snap.endpoint_ref,snap.health_evidence_ref,snap.model_evidence_ref,
              snap.executable_evidence_ref,snap.sandbox_evidence_ref}
    if None in required or len(required)!=5 or len(snap.evidence_refs)!=5:
        return RejectionReason.CAPABILITY
    by_id={row.get("id"):row for row in snap.evidence_refs}
    if set(by_id)!=required:
        return RejectionReason.CAPABILITY
    expected={
        snap.endpoint_ref:("endpoint",{"endpoint_ref":snap.endpoint_ref,"model":snap.models[0] if snap.models else None}),
        snap.health_evidence_ref:("health",{"health":snap.health,"endpoint_ref":snap.endpoint_ref}),
        snap.model_evidence_ref:("model",{"model":snap.models[0] if snap.models else None,"endpoint_ref":snap.endpoint_ref}),
        snap.executable_evidence_ref:("executable",{"executable":snap.executable}),
        snap.sandbox_evidence_ref:("sandbox",{"sandbox":snap.sandbox,"worktree":snap.sandbox_proof.get("worktree") if snap.sandbox_proof else None}),
    }
    for row in snap.evidence_refs:
        kind,fields=expected.get(row.get("id"),(None,{}))
        if kind is None or set(row)!={"id","sha256","kind","adapter","observed_at","version",*fields}:
            return RejectionReason.CAPABILITY
        try:observed=contracts.parse_time(row.get("observed_at"))
        except Exception:return RejectionReason.CAPABILITY
        delta=(reference-observed).total_seconds()
        if delta < -CLI_EVIDENCE_MAX_FUTURE_SKEW_SECONDS:return RejectionReason.FUTURE
        if delta > min(CLI_EVIDENCE_MAX_AGE_SECONDS,snap.max_freshness_seconds):return RejectionReason.STALE
        if row.get("kind")!=kind or row.get("adapter")!=snap.adapter or row.get("observed_at")!=snap.observed_at:
            return RejectionReason.CAPABILITY
        if row.get("version")!=CLI_EVIDENCE_VERSION or row.get("version")!=snap.version:
            return RejectionReason.CAPABILITY
        if any(row.get(key)!=value for key,value in fields.items()):
            return RejectionReason.CAPABILITY
    return None
def _validate_provenance(spec,snap):
    if spec.name=="qwen-local":
        ids=(snap.endpoint_ref,snap.health_evidence_ref,snap.model_evidence_ref,snap.executable_evidence_ref,snap.sandbox_evidence_ref)
        if not snap.measured_health or any(x is None for x in ids) or len(set(ids))!=5:return False
        _claim(snap.endpoint_ref,snap.evidence_refs,"endpoint",snap,required=("endpoint_ref","version","model"))
        _claim(snap.health_evidence_ref,snap.evidence_refs,"health",snap,required=("health","endpoint_ref"))
        _claim(snap.model_evidence_ref,snap.evidence_refs,"model",snap,required=("model","version","endpoint_ref"))
        _claim(snap.executable_evidence_ref,snap.evidence_refs,"executable",snap,required=("executable","version"))
        _claim(snap.sandbox_evidence_ref,snap.evidence_refs,"sandbox",snap,required=("sandbox","worktree"))
    elif spec.name=="hermes-api":
        if not snap.endpoint_ref or not snap.credential_ref:return False
        if snap.endpoint_ref==snap.credential_ref:return False
        _claim(snap.endpoint_ref,snap.evidence_refs,"endpoint",snap,required=("endpoint_ref","version","model"))
        _claim(snap.credential_ref,snap.evidence_refs,"credential",snap,required=("endpoint_ref",))
    elif spec.name=="opencode-openrouter":
        if not snap.endpoint_ref or not snap.executable_evidence_ref or not snap.sandbox_evidence_ref or snap.sandbox_proof is None:return False
        _claim(snap.endpoint_ref,snap.evidence_refs,"endpoint",snap,required=("endpoint_ref","version","model"))
        _claim(snap.executable_evidence_ref,snap.evidence_refs,"executable",snap,required=("executable","version"))
        _claim(snap.sandbox_evidence_ref,snap.evidence_refs,"sandbox",snap,required=("sandbox","worktree"))
    return True
def _worktree(v):
    v=_s(v,"worktree")
    if v=="<validated-worktree>":return v
    if not ((v.startswith("/") or re.match(r"^[A-Za-z]:[\\/]",v)) and ".." not in v) or any(c in v for c in ('"',"'",';','|','&','<','>',"\n","\r",chr(96))):raise AdapterError("malformed","unsafe worktree")
    return v
def _sandbox(v,refs,worktree=None):
    p=_obj(v,"sandbox_proof")
    if set(p)!={"kind","worktree","method","evidence_ref"} or p["kind"]!="enclosing-sandbox" or p["method"]!="host-enclosure":raise AdapterError("sandbox","enclosing sandbox proof required")
    _worktree(p["worktree"]);_ref(p["evidence_ref"],"sandbox proof evidence");_declared(p["evidence_ref"],refs,"sandbox")
    if worktree is not None and p["worktree"]!=worktree:raise AdapterError("sandbox","worktree not bound")
    return _freeze(p)

@dataclass(frozen=True)
class AdapterSpec:
    name:str;roles:tuple[str,...];capabilities:tuple[str,...];network:str;provider:str;billing:str;models:tuple[str,...];host:str;command:tuple[str,...]=();sandbox:str="";concurrency:int=1;metered:bool=False;secret_ref:str|None=None;executable:str="";auth:str="";availability:bool=True;enabled:bool=True;version:str="v1";quota:int=1;allowed_billing:tuple[str,...]=()
    @property
    def billing_basis(self):return self.billing
    def __post_init__(self):
        _s(self.name);r=_ss(self.roles,"roles",False)
        if not set(r)<=ROLES or self.network not in NETWORK or self.billing not in BILLING:raise AdapterError("malformed","spec enum")
        _ss(self.capabilities,"capabilities",False);_s(self.provider);_ss(self.models,"models");_s(self.host);_ss(self.command,"command");_s(self.sandbox,"sandbox",True);_i(self.concurrency,"concurrency",1);_b(self.metered,"metered");_s(self.executable,"executable",True);_s(self.auth);_b(self.availability,"availability");_b(self.enabled,"enabled");_s(self.version);_i(self.quota,"quota")
        if self.secret_ref is not None:_s(self.secret_ref)
        a=_ss(self.allowed_billing or (self.billing,),"allowed_billing",False)
        if not set(a)<=BILLING:raise AdapterError("malformed","allowed billing")
        for k,v in (("roles",r),("capabilities",_ss(self.capabilities,"capabilities",False)),("models",_ss(self.models,"models")),("command",_ss(self.command,"command")),("allowed_billing",a)):object.__setattr__(self,k,v)

@dataclass(frozen=True)
class CapabilitySnapshot:
    adapter:str;available:bool;enabled:bool;auth_proven:bool;observed_at:str;freshness_seconds:int=0;quota_remaining:int=0;concurrency_available:int=0;capabilities:tuple[str,...]=();roles:tuple[str,...]=();models:tuple[str,...]=();network:str="none";provider:str="";billing:str="";version:str="";health:str="unknown";max_freshness_seconds:int=300;expires_at:str|None=None;ttl_seconds:int|None=None;executable:str="";sandbox:str="";host:str="";auth:str="";measured_health:bool=False;included_pool_proven:bool=False;on_demand:bool=False;evidence_refs:tuple[Mapping[str,Any],...]=();endpoint_ref:str|None=None;credential_ref:str|None=None;health_evidence_ref:str|None=None;model_evidence_ref:str|None=None;executable_evidence_ref:str|None=None;sandbox_evidence_ref:str|None=None;sandbox_proof:Mapping[str,Any]|None=None
    @property
    def billing_basis(self):return self.billing
    def __post_init__(self):
        _s(self.adapter);_b(self.available,"available");_b(self.enabled,"enabled");_b(self.auth_proven,"auth_proven");_time(self.observed_at,"observed_at");_i(self.freshness_seconds,"freshness_seconds");_i(self.quota_remaining,"quota_remaining");_i(self.concurrency_available,"concurrency_available");caps=_ss(self.capabilities,"capabilities");roles=_ss(self.roles,"roles");models=_ss(self.models,"models")
        if not set(roles)<=ROLES or self.network not in NETWORK or self.billing not in BILLING:raise AdapterError("malformed","snapshot enum")
        _s(self.provider);_s(self.version);_s(self.health);_i(self.max_freshness_seconds,"max_freshness_seconds",1);_s(self.executable,"executable",True);_s(self.sandbox);_s(self.host);_s(self.auth)
        if self.ttl_seconds is not None:_i(self.ttl_seconds,"ttl_seconds",1)
        if self.expires_at is not None:_time(self.expires_at,"expires_at")
        if self.expires_at and contracts.parse_time(self.expires_at)<contracts.parse_time(self.observed_at):raise AdapterError("malformed","reversed interval")
        for n in ("measured_health","included_pool_proven","on_demand"):_b(getattr(self,n),n)
        refs=_refs(self.evidence_refs)
        for n in ("endpoint_ref","credential_ref","health_evidence_ref","model_evidence_ref","executable_evidence_ref","sandbox_evidence_ref"):
            if getattr(self,n) is not None:_ref(getattr(self,n),n)
        proof=_sandbox(self.sandbox_proof,refs) if self.sandbox_proof is not None else None
        for k,v in (("capabilities",caps),("roles",roles),("models",models),("evidence_refs",refs),("sandbox_proof",proof)):object.__setattr__(self,k,v)

@dataclass(frozen=True)
class NegotiationRequest:
    role:str;capabilities:tuple[str,...]=();model:str|None=None;network:str="none";metered_spend_cents:int=0;approval_digest:str|None=None;affinity:str|None=None;execution_mode:str="live";on_demand:bool=False
    def __post_init__(self):
        _s(self.role)
        if self.role not in ROLES:raise AdapterError("malformed","unknown role")
        object.__setattr__(self,"capabilities",_ss(self.capabilities,"capabilities"));
        if self.model is not None:_s(self.model,"model")
        if self.network not in NETWORK:raise AdapterError("malformed","network")
        _i(self.metered_spend_cents,"metered_spend_cents");
        if self.approval_digest is not None:_digest(self.approval_digest,"approval_digest")
        if self.affinity is not None:_s(self.affinity,"affinity")
        if not isinstance(self.execution_mode,str) or self.execution_mode not in MODES:raise AdapterError("malformed","execution mode")
        _b(self.on_demand,"on_demand")
@dataclass(frozen=True)
class NegotiationResult:
    adapter:AdapterSpec|None;accepted:bool;reason:RejectionReason|None=None;rejected:tuple[tuple[str,RejectionReason|None],...]=();snapshot:CapabilitySnapshot|None=None;request:NegotiationRequest|None=None;authority_snapshots:Mapping[str,CapabilitySnapshot]|None=None;reference_time:str|None=None;pause:bool=False;budget:Mapping[str,Any]|None=None;_trust:object|None=field(default=None,repr=False,compare=False)
    @property
    def rejection_trace(self):return self.rejected
    def __post_init__(self):
        try:
            if type(self.accepted) is not bool or (self.adapter is not None and self.adapter is not REGISTRY.get(self.adapter.name)):
                raise AdapterError("malformed","negotiation authority")
            if self.adapter is not None and not isinstance(self.adapter,AdapterSpec):raise AdapterError("malformed","negotiation adapter")
            if self.snapshot is not None and not isinstance(self.snapshot,CapabilitySnapshot):raise AdapterError("malformed","negotiation snapshot")
            if self.request is not None and not isinstance(self.request,NegotiationRequest):raise AdapterError("malformed","negotiation request")
            trace=tuple((str(n), reason if isinstance(reason,RejectionReason) or reason is None else RejectionReason(reason)) for n,reason in self.rejected)
            if self.accepted:
                if self.adapter is None or self.snapshot is None or self.request is None or not isinstance(self.authority_snapshots,Mapping) or self.reference_time is None or self.pause or self._trust is not _NEGOTIATION_TRUST:
                    raise AdapterError("malformed","accepted result lacks immutable authority")
                ref=_time(self.reference_time,"reference_time")
                amap={str(n):_snap(v) for n,v in self.authority_snapshots.items()}
                if not set(amap)<=set(NAMES) or amap.get(self.adapter.name)!=self.snapshot:raise AdapterError("malformed","snapshot authority mismatch")
                bud=_budget(self.budget) if self.budget is not None else None
                object.__setattr__(self,"authority_snapshots",_freeze(amap));object.__setattr__(self,"budget",_freeze(bud) if bud is not None else None)
            elif self.authority_snapshots is not None:object.__setattr__(self,"authority_snapshots",_freeze(self.authority_snapshots))
            if self.reference_time is not None:_time(self.reference_time,"reference_time")
            if type(self.pause) is not bool:raise AdapterError("malformed","pause")
            object.__setattr__(self,"rejected",trace)
        except AdapterError:raise
        except Exception as e:raise AdapterError("malformed","invalid negotiation result") from e

class _PacketAnchor:
    """Compatibility name; packet anchors are no longer constructible."""

    def __new__(cls, *args, **kwargs):
        raise AdapterError("binding", "packet anchors are factory-issued")


def _packet_anchor(packet, *, create=False):
    # Deliberately no longer attaches state to TaskPacket.  In particular, an
    # ordinary caller cannot mint authority for dataclasses.replace(packet).
    raise AdapterError("binding", "packet anchors are factory-issued")


class _PlanSeal:
    """Compatibility name; the factory seal is an opaque closure value."""

    def __new__(cls, *args, **kwargs):
        raise AdapterError("binding", "plan seals are factory-issued")


class _DispatchPlanType(type):
    def __setattr__(cls,name,value):
        if name=="_factory_check" and name in cls.__dict__:
            raise AttributeError("factory plan checker is immutable")
        super().__setattr__(name,value)


@dataclass(frozen=True)
class DispatchPlan(metaclass=_DispatchPlanType):
    adapter:str;packet_digest:str;assignment_digest:str;source_sha:str;budget_digest:str;grant_digest:str;worktree:str;argv:tuple[str,...];request:Mapping[str,Any];instruction_summary:str;evidence_refs:tuple[Mapping[str,Any],...]=();model:str="";execution_mode:str="live";endpoint_ref:str|None=None;credential_ref:str|None=None;sandbox_proof:Mapping[str,Any]|None=None;negotiation:NegotiationResult|None=None;packet_authority:Mapping[str,Any]|None=None;_trust:object|None=field(default=None,repr=False,compare=False);_seal:object|None=field(default=None,repr=False,compare=False)
    def __post_init__(self):
        if not isinstance(self.adapter,str) or self.adapter not in REGISTRY:raise AdapterError("binding","adapter not registered")
        if not isinstance(self.negotiation,NegotiationResult) or not self.negotiation.accepted or self.negotiation.adapter is not REGISTRY[self.adapter]:raise AdapterError("binding","plan negotiation authority invalid")
        _reprove_negotiation(self.negotiation)
        if self.negotiation.request.execution_mode!=self.execution_mode:raise AdapterError("binding","execution mode not negotiated")
        _digest(self.packet_digest,"packet_digest");_digest(self.assignment_digest,"assignment_digest");
        if not SHA.fullmatch(_s(self.source_sha,"source_sha")):raise AdapterError("malformed","source sha")
        _digest(self.budget_digest,"budget_digest");_digest(self.grant_digest,"grant_digest");wt=_worktree(self.worktree);argv=_argv(self.argv,self.adapter=="hermes-api");req=_obj(self.request,"request");summary=_s(self.instruction_summary,"instruction_summary");refs=_refs(self.evidence_refs);_safe({"request":req,"summary":summary,"refs":refs},"plan")
        bad={"--yolo","--force","--dangerously-skip-permissions","--api-key","--header","--trust","--auto-review","--config","--search"}
        if any(x in bad or any(x.startswith(y+"=") for y in bad) for x in argv):raise AdapterError("malformed","unsafe flag")
        if not isinstance(self.execution_mode,str) or self.execution_mode not in MODES:raise AdapterError("malformed","execution mode")
        _s(self.model,"model",True)
        if self.endpoint_ref is not None:_ref(self.endpoint_ref,"endpoint_ref")
        if self.credential_ref is not None:_ref(self.credential_ref,"credential_ref")
        authority=_obj(self.packet_authority,"packet authority")
        expected_authority={"packet_digest","assignment_digest","source_sha","budget_digest","grant_digest","adapter","execution_mode","model","worktree","endpoint_ref","credential_ref","context_digest","context_projection","authority_digest"}
        if set(authority)!=expected_authority or authority.get("authority_digest")!=contracts.canonical_digest({k:v for k,v in authority.items() if k!="authority_digest"}):raise AdapterError("binding","packet authority digest mismatch")
        projection=authority.get("context_projection")
        if not isinstance(projection,list) or authority.get("context_digest")!=hashlib.sha256(contracts.canonical_json(projection)).hexdigest():raise AdapterError("binding","packet context authority mismatch")
        for key,value in (("packet_digest",self.packet_digest),("assignment_digest",self.assignment_digest),("source_sha",self.source_sha),("budget_digest",self.budget_digest),("grant_digest",self.grant_digest),("adapter",self.adapter),("execution_mode",self.execution_mode),("model",self.model),("worktree",self.worktree),("endpoint_ref",self.endpoint_ref),("credential_ref",self.credential_ref)):
            if authority.get(key)!=value:raise AdapterError("binding",f"packet authority {key} mismatch")
        snap=self.negotiation.snapshot
        expected_endpoint=snap.endpoint_ref if self.adapter in {"hermes-api","opencode-openrouter","qwen-local"} else None
        expected_credential=snap.credential_ref if self.adapter=="hermes-api" else self.credential_ref if self.adapter=="opencode-openrouter" else None
        if self.endpoint_ref!=expected_endpoint or self.credential_ref!=expected_credential:raise AdapterError("binding","adapter refs are not negotiated")
        if self.adapter=="hermes-api":
            if argv or not self.endpoint_ref or not self.credential_ref or set(req)!={"endpoint_ref","credential_ref","packet_digest","assignment_digest","summary"}:raise AdapterError("malformed","invalid Hermes API plan")
            if req["endpoint_ref"]!=self.endpoint_ref or req["credential_ref"]!=self.credential_ref:raise AdapterError("binding","Hermes refs mismatch")
        else:
            if self.adapter=="opencode-openrouter":
                expected={"model","endpoint_ref","credential_ref","packet_digest","assignment_digest","summary"}
                if not self.endpoint_ref or not self.credential_ref or req.get("endpoint_ref")!=self.endpoint_ref or req.get("credential_ref")!=self.credential_ref:raise AdapterError("binding","OpenRouter refs mismatch")
            elif self.adapter=="qwen-local":
                expected={"model","packet_digest","assignment_digest","summary"}
                if self.credential_ref is not None or not self.endpoint_ref:raise AdapterError("malformed","Qwen endpoint ref required")
            else:
                expected={"model","packet_digest","assignment_digest","summary"}
                if self.endpoint_ref is not None or self.credential_ref is not None:raise AdapterError("malformed","unexpected CLI refs")
            if set(req)!=expected:raise AdapterError("malformed","invalid CLI plan")
            if req.get("model")!=self.model:raise AdapterError("binding","model mismatch")
        if req.get("packet_digest")!=self.packet_digest or req.get("assignment_digest")!=self.assignment_digest or req.get("summary")!=summary:raise AdapterError("binding","request mismatch")
        if self.adapter=="codex-cli":
            expected=("codex","exec","--json","--strict-config","--sandbox","workspace-write","--ask-for-approval","never","--ephemeral","-C",wt,"-")
            if argv!=expected:raise AdapterError("malformed","codex command does not match spec")
        elif self.adapter=="cursor-cli":
            expected=("cursor-agent","--print","--output-format","stream-json","--sandbox","enabled","--workspace",wt)
            if argv!=expected:raise AdapterError("malformed","cursor command does not match spec")
        elif self.adapter in {"opencode-openrouter","qwen-local"}:
            expected=("opencode","run","--format","json","--dir",wt,"--model",self.model,summary)
            if argv!=expected:raise AdapterError("malformed","OpenCode command does not match spec")
        proof=_sandbox(self.sandbox_proof,refs,worktree=wt) if self.adapter in {"opencode-openrouter","qwen-local"} else None
        for k,v in (("worktree",wt),("argv",argv),("request",_freeze(req)),("evidence_refs",refs),("sandbox_proof",proof),("packet_authority",_freeze(authority))):object.__setattr__(self,k,v)

SPECS=(AdapterSpec("codex-cli",("implementer","verifier"),("workspace-edit","jsonl"),"none","openai","subscription",("codex",),"local",("codex","exec"),"workspace-write",executable="codex",auth="oauth"),AdapterSpec("cursor-cli",("implementer","verifier"),("workspace-edit","structured-output"),"none","cursor","metered",("cursor",),"local",("cursor-agent",),"enabled",metered=True,executable="cursor-agent",auth="reviewed-manifest",allowed_billing=("metered","included","subscription")),AdapterSpec("hermes-api",("implementer","verifier"),("workspace-edit","api"),"provider-only","hermes","metered",("hermes",),"remote",(),"enclosing",metered=True,auth="credential-ref",secret_ref="credential_ref"),AdapterSpec("opencode-openrouter",("implementer","verifier"),("workspace-edit","api"),"provider-only","openrouter","metered",("opencode",),"remote",("opencode",),"enclosing",metered=True,executable="opencode",auth="credential-ref",secret_ref="credential_ref"),AdapterSpec("qwen-local",("implementer","verifier"),("workspace-edit","local"),"none","qwen","local",("qwen",),"local",("opencode","run"),"enclosing",executable="opencode",auth="none"))
REGISTRY=MappingProxyType({x.name:x for x in SPECS})
def adapter_registry():return REGISTRY
def _snap(v):
    if isinstance(v,CapabilitySnapshot):return v
    if isinstance(v,Mapping):
        try:return CapabilitySnapshot(**dict(v))
        except AdapterError:raise
        except Exception as e:raise AdapterError("malformed","snapshot") from e
    raise AdapterError("malformed","snapshot")
def _budget(v):
    if v is None:return None
    r=_obj(v,"budget")
    try:
        contracts.validate(r)
        if r.get("budget_digest")!=contracts.canonical_digest(r):raise AdapterError("malformed","budget digest mismatch")
    except Exception as e:raise AdapterError("malformed","budget") from e
    return r
def _why(spec,snap,req,bud,ref):
    obs=contracts.parse_time(snap.observed_at)
    if obs>ref:return RejectionReason.FUTURE
    if snap.expires_at and ref>contracts.parse_time(snap.expires_at):return RejectionReason.EXPIRED
    ttl=snap.ttl_seconds or snap.max_freshness_seconds
    if snap.freshness_seconds>snap.max_freshness_seconds or (not snap.expires_at and (ref-obs).total_seconds()>ttl):return RejectionReason.STALE
    if not snap.available or not spec.availability:return RejectionReason.LOCAL_UNAVAILABLE if spec.name=="qwen-local" else RejectionReason.ABSENT
    if not snap.enabled or not spec.enabled:return RejectionReason.DISABLED
    if snap.adapter!=spec.name:return RejectionReason.MALFORMED
    if snap.provider!=spec.provider:return RejectionReason.PROVIDER
    if snap.network!=spec.network:return RejectionReason.NETWORK
    if snap.sandbox!=spec.sandbox:return RejectionReason.SANDBOX
    if snap.executable!=spec.executable:return RejectionReason.EXECUTABLE
    if not snap.models or snap.health not in {"ok","healthy"}:return RejectionReason.LOCAL_UNAVAILABLE if spec.name=="qwen-local" else RejectionReason.ABSENT
    if set(snap.roles)!=set(spec.roles):return RejectionReason.ROLE
    if set(snap.capabilities)!=set(spec.capabilities):return RejectionReason.CAPABILITY
    if spec.name not in {"cursor-cli","hermes-api","opencode-openrouter","qwen-local"} and set(snap.models)!=set(spec.models):return RejectionReason.MODEL
    if snap.host!=spec.host:return RejectionReason.PROVIDER
    if snap.billing not in spec.allowed_billing:return RejectionReason.BILLING
    if not snap.auth_proven or snap.auth!=spec.auth:return RejectionReason.AUTH_UNPROVEN
    if snap.version!=spec.version:return RejectionReason.CAPABILITY
    if req.role not in spec.roles or req.role not in snap.roles:return RejectionReason.ROLE
    if not set(req.capabilities)<=set(spec.capabilities):return RejectionReason.CAPABILITY
    if req.network!=spec.network:return RejectionReason.NETWORK
    if req.model and req.model not in spec.models and req.model not in snap.models:return RejectionReason.MODEL
    if snap.quota_remaining<1 or snap.concurrency_available<1:return RejectionReason.QUOTA_EXHAUSTED
    metered=spec.metered and not(spec.name=="cursor-cli" and snap.billing in {"included","subscription"} and snap.included_pool_proven)
    if req.on_demand or snap.on_demand:return RejectionReason.METERED_NOT_APPROVED if metered else RejectionReason.BILLING
    if metered:
        if not bud or not bud.get("metered_spend_allowed") or bud.get("approval_digest")!=req.approval_digest or req.metered_spend_cents<=0:return RejectionReason.METERED_NOT_APPROVED
        if req.metered_spend_cents>bud.get("cost_limit_cents",-1) or req.metered_spend_cents>bud.get("remaining_cost_cents",-1) or req.metered_spend_cents>bud.get("calendar_month_ceiling_cents",-1) or req.metered_spend_cents>2000:return RejectionReason.OVERSHOOT
    elif req.metered_spend_cents:return RejectionReason.METERED_NOT_APPROVED
    if spec.name in {"codex-cli","cursor-cli"}:
        evidence_reason=_validate_cli_evidence(snap,ref)
        if evidence_reason is not None:return evidence_reason
    if not _validate_provenance(spec,snap):return RejectionReason.LOCAL_UNAVAILABLE if spec.name=="qwen-local" else RejectionReason.CAPABILITY
    return None
def negotiate(request,snapshots,*,reference_time=None,pause=False,budget=None):
    try:
        if not isinstance(request,NegotiationRequest) or reference_time is None or not isinstance(snapshots,Mapping):raise AdapterError("malformed")
        ref=contracts.parse_time(reference_time) if isinstance(reference_time,str) else reference_time
        if not isinstance(ref,_dt.datetime) or ref.tzinfo is None:raise AdapterError("malformed")
        bud=_budget(budget)
    except Exception:return NegotiationResult(None,False,RejectionReason.MALFORMED,tuple((n,RejectionReason.MALFORMED) for n in NAMES),request=request if isinstance(request,NegotiationRequest) else None)
    trace=[];eligible={};unknown=False
    for n in NAMES:
        if n not in snapshots:trace.append((n,RejectionReason.ABSENT));continue
        try:snap=_snap(snapshots[n]);reason=RejectionReason.PAUSE if pause else _why(REGISTRY[n],snap,request,bud,ref)
        except Exception:snap=None;reason=RejectionReason.MALFORMED
        if reason is None:eligible[n]=(REGISTRY[n],snap)
        trace.append((n,reason))
    for n in snapshots:
        if n not in REGISTRY:trace.append((str(n),RejectionReason.MALFORMED));unknown=True
    if unknown:eligible.clear()
    if pause:trace=[(n,RejectionReason.PAUSE) for n in NAMES]
    chosen=None if pause else (eligible.get(request.affinity) if request.affinity else None);blocked=bool(request.affinity and not chosen and not pause)
    if chosen is None and not pause and not request.affinity and eligible:chosen=next(eligible[n] for n in NAMES if n in eligible)
    authority={}
    for n in NAMES:
        if n in snapshots:
            try:authority[n]=_snap(snapshots[n])
            except Exception:pass
    return NegotiationResult(chosen[0] if chosen else None,bool(chosen),None if chosen else (RejectionReason.PAUSE if pause else (RejectionReason.AFFINITY_UNAVAILABLE if blocked else (trace[0][1] if trace else RejectionReason.ABSENT))),tuple(trace),chosen[1] if chosen else None,request,authority,reference_time,pause,bud,_NEGOTIATION_TRUST)
def _model(result,model):
    m=model or (result.request.model if result.request else None) or (result.snapshot.models[0] if result.snapshot and result.snapshot.models else None) or result.adapter.models[0]
    if model is not None and result.request and result.request.model and model!=result.request.model:raise AdapterError("model","model mismatch")
    if m not in result.adapter.models and not(result.snapshot and m in result.snapshot.models):raise AdapterError("model","model not negotiated")
    return m
def _reprove_negotiation(result):
    if not isinstance(result,NegotiationResult) or not result.accepted or result.pause or result.request is None or result.reference_time is None or result.authority_snapshots is None or result._trust is not _NEGOTIATION_TRUST:
        raise AdapterError("malformed","negotiation result is not trusted")
    try:again=negotiate(result.request,result.authority_snapshots,reference_time=result.reference_time,pause=False,budget=result.budget)
    except AdapterError:raise
    except Exception as e:raise AdapterError("malformed","negotiation reproof failed") from e
    if not again.accepted or again.adapter is not result.adapter or again.snapshot!=result.snapshot or again.request!=result.request:
        raise AdapterError("binding","negotiation authority changed")
    return again
def _reprove(result,packet):
    again=_reprove_negotiation(result)
    pb=_obj(packet["budget"],"packet budget")
    needs_budget=result.request.metered_spend_cents>0 or result.adapter.name in {"hermes-api","opencode-openrouter"}
    if pb.get("budget_digest")!=contracts.canonical_digest(pb) or result.budget is None and needs_budget:
        raise AdapterError("binding","task budget is not authorized")
    if result.budget is not None and _plain(result.budget)!=pb:
        raise AdapterError("binding","negotiated budget is not task budget")
    if result.budget is not None and (result.budget.get("task_id")!=packet["task"]["id"] or result.budget.get("task_digest")!=packet["task"]["task_digest"]):
        raise AdapterError("binding","budget task binding mismatch")
    return again
def _build_dispatch_plan_impl(packet,result,*,worktree="<validated-worktree>",model=None,execution_mode="live",endpoint_ref=None,credential_ref=None,expected_parent=None,expected_parent_digest=None,expected_lineage=None,_construct):
    if not isinstance(result,NegotiationResult):raise AdapterError("malformed","negotiation result required")
    if not isinstance(packet,kernel.TaskPacket):raise AdapterError("malformed","immutable task packet required")
    if not result.accepted or not result.adapter or not result.snapshot:raise AdapterError("malformed","rejected negotiation")
    try:kernel.validate_packet(packet,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage)
    except Exception as e:raise AdapterError("binding","invalid or untrusted packet anchor") from e
    if not isinstance(execution_mode,str) or execution_mode not in MODES:raise AdapterError("malformed","mode")
    _reprove(result,packet)
    if result.request.execution_mode!=execution_mode:raise AdapterError("binding","execution mode not negotiated")
    wt=_worktree(worktree);m=_model(result,model);task,assignment,budget,grant=(packet[k] for k in ("task","assignment","budget","grant"));summary="Execute only bounded acceptance gates; return a bounded public summary.";n=result.adapter.name;snap=result.snapshot;refs=snap.evidence_refs;proof=None
    if n=="codex-cli":argv=("codex","exec","--json","--strict-config","--sandbox","workspace-write","--ask-for-approval","never","--ephemeral","-C",wt,"-")
    elif n=="cursor-cli":argv=("cursor-agent","--print","--output-format","stream-json","--sandbox","enabled","--workspace",wt)
    elif n in {"opencode-openrouter","qwen-local"}:
        proof=_sandbox(snap.sandbox_proof,refs,worktree=wt);endpoint_ref=endpoint_ref or snap.endpoint_ref
        if not endpoint_ref:raise AdapterError("malformed","endpoint reference required")
        _declared(endpoint_ref,refs,"endpoint")
        _claim(endpoint_ref,refs,"endpoint",snap,required=("endpoint_ref","version","model"))
        if n=="opencode-openrouter":
            if not credential_ref:raise AdapterError("malformed","OpenRouter credential ref required")
            _ref(credential_ref,"credential_ref")
            _claim(credential_ref,refs,"credential",snap,required=("endpoint_ref",))
        elif credential_ref is not None:raise AdapterError("malformed","Qwen is credential-free")
        argv=("opencode","run","--format","json","--dir",wt,"--model",m,summary)
    else:argv=()
    if n=="hermes-api":
        if not endpoint_ref or not credential_ref:raise AdapterError("malformed","Hermes refs required")
        _claim(endpoint_ref,refs,"endpoint",snap,required=("endpoint_ref","version","model"))
        _claim(credential_ref,refs,"credential",snap,required=("endpoint_ref",))
        req={"endpoint_ref":_ref(endpoint_ref,"endpoint_ref"),"credential_ref":_ref(credential_ref,"credential_ref"),"packet_digest":packet.packet_digest,"assignment_digest":assignment["assignment_digest"],"summary":summary}
    else:
        if n=="opencode-openrouter" and not credential_ref:raise AdapterError("malformed","credential ref required")
        if n not in {"opencode-openrouter","qwen-local"} and (endpoint_ref is not None or credential_ref is not None):raise AdapterError("malformed","unexpected refs")
        req={"model":m,"packet_digest":packet.packet_digest,"assignment_digest":assignment["assignment_digest"],"summary":summary}
        if n=="opencode-openrouter": req.update(endpoint_ref=endpoint_ref,credential_ref=credential_ref)
    plan_endpoint=endpoint_ref if n in {"hermes-api","opencode-openrouter","qwen-local"} else None
    plan_credential=credential_ref if n in {"hermes-api","opencode-openrouter"} else None
    context_projection=_plain(packet["context"]);context_digest=hashlib.sha256(contracts.canonical_json(context_projection)).hexdigest()
    authority={"packet_digest":packet.packet_digest,"assignment_digest":assignment["assignment_digest"],"source_sha":task["source_sha"],"budget_digest":budget["budget_digest"],"grant_digest":grant["grant_digest"],"adapter":n,"execution_mode":execution_mode,"model":m,"worktree":wt,"endpoint_ref":plan_endpoint,"credential_ref":plan_credential,"context_digest":context_digest,"context_projection":context_projection}
    authority["authority_digest"]=contracts.canonical_digest(authority)
    return _construct((n,packet.packet_digest,assignment["assignment_digest"],task["source_sha"],budget["budget_digest"],grant["grant_digest"],wt,argv,req,summary,refs,m,execution_mode,plan_endpoint,plan_credential,proof,result,authority),packet,result)


def _make_dispatch_builder(implementation):
    """Close issuance state over the only plan-construction capability.

    The ledger is keyed by object identity and retains only weak references to
    live plans and packets.  A one-shot construction ticket is consumed by the
    dataclass initializer, so replace/copy/rebuilt plans cannot become issued.
    """
    pending={}
    issued={}
    original_post=DispatchPlan.__post_init__

    def consume(plan):
        token=plan._trust
        row=pending.pop(id(token),None)
        if row is None or row[0] is not token or row[3] is not plan._seal:
            raise AdapterError("binding","factory-issued dispatch plan required")
        if row[1] is not plan.negotiation or row[2] is not plan.packet_authority:
            raise AdapterError("binding","factory plan authority changed")
        key=id(plan)
        def drop(ref, key=key):
            current=issued.get(key)
            if current is not None and current[0] is ref:
                issued.pop(key,None)
        try:
            plan_ref=weakref.ref(plan,drop);packet_ref=weakref.ref(row[4])
        except TypeError as e:
            raise AdapterError("binding","factory plan is not weak-referenceable") from e
        issued[key]=(plan_ref,packet_ref,token,row[3])

    def post(plan):
        consume(plan)
        original_post(plan)

    def factory_check(plan,packet):
        row=issued.get(id(plan))
        if (row is None or row[0]() is not plan or row[1]() is not packet or
                plan._trust is not row[2] or plan._seal is not row[3]):
            raise AdapterError("binding","exact factory-issued plan and packet required")

    def construct(fields,packet,negotiation):
        token=object();seal=object()
        authority=fields[17]
        pending[id(token)]=(token,negotiation,authority,seal,packet)
        try:
            return DispatchPlan(*fields,_trust=token,_seal=seal)
        except Exception:
            pending.pop(id(token),None)
            raise

    DispatchPlan.__post_init__=post
    DispatchPlan._factory_check=factory_check

    def build_dispatch_plan(packet,result,*,worktree="<validated-worktree>",model=None,execution_mode="live",endpoint_ref=None,credential_ref=None,expected_parent=None,expected_parent_digest=None,expected_lineage=None):
        return implementation(packet,result,worktree=worktree,model=model,execution_mode=execution_mode,endpoint_ref=endpoint_ref,credential_ref=credential_ref,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage,_construct=construct)

    return build_dispatch_plan


build_dispatch_plan=_make_dispatch_builder(_build_dispatch_plan_impl)
del _make_dispatch_builder

def _signed(r):r[contracts.DIGEST_FIELD[r["kind"]]]=contracts.canonical_digest(r);return r
def _rid(prefix,p,t,d,a):return prefix+"-"+hashlib.sha256("\0".join((prefix,p,t,d,a)).encode()).hexdigest()[:48]
def _usage(v):
    v=_obj(v,"usage");keys={"tokens","input_tokens","output_tokens","wall_seconds","cost_cents"}
    if set(v)!=keys:raise AdapterError("malformed","usage fields")
    for k in keys:_i(v[k],"usage."+k)
    if v["tokens"]!=v["input_tokens"]+v["output_tokens"]:raise AdapterError("malformed","usage arithmetic")
    return {k:int(v[k]) for k in keys}
def _check_cps(packet,values,reference):
    if not isinstance(values,(list,tuple)) or not values:raise AdapterError("malformed","checkpoints required")
    out=[];ctx=hashlib.sha256(contracts.canonical_json(_plain(packet["context"]))).hexdigest()
    for value in values:
        cp=_obj(value,"checkpoint")
        try:contracts.validate(cp,reference_time=reference)
        except Exception as e:raise AdapterError("binding","invalid checkpoint") from e
        if cp.get("task_id")!=packet["task"]["id"] or cp.get("task_digest")!=packet["task"]["task_digest"] or cp.get("packet_digest")!=packet.packet_digest or cp.get("context_digest")!=ctx:raise AdapterError("binding","checkpoint anchor mismatch")
        if cp.get("checkpoint_digest")!=contracts.canonical_digest(cp):raise AdapterError("binding","checkpoint digest mismatch")
        out.append(cp)
    try:contracts.validate_checkpoint_chain(out)
    except Exception as e:raise AdapterError("binding","checkpoint chain invalid") from e
    return out
def _envelope(packet,assignment,grant,budget,adapter,delivery,run,mode,usage,output,cps,start,finish,reference):
    context=_plain(packet["context"]);context_digest=hashlib.sha256(contracts.canonical_json(context)).hexdigest()
    e={"packet_digest":packet.packet_digest,"task":_plain(packet["task"]),"task_digest":packet["task"]["task_digest"],"source_sha":packet["task"]["source_sha"],"context":context,"context_digest":context_digest,"assignment":_plain(assignment),"grant":_plain(grant),"budget":_plain(budget),"adapter":adapter,"delivery_id":delivery,"run_id":run,"execution_mode":mode,"usage":usage,"output":_plain(output),"checkpoints":cps,"started_at":start,"finished_at":finish,"reference_time":reference};_safe(e,"result envelope");return e
def _attach_plan(env,plan):
    """Attach the immutable plan authority to an envelope before hashing."""
    authority=_plain(plan.packet_authority)
    env["packet_authority"]=authority
    env["dispatch_plan"]=_plain({"adapter":plan.adapter,"worktree":plan.worktree,"argv_digest":hashlib.sha256("\0".join(plan.argv).encode()).hexdigest(),"request":plan.request,"instruction_summary":plan.instruction_summary,"model":plan.model,"endpoint_ref":plan.endpoint_ref,"credential_ref":plan.credential_ref,"sandbox_proof":plan.sandbox_proof,"budget_digest":plan.budget_digest,"grant_digest":plan.grant_digest,"packet_authority":authority})
    return env
def _authority_records(packet,expected_parent=None,expected_lineage=None):
    out=[];seen=set()
    def add(value):
        if not isinstance(value,Mapping):return
        row=_plain(value)
        for key in ("task","budget"):
            item=row.get(key)
            if isinstance(item,Mapping) and item.get("id") not in seen:
                out.append(item);seen.add(item.get("id"))
        prior=row.get("parent")
        if isinstance(prior,Mapping):add(prior)
    add(_plain(packet["parent"]))
    if expected_parent is not None:
        add(expected_parent.to_dict() if isinstance(expected_parent,kernel.TaskPacket) else expected_parent)
    if expected_lineage is not None:
        for anchor in expected_lineage:
            add(anchor.to_dict() if isinstance(anchor,kernel.TaskPacket) else anchor)
    return out
def _validate_plan_for_packet(packet,plan,expected_parent=None,expected_parent_digest=None,expected_lineage=None):
    if not isinstance(plan,DispatchPlan) or plan.negotiation is None:raise AdapterError("binding","accepted dispatch plan required")
    DispatchPlan._factory_check(plan,packet)
    try:rebuilt=build_dispatch_plan(packet,plan.negotiation,worktree=plan.worktree,model=plan.model,execution_mode=plan.execution_mode,endpoint_ref=plan.endpoint_ref,credential_ref=plan.credential_ref,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage)
    except AdapterError:raise
    except Exception as e:raise AdapterError("binding","plan reconstruction failed") from e
    if rebuilt!=plan:raise AdapterError("binding","dispatch plan changed")
    if plan.budget_digest!=packet["budget"]["budget_digest"] or plan.grant_digest!=packet["grant"]["grant_digest"] or plan.packet_digest!=packet.packet_digest or plan.assignment_digest!=packet["assignment"]["assignment_digest"] or plan.source_sha!=packet["task"]["source_sha"]:raise AdapterError("binding","dispatch plan authority mismatch")
    return rebuilt
def record_result(packet,*,delivery_id,run_id,adapter,execution_mode,started_at,finished_at,reference_time,current_source_sha,candidate_commit,output,usage,checkpoint_records,plan=None,status="succeeded",result_digest=None,expected_parent=None,expected_parent_digest=None,expected_lineage=None,hermetic_proof=None):
    try:
        kernel.validate_packet(packet,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage);_s(delivery_id,"delivery_id");_s(run_id,"run_id");_s(adapter,"adapter")
        if not ID.fullmatch(delivery_id) or not ID.fullmatch(run_id) or adapter not in REGISTRY:raise AdapterError("binding","identity invalid")
        if execution_mode not in MODES:raise AdapterError("malformed","mode")
        _time(started_at,"started_at");_time(finished_at,"finished_at");_time(reference_time,"reference_time");start,finish,reference=map(contracts.parse_time,(started_at,finished_at,reference_time));created=contracts.parse_time(packet["task"]["created_at"]);expires=contracts.parse_time(packet["task"]["expires_at"]) if packet["task"].get("expires_at") else None
        if not created<=start<=finish<=reference or reference<created or (expires and (finish>expires or reference>expires)):raise AdapterError("future","result outside task window")
        if _s(current_source_sha,"current_source_sha")!=packet["task"]["source_sha"]:raise AdapterError("stale-source","source changed")
        if execution_mode=="live":_validate_plan_for_packet(packet,plan,expected_parent,expected_parent_digest,expected_lineage)
        elif plan is not None:_validate_plan_for_packet(packet,plan,expected_parent,expected_parent_digest,expected_lineage)
        elif execution_mode!="hermetic" or output.get("execution_mode")!="hermetic" or hermetic_proof is not _HERMETIC_PROOF:raise AdapterError("binding","hermetic proof required")
        else:raise AdapterError("binding","accepted hermetic plan required")
        if plan is not None and plan.adapter!=adapter:raise AdapterError("binding","plan adapter mismatch")
        if plan is not None and plan.execution_mode!=execution_mode:raise AdapterError("binding","plan execution mode mismatch")
        commit=_s(candidate_commit,"candidate_commit")
        if not SHA.fullmatch(commit):raise AdapterError("malformed","commit")
        if status not in {"queued","running","succeeded","failed","cancelled","expired","rejected"}:raise AdapterError("malformed","status")
        out=_obj(output,"output");use=_usage(usage);cps=_check_cps(packet,checkpoint_records,reference_time);task,assignment,budget,grant=(_plain(packet[k]) for k in ("task","assignment","budget","grant"));env=_envelope(packet,assignment,grant,budget,adapter,delivery_id,run_id,execution_mode,use,out,cps,started_at,finished_at,reference_time)
        if plan is not None:_attach_plan(env,plan)
        _safe(env,"result envelope");actual=hashlib.sha256(contracts.canonical_json(env)).hexdigest()
        if result_digest is None or result_digest!=actual:raise AdapterError("result-digest","result digest mismatch")
        cid=_rid("candidate",packet.packet_digest,task["task_digest"],delivery_id,adapter);eid=_rid("evidence",packet.packet_digest,task["task_digest"],delivery_id,adapter);rid=_rid("receipt",packet.packet_digest,task["task_digest"],delivery_id,adapter);ud=hashlib.sha256(contracts.canonical_json(use)).hexdigest()
        cand=_signed({"kind":"candidate","id":cid,"task_digest":task["task_digest"],"candidate_id":cid,"candidate_commit":commit,"result_digest":result_digest,"result_envelope":env});evid=_signed({"kind":"evidence","id":eid,"task_id":task["id"],"task_digest":task["task_digest"],"packet_digest":packet.packet_digest,"assignment_digest":assignment["assignment_digest"],"source_sha":current_source_sha,"adapter":adapter,"execution_mode":execution_mode,"result_digest":result_digest,"result_envelope_digest":result_digest,"usage_digest":ud,"observed_at":reference_time,"delivery_id":delivery_id,"run_id":run_id});rec=_signed({"schema_version":2,"kind":"receipt","id":rid,"task_id":task["id"],"task_digest":task["task_digest"],"assignment_digest":assignment["assignment_digest"],"adapter":adapter,"candidate_id":cid,"candidate_commit":commit,"result_digest":result_digest,"status":status,"usage":use,"checkpoint_digests":[x["checkpoint_digest"] for x in cps],"started_at":started_at,"finished_at":finished_at,"receipt_digest":""});records=_authority_records(packet,expected_parent,expected_lineage)+[task,budget,grant,assignment,*cps,cand,evid,rec];contracts.validate_cross_records(records,reference_time=reference_time);bd=hashlib.sha256(contracts.canonical_json(records)).hexdigest();authority=_plain(plan.packet_authority) if plan is not None else None;return _freeze({"packet_digest":packet.packet_digest,"task_digest":task["task_digest"],"source_sha":task["source_sha"],"assignment_digest":assignment["assignment_digest"],"grant_digest":grant["grant_digest"],"budget_digest":budget["budget_digest"],"adapter":adapter,"delivery_id":delivery_id,"run_id":run_id,"execution_mode":execution_mode,"reference_time":reference_time,"candidate":cand,"evidence":evid,"receipt":rec,"checkpoints":cps,"task":task,"budget":budget,"grant":grant,"assignment":assignment,"packet_authority":authority,"records":records,"result_envelope":env,"result_digest":result_digest,"usage_digest":ud,"bundle_digest":bd})
    except AdapterError:raise
    except Exception as e:raise AdapterError("malformed","result rejected") from e
def _revalidate(bundle, packet=None, plan=None, *, expected_parent=None, expected_parent_digest=None, expected_lineage=None):
    """Revalidate a result against live trusted anchors supplied by the caller.

    Persisted JSON is not self-authenticating: the immutable packet and its
    factory-bound dispatch plan are deliberately required at this boundary.
    """
    if not isinstance(packet,kernel.TaskPacket) or not isinstance(plan,DispatchPlan):
        raise AdapterError("binding","trusted packet and dispatch plan required")
    try:
        kernel.validate_packet(packet,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage)
        _validate_plan_for_packet(packet,plan,expected_parent,expected_parent_digest,expected_lineage)
    except AdapterError:raise
    except Exception as e:raise AdapterError("binding","external authority anchor invalid") from e
    v=_plain(bundle);_safe(v,"bundle");records=v.get("records")
    if not isinstance(records,list) or not records:raise AdapterError("malformed","bundle records")
    try:contracts.validate_cross_records(records,reference_time=v.get("reference_time"))
    except Exception as e:raise AdapterError("malformed","bundle records invalid") from e
    bykind={}
    for row in records:
        if isinstance(row,Mapping) and row.get("kind") in {"task","budget","capability_grant","assignment","checkpoint","candidate","evidence","receipt"}:
            bykind.setdefault(row["kind"],[]).append(row)
    env=v.get("result_envelope");_safe(env,"result envelope")
    if not isinstance(env,Mapping):raise AdapterError("duplicate-conflict","result envelope missing")
    def one(kind,predicate=None):
        vals=[x for x in bykind.get(kind,[]) if predicate is None or predicate(x)]
        if len(vals)!=1:raise AdapterError("duplicate-conflict",f"bundle {kind} ambiguous")
        return vals[0]
    task=one("task",lambda x:x.get("task_digest")==env.get("task_digest"));budget=one("budget",lambda x:x.get("budget_digest")==env.get("budget",{}).get("budget_digest"));grant=one("capability_grant",lambda x:x.get("grant_digest")==env.get("grant",{}).get("grant_digest"));assignment=one("assignment",lambda x:x.get("assignment_digest")==env.get("assignment",{}).get("assignment_digest"));candidate=one("candidate");evidence=one("evidence");receipt=one("receipt")
    if not isinstance(env,Mapping) or candidate.get("result_envelope")!=env:raise AdapterError("duplicate-conflict","candidate envelope mismatch")
    expected_packet={k:_plain(packet[k]) for k in ("task","budget","grant","assignment")}
    if (env.get("packet_digest")!=packet.packet_digest or
            any(env.get(k)!=value for k,value in expected_packet.items()) or
            env.get("adapter")!=plan.adapter or env.get("execution_mode")!=plan.execution_mode):
        raise AdapterError("duplicate-conflict","external packet authority mismatch")
    rd=hashlib.sha256(contracts.canonical_json(env)).hexdigest();bd=hashlib.sha256(contracts.canonical_json(records)).hexdigest()
    checks=(("candidate",candidate),("evidence",evidence),("receipt",receipt))
    for kind,row in checks:
        if row.get(contracts.DIGEST_FIELD[kind])!=contracts.canonical_digest(row):raise AdapterError("duplicate-conflict",f"{kind} digest mismatch")
    if v.get("bundle_digest")!=bd or v.get("result_digest")!=rd or candidate.get("result_digest")!=rd or candidate.get("candidate_id")!=candidate.get("id"):
        raise AdapterError("duplicate-conflict","bundle digest mismatch")
    if evidence.get("result_digest")!=rd or evidence.get("result_envelope_digest")!=rd or evidence.get("usage_digest")!=hashlib.sha256(contracts.canonical_json(env.get("usage"))).hexdigest():raise AdapterError("duplicate-conflict","evidence envelope mismatch")
    if not all(v.get(key)==env.get(key) for key in ("delivery_id","run_id","execution_mode","reference_time")):raise AdapterError("duplicate-conflict","outer envelope binding mismatch")
    if not all(evidence.get(key)==env.get(key) for key in ("delivery_id","run_id","execution_mode")) or evidence.get("observed_at")!=env.get("reference_time"):raise AdapterError("duplicate-conflict","evidence binding mismatch")
    expected_outer={"packet_digest":env.get("packet_digest"),"task_digest":task.get("task_digest"),"source_sha":task.get("source_sha"),"assignment_digest":assignment.get("assignment_digest"),"grant_digest":grant.get("grant_digest"),"budget_digest":budget.get("budget_digest"),"adapter":env.get("adapter")}
    if any(v.get(key)!=value for key,value in expected_outer.items()) or env.get("task_digest")!=task.get("task_digest") or env.get("source_sha")!=task.get("source_sha") or env.get("adapter")!=evidence.get("adapter") or env.get("adapter")!=receipt.get("adapter"):raise AdapterError("duplicate-conflict","task envelope binding mismatch")
    if v.get("task")!=task or v.get("budget")!=budget or v.get("grant")!=grant or v.get("assignment")!=assignment or v.get("candidate")!=candidate or v.get("evidence")!=evidence or v.get("receipt")!=receipt:raise AdapterError("duplicate-conflict","outer records mismatch")
    authority=v.get("packet_authority")
    if not isinstance(authority,Mapping):authority=env.get("packet_authority")
    if not isinstance(authority,Mapping) or env.get("packet_authority")!=authority:raise AdapterError("duplicate-conflict","packet authority missing")
    if authority != _plain(plan.packet_authority):raise AdapterError("duplicate-conflict","dispatch plan authority mismatch")
    expected_authority={"packet_digest","assignment_digest","source_sha","budget_digest","grant_digest","adapter","execution_mode","model","worktree","endpoint_ref","credential_ref","context_digest","context_projection","authority_digest"}
    if set(authority)!=expected_authority or authority.get("authority_digest")!=contracts.canonical_digest({k:x for k,x in authority.items() if k!="authority_digest"}):raise AdapterError("duplicate-conflict","packet authority digest mismatch")
    projection=authority.get("context_projection")
    if not isinstance(projection,list) or authority.get("context_digest")!=hashlib.sha256(contracts.canonical_json(projection)).hexdigest():raise AdapterError("duplicate-conflict","packet context authority mismatch")
    if any(authority.get(key)!=value for key,value in {"packet_digest":env.get("packet_digest"),"assignment_digest":assignment.get("assignment_digest"),"source_sha":task.get("source_sha"),"budget_digest":budget.get("budget_digest"),"grant_digest":grant.get("grant_digest"),"adapter":env.get("adapter"),"execution_mode":env.get("execution_mode")}.items()):raise AdapterError("duplicate-conflict","packet authority binding mismatch")
    context=env.get("context")
    expected_context=_plain(packet["context"])
    expected_context_digest=hashlib.sha256(contracts.canonical_json(expected_context)).hexdigest()
    if (context!=expected_context or context!=projection or
            env.get("context_digest")!=expected_context_digest or
            env.get("context_digest")!=authority.get("context_digest") or
            not isinstance(env.get("context_digest"),str) or not HEX64.fullmatch(env.get("context_digest"))):
        raise AdapterError("duplicate-conflict","context anchor mismatch")
    expected_dispatch={"adapter":plan.adapter,"worktree":plan.worktree,
        "argv_digest":hashlib.sha256("\0".join(plan.argv).encode()).hexdigest(),
        "request":_plain(plan.request),"instruction_summary":plan.instruction_summary,
        "model":plan.model,"endpoint_ref":plan.endpoint_ref,"credential_ref":plan.credential_ref,
        "sandbox_proof":_plain(plan.sandbox_proof) if plan.sandbox_proof is not None else None,
        "budget_digest":plan.budget_digest,"grant_digest":plan.grant_digest,
        "packet_authority":_plain(plan.packet_authority)}
    if env.get("dispatch_plan")!=expected_dispatch:
        raise AdapterError("duplicate-conflict","dispatch plan binding mismatch")
    cps=v.get("checkpoints")
    if not isinstance(cps,list) or cps!=bykind.get("checkpoint",[]) or [x.get("checkpoint_digest") for x in cps]!=receipt.get("checkpoint_digests"):raise AdapterError("duplicate-conflict","checkpoint binding mismatch")
    try:contracts.validate_checkpoint_chain(cps)
    except Exception as e:raise AdapterError("duplicate-conflict","checkpoint chain invalid") from e
    for cp in cps:
        if (cp.get("task_id")!=task.get("id") or cp.get("task_digest")!=task.get("task_digest") or cp.get("packet_digest")!=env.get("packet_digest") or cp.get("context_digest")!=env.get("context_digest") or cp.get("checkpoint_digest")!=contracts.canonical_digest(cp)):
            raise AdapterError("duplicate-conflict","checkpoint anchor mismatch")
    if candidate.get("candidate_commit")!=receipt.get("candidate_commit") or candidate.get("candidate_id")!=receipt.get("candidate_id") or evidence.get("assignment_digest")!=assignment.get("assignment_digest") or receipt.get("assignment_digest")!=assignment.get("assignment_digest"):raise AdapterError("duplicate-conflict","assignment binding mismatch")
    if candidate.get("id")!=_rid("candidate",env.get("packet_digest"),task.get("task_digest"),env.get("delivery_id"),env.get("adapter")) or evidence.get("id")!=_rid("evidence",env.get("packet_digest"),task.get("task_digest"),env.get("delivery_id"),env.get("adapter")) or receipt.get("id")!=_rid("receipt",env.get("packet_digest"),task.get("task_digest"),env.get("delivery_id"),env.get("adapter")):raise AdapterError("duplicate-conflict","deterministic result id mismatch")
    return v,bd,rd
def deduplicate_result(bundle,previous,packet=None,plan=None,*,expected_parent=None,expected_parent_digest=None,expected_lineage=None):
    if not isinstance(bundle,Mapping):raise AdapterError("malformed","bundle is not object")
    cur,bd,rd=_revalidate(bundle,packet,plan,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage);delivery=cur.get("delivery_id")
    if not isinstance(delivery,str):raise AdapterError("malformed","delivery")
    try:vals=[] if previous is None else [previous] if isinstance(previous,Mapping) and "delivery_id" in previous else list(previous.values()) if isinstance(previous,Mapping) else list(previous)
    except Exception as e:raise AdapterError("malformed","previous results") from e
    for old in vals:
        if isinstance(old,Mapping) and old.get("delivery_id")==delivery:
            _,ob,or_= _revalidate(old,packet,plan,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage)
            if (ob,or_)==(bd,rd):return old
            raise AdapterError("duplicate-conflict","delivery conflict")
    return _freeze(cur)
duplicate_result=deduplicate_result;check_duplicate=deduplicate_result
def fake_completion(packet,authority,*,delivery_id=None,reference_time="2026-08-31T12:00:00Z",expected_parent=None,expected_parent_digest=None,expected_lineage=None):
    try:
        if not isinstance(packet,kernel.TaskPacket):raise AdapterError("malformed","immutable task packet required")
        if isinstance(authority,DispatchPlan):
            if authority.execution_mode!="hermetic":raise AdapterError("binding","hermetic plan required")
            plan=_validate_plan_for_packet(packet,authority,expected_parent,expected_parent_digest,expected_lineage)
        elif isinstance(authority,NegotiationResult):
            if not authority.accepted or authority.request is None or authority.request.execution_mode!="hermetic":raise AdapterError("binding","hermetic negotiation required")
            plan=build_dispatch_plan(packet,authority,execution_mode="hermetic",expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage)
        else:raise AdapterError("binding","accepted hermetic authority required")
        adapter=plan.adapter
        if adapter not in {"codex-cli","cursor-cli"}:raise AdapterError("binding","fake completion is limited to hermetic CLI adapters")
        kernel.validate_packet(packet,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage);delivery=delivery_id or "fake-"+adapter
        if not ID.fullmatch(delivery):raise AdapterError("malformed","delivery")
        cp=_signed({"schema_version":2,"kind":"checkpoint","id":_rid("checkpoint",packet.packet_digest,packet["task"]["task_digest"],delivery,adapter),"task_id":packet["task"]["id"],"task_digest":packet["task"]["task_digest"],"packet_digest":packet.packet_digest,"context_digest":hashlib.sha256(contracts.canonical_json(_plain(packet["context"]))).hexdigest(),"state_digest":hashlib.sha256(b"hermetic-result").hexdigest(),"sequence":0,"prev_digest":None,"created_at":reference_time,"checkpoint_digest":""});out={"adapter":adapter,"summary":"bounded public summary","execution_mode":"hermetic"};use={"tokens":1,"input_tokens":1,"output_tokens":0,"wall_seconds":1,"cost_cents":0};env=_envelope(packet,_plain(packet["assignment"]),_plain(packet["grant"]),_plain(packet["budget"]),adapter,delivery,"run-"+adapter,"hermetic",use,out,[cp],reference_time,reference_time,reference_time);_attach_plan(env,plan);rd=hashlib.sha256(contracts.canonical_json(env)).hexdigest();return record_result(packet,delivery_id=delivery,run_id="run-"+adapter,adapter=adapter,execution_mode="hermetic",started_at=reference_time,finished_at=reference_time,reference_time=reference_time,current_source_sha=packet["task"]["source_sha"],candidate_commit="a"*40,output=out,usage=use,checkpoint_records=[cp],plan=plan,result_digest=rd,expected_parent=expected_parent,expected_parent_digest=expected_parent_digest,expected_lineage=expected_lineage,hermetic_proof=_HERMETIC_PROOF)
    except AdapterError:raise
    except Exception as e:raise AdapterError("malformed","fake completion rejected") from e
__all__=["AdapterError","AdapterSpec","CapabilitySnapshot","NegotiationRequest","NegotiationResult","DispatchPlan","RejectionReason","SPECS","REGISTRY","adapter_registry","negotiate","build_dispatch_plan","record_result","deduplicate_result","duplicate_result","check_duplicate","fake_completion"]
