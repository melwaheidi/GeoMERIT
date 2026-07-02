"""
failure_analysis.py
===================
Classifies the benchmark cases in which GeoMERIT's top recommendation differs
from the deployed method (and that difference is stable under parameter
perturbation) into interpretable categories, rather than reporting the
disagreement count alone. Categories are assigned from the case record and the
computed rankings:

  operational : deployed method was physically appropriate (placed high by the
                tool, typically rank 2) but chosen over the top-ranked method
                for operational or logistical reasons the criteria do not
                encode (non-contact deployment, coverage speed).
  matrix      : the tool ranks a high-resolution electrical/radar method above
                the deployed method because the contrast-matrix and resolution
                structure favour ERT/GPR; the deployed method still reaches the
                top three (shortlist retained) but not first place.
  scope       : the deployed method is one whose diagnostic basis is weakly
                represented in the current criteria (e.g. gamma-ray radioelement
                contrast for radiometric; velocity contrast for seismic), so it
                is under-ranked and may fall outside the top three.

The classification is derived deterministically from the rank of the deployed
method and its Monte Carlo top-3 retention; no new data is used.
Output: failure_analysis.csv
"""
import csv

rob = {r['case_id']: r for r in csv.DictReader(open('benchmark_robustness.csv'))}
res = {r['case_id']: r for r in csv.DictReader(open('benchmark_results.csv'))}
cases = {r['case_id']: r for r in csv.DictReader(open('benchmark_cases.csv'))}

def classify(cid):
    r = res[cid]; c = cases[cid]
    rank = int(r['rank_of_deployed_aware'])
    mc_top3 = float(rob[cid]['mc_top3_rate'])
    dep = c['deployed_method']
    # scope: deployed method weakly represented and falls out of top-3
    if mc_top3 < 0.20:
        return 'scope'
    # operational: physically appropriate, ranked 2nd, strong top-3 retention
    if rank == 2 and mc_top3 >= 0.90:
        return 'operational'
    # otherwise matrix/resolution dominance but shortlist retained
    return 'matrix'

rows = []
for cid in sorted(rob):
    if rob[cid]['stability'] == 'stable-mismatch':
        cat = classify(cid)
        c = cases[cid]; r = res[cid]
        rows.append(dict(case_id=cid, target_class=c['target_class'],
                         deployed=c['deployed_method'], top1=r['top1_aware'],
                         rank_of_deployed=r['rank_of_deployed_aware'],
                         mc_top3_retention=rob[cid]['mc_top3_rate'],
                         category=cat))

with open('failure_analysis.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    for r in rows: w.writerow(r)

from collections import Counter
cnt = Counter(r['category'] for r in rows)
print(f"Stable mismatches classified (n={len(rows)}):\n")
for cat in ['operational', 'matrix', 'scope']:
    sub = [r for r in rows if r['category'] == cat]
    ids = ', '.join(r['case_id'] for r in sub)
    print(f"  {cat:12s} {len(sub):2d}  [{ids}]")
print("\nPer-case:")
for r in rows:
    print(f"  {r['case_id']:6s} {r['target_class']:12s} deployed={r['deployed']:20s} "
          f"top1={r['top1']:14s} rank={r['rank_of_deployed']} "
          f"mc_top3={r['mc_top3_retention']}  -> {r['category']}")
