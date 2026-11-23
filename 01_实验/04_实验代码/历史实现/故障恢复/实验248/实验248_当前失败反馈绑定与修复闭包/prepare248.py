"""Pure public-prefix replay; never imports a transport or invokes native/private IO."""
import ast, copy, datetime, difflib, hashlib, importlib.util, inspect, json, os, sys, textwrap, types, time
from decimal import Decimal
from pathlib import Path

sys.dont_write_bytecode = True
if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = Path('D:/Code/毕设/graduate-thesis-experiments')
OLD = ROOT/'工作区/1011-our19'
FIN = ROOT/'工作区/1010-unified-six/finance_queue_remaining_SOURCE'
COMMON = ROOT/'工作区/1011-unbudgeted-common'
sys.path[:0] = [str(OLD), str(FIN)]

def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def canonical(v): return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def digest(v): return hashlib.sha256(canonical(v).encode()).hexdigest()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def clean(v):
    if isinstance(v, dict): return {str(k): clean(x) for k,x in v.items()}
    if isinstance(v, (set, tuple)): return [clean(x) for x in sorted(v)]
    if isinstance(v, list): return [clean(x) for x in v]
    if isinstance(v, Path): return str(v)
    return v
def save(p,v):
    p=Path(p).resolve(); assert p.is_relative_to(HERE)
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.'+str(os.getpid())+'.tmp')
    with tmp.open('w',encoding='utf-8') as stream:
        json.dump(clean(v),stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    os.replace(tmp,p)
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def assignment(path,name):
    tree=ast.parse(Path(path).read_text('utf-8-sig')); ns={}
    for node in tree.body:
        if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in node.targets):
            exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
        elif isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id==name:
            exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
    return ns[name]

import relations248 as relations240, current_feedback248, feedback_codec242, public_projection181
from progress_guard240 import RepairProgressGuard, source_sha
projection=module('_projection248',OLD/'shared_projection224.py')
codec=module('_codec248',OLD/'publicpack_v2_224.py')
common=module('_common_input248',FIN/'common_model_input_six.py')
config=read(COMMON/'FINANCE_CONFIG_CONTINUE.json')

original=(OLD/'ranked_repair240.py').read_text('utf-8-sig')
assert original.count('selected = all_evidence[:MAX_ATTEMPTS]')==1
assert original.count('for attempt in range(1, MAX_ATTEMPTS + 1):')==1
source=original
source=source.replace('calls += 1\n            try:', 'env.checkpoint_boundary("MODEL_READY", locals())\n            calls += 1\n            try:')
(HERE/'ranked_repair248.py').write_text(source,'utf-8')
core=module('_ranked248',HERE/'ranked_repair248.py')

environment_source=(OLD/'environment240.py').read_text('utf-8-sig')
env_ast=ast.parse(environment_source)
klass=next(n for n in env_ast.body if isinstance(n,ast.ClassDef) and n.name=='Environment240')
node=next(n for n in klass.body if isinstance(n,ast.FunctionDef) and n.name=='body')
body_source=textwrap.dedent(ast.get_source_segment(environment_source,node))
body_source=body_source.replace("public_failure={'initial_public_failure': self.initial_public_feedback,\n                                        'latest_public_feedback': latest_current}", 'public_failure=current_feedback248.anchor_input(self,payload,files,latest_current)')
assert 'current_feedback248.anchor_input' in body_source
(HERE/'body248.py').write_text(body_source+'\n','utf-8')
namespace={'copy':copy,'json':json,'hashlib':hashlib,'canonical':canonical,'digest':digest,'save':save,
    'projection':projection,'relations240':relations240,'current_feedback248':current_feedback248,'codec':codec,'feedback_codec242':feedback_codec242,
    'shared':types.SimpleNamespace(TOOLS=assignment(OLD/'ancestor_sources/common_environment224.py','TOOLS')),
    'masked_boundary242':types.SimpleNamespace(TOOLS=assignment(OLD/'masked_boundary242.py','TOOLS'))}
exec(compile(body_source,'body248.py','exec'),namespace)
financial_source=(FIN/'continuous_core_v3.py').read_text('utf-8-sig')
bounds_node=next(n for n in ast.parse(financial_source).body if isinstance(n,ast.FunctionDef) and n.name=='bounds')
bounds_namespace={'canonical':canonical,'D':Decimal,'GateRejected':RuntimeError}
exec(compile(ast.Module(body=[bounds_node],type_ignores=[]),'original_pure_financial_bounds','exec'),bounds_namespace)

class Ready(BaseException): pass
class Mismatch(BaseException): pass
class Replay:
    def body(self,*args,**kwargs):return current_feedback248.finish_body(self,namespace['body'](self,*args,**kwargs))
    def __init__(self,index,ref):
        self.index=index;self.ref=ref;self.task_id=ref['task_id'];self.method=core.METHODS[0]
        self.oldout=OLD/'r'/str(index)/'f';self.out=HERE/'replay'/str(index)
        self.records=[json.loads(line) for line in (self.oldout/'stage_ledger.jsonl').read_text('utf-8-sig').splitlines() if line.strip()]
        self.records=[r for r in self.records if r['stage'] not in ('ranked_repair178_selection','ranked_repair178_terminal_frontier_eligible_selection')]
        pack_path=ROOT/'工作区/1008-2320-exp224-flash-common/实验/实验224_二十三题Flash完整共同恢复比较/v2_auth_direct_publicpack/packs'/(self.task_id+'.json')
        self.pack=read(pack_path);semantic=codec.decode(self.pack)
        self.protocol_origin=OLD/'protocol240.json'
        self._initial_public_captured_output=copy.deepcopy(semantic.get('original_public_captured_output'))
        self.initial_public_feedback=copy.deepcopy(semantic['failure_feedback'])
        self.task={'failure_feedback':copy.deepcopy(self.initial_public_feedback)}
        self.goal='Recover the observed public failure and preserve initially-passing public ordinary behavior. Original issue background: '+semantic['original_issue']
        self._encoded_initial_public_failure=copy.deepcopy(self.pack['semantic_structure']['failure_feedback'])
        self.files={p:(Path(ref['template'])/p).read_text('utf-8') for p in self.pack['c0_business_paths_sha256']}
        assert source_sha(self)==self.pack['c0_business_paths_sha256'],'C0 source drift'
        self._failure_anchor_initial_files=copy.deepcopy(self.files)
        self.initial_snapshot=read(self.oldout/'snapshots/s0001/snapshot.json')
        self.current_snapshot=copy.deepcopy(self.initial_snapshot)
        self.snap_files={self.initial_snapshot['id']:copy.deepcopy(self.files)};self.snap_diffs={self.initial_snapshot['id']:[]}
        self.repo_root=OLD/'r'/str(index)/'n/repo';self.active=self.repo_root.parent
        self._paths={'frozen':Path(ref['frozen_tests'])}
        self.arm='FULL_CLOSURE_SET';self.context_mode='RELATION';self.closure_enabled=True
        self.state_admission_mode='PROGRESS_SET';self.public_regression_nodes=ref['public_regression_nodes']
        observed=next(r['evidence'] for r in self.records if r['stage']=='progress_initial_actual_public_observation_reused')
        assert sha(observed['path'])==observed['sha256']
        raw=read(observed['path']);self.recovery_goal_nodes=sorted(set(raw['requested_nodes'])-set(self.public_regression_nodes))
        self._native_witness_by_inventory={digest(source_sha(self)):observed['sha256']}
        self.initial_validation={'native_record':raw,'outcomes':{n:copy.deepcopy(raw['pytest']['outcomes'][n]) for n in self.public_regression_nodes}}
        self.shared_current_C0_supplement,self.shared_current_C0_decoded=common.supplement(config,self.task_id)
        assert self.shared_current_C0_supplement['current_C0_native_record_SHA256']==observed['sha256']
        assert self.shared_current_C0_decoded['observed_business_inventory_sha256']==digest(source_sha(self))
        guard=RepairProgressGuard.begin(self,self.initial_validation)
        self._Root_C0_unprojected_feedback=core._public_feedback(guard.current_public_feedback(source_sha(self)))
        self.calls=0;self.native_calls=0;self.out_tokens=0;self.rejected_history=[];self.reuse=[];self.rows=[];self.checkpoint={}
        self.public_queue=[r['evidence'] for r in self.records if r['stage']=='ordinary_regression']
        self.app_queue=[r['evidence'] for r in self.records if r['stage']=='patch_application']
        t0_path=HERE/'science'/self.task_id/'SCIENCE_T0_ACTUAL_POST_DISPATCH.json'
        self.original_started=read(t0_path) if t0_path.exists() else {'new_mechanism_version':248,'actual_not_started':True,'source_preparation_UTC':now(),'old_source_run_scientific_clock_retained_as_prior_record':read(OLD/'r'/str(index)/'STARTED.json')}
        self.public_queue=[];self.app_queue=[]
    def business_files(self):return self.files
    def read_file(self,p):return self.files[p]
    def initial_guard_observation(self):return copy.deepcopy(self.initial_validation)
    def source_evidence(self):return core._source_evidence(self)
    def diff(self):return copy.deepcopy(self.snap_diffs[self.current_snapshot['id']])
    def snapshot(self,label):return copy.deepcopy(self.current_snapshot)
    def select(self,snapshot,reason):
        self.restore(snapshot)
        return {'snapshot':copy.deepcopy(snapshot),'reason':copy.deepcopy(reason),'uses_hidden':False,'pure_public_replay_selection':True}
    def restore(self,snapshot):
        self.current_snapshot=copy.deepcopy(snapshot);self.files=copy.deepcopy(self.snap_files[snapshot['id']])
    def record(self,stage,data):self.rows.append({'stage':stage,'evidence':copy.deepcopy(data)})
    def checkpoint_boundary(self,status,state):
        guard=state.get('admission')
        self.checkpoint={'schema':'public-prefix-safe-resume/1','status':status,'at_utc':now(),'task':self.task_id,
          'attempt':state.get('attempt'),'messages':state.get('messages'),'seed':state.get('seed'),
          'cursor':{'calls':self.calls,'native':self.native_calls,'output_tokens':self.out_tokens},
          'guard':vars(guard) if guard else None,'current_snapshot':self.current_snapshot,
          'business_source':self.files,'business_source_sha256':source_sha(self),
          'public_events':state.get('public_events'),'candidates':state.get('candidates'),'history':state.get('history'),
          'first_pass':state.get('first_pass'),'best_key':state.get('best_key'),'initial_source':state.get('initial_source'),
          'original_science_started':self.original_started,'forward_lease':'NOT_STARTED_SOURCE_ONLY',
          'reused_calls':self.reuse,'POST':0,'new_native':0,'private_reads':0,'ledger_writes':0,
          'unknown_or_inflight_may_not_resend':True,
          'current_native_witness_by_business_inventory':copy.deepcopy(self._native_witness_by_inventory)}
        save(self.out/'checkpoint.json',self.checkpoint)
    def llm(self,role,messages,temperature,seed,max_tokens,schema=None,tools=None):
        self.calls+=1
        destination=self.out
        namespace['save']=lambda path,value:save(destination/Path(path).relative_to(self.oldout),value)
        self.out=self.oldout
        try:body=self.body(role,messages,temperature,seed,max_tokens,tools=tools)
        finally:self.out=destination
        body=common.inject(body,config,self.task_id)
        bounds=bounds_namespace['bounds'](body,config)
        save(self.out/'FIRST_UNPOST_BODY.json',body)
        prior=read(self.oldout/'llm/001_request.json')
        save(self.out/'FIRST_UNPOST_READY.json',{'task':self.task_id,'attempt':self.checkpoint['attempt'],
            'body_SHA256':digest(body),'canonical_bytes':len(canonical(body).encode()),'input_upper':bounds['input_bound'],
            'output_reservation':body['max_tokens'],'full_peak_reserve_CNY':str(bounds['global_reserve']),
            'full_unchanged_original_financial_bounds':bounds,'finance_configuration_SHA256':sha(COMMON/'FINANCE_CONFIG_CONTINUE.json'),
            'bounds_source_SHA256':sha(FIN/'continuous_core_v3.py'),'old_body_SHA256':prior['body_SHA256'],
            'old_response_reuse_permitted':False,'old_body_exact_equal':body==prior['body'],
            'POST':0,'new_native':0,'private_reads':0,'ledger_writes':0})
        self.checkpoint['prepared_body']=body;self.checkpoint['status']='FIRST_NEW_BODY_READY_NOT_POSTED'
        save(self.out/'checkpoint.json',self.checkpoint)
        raise Ready()
    def apply_patch(self,edits,label,from_snapshot=None):
        application=copy.deepcopy(self.app_queue.pop(0))
        assert edits==application['edits'],'replayed patch differs'
        if application.get('apply_errors'):
            prospective=copy.deepcopy(self.files);failed=False
            for edit in edits:
                p=edit['path'].removeprefix('repo/')
                if prospective[p].count(edit['old'])!=1:failed=True;break
                prospective[p]=prospective[p].replace(edit['old'],edit['new'],1)
            assert failed,'old application failure is not reproduced'
            return application
        for edit in edits:
            p=edit['path'].removeprefix('repo/');assert self.files[p].count(edit['old'])==1
            self.files[p]=self.files[p].replace(edit['old'],edit['new'],1)
        snap=application['snapshot'];self.snap_files[snap['id']]=copy.deepcopy(self.files)
        self.snap_diffs[snap['id']]=copy.deepcopy(application['raw_diff']);self.current_snapshot=copy.deepcopy(snap)
        for p,h in snap['diff'].items():assert source_sha(self)[p]==h
        return application
    def run_regression(self,snapshot,label):
        self.native_calls+=1;saved=copy.deepcopy(self.public_queue.pop(0))
        # JSONL ledger canonicalization sorts keys. Rebuild the original runtime
        # dictionary order from its untouched public run.json so exact-line-pool
        # serialization, not only decoded semantics, matches the paid wire body.
        native_path=Path(saved['native_record']['path']);probe=read(native_path)
        witness=next(r['evidence'] for r in self.records if r['stage']=='public_native_actual' and Path(r['evidence']['path'])==native_path)
        assert sha(native_path)==witness['sha256']
        outcomes=probe['pytest']['outcomes']
        ordinary={n:{**outcomes[n],'outcome':outcomes[n]['status']} for n in self.public_regression_nodes if n in outcomes}
        failures=sum(v['status']!='passed' for v in ordinary.values())
        result={'passed':failures==0 and len(ordinary)==len(self.public_regression_nodes),'failure_count':failures,
            'outcomes':ordinary,'status':'GUARDED_ORDINARY_REGRESSION','native_record':{**probe,'path':str(native_path)},
            'public_goal_not_added_to_paper_ranking':True}
        assert result==saved,'public native wrapper semantic drift'
        self.record('PUBLIC_NATIVE_EXACT_READONLY_REUSE',{'label':label,'snapshot':snapshot,'validation_sha256':digest(result),'new_native':0})
        return result

def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--indices',default='3,4');args=parser.parse_args()
    tasks=read(COMMON/'COMMON_CONTRACT_SOURCE.json')['task_order'];refs=read(OLD/'selected_task_bindings240.json')['tasks']
    output=[]
    for index in [int(x) for x in args.indices.split(',')]:
        prepare_start_UTC=now();prepare_start_monotonic=time.perf_counter()
        ref=next(copy.deepcopy(row) for row in refs if row['task_id']==tasks[index]);env=Replay(index,ref)
        try:
            result=core.run(env)
            raise RuntimeError('EXP248_BODY_PREPARE_DID_NOT_STOP_BEFORE_MODEL '+canonical(result))
        except Ready:
            output.append({'task':env.task_id,'index':index,'status':'FIRST_NEW_BODY_READY_NOT_POSTED','MAX_ATTEMPTS':core.MAX_ATTEMPTS})
        source_record=next(row['evidence'] for row in env.rows if row['stage']=='ranked_repair178_source_evidence')
        initial_record=next(row['evidence'] for row in env.records if row['stage']=='progress_initial_actual_public_observation_reused')
        save(env.out/'SOURCE_BODY_PREPARATION_COST.json',{'schema':'source-body-preparation-cost/1',
            'started_UTC':prepare_start_UTC,'finished_UTC':now(),'elapsed_seconds':time.perf_counter()-prepare_start_monotonic,
            'scope':'Replay constructor + current C0 public witness verification + frozen RQ1 plan read + actual business/masked AST retrieval + complete first wire body and reserve preparation',
            'scientific_T0_started':False,'source_preparation_does_not_count_as_model_POST_or_native':True,
            'frozen_RQ1_plan_path':source_record['G_frozen_plan'],'frozen_RQ1_plan_SHA256':source_record['G_frozen_plan_sha256'],
            'RQ1_compute_in_this_prepare':0,'RQ1_original_inference_or_training_cost_not_remeasured_or_claimed_zero':True,
            'public_C0_observation_reuse':{'path':initial_record['path'],'SHA256':initial_record['sha256'],'same_source_verified':True,'new_native':0},
            'prior_version_clock_reference':str(OLD/'r'/str(index)/'STARTED.json'),
            'total_chain_time_requires_this_preparation_plus_prior_ranking_preprocessing_cost_and_actual_POST_native_time':True})
        save(env.out/'PUBLIC_PRE_MODEL_RECORDS.json',env.rows)
        save(HERE/'PREPARE_STATUS.json',output)
        print(canonical(output[-1]),flush=True)
if __name__=='__main__':main()
