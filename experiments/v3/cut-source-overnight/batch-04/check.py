"""Frozen Batch04 comparison gate; execute only through its owned runner."""
import argparse
import json
from pathlib import Path
import sys
import correspondence as c

def main(output):
    output.mkdir(parents=True, exist_ok=False)
    manifest = c.read(c.DOC/'manifest.json')
    registered = {row['path'] for row in manifest['inputs']} | set(manifest['sources'])
    loaded = set()
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename:
            path = Path(filename).resolve()
            if path.is_relative_to(c.ROOT) and path.suffix == '.py': loaded.add(path.relative_to(c.ROOT).as_posix())
    c.require(loaded <= registered, 'loaded module manifest closure: '+repr(sorted(loaded-registered)))
    result = c.run()
    result['registered_local_modules'] = sorted(loaded)
    packed = c.codec.pack(result)
    accepted = c.DOC/'results.json'
    if accepted.exists(): c.require(packed == c.read(accepted), 'exact accepted Batch04 reproduction')
    (output/'result.json').write_text(json.dumps(packed, sort_keys=True, separators=(',',':'))+'\n', encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','states_per_representation','edges_per_representation','classifications')}), flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('output',type=Path)
    parser.add_argument('--packet',choices=('C',),required=True)
    main(parser.parse_args().output)
