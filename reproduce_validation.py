"""
reproduce_validation.py
Regenerates the expert-consensus validation metrics reported for GeoMERIT
(Spearman's rho, Kendall's tau, and inter-expert Kendall's W) for the three
published scenarios, directly from the released model and expert data.

Run:  python reproduce_validation.py
Requires: geophysical_method_selector_v2.py, actual_expert_rankings_9methods.csv
"""
import numpy as np, pandas as pd
from scipy import stats
from itertools import combinations
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2

ORDER = ["ERT","TEM","Induced_Polarization","Seismic_Refraction",
         "Self_Potential","GPR","Gravity","Magnetometry","Radiometric"]
SCEN = {
 "Groundwater":   dict(target='groundwater', target_depth=50, conductivity=100, noise_level=20, budget=5000, time_constraint=3,   required_resolution=0.7),
 "Void_Detection":dict(target='void',        target_depth=15, conductivity=20,  noise_level=60, budget=10000,time_constraint=6,   required_resolution=0.9),
 "Archaeology":   dict(target='archaeology', target_depth=2.5,conductivity=50,  noise_level=20, budget=2500, time_constraint=1.5, required_resolution=0.9),
}

def kendalls_w(rank_matrix):
    # rank_matrix: experts x items (ranks). Returns Kendall's W.
    m, n = rank_matrix.shape
    Rj = rank_matrix.sum(axis=0)
    S = ((Rj - Rj.mean())**2).sum()
    return 12*S / (m**2 * (n**3 - n))

def main():
    sel = GeophysicalMethodSelectorV2()
    exp = pd.read_csv("actual_expert_rankings_9methods.csv")
    print(f"{'Scenario':16} {'rho':>6} {'p(rho)':>9} {'tau':>6} {'W(experts)':>11}  top method")
    print("-"*70)
    for scn, p in SCEN.items():
        E = exp[exp.Scenario==scn].pivot(index='Expert', columns='Method', values='Rank')[ORDER]
        mean_expert = E.mean(axis=0).values
        rk = sel.rank_methods(p)
        pos = {meth:i+1 for i,(meth,_) in enumerate(rk)}
        framework = np.array([pos[m] for m in ORDER])
        rho, prho = stats.spearmanr(mean_expert, framework)
        tau, _    = stats.kendalltau(mean_expert, framework)
        W = kendalls_w(E.values)
        print(f"{scn:16} {rho:6.3f} {prho:9.4f} {tau:6.3f} {W:11.3f}  {rk[0][0]}")
    print("\nExpected (manuscript): rho = 0.933 / 0.900 / 0.933 ; tau = 0.833 / 0.778 / 0.833")

if __name__ == "__main__":
    main()
