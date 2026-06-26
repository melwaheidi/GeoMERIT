"""
case_study_runner.py
====================
Runs the v2 geophysical method-selection framework against three real KSU field
case studies and reports whether the tool's top-ranked method matches the method
actually deployed. Also reproduces the published expert-consensus correlations as
an integrity check that the model is being driven correctly.

Requires (same directory):
    geophysical_method_selector_v2.py
    actual_expert_rankings_9methods.csv

Outputs:
    case_study_results.csv   (full per-site rankings, long form)
"""
import csv
import numpy as np
import pandas as pd
from scipy import stats
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2

sel = GeophysicalMethodSelectorV2()
ORDER = ["ERT", "TEM", "Induced_Polarization", "Seismic_Refraction",
         "Self_Potential", "GPR", "Gravity", "Magnetometry", "Radiometric"]

# ---------------------------------------------------------------------------
# Qualitative -> numeric encoding of the intake-workbook fields.
# Derived from the manuscript's scenario exemplars. Edit here to re-encode;
# the rankings below are recomputed from these values, nothing is hard-coded.
# ---------------------------------------------------------------------------
NOISE  = {"rural": 20, "urban": 40, "industrial": 60}        # ambient noise (%)
COND   = {"resistive": 20, "moderate": 50, "conductive": 100}  # ground conductivity (mS/m)
RESOL  = {"low": 0.5, "moderate": 0.7, "high": 0.9}          # required resolution (0-1)
BUDGET = {"low": 2500, "moderate": 5000, "high": 10000}      # budget available (USD)
SCHED  = {"low": 1.5, "moderate": 3, "high": 6}              # field-days available

# Targets outside the three validated columns are conductive-plume targets,
# governed by the same pore-fluid-conductivity contrast -> 'groundwater' column.
TARGET_MAP = {"seawater intrusion": "groundwater", "landfill leachate": "groundwater",
              "groundwater": "groundwater", "void": "void", "archaeology": "archaeology"}
# VES is 1-D DC resistivity; the framework represents it by ERT.
METHOD_MAP = {"VES": "ERT", "ERT": "ERT", "TDEM": "TEM", "TEM": "TEM"}

SITES = [
    dict(name="Site 1 - Jizan ERT", workbook_target="seawater intrusion", deployed="ERT",
         depth=50, cond="conductive", noise="rural", budget="moderate", sched="moderate", resol="high"),
    dict(name="Site 2 - Jazan TDEM", workbook_target="seawater intrusion", deployed="TDEM",
         depth=30, cond="conductive", noise="rural", budget="moderate", sched="low", resol="moderate"),
    dict(name="Site 3 - SE-Riyadh VES", workbook_target="landfill leachate", deployed="VES",
         depth=50, cond="conductive", noise="industrial", budget="low", sched="high", resol="moderate"),
]


def encode(s):
    return dict(target=TARGET_MAP[s["workbook_target"]], target_depth=s["depth"],
                conductivity=COND[s["cond"]], noise_level=NOISE[s["noise"]],
                budget=BUDGET[s["budget"]], time_constraint=SCHED[s["sched"]],
                required_resolution=RESOL[s["resol"]])


def sanity_check():
    exp = pd.read_csv("actual_expert_rankings_9methods.csv")
    paper = {
        "Groundwater":    dict(target='groundwater', target_depth=50, conductivity=100, noise_level=20, budget=5000, time_constraint=3, required_resolution=0.7),
        "Void_Detection": dict(target='void', target_depth=15, conductivity=20, noise_level=60, budget=10000, time_constraint=6, required_resolution=0.9),
        "Archaeology":    dict(target='archaeology', target_depth=2.5, conductivity=50, noise_level=20, budget=2500, time_constraint=1.5, required_resolution=0.9),
    }
    print("Integrity check - code vs published expert consensus:")
    for scn, p in paper.items():
        rk = sel.rank_methods(p)
        pos = {m: i + 1 for i, (m, _) in enumerate(rk)}
        me = exp[exp.Scenario == scn].pivot(index='Expert', columns='Method', values='Rank')[ORDER].mean().values
        fr = np.array([pos[m] for m in ORDER])
        rho, pv = stats.spearmanr(me, fr)
        print(f"  {scn:16s} rho={rho:.3f} (p={pv:.1e})")


def main():
    sanity_check()
    print("\nCase-study runs (real v2 model):")
    rows = []
    for s in SITES:
        p = encode(s)
        rk = sel.rank_methods(p)
        pos = {m: i + 1 for i, (m, _) in enumerate(rk)}
        dep = METHOD_MAP[s["deployed"]]
        match = "MATCH" if pos[dep] == 1 else f"top-{pos[dep]}"
        print(f"\n  {s['name']}  (deployed {s['deployed']} -> {dep})")
        print(f"    top-3: {', '.join(f'{m}({sc:.1f})' for m, sc in rk[:3])}")
        print(f"    deployed ranks #{pos[dep]}  =>  {match}")
        for rank, (m, sc) in enumerate(rk, 1):
            rows.append(dict(site=s["name"], deployed=dep, method=m, rank=rank,
                             score=round(sc, 2), is_deployed=(m == dep)))
    with open("case_study_results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["site", "deployed", "method", "rank", "score", "is_deployed"])
        w.writeheader()
        w.writerows(rows)
    print("\nWrote case_study_results.csv")


if __name__ == "__main__":
    main()
