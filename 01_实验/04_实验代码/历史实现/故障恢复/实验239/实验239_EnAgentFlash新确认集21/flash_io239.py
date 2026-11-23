"""Root registered continuous finance only; all raw requests/responses retained."""
from common166 import *
_transport=None
def generate(env,body,role,phase):
 global _transport
 if _transport is None:
  transport=module('exp239_resume_finance',ROOT/'工作区/1009-research-resume/finance/resume_transport.py')
  _transport=transport.make_transport(read(E/'finance_config239.json'))
 return _transport.generate(env,body,role,phase)
