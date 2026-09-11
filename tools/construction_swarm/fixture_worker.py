"""Zero-provider scheduling fixture. Not evidence of model quality or entitlement."""
import json
import sys
import time
from pathlib import Path

packet = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
time.sleep(.03)
files = ([{'path': packet['job']['allowed_paths'][0], 'content': 'answer = 42\n'}]
         if packet['job']['kind'] == 'develop' and packet['job']['allowed_paths'] else [])
print(json.dumps({'job_id': packet['job']['id'], 'summary': 'Synthetic scheduling fixture.',
                  'findings': [], 'evidence': packet['citation_ids'], 'dissent': [],
                  'limitations': ['No model, research or implementation executed.'], 'files': files}))
