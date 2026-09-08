"""Prospective finite environments; data only, no transition implementation."""
from dataclasses import dataclass, fields

@dataclass(frozen=True, slots=True)
class State:
    free: tuple = (10, 0)
    reserved: tuple = (0, 0)
    consumed: tuple = (0, 0)
    issued: int = 0
    intent: int = 0
    sent: tuple = (0, 0)
    remote: tuple = (0, 0)  # 1 success; 2 terminal nonexecution
    receipt: tuple = (0, 0)
    classification: tuple = (0, 0)
    conflict: int = 0
    quarantine: int = 0
    reads: tuple = (-1, -1)
    transfer: int = 0  # 0 absent; 1 durable debit; 2 durable application
    ack: bool = False
    revision: int = 0
    boot: int = 0
    worker: int = 0  # running, exited, waited
    incarnation: int = 0
    lifetime: tuple = (1, 0)
    quota_epoch: int = 0
    quota_used: int = 1
    generation: int = 1
    reader_pin: bool = False
    snapshot: tuple = ()
    copied: bool = False
    installed: tuple = ()
    done: int = 0

NAMES = tuple(f.name for f in fields(State))
BROKER = frozenset(('reads','worker','incarnation','quota_used','reader_pin','snapshot','copied','installed','done'))

def initial(design):
    return State(free=(10,0) if design == 'central' else (5,5))

def profile(actions, chains=(), source=1):
    deps = {a: set() for a in actions}
    for chain in chains:
        for a,b in zip(chain,chain[1:]): deps[b].add(a)
    return {'actions':tuple(actions), 'requires':{a:tuple(sorted(v)) for a,v in deps.items()}, 'source':source}

def sequence(*actions, source=1):
    return profile(actions,(actions,),source)

PROFILES = {
 'free-admission': profile(('read0','read1','reserve0','reserve1','duplicate0','duplicate1','restart','quota_reset')),
 'stale-read-race': sequence('read0','read1','reserve0','reserve1'),
 'lost-receipt-restart': sequence('transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','restart','duplicate0','resend0','reserve1'),
 'lost-receipt-refusal': sequence('transfer_debit','transfer_install','reserve0','intent0','send0','refuse0','lose0','restart','query0','classify0','reconcile0','settle_again0','reserve1'),
 'success-consumption': sequence('transfer_debit','transfer_install','reserve0','intent0','send0','accept0','receive0','classify0','reconcile0','settle_again0','reserve1'),
 'classification-hold': sequence('transfer_debit','transfer_install','reserve0','intent0','send0','accept0','receive0','classify0','conflict0','reconcile0','reserve1'),
 'owner-and-identity': sequence('transfer_debit','transfer_install','reserve0','wrong_owner0','changed_payload0','intent0','send0','accept0','lose0','foreign_release0','duplicate0'),
 'snapshot-uncertainty': profile(('capture','copy','reader_wait','transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','install','restore_old','reserve1'),
    (('capture','copy','reader_wait','install'),('capture','transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','install','restore_old','reserve1'))),
 'local-lifetime': profile(('transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','exit','wait','quota_reset','restart','new_worker','compute','resend0','reserve1'),
    (('transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','exit','wait','new_worker','compute','resend0','reserve1'),('lose0','quota_reset','compute'),('lose0','restart','new_worker'))),
 'pin-and-reservation': sequence('capture','transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','publish','copy','reader_wait','install','reserve1'),
 'transfer-interruption': sequence('capture','copy','reader_wait','transfer_debit','restart','transfer_install','transfer_duplicate','transfer_timeout','transfer_ack','restore_old','install','reserve0','reserve1'),
 'transfer-free': profile(('transfer_debit','transfer_install','transfer_duplicate','transfer_timeout','transfer_ack','restart','reserve0','reserve1'),
     (('transfer_debit','transfer_install','transfer_duplicate'),('transfer_install','transfer_ack'),('transfer_debit','transfer_timeout'))),
 'transfer-mirror': sequence('transfer_debit','restart','transfer_install','transfer_duplicate','transfer_timeout','reserve1','reserve0',source=0),
 'receipt-and-local-interleavings': profile(('transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','query0','classify0','reconcile0','exit','wait','restart','quota_reset'),
     (('transfer_debit','transfer_install','reserve0','intent0','send0','accept0','lose0','query0','classify0','reconcile0'),('send0','exit','wait'),('lose0','restart'))),
}

def available(s, p):
    names=p['actions']; seen={a for i,a in enumerate(names) if s.done & (1<<i)}
    return [a for a in names if a not in seen and all(d in seen for d in p['requires'][a])]

def finish(s, action, p):
    return s.done | (1 << p['actions'].index(action))

def visible(s):
    """Safety observation, not an assertion of equal design availability."""
    return (s.reserved,s.consumed,s.issued,s.intent,s.sent,s.receipt,s.classification,s.conflict,s.quarantine)
