"""
run_benchmark_statistics.py
===========================
Additional statistical characterisation of the benchmark agreement:
bootstrap confidence intervals on the top-1 and top-3 agreement rates, and
Cohen's kappa against a random-choice baseline. These quantify the precision
of the agreement estimates and the agreement beyond chance.

Only ranking-appropriate statistics are computed. Classifier metrics such as
ROC, F1, precision and recall are deliberately not used: GeoMERIT produces a
ranking of candidate methods, not a binary classification against a labelled
ground truth, so those metrics would not be well defined here.

Deterministic under a fixed seed.
Output: benchmark_statistics.csv
"""
import csv
import numpy as np

SEED = 20260701
N_BOOT = 10000

def load_results(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))

def b(x): return str(x).strip().lower() == 'true'

def bootstrap_ci(hits, n, rng, n_boot=N_BOOT):
    """Percentile bootstrap CI for a proportion given a 0/1 hit vector."""
    hits = np.array(hits, dtype=float)
    means = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, n, n)
        means[i] = hits[idx].mean()
    return means.mean(), np.percentile(means, 2.5), np.percentile(means, 97.5)

def cohens_kappa_vs_random(hits, n_methods=9, top_k=1):
    """
    Cohen's kappa comparing observed agreement (deployed method in top-k) with
    the agreement expected if the top-k set were chosen at random.
    p_o = observed agreement rate.
    p_e = chance that the deployed method falls in a random top-k set = k / n_methods.
    kappa = (p_o - p_e) / (1 - p_e).
    """
    p_o = np.mean(hits)
    p_e = top_k / n_methods
    if 1 - p_e == 0:
        return float('nan')
    return (p_o - p_e) / (1 - p_e)

def main():
    rows = load_results('benchmark_results.csv')
    n = len(rows)
    rng = np.random.default_rng(SEED)

    top1 = [1 if b(r['top1_match_aware']) else 0 for r in rows]
    top3 = [1 if b(r['top3_match_aware']) else 0 for r in rows]

    m1, lo1, hi1 = bootstrap_ci(top1, n, rng)
    m3, lo3, hi3 = bootstrap_ci(top3, n, rng)
    k1 = cohens_kappa_vs_random(top1, 9, 1)
    k3 = cohens_kappa_vs_random(top3, 9, 3)

    print(f"N = {n} benchmark cases, bootstrap draws = {N_BOOT}, seed = {SEED}\n")
    print("=== Agreement with 95% bootstrap confidence intervals ===")
    print(f"Top-1: {m1*100:.1f}%  95% CI [{lo1*100:.1f}, {hi1*100:.1f}]")
    print(f"Top-3: {m3*100:.1f}%  95% CI [{lo3*100:.1f}, {hi3*100:.1f}]")
    print("\n=== Cohen's kappa vs random method choice ===")
    print(f"Top-1 kappa (chance = 1/9): {k1:.3f}")
    print(f"Top-3 kappa (chance = 3/9): {k3:.3f}")

    with open('benchmark_statistics.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['metric', 'value_pct', 'ci_low_pct', 'ci_high_pct', 'kappa_vs_random'])
        w.writerow(['top1', round(m1*100,1), round(lo1*100,1), round(hi1*100,1), round(k1,3)])
        w.writerow(['top3', round(m3*100,1), round(lo3*100,1), round(hi3*100,1), round(k3,3)])
    print("\nwrote benchmark_statistics.csv")

if __name__ == '__main__':
    main()
