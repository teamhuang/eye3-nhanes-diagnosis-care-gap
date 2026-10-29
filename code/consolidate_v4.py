import os, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[v]="1"
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; T=ROOT/"results"/"tables"
def rd(n): 
    with open(T/n,encoding="utf-8") as f: return list(csv.DictReader(f))
def f(x): return float(x)
def r2(x): return f"{float(x):.2f}"
def r1(x): return f"{float(x):.1f}"
def ci(x,dec=2): 
    return f"{x['est']:.{dec}f} ({x['lo']:.{dec}f}\u2013{x['hi']:.{dec}f})" if 'est' in x else x
def cicol(row,est="est",lo="lo",hi="hi",dec=1):
    return f"{f(row[est]):.{dec}f} ({f(row[lo]):.{dec}f}\u2013{f(row[hi]):.{dec}f})"
def aor(row,dec=2):
    return f"aOR {f(row['aOR']):.{dec}f} ({f(row['lo']):.{dec}f}\u2013{f(row['hi']):.{dec}f}) Holm {f(row['p_holm']):.3g} [n={row['n']}]"
def aorp(row,dec=2):
    return f"aOR {f(row['aOR']):.{dec}f} ({f(row['lo']):.{dec}f}\u2013{f(row['hi']):.{dec}f}) p {f(row['p_raw']):.3g} [n={row['n']}]"

out=[]
def add(k,v): out.append((k,v))

prev=rd("t_prevalence_v4.csv")
for r in prev: add("prev|"+r["measure"], f"{r2(r['est'])} ({r2(r['lo'])}\u2013{r2(r['hi'])}) [n={r['n']}]")
gap=rd("t_gaps_v4.csv")
for r in gap: add("gap|"+r["measure"], f"{r1(r['est'])} ({r1(r['lo'])}\u2013{r1(r['hi'])}) [n={r['n']}]")
sev=rd("t_severity_unified_v4.csv")
for r in sev:
    add(f"sevdx|OPDURL4={r['OPDURL4']}", f"{f(r['pct_reported_dx']):.1f} [n={r['n_responders']}]")
    if r['OPDURL4'] in ("2","3","4"):
        add(f"sevgap|OPDURL4={r['OPDURL4']}", f"{f(r['gap_pct_undiagnosed']):.1f} ({f(r['lo']):.1f}\u2013{f(r['hi']):.1f}) [n={r['n_responders']}]")
ag=rd("t_agestrata_v4.csv")
for r in ag: add("age|"+r["stratum"], f"{f(r['est']):.1f} ({f(r['lo']):.1f}\u2013{f(r['hi']):.1f}) [n={r['n']}]")
sub=rd("t_lateAMD_subtype_v4.csv")
for r in sub: add("lateSub|"+r["subtype"], f"{f(r['est']):.1f} ({f(r['lo']):.1f}\u2013{f(r['hi']):.1f}) [n={r['n']}]")
mn=rd("t_modeln_v4.csv")
for r in mn: add("modeln|"+r["quantity"], r["n"])
ms=rd("t_missingness_v4.csv")
for r in ms: add("miss|"+r["cohort"]+"|"+r["variable"], r["n_missing"])
prim=rd("t_logistic_primary_v4.csv")
for r in prim: add("prim|"+r["model"]+"|"+r["term"], aor(r))
ins=rd("t_logistic_insurance_DR_v4.csv")
for r in ins: add("insDR|"+r["term"], aorp(r))
mi=rd("t_sensitivityC_v4.csv")
for r in mi: add("miC|"+r["term"], aorp(r))
ai=rd("t_insurance_AMD_descriptive_v4.csv")[0]
add("AMDins", f"insured {ai['insured_undiag']}/{ai['insured_n']}; uninsured {ai['uninsured_undiag']}/{ai['uninsured_n']} (known_insured_n={ai['known_insured_n']})")
cr=rd("tA_crude_v4.csv")
for r in cr: add(f"Acrude|exam={r['recent_dilated_exam']}", f"{100*f(r['y_dr']):.1f}% unweighted_n={r['unweighted_n']}")
adj=rd("tA_adjusted_v4.csv")
for r in adj: add("Aadj|"+r["term"], aor(r))
gc=rd("tA_gcom_v4.csv")
for r in gc: add("Agcom|"+r["quantity"], (f"{100*f(r['est']):.1f}%" if 'RD' not in r['quantity'] else f"{100*f(r['est']):.1f} pts") + (" (no reliable CI)" if r['ci_available']=='FALSE' else ""))
it=rd("tA_interaction_v4.csv")[0]
add("Ainter", f"aOR {f(it['aOR']):.2f} ({f(it['lo']):.2f}\u2013{f(it['hi']):.2f}) p {f(it['p']):.3g} [n={it['n']}]")
nh=rd("t_nhis_weighted_std_v4.csv")
for r in nh: add("NHIS|"+r["quantity"], f"{f(r['est_pct']):.2f} ({f(r['lo_pct']):.2f}\u2013{f(r['hi_pct']):.2f})")
nhd=rd("t_nhis_std_detail_v4.csv")
for r in nhd: add("NHISband|"+r["band"], f"rate={100*f(r['rate']):.2f}% stdw={f(r['standard_weight_NHANES']):.4f}")

with open(T/"numbers_v4.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["key","value"]); [w.writerow(k) for k in out]
print(f"numbers_v4.csv written: {len(out)} keys")
