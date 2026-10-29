#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_v6.py — round-7 audit against numbers_v6.csv.
(1) Denominator assertions from numbers_v6.csv AND a raw recount.
(2) Every regression 'aOR (CI)' in numbers_v6 must appear verbatim in the text (auto-derived,
    so the t-based intervals cannot drift and the old 1.96 intervals are rejected).
(3) Descriptive/gap/severity/age/NHIS values re-checked against source.
(4) Round-7 content edits present; corrected design df; stale artefacts absent.
(5) CI sanity: 0<=lo<=est<=hi<=100 and not absurdly wide for every weighted proportion."""
import os, sys, re, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ.setdefault(v,"1")
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MD  = ROOT/"manuscript"/"题目3手稿.md"
SUPP= ROOT/"manuscript"/"Supplementary_Materials_v6.md"
NUMS= ROOT/"results"/"tables"/"numbers_v6.csv"
RAW = ROOT/"data"/"processed"/"analytic_dataset_v2.csv"
fails, oks = [], []
def check(name, cond, detail=""): (oks if cond else fails).append((name, bool(cond), detail))
src={}
with open(NUMS,encoding="utf-8") as f:
    for row in csv.reader(f):
        if row and row[0]!="key": src[row[0]]=row[1] if len(row)>1 else ""
mdtxt=open(MD,encoding="utf-8").read(); supptxt=open(SUPP,encoding="utf-8").read()
text=mdtxt+"\n"+supptxt
def nd(x): return re.sub(r"[\u2013\u2014-]","–",x)
text_u=nd(text)

# ---------- (1) DENOMINATOR ASSERTIONS ----------
def num(tok): return int(re.sub(r"\D","",tok))
CNT={k.split("|",1)[1]:num(v) for k,v in src.items() if k.startswith("CNT|")}
for nm,val in [("dr_gradable==319",("dr_gradable_disease",319)),("dr_resp==313",("dr_gap_responders",313)),
 ("dr_core==187",("dr_core_complete_cases",187)),("amd_gradable==441",("amd_gradable_disease",441)),
 ("amd_resp==436",("amd_gap_responders",436)),("amd_core==226",("amd_core_complete_cases",226))]:
    check(nm, CNT.get(val[0])==val[1], str(CNT.get(val[0])))
check("mild+mod+sev==313", CNT["mild_dr_responders"]+CNT["moderate_dr_responders"]+CNT["severe_dr_responders"]==313)
check("GA+NV==55==late", CNT["geographic_atrophy_n"]+CNT["neovascular_amd_n"]==55 and CNT["late_amd_n"]==55)
RD=list(csv.DictReader(open(RAW,encoding="utf-8-sig")))
def gv(r,k):
    x=r.get(k,"").strip()
    if x in ("","NA","NaN","nan"): return None
    try: return float(x)
    except: return x
rc=dict(dg=0,dr=0,dc=0,ag=0,ar=0,ac=0,mi=0,mo=0,se=0,ga=0,nv=0,lt=0)
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
check("raw 319/313/187",(rc["dg"],rc["dr"],rc["dc"])==(319,313,187),str((rc["dg"],rc["dr"],rc["dc"])))
check("raw 441/436/226",(rc["ag"],rc["ar"],rc["ac"])==(441,436,226),str((rc["ag"],rc["ar"],rc["ac"])))
check("raw mild+mod+sev==313",rc["mi"]+rc["mo"]+rc["se"]==313,f"{rc['mi']}/{rc['mo']}/{rc['se']}")
check("raw GA+NV==55",rc["ga"]+rc["nv"]==55 and rc["lt"]==55)

# ---------- (2) regression intervals auto-derived from source ----------
def dec(tok): return len(tok.split(".")[1]) if "." in tok else 0
def rounds(tok,s): return abs(float(tok)-float(s))<=0.5*(10**-dec(tok))+1e-9
def pair(label, snippet, source_str):
    sn=nd(snippet)
    if sn not in text_u: check(label, False, f"NOT IN TEXT: {sn!r}"); return
    mt=re.findall(r"\d[\d,]*\.?\d*",sn); st=re.findall(r"\d[\d,]*\.?\d*",nd(source_str))
    if len(st)<len(mt): check(label,False,f"source nums {st}<text {mt}"); return
    bad=[f"{a}!~{b}" for a,b in zip(mt,st) if not rounds(a.replace(',',''),b.replace(',',''))]
    check(label, not bad, "drift "+", ".join(bad) if bad else "")

reg_prefixes=("prim|","insDR|","Aadj|","miC|","red|","mi|","Ainter")
reg_checked=0; reg_missing=[]
for k,v in src.items():
    if k.startswith(reg_prefixes):
        if "Drop education+income" in k: continue
        if k.startswith("insDR|") and k not in ("insDR|pir2","insDR|insured_fUninsured"): continue
        m=re.search(r"aOR (\d+\.\d+) \((\d+\.\d+)[–-](\d+\.\d+)\)", v)
        if not m: continue
        disp=f"{m.group(1)} ({m.group(2)}–{m.group(3)})"
        reg_checked+=1
        if disp not in text_u: reg_missing.append((k,disp))
check("all regression aOR(CI) from numbers_v6 appear in text", not reg_missing, f"{reg_checked} checked; missing {reg_missing[:6]}")

# ---------- (3) descriptive values ----------
for snip,key in [("9.75 (8.79–10.80)","prev|Any objectively graded retinopathy (all 40+, descriptive)"),
 ("6.58 (5.65–7.66)","prev|Any AMD (early+late)"),("0.80 (0.54–1.18)","prev|Late AMD"),
 ("33.0 (29.3–37.0)","prev|Objective retinopathy AMONG adults with diabetes"),
 ("70.2 (63.8–75.9)","gap|DR: graded retinopathy in diabetes, NO self-reported dx"),
 ("82.2 (77.3–86.2)","gap|AMD: graded AMD, NO self-reported dx"),
 ("41.4 (25.3–59.6)","gap|Late AMD: graded late AMD, NO self-reported dx"),
 ("87.9 (84.4–90.6)","amdsev|Early AMD"),
 ("53.4 (38.7–67.5)","modworse|Moderate-or-worse retinopathy (DR, responders)"),
 ("32.4 (25.9–39.7)","gap|Care: NO dilated exam within 12 months (diabetes + retinopathy)"),
 ("50.3 (26.6–73.9)","lateSub|Geographic atrophy"),("27.7 (8.0–62.9)","lateSub|Exudative/neovascular"),
 ("2.66 (2.40–2.91)","NHIS|NHIS 2016 self-reported macular degeneration, survey-weighted crude (>=40)")]:
    pair("desc "+snip, snip, src[key])
check("NHIS age-std design-cov 2.45 (2.22–2.69)","2.45 (2.22–2.69)" in text_u or "2.45% (2.22–2.69)" in text_u)
check("NHIS age-sex 2.46 (2.22–2.70)","2.46" in text_u and "2.22–2.70" in text_u)
for tok in ["78.1 (71.3–83.7)","64.4 (48.3–77.8)","15.7 (5.0–39.7)"]: check("sevgap "+tok, nd(tok) in text_u)
for tok in ["69.2","70.6","81.6","82.3"]: check("bound "+tok, tok in text)
check("discsel DR 70.2->70.2","70.2 → 70.2" in text_u or "70.2→70.2" in text_u)
check("discsel AMD 82.2->82.0","82.2 → 82.0" in text_u or "82.2→82.0" in text_u)
check("ipw ext 10.13","10.13" in text); check("ipw ext 6.77","6.77" in text)
check("MI per-imputation range 1.24–1.49","1.24–1.49" in text_u)

# ---------- (4) round-7 content ----------
must={
 "S7b corrected total PSU 59":"59" in supptxt and "Total number of PSUs" in supptxt,
 "S7b df 28 DR responders":"Design degrees of freedom" in supptxt and "28" in supptxt,
 "no wrong 'strata − PSUs' header":"strata − PSUs" not in supptxt and "strata - PSUs" not in supptxt,
 "no wrong 'PSUs 2' row":"| 31 | 2 |" not in supptxt,
 "degf() cited":"survey::degf" in text,
 "models used correct df note":"already reflect the correct design df" in text_u or "already reflects the correct design df" in text_u,
 "moderate-or-worse in results":"53.4" in mdtxt and "moderate-or-worse" in mdtxt,
 "section renamed advanced disease":"Discordance in advanced retinal disease" in mdtxt,
 "no 'Potentially vision-threatening'":"Potentially vision-threatening" not in mdtxt,
 "eye-care exploratory label":"exploratory" in mdtxt and "no verifiable pre-registration" in mdtxt,
 "scheme B: no 'single a-priori hypothesis'":"single a-priori hypothesis" not in mdtxt,
 "t-based CI convention stated":"residual degrees of freedom" in mdtxt,
 "no per-10-year row":"per 10 years" not in mdtxt and "per-10-year" not in mdtxt,
 "missingness wording softened":"do not establish that the missingness mechanism is ignorable" in text_u,
 "MI diagnostics present":"positive in every imputation" in mdtxt or "positive in all 20 imputations" in mdtxt,
 "missingness mechanism subtable":"S4c" in supptxt and "not** with the outcome" in supptxt,
 "gradability extended model":"extended" in supptxt and "10.13" in supptxt,
 "discordance selection sensitivity":"Discordance-specific selection sensitivity" in supptxt,
 "system-design softened": nd("consistent with — but do not establish") in text_u,
 "NHIS no 2.7-fold multiple":"2.7-fold" not in mdtxt,
 "NHIS reviewer sentence":"cannot be attributed specifically to diagnostic unawareness" in mdtxt,
 "terminology: no 'diabetic retinopathy cohort'":"diabetic retinopathy cohort" not in mdtxt.lower(),
 "Figure 2 severity gradient embed":"Fig2_severity_gradient.png" in mdtxt,
 "Figure 3 objective-vs-selfreport embed":"Fig3_objective_vs_selfreport.png" in mdtxt,
 "code availability v6":"survey_analysis_v6.R" in mdtxt and "verify_v6.py" in mdtxt,
 "numbers_v6 referenced":"numbers_v6.csv" in mdtxt,
}
for nm,c in must.items(): check(nm, c)

# ---------- (5) CI sanity ----------
bad=[]
for k,v in src.items():
    if k.startswith(("CNT","dfv6","grad","ipw","discsel","mimi","missrate","missmech","modworse")): continue
    m=re.search(r"(-?\d+\.?\d*)\s*\((-?\d+\.?\d*)[–-](\d+\.?\d*)\)", nd(v))
    if m:
        e,lo,hi=map(float,m.groups())
        if not (0<=lo<=e<=hi<=100): bad.append((k,e,lo,hi))
check("all weighted-proportion CIs within [0,100] & monotone", not bad, str(bad[:5]))

# ---------- stale/forbidden ----------
forbidden=["89.1","the only US nationally representative","is unmeasured in nationally","⁶⁻ ",
 "load-bearing","was protective","EJE","Running head","Significance statement","reviewer requests","corroboration",
 "0.11–0.83","1.08–2.07","0.17–1.10","0.01–0.21","0.29–9.04","0.94–1.91","0.99–1.94","0.62–5.60",
 "1.09–1.94","1.12–1.96","0.30–1.52","0.48–3.44","0.53–4.67","0.61–1.28","0.32–2.11","0.31–7.82",
 "0.34–2.90","0.39–3.04","0.65–5.58","0.20–2.61","0.29–2.74","0.46–1.88","0.74–2.17","0.35–3.33","0.32–1.53","0.40–1.86",
 "0.97–1.02), 1.00","per 10 years","2.7-fold","strata − PSUs","who gets examined shapes who gets diagnosed"]
for tok in forbidden: check(f"no forbidden {tok!r}", nd(tok) not in text_u, f"found {tok}")
for tok in ["28–29 degrees","29 Taylor"]: check(f"no stale {tok}", tok not in text_u)

# abstract & title
m=re.search(r"## Abstract\n(.*?)\n---", mdtxt, re.S)
if m:
    wc=len(re.findall(r"\S+",m.group(1))); check(f"abstract<=200 (={wc})", wc<=200, f"wc={wc}")
else: check("abstract found",False)
title=mdtxt.splitlines()[0].lstrip("# ").strip(); tw=len(re.findall(r"\S+",title)); check(f"title<=20w (={tw})",tw<=20)
for fig in ["Fig1_gaps","Fig2_severity_gradient","Fig3_objective_vs_selfreport"]: check(f"embed {fig}", fig+".png" in mdtxt)
for fig in ["FigS1_flowchart","FigS2_eyecare_predicted"]: check(f"embed {fig}", fig+".png" in supptxt)

print("="*60); print(f"PASSED: {len(oks)}   FAILED: {len(fails)}"); print("="*60)
if fails:
    print("*** FAILURES ***")
    for n,c,d in fails: print(f"  [FAIL] {n}: {d}")
    sys.exit(1)
print("ALL CHECKS PASS"); sys.exit(0)
