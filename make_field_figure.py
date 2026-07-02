"""
make_field_figure.py
====================
Field-test figure (Figure of the three Saudi sites) at 300 dpi from the
canonical v3 field-test results (field_test_results.csv). Shows the
ranked GeoMERIT score for every method at each site, deployed method
highlighted.
"""
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'savefig.dpi': 300, 'figure.dpi': 300})

C_DEP = '#b5443a'   # deployed method
C_TOP = '#2c5f8a'   # top-ranked (if not deployed)
C_OTH = '#a8c4dd'

with open('field_test_results.csv', newline='') as f:
    rows = list(csv.DictReader(f))

sites = []
for r in rows:
    if r['site'] not in sites:
        sites.append(r['site'])

fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.2), sharey=False)
short = {'Site 1 - Jizan ERT': 'Site 1: Jizan (deployed ERT)',
         'Site 2 - Jazan TDEM': 'Site 2: Jazan (deployed TEM)',
         'Site 3 - SE-Riyadh VES': 'Site 3: SE-Riyadh (deployed VES/ERT)'}

for ax, site in zip(axes, sites):
    srows = [r for r in rows if r['site'] == site]
    srows = sorted(srows, key=lambda r: float(r['score']), reverse=True)
    methods = [r['method'].replace('_', ' ') for r in srows]
    scores = [float(r['score']) for r in srows]
    deployed = [r['is_deployed'].strip().lower() == 'true' for r in srows]

    colours = []
    for i, (r, dep) in enumerate(zip(srows, deployed)):
        if dep:
            colours.append(C_DEP)
        elif i == 0:
            colours.append(C_TOP)
        else:
            colours.append(C_OTH)

    y = np.arange(len(methods))
    ax.barh(y, scores, color=colours, edgecolor='#5a7fa0', linewidth=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(methods, fontsize=7.5)
    ax.invert_yaxis()
    ax.set_title(short.get(site, site), fontsize=9, loc='left')
    ax.set_xlabel('GeoMERIT score')
    ax.grid(axis='x', alpha=0.25, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.set_xlim(0, max(scores) * 1.14)
    for i, s in enumerate(scores):
        ax.text(s + 0.8, i, f"{s:.0f}", va='center', fontsize=7, color='#333')

# shared legend
import matplotlib.patches as mpatches
handles = [mpatches.Patch(color=C_DEP, label='Deployed method'),
           mpatches.Patch(color=C_TOP, label='GeoMERIT top-ranked'),
           mpatches.Patch(color=C_OTH, label='Other methods')]
fig.legend(handles=handles, frameon=False, fontsize=8, loc='lower center',
           ncol=3, bbox_to_anchor=(0.5, -0.04))
fig.tight_layout(rect=[0, 0.03, 1, 1])
fig.savefig('Fig_field_test.png', bbox_inches='tight')
plt.close(fig)
print("wrote Fig_field_test.png")
