"""Exact paired binary power for stated design assumptions; no task execution."""
import json,math
from pathlib import Path
E=Path(__file__).resolve().parent
def pmf(n,k,p):
 if p==0:return float(k==0)
 if p==1:return float(k==n)
 return math.comb(n,k)*p**k*(1-p)**(n-k)
def power(n,discordance,delta,alpha=.025):
 theta=(discordance+delta)/(2*discordance)
 total=0
 for k in range(n+1):
  fair=[math.comb(k,w)*.5**k for w in range(k+1)]
  cumulative=[];s=0
  for mass in fair:s+=mass;cumulative.append(s)
  for w in range(k+1):
   p=min(1.,2*cumulative[min(w,k-w)])
   if p<=alpha:total+=pmf(n,k,discordance)*pmf(k,w,theta)
 return total
def main():
 rows=[{'n_distinct_tasks':n,'assumed_discordance_probability':q,'assumed_success_rate_difference':d,'alpha_per_first_Holm_comparison':.025,'exact_rejection_probability':power(n,q,d)} for q,d in ((.2,.1),(.4,.1),(.4,.2)) for n in (21,23,50,100,200)]
 report={'schema':'Exp224-prospective-paired-power/1','assumptions_not_measured_results':True,
         'model':'Independent distinct-task paired outcomes W=(q+delta)/2, L=(q-delta)/2, ties=1-q',
         'test':'Two-sided conditional exact McNemar; reject at .025, conservative first-Holm threshold for two comparisons',
         'rows':rows,'no_new_model_native_private_gold':True,
         'limits':'Single-comparison power under assumed rates, not the probability of beating both baselines; shared-method correlation is unspecified.'}
 (E/'audit224/prospective_paired_power224.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
