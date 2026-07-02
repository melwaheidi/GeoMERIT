"""Figures for uncertainty (rank-1 probability at field sites) and failure taxonomy."""
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

plt.rcParams.update({'font.family': 'DejaVu Sans', 'savefig.dpi': 300, 'figure.dpi': 300})
C1='#2c5f8a'; C3='#a8c4dd'; CB='#444444'

# ---- Figure: rank-1 probability + score bands at the three field sites ----
rows = list(csv.DictReader(open('rank1_probability_fieldsites.csv')))
sites = []
for r in rows:
    if r['scenario'] not in sites: sites.append(r['scenario'])

fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.0))
for ax, site in zip(axes, sites):
    sr = [r for r in rows if r['scenario'] == site]
    sr = sorted(sr, key=lambda r: float(r['mean_score']), reverse=True)
    methods = [r['method'].replace('_',' ') for r in sr]
    mean = [float(r['mean_score']) for r in sr]
    p5 = [float(r['p5_score']) for r in sr]
    p95 = [float(r['p95_score']) for r in sr]
    prob = [float(r['rank1_prob']) for r in sr]
    y = np.arange(len(methods))
    # colour by rank1 probability (dark if it ever wins)
    cols = [C1 if pr > 0.001 else C3 for pr in prob]
    err_low = [m - lo for m, lo in zip(mean, p5)]
    err_hi = [hi - m for m, hi in zip(mean, p95)]
    ax.barh(y, mean, xerr=[err_low, err_hi], color=cols, height=0.62,
            error_kw=dict(ecolor='#888', lw=0.9, capsize=2), edgecolor='#5a7fa0', linewidth=0.4)
    ax.set_yticks(y); ax.set_yticklabels(methods, fontsize=7.5)
    ax.invert_yaxis()
    short = site.split('(')[0].strip()
    ax.set_title(short, fontsize=9, loc='left')
    ax.set_xlabel('Composite score (mean, 5th-95th pct)')
    ax.grid(axis='x', alpha=0.25, lw=0.5); ax.set_axisbelow(True)
    ax.set_xlim(0, max(p95)*1.12)
    # annotate rank-1 method probability
    top = sr[0]
    ax.text(float(top['mean_score'])*0.5, -0.35, f"P(rank 1)={float(top['rank1_prob']):.2f}",
            fontsize=7.5, color=C1, ha='center')

handles = [mpatches.Patch(color=C1, label='Attains rank 1 in some draw'),
           mpatches.Patch(color=C3, label='Never rank 1')]
fig.legend(handles=handles, frameon=False, fontsize=8, loc='lower center', ncol=2,
           bbox_to_anchor=(0.5,-0.04))
fig.tight_layout(rect=[0,0.03,1,1])
fig.savefig('Fig_rank1_probability.png', bbox_inches='tight')
plt.close(fig)
print("wrote Fig_rank1_probability.png")

# ---- Figure: failure taxonomy stacked by target class ----
fa = list(csv.DictReader(open('failure_analysis.csv')))
cats = ['operational','matrix','scope']
classes = ['groundwater','void','archaeology']
catcol = {'operational':'#3a7d44','matrix':'#d9a441','scope':'#b5443a'}
counts = {cl:{c:0 for c in cats} for cl in classes}
for r in fa:
    counts[r['target_class']][r['category']] += 1

fig, ax = plt.subplots(figsize=(6.6, 3.8))
x = np.arange(len(classes)); bottom = np.zeros(len(classes))
for c in cats:
    vals = [counts[cl][c] for cl in classes]
    ax.bar(x, vals, bottom=bottom, color=catcol[c], label=c, width=0.6, edgecolor='white', linewidth=0.6)
    for i,(v,b0) in enumerate(zip(vals,bottom)):
        if v>0:
            ax.text(i, b0+v/2, str(v), ha='center', va='center', color='white', fontsize=9, fontweight='bold')
    bottom += vals
ax.set_xticks(x); ax.set_xticklabels([c.capitalize() for c in classes], fontsize=9)
ax.set_ylabel('Number of stable mismatches')
ax.set_title('Classification of stable top-1 mismatches (n=12)', fontsize=10, loc='left')
lab = {'operational':'Operational (deployed method rank 2; logistical choice)',
       'matrix':'Matrix/resolution (ERT-GPR dominance; shortlist retained)',
       'scope':'Scope (diagnostic basis weakly represented; out of top-3)'}
handles = [mpatches.Patch(color=catcol[c], label=lab[c]) for c in cats]
ax.legend(handles=handles, frameon=False, fontsize=7.6, loc='upper right')
ax.grid(axis='y', alpha=0.25, lw=0.5); ax.set_axisbelow(True)
ax.set_ylim(0, 7)
fig.tight_layout()
fig.savefig('Fig_failure_taxonomy.png', bbox_inches='tight')
plt.close(fig)
print("wrote Fig_failure_taxonomy.png")
