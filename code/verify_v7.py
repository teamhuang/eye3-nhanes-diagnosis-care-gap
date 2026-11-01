#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_v7.py — round-8 audit against numbers_v7.csv.
(1) Denominator assertions from numbers_v7.csv AND a raw recount.
(2) Every authoritative regression 'aOR (CI)' (prim/insDR/Aadj 2-dp strings) must appear verbatim.
(3) Per-model AUDIT re-derivation: recompute aOR/CI and P from coef/SE/residual-df independently
    and require they reproduce the stored values -> proves CI and P come from ONE df / ONE object.
(4) Descriptive/gap/severity/age/NHIS values re-checked against source.
(5) Round-8 content edits present (S7c audit, S9 age-vs-severity, S8 weight decomposition, S4c
    logic fix, no 'consistent with MAR'), corrected design df, stale artefacts absent.
(6) CI sanity: 0<=lo<=est<=hi<=100 and not absurdly wide for every weighted proportion.
(7) Cover-letter fixes checked against the separate cover_letter.md file."""
import os, sys, re, csv
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ.setdefault(v,"1")
from pathlib import Path
from math import exp
from scipy.stats import t as _st
def tinv(p,df): return float(_st.ppf(p,df))
def t2p(tt,df): return float(2*_st.sf(abs(tt),df))
ROOT=Path(__file__).resolve().parents[1]
MD  = ROOT/"manuscript"/"题目3手稿.md"
MD_DOCX = ROOT/"manuscript"/"\u9898\u76ee3\u624b\u7a3f\u6700\u65b0\u7248\u672c.docx"
SUPP= ROOT/"manuscript"/"Supplementary_Materials_v7.md"
NUMS= ROOT/"results"/"tables"/"numbers_v7.csv"
RAW = ROOT/"data"/"processed"/"analytic_dataset_v2.csv"
AUDT= ROOT/"results"/"tables"/"t_model_audit_v7.csv"
CL  = ROOT/"manuscript"/"cover_letter.md"
CL_DOCX  = ROOT/"manuscript"/"cover_letter.docx"

def _read_docx_text(path):
    try:
        import docx
        d = docx.Document(str(path))
        parts = [p.text for p in d.paragraphs]
        for tbl in d.tables:
            for row in tbl.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        parts.append(p.text)
        return "\n".join(parts)
    except Exception:
        return ""

def _load_text(md_path, docx_fallback):
    if md_path.exists():
        return open(md_path, encoding="utf-8").read()
    if docx_fallback is not None and Path(docx_fallback).exists():
        return _read_docx_text(docx_fallback)
    return ""

fails, oks = [], []
def check(name, cond, detail=""): (oks if cond else fails).append((name, bool(cond), detail))
src={}
with open(NUMS,encoding="utf-8") as f:
    for row in csv.reader(f):
        if row and row[0]!="key": src[row[0]]=row[1] if len(row)>1 else ""
mdtxt = _load_text(MD, MD_DOCX)
if not MD.exists():
    print("[verify_v7] manuscript .md deleted; loaded docx instead (%d chars)" % len(mdtxt))
supptxt = open(SUPP, encoding="utf-8").read() if SUPP.exists() else ""
cltxt   = _load_text(CL, CL_DOCX)
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

# ---------- (2b) PER-MODEL AUDIT RE-DERIVATION (CI and P recomputed from coef/SE/residual-df) ----------
AR=list(csv.DictReader(open(AUDT,encoding="utf-8-sig")))
recompute_bad=[]; ci_p_pair_bad=[]
for r in AR:
    dfres=int(r["residual_df"]); coef=float(r["coef"]); se=float(r["SE"])
    tc=tinv(0.975,dfres)
    lo_r=exp(coef-tc*se); hi_r=exp(coef+tc*se); or_r=exp(coef)
    p_r=t2p(coef/se,dfres)
    # (i) independently recompute the stored full-precision aOR/lo/hi/p from coef,SE and residual df
    if abs(or_r-float(r["aOR"]))>1e-4: recompute_bad.append((r["model"],r["term"],"aOR"))
    if abs(lo_r-float(r["lo"]))>1e-4: recompute_bad.append((r["model"],r["term"],"lo"))
    if abs(hi_r-float(r["hi"]))>1e-4: recompute_bad.append((r["model"],r["term"],"hi"))
    if abs(p_r-float(r["p_raw"]))>max(1e-4,abs(float(r["p_raw"]))*0.01): recompute_bad.append((r["model"],r["term"],"p"))
    # (ii) confirm the 2-dp DISPLAY strings equal single-rounding of the recomputed values
    for got,want in (("aOR_disp",f"{or_r:.2f}"),("lo_disp",f"{lo_r:.2f}"),("hi_disp",f"{hi_r:.2f}")):
        if r[got]!=want: ci_p_pair_bad.append((r["model"],r["term"],got,r[got],want))
    # (iii) confirm the model's CI multiplier equals qt(0.975,residual_df)
    if abs(tc-float(r["ci_multiplier"]))>5e-4: recompute_bad.append((r["model"],r["term"],"ci_mult"))
check("audit: aOR/CI/P recomputed from coef,SE & residual df reproduce stored values (single object)", not recompute_bad, str(recompute_bad[:8]))
check("audit: 2-dp display strings are single-rounded from full precision (no double-round)", not ci_p_pair_bad, str(ci_p_pair_bad[:8]))
# residual df identity: dfres == max(1, design_df - rank + 1)
dfid_bad=[(r["model"],r["term"]) for r in AR if int(r["residual_df"])!=max(1,int(r["design_df"])-int(r["rank"])+1)]
check("audit: residual_df == degf - rank + 1 for every row", not dfid_bad, str(dfid_bad[:5]))
# Holm >= raw within every model (adjustment never lowers a p)
holm_bad=[]
for r in AR:
    try:
        if float(r["p_holm"]) < float(r["p_raw"])-1e-12: holm_bad.append((r["model"],r["term"],r["p_raw"],r["p_holm"]))
    except ValueError: pass
check("audit: Holm p >= raw p within every model", not holm_bad, str(holm_bad[:5]))

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

# ---------- (4) round-7 + round-8 content ----------
must={
 "S7b corrected total PSU 59":"59" in supptxt and "Total number of PSUs" in supptxt,
 "S7b df 28 DR responders":"Design degrees of freedom" in supptxt and "28" in supptxt,
 "no wrong 'strata − PSUs' header":"strata − PSUs" not in supptxt and "strata - PSUs" not in supptxt,
 "no wrong 'PSUs 2' row":"| 31 | 2 |" not in supptxt,
 "degf() cited":"survey::degf" in text,
 "residual-df explanation (minus model rank plus one)":"minus model rank plus one" in text_u or "model rank + 1" in text_u,
 "moderate-or-worse in results":"53.4" in mdtxt and "moderate-or-worse" in mdtxt,
 "section renamed advanced disease":"Discordance in advanced retinal disease" in mdtxt,
 "no 'Potentially vision-threatening'":"Potentially vision-threatening" not in mdtxt,
 "eye-care exploratory label":"exploratory" in mdtxt and "no verifiable pre-registration" in mdtxt,
 "scheme B: no 'single a-priori hypothesis'":"single a-priori hypothesis" not in mdtxt,
 "t-based CI convention stated":"residual degrees of freedom" in mdtxt,
 "no per-10-year row":"per 10 years" not in mdtxt and "per-10-year" not in mdtxt,
 "missingness wording softened":"do not establish that the missingness mechanism is ignorable" in text_u,
 "MI not independent replications (S4b)":"independent replications" in supptxt and "not 20 independent" in supptxt,
 "MI above-1 phrasing (no 'every imputation')":"above 1 in each" in text_u or "lay above 1 in each" in text_u,
 "missingness mechanism subtable":"(c) Missingness-mechanism models" in supptxt and "not** with the outcome" in supptxt,
 "gradability extended model":"extended" in supptxt and "10.13" in supptxt,
 "discordance selection sensitivity":"Discordance-specific selection sensitivity" in supptxt,
 "system-design softened": "weighting cannot address unmeasured selection" in text_u,
 "NHIS no 2.7-fold multiple":"2.7-fold" not in mdtxt,
 "NHIS reviewer sentence":"cannot be attributed specifically to diagnostic unawareness" in mdtxt,
 "terminology: no 'diabetic retinopathy cohort'":"diabetic retinopathy cohort" not in mdtxt.lower(),
 "Figure 2 severity gradient embed":"Fig2_gradient_forest.png" in mdtxt,
 "Figure 3 objective-vs-selfreport embed":"Fig3_eyecare_dots.png" in mdtxt,
 "code availability names the repo":"Code availability" in mdtxt and "github.com/teamhuang/eye3-nhanes-diagnosis-care-gap" in mdtxt,
 "numbers_v7 referenced":"numbers_v7.csv" in mdtxt and "numbers_v7.csv" in supptxt,
 # ---- round-8 additions ----
 "regression-audit table heading (new S2)":"Supplementary Table S2" in supptxt,
 "S7c exam row 0.30 (0.10–0.92)":"0.30 (0.10–0.92)" in nd(supptxt),
 "S7c exam P 0.038 & Holm 0.266":"0.038" in supptxt and "0.266" in supptxt,
 "S7c residual df 13 stated":"residual df 13" in text_u or "Residual df" in supptxt,
 "S7c DR pir 1.34 (0.92–1.96)":"1.34 (0.92–1.96)" in nd(supptxt),
 "S7c sev3 0.43 (0.15–1.21) not 1.22":"0.43 (0.15–1.21)" in nd(supptxt) and "0.43 (0.15–1.22)" not in nd(supptxt),
 "S9 AMD age+severity heading":"Supplementary Table S9" in supptxt,
 "S9 age 0.92 (0.89–0.95)":"0.92 (0.89–0.95)" in nd(supptxt),
 "S9 late 0.18 (0.08–0.37) not 0.38":"0.18 (0.08–0.37)" in nd(supptxt) and "0.18 (0.08–0.38)" not in nd(supptxt),
 "S9 early-AMD strata 99.1/92.4/78.4":"99.1 (95.6–99.8)" in nd(supptxt) and "78.4 (72.9–82.9)" in nd(supptxt),
 "S8 weight decomposition 0.637/0.569":"0.637" in supptxt and "0.569" in supptxt,
 "S8 1/P factor range 1.76":"1.76" in supptxt and "Inverse-probability factor" in supptxt,
 "S8 combined-weight 110,456/115,872":"110,456" in supptxt and "115,872" in supptxt,
 "S8 floor non-binding":"never binding" in supptxt,
 "S8 extended model_n 3,687":"3,687" in supptxt,
 "S8 ESS only limited check":"limited stability check" in supptxt or "only a **limited" in supptxt,
 "NHIS glaucoma/cataract moved out (new S4)":"Supplementary Table S4" in supptxt and "21.17 (20.37–21.96)" in supptxt,
 "S4c no artefact claim":"not an artefact of the chosen covariate set" not in supptxt,
 "S4c does-not-test robustness":"does not test" in supptxt and "consistency of the income association" in supptxt,
 "Discussion no 'sight-threatening'":"sight-threatening" not in mdtxt,
 "Discussion retinal abnormalities":"retinal abnormalities, patient-reported diagnosis" in mdtxt,
 "Discussion targeted not broad screening":"speaks to the effectiveness or cost-effectiveness of broader population screening" in mdtxt,
 "Discussion novelty not within-individual pairing":"already paired objective grading with a patient-reported diagnosis" in mdtxt,
 "Intro no 'specified for this study before estimation'":"specified for this study before estimation" not in mdtxt,
 "Intro four objectives sentence":"aimed to (i)" in mdtxt and "(iv)" in mdtxt,
 "Table3 AMD insurance not fitted row":"Insurance was not estimable in the AMD model" in mdtxt,
}
for nm,c in must.items(): check(nm, c)

# ---------- (4b) cover-letter fixes ----------
cltxt_n=re.sub(r"\s+"," ",cltxt)  # cover letter is hard-wrapped; match on collapsed whitespace
check("CL no false 'declarations completed' claim","disclosure are completed" not in cltxt_n and "interests and AI-use disclosure are completed" not in cltxt_n, "still claims complete")
check("CL: declarations completed, only DOI pending","the one remaining item is the citable code doi" in cltxt_n.lower() and "github.com/teamhuang/eye3-nhanes-diagnosis-care-gap" in cltxt_n)
check("CL drops '118 checks' count emphasis","118 checks" not in cltxt_n)
check("CL eye-care overclaim replaced","most robust correlate" not in cltxt_n)
check("CL eye-care reviewer sentence present","clearest association with patient-reported diagnosis" in cltxt_n and "did not consistently withstand multiple-testing correction" in cltxt_n)
check("CL novelty vs 2025 ref acknowledged","not, in itself, our novelty" in cltxt_n)
check("CL references numbers_v7","numbers_v7.csv" in cltxt_n)

# ---------- (4c) submission declarations FILLED + NO-FABRICATION guards ----------
# author supplied byline/funding/contributions/COI this round; verify they are FILLED and that no
# AUTHOR INPUT placeholder survives in the manuscript (the code DOI stays an explicit placeholder).
check("main: real authors present","Jianhuang Huang" in mdtxt and "Jing Wang" in mdtxt)
check("main: real affiliations present","Affiliated Hospital of Putian University" in mdtxt and "Shandong First Medical University" in mdtxt)
check("main: corresponding emails present","teamhuang@sina.com" in mdtxt and "13273530801@163.com" in mdtxt)
check("main: funding = no-specific-grant statement","received no specific grant from any funding agency" in mdtxt)
check("main: author contributions assigned (named CRediT)","Jianhuang Huang: Conceptualization, Methodology, Software" in mdtxt and "Jing Wang: Conceptualization, Resources, Supervision" in mdtxt)
check("main: competing-interests declaration present","The authors declare no competing financial or non-financial interests." in mdtxt)
check("main: AI/LLM disclosure present (truthful)","AI coding assistant (QoderWork" in mdtxt and "No AI tool meets the ICMJE authorship criteria" in mdtxt)
check("main: NO leftover AUTHOR INPUT placeholder","AUTHOR INPUT REQUIRED" not in mdtxt)
check("main: code-availability cites real public GitHub repo","github.com/teamhuang/eye3-nhanes-diagnosis-care-gap" in mdtxt and "releases/tag/v10.0.0" in mdtxt)
check("Discussion gap-direction logic fixed (overstate apparent gap)","overstate the apparent diagnosis gap" in mdtxt)
check("CL: signed by corresponding author","Jianhuang Huang" in cltxt_n and "teamhuang@sina.com" in cltxt_n and "2026-10-29" in cltxt_n)
check("CL: internal author work-list removed from cover letter","Final steps before clicking submit" not in cltxt_n and "Checklist to complete" not in cltxt_n)
_SUBMIT=ROOT/"manuscript"/"SUBMISSION_CHECKLIST.md"
_subtxt=open(_SUBMIT,encoding="utf-8").read() if _SUBMIT.exists() else ""
check("work-list retained in SUBMISSION_CHECKLIST.md","FINAL SUBMISSION-FILE VERIFICATION" in _subtxt and "Zenodo" in _subtxt)
# NO-FABRICATION: a REAL-looking Zenodo/DOI or ORCID must NOT appear (would be invented)
fake_doi=re.search(r"10\.\d{4,5}/zenodo\.\d+", mdtxt+cltxt_n)
check("no fabricated Zenodo DOI anywhere", not fake_doi, str(fake_doi.group(0) if fake_doi else ""))
fake_orcid=re.search(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", mdtxt)
check("no fabricated ORCID in manuscript", not fake_orcid, str(fake_orcid.group(0) if fake_orcid else ""))
# The Round-11 polish removed the defensive "no DOI yet" sentence; the substantive guarantee is that
# availability pins a resolvable version tag and mints NO unbacked DOI. Enforce that instead.
check("code availability pins a resolvable version tag, cites no DOI",
      "releases/tag/v10.0.0" in mdtxt and not re.search(r"\bdoi\.org/10\.5281|\b10\.5281/", mdtxt),
      "")
# STROBE must use official items 1-22 and give real line anchors (no leftover TBD)
STROBE=ROOT/"manuscript"/"STROBE_checklist.md"
strotxt=open(STROBE,encoding="utf-8").read() if STROBE.exists() else ""
check("STROBE has official item 22 (Funding)","| 22 | Funding" in strotxt)
check("STROBE has official item 12d cross-sectional text","Cross-sectional:" in strotxt and "sampling strategy" in strotxt)
check("STROBE no leftover TBD page column","TBD" not in strotxt)
check("STROBE uses line anchors","M15" in strotxt)
check("STROBE marks not-applicable with reason","Not applicable" in strotxt and "no follow-up" in strotxt)

# ---------- (5) stale/forbidden ----------
forbidden=["89.1","the only US nationally representative","is unmeasured in nationally","⁶⁻ ",
 "load-bearing","was protective","EJE","Running head","Significance statement","reviewer requests","corroboration",
 "0.11–0.83","1.08–2.07","0.17–1.10","0.01–0.21","0.29–9.04","0.94–1.91","0.99–1.94","0.62–5.60",
 "1.09–1.94","1.12–1.96","0.30–1.52","0.48–3.44","0.53–4.67","0.61–1.28","0.32–2.11","0.31–7.82",
 "0.34–2.90","0.39–3.04","0.65–5.58","0.20–2.61","0.29–2.74","0.46–1.88","0.74–2.17","0.35–3.33","0.32–1.53","0.40–1.86",
 "0.97–1.02), 1.00","per 10 years","2.7-fold","strata − PSUs","who gets examined shapes who gets diagnosed",
 # ---- round-8 removals ----
 "consistent with, though not proving, MAR","consistent with — though does not prove — ignorability","consistent with, though not proving",
 "confirming that the income signal","is not an artefact of the chosen covariate set",
 "no small set of weights dominated","did not dominate","1,733","104,939",
 "numbers_v5.csv","numbers_v6.csv",
 "sight-threatening","opportunistic imaging-based screening","specified for this study before estimation",
 "screening failure","non-adherence","missed care","positive in every imputation"]
for tok in forbidden: check(f"no forbidden {tok!r}", nd(tok) not in text_u, f"found {tok}")
for tok in ["28–29 degrees","29 Taylor"]: check(f"no stale {tok}", tok not in text_u)
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
for fig in ["Fig1_flowchart","Fig2_gradient_forest","Fig3_eyecare_dots"]: check(f"embed {fig}", fig+".png" in mdtxt)
for fig in ["FigS1_gradability_ipw","FigS2_nhis_amd"]: check(f"embed {fig}", fig+".png" in supptxt)

print("="*60); print(f"PASSED: {len(oks)}   FAILED: {len(fails)}"); print("="*60)
if fails:
    print("*** FAILURES ***")
    for n,c,d in fails: print(f"  [FAIL] {n}: {d}")
    sys.exit(1)
print("ALL CHECKS PASS"); sys.exit(0)
