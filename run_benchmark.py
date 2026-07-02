"""
run_benchmark.py
=================
Runs the real GeophysicalMethodSelector (target-aware) and a target-blind
variant against benchmark_cases.csv, and reports top-1 / top-3 agreement
with the method actually deployed at each site, overall and broken down
by method and by target class.

The target-blind variant reduces the physical-property-contrast criterion
to each method's generic resolution constant (removing the target-specific
contrast matrix). This target-blind control isolates whether the
agreement of GeoMERIT with documented field practice comes from the
target-specific contrast matrix or would arise regardless from the
cost, time, and noise terms alone.
"""

import csv
import copy
from geophysical_method_selector import GeophysicalMethodSelector

def rank_target_blind(selector, p):
    """Same scoring as rank_methods, but physical-contrast criterion uses
    generic resolution instead of the target-specific contrast matrix."""
    req_res = p.get('required_resolution', 0.6)
    scores = {}
    for m in selector.methods:
        df = selector.depth_factor(m, p['target_depth'])
        nf = selector.noise_factor(m, p['noise_level'])
        cf = selector.conductivity_factor(m, p['conductivity'])
        rm = selector.resolution_match(m, req_res)

        # target-blind: physical score driven by generic resolution, not X_m,t
        physical = selector.methods[m]['resolution'] * 100 * df * cf
        quality  = selector.methods[m]['resolution'] * 100 * nf * rm
        cost     = max(0.0, 100 - (selector.methods[m]['cost_per_km'] / p['budget']) * 100)
        effort   = max(0.0, 100 - (selector.methods[m]['time_per_km'] / p['time_constraint']) * 100)

        scores[m] = (selector.weights['physical_contrast'] * physical +
                     selector.weights['data_quality']     * quality  +
                     selector.weights['cost']             * cost     +
                     selector.weights['effort']           * effort)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


def load_cases(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def main():
    selector = GeophysicalMethodSelector()
    cases = load_cases('benchmark_cases.csv')

    results = []
    for row in cases:
        p = dict(
            target=row['target_class'],
            target_depth=float(row['target_depth_m']),
            conductivity=float(row['conductivity_mScm']),
            noise_level=float(row['noise_level_pct']),
            budget=float(row['budget_usd']),
            time_constraint=float(row['time_constraint_d']),
            required_resolution=float(row['required_resolution']),
        )
        ranked_aware = selector.rank_methods(p)
        ranked_blind = rank_target_blind(selector, p)

        top1_aware = ranked_aware[0][0]
        top3_aware = [m for m, s in ranked_aware[:3]]
        top1_blind = ranked_blind[0][0]
        top3_blind = [m for m, s in ranked_blind[:3]]

        deployed = row['deployed_method']

        results.append(dict(
            case_id=row['case_id'],
            location=row['location'],
            target_class=row['target_class'],
            deployed=deployed,
            top1_aware=top1_aware,
            top1_match_aware=(top1_aware == deployed),
            top3_match_aware=(deployed in top3_aware),
            top1_blind=top1_blind,
            top1_match_blind=(top1_blind == deployed),
            top3_match_blind=(deployed in top3_blind),
            rank_of_deployed_aware=[m for m, s in ranked_aware].index(deployed) + 1,
            score_top1_aware=round(ranked_aware[0][1], 2),
            score_deployed_aware=round(dict(ranked_aware)[deployed], 2),
        ))

    # --- write full per-case result table ---
    with open('benchmark_results.csv', 'w', newline='') as f:
        fieldnames = list(results[0].keys())
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow(r)

    n = len(results)
    top1_aware = sum(r['top1_match_aware'] for r in results)
    top3_aware = sum(r['top3_match_aware'] for r in results)
    top1_blind = sum(r['top1_match_blind'] for r in results)
    top3_blind = sum(r['top3_match_blind'] for r in results)

    print(f"N = {n} benchmark cases\n")
    print("=== Overall agreement with deployed method ===")
    print(f"Target-aware GeoMERIT: top-1 = {top1_aware}/{n} ({100*top1_aware/n:.1f}%), "
          f"top-3 = {top3_aware}/{n} ({100*top3_aware/n:.1f}%)")
    print(f"Target-blind variant:  top-1 = {top1_blind}/{n} ({100*top1_blind/n:.1f}%), "
          f"top-3 = {top3_blind}/{n} ({100*top3_blind/n:.1f}%)")

    print("\n=== Per target-class agreement (target-aware) ===")
    for cls in ['groundwater', 'void', 'archaeology']:
        sub = [r for r in results if r['target_class'] == cls]
        t1 = sum(r['top1_match_aware'] for r in sub)
        t3 = sum(r['top3_match_aware'] for r in sub)
        print(f"{cls:12s} n={len(sub):2d}  top-1={t1}/{len(sub)} ({100*t1/len(sub):.0f}%)  "
              f"top-3={t3}/{len(sub)} ({100*t3/len(sub):.0f}%)")

    print("\n=== Per deployed-method agreement (target-aware) ===")
    methods = sorted(set(r['deployed'] for r in results))
    for m in methods:
        sub = [r for r in results if r['deployed'] == m]
        t1 = sum(r['top1_match_aware'] for r in sub)
        t3 = sum(r['top3_match_aware'] for r in sub)
        print(f"{m:22s} n={len(sub):2d}  top-1={t1}/{len(sub)} ({100*t1/len(sub):.0f}%)  "
              f"top-3={t3}/{len(sub)} ({100*t3/len(sub):.0f}%)")

    print("\n=== Case-by-case (target-aware) ===")
    for r in results:
        flag = "MATCH" if r['top1_match_aware'] else f"mismatch (deployed ranked #{r['rank_of_deployed_aware']})"
        print(f"{r['case_id']:6s} {r['target_class']:12s} deployed={r['deployed']:22s} "
              f"top1={r['top1_aware']:22s} {flag}")


if __name__ == '__main__':
    main()
