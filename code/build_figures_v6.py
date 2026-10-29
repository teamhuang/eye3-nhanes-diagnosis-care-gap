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
sev=pd.read_csv(T/"t_severity_unified_v4.csv"); mn=pd.read_csv(T/"t_modeln_v4.csv"); gcom=pd.read_csv(T/"tA_gcom_v4.csv")
nstdv=pd.read_csv(T/"t_nhis_std_versions_v5.csv")
amdsev=pd.read_csv(T/"t_amd_severity_v5.csv"); modw=pd.read_csv(T/"t_modworse_gap_v6.csv")
def m(sub):
    r=mn[mn.quantity.str.contains(sub,regex=False)]; return int(r.n.iloc[0])

# ---- FIGURE 1: diagnosis + care gaps (unchanged) ----
labels=["DR: no self-reported\ndiagnosis (diabetes + retinopathy)",
        "AMD: no self-reported\ndiagnosis (objective any AMD)",
        "Late AMD: no self-reported\ndiagnosis",
        "Care: no dilated exam\nwithin 12 mo (all diabetes)",
        "Care: no dilated exam\nwithin 12 mo (diabetes + retinopathy)"]
vals=gaps.est.values; lo=gaps.lo.values; hi=gaps.hi.values
err=np.vstack([vals-lo,hi-vals]); cols=[OI["verm"],OI["verm"],OI["orange"],OI["blue"],OI["blue"]]
fig,ax=plt.subplots(figsize=(6.8,3.8)); y=np.arange(len(vals))[::-1]
ax.barh(y,vals,color=cols,height=0.62,xerr=err,error_kw=dict(ecolor=OI["gray"],lw=1.2,capsize=3))
for yi,v in zip(y,vals): ax.text(v-2.5,yi,f"{v:.1f}%",va="center",ha="right",fontsize=9,fontweight="bold",color="white")
ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=8); ax.set_xlim(0,100)
ax.set_xlabel("Weighted % of U.S. adults aged 40+ (NHANES 2005-2008, self-report responders); bars = 95% CI")
ax.set_title("Diagnosis and care gaps in eye disease",fontweight="bold",loc="left")
ax.grid(axis="x",ls=":",color="#cccccc",lw=0.6); fig.tight_layout(); save(fig,"Fig1_gaps")

# ---- FIGURE 2 (NEW): severity gradient of the diagnosis gap, faceted by disease ----
fig,(axl,axr)=plt.subplots(1,2,figsize=(7.6,3.9))
# Left: DR severity (tiers 2/3/4) + moderate-or-worse combined
d=sev[sev.OPDURL4.isin([2,3,4])].sort_values("OPDURL4")
dr_lab=["Mild\nNPDR","Moderate\nNPDR","Severe /\nPDR"]
dr_v=d.gap_pct_undiagnosed.values; dr_lo=d.lo.values; dr_hi=d.hi.values; dr_n=d.n_responders.values
mv=modw.iloc[0]; mv_v=float(mv.est); mv_lo=float(mv.lo); mv_hi=float(mv.hi); mv_n=int(mv.n)
xd=np.arange(len(dr_lab)+1)
barv=list(dr_v)+[mv_v]; blo=list(dr_lo)+[mv_lo]; bhi=list(dr_hi)+[mv_hi]; bn=list(dr_n)+[mv_n]
colr=[OI["sky"],OI["blue"],OI["verm"]]+[OI["orange"]]
e=np.vstack([np.array(barv)-np.array(blo),np.array(bhi)-np.array(barv)])
axl.bar(xd,barv,width=0.62,color=colr,yerr=e,error_kw=dict(ecolor=OI["gray"],lw=1.1,capsize=3))
for xi,v,h,n in zip(xd,barv,bhi,bn): axl.text(xi,h+2,f"{v:.0f}%",ha="center",fontsize=8.5,fontweight="bold",color=OI["gray"])
axl.set_xticks(xd); axl.set_xticklabels([f"{a}\nn={b}" for a,b in zip(dr_lab+["Moderate-\nor-worse"],bn)],fontsize=7.6)
axl.set_ylim(0,100); axl.set_ylabel("% with NO self-reported\ndiabetic-eye diagnosis")
axl.set_title("Retinopathy severity\n(adults with diabetes)",loc="left",fontweight="bold",fontsize=9.5)
axl.grid(axis="y",ls=":",color="#cccccc",lw=0.6)
# Right: AMD stage + late phenotypes
amap={"Early AMD":0,"Late AMD":1,"Geographic atrophy":2,"Neovascular/exudative":3}
order=["Early AMD","Late AMD","Geographic atrophy","Neovascular/exudative"]
alab=["Early\nAMD","Late\nAMD","Geographic\natrophy","Neo-\nvascular"]
a_v=[float(amdsev[amdsev.tier==t].est.iloc[0]) for t in order]
a_lo=[float(amdsev[amdsev.tier==t].lo.iloc[0]) for t in order]
a_hi=[float(amdsev[amdsev.tier==t].hi.iloc[0]) for t in order]
a_n=[int(amdsev[amdsev.tier==t].n.iloc[0]) for t in order]
colr2=[OI["orange"],OI["verm"],OI["blue"],OI["sky"]]
e2=np.vstack([np.array(a_v)-np.array(a_lo),np.array(a_hi)-np.array(a_v)])
xr=np.arange(4)
axr.bar(xr,a_v,width=0.62,color=colr2,yerr=e2,error_kw=dict(ecolor=OI["gray"],lw=1.1,capsize=3))
for xi,v,h,n in zip(xr,a_v,a_hi,a_n): axr.text(xi,h+2,f"{v:.0f}%",ha="center",fontsize=8.5,fontweight="bold",color=OI["gray"])
axr.set_xticks(xr); axr.set_xticklabels([f"{a}\nn={b}" for a,b in zip(alab,a_n)],fontsize=7.6)
axr.set_ylim(0,100); axr.set_ylabel("% with NO self-reported\nmacular-degeneration diagnosis")
axr.set_title("AMD stage / phenotype",loc="left",fontweight="bold",fontsize=9.5)
axr.grid(axis="y",ls=":",color="#cccccc",lw=0.6)
fig.suptitle("Figure 2. Diagnosis-gap gradient by disease severity (NHANES 2005-2008)",fontweight="bold",x=0.02,ha="left",y=0.99)
fig.text(0.5,-0.02,"Design-weighted % with no self-reported diagnosis, 95% CI (logit); unweighted responder n below each bar.\nFacets are separate diseases on separate severity scales \u2014 not a within-figure causal comparison.",ha="center",fontsize=6.8,color=OI["gray"])
fig.tight_layout(rect=[0,0.05,1,0.95]); save(fig,"Fig2_severity_gradient")

# ---- FIGURE 3: objective vs self-reported AMD (was Fig2) ----
obj=prev[prev.measure.str.contains("Any AMD")].iloc[0]
crude=nstdv[nstdv.quantity.str.contains("crude")].iloc[0]
ags=nstdv[nstdv.quantity.str.contains("age-standardised") & (~nstdv.quantity.str.contains("and-sex"))].iloc[0]
xs=[0,1,2]; vals=[obj.est,float(crude.est_pct),float(ags.est_pct)]
err=np.vstack([[vals[0]-obj.lo,vals[1]-float(crude.lo_pct),vals[2]-float(ags.lo_pct)],
               [obj.hi-vals[0],float(crude.hi_pct)-vals[1],float(ags.hi_pct)-vals[2]]])
fig,ax=plt.subplots(figsize=(5.2,3.6))
ax.bar(xs,vals,width=0.62,color=[OI["verm"],OI["sky"],OI["blue"]],yerr=err,error_kw=dict(ecolor=OI["gray"],lw=1.2,capsize=4))
for xi,v,h in zip(xs,vals,[obj.hi,float(crude.hi_pct),float(ags.hi_pct)]): ax.text(xi,h+0.15,f"{v:.2f}%",ha="center",fontsize=9,fontweight="bold",color=OI["gray"])
ax.set_xticks(xs); ax.set_xticklabels(["Objectively graded\nNHANES 2005-08\n(retinal photos)","Self-reported dx\nNHIS 2016\n(weighted crude)","Self-reported dx\nNHIS 2016\n(age-std, design cov.)"],fontsize=7.4)
ax.set_ylabel("Weighted % of U.S. adults aged 40+"); ax.set_ylim(0,max(vals)*1.35)
ax.set_title("AMD: objectively graded vs self-reported\n(different surveys, years, methods)",fontweight="bold",loc="left",fontsize=9.5)
ax.grid(axis="y",ls=":",color="#cccccc",lw=0.6); fig.tight_layout(); save(fig,"Fig3_objective_vs_selfreport")

# ---- FIGURE S2: g-computation (unchanged) ----
g0=float(gcom[gcom.quantity.str.contains("exam=0")].est.iloc[0])*100
g1=float(gcom[gcom.quantity.str.contains("exam=1")].est.iloc[0])*100
fig,ax=plt.subplots(figsize=(4.2,3.6))
ax.bar([0,1],[g0,g1],width=0.55,color=[OI["verm"],OI["green"]])
for xi,v in zip([0,1],[g0,g1]): ax.text(xi,v+1.5,f"{v:.1f}%",ha="center",fontsize=9,fontweight="bold",color=OI["gray"])
ax.set_xticks([0,1]); ax.set_xticklabels(["No dilated exam\nwithin 12 months","Dilated exam\nwithin 12 months"],fontsize=8)
ax.set_ylabel("Adjusted predicted % with\nNO reported diabetic-eye dx"); ax.set_ylim(0,100)
ax.set_title("Model-adjusted (g-computation) risk,\nDR cohort; descriptive point estimates",fontweight="bold",loc="left",fontsize=9)
ax.grid(axis="y",ls=":",color="#cccccc",lw=0.6); fig.tight_layout(); save(fig,"FigS2_eyecare_predicted")

# ---- FIGURE S1: study flowchart (unchanged) ----
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
ax.text(0.5,0.06,"Attrition driven by missing education/income, not the outcome.\nResponders-only: {0} DR / {1} AMD non-responders excluded from gap denominators.".format(retin_dm-dr_den,amd_obj-amd_den),ha="center",fontsize=6.4,color=OI["gray"])
ax.set_title("Figure S1. Study flow (NHANES 2005-2008)",fontweight="bold",loc="left")
fig.tight_layout(); save(fig,"FigS1_flowchart")
print("\nFig2 DR gaps:",barv,"; AMD gaps:",a_v,"; Fig3 bars:",vals)
