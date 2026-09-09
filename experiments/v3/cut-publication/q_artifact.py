"""Lossless text-object interning for evidence storage; never model-state merging."""
import hashlib
TAG='$text_sha256'
def sha(text):return hashlib.sha256(text.encode('utf-8')).hexdigest()
def pack(result):
 objects={}
 def visit(x):
  if isinstance(x,str) and len(x)>512:
   key=sha(x)
   if key in objects:assert objects[key]==x,'text digest collision'
   objects[key]=x;return {TAG:key}
  if isinstance(x,dict):
   assert TAG not in x,'reserved artifact key';return {k:visit(v) for k,v in x.items()}
  if isinstance(x,(list,tuple)):return [visit(v) for v in x]
  return x
 value=visit(result);return {'format':'text-interning/1','objects':objects,'result':value}
def unpack(envelope):
 if not isinstance(envelope,dict) or set(envelope)!={'format','objects','result'} or envelope['format']!='text-interning/1':raise ValueError('artifact envelope')
 objects=envelope['objects'];used=set()
 if not isinstance(objects,dict) or len(objects)>2048:raise ValueError('artifact object bound')
 for key,value in objects.items():
  if not isinstance(value,str) or key!=sha(value):raise ValueError('artifact text hash')
 def visit(x):
  if isinstance(x,dict):
   if TAG in x:
    if set(x)!={TAG} or x[TAG] not in objects:raise ValueError('artifact text reference')
    used.add(x[TAG]);return objects[x[TAG]]
   return {k:visit(v) for k,v in x.items()}
  if isinstance(x,list):return [visit(v) for v in x]
  return x
 result=visit(envelope['result'])
 if used!=set(objects):raise ValueError('unreferenced artifact text')
 return result
