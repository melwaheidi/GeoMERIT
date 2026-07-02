"""
run_benchmark_robustness.py
===========================
Monte Carlo parameter-perturbation check across the 22 benchmark cases.

For every case, the a-priori parameters (target_depth, conductivity,
noise_level, budget, time_constraint) were extracted from the source paper
or, where not stated, encoded from a qualitative band. Single-point encoding
can make a top-1 result an artifact of one arbitrary numeric choice inside
that band. This script perturbs each parameter randomly within a plausible
band around its encoded value and records how STABLE each case's top-1 /
top-3 agreement with the deployed method is across N_MC draws.

Design is the Monte Carlo robustness analysis reported in the manuscript. Fixed seed for reproducibility. The tool itself is deterministic;
only the INPUT parameters are perturbed, using the actual
GeophysicalMethodSelector scoring unchanged.

Perturbation model (per case, per draw):
  target_depth  : multiplicative, uniform in [0.6, 1.4] (depth is the most
                  uncertain qualitative-to-numeric mapping)
  conductivity  : sampled across the ordinal band it belongs to
                  (20 -> low, 50 -> moderate, 100 -> high), staying inside band
  noise_level   : additive +/- 15 percentage points, clipped to [0, 95]
  budget        : multiplicative, uniform in [0.7, 1.6] (cost ceilings were
                  the least constrained encodings)
  time          : multiplicative, uniform in [0.7, 1.6]
  required_res  : held fixed (it reflects the target class, not site logistics)

Reported per case: fraction of draws in which the deployed method is top-1,
and fraction in which it is top-3. A case whose baseline top-1 match holds
in, say, >80% of draws is "stable-match"; one that only matches in a small
fraction is "encoding-sensitive".
"""

import csv
import random
import statistics
from geophysical_method_selector import GeophysicalMethodSelector

N_MC = 2000
SEED = 20260701

# conductivity ordinal bands (mS/cm) -> plausible in-band sampling range
COND_BANDS = {
    20:  (5, 35),     # low / resistive ground
    30:  (15, 45),    # low-moderate
    50:  (30, 80),    # moderate
    100: (70, 160),   # high / saline-affected
}

def perturb(row, rng):
    depth0 = float(row['target_depth_m'])
    cond0  = float(row['conductivity_mScm'])
    noise0 = float(row['noise_level_pct'])
    budget0 = float(row['budget_usd'])
    time0  = float(row['time_constraint_d'])

    depth = depth0 * rng.uniform(0.6, 1.4)
    lo, hi = COND_BANDS.get(int(cond0), (cond0 * 0.6, cond0 * 1.4))
    cond = rng.uniform(lo, hi)
    noise = min(95.0, max(0.0, noise0 + rng.uniform(-15, 15)))
    budget = budget0 * rng.uniform(0.7, 1.6)
    time = time0 * rng.uniform(0.7, 1.6)

    return dict(
        target=row['target_class'],
        target_depth=depth,
        conductivity=cond,
        noise_level=noise,
        budget=budget,
        time_constraint=time,
        required_resolution=float(row['required_resolution']),
    )


def main():
    selector = GeophysicalMethodSelector()
    with open('benchmark_cases.csv', newline='') as f:
        cases = list(csv.DictReader(f))

    rng = random.Random(SEED)

    per_case = []
    # accumulators for aggregate stability of the headline agreement rates
    agg_top1_rates = []
    agg_top3_rates = []

    for row in cases:
        deployed = row['deployed_method']
        top1_hits = 0
        top3_hits = 0
        for _ in range(N_MC):
            p = perturb(row, rng)
            ranked = selector.rank_methods(p)
            order = [m for m, s in ranked]
            if order[0] == deployed:
                top1_hits += 1
            if deployed in order[:3]:
                top3_hits += 1
        t1 = top1_hits / N_MC
        t3 = top3_hits / N_MC
        agg_top1_rates.append(t1)
        agg_top3_rates.append(t3)

        # baseline (single-point) result for comparison
        p0 = dict(
            target=row['target_class'],
            target_depth=float(row['target_depth_m']),
            conductivity=float(row['conductivity_mScm']),
            noise_level=float(row['noise_level_pct']),
            budget=float(row['budget_usd']),
            time_constraint=float(row['time_constraint_d']),
            required_resolution=float(row['required_resolution']),
        )
        order0 = [m for m, s in selector.rank_methods(p0)]
        base_top1 = (order0[0] == deployed)
        base_top3 = (deployed in order0[:3])

        # classify
        if base_top1 and t1 >= 0.80:
            cls = 'stable-match'
        elif (not base_top1) and t1 <= 0.20:
            cls = 'stable-mismatch'
        else:
            cls = 'encoding-sensitive'

        per_case.append(dict(
            case_id=row['case_id'],
            target_class=row['target_class'],
            deployed=deployed,
            baseline_top1=base_top1,
            baseline_top3=base_top3,
            mc_top1_rate=round(t1, 3),
            mc_top3_rate=round(t3, 3),
            stability=cls,
        ))

    # write per-case robustness table
    with open('benchmark_robustness.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(per_case[0].keys()))
        w.writeheader()
        for r in per_case:
            w.writerow(r)

    n = len(per_case)
    print(f"N = {n} cases, N_MC = {N_MC} draws per case, seed = {SEED}\n")

    # aggregate: expected agreement rate under perturbation +/- spread
    mean_t1 = statistics.mean(agg_top1_rates)
    mean_t3 = statistics.mean(agg_top3_rates)
    print("=== Expected agreement under parameter perturbation ===")
    print(f"Mean per-case top-1 match probability: {mean_t1:.3f}")
    print(f"Mean per-case top-3 match probability: {mean_t3:.3f}")
    print("(These are averages of per-case match probabilities, i.e. how often")
    print(" a randomly-perturbed encoding still agrees with documented practice.)\n")

    print("=== Stability classification ===")
    for cls in ['stable-match', 'stable-mismatch', 'encoding-sensitive']:
        subs = [r for r in per_case if r['stability'] == cls]
        ids = ', '.join(r['case_id'] for r in subs)
        print(f"{cls:20s} {len(subs):2d}  [{ids}]")

    print("\n=== Encoding-sensitive cases (top-1 match rate strictly between 0.20 and 0.80) ===")
    sens = [r for r in per_case if r['stability'] == 'encoding-sensitive']
    if not sens:
        print("  none")
    for r in sens:
        print(f"  {r['case_id']:6s} {r['target_class']:12s} deployed={r['deployed']:22s} "
              f"baseline_top1={str(r['baseline_top1']):5s} mc_top1={r['mc_top1_rate']:.2f} "
              f"mc_top3={r['mc_top3_rate']:.2f}")

    print("\n=== Full per-case table ===")
    print(f"{'case':6s} {'class':12s} {'deployed':22s} {'base_t1':7s} {'mc_t1':6s} {'mc_t3':6s} stability")
    for r in per_case:
        print(f"{r['case_id']:6s} {r['target_class']:12s} {r['deployed']:22s} "
              f"{str(r['baseline_top1']):7s} {r['mc_top1_rate']:<6.2f} {r['mc_top3_rate']:<6.2f} {r['stability']}")


if __name__ == '__main__':
    main()
