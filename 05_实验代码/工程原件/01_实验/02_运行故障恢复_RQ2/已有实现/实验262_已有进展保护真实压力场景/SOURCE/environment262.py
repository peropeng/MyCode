"""Complete original MAX3/relations/current-feedback/SET method environment.

The original eleven core files are unchanged. The two rank conditions substitute
only a frozen G plan. NO_DIAG obtains current failure anchors from the unchanged
body and retrieves historical edits chronologically, without opening a G plan.
"""
import argparse, ast, difflib, inspect, types
from decimal import Decimal
from common262 import *
CORE = SOURCE / 'ours_core'
sys.path.insert(0, str(CORE))
import ranked_repair248 as core
import relations248, current_feedback248, feedback_codec242
import publicpack_v2_224 as codec
import shared_projection224 as projection
from progress_guard240 import RepairProgressGuard, source_sha
import shared_input262 as shared_input249


def extract_functions(path, names, namespace):
    nodes = [n for n in ast.parse(Path(path).read_text('utf-8-sig')).body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in nodes} == names
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path) + ':selected-original-pure-functions', 'exec'), namespace)


def original_body():
    ns = {'copy': copy, 'json': json, 'hashlib': hashlib, 'canonical': canonical, 'digest': digest, 'save': save, 'ast': ast, 'Path': Path,
          'projection': projection, 'relations240': relations248, 'current_feedback248': current_feedback248,
          'codec': codec, 'feedback_codec242': feedback_codec242}
    extract_functions(SOURCE / 'ours_entry249_original.py', {'assignment'}, ns)
    ns['shared'] = types.SimpleNamespace(TOOLS=ns['assignment'](OLD / 'ancestor_sources/common_environment224.py', 'TOOLS'))
    ns['masked_boundary242'] = types.SimpleNamespace(TOOLS=ns['assignment'](OLD / 'masked_boundary242.py', 'TOOLS'))
    exec(compile((CORE / 'body248.py').read_text('utf-8-sig'), str(CORE / 'body248.py'), 'exec'), ns)
    return ns['body']


def chronological_evidence(env):
    # Preserve original ordinal/call-ID, changed-path and real before!=after
    # filtering exactly; replace only the source-order branch with chronology.
    tree = ast.parse((CORE / 'ranked_repair248.py').read_text('utf-8-sig'))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_source_evidence')
    fn.name = '_chronological_public_evidence260'
    branch = next(i for i,n in enumerate(fn.body) if isinstance(n, ast.If) and ast.unparse(n.test).startswith('env.method =='))
    replacement = ast.parse("order = ordinals.copy()\nreceipt['order_source'] = 'No diagnosis: original chronological public successful changed business edits'\nreceipt['no_rank_plan_or_score_read'] = True").body
    fn.body[branch:branch+1] = replacement
    ns = dict(vars(core))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), str(CORE / 'ranked_repair248.py') + ':NO_DIAG-order-only-adaptation', 'exec'), ns)
    receipt, selected = ns[fn.name](env)
    receipt['system_control_start'] = 'Current complete public feedback business frames/API names from current_feedback248 and failure_anchors248; historical edits only chronological'
    return receipt, selected


_original_source_evidence = core._source_evidence
def control_evidence(env):
    return chronological_evidence(env) if env.control == 'NO_DIAG' else _original_source_evidence(env)
core._source_evidence = control_evidence


def inherited_environment():
    tree = ast.parse((SOURCE / 'ours_entry249_original.py').read_text('utf-8-sig'))
    old = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Environment')
    names = {'business_files', 'read_file', 'initial_guard_observation', 'source_evidence', 'diff', 'snapshot', 'restore', 'select', 'record', 'checkpoint_boundary', 'reader', 'apply_patch'}
    old.name = 'OriginalEnvironmentMethods'
    old.body = [n for n in old.body if isinstance(n, ast.FunctionDef) and n.name in names]
    assert {n.name for n in old.body} == names
    ns = dict(globals())
    exec(compile(ast.fix_missing_locations(ast.Module(body=[old], type_ignores=[])), str(SOURCE / 'ours_entry249_original.py') + ':original-Env-methods', 'exec'), ns)
    return ns[old.name]


class Environment(inherited_environment()):
    def __init__(self, contract_path, *, preview=True, policy_path=None, finance_grant_path=None, whole_grant_path=None):
        preparation_started = time.monotonic()
        self.contract_path=Path(contract_path).resolve();self.contract=read(self.contract_path)
        self.out=owned(self.contract['output_root']);self.control='SOURCE3';self.condition=self.contract['policy']
        self.preview=preview;self.policy_path=policy_path;self.finance_grant_path=finance_grant_path;self.whole_grant_path=whole_grant_path
        mode={'SET':'PROGRESS_SET','COUNT':'COUNT_TNR','O_ONLY':'ORDINARY_GUARD'}[self.condition]
        self.source_seal=verify_seal(self.contract['method_source_seal'])
        start=verify_ref(self.contract['current_partial_start'])
        if start.get('current_qualified_partial_START') is not True:raise RuntimeError('EXP262_CURRENT_PARTIAL_START_NOT_QUALIFIED')
        state=verify_ref(self.contract['pressure_state']);self.task_id='getmoto__moto-7081'
        self.files={p:(Path(state['source_root'])/p).read_bytes().decode('utf-8') for p in state['business_SHA256']}
        if source_sha(self)!=state['business_SHA256'] or start['business_SHA256']!=state['business_SHA256']:raise RuntimeError('EXP262_EXACT_PARTIAL_BUSINESS_DRIFT')
        p=read(E/'PROTOCOL262_FALSE.json');self.ref=copy.deepcopy(p['original_public_binding']);self.ref['G_frozen_plan']=self.contract['G_plan']['path'];verify_ref(self.contract['G_plan'])
        self.pack=verify_ref(self.contract['public_pack']);self.semantic=codec.decode(self.pack)
        self.public_contract=verify_ref(self.contract['public_contract']);self.scope=verify_ref(self.contract['public_test_scope_contract'])
        if self.scope.get('materialization_qualified') is not True or self.scope.get('Root_original_G_O_public_permission_accepted') is not True:raise RuntimeError('EXP262_CURRENT_MASKED_PUBLIC_SCOPE_NOT_QUALIFIED')
        self.supports={p:h for p,h in {**self.scope['business_and_support_files_in_view'],**self.scope['public_test_py_files_SHA256']}.items() if p not in self.files}
        self.original_files=copy.deepcopy(self.files);self._failure_anchor_initial_files=copy.deepcopy(self.files)
        self.config=verify_ref(self.contract['common_input_configuration'])
        self.method=core.METHODS[0];self.rows=[];self.calls=0;self.native_calls=0;self.out_tokens=0
        self.rejected_history=[];self.snap_files={};self.snap_diffs={};self.forward_records=[];self.checkpoint={}
        self.arm='FULL_CLOSURE_PRESSURE_'+self.condition;self.context_mode='RELATION';self.closure_enabled=True;self.state_admission_mode=mode
        self.repo_root=self.out/'current_actor/repo';self.active=self.repo_root.parent;self._paths={'frozen':Path(self.public_contract['frozen_public_test_root'])}
        self.public_regression_nodes=list(self.contract['ordinary_nodes']);self.recovery_goal_nodes=list(self.contract['goal_nodes'])
        self.initial_validation=copy.deepcopy(start['public_validation']);guard=RepairProgressGuard.begin(self,self.initial_validation)
        if sorted(guard.initial_goal_pass)!=start['current_P']:raise RuntimeError('EXP262_CURRENT_P_NOT_DERIVED_FROM_CURRENT_NATIVE')
        self._Root_C0_unprojected_feedback=core._public_feedback(guard.current_public_feedback(source_sha(self)))
        current_outcomes=start['public_validation']['native_record']['pytest']['outcomes']
        self.initial_public_feedback={n:copy.deepcopy(current_outcomes[n]) for n in self.recovery_goal_nodes if current_outcomes[n]['status']!='passed'}
        self._encoded_initial_public_failure=copy.deepcopy(self.pack['semantic_structure']['failure_feedback']);self._initial_public_captured_output=None
        self.task={'failure_feedback':copy.deepcopy(self.initial_public_feedback)}
        self.goal='Continue from a previously exposed, currently validated partial repair; recover the remaining public failure and preserve current public ordinary behavior. Original issue background: '+self.semantic['original_issue']
        self.initial_snapshot={'id':'PARTIAL_START','label':'EXPOSED_PARTIAL_PRESSURE','inventory_sha256':digest({**source_sha(self),**self.supports}),'diff':{},'archive_path':str(self.out/'snapshots/PARTIAL_START')}
        self.current_snapshot=copy.deepcopy(self.initial_snapshot);self.snap_files['PARTIAL_START']=copy.deepcopy(self.files);self.snap_diffs['PARTIAL_START']=[]
        self.shared_current_C0_supplement,self.shared_current_C0_decoded=shared_input249.supplement(self.config,self.task_id)
        if self.shared_current_C0_decoded!=self._Root_C0_unprojected_feedback:raise RuntimeError('EXP262_COMPLETE_CURRENT_FEEDBACK_NOT_ROOT_SHARED_OBJECT')
        self._native_witness_by_inventory={digest(source_sha(self)):start['native_record_ref']['sha256']}
        self.protocol_origin=E/'PUBLIC_RUNTIME_SCOPE262.json'
        t0=self.out/'SCIENCE_T0_TRIAL_PREPARATION_STARTED.json'
        if preview:
            self.started=preparation_started
            self.original_started={'actual_POST_not_started':True,'preparation_only':True,'preview_clock_does_not_start_science':True}
        else:
            granted_start=read(whole_grant_path)['flow']['original_T0_monotonic']
            if not t0.exists():save(t0,{'monotonic':granted_start,'at_UTC':now(),'actual_POST_not_started':True,'task_id':self.task_id,'policy':self.condition,'trial_id':self.contract['trial_id']})
            self.started=read(t0)['monotonic']
            self.original_started=read(t0)
        self.body_function=original_body();self.transport=None;self.whole_grant=None
        if not preview:
            self.whole_grant_SHA256=sha(whole_grant_path);self.whole_grant=read(whole_grant_path);self.check_execution()
            finance_policy=read(policy_path);finance_seal=verify_ref(finance_policy['source_seal']);engines=[Path(p) for p in finance_seal['sources'] if Path(p).name=='isolation_transport.py']
            if len(engines)!=1:raise RuntimeError('EXP262_EXACT_ROOT_FINANCE_ENGINE_REQUIRED')
            sys.path.insert(0,str(engines[0].parent));finance_engine=module('_exp262_Root_reviewed_finance_engine',engines[0]);self.transport=finance_engine.make_transport(policy_path,finance_grant_path)
            self.check_execution()

    def time_left(self):
        end = datetime.datetime.fromisoformat('2026-10-12T23:29:05+08:00').timestamp()
        return min(1800 - (time.monotonic() - self.started), end - time.time())

    def check_execution(self):
        g = self.whole_grant
        if not g or not all(g.get(k) is True for k in ('execution_authorized','model_generation_authorized','native_execution_authorized','Root_full_method_qualified','Root_same_C0_public_scope_qualified','delegate_exact_child_actions_authorized')): raise RuntimeError('EXP262_DEFAULT_FALSE_WHOLE_SCIENTIFIC_GRANT')
        if g.get('private_authorized') is not False or g.get('old_flow_resume_authorized') is not False: raise RuntimeError('EXP262_NO_PRIVATE_OR_OLD_FLOW_AUTHORITY')
        if sha(self.whole_grant_path) != self.whole_grant_SHA256 or any(Path(p).exists() for p in g.get('root_stop_paths',[])): raise RuntimeError('EXP262_LIVE_ROOT_AUTHORITY_CHANGED_OR_STOPPED')
        if g['method_contract'] != {'path':str(self.contract_path), 'sha256':sha(self.contract_path)}: raise RuntimeError('EXP262_WHOLE_CONTRACT_DRIFT')
        verify_seal(self.contract['method_source_seal'])
        if self.transport is not None:
            owner=self.transport.current.owner()
            if owner.get('owner_PID')!=g['owner_PID'] or owner.get('owner_birth')!=g['owner_birth']:raise RuntimeError('EXP262_REAL_PRIMARY_OWNER_BIRTH_NOT_ROOT_GRANT')
            self.transport.control.check_new_owner_job(owner)
        if self.time_left() <= 0: raise BudgetExhausted('EXP262_FIXED_BUDGET_OR_WINDOW_CUTOFF')
        if self.calls > 128 or self.out_tokens > 131072: raise BudgetExhausted('EXP262_COMMON_MODEL_RESOURCE_BUDGET_EXHAUSTED')

    def body(self, role, messages, temperature, seed, max_tokens, reader_index=0, tools=None):
        value = self.body_function(self, role, messages, temperature, seed, max_tokens, reader_index, tools)
        value = current_feedback248.finish_body(self, value)
        value['seed'] = int(hashlib.sha256(canonical({'master':self.contract['trial_master_seed'],'task':self.task_id,'stage':role,'original_fixed_stage_seed':int(seed),'reader_index':reader_index}).encode()).hexdigest()[:8],16)%2147483647
        # The reviewed finance transport injects the same complete common C0.
        # Preview applies it locally to verify exact actual-HTTP body bounds.
        return value

    def llm(self, role, messages, temperature, seed, max_tokens, schema=None, tools=None):
        current = copy.deepcopy(messages); reader_index = 0
        while True:
            self.calls += 1
            scientific_body = self.body(role, current, temperature, seed, max_tokens, reader_index, tools)
            value = shared_input249.inject(scientific_body, self.config, self.task_id)
            slot = self.out / 'calls' / ('call' + str(self.calls).zfill(3))
            config = {'max_per_call_output':16384, 'official_model_input_capacity_tokens':1048576}
            ns = {'canonical':canonical, 'D':Decimal, 'GateRejected':RuntimeError}
            extract_functions(COMMON / 'finance_queue_remaining_SOURCE/continuous_core_v3.py', {'bounds'}, ns)
            bounds = ns['bounds'](value, config)
            if (slot / 'FIRST_UNPOST_BODY.json').exists() and read(slot / 'FIRST_UNPOST_BODY.json') != value:
                raise RuntimeError('EXP262_SAME_FLOW_REPLAY_BODY_DRIFT_NO_POST')
            save(slot / 'FIRST_UNPOST_BODY.json', value)
            save(slot / 'FIRST_UNPOST_READY.json', {'schema':'EXP262-complete-body-unposted-ready/1','task_id':self.task_id,'control':self.control,'trial_id':self.contract['trial_id'],'attempt':self.checkpoint['attempt'],'reader_index':reader_index,'call_ordinal':self.calls,'role':role,'body_SHA256':digest(value),'canonical_bytes':len(canonical(value).encode()),'complete_original_bounds':bounds,'full_peak_reserve_CNY':bounds['global_reserve'],'model_native_private_finance':0})
            checkpoint = copy.deepcopy(self.checkpoint); checkpoint['cursor']['calls'] = self.calls - 1
            checkpoint.update(prepared_body=value, complete_current_messages=value['messages'], current_reader_index=reader_index, status='EXACT_REQUEST_READY_NOT_POSTED')
            save(slot / 'checkpoint.json', checkpoint)
            if self.preview:
                save(self.out / 'STATUS.json', {'status':'MODEL_READY_NOT_POSTED','task_id':self.task_id,'control':self.control,'trial_id':self.contract['trial_id'],'call':self.calls,'body_SHA256':digest(value),'full_peak_reserve_CNY':bounds['global_reserve'],'actual_model_generation':0})
                raise BoundaryReady()
            self.check_execution()
            context = dict(self.whole_grant['flow']); context.update(stage='recover',stage_index=self.checkpoint['attempt']-1,stage_turn=reader_index+1,call_ordinal=self.calls,role=role,model_request_boundary='UNPOST_READY',fresh_flow_id=self.whole_grant['flow']['flow_id'],old_flow_resume_authorized=False)
            self._finance_isolation_context = context
            if (slot / 'SETTLED_RAW_RESPONSE.json').exists():
                response = read(slot / 'SETTLED_RAW_RESPONSE.json')
                replayed = True
            else:
                response = self.transport.generate(self, scientific_body, role, self.contract['finance_phase'])
                replayed = False
            receipt=response.get('_finance_receipt',{})
            if receipt.get('status')!='SETTLED' or receipt.get('body_SHA256')!=digest(value) or receipt.get('flow_id')!=context['flow_id'] or receipt.get('call_ordinal')!=self.calls or receipt.get('role')!=role:
                raise RuntimeError('EXP262_RAW_RESPONSE_NOT_EXACT_SETTLED_SAME_FLOW_BODY')
            usage = response['usage']; self.out_tokens += usage['completion_tokens']
            save(slot / 'SETTLED_RAW_RESPONSE.json', response)
            message = response['choices'][0]['message']; finish = response['choices'][0].get('finish_reason')
            self.forward_records.append({'call':self.calls,'body_SHA256':digest(value),'response_SHA256':sha(slot / 'SETTLED_RAW_RESPONSE.json'),'exact_same_flow_only':True,'exact_settled_replay_no_POST':replayed})
            if not message.get('tool_calls'):
                return {'content':message.get('content') or '', 'message':message, 'usage':usage,'call_ordinal':self.calls,'finish_reason':finish}
            current = [copy.deepcopy(m) for m in value['messages'] if not str(m.get('content','')).startswith(shared_input249.TAG)]
            current.append(copy.deepcopy(message))
            for call in message['tool_calls']:
                name = call['function']['name']
                try: output = self.reader(name,json.loads(call['function']['arguments']))
                except (ValueError,KeyError,TypeError) as exc: output = {'status':'PUBLIC_READER_ARGUMENT_ERROR','message':str(exc),'correct_public_failure_node_ids':sorted(self.initial_public_feedback),'protected_contents_not_returned':True}
                if name in ('read_full_failure','read_public_history'):
                    output = projection.project(output,[(self.repo_root,'/workspace/repo'),(self._paths['frozen'],'/public-tests'),(self.active,'/workspace'),(self.out,'/public-feedback')]); output,_ = feedback_codec242.encode(output)
                current.append({'role':'tool','tool_call_id':call['id'],'content':canonical(output)})
                save(self.out / 'tool_boundaries' / (str(self.calls).zfill(3)+'_'+call['id']+'.json'), {'complete_messages':current,'source_SHA256':source_sha(self),'tool':call,'output':output,'no_original_unmasked_test_or_private_read':True})
            reader_index += 1

    def run_regression(self, snapshot, label):
        self.check_execution()
        self.checkpoint_boundary('PUBLIC_NATIVE_READY', inspect.currentframe().f_back.f_locals)
        from native262 import candidate_native
        receipt = candidate_native(self, snapshot, label)
        self.native_calls += 1
        self._native_witness_by_inventory[digest(source_sha(self))] = receipt['public_native_SHA256']
        probe = read(receipt['public_native_path'])
        ordinary = {n:{**probe['pytest']['outcomes'][n],'outcome':probe['pytest']['outcomes'][n]['status']} for n in self.public_regression_nodes}
        failures = sum(v['status'] != 'passed' for v in ordinary.values())
        return {'passed':failures==0,'failure_count':failures,'outcomes':ordinary,'status':'GUARDED_ORDINARY_REGRESSION','native_record':{**probe,'path':receipt['public_native_path']},'public_goal_not_added_to_paper_ranking':True}

    def record(self, stage, data):
        self.rows.append({'stage':stage,'evidence':copy.deepcopy(data)})
        save(self.out / 'PUBLIC_STAGE_RECORDS.json', self.rows)


def main():
    p = argparse.ArgumentParser(); p.add_argument('--contract',required=True); p.add_argument('--execute',action='store_true'); p.add_argument('--policy'); p.add_argument('--finance-grant'); p.add_argument('--whole-grant')
    args = p.parse_args(); env = Environment(args.contract,preview=not args.execute,policy_path=args.policy,finance_grant_path=args.finance_grant,whole_grant_path=args.whole_grant)
    try:
        result = core.run(env)
        save(env.out / 'PUBLIC_ONLY_NATURAL_TERMINAL.json',result); save(env.out / 'SELECTED_BUSINESS_SOURCE.json',env.files)
        save(env.out / 'STATUS.json',{'status':result['status'] if result.get('error') else 'PUBLIC_ONLY_NATURAL_TERMINAL','core_status':result['status'],'task_id':env.task_id,'control':env.control,'trial_id':env.contract['trial_id'],'error':result.get('error'),'budget_censored_not_scientific_normal_failure':result['status']=='BUDGET_CENSORED','requires_separate_once_independent_final_acceptance':True})
    except BoundaryReady: pass
    finally:
        save(env.out / 'PUBLIC_STAGE_RECORDS.json',env.rows); save(env.out / 'EXACT_SETTLED_REPLAY.json',env.forward_records)
    print(canonical(read(env.out / 'STATUS.json')),flush=True)

if __name__ == '__main__': main()
