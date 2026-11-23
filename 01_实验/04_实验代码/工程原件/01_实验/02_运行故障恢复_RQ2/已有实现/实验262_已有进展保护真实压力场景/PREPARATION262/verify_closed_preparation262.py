"""Pure closed-grant and held-owner ordering verification; no process/T0."""
import ast,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P));import stage_entry262 as stage
template=P/'ROOT_PREPARATION_GRANT262_TEMPLATE_FALSE.json';g=stage.read(template)
before=[str(p) for p in P.parent.glob('runs/*/*/*/SCIENCE_T0_TRIAL_PREPARATION_STARTED.json')];assert not before
try:stage.authority(template,'trial1','SET');raise AssertionError('DEFAULT_FALSE_PREPARATION_ACCEPTED')
except RuntimeError as e:assert str(e)=='EXP262_PREPARATION_DEFAULT_CLOSED'
assert [str(p) for p in P.parent.glob('runs/*/*/*/SCIENCE_T0_TRIAL_PREPARATION_STARTED.json')]==before
seal=stage.checked(g['preparation_source_seal'])
for p,h in {**seal['sources'],**seal['dependencies'],**seal['public_inputs_SHA256']}.items():assert stage.sha(p)==h
text=(P/'launch262.py').read_text('utf-8-sig');ast.parse(text)
assert text.index('creationflags=0x08000000|4')<text.index('AssignProcessToJobObject')<text.index("save(out/'SUSPENDED_OWNER_READY.json'")<text.index('NtResumeProcess(held)')
assert "specific_owned_Job" in text and "args.suspend_timeout!=600" in text and 'stop_owned(k,job,process,assigned)' in text
print(json.dumps({'PASS':True,'default_false_refuses_before_T0_or_owner':True,'held_CREATE_SUSPENDED_assign_Job_ready_resume_order_preserved':True,'actual_owner_launch_T0_POST_native':0,'prep_seal':stage.ref(P/'SOURCE_SEAL262_PREPARATION_FALSE.json')}))
