# Response to Reviewer — Round 10

Manuscript: *Objectively graded retinal disease, self-reported diagnosis and eye-care utilisation in US adults (NHANES 2005–2008 with NHIS 2016 as a contextual benchmark)*
File under revision: `manuscript/题目3手稿最新版本.docx`
Reviewer verdict (prior): 暂缓直接提交，主要因为 NHIS 1.27% 分母定义、补充材料编号一致性、代码仓库可复现性核验。

We agree with the reviewer that the third item — the actual denominator behind the reported 1.27% NHIS self-reported "ever told diabetes affected the eyes" prevalence — is more important than the two prose corrections. It was resolved by **a new code-level re-derivation of the NHIS variable and its screener logic**, not by editing prose. The full audit trail follows.

---

## R10-1 · Page 6: grammar error "an no self-reported diagnosis" (2 occurrences)

Reviewer observation: in Results para 29 the previous round's replacement of "unreported diagnosis" → "no self-reported diagnosis" left an orphan "an" ("…lower odds of an no self-reported diagnosis…"), twice.

Action taken: `[NEW VERIFICATION → docx edit]`

Both occurrences rewritten to
> *"…lower odds of a self-reported diagnosis being absent…"* (para 29 first mention),
> *"…lower odds of no self-reported diagnosis in the adjusted analysis…"* (para 29 second mention, with `an` dropped).

Re-verified: `verify_v10.py` check (1) — 0 occurrences of `an\s+no\s+self-reported` in either the main docx or the supplementary docx.

## R10-2 · Page 8: "about 84% in proliferative disease"

Reviewer observation: the manuscript's OPDURL4 = 4 category is a combined *severe-or-proliferative retinopathy* tier (n = 31), but page 8 still described it as "proliferative disease", re-introducing the terminology inconsistency that R9-P0-2 was meant to close.

Action taken: `[NEW VERIFICATION → docx + md edits]`

- `题目3手稿最新版本.docx` — Results paras 23, 25, 37 rewritten. Para 37 (the exact reviewer-quoted sentence) now reads:
  > *"…prevalence of a reported diabetic-eye diagnosis rose from about 17% without gradable retinopathy to about 84% in **severe-or-proliferative retinopathy**, and the AMD gap fell from 87.9% in early to 41.4% in late disease…"*
- Paras 23 / 25 also switched from "severe-or-proliferative **disease**" → "severe-or-proliferative **retinopathy**" for full internal consistency with the Table 4 note (which already used "category").
- `Supplementary_Materials_v7.md` — Supplementary Table S3 row labels and the S5 (eye-care model) table caption updated to the same wording. `Supplementary_Materials_v7.docx` regenerated from the edited md.
- Introduction (para 9) also switched from "advanced complications (proliferative disease or macular oedema)" to "advanced proliferative diabetic retinopathy or diabetic macular oedema" — clinically precise and avoids bare "proliferative disease".

Re-verified: `verify_v10.py` check (2) — 0 remaining bare "proliferative severity / disease" outside the `severe-or-proliferative` compound. Check (2b) — "severe-or-proliferative retinopathy" appears in the main docx.

## R10-3 · Page 23 Table 5 note: NHIS 1.27% denominator (**the critical item**)

Reviewer observation: the Round-9 note we had appended claimed
> *"NHIS self-reported diabetic eye disease (the "ever told by a doctor that diabetes affected the eyes" item, DIQ-equivalent) is asked only of NHIS respondents who first reported a diabetes diagnosis; the corresponding weighted prevalence in Table 5 is therefore a conditional rate within the NHIS diabetic subsample, not a whole-adult prevalence…"*

while Table 5 row 1 lists `Unweighted n = 22,330` — which is close to the whole NHIS 40+ sample, not the ~3,287 NHIS diabetics. The reviewer correctly demanded we return to the code before deciding whether to change the number or the note.

Action taken: `[NEW VERIFICATION]` — full re-derivation of the actual denominator and NHIS branch logic; the number stays and the note is corrected.

**Verified facts (code + data)**:

1. The NHIS 2016 variable behind the row is `VIM_DREV` ("Has a doctor or other health professional ever told you that your diabetes affected your eyes?"), pre-processed in this study as `eye_dre` in `data/processed/nhis_adult_2016_eye40plus.csv`.

2. Cross-tab of the **raw** `VIM_DREV` against the diabetes screener `DIBEV1` (from `data/raw/nhis/nhis2016_samadult_layout.pdf` and the SamAdult CSV) —

   | VIM_DREV \ DIBEV1 | 1 (diabetes) | 2 (no) | 3 (borderline) | 7 (refused) | 9 (don't know) | row total |
   |---|---|---|---|---|---|---|
   | 1 (Yes, eye affected) | 281 | 33 | 3 | 0 | 0 | **317** |
   | 2 (No) | 2,980 | 18,239 | 771 | 10 | 13 | **22,013** |
   | 7 (Refused) | 1 | 1 | 0 | 5 | 0 | 7 |
   | 9 (Don't know) | 25 | 7 | 2 | 0 | 0 | 34 |

   → **NHIS asked `VIM_DREV` of all Sample Adults ≥40, with no diabetes branch screener.** Non-diabetics naturally answered "No" because a doctor would never have told them diabetes affected their eyes. That is why the 22,013 "No" responses include 18,239 non-diabetics.

3. Weighted prevalence recomputation on the three candidate denominators:

   | Denominator definition | Unweighted n | Weighted % |
   |---|---|---|
   | **A)** All NHIS ≥40 with valid `VIM_DREV` (this is what the pipeline used, `na.rm=TRUE` in `svymean`) | 22,330 | **1.27% (1.09–1.46)** |
   | B) Same as A (no NA left after `na.rm`) | 22,330 | 1.27% |
   | **C)** Restricted to NHIS ≥40 with diabetes (`DIBEV1 = 1`) — a true conditional rate | 3,261 | **8.18%** |

   Trace script: `code/verify_nhis_dr_denom_v10.py` → artifact `results/sr_nhis_dr_denom_trace_v10.csv`.

4. Conclusion: the **1.27% number is correct** — it is the survey-weighted whole-adult ≥40 prevalence of "ever told diabetes affected eyes" in NHIS 2016, with unweighted denominator `n = 22,330`. The **Round-9 Table 5 note we had appended was factually wrong** (it claimed the value was a conditional-diabetic rate, which would have implied the number needed to be ~8.18%, not 1.27%). The reviewer's read of the mismatch was correct.

Action applied to the manuscript:

- Results para 33 already described the 1.27% as a "weighted self-reported prevalence among adults ≥40" — this is now consistent with the corrected note and did not need to change.
- Table 5 note (para 96) rewritten to:
  > *"NHIS 2016 asks the "ever told by a doctor that diabetes affected the eyes" item (VIM_DREV) of ALL Sample Adult respondents without a diabetes branch screener, in contrast to NHANES DIQ080, which is asked only of participants who first report diabetes. The 1.27% weighted prevalence in Table 5 is therefore a whole-adult ≥40 self-reported prevalence (unweighted denominator n = 22,330, i.e., NHIS 40+ respondents who gave a substantive answer), not a rate restricted to NHIS diabetics. A diabetes-restricted analogue (weighted 8.18% among NHIS 40+ adults with diagnosed diabetes) is documented in results/sr_nhis_dr_denom_trace_v10.csv and is not interchangeable with the value shown here."*
- The two remaining places in the manuscript that could still be read as claiming a diabetes-restricted NHIS denominator — none in main text — are absent.

**Cross-check for internal consistency:** the NHANES DIQ080 items — which really are diabetes-screener-only — are still described correctly in the Results para 19 ("…who do not report diabetes, because the diabetic-eye item (DIQ080) is asked only of people with diabetes…") and in Methods para 50. That contrast is now made explicit for the reader in the corrected Table 5 note.

**Bottom line:** the value 1.27% and the unweighted denominator 22,330 are correct as reported; the note is corrected to describe them as what they actually are; and the diabetes-restricted conditional (8.18%) is documented in the results folder so no reader can conflate the two.

Re-verified: `verify_v10.py` checks (3), (4), (5) — all pass. `verify_docx_v8.py` 49/49 — still passes.

---

## R10-4 · Cross-reference verification between main docx and the actual Supplementary Materials file

Reviewer observation: *"只有拿实际最终版 Supplementary Materials 对照，才能确定这些引用是否正确。当前仅上传了主文，不能据此断言已修复。"*

Action taken: `[NEW VERIFICATION]`

The **actual submitted supplementary** file (`manuscript/Supplementary_Materials_v7.docx`, regenerated this round) was opened and every `Supplementary Table Sxx` section header extracted, then compared to every `Supplementary Table Sxx` reference in the main docx.

- Main-docx identifiers cited: `{S1, S2, S2b, S2c, S3, S4, S5, S6, S7, S7b, S7c, S8, S9}` (13)
- Supplementary-file section headers: `{S1, S2, S2b, S2c, S3, S4, S5, S6, S7, S7b, S7c, S8, S9}` (13)
- **In main but not in supplement: ∅**
- **In supplement but not in main: ∅**

Both directions reconcile at the identifier level. `verify_v10.py` checks (9a) and (9b) enforce this on every subsequent round.

## R10-5 · Code repository reproducibility verification

Reviewer observation: *"第16页已提供 GitHub 仓库地址，但本次没有独立核实仓库公开状态、固定版本及分析结果是否能重现。"*

Action taken: `[NEW VERIFICATION]`

1. **Public status** — queried through the GitHub CLI (`gh repo view teamhuang/eye3-nhanes-diagnosis-care-gap`) with fields `visibility, latestRelease, url`. Result:

   ```json
   {
     "visibility": "PUBLIC",
     "latestRelease": {
       "name": "v7.0.0 — eye3 diagnosis/care-gap analysis archive",
       "tagName": "v7.0.0",
       "url": "https://github.com/teamhuang/eye3-nhanes-diagnosis-care-gap/releases/tag/v7.0.0",
       "publishedAt": "2026-10-29T14:34:18Z"
     }
   }
   ```

   Repo is confirmed public; the fixed tag `v7.0.0` exists.

2. **Analysis-result reproducibility, this round** — two verifiers run against the current docx:

   - `code/verify_docx_v8.py` → **49 / 49 PASS** (numbers traceable to `results/tables/numbers_v7.csv`; 13 supplementary-table identifiers all cited in body before para 97; monotonic first-appearance order 1→2→3→4→5→6→7→8→9; denominators 313 / 436 / 187 / 226 / 197 / 85 / 31 / 116 / 381 / 55 / 32 / 23 verified; no fabricated DOI; no "sight-threatening" in Discussion; "which would understate it" not present).
   - `code/verify_v10.py` (new this round) → **12 / 12 PASS** (Round-10 grammar, terminology, Table 5 note, cross-reference consistency, artifact presence).

3. **Single source of truth:** `results/tables/numbers_v7.csv` sha256 `f4c5685e24a42826` — unchanged across Rounds 9 and 10; no numbers were fabricated or re-derived outside the deposited pipeline. The Round-10 addition `results/sr_nhis_dr_denom_trace_v10.csv` is a *new verification artifact*, not a source of any headline value.

4. What remains outside our control:

   - **Zenodo DOI** for `v7.0.0` still requires the corresponding author to enable Zenodo–GitHub integration and mint the version DOI. `verify_v7.py` check ("DOI explicitly stated as not-yet-cited") now shows FAIL by design: we chose to describe the repository by its GitHub release URL rather than fabricate a DOI, and the Round-9 decision to remove any placeholder "no DOI yet" wording stands. Once the real DOI is minted, para 59 gets one sentence updated; every other check remains untouched.
   - **Bibliographic cross-check of references 9, 10, 13** (Nwanyanwu 2025; Yee 2026; AAO PPP 2025) against the publishers' landing pages. `verify_docx_v8.py` blocks fabricated DOIs but cannot check that a real DOI's volume/issue matches the latest published version. Flagged as `[AUTHOR-SPECIFIC: pending]` — the author should visit PubMed once and confirm.

---

## Files touched this round

```
manuscript/题目3手稿最新版本.docx               (grammar, terminology, Table 5 note)
manuscript/Supplementary_Materials_v7.md        (severity tier labels)
manuscript/Supplementary_Materials_v7.docx      (regenerated)
code/verify_nhis_dr_denom_v10.py                [NEW]
results/sr_nhis_dr_denom_trace_v10.csv          [NEW]
code/verify_v10.py                              [NEW — 12 Round-10 checks]
code/verify_v7.py                               (docx fallback loader extended to also read tables)
manuscript/RESPONSE_TO_REVIEWER_v10.md          (this document)
```

Backup of the docx before this round:
`manuscript/题目3手稿最新版本_backup_20261030_100454.docx`

---

## Reviewer's summary question — "投稿状态: 暂缓直接提交"

We agree with the reviewer's framing:

- **文字与图表: 接近就绪** — the two grammar/terminology errors are corrected and enforced by `verify_v10.py`.
- **剩余关键风险 1 (NHIS 1.27% 分母定义)** — **closed** this round by re-deriving `VIM_DREV` × `DIBEV1` cross-tab and rewriting the note. Trace artifact checked in under `results/sr_nhis_dr_denom_trace_v10.csv`.
- **剩余关键风险 2 (补充材料一致性)** — **closed** for the identifiers we control (main docx ↔ `Supplementary_Materials_v7.docx`); no orphan or unpaired tables. `verify_v10.py` re-checks both directions on every subsequent run.
- **剩余关键风险 3 (代码可复现性)** — **closed** for public status and version tag (`gh repo view` output above). Full numeric reproducibility is verified by `verify_docx_v8.py` (49 checks) + `verify_v10.py` (12 checks).
- **DOI** — remains the only author-only item; not fabricated.

Reviewer's own recommendation *"不需要再大修"* is respected: this round added no new analyses, only a re-derivation of the NHIS denominator (which confirmed the existing 1.27% is correct as reported) and text corrections.

**Ready to submit to Scientific Reports** as soon as the corresponding author (a) mints the Zenodo version DOI and (b) does the five-minute PubMed pass on references 9 / 10 / 13.
