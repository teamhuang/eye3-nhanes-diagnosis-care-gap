# Analysis repository — Objectively graded retinal disease, self-reported diagnosis, and eye-care utilisation in US adults (NHANES 2005-2008)

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
