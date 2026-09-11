"""o12 bounded retained-certificate check + adversarial controls: actual Q
invocations and the Q core done-mask preserve subprofile positions for
delegated calls only, including absence of guard-refused source-attest calls.

Per adapter prefix, from retained evidence only: q_profile equals the
independent subprofile construction; state['invocations'] is the chronological
tuple of exactly the calls Q executed (strictly increasing literal-schedule
positions, no source-handled action); core['done'] is the bitmask over
q_profile positions of exactly those invocations and outer done equals the
executed-prefix mask; rows[i].q_invoked / adapter_observation.decision agree
with the retained invocation delta and adapter decision; a refused
source-attest is absent from invocations and its mask bit is unset.

Anchors (representation only; no reducer is imported or executed):
a_domain.source_only/subprofile; a_audit.check 'Q completion exactly actual
invocations' and 'source-handled or refused call leaves entire Q core
unchanged'; adapter_traces.restore 'fixed Q occurrence positions' and
'retained actual Q invocation mask'; check.py audit_case 'actual Q invocation
and translation retained'; wave04/review-defects.json required controls (false
Q invocation on refused attest, dropped refusal, moved Q positions, tuple
loss; outer-hash rejection alone is not a semantic control).

Accounting/status: charge.take(1) before every inspected prefix, repetitions
included; audited_prefixes reports the same count. 'supported' requires every
supplied prefix verified plus >=1 delegated invocation and >=1 refused-attest
witness; 'counterexample' on a reachable semantic violation; 'unproved' on
unreconstructable evidence, exhausted charge or an unwitnessed clause;
'not_applicable' with no cases. Local finite-evidence result only; no global
theorem or scientific PASS.

run_controls deepcopy-mutates real supplied cases. Controls marked
hash_resealed recompute the trace sha256 chain so detection must reach
semantics; controls needing a genuinely reachable witness report skipped with
a missing-witness limitation when absent - never claimed detected.
observed_status 'counterexample' is semantic detection, 'unproved' is
evidence-binding detection; neither alone is an original-domain counterexample.
"""
import copy,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'experiments/v3/cut-source-overnight/batch-05'))
import semantic as rel
digest,exact=rel.digest,rel.exact
SOURCE_PREFIXES=('register:','attempt:','atomic:','append:','collect:','source:');SOURCE_EXACT=('append-lose-reply','collect-open')
class Violation(Exception):pass
class ChargeFault(Exception):pass
def source_only(a):k=a.split('@')[0];return k.startswith(SOURCE_PREFIXES) or k in SOURCE_EXACT
def expected_subprofile(p):
 a=tuple(x for x in p['actions'] if not source_only(x));return dict(p,actions=a,requires={x:() for x in a}),a
def apply_patch(current,event):
 for k,v in event['patch'].items():
  if k in ('core','journal'):current[k].update(copy.deepcopy(v))
  else:current[k]=copy.deepcopy(v)
def states(trace):
 if trace.get('side')!='adapter' or len(trace['events'])!=len(trace['actions']):raise ValueError('complete adapter visible event inventory')
 out,done=[copy.deepcopy(trace['initial'])],[]
 for action,event in zip(trace['actions'],trace['events']):
  if event['action']!=action or action in done or not set(trace['profile']['requires'][action])<=set(done):raise ValueError('literal occurrence and outer dependency')
  if digest(out[-1])!=event['before_sha256']:raise ValueError('history prestate binding')
  current=copy.deepcopy(out[-1]);apply_patch(current,event)
  if digest(current)!=event['after_sha256']:raise ValueError('history poststate binding')
  done.append(action);out.append(current)
 return out
def rehash(trace):
 current=copy.deepcopy(trace['initial'])
 for event in trace['events']:
  event['before_sha256']=digest(current);current=copy.deepcopy(current);apply_patch(current,event);event['after_sha256']=digest(current)
def audit_adapter(case,charge,counter):
 adapter=case['adapter'];profile=adapter['profile'];actions=tuple(adapter['actions']);rows=case['rows']
 if (tuple(case['source']['actions'])!=actions or not exact(case['source']['profile'],profile)
  or len(rows)!=len(actions) or len(case['prefixes'])!=len(actions)+1):
  raise ValueError('matched retained source/adapter/row/prefix inventory')
 expected,positions=expected_subprofile(profile)
 if not exact(adapter['q_profile'],expected):raise Violation('q_profile differs from independent subprofile positions')
 seq=states(adapter);facts={'invocations':0,'delegated':0,'refused_attest':0};witnesses=[]
 for i,st in enumerate(seq):
  try:charge.take(1)
  except Exception as e:raise ChargeFault(str(e))
  counter[0]+=1;inv=st['invocations']
  if type(inv) is not tuple or any(type(a) is not str for a in inv):raise Violation('non-tuple Q invocation list at prefix '+str(i))
  order=[]
  for a in inv:
   if a not in actions:raise Violation('invocation outside literal schedule at prefix '+str(i))
   order.append(actions.index(a))
  if order!=sorted(order) or len(set(order))!=len(order) or (order and order[-1]>=i):raise Violation('Q invocation order/uniqueness/prefix bound at prefix '+str(i))
  if any(source_only(a) for a in inv):raise Violation('source-handled action inside Q invocations at prefix '+str(i))
  if st['core']['done']!=sum(1<<positions.index(a) for a in inv):raise Violation('Q done-mask != invoked subprofile positions at prefix '+str(i))
  if st['done']!=sum(1<<profile['actions'].index(a) for a in actions[:i]):raise Violation('outer done mask != executed prefix at prefix '+str(i))
  facts['invocations']=len(inv)
  if not i:continue
  row,action=rows[i-1],actions[i-1]
  if row['index']!=i-1 or row['adapter_action']!=action or type(row['q_invoked']) is not bool:raise ValueError('chronological retained row binding')
  delta=len(inv)-len(seq[i-1]['invocations'])
  if delta not in (0,1) or row['q_invoked']!=(delta==1) or (delta==1 and inv[-1]!=action):raise Violation('row q_invoked disagrees with retained invocation delta')
  if row['adapter_observation']['decision']!=st['decision']:raise Violation('retained visible adapter decision changed')
  if action.split('@')[0]=='source-attest':
   bit=bool(st['core']['done']&(1<<positions.index(action)))
   witnesses.append(dict(prefix=i,action=action,decision=st['decision'],q_invoked=row['q_invoked'],in_invocations=action in inv,mask_bit=bit))
   if not row['q_invoked'] and (action in inv or bit):raise Violation('guard-refused source-attest kept in invocation/mask')
   facts['refused_attest']+=not row['q_invoked']
  facts['delegated']+=bool(row['q_invoked'])
 return dict(case=case['case'],prefixes=len(seq),facts=facts,attestation_witnesses=witnesses)
def inspect_cases(cases,charge):
 try:case_list=list(cases)
 except TypeError:case_list=[]
 if not case_list:return dict(status='not_applicable',observations=[],limitations=['no supplied adapter cases'],audited_prefixes=0)
 observations,limitations,counter=[],[],[0];counterexample=incomplete=False;delegated=refused=0
 for index,case in enumerate(case_list):
  try:item=audit_adapter(case,charge,counter)
  except Violation as e:counterexample=True;observations.append(dict(case=index,counterexample=str(e)))
  except ChargeFault as e:incomplete=True;limitations.append('charge exhausted during case '+str(index)+': '+str(e));break
  except (ValueError,KeyError,IndexError,TypeError,AttributeError) as e:incomplete=True;observations.append(dict(case=index,evidence_fault=str(e)))
  else:observations.append(item);delegated+=item['facts']['delegated'];refused+=item['facts']['refused_attest']
 if not counterexample and not incomplete:
  if not delegated:limitations.append('no actual delegated Q invocation witnessed; delegation clause unproved')
  if not refused:limitations.append('no guard-refused source-attest prefix witnessed; absence clause unproved')
 limitations.append('finite supplied-case audit only; no all-orders reachability or scientific PASS')
 status='counterexample' if counterexample else 'unproved' if incomplete or not delegated or not refused else 'supported'
 return dict(status=status,observations=observations,limitations=limitations,audited_prefixes=counter[0])
def run_controls(cases,inspect_cases,charge):
 case_list=list(cases);controls,limitations,found=[],[],{}
 try:baseline=inspect_cases(case_list,charge)
 except Exception as e:baseline={'status':'exception','limitations':[str(e)]}
 def locate(key,pred,need):
  if key not in found:
   found[key]=None
   for ci,case in enumerate(case_list):
    try:acts=case['adapter']['actions']
    except (KeyError,TypeError):continue
    for j,action in enumerate(acts):
     try:hit=pred(case,j,action)
     except (KeyError,IndexError,TypeError):hit=False
     if hit:found[key]=(ci,j);break
    if found[key]:break
   if found[key] is None:limitations.append('missing reachable witness: '+need)
  return found[key]
 def probe(label,at,mutate,target,resealed,needs_witness):
  entry=dict(control=label,target=target,hash_resealed=resealed,needs_reachable_witness=needs_witness)
  if at is None:entry.update(skipped=True,detected=None);controls.append(entry);return
  mutated=copy.deepcopy(case_list)
  try:mutate(mutated,*at)
  except Exception as e:entry.update(skipped=True,detected=None,detail='mutation failed: '+str(e));controls.append(entry);return
  try:out=inspect_cases(mutated,charge)
  except Exception as e:entry.update(detected=None,observed_status='exception',detail=str(e))
  else:
   status=out.get('status')
   if any('charge exhausted' in x for x in out.get('limitations',())):entry.update(detected=None,detail='inspection charge exhausted')
   else:entry.update(detected=status=='counterexample' or (status=='unproved' and baseline.get('status')!='unproved'),audited_prefixes=out.get('audited_prefixes'),observed=(out.get('observations') or [None])[0])
   entry['observed_status']=status
  controls.append(entry)
 refused=locate('refused',lambda c,j,a:a.split('@')[0]=='source-attest' and c['rows'][j]['q_invoked'] is False,'guard-refused source-attest')
 probe('false-q-invocation-on-refused-attest',refused,lambda m,ci,j:m[ci]['rows'][j].update(q_invoked=True),'rows[i].q_invoked',False,True)
 probe('refused-decision-rewritten-ok',refused,lambda m,ci,j:m[ci]['rows'][j]['adapter_observation'].update(decision='source-attest:ok'),'rows[i].adapter_observation.decision',False,True)
 probe('dropped-row-invocation-flag',locate('delegated',lambda c,j,a:c['rows'][j]['q_invoked'] is True,'actual delegated Q call'),lambda m,ci,j:m[ci]['rows'][j].update(q_invoked=False),'rows[i].q_invoked',False,True)
 def phantom(m,ci,j):
  t=m[ci]['adapter'];t['events'][j]['patch']['invocations']=states(t)[j]['invocations']+(t['actions'][j],);rehash(t)
 probe('source-handled-action-invoked',locate('source',lambda c,j,a:source_only(a),'source-handled event'),phantom,'events[i].patch.invocations',True,False)
 def extra_bit(m,ci,j):
  t=m[ci]['adapter'];pos=expected_subprofile(t['profile'])[1];done=states(t)[j+1]['core']['done']
  bit=next((b for b in range(len(pos)) if not done&(1<<b)),len(pos))
  t['events'][j]['patch'].setdefault('core',{})['done']=done|(1<<bit);rehash(t)
 probe('mask-bit-without-invocation',(0,0) if case_list and case_list[0].get('adapter',{}).get('events') else None,extra_bit,'events[i].patch.core.done',True,False)
 def drop_invocation(m,ci,j):
  t=m[ci]['adapter'];t['events'][j]['patch']['invocations']=t['events'][j]['patch']['invocations'][:-1];rehash(t)
 probe('dropped-invocation-entry',locate('invoked',lambda c,j,a:len(c['adapter']['events'][j]['patch'].get('invocations',()))>0,'invocation-retaining event'),drop_invocation,'events[i].patch.invocations',True,True)
 probe('q-profile-positions-reversed',(0,0) if case_list else None,lambda m,ci,j:m[ci]['adapter']['q_profile'].update(actions=tuple(reversed(m[ci]['adapter']['q_profile']['actions']))),'q_profile.actions',False,False)
 def swap_invocations(m,ci,j):
  p=m[ci]['adapter']['events'][j]['patch'];inv=p['invocations'];p['invocations']=inv[:-2]+(inv[-1],inv[-2]);rehash(m[ci]['adapter'])
 probe('swapped-invocation-order',locate('multi',lambda c,j,a:len(c['adapter']['events'][j]['patch'].get('invocations',()))>1,'prefix retaining >=2 invocations'),swap_invocations,'events[i].patch.invocations',True,True)
 return dict(cases=len(case_list),baseline_status=baseline.get('status'),baseline_audited_prefixes=baseline.get('audited_prefixes'),controls=controls,limitations=limitations)
