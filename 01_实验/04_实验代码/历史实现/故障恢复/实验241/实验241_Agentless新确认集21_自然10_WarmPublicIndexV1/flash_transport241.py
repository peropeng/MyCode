"""Actual scoped constructor shared by zero-POST mechanical and live generation."""
import json,threading
from contracts241 import *
root=module('_root_resume_transport241',ROOT/'工作区/1009-research-resume/finance/resume_transport.py')
FinanceError=root.FinanceError
FinanceGateRejected=GateRejected=root.GateRejected
FinanceUnknown=Unknown=root.Unknown
LegacyIO=root.LegacyIO;Transport=root.Transport;old=root.old
bounds,usage,dec=root.bounds,root.usage,root.dec
_instance=None;_owner=None;_lock=threading.Lock()

def construct(owner):
 global _instance,_owner
 with _lock:
  if _instance is None:
   from scoped_finance_artifacts241 import install
   install(__import__(__name__),owner)
   _instance=root.make_transport(read(HERE/'finance_config241.json'),LegacyIO())
   _owner=owner
  if _owner is not owner:raise EngineeringUnknown('SCOPED_TRANSPORT_OWNER_NOT_REUSABLE_ACROSS_TASKS')
 return _instance

def generate(owner,body,role,phase=FINANCE_PHASE):
 if phase!=FINANCE_PHASE:raise FinanceUnknown('PHASE_MISMATCH')
 return construct(owner).generate(owner,body,role,FINANCE_PHASE)
