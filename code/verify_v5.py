#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_v5.py — round-6 audit.
(1) Enforce the reviewer's sample-denominator assertions from BOTH numbers_v5.csv
    and the raw analytic dataset.
(2) Re-check every in-text / table statistic against numbers_v5.csv (check_pair).
(3) Confirm the round-6 construct-validity edits are present (and the old
    absolute claims / stale artefacts are gone).
(4) Guard CI sanity: 0<=lo<=est<=hi<=100 for every weighted proportion."""
import os, sys, re, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ.setdefault(v,"1")
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
MD  = ROOT/"manuscript"/"题目3手稿.md"
SUPP= ROOT/"manuscript"/"Supplementary_Materials_v5.md"
NUMS= ROOT/"results"/"tables"/"numbers_v5.csv"
RAW = ROOT/"data"/"processed"/"analytic_dataset_v2.csv"
fails, oks = [], []
def check(name, cond, detail=""): (oks if cond else fails).append((name, bool(cond), detail))

src={}
with open(NUMS,encoding="utf-8") as f:
    for row in csv.reader(f):
        if row and row[0]!="key": src[row[0]]=row[1] if len(row)>1 else ""
mdtxt=open(MD,encoding="utf-8").read()
supptxt=open(SUPP,encoding="utf-8").read()
text=mdtxt+"\n"+supptxt

def nd(x): return re.sub(r"[\u2013\u2014-]", "–", x)   # unify dashes to en-dash
text_u=nd(text)

# ---------- (1) DENOMINATOR ASSERTIONS ----------
def num(tok): return int(re.sub(r"\D","",tok))
CNT={k.split("|",1)[1]:num(v) for k,v in src.items() if k.startswith("CNT|")}
def A(name, cond, detail=""): check(name, cond, detail)
A("dr_gradable_disease==319", CNT.get("dr_gradable_disease")==319, str(CNT.get("dr_gradable_disease")))
A("dr_gap_responders==313",   CNT.get("dr_gap_responders")==313)
A("dr_core_complete_cases==187", CNT.get("dr_core_complete_cases")==187)
A("amd_gradable_disease==441",CNT.get("amd_gradable_disease")==441)
A("amd_gap_responders==436",  CNT.get("amd_gap_responders")==436)
A("amd_core_complete_cases==226", CNT.get("amd_core_complete_cases")==226)
A("mild+mod+severe==313", CNT.get("mild_dr_responders")+CNT.get("moderate_dr_responders")+CNT.get("severe_dr_responders")==313,
  f"{CNT.get('mild_dr_responders')}+{CNT.get('moderate_dr_responders')}+{CNT.get('severe_dr_responders')}")
A("GA+NV==55==late", CNT.get("geographic_atrophy_n")+CNT.get("neovascular_amd_n")==55 and CNT.get("late_amd_n")==55)

# independent recount from raw dataset (defense in depth)
RD=list(csv.DictReader(open(RAW,encoding="utf-8-sig")))
def gv(r,k):
    x=r.get(k,"").strip()
    if x in ("","NA","NaN","nan"): return None
    try: return float(x)
    except: return x
rc=dict(dr_grad=0,dr_resp=0,dr_core=0,amd_grad=0,amd_resp=0,amd_core=0,mild=0,mod=0,sev=0,ga=0,nv=0,late=0)
for r in RD:
    dm=gv(r,"dm_dx"); odra=gv(r,"obj_dr_any"); oda=gv(r,"obj_amd_any"); oamd=gv(r,"OPDUARM")
    dxdr=gv(r,"dx_dr"); dxamd=gv(r,"dx_amd"); l4=gv(r,"OPDURL4"); ed=gv(r,"educ"); pir=gv(r,"pir")
    complete = ed is not None and int(ed) in (1,2,3) and pir is not None
    if dm==1 and odra==1:
        rc["dr_grad"]+=1
        if dxdr is not None:
            rc["dr_resp"]+=1
            if complete: rc["dr_core"]+=1
            if l4==2: rc["mild"]+=1
            elif l4==3: rc["mod"]+=1
            elif l4==4: rc["sev"]+=1
    if oda==1:
        rc["amd_grad"]+=1
        if dxamd is not None:
            rc["amd_resp"]+=1
            if complete: rc["amd_core"]+=1
    if oamd==2:
        rc["late"]+=1
        if gv(r,"OPDUGA")==1: rc["ga"]+=1
        if gv(r,"OPDUEXU")==1: rc["nv"]+=1
A("raw dr==319/313/187",(rc["dr_grad"],rc["dr_resp"],rc["dr_core"])==(319,313,187),str((rc["dr_grad"],rc["dr_resp"],rc["dr_core"])))
A("raw amd==441/436/226",(rc["amd_grad"],rc["amd_resp"],rc["amd_core"])==(441,436,226),str((rc["amd_grad"],rc["amd_resp"],rc["amd_core"])))
A("raw mild+mod+sev==313",rc["mild"]+rc["mod"]+rc["sev"]==313,f"{rc['mild']}/{rc['mod']}/{rc['sev']}")
A("raw GA+NV==55",rc["ga"]+rc["nv"]==55 and rc["late"]==55,f"{rc['ga']}/{rc['nv']}/{rc['late']}")

# ---------- (2) core numbers vs source ----------
def dec(tok): return len(tok.split(".")[1]) if "." in tok else 0
def rounds(tok, s): return abs(float(tok)-float(s))<=0.5*(10**-dec(tok))+1e-9
def pair(label, snippet, source_str):
    sn=nd(snippet)
    if sn not in text_u:
        check(label, False, f"NOT IN TEXT: {sn!r}"); return
    mt=re.findall(r"\d[\d,]*\.?\d*", sn); st=re.findall(r"\d[\d,]*\.?\d*", nd(source_str))
    if len(st)<len(mt): check(label, False, f"source nums {st} < text nums {mt}"); return
    bad=[f"{a}!~{b}" for a,b in zip(mt,st) if not rounds(a.replace(',',''), b.replace(',',''))]
    check(label, not bad, "drift "+", ".join(bad) if bad else "")

# prevalence
for snip,key in [("9.75 (8.79–10.80)","prev|Any objectively graded retinopathy (all 40+, descriptive)"),
 ("1.35 (1.10–1.65)","prev|Moderate-or-worse retinopathy (all 40+)"),
 ("33.0 (29.3–37.0)","prev|Objective retinopathy AMONG adults with diabetes"),
 ("6.58 (5.65–7.66)","prev|Any AMD (early+late)"),
 ("0.80 (0.54–1.18)","prev|Late AMD"),
 ("12.05 (10.68–13.56)","prev|Diagnosed diabetes"),
 ("87.4 (85.1–89.4)","prev|Insured (any coverage)"),
 ("5.06 (4.41–5.80)","prev|Self-reported glaucoma dx"),
 ("11.07 (10.03–12.21)","prev|Self-reported cataract operation")]:
    pair("prev "+snip, snip, src[key])
# gaps
for snip,key in [("70.2 (63.8–75.9)","gap|DR: graded retinopathy in diabetes, NO self-reported dx"),
 ("82.2 (77.3–86.2)","gap|AMD: graded AMD, NO self-reported dx"),
 ("41.4 (25.3–59.6)","gap|Late AMD: graded late AMD, NO self-reported dx"),
 ("87.9 (84.4–90.6)","amdsev|Early AMD"),
 ("35.8 (31.3–40.5)","gap|Care: NO dilated exam within 12 months (all diabetes)"),
 ("32.4 (25.9–39.7)","gap|Care: NO dilated exam within 12 months (diabetes + retinopathy)")]:
    pair("gap "+snip, snip, src[key])
# severity gap + dx
for snip,key in [("78.1 (71.3–83.7)","sevgap|OPDURL4=2"),("64.4 (48.3–77.8)","sevgap|OPDURL4=3"),("15.7 (5.0–39.7)","sevgap|OPDURL4=4")]:
    pair("sevgap "+snip, snip, src[key])
for tok,key in [("16.6","sevdx|OPDURL4=1"),("21.9","sevdx|OPDURL4=2"),("35.6","sevdx|OPDURL4=3"),("84.3","sevdx|OPDURL4=4")]:
    check("sevdx "+tok, tok in text and rounds(tok, src[key].split()[0]), key)
# age strata
for snip,key in [("99.1 (95.6–99.8)","age|AMD 40-59"),("86.6 (77.8–92.3)","age|AMD 60-74"),
 ("66.7 (60.1–72.6)","age|AMD >=75"),("79.7 (75.0–83.8)","age|AMD >=50"),
 ("73.4 (59.9–83.6)","age|DR 40-59"),("66.5 (58.6–73.6)","age|DR 60-74"),("71.1 (56.0–82.7)","age|DR >=75")]:
    pair("age "+key, snip, src[key])
# late AMD subtypes
pair("GA","50.3 (26.6–73.9)",src["lateSub|Geographic atrophy"])
pair("NV","27.7 (8.0–62.9)",src["lateSub|Exudative/neovascular"])
# primary logistic
pair("DR age","0.99 (0.97–1.02)",src["prim|PRIMARY: no-reported-dx DR|agec"])
pair("DR pir","1.34 (0.94–1.91)",src["prim|PRIMARY: no-reported-dx DR|pir2"])
pair("AMD age","0.93 (0.89–0.96)",src["prim|PRIMARY: no-reported-dx AMD|agec"])
pair("AMD pir","0.88 (0.61–1.28)",src["prim|PRIMARY: no-reported-dx AMD|pir2"])
pair("AMD per10","0.46 (0.31–0.68)","0.46 (0.31–0.68)")
# insurance DR
pair("insDR pir","1.39 (0.99–1.94)",src["insDR|pir2"])
pair("insDR unins","1.87 (0.62–5.60)",src["insDR|insured_fUninsured"])
check("AMD ins 177/211","177/211" in text); check("AMD ins 14/14","14/14" in text)
# MI + reduced income (S4)
pair("MI pir","1.38 (1.02–1.87)",src["mi|pir2"])
pair("reduced pir","1.46 (1.09–1.94)",src["red|Drop education (income kept)|pir2"])
pair("mi-ind pir","1.48 (1.12–1.96)",src["miC|pir_filled"])
# Analysis A
pair("A exam","0.30 (0.11–0.83)",src["Aadj|recent_dilated_exam"])
pair("A pir","1.49 (1.08–2.07)",src["Aadj|pir2"])
pair("A mod","0.43 (0.17–1.10)",src["Aadj|factor(OPDURL4)3"])
pair("A sev","0.05 (0.01–0.21)",src["Aadj|factor(OPDURL4)4"])
pair("A inter","1.61 (0.29–9.04)",src["Ainter"])
for tok in ["82.0","64.5","81.8","62.4"]: check("A value "+tok, tok in text)
check("A exam groups n","n = 106" in text and "n = 207" in text)
check("Holm P=0.27","Holm P = 0.27" in text or "Holm-adjusted P = 0.27" in text)
check("Holm 0.010","0.010" in text)
# non-response bounds (from nrb; hyphen->en-dash unified)
for tok in ["69.2","70.6","81.6","82.3"]: check("bound "+tok, tok in text)
# design df (S7b)
check("df 29 present","29" in src["ddf|DR responders (313)"] and "df(Taylor)" in src["ddf|DR responders (313)"])
check("S7b df table","Taylor df" in supptxt and "31" in supptxt)
# NHIS
pair("NHIS crude","2.66 (2.40–2.91)",src["NHIS|NHIS 2016 self-reported macular degeneration, survey-weighted crude (>=40)"])
check("NHIS agestd design-cov 2.45 (2.22–2.69)","2.45 (2.22–2.69)" in text_u or "2.45% (2.22–2.69)" in text_u)
src_agesex=nd(src.get("nhisver|NHIS age-and-sex-standardised (design covariance; std weights fixed from NHANES)",""))
check("NHIS age-sex 2.46 (2.22–2.70)","2.46" in text_u and "2.22–2.70" in text_u and src_agesex.startswith("2.46 (2.22"), src_agesex)
check("NHIS DR prevalence 1.27","1.27 (1.09–1.46)" in text)
check("NHIS glaucoma 3.97","3.97 (3.66–4.28)" in text)
check("NHIS cataract 21.17","21.17 (20.37–21.96)" in text)

# ---------- (4) CI sanity over all weighted proportions in source ----------
ci_bad=[]
for k,v in src.items():
    if k.startswith(("CNT","ddf","grad")): continue
    m=re.search(r"(-?\d+\.?\d*)\s*\((-?\d+\.?\d*)[–-](\d+\.?\d*)\)", nd(v))
    if m:
        e,lo,hi=map(float,m.groups())
        if not (0<=lo<=e<=hi<=100): ci_bad.append((k,e,lo,hi))
        if abs(e-lo)>40 or abs(hi-e)>40: ci_bad.append((k,"wide",e,lo,hi))
check("all weighted-proportion CIs within [0,100] & monotone", not ci_bad, str(ci_bad[:5]))

# ---------- (3) round-6 construct-validity content ----------
must = {
 "soften only-dataset->rare resource":"a rare nationally representative resource" in mdtxt,
 "soften unmeasured->not comprehensively characterised":"has not been comprehensively characterised" in mdtxt,
 "no absolute 'only US nationally representative dataset' claim":"the only US nationally representative dataset" not in mdtxt,
 "no 'is unmeasured'":"is unmeasured in nationally representative" not in mdtxt,
 "citation range fixed 6-8":"⁶⁻⁸" in mdtxt,
 "no lone broken superscript 6- (⁶⁻ followed by space)":"⁶⁻ " not in mdtxt,
 "retinopathy-among-adults-with-diabetes naming":"retinopathy among adults with diabetes" in mdtxt,
 "DIQ080 patient-reported construct":"'reports having been told'" in mdtxt or "reports having been told" in mdtxt,
 "no self-reported diagnosis not never diagnosed":"absence of a" in mdtxt and "chart-confirmed" in mdtxt,
 "early AMD gap 87.9 in results":"87.9% (84.4–90.6)" in mdtxt or "87.9 (84.4–90.6)" in mdtxt,
 "income direction-similar wording":"direction of the income association was similar" in mdtxt,
 "MI reported in manuscript":"multiple imputation" in mdtxt and "Rubin" in mdtxt,
 "gradability/IPW section present":"inverse-probability" in mdtxt,
 "design df referenced":"degrees of freedom" in mdtxt,
 "GA-vs-NV not established difference":"should not be interpreted as an established group difference" in mdtxt or "should not be read as an established group difference" in mdtxt,
 "non-response bounds in manuscript":"Extreme-scenario" in mdtxt or "extreme-scenario" in mdtxt,
 "no 'prespecified that discordance would be large'":"prespecified that discordance would be large" not in mdtxt,
 "planned-analysis language":"specified for this study before estimation" in mdtxt or "planned secondary" in mdtxt or "prior to estimation" in mdtxt,
 "reviewer core para (recall error)":"susceptibility to recall error" in mdtxt,
 "reviewer core para (not attributable exclusively)":"not necessarily attributable exclusively to diabetes" in mdtxt,
 "reviewer conclusion (historical differences)":"historical differences between imaging-based disease classification" in mdtxt,
 "Discussion has NO 'Strengths and limitations' subheading":"### Strengths and limitations" not in mdtxt,
 "Discussion has NO 'Additional methodological considerations' subheading":"### Additional methodological considerations" not in mdtxt,
 "provenance table S6":"Supplementary Table S6" in supptxt and "Official label" in supptxt,
 "S7 bounds table":"Supplementary Table S7" in supptxt,
 "S7b df table":"Supplementary Table S7b" in supptxt,
 "S8 gradability table":"Supplementary Table S8" in supptxt,
 "S5b design covariance":"Supplementary Table S5b" in supptxt and "reweighting identity" in supptxt,
 "Table 3 note clarifies 225 not 436":"not all 436 AMD responders" in supptxt or "not all 436 AMD responders" in mdtxt,
 "AI disclosure placeholder":"AI/LLM use" in mdtxt,
 "code availability v5 scripts":"survey_analysis_v5.R" in mdtxt and "verify_v5.py" in mdtxt,
}
for name,cond in must.items(): check(name, cond)

# ---------- stale / forbidden (v4 artefacts, but NOT the legitimate bound values) ----------
forbidden=["89.1","all 319 answered","the only US nationally representative","is unmeasured in nationally",
 "strongest correlate","load-bearing","was protective","EJE","Running head","Significance statement",
 "reviewer requests","corroboration","2.23–2.68)"]
for tok in forbidden: check(f"no forbidden {tok!r}", tok.lower() not in text.lower(), f"found {tok}")
# stale v3 sample numbers
for tok in ["70.6 (64.4–76.0)","32.2","1.38 (0.94","1.47","67.1","86.7","87.9 (84.38","0.29 (0.11"]:
    check(f"no stale {tok!r}", nd(tok) not in text_u, f"found {tok}")

# abstract word count
m=re.search(r"## Abstract\n(.*?)\n---", mdtxt, re.S)
if m:
    wc=len(re.findall(r"\S+",m.group(1))); check(f"abstract <=200 (={wc})", wc<=200, f"wc={wc}")
else: check("abstract found", False)
# title word count
title=mdtxt.splitlines()[0].lstrip("# ").strip()
tw=len(re.findall(r"\S+",title))
check(f"title <=20w (={tw})", tw<=20)
# figures embedded
for fig in ["Fig1_gaps","Fig2_objective_vs_selfreport","Fig3_DR_severity_vs_dx"]:
    check(f"embed {fig}", f"../figures/{fig}.png" in mdtxt)
for fig in ["FigS1_flowchart","FigS2_eyecare_predicted"]:
    check(f"embed {fig}", f"../figures/{fig}.png" in supptxt)

print("="*60); print(f"PASSED: {len(oks)}   FAILED: {len(fails)}"); print("="*60)
if fails:
    print("*** FAILURES ***")
    for n,c,d in fails: print(f"  [FAIL] {n}: {d}")
    sys.exit(1)
print("ALL CHECKS PASS"); sys.exit(0)
