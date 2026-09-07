"""Prospective packet release guard; bounded reservations are never silently refunded."""
import datetime
import hashlib
import json
import os
import pathlib


def validate(packet, case, launches, used, now):
    if packet.get('status')!='open':raise ValueError('packet is not open')
    if not any(c['id']==case for c in packet['cases']):raise ValueError('case is outside packet')
    if type(packet['case_limit'])is not int or not 0<len(packet['cases'])<=packet['case_limit']<=2:raise ValueError('case bound')
    if len({c['id'] for c in packet['cases']})!=len(packet['cases']):raise ValueError('duplicate case')
    if type(launches)is not int or launches<1 or type(used)is not int or used<0:raise ValueError('invalid reservation count')
    if type(packet['execution_limit'])is not int or not 0<packet['execution_limit']<=6:raise ValueError('execution bound')
    if used+launches>packet['execution_limit']:raise ValueError('packet launch capacity exhausted')
    start=datetime.datetime.fromisoformat(packet['at']);deadline=datetime.datetime.fromisoformat(packet['deadline_utc'])
    if not start<=now<deadline or (deadline-start).total_seconds()>1800:raise ValueError('packet clock bound')


def reserve(path, lab, case, launches):
    path=pathlib.Path(path);raw=path.read_bytes();packet=json.loads(raw)
    ident=packet['id']
    closure=path.with_name(path.stem+'-closure.json')
    if closure.exists():
        closed=json.loads(closure.read_text())
        if closed.get('packet_id')==ident and closed.get('status')=='closed':raise ValueError('packet has a closure receipt')
    if any(c not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in ident):raise ValueError('packet identifier')
    folder=pathlib.Path(lab)/'private/packet-leases';folder.mkdir(exist_ok=True)
    lock=folder/(ident+'.lock');ledger=folder/(ident+'.json')
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    try:
        previous=json.loads(ledger.read_text()) if ledger.exists() else {'packet_sha256':hashlib.sha256(raw).hexdigest(),'reservations':[]}
        if previous['packet_sha256']!=hashlib.sha256(raw).hexdigest():raise ValueError('packet changed during release; register a new packet')
        now=datetime.datetime.now(datetime.timezone.utc);used=sum(x['launches'] for x in previous['reservations'])
        validate(packet,case,launches,used,now)
        receipt={'packet_id':ident,'packet_sha256':hashlib.sha256(raw).hexdigest(),'case':case,'launches':launches,
                 'ordinal':len(previous['reservations'])+1,'reserved_at':now.isoformat(),'packet':packet}
        previous['reservations'].append(receipt)
        temporary=ledger.with_suffix('.new');temporary.write_text(json.dumps(previous,indent=2)+'\n');os.replace(temporary,ledger)
        return receipt
    finally:
        os.close(fd);lock.unlink()
