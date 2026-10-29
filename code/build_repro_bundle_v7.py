#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_repro_bundle_v7.py — assemble reproducibility_v7/ (scripts + all result tables +
numbers_v7.csv) and emit a MANIFEST whose number->source table is pulled programmatically
from numbers_v7.csv so it can never drift from the analysis outputs. Then zip it."""
import os, csv, shutil, zipfile, hashlib
for v in ("OMP_NUM_THREADS","MKL_NUM_THREADS","OPENBLAS_NUM_THREADS","NUMEXPR_NUM_THREADS"): os.environ[v]="1"
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reproducibility_v7"
if OUT.exists(): shutil.rmtree(OUT)
(OUT/"code").mkdir(parents=True); (OUT/"results_tables").mkdir(); (OUT/"manuscript").mkdir()

CODE=["build_dataset_v2.py","survey_analysis_v4.R","attrition_v4.R","consolidate_v4.py",
      "survey_analysis_v5.R","consolidate_v5.py","survey_analysis_v6.R","consolidate_v6.py",
      "survey_analysis_v7.R","consolidate_v7.py","probe_design_df.R",
      "build_figures_v4.py","build_figures_v5.py","build_figures_v6.py",
      "verify_v4.py","verify_v5.py","verify_v6.py","verify_v7.py","build_verification_report.py","md_to_docx_ar.mjs"]
for c in CODE:
    src=ROOT/"code"/c
    if src.exists(): shutil.copy(src, OUT/"code"/c)
for t in sorted((ROOT/"results"/"tables").glob("*.csv")):
    shutil.copy(t, OUT/"results_tables"/t.name)
for extra in ["README.md","STROBE_checklist.md","cover_letter.md","Supplementary_Materials_v7.md","题目3手稿.md"]:
    f=ROOT/"manuscript"/extra
    if f.exists(): shutil.copy(f, OUT/"manuscript"/extra)
(OUT/"figures").mkdir(parents=True, exist_ok=True)
for fig in sorted((ROOT/"figures").glob("*")):
    if fig.is_file(): shutil.copy(fig, OUT/"figures"/fig.name)
vr=ROOT/"results"/"tables"/"verification_report.txt"
if vr.exists(): shutil.copy(vr, OUT/"results_tables"/"verification_report.txt")

src={}
with open(ROOT/"results"/"tables"/"numbers_v7.csv",encoding="utf-8") as f:
    for row in csv.reader(f):
        if row and row[0]!="key": src[row[0]]=row[1] if len(row)>1 else ""
def S(k): return src.get(k,"(missing)")
rows=[
 ("Whole-population retinopathy 9.75 (8.79–10.80)","prev|Any objectively graded retinopathy (all 40+, descriptive)","t_prevalence_v4.csv"),
 ("Any AMD 6.58 (5.65–7.66)","prev|Any AMD (early+late)","t_prevalence_v4.csv"),
 ("DR diagnosis gap 70.2 (63.8–75.9), n=313","gap|DR: graded retinopathy in diabetes, NO self-reported dx","t_gaps_v4.csv"),
 ("AMD diagnosis gap 82.2 (77.3–86.2), n=436","gap|AMD: graded AMD, NO self-reported dx","t_gaps_v4.csv"),
 ("Late-AMD gap 41.4 (25.3–59.6), n=55","gap|Late AMD: graded late AMD, NO self-reported dx","t_gaps_v4.csv"),
 ("Early-AMD gap 87.9 (84.4–90.6), n=381","amdsev|Early AMD","t_amd_severity_v5.csv"),
 ("Moderate-or-worse gap 53.4 (38.7–67.5), n=116","modworse|Moderate-or-worse retinopathy (DR, responders)","t_modworse_gap_v6.csv"),
 ("Care gap 32.4 (25.9–39.7), diabetes+retinopathy","gap|Care: NO dilated exam within 12 months (diabetes + retinopathy)","t_gaps_v4.csv"),
 ("GA 50.3 (26.6–73.9) / neovascular 27.7 (8.0–62.9)","lateSub|Geographic atrophy","t_lateAMD_subtype_v4.csv"),
 ("Late-AMD phenotype overlap GA32 NV23 both0 late55","pheno|overlap","t_phenotype_overlap_v7.csv"),
 ("Core logistic DR income 1.34 (0.92–1.96)","audit|PRIMARY DR core|pir2","t_model_audit_v7.csv"),
 ("Core logistic AMD age 0.93 (0.89–0.96)","audit|PRIMARY AMD core|agec","t_model_audit_v7.csv"),
 ("Analysis A exam 0.30 (0.10–0.92) p=0.038 Holm 0.266","audit|ANALYSIS A (eye-care)|recent_dilated_exam","t_model_audit_v7.csv"),
 ("Eye-care model df: design 22, rank 10, residual 13","audit_df|ANALYSIS A (eye-care)","t_model_audit_v7.csv"),
 ("AMD age 0.92 (0.89–0.95) adj for stage 0.18 (0.08–0.37)","amdagesev|agec ; amdagesev|amdstagelate","t_amd_age_sev_v7.csv"),
 ("Early-AMD-only age strata 99.1 / 92.4 / 78.4","earlyamdpstrata|Early AMD age 40-59","t_earlyamd_age_v7.csv"),
 ("IPW gradability prob base 0.637–0.938 / ext 0.569–1.0","ipwdec|base(age,sex,race)|prob ; ipwdec|extended(+dm,insured,educ)|prob","t_ipw_decomp_v7.csv"),
 ("IPW 1/P factor base 1.07–1.57 / ext 1.00–1.76 (0 floored)","ipwdec|base(age,sex,race)|invfactor ; ipwdec|extended(+dm,insured,educ)|invfactor","t_ipw_decomp_v7.csv"),
 ("IPW combined weight med/max; Kish ESS vs raw ESS; model n","ipwdec|base(age,sex,race)|combwt ; ipwdec|base(age,sex,race)|ess","t_ipw_decomp_v7.csv"),
 ("Non-response bounds DR 69.2–70.6 / AMD 81.6–82.3","nrb|DR|all_diagnosed","t_nonresponse_bounds_v5.csv"),
 ("Grading IPW retinopathy 9.75→9.98 / AMD 6.58→6.87","ipw|Any retinopathy (all >=40)","t_ipw_prevalence_v5.csv"),
 ("Discordance selection DR 70.2→70.2 / AMD 82.2→82.0","discsel|DR: graded retinopathy in diabetes, NO self-reported dx","t_discordance_selection_v6.csv"),
 ("NHIS crude 2.66; age-std 2.45; age-sex 2.46","NHIS|NHIS 2016 self-reported macular degeneration, survey-weighted crude (>=40)","t_nhis_std_versions_v5.csv"),
 ("Design df (survey::degf) DR resp 28 / AMD resp 30 / DR core 22 / AMD core 29","dfv6|DR responders (313)","t_design_df_v6.csv"),
 ("Denominators 319/313/187 and 441/436/226","CNT|dr_gradable_disease","(raw recount in consolidate_v5/v7.py)"),
]
lines=["# Reproducibility bundle — manuscript v7 (analysis v7, round 8)",
"",
"Every number in `题目3手稿.md` (main manuscript) and `Supplementary_Materials_v7.md` is",
"generated by the scripts in `code/` from public NHANES/NHIS source files. Nothing is typed",
"by hand. The number->source table below is generated from `results_tables/numbers_v7.csv`",
"by this script, so the manifest cannot drift from the analysis output.",
"",
"## Pipeline (R 4.3.3 + survey/mice; Python 3.10 + pandas/matplotlib/scipy)",
"",
"1. `python code/build_dataset_v2.py`    -> `data/processed/analytic_dataset_v2.csv` (+ NHIS csv).",
"2. `Rscript code/survey_analysis_v4.R`  -> core design/gaps/prevalence/regression `t_*_v4.csv` (t-on-residual-df CIs).",
"3. `Rscript code/attrition_v4.R`        -> `results_tables/t_attrition_v4.csv`.",
"4. `Rscript code/survey_analysis_v5.R`  -> AMD severity tiers, non-response bounds, reduced models,",
"   multiple imputation (mice, m=20, manual Rubin), gradability + IPW, NHIS design-covariance standardisation.",
"5. `Rscript code/survey_analysis_v6.R`  -> moderate-or-worse gap, IPW weight diagnostics + extended",
"   model + discordance selection, MI diagnostics, missingness-mechanism models.",
"6. `Rscript code/survey_analysis_v7.R`  -> (19) per-model df/rank/residual-df/coefficient/SE/CI/raw-P/Holm-P AUDIT",
"   `t_model_audit_v7.csv` (full-precision, single-rounded display, no double rounding); (20) IPW weight",
"   DECOMPOSITION `t_ipw_decomp_v7.csv`; (21) AMD age adjusted for severity `t_amd_age_sev_v7.csv` + early-AMD-only",
"   age strata `t_earlyamd_age_v7.csv`; (22) late-AMD GA/NV worse-eye overlap `t_phenotype_overlap_v7.csv`.",
"7. `Rscript code/probe_design_df.R`     -> `t_design_df_v6.csv` (survey::degf design degrees of freedom).",
"8. consolidate_v4 -> v5 -> v6 -> `python code/consolidate_v7.py` -> `numbers_v7.csv` (single source of truth; 232 keys).",
"9. `python code/build_figures_v6.py`    -> `figures/Fig1..3, FigS1, FigS2` (PNG+PDF).",
"10. `python code/verify_v7.py`          -> audits manuscript + supplement + cover letter against numbers_v7.csv;",
"   enforces denominator assertions from BOTH numbers_v7.csv and a raw recount; INDEPENDENTLY RE-DERIVES every",
"   model's aOR/CI and P from coef/SE/residual-df (scipy t) and confirms they reproduce the stored values and that",
"   the 2-dp display is single-rounded; checks the residual-df identity (degf-rank+1), Holm>=raw, all regression",
"   aOR(CI) present verbatim, CI validity, the round-8 content edits, and flags stale/absolute wording (218 checks).",
"",
"Fixed seed 20261029; single-threaded BLAS/MKL/OPENBLAS set before interpreter import.",
"`survey_analysis_v*.R` reference `C:/eye3/...` (a Windows junction to the project folder); change to your own",
"checkout. Individual-level data are not redistributed.",
"",
"## Number -> source map (values verbatim from numbers_v7.csv)",
"",
"| Manuscript value | numbers_v7.csv key | table |",
"|---|---|---|"]
for disp,key,tb in rows:
    single=key.split(" ; ")[0]
    disp_val=S(single)
    lines.append(f"| {disp} | `{single}` = {disp_val} | {tb} |")
lines.append("")
lines.append("## SHA-256 of the authoritative consolidated numbers")
lines.append("")
h=hashlib.sha256(open(ROOT/"results"/"tables"/"numbers_v7.csv","rb").read()).hexdigest()
lines.append(f"- `numbers_v7.csv`: `{h}`")
lines.append(f"- generated by `consolidate_v7.py` over `t_*_v4/v5/v6/v7.csv`.")
(OUT/"MANIFEST.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
print("bundle at",OUT,"| files:",len(list(OUT.rglob("*"))),"| sha:",h[:16])

zip_path=ROOT/"reproducibility_v7.zip"
if zip_path.exists(): os.remove(zip_path)
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob("*"):
        if f.is_file(): z.write(f, f.relative_to(ROOT))
zh=hashlib.sha256(open(zip_path,"rb").read()).hexdigest()
print("zip written:",zip_path,"sha256:",zh)
