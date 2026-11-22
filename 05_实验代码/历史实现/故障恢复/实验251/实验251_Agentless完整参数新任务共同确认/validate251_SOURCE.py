"""Source and synthetic checkpoint invariants; never model/product execution."""
import shutil,types
from runtime251 import *
from entry251 import Journal

parsed=[]
for p in sorted(HERE.rglob('*.py')):
 if any(x in ('runs','source_previews','source_validation') for x in p.relative_to(HERE).parts):continue
 ast.parse(p.read_text('utf-8-sig'));parsed.append(ref(p))
for p in sorted((HERE/'native_core').glob('*.py')):ast.parse(p.read_text('utf-8-sig'),feature_version=(3,8))
mapping=read(HERE/'COPIED_SOURCE_MAP251.json')['files']
for p,row in mapping.items():
 if sha(p)!=row['copy_SHA256'] or sha(row['source'])!=row['source_SHA256'] or Path(p).read_bytes()!=Path(row['source']).read_bytes():raise RuntimeError('EXP251_EXACT_COPY_VALIDATION')

scratch=HERE/'source_validation/synthetic_checkpoint';scratch.mkdir(parents=True,exist_ok=False)
actual={'llm':0,'reproduction':0,'regression':0,'patch':0,'dense':0};flags={'model_settled':False,'native_complete':False}
class MockOwner:
 def __init__(self,out):
  self.out=out;self.calls=0;self.out_tokens=0;self.native_calls=0;self.native_actual_OS_processes=0;self.original_files={'demo.py':'value=0\n'};self.files=copy.deepcopy(self.original_files);self.snapshots={'C0':{'id':'C0'}};self.snapshot_files={'C0':copy.deepcopy(self.files)};self.current_snapshot=self.snapshots['C0'];self.patch_candidates=[];self.rows=[];self.forward_records=[];self.t0={'source_synthetic_no_science':True};self.contract={'method_source_seal':{'synthetic':True}}
 def fixed_endpoint(self):pass
 def business_files(self):return copy.deepcopy(self.files)
 def restore(self,s):self.current_snapshot=s;self.files=copy.deepcopy(self.snapshot_files[s['id']])
 def apply_patch(self,edits,label):
  actual['patch']+=1;self.files['demo.py']='value=1\n';self.snapshots['s1']={'id':'s1'};self.snapshot_files['s1']=copy.deepcopy(self.files);self.current_snapshot=self.snapshots['s1'];self.patch_candidates.append(label);return self.current_snapshot
 def llm(self,*args):
  if not flags['model_settled']:raise BoundaryReady()
  actual['llm']+=1;self.calls+=1;self.out_tokens+=7;return {'content':'synthetic complete response','usage':{'completion_tokens':7}}
 def run_reproduction(self,*args):
  if not flags['native_complete']:raise BoundaryReady()
  actual['reproduction']+=1;self.native_calls+=1;return {'reproduced':True,'synthetic':True}
 def run_regression(self,*args):actual['regression']+=1;self.native_calls+=1;return {'passed':True,'synthetic':True}
 def select(self,s,reason):self.restore(s);return {'snapshot':s,'reason':reason}
 def dense_retrieval(self,*args):actual['dense']+=1;return (['demo.py'],{'synthetic':True})
def trajectory(o):
 o.business_files();o.llm('model',[{'role':'user','content':'complete synthetic message'}],.8,17,9)
 o.restore({'id':'C0'});s=o.apply_patch([{'path':'demo.py','old':'0','new':'1'}],'patch')
 o.run_reproduction('synthetic',s);o.run_regression(s,['public']);o.dense_retrieval({},'query','cache',['demo.py']);return o.select(s,{'synthetic_vote':1})
paused=[]
for i in range(3):
 o=MockOwner(scratch/'replay');j=Journal(o)
 try:result=trajectory(o)
 except BoundaryReady:
  paused.append(i)
  pending=read(j.root/'actions'/('%06d.json'%j.cursor))
  if pending['status']!='PREPARED_NOT_STARTED':raise RuntimeError('EXP251_SYNTHETIC_BOUNDARY_MISCLASSIFIED_UNKNOWN')
 if i==0:flags['model_settled']=True
 elif i==1:flags['native_complete']=True
if paused!=[0,1] or o.calls!=1 or o.out_tokens!=7 or o.native_calls!=2 or o.files!={'demo.py':'value=1\n'} or actual!={'llm':1,'reproduction':1,'regression':1,'patch':1,'dense':1}:raise RuntimeError('EXP251_SYNTHETIC_REPLAY_DUPLICATED_ACTION_OR_STATE')
drift=False
try:
 bad=MockOwner(scratch/'replay');Journal(bad);bad.business_files();bad.llm('changed',[],.8,17,9)
except RuntimeError as e:drift='CURSOR_DRIFT' in str(e)
if not drift:raise RuntimeError('EXP251_SYNTHETIC_DRIFT_NOT_REJECTED')
save(HERE/'SOURCE_VALIDATION251.json',{'schema':'EXP251-source-zero-model-native-validation/1','source_AST_parsed':parsed,'native_entry_3_8_syntax_passed':True,'exact_source_copies':len(mapping),
 'synthetic_action_checkpoint':{'three_fresh_process_equivalent_owner_passes':3,'boundary_pauses':paused,'completed_actions_invoked_once':actual,'settled_same_trial_replay_no_duplicate':True,'action_body_drift_rejected':drift},
 'actual_model_product_native_private_encoder_finance':0,'synthetic_is_not_science_result':True})
# Only this invocation's explicitly owned synthetic temporary subtree is removed.
if scratch.resolve()!= (HERE/'source_validation/synthetic_checkpoint').resolve() or not scratch.resolve().is_relative_to(HERE):raise RuntimeError('EXP251_TEMP_SCOPE')
shutil.rmtree(scratch)
print(canonical({'status':'SOURCE_AND_ATOMIC_REPLAY_CHECK_PASS','parsed':len(parsed),'exact_copies':len(mapping),'actual_model_native':0}))
