#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_verification_report_v7.py — assemble verification_report.txt for round 8: denominator
assertions, design + residual degrees of freedom, the per-model CI/P re-derivation, headline
numbers, IPW weight decomposition, AMD age-vs-severity, CI-sanity summary and the verify_v7 result,
all pulled from numbers_v7.csv and a raw recount so the report cannot drift from the data."""
import os, csv, subprocess, sys, datetime
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[v]="1"
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; T=ROOT/"results"/"tables"
src={}
for row in csv.reader(open(T/"numbers_v7.csv",encoding="utf-8")):
    if row and row[0]!="key": src[row[0]]=row[1] if len(row)>1 else ""
RD=list(csv.DictReader(open(ROOT/"data"/"processed"/"analytic_dataset_v2.csv",encoding="utf-8-sig")))
def gv(r,k):
    x=r.get(k,"").strip()
    if x in ("","NA","NaN","nan"): return None
    try: return float(x)
    except: return x
rc=dict(dg=0,dr=0,dc=0,ag=0,ar=0,ac=0,mi=0,mo=0,se=0,ga=0,nv=0,lt=0,both=0)
for r in RD:
    dm=gv(r,"dm_dx");odra=gv(r,"obj_dr_any");oda=gv(r,"obj_amd_any");oamd=gv(r,"OPDUARM")
    dxdr=gv(r,"dx_dr");dxamd=gv(r,"dx_amd");l4=gv(r,"OPDURL4");ed=gv(r,"educ");pir=gv(r,"pir")
    comp=ed is not None and int(ed) in (1,2,3) and pir is not None
    if dm==1 and odra==1:
        rc["dg"]+=1
        if dxdr is not None:
            rc["dr"]+=1
            if comp: rc["dc"]+=1
            if l4==2:rc["mi"]+=1
            elif l4==3:rc["mo"]+=1
            elif l4==4:rc["se"]+=1
    if oda==1:
        rc["ag"]+=1
        if dxamd is not None:
            rc["ar"]+=1
            if comp: rc["ac"]+=1
    if oamd==2:
        rc["lt"]+=1
    if gv(r,"OPDUGA")==1:rc["ga"]+=1
    if gv(r,"OPDUEXU")==1:rc["nv"]+=1
    if gv(r,"OPDUGA")==1 and gv(r,"OPDUEXU")==1:rc["both"]+=1
L=[]
def p(s=""): L.append(s)
p("VERIFICATION REPORT — eye3 diagnosis/care-gap manuscript (analysis v7, round 8)")
p("Generated: %s  |  source of truth: results/tables/numbers_v7.csv  |  audit: code/verify_v7.py" % datetime.date.today().isoformat())
p("="*78)
p("")
p("1. SAMPLE-DENOMINATOR ASSERTIONS (numbers_v7.csv CNT keys vs raw recount of analytic_dataset_v2.csv)")
p("-"*78)
pairs=[("dr_gradable_disease",319,rc["dg"]),("dr_gap_responders",313,rc["dr"]),("dr_core_complete_cases",187,rc["dc"]),
 ("amd_gradable_disease",441,rc["ag"]),("amd_gap_responders",436,rc["ar"]),("amd_core_complete_cases",226,rc["ac"]),
 ("mild_dr_responders",197,rc["mi"]),("moderate_dr_responders",85,rc["mo"]),("severe_dr_responders",31,rc["se"]),
 ("geographic_atrophy_n",32,rc["ga"]),("neovascular_amd_n",23,rc["nv"]),("late_amd_n",55,rc["lt"])]
allok=True
for k,expect,raw in pairs:
    cnt=int(src["CNT|"+k]); ok=(cnt==expect==raw); allok&=ok
    p("  %-26s numbers_v7=%d  raw_recount=%d  expected=%d  %s" % (k,cnt,raw,expect,"OK" if ok else "MISMATCH"))
p("  mild+mod+severe == 313 : %d+%d+%d = %d  %s" % (rc["mi"],rc["mo"],rc["se"],rc["mi"]+rc["mo"]+rc["se"],
  "OK" if rc["mi"]+rc["mo"]+rc["se"]==313 else "MISMATCH"))
p("  GA + neovascular == late(55): %d+%d = %d  %s" % (rc["ga"],rc["nv"],rc["ga"]+rc["nv"],
  "OK" if rc["ga"]+rc["nv"]==55 else "MISMATCH"))
p("  GA & neovascular SAME worse eye (mutual exclusivity): both=%d (expected 0)  %s" % (rc["both"],
  "OK" if rc["both"]==0 else "CHECK"))
p("  RESULT: %s" % ("ALL DENOMINATORS RECONCILE" if (allok and rc["both"]==0) else "MISMATCH — DO NOT SUBMIT"))
p("")
p("2. DESIGN + RESIDUAL DEGREES OF FREEDOM (per model; from survey_analysis_v7.R audit)")
p("-"*78)
for k in sorted(src):
    if k.startswith("audit_df|"): p("  %-32s %s" % (k.split("|",1)[1], src[k]))
for k in sorted(src):
    if k.startswith("dfv6|"): p("  design-only  %-30s %s" % (k.split("|",1)[1], src[k]))
p("  NOTE: CIs use exp(coef +/- qt(0.975, residual_df)*SE) at residual_df = degf(design) - rank + 1;")
p("        verify_v7 independently re-derives each aOR/CI/P from coef/SE/residual-df and matches.")
p("")
p("3. PER-MODEL CI / P RE-DERIVATION (audit key rows)")
p("-"*78)
for k in ["audit|PRIMARY DR core|pir2","audit|PRIMARY AMD core|agec",
 "audit|SUPP DR + insurance|pir2","audit|SUPP DR + insurance|insured_fUninsured",
 "audit|ANALYSIS A (eye-care)|recent_dilated_exam","audit|ANALYSIS A (eye-care)|factor(OPDURL4)4"]:
    p("  %-52s %s" % (k.split("|",1)[1], src[k]))
p("")
p("4. HEADLINE ESTIMATES (design-weighted, logit CIs)")
p("-"*78)
for k in ["gap|DR: graded retinopathy in diabetes, NO self-reported dx","gap|AMD: graded AMD, NO self-reported dx",
 "amdsev|Early AMD","gap|Late AMD: graded late AMD, NO self-reported dx",
 "modworse|Moderate-or-worse retinopathy (DR, responders)",
 "gap|Care: NO dilated exam within 12 months (diabetes + retinopathy)",
 "prev|Any AMD (early+late)","nhisver|NHIS age-standardised (design covariance; std weights fixed from NHANES)"]:
    p("  %-70s %s" % (k.split("|",1)[1], src.get(k,"(missing)")))
p("")
p("5. AMD AGE GRADIENT vs SEVERITY (round-8 addition, Supplementary Table S9)")
p("-"*78)
for k in ["amdagesev|agec","amdagesev|amdstagelate","amdagesev|df",
 "earlyamdpstrata|Early AMD age 40-59","earlyamdpstrata|Early AMD age 60-69","earlyamdpstrata|Early AMD age 70+"]:
    p("  %-42s %s" % (k.split("|",1)[1], src.get(k,"(missing)")))
p("")
p("6. IPW WEIGHT DECOMPOSITION (round-8 fix of S8 labels)")
p("-"*78)
for k in sorted(src):
    if k.startswith("ipwdec|"): p("  %-52s %s" % (k.split("|",1)[1], src[k]))
p("")
p("7. ROBUSTNESS / SENSITIVITY")
p("-"*78)
p("  Non-response bounds  DR: %s / %s / %s" % (src["nrb|DR|responders_only"],src["nrb|DR|all_diagnosed"],src["nrb|DR|all_undiagnosed"]))
p("                       AMD: %s / %s / %s" % (src["nrb|AMD|responders_only"],src["nrb|AMD|all_diagnosed"],src["nrb|AMD|all_undiagnosed"]))
p("  Income across missing-data handling:")
p("     complete-case  %s" % src["prim|PRIMARY: no-reported-dx DR|pir2"])
p("     +insurance     %s" % src["insDR|pir2"])
p("     drop-education %s" % src["red|Drop education (income kept)|pir2"])
p("     multiple-imput %s" % src["mi|pir2"])
p("     per-imputation %s" % src["mimi|pir2"])
p("  Grading-feasibility IPW: %s | %s" % (src["ipwext|Any retinopathy (all >=40)"], src["ipwext|Any AMD (all >=40)"]))
p("  Discordance selection:   DR %s ; AMD %s" % (src["discsel|DR diagnosis gap"], src["discsel|AMD diagnosis gap"]))
p("")
p("8. AUTOMATED AUDIT (verify_v7.py)")
p("-"*78)
r=subprocess.run([sys.executable,str(ROOT/"code"/"verify_v7.py")],capture_output=True,text=True)
tail=[l for l in r.stdout.splitlines() if "PASSED" in l or "ALL CHECKS" in l or "FAIL" in l]
for l in tail: p("  "+l)
p("  verify_v7 exit code: %d" % r.returncode)
p("")
p("9. CI SANITY + double-rounding guard: every weighted proportion satisfies 0<=lo<=est<=hi<=100;")
p("   every audit display string is single-rounded from full precision (verify_v7 checks both).")
p("")
p("OVERALL: %s" % ("PASS — manuscript numbers are reproducible from source data and internally consistent."
   if (allok and rc["both"]==0 and r.returncode==0) else "FAIL — resolve before submission."))
(T/"verification_report.txt").write_text("\n".join(L)+"\n",encoding="utf-8")
print(L[0]); print("wrote verification_report.txt (%d lines)"%len(L))
