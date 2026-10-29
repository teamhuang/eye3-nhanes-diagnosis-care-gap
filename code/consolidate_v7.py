#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""consolidate_v7.py — extend numbers_v6.csv with the round-8 (v7) keys into numbers_v7.csv.
Every v7 value is read from the survey_analysis_v7.R output tables; nothing is hand-entered.
The per-model audit table is the single source of truth for design df / residual df / rank /
coef / SE / aOR / CI / raw P / Holm P, so the manuscript can never drift from the model objects."""
import os, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[v]="1"
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; T=ROOT/"results"/"tables"
def rd(n):
    with open(T/n,encoding="utf-8-sig") as f: return list(csv.DictReader(f))
def f(x): return float(x)
def disp(r): return f"{r['aOR_disp']} ({r['lo_disp']}\u2013{r['hi_disp']})"  # single-rounded from full precision
out=[]
def add(k,v): out.append((k,v))
# carry every v6 key verbatim
with open(T/"numbers_v6.csv",encoding="utf-8") as fh:
    for row in csv.reader(fh):
        if row and row[0]!="key": add(row[0], row[1] if len(row)>1 else "")

# 19 per-model audit table (design df / residual df / rank / CI multiplier / term-level estimates)
aud=rd("t_model_audit_v7.csv")
seen={}
for r in aud:
    m=r["model"]
    if m not in seen:
        seen[m]=(int(r["design_df"]),int(r["rank"]),int(r["residual_df"]),float(r["ci_multiplier"]),int(r["n"]))
    add(f"audit|{m}|{r['term']}", f"aOR {disp(r)}; coef {f(r['coef']):.4f} SE {f(r['SE']):.4f}; p {f(r['p_raw']):.3g}; Holm p {f(r['p_holm']):.3g}")
for m,(dd,rk,rd_,tc,n) in seen.items():
    add(f"audit_df|{m}", f"design_df={dd}; rank={rk}; residual_df={rd_}; CI multiplier t(0.975,{rd_})={tc:.4f}; n={n}")

# 20 IPW weight decomposition
for r in rd("t_ipw_decomp_v7.csv"):
    add(f"ipwdec|{r['model']}|prob", f"gradability prob min {f(r['prob_min']):.3f} / median {f(r['prob_median']):.3f} / max {f(r['prob_max']):.3f}; n floored at 0.05 = {r['n_floored']}")
    add(f"ipwdec|{r['model']}|invfactor", f"1/P factor min {f(r['invfactor_min']):.2f} / median {f(r['invfactor_median']):.2f} / max {f(r['invfactor_max']):.2f}")
    add(f"ipwdec|{r['model']}|combwt", f"combined survey\u00d7IPW weight median {int(f(r['combwt_median'])):,} / max {int(f(r['combwt_max'])):,}")
    add(f"ipwdec|{r['model']}|ess", f"Kish ESS (combined) {int(f(r['ess_kish'])):,}; raw-ESS {int(f(r['raw_ess'])):,}; gradable rows={r['n_gradable']}; model complete-case n={r['model_n']}")

# 21 AMD age gradient adjusted for severity + early-AMD-only age strata
for r in rd("t_amd_age_sev_v7.csv"):
    add(f"amdagesev|{r['term']}", f"aOR {disp(r)}; p {f(r['p_raw']):.3g}; Holm p {f(r['p_holm']):.3g}")
add("amdagesev|df", f"design_df={rd('t_amd_age_sev_v7.csv')[0]['design_df']}; rank={rd('t_amd_age_sev_v7.csv')[0]['rank']}; residual_df={rd('t_amd_age_sev_v7.csv')[0]['residual_df']}; n={rd('t_amd_age_sev_v7.csv')[0]['n']}")
for r in rd("t_earlyamd_age_v7.csv"):
    add(f"earlyamdpstrata|{r['stratum']}", f"{f(r['est']):.1f} ({f(r['lo']):.1f}\u2013{f(r['hi']):.1f}) [n={r['n']}]")

# 22 late-AMD phenotype overlap (worse-eye mutual exclusivity)
ov=rd("t_phenotype_overlap_v7.csv")[0]
add("pheno|overlap", f"GA n={ov['geographic_atrophy_n']}; neovascular n={ov['neovascular_n']}; both same worse eye n={ov['both_worse_eye_n']}; late AMD n={ov['late_amd_n']}")

with open(T/"numbers_v7.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["key","value"]); [w.writerow(k) for k in out]
print(f"numbers_v7.csv written: {len(out)} keys")
for k,v in out:
    if k.startswith(("audit_df","audit|ANALYSIS A","ipwdec|extended|ess","amdagesev|","pheno|overlap")):
        print(" ",k,"=",v)
