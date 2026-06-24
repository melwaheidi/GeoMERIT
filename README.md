# Supplementary code and data

Reproduces every reported ranking, statistic, and figure in the manuscript
"An Open-Source Multi-Criteria Decision Framework for Geophysical Method
Selection: Target-Specific Physical-Property Contrast and Validation Against
Expert Consensus".

## Requirements
```
pip install -r requirements.txt      # numpy, pandas, scipy, matplotlib
```

## Files and what they reproduce

Models
- `geophysical_method_selector_v2.py`        — target-aware framework (contrast matrix + corrected depth/conductivity factors).
- `geophysical_method_selector_v1_target_blind.py` — original target-blind variant (contrast criterion = generic resolution); source of the comparison column.

Statistics
- `validation_9methods_fixed.py`             — Spearman rho (Fisher-z CI), Kendall tau, Kendall's W.

Drivers (each maps to a reported result)
- `run_v2.py`             -> Table 6 (framework vs expert ranks) and Table 7 (target-aware metrics); writes `framework_rankings_v2.csv`, `validation_results_v2.csv`.
- `robustness_v2.py`      -> Table 8 and Figure 4 (robustness to the qualitative->numeric encoding).
- `matrix_sensitivity_v2.py` -> Section 4.3, matrix-perturbation result (+/-0.1 on every contrast value, 1000 draws).
- `figures.py`            -> Figures 1-5.

Data
- `actual_expert_rankings_9methods.csv`      — per-expert rankings (E1-E5 x 3 scenarios); raw validation data.
- `framework_rankings_v2.csv`                — target-aware framework rankings (Table 6).
- `validation_results_v2.csv`                — target-aware validation metrics (Table 7).
- `framework_rankings_target_blind.csv`      — target-blind rankings; validating these reproduces the Table 7 target-blind column and the grey bars of Figure 5 (rho = 0.033, 0.450, 0.967).

## Reproduce
```
python run_v2.py              # target-aware rankings + validation
python robustness_v2.py       # encoding robustness
python matrix_sensitivity_v2.py
python figures.py             # writes figs/

# target-blind comparison column:
python -c "from validation_9methods_fixed import validate_framework; \
print(validate_framework('actual_expert_rankings_9methods.csv','framework_rankings_target_blind.csv')[['Scenario','Spearman_rho','Spearman_p']])"
```

## Scenario encodings (Table 5)
Groundwater: target_depth=50 m, conductivity=100 mS/m, noise=20%, budget=5000, time=3 d, required_resolution=0.7
Void detection: 15 m, 20 mS/m, 60%, 10000, 6 d, 0.9
Archaeology: 2.5 m, 50 mS/m, 20%, 2500, 1.5 d, 0.9
