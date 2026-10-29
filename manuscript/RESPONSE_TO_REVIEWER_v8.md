# Response to Pre-Submission Review (v6 report) — point by point

Manuscript: *Objectively graded retinal disease, self-reported diagnosis, and eye-care utilisation in US adults (NHANES 2005–2008)*. All analysis outputs are consolidated in `results/tables/numbers_v7.csv` and re-audited by `code/verify_v7.py` (234 checks, all pass). Every fix below was made in the working files; nothing is claimed to be done that is not present in the text/tables/scripts. Items are classified **BLOCKING** (a claim that does not hold as written / methodological error) or **OBSERVATION** (improvement).

## P0 — must fix before submission

**1 (BLOCKING). Regression residual degrees of freedom; aOR/CI/P from one model object.**
Adopted. `code/survey_analysis_v7.R` §19 fits each reported model once and exports design df (`survey::degf`), model rank, residual df, the exact `qt(0.975, df)` multiplier and, per term, coefficient/SE/aOR/CI/raw-P/Holm-P — all from the *same* `svyglm` object — into `t_model_audit_v7.csv`, surfaced as **Supplementary Table S7c**. We confirmed empirically that `survey` infers at residual df = `degf − rank + 1`: the DR eye-care model has design df 22, rank 10, residual df **13**, and that single df reproduces **both** exam aOR **0.30 (0.10–0.92)** and **P = 0.038** (Holm 0.266). `verify_v7.py` independently re-derives every audit row from coef/SE/residual-df (scipy t), checks the residual-df identity and Holm ≥ raw. The 2-dp display strings are single-rounded from full precision (we found and fixed a double-rounding error: 1.9649 had been shown as 1.97 instead of 1.96, 1.215 as 1.22 instead of 1.21, 0.375 as 0.38 instead of 0.37).

**2 (BLOCKING). S8 IPW weight labels / interpretation.**
Adopted. S8(b) is decomposed into separate labelled rows: gradability probability P (base 0.637–0.938, extended 0.569–1.000), inverse-probability factor 1/P (base 1.07–1.57, extended 1.00–1.76), combined survey×IPW weight (the 16,566/110,456-type numbers), Kish ESS with formula and scope, the 0.05 truncation, and the model complete-case n. Corrections: the 0.05 floor was **never binding** (min probability 0.569, no truncation); the **extended model was fitted on 3,687 rows vs 6,797** for the base model (missing-covariate respondents get P = 1), so it reweights a subset and targets a slightly different effective population — now stated. The ESS claim is softened to a *limited* stability check, not proof that no weights dominated.

**3 (BLOCKING). STROBE official 22-item numbering.**
Adopted. `STROBE_checklist.md` rewritten against the official STROBE Statement items **1–22 with sub-items (a–e)**; the earlier custom numbering is discarded. Design-inapplicable sub-items (6b matching, 14c cohort follow-up, 16c relative→absolute risk) are marked **Not applicable with reason**. The location column now gives **real line anchors** in the submitted files (`M##`/`S##`), not "TBD".

## P1 — substantive

**4 (OBSERVATION). Novelty vs the 2025 same-cycle NHANES study (ref 9).** Adopted. The Discussion states that within-respondent imaging–questionnaire pairing is "not, by itself, a novelty"; contributions re-ordered to parallel DR + AMD with disease-specific denominators, severity-stratified discordance, the exam link with a reciprocal-direction caveat, systematic sensitivity analyses, and NHIS as auxiliary context. Cover letter mirrors this.

**5 (OBSERVATION). Abstract compression / demote eye-care.** Adopted. Eye-care is now "In an exploratory adjusted analysis…"; Abstract trimmed to ≤200 words (enforced).

**6 (OBSERVATION). "specified before estimation".** Adopted. Replaced with "The present analysis focuses on these four objectives," plus an explicit note that primary descriptive estimands were fixed before estimation while the secondary covariate/eye-care analyses were not pre-registered (exploratory).

**7 (OBSERVATION). Terminology; GA/NV mutual exclusivity.** Adopted. §22 verifies **0 of 55** late-AMD participants carry both geographic atrophy and neovascular disease in the same worse eye, so 32 + 23 = 55 is exact and non-double-counted; S7(a) notes the single-worse-eye rule could miss a bilateral-mixed eye. Legends keep "retinopathy among adults with diabetes."

**8 (OBSERVATION). AMD age gradient vs severity.** Adopted with new analysis. **S9**: age adjusted for stage stays **0.92 (0.89–0.95)** with late stage independently **0.18 (0.08–0.37)**; within early AMD only the gap still falls 99.1% → 92.4% → 78.4%. So the age gradient is not a severity proxy.

**9 (OBSERVATION). Eye-care ≠ adherence.** Confirmed; forbidden framing (screening failure / non-adherence / missed care) absent and now enforced.

**10 (OBSERVATION). Two Discussion overreaches.** Adopted. "sight-threatening retinal disease" → "retinal abnormalities…"; the opportunistic/broad-screening sentence replaced with a targeted framing that explicitly disclaims screening-effectiveness/cost-effectiveness claims.

**11 (OBSERVATION). Multiple imputation / "MAR".** Adopted. "consistent with … MAR" removed; S4b states the 20 imputations are **not independent replications** and that trace plots / fraction-of-missing-information were not generated.

**12 (BLOCKING). S4c logic error.** Adopted. The invalid "the drop-both model confirms the income signal is not an artefact" claim is deleted; S4c now says that model "does not test — and is not interpreted as evidence for — the robustness of the income association."

**13 (OBSERVATION). AMD insurance descriptive out of the model table.** Adopted. Table 3 AMD column now reads only "not included (complete separation)"; the raw counts (177/211 insured, 14/14 uninsured) moved to **S1**.

**14 (OBSERVATION). NHIS Table 5 trim.** Adopted. Table 5 keeps DR, macular degeneration and the eye-care items; glaucoma/cataract moved to **S5c** with an explicit note that NHIS "ever told cataract" ≠ NHANES cataract-**surgery** history and is not compared side-by-side.

## P2 / consistency / cover letter

**15 (BLOCKING). Cover-letter "declarations completed" vs placeholders.** Adopted. The false claim is removed; the cover letter and manuscript now carry honest, clearly-marked **AUTHOR INPUT** placeholders for funding / contributions / competing interests / AI-use / code DOI, and state we do not claim they are finished.

**16 (OBSERVATION). "118 checks".** Adopted. The count emphasis is removed; the cover letter describes what the checks actually verify (denominators, design/residual df, CI/P consistency).

**17 (OBSERVATION). Cover-letter eye-care overclaim.** Adopted. Replaced with: severity showed the clearest association; socioeconomic and eye-care estimates were less precise and did not consistently withstand multiple-testing correction.

## Post-review additions (this round)
Beyond the numbered points, we completed the submission logistics the reviewer flagged: (i) a truthful **AI/LLM-use disclosure** and structured CRediT/funding/COI templates (author-only facts left as marked placeholders, not fabricated); (ii) a **deposit-ready public repository** `submission_repo_v7/` (code + result tables + `numbers_v7.csv` + figures + manuscript, **no individual-level data**, MIT-licensed, with `README`/`CITATION.cff`/`.zenodo.json` and step-by-step Zenodo DOI instructions) — the DOI itself must be minted by the corresponding author and is explicitly marked "not yet created"; (iii) **figures visually verified** against `numbers_v7`; (iv) STROBE **line anchors** replacing "TBD"; (v) a **`SUBMISSION_CHECKLIST.md`** listing exactly what the authors must still fill.

## Cross-file consistency
DR 319/313/187, AMD 441/436/226, severity 197+85+31=313, moderate-or-worse 85+31=116, AMD 381+55=436, late 32+23=55 (GA∩NV-both = 0), NHIS 2.45%, exam 0.30 (0.10–0.92) — all reproduced from source in `verification_report.txt`.

## What remains OPEN (author-side, not fabricated)
Author byline/affiliations/email, funding grant numbers, real competing interests, confirmation of the AI-use wording, the corresponding-author signature, and the **minted code DOI** are facts only the authors can supply; they are left as marked placeholders. Typeset **page** numbers are unavailable (no PDF renderer here), so STROBE uses line anchors. Once these are completed and `verify_v7.py` is re-run, v7 is ready to submit to *Scientific Reports* (readiness to submit ≠ guarantee of editorial or peer-review acceptance).
