"""Independent future PatchPilotNative owner. No API, clone, process or ledger on import."""
import asyncio, ast, base64, copy, datetime, json, os, re, shlex, sys, time, types
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace as NS
from contracts241 import *

class Owner:
    def __init__(self,protocol_path,grant_path,seal_path,contract_path):
        self.protocol_path=Path(protocol_path).resolve();self.grant_path=Path(grant_path).resolve();self.seal_path=Path(seal_path).resolve()
        self.protocol=read(protocol_path);self.grant=read(grant_path);self.seal=read(seal_path);self.contract=read(contract_path)
        self.task_id=self.contract['task_id'];self.method=METHOD;self.finance_phase=FINANCE_PHASE;self.calls=0;self.out_tokens=0
        self.native_roots=1;self.native_calls=0;self.roles={};self.unknown=None;self.budget_end=None;self.public_runs=[]
        self.native_root_kinds={'controller':1};self._native_kind='helper'
        self.started=time.monotonic();self.flow_deadline=min(self.started+900,self.started+max(0,deadline_epoch(HARD)-time.time()))
        self.output_root=Path(self.protocol['output_root']).resolve();self.out=self.output_root
        if not inside(self.output_root,HERE) or not any('agentless' in x.lower() for x in self.output_root.parts):
            raise EngineeringUnknown('INDEPENDENT_PATCHPILOT_OUTPUT_SCOPE_REQUIRED')
        if self.output_root.exists():raise EngineeringUnknown('EXCLUSIVE_NEW_FLOW_OUTPUT_REQUIRED_NO_RERUN')
        self.actor_root=self.output_root/'actor/repo';self.active=self.output_root/'runtime/tree';self.repo_root=self.active/'repo'
        self.logical_python=Path(self.contract['logical_product_python']);self.physical_python=self.contract['physical_product_python_expected']
        self.pack=read(self.contract['pack']);self.semantic=decode(self.pack)
        self._public_cache={};self.runner=None;self.qualify=None

    def record(self,value):
        self.output_root.mkdir(parents=True,exist_ok=True)
        with (self.output_root/'events.jsonl').open('a',encoding='utf-8') as f:
            f.write(canonical({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**value})+'\n')

    def latch_unknown(self,error,stage):
        if isinstance(error,DeclaredBudgetEnd):
            if self.budget_end is None:self.budget_end={'stage':stage,'message':str(error)}
            return
        if self.unknown is None:
            self.unknown={'stage':stage,'type':type(error).__name__,'message':str(error)}
            self.record({'event':'STICKY_UNKNOWN','unknown':self.unknown})

    def assert_no_unknown(self):
        if self.unknown:raise EngineeringUnknown('STICKY_UNKNOWN_NO_POST_NATIVE_PRIVATE '+canonical(self.unknown))

    def time_left(self):return max(0,self.flow_deadline-time.monotonic())

    def require_action(self,kind,allow_no_new=False):
        self.assert_no_unknown()
        verify_grant(self.protocol,read(self.grant_path),read(self.seal_path),self.task_id,
                     now=min(time.time(),deadline_epoch(NO_NEW)-1) if allow_no_new else None)
        if time.time()>=deadline_epoch(HARD):raise EngineeringUnknown('GLOBAL_HARD_STOP')
        if self.time_left()<=0:raise DeclaredBudgetEnd('DECLARED_COMMON900_WALL_END')
        if self.budget_end:raise DeclaredBudgetEnd('DECLARED_FLOW_ALREADY_TERMINAL')
        if sha(self.protocol_path)!=self.grant['protocol_raw_sha256'] or sha(self.contract['pack'])!=self.contract['pack_sha256']:
            raise EngineeringUnknown('PROTOCOL_OR_PUBLIC_PACK_DRIFT')
        for rel,expected in self.contract['c0_business_paths_sha256'].items():
            if sha(Path(self.contract['template'])/rel)!=expected:
                raise EngineeringUnknown('READONLY_C0_BUSINESS_SOURCE_DRIFT '+rel)
        if self.actor_root.exists():self.actor_business_inventory()

    def before_controller(self):
        self.require_action('controller')
        from winjob241 import self_identity,JobRunner
        expected=self.grant.get('controller_physical_python_expected');job=os.environ.get('PATCHPILOT_CONTROLLER_JOB')
        if not expected or not job:raise EngineeringUnknown('PARENT_CONTROLLER_BIRTH_AND_JOB_NOT_SUPPLIED')
        identity=self_identity(job,expected)
        original_birth=identity['creation_time100ns']/10000000-11644473600
        self.flow_deadline=min(self.flow_deadline,time.monotonic()+max(0,original_birth+900-time.time()))
        self.record({'event':'CONTROLLER_SELF_IDENTITY_BEFORE_AUTHOR_IMPORT','identity':identity})
        self.output_root.mkdir(parents=True,exist_ok=True)
        os.chdir(self.output_root)
        if not self.physical_python:raise EngineeringUnknown('NEUTRAL_QUALIFIED_PRODUCT_PHYSICAL_PYTHON_REQUIRED')
        if self.grant.get('product_physical_python_expected')!=self.physical_python:
            raise EngineeringUnknown('PRODUCT_PHYSICAL_PYTHON_GRANT_MISMATCH')
        if self.seal['author_pin']!=SOURCE_PIN:raise EngineeringUnknown('AUTHOR_PIN_NOT_FROZEN')
        self.runner=JobRunner(self)
        copy_bytes(self.contract['template'],self.actor_root,self.contract['c0_business_paths_sha256'])
        (self.actor_root/'generated_tests').mkdir(exist_ok=True)
        copy_bytes(self.contract['template'],self.repo_root,self.contract['template_inventory'])
        if digest(inventory(self.actor_root))!=self.contract['c0_business_inventory_sha256']:
            raise EngineeringUnknown('ACTOR_C0_FULL_BUSINESS_HASH_MISMATCH')
        self.qualify=module('patchpilot_readonly_qualification',Path(self.contract['harness'])/'qualify.py')
        self.qualify.HERE=Path(self.contract['harness']);self.qualify.execute=self.native_execute
        self.record({'event':'EXACT_BYTES_C0_CLONES','actor_business_sha256':digest(inventory(self.actor_root)),
                     'full_runtime_source_sha256':digest(inventory(self.repo_root)),'only_new_independent_outputs':True})

    def reserve_native(self):
        if self.native_roots>=self.protocol['budget']['native_roots_total']:
            raise EngineeringUnknown('DEPLOYMENT_ALL_OS_NATIVE90_RESOURCE_CENSORED')
        kind=getattr(self,'_native_kind','helper')
        product_kinds=('pytest','generated','generated_pytest','coverage')
        products=sum(self.native_root_kinds.get(k,0) for k in product_kinds)
        if kind in product_kinds and products>=self.protocol['budget']['product_native_roots_total']:
            raise DeclaredBudgetEnd('COMMON_ACTUAL_PRODUCT_NATIVE64_BUDGET_BEFORE_SPAWN')
        self.native_roots+=1;self.native_calls+=1
        self.native_root_kinds[kind]=self.native_root_kinds.get(kind,0)+1

    @contextmanager
    def native_lane(self):
        import msvcrt
        lock=ROOT/'工作区/1003-diagnosis-investigation/exp132_review/new_window_2332/finance/shared_flash_budget.lock'
        contract=read(lock.parent.parent/'shared_native_two_chat_lock_contract.json')
        if Path(contract['path']).resolve()!=lock.resolve():raise EngineeringUnknown('SHARED_NATIVE_LOCK_DRIFT')
        offsets=[3,2] if self.contract['package']=='monai' else [2];held=[]
        with lock.open('r+b') as f:
            try:
                for offset in offsets:
                    while True:
                        self.require_action('native_queue')
                        try:f.seek(offset);msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1);held.append(offset);break
                        except OSError:time.sleep(.04)
                yield
            finally:
                for offset in reversed(held):f.seek(offset);msvcrt.locking(f.fileno(),msvcrt.LK_UNLCK,1)

    def native_execute(self,argv,cwd,log,timeout=90,env=None):
        self.require_action('native')
        argv=list(map(str,argv));env=dict(env or {})
        if Path(argv[0]).resolve()!=self.logical_python.resolve():raise EngineeringUnknown('UNDECLARED_PRODUCT_LAUNCHER')
        envelope=Path(log).parent/'entry_envelope.json';identity=Path(log).parent/'actual_python_identity.json'
        # Existing harness guards and exact pytest plugin run only after actual
        # physical Python self certificate; candidate is absent from startup path.
        mode=env.pop('PATCHPILOT_ENTRY_MODE','pytest')
        save(envelope,{'mode':mode,'argv_tail':argv[1:],'expected_physical_python':self.physical_python,
                       'identity_path':str(identity),'harness_guard':str(Path(self.contract['harness'])/'sitecustomize.py'),
                       'harness':self.contract['harness'],'source_root':str(self.repo_root),
                       'frozen_root':self.contract['frozen_public_test_root'],'output':str(Path(log).parent),
                       'package':self.contract['package'],'dependency_paths':self.protocol.get('product_dependency_paths',[]),
                       'dependency_files_sha256':{p:h for p,h in self.seal['sources'].items() if any(inside(p,root) for root in self.protocol.get('product_dependency_paths',[]))}},scope=self.output_root)
        env['PYTHONPATH']='';env['PYTHONNOUSERSITE']='1';env['PYTHONDONTWRITEBYTECODE']='1'
        entry=[str(self.logical_python),'-X','utf8','-B',str(HERE/'product_entry241.py'),str(envelope)]
        previous=getattr(self,'_native_kind','helper');self._native_kind=mode
        try:
            with self.native_lane():value=self.runner.execute(entry,cwd,log,min(90,timeout),env)
        finally:self._native_kind=previous
        if not identity.is_file():raise EngineeringUnknown('ACTUAL_PRODUCT_SELF_CERTIFICATE_MISSING')
        cert=read(identity)
        if not cert.get('before_product_import') or not cert.get('IsProcessInJob_specific_own_Job') or Path(cert['actual_OS_image_GetModuleFileName']).resolve()!=Path(self.physical_python).resolve():
            raise EngineeringUnknown('ACTUAL_PRODUCT_SELF_IDENTITY_NOT_QUALIFIED')
        value['actual_product_python_identity']=cert;return value

    def actor_path(self,value,allow_directory=False):
        if not isinstance(value,str) or any(c in value for c in ('\x00','\r','\n','\\','`','$',';','&','|','<','>')):
            raise IllegalTool('UNSAFE_ACTOR_PATH')
        value=value.removeprefix('/testbed/').removeprefix('/workspace/repo/')
        if value in ('/testbed','/workspace/repo','.'):p=self.actor_root
        else:p=self.actor_root/value
        if p.is_symlink() or not inside(p,self.actor_root):raise IllegalTool('ACTOR_PATH_TRAVERSAL')
        rel=p.resolve().relative_to(self.actor_root).as_posix()
        if allow_directory and p.is_dir() and '.git' not in p.parts:return p.resolve()
        if not business_path(rel,self.contract['package']) and not (rel.startswith('generated_tests/') and rel.endswith('.py')):
            raise IllegalTool('BUSINESS_OR_OWN_GENERATED_PYTHON_ONLY')
        return p.resolve()

    def actor_business_inventory(self):
        inv=inventory(self.actor_root)
        result={}
        for rel,expected in inv.items():
            if rel.startswith('generated_tests/') and rel.endswith('.py'):continue
            if not business_path(rel,self.contract['package']):raise IllegalTool('UNDECLARED_ACTOR_FILE '+rel)
            result[rel]=expected
        if not set(self.contract['c0_business_paths_sha256'])<=set(result):raise IllegalTool('ORIGINAL_BUSINESS_DELETION_NOT_SUPPORTED')
        return result

    def materialize_actor(self):
        self.require_action('materialize');business=self.actor_business_inventory()
        for rel in business:
            target=self.repo_root/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((self.actor_root/rel).read_bytes())
        current=inventory(self.repo_root);initial=self.contract['template_inventory']
        forbidden=[rel for rel in set(current)|set(initial) if current.get(rel)!=initial.get(rel) and not business_path(rel,self.contract['package'])]
        if forbidden:raise EngineeringUnknown('NONBUSINESS_RUNTIME_DRIFT '+canonical(forbidden))
        if {rel:current[rel] for rel in business}!=business:raise EngineeringUnknown('ACTOR_RUNTIME_BYTES_MISMATCH')
        return business

    def verify_public(self,nodes=None):
        self.require_action('public');business=self.materialize_actor()
        nodes=list(dict.fromkeys(nodes or self.contract['public_target_nodes']+self.contract['ordinary_nodes']))
        allowed=set(self.contract['public_target_nodes']+self.contract['ordinary_nodes'])
        if not nodes or not set(nodes)<=allowed:raise IllegalTool('PUBLIC_NODE_CONTRACT_ONLY')
        key=digest([business,nodes])
        if key in self._public_cache:return copy.deepcopy(self._public_cache[key])
        out=self.output_root/'public_native'/f'{len(self.public_runs):03d}'
        if inventory(self.contract['frozen_public_test_root'])!=self.contract['frozen_inventory']:
            raise EngineeringUnknown('FROZEN_TEST_ASSET_DRIFT')
        before=inventory(self.repo_root)
        # The frozen plugin version is checked for its explicit exact selector.
        plugin=Path(self.contract['harness'])/'qualification_plugin.py'
        selector=any(isinstance(n,ast.Constant) and n.value=='EXP129_SELECTED_NODES' for n in ast.walk(ast.parse(plugin.read_text('utf-8-sig'))))
        if selector:
            result=self.qualify.probe(self.active,Path(self.contract['frozen_public_test_root']),nodes,out,self.logical_python,self.contract['package'],min(self.flow_deadline,time.monotonic()+90))
        else:
            out.mkdir(parents=True);frozen=Path(self.contract['frozen_public_test_root'])
            env=self.qualify.isolated_env(self.active,self.repo_root,frozen,out,self.logical_python,self.contract['package'])
            args=[self.logical_python,'-m','pytest','-p','qualification_plugin','-p','no:cacheprovider','-q','--disable-warnings','--import-mode=importlib','--continue-on-collection-errors','-o','addopts=','--rootdir',frozen]
            if self.contract['package'] in ('mypy','conans','dvc'):args.append('--assert=plain')
            args+=nodes;result=self.native_execute(args,frozen,out/'pytest.log',90,env)
            result.update(executed=True,guard_loaded=(out/'guard_ready.json').is_file(),pytest=read(out/'outcomes.json') if (out/'outcomes.json').is_file() else {})
        outcomes=result.get('pytest',{}).get('outcomes',{})
        exact=set(outcomes)==set(nodes) and not result.get('pytest',{}).get('collection_errors')
        stable=before==inventory(self.repo_root) and inventory(self.contract['frozen_public_test_root'])==self.contract['frozen_inventory']
        if not (result.get('executed') and result.get('guard_loaded') and exact and stable and not result.get('timeout')):
            raise EngineeringUnknown('PUBLIC_GUARD_IDENTITY_EXACT_COVERAGE_UNKNOWN')
        passed=result['exit_code']==0 and all(outcomes[n].get('status')=='passed' for n in nodes)
        value={'passed':passed,'outcomes':outcomes,'stdout':self.neutral(result.get('stdout','')),
               'stderr':self.neutral(result.get('stderr','')),'exit_code':result['exit_code'],'business_sha256':digest(business),
               'guarded_exact_nodes':True,'native_record':result}
        self.public_runs.append(value);self._public_cache[key]=copy.deepcopy(value)
        self.record({'event':'ACTUAL_PUBLIC_FEEDBACK','task_id':self.task_id,'requested_nodes':nodes,'passed':passed,'native_log':result.get('log')})
        return value

    def neutral(self,value):
        if isinstance(value,str):
            for root,virtual in ((self.actor_root,'/workspace/repo'),(self.repo_root,'/workspace/repo'),(self.contract['frozen_public_test_root'],'/public-tests'),(self.output_root,'/public-feedback')):
                value=value.replace(str(root),virtual).replace(Path(root).as_posix(),virtual)
            return value
        if isinstance(value,dict):return {k:self.neutral(v) for k,v in value.items()}
        if isinstance(value,list):return [self.neutral(v) for v in value]
        return value

