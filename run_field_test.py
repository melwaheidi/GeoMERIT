"""
run_field_test.py
=================
Runs the three documented Saudi field sites through GeoMERIT. The survey
objectives, seawater intrusion (Sites 1 and 2) and landfill impact (Site 3),
are conductive-plume targets whose detectability is governed by the pore-fluid
resistivity contrast that defines the 'groundwater' class, and they are scored
within that class; the mapping is stated explicitly in the manuscript.

The a-priori parameters below encode only information available before each
survey. Qualitative levels (conductive, rural, moderate) are encoded with the
documented mapping. The encodings are the single source of truth for the
field-test results reported in the manuscript.

Output: field_test_results.csv
"""
import csv
from geophysical_method_selector import GeophysicalMethodSelector

sites = [
    dict(name='Site 1 - Jizan ERT', deployed='ERT', target='groundwater',
         target_depth=35, conductivity=100, noise_level=20,
         budget=5000, time_constraint=3, required_resolution=0.7),
    dict(name='Site 2 - Jazan TDEM', deployed='TEM', target='groundwater',
         target_depth=20, conductivity=100, noise_level=20,
         budget=5000, time_constraint=2, required_resolution=0.6),
    dict(name='Site 3 - SE-Riyadh VES', deployed='ERT', target='groundwater',
         target_depth=45, conductivity=100, noise_level=60,
         budget=3000, time_constraint=4, required_resolution=0.6),
]

def main():
    sel = GeophysicalMethodSelector()
    rows = []
    for s in sites:
        p = {k: s[k] for k in ('target', 'target_depth', 'conductivity',
                               'noise_level', 'budget', 'time_constraint',
                               'required_resolution')}
        ranked = sel.rank_methods(p)
        order = [m for m, sc in ranked]
        deployed_rank = order.index(s['deployed']) + 1
        top1 = order[0]
        print(f"{s['name']}: deployed={s['deployed']}  top1={top1}  "
              f"deployed_rank={deployed_rank}  "
              f"{'MATCH' if top1 == s['deployed'] else 'mismatch'}")
        for rank, (m, sc) in enumerate(ranked, 1):
            rows.append(dict(site=s['name'], deployed=s['deployed'], method=m,
                             rank=rank, score=round(sc, 2),
                             is_deployed=(m == s['deployed'])))
        print("   " + "  ".join(f"{m}:{sc:.1f}" for m, sc in ranked))
        print()
    with open('field_test_results.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['site', 'deployed', 'method', 'rank', 'score', 'is_deployed'])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print("wrote field_test_results.csv")

if __name__ == '__main__':
    main()
