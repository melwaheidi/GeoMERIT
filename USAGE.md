# Using GeoMERIT

## Minimal example

```python
from geophysical_method_selector import GeophysicalMethodSelector

selector = GeophysicalMethodSelector()

scenario = dict(
    target='groundwater',      # 'groundwater' | 'void' | 'archaeology'
    target_depth=40,           # metres
    conductivity=100,          # mS/cm (see mapping below)
    noise_level=20,            # per cent (0-100)
    budget=5000,               # USD per km
    time_constraint=3,         # days per km
    required_resolution=0.7,   # 0-1, same scale as method resolution
)

ranked = selector.rank_methods(scenario)
for method, score in ranked:
    print(f"{method:22s} {score:6.2f}")
```

`rank_methods` returns a list of `(method, score)` tuples ordered from best to
worst. The first element is the top recommendation; treat the top three as the
reliable shortlist (see limitations in the README).

## Inputs and accepted values

| Input | Type | Accepted values / guidance |
|---|---|---|
| `target` | str | `groundwater`, `void`, or `archaeology`. Seawater intrusion and conductive contamination/leachate map to `groundwater` (same pore-fluid resistivity contrast). |
| `target_depth` | number | Target depth in metres. |
| `conductivity` | number | Ground conductivity in mS/cm. Diagnostic for ERT/TEM/IP; attenuating for GPR; neutral otherwise. |
| `noise_level` | number | Ambient noise, 0 (quiet) to 100 (severe), per cent. |
| `budget` | number | Budget in USD per km; sets the cost score via Equation (4). |
| `time_constraint` | number | Available time in days per km; sets the time score via Equation (5). |
| `required_resolution` | number | Required spatial resolution, 0-1. A higher value favours high-resolution methods through the resolution-match factor. |

### Qualitative-to-numerical mapping

When only qualitative site information is available, the following documented
mapping is used throughout the manuscript and benchmark. Any run may instead
supply explicit numbers for full control.

| Qualitative level | Encoding |
|---|---|
| Conductivity: resistive / low | ~20 mS/cm |
| Conductivity: moderate | ~50 mS/cm |
| Conductivity: conductive / high (saline) | ~100 mS/cm |
| Noise: rural / low | 20 % |
| Noise: industrial / high | 60 % |
| Budget: low | 3000 USD/km |
| Budget: moderate | 5000 USD/km |
| Budget: high | 10000 USD/km |
| Time: tight schedule | shorter days/km (e.g. 1.5-2) |
| Time: relaxed schedule | longer days/km (e.g. 3-6) |
| Required resolution: moderate | 0.6 |
| Required resolution: high | 0.7-0.9 |

## Inspecting and modifying the knowledge base

All knowledge is exposed as plain attributes on the selector instance:

```python
selector.methods            # capability parameters per method
selector.target_contrast    # method-by-target contrast matrix X(m,t)
selector.weights            # the four criterion weights
```

Edit any value and re-run `rank_methods` to see the effect immediately. Because
scoring is deterministic and unfitted, the effect of any change is fully
traceable.

## Reproducing paper results

See the README. `python reproduce.py` regenerates every table and figure;
`benchmark_cases.csv` is the auditable source of the literature benchmark.
