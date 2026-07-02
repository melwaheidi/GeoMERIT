# GeoMERIT

**Geophysical Method Evaluation and Ranking by Investigation Target**

Open-source, knowledge-based tool that ranks nine common near-surface
geophysical methods for a stated investigation target, using a transparent
weighted sum over an explicit, literature-derived method-by-target
physical-property-contrast matrix.

- **Manuscript:** "GeoMERIT: an open-source tool for reproducible
  target-specific selection of near-surface geophysical methods."
- **Author:** Mahmoud M. Elwaheidi, King Saud University
  (melwaheidi@ksu.edu.sa; ORCID 0000-0003-4863-3184)
- **License:** MIT (see `LICENSE`)
- **Archive:** Zenodo concept DOI 10.5281/zenodo.20932723

## What it does

For a scenario (target class, target depth, ground conductivity, ambient noise,
budget, schedule, required resolution), GeoMERIT scores each of nine methods
(ERT, IP, SP, GPR, TEM, seismic refraction, magnetometry, gravity, radiometric)
on four fixed-weight criteria: physical-property contrast (0.40), data quality
(0.30), cost (0.20), and time and effort (0.10). Both physics-based criteria are
anchored on a target-conditioned contrast value, so the recommendation depends
on what the target is, not on generic method resolution. The output is the full
ranked list of methods with composite scores.

Scoring is deterministic and no parameter is fitted to data: every
recommendation traces to the published tables in
`geophysical_method_selector.py`, which a user can inspect and edit.

## Environment

- Python 3.8 or later (developed and tested under Python 3.12)
- Dependencies in `requirements.txt` (NumPy; pandas and Matplotlib for the
  benchmark and figures)

```
pip install -r requirements.txt
```

## Reproducing the study

```
python reproduce.py    # all results, tables, and figures (seeded)
```

Individual analyses:

```
python run_field_test.py              # three retrospective field sites
python run_benchmark.py               # 22-case benchmark + target-blind control
python run_benchmark_robustness.py    # Monte Carlo stability (fixed seed)
python run_benchmark_statistics.py    # bootstrap CIs and Cohen kappa
python run_weight_sensitivity.py      # global weight sensitivity (fixed seed)
python run_weight_derivation.py       # objective (entropy) weight comparison
python run_rank1_probability.py       # rank-1 probability under uncertainty
python failure_analysis.py            # classification of disagreements
```

Tests and demonstration:

```
python test_geomerit.py               # basic tests (determinism, sanity, ranges)
jupyter notebook GeoMERIT_demo.ipynb  # worked demonstration
```

## File manifest

| File | Purpose |
|---|---|
| `geophysical_method_selector.py` | Core tool (single deterministic class) |
| `benchmark_cases.csv` | 22 documented literature cases: a-priori parameters, deployed method, ground truth, citation, encoding flags |
| `run_field_test.py` | Three retrospective field sites |
| `run_benchmark.py` | Benchmark runner (target-aware and target-blind control) |
| `run_benchmark_robustness.py` | Monte Carlo parameter-perturbation stability (fixed seed) |
| `run_benchmark_statistics.py` | Bootstrap confidence intervals and Cohen kappa |
| `run_weight_sensitivity.py` | Global weight sensitivity analysis (fixed seed) |
| `run_weight_derivation.py` | Objective entropy-weighting comparison |
| `run_rank1_probability.py` | Rank-1 probability under input uncertainty (fixed seed) |
| `failure_analysis.py` | Classification of stable disagreements |
| `make_figures.py`, `make_field_figure.py`, `make_fig12.py`, `make_weight_figure.py`, `make_extra_figures.py`, `make_architecture_figure.py` | Figure generation |
| `reproduce.py` | Regenerates everything in order |
| `test_geomerit.py` | Basic test suite |
| `GeoMERIT_demo.ipynb` | Worked demonstration notebook |
| `requirements.txt`, `LICENSE`, `USAGE.md` | Environment, licence, usage guide |

## Data provenance

`benchmark_cases.csv` contains, for each case, the a-priori parameters extracted
from the source publication together with the full citation and a flag recording
any qualitative-to-numerical encoding assumption. Third-party datasets and
source texts are **not** redistributed here; each case is cited to its original
publication.

## Scope and limitations

GeoMERIT operationalizes established literature knowledge; it is a transparent,
reproducible decision aid, not an independently validated predictor. Benchmarked
against 22 documented field cases, it places the deployed method within its
top-three shortlist in 82% of cases (Cohen kappa 0.73) and beats a target-blind
control, but first-place agreement concentrates in ERT-dominant and GPR-dominant
targets and several methods are under-ranked at first place even where they were
the field-validated choice. A Monte Carlo analysis confirms this is structural
rather than an encoding artefact; a weight sensitivity analysis shows the
recommendations are stable across weightings that respect the intended priority
order; and an entropy-weighting comparison shows a purely statistical weighting
performs worse. The benchmark reflects publication and selection bias (published
surveys favour methods that worked). Rely on the top-three shortlist rather than
the single top pick. See the manuscript Discussion for the full statement.
