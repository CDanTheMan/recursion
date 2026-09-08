"""Shared finite declarations only; no transition or outcome implementation."""
import json,pathlib
MANIFEST=pathlib.Path(__file__).resolve().parents[3]/'docs/v3/construction/formal-comparison-20260907/domains.json'
CONFIG=json.loads(MANIFEST.read_text())['slice']
TOKENS=('E1','E2','CREDIT','ACK0','ACK1','ACK2','HELLO','WELCOME','SNAPSHOT','INPUT','RESIZE','RESET')
LIMIT=CONFIG['total_inflight_messages']
CHANNEL=CONFIG['queue_slot_limit_per_stage']
FRAME=CONFIG['partial_frame_quanta_max']
CREDIT_SOURCES=CONFIG['credit_source_offers']
assert type(CREDIT_SOURCES)is int and CREDIT_SOURCES==2
FAIR_ACTIONS=('stop_apply','pump_sdk','pump_broker','consume')
