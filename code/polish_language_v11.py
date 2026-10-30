"""Round-11 language polish: reduce AI-tone and defensive phrasing while preserving
every statistical caveat that protects against over-claiming. Each rewrite keeps the
same numbers, the same denominator definitions, and the same inferential limits; only
the wording is tightened toward natural American scientific prose."""
import docx
from pathlib import Path

DOCX = Path('manuscript/题目3手稿最新版本.docx')

# (paragraph_index, [(old_snippet, new_snippet), ...])
EDITS = [
    # --- Para 7 (abstract): remove "rather than paired" clause; more natural ---
    (7, [
        ('Objectively graded AMD prevalence (6.58%) exceeded age-standardised self-report (2.45%), a contextual rather than paired comparison.',
         'Objectively graded AMD prevalence (6.58%) exceeded age-standardised self-report (2.45%); this is a contextual comparison, not a paired one.'),
    ]),

    # --- Para 27: cut exploratory + trim trailing defensive tail ---
    (27, [
        ('These covariate analyses are exploratory and describe factors that travel with the patient-reported gap; they are not causal.',
         'These covariate analyses are descriptive; they identify factors that co-occur with the patient-reported gap and do not support causal reading.'),
        ('We therefore treat higher income as a tentative, imprecise correlate rather than an established driver.',
         'Higher income is therefore treated as a tentative correlate with imprecise magnitude, not an established driver.'),
        ('Overall, we did not detect statistically robust socioeconomic associations with diagnosis discordance, although limited precision precludes excluding clinically meaningful differences.',
         'Across specifications we found no consistent socioeconomic association with diagnosis discordance; limited precision does not rule out differences of clinical size.'),
    ]),

    # --- Para 29: consolidate exploratory uses; trim final repetition ---
    (29, [
        ('This is an exploratory secondary analysis; the adjusted odds ratio with its confidence interval is the primary quantity (full model in Supplementary Table S5).',
         'This secondary analysis is exploratory; the adjusted odds ratio with its confidence interval is the primary quantity (full model in Supplementary Table S5).'),
        ('An exploratory eye-care \u00d7 severity interaction gave no evidence of effect modification (aOR 1.61, 0.24\u201310.79, P = 0.59).',
         'An eye-care \u00d7 severity interaction tested in the same model gave no evidence of effect modification (aOR 1.61, 0.24\u201310.79, P = 0.59).'),
        ('Recent dilated examination was therefore associated with lower odds of a self-reported diagnosis being absent in the adjusted analysis, although the association did not survive multiple-testing correction; being cross-sectional, the design cannot establish whether examination leads to diagnosis or diagnosis prompts examination.',
         'A recent dilated examination was thus associated with lower odds of an absent self-reported diagnosis in the adjusted model, though the association did not survive Holm correction; the cross-sectional design cannot separate examination-driven diagnosis from diagnosis-driven examination.'),
    ]),

    # --- Para 31: remove "robust" ---
    (31, [
        ('This is a limited stability check rather than proof of weight robustness: an unchanged aggregate ESS can coexist with a long weight tail and speaks only to observable differences.',
         'This stability check is limited; an unchanged aggregate ESS can still sit alongside a long weight tail and speaks only to observable differences.'),
        ('The descriptive prevalence and primary discordance proportions are therefore robust to observable differences between gradable and ungradable images, although inverse-probability weighting cannot address unmeasured selection',
         'The descriptive prevalence and primary discordance proportions therefore move little under observable gradable-vs-ungradable reweighting; inverse-probability weighting cannot address unmeasured selection'),
    ]),

    # --- Para 37: cut "exploratory" (keep once at most); simplify closing caveat ---
    (37, [
        ('Second, discordance was broadly distributed across sociodemographic strata: after adjustment we did not detect statistically robust associations with education, income or insurance, with only age significant for AMD and the income association varying in precision with missing-data handling.',
         'Second, discordance was broadly distributed across sociodemographic strata: after adjustment we found no consistent association with education, income or insurance; only age was significant for AMD, and the income association varied in precision with missing-data handling.'),
        ('Third, the eye-care\u2013awareness association was a secondary, exploratory finding: recent dilated examination was associated with a lower likelihood of reporting no prior diagnosis, but the association did not survive multiple-comparison correction, and the cross-sectional design cannot distinguish whether eye-care contact facilitates recognition, whether a known diagnosis prompts examination, or whether both reflect severity and access.',
         'Third, the eye-care\u2013awareness association was secondary: a recent dilated examination was linked to a lower likelihood of reporting no prior diagnosis, but the association did not survive Holm correction, and a cross-sectional design cannot tell whether eye-care contact facilitates recognition, whether a known diagnosis prompts examination, or whether both track severity and access.'),
        ('These patterns are consistent with, but do not establish, a hypothesis that examination patterns shape diagnostic awareness; because prior diagnosis can itself prompt eye-care visits, the relationship is bidirectional and remains a question for prospective study.',
         'Examination patterns may shape diagnostic awareness, but these data do not test that pathway; prior diagnosis can itself prompt eye-care visits, so the relationship is bidirectional and requires prospective study.'),
    ]),

    # --- Para 38: soften trailing defensive tail; also tighten "at older ages rather than severity alone" ---
    (38, [
        ('consistent with greater cumulative ophthalmic contact at older ages rather than severity alone.',
         'consistent with greater cumulative ophthalmic contact at older ages, not severity alone.'),
        ('This study did not compare screening strategies, diagnostic yield, false-positive rates, referral burden or cost-effectiveness, so it does not establish the effectiveness or cost-effectiveness of broader population screening.',
         'This study did not compare screening strategies, diagnostic yield, false-positive rates, referral burden or cost-effectiveness, so nothing here speaks to the effectiveness or cost-effectiveness of broader population screening.'),
    ]),

    # --- Para 39: consolidate exploratory usage ---
    (39, [
        ('We therefore interpret all socioeconomic associations as exploratory and do not regard the direction of the income association as established.',
         'We therefore read all socioeconomic associations as exploratory; the direction of the income association is not settled.'),
    ]),

    # --- Para 41: replace "rather than" with clearer split sentence ---
    (41, [
        ('These findings describe historical differences between imaging-based classification, diagnostic awareness and eye-care utilisation rather than definitive clinical underdiagnosis or current US practice.',
         'These findings describe historical differences between imaging-based classification, diagnostic awareness and eye-care utilisation; they are not estimates of current clinical underdiagnosis or of present US practice.'),
    ]),

    # --- Para 50: strip "Importantly, " opener (AI tell) ---
    (50, [
        ('Importantly, DIQ080 measures whether',
         'DIQ080 measures whether'),
    ]),

    # --- Para 52: 3 exploratory -> 1; consolidate ---
    (52, [
        ('A secondary, exploratory association analysis examined the link between recent (within-12-month) dilated examination and having no self-reported diabetic-eye diagnosis, adjusted for demographics, income, insurance and retinopathy severity. Because no verifiable pre-registration exists for this secondary analysis, we classify it as exploratory alongside the covariate and interaction analyses, reporting effect sizes, confidence intervals and corrected P values and interpreting them without causal intent. Associations with sociodemographic covariates and all interaction terms are exploratory, reported with odds ratios, confidence intervals and corrected P values and interpreted conservatively.',
         'A secondary association analysis examined the link between recent (within-12-month) dilated examination and having no self-reported diabetic-eye diagnosis, adjusted for demographics, income, insurance and retinopathy severity. No verifiable pre-registration exists for this or any other regression analysis reported here, so all regression results \u2014 the covariate models, the eye-care model and the interaction terms \u2014 are exploratory: we report effect sizes, confidence intervals and Holm-corrected P values and interpret them without causal intent.'),
    ]),

    # --- Para 55: replace "rather than as the primary" and "not evidence that" ---
    (55, [
        ('(this is an auxiliary check of stability, not evidence that missingness is ignorable)',
         '(an auxiliary stability check; it does not show that missingness is ignorable)'),
        ('pooled inference is presented as a sensitivity analysis supporting the direction of the income association rather than as the primary inferential estimate.',
         'pooled inference is presented as a sensitivity analysis that supports the direction of the income association, not as the primary inferential estimate.'),
        ('These tests are informative about which observed covariates to adjust or impute for but cannot identify the missingness mechanism, and do not establish that missingness is ignorable (MAR) or free of unobserved bias.',
         'These tests inform which observed covariates to adjust or impute for; they do not identify the missingness mechanism and do not establish MAR or exclude unobserved bias.'),
    ]),

    # --- Para 57: single "exploratory" is fine; just tighten the "not as a gate" phrasing ---
    (57, [
        ('Holm adjustment is applied within each model purely for transparency (raw and adjusted P values shown together), not as a gate on interpretation.',
         'Holm adjustment is applied within each model for transparency only (raw and adjusted P values shown together), not as a filter on interpretation.'),
    ]),
]

doc = docx.Document(str(DOCX))

def rewrite_para(p, new_text):
    if not p.runs:
        p.text = new_text
        return
    p.runs[0].text = new_text
    for r in p.runs[1:]:
        r.text = ''

count_applied = 0
count_missing = 0
for pi, subs in EDITS:
    p = doc.paragraphs[pi]
    txt = p.text
    changed = False
    for old, new in subs:
        if old in txt:
            txt = txt.replace(old, new)
            changed = True
            count_applied += 1
        else:
            print('  [MISS] para %d, snippet not found: %s...' % (pi, old[:70]))
            count_missing += 1
    if changed:
        rewrite_para(p, txt)

doc.save(str(DOCX))
print('Applied %d rewrites; %d misses' % (count_applied, count_missing))
