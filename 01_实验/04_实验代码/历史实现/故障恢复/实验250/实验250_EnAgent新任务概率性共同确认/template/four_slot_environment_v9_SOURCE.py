"""Only native queue deployment override. Original finite class bytes unchanged."""
from contextlib import contextmanager
from pathlib import Path

def four_slot_environment(base):
 class FourSlotEnvironment(base):
  @contextmanager
  def native_lane(self,final=False):
   from common166 import E,authorization,read,sha,module,require_open
   from flow_bounds239 import require_time
   import control235
   require_open();p=authorization()
   if final:require_time(self.deadline)
   else:self._require()
   grant_name='mechanical_exact_leaf_grant239.json' if getattr(control235,'SINGLE_PUBLIC_LEAF',False) else 'mechanical_grant239_v3.json' if control235.MECHANICAL else 'root_grant239.json'
   grant_path=E/grant_name;grant_before=read(grant_path);protocol_sha=sha(E/'protocol225.json')
   contract_path=Path(p['native_scheduling_contract']);helper_path=Path(p['native_scheduling_helper'])
   if sha(contract_path)!=p['native_scheduling_contract_sha256'] or sha(helper_path)!=p['native_scheduling_helper_sha256']:raise RuntimeError('NATIVE_FOUR_SLOT_SOURCE_BINDING_DRIFT')
   contract=read(contract_path)
   if contract['source_SHA256']!=p['native_scheduling_helper_sha256'] or contract['native_slot_offsets']!=[1,2,4,5] or contract['MONAI_exclusive_offset']!=3 or contract['financial_offset_zero_untouched'] is not True:raise RuntimeError('NATIVE_FOUR_SLOT_COMMON_CONTRACT_DRIFT')
   helper=module('ea22_shared_native_four_slots_v5',helper_path)
   def check_wait():
    require_open()
    if read(grant_path)!=grant_before:raise RuntimeError('NATIVE_QUEUE_ROOT_AUTHORITY_CHANGED')
    if sha(E/'protocol225.json')!=protocol_sha or sha(p['root_protocol'])!=p['root_protocol_sha256']:raise RuntimeError('NATIVE_QUEUE_PROTOCOL_CHANGED')
    if final:require_time(self.deadline)
    else:self._require()
   def record_slot(row):self.record(row['event'],{k:v for k,v in row.items() if k!='event'})
   with helper.native_lane(contract['lock_path'],self.package,check_wait,record_slot):
    check_wait();authorization();yield
 return FourSlotEnvironment
