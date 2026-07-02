"""
run_weight_sensitivity.py
=========================
Global sensitivity analysis of the four fixed criterion weights.

The manuscript uses fixed weights (physical contrast 0.40, data quality 0.30,
cost 0.20, effort 0.10). A referee will ask whether the recommendations depend
on that specific choice. This script answers that using only the existing
pipeline and data (the 22 benchmark cases plus the 3 retrospective field
sites), with no new data.

Three complementary analyses:

  (A) One-at-a-time (OAT) perturbation, for a tornado-style summary. Each
      weight is scaled by +/-10%, +/-20%, +/-30% in turn, the remaining three
      weights are renormalised to preserve their relative proportions and keep
      the sum at 1.0, and the top-1 / top-3 benchmark agreement is recomputed.

  (B) Global random-weight sampling. Weight vectors are drawn uniformly from
      the 4-simplex (Dirichlet(1,1,1,1)) so that every valid weighting summing
      to 1.0 is equally likely, and for each draw the benchmark agreement and
      the per-case rank-1 method are recorded. This gives the distribution of
      agreement over ALL admissible weightings, and the probability that each
      case keeps its baseline rank-1 method.

  (C) Constrained global sampling that preserves the intended ORDER of the
      criteria (physical >= quality >= cost >= effort). This tests robustness
      within the family of weightings that respect the same qualitative
      priorities as the fixed scheme, which is the practically relevant space.

Outputs:
  weight_sensitivity_oat.csv        OAT table (tornado data)
  weight_sensitivity_global.csv     summary stats for (B) and (C)
  weight_rank1_stability.csv        per-case rank-1 retention probability
Deterministic under a fixed seed.
"""

import csv
import numpy as np
from geophysical_method_selector import GeophysicalMethodSelector

SEED = 20260701
N_GLOBAL = 5000
BASE = dict(physical_contrast=0.40, data_quality=0.30, cost=0.20, effort=0.10)
ORDER = ['physical_contrast', 'data_quality', 'cost', 'effort']


def load_cases(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def scenario_from_row(row):
    return dict(
        target=row['target_class'],
        target_depth=float(row['target_depth_m']),
        conductivity=float(row['conductivity_mScm']),
        noise_level=float(row['noise_level_pct']),
        budget=float(row['budget_usd']),
        time_constraint=float(row['time_constraint_d']),
        required_resolution=float(row['required_resolution']),
    )


def rank_with_weights(sel, p, w):
    """Replicates rank_methods but with an arbitrary weight dict w."""
    target = p['target'].lower()
    req_res = p.get('required_resolution', 0.6)
    scores = {}
    for m in sel.methods:
        df = sel.depth_factor(m, p['target_depth'])
        nf = sel.noise_factor(m, p['noise_level'])
        cf = sel.conductivity_factor(m, p['conductivity'])
        rm = sel.resolution_match(m, req_res)
        physical = sel.target_contrast[target][m] * 100 * df * cf
        quality = sel.target_contrast[target][m] * 100 * nf * rm
        cost = max(0.0, 100 - (sel.methods[m]['cost_per_km'] / p['budget']) * 100)
        effort = max(0.0, 100 - (sel.methods[m]['time_per_km'] / p['time_constraint']) * 100)
        scores[m] = (w['physical_contrast'] * physical + w['data_quality'] * quality +
                     w['cost'] * cost + w['effort'] * effort)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def agreement(sel, cases, w):
    t1 = t3 = 0
    rank1 = {}
    for row in cases:
        p = scenario_from_row(row)
        order = [m for m, s in rank_with_weights(sel, p, w)]
        dep = row['deployed_method']
        if order[0] == dep:
            t1 += 1
        if dep in order[:3]:
            t3 += 1
        rank1[row['case_id']] = order[0]
    n = len(cases)
    return t1 / n, t3 / n, rank1


def renorm_others(w_target_name, new_val, base):
    """Set one weight to new_val; scale the other three to preserve their
    mutual proportions so the total returns to 1.0."""
    others = [k for k in base if k != w_target_name]
    rem = 1.0 - new_val
    base_rem = sum(base[k] for k in others)
    w = {w_target_name: new_val}
    for k in others:
        w[k] = rem * (base[k] / base_rem)
    return w


def main():
    sel = GeophysicalMethodSelector()
    cases = load_cases('benchmark_cases.csv')
    rng = np.random.default_rng(SEED)

    base_t1, base_t3, base_rank1 = agreement(sel, cases, BASE)
    print(f"Baseline (fixed weights): top-1 = {base_t1*100:.1f}%, top-3 = {base_t3*100:.1f}%\n")

    # ---------------- (A) OAT ----------------
    print("=== (A) One-at-a-time weight perturbation ===")
    oat_rows = []
    for wname in ORDER:
        for pct in [-30, -20, -10, 10, 20, 30]:
            new_val = BASE[wname] * (1 + pct / 100.0)
            if new_val <= 0 or new_val >= 1:
                continue
            w = renorm_others(wname, new_val, BASE)
            t1, t3, _ = agreement(sel, cases, w)
            oat_rows.append(dict(weight=wname, perturbation_pct=pct,
                                 new_weight=round(new_val, 3),
                                 top1=round(t1 * 100, 1), top3=round(t3 * 100, 1),
                                 d_top1=round((t1 - base_t1) * 100, 1),
                                 d_top3=round((t3 - base_t3) * 100, 1)))
    with open('weight_sensitivity_oat.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(oat_rows[0].keys()))
        w.writeheader()
        for r in oat_rows:
            w.writerow(r)
    # print compact tornado summary: range of top-1 per weight
    for wname in ORDER:
        sub = [r for r in oat_rows if r['weight'] == wname]
        t1s = [r['top1'] for r in sub]
        print(f"  {wname:18s} top-1 range over +/-30%: {min(t1s):.1f}% to {max(t1s):.1f}% "
              f"(baseline {base_t1*100:.1f}%)")

    # ---------------- (B) global unconstrained ----------------
    print(f"\n=== (B) Global random weights (Dirichlet, N={N_GLOBAL}) ===")
    t1_samples = []
    t3_samples = []
    rank1_match = {row['case_id']: 0 for row in cases}
    for _ in range(N_GLOBAL):
        draw = rng.dirichlet(np.ones(4))
        w = dict(zip(ORDER, draw))
        t1, t3, rank1 = agreement(sel, cases, w)
        t1_samples.append(t1)
        t3_samples.append(t3)
        for cid, m in rank1.items():
            if m == base_rank1[cid]:
                rank1_match[cid] += 1
    t1_samples = np.array(t1_samples) * 100
    t3_samples = np.array(t3_samples) * 100
    print(f"  top-1 agreement: mean {t1_samples.mean():.1f}%, "
          f"5th-95th pct [{np.percentile(t1_samples,5):.1f}, {np.percentile(t1_samples,95):.1f}]")
    print(f"  top-3 agreement: mean {t3_samples.mean():.1f}%, "
          f"5th-95th pct [{np.percentile(t3_samples,5):.1f}, {np.percentile(t3_samples,95):.1f}]")

    # ---------------- (C) global order-preserving ----------------
    print(f"\n=== (C) Global random weights preserving order (phys>=qual>=cost>=effort) ===")
    t1_c = []
    t3_c = []
    n_c = 0
    tries = 0
    while n_c < N_GLOBAL and tries < N_GLOBAL * 50:
        tries += 1
        draw = np.sort(rng.dirichlet(np.ones(4)))[::-1]  # descending
        w = dict(zip(ORDER, draw))
        t1, t3, _ = agreement(sel, cases, w)
        t1_c.append(t1)
        t3_c.append(t3)
        n_c += 1
    t1_c = np.array(t1_c) * 100
    t3_c = np.array(t3_c) * 100
    print(f"  N={n_c} order-preserving draws")
    print(f"  top-1 agreement: mean {t1_c.mean():.1f}%, "
          f"5th-95th pct [{np.percentile(t1_c,5):.1f}, {np.percentile(t1_c,95):.1f}]")
    print(f"  top-3 agreement: mean {t3_c.mean():.1f}%, "
          f"5th-95th pct [{np.percentile(t3_c,5):.1f}, {np.percentile(t3_c,95):.1f}]")

    with open('weight_sensitivity_global.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['analysis', 'metric', 'mean_pct', 'p5_pct', 'p50_pct', 'p95_pct', 'n'])
        w.writerow(['unconstrained', 'top1', round(t1_samples.mean(),1),
                    round(np.percentile(t1_samples,5),1), round(np.percentile(t1_samples,50),1),
                    round(np.percentile(t1_samples,95),1), N_GLOBAL])
        w.writerow(['unconstrained', 'top3', round(t3_samples.mean(),1),
                    round(np.percentile(t3_samples,5),1), round(np.percentile(t3_samples,50),1),
                    round(np.percentile(t3_samples,95),1), N_GLOBAL])
        w.writerow(['order_preserving', 'top1', round(t1_c.mean(),1),
                    round(np.percentile(t1_c,5),1), round(np.percentile(t1_c,50),1),
                    round(np.percentile(t1_c,95),1), n_c])
        w.writerow(['order_preserving', 'top3', round(t3_c.mean(),1),
                    round(np.percentile(t3_c,5),1), round(np.percentile(t3_c,50),1),
                    round(np.percentile(t3_c,95),1), n_c])

    # ---------------- per-case rank-1 retention ----------------
    with open('weight_rank1_stability.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['case_id', 'target_class', 'deployed', 'baseline_rank1',
                    'rank1_retention_prob'])
        for row in cases:
            cid = row['case_id']
            w.writerow([cid, row['target_class'], row['deployed_method'],
                        base_rank1[cid], round(rank1_match[cid] / N_GLOBAL, 3)])
    ret = np.array([rank1_match[row['case_id']] / N_GLOBAL for row in cases])
    print(f"\nPer-case rank-1 retention over global weights: "
          f"mean {ret.mean():.2f}, min {ret.min():.2f}, "
          f"cases with retention >= 0.90: {int((ret>=0.90).sum())}/{len(ret)}")


if __name__ == '__main__':
    main()
