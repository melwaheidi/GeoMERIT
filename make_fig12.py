"""Generate Figure 1 (workflow) and Figure 2 (contrast heatmap) for the manuscript."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import sys
sys.path.insert(0, '/home/claude/geomerit_benchmark')
from geophysical_method_selector import GeophysicalMethodSelector

plt.rcParams.update({'font.family': 'DejaVu Sans', 'savefig.dpi': 300, 'figure.dpi': 300})

# ---------- Figure 1: decision pathway ----------
fig, ax = plt.subplots(figsize=(6.8, 4.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis('off')

def box(x, y, w, h, text, fc, fs=8.5):
    b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.12",
                       fc=fc, ec='#33506b', lw=1.1)
    ax.add_patch(b)
    ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=fs, color='#1a1a1a')

def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=12,
                                 lw=1.1, color='#55606b'))

# inputs
box(0.3, 7.6, 3.2, 1.9,
    'Scenario inputs\ntarget class, depth,\nconductivity, noise,\nbudget, time, resolution', '#dbe7f3', 8)
# criteria
box(4.4, 8.4, 5.2, 1.1, 'Four weighted criteria (Eq. 1)', '#cfe0ee', 9)
box(4.4, 7.0, 5.2, 1.0, 'Physical contrast 0.40   +   Data quality 0.30', '#e8eef4', 8)
box(4.4, 5.9, 5.2, 0.9, 'Cost 0.20   +   Time and effort 0.10', '#e8eef4', 8)
# matrix
box(0.3, 5.2, 3.2, 1.6, 'Method x target\ncontrast matrix\nX(m,t)  (Table 3)', '#f2ddc4', 8.2)
# adjustment
box(0.3, 2.7, 3.2, 1.8,
    'Site adjustment factors\ndepth, conductivity,\nnoise, resolution-match', '#dbe7f3', 8.2)
# scoring
box(4.4, 3.0, 5.2, 1.5, 'Deterministic weighted sum\nS(m) = weighted criterion scores', '#cfe0ee', 8.6)
# output
box(2.6, 0.5, 4.8, 1.4, 'Ranked list of nine methods\nwith composite scores', '#c9e6cf', 9)

arrow(2.0, 7.6, 2.0, 6.85)      # inputs -> matrix
arrow(3.5, 8.5, 4.4, 8.9)       # inputs -> criteria
arrow(1.9, 5.2, 1.9, 4.55)      # matrix -> adjustment
arrow(3.5, 6.0, 4.4, 6.3)       # matrix -> criteria (contrast)
arrow(3.5, 3.5, 4.4, 3.7)       # adjustment -> scoring
arrow(7.0, 5.9, 7.0, 4.55)      # criteria -> scoring
arrow(5.0, 3.0, 4.2, 2.0)       # scoring -> output (curve-ish)
arrow(6.5, 3.0, 6.0, 2.0)

fig.tight_layout()
fig.savefig('/home/claude/manuscript_build/fig1_placeholder.png', bbox_inches='tight')
plt.close(fig)
print("wrote fig1")

# ---------- Figure 2: contrast heatmap ----------
sel = GeophysicalMethodSelector()
methods = ['ERT', 'TEM', 'Induced_Polarization', 'Seismic_Refraction', 'Self_Potential',
           'GPR', 'Gravity', 'Magnetometry', 'Radiometric']
classes = ['groundwater', 'void', 'archaeology']
M = np.array([[sel.target_contrast[c][m] for c in classes] for m in methods])

fig, ax = plt.subplots(figsize=(4.6, 4.6))
im = ax.imshow(M, cmap='YlGnBu', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(range(len(classes)))
ax.set_xticklabels([c.capitalize() for c in classes], fontsize=9)
ax.set_yticks(range(len(methods)))
ax.set_yticklabels([m.replace('_', ' ') for m in methods], fontsize=8.5)
for i in range(len(methods)):
    for j in range(len(classes)):
        v = M[i, j]
        ax.text(j, i, f"{v:.2f}", ha='center', va='center',
                color='white' if v > 0.55 else '#222', fontsize=8)
cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.set_label('Physical-property contrast X(m,t)', fontsize=8.5)
cbar.ax.tick_params(labelsize=7.5)
ax.set_title('Method-by-target contrast matrix', fontsize=10, pad=8)
fig.tight_layout()
fig.savefig('/home/claude/manuscript_build/fig2_placeholder.png', bbox_inches='tight')
plt.close(fig)
print("wrote fig2")
