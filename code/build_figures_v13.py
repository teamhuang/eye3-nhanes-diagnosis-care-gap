"""Round-13 figure restructure per reviewer's 3-figure architecture.

NEW MAIN FIGURES
  Figure 1 = study flow / dual-cohort denominators (promoted from old Figure S1),
             annotated with the 6 (DR) and 5 (AMD) self-report non-responders.
  Figure 2 = 2-panel forest (dot-whisker) diagnosis-inconsistency + severity gradient.
             Moderate-or-worse DR is shown as a separate OVERLAPPING summary row, not a
             4th mutually-exclusive tier.
  Figure 3 = eye-care association: two model-adjusted predicted probabilities as
             POINTS ONLY (no error bars: numbers_v7 flags "no reliable CI").

NEW SUPPLEMENT FIGURES
  Figure S1 = NHIS vs NHANES AMD cross-survey comparison (demoted from old main Figure 3).
  Figure S2 = gradability / IPW sensitivity (naive vs IPW base vs IPW extended).

House style: Nature look, Arial, Okabe-Ito, 600 dpi PNG + vector PDF, 5 cm x 5 cm for
EVERY figure, no title/footnote/text-note ON the plot (panel letters a/b are the only
on-figure text, per the panel-label convention).
"""
import os
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[v] = "1"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd, numpy as np
from pathlib import Path

CM = 1.0/2.54
plt.rcParams.update({
    "font.family":"sans-serif", "font.sans-serif":["Arial","DejaVu Sans"],
    "font.size":7, "axes.linewidth":0.6, "axes.spines.top":False, "axes.spines.right":False,
    "axes.titlesize":7.5, "axes.labelsize":6.8, "xtick.labelsize":6.0, "ytick.labelsize":6.2,
    "xtick.major.width":0.5, "ytick.major.width":0.5, "xtick.major.size":2.2, "ytick.major.size":2.2,
    "xtick.direction":"in", "ytick.direction":"in", "legend.fontsize":6.2, "legend.frameon":False,
    "savefig.dpi":600, "figure.dpi":300, "savefig.bbox":None,
})
OI = {"blue":"#0072B2","orange":"#E69F00","green":"#009E73",
      "verm":"#D55E00","sky":"#56B4E9","gray":"#555555"}
ROOT = Path(__file__).resolve().parents[1]
T = ROOT/"results"/"tables"; F = ROOT/"figures"; F.mkdir(exist_ok=True)

def save(fig, name):
    fig.savefig(F/(name+".png")); fig.savefig(F/(name+".pdf")); plt.close(fig)
    print("wrote", name)

gaps  = pd.read_csv(T/"t_gaps_v4.csv")
sev   = pd.read_csv(T/"t_severity_unified_v4.csv")
mn    = pd.read_csv(T/"t_modeln_v4.csv")
modw  = pd.read_csv(T/"t_modworse_gap_v6.csv")
amdsev= pd.read_csv(T/"t_amd_severity_v5.csv")
gcom  = pd.read_csv(T/"tA_gcom_v4.csv")
nstdv = pd.read_csv(T/"t_nhis_std_versions_v5.csv")
prev  = pd.read_csv(T/"t_prevalence_v4.csv")

def modeln(sub):
    return int(mn[mn.quantity.str.contains(sub, regex=False)].n.iloc[0])

# row order in t_gaps_v4 (matches v11 labels)
G = {name:(float(r.est),float(r.lo),float(r.hi))
     for name,r in zip(["DR dx gap","AMD dx gap","Late AMD gap","Care all DM","Care DM+ret"],
                       gaps.itertuples())}

# ==========================================================
# FIGURE 1 (main): study flow / dual-cohort denominators
# ==========================================================
examined=6797; grad_dr=5704; grad_amd=5604; dm_grad=884
retin_dm=319; dr_den=313; amd_obj=441; amd_den=436
dr_model=modeln("CORE complete-case"); amd_model=modeln("AMD CORE")
dr_nonresp=retin_dm-dr_den; amd_nonresp=amd_obj-amd_den

fig, ax = plt.subplots(figsize=(5*CM, 5*CM))
ax.axis("off"); ax.set_xlim(0,1); ax.set_ylim(0,1)
def box(x,y,w,h,txt,fc,fs=6.0):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.008",fc=fc,ec=OI["gray"],lw=0.6,mutation_scale=0.5))
    ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=fs,color="black",linespacing=1.15)
def arrow(y1,y2,x=0.5):
    ax.annotate("",xy=(x,y2),xytext=(x,y1),arrowprops=dict(arrowstyle="-|>",color=OI["gray"],lw=0.7))

box(0.02,0.86,0.96,0.11,f"Examined NHANES \u2265 40 with retinal photography\n2005\u201308   n = {examined:,}",OI["sky"],fs=6.2)
arrow(0.86,0.80)
box(0.02,0.68,0.46,0.10,f"Gradable DR\nn = {grad_dr:,}",'#eef6fb')
box(0.52,0.68,0.46,0.10,f"Gradable AMD\nn = {grad_amd:,}",'#eef6fb')
arrow(0.68,0.61,x=0.25); arrow(0.68,0.61,x=0.75)
box(0.02,0.49,0.46,0.10,f"Diabetes +\nretinopathy  n = {retin_dm:,}",'#fdeee6')
box(0.52,0.49,0.46,0.10,f"Graded AMD\nn = {amd_obj:,}",'#fdeee6')
arrow(0.49,0.42,x=0.25); arrow(0.49,0.42,x=0.75)
box(0.02,0.30,0.46,0.10,f"Gap denominator\nn = {dr_den:,}  (\u2212{dr_nonresp})",'#fdf3d8')
box(0.52,0.30,0.46,0.10,f"Gap denominator\nn = {amd_den:,}  (\u2212{amd_nonresp})",'#fdf3d8')
arrow(0.30,0.23,x=0.25); arrow(0.30,0.23,x=0.75)
box(0.02,0.08,0.46,0.12,f"DR core model\nn = {dr_model:,}  (\u2212{dr_den-dr_model} missing)",OI["green"])
box(0.52,0.08,0.46,0.12,f"AMD core model\nn = {amd_model:,}  (\u2212{amd_den-amd_model} missing)",OI["green"])
fig.subplots_adjust(left=0.01,right=0.99,top=0.99,bottom=0.01)
save(fig,"Fig1_flowchart")

# ==========================================================
# FIGURE 2 (main): 2-panel forest, diagnosis inconsistency + severity gradient
# dot-whisker (NOT bars); moderate-or-worse = overlapping summary row (hollow marker)
# ==========================================================
def forest(ax, rows, colors, title_side):
    """rows: list of (label, est, lo, hi, n, hollow). Draws dot+CI whisker per row."""
    ypos=np.arange(len(rows))[::-1]
    for yi,(lab,e,lo,hi,n,hollow) in zip(ypos,rows):
        ax.plot([lo,hi],[yi,yi],color=OI["gray"],lw=0.9,solid_capstyle="round",zorder=1)
        for b in (lo,hi):
            ax.plot([b,b],[yi-0.16,yi+0.16],color=OI["gray"],lw=0.9,zorder=1)
        if hollow:
            ax.plot(e,yi,marker="o",ms=5.2,mfc="white",mec=colors[rows.index((lab,e,lo,hi,n,hollow))],
                    mew=1.1,zorder=3)
        else:
            ax.plot(e,yi,marker="o",ms=5.4,color=colors[rows.index((lab,e,lo,hi,n,hollow))],zorder=3)
        ax.text(104,yi,f"{e:.1f}",va="center",ha="left",fontsize=5.6,color=OI["gray"])
    ax.set_yticks(ypos)
    ax.set_yticklabels([f"{r[0]}\nn={r[4]:,}" for r in rows],fontsize=5.4)
    ax.set_xlim(0,124); ax.set_xticks([0,50,100])
    ax.axvline(0,color=OI["gray"],lw=0.5)
    ax.tick_params(axis="y",length=0)

d=sev[sev.OPDURL4.isin([2,3,4])].sort_values("OPDURL4")
dmap=dict(zip(d.OPDURL4.values,zip(d.gap_pct_undiagnosed.values,d.lo.values,d.hi.values,d.n_responders.values)))
mv=modw.iloc[0]
dr_rows=[("Any retinopathy",G["DR dx gap"][0],G["DR dx gap"][1],G["DR dx gap"][2],313,False),
         ("Mild NPDR",dmap[2][0],dmap[2][1],dmap[2][2],int(dmap[2][3]),False),
         ("Moderate NPDR",dmap[3][0],dmap[3][1],dmap[3][2],int(dmap[3][3]),False),
         ("Severe/Prolif.",dmap[4][0],dmap[4][1],dmap[4][2],int(dmap[4][3]),False),
         ("Mod-or-worse*",float(mv.est),float(mv.lo),float(mv.hi),int(mv.n),True)]
dr_cols=[OI["verm"],OI["sky"],OI["blue"],OI["orange"],OI["verm"]]

def amd_get(tier):
    r=amdsev[amdsev.tier==tier].iloc[0]; return float(r.est),float(r.lo),float(r.hi),int(r.n)
amd_rows=[("Any AMD",G["AMD dx gap"][0],G["AMD dx gap"][1],G["AMD dx gap"][2],436,False)]
e=amd_get("Early AMD"); l=amd_get("Late AMD")
amd_rows+=[("Early AMD",e[0],e[1],e[2],e[3],False),
           ("Late AMD",l[0],l[1],l[2],l[3],False)]
amd_cols=[OI["verm"],OI["orange"],OI["blue"]]

fig,(axl,axr)=plt.subplots(2,1,figsize=(5*CM,5*CM))
forest(axl,dr_rows,dr_cols,"DR")
forest(axr,amd_rows,amd_cols,"AMD")
for ax,(t,col) in zip((axl,axr),[("Diabetic retinopathy",OI["verm"]),("Age-related macular degeneration",OI["blue"])]):
    ax.set_xlabel("% no self-reported dx",fontsize=6.0,labelpad=2)
axl.text(0.015,0.99,"a",transform=axl.transAxes,fontsize=8,fontweight="bold",va="top",ha="left")
axr.text(0.015,0.99,"b",transform=axr.transAxes,fontsize=8,fontweight="bold",va="top",ha="left")
fig.subplots_adjust(hspace=0.85,left=0.36,right=0.98,top=0.92,bottom=0.13)
save(fig,"Fig2_gradient_forest")

# ==========================================================
# FIGURE 3 (main): eye-care association, two POINTS only (no CI)
# ==========================================================
g0=float(gcom[gcom.quantity.str.contains("exam=0")].est.iloc[0])*100
g1=float(gcom[gcom.quantity.str.contains("exam=1")].est.iloc[0])*100
fig,ax=plt.subplots(figsize=(5*CM,5*CM))
for xi,v,c in zip([0,1],[g0,g1],[OI["verm"],OI["green"]]):
    ax.plot(xi,v,marker="o",ms=8,color=c,zorder=3)
    ax.text(xi,v+3.0,f"{v:.1f}%",ha="center",fontsize=7,color=OI["gray"],fontweight="bold")
ax.set_xticks([0,1]); ax.set_xticklabels(["No dilated exam\n\u2264 12 months","Dilated exam\n\u2264 12 months"],fontsize=5.8)
ax.set_xlim(-0.75,1.75); ax.set_ylim(0,100); ax.set_yticks([0,25,50,75,100])
ax.set_ylabel("Model-adjusted predicted %\nwith no self-reported diagnosis",fontsize=6.3,labelpad=2)
ax.tick_params(axis="x",length=0)
fig.subplots_adjust(left=0.28,right=0.97,top=0.98,bottom=0.16)
save(fig,"Fig3_eyecare_dots")

# ==========================================================
# FIGURE S2 (supp): NHIS vs NHANES AMD cross-survey (demoted from old main Fig 3)
# ==========================================================
obj=prev[prev.measure.str.contains("Any AMD")].iloc[0]
crude=nstdv[nstdv.quantity.str.contains("crude")].iloc[0]
ags=nstdv[nstdv.quantity.str.contains("age-standardised") & (~nstdv.quantity.str.contains("and-sex"))].iloc[0]
xs=[0,1,2]
vals3=[obj.est,float(crude.est_pct),float(ags.est_pct)]
err3=np.vstack([[vals3[0]-obj.lo,vals3[1]-float(crude.lo_pct),vals3[2]-float(ags.lo_pct)],
                [obj.hi-vals3[0],float(crude.hi_pct)-vals3[1],float(ags.hi_pct)-vals3[2]]])
fig,ax=plt.subplots(figsize=(5*CM,5*CM))
ax.bar(xs,vals3,width=0.55,color=[OI["verm"],OI["sky"],OI["blue"]],yerr=err3,
       error_kw=dict(ecolor=OI["gray"],lw=0.8,capsize=2.5,capthick=0.6))
for xi,v,h in zip(xs,vals3,[obj.hi,float(crude.hi_pct),float(ags.hi_pct)]):
    ax.text(xi,h+0.25,f"{v:.2f}%",ha="center",fontsize=6.2,color=OI["gray"],fontweight="bold")
ax.set_xticks(xs)
ax.set_xticklabels(["NHANES\ngraded\n2005\u201308","NHIS\nself-report\ncrude","NHIS\nself-report\nage-std."],fontsize=5.8)
ax.set_xlim(-0.6,2.6); ax.set_ylabel("Weighted % (US adults \u2265 40)",fontsize=6.5,labelpad=2)
ax.set_ylim(0,max(vals3)*1.30)
fig.subplots_adjust(left=0.16,right=0.98,top=0.98,bottom=0.20)
save(fig,"FigS2_nhis_amd")

# ==========================================================
# FIGURE S1 (supp): gradability / IPW sensitivity (naive vs IPW base vs IPW extended)
# ==========================================================
meas=["Any retinopathy","Any AMD"]
naive=[9.75,6.58]; ipw_base=[9.98,6.87]; ipw_ext=[10.13,6.77]
x=np.arange(len(meas)); w=0.26
fig,ax=plt.subplots(figsize=(5*CM,5*CM))
for off,vals,c,lbl in zip([-w,0,w],[naive,ipw_base,ipw_ext],[OI["gray"],OI["sky"],OI["blue"]],
                          ["Naive (gradable)","IPW base","IPW extended"]):
    ax.bar(x+off,vals,width=w,color=c,label=lbl)
    for xi,v in zip(x+off,vals):
        ax.text(xi,v+0.15,f"{v:.2f}",ha="center",fontsize=5.2,color=OI["gray"])
ax.set_xticks(x); ax.set_xticklabels(meas,fontsize=6.2)
ax.set_ylim(0,max(ipw_ext)*1.28); ax.set_ylabel("Weighted % (US adults \u2265 40)",fontsize=6.3,labelpad=2)
ax.legend(fontsize=5.4,loc="upper right",handlelength=1.0,ncol=1)
fig.subplots_adjust(left=0.17,right=0.98,top=0.98,bottom=0.14)
save(fig,"FigS1_gradability_ipw")

print("\nFig2 DR rows:",dr_rows)
print("Fig2 AMD rows:",amd_rows)
print("Fig3 points:",g0,g1,"| Fig1 nonresp:",dr_nonresp,amd_nonresp)
