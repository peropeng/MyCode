"""Exp132 fixed paired summaries. Receives saved correctness/choices, never labels or models."""
from math import comb, log, sqrt
from statistics import mean, stdev


def _binary(values):
    values=list(values)
    if not values or any(type(x) not in (bool,int) or x not in (0,1) for x in values):
        raise ValueError('Expected nonempty Python bool/0/1 correctness sequence')
    return [int(x) for x in values]


def clopper_pearson(successes,n,alpha):
    if not 0<=successes<=n or n<=0 or not 0<alpha<1:
        raise ValueError('Invalid binomial confidence inputs')
    def tail(p,lower,upper):
        return sum(comb(n,k)*p**k*(1-p)**(n-k) for k in range(lower,upper+1))
    low=0.0
    if successes:
        lo,hi=0.0,1.0
        for _ in range(80):
            mid=(lo+hi)/2
            if tail(mid,successes,n)<alpha/2:lo=mid
            else:hi=mid
        low=(lo+hi)/2
    high=1.0
    if successes<n:
        lo,hi=0.0,1.0
        for _ in range(80):
            mid=(lo+hi)/2
            if tail(mid,0,successes)>alpha/2:lo=mid
            else:hi=mid
        high=(lo+hi)/2
    return [low,high]


def paired_binary(ours,other,alpha=.05):
    """Exact McNemar and conservative paired probability-difference interval.

    q=P(discordance), theta=P(ours only | discordance), delta=q*(2*theta-1).
    Each CP interval has error <=alpha/2. Their rectangle has simultaneous
    coverage >=1-alpha by union bound; project all four corners onto delta.
    With zero observed discordance theta is [0,1], not estimated as 1/2.
    These task-level intervals assume independent task sampling; repetitions
    must not be supplied as independent tasks.
    """
    a,b=_binary(ours),_binary(other)
    if len(a)!=len(b):raise ValueError('Paired denominators differ')
    n=len(a)
    ours_only=sum(x==1 and y==0 for x,y in zip(a,b))
    other_only=sum(x==0 and y==1 for x,y in zip(a,b))
    both_right=sum(x==1 and y==1 for x,y in zip(a,b))
    both_wrong=n-ours_only-other_only-both_right
    m=ours_only+other_only
    p=1.0 if m==0 else min(1.0,2*sum(comb(m,k) for k in range(min(ours_only,other_only)+1))/(2**m))
    q=clopper_pearson(m,n,alpha/2)
    theta=clopper_pearson(ours_only,m,alpha/2) if m else [0.0,1.0]
    corners=[qq*(2*tt-1) for qq in q for tt in theta]
    return dict(n_tasks=n,ours_hits=sum(a),other_hits=sum(b),ours_only=ours_only,
        other_only=other_only,both_right=both_right,both_wrong=both_wrong,
        difference=(ours_only-other_only)/n,exact_mcnemar_two_sided_p=p,
        paired_difference_interval=[min(corners),max(corners)],interval_confidence=1-alpha,
        interval_method='Bonferroni rectangle of exact binomial intervals for discordance rate and conditional direction, projected to paired difference',
        assumptions='Independent task units; no replicate-as-task inflation; inference does not establish broad population representativeness.')


def holm_adjust(pvalues):
    if not pvalues or any(not 0<=float(p)<=1 for p in pvalues.values()):
        raise ValueError('Invalid p-value family')
    ordered=sorted(pvalues,key=lambda k:(pvalues[k],k));m=len(ordered)
    running=0.0;answer={}
    for j,key in enumerate(ordered):
        running=max(running,min(1.0,(m-j)*float(pvalues[key])))
        answer[key]=running
    return answer


def paired_family(comparisons,alpha=.05):
    """Pass exactly frozen 12 primary/baseline or separate 9 component pairs."""
    m=len(comparisons)
    if m not in (12,9):raise ValueError('Unexpected preregistered comparison family size')
    rows={key:paired_binary(*pair,alpha=alpha) for key,pair in comparisons.items()}
    adjusted=holm_adjust({key:row['exact_mcnemar_two_sided_p'] for key,row in rows.items()})
    for key,row in rows.items():
        simultaneous=paired_binary(*comparisons[key],alpha=alpha/m)
        row.update(holm_adjusted_p=adjusted[key],family_tests=m,
            familywise_difference_interval=simultaneous['paired_difference_interval'],
            familywise_interval_coverage_at_least=1-alpha,
            point_estimate_leads=row['difference']>0,
            statistically_supported_lead=(row['difference']>0 and adjusted[key]<alpha
                and simultaneous['paired_difference_interval'][0]>0))
    return rows


def development_summary(correct_by_repeat,choices_by_repeat=None,valid_by_repeat=None):
    rows=[_binary(v) for v in correct_by_repeat]
    if len(rows)!=3 or len({len(v) for v in rows})!=1:
        raise ValueError('Development requires exactly3 repetitions on same tasks')
    n=len(rows[0]);acc=[sum(v)/n for v in rows]
    result=dict(n_independent_tasks=n,repetitions=3,number_of_predictions=3*n,
        hits_by_repetition=[sum(v) for v in rows],accuracy_by_repetition=acc,
        mean_accuracy=mean(acc),sample_sd_across_three_repetition_accuracies=stdev(acc),
        min_accuracy=min(acc),max_accuracy=max(acc),
        mean_correctness_by_task=[mean(v[i] for v in rows) for i in range(n)],
        interpretation='Repeated calls estimate prediction fluctuation on fixed development tasks, not three times as many independent tasks.')
    if choices_by_repeat is not None:
        if valid_by_repeat is None:raise ValueError('Explicit validity is required for choice agreement')
        if len(choices_by_repeat)!=3 or any(len(v)!=n for v in choices_by_repeat):
            raise ValueError('Choice repetition shape differs')
        valid=[_binary(v) for v in valid_by_repeat]
        if len(valid)!=3 or any(len(v)!=n for v in valid):raise ValueError('Validity shape differs')
        good=sum(all(v[i] for v in valid) and len({v[i] for v in choices_by_repeat})==1 for i in range(n))
        result.update(all_three_valid_and_same_step_tasks=good,
            all_three_valid_and_same_step_fraction=good/n,
            invalid_predictions=sum(1-x for row in valid for x in row))
    return result


def development_paired_difference(ours_by_repeat,other_by_repeat,alpha=.05):
    a=development_summary(ours_by_repeat);b=development_summary(other_by_repeat)
    if a['n_independent_tasks']!=b['n_independent_tasks']:raise ValueError('Paired tasks differ')
    diffs=[x-y for x,y in zip(a['mean_correctness_by_task'],b['mean_correctness_by_task'])]
    n=len(diffs);d=mean(diffs);radius=sqrt(2*log(2/alpha)/n)
    return dict(n_tasks=n,repetitions=3,difference=d,paired_task_differences=diffs,
        conservative_hoeffding_interval=[max(-1.0,d-radius),min(1.0,d+radius)],
        confidence=1-alpha,confirmatory=False,
        method='Bounded paired task mean in[-1,1]; task-cluster repetitions remain together. This small development set is descriptive.')


def synthetic_qualification():
    extreme=paired_binary([1]*4,[0]*4)
    identical=paired_binary([1,0,1,0],[1,0,1,0])
    assert extreme['exact_mcnemar_two_sided_p']==.125
    assert extreme['paired_difference_interval'][0]<0<extreme['paired_difference_interval'][1]
    assert identical['exact_mcnemar_two_sided_p']==1.0
    assert identical['paired_difference_interval'][0]<0<identical['paired_difference_interval'][1]
    assert set(holm_adjust({str(i):.125 for i in range(12)}).values())=={1.0}
    repeated=development_summary([[1,0],[0,1],[1,0]],[[0,2],[1,2],[0,2]],[[1,1],[1,1],[1,1]])
    assert repeated['n_independent_tasks']==2 and repeated['mean_accuracy']==.5
    assert repeated['all_three_valid_and_same_step_fraction']==.5
    assert development_paired_difference([[1,0]]*3,[[0,1]]*3)['conservative_hoeffding_interval']==[-1.0,1.0]
    return dict(status='PASS_ONE_NEW_SYNTHETIC_STATISTICS_CHECK',source_labels_or_predictions_read=False,
        real_model_API_or_evaluation_execution=False,
        analytic_four_discordance_p=.125,paired_CI_not_spurious_degenerate=True,
        development_independent_N_remains2=True)


if __name__=='__main__':
    import json
    print(json.dumps(synthetic_qualification(),ensure_ascii=False))
