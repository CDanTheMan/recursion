"""Explicit successor/historical namespace bridge; historical globals stay untouched."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
OLD_NAME = 'eight-hour-research-20260910-01a08a22'
NEW_NAME = OLD_NAME + '-slice2'
OLD_CODE = 'experiments/v3/' + OLD_NAME + '/'
NEW_CODE = 'experiments/v3/' + NEW_NAME + '/'
OLD_DOC = 'docs/v3/construction/' + OLD_NAME + '/'
NEW_DOC = 'docs/v3/construction/' + NEW_NAME + '/'
sys.path.insert(0, str(ROOT / OLD_CODE))
import check as check
assert Path(check.__file__).resolve() == ROOT / OLD_CODE / 'check.py'
assert check.NAME == OLD_NAME

def packet_doc(packet):
    assert packet in ('packet-01','packet-02','packet-03','packet-04','packet-05')
    return OLD_DOC if packet in ('packet-01','packet-02','packet-03') else NEW_DOC

def reference_script(packet):
    assert packet in ('packet-01','packet-04')
    return OLD_CODE + 'check.py' if packet == 'packet-01' else NEW_CODE + 'selected.py'

def added_module_paths():
    return {OLD_CODE + x for x in ('check.py','artifact.py')} | {NEW_CODE + x for x in ('baseline.py','selected.py','shared.py','prefix_kernel.py')}
