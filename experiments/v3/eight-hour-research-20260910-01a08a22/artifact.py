"""Typed evidence transport only; original model identity/encoding is unchanged."""
import identity as relation
r, d = relation.r, relation.d

def encode(value):
    return r.typed(value)

def decode(value):
    d.require(type(value) is list and len(value) == 2, 'typed evidence node')
    tag, body = value
    if tag == 'dict':
        d.require(type(body) is list and all(type(x) is list and len(x) == 2 and type(x[0]) is str for x in body), 'typed dictionary entries')
        d.require(len({x[0] for x in body}) == len(body), 'no duplicate evidence keys')
        return {k: decode(v) for k, v in body}
    if tag in ('tuple', 'list', 'Envelope'):
        d.require(type(body) is list, 'typed sequence body')
        values = [decode(v) for v in body]
        return d.q.Envelope(*values) if tag == 'Envelope' else tuple(values) if tag == 'tuple' else values
    scalars = {'str': str, 'int': int, 'bool': bool, 'float': float, 'NoneType': type(None)}
    d.require(tag in scalars and type(body) is scalars[tag], 'allowed exact scalar evidence type')
    return body
