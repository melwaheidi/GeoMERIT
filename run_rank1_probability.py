"""
run_rank1_probability.py
========================
Probabilistic ranking via input-parameter uncertainty propagation.

The reviewer asks for probability of each method occupying rank 1 rather than
a single deterministic ranking. This propagates uncertainty in the site
parameters (target depth, conductivity, noise, budget, time) through the
deterministic GeoMERIT scoring by Monte Carlo, and reports, for each scenario,
the probability that each method is ranked first, plus the mean composite score
with its 5th-95th percentile band.

Reuses the same perturbation model as the benchmark robustness analysis,
applied to the three retrospective field sites and the worked example.
Deterministic under a fixed seed.

Outputs:
  rank1_probability_fieldsites.csv
  rank1_probability_worked.csv
"""

import csv
import numpy as np
from geophysical_method_selector import GeophysicalMethodSelector

SEED = 20260701
N_MC = 5000
COND_BANDS = {20: (5, 35), 30: (15, 45), 50: (30, 80), 100: (70, 160)}

SCENARIOS = [
    dict(name='Site 1 (Jizan, ERT)', deployed='ERT', target='groundwater',
         target_depth=35, conductivity=100, noise_level=20, budget=5000,
         time_constraint=3, required_resolution=0.7),
    dict(name='Site 2 (Jazan, TDEM)', deployed='TEM', target='groundwater',
         target_depth=20, conductivity=100, noise_level=20, budget=5000,
         time_constraint=2, required_resolution=0.6),
    dict(name='Site 3 (SE-Riyadh, VES)', deployed='ERT', target='groundwater',
         target_depth=45, conductivity=100, noise_level=60, budget=3000,
         time_constraint=4, required_resolution=0.6),
    dict(name='Worked example (groundwater)', deployed=None, target='groundwater',
         target_depth=40, conductivity=100, noise_level=20, budget=5000,
         time_constraint=3, required_resolution=0.7),
]

def perturb(s, rng):
    depth = s['target_depth'] * rng.uniform(0.6, 1.4)
    lo, hi = COND_BANDS.get(int(s['conductivity']), (s['conductivity']*0.6, s['conductivity']*1.4))
    cond = rng.uniform(lo, hi)
    noise = min(95.0, max(0.0, s['noise_level'] + rng.uniform(-15, 15)))
    budget = s['budget'] * rng.uniform(0.7, 1.6)
    time = s['time_constraint'] * rng.uniform(0.7, 1.6)
    return dict(target=s['target'], target_depth=depth, conductivity=cond,
                noise_level=noise, budget=budget, time_constraint=time,
                required_resolution=s['required_resolution'])

def analyse(sel, s, rng):
    methods = list(sel.methods.keys())
    rank1_count = {m: 0 for m in methods}
    score_samples = {m: [] for m in methods}
    for _ in range(N_MC):
        p = perturb(s, rng)
        ranked = sel.rank_methods(p)
        rank1_count[ranked[0][0]] += 1
        for m, sc in ranked:
            score_samples[m].append(sc)
    rows = []
    for m in methods:
        arr = np.array(score_samples[m])
        rows.append(dict(method=m, rank1_prob=round(rank1_count[m] / N_MC, 3),
                         mean_score=round(arr.mean(), 2),
                         p5_score=round(np.percentile(arr, 5), 2),
                         p95_score=round(np.percentile(arr, 95), 2)))
    rows.sort(key=lambda r: r['rank1_prob'], reverse=True)
    return rows

def main():
    sel = GeophysicalMethodSelector()
    rng = np.random.default_rng(SEED)
    field_rows, worked_rows = [], []
    for s in SCENARIOS:
        rows = analyse(sel, s, rng)
        print(f"\n=== {s['name']} ===")
        if s['deployed']:
            print(f"    deployed: {s['deployed']}")
        for r in rows[:5]:
            print(f"    {r['method']:22s} P(rank1)={r['rank1_prob']:.3f}  "
                  f"score {r['mean_score']:.1f} [{r['p5_score']:.1f}, {r['p95_score']:.1f}]")
        for r in rows:
            r2 = dict(scenario=s['name'], **r)
            (worked_rows if s['name'].startswith('Worked') else field_rows).append(r2)
    fn = ['scenario', 'method', 'rank1_prob', 'mean_score', 'p5_score', 'p95_score']
    with open('rank1_probability_fieldsites.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
        for r in field_rows: w.writerow(r)
    with open('rank1_probability_worked.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fn); w.writeheader()
        for r in worked_rows: w.writerow(r)
    print("\nwrote rank1_probability_fieldsites.csv, rank1_probability_worked.csv")

if __name__ == '__main__':
    main()
