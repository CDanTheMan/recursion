"""o05 retained-evidence controls: collect-open capture + exact stale boundary.
Anchors (unchanged originals; representation reference only, never imported/run):
  s_inclusive.py / s_audit.py collect-open, collect:i, source-attest branches;
  guard_audit.py adapter ledger patches; a_domain.view overlay dict(core,**journal).
Obligation re-derived from retained typed fields, not from any reducer: a
successful collect-open writes collection=(source_generation, source_revision,
registration, attempts, len(append_log)) and resets collected=(); collect:i
admits only 0<=i<min(collection[4],len(append_log)) unduplicated indices copying
append_log[i]; attestation staleness is exactly collection[:2] !=
(source_generation, source_revision) given a cut_delivery. Fresh attestation
refusal subtypes (inventory/registry) are not re-derived: they need original
fixture bytes. Accounting: inspect_cases calls charge.take(1) before each of
len(actions)+1 prefixes per case; every repetition counts. run_controls adds no
charge; it forwards charge into each inspect_cases call. No reducer, guard,
inventory or boundary helper executes; detections are field-semantic (outer
digests never recomputed). 'counterexample' marks inconsistent retained
evidence; only violations in unmodified executed cases are original-domain
counterexamples. Controls needing a genuinely reachable witness (refused
collect-open, stale attestation) report missing-witness, never fabricate.
"""
import copy

CAP=('collection','collected')
ALLF=('registration','attempts','append_log','append_receipts','append_reply',
 'source_revision','source_generation','attestation','staged_source','selected_source')+CAP
KEYS=('patch','changes','updates','delta','fields','state','after','post','next','snapshot')
HINTS=('journal','core','decision','done','registration','attempts','source_revision')

def _ledger(s):
    return dict(s['core'],**s['journal']) if type(s.get('journal')) is dict and type(s.get('core')) is dict else s
def _eq(a,b):
    if type(a) is not type(b): return False
    if isinstance(a,dict): return set(a)==set(b) and all(_eq(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)): return len(a)==len(b) and all(_eq(x,y) for x,y in zip(a,b))
    return a==b
def _js(x):
    if isinstance(x,dict): return {str(k):_js(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [_js(v) for v in x]
    return x if x is None or type(x) in (str,int,bool,float) else repr(x)
def _post(prev,ev):
    if type(ev) is not dict: raise ValueError('non-dict retained event')
    patch=next((ev[k] for k in KEYS if type(ev.get(k)) is dict),None)
    if patch is None: patch={k:v for k,v in ev.items() if k in prev}
    if not patch: raise ValueError('event holds no state or patch')
    n=copy.deepcopy(prev); n.update(copy.deepcopy(patch)); return n
def _states(tr):
    out=[copy.deepcopy(tr['initial'])]
    for ev in tr['events']: out.append(_post(out[-1],ev))
    return out

def _frag(pre,post,dec,a):
    k=a.split('@')[0]; exp,forbid,patch=None,(),{}
    if k=='collect-open':
        if pre['registration']:
            exp=k+':ok'; patch={'collection':(pre['source_generation'],pre['source_revision'],
                pre['registration'],pre['attempts'],len(pre['append_log'])),'collected':()}
        else: exp=k+':no-registration'
    elif k.startswith('collect:'):
        i=int(k.split(':')[1]); c=pre['collection']
        if not c or not 0<=i<min(c[4],len(pre['append_log'])): exp=k+':outside-captured-cut'
        elif any(j==i for j,_ in pre['collected']): exp=k+':duplicate-collection'
        else: exp=k+':ok'; patch={'collected':tuple(sorted(pre['collected']+((i,pre['append_log'][i]),)))}
    elif k=='source-attest':
        c,name=pre['collection'],pre['cut_delivery']
        if not c or not name: exp=k+':no-captured-source'
        elif len(c)<2 or not (_eq(c[0],pre['source_generation']) and _eq(c[1],pre['source_revision'])):
            exp=k+':stale-collection'
        else:
            forbid=(k+':stale-collection',k+':no-captured-source')
            if dec==k+':ok': patch={'attestation':(c[0],c[1],name)}
    v=[('decision',exp,dec)] if exp is not None and dec!=exp else []
    if dec in forbid: v.append(('decision','non-stale verdict',dec))
    for f,w in patch.items():
        if not _eq(post.get(f),w): v.append(('write-'+f,w,post.get(f)))
    keep=ALLF if k=='collect-open' or k=='source-attest' or k.startswith('collect:') else CAP
    for f in keep:
        if f not in patch and not _eq(post.get(f),pre.get(f)):
            v.append(('keep-'+f,pre.get(f),post.get(f)))
    return [{'kind':t[0],'expected':_js(t[1]),'observed':_js(t[2])} for t in v]

def inspect_cases(cases,charge):
    obs,lim=[],[]; audited=relevant=viol=failed=unver=0
    for case in cases:
        try:
            name=case.get('case'); acts=list(case['source']['actions'])
            ss,aa=_states(case['source']),_states(case['adapter'])
            if acts!=list(case['adapter']['actions']) or len(ss)!=len(aa)!=len(acts)+1:
                raise ValueError('trace cardinality mismatch')
        except Exception as e:
            failed+=1; lim.append('case not auditable: %.140s'%(e,)); continue
        rows=case.get('rows') or ()
        for i in range(len(ss)):
            charge.take(1); audited+=1; sl,al=_ledger(ss[i]),_ledger(aa[i])
            if not _eq(sl.get('collection'),al.get('collection')):
                viol+=1; obs.append({'case':name,'prefix':i,'kind':'capture-side-disagreement',
                    'expected':_js(sl.get('collection')),'observed':_js(al.get('collection'))})
            if i==0:
                for side,l in (('source',sl),('adapter',al)):
                    for f in CAP:
                        if not _eq(l.get(f),()):
                            viol+=1; obs.append({'case':name,'prefix':0,'side':side,'kind':'initial-'+f,
                                'expected':[],'observed':_js(l.get(f))})
                continue
            a=acts[i-1]; k=a.split('@')[0]
            for side,pre,post,dec in (('source',_ledger(ss[i-1]),sl,ss[i].get('decision')),
                                      ('adapter',_ledger(aa[i-1]),al,aa[i].get('decision'))):
                try: diffs=_frag(pre,post,dec,a)
                except Exception as e: diffs=[{'kind':'fragment-error','expected':'well-typed','observed':'%.120s'%(e,)}]
                for d in diffs:
                    viol+=1; obs.append(dict(d,case=name,prefix=i,side=side,action=a))
            row=rows[i-1] if i-1<len(rows) and type(rows[i-1]) is dict else {}
            for side,want in (('source',ss[i].get('decision')),('adapter',aa[i].get('decision'))):
                got=(row.get(side+'_observation') or {}).get('decision')
                if got is not None and got!=want:
                    viol+=1; obs.append({'case':name,'prefix':i,'side':side,'action':a,'kind':'row-decision',
                        'expected':_js(want),'observed':_js(got)})
            if k=='collect-open' or k=='source-attest' or k.startswith('collect:'):
                relevant+=1; pl=_ledger(ss[i-1]); c=pl.get('collection')
                fresh=bool(c) and len(c)>1 and _eq(c[0],pl.get('source_generation')) and _eq(c[1],pl.get('source_revision'))
                if k=='source-attest' and fresh and ss[i].get('decision')!='source-attest:ok': unver+=1
                obs.append({'case':name,'prefix':i,'action':a,'kind':'inspected',
                    'source_decision':_js(ss[i].get('decision')),'adapter_decision':_js(aa[i].get('decision')),
                    'capture_fresh':fresh})
    st='counterexample' if viol else 'unproved' if failed else 'supported' if relevant else 'not_applicable'
    if failed: lim.append('%d case(s) unauditable; verdict excludes them'%failed)
    if unver: lim.append('%d fresh attestation refusal subtype(s) not re-derived (need original fixture bytes)'%unver)
    return {'status':st,'observations':obs,'limitations':lim,'audited_prefixes':audited}

def _find(cases,pred):
    for case in cases:
        try:
            ss,aa=_states(case['source']),_states(case['adapter']); acts=case['source']['actions']
            if len(ss)!=len(aa)!=len(acts)+1: continue
            for i,a in enumerate(acts):
                if pred(a.split('@')[0],ss[i],ss[i+1],aa[i],aa[i+1]): return case,i
        except Exception: continue
    return None,None

def _mut(ev,field,fn):
    hits=[0]
    def rec(d,dep):
        if type(d) is not dict or dep>4: return
        if field in d and any(h in d for h in HINTS): d[field]=fn(d[field]); hits[0]+=1
        for x in d.values():
            if type(x) is dict: rec(x,dep+1)
    rec(ev,0)
    if not hits[0]:
        for k in KEYS:
            p=ev.get(k)
            if type(p) is dict:
                (p['journal'] if type(p.get('journal')) is dict else p)[field]=fn(None); hits[0]+=1; break
    return hits[0]

def _cedit(m,i,side,j,fn):
    return _mut(m[side]['events'][i],'collection',lambda c:c[:j]+(fn(c[j]),)+c[j+1:])
def _fdec(m,i,verdict):
    hits=_mut(m['source']['events'][i],'decision',lambda d:verdict)+_mut(m['adapter']['events'][i],'decision',lambda d:verdict)
    rows=m.get('rows') or []
    if i<len(rows) and type(rows[i]) is dict:
        for side in ('source','adapter'):
            o=rows[i].get(side+'_observation')
            if type(o) is dict and 'decision' in o: o['decision']=verdict; hits+=1
    return hits
def _bump(m,i,field):
    g=_ledger(_states(m['source'])[i])[field]
    return _mut(m['source']['events'][i-1],field,lambda old:g[:-1]+(g[-1]+1,) if field=='source_generation' else g+1)

def run_controls(cases,inspect_cases,charge):
    out=[]
    def P(v,d): return lambda k,sp,sp2,ap,ap2: k==v and sp2.get('decision')==d
    o_ok,a_ok=P('collect-open','collect-open:ok'),P('source-attest','source-attest:ok')
    coll=lambda k,sp,sp2,ap,ap2: k.startswith('collect:') and sp2.get('decision')==k+':ok'
    def _reset(m,i):
        pre=_ledger(_states(m['source'])[i])
        f=pre['collected'] or (((0,pre['append_log'][0]),) if pre['append_log'] else (('x','forged'),))
        return _mut(m['source']['events'][i],'collected',lambda old:f)
    def _fbytes(m,i):
        j=int(m['source']['actions'][i].split('@')[0].split(':')[1])
        return _mut(m['source']['events'][i],'collected',lambda c:tuple((x,'forged-raw') if x==j else (x,y) for x,y in c))
    spec=[('capture-tuple-dropped',o_ok,lambda m,i:_mut(m['source']['events'][i],'collection',lambda c:()),'implausible','capture erased at open'),
        ('capture-reset-skipped',o_ok,_reset,'plausible','post-open collected not reset'),
        ('collect-bytes-substituted',coll,_fbytes,'implausible','raw not copied from append_log'),
        ('stale-refusal-dropped',P('source-attest','source-attest:stale-collection'),lambda m,i:_fdec(m,i,'source-attest:ok'),'plausible','stale refusal rewritten to ok'),
        ('open-refusal-dropped',P('collect-open','collect-open:no-registration'),lambda m,i:_fdec(m,i,'collect-open:ok'),'plausible','visible refusal rewritten to ok'),
        ('adapter-journal-capture-only',o_ok,lambda m,i:_cedit(m,i,'adapter',1,lambda x:x+1),'plausible','adapter journal capture alone'),
        ('boundary-generation-only',a_ok,lambda m,i:_bump(m,i,'source_generation'),'plausible','generation-only bump must force stale'),
        ('boundary-revision-only',a_ok,lambda m,i:_bump(m,i,'source_revision'),'plausible','revision-only bump must force stale')]
    for j,(nm,fn) in enumerate((('generation',lambda x:x[:-1]+(x[-1]+1,)),('revision',lambda x:x+1),
            ('registration',lambda x:'forged'),('attempts',lambda x:()),('log-length',lambda x:x+1))):
        spec.append(('capture-'+nm,o_ok,(lambda j,fn:lambda m,i:_cedit(m,i,'source',j,fn))(j,fn),'plausible','capture component rewritten'))
    for name,pred,mut,shape,note in spec:
        e={'control':name,'forged_state_shape':shape,'note':note}
        case,i=_find(cases,pred)
        if case is None: e['status']='missing-witness'; out.append(e); continue
        m=copy.deepcopy(case); e['witness']={'case':case.get('case'),'event_index':i}
        try: e['mutation_applied']=bool(mut(m,i))
        except Exception as x: e['status']='mutation-error:'+type(x).__name__
        if 'status' not in e and not e['mutation_applied']: e['status']='mutation-unapplied'
        if 'status' in e: out.append(e); continue
        try: e['observed_status']=inspect_cases([m],charge).get('status')
        except Exception as x: e['observed_status']='audit-error:'+type(x).__name__
        e['detected']=e['observed_status']=='counterexample'; out.append(e)
    return {'controls':out,'cases':len(cases),'note':'detections measure audit sensitivity on retained '
        'evidence; only violations in unmodified executed cases are original-domain counterexamples'}
