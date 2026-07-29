# Age accessibility, geriatric-context specification, and planned outcome coverage in registered chronic-wound trials: a finite-population registry audit

Guoyong Wang<sup>1</sup>, Kaijun Zhang<sup>2</sup>, Jiyue Jiang<sup>3</sup>, Chaonan Wang<sup>1</sup>, Weixin Wang<sup>1</sup>, Hui Bi<sup>4</sup>, Haojun Liang<sup>5</sup>, Zuoliang Qi<sup>5</sup>, Ying Huang<sup>2,*</sup>, Yu Li<sup>3,*</sup>, Xiaonan Yang<sup>1,*</sup>

## Affiliations

1. Department of Hemangioma and Vascular Malformation, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China.
2. Department of Gastroenterology, Children’s Hospital of Fudan University, National Children’s Medical Center, No. 399 Wanyuan Road, Minhang District, Shanghai 201102, People’s Republic of China.
3. Department of Computer Science and Engineering, The Chinese University of Hong Kong, Sha Tin, New Territories, Hong Kong SAR, China.
4. Department of Internal Medicine, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China.
5. Department of Comprehensive Plastic Surgery, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China.

*Correspondence:
Ying Huang (yhuang815@163.com), Department of Gastroenterology, Children’s Hospital of Fudan University, National Children’s Medical Center, No. 399 Wanyuan Road, Minhang District, Shanghai 201102, People’s Republic of China.

Yu Li (liyu@cse.cuhk.edu.hk), Department of Computer Science and Engineering, The Chinese University of Hong Kong, Sha Tin, New Territories, Hong Kong SAR, China; and The CUHK Shenzhen Research Institute, Hi-Tech Park, Nanshan, Shenzhen 518057, China.

Xiaonan Yang (yxnan@aliyun.com), Department of Hemangioma and Vascular Malformation, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China. Tel: +86 18810601889; Fax: +86 10 53968149.

## Structured abstract

### Background

Older adults are frequently underrepresented or insufficiently characterized in clinical trials, and registry eligibility does not establish who was actually enrolled.[1,2] We evaluated whether registered chronic-wound trials permitted older adults to enroll, publicly specified geriatric context, and planned condition-specific core outcomes.

### Methods

We conducted a finite-population descriptive audit of 1,218 adjudicated ClinicalTrials.gov records with 1,218 hash-verified complete official JSON records.[3,7] Structured and human-reconciled age measures were kept separate. The primary geriatric composite comprised eight clinical domains; proxy-consent pathways were coded and reported separately. Planned outcome coverage was evaluated using CoreVen only for venous-leg-ulcer active-treatment trials and OUTPUTs only for pressure-injury prevention trials.[4–6] Missing states were preserved. No sampling inference, regression, causal modelling, or imputation was used.

### Results

A finite structured upper-age limit was present in 456 of 1,218 records (37.44%; unknown 39). Reconciled eligibility at age 85 years was present in 834 of 1,218 (68.47%; unknown 38). At least one of the eight primary geriatric domains was publicly specified in 575 of 1,218 (47.21%; unknown 319); a proxy-consent pathway was specified in 29 of 1,218 (2.38%; unknown 140). Complete any-planned CoreVen coverage occurred in 2 of 304 applicable trials (0.66%; unknown 61), and complete any-planned OUTPUTs coverage occurred in 0 of 184 applicable trials (0.00%; unknown 33).

### Conclusions

Age accessibility, public geriatric-context specification, and condition-specific planned outcome coverage were distinct registry-level dimensions. Their separate reporting identifies registration and trial-planning gaps without estimating treatment effects or actual enrollment of older adults.

## Introduction

Older adults remain underrepresented in randomized trials, and even trials involving older populations often incompletely report frailty, function, cognition, multimorbidity, and other geriatric characteristics.[1,2] Age eligibility criteria, public geriatric-context information, and planned outcomes therefore answer different questions about older-adult relevance. Permission to enroll does not establish who was actually enrolled, and a public registry can omit clinically relevant context that was considered outside the record.

ClinicalTrials.gov provides a structured public record of trial design, eligibility, and planned outcomes, but registry information is not equivalent to participant-level clinical data or published trial results.[3,7] Core outcome sets define the minimum outcomes that should be measured and reported in trials of a given condition and can improve comparability and reduce selective outcome reporting.[4] CoreVen recommends five outcome domains—healing, pain, quality of life, resource use, and adverse events—for trials of interventions treating venous leg ulcers.[5] OUTPUTs defines six core outcomes for pressure-injury prevention trials: pressure-injury occurrence, precursor signs or symptoms, mobility, acceptability or comfort, adherence or compliance, and adverse events or safety.[6]

We used a locked, independently validated registry dataset to describe age accessibility, public specification of eight primary geriatric domains, separately reported proxy-consent pathways, and planned CoreVen or OUTPUTs coverage in their approved applicable populations. The study was a registry audit, not a treatment-effect, causal, enrollment, age-discrimination, or global-representativeness study.

## Methods

### Design and frozen population

This was a finite-population descriptive audit of 1,218 adjudicated registered interventional studies in ClinicalTrials.gov.[3,7] Complete official JSON with matching stored hashes was available for 1,218 of 1,218 records. The corrected frozen coding master contained 18,270 age-field rows, 10,962 geriatric-domain rows, 1,218 framework rows, and 7,633 planned-outcome rows, with no unresolved final values.

Registration periods were prespecified from the first-posted year as 2008–2016, 2017–2018, and 2019–2025. Descriptive earlier-versus-later contrasts compared 2008–2016 with 2019–2025; the 2017–2018 period was retained as a separately reported middle stratum.

### Age accessibility

Eligibility was evaluated at 65, 75, 80, and 85 years. Structured values came from frozen registry fields; reconciled values retained governed full-JSON human-confirmed coding. The scales were not merged. Unknown and expert-decision states remained distinct. These measures indicate registry-defined accessibility, not actual participant ages or enrollment.

### Geriatric-context specification

The primary geriatric composite comprised eight clinical domains: frailty; mobility, activities of daily living, or function; cognition or decision capacity; nutrition; multimorbidity; life expectancy or advanced illness; care setting or caregiver involvement; and polypharmacy or medication burden. Proxy-consent pathways were coded and reported separately and were not included in the primary eight-domain composite. Present, not-publicly-specified, and expert-decision states remained separate. These are registry-level public specifications, not patient diagnoses, measured prevalence, or a validated frailty score.

### Planned outcome coverage

Every one of the 7,633 rows represented a protocol-planned outcome, not a reported clinical result. CoreVen was applied only to venous-leg-ulcer active-treatment trials and OUTPUTs only to pressure-injury prevention trials.[5,6] Pressure-injury treatment, venous-leg-ulcer recurrence prevention, and mixed-wound studies remained within their approved descriptive boundaries. Primary-only and any-planned windows were not mixed.

### Descriptive analysis and validation

We reported observations, denominators, proportions, unknown counts, numeric age summaries, and prespecified absolute percentage-point differences. Missing, unknown, not-applicable, not-publicly-specified, and expert-decision states were not collapsed. No *P* values, sampling confidence intervals, regression, prediction, causal model, multiple imputation, composite geriatric score, or result-driven rule change was used.

The corrected results passed fresh independent machine validation, item-level review by named experts, and principal-investigator interpretation authorization.

## Results

### Population and input integrity

All 1,218 included records were interventional studies. Randomization was recorded for 809 of 1,218 (66.42%; unknown 2), and device studies accounted for 595 of 1,218 (48.85%).

Registration-period counts were 440 of 1,218 records (36.12%) in 2008–2016, 134 of 1,218 (11.00%) in 2017–2018, and 644 of 1,218 (52.87%) in 2019–2025.

### Age accessibility

Structured accessibility was 1,097 of 1,218 at age 65 (90.07%; unknown 42); 969 of 1,218 at age 75 (79.56%; unknown 42); 914 of 1,218 at age 80 (75.04%; unknown 42); and 846 of 1,218 at age 85 (69.46%; unknown 42).

Reconciled accessibility was 1,083 of 1,218 at age 65 (88.92%; unknown 38); 956 of 1,218 at age 75 (78.49%; unknown 38); 900 of 1,218 at age 80 (73.89%; unknown 38); and 834 of 1,218 at age 85 (68.47%; unknown 38).

A finite structured upper-age limit occurred in 456 of 1,218 records (37.44%; unknown 39), while 723 of 1,218 had no explicit structured upper-age limit (59.36%; unknown 39). Structured and reconciled age fields conflicted in 46 of 1,218 (3.78%; unknown 3).

Among records with observed numeric values, minimum age was median 18.0 years (interquartile range 18.0–18.0; range 0.0–75.0; observed 1,176 of 1,218). Maximum age was median 75.0 years (interquartile range 65.0–85.0; range 18.0–130.0; observed 456 of 1,218).

### Geriatric-context specification

At least one of the eight primary geriatric domains was publicly specified in 575 of 1,218 records (47.21%; unknown 319). Separately, a proxy-consent pathway was specified in 29 of 1,218 (2.38%; unknown 140).

Domain-specific public specification was frailty 11 of 1,218 (0.90%; unknown 32); mobility or function 291 of 1,218 (23.89%; unknown 164); cognition or decision capacity 157 of 1,218 (12.89%; unknown 136); nutrition 105 of 1,218 (8.62%; unknown 216); multimorbidity 7 of 1,218 (0.57%; unknown 64); life expectancy or advanced illness 135 of 1,218 (11.08%; unknown 22); care setting or caregiver 52 of 1,218 (4.27%; unknown 157); and polypharmacy 1 of 1,218 (0.08%; unknown 17). Proxy-consent pathways were reported separately as above.

### Planned CoreVen coverage

Within applicable venous-leg-ulcer active-treatment trials, any-planned coverage was healing 129 of 304 (42.43%; unknown 36); pain 115 of 304 (37.83%; unknown 25); quality of life 79 of 304 (25.99%; unknown 40); resource use 17 of 304 (5.59%; unknown 58); and adverse events 112 of 304 (36.84%; unknown 32).[5]

All CoreVen domains were covered by any planned outcome in 2 of 304 applicable trials (0.66%; unknown 61).

### Planned OUTPUTs coverage

Within applicable pressure-injury prevention trials, any-planned coverage was pressure-injury occurrence 40 of 184 (21.74%; unknown 29); precursor signs or symptoms 4 of 184 (2.17%; unknown 33); mobility 29 of 184 (15.76%; unknown 28); acceptability or comfort 23 of 184 (12.50%; unknown 28); adherence or compliance 4 of 184 (2.17%; unknown 33); and adverse events or safety 22 of 184 (11.96%; unknown 27).[6]

All OUTPUTs domains were covered by any planned outcome in 0 of 184 applicable trials (0.00%; unknown 33).

### Prespecified descriptive contrasts

Comparing the prespecified earlier period (2008–2016) with the later period (2019–2025), finite structured upper-age limits were present in 33.86% versus 39.75% of records, an absolute difference of +5.89 percentage points. Reconciled accessibility at age 85 years was 73.64% versus 64.44%, an absolute difference of −9.20 percentage points. At least one primary geriatric domain was publicly specified in 40.68% versus 51.86%, an absolute difference of +11.18 percentage points. These were descriptive finite-population contrasts.

For venous-leg-ulcer active treatment versus pressure-injury prevention, reconciled accessibility at age 85 years was 78.95% versus 67.93%, an absolute difference of −11.01 percentage points. At least one primary geriatric domain was publicly specified in 27.30% versus 63.59%, an absolute difference of +36.28 percentage points.

## Discussion

The validated registry audit separates age accessibility, public geriatric-context specification, and condition-specific planned outcome coverage. These dimensions cannot be replaced by a single older-adult applicability score and should not be interpreted as actual enrollment, patient-level diagnoses, measured frailty, or treatment effects.

Parallel structured and reconciled age measures make field interpretation and missingness visible. Neither scale establishes the age distribution of enrolled participants, and the absence of an explicit upper-age limit does not show that older adults were recruited.

The public registry often did not specify primary geriatric domains. Not-publicly-specified and expert-decision states therefore mark limits of public evidence; they are not evidence that a domain was clinically absent. Proxy-consent pathways were reported separately because they concern decision-making access rather than the eight clinical geriatric domains. Improved registry specification could support more transparent judgments about older-adult relevance.

Planned outcome coverage was incomplete within both approved framework populations, but the denominators and clinical purposes differ. CoreVen findings are confined to venous-leg-ulcer active treatment, and OUTPUTs findings to pressure-injury prevention.[5,6] Pressure-injury treatment, venous-leg-ulcer recurrence prevention, and mixed-wound studies remain descriptive and are not forced into either framework.

Keeping unknown, unclear, not-applicable, not-publicly-specified, and expert-decision states separate prevents unsupported conversion of missing registry information into clinical absence. Primary-only and any-planned windows likewise answer different questions and were not combined. The registration-period comparisons were prespecified descriptive contrasts between 2008–2016 and 2019–2025 and do not establish temporal causation.

## Strengths and limitations

Strengths include a frozen adjudicated population, hash-verified official JSON, human-confirmed final eligibility and coding, principal-investigator adjudication, framework-specific denominators, explicit missing states, denominator-level audits, and fresh independent validation before interpretation.

The study is limited to publicly registered information. Registry-defined age accessibility does not establish actual enrollment; geriatric-domain codes do not represent patient diagnoses or a validated frailty scale; and planned outcomes are not reported clinical results. The frozen population should not be generalized to all trials worldwide.

Reporter and unit-of-analysis fields had lower reliability and are retained only for supplementary or exploratory description. They do not support the primary interpretation.

The Record History conditional module was not executed because no version-level official history dataset was frozen. The guide document is supporting audit material only and had no analytic impact. Any future execution requires a governed amendment.

The added-record cross-scale quality-control agreement is not traditional unassisted independent-human reliability. Final decisions and scientific responsibility remained with the named human investigators.

## Conclusions

Older-adult relevance in registered chronic-wound trials requires separate appraisal of age accessibility, geriatric-context specification, and condition-specific planned outcome coverage. The corrected validated audit identifies opportunities to improve registry completeness and trial planning while avoiding claims about treatment effects, causality, actual enrollment, age discrimination, or global representativeness.

## Ethics statement

This study analyzed only publicly available ClinicalTrials.gov registration records and did not involve participant recruitment, intervention, contact, access to identifiable private data, or use of patient-level clinical records. The lead institution determined that this public-data registry audit was exempt from formal ethics review and that informed consent was not required.

## Data availability

The source records analyzed in this study are publicly accessible through ClinicalTrials.gov.[7] The governed project retains the frozen list of 1,218 NCT identifiers, source hashes, minimized derived analysis data, final human-confirmed coding, validated tables and figures, and provenance records. A public reproducibility release package has been prepared. The final public repository URL and archival DOI will be inserted after repository creation and verification and before manuscript submission.

## Code availability

The complete analysis code, independent validation code, environment lock files, tests, analytical input manifest, validated tables and figures, and reproducibility documentation have been assembled in a public-release package. Nature Portfolio requires central custom code to be accessible and described in a separate Code availability section. A dedicated public GitHub repository and DOI-bearing archival release will be created and the verified identifiers inserted before submission. No repository URL is claimed in this draft because the dedicated repository has not yet been created.

## Author contributions

Guoyong Wang: Conceptualization, methodology, formal analysis, investigation, project administration, validation, visualization, writing—original draft, and writing—review and editing. Kaijun Zhang: Methodology, investigation, literature verification, validation, and writing—review and editing. Jiyue Jiang: Software, data curation, formal analysis, methodology, validation, visualization, and writing—review and editing. Chaonan Wang: Investigation, data curation, validation, funding acquisition, and writing—review and editing. Weixin Wang: Investigation, data curation, independent validation, and writing—review and editing. Hui Bi: Methodology, geriatric-construct validation, clinical interpretation, and writing—review and editing. Haojun Liang: Methodology, wound-clinical validation, outcome-framework validation, and writing—review and editing. Zuoliang Qi: Supervision, resources, senior clinical validation, and writing—review and editing. Ying Huang: Methodology, supervision, project administration, and writing—review and editing. Yu Li: Methodology, software audit, formal analysis, independent reproducibility validation, supervision, visualization, and writing—review and editing. Xiaonan Yang: Conceptualization, supervision, resources, funding acquisition, clinical validation, and writing—review and editing. All authors approved the final manuscript and agree to be accountable for their own contributions and for resolving questions concerning the accuracy or integrity of the work.

## Funding

Xiaonan Yang acknowledges support for this work from the Special Program for Clinical and Translational Medical Research of the Chinese Academy of Medical Sciences (2025-12M-C&T-B-067), the National Clinical Key Specialty Construction Project (23003), the Plastic Medicine Research Fund of the Chinese Academy of Medical Sciences (2024-ZX-1-01), and the Special Research Fund for Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College (YSZ2024CG007). Chaonan Wang acknowledges support from the Beijing Natural Science Foundation (L256048). No other funding was reported for this work.

## Competing interests

The authors declare no competing interests.

## Acknowledgements

None.


## References

1. Zulman, D. M. et al. Examining the evidence: a systematic review of the inclusion and analysis of older adults in randomized controlled trials. *J. Gen. Intern. Med.* **26**, 783–790 (2011). https://doi.org/10.1007/s11606-010-1629-x
2. van Deudekom, F. J. et al. External validity of randomized controlled trials in older adults, a systematic review. *PLoS ONE* **12**, e0174053 (2017). https://doi.org/10.1371/journal.pone.0174053
3. Zarin, D. A., Tse, T., Williams, R. J. & Carr, S. Trial reporting in ClinicalTrials.gov—the final rule. *N. Engl. J. Med.* **375**, 1998–2004 (2016). https://doi.org/10.1056/NEJMsr1611785
4. Williamson, P. R. et al. The COMET Handbook: version 1.0. *Trials* **18** (Suppl 3), 280 (2017). https://doi.org/10.1186/s13063-017-1978-4
5. Hallas, S. et al. Development of a core outcome set for use in research evaluations of interventions for venous leg ulceration: international eDelphi consensus. *J. Tissue Viability* **33**, 324–331 (2024). https://doi.org/10.1016/j.jtv.2024.02.006
6. Lechner, A. et al. Core outcomes for pressure ulcer prevention trials: results of an international consensus study. *Br. J. Dermatol.* **187**, 743–752 (2022). https://doi.org/10.1111/bjd.21741
7. ClinicalTrials.gov. U.S. National Library of Medicine. https://clinicaltrials.gov/ (accessed 25 July 2026).
