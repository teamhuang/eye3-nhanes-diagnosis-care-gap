# Response to Reviewer — Round 12 (figure beautification, Nature style)

Manuscript: *Objectively graded retinal disease, self-reported diagnosis and eye-care utilisation in US adults (NHANES 2005–2008 with NHIS 2016 as a contextual benchmark)*
Files rewritten: `figures/Fig1_gaps.png`, `figures/Fig2_severity_gradient.png`, `figures/Fig3_objective_vs_selfreport.png`, `figures/FigS1_flowchart.png`, `figures/FigS2_eyecare_predicted.png` (plus matching `.pdf` vectors)
Embedding: all 5 replaced inside `manuscript/题目3手稿最新版本.docx` and `manuscript/Supplementary_Materials_v7.docx`

---

## Design rules applied

| Rule | Implementation |
|---|---|
| Height | **5 cm** for every figure |
| Width | **6.5 cm** for multi-panel or wide (Fig1, Fig2, FigS1); **5 cm** for single-panel compact (Fig3, FigS2) |
| No note ON the figure | Removed every `ax.set_title(...)`, `fig.suptitle(...)`, and `fig.text(...)` annotation. Titles and legends live only in the Word caption paragraph. |
| Nature typography | Arial 6–7 pt; axis labels 6.5–6.8 pt; tick labels 5.2–6.5 pt |
| Minimal chart junk | Top and right spines removed; 0.6 pt left/bottom spines; tick marks inward; no gridlines |
| Colour-blind-safe palette | Okabe-Ito retained (`#0072B2`, `#E69F00`, `#009E73`, `#D55E00`, `#56B4E9`) |
| Panel labels | Fig2 uses bold lowercase **a** / **b** at top-left of each panel (Nature convention) |
| Resolution | 600 dpi PNG + vector PDF |

## Numerical integrity

Every plotted value is read from the same CSVs the manuscript cites (`results/tables/t_gaps_v4.csv`, `t_severity_unified_v4.csv`, `t_amd_severity_v5.csv`, `t_modworse_gap_v6.csv`, `t_prevalence_v4.csv`, `t_nhis_std_versions_v5.csv`, `tA_gcom_v4.csv`, `t_modeln_v4.csv`). Values plotted are unchanged from the v6 figure generation:

- **Figure 1**: 70.2% / 82.2% / 41.4% / 35.8% / 32.4%
- **Figure 2** panel a (DR severity): 78% / 64% / 16% / 53% with n = 197 / 85 / 31 / 116
- **Figure 2** panel b (AMD severity): 88% / 41% / 50% / 28% with n = 381 / 55 / 32 / 23
- **Figure 3**: 6.58% / 2.66% / 2.45%
- **Figure S1**: n = 6,797 → 5,704 / 5,604 → 319 / 441 → 313 / 436 → 187 / 226
- **Figure S2**: 81.8% / 62.4%

`verify_docx_v8.py` re-checks every headline number against `numbers_v7.csv` (sha256 `f4c5685e24a42826`) after the images were embedded — **49 / 49 PASS**.

## Visual-check iterations

Five passes were run, each with the PNG opened and inspected:

| Pass | Issue found | Fix |
|---|---|---|
| 1 | Fig1 x-axis label clipped on right; 41.4% label hard to read on orange | Shortened x-label; label colour logic per bar |
| 2 | Fig1 y-tick labels clipped; Fig2 y-axis label clipped; Fig2 panel a x-tick labels overlapping; FigS2 y-axis label clipped; FigS1 bottom-row text overflowing boxes | Increased left margins; rotated Fig2 panel a ticks; shrank FigS1 fonts |
| 3 | Fig1 "Care gap: DM+retinopathy" still clipped; Fig1 41.4% label still overlapping error bar | Shortened to "Care gap: DM+ret"; moved label to right of CI upper bound |
| 4 | Fig1 "Care gap: DM+retinopathy" still clipped at left margin 0.36 | Shortened further to "Care gap: DM+ret"; margin 0.36 → 0.30 |
| 5 | Fig2 panel a x-tick labels overlapping due to rotation | Removed rotation; shortened labels to "Mild / Mod / Sev / Mod+" |

Final pass confirmed all five figures render cleanly: no clipped labels, no overlapping text, no on-figure titles or footnotes, exact target dimensions.

## Files produced

```
figures/Fig1_gaps.png / .pdf                       6.50 × 5.00 cm
figures/Fig2_severity_gradient.png / .pdf          6.50 × 5.00 cm
figures/Fig3_objective_vs_selfreport.png / .pdf    5.00 × 5.00 cm
figures/FigS1_flowchart.png / .pdf                 6.50 × 5.00 cm
figures/FigS2_eyecare_predicted.png / .pdf         5.00 × 5.00 cm
code/build_figures_v11.py                          [NEW]
code/embed_figures_v11.py                          [NEW]
manuscript/题目3手稿最新版本.docx                   3 images replaced
manuscript/Supplementary_Materials_v7.docx         2 images replaced
manuscript/RESPONSE_TO_REVIEWER_v12.md             this file
```

## Verification

- `verify_docx_v8.py` → **49 / 49 PASS** (all numbers preserved, all figure/table citations intact, no bold in body, abstract = 200 words)
- `verify_v10.py` → **12 / 12 PASS** (Round-10 grammar/terminology/Table 5 note/cross-reference checks)
- PNG dimensions verified with PIL: every figure exactly 5.00 cm tall; widths 6.50 or 5.00 cm per rule
- Visual inspection of all 5 PNGs: no on-figure titles, no clipped labels, no overlapping text

## Notes

- Figure legends in the Word document (paras 71–75) already carry the descriptive titles and are bold per the Round-11 formatting rule; the images themselves contain only the plot.
- The v6 script (`code/build_figures_v6.py`) is retained for provenance; v11 is the new authoritative generator.
- PDF versions are provided for print-quality submission; PNG versions are what the docx embeds.

No numbers changed. No analyses added. This round is purely figure beautification per the user's Nature-style spec.
