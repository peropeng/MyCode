"""Author public runner over declared G+O; local initial PASS stays empirical."""
from bridge225 import IllegalTool
def local_bridge(base):
 class LocalPublicBridge(base):
  def public_runner(self,root,ids):
   before=self._check_assets();ids=list(ids)
   allowed=set(self.env.recovery_goal_nodes)|set(self.env.public_regression_nodes)
   if len(ids)!=len(set(ids)) or not set(ids)<=allowed:raise IllegalTool('PUBLIC_RUNNER_EXACT_DECLARED_G_O_ONLY')
   if not ids:return {}
   original=self.env.snapshot('bridge_public_entry');self._number+=1
   try:
    snapshot=self.snapshot_clone(root,'enagent_local_public_'+str(self._number))
    native=self.env._public_native(ids,snapshot,'enagent_local_public_'+str(self._number));self._valid(native)
    outcomes=native.get('pytest',{}).get('outcomes',{});answer={}
    if set(outcomes)!=set(ids):self._fatal('LOCAL_G_O_EXACT_OUTCOMES_UNKNOWN')
    for node in ids:
     status=outcomes[node].get('status')
     if status not in {'passed','failed','error'}:self._fatal('LOCAL_PUBLIC_NODE_OUTCOME_UNKNOWN '+node)
     answer[node]='PASS' if status=='passed' else 'FAIL'
    self._record('public_runner',{'root':str(root),'declared_local_G_O_ids':ids,'actual_outcomes':answer,'native_record':native,'whole_repo_discovery_claimed':False,'immutable_sha256':before})
    return answer
   finally:self.env.restore(original);self._check_assets()
 return LocalPublicBridge
