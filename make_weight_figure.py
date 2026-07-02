"""Weight sensitivity figures: (a) tornado plot of OAT top-1 sensitivity,
(b) distribution of top-1/top-3 agreement over constrained vs unconstrained
global weight sampling. Reads the CSVs written by run_weight_sensitivity.py."""
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams.update({'font.family': 'DejaVu Sans', 'savefig.dpi': 300, 'figure.dpi': 300})

C_LOW = '#b5443a'
C_HIGH = '#2c5f8a'
C_BASE = '#444444'
C_CON = '#3a7d44'
C_UNC = '#a8c4dd'

BASE_T1 = 45.5

# ---- read OAT ----
oat = list(csv.DictReader(open('weight_sensitivity_oat.csv')))
order = ['physical_contrast', 'data_quality', 'cost', 'effort']
labels = {'physical_contrast': 'Physical contrast\n(0.40)', 'data_quality': 'Data quality\n(0.30)',
          'cost': 'Cost\n(0.20)', 'effort': 'Time and effort\n(0.10)'}

# for tornado: min and max top-1 achieved over the +/-30% sweep per weight
tor = {}
for wn in order:
    sub = [float(r['top1']) for r in oat if r['weight'] == wn]
    tor[wn] = (min(sub), max(sub))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.4, 4.2), gridspec_kw={'width_ratios': [1.05, 1]})

y = np.arange(len(order))
for i, wn in enumerate(order):
    lo, hi = tor[wn]
    # bar from lo to hi, split at baseline
    ax1.barh(i, BASE_T1 - lo, left=lo, color=C_LOW, height=0.6, zorder=2)
    ax1.barh(i, hi - BASE_T1, left=BASE_T1, color=C_HIGH, height=0.6, zorder=2)
ax1.axvline(BASE_T1, color=C_BASE, lw=1.4, zorder=3, label=f'Baseline {BASE_T1:.1f}%')
ax1.set_yticks(y)
ax1.set_yticklabels([labels[w] for w in order], fontsize=8.5)
ax1.invert_yaxis()
ax1.set_xlabel('Top-1 benchmark agreement (%)')
ax1.set_title('(a) One-at-a-time weight perturbation (+/-30%)', fontsize=9.5, loc='left')
ax1.set_xlim(38, 58)
ax1.grid(axis='x', alpha=0.25, lw=0.5)
ax1.set_axisbelow(True)
lh = [mpatches.Patch(color=C_LOW, label='Agreement decrease'),
      mpatches.Patch(color=C_HIGH, label='Agreement increase')]
ax1.legend(handles=lh + [plt.Line2D([0],[0], color=C_BASE, lw=1.4, label=f'Baseline {BASE_T1:.1f}%')],
           fontsize=7.5, frameon=False, loc='lower right')

# ---- global distributions ----
# re-read raw samples is not stored; use summary CSV percentiles to draw box-like bars,
# but better: recompute quickly from global CSV summary
g = list(csv.DictReader(open('weight_sensitivity_global.csv')))
def getrow(analysis, metric):
    for r in g:
        if r['analysis'] == analysis and r['metric'] == metric:
            return r
    return None

groups = [('order_preserving', 'top1', 'Order-preserving\ntop-1'),
          ('order_preserving', 'top3', 'Order-preserving\ntop-3'),
          ('unconstrained', 'top1', 'Unconstrained\ntop-1'),
          ('unconstrained', 'top3', 'Unconstrained\ntop-3')]
xs = np.arange(len(groups))
for i, (an, mt, lab) in enumerate(groups):
    r = getrow(an, mt)
    p5, p50, p95 = float(r['p5_pct']), float(r['p50_pct']), float(r['p95_pct'])
    mean = float(r['mean_pct'])
    col = C_CON if an == 'order_preserving' else C_UNC
    # whisker p5-p95
    ax2.plot([i, i], [p5, p95], color=col, lw=2, zorder=2)
    ax2.plot([i-0.12, i+0.12], [p5, p5], color=col, lw=2)
    ax2.plot([i-0.12, i+0.12], [p95, p95], color=col, lw=2)
    # box-ish marker at median, dot at mean
    ax2.scatter([i], [p50], color=col, s=55, zorder=3, edgecolor='white', linewidth=0.8)
    ax2.scatter([i], [mean], color=C_BASE, marker='D', s=26, zorder=4)
ax2.axhline(BASE_T1, color=C_BASE, lw=1.0, ls='--', alpha=0.6)
ax2.text(3.35, BASE_T1 + 0.8, 'baseline top-1', fontsize=7, color=C_BASE, ha='right')
ax2.set_xticks(xs)
ax2.set_xticklabels([g[2] for g in groups], fontsize=8)
ax2.set_ylabel('Benchmark agreement (%)')
ax2.set_title('(b) Agreement over global weight sampling', fontsize=9.5, loc='left')
ax2.set_ylim(0, 100)
ax2.grid(axis='y', alpha=0.25, lw=0.5)
ax2.set_axisbelow(True)
lh2 = [mpatches.Patch(color=C_CON, label='Order-preserving weightings'),
       mpatches.Patch(color=C_UNC, label='All admissible weightings'),
       plt.Line2D([0],[0], marker='D', color=C_BASE, lw=0, label='Mean', markersize=6),
       plt.Line2D([0],[0], marker='o', color='#888', lw=0, label='Median (p50)', markersize=7)]
ax2.legend(handles=lh2, fontsize=7, frameon=False, loc='lower left')
ax2.text(0.5, 6, 'whiskers: 5th-95th percentile', fontsize=6.8, color='#666')

fig.tight_layout()
fig.savefig('Fig_weight_sensitivity.png', bbox_inches='tight')
plt.close(fig)
print("wrote Fig_weight_sensitivity.png")
