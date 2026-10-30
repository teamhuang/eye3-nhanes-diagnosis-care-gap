"""Phase-2 [NEW VERIFICATION]: trace the NHIS 1.27% self-reported 'diabetic eye disease'
weighted rate — actual denominator, NA handling, and survey-weight construction.

Reviewer round 10 concern (page 23 Table 5):
  "Diabetic retinopathy (ever told) | Unweighted n=22,330 | Weighted % 1.27"
  claimed to be a *conditional* rate within NHIS diabetics (per current Table 5 note)
  but the reported denominator looks like the whole 40+ sample.

Writes: results/sr_nhis_dr_denom_trace_v10.csv
"""
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NHIS = ROOT / "data" / "processed" / "nhis_adult_2016_eye40plus.csv"
OUT  = ROOT / "results" / "sr_nhis_dr_denom_trace_v10.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(NHIS)
print("NHIS 2016 40+ file:", NHIS.name, "rows:", len(df))
print("columns:", list(df.columns))

# NHIS 'ever told diabetes affected eyes' is the raw VIM_DREV (already mapped to eye_dre)
# Coding convention for the *_EV eye modules (per NHIS 2016 SamAdult questionnaire):
#   1 = Yes, has been told
#   5 = No, has not been told   (NHIS uses 5 for "No" in the Yes/No/Refused pattern)
#   7 = Refused
#   9 = Don't know
#   Missing = question not applicable (e.g., respondent did NOT answer "yes" to the
#     diabetes screener DIBEV1, so NHIS branch logic skips the diabetic-eye item)
print("\neye_dre value counts (raw):")
print(df['eye_dre'].value_counts(dropna=False).sort_index())
print("\nDIBEV1 (has-diabetes flag) value counts (raw):")
if 'DIBEV1' in df.columns:
    print(df['DIBEV1'].value_counts(dropna=False).sort_index())
else:
    print("(column absent) — using eye_dre NA-vs-answered as the proxy screener")
print("\ndiabetes column value counts:")
print(df['diabetes'].value_counts(dropna=False).sort_index())

# Reconstruct the analytic variables the manuscript used
# eye_dre was mapped to a 0/1 with 5 = "No". Verify:
mask_valid = df['eye_dre'].isin([0, 1, 5, 7, 9])
print("\neye_dre in {0,1,5,7,9}:", mask_valid.sum(), "of", len(df))

# Recode: 1 -> 1; 5 -> 0; NA / 7 / 9 -> NaN
def recode(x):
    if pd.isna(x): return np.nan
    if x == 1: return 1
    if x in (0, 5): return 0
    return np.nan
df['dx_dibeye'] = df['eye_dre'].apply(recode)

# Weight column and design vars
wt = df['wt'].astype(float)
df['w'] = wt

# Three candidate denominators the reviewer might be asking about:
#   (A) ALL 40+ NHIS respondents (with non-diabetics coded 0)   -> unconditional
#   (B) NHIS respondents with valid eye_dre answer (0/1/5)      -> "ever told" among those asked
#   (C) NHIS respondents with diabetes==1 and valid eye_dre     -> conditional on diabetes

# (A) all 40+ (treat NA as 0 = never-told, i.e., NOT asked = implicitly 'no')
df['dx_dibeye_A'] = df['dx_dibeye'].fillna(0)
# (B) those who answered
df['dx_dibeye_B'] = df['dx_dibeye']
# (C) diabetics who answered
mask_dm = (df['diabetes'] == 1) if df['diabetes'].dtype != 'object' else (df['diabetes'].astype(str).isin(['1','Yes']))
df['dx_dibeye_C'] = np.where(mask_dm, df['dx_dibeye'], np.nan)

def wmean_rate(subset_col):
    m = df[subset_col].notna()
    vals = df.loc[m, subset_col].astype(float).values
    ws = df.loc[m, 'w'].astype(float).values
    return 100 * np.average(vals, weights=ws), m.sum(), ws.sum()

# Use `survey`-style weighted proportion (approximate; Taylor variance not needed here)
row_A = wmean_rate('dx_dibeye_A')
row_B = wmean_rate('dx_dibeye_B')
row_C = wmean_rate('dx_dibeye_C')

print("\n--- NHIS 1.27% denominator trace ---")
print("A) all 40+ (NA filled as 0 = 'not ever told'):  %.2f%%  n=%d  sum_w=%.1f" % row_A)
print("B) only those who answered eye_dre item:        %.2f%%  n=%d  sum_w=%.1f" % row_B)
print("C) diabetics who answered eye_dre item:         %.2f%%  n=%d  sum_w=%.1f" % row_C)
print("\nManuscript currently reports 1.27% with Unweighted n = 22,330.")
print("Match with A -> unconditional whole-40+ prevalence (NA treated as 'no').")
print("Match with B -> weighted rate among those asked the item (non-responders excluded).")
print("Match with C -> conditional rate within NHIS diabetics.")

# Also break down: how many diabetics vs non-diabetics answered eye_dre?
print("\nBreakdown of 'answered eye_dre' (non-NA) by diabetes status:")
sub = df[df['dx_dibeye'].notna()]
print("  Total answered:", len(sub))
print("  Among these, diabetes==1:", (sub['diabetes']==1).sum() if sub['diabetes'].dtype != 'object' else 'check')
print("  Among these, diabetes==0:", (sub['diabetes']==0).sum() if sub['diabetes'].dtype != 'object' else 'check')
print("  eye_dre==1 (yes, ever told):", (sub['dx_dibeye']==1).sum())

# Save the trace CSV
trace = pd.DataFrame([
    dict(scenario="A: all 40+ (NA filled 0)", pct=row_A[0], n_unweighted=row_A[1], sum_weight=row_A[2]),
    dict(scenario="B: only answered item",     pct=row_B[0], n_unweighted=row_B[1], sum_weight=row_B[2]),
    dict(scenario="C: diabetics + answered",   pct=row_C[0], n_unweighted=row_C[1], sum_weight=row_C[2]),
])
trace['manuscript_row_unweighted_n'] = 22330
trace['manuscript_weighted_pct'] = 1.27
trace.to_csv(OUT, index=False)
print("\nWrote:", OUT)
