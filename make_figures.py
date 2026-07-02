"""
make_figures.py
===============
Generates the benchmark figures for the GeoMERIT manuscript at 300 dpi
from the real result files produced by run_benchmark_v3.py and
run_benchmark_robustness_v3.py. No values are hard-coded; everything is
read from the CSVs so the figures regenerate exactly from the pipeline.

Figures:
  Fig_benchmark_agreement.png : grouped bar chart of top-1 and top-3
     agreement per deployed method (target-aware v3), with per-class panel.
  Fig_benchmark_robustness.png : Monte Carlo top-1 and top-3 match
     probability per case, coloured by stability class.
  Fig_worked_example.png : ranked GeoMERIT output for one worked input
     (a transparent usage example), generated live from the v3 selector.
"""

import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from geophysical_method_selector import GeophysicalMethodSelector

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 9,
    'axes.linewidth': 0.8,
    'savefig.dpi': 300,
    'figure.dpi': 300,
})

# muted, print-safe palette
C_TOP1 = '#2c5f8a'
C_TOP3 = '#a8c4dd'
C_MATCH = '#3a7d44'
C_MIS = '#b5443a'
C_SENS = '#d9a441'


def load(path):
    with open(path, newline='') as f:
        return list(csv.DictReader(f))


def fig_agreement():
    rows = load('benchmark_results.csv')

    def b(x):
        return str(x).strip().lower() == 'true'

    methods = sorted(set(r['deployed'] for r in rows))
    n_by = {}
    t1_by = {}
    t3_by = {}
    for m in methods:
        sub = [r for r in rows if r['deployed'] == m]
        n_by[m] = len(sub)
        t1_by[m] = sum(b(r['top1_match_aware']) for r in sub) / len(sub) * 100
        t3_by[m] = sum(b(r['top3_match_aware']) for r in sub) / len(sub) * 100

    # order methods by top-3 then top-1 for readability
    order = sorted(methods, key=lambda m: (t3_by[m], t1_by[m]), reverse=True)
    labels = [m.replace('_', ' ') for m in order]
    x = np.arange(len(order))
    w = 0.38

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.0),
                                   gridspec_kw={'width_ratios': [2.3, 1]})

    ax1.bar(x - w/2, [t1_by[m] for m in order], w, label='Top-1', color=C_TOP1)
    ax1.bar(x + w/2, [t3_by[m] for m in order], w, label='Top-3', color=C_TOP3)
    for i, m in enumerate(order):
        ax1.text(i, -8, f"n={n_by[m]}", ha='center', va='top', fontsize=7.5, color='#444')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=40, ha='right', fontsize=8)
    ax1.set_ylabel('Agreement with deployed method (%)')
    ax1.set_ylim(0, 105)
    ax1.set_title('(a) Agreement by deployed method', fontsize=9.5, loc='left')
    ax1.legend(frameon=False, fontsize=8, loc='upper right')
    ax1.grid(axis='y', alpha=0.25, linewidth=0.5)
    ax1.set_axisbelow(True)

    # per-class panel
    classes = ['groundwater', 'void', 'archaeology']
    ct1, ct3, cn = [], [], []
    for c in classes:
        sub = [r for r in rows if r['target_class'] == c]
        cn.append(len(sub))
        ct1.append(sum(b(r['top1_match_aware']) for r in sub) / len(sub) * 100)
        ct3.append(sum(b(r['top3_match_aware']) for r in sub) / len(sub) * 100)
    xc = np.arange(len(classes))
    ax2.bar(xc - w/2, ct1, w, color=C_TOP1)
    ax2.bar(xc + w/2, ct3, w, color=C_TOP3)
    for i, c in enumerate(classes):
        ax2.text(i, -8, f"n={cn[i]}", ha='center', va='top', fontsize=7.5, color='#444')
    ax2.set_xticks(xc)
    ax2.set_xticklabels([c.capitalize() for c in classes], rotation=40, ha='right', fontsize=8)
    ax2.set_ylim(0, 105)
    ax2.set_title('(b) Agreement by target class', fontsize=9.5, loc='left')
    ax2.grid(axis='y', alpha=0.25, linewidth=0.5)
    ax2.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig('Fig_benchmark_agreement.png', bbox_inches='tight')
    plt.close(fig)
    print("wrote Fig_benchmark_agreement.png")


def fig_robustness():
    rows = load('benchmark_robustness.csv')
    rows = sorted(rows, key=lambda r: (r['target_class'], r['case_id']))

    ids = [r['case_id'] for r in rows]
    t1 = [float(r['mc_top1_rate']) * 100 for r in rows]
    t3 = [float(r['mc_top3_rate']) * 100 for r in rows]
    stab = [r['stability'] for r in rows]
    colour = {'stable-match': C_MATCH, 'stable-mismatch': C_MIS, 'encoding-sensitive': C_SENS}
    bar_c = [colour[s] for s in stab]

    y = np.arange(len(ids))
    fig, ax = plt.subplots(figsize=(8.6, 6.4))

    # top-3 as light background bar, top-1 as solid foreground
    ax.barh(y, t3, color='#e7e7e7', edgecolor='none', height=0.72, label='Top-3 match prob.')
    ax.barh(y, t1, color=bar_c, edgecolor='none', height=0.72, label='Top-1 match prob.')

    ax.axvline(80, color='#888', linestyle='--', linewidth=0.8)
    ax.axvline(20, color='#888', linestyle=':', linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(ids, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_xlabel('Match probability under parameter perturbation (%)  |  2000 draws/case')
    ax.set_xlim(0, 100)
    ax.set_title('Monte Carlo stability of agreement with documented practice (v3)',
                 fontsize=10, loc='left')

    # class separators
    prev = None
    for i, r in enumerate(rows):
        if r['target_class'] != prev:
            if i != 0:
                ax.axhline(i - 0.5, color='#ccc', linewidth=0.6)
            ax.text(101.5, i, r['target_class'][:4].upper(), rotation=0,
                    va='top', ha='left', fontsize=7, color='#666')
            prev = r['target_class']

    legend_handles = [
        mpatches.Patch(color=C_MATCH, label='Stable match (top-1 >= 80%)'),
        mpatches.Patch(color=C_MIS, label='Stable mismatch (top-1 <= 20%)'),
        mpatches.Patch(color=C_SENS, label='Encoding-sensitive'),
        mpatches.Patch(color='#e7e7e7', label='Top-3 match probability'),
    ]
    ax.legend(handles=legend_handles, frameon=False, fontsize=7.8,
              loc='lower right', ncol=1)
    ax.grid(axis='x', alpha=0.2, linewidth=0.5)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig('Fig_benchmark_robustness.png', bbox_inches='tight')
    plt.close(fig)
    print("wrote Fig_benchmark_robustness.png")


def fig_worked_example():
    """Transparent usage example: one representative groundwater input,
    ranked live by the v3 selector, with the criterion breakdown."""
    sel = GeophysicalMethodSelector()
    p = dict(target='groundwater', target_depth=40, conductivity=100,
             noise_level=20, budget=5000, time_constraint=3,
             required_resolution=0.7)
    ranked = sel.rank_methods(p)
    methods = [m.replace('_', ' ') for m, s in ranked]
    scores = [s for m, s in ranked]

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    y = np.arange(len(methods))
    bars = ax.barh(y, scores, color=C_TOP3, edgecolor='#5a7fa0', linewidth=0.6)
    bars[0].set_color(C_TOP1)
    ax.set_yticks(y)
    ax.set_yticklabels(methods, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('GeoMERIT composite score')
    ax.set_title('Worked example: groundwater target, 40 m depth, saline-affected coastal setting',
                 fontsize=9, loc='left')
    for i, s in enumerate(scores):
        ax.text(s + 0.6, i, f"{s:.1f}", va='center', fontsize=7.5, color='#333')
    ax.grid(axis='x', alpha=0.25, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_xlim(0, max(scores) * 1.12)

    # caption text of inputs
    txt = ("Inputs: target=groundwater, depth=40 m, ground conductivity=high, "
           "noise=low, budget=5000 USD/km, time=3 d/km, required resolution=0.7")
    fig.text(0.01, -0.02, txt, fontsize=7, color='#555')

    fig.tight_layout()
    fig.savefig('Fig_worked_example.png', bbox_inches='tight')
    plt.close(fig)
    print("wrote Fig_worked_example.png")


if __name__ == '__main__':
    fig_agreement()
    fig_robustness()
    fig_worked_example()
