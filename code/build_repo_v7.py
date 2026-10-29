#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""build_repo_v7.py — assemble submission_repo_v7/, a DEPOSIT-READY public analysis repository
(no individual-level data), ready to be pushed to GitHub and archived on Zenodo for a version DOI.
Includes code, result tables, numbers_v7.csv, verification report, figures, manuscript, LICENSE,
README, CITATION.cff, .zenodo.json and a .gitignore that keeps person-level data out."""
import os, shutil, json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"submission_repo_v7"
if OUT.exists(): shutil.rmtree(OUT)
(OUT/"code").mkdir(parents=True); (OUT/"results"/"tables").mkdir(parents=True); (OUT/"figures").mkdir(parents=True); (OUT/"manuscript").mkdir()

CODE=["build_dataset_v2.py","survey_analysis_v4.R","attrition_v4.R","consolidate_v4.py",
      "survey_analysis_v5.R","consolidate_v5.py","survey_analysis_v6.R","consolidate_v6.py",
      "survey_analysis_v7.R","consolidate_v7.py","probe_design_df.R",
      "build_figures_v4.py","build_figures_v5.py","build_figures_v6.py",
      "verify_v4.py","verify_v5.py","verify_v6.py","verify_v7.py",
      "build_verification_report_v7.py","build_repro_bundle_v7.py","md_to_docx_ar.mjs"]
for c in CODE:
    s=ROOT/"code"/c
    if s.exists(): shutil.copy(s, OUT/"code"/c)
for t in sorted((ROOT/"results"/"tables").glob("*.csv")):
    shutil.copy(t, OUT/"results"/"tables"/t.name)
vr=ROOT/"results"/"tables"/"verification_report.txt"
if vr.exists(): shutil.copy(vr, OUT/"results"/"tables"/"verification_report.txt")
for f in sorted((ROOT/"figures").glob("*")):
    if f.is_file(): shutil.copy(f, OUT/"figures"/f.name)
for m in ["题目3手稿.md","Supplementary_Materials_v7.md","STROBE_checklist.md","cover_letter.md",
          "RESPONSE_TO_REVIEWER_v8.md","README.md"]:
    s=ROOT/"manuscript"/m
    if s.exists(): shutil.copy(s, OUT/"manuscript"/m)

(OUT/".gitignore").write_text(
"# never publish individual-level / derived person-level data\n"
"data/\n*.xpt\n*.XPT\nanalytic_dataset*.csv\n*.sas7bdat\n"
"# build artefacts\n__pycache__/\n*.pyc\nreproducibility_v*/\nsubmission_repo_v*/\n*.zip\n"
".Rhistory\n.RData\n",encoding="utf-8")

(OUT/"LICENSE.md").write_text(
"# Licences\n\n"
"**Code** in `code/` is released under the MIT License (see below).\n\n"
"**Manuscript text, tables and figures** are intended for release under CC BY 4.0 upon publication "
"(Scientific Reports default); until then they are the authors' work.\n\n"
"**Data:** no individual-level data are included. NHANES and NHIS are public-use files from NCHS/CDC "
"(see https://wwwn.cdc.gov/nchs/nhanes/); users download them directly and run `code/build_dataset_v2.py`.\n\n"
"## MIT License (code)\n\nPermission is hereby granted, free of charge, to any person obtaining a copy "
"of this software and associated documentation files, to deal in the Software without restriction, "
"including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, "
"and/or sell copies of the Software, subject to the following: the above copyright notice and this "
"permission notice shall be included in all copies. THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT "
"WARRANTY OF ANY KIND.\n\nCopyright (c) 2026 [AUTHOR INPUT: copyright holder name]\n",encoding="utf-8")

README="""# Analysis repository — Objectively graded retinal disease, self-reported diagnosis, and eye-care utilisation in US adults (NHANES 2005-2008)

Deposit-ready archive accompanying the *Scientific Reports* submission. **Contains no individual-level
data** (see .gitignore / LICENSE): you download the public NHANES/NHIS files yourself and rebuild.

## Layout
- `code/` — all R and Python scripts (analysis + consolidation + figures + audit).
- `results/tables/` — every `t_*.csv` output plus the single source of truth `numbers_v7.csv` and `verification_report.txt`.
- `figures/` — publication figures (PNG + PDF).
- `manuscript/` — main text, Supplementary Materials, STROBE checklist, cover letter, reviewer response.

## Environment
R 4.3.3 (packages `survey`, `mice`); Python 3.10 (`pandas`, `numpy`, `matplotlib`, `scipy`).
Fixed seed 20261029; single-threaded BLAS set before import. Scripts reference the path `C:/eye3/`
(a junction to the project root) — change it to your own checkout, or set the CSV/TBL paths at the top
of each R script.

## Reproduce end-to-end
```bash
# 1. download NHANES 2005-2008 OPXRET/VIQ/DIQ/DEMO/HUQ/HIQ + NHIS 2016 Sample Adult into data/raw/
python code/build_dataset_v2.py          # -> data/processed/analytic_dataset_v2.csv
Rscript code/survey_analysis_v4.R
Rscript code/attrition_v4.R
Rscript code/survey_analysis_v5.R
Rscript code/survey_analysis_v6.R
Rscript code/survey_analysis_v7.R        # per-model df/CI/P audit + IPW decomposition + AMD age/severity + phenotype overlap
Rscript code/probe_design_df.R
python code/consolidate_v4.py && python code/consolidate_v5.py && python code/consolidate_v6.py && python code/consolidate_v7.py
python code/build_figures_v6.py
python code/verify_v7.py                 # 218 checks incl. independent re-derivation of every aOR/CI/P
python code/build_verification_report_v7.py
```
`verify_v7.py` exits non-zero if any manuscript/supplement/cover-letter number drifts from
`numbers_v7.csv`, if any denominator assertion fails against a raw recount, or if any model's
confidence interval / P value cannot be reproduced from its coefficient, standard error and residual
degrees of freedom.

## Getting a version DOI (corresponding author, ~10 minutes)
1. Create a **public** GitHub repo and push this folder:
   `git init && git add -A && git commit -m "v7 analysis archive" && git remote add origin <URL> && git push -u origin main`
2. Go to https://zenodo.org → Log in → "New community/Deposition" → **Upload** or link the GitHub repo
   (GitHub integration auto-archives a concept + version DOI on each release/tag).
3. Fill the metadata (title, authors, ORCIDs, keywords, license MIT/CC-BY) — a starting `.zenodo.json`
   is provided here; edit the author fields.
4. Publish → copy the version DOI (e.g. `10.5281/zenodo.XXXXXXX`) into the manuscript's
   **Code availability** statement and this README. **Do not** cite a DOI that has not been minted.
"""
(OUT/"README.md").write_text(README,encoding="utf-8")

cff={"cff-version":"1.2.0","message":"If you use this software, please cite it as below.",
 "title":"Analysis code: Objectively graded retinal disease, self-reported diagnosis, and eye-care utilisation in US adults (NHANES 2005-2008)",
 "version":"7.0.0","date-released":__import__("datetime").date.today().isoformat(),
 "repository-code":"[AUTHOR INPUT: GitHub URL]","license":"MIT",
 "authors":[{"name":"[AUTHOR INPUT: Family, Given]"}],
 "keywords":["NHANES","diabetic retinopathy","age-related macular degeneration","diagnosis gap","survey methods"]}
(OUT/"CITATION.cff").write_text(json.dumps(cff,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

zen={"title":"Objectively graded retinal disease, self-reported diagnosis, and eye-care utilisation in US adults (NHANES 2005-2008): analysis archive v7",
 "version":"v7.0.0","license":"MIT","upload_type":"software","keywords":["NHANES","NHIS","diabetic retinopathy","AMD","diagnosis gap","care gap","survey methodology","STROBE"],
 "creators":[{"person":{"name":"[AUTHOR INPUT: Family, Given]","affiliation":"[AUTHOR INPUT]","orcid":"[optional]"}}],
 "description":"R/Python analysis code, consolidated result tables (numbers_v7.csv) and figures reproducing every number in the manuscript. Contains no individual-level data.",
 "access_right":"open"}
(OUT/".zenodo.json").write_text(json.dumps(zen,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

nfiles=sum(1 for _ in OUT.rglob("*") if _.is_file())
print("submission_repo_v7 assembled:",nfiles,"files")
print("next: git init + commit + push (see README DOI steps)")
