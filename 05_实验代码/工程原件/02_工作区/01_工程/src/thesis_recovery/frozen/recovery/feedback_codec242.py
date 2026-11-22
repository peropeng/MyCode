"""Exact shared-line representation of complete current/historical public feedback."""
import copy,hashlib,json
SCHEMA='lossless-public-feedback-lines/1'
LINES='$public_feedback_exact_lines'
LITERAL='$public_feedback_literal_object'
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def encode(value):
 pool=[];by={};occurrences=[]
 def visit(v,path):
  if isinstance(v,str) and ('\n' in v or '\r' in v or len(v)>=160):
   ids=[]
   for line in v.splitlines(keepends=True):
    if line not in by:by[line]=len(pool);pool.append(line)
    ids.append(by[line])
   occurrences.append({'path':path,'line_ids':ids});return {LINES:ids}
  if isinstance(v,list):return [visit(x,path+[i]) for i,x in enumerate(v)]
  if isinstance(v,dict):
   encoded={k:visit(x,path+[k]) for k,x in v.items()}
   return {LITERAL:encoded} if set(v) in ({LINES},{LITERAL}) else encoded
  return copy.deepcopy(v)
 result={'schema':SCHEMA,'unique_exact_lines':pool,'semantic_structure':visit(value,[]),
 'decoded_semantic_sha256':digest(value),
 'decode_instructions':'Within this envelope only: concatenate unique_exact_lines indices in $public_feedback_exact_lines exactly in order; $public_feedback_literal_object escapes a literal object. All status/node/phase/source SHA/observations remain complete. Decode before interpreting current versus explicitly historical rejected state.',
 'no_fields_nodes_text_or_source_removed':True}
 if decode(result)!=value:raise ValueError('PUBLIC_FEEDBACK_EXACT_ROUNDTRIP_FAILED')
 return result,{'schema':SCHEMA,'exact_roundtrip':True,'raw_sha256':digest(value),
 'encoded_sha256':digest(result),'raw_canonical_bytes':len(canonical(value).encode()),
 'encoded_canonical_bytes':len(canonical(result).encode()),'unique_exact_line_count':len(pool),
 'encoded_text_occurrences':len(occurrences),'occurrence_map':occurrences}
def decode(pack):
 if pack.get('schema')!=SCHEMA:raise ValueError('PUBLIC_FEEDBACK_CODEC_SCHEMA_UNKNOWN')
 pool=pack['unique_exact_lines']
 if not isinstance(pool,list) or not all(isinstance(s,str) for s in pool):raise ValueError('PUBLIC_FEEDBACK_POOL_INVALID')
 def visit(v):
  if isinstance(v,dict) and set(v)=={LINES}:
   ids=v[LINES]
   if not isinstance(ids,list) or any(isinstance(i,bool) or not isinstance(i,int) or not 0<=i<len(pool) for i in ids):
    raise ValueError('PUBLIC_FEEDBACK_LINE_INDEX_INVALID')
   return ''.join(pool[i] for i in ids)
  if isinstance(v,dict) and set(v)=={LITERAL}:
   if not isinstance(v[LITERAL],dict):raise ValueError('PUBLIC_FEEDBACK_LITERAL_ESCAPE_INVALID')
   return {k:visit(x) for k,x in v[LITERAL].items()}
  if isinstance(v,dict):return {k:visit(x) for k,x in v.items()}
  if isinstance(v,list):return [visit(x) for x in v]
  return copy.deepcopy(v)
 result=visit(pack['semantic_structure'])
 if digest(result)!=pack['decoded_semantic_sha256']:raise ValueError('PUBLIC_FEEDBACK_DECODE_DIGEST_DRIFT')
 return result
def pack_payload_feedback(payload):
 value=copy.deepcopy(payload)
 raw=value.get('latest_public_feedback')
 if not isinstance(raw,dict):raise ValueError('PUBLIC_FEEDBACK_OBJECT_REQUIRED')
 envelope,audit=encode(raw);value['latest_public_feedback']=envelope
 value['current_and_historical_feedback_representation']={'schema':SCHEMA,
 'scope':'all complete_attempt_feedback and current_incumbent_public_feedback fields',
 'complete_decoded_sha256':digest(raw),'historical_rejected_attempts_not_current':True,
 'exact_decode_equals_original_complete_feedback':True}
 return value,audit
