"""Round-13 main-manuscript restructure (docx surgery).

Reviewer's 3-figure / 3-table architecture, applied to the authoritative .docx:
  Figure 1 = study flow (was Fig S1)         Figure S1 = NHIS cross-survey (was Fig 3)
  Figure 2 = dx-inconsistency+severity forest (was Fig 1+2)   Figure S2 = gradability/IPW (new)
  Figure 3 = eye-care association (was Fig S2)
  Table 1  = prevalence (trimmed)            Table 2 = core descriptive (severity + eye-care)
  Table 3  = three model columns             (old Table 4 -> Table S3; old Table 5 -> Table S6)
Every number is copied verbatim from numbers_v7.csv / the current tables (no re-derivation).
"""
from pathlib import Path
import re
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn

ROOT = Path("C:/eye3/manuscript/eye3")
DOCX = ROOT/"manuscript"/"题目3手稿最新版本.docx"
FIG  = ROOT/"figures"
d = Document(str(DOCX))

# ------------------------------------------------------------------ body re-pointing
# ordered (longest / most specific first); run-level replace preserves superscript runs
REPL = [
 ("(Supplementary Table S1, Figure S1)", "(Supplementary Table S1, Figure 1)"),
 ("Supplementary Table S2c reports the design df", "Supplementary Table S3 reports the design df"),
 ("(Supplementary Table S2b)", "(Supplementary Table S3)"),
 ("no self-reported diagnosis (Table 2, Figure 1).", "no self-reported diagnosis (Table 2, Figure 2)."),
 ("not an artefact of non-response (Supplementary Table S2)", "not an artefact of non-response (Supplementary Table S9)"),
 ("had not (Table 2, Figure 1).", "had not (Table 2)."),
 ("severe-or-proliferative retinopathy (Figure 2, left panel; Supplementary Table S3).",
  "severe-or-proliferative retinopathy (Figure 2, panel a; Supplementary Table S2)."),
 ("own responder set (Figure 2, right panel).", "own responder set (Figure 2, panel b)."),
 ("whereas the DR gap was flatter (Supplementary Table S3).", "whereas the DR gap was flatter (Supplementary Table S2)."),
 ("for severe-or-proliferative retinopathy (Figure 2, left panel).", "for severe-or-proliferative retinopathy (Figure 2, panel a)."),
 ("(full model in Supplementary Table S5)", "(full model in Supplementary Table S3)"),
 ("In the fully adjusted model (Table 4, n = 187)", "In the fully adjusted eye-care model (Table 3, n = 187)"),
 ("descriptive difference; Figure S2)", "descriptive difference; Figure 3)"),
 ("education (23.2% vs 14.4%) (Supplementary Table S6).", "education (23.2% vs 14.4%) (Supplementary Table S5)."),
 ("cannot address unmeasured selection (Supplementary Table S6).", "cannot address unmeasured selection (Supplementary Table S5)."),
 ("a dilated examination within 12 months (Table 5).", "a dilated examination within 12 months (Table S6)."),
 ("reported in Supplementary Table S7c and, being outside", "reported in Supplementary Table S6 and, being outside"),
 ("gave 2.46% (2.22\u20132.70) (Figure 3; Supplementary Table S7, S7b).",
  "gave 2.46% (2.22\u20132.70) (Figure S1; Supplementary Table S6)."),
 ("and any health insurance in 87.4% (85.1\u201389.4) (Table 1).",
  "(Table 1; additional NHANES descriptive measures in Supplementary Table S1)."),
 ("(Supplementary Table S8)", "(Supplementary Table S7)"),
 ("(Supplementary Table S9)", "(Supplementary Table S8)"),
 ("Supplementary Table S2c", "Supplementary Table S3"),
 ("Supplementary Table S7b", "Supplementary Table S6"),
]
misses=[]
for old,new in REPL:
    found=False
    for p in d.paragraphs:
        for r in p.runs:
            if old in r.text:
                r.text=r.text.replace(old,new); found=True
        # also try whole-paragraph single-run case
        if not found and len(p.runs)==1 and old in p.runs[0].text:
            pass
    if not found: misses.append(old)
print("BODY misses:", misses)

# ------------------------------------------------------------------ caption rewrites
def set_para(p, text):
    for r in list(p.runs): r._element.getparent().remove(r._element)
    run=p.add_run(text)
    # captions keep their bold state from style; do not force
    return p
def find_para(startswith):
    for p in d.paragraphs:
        if p.text.strip().startswith(startswith): return p
    return None

CAPS = {
 "Figure 1. Diagnosis and eye-care discordance":
   "Figure 1. Study flow and analysis denominators (NHANES 2005\u20132008). Examined adults \u2265 40 with retinal "
   "photography (n = 6,797) split into the retinopathy (gradable image n = 5,704) and AMD (gradable image n = 5,604) "
   "streams. Diagnosis-discordance denominators are restricted to item responders (DR 313 of 319 diabetic adults with "
   "graded retinopathy; AMD 436 of 441 with graded AMD); the 6 and 5 self-report non-responders are excluded. "
   "Complete-case core models further drop participants missing education or income (DR n = 187; AMD n = 226). The two "
   "streams share the same source cohort and are not mutually exclusive.",
 "Figure 2. Diagnosis-gap gradient":
   "Figure 2. Diagnosis discordance and its severity gradient (NHANES 2005\u20132008), survey-weighted % with no "
   "self-reported diagnosis and design-based 95% CIs (logit) among item responders. Panel a: diabetic retinopathy \u2014 "
   "the \u201cAny retinopathy\u201d point is the headline DR gap (70.2%), with the gradient across mild (n = 197), moderate "
   "(n = 85) and severe-or-proliferative (n = 31) NPDR. Panel b: AMD \u2014 \u201cAny AMD\u201d (82.2%) with early (n = 381) "
   "and late (n = 55) AMD. The open marker \u201cMod-or-worse*\u201d (n = 116) is a pooled, overlapping summary of the "
   "moderate and severe strata shown for reference, not a fourth mutually exclusive tier. The two panels are separate "
   "diseases on separate scales and are not a within-figure causal comparison.",
 "Figure 3. Objectively graded versus self-reported AMD":
   "Figure 3. Recent dilated examination and model-adjusted probability of no self-reported diagnosis (DR cohort, "
   "complete-case n = 187). Points are g-computation predicted probabilities (descriptive; a design-based interval was "
   "not reliable for these sparse strata and is not shown): 81.8% without a recent examination vs 62.4% with one. The "
   "adjusted association was aOR 0.30 (0.10\u20130.92), raw P = 0.038, Holm-adjusted P = 0.27. Exploratory cross-sectional "
   "association; no causal interpretation, and it did not survive multiplicity correction.",
 "Figure S1. Study flow":
   "Figure S1. Objectively graded versus self-reported AMD among US adults \u2265 40: NHANES retinal-photograph grading "
   "(2005\u20132008, weighted 6.58%) compared with NHIS self-reported diagnosis (2016, survey-weighted crude 2.66% and "
   "age-standardised 2.45% to the NHANES 40+ structure). The surveys differ in instrument, year and measurement method "
   "and are shown only as a contextual comparison; bars show 95% CIs. The age-standardised CI is conditional on the "
   "fixed NHANES-derived standard weights.",
 "Figure S2. Model-adjusted (g-computation)":
   "Figure S2. Grading-feasibility sensitivity: naive (gradable-only) versus inverse-probability-weighted whole-population "
   "prevalence of any retinopathy and any AMD under a base (age, sex, race) and an extended (+ diabetes, insurance, "
   "education) gradability model. IPW shifts each estimate by \u2264 0.6 percentage points, indicating observable "
   "gradable-vs-ungradable differences do not materially move the descriptive prevalence (full weight decomposition in "
   "Supplementary Table S5).",
 "Table 1. Weighted prevalence":
   "Table 1. Prevalence of objectively graded retinal abnormalities among US adults aged \u2265 40 years, NHANES "
   "2005\u20132008. Unweighted n is the analytic (gradable-image) denominator for each measure, not the case count; the "
   "\u201camong adults with diabetes\u201d row uses n = 884. The final row is population context, not an imaging outcome. "
   "Additional NHANES descriptive measures (insurance, glaucoma, cataract-surgery history) are in Supplementary Table S1.",
 "Table 2. Diagnosis and eye-care discordance":
   "Table 2. Diagnosis discordance by disease severity and eye-care utilisation among item responders, US adults aged "
   "\u2265 40, NHANES 2005\u20132008.",
 "Table 3. Survey-adjusted odds":
   "Table 3. Survey-adjusted odds of having no self-reported diagnosis (given objectively graded disease): DR core, AMD "
   "core, and the exploratory DR eye-care model.",
 "Core model excludes insurance.":
   "Each column is a separate model with its own adjustment set and must not be read as one pooled estimate. DR core "
   "(n = 187) and AMD core (n = 226) adjust for age, sex, education, race/ethnicity and poverty-income ratio; the DR "
   "eye-care model (n = 187) additionally adjusts for insurance and severity and includes recent dilated examination. "
   "Insurance was not estimable in the AMD model (complete separation). Intervals use the design-based t critical value "
   "on each model's residual degrees of freedom, matching the Wald P values; per-model design df, rank, residual df, "
   "t-multiplier, coefficients, SEs, CIs and raw/Holm P are audited in Supplementary Table S3, where Holm-adjusted P "
   "values are tabulated (\u2020 marks the two terms whose Holm-adjusted P < 0.05: AMD age and DR severe/proliferative). "
   "Income is reported once per model and must not be conflated across columns; missing-data sensitivity is in "
   "Supplementary Table S4.",
}
cap_miss=[]
for old,new in CAPS.items():
    p=find_para(old)
    if p is None: cap_miss.append(old); continue
    bold = any(r.bold for r in p.runs if r.bold)
    set_para(p,new)
    if bold:
        for r in p.runs: r.bold=True
print("CAPTION misses:", cap_miss)

# ------------------------------------------------------------------ table rebuild
def set_table(t, data):
    ncols=max(len(r) for r in data)
    while len(t.columns)<ncols: t.add_column(Cm(3))
    while len(t.rows)<len(data): t.add_row()
    while len(t.rows)>len(data): t._tbl.remove(t.rows[-1]._tr)
    while len(t.columns)>ncols:
        for tr in t._tbl.findall(qn('w:tr')):
            tcs=tr.findall(qn('w:tc'))
            if len(tcs)>ncols: tr.remove(tcs[-1])
        grid=t._tbl.find(qn('w:tblGrid'))
        cols=grid.findall(qn('w:gridCol'))
        if len(cols)>ncols: grid.remove(cols[-1])
    for ri,row in enumerate(data):
        for ci in range(ncols):
            t.cell(ri,ci).text = (row[ci] if ci<len(row) else "")

T1=[["Measure","Unweighted n","Weighted % (95% CI)"],
 ["Any objectively graded retinopathy (all \u2265 40)","5,704","9.75 (8.79\u201310.80)"],
 ["Moderate-or-worse retinopathy (all \u2265 40)","5,704","1.35 (1.10\u20131.65)"],
 ["Objective retinopathy among adults with diabetes","884","33.0 (29.3\u201337.0)"],
 ["Any AMD (early or late)","5,604","6.58 (5.65\u20137.66)"],
 ["Late AMD","5,604","0.80 (0.54\u20131.18)"],
 ["Population context \u2014 diagnosed diabetes","6,639","12.05 (10.68\u201313.56)"]]

T2=[["Group","Unweighted n","% with no self-reported diagnosis (95% CI)"],
 ["Diabetes + objective retinopathy (any)","313","70.2 (63.8\u201375.9)"],
 ["Mild NPDR","197","78.1 (71.3\u201383.7)"],
 ["Moderate NPDR","85","64.4 (48.3\u201377.8)"],
 ["Severe-or-proliferative retinopathy","31","15.7 (5.0\u201339.7)"],
 ["Moderate-or-worse (pooled, overlapping)","116","53.4 (38.7\u201367.5)"],
 ["Objective any AMD","436","82.2 (77.3\u201386.2)"],
 ["Early AMD","381","87.9 (84.4\u201390.6)"],
 ["Late AMD","55","41.4 (25.3\u201359.6)"],
 ["Eye-care utilisation (% not examined within 12 months)","",""],
 ["No dilated exam \u2264 12 mo, all adults with diabetes","1,119","35.8 (31.3\u201340.5)"],
 ["No dilated exam \u2264 12 mo, diabetes + retinopathy","313","32.4 (25.9\u201339.7)"]]

T3=[["Term","DR core (n = 187)","AMD core (n = 226)","DR eye-care (n = 187)"],
 ["Age (per year)","0.99 (0.96\u20131.02)","0.93 (0.89\u20130.96) \u2020","1.00 (0.97\u20131.03)"],
 ["Male vs female","1.29 (0.45\u20133.71)","0.99 (0.32\u20133.08)","1.09 (0.35\u20133.38)"],
 ["Education <HS vs \u2265HS","0.67 (0.28\u20131.61)","0.82 (0.31\u20132.21)","0.90 (0.26\u20133.07)"],
 ["Race non-White vs White","1.57 (0.49\u20135.07)","1.56 (0.29\u20138.52)","1.90 (0.58\u20136.23)"],
 ["Poverty-income ratio (per unit)","1.34 (0.92\u20131.96)","0.88 (0.60\u20131.31)","1.49 (1.04\u20132.15)"],
 ["Recent dilated exam (within 12 mo)","\u2014","\u2014","0.30 (0.10\u20130.92)"],
 ["Moderate NPDR (ref = mild)","\u2014","\u2014","0.43 (0.15\u20131.21)"],
 ["Severe/proliferative (ref = mild)","\u2014","\u2014","0.05 (0.01\u20130.24) \u2020"]]

set_table(d.tables[0],T1)
set_table(d.tables[1],T2)
set_table(d.tables[2],T3)

# delete old Table 4 (index 3) and Table 5 (index 4)
for idx in (4,3):
    t=d.tables[idx]; t._tbl.getparent().remove(t._tbl)

# delete captions/notes for old Table 4 / Table 5
for pref in ["Table 4. Eye-care utilisation","Table 5. Cross-survey benchmark",
             "Adjusted model also included","Table 5 is restricted"]:
    p=find_para(pref)
    if p is not None: p._element.getparent().remove(p._element)

# ------------------------------------------------------------------ figure re-embed
EMBED=[("Figure 1","Fig1_flowchart",6.5),("Figure 2","Fig2_gradient_forest",6.5),("Figure 3","Fig3_eyecare_dots",5.0)]
for label,fn,wcm in EMBED:
    for p in d.paragraphs:
        if p.text.strip()==label:
            for r in list(p.runs): r._element.getparent().remove(r._element)
            run=p.add_run(); run.add_picture(str(FIG/(fn+".png")),width=Cm(wcm),height=Cm(5.0))
            break

d.save(str(DOCX))
print("SAVED. tables now:",len(d.tables))
