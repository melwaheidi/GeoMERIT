"""Software architecture figure: emphasizes separation of the editable knowledge
base from the fixed decision algorithm (distinct from Fig 1's decision logic)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.font_manager as fm

plt.rcParams.update({'font.family': 'DejaVu Sans', 'savefig.dpi': 300, 'figure.dpi': 300})

fig, ax = plt.subplots(figsize=(8.2, 5.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 11); ax.axis('off')

# Colours
C_INPUT = '#e8eef4'; C_INPUT_E = '#4a6d8c'
C_KB = '#f3ead9';   C_KB_E = '#b5843a'
C_ALG = '#e6eef0';  C_ALG_E = '#3a7d8c'
C_OUT = '#e4efe4';  C_OUT_E = '#3a7d44'

def box(x, y, w, h, text, fc, ec, fs=9, bold=False, style='round'):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"{style},pad=0.02,rounding_size=0.12",
                       fc=fc, ec=ec, lw=1.3)
    ax.add_patch(p)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=fs,
            fontweight='bold' if bold else 'normal', color='#1a1a1a', linespacing=1.3)

def arrow(x1, y1, x2, y2, color='#555', style='-|>', lw=1.5, ls='-'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                 mutation_scale=14, lw=lw, color=color, linestyle=ls,
                 shrinkA=2, shrinkB=2))

# --- Top: scenario inputs (spans width) ---
box(1.7, 9.7, 6.6, 1.0, 'Scenario inputs\ntarget · depth · conductivity · noise · budget · time · resolution',
    C_INPUT, C_INPUT_E, fs=8.5, bold=True)

# --- Middle band: two columns. LEFT = knowledge base (editable), RIGHT = algorithm (fixed) ---
# Left column: knowledge base container
box(0.4, 3.2, 4.0, 5.6, '', '#faf5ea', C_KB_E, style='round')
ax.text(2.4, 8.4, 'Knowledge base', ha='center', va='center', fontsize=10.5,
        fontweight='bold', color=C_KB_E)
ax.text(2.4, 8.02, '(user-editable, no code change)', ha='center', va='center',
        fontsize=7.6, style='italic', color=C_KB_E)
box(0.7, 6.7, 3.4, 1.05, 'Method-capability table\ndepth · resolution · cost · time', C_KB, C_KB_E, fs=8)
box(0.7, 5.4, 3.4, 1.05, 'Physical-property-contrast\nmatrix  X(m, t)', C_KB, C_KB_E, fs=8)
box(0.7, 4.1, 3.4, 1.05, 'Criterion weights\n0.40 · 0.30 · 0.20 · 0.10', C_KB, C_KB_E, fs=8)

# Right column: fixed algorithm container
box(5.6, 3.2, 4.0, 5.6, '', '#eaf3f4', C_ALG_E, style='round')
ax.text(7.6, 8.4, 'Decision algorithm', ha='center', va='center', fontsize=10.5,
        fontweight='bold', color=C_ALG_E)
ax.text(7.6, 8.02, '(fixed computational core)', ha='center', va='center',
        fontsize=7.6, style='italic', color=C_ALG_E)
box(5.9, 6.7, 3.4, 1.05, 'Criterion scores\ncontrast · quality · cost · time', C_ALG, C_ALG_E, fs=8)
box(5.9, 5.4, 3.4, 1.05, 'Adjustment factors\ndepth · conductivity · noise · resolution', C_ALG, C_ALG_E, fs=7.6)
box(5.9, 4.1, 3.4, 1.05, 'Weighted-sum\naggregation  (Eq. 1)', C_ALG, C_ALG_E, fs=8)

# --- Bottom: ranked output ---
box(2.9, 1.2, 4.2, 1.0, 'Ranked method recommendations\nwith composite scores', C_OUT, C_OUT_E, fs=9, bold=True)

# --- Arrows ---
# inputs down into both columns
arrow(3.6, 9.7, 2.7, 7.85)   # to capability/scores region (left)
arrow(6.4, 9.7, 7.3, 7.85)   # to right column
# knowledge base feeds algorithm (three horizontal arrows, dashed to signal "supplies parameters")
arrow(4.1, 7.22, 5.9, 7.22, color=C_KB_E, ls=(0,(4,2)), lw=1.3)
arrow(4.1, 5.92, 5.9, 5.92, color=C_KB_E, ls=(0,(4,2)), lw=1.3)
arrow(4.1, 4.62, 5.9, 4.62, color=C_KB_E, ls=(0,(4,2)), lw=1.3)
# algorithm internal downward flow
arrow(7.6, 6.7, 7.6, 6.45, color=C_ALG_E)
arrow(7.6, 5.4, 7.6, 5.15, color=C_ALG_E)
# aggregation down to output
arrow(7.6, 4.1, 5.6, 2.2, color='#555')

# legend note for dashed arrows
ax.text(5.0, 3.45, 'dashed: knowledge base supplies parameters to the algorithm',
        ha='center', va='center', fontsize=6.8, style='italic', color='#666')

fig.tight_layout()
fig.savefig('Fig_architecture.png', bbox_inches='tight', facecolor='white')
plt.close(fig)
print("wrote Fig_architecture.png")
