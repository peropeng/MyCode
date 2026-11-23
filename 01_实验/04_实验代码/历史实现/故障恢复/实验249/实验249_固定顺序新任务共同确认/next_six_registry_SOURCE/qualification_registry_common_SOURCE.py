"""Public-only qualification registry definitions; no native or finance client."""
import datetime
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
S=Path(__file__).resolve().parent;Q=S.parent;C=Q/'next_six_current_C0_SOURCE';I=Q/'next_six_qualification_SOURCE';M=Q/'method_sources'
R=Path('D:/Code/毕设/graduate-thesis-experiments');W=R/'工作区/1012-until0900-common'
OUTPUT=W/'confirmation_common_C0_next6_prospective_v1'
TASKS=['python__mypy-10392','python__mypy-11134','getmoto__moto-7081','getmoto__moto-6212','getmoto__moto-5406','getmoto__moto-6387']
COMPLETE='FRESH_CURRENT_C0_ORIGINAL_GFAIL_OPASS_AND_MASKED_V14_CHANNEL_PASS'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
def ref(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def exact(value):
 if sha(value['path'])!=value['sha256']:raise RuntimeError('NEXT_REGISTRY_PUBLIC_REFERENCE_DRIFT:'+value['path'])
 return read(value['path'])
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def parent_stopped(parent):
 stop=parent.get('stop_receipt',{})
 return parent.get('exit_code')==0 and parent.get('error') is None and stop.get('all_owned_descendants_terminated') is True and stop.get('job_active_processes_after_termination')==0
def classify(*,parent_ok,worker_ok,go_known,go_eligible,masked_ok):
 if not parent_ok:return 'UNKNOWN'
 if worker_ok and go_known and go_eligible and masked_ok:return 'QUALIFIED'
 if go_known and not go_eligible:return 'INELIGIBLE_PUBLIC_C0'
 return 'UNKNOWN'
def verify_seal(path):
 seal=read(path)
 for group in ('sources_SHA256','public_inputs_SHA256'):
  for p,h in seal.get(group,{}).items():
   if sha(p)!=h:raise RuntimeError('NEXT_REGISTRY_SOURCE_INPUT_DRIFT:'+p)
 return seal
