"""Round-13b: no explicit figure/table callout in the FIRST sentence after a subheading.
Each callout is deferred into the paragraph body (moved, never deleted). All numbers preserved."""
from pathlib import Path
from docx import Document
ROOT=Path("C:/eye3/manuscript/eye3")
D=ROOT/"manuscript"/"题目3手稿最新版本.docx"
d=Document(str(D))
P=d.paragraphs

def rep(i,old,new):
    r=P[i].runs[0]; assert old in r.text, f"para {i}: NOT FOUND -> {old[:50]}"
    r.text=r.text.replace(old,new)

def full(i,new):
    P[i].runs[0].text=new

# para 15: move (Supplementary Table S1, Figure 1) out of S1; Figure 1 -> S2 (S1 kept later in para)
rep(15,"5,604 a gradable AMD image (Supplementary Table S1, Figure 1). Because the diagnosis-discordance outcome requires an answer to the corresponding self-report item, all denominators below are responders.",
      "5,604 a gradable AMD image. Because the diagnosis-discordance outcome requires an answer to the corresponding self-report item, all denominators below are responders (Figure 1).")

# para 19: move (Table 2, Figure 2) from S1 to S2
rep(19,"reported no prior diabetic-eye diagnosis (Table 2, Figure 2). Among adults",
      "reported no prior diabetic-eye diagnosis. Among adults")
rep(19,"reported no diagnosis (n = 55). The outcome is",
      "reported no diagnosis (n = 55; Table 2, Figure 2). The outcome is")

# para 21: move (Table 2) from S1 to S2
rep(21,"32.4% (25.9\u201339.7) had not (Table 2). Because clinical guidance",
      "32.4% (25.9\u201339.7) had not. Because clinical guidance")
rep(21,"individualised guideline.\"", "individualised guideline\" (Table 2).")

# para 23: split lead sentence; callouts now in S2/S3 (panel a before panel b preserved)
full(23,"Self-reported diagnosis rose steeply with retinopathy severity among adults with diabetes. "
 "The proportion reporting no prior diagnosis fell from 78.1% (71.3\u201383.7) for mild NPDR (n = 197), to "
 "64.4% (48.3\u201377.8) for moderate (n = 85), to 15.7% (5.0\u201339.7) for severe-or-proliferative retinopathy "
 "(n = 31), while the percentage actually diagnosed rose across the same tiers from 16.6% among those with no "
 "gradable retinopathy to 21.9%, 35.6% and 84.3% (Figure 2, panel a; Supplementary Table S2). AMD discordance was "
 "similarly graded: the gap was higher for early AMD \u2014 87.9% (84.4\u201390.6), n = 381 \u2014 than for late AMD "
 "(41.4%, 25.3\u201359.6, n = 55), each computed from its own responder set (Figure 2, panel b). By age stratum, AMD "
 "discordance was near-complete at 40\u201359 years (99.1%, 95.6\u201399.8), fell to 86.6% (77.8\u201392.3) at 60\u201374 "
 "and 66.7% (60.1\u201372.6) at \u226575, whereas the DR gap was flatter (Supplementary Table S2). The severe-DR and "
 "late-AMD strata are small and their intervals wide, so the fall in discordance with severity is best read as a "
 "graded descriptive pattern rather than a series of individually tested contrasts.")

# para 25: split lead sentence; (Figure 2, panel a) now in S2
full(25,"Reframing around clinically more advanced disease, the diagnosis gap remained substantial at or above the "
 "moderate-non-proliferative threshold. Among adults with diabetes and moderate-or-worse retinopathy (n = 116) the "
 "pooled gap was 53.4% (38.7\u201367.5), comprising 64.4% (48.3\u201377.8) for moderate and 15.7% (5.0\u201339.7) for "
 "severe-or-proliferative retinopathy (Figure 2, panel a). For AMD, 41.4% (25.3\u201359.6) of objectively graded late "
 "AMD carried no reported diagnosis. The \"moderate-or-worse\" grouping denotes clinically more advanced disease, not "
 "a treatable or immediately blinding category \u2014 moderate non-proliferative retinopathy is typically monitored "
 "rather than treated \u2014 and imaging severity is not a treatment indication. Splitting late AMD, geographic "
 "atrophy was undiagnosed in 50.3% (26.6\u201373.9; n = 32) and exudative/neovascular AMD in 27.7% (8.0\u201362.9; "
 "n = 23); both strata are small with widely overlapping intervals, so this difference is not an established group "
 "difference. The two phenotypes also differ in therapy and in treatability at the time these data were collected.")

# para 31: drop redundant (Supplementary Table S5) from S1 (still cited at paragraph end)
rep(31,"less than a high-school education (23.2% vs 14.4%) (Supplementary Table S5). To test",
      "less than a high-school education (23.2% vs 14.4%). To test")

# para 33: drop redundant (Table S6) from S1 (Supplementary Table S6 cited in S2)
rep(33,"had a dilated examination within 12 months (Table S6). Self-reported glaucoma",
      "had a dilated examination within 12 months. Self-reported glaucoma")

d.save(str(D)); print("Round-13b saved")
