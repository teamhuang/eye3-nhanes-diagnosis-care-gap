# Project guide — eye3 "diagnosis gap / care gap" (NHANES 2005–2008)

Secondary analysis of NHANES 2005–2008 (main, individual-level) with NHIS 2016 as an auxiliary
cross-survey benchmark. Studies the **diagnosis gap** (objectively graded retinal disease with no
self-reported diagnosis) and **care gap** (no dilated exam within 12 months) for diabetic retinopathy
(in adults with diabetes) and AMD. Target journal: *Scientific Reports*. Working language: English
manuscript, Chinese conversation.

## Where things are
- `manuscript/题目3手稿.md` (+ `.docx`) — main text. `manuscript/Supplementary_Materials_v7.md` (+ `.docx`) — S1–S9.
- `manuscript/STROBE_checklist.md`, `cover_letter.md`, `RESPONSE_TO_REVIEWER_v8.md`, `SUBMISSION_CHECKLIST.md`.
- `code/` — R (survey_analysis_v4–v7.R) + Python (build_dataset, consolidate_v4–v7, build_figures, verify_v7).
- `results/tables/numbers_v7.csv` — **single source of truth** for every reported number; `verification_report.txt`.
- `figures/` — Fig1–3, FigS1–S2 (PNG+PDF), colorblind-safe Okabe-Ito, Arial.
- `submission_repo_v7/` — deposit-ready public code archive (no individual-level data); `reproducibility_v7.zip`.

## Reproduce / audit
```bash
Rscript code/survey_analysis_v7.R
python code/consolidate_v7.py            # -> numbers_v7.csv
python code/verify_v7.py                 # 234 checks; non-zero exit on any drift
python code/build_verification_report_v7.py
python code/build_repro_bundle_v7.py     # -> reproducibility_v7.zip
python code/build_repo_v7.py             # -> submission_repo_v7/
```
Environment: R 4.3.3 (survey, mice); Python 3.10 (pandas/numpy/matplotlib/scipy). Fixed seed 20261029;
single-threaded BLAS. Scripts reference `C:/eye3/` (a Windows junction to this folder).

## Guardrails (project rules)
Never fabricate data; report honest negatives; every number traceable to code; references verified
online; no causal overreach; a seven-dimension self-check + verdict precedes each quantitative
delivery. Author-only facts (names, grants, real conflicts, minted DOI) stay as marked placeholders
until the authors supply them.
