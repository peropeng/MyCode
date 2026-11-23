"""Four small artificial rule checks, with no neural/data/target access."""
from fractions import Fraction
from common import *
from rules156 import *

def run():
 require_time(new_test=True);counts={'artificial_rule_prediction_calls':0,'artificial_fit_table_calls':0,'neural_model_forwards':0,'optimizer_updates':0,'real_records':0,'real_Gold':0}
 def record(sid,roles,group=None):return {'sample_id':sid,'task_group':group or sid,'turns':[{'role':r} for r in roles]}
 def prior(control,hist=None):return {'control':control,'histogram_exact':hist or {},'fit_ids_sha256':'synthetic'}
 def pred(control,r,table=None):counts['artificial_rule_prediction_calls']+=1;return predict_rule(control,r,table)
 n1=record('single',['other'])
 for control in CONTROLS:
  p=pred(control,n1,prior(control) if control in PRIORS else None)
  assert p['order']==[0] and p['chosen_step']==0 and p['probabilities']==[1.0]
 endpoints=[bin_for(i,12) for i in range(12)]
 assert endpoints[0]==0 and endpoints[-1]==9 and bin_for(0,1)==0
 p=pred(PRIORS[1],record('twelve',['other']*12),prior(PRIORS[1]))
 assert p['order']==list(range(2,10))+[0,1,10,11]
 assert p['probabilities'][0]==p['probabilities'][-1]==.05 and p['probabilities'][2]==.1
 r=record('roles',['other','  ENGINEER\t','engineerish','Engineer'])
 assert pred('FIRST',r)['order']==[0,1,2,3]
 assert pred('LAST',r)['order']==[3,2,1,0]
 p=pred('FIRST_ENGINEER',r);assert p['order']==[1,3,0,2] and p['engineer_coverage'] and not p['fallback_to_FIRST']
 p=pred('FIRST_ENGINEER',record('anonymous',['role_0','role_1']));assert p['order']==[0,1] and p['fallback_to_FIRST']
 by={r['sample_id']:r for r in [record('a',['o']*3,'group1'),record('b',['o']*3,'group1'),record('c',['o']*3,'group2'),record('held',['o']*3,'heldgroup')]}
 labels={'a':0,'b':0,'c':2,'held':999}
 counts['artificial_fit_table_calls']+=1;t=fit_table(PRIORS[0],['a','b','c'],['held'],by,labels,{'suite':'artificial'})
 assert t['histogram_exact']=={'0':{'numerator':1,'denominator':1},'2':{'numerator':1,'denominator':1}} and t['fit_group_count']==2
 assert t['consumed_label_ids']==['a','b','c'] and t['held_label_values_used_for_fit']==0
 p=pred(PRIORS[0],record('tie',['o']*3),t);assert p['order']==[0,2,1]
 counts['artificial_fit_table_calls']+=1
 try:fit_table(PRIORS[0],['a'],['a'],by,labels,{})
 except ValueError:pass
 else:raise AssertionError('Held-ID gate must reject overlap before a fit')
 receipt={'at_utc':now(),'experiment':'Exp156','status':'PASS','tests_run':4,'tests':['n1_all5rules','relative_endpoints_bin_uniform_mass','explicit_full_rank_role_exact_match_and_fallback','group_weight_and_held_ID_label_gate'],
  'approved_plan_sha256':PLAN_SHA,'source_sha256':{n:sha(E/n) for n in ('common.py','rules156.py','test_rules156.py')},'compute_counters':counts,'physical_cumulative_compute_counters':counts,'new_real_ranker_outputs':0}
 write_new(E/'fixtures/rule_test_receipt.json',receipt)
 print(canonical({'Exp156':'necessary_rule_checks_PASS','tests':4,'physical_artificial_calls':counts}),flush=True)
if __name__=='__main__':run()
