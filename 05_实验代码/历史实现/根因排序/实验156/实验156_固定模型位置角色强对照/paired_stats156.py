"""Exp156 fixed joint Holm30; reused exact/rational paired methods.

The binary interval follows Exp143's overflow-safe exact binomial procedure.
AF duplicates follow Exp138's within-group mean/sign-flip and paired bootstrap.
No labels, predictions, models or files are loaded by this module.
"""
import math
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import numpy as np

ALPHA = .05
BOOTSTRAP_SEED = 20261006
BOOTSTRAP_DRAWS = 5000


@lru_cache(maxsize=64)
def log_coefficients(n):
    return tuple(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
                 for k in range(n + 1))


def clopper_pearson(successes, n, alpha):
    if not 0 <= successes <= n or n <= 0 or not 0 < alpha < 1:
        raise ValueError('Invalid exact-binomial interval inputs')
    coefficients = log_coefficients(n)

    def tail(p, first, last):
        if p == 0:
            return float(first <= 0 <= last)
        if p == 1:
            return float(first <= n <= last)
        logp, logq = math.log(p), math.log1p(-p)
        terms = [coefficients[k] + k * logp + (n - k) * logq
                 for k in range(first, last + 1)]
        maximum = max(terms)
        return min(1., math.exp(maximum) * math.fsum(math.exp(t - maximum) for t in terms))

    low, high = 0., 1.
    if successes:
        a, b = 0., 1.
        for _ in range(80):
            mid = (a + b) / 2
            if tail(mid, successes, n) < alpha / 2:
                a = mid
            else:
                b = mid
        low = (a + b) / 2
    if successes < n:
        a, b = 0., 1.
        for _ in range(80):
            mid = (a + b) / 2
            if tail(mid, 0, successes) > alpha / 2:
                a = mid
            else:
                b = mid
        high = (a + b) / 2
    return [low, high]


def binary_pair(ours, other, alpha=ALPHA):
    a, b = list(ours), list(other)
    if not a or len(a) != len(b) or any(type(x) not in (int, bool) or x not in (0, 1) for x in a + b):
        raise ValueError('Nonempty paired binary original-task vectors required')
    n = len(a)
    ours_only = sum(x == 1 and y == 0 for x, y in zip(a, b))
    other_only = sum(x == 0 and y == 1 for x, y in zip(a, b))
    both_right = sum(x == 1 and y == 1 for x, y in zip(a, b))
    discordant = ours_only + other_only
    p = 1. if not discordant else min(1., 2 * sum(math.comb(discordant, k)
            for k in range(min(ours_only, other_only) + 1)) / (2 ** discordant))
    q = clopper_pearson(discordant, n, alpha / 2)
    theta = clopper_pearson(ours_only, discordant, alpha / 2) if discordant else [0., 1.]
    corners = [qq * (2 * tt - 1) for qq in q for tt in theta]
    return {'unit': 'original independent task', 'n_tasks': n, 'ours_hits': sum(a),
            'other_hits': sum(b), 'ours_only': ours_only, 'other_only': other_only,
            'both_right': both_right, 'both_wrong': n - discordant - both_right,
            'difference': (ours_only - other_only) / n, 'p_value': p,
            'exact_mcnemar_two_sided_p': p, 'paired_difference_interval': [min(corners), max(corners)],
            'interval_confidence': 1 - alpha,
            'interval_method': 'Exact-binomial Bonferroni rectangle for discordance/direction projected onto paired difference',
            'assumptions': 'Independent task units; fixed exposed development comparison, not new blind population confirmation'}


def exact_weighted_signflip(differences):
    nonzero = [d for d in differences if d]
    if not nonzero:
        return 1.
    denominator = math.lcm(*(d.denominator for d in nonzero))
    weights = Counter(int(abs(d) * denominator) for d in nonzero)
    observed = abs(int(sum(nonzero) * denominator))
    distribution = {0: 1}
    for weight, repeats in sorted(weights.items()):
        terms = [(weight * (2 * k - repeats), math.comb(repeats, k)) for k in range(repeats + 1)]
        next_distribution = defaultdict(int)
        for value, count in distribution.items():
            for shift, multiplicity in terms:
                next_distribution[value + shift] += count * multiplicity
        distribution = dict(next_distribution)
    return sum(count for value, count in distribution.items() if abs(value) >= observed) / (2 ** len(nonzero))


def bootstrap_indices(n):
    return np.random.default_rng(BOOTSTRAP_SEED).integers(0, n, size=(BOOTSTRAP_DRAWS, n), dtype=np.int32)


def group_pair(ours, other, ids, by, family_size, draws):
    grouped = defaultdict(list)
    for sid in ids:
        grouped[by[sid]['task_group']].append(sid)
    groups = sorted(grouped)
    if draws.shape != (BOOTSTRAP_DRAWS, len(groups)):
        raise ValueError('Shared fixed group bootstrap draws required')
    fractions = [Fraction(sum(ours[s]['Top1'] - other[s]['Top1'] for s in grouped[g]), len(grouped[g]))
                 for g in groups]
    diff = np.asarray([float(x) for x in fractions], dtype=np.float64)
    boot = diff[draws].mean(axis=1)
    p = exact_weighted_signflip(fractions)
    row = {'unit': 'independent task group; records first averaged within group',
           'n_independent_task_groups': len(groups), 'n_records': len(ids),
           'duplicate_records_above_group_count': len(ids) - len(groups),
           'difference': float(diff.mean()), 'group_equal_Top1_difference': float(diff.mean()),
           'p_value': p, 'exact_weighted_group_signflip_two_sided_p': p,
           'positive_groups': sum(d > 0 for d in fractions), 'negative_groups': sum(d < 0 for d in fractions),
           'zero_difference_groups': sum(d == 0 for d in fractions),
           'nonzero_group_differences': sum(d != 0 for d in fractions),
           'record_ours_only': sum(ours[s]['Top1'] == 1 and other[s]['Top1'] == 0 for s in ids),
           'record_other_only': sum(ours[s]['Top1'] == 0 and other[s]['Top1'] == 1 for s in ids),
           'paired_difference_interval': np.quantile(boot, [ALPHA / 2, 1 - ALPHA / 2]).tolist(),
           'familywise_difference_interval': np.quantile(boot, [ALPHA / (2 * family_size), 1 - ALPHA / (2 * family_size)]).tolist(),
           'interval_confidence': 1 - ALPHA, 'family_interval_per_pair_nominal_confidence': 1 - ALPHA / family_size,
           'interval_method': 'Exp138 paired5000 group bootstrap percentile; Bonferroni levels across the frozen joint family',
           'familywise_interval_coverage': 'Nominal bootstrap coverage; no finite-sample exact-coverage claim',
           'bootstrap_seed': BOOTSTRAP_SEED, 'bootstrap_draws': BOOTSTRAP_DRAWS,
           'group_order_sha256': hashlib.sha256(json.dumps(groups,separators=(',',':')).encode()).hexdigest(),
           'paired_group_differences': [{'group': g, 'numerator': d.numerator, 'denominator': d.denominator}
                                       for g, d in zip(groups, fractions)],
           'assumptions': 'Exploratory OOF comparison; exchangeable paired signs/independent groups; shared overlapping fits and reused data limit confirmation'}
    for metric in ('MRR', 'Top3'):
        differences = np.asarray([sum(float(ours[s][metric]) - float(other[s][metric])
                                          for s in grouped[g]) / len(grouped[g]) for g in groups])
        row[metric] = {'difference': float(differences.mean()),
                       'paired_group_bootstrap95_interval': np.quantile(differences[draws].mean(1), [.025, .975]).tolist(),
                       'descriptive_only': True}
    return row


def family(comparisons, family_size):
    """Exactly30 prespecified cached-view/simple-control comparisons with fixed family CI."""
    if family_size != 30 or len(comparisons) != 30:
        raise ValueError('Frozen joint Holm30 family required')
    ordered = sorted(comparisons, key=lambda k: (comparisons[k]['p_value'], k))
    maximum = 0.
    for index, key in enumerate(ordered):
        row = comparisons[key]
        maximum = max(maximum, min(1., (family_size - index) * row['p_value']))
        row.update(holm_adjusted_p=maximum, family_tests=family_size,
                   holm_reject_at05=maximum < ALPHA, point_estimate_leads=row['difference'] > 0,
                   statistically_supported_lead=row['difference'] > 0 and maximum < ALPHA
                   and row['familywise_difference_interval'][0] > 0,
                   scope='Prespecified fixed comparisons on exposed historical development; no control promoted to primary')
    return comparisons


def binary_family_row(ours, other, family_size):
    row = binary_pair(ours, other)
    adjusted = binary_pair(ours, other, alpha=ALPHA / family_size)
    row.update(familywise_difference_interval=adjusted['paired_difference_interval'],
               family_interval_per_pair_nominal_confidence=1 - ALPHA / family_size,
               familywise_interval_coverage='Conservative coverage at least95% across family by Bonferroni; Holm p adjustment separate')
    return row
