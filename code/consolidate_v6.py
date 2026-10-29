#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""consolidate_v6.py — extend numbers_v5.csv with the round-7 (v6) keys into numbers_v6.csv.
All v6 values are read from the survey_analysis_v6.R output tables; nothing is hand-entered."""
import os, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[v]="1"
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; T=ROOT/"results"/"tables"
def rd(n):
    with open(T/n,encoding="utf-8-sig") as f: return list(csv.DictReader(f))
def f(x): return float(x)
def c1(est,lo,hi): return f"{f(est):.1f} ({f(lo):.1f}\u2013{f(hi):.1f})"
out=[]
def add(k,v): out.append((k,v))
# carry every v5 key verbatim
with open(T/"numbers_v5.csv",encoding="utf-8") as fh:
    for row in csv.reader(fh):
        if row and row[0]!="key": add(row[0], row[1] if len(row)>1 else "")

# 16 moderate-or-worse DR
for r in rd("t_modworse_gap_v6.csv"):
    add("modworse|"+r["stratum"], c1(r["est"],r["lo"],r["hi"])+f" [n={r['n']}]")
# 17 IPW weight diagnostics
for r in rd("t_ipw_weightdiag_v6.csv"):
    add("ipwwd|"+r["model"], f"weight min {int(f(r['wt_min'])):,} / median {int(f(r['wt_median'])):,} / max {int(f(r['wt_max'])):,}; IPW ESS {int(f(r['ipw_ess'])):,} (raw ESS {int(f(r['raw_ess'])):,}); floor {r['floor_p']}")
for r in rd("t_ipw_prevalence_ext_v6.csv"):
    add("ipwext|"+r["measure"], f"naive {f(r['naive']):.2f} \u2192 IPW(extended) {f(r['ipw_ext']):.2f}")
for r in rd("t_discordance_selection_v6.csv"):
    add("discsel|"+r["outcome"], f"{r['responders_weighted']} \u2192 {r['ipw_gradability']}")
# 18 MI diagnostics
for r in rd("t_mi_missingness_v6.csv"):
    add("missrate|"+r["variable"], f"{f(r['pct_missing']):.1f}% missing")
for r in rd("t_mi_perimputation_v6.csv"):
    add("mimi|"+r["term"], f"pooled aOR {f(r['aOR']):.3f} (across m: {f(r['min_aOR']):.3f}\u2013{f(r['max_aOR']):.3f}, SD {f(r['sd_across_m']):.3f}, n_imputations={r['n_imputations']})")
for r in rd("t_missing_mechanism_v6.csv"):
    add("missmech|"+r["model"]+"|"+r["term"], f"OR {f(r['OR']):.3f}, p {f(r['p']):.3g}")
# design df (v6, survey::degf corrected)
for r in rd("t_design_df_v6.csv"):
    add("dfv6|"+r["subset"], f"{r['n']} resp; strata={r['strata']}; total PSU={r['total_PSU']}; design df (survey::degf)={r['degf_survey']}")
with open(T/"numbers_v6.csv","w",newline="",encoding="utf-8") as fh:
    w=csv.writer(fh); w.writerow(["key","value"]); [w.writerow(k) for k in out]
print(f"numbers_v6.csv written: {len(out)} keys")
print({k:v for k,v in out if k.startswith(("modworse","ipwext","discsel","mimi|pir2"))})
