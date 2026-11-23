"""Path-only public projection, including escaped and ANSI-decoded known roots."""
import json,re
METHODS=('AGENTLESS_FSE2025_4L4P4T_FLASH','G_PROGRESSIVE_SEMANTIC_FLASH','ENAGENT_ICSE2026','ENAGENT_ICSE2026_N3')
def variants(path):
 values={str(path),str(path).replace('\\','/'),str(path).replace('/','\\')}
 for text in tuple(values):
  values.add(json.dumps(text,ensure_ascii=False)[1:-1]);values.add(json.dumps(text,ensure_ascii=True)[1:-1])
  for encoding in ('cp1252','cp936','cp850'):
   values.add(text.encode('utf-8').decode(encoding,errors='replace'))
 return sorted(values,key=len,reverse=True)
def normalize_text(text,root_map):
 for original,virtual in sorted(root_map,key=lambda x:len(str(x[0])),reverse=True):
  for version in variants(original):text=text.replace(version,virtual)
 # Relative pytest frames can carry an arm directory without an absolute root.
 # Only recognized temporary/native-active path tokens are eligible.
 token=re.compile(r'(?:[A-Za-z]:)?[^\s<>"\']*(?:[\\/])[^\s<>"\']+')
 def replace(match):
  value=match.group(0);logical=value.replace('\\','/')
  marked=('/native_active/' in logical or '/public_native/' in logical or '1008-2320-exp224-flash-common/' in logical or '1008-2320-exp225-enagent-flash/' in logical)
  if not marked or not any('/'+method+'/' in logical for method in METHODS):return value
  if '/repo/' in logical:return '/workspace/repo/'+logical.split('/repo/',1)[1]
  if '/public_native/' in logical:return '/public-feedback/'+logical.split('/public_native/',1)[1]
  return '/public-feedback/'+logical.rsplit('/',1)[-1]
 return token.sub(replace,text)
def project(value,root_map):
 if isinstance(value,str):return normalize_text(value,root_map)
 if isinstance(value,list):return [project(x,root_map) for x in value]
 if isinstance(value,dict):return {k:project(v,root_map) for k,v in value.items()}
 return value
