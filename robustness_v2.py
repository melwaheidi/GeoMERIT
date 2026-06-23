"""
Robustness of v2 results to the qualitative->numeric encoding.
Randomly perturbs conductivity, noise, budget, time and the representative depth
within each scenario's qualitative band, and reports the distribution of
Spearman rho vs the expert consensus. If correlations stay high across plausible
encodings, the result is driven by the target-contrast structure, not by the
specific numbers chosen.
"""
import numpy as np, pandas as pd
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2
from scipy import stats

sel = GeophysicalMethodSelectorV2()
exp = pd.read_csv('actual_expert_rankings_9methods.csv')
METHODS = ['GPR','ERT','Magnetometry','Radiometric','Self_Potential',
           'Induced_Polarization','Seismic_Refraction','TEM','Gravity']

def mean_expert(scn):
    d = exp[exp.Scenario==scn].pivot(index='Expert', columns='Method', values='Rank')
    return d[METHODS].mean(axis=0).values

# bands: depth drawn within qualitative range; others within plausible spread
BANDS = {
  'Groundwater':    dict(scn='Groundwater', target='groundwater', depth=(30,100),  cond=(60,150),  noise=(10,30), budget=(4000,7000),  time=(2,4),   res=0.7),
  'Void_Detection': dict(scn='Void_Detection', target='void',     depth=(5,30),    cond=(5,40),    noise=(40,75), budget=(8000,14000), time=(4,8),   res=0.9),
  'Archaeology':    dict(scn='Archaeology', target='archaeology', depth=(0.5,5),   cond=(20,80),   noise=(10,30), budget=(1500,4000),  time=(1,2.5), res=0.9),
}

rng = np.random.default_rng(42)
N = 500
print(f"{'Scenario':16s} {'rho_median':>11s} {'rho_5th':>9s} {'rho_95th':>9s} {'%sig(p<.05)':>12s}")
for name,b in BANDS.items():
    me = mean_expert(b['scn'])
    rhos, sig = [], 0
    for _ in range(N):
        p = dict(target=b['target'],
                 target_depth=float(rng.uniform(*b['depth'])),
                 conductivity=float(rng.uniform(*b['cond'])),
                 noise_level=float(rng.uniform(*b['noise'])),
                 budget=float(rng.uniform(*b['budget'])),
                 time_constraint=float(rng.uniform(*b['time'])),
                 required_resolution=b['res'])
        ranked = sel.rank_methods(p)
        order = {m:i+1 for i,(m,s) in enumerate(ranked)}
        fr = np.array([order[m] for m in METHODS], float)
        rho,pv = stats.spearmanr(me, fr)
        rhos.append(rho); sig += (pv<0.05)
    rhos=np.array(rhos)
    print(f"{name:16s} {np.median(rhos):11.3f} {np.percentile(rhos,5):9.3f} "
          f"{np.percentile(rhos,95):9.3f} {100*sig/N:11.1f}%")
