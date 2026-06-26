# GeoMERIT

**Geophysical Method Evaluation and Ranking by Investigation Target**

Reproducibility package for the manuscript:

> Elwaheidi, M. M. *GeoMERIT: an open-source tool for geophysical method selection
> using target-specific physical-property contrast, validated against expert
> consensus and field deployments.* Submitted to *Applied Computing and Geosciences*.

Author: Mahmoud M. Elwaheidi, Department of Geology and Geophysics, College of
Science, King Saud University (ORCID: 0000-0003-4863-3184).

GeoMERIT is an open-source tool that ranks nine common near-surface geophysical
methods (ERT, IP, SP, GPR, TEM, seismic refraction, magnetometry, gravity, and
radiometric) for a stated investigation scenario. Methods are scored against
four weighted criteria — physical-property contrast (0.40), data quality (0.30),
cost (0.20), and time/effort (0.10) — refined by site-specific adjustment
factors for target depth, ambient noise, and ground conductivity. The element
that governs the ranking is an explicit method-by-target physical-property
contrast matrix, so the score a method receives is conditioned on what the
target is rather than on a generic measure of resolution.

## Requirements

Python 3.8+ with the packages in `requirements.txt`:

```
pip install -r requirements.txt
```

## Contents

| File | Description |
|------|-------------|
| `geophysical_method_selector_v2.py` | Core tool: the `GeophysicalMethodSelectorV2` class (method table, contrast matrix, weights, scoring). |
| `actual_expert_rankings_9methods.csv` | Expert rankings (5 experts x 9 methods x 3 scenarios) used for validation. |
| `GeoMethod_CaseStudy_Intake_2.xlsx` | Intake workbook with the three field-site case-study encodings. |
| `reproduce_validation.py` | Regenerates the expert-consensus metrics (Spearman rho, Kendall tau, inter-expert W). |
| `case_study_runner.py` | Runs GeoMERIT on the three documented field sites and writes `case_study_results.csv`. |
| `make_usage_figure.py` | Reproduces the worked usage example shown in Figure 3. |
| `case_study_results.csv` | Output: field-site rankings and deployed-vs-recommended comparison. |
| `geomerit_usage_figure.png` | Output: Figure 3 (example use of GeoMERIT). |
| `case_study_figure.png` | Output: Figure 7 (field-site rankings and depth crossover). |
| `LICENSE` | MIT License. |

## Reproducing the results

```bash
python reproduce_validation.py     # expert-consensus metrics (Table of validation metrics)
python case_study_runner.py        # field-site validation (Section 5.4 / Figure 7)
python make_usage_figure.py        # worked example (Figure 3)
```

Expected output of `reproduce_validation.py`:

```
Groundwater       rho=0.933  tau=0.833   top method ERT
Void_Detection    rho=0.900  tau=0.778   top method GPR
Archaeology       rho=0.933  tau=0.833   top method GPR
```

The scoring is deterministic and contains no fitted parameters, so these values
reproduce exactly. The Monte Carlo robustness analysis (Figure 5) uses a fixed
random seed; set the same seed to reproduce the reported distribution.

## Using GeoMERIT on a new scenario

```python
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2
selector = GeophysicalMethodSelectorV2()
scenario = dict(target='groundwater', target_depth=50, conductivity=100,
                noise_level=20, budget=5000, time_constraint=3,
                required_resolution=0.7)
for rank, (method, score) in enumerate(selector.rank_methods(scenario), 1):
    print(rank, method, round(score, 1))
```

See `USAGE.md` for the full list of input fields and accepted values.

## Data provenance

The expert rankings and the derived case-study encodings are released here as
research artifacts of this study. The underlying field datasets that motivated
the three case-study sites are not redistributed and remain credited to their
original sources (Maeshi et al. 2026; Alharbi et al., 2023; Badhrais, 2025), as cited
in the manuscript.

## Citation

Please cite the manuscript above and the archived release. After minting a
Zenodo DOI, cite the concept DOI:https://doi.org/10.5281/zenodo.20932723. 

> Elwaheidi, M. M. (2026). GeoMERIT (Version 1.0.0) [Software]. Zenodo.
> https://doi.org/10.5281/zenodo.20932723.

## License

MIT License — see `LICENSE`.
