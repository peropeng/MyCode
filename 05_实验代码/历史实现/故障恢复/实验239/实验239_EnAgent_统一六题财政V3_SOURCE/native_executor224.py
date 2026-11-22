"""Synchronous native root born suspended, assigned own Job before execution."""
from common166 import *
import ctypes,subprocess
from ctypes import wintypes
from contextlib import contextmanager
class Basic(ctypes.Structure):
 _fields_=[('PerProcessUserTimeLimit',ctypes.c_longlong),('PerJobUserTimeLimit',ctypes.c_longlong),('LimitFlags',wintypes.DWORD),('MinimumWorkingSetSize',ctypes.c_size_t),('MaximumWorkingSetSize',ctypes.c_size_t),('ActiveProcessLimit',wintypes.DWORD),('Affinity',ctypes.c_size_t),('PriorityClass',wintypes.DWORD),('SchedulingClass',wintypes.DWORD)]
class IO(ctypes.Structure):_fields_=[(n,ctypes.c_ulonglong) for n in ('ReadOperationCount','WriteOperationCount','OtherOperationCount','ReadTransferCount','WriteTransferCount','OtherTransferCount')]
class Extended(ctypes.Structure):_fields_=[('BasicLimitInformation',Basic),('IoInfo',IO),('ProcessMemoryLimit',ctypes.c_size_t),('JobMemoryLimit',ctypes.c_size_t),('PeakProcessMemoryUsed',ctypes.c_size_t),('PeakJobMemoryUsed',ctypes.c_size_t)]
_HELD=None

def execute(argv,cwd,log,timeout=90,env=None):
 """Same actual held-handle implementation as Root-qualified E242 source.

 Counters here reserve this executor's roots; caller and parent Job lifetime
 accounting separately cover Bash/git/controller and every other owned root.
 """
 global _HELD
 p=authorization()
 if _HELD is None:
  _HELD=module('exp239_qualified_held_native',E/'native_executor239_held.py')
 _HELD.MAX_ALL_OS_ROOTS=p['budget']['all_owned_OS_roots_total']
 _HELD.MAX_PRODUCT_NATIVE_ROOTS=p['budget']['native_roots_total']
 _HELD.NATIVE_TIMEOUT_SECONDS=p['budget']['native_timeout_seconds']
 return _HELD.execute(argv,cwd,log,timeout=timeout,env=env,product_native=True)

def install(env):
 """Install after constructor, before any actual public/private native callback."""
 original=execute
 def bounded(argv,cwd,log,timeout=90,env_arg=None,**kwargs):
  child=kwargs.pop('env',env_arg)
  if kwargs:raise RuntimeError('UNDECLARED_NATIVE_EXECUTOR_KEYWORD')
  require_open();p=authorization();env._require() if not getattr(env,'_final_validation_running',False) else None
  from flow_bounds239 import check_count
  try:
   count=check_count(getattr(env,'_product_native_roots',0),p['budget']['native_roots_total'],'PRODUCT_NATIVE')
   if isinstance(timeout,bool) or not isinstance(timeout,(int,float)) or timeout<=0:raise RuntimeError('FINITE_NATIVE_TIMEOUT_REQUIRED')
   env._product_native_roots=count
   final=getattr(env,'_final_validation_running',False)
   left=max(0.,(env.deadline if final else env.search_deadline)-time.monotonic())
   if left<=0:raise RuntimeError('METHOD_NATIVE_QUEUE_WALL_BUDGET')
   return original(argv,cwd,log,min(timeout,p['budget']['native_timeout_seconds'],left),child)
  except BaseException as exc:env._generation_fatal=exc;raise
 env.run.qualify.execute=bounded
 return env
