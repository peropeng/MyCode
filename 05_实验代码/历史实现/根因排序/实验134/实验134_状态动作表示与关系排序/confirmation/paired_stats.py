"""Same exact paired procedure, with the explicitly frozen13/9 families."""
from shared import *
reference=module(T/'paired_statistics_reference.py','exp134_confirmation_qualified_exact_statistics')
def family(comparisons,expected,alpha=.05):
    if len(comparisons)!=expected or expected not in (13,9):raise ValueError('frozen_confirmation_family_size_changed')
    rows={key:reference.paired_binary(*values,alpha=alpha) for key,values in comparisons.items()}
    adjusted=reference.holm_adjust({key:r['exact_mcnemar_two_sided_p'] for key,r in rows.items()})
    for key,row in rows.items():
        simultaneous=reference.paired_binary(*comparisons[key],alpha=alpha/expected)
        row.update(holm_adjusted_p=adjusted[key],family_tests=expected,
            familywise_difference_interval=simultaneous['paired_difference_interval'],familywise_interval_coverage_at_least=1-alpha,
            point_estimate_leads=row['difference']>0,
            statistically_supported_lead=row['difference']>0 and adjusted[key]<alpha and simultaneous['paired_difference_interval'][0]>0)
    return rows
