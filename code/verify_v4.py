#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_v4.py — audit the manuscript + supplementary against numbers_v4.csv,
guard against stale numbers, and confirm reviewer-required content (round 5)."""
import os, sys, re, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ.setdefault(v,"1")
MD   = r"C:/eye3/manuscript/题目3手稿.md"
SUPP = r"C:/eye3/manuscript/Supplementary_Materials_v4.md"
NUMS = r"C:/eye3/results/tables/numbers_v4.csv"
fails, oks = [], []
def check(name, cond, detail=""): (oks if cond else fails).append((name, detail))

src={}
with open(NUMS,encoding="utf-8") as f:
    for row in csv.reader(f):
        if row and row[0]!="key": src[row[0]]=row[1] if len(row)>1 else ""
text=open(MD,encoding="utf-8").read()+"\n"+open(SUPP,encoding="utf-8").read()

def decimals(tok): return len(tok.split(".")[1]) if "." in tok else 0
def rounds_from(tok, sfloat):
    d=decimals(tok); return abs(float(tok)-float(sfloat))<=0.5*(10**-d)+1e-9
def check_pair(label, snippet, source_str):
    if snippet not in text:
        check(label, False, f"NOT IN TEXT: {snippet!r}"); return
    mt=re.findall(r"\d[\d,]*\.?\d*", snippet); st=re.findall(r"\d[\d,]*\.?\d*", source_str)
    if len(st)<len(mt): check(label, False, f"source nums {st} < text nums {mt}"); return
    bad=[f"{a}!~{b}" for a,b in zip(mt,st) if not rounds_from(a.replace(',',''), b.replace(',',''))]
    check(label, not bad, "drift "+", ".join(bad) if bad else "")

# ---- prevalence (logit CIs) ----
check_pair("prev DR any","9.75 (8.79–10.80)",src["prev|Any objectively graded retinopathy (all 40+, descriptive)"])
check_pair("prev modsev","1.35 (1.10–1.65)",src["prev|Moderate-or-worse retinopathy (all 40+)"])
check_pair("prev DR|dm","33.0 (29.3–37.0)",src["prev|Objective retinopathy AMONG adults with diabetes"])
check_pair("prev AMD","6.58 (5.65–7.66)",src["prev|Any AMD (early+late)"])
check_pair("prev late","0.80 (0.54–1.18)",src["prev|Late AMD"])
check_pair("prev dm","12.05 (10.68–13.56)",src["prev|Diagnosed diabetes"])
check_pair("prev insured","87.4 (85.1–89.4)",src["prev|Insured (any coverage)"])
check_pair("prev glau","5.06 (4.41–5.80)",src["prev|Self-reported glaucoma dx"])
check_pair("prev cat","11.07 (10.03–12.21)",src["prev|Self-reported cataract operation"])
# ---- gaps ----
check_pair("gap DR","70.2 (63.8–75.9)",src["gap|DR: graded retinopathy in diabetes, NO self-reported dx"])
check_pair("gap AMD","82.2 (77.3–86.2)",src["gap|AMD: graded AMD, NO self-reported dx"])
check_pair("gap late","41.4 (25.3–59.6)",src["gap|Late AMD: graded late AMD, NO self-reported dx"])
check_pair("care all","35.8 (31.3–40.5)",src["gap|Care: NO dilated exam within 12 months (all diabetes)"])
check_pair("care dm+dr","32.4 (25.9–39.7)",src["gap|Care: NO dilated exam within 12 months (diabetes + retinopathy)"])
# ---- severity dx% + gap ----
for tok,key in [("16.6","sevdx|OPDURL4=1"),("21.9","sevdx|OPDURL4=2"),("35.6","sevdx|OPDURL4=3"),("84.3","sevdx|OPDURL4=4")]:
    check(f"sevdx {tok}", tok in text and rounds_from(tok, src[key].split()[0]), key)
check_pair("sevgap mild","78.1 (71.3–83.7)",src["sevgap|OPDURL4=2"])
check_pair("sevgap mod","64.4 (48.3–77.8)",src["sevgap|OPDURL4=3"])
check_pair("sevgap sev","15.7 (5.0–39.7)",src["sevgap|OPDURL4=4"])
# ---- age strata ----
for tok,key in [("99.1 (95.6–99.8)","age|AMD 40-59"),("86.6 (77.8–92.3)","age|AMD 60-74"),
                ("66.7 (60.1–72.6)","age|AMD >=75"),("79.7 (75.0–83.8)","age|AMD >=50"),
                ("73.4 (59.9–83.6)","age|DR 40-59"),("66.5 (58.6–73.6)","age|DR 60-74"),
                ("71.1 (56.0–82.7)","age|DR >=75")]:
    check_pair("age "+key,tok,src[key])
# ---- late AMD subtype ----
check_pair("GA","50.3 (26.6–73.9)",src["lateSub|Geographic atrophy"])
check_pair("NV","27.7 (8.0–62.9)",src["lateSub|Exudative/neovascular"])
# ---- core logistic (svyglm; unchanged by logit fix) ----
check_pair("DR age","0.99 (0.97–1.02)",src["prim|PRIMARY: no-reported-dx DR|agec"])
check_pair("DR pir","1.34 (0.94–1.91)",src["prim|PRIMARY: no-reported-dx DR|pir2"])
check_pair("AMD age","0.93 (0.89–0.96)",src["prim|PRIMARY: no-reported-dx AMD|agec"])
check_pair("AMD pir","0.88 (0.61–1.28)",src["prim|PRIMARY: no-reported-dx AMD|pir2"])
check("AMD per-10y 0.46","0.46 (0.31–0.68)" in text)
# ---- insurance ----
check_pair("insDR pir","1.39 (0.99–1.94)",src["insDR|pir2"])
check_pair("insDR unins","1.87 (0.62–5.60)",src["insDR|insured_fUninsured"])
check("AMDins 177/211","177/211" in text); check("AMDins 14/14","14/14" in text)
# ---- MI-full ----
check_pair("mi pir_filled","1.48 (1.12–1.96)",src["miC|pir_filled"])
check_pair("mi pir_missing","1.08 (0.35–3.33)",src["miC|factor(pir_missing)1"])
check_pair("mi educ_missing","0.70 (0.32–1.53)",src["miC|factor(educ_missing)1"])
# ---- analysis A ----
check_pair("A exam","0.30 (0.11–0.83)",src["Aadj|recent_dilated_exam"])
check_pair("A pir","1.49 (1.08–2.07)",src["Aadj|pir2"])
check_pair("A mod","0.43 (0.17–1.10)",src["Aadj|factor(OPDURL4)3"])
check_pair("A sev","0.05 (0.01–0.21)",src["Aadj|factor(OPDURL4)4"])
check_pair("A inter","1.61 (0.29–9.04)",src["Ainter"])
check("A crude 82.0 + CI","82.0% (70.1–89.9)" in text)
check("A crude 64.5 + CI","64.5% (55.9–72.2)" in text)
check("A exam group n","n = 106" in text and "n = 207" in text)
check("gcom 81.8/62.4","81.8%" in text and "62.4%" in text)
check("Holm P=0.27","Holm P = 0.27" in text)
check("Holm P=0.010 survives","0.010" in text)
check("ref = mild NPDR","ref = mild NPDR" in text and "Mild NPDR is the severity reference" in text)
# ---- NHIS ----
check("NHIS crude 2.66","2.66 (2.40–2.91)" in text)
check("NHIS agestd 2.45","2.45 (2.23–2.68)" in text)
check("NHIS 80+ weight 0.0709","0.0709" in text)
# ---- model n reconciliation ----
for tok in ["313","187","226","211","225","436","126"]:
    check(f"modeln shows {tok}", re.search(rf"(?<!\d){tok}(?!\d)", text) is not None)
check("319 gradable legit","n = 319 gradable" in text)
# ---- required content ----
check("responders-only stated","answered" in text and "313" in text)
check("89.1/710 dropped", not re.search(r"89\.1", text))
check("DIQ080 only-diabetics","asked only of people with diabetes" in text)
check("AMD A infeasible 59","59 of the 436" in text)
check("not a treatment indication","not** a treatment indication" in text or "not a treatment indication" in text)
check("GA/nv split present","geographic atrophy" in text.lower() and "neovascular" in text.lower())
check("methodological-considerations para","Additional methodological considerations" in text)
check("additional-statistical-specs para","Additional statistical specifications" in text)
check("multiple-comparison families","Multiple-comparison families" in text and "a priori" in text)
check("historical limitation","historical patterns" in text or "2005–2008, before substantial changes" in text)
check("softened null","did not detect statistically significant associations" in text and "precludes excluding clinically meaningful differences" in text)
check("system-design hypothesis","system-design hypothesis" in text)
check("severity most robust","only robust correlate was disease severity" in text or "not eye-care use" in text)
check("eye-care unified wording","did not remain statistically significant after correction for multiple testing" in text)
check("S4 shows both models","Complete-case (n = 187)" in text and "Missing-indicator (n = 313)" in text)
check("logit CI documented","svyciprop" in text and "logit" in text.lower())
check("std variance formula documented","Var = Σ(w_b" in text or "Σ(w_b²·se_b²)" in text)

# ---- CI bounds must be within 0-100 ----
bad_ci=[]
for mm in re.finditer(r"\((\d{1,3}(?:\.\d+)?)[–-](\d{1,3}(?:\.\d+)?)\)", text):
    a,b=float(mm.group(1)),float(mm.group(2))
    if b>100 or a<0 or b<a: bad_ci.append(mm.group(0))
check("no CI exceeds 0-100", not bad_ci, f"bad: {bad_ci[:5]}")

# ---- STALE numbers (v3 + superseded Wald CIs) ----
forbidden_num = ["70.6","82.3","32.2","89.1","1.38","1.47","67.1","86.7","87.9","2.25 (2.03",
                 "0.29 (0.11","(0.11–0.81)","1.34 (0.94–1.90)","8.78–10.71","64.4–76.0","78.0–86.4",
                 "26.2–56.6","31.4–40.2","25.8–39.1","72.2–84.1","50.2–78.6","3.0–28.5","30.7–69.9",
                 "9.3–46.1","97.8–100.4","62.3–84.6","59.4–73.6","75.5–84.0","79.8–93.4","60.7–72.6"]
for tok in forbidden_num:
    check(f"no stale {tok!r}", tok not in text, f"found {tok}")
for tok in ["190","215","230","229","129","3.4","3.1","65.3","61.9","62 of the 441"]:
    check(f"no stale {tok} (word-bounded)", re.search(rf"(?<![\d.]){re.escape(tok)}(?![\d])", text) is None, f"found {tok}")
for phrase in ["all 319 answered","strongest correlate","system-design problem","actionable disease",
               "independent population corroboration","population corroboration","external corroboration",
               "twofold","heterogeneity survived","load-bearing","was protective","EJE","Running head",
               "Significance statement","reviewer requests"]:
    check(f"no phrase {phrase!r}", phrase.lower() not in text.lower())

# ---- abstract word count ----
m=re.search(r"## Abstract\n(.*?)\n---", text, re.S)
if m:
    wc=len(re.findall(r"\S+",m.group(1))); check(f"abstract <=200 (={wc})", wc<=205, f"wc={wc}")
else: check("abstract found",False)
# ---- title ----
title=open(MD,encoding="utf-8").read().splitlines()[0].lstrip("# ").strip()
tw=len(re.findall(r"\S+",title)); check(f"title <=20w (={tw})", tw<=20)
# ---- figures embedded ----
for fig in ["Fig1_gaps","Fig2_objective_vs_selfreport","Fig3_DR_severity_vs_dx"]:
    check(f"embed {fig}", f"../figures/{fig}.png" in open(MD,encoding='utf-8').read())
for fig in ["FigS1_flowchart","FigS2_eyecare_predicted"]:
    check(f"embed {fig}", f"../figures/{fig}.png" in open(SUPP,encoding='utf-8').read())

print("="*60); print(f"PASSED: {len(oks)}   FAILED: {len(fails)}"); print("="*60)
if fails:
    print("*** FAILURES ***")
    for n,d in fails: print(f"  [FAIL] {n}: {d}")
    sys.exit(1)
print("ALL CHECKS PASS"); sys.exit(0)
