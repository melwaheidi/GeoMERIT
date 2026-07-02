"""
reproduce.py
============
Master reproduction script for the GeoMERIT manuscript. Regenerates every
reported result, table, and figure from documented parameters, in order.
Stochastic steps (Monte Carlo robustness, weight sampling, uncertainty
propagation) use a fixed seed.

Run:  python reproduce.py

Deterministic tool: GeophysicalMethodSelector in
geophysical_method_selector.py, applied to the documented inputs in
benchmark_cases.csv and the field-site encodings in run_field_test.py.
No reported value is hard-coded.
"""
import runpy, sys

STEPS = [
    ("Retrospective field test",               "run_field_test.py",             []),
    ("Literature benchmark + target-blind",    "run_benchmark.py",              []),
    ("Monte Carlo robustness (seeded)",        "run_benchmark_robustness.py",   []),
    ("Bootstrap CIs and Cohen kappa",          "run_benchmark_statistics.py",   []),
    ("Weight sensitivity analysis (seeded)",   "run_weight_sensitivity.py",     []),
    ("Objective (entropy) weight comparison",  "run_weight_derivation.py",      []),
    ("Rank-1 probability / uncertainty (seeded)", "run_rank1_probability.py",   []),
    ("Failure-mode classification",            "failure_analysis.py",           []),
    ("Benchmark and worked-example figures",   "make_figures.py",               []),
    ("Field-test figure",                      "make_field_figure.py",          []),
    ("Framework and matrix figures",           "make_fig12.py",                 []),
    ("Weight sensitivity figure",              "make_weight_figure.py",         []),
    ("Uncertainty and failure-taxonomy figures", "make_extra_figures.py",       []),
]

def main():
    for title, script, args in STEPS:
        print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)
        sys.argv = [script] + args
        runpy.run_path(script, run_name="__main__")
    print("\nAll results, tables, and figures regenerated.")

if __name__ == "__main__":
    main()
