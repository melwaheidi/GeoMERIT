"""
test_geomerit.py
================
Basic tests for GeoMERIT: determinism, output completeness, physical sanity,
and score-range validity. Run with:  python -m pytest test_geomerit.py
or simply:  python test_geomerit.py
"""
from geophysical_method_selector import GeophysicalMethodSelector

def _scenario(**kw):
    base = dict(target='groundwater', target_depth=40, conductivity=100,
                noise_level=20, budget=5000, time_constraint=3,
                required_resolution=0.7)
    base.update(kw)
    return base

def test_returns_all_nine_methods():
    sel = GeophysicalMethodSelector()
    ranked = sel.rank_methods(_scenario())
    assert len(ranked) == 9
    assert len({m for m, s in ranked}) == 9

def test_deterministic():
    sel = GeophysicalMethodSelector()
    r1 = sel.rank_methods(_scenario())
    r2 = sel.rank_methods(_scenario())
    assert r1 == r2

def test_scores_sorted_descending():
    sel = GeophysicalMethodSelector()
    scores = [s for m, s in sel.rank_methods(_scenario())]
    assert scores == sorted(scores, reverse=True)

def test_ert_leads_conductive_groundwater():
    # For a saline (conductive) groundwater target, an electrical/EM method
    # should lead and GPR should not, on physical grounds.
    sel = GeophysicalMethodSelector()
    order = [m for m, s in sel.rank_methods(_scenario())]
    assert order[0] in ('ERT', 'TEM', 'Induced_Polarization')
    assert order[0] != 'GPR'

def test_gpr_leads_shallow_archaeology():
    sel = GeophysicalMethodSelector()
    order = [m for m, s in sel.rank_methods(
        _scenario(target='archaeology', target_depth=2, conductivity=20,
                  required_resolution=0.9))]
    assert order[0] in ('GPR', 'Magnetometry')

def test_unknown_target_raises():
    sel = GeophysicalMethodSelector()
    try:
        sel.rank_methods(_scenario(target='not_a_target'))
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown target")

def test_depth_factor_penalises_beyond_reach_more_than_overcapable():
    sel = GeophysicalMethodSelector()
    # GPR max reach 15 m: a 60 m target is beyond reach (strong penalty),
    # a 0.2 m target is over-capable (mild penalty).
    beyond = sel.depth_factor('GPR', 60)
    over = sel.depth_factor('GPR', 0.2)
    assert beyond < over

def test_conductivity_diagnostic_not_penalised():
    sel = GeophysicalMethodSelector()
    # ERT conductivity is diagnostic -> factor 1.0 regardless of conductivity
    assert sel.conductivity_factor('ERT', 500) == 1.0
    # GPR is attenuated -> factor < 1.0 in conductive ground
    assert sel.conductivity_factor('GPR', 500) < 1.0

if __name__ == '__main__':
    fns = [v for k, v in sorted(globals().items()) if k.startswith('test_') and callable(v)]
    passed = 0
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests passed")
