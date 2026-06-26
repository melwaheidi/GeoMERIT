# Using GeoMERIT

GeoMERIT ranks nine near-surface methods for a single investigation scenario.
A scenario is a Python `dict` passed to `selector.rank_methods(scenario)`, which
returns a list of `(method, score)` pairs ordered from best to worst.

## Input fields

| Field | Meaning | Accepted values |
|-------|---------|-----------------|
| `target` | Investigation target class | `'groundwater'`, `'void'`, `'archaeology'` (seawater intrusion and landfill leachate map to the groundwater pore-fluid-conductivity column) |
| `target_depth` | Depth of interest (m) | positive number |
| `conductivity` | Ground/target conductivity (mS/m) | positive number |
| `noise_level` | Ambient cultural/EM noise (%) | 0–100 (rural ~20, urban ~40, industrial ~60) |
| `budget` | Indicative budget per line-km (USD) | positive number |
| `time_constraint` | Indicative time per line-km (days) | positive number |
| `required_resolution` | Required resolution (0–1, higher = finer) | 0–1 |

## Example

```python
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2

selector = GeophysicalMethodSelectorV2()

scenario = dict(target='void', target_depth=15, conductivity=20,
                noise_level=60, budget=10000, time_constraint=6,
                required_resolution=0.9)

ranking = selector.rank_methods(scenario)
for rank, (method, score) in enumerate(ranking, 1):
    print(f"{rank:>2}  {method:<22} {score:6.1f}")
```

## Adapting the knowledge base

Every parameter that drives a recommendation is inspectable and editable inside
`geophysical_method_selector_v2.py`: the per-method capability table, the
method-by-target contrast matrix, and the four criteria weights. Edit a value
and re-run to see its effect immediately; nothing is fitted or hidden.
