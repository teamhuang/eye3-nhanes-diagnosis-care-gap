"""Round-11 figure beautification: Nature-journal style, strict size rules.

Rules applied:
  Height  = 5 cm
  Width   = 5 cm (single-panel) or 6.5 cm (multi-panel or wide)
  No note text ON the figure (no title, no footnote, no "Figure N." label inside image).
  Titles and legends live in the Word caption, not on the plot.
  Arial; thin 0.6 pt spine, top/right removed, ticks inward; no gridlines.
  Colour-blind-safe Okabe-Ito palette retained.
  600 dpi PNG + vector PDF output.

Visual-check pass 2 (this revision) fixes:
  Fig1: shorten x-axis label; darker text on light-orange bar for readability.
  Fig2: bigger left margin so ylabel fits; smaller x-tick labels; panel labels
        moved to top-left corner; ylim raised to 110 so 88% bar has headroom.
  Fig3: shorter x-tick labels; more space between bars.
  FigS1: bottom-row boxes widened slightly; smaller font so n=187/226 fits.
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
    "font.family":"sans-serif",
    "font.sans-serif":["Arial","DejaVu Sans"],
    "font.size":7,
    "axes.linewidth":0.6,
    "axes.spines.top":False,
    "axes.spines.right":False,
    "axes.titlesize":7.5,
    "axes.labelsize":6.8,
    "xtick.labelsize":6.0,
    "ytick.labelsize":6.2,
    "xtick.major.width":0.5,
    "ytick.major.width":0.5,
    "xtick.major.size":2.2,
    "ytick.major.size":2.2,
    "xtick.direction":"in",
    "ytick.direction":"in",
    "legend.fontsize":6.2,
    "legend.frameon":False,
    "savefig.dpi":600,
    "figure.dpi":300,
    "savefig.bbox":None,
})

OI = {"blue":"#0072B2","orange":"#E69F00","green":"#009E73",
      "verm":"#D55E00","sky":"#56B4E9","gray":"#555555"}
ROOT = Path(__file__).resolve().parents[1]
T = ROOT/"results"/"tables"
F = ROOT/"figures"; F.mkdir(exist_ok=True)

def save(fig, name):
    fig.savefig(F/(name+".png"))
    fig.savefig(F/(name+".pdf"))
    plt.close(fig)
    print("wrote", name)

gaps = pd.read_csv(T/"t_gaps_v4.csv")
prev = pd.read_csv(T/"t_prevalence_v4.csv")
sev  = pd.read_csv(T/"t_severity_unified_v4.csv")
mn   = pd.read_csv(T/"t_modeln_v4.csv")
gcom = pd.read_csv(T/"tA_gcom_v4.csv")
nstdv= pd.read_csv(T/"t_nhis_std_versions_v5.csv")
amdsev=pd.read_csv(T/"t_amd_severity_v5.csv")
modw  = pd.read_csv(T/"t_modworse_gap_v6.csv")

def modeln(sub):
    r = mn[mn.quantity.str.contains(sub, regex=False)]
    return int(r.n.iloc[0])

# ==========================================================
# FIGURE 1: 6.5 x 5 cm, horizontal bars, no title
# ==========================================================
labels = ["DR diagnosis gap", "AMD diagnosis gap", "Late AMD gap",
          "Care gap: all DM", "Care gap: DM+ret"]
vals = gaps.est.values
lo   = gaps.lo.values
hi   = gaps.hi.values
err  = np.vstack([vals-lo, hi-vals])
cols = [OI["verm"], OI["verm"], OI["orange"], OI["blue"], OI["blue"]]

fig, ax = plt.subplots(figsize=(6.5*CM, 5*CM))
ypos = np.arange(len(vals))[::-1]
ax.barh(ypos, vals, color=cols, height=0.62,
        xerr=err, error_kw=dict(ecolor=OI["gray"], lw=0.8, capsize=2.5, capthick=0.6))
for yi, v, h, c in zip(ypos, vals, hi, cols):
    if c == OI["orange"]:
        # light-orange bar: put label to the right of the CI upper bound, dark text
        ax.text(h+2, yi, f"{v:.1f}%", va="center", ha="left",
                fontsize=6.5, color=OI["gray"], fontweight="bold")
    else:
        # dark bars (verm, blue): white label inside the bar
        ax.text(v-2.0, yi, f"{v:.1f}%", va="center", ha="right",
                fontsize=6.5, color="white", fontweight="bold")
ax.set_yticks(ypos)
ax.set_yticklabels(labels, fontsize=6.2)
ax.set_xlim(0, 100)
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("Weighted % (US adults \u2265 40)", fontsize=6.8, labelpad=2)
ax.tick_params(axis="y", length=0)
fig.subplots_adjust(left=0.36, right=0.98, top=0.98, bottom=0.16)
save(fig, "Fig1_gaps")

# ==========================================================
# FIGURE 2: two-panel 6.5 x 5 cm, panel labels (a)/(b)
# ==========================================================
fig, (axl, axr) = plt.subplots(1, 2, figsize=(6.5*CM, 5*CM))

d = sev[sev.OPDURL4.isin([2,3,4])].sort_values("OPDURL4")
dr_lab = ["Mild", "Mod", "Sev", "Mod+"]
dr_v   = list(d.gap_pct_undiagnosed.values)
dr_lo  = list(d.lo.values); dr_hi = list(d.hi.values)
dr_n   = list(d.n_responders.values)
mv = modw.iloc[0]
dr_v  += [float(mv.est)]
dr_lo += [float(mv.lo)]; dr_hi += [float(mv.hi)]; dr_n += [int(mv.n)]
colr_l = [OI["sky"], OI["blue"], OI["verm"], OI["orange"]]
e_l = np.vstack([np.array(dr_v)-np.array(dr_lo), np.array(dr_hi)-np.array(dr_v)])
x_l = np.arange(4)
axl.bar(x_l, dr_v, width=0.62, color=colr_l, yerr=e_l,
        error_kw=dict(ecolor=OI["gray"], lw=0.7, capsize=2.2, capthick=0.5))
for xi, v, h in zip(x_l, dr_v, dr_hi):
    axl.text(xi, h+4, f"{v:.0f}%", ha="center", fontsize=5.8, color=OI["gray"], fontweight="bold")
axl.set_xticks(x_l)
axl.set_xticklabels([f"{a}\nn={b}" for a, b in zip(dr_lab, dr_n)], fontsize=5.2)
axl.set_ylim(0, 110)
axl.set_yticks([0, 25, 50, 75, 100])
axl.set_ylabel("% no self-reported dx", fontsize=6.5, labelpad=2)
axl.text(-0.22, 1.05, "a", transform=axl.transAxes,
         fontsize=8, fontweight="bold", va="top", ha="left")

order = ["Early AMD","Late AMD","Geographic atrophy","Neovascular/exudative"]
alab  = ["Early", "Late", "GA", "NV"]
a_v  = [float(amdsev[amdsev.tier==t].est.iloc[0]) for t in order]
a_lo = [float(amdsev[amdsev.tier==t].lo.iloc[0]) for t in order]
a_hi = [float(amdsev[amdsev.tier==t].hi.iloc[0]) for t in order]
a_n  = [int(amdsev[amdsev.tier==t].n.iloc[0]) for t in order]
colr_r = [OI["orange"], OI["verm"], OI["blue"], OI["sky"]]
e_r = np.vstack([np.array(a_v)-np.array(a_lo), np.array(a_hi)-np.array(a_v)])
x_r = np.arange(4)
axr.bar(x_r, a_v, width=0.62, color=colr_r, yerr=e_r,
        error_kw=dict(ecolor=OI["gray"], lw=0.7, capsize=2.2, capthick=0.5))
for xi, v, h in zip(x_r, a_v, a_hi):
    axr.text(xi, h+4, f"{v:.0f}%", ha="center", fontsize=5.8, color=OI["gray"], fontweight="bold")
axr.set_xticks(x_r)
axr.set_xticklabels([f"{a}\nn={b}" for a, b in zip(alab, a_n)], fontsize=5.2)
axr.set_ylim(0, 110)
axr.set_yticks([0, 25, 50, 75, 100])
axr.text(-0.16, 1.05, "b", transform=axr.transAxes,
         fontsize=8, fontweight="bold", va="top", ha="left")

fig.subplots_adjust(wspace=0.85, left=0.16, right=0.99, top=0.92, bottom=0.18)
save(fig, "Fig2_severity_gradient")

# ==========================================================
# FIGURE 3: 5 x 5 cm, three bars
# ==========================================================
obj  = prev[prev.measure.str.contains("Any AMD")].iloc[0]
crude= nstdv[nstdv.quantity.str.contains("crude")].iloc[0]
ags  = nstdv[nstdv.quantity.str.contains("age-standardised") &
              (~nstdv.quantity.str.contains("and-sex"))].iloc[0]
xs   = [0, 1, 2]
vals3= [obj.est, float(crude.est_pct), float(ags.est_pct)]
err3 = np.vstack([[vals3[0]-obj.lo, vals3[1]-float(crude.lo_pct), vals3[2]-float(ags.lo_pct)],
                  [obj.hi-vals3[0], float(crude.hi_pct)-vals3[1], float(ags.hi_pct)-vals3[2]]])
fig, ax = plt.subplots(figsize=(5*CM, 5*CM))
ax.bar(xs, vals3, width=0.55, color=[OI["verm"], OI["sky"], OI["blue"]], yerr=err3,
       error_kw=dict(ecolor=OI["gray"], lw=0.8, capsize=2.5, capthick=0.6))
for xi, v, h in zip(xs, vals3, [obj.hi, float(crude.hi_pct), float(ags.hi_pct)]):
    ax.text(xi, h+0.25, f"{v:.2f}%", ha="center", fontsize=6.2, color=OI["gray"], fontweight="bold")
ax.set_xticks(xs)
ax.set_xticklabels(["NHANES\ngraded\n2005\u201308",
                    "NHIS\nself-report\ncrude",
                    "NHIS\nself-report\nage-std."], fontsize=5.8)
ax.set_xlim(-0.6, 2.6)
ax.set_ylabel("Weighted % (US adults \u2265 40)", fontsize=6.5, labelpad=2)
ax.set_ylim(0, max(vals3)*1.30)
fig.subplots_adjust(left=0.16, right=0.98, top=0.98, bottom=0.20)
save(fig, "Fig3_objective_vs_selfreport")

# ==========================================================
# FIGURE S2: 5 x 5 cm, two bars
# ==========================================================
g0 = float(gcom[gcom.quantity.str.contains("exam=0")].est.iloc[0])*100
g1 = float(gcom[gcom.quantity.str.contains("exam=1")].est.iloc[0])*100
fig, ax = plt.subplots(figsize=(5*CM, 5*CM))
ax.bar([0, 1], [g0, g1], width=0.55, color=[OI["verm"], OI["green"]])
for xi, v in zip([0, 1], [g0, g1]):
    ax.text(xi, v+1.5, f"{v:.1f}%", ha="center", fontsize=6.5, color=OI["gray"], fontweight="bold")
ax.set_xticks([0, 1])
ax.set_xticklabels(["No dilated exam\nwithin 12 mo",
                    "Dilated exam\nwithin 12 mo"], fontsize=6.2)
ax.set_xlim(-0.6, 1.6)
ax.set_ylabel("Adjusted predicted % with\nno self-reported dx", fontsize=6.5, labelpad=2)
ax.set_ylim(0, 100)
fig.subplots_adjust(left=0.26, right=0.98, top=0.98, bottom=0.16)
save(fig, "FigS2_eyecare_predicted")

# ==========================================================
# FIGURE S1: flowchart, 6.5 x 5 cm, no title / no footnote
# ==========================================================
examined = 6797; grad_dr = 5704; grad_amd = 5604
dm_grad  = 884;  retin_dm = 319; dr_den = 313
amd_obj  = 441;  amd_den = 436
dr_model = modeln("CORE complete-case"); amd_model = modeln("AMD CORE")

fig, ax = plt.subplots(figsize=(6.5*CM, 5*CM))
ax.axis("off")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)

def box(x, y, w, h, txt, fc, fs=5.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
        boxstyle="round,pad=0.008", fc=fc, ec=OI["gray"], lw=0.6,
        mutation_scale=0.5))
    ax.text(x+w/2, y+h/2, txt, ha="center", va="center", fontsize=fs, color="black")

def arrow(y1, y2, x=0.5):
    ax.annotate("", xy=(x, y2), xytext=(x, y1),
        arrowprops=dict(arrowstyle="-|>", color=OI["gray"], lw=0.7))

box(0.02, 0.86, 0.96, 0.11,
    f"Examined NHANES \u2265 40 (2005\u201308)  n = {examined:,}", OI["sky"], fs=5.8)
arrow(0.86, 0.80)

box(0.02, 0.67, 0.46, 0.11,
    f"Gradable photo (DR)  n = {grad_dr:,}", "#eef6fb", fs=5.5)
box(0.52, 0.67, 0.46, 0.11,
    f"Gradable photo (AMD)  n = {grad_amd:,}", "#eef6fb", fs=5.5)
arrow(0.67, 0.60, x=0.25); arrow(0.67, 0.60, x=0.75)

box(0.02, 0.47, 0.46, 0.12,
    f"DM + retinopathy  n = {retin_dm:,}\n(of {dm_grad:,} gradable with DM)", "#fdeee6", fs=5.2)
box(0.52, 0.47, 0.46, 0.12,
    f"Objective any-AMD  n = {amd_obj:,}", "#fdeee6", fs=5.5)
arrow(0.47, 0.40, x=0.25); arrow(0.47, 0.40, x=0.75)

box(0.02, 0.27, 0.46, 0.12,
    f"DR gap denominator\n(item answered)  n = {dr_den:,}", "#fdf3d8", fs=5.2)
box(0.52, 0.27, 0.46, 0.12,
    f"AMD gap denominator\n(item answered)  n = {amd_den:,}", "#fdf3d8", fs=5.2)
arrow(0.27, 0.20, x=0.25); arrow(0.27, 0.20, x=0.75)

box(0.02, 0.05, 0.46, 0.14,
    f"DR model (complete cov.)\nn = {dr_model:,}\n(\u2212{dr_den-dr_model} missing educ/PIR)", OI["green"], fs=5.0)
box(0.52, 0.05, 0.46, 0.14,
    f"AMD model (complete cov.)\nn = {amd_model:,}\n(\u2212{amd_den-amd_model} missing educ/PIR)", OI["green"], fs=5.0)

fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
save(fig, "FigS1_flowchart")

print("\nFig1 values:", vals)
print("Fig2 (a) DR:", dr_v, "; (b) AMD:", a_v)
print("Fig3:", vals3)
print("FigS2:", g0, g1)
print("FigS1 model n: DR", dr_model, "AMD", amd_model)
