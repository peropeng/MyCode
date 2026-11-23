"""Copy the already verified owned author/evaluator boundary into this scope."""
from pathlib import Path
from contracts241 import *

def main():
 pp=ROOT/'工作区/1009-exp227-patchpilot-full/实验/实验238_晚间Flash完整PatchPilot两题小试'
 for old,new in [('supervisor_pp.py','supervisor241.py'),('external_once_private_pp.py','external_once_private241.py')]:
  s=(pp/old).read_text('utf-8-sig')
  s=s.replace('contracts_pp','contracts241').replace('winjob_pp','winjob241')
  s=s.replace('cli_pp.py','cli241.py').replace('external_once_private_pp.py','external_once_private241.py')
  s=s.replace('from port_owner_pp import PatchPilotOwner','from environment241 import Environment241 as PatchPilotOwner')
  s=s.replace("str(HERE/'cli241.py'),'run'","str(HERE/'cli241.py')")
  s=s.replace('own.output_root=flow;own.out=flow;own.actor_root=selected;',
   'own._external_evaluator=True;own.output_root=flow;own.out=flow;own.actor_root=selected;')
  (HERE/new).write_bytes(s.encode('utf-8'))
 print(canonical({'owned_supervisor_and_separate_evaluator_prepared':True,'generation_native_private_ledger_write':0}))
if __name__=='__main__':main()
