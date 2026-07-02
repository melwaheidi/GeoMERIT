"""
Geophysical Method Selection Framework
======================================

Weighted sum model for near-surface geophysical method selection. Nine methods
are scored against four criteria (physical-property contrast 0.40, data quality
0.30, cost 0.20, time and effort 0.10) and modulated by site adjustment factors
for target depth, ambient noise, and ground conductivity.

Both physics-based criteria are anchored on a method-by-target physical-property
contrast value X(m,t): the physical-contrast score modulates it by the depth and
conductivity factors that determine whether the target contrast is reachable and
diagnostic at the site, and the data-quality score modulates it by the noise and
resolution-match factors that determine the achievable signal-to-noise and
spatial detail. The intrinsic resolution of a method enters only through the
resolution-match requirement of the scenario, not as the base of the data-quality
criterion. The contrast matrix therefore governs both physics-based criteria, a
design whose justification and consequences are documented in the accompanying
manuscript.

The contrast matrix and method-capability parameters are derived from published
physical-property and method-applicability references (Telford et al. 1990;
Reynolds 2011; Milsom & Eriksen 2013; Everett 2013; Butler 2005; Loke 1999;
Binley & Kemna 2005) and are independent of any deployment outcome or agreement
statistic. Scoring is deterministic; no parameter is fitted to data.
"""

import numpy as np
from typing import Dict, List, Tuple

class GeophysicalMethodSelector:

    def __init__(self):
        # ---- Method capability parameters --------------------------------
        # depth_range (m), resolution (0-1), cost_per_km (USD), time_per_km (d),
        # noise_sensitivity (0-1), conductivity response type, conductivity
        # sensitivity (0-1, only used when response == 'attenuated').
        self.methods = {
            'ERT':                 dict(depth_range=(1,100),  resolution=0.80, cost_per_km=3000, time_per_km=2.0, noise_sensitivity=0.6, cond_response='diagnostic', cond_sensitivity=0.0),
            'Induced_Polarization':dict(depth_range=(1,50),   resolution=0.70, cost_per_km=4000, time_per_km=2.5, noise_sensitivity=0.7, cond_response='diagnostic', cond_sensitivity=0.0),
            'Self_Potential':      dict(depth_range=(0.5,30), resolution=0.60, cost_per_km=1500, time_per_km=1.0, noise_sensitivity=0.9, cond_response='diagnostic', cond_sensitivity=0.0),
            'GPR':                 dict(depth_range=(0.5,15), resolution=0.95, cost_per_km=2500, time_per_km=1.5, noise_sensitivity=0.4, cond_response='attenuated', cond_sensitivity=0.95),
            'TEM':                 dict(depth_range=(10,300), resolution=0.60, cost_per_km=5000, time_per_km=3.0, noise_sensitivity=0.5, cond_response='diagnostic', cond_sensitivity=0.0),
            'Seismic_Refraction':  dict(depth_range=(5,100),  resolution=0.70, cost_per_km=6000, time_per_km=4.0, noise_sensitivity=0.6, cond_response='neutral',    cond_sensitivity=0.0),
            'Magnetometry':        dict(depth_range=(0.5,50), resolution=0.65, cost_per_km=2000, time_per_km=1.0, noise_sensitivity=0.5, cond_response='neutral',    cond_sensitivity=0.0),
            'Gravity':             dict(depth_range=(10,500), resolution=0.50, cost_per_km=4500, time_per_km=3.5, noise_sensitivity=0.4, cond_response='neutral',    cond_sensitivity=0.0),
            'Radiometric':         dict(depth_range=(0,0.5),  resolution=0.80, cost_per_km=3500, time_per_km=1.5, noise_sensitivity=0.3, cond_response='neutral',    cond_sensitivity=0.0),
        }

        # ---- Method x target-class physical-property-contrast matrix ------
        # Values in [0,1] reflect the PHYSICAL basis for detecting each target
        # class, from the references cited in the module docstring. They are
        # independent of any deployment outcome or agreement statistic.
        #   groundwater : pore-fluid conductivity / saturation contrast -> DC & EM
        #   void        : density deficit & resistivity/velocity contrast -> gravity/GPR/ERT/seismic
        #   archaeology : magnetic susceptibility & shallow structure -> mag/GPR/ERT
        self.target_contrast = {
            'groundwater': dict(ERT=0.95, TEM=0.90, Induced_Polarization=0.75, Seismic_Refraction=0.70,
                                Self_Potential=0.55, GPR=0.30, Gravity=0.20, Magnetometry=0.15, Radiometric=0.05),
            'void':        dict(GPR=0.90, Gravity=0.85, ERT=0.80, Seismic_Refraction=0.70, TEM=0.40,
                                Induced_Polarization=0.35, Magnetometry=0.30, Self_Potential=0.25, Radiometric=0.05),
            'archaeology': dict(GPR=0.92, Magnetometry=0.90, ERT=0.75, Radiometric=0.45, Induced_Polarization=0.45,
                                Self_Potential=0.30, Gravity=0.25, Seismic_Refraction=0.25, TEM=0.20),
        }

        # ---- Static, transparent criteria weights (sum = 1.0) -------------
        # NOTE: v2 uses FIXED weights. The v1 manuscript claim of "dynamically
        # adjusted weights" did not exist in code and is removed. Adaptive
        # weighting remains future work.
        self.weights = dict(physical_contrast=0.40, data_quality=0.30, cost=0.20, effort=0.10)

    # ---- Adjustment factors ----------------------------------------------
    def depth_factor(self, method: str, target_depth: float) -> float:
        """1.0 within range; strong penalty when target is BEYOND reach
        (deeper than max); mild penalty when over-capable (shallower than min)."""
        dmin, dmax = self.methods[method]['depth_range']
        if dmin <= target_depth <= dmax:
            return 1.0
        if target_depth > dmax:                      # method cannot reach target
            return max(0.20, 1.0 - (target_depth - dmax) / dmax)
        return 0.85                                  # over-capable: mild penalty

    def noise_factor(self, method: str, noise_level: float) -> float:
        s = self.methods[method]['noise_sensitivity']
        return max(0.0, 1.0 - s * (noise_level / 100.0) ** 2)

    def conductivity_factor(self, method: str, conductivity: float) -> float:
        """Conductive ground attenuates GPR (penalty); for ERT/TEM/IP pore-fluid
        conductivity is the target contrast, not a penalty (factor = 1.0)."""
        resp = self.methods[method]['cond_response']
        if resp == 'attenuated':
            s = self.methods[method]['cond_sensitivity']
            return max(0.0, 1.0 - s * (conductivity / 1000.0))
        return 1.0  # 'diagnostic' or 'neutral'

    def resolution_match(self, method: str, required_resolution: float) -> float:
        r = self.methods[method]['resolution']
        return 1.0 if r >= required_resolution else r / required_resolution

    # ---- Core ranking -----------------------------------------------------
    def rank_methods(self, p: Dict) -> List[Tuple[str, float]]:
        target = p['target'].lower()
        if target not in self.target_contrast:
            raise ValueError(f"Unknown target '{target}'. Known: {list(self.target_contrast)}")
        req_res = p.get('required_resolution', 0.6)
        scores = {}
        for m in self.methods:
            df = self.depth_factor(m, p['target_depth'])
            nf = self.noise_factor(m, p['noise_level'])
            cf = self.conductivity_factor(m, p['conductivity'])
            rm = self.resolution_match(m, req_res)

            physical = self.target_contrast[target][m] * 100 * df * cf
            # Note: data-quality base is the method's target-specific contrast
            # (achievable signal-to-noise for THIS target), not its context-free
            # resolution constant, still modulated by site noise (nf) and the
            # resolution match (rm). See module note below.
            quality  = self.target_contrast[target][m] * 100 * nf * rm
            cost     = max(0.0, 100 - (self.methods[m]['cost_per_km'] / p['budget']) * 100)
            effort   = max(0.0, 100 - (self.methods[m]['time_per_km'] / p['time_constraint']) * 100)

            scores[m] = (self.weights['physical_contrast'] * physical +
                         self.weights['data_quality']     * quality  +
                         self.weights['cost']             * cost     +
                         self.weights['effort']           * effort)
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)
