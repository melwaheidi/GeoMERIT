# Supplementary code — revised framework (v2)

Reproduces all rankings, validation statistics, and the robustness analysis in the manuscript.

## Files
- `geophysical_method_selector_v2.py` — corrected framework (adds target-by-method physical-property-contrast matrix; corrected depth and conductivity factors).
- `run_v2.py` — maps the Section 5 / Table 5 scenario parameters to numeric inputs, regenerates `framework_rankings_v2.csv`, and revalidates → `validation_results_v2.csv`.
- `robustness_v2.py` — Monte Carlo robustness of Spearman's rho to the qualitative→numeric encoding (Table 8).
- `validation_9methods_fixed.py` — unchanged statistics module (Spearman rho, Kendall tau, Kendall's W).
- `actual_expert_rankings_9methods.csv` — per-expert rankings (5 experts × 3 scenarios), unchanged.
- `framework_rankings_v2.csv`, `validation_results_v2.csv` — generated outputs.

## Reproduce
```bash
pip install numpy pandas scipy
python run_v2.py          # rankings + validation
python robustness_v2.py   # robustness table
```
