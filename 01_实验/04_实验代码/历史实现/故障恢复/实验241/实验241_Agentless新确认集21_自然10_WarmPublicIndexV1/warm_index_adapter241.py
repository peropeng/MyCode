"""Read-only complete warm index; original dense scores/order, no encoder fallback."""
from contracts241 import *
def retrieve(owner,files,query,ref,allowed):
 from agentless_bridge import dense166
 binding=read(owner.protocol['warm_public_index_binding'])
 if binding.get('qualified') is not True or binding.get('resource_complete') is not True or not binding.get('Root_actual_resource_review'):raise EngineeringUnknown('WARM_RESOURCE_NOT_QUALIFIED')
 for key in ('resource_terminal','resource_complete_receipt','index_manifest'):
  if not binding.get(key) or sha(binding[key])!=binding[key+'_sha256']:raise EngineeringUnknown('WARM_ACTUAL_RECEIPT_SHA '+key)
 terminal=read(binding['resource_terminal']);complete=read(binding['resource_complete_receipt']);cache=read(binding['index_manifest'])
 stop=terminal.get('job_result',{}).get('stop_receipt',{})
 if terminal.get('status')!='COMPLETE' or not all(stop.get(k) is True for k in ('root_stopped','own_Job_empty_before_close','descendants_stopped')):raise EngineeringUnknown('WARM_RESOURCE_FULL_STOP_REQUIRED')
 if complete.get('vectors_verified')!=4105 or complete.get('source_chunks')!=4104 or complete.get('query_complete_tokens')!=560:raise EngineeringUnknown('WARM_FULL4105_ACTUAL_COMPLETE_REQUIRED')
 exact={path:hashlib.sha256(text.encode('utf-8')).hexdigest() for path,text in sorted(files.items())}
 if cache.get('status')!='SEALED' or cache.get('source_files_sha256')!=exact or cache.get('query_sha256')!=hashlib.sha256(query.encode('utf-8')).hexdigest() or cache.get('query_complete') is not True or cache.get('query_truncated') is not False:raise EngineeringUnknown('WARM_EXACT_SOURCE_QUERY_INPUT_REQUIRED_NO_ENCODER_FALLBACK')
 if cache.get('model_identity')!=dense166.identity() or cache.get('model_identity_sha256')!=binding['resource_model_identity_sha256'] or len(cache.get('nodes',[]))!=4104 or len(cache.get('vector_sha256',{}))!=4105:raise EngineeringUnknown('WARM_MODEL_OR_CORE_COVERAGE_DRIFT')
 result,evidence=dense166.retrieve(files,query,binding['index_manifest'],allowed)
 evidence.update(warm_public_index=True,warm_index_manifest_sha256=binding['index_manifest_sha256'],resource_preprocessing_elapsed_seconds=binding['resource_preprocessing_elapsed_seconds'],resource_terminal_sha256=binding['resource_terminal_sha256'],actual_new_encoding_texts=0,cold900_completion_claim=False,original_dense_cosine_and_node_ordinal_tie_unchanged=True)
 return result,evidence
