"""Focused public-boundary, event-residual and batch-isolation checks."""
import json
import sys
sys.dont_write_bytecode=True
import torch
from common import *
import models

def main():
    public={'question':'a {quoted} question','question_ID':'x','history':[{'step':0,'role':'r','content':'literal, } \\"'}]}
    original={**public,'ground_truth':'SECRET','mistake_step':'999','mistake_reason':{'nested':[1,'comma, quote \\"']},'error_source':'SECRET'}
    selected=public_object(canonical(original),set(public))
    if selected!=public:raise AssertionError('public whitelisting changed raw history')
    modified={**original,'ground_truth':['different'],'mistake_step':0,'mistake_reason':'changed','error_source':None}
    if public_object(canonical(modified),set(public))!=selected:raise AssertionError('private metadata affects public projection')
    torch.manual_seed(1);event=models.EventResidual().eval();x=torch.randn(6,183);partner=torch.zeros(6,2,dtype=torch.long);valid=torch.zeros(6,2)
    if not torch.equal(event(x,partner,valid),x):raise AssertionError('unpaired nodes receive nonzero event residual')
    partner[0,0]=1;valid[0,0]=1;first=event(x,partner,valid);changed=x.clone();changed[1,:128]+=1
    second=event(changed,partner,valid)
    if torch.equal(first[0],second[0]):raise AssertionError('observed linked content has no learned residual path')
    if not torch.equal(first[2:],x[2:]):raise AssertionError('unpaired residual contaminates other nodes')
    data={}
    for sid,n in [('one',6),('two',8)]:
        indices=torch.zeros(n,2,dtype=torch.long);mask=torch.zeros(n,2)
        for i in range(n):
            neighbors=([i-1] if i else [])+([i+1] if i+1<n else [])
            indices[i,:len(neighbors)]=torch.tensor(neighbors);mask[i,:len(neighbors)]=1
        data[sid]={'content':torch.randn(n,128),'agent':torch.randn(n,32),'raw_structure':torch.randn(n,23),
            'adjacency':[(indices.clone(),mask.clone()) for _ in range(4)],
            'paired_partner':torch.zeros(n,2,dtype=torch.long),'paired_valid':torch.zeros(n,2)}
    scaler=(torch.zeros(23),torch.ones(23))
    for arm in ('N','A','B','AB'):
        model=models.create(arm).eval();combined=models.collate(['one','two'],data,scaler,'cpu');scores,_=models.forward(model,arm,combined)
        separate=[models.forward(model,arm,models.collate([sid],data,scaler,'cpu'))[0][0] for sid in ('one','two')]
        if not all(torch.allclose(a,b,atol=1e-6,rtol=1e-5) for a,b in zip(scores,separate)):raise AssertionError('cross-trajectory batch contamination:'+arm)
        model.train();scores,extra=models.forward(model,arm,combined);value=models.loss(scores,extra,arm,combined,{'one':1,'two':2});value.backward()
        if not all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in model.parameters()):raise AssertionError('nonfinite gradient:'+arm)
    model=models.create('StepFinder');batch=models.collate(['one','two'],data,scaler,'cpu');scores,extra=models.forward(model,'StepFinder',batch)
    value=models.loss(scores,extra,'StepFinder',batch,{'one':1,'two':2});value.backward()
    if [len(s) for s in scores]!=[6,8] or not bool(torch.isfinite(value)):raise AssertionError('official StepFinder mask/length/loss invalid')
    receipt={'at_utc':now(),'checks':['private metadata cannot affect public projection','raw text is preserved',
        'unpaired event residual is exactly zero','paired content has learned path','owned batch graphs cannot cross trajectories',
        'all arm gradients finite','official SF mask/length/loss works'],'paid_API_calls':0,'test_label_accesses':0,
        'source_hashes':{name:sha(E/name) for name in ('common.py','models.py','check_engineering.py')}}
    write_new(E/'engineering_check.json',receipt);print(canonical({'engineering_checks':'passed','paid_API_calls':0}),flush=True)

if __name__=='__main__':main()
