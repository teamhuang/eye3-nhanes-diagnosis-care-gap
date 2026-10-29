#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""consolidate_v5.py — merge the v4 core numbers with the v5 construct-validity
extensions into a single deterministic numbers_v5.csv, and recompute the
reviewer-required analytic denominators straight from the raw analytic dataset
so every downstream assertion has a data-backed source."""
import os, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[v]="1"
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; T=ROOT/"results"/"tables"
def rd(n):
    with open(T/n,encoding="utf-8-sig") as f: return list(csv.DictReader(f))
def f(x): return float(x)
def p1(x): return f"{f(x):.1f}"
def c1(est,lo,hi): return f"{f(est):.1f} ({f(lo):.1f}\u2013{f(hi):.1f})"
def aorp(row,dec=2):
    return f"aOR {f(row['aOR']):.{dec}f} ({f(row['lo']):.{dec}f}\u2013{f(row['hi']):.{dec}f}) p {f(row['p']):.3g} [n={row['n']}]"

out=[]
def add(k,v): out.append((k,v))

# ---- carry forward every v4 key verbatim ----
with open(T/"numbers_v4.csv",encoding="utf-8") as fh:
    for row in csv.reader(fh):
        if row and row[0]!="key": add(row[0], row[1] if len(row)>1 else "")

# ---- S7a: AMD severity tiers (early / late / GA / NV) ----
for r in rd("t_amd_severity_v5.csv"):
    add("amdsev|"+r["tier"], c1(r["est"],r["lo"],r["hi"])+f" [n={r['n']}]")

# ---- S7b: non-response extreme-scenario bounds ----
nr=rd("t_nonresponse_bounds_v5.csv")
for r in nr:
    tag="DR" if r["cohort"].startswith("DR") else "AMD"
    add(f"nrb|{tag}|responders_only", r["responders_only"])
    add(f"nrb|{tag}|all_diagnosed", r["all_nonresponder_diagnosed"])
    add(f"nrb|{tag}|all_undiagnosed", r["all_nonresponder_undiagnosed"])

# ---- S4b: reduced models (drop high-missing covariates) ----
for r in rd("t_reduced_models_v5.csv"):
    add("red|"+r["model"]+"|"+r["term"], aorp(r))

# ---- S4c: multiple imputation (Rubin-pooled, m=20) ----
for r in rd("t_mi_v5.csv"):
    add("mi|"+r["term"], aorp(r))

# ---- S8a: gradable vs ungradable comparison ----
g=rd("t_gradability_v5.csv")
for r in g:
    grp=r.get("","") or r.get("group","")
    add("grad|"+grp, f"n={int(f(r['n']))}, mean age {f(r['age']):.1f}, male {f(r['male']):.1f}%, diabetes {f(r['dm']):.1f}%, non-White {f(r['nonwhite']):.1f}%, insured {f(r['insured']):.1f}%, <HS {f(r['educ_lt_hs']):.1f}%")

# ---- S8b: IPW for gradability selection ----
for r in rd("t_ipw_prevalence_v5.csv"):
    add("ipw|"+r["measure"], f"naive {f(r['naive_pct']):.2f} \u2192 IPW {f(r['ipw_gradability_pct']):.2f}")

# ---- design degrees of freedom per subset ----
for r in rd("t_design_df_v5.csv"):
    add("ddf|"+r["subset"], f"n={r['n']}, strata={r['strata']}, PSU={r['psu']}, df(Taylor)={r['df_taylor']}")

# ---- S5b: NHIS standardisation versions (design covariance) ----
for r in rd("t_nhis_std_versions_v5.csv"):
    q=r["quantity"]; add("nhisver|"+q, f"{f(r['est_pct']):.2f} ({f(r['lo_pct']):.2f}\u2013{f(r['hi_pct']):.2f})")

# ---- S5b band detail (rates, responder weighted N, std weight) ----
for r in rd("t_nhis_std_cov_v5.csv"):
    add("nhisband5|"+r["band"], f"rate {f(r['rate_pct']):.2f}% (weighted N {int(f(r['responder_weighted_N'])):,}; std weight {f(r['std_weight']):.4f})")

# ---- deterministic denominators recomputed from raw analytic dataset (assertion source) ----
with open(ROOT/"data"/"processed"/"analytic_dataset_v2.csv",encoding="utf-8-sig") as fh:
    D=list(csv.DictReader(fh))
def g(row,k):
    v=row.get(k,"")
    if v in ("","NA","NaN"): return None
    try: return float(v)
    except: return v
def notna(v): return v is not None and v!="NA" and v!=""
dr_grad=dr_resp=dr_core=0; amd_grad=amd_resp=amd_core=0
mild=mod=sev=ga=nv=late=0
for row in D:
    dm=g(row,"dm_dx"); odra=g(row,"obj_dr_any"); odama=g(row,"obj_amd_any")
    dxdr=g(row,"dx_dr"); dxamd=g(row,"dx_amd"); l4=g(row,"OPDURL4")
    educ=g(row,"educ"); pir=g(row,"pir"); ga1=g(row,"OPDUGA"); ex=g(row,"OPDUEXU"); oamd=g(row,"OPDUARM")
    if dm==1 and odra==1:
        dr_grad+=1
        if notna(dxdr):
            dr_resp+=1
            if notna(educ) and int(educ) in (1,2,3) and notna(pir): dr_core+=1
            if l4==2: mild+=1
            elif l4==3: mod+=1
            elif l4==4: sev+=1
    if odama==1:
        amd_grad+=1
        if notna(dxamd):
            amd_resp+=1
            if notna(educ) and int(educ) in (1,2,3) and notna(pir): amd_core+=1
    if oamd==2:
        late+=1
        if ga1==1: ga+=1
        if ex==1: nv+=1
add("CNT|dr_gradable_disease", str(dr_grad))
add("CNT|dr_gap_responders", str(dr_resp))
add("CNT|dr_core_complete_cases", str(dr_core))
add("CNT|amd_gradable_disease", str(amd_grad))
add("CNT|amd_gap_responders", str(amd_resp))
add("CNT|amd_core_complete_cases", str(amd_core))
add("CNT|mild_dr_responders", str(mild))
add("CNT|moderate_dr_responders", str(mod))
add("CNT|severe_dr_responders", str(sev))
add("CNT|geographic_atrophy_n", str(ga))
add("CNT|neovascular_amd_n", str(nv))
add("CNT|late_amd_n", str(late))

with open(T/"numbers_v5.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["key","value"]); [w.writerow(k) for k in out]
print(f"numbers_v5.csv written: {len(out)} keys")
print("CNT denominators:", {k:v for k,v in out if k.startswith("CNT|")})
