import numpy as np, pandas as pd, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy import stats
from geophysical_method_selector_v2 import GeophysicalMethodSelectorV2

plt.rcParams.update({
    "font.family": "serif", "font.size": 11, "axes.titlesize": 12,
    "axes.labelsize": 11, "savefig.dpi": 300, "figure.dpi": 300,
    "axes.edgecolor": "#333333", "axes.linewidth": 0.8,
})
import os; os.makedirs("figs", exist_ok=True)
NAVY="#1f3b57"; TEAL="#2a8a8a"; STEEL="#4f7aa3"; AMBER="#c98a2b"; GREY="#888888"
sizes={}
def save(fig,name):
    fig.savefig(f"figs/{name}.png", bbox_inches="tight", facecolor="white")
    w,h=fig.get_size_inches(); sizes[name]=[float(w),float(h)]; plt.close(fig)

# ---------------- Figure 1: workflow ----------------
fig,ax=plt.subplots(figsize=(7.4,5.4)); ax.set_xlim(0,10); ax.set_ylim(0,10); ax.axis("off")
def box(x,y,w,h,text,fc,tc="white",fs=10,bold=True):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.08,rounding_size=0.12",
                 linewidth=1.0,edgecolor="#22333b",facecolor=fc))
    ax.text(x+w/2,y+h/2,text,ha="center",va="center",color=tc,fontsize=fs,
            fontweight="bold" if bold else "normal",wrap=True)
def arrow(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=14,
                 lw=1.3,color="#22333b"))
box(1.6,8.55,6.8,1.15,"Scenario inputs\ntarget · depth · conductivity · noise\nbudget · schedule · required resolution",NAVY,fs=8.5)
arrow(5,8.55,5,8.05)
# four criteria
cw=2.25; gap=0.18; x0=0.35; y=6.0
labels=[("Physical-property\ncontrast (target-\nconditioned)",TEAL),
        ("Data quality\n& resolution",STEEL),
        ("Cost",AMBER),("Time & effort",GREY)]
for i,(lab,fc) in enumerate(labels):
    box(x0+i*(cw+gap),y,cw,1.4,lab,fc,fs=8.5)
    arrow(5,8.05,x0+i*(cw+gap)+cw/2,y+1.42)
# adjustment factors band
box(0.35,4.35,9.3,0.85,"Site adjustment factors:  depth · noise · conductivity (attenuated / diagnostic) · resolution-match",
    "#e8eef3",tc="#22333b",fs=8.5)
for i in range(4):
    arrow(x0+i*(cw+gap)+cw/2,y, x0+i*(cw+gap)+cw/2,5.22)
arrow(5,4.35,5,3.75)
box(2.6,2.55,4.8,1.05,"Weighted sum  (Eq. 1)\n0.40 · 0.30 · 0.20 · 0.10",NAVY,fs=9.5)
arrow(5,2.55,5,1.95)
box(2.1,0.7,5.8,1.05,"Ranked method recommendations\n(scores + per-criterion justification)",TEAL,fs=9.5)
save(fig,"fig1_workflow")

# ---------------- Figure 2: contrast matrix heatmap ----------------
methods=["ERT","TEM","Induced Polarization","Seismic Refraction","Self-Potential","GPR","Gravity","Magnetometry","Radiometric"]
M={"groundwater":[0.95,0.90,0.75,0.70,0.55,0.30,0.20,0.15,0.05],
   "void":       [0.80,0.40,0.35,0.70,0.25,0.90,0.85,0.30,0.05],
   "archaeology":[0.75,0.20,0.45,0.25,0.30,0.92,0.25,0.90,0.45]}
data=np.array([M["groundwater"],M["void"],M["archaeology"]]).T
fig,ax=plt.subplots(figsize=(5.6,5.4))
im=ax.imshow(data,cmap="YlGnBu",vmin=0,vmax=1,aspect="auto")
ax.set_xticks(range(3)); ax.set_xticklabels(["Groundwater","Void","Archaeology"])
ax.set_yticks(range(len(methods))); ax.set_yticklabels(methods)
for i in range(len(methods)):
    for j in range(3):
        v=data[i,j]; ax.text(j,i,f"{v:.2f}",ha="center",va="center",
            color="white" if v>0.55 else "#22333b",fontsize=9)
cb=fig.colorbar(im,ax=ax,fraction=0.046,pad=0.04); cb.set_label("Physical-property contrast  $X_{m,t}$")
ax.set_title("Method × target contrast matrix")
save(fig,"fig2_matrix")

# ---------------- compute rankings & expert means ----------------
exp=pd.read_csv("actual_expert_rankings_9methods.csv")
order=["ERT","TEM","Induced_Polarization","Seismic_Refraction","Self_Potential","GPR","Gravity","Magnetometry","Radiometric"]
disp={"Induced_Polarization":"IP","Seismic_Refraction":"Seismic","Self_Potential":"SP"}
sel=GeophysicalMethodSelectorV2()
SCEN={"Groundwater":dict(target="groundwater",target_depth=50,conductivity=100,noise_level=20,budget=5000,time_constraint=3,required_resolution=0.7),
      "Void_Detection":dict(target="void",target_depth=15,conductivity=20,noise_level=60,budget=10000,time_constraint=6,required_resolution=0.9),
      "Archaeology":dict(target="archaeology",target_depth=2.5,conductivity=50,noise_level=20,budget=2500,time_constraint=1.5,required_resolution=0.9)}
titles={"Groundwater":"Groundwater","Void_Detection":"Void detection","Archaeology":"Archaeology"}
fwrank={}; exprank={}
for s,p in SCEN.items():
    ranked=sel.rank_methods(p); o={m:i+1 for i,(m,sc) in enumerate(ranked)}
    fwrank[s]=o
    d=exp[exp.Scenario==s].pivot(index="Expert",columns="Method",values="Rank")
    exprank[s]=d.mean(axis=0)

# ---------------- Figure 3: agreement scatter (3 panels) ----------------
fig,axes=plt.subplots(1,3,figsize=(9.6,3.5))
for ax,s in zip(axes,["Groundwater","Void_Detection","Archaeology"]):
    x=np.array([exprank[s][m] for m in order]); y=np.array([fwrank[s][m] for m in order])
    rho,p=stats.spearmanr(x,y)
    ax.plot([0.5,9.5],[0.5,9.5],ls="--",color=GREY,lw=1)
    ax.scatter(x,y,s=42,color=TEAL,edgecolor="#22333b",zorder=3)
    for m in order:
        ax.annotate(disp.get(m,m),(exprank[s][m],fwrank[s][m]),fontsize=6.5,
                    xytext=(3,3),textcoords="offset points")
    ax.set_xlim(0,10); ax.set_ylim(0,10); ax.set_xticks(range(1,10,2)); ax.set_yticks(range(1,10,2))
    ax.invert_xaxis(); ax.invert_yaxis()
    ax.set_title(f"{titles[s]}\n$\\rho$ = {rho:.2f}  (p = {p:.3g})",fontsize=10)
    ax.set_xlabel("Mean expert rank")
axes[0].set_ylabel("Framework rank")
fig.tight_layout()
save(fig,"fig3_agreement")

# ---------------- Figure 4: v1 vs v2 rho ----------------
v1={"Groundwater":0.033,"Void_Detection":0.450,"Archaeology":0.967}
v2={"Groundwater":0.933,"Void_Detection":0.900,"Archaeology":0.933}
scn=["Groundwater","Void_Detection","Archaeology"]; xlab=[titles[s] for s in scn]
xi=np.arange(3); bw=0.36
fig,ax=plt.subplots(figsize=(6.6,4.0))
b1=ax.bar(xi-bw/2,[v1[s] for s in scn],bw,label="Target-blind (original)",color=GREY,edgecolor="#22333b")
b2=ax.bar(xi+bw/2,[v2[s] for s in scn],bw,label="Target-aware (revised)",color=TEAL,edgecolor="#22333b")
rho_crit=0.683
ax.axhline(rho_crit,ls="--",color=AMBER,lw=1.3)
ax.text(2.45,rho_crit+0.02,"p = 0.05 (n = 9)",color=AMBER,fontsize=8,ha="right")
for b in list(b1)+list(b2):
    ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.015,f"{b.get_height():.2f}",ha="center",fontsize=8.5)
ax.set_xticks(xi); ax.set_xticklabels(xlab); ax.set_ylim(0,1.05)
ax.set_ylabel("Spearman's $\\rho$ vs expert consensus")
ax.set_title("Effect of the target-contrast matrix"); ax.legend(frameon=False,fontsize=9,loc="upper left")
save(fig,"fig4_v1v2")

# ---------------- Figure 5: robustness distributions ----------------
BANDS={"Groundwater":dict(target="groundwater",depth=(30,100),cond=(60,150),noise=(10,30),budget=(4000,7000),time=(2,4),res=0.7),
       "Void_Detection":dict(target="void",depth=(5,30),cond=(5,40),noise=(40,75),budget=(8000,14000),time=(4,8),res=0.9),
       "Archaeology":dict(target="archaeology",depth=(0.5,5),cond=(20,80),noise=(10,30),budget=(1500,4000),time=(1,2.5),res=0.9)}
rng=np.random.default_rng(42); dists={}
for s,b in BANDS.items():
    me=np.array([exprank[s][m] for m in order]); arr=[]
    for _ in range(500):
        p=dict(target=b["target"],target_depth=float(rng.uniform(*b["depth"])),
               conductivity=float(rng.uniform(*b["cond"])),noise_level=float(rng.uniform(*b["noise"])),
               budget=float(rng.uniform(*b["budget"])),time_constraint=float(rng.uniform(*b["time"])),
               required_resolution=b["res"])
        rk=sel.rank_methods(p); o={m:i+1 for i,(m,sc) in enumerate(rk)}
        fr=np.array([o[m] for m in order]); arr.append(stats.spearmanr(me,fr)[0])
    dists[s]=np.array(arr)
fig,ax=plt.subplots(figsize=(6.6,4.0))
parts=ax.violinplot([dists[s] for s in scn],positions=xi,showmedians=True,widths=0.7)
for pc in parts["bodies"]: pc.set_facecolor(TEAL); pc.set_alpha(0.55); pc.set_edgecolor("#22333b")
for k in ("cmedians","cmins","cmaxes","cbars"):
    if k in parts: parts[k].set_color("#22333b")
ax.axhline(rho_crit,ls="--",color=AMBER,lw=1.3); ax.text(2.45,rho_crit-0.05,"p = 0.05 (n = 9)",color=AMBER,fontsize=8,ha="right")
ax.set_xticks(xi); ax.set_xticklabels(xlab); ax.set_ylim(0,1.02)
ax.set_ylabel("Spearman's $\\rho$ (500 random encodings)")
ax.set_title("Robustness to qualitative→numeric encoding")
save(fig,"fig5_robustness")

json.dump(sizes,open("figs/sizes.json","w"),indent=2)
print("Figures written:",list(sizes.keys()))
