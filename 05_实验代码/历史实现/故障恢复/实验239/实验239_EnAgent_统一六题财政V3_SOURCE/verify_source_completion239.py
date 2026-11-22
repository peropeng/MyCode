"""Meaningful SOURCE boundary fixtures. No product process, actual model or shared IO."""
import ast,copy,hashlib,json,math,pathlib,sys,types,subprocess
E=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(E));sys.dont_write_bytecode=True
import common166 as C
import flow_bounds239 as F
rows=[]
def case(label,fn):
    fn();rows.append({'case':label,'PASS':True,'actual_product_native':0,'actual_HTTP':0,'actual_private':0,'actual_shared_finance_IO':0})
def denied(fn,fragment):
    try:fn()
    except BaseException as exc:
        assert fragment in str(exc),(type(exc).__name__,str(exc),fragment)
    else:raise AssertionError('EXPECTED_REJECTION '+fragment)
def no_process(*a,**kw):raise AssertionError('SOURCE_FIXTURE_PROCESS_FORBIDDEN')
original_popen=subprocess.Popen;subprocess.Popen=no_process
def assertion(value):assert value
try:
    case('new global deadline None; old12 clock is not active',lambda:assertion(C.DEADLINE is None and C.NO_TEST is None))
    def finite_cases():
        assert F.deadline_for(100.,3600.)==3700.
        assert F.deadline_for(100.,3600.,3600.)==3600.
        for value in (None,True,0,-1,float('inf'),float('nan'),3601):denied(lambda value=value:F.finite_seconds(value),'FINITE_INDIVIDUAL_FLOW_REQUIRED')
        assert F.time_left(3700.,100.)==3600. and F.time_left(3700.,3700.)==0.
    case('finite parent whole-flow deadline and invalid3600 bypasses rejected',finite_cases)
    case('completion flag rejects before any new action',lambda:denied(lambda:F.check_open(('root-stop','local-stop'),lambda p:p=='root-stop'),'USER_STOP_COMPLETION_FLAG'))
    def counter_cases():
        assert F.check_count(32,2048,'PRODUCT_NATIVE')==33
        assert F.check_count(63,2048,'PRODUCT_NATIVE')==64
        assert F.check_count(2047,2048,'PRODUCT_NATIVE')==2048
        denied(lambda:F.check_count(2048,2048,'PRODUCT_NATIVE'),'DECLARED_PRODUCT_NATIVE_ROOT_CAP')
        assert F.check_count(4095,4096,'ALL_OWNED_OS')==4096
        denied(lambda:F.check_count(4096,4096,'ALL_OWNED_OS'),'DECLARED_ALL_OWNED_OS_ROOT_CAP')
    case('old32/63 are not the new native ceiling;2048 and OS4096 enforce next-root denial',counter_cases)
    case('private permission remains separate from execution/native flags',lambda:denied(lambda:F.public_final_permission({'execution_authorized':True,'model_generation_authorized':True,'native_authorized':True,'private_authorized':False,'once_private_authorized':False}),'PRIVATE_ONCE_INDEPENDENT_AUTHORITY_REQUIRED'))
    def classification_cases():
        unknown,within=F.final_classification(1800,3600,False,None,None,False,None,False)
        assert unknown is None and within is True
        unknown,within=F.final_classification(3601,3600,False,None,None,False,None,False)
        assert unknown is None and within is False
    case('past old900 can be within3600; no synthetic private acceptance values assigned',classification_cases)
    # Exercise the actual new native wrapper with an intercepted executor, not a
    # product mock result. Its return is an interception sentinel, no test outcomes.
    import native_executor224 as N
    protocol=C.read(E/'protocol225.json');N.authorization=lambda:protocol;N.require_open=lambda:None
    N.time=types.SimpleNamespace(monotonic=lambda:100.)
    calls=[]
    N.execute=lambda argv,cwd,log,timeout,env:calls.append({'timeout':timeout,'argv':argv}) or {'intercepted_source_boundary':True}
    fake=types.SimpleNamespace(run=types.SimpleNamespace(qualify=types.SimpleNamespace()),_require=lambda:None,search_deadline=1000.,deadline=1100.,_product_native_roots=63)
    N.install(fake)
    result=fake.run.qualify.execute(['synthetic-root'],E,E/'synthetic-uncreated.log',300)
    assert result=={'intercepted_source_boundary':True} and calls==[{'timeout':90,'argv':['synthetic-root']}] and fake._product_native_roots==64
    fake._product_native_roots=2048
    case('actual native facade allows root64, clamps90, rejects root2049 without execution',lambda:denied(lambda:fake.run.qualify.execute(['synthetic-root'],E,E/'synthetic-uncreated.log',90),'DECLARED_PRODUCT_NATIVE_ROOT_CAP'))
    assert len(calls)==1
    import flash_io239 as IO
    assert IO._transport is None and 'exp239_completion_finance_v3' not in sys.modules
    provider_calls=[];IO.module=lambda *a:provider_calls.append(a) or (_ for _ in ()).throw(AssertionError('REAL_FINANCE_PROVIDER_FORBIDDEN'))
    IO.authorization=lambda:(_ for _ in ()).throw(RuntimeError('FRESH_SIX_SCIENCE_ROOT_RELEASE_REQUIRED'))
    case('lazy finance false science grant rejects before provider or shared IO construction',lambda:denied(lambda:IO.generate(types.SimpleNamespace(time_left=lambda:3600.),{},'source','UnifiedSixEnAgent23920261010'),'FRESH_SIX_SCIENCE_ROOT_RELEASE_REQUIRED'))
    assert provider_calls==[] and IO._transport is None
    fake_protocol=copy.deepcopy(protocol);fake_protocol['model_generation_authorized']=True
    IO.authorization=lambda:fake_protocol;IO.require_open=lambda:None
    case('false finance template rejects before provider even with synthetic external grant',lambda:denied(lambda:IO.generate(types.SimpleNamespace(time_left=lambda:3600.),{},'source',fake_protocol['finance_phase']),'COMPLETION_V3_MODEL_FINANCE_PERMISSION_FALSE'))
    assert provider_calls==[]
    import common_six_C0_supplement239 as S
    missing_supplement=copy.deepcopy(protocol)
    missing_supplement.update(common_six_C0_supplement_file=None,common_six_C0_supplement_sha256=None)
    case('fresh common supplement null blocks before model rather than using old pack alone',lambda:denied(lambda:S.load_supplement(protocol['task_order'][0],missing_supplement),'NEW_SHARED_C0_SUPPLEMENT_REQUIRED_BEFORE_MODEL'))
    # In-memory registry fixtures use no actual files and no goal/private values.
    synthetic=copy.deepcopy(protocol)
    synthetic_registry_path=str(C.ROOT/'工作区/1010-unified-six/SOURCE_FIXTURE_NOT_CREATED_REGISTRY.json')
    synthetic['common_six_C0_supplement_file']=synthetic_registry_path;synthetic['common_six_C0_supplement_sha256']='synthetic-registry-hash'
    registry={'task_supplements':{task:{'path':str(C.ROOT/'工作区/1010-unified-six'/('SOURCE_FIXTURE_NOT_CREATED_'+str(i)+'.json')),'sha256':'fixture-'+str(i)} for i,task in enumerate(protocol['task_order'])}}
    storage={synthetic_registry_path:registry}
    hashes={synthetic_registry_path:'synthetic-registry-hash'}
    for task,ref in registry['task_supplements'].items():storage[ref['path']]={'task_id':task,'source_boundary_fixture_only':True};hashes[ref['path']]=ref['sha256']
    S.read=lambda path:copy.deepcopy(storage[str(path)]);S.sha=lambda path:hashes[str(path)]
    snapshot=copy.deepcopy(storage)
    approved,proof=S.load_supplement(protocol['task_order'][0],synthetic)
    assert approved=={'task_id':protocol['task_order'][0],'source_boundary_fixture_only':True}
    assert proof['complete_approved_public_object'] and storage==snapshot
    backend=ast.parse((E/'backend225.py').read_text('utf-8'))
    assert not hasattr(S,'inject')
    assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='inject' for n in ast.walk(backend))
    case('method validates references without appending; Root common-v4 is sole injector',lambda:assertion(storage==snapshot))
    hashes[synthetic_registry_path]='different-registry'
    case('fresh supplement registry SHA drift denies before model',lambda:denied(lambda:S.load_supplement(protocol['task_order'][0],synthetic),'SUPPLEMENT_REGISTRY_DRIFT'))
    assert list(storage.values())[1].get('source_boundary_fixture_only') is True
    for value in (float('inf'),float('nan'),3601):
        case('lazy finance refuses nonfinite/excess owner time '+str(value),lambda value=value:denied(lambda:IO.generate(types.SimpleNamespace(time_left=lambda:value),{},'source',fake_protocol['finance_phase']),'FINITE_INDIVIDUAL_FLOW_REQUIRED'))
    assert provider_calls==[]
    # Audit loader transformations by evaluating only its replacement literals.
    # Do not import the historical Environment, retrieval or any product package.
    boot=ast.parse((E/'bootstrap224.py').read_text('utf-8'))
    rewrites=[]
    for node in ast.walk(boot):
        if not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='original' or len(node.args)<3:continue
        if not isinstance(node.args[1],ast.Constant) or node.args[1].value not in ('environment166.py','flash_environment178.py'):continue
        filename=node.args[1].value;raw=(C.OLD/filename).read_text('utf-8-sig')
        replacements=eval(compile(ast.Expression(node.args[2]),str(E/'bootstrap224.py'),'eval'),{'OLD':C.OLD,'Path':pathlib.Path,'repr':repr,'str':str})
        for a,b in replacements:assert a in raw,(filename,a);raw=raw.replace(a,b)
        ast.parse(raw)
        assert 'self.native_calls>=32' not in raw and 'self.native_calls<32' not in raw
        assert 'time.time()<NO_TEST' not in raw and 'time.time()>=NO_TEST' not in raw
        if filename=='flash_environment178.py':assert 'self.started+900' not in raw and "full['elapsed_seconds']<=900" not in raw
        rewrites.append({'file':str(C.OLD/filename),'source_sha256':C.sha(C.OLD/filename),'rewritten_sha256':hashlib.sha256(raw.encode()).hexdigest(),'pairs':len(replacements),'AST_PASS':True,'not_executed':True})
    assert len(rewrites)==2
    rows.append({'case':'real historical source replacement anchors all present and dynamic cap/None-safe grammar pass','PASS':True,'rewrites':rewrites,'actual_product_native':0,'actual_HTTP':0,'actual_private':0,'actual_shared_finance_IO':0})
    p=protocol['budget'];assert (p['enagent_ensemble_size'],p['enagent_coder_max_steps'],p['enagent_selector_max_turn'])==(3,200,30)
    assert 3*200+1+3*30==691<=p['max_model_calls_per_flow'] and 691*4096<=p['max_output_tokens_per_flow']
    case('paper internal N3/200/30 model/output capacity fits common1024/8388608',lambda:assertion(p['max_model_calls_per_flow']==1024 and p['max_output_tokens_per_flow']==8388608))
    for f in E.rglob('*.py'):ast.parse(f.read_text('utf-8-sig'))
    case('all local source AST valid without importing actor/environment or launching process',lambda:None)
finally:subprocess.Popen=original_popen
receipt={'schema':'EnAgent239-source-completion-boundaries/1','status':'PASS','cases':rows,'case_count':len(rows),'real_product_native':0,'real_HTTP_POST':0,'real_HTTP_GET':0,'real_private':0,'real_shared_finance_IO':0,'no_actual_C0_ABI_job_or_scope_claim':True,'synthetic_executor_interception_calls':1,'model_responses_fabricated':0,'private_acceptance_values_fabricated':0,'Root_actual_mechanical_still_required':True}
(E/'SOURCE_BOUNDARY_FIXTURES239.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8',newline='')
print(json.dumps({'status':receipt['status'],'cases':len(rows),'real_native_HTTP_private_sharedIO':0},ensure_ascii=False))
