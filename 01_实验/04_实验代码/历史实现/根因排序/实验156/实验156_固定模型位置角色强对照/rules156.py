"""Frozen roles/positions only; exact rational counts and deterministic full ranks."""
from collections import Counter
from fractions import Fraction
from common import *

def bin_for(i,n):
 if n<1 or not 0<=i<n:raise ValueError('Original candidate ordinal required')
 return 0 if n==1 else min(9,(10*i)//(n-1))

def encode_fraction(value):return {'numerator':value.numerator,'denominator':value.denominator}
def decode_fraction(value):return Fraction(value['numerator'],value['denominator'])

def fit_table(control,fit_ids,held_ids,by,labels,spec):
 if control not in PRIORS:raise ValueError('Only the two frozen analytical priors fit')
 if len(fit_ids)!=len(set(fit_ids)) or set(fit_ids)&set(held_ids):raise ValueError('Fit/held identity gate failed')
 groups=Counter(by[s]['task_group'] for s in fit_ids)
 histogram={};consumed=[];total=Fraction()
 # Iteration is over the allowlist, never over all labels from the shared file.
 for sid in fit_ids:
  if sid not in labels:raise ValueError('Required fit label absent')
  target=labels[sid];n=len(by[sid]['turns'])
  if type(target) is not int or not 0<=target<n:raise ValueError('Fit original target ordinal invalid')
  weight=Fraction(1,groups[by[sid]['task_group']]);key=target if control==PRIORS[0] else bin_for(target,n)
  histogram[key]=histogram.get(key,Fraction())+weight;total+=weight;consumed.append(sid)
 if total!=len(groups):raise ValueError('Each complete fit group must have unit total weight')
 return {'schema':'Exp156-fixed-position-counts/1.0','control':control,**spec,
  'fit_ids':fit_ids,'held_ids':held_ids,'fit_ids_sha256':digest(fit_ids),'held_ids_sha256':digest(held_ids),
  'consumed_label_ids':consumed,'consumed_label_ids_sha256':digest(consumed),'fit_record_count':len(fit_ids),'fit_group_count':len(groups),
  'group_record_counts':dict(groups),'histogram_exact':{str(k):encode_fraction(v) for k,v in sorted(histogram.items())},
  'total_fit_weight_exact':encode_fraction(total),'smoothing':1,'relative_bins':10 if control==PRIORS[1] else None,
  'fit_ID_gate':True,'held_label_values_used_for_fit':0,'validation_or_target_based_parameter_selection':0,
  'new_optimization_training':0,'new_neural_models':0,'at_utc':now()}

def predict_rule(control,record,table=None):
 if control not in CONTROLS:raise ValueError('Frozen156 rule required')
 n=len(record['turns'])
 if n<1:raise ValueError('Empty trajectory')
 engineers=[i for i,t in enumerate(record['turns']) if isinstance(t.get('role'),str) and t['role'].strip().casefold()=='engineer']
 if control=='FIRST':order=list(range(n));prob=[float(i==0) for i in range(n)]
 elif control=='LAST':order=list(range(n-1,-1,-1));prob=[float(i==n-1) for i in range(n)]
 elif control=='FIRST_ENGINEER':
  chosen=set(engineers);order=engineers+[i for i in range(n) if i not in chosen];prob=[float(i==order[0]) for i in range(n)]
 else:
  if table is None or table['control']!=control:raise ValueError('Matching frozen count table required')
  hist={int(k):decode_fraction(v) for k,v in table['histogram_exact'].items()}
  if control==PRIORS[0]:weights=[hist.get(i,Fraction())+1 for i in range(n)]
  else:
   bins=[bin_for(i,n) for i in range(n)];members=Counter(bins)
   weights=[(hist.get(b,Fraction())+1)/members[b] for b in bins]
  total=sum(weights,Fraction());exact=[v/total for v in weights];prob=[float(v) for v in exact]
  order=sorted(range(n),key=lambda i:(-exact[i],i))
 out={'probabilities':prob,'order':order,'chosen_step':order[0],'predicted_role':record['turns'][order[0]]['role'],
  'valid':True,'native_complete_ranking':True,'original_zero_based_ordinals':True,'candidate_count':n}
 if control=='FIRST_ENGINEER':out.update(engineer_coverage=bool(engineers),engineer_candidates=engineers,fallback_to_FIRST=not engineers)
 if control in PRIORS:out.update(fit_ids_sha256=table['fit_ids_sha256'],count_table_sha256=digest(table),probability_exact=[encode_fraction(v) for v in exact])
 return out
