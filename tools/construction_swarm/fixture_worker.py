"""Zero-provider scheduling fixture. Not evidence of model quality or entitlement."""
import json
import sys
import time

packet = json.loads(open(sys.argv[1], encoding='utf-8').read())
time.sleep(.03)
print(json.dumps({'job_id': packet['job']['id'], 'summary': 'Synthetic scheduling fixture.',
                  'findings': [], 'evidence': packet['citation_ids'], 'dissent': [],
                  'limitations': ['No model, research or implementation executed.'], 'files': []}))
