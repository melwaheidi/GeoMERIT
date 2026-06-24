"""
Matrix-perturbation sensitivity (Section 4.3, second paragraph).
Each value of the target-by-method contrast matrix is independently perturbed by
a uniform random amount of up to +/-0.1 (clipped to [0,1]); rankings and the
Spearman correlation with the expert consensus are recomputed over 1000 draws
per scenario. Reproduces the reported medians, 5th percentiles, significance,
and top-1 stability.
"""
import numpy as np, pandas as pd
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2
from scipy import stats

exp = pd.read_csv('actual_expert_rankings_9methods.csv')
ORDER = ["ERT","TEM","Induced_Polarization","Seismic_Refraction","Self_Potential",
         "GPR","Gravity","Magnetometry","Radiometric"]
SCEN = {
 "Groundwater":    dict(target='groundwater', target_depth=50,  conductivity=100, noise_level=20, budget=5000,  time_constraint=3,   required_resolution=0.7),
 "Void_Detection": dict(target='void',        target_depth=15,  conductivity=20,  noise_level=60, budget=10000, time_constraint=6,   required_resolution=0.9),
 "Archaeology":    dict(target='archaeology', target_depth=2.5, conductivity=50,  noise_level=20, budget=2500,  time_constraint=1.5, required_resolution=0.9),
}
TMAP = {"Groundwater":"groundwater","Void_Detection":"void","Archaeology":"archaeology"}
N, AMP, SEED = 1000, 0.10, 7

def mean_expert(scn):
    d = exp[exp.Scenario==scn].pivot(index='Expert', columns='Method', values='Rank')
    return d[ORDER].mean(axis=0).values

rng = np.random.default_rng(SEED)
base = GeophysicalMethodSelectorV2()
print(f"Matrix perturbation: uniform +/-{AMP} on every X_m,t, clipped to [0,1], N={N}, seed={SEED}")
print(f"{'Scenario':16s} {'median rho':>10s} {'5th pct':>8s} {'%sig':>6s} {'%top1 kept':>11s}")
for scn, p in SCEN.items():
    me = mean_expert(scn); t = TMAP[scn]
    base_top = base.rank_methods(p)[0][0]
    rhos, sig, top1 = [], 0, 0
    for _ in range(N):
        sel = GeophysicalMethodSelectorV2()
        for m in sel.target_contrast[t]:
            sel.target_contrast[t][m] = min(1.0, max(0.0, sel.target_contrast[t][m] + rng.uniform(-AMP, AMP)))
        rk = sel.rank_methods(p); o = {m: i+1 for i,(m,s) in enumerate(rk)}
        fr = np.array([o[m] for m in ORDER]); r, pv = stats.spearmanr(me, fr)
        rhos.append(r); sig += (pv < 0.05); top1 += (rk[0][0] == base_top)
    rhos = np.array(rhos)
    print(f"{scn:16s} {np.median(rhos):10.3f} {np.percentile(rhos,5):8.3f} {100*sig/N:5.0f}% {100*top1/N:10.0f}%")
