"""
Reproducible build + validation for v2 framework.
Maps the qualitative Section 5.1 scenario descriptors to numeric model inputs
(every assumption explicit), regenerates framework rankings, and revalidates
against the unchanged expert panel using the original validation module.
"""
import pandas as pd
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2
from validation_9methods_fixed import validate_framework

# ---- Explicit qualitative -> numeric encoding of Section 5.1 -------------
# required_resolution: Low=0.5, Moderate=0.7, High=0.9
SCENARIOS = {
    'Groundwater':    dict(target='groundwater', target_depth=50.0,  conductivity=100.0, noise_level=20.0, budget=5000.0,  time_constraint=3.0, required_resolution=0.7),
    'Void_Detection': dict(target='void',        target_depth=15.0,  conductivity=20.0,  noise_level=60.0, budget=10000.0, time_constraint=6.0, required_resolution=0.9),
    'Archaeology':    dict(target='archaeology', target_depth=2.5,   conductivity=50.0,  noise_level=20.0, budget=2500.0,  time_constraint=1.5, required_resolution=0.9),
}

METHOD_ORDER = ['GPR','ERT','Magnetometry','Radiometric','Self_Potential',
                'Induced_Polarization','Seismic_Refraction','TEM','Gravity']

sel = GeophysicalMethodSelectorV2()

# ---- Generate rankings ---------------------------------------------------
rows = []
print("="*78)
print("v2 FRAMEWORK RANKINGS (with scores)")
print("="*78)
rank_lookup = {}
for name, p in SCENARIOS.items():
    ranked = sel.rank_methods(p)
    print(f"\n{name}  [target={p['target']}, depth={p['target_depth']}m, "
          f"cond={p['conductivity']}mS/m, noise={p['noise_level']}%, "
          f"budget=${p['budget']:.0f}, time={p['time_constraint']}d]")
    order = {m: i+1 for i,(m,s) in enumerate(ranked)}
    for i,(m,s) in enumerate(ranked,1):
        print(f"   {i}. {m:22s} {s:6.2f}")
    rank_lookup[name] = order
    rows.append({'Scenario': name, **{m: order[m] for m in METHOD_ORDER}})

framework_df = pd.DataFrame(rows)[['Scenario']+METHOD_ORDER]
framework_df.to_csv('framework_rankings_v2.csv', index=False)

# ---- Revalidate ----------------------------------------------------------
res = validate_framework('actual_expert_rankings_9methods.csv', 'framework_rankings_v2.csv')
print("\n"+"="*78)
print("v2 VALIDATION vs EXPERT CONSENSUS")
print("="*78)
print(res[['Scenario','Spearman_rho','Spearman_p','Kendall_tau','Kendall_p','Kendalls_W']].to_string(index=False))
res.to_csv('validation_results_v2.csv', index=False)
