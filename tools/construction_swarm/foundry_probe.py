"""Known-answer repository contract probes for native worker/tool qualification."""
import json
import sys

from .contracts import Refused, digest, encoded, integer, path, strict_json, timestamp


def refused(function, *args):
    try:
        function(*args)
    except Refused:
        return
    raise AssertionError('invalid input accepted')


def probe(number):
    integer(number, 0, 99)
    group = number % 6
    if group == 0:
        name = f'tools/case_{number}.py'
        assert path(name) == name
        for name in ['../escape', 'tools/.env', '/etc/passwd', 'tools/CON.py', 'tools/x..']:
            refused(path, name)
    elif group == 1:
        refused(strict_json, ('{"case":' + str(number) + ',"case":0}').encode())
        refused(strict_json, b'{"value":NaN}')
        refused(strict_json, b'{"value":Infinity}')
    elif group == 2:
        value = {'case': number, 'text': '\u03bb\u00e9\n', 'items': [True, None, number]}
        assert strict_json(encoded(value)) == value
        assert digest(encoded(value)) == digest(encoded(dict(reversed(list(value.items())))))
    elif group == 3:
        integer(number, 0, 99)
        for value in [True, False, float(number), str(number), -1, 100]:
            refused(integer, value, 0, 99)
    elif group == 4:
        assert timestamp('2026-09-11T00:00:00Z') == timestamp('2026-09-11T00:00:00+00:00')
        refused(timestamp, '2026-09-11T00:00:00')
        refused(timestamp, '2026-09-11T00:00:00+01:00')
    else:
        for name in [f'tools/case_{number}.', f'tools//case_{number}', f'tools/../case_{number}',
                     f'tools\\case_{number}', f'tools/.case_{number}']:
            refused(path, name)
    return {'case': number, 'group': group, 'passed': True}


if __name__ == '__main__':
    print(json.dumps(probe(int(sys.argv[1])), sort_keys=True))
