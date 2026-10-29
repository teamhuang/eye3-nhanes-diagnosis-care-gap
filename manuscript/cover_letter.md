# Cover Letter

Dear Editors,

We submit our original research article, **"Objectively graded retinal disease, self-reported
diagnosis, and eye-care utilisation in US adults (NHANES 2005–2008)"**, for consideration by
*Scientific Reports*.

**What we did.** Using NHANES 2005–2008 — a nationally representative resource that pairs
centrally graded retinal photographs with patient-reported diagnoses and diabetic eye-examination
history in the *same* examined adults aged ≥40 (n = 6,797) — we measured, within individuals, the
concordance between objectively graded disease, patient-reported diagnosis, and eye-care utilisation.
The 2016 NHIS serves only as an auxiliary population-level benchmark, not a paired validation. We
used complex-survey inference throughout (design-weighted logit intervals, design-based **t** for
regression inference at each model's residual degrees of freedom, `subset()`-preserved designs, and
`survey::degf()` design degrees of freedom).

**What we found.** Among adults with diabetes and objectively graded retinopathy who answered the
item, 70.2% (95% CI 63.8–75.9) reported no prior diabetic-eye diagnosis; among those with graded
AMD, 82.2% (77.3–86.2) reported none, including 41.4% with late AMD and 87.9% with early AMD.
Discordance narrowed with severity but did not close, and about one third of high-risk adults with
diabetes had not been examined within 12 months. Disease severity showed the clearest association
with patient-reported diagnosis, whereas estimates for socioeconomic factors and recent eye-care use
were less precise and did not consistently withstand multiple-testing correction.

**Relation to prior work and our contribution.** A 2025 NHANES 2005–2008 study already linked retinal
imaging with the diagnosis questionnaire to examine diabetic-retinopathy awareness in these same
cycles, so pairing objective grading with patient-reported diagnosis within a respondent is not, in
itself, our novelty. Our incremental contributions are (i) a parallel treatment of diabetic
eye-disease and AMD with explicit, disease-specific responder denominators; (ii) presentation of
discordance across clinically relevant severity strata, including moderate-or-worse retinopathy and
late AMD; (iii) relating reported diagnosis to recent dilated eye examination among adults with
diabetes, reported with the reciprocal-direction caveat appropriate to a cross-section; (iv)
systematic, design-aware sensitivity analyses addressing item non-response, covariate missingness and
retinal-image gradability; and (v) an NHIS comparison used only as auxiliary context. We explicitly
frame the "diagnosis gap" as a patient-reported construct, not a chart-confirmed under-diagnosis, and
characterise a historical period rather than current US practice.

**Rigour and reproducibility.** The analyses are supported by version-controlled scripts, a
consolidated results file (`numbers_v7.csv`), and automated checks of analytic denominators,
survey-design and model residual degrees of freedom, and the internal consistency between each
reported odds ratio, its confidence interval and its P value (all read from the same fitted model
object). We have addressed prior methodological review points on construct validity, missing data
(complete-case plus missing-indicator, reduced-model and multiple-imputation sensitivity, with the
imputation framed as a limited stability check rather than independent replication), grading
feasibility (inverse-probability weighting with a full weight decomposition — reporting the
gradability probability, the inverse-probability factor and the combined survey weight separately,
and clarifying that the 0.05 floor was non-binding — plus a discordance-specific selection check),
design-based standardisation, and a supplementary audit of every model's degrees of freedom.

This article is original, not under consideration elsewhere, and all authors have approved the
submission in its submitted form. Data are public third-party files; no individual-level data are
redistributed. **Funding, author contributions, competing interests, an AI/LLM-use disclosure and a
versioned public code repository with its DOI are not yet finalised and will be completed in the
manuscript and code repository before submission** — they are currently marked as author-to-complete
placeholders and we do not claim they are finished. The full analysis archive (code, result tables,
the consolidated `numbers_v7.csv`, figures and manuscript; no individual-level data) is provided as
`submission_repo_v7/`, and the corresponding author will deposit it on GitHub and archive the release
on Zenodo to obtain the version DOI before submitting.

*Checklist to complete before clicking submit (corresponding author): (1) fill the author byline,
affiliations and corresponding-author email at the top of the manuscript; (2) fill Funding, Author
contributions (CRediT) and Competing interests, and confirm the AI-use wording; (3) create the public
repository, mint the Zenodo DOI and paste it into the Code-availability statement; (4) confirm the
figures and that `verify_v7.py` reproduces every number. This cover letter should then be signed
below.*

Sincerely,
*[AUTHOR INPUT REQUIRED — corresponding author name, degree(s), position, institution, postal
address, email, and date; sign on behalf of all authors.]*
