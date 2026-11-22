"""Refresh only a new false-grant task; preserve every closed case seal."""
import argparse,ast
from contracts241 import *
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--task',required=True);args=parser.parse_args()
 base=HERE/'candidate'/args.task;p=read(base/'protocol.json');g=read(base/'root_grant.template.json')
 if p['execution_authorized'] or g['root_authorized'] or (HERE/'supervision'/args.task).exists():
  raise EngineeringUnknown('PRESEAL_ONLY_NEVER_STARTED_FALSE_TASK')
 s=read(base/'source_seal.json')
 for f in HERE.glob('*.py'):ast.parse(f.read_text('utf-8-sig'));s['sources'][str(f)]=sha(f)
 for name in ('resume_transport.py','continuous_core_v2.py'):
  f=ROOT/'工作区/1009-research-resume/finance'/name;s['sources'][str(f)]=sha(f)
 for path,h in {**s['sources'],**s['inputs']}.items():
  if sha(path)!=h:raise EngineeringUnknown('PRESEAL_SHARED_INPUT_SOURCE_DRIFT '+path)
 save(base/'source_seal.json',s);g.update(source_seal_sha256=digest(s),protocol_sha256=digest(p),protocol_raw_sha256=sha(base/'protocol.json'))
 save(base/'root_grant.template.json',g)
 print(canonical({'task_id':args.task,'only_this_case_presealed':True,'science_grant_false':True,'sources':len(s['sources'])}))
if __name__=='__main__':main()
