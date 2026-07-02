"""
run_weight_derivation.py
========================
Objective, data-driven derivation of the criterion weights, to test whether the
fixed 40/30/20/10 scheme is defensible or arbitrary. No human elicitation is
used (which would reintroduce a human-subjects component); instead the weights
are derived by the entropy method, a standard objective MCDA weighting that
assigns higher weight to criteria that discriminate more strongly among the
alternatives.

Method (Shannon entropy weighting):
  1. Build the decision matrix of criterion scores (physical, quality, cost,
     effort) for all methods across all 22 benchmark cases, using the real v3
     scoring components.
  2. Normalise each criterion column to a probability distribution.
  3. Compute the Shannon entropy e_j of each criterion; its degree of
     diversification d_j = 1 - e_j.
  4. Entropy weight w_j = d_j / sum_k d_k.

The entropy weights are then compared with the fixed scheme. Because the
manuscript retains fixed weights, the purpose is to show the fixed weights are
close to, and consistent with, an objective derivation, and to report the
benchmark agreement obtained under the entropy weights.

Deterministic; no randomness.
"""

import csv
import numpy as np
from geophysical_method_selector import GeophysicalMethodSelector

ORDER = ['physical_contrast', 'data_quality', 'cost', 'effort']
FIXED = np.array([0.40, 0.30, 0.20, 0.10])


def load(path):
    return list(csv.DictReader(open(path)))


def score_components(sel, p):
    """Return dict method -> [physical, quality, cost, effort] (pre-weight)."""
    target = p['target'].lower()
    req_res = p.get('required_resolution', 0.6)
    comp = {}
    for m in sel.methods:
        df = sel.depth_factor(m, p['target_depth'])
        nf = sel.noise_factor(m, p['noise_level'])
        cf = sel.conductivity_factor(m, p['conductivity'])
        rm = sel.resolution_match(m, req_res)
        physical = sel.target_contrast[target][m] * 100 * df * cf
        quality = sel.target_contrast[target][m] * 100 * nf * rm
        cost = max(0.0, 100 - (sel.methods[m]['cost_per_km'] / p['budget']) * 100)
        effort = max(0.0, 100 - (sel.methods[m]['time_per_km'] / p['time_constraint']) * 100)
        comp[m] = [physical, quality, cost, effort]
    return comp


def scenario(row):
    return dict(target=row['target_class'], target_depth=float(row['target_depth_m']),
                conductivity=float(row['conductivity_mScm']), noise_level=float(row['noise_level_pct']),
                budget=float(row['budget_usd']), time_constraint=float(row['time_constraint_d']),
                required_resolution=float(row['required_resolution']))


def rank_with_weights(sel, p, w):
    comp = score_components(sel, p)
    scores = {m: float(np.dot(w, comp[m])) for m in comp}
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def agreement(sel, cases, w):
    t1 = t3 = 0
    for row in cases:
        order = [m for m, s in rank_with_weights(sel, scenario(row), w)]
        dep = row['deployed_method']
        if order[0] == dep:
            t1 += 1
        if dep in order[:3]:
            t3 += 1
    n = len(cases)
    return t1 / n, t3 / n


def main():
    sel = GeophysicalMethodSelector()
    cases = load('benchmark_cases.csv')

    # build full decision matrix: rows = (case, method), cols = criteria
    rows_mat = []
    for row in cases:
        comp = score_components(sel, scenario(row))
        for m in comp:
            rows_mat.append(comp[m])
    X = np.array(rows_mat)  # (22*9, 4)

    # entropy weighting
    # shift to strictly positive to allow normalisation (add small epsilon where column has zeros)
    col_sums = X.sum(axis=0)
    # avoid divide-by-zero; if a column is all zero it carries no info
    P = np.zeros_like(X)
    for j in range(X.shape[1]):
        if col_sums[j] > 0:
            P[:, j] = X[:, j] / col_sums[j]
    m_rows = X.shape[0]
    k = 1.0 / np.log(m_rows)
    e = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        col = P[:, j]
        nz = col[col > 0]
        e[j] = -k * np.sum(nz * np.log(nz))
    d = 1 - e
    w_entropy = d / d.sum()

    print("=== Objective (entropy) weight derivation ===\n")
    print(f"{'criterion':20s} {'entropy e_j':>12s} {'diversif. d_j':>14s} {'entropy w_j':>12s} {'fixed w_j':>10s}")
    for j, name in enumerate(ORDER):
        print(f"{name:20s} {e[j]:12.4f} {d[j]:14.4f} {w_entropy[j]:12.3f} {FIXED[j]:10.2f}")

    t1_e, t3_e = agreement(sel, cases, w_entropy)
    t1_f, t3_f = agreement(sel, cases, FIXED)
    print(f"\nBenchmark agreement under FIXED weights:   top-1 {t1_f*100:.1f}%, top-3 {t3_f*100:.1f}%")
    print(f"Benchmark agreement under ENTROPY weights: top-1 {t1_e*100:.1f}%, top-3 {t3_e*100:.1f}%")

    # rank correlation between the two weight vectors (do they order criteria the same?)
    order_fixed = np.argsort(-FIXED)
    order_entropy = np.argsort(-w_entropy)
    same_order = np.array_equal(order_fixed, order_entropy)
    print(f"\nFixed weights order:   {[ORDER[i] for i in order_fixed]}")
    print(f"Entropy weights order: {[ORDER[i] for i in order_entropy]}")
    print(f"Same criterion ordering: {same_order}")
    # L1 distance
    print(f"L1 distance |fixed - entropy| = {np.abs(FIXED - w_entropy).sum():.3f}")

    with open('weight_derivation.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['criterion', 'entropy_e', 'diversification_d', 'entropy_weight', 'fixed_weight'])
        for j, name in enumerate(ORDER):
            w.writerow([name, round(e[j],4), round(d[j],4), round(w_entropy[j],3), FIXED[j]])
        w.writerow([])
        w.writerow(['agreement', 'top1_pct', 'top3_pct', '', ''])
        w.writerow(['fixed', round(t1_f*100,1), round(t3_f*100,1), '', ''])
        w.writerow(['entropy', round(t1_e*100,1), round(t3_e*100,1), '', ''])
    print("\nwrote weight_derivation.csv")


if __name__ == '__main__':
    main()
