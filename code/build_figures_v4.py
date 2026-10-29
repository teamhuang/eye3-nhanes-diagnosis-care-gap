import os
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"):
    os.environ[v]="1"
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd, numpy as np
from pathlib import Path
plt.rcParams.update({"font.family":"sans-serif","font.sans-serif":["Arial","DejaVu Sans"],
    "font.size":9,"axes.linewidth":0.8,"axes.spines.top":False,"axes.spines.right":False,
    "savefig.dpi":300,"figure.dpi":120})
OI={"blue":"#0072B2","orange":"#E69F00","green":"#009E73","verm":"#D55E00","sky":"#56B4E9","gray":"#555555"}
ROOT=Path(__file__).resolve().parents[1]; T=ROOT/"results"/"tables"; F=ROOT/"figures"; F.mkdir(exist_ok=True)
def save(fig,name): fig.savefig(F/(name+".png")); fig.savefig(F/(name+".pdf")); plt.close(fig); print("wrote",name)

gaps=pd.read_csv(T/"t_gaps_v4.csv"); prev=pd.read_csv(T/"t_prevalence_v4.csv")
sev=pd.read_csv(T/"t_severity_unified_v4.csv"); nstd=pd.read_csv(T/"t_nhis_weighted_std_v4.csv")
mn=pd.read_csv(T/"t_modeln_v4.csv"); gcom=pd.read_csv(T/"tA_gcom_v4.csv")
def mnval(sub): return int(pd.read_csv(T/"t_modeln_v4.csv").query("quantity==@sub",engine="python").n.iloc[0]) if False else None
# helper to grab modeln by substring
def m(sub): 
    r=mn[mn.quantity.str.contains(sub,regex=False)]; return int(r.n.iloc[0])

# ---- FIGURE 1: diagnosis + care gaps (responders-only) ----
labels=["DR: no self-reported\ndiagnosis (diabetes + retinopathy)",
        "AMD: no self-reported\ndiagnosis (objective any AMD)",
        "Late AMD: no self-reported\ndiagnosis",
        "Care: no dilated exam\nwithin 12 mo (all diabetes)",
        "Care: no dilated exam\nwithin 12 mo (diabetes + retinopathy)"]
g=gaps.copy()
vals=g.est.values; lo=g.lo.values; hi=g.hi.values
err=np.vstack([vals-lo,hi-vals]); cols=[OI["verm"],OI["verm"],OI["orange"],OI["blue"],OI["blue"]]
fig,ax=plt.subplots(figsize=(6.8,3.8)); y=np.arange(len(vals))[::-1]
ax.barh(y,vals,color=cols,height=0.62,xerr=err,error_kw=dict(ecolor=OI["gray"],lw=1.2,capsize=3))
for yi,v in zip(y,vals): ax.text(v-2.5,yi,f"{v:.1f}%",va="center",ha="right",fontsize=9,fontweight="bold",color="white")
ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=8); ax.set_xlim(0,100)
ax.set_xlabel("Weighted % of U.S. adults aged 40+ (NHANES 2005-2008, self-report responders); bars = 95% CI")
ax.set_title("Diagnosis and care gaps in eye disease",fontweight="bold",loc="left")
ax.grid(axis="x",ls=":",color="#cccccc",lw=0.6); fig.tight_layout(); save(fig,"Fig1_gaps")

# ---- FIGURE 2: objective vs self-reported AMD, annotate age-standardised ----
obj=prev[prev.measure.str.contains("Any AMD")].iloc[0]
crude=nstd[nstd.quantity.str.contains("crude")].iloc[0]; ags=nstd[nstd.quantity.str.contains("standardised")].iloc[0]
xs=[0,1,2]; vals=[obj.est,float(crude.est_pct),float(ags.est_pct)]
err=np.vstack([[vals[0]-obj.lo,vals[1]-float(crude.lo_pct),vals[2]-float(ags.lo_pct)],
               [obj.hi-vals[0],float(crude.hi_pct)-vals[1],float(ags.hi_pct)-vals[2]]])
fig,ax=plt.subplots(figsize=(5.2,3.6))
ax.bar(xs,vals,width=0.62,color=[OI["verm"],OI["sky"],OI["blue"]],yerr=err,error_kw=dict(ecolor=OI["gray"],lw=1.2,capsize=4))
for xi,v,h in zip(xs,vals,[obj.hi,float(crude.hi_pct),float(ags.hi_pct)]): ax.text(xi,h+0.15,f"{v:.2f}%",ha="center",fontsize=9,fontweight="bold",color=OI["gray"])
ax.set_xticks(xs); ax.set_xticklabels(["Objectively graded\nNHANES 2005-08\n(retinal photos)","Self-reported dx\nNHIS 2016\n(weighted crude)","Self-reported dx\nNHIS 2016\n(age-std to NHANES)"],fontsize=7.4)
ax.set_ylabel("Weighted % of U.S. adults aged 40+"); ax.set_ylim(0,max(vals)*1.35)
ax.set_title("AMD: objectively graded vs self-reported\n(different surveys, years, methods)",fontweight="bold",loc="left",fontsize=9.5)
ax.grid(axis="y",ls=":",color="#cccccc",lw=0.6); fig.tight_layout(); save(fig,"Fig2_objective_vs_selfreport")

# ---- FIGURE 3: prior-diagnosis % by DR severity (dx% CI = 100 - gap CI) ----
nm=["No DR","Mild\nNPDR","Moderate\nNPDR","Severe /\nPDR"]
dxp=sev.pct_reported_dx.values; dlo=100-sev.hi.values; dhi=100-sev.lo.values; ns=sev.n_responders.values
e=np.vstack([dxp-dlo,dhi-dxp]); xd=np.arange(4)
fig,ax=plt.subplots(figsize=(5.6,3.7))
ax.bar(xd,dxp,width=0.62,color=[OI["sky"],OI["blue"],OI["orange"],OI["verm"]],yerr=e,error_kw=dict(ecolor=OI["gray"],lw=1.1,capsize=3))
for xi,p,n in zip(xd,dxp,ns): ax.text(xi,dhi[xi]+2,f"{p:.0f}%",ha="center",fontsize=9,fontweight="bold",color=OI["gray"])
ax.set_xticks(xd); ax.set_xticklabels([f"{a}\nn={b}" for a,b in zip(nm,ns)],fontsize=8)
ax.set_ylabel("Weighted % previously told they had\ndiabetic eye disease"); ax.set_ylim(0,108)
ax.set_xlabel("Graded retinopathy severity, worse eye (adults with diabetes who answered the item); bars = 95% CI")
ax.set_title("Prior diagnosis rises with severity but stays partial",fontweight="bold",loc="left",fontsize=9.5)
ax.grid(axis="y",ls=":",color="#cccccc",lw=0.6); fig.tight_layout(); save(fig,"Fig3_DR_severity_vs_dx")

# ---- FIGURE S2: adjusted predicted probability of NO reported dx by eye-care (g-computation) ----
g0=float(gcom[gcom.quantity.str.contains("exam=0")].est.iloc[0])*100
g1=float(gcom[gcom.quantity.str.contains("exam=1")].est.iloc[0])*100
fig,ax=plt.subplots(figsize=(4.2,3.6))
ax.bar([0,1],[g0,g1],width=0.55,color=[OI["verm"],OI["green"]])
for xi,v in zip([0,1],[g0,g1]): ax.text(xi,v+1.5,f"{v:.1f}%",ha="center",fontsize=9,fontweight="bold",color=OI["gray"])
ax.set_xticks([0,1]); ax.set_xticklabels(["No dilated exam\nwithin 12 months","Dilated exam\nwithin 12 months"],fontsize=8)
ax.set_ylabel("Adjusted predicted % with\nNO reported diabetic-eye dx"); ax.set_ylim(0,100)
ax.set_title("Model-adjusted (g-computation) risk,\nDR cohort; descriptive point estimates",fontweight="bold",loc="left",fontsize=9)
ax.grid(axis="y",ls=":",color="#cccccc",lw=0.6); fig.tight_layout(); save(fig,"FigS2_eyecare_predicted")

# ---- FIGURE S1: study flowchart (corrected denominators) ----
examined=6797; grad_dr=5704; grad_amd=5604; dm_grad=884; retin_dm=319
dr_den=313; amd_obj=441; amd_den=436; dr_model=m("CORE complete-case"); amd_model=m("AMD CORE")
fig,ax=plt.subplots(figsize=(5.8,5.4)); ax.axis("off"); ax.set_xlim(0,1); ax.set_ylim(0,1)
def box(x,y,w,h,txt,fc): ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.012",fc=fc,ec=OI["gray"],lw=0.8)); ax.text(x+w/2,y+h/2,txt,ha="center",va="center",fontsize=7.3)
def arrow(y1,y2,x=0.5): ax.annotate("",xy=(x,y2),xytext=(x,y1),arrowprops=dict(arrowstyle="-|>",color=OI["gray"],lw=1))
box(0.15,0.88,0.7,0.09,f"Examined NHANES adults >=40 (2005-2008)  n = {examined:,}",OI["sky"]); arrow(0.88,0.80)
box(0.05,0.70,0.42,0.09,f"Gradable retinal photo (DR)  n = {grad_dr:,}",'#eef6fb')
box(0.53,0.70,0.42,0.09,f"Gradable retinal photo (AMD)  n = {grad_amd:,}",'#eef6fb'); arrow(0.70,0.62,x=0.26); arrow(0.70,0.62,x=0.74)
box(0.05,0.52,0.42,0.10,f"Diabetes AND objective retinopathy  n = {retin_dm:,}\n(of {dm_grad:,} gradable with diabetes)",'#fdeee6')
box(0.53,0.52,0.42,0.10,f"Objective any-AMD  n = {amd_obj:,}",'#fdeee6'); arrow(0.52,0.44,x=0.26); arrow(0.52,0.44,x=0.74)
box(0.05,0.34,0.42,0.10,f"DR gap denominator\n(diabetic-eye item answered)  n = {dr_den:,}",'#fdf3d8')
box(0.53,0.34,0.42,0.10,f"AMD gap denominator\n(AMD item answered)  n = {amd_den:,}",'#fdf3d8'); arrow(0.34,0.26,x=0.26); arrow(0.34,0.26,x=0.74)
box(0.05,0.15,0.42,0.11,f"DR multivariable model\n(complete covariates)  n = {dr_model:,}\n(excluded {dr_den-dr_model} missing educ/income)",OI["green"])
box(0.53,0.15,0.42,0.11,f"AMD multivariable model\n(complete covariates)  n = {amd_model:,}\n(excluded {amd_den-amd_model} missing educ/income)",OI["green"])
ax.text(0.5,0.06,"Attrition driven by missing education/income, not the outcome; excluded vs entrants similar on the outcome (Table S1).\nResponders-only: {0} DR / {1} AMD non-responders excluded from gap denominators.".format(retin_dm-dr_den,amd_obj-amd_den),ha="center",fontsize=6.4,color=OI["gray"])
ax.set_title("Figure S1. Study flow (NHANES 2005-2008)",fontweight="bold",loc="left")
fig.tight_layout(); save(fig,"FigS1_flowchart")
print("\nFig2 AMD bars:",vals,"; S2 predicted:",g0,g1)
