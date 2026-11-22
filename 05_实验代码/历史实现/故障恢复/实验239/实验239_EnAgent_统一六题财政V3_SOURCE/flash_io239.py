"""Lazy completion-v3 finance; import has no IO factory or shared ledger access."""
from common166 import *
from flow_bounds239 import finite_seconds
_transport=None;_config_digest=None

def generate(env,body,role,phase):
 global _transport,_config_digest
 require_open();p=authorization()
 if not p.get('model_generation_authorized') or phase!=p['finance_phase']:raise RuntimeError('SCOPED_SCIENCE_MODEL_AUTHORITY_REQUIRED')
 finite_seconds(env.time_left())
 config=read(E/'finance_config239.json')
 if config.get('schema')!='continuous-human-completion/3' or config.get('model_generation_authorized') is not True:raise RuntimeError('COMPLETION_V3_MODEL_FINANCE_PERMISSION_FALSE')
 if p.get('finance_common_C0_configuration_pending') or config.get('common_C0_supplement_registry')!=p.get('common_six_C0_supplement_file') or config.get('common_C0_supplement_registry_SHA256')!=p.get('common_six_C0_supplement_sha256'):raise RuntimeError('ROOT_COMMON_V4_C0_CONFIG_REQUIRED')
 if Path(p['finance_transport']).name!='completion_transport_common_C0_v4.py':raise RuntimeError('ROOT_COMMON_V4_SOLE_INJECTOR_REQUIRED')
 if config.get('hard_deadline_utc') is not None or config.get('no_new_utc') is not None or config.get('closure_flag')!=p['closure_flag'] or config.get('common_tasks')!=p['task_order'] or phase not in config['phases']:raise RuntimeError('COMPLETION_V3_SCOPE_OR_STOP_DRIFT')
 identity=digest(config)
 if _transport is None:
  if sha(p['finance_transport'])!=p['finance_transport_sha256'] or sha(p['finance_core'])!=p['finance_core_sha256']:raise RuntimeError('COMPLETION_FINANCE_SOURCE_DRIFT')
  provider=module('exp239_completion_finance_v3',p['finance_transport'])
  _transport=provider.make_transport(config);_config_digest=identity
 elif _config_digest!=identity:raise RuntimeError('LIVE_FINANCE_CONFIG_CHANGED_NO_RETRY')
 return _transport.generate(env,body,role,phase)
