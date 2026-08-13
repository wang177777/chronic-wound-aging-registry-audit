# Age accessibility, geriatric context, and registered outcome coverage in chronic wound trials

Guoyong Wang<sup>1,†</sup>, Fabao Hao<sup>7,†</sup>, Jiyue Jiang<sup>3,†</sup>, Kaijun Zhang<sup>2,†</sup>, Weixin Wang<sup>1</sup>, Chaonan Wang<sup>1</sup>, Hui Bi<sup>4</sup>, Haojun Liang<sup>5</sup>, Zuoliang Qi<sup>5</sup>, Ying Huang<sup>2</sup>, Yu Li<sup>3,6</sup>, Xiaonan Yang<sup>1,*</sup>

## Affiliations

1. Department of Hemangioma and Vascular Malformation, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China.

2. Department of Gastroenterology, Children’s Hospital of Fudan University, National Children’s Medical Center, No. 399 Wanyuan Road, Minhang District, Shanghai 201102, People’s Republic of China.

3. Department of Computer Science and Engineering, The Chinese University of Hong Kong, Sha Tin, New Territories, Hong Kong SAR, China.

4. Department of Internal Medicine, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China.

5. Department of Comprehensive Plastic Surgery, Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College, Beijing 100144, China.

6. The CUHK Shenzhen Research Institute, Hi-Tech Park, Nanshan, Shenzhen 518057, China.

7. Children’s Trauma Center, Qingdao Women and Children’s Hospital, Women and Children’s Hospital, Qingdao University, Qingdao, China.

†These authors contributed equally: Guoyong Wang, Fabao Hao, Jiyue Jiang and Kaijun Zhang.

*Correspondence: Xiaonan Yang (yxnan@aliyun.com).

## Abstract

Older adults with chronic wounds may be formally eligible for trials while geriatric complexity and patient-important outcomes remain incompletely specified. We audited 1,218 eligible ClinicalTrials.gov records first posted in 2008–2025 using hash-verified frozen JSON. Reconciled eligibility at age 85 was documented for 858 records (70.44%), at least one of eight geriatric-context domains for 575 (47.21%), and both features for 392 (32.18%). In venous-leg-ulcer active-treatment trials, complete any-registered CoreVen coverage occurred in 2 of 304 records; in pressure-injury-prevention trials, complete OUTPUTs coverage occurred in 0 of 184. Domain-level coverage varied substantially and indeterminate states were common. These registry-level findings distinguish formal age access from public documentation of geriatric context and registered outcome coverage, three complementary dimensions of trial transparency for older adults.

## Introduction

Older adults remain incompletely represented in many trials.[1,2] Restrictive eligibility criteria can narrow the generalizability of trial evidence.[3] Participation also depends on practical access, consent processes, comorbidity, transport, and tolerable study burden.[4] Empirical analyses of cancer trials and regulatory submissions show age-related gaps between study participants and populations likely to use interventions.[5,6] Reviews of participation barriers further indicate that enrollment systems must be designed around older adults’ needs.[7] A permissive chronological-age criterion alone does not resolve these gaps. Eligibility establishes who may enter a study under the protocol; it does not show who was approached, enrolled, retained, or represented in the final analysis. Assessing older-adult applicability therefore requires formal access to be distinguished from the clinical complexity that shapes participation and outcome relevance.

Frailty is multidimensional and can be represented by a clinical phenotype.[8,9] Mobility, cognition, nutrition, and other geriatric syndromes interact across conventional disease boundaries.[10] Multimorbidity is common in later life.[11] It also complicates the applicability of single-disease guidance and trial evidence.[12,13] Polypharmacy adds treatment burden and safety concerns that may not be visible in a diagnosis-only description.[14] A deficit-accumulation approach provides a complementary model of frailty rather than an interchangeable label.[15] In a public registry, these dimensions are observable as documented design context rather than measured patient phenotypes.

Chronic wounds impose substantial clinical and functional burdens.[16,17] Venous leg ulcers are particularly relevant to older populations.[18] Their health-system and humanistic burdens are also substantial.[19,20] Pressure injuries intersect with multimorbidity and remain common among hospitalized adults.[21,22] Pressure injury is the main manuscript term; pressure ulcer is retained when reproducing OUTPUTs terminology and source titles. Trial applicability in this area is consequently multidimensional. An older person may be age-eligible while a protocol says little about mobility, cognition, nutrition, life expectancy, care setting, or medication burden. Conversely, a study may specify some geriatric context but select registered outcome entries that do not cover domains considered important by patients, clinicians, and other stakeholders.

ClinicalTrials.gov provides structured public information on study design and results reporting under a defined regulatory framework.[23,24] Incomplete posting and selective outcome reporting constrain the public evidence base.[25,26] Discrepancies between registrations and publications create an additional source of uncertainty.[27,28] Registry-based meta-research therefore requires explicit attention to record versions, field definitions, missingness, and denominator construction.[29] A registration record is valuable because it exposes entered design information at scale, but it remains a public design record rather than participant-level data or a substitute for a clinical study report.

Core outcome sets define minimum outcomes for consistent measurement and reporting.[30,31] Established standards guide their development and reporting.[32,33] CoreVen was developed through a protocol and a systematic outcome review for venous leg ulcer treatment trials.[34,35] International consensus then identified patient-important domains including healing, pain, and quality of life.[36] These domains align with separate evidence on the lived importance of pain and quality of life in venous leg ulcer care.[37] The OUTPUTs programme was developed specifically for pressure-ulcer prevention trials through a protocol and an outcome-classification review.[38,39] International consensus established six core domains, and subsequent commentary emphasized their value for standardizing prevention research.[40,41] The two frameworks address different clinical purposes and populations and were therefore analyzed separately. We therefore examined age accessibility, public specification of eight primary geriatric domains, separately reported proxy-consent pathways, and registered CoreVen or OUTPUTs domain coverage in their prespecified condition-specific applicable trial groups. Our prespecified premise was that age accessibility, geriatric-context specification, and condition-specific registered outcome-domain coverage are related but non-interchangeable dimensions of registry-level older-adult applicability.

## Methods

### Study design and review amendment

This was a cross-sectional registry audit of every eligible record in a frozen cohort; the trial-registration record was the primary unit of analysis. Counts, denominators, proportions, unknown counts, medians, interquartile ranges and ranges were descriptive summaries of the complete frozen cohort. Reporting was informed by STROBE and partially cross-walked to RECORD.[42,43] The original protocol and statistical analysis plan were frozen before the formal reliability assessment and before inspection of the primary results. After completion of the original analysis, a dated amendment on 29 July 2026 added cohort-flow, missingness-bound, registration-timing, core-outcome-set publication-time, joint-distribution, posted-age-category and supplementary reliability analyses. These modules are reported as secondary descriptive or sensitivity analyses.

### Data source, retrieval and candidate construction

We used the AACT database snapshot[44] and the ClinicalTrials.gov version 2 API (https://clinicaltrials.gov/data-api/about-api; accessed 28 July 2026). Data acquisition closed on 25 July 2026. Frozen API condition and term queries and literal case-folded AACT searches covered venous-leg-ulcer and pressure-injury terminology across titles, conditions, keywords, summaries, descriptions, eligibility criteria and browse conditions. Pagination used 1,000-record pages until no next-page token remained. Non-additive query paths yielded 5,693 AACT exact hits, 8,496 AACT broad hits, 10,765 API condition hits and 72,328 API term hits. Deduplication by NCT identifier produced 34,972 candidates (15,438 exact-retrieved and 19,534 broad-only) before eligibility review.

### Eligibility, scope and cohort correction

Eligible records were interventional studies of venous-leg-ulcer (VLU) active treatment or recurrence prevention, pressure-injury prevention or treatment, or mixed-wound studies with a separable target component. Other wound types were outside scope unless this separability rule was met. The prespecified 120-record reliability sample was independently screened by Chaonan Wang and Weixin Wang and adjudicated by Guoyong Wang when their decisions differed. For the remaining 34,852 candidates, a source-linked computational workflow assisted the initial provisional classification under sensitivity- and specificity-oriented boundary policies. Chaonan Wang and Weixin Wang then independently rereviewed all 34,852 candidates from the frozen source evidence under a harmonized protocol, without access to AI outputs or each other's labels. Their concordant decisions confirmed 32,583 common exclusions, while 2,269 boundary records received focused review. Guoyong Wang adjudicated disagreements and unresolved records, and the cohort used the resulting human-reviewed decisions.

The exclusion audit comprised a 300-record fixed-seed probability sample and a separate 200-record boundary-enriched sample. Reviewers were blinded to the previous exclusion decision and rationale. One eligible record was found in the enriched stratum, prompting a rule-based high-sensitivity scan of all 33,658 exclusions in the full-screening component. The scan searched titles, conditions, eligibility text and intervention descriptions for prespecified direct VLU and pressure-injury signals, non-standard purpose labels and contradictory exclusion rationales, while suppressing isolated positional uses of prone or decubitus. Dual human review, expert review and principal-investigator adjudication of 915 flagged records yielded 12 eligible additions and 33,646 remaining exclusions. Together with the separately adjudicated reliability sample, the corrected cohort comprised 1,218 included and 33,754 excluded records, with no duplicate NCT identifiers (Figure 1; Supplementary Table S1). Because the scan targeted prespecified triggers, it did not provide a post-scan population false-negative estimate.

### Frozen record version and registration timing

Every included NCT identifier was bound to a complete official JSON file and SHA-256 value; coverage was 1,218/1,218. The signed original master contained 18,270 age rows, 10,962 geriatric-domain rows, 1,218 framework rows and 7,633 distinct registered outcome rows. The append-only age-correction layer preserved the 18,270-row age layer. Chaonan Wang and Weixin Wang independently confirmed all 431 affected records, and Guoyong Wang approved 431/431 final corrections; no records remained unresolved. The analysis represents the frozen current record at acquisition; complete official version histories were unavailable, so outcome fields are described as registered in that snapshot.

Registration was classified as prospective or same-day when first submission did not follow study start, retrospective when it did, and unknown when either date was unavailable. Framework-date analyses used the earliest verified electronic publication date: 4 March 2024 for final CoreVen and 9 August 2022 for final OUTPUTs. The latter differs from the 1 November 2022 issue/online metadata on publisher and Crossref records; the earliest PubMed electronic date was frozen, and the discrepancy was retained. Records were classified as pre-final COS or as posted at least 0, 6 or 12 months after publication. These strata provided descriptive timing categories rather than measures of framework awareness or adoption.

### Age accessibility and posted age-category results

Structured minimum and maximum ages and the complete eligibility text were extracted from frozen JSON. Sub-year units were converted to years; strict lower and upper inequalities were preserved; cohort-specific inclusion and exclusion clauses were interpreted in section context; a lower-bound exclusion was not treated as an upper limit; and multiple explicitly enrolled target cohorts were evaluated over their union. Exact source evidence was required for free-text rules such as “any age” or adult-only eligibility. Accessibility was prespecified as a threshold ladder at ages 65, 75, 80 and 85 years and was reported on separate structured and reconciled scales. Age 85 was the highest prespecified threshold, chosen to test formal protocol access at advanced old age rather than selected after examining condition-specific results. A finite structured upper-age limit was also reported. “No explicit structured upper-age limit” refers to registry field status; recruitment was outside the scope of this measure. Two 130-year maximum-age entries were source-verified as Years and retained; excluding them affected only the observed maximum range endpoint.

For records with posted results, the full results module was searched for age-category groups. Categories were retained only when their age boundaries were interpretable. This exploratory registry summary describes posted age-category fields rather than participant-level age distributions.

### Geriatric-context documentation

Eight clinical domains were assessed: frailty; mobility, activities of daily living or function; cognition or decision capacity; nutrition or malnutrition; multimorbidity burden; life expectancy or advanced illness; care setting or caregiver involvement; and polypharmacy or medication burden. Proxy consent was a ninth, separately reported access domain. Each domain was classified as PRESENT, NOT_PUBLICLY_SPECIFIED or INDETERMINATE_AFTER_REVIEW from the frozen public record. PRESENT captured the recorded function, including an inclusion criterion, exclusion criterion, support or accommodation, stratification factor, measurement, intervention component or contextual description. Directionality was additionally classified across 788 source-linked PRESENT rows as exclusion or restriction, inclusion or accommodation, baseline measurement or stratification, consent or proxy support, intervention or care adaptation, contextual description, multiple functions, or indeterminate direction. Two named reviewers independently coded these rows, followed by geriatric-domain expert review and principal-investigator adjudication. Analysis used the final reviewed labels. Agreement was calculated from the reviewers’ pre-adjudication labels. The eight domains were retained separately rather than combined into a geriatric score.

### Registered outcome-domain coverage

Each distinct current-snapshot primary or secondary outcome entry retained its level, measure, description, time frame, exact JSON Pointer and source hash. “Primary-registered” denotes mapped primary outcome fields in the frozen current record; “any-registered” denotes primary or secondary fields. These labels characterize the level and scope of outcome fields in the registry snapshot.

CoreVen was applied only to 304 VLU active-treatment records and was operationalized at the five published consensus-domain levels: healing, pain, quality of life, resource use and adverse events. The 11 CoreVen outcome items were grouped into these five parent domains, with all items retained. OUTPUTs was applied only to 184 pressure-injury-prevention records using its six published domains: pressure-ulcer occurrence, precursor signs or symptoms, mobility, acceptability or comfort, adherence or compliance, and adverse events or safety. Mapping used the registered measure, description and time frame; proxy or process measures required explicit evidence of a domain match. The source-to-operational crosswalk and merge rules are provided in Supplementary Table S21. Complete coverage required every applicable framework domain within the stated window. VLU recurrence, pressure-injury treatment and mixed-wound studies remained descriptive outside the framework-applicable populations.

### Missingness, bounds and joint analyses

Publication-facing INDETERMINATE_AFTER_REVIEW preserved underlying unknown, unclear and expert-decision states without reassignment. For every principal metric we calculated: (1) confirmed full-cohort percentage; (2) confirmed evaluable-denominator percentage; (3) lower bound, treating indeterminate records as not present; (4) upper bound, treating all indeterminate records as present; and (5) indeterminate percentage. NOT_APPLICABLE was retained separately.

Trial-level joint tables cross-classified reconciled age-85 accessibility, any public documentation across the eight geriatric domains, and framework-specific any-registered coverage. CoreVen and OUTPUTs denominators remained separate. The dimensions were retained separately without a composite older-adult-applicability score.

### Artificial intelligence and human verification

OpenAI Codex (GPT-5.6 and GPT-5.6 Pro service environments) assisted the initial provisional screening, coding and manuscript drafting. Final classifications, analyses and manuscript content were independently reviewed and approved by human investigators, with final verification by Guoyong Wang.

The prespecified formal reliability analysis used 120 records independently assessed by two human reviewers, with agreement calculated from their pre-adjudication labels. Supplementary human agreement audits were conducted for 788 geriatric-directionality rows and a fixed-seed sample of 100 registered outcome rows (50 CoreVen and 50 OUTPUTs). The latter underwent independent two-reviewer mapping, outcome-domain expert review and principal-investigator adjudication. Agreement was calculated from the reviewers’ pre-adjudication labels. Reviewer confirmations, adjudication records, and reproducibility materials are retained in the study archive.

### Statistical analysis and validation

The analysis was descriptive and used observations, denominators, proportions, unknown counts, medians, interquartile ranges, ranges and absolute percentage-point differences. Following human confirmation, the complete age-corrected analysis was rerun in the project environment and independently in a clean environment. Both runs verified all 1,221 inputs and 1,218 frozen JSON records and produced 36 byte-identical scientific outputs. Independent validation reconciled all 596 denominator rows, 17 age checks and seven conclusion anchors. Weiwei Chen independently reviewed the complete evidence package and confirmed reproducibility.

## Results

### Cohort ascertainment and characteristics

The 34,972-record candidate frame was fully adjudicated. Twelve audit-driven additions produced 1,218 included records, with no duplicate NCT identifiers and complete JSON/hash coverage (Figure 1; Supplementary Table S1). The cohort comprised 304 VLU active-treatment, 25 VLU recurrence-prevention, 184 pressure-injury-prevention, 517 pressure-injury-treatment, 186 explicit mixed-wound and 2 other governed mixed-wound records. Registration was prospective or same-day for 698/1,218 (57.31%), retrospective for 519/1,218 (42.61%) and unknown for 1/1,218 (0.08%). Randomization was recorded for 809/1,218 (66.42%; unknown, 2), and 595/1,218 (48.85%) were device studies (Table 1).

### Age eligibility

In the age-corrected analysis, structured accessibility was 1,098/1,218 at age 65 years (90.15%; indeterminate, 39), 970/1,218 at age 75 (79.64%; 39), 915/1,218 at age 80 (75.12%; 39) and 847/1,218 at age 85 (69.54%; 39). Reconciled values were 1,103/1,218 (90.56%; indeterminate, 27), 978/1,218 (80.30%; 27), 925/1,218 (75.94%; 27) and 858/1,218 (70.44%; 27), respectively (Figure 2; Supplementary Tables S3 and S4).

A finite structured upper-age limit appeared in 456/1,218 records (37.44% of all records; 38.64% of 1,180 evaluable; indeterminate, 38/1,218 [3.12%]); 724 had no explicit structured upper limit. Structured and reconciled age fields conflicted in 32 records. Reconciliation narrowed accessibility for 8 records, widened it for 1, resolved structured-field uncertainty from full eligibility text for 12, and retained the same four threshold categories despite a source conflict for 11. Across the four thresholds, the corresponding cell changes were 39 UNKNOWN-to-YES, 9 UNKNOWN-to-NO, 8 YES-to-NO and 3 NO-to-YES. Source-linked examples and the classification rules are provided in Supplementary Table S22. Among observed numeric values, minimum age was a median of 18 years (IQR, 18–18; range, 0–75; observed, 1,179), and maximum age was 75 years (IQR, 65–85; range, 18–130; observed, 456). Excluding the two verified 130-year entries changed only the upper range endpoint.

### Geriatric-context documentation and joint distribution

At least one of eight clinical geriatric-context domains was publicly documented in 575/1,218 records (47.21% of all; 63.96% of 899 evaluable; indeterminate, 319/1,218 [26.19%]). Mobility/function was documented in 291 (23.89%; indeterminate, 164), cognition/capacity in 157 (12.89%; 136), life expectancy/advanced illness in 135 (11.08%; 22), nutrition in 105 (8.62%; 216), care setting/caregiver involvement in 52 (4.27%; 157), frailty in 11 (0.90%; 32), multimorbidity burden in 7 (0.57%; 64), and polypharmacy/medication burden in 1 (0.08%; 17). Proxy-consent pathways were separately documented in 29/1,218 (2.38% of all; 2.69% of 1,078 evaluable; indeterminate, 140/1,218 [11.49%]) (Figure 3; Supplementary Tables S5 and S6).

Across 788 source-linked PRESENT rows, final direction labels identified 247/788 exclusion-or-restriction statements (31.35%), 118/788 inclusion-or-accommodation statements (14.97%), 97/788 baseline-measurement-or-stratification statements (12.31%), 29/788 consent-or-proxy-support statements (3.68%), 90/788 intervention-or-care-adaptation statements (11.42%), 106/788 contextual descriptions (13.45%), 2/788 multiple-function statements (0.25%) and 99/788 indeterminate directions (12.56%). These source-row categories describe the operational function of public text and do not establish participant-level exclusion, support or clinical prevalence (Supplementary Table S19).

In the age-corrected analysis, the age-85 and geriatric-context dimensions overlapped incompletely: 392/1,218 records (32.18%) were both age-85 accessible and had at least one publicly documented geriatric domain; 240 (19.70%) were accessible with no such public documentation, and 226 (18.56%) were accessible but geriatric-context status remained indeterminate (Supplementary Figure S1; Supplementary Table S12). These cells describe record states and not participant characteristics.

### CoreVen registered domain coverage and publication timing

Among 304 VLU active-treatment records, complete any-registered CoreVen coverage occurred in 2/304 (0.66% of all; 0.83% of 242 evaluable; indeterminate, 62/304). Complete primary-registered coverage was 0/304 (indeterminate, 22). Any-registered coverage ranged from 132/304 for healing (43.42%) and 115/304 for pain (37.83%) to 18/304 for resource use (5.92%); primary-registered coverage ranged from 89/304 for healing (29.28%) to 1/304 for resource use (0.33%). Full domain-level results, including indeterminate counts, are reported in Figure 4 and Supplementary Tables S7 and S20.

Using the final CoreVen electronic publication date of 4 March 2024, complete any-registered coverage was 1/265 (indeterminate, 54) before publication, 1/39 (indeterminate, 8) after publication without a lag, 1/31 (indeterminate, 7) after a 6-month lag and 0/12 (indeterminate, 3) after a 12-month lag. The post-publication strata were small and were used to describe timing rather than framework adoption.

### OUTPUTs registered domain coverage and publication timing

Among 184 pressure-injury-prevention records, complete any-registered OUTPUTs coverage was 0/184 (0.00% of all; 0.00% of 152 evaluable; indeterminate, 32/184); complete primary-registered coverage was 0/184 (indeterminate, 22). Any-registered coverage ranged from 43/184 for pressure-ulcer occurrence (23.37%) and 32/184 for mobility (17.39%) to 5/184 for precursor signs or symptoms and 5/184 for adherence or compliance (2.72% each). Primary-registered coverage ranged from 37/184 for pressure-ulcer occurrence (20.11%) to 1/184 for adherence or compliance (0.54%). Full domain-level results are reported in Figure 4 and Supplementary Tables S9 and S20.

Using the final OUTPUTs electronic publication date of 9 August 2022, complete any-registered coverage was 0/120 (indeterminate, 15) before publication, 0/64 (indeterminate, 17) after publication without a lag, 0/56 (indeterminate, 17) after a 6-month lag and 0/49 (indeterminate, 16) after a 12-month lag. These post-publication strata were small and used descriptively.

### Registration-timing sensitivity

Among prospectively or same-day registered framework-applicable records, complete any-registered coverage was 2/165 (indeterminate, 40) for CoreVen and 0/104 (indeterminate, 21) for OUTPUTs. Corresponding retrospective strata were 0/139 (indeterminate, 22) and 0/80 (indeterminate, 11). Current-snapshot outcome edits leave residual temporal ambiguity in this stratification.

### Posted age-category exploration

Results were posted for 207/1,218 records (17.00%). This subset was compositionally different from the full cohort: 133/207 (64.25%) were first registered in 2008–2016 versus 440/1,218 (36.12%) overall, 153/207 (73.91%) were completed versus 590/1,218 (48.44%) overall, and disease-group proportions also differed (Supplementary Table S23). Interpretable age-category groups were extractable for 96 records (7.88% of all records; 46.38% of records with results), and 86 records explicitly displayed an older age category (7.06% of all; 41.55% of records with results) (Supplementary Table S13). The 46.38% denominator summarizes availability within this selected subgroup; participant age representation remained unmeasured.

### Reliability and validation

In the 120-record prespecified independent human reliability sample, eligibility agreement was 119/120 (99.17%), Cohen κ was 0.9556 and Gwet AC1 was 0.9908. INCLUDE-specific agreement was 100.00% and EXCLUDE-specific agreement was 99.53%; the sole disagreement was EXCLUDE versus UNCERTAIN. With UNCERTAIN retained as a third category, these label-specific statistics are category-specific rather than binary positive agreement. The supplementary independent human agreement audit for geriatric directionality yielded 713/788 agreements and 75/788 disagreements (raw agreement, 0.9048223350; Cohen κ, 0.8835674462). The supplementary independent human outcome-mapping audit yielded 90/100 agreements and 10/100 disagreements (raw agreement, 0.9000000000; Cohen κ, 0.8805542284). All agreement statistics use pre-adjudication human labels. All derived numerical outputs passed deterministic reconciliation (Supplementary Tables S14 and S15).

## Discussion

This audit separates three complementary dimensions of registry-level trial transparency for older adults: formal age accessibility, public documentation of geriatric context and condition-specific registered outcome-domain coverage. Many records permitted entry at older ages, whereas geriatric-context documentation was less common and often indeterminate. Outcome-domain coverage overlapped only partly with both measures. Together, the results show that protocol access alone provides an incomplete account of trial applicability for older adults.

Age-85 accessibility describes protocol-level access, while actual representation depends on recruitment, retention and analysis. Structured age fields were reproducible but incomplete; full-text reconciliation added context and required governed judgment. The posted-results exploration could not bridge this gap because only 207 records had results, fewer than half contained interpretable age categories and the category definitions varied. Standardized participant age-band reporting would make representation directly assessable.

Geriatric-context coding captured what the public record documented. PRESENT could denote a restriction, accommodation, assessment, intervention component or contextual statement, and indeterminate states captured unresolved source ambiguity. The large difference between full-cohort and evaluable-denominator percentages shows the value of presenting missingness explicitly. Keeping the eight domains separate, and treating proxy consent as an access domain, also preserved their distinct clinical meanings.

CoreVen and OUTPUTs provided condition-specific reference frameworks rather than geriatric quality measures. Primary-registered and any-registered windows addressed complementary questions about outcome priority and breadth. Most applicable trials predated the final frameworks, post-publication strata were small and current registry outcomes may have been edited; accordingly, the publication-time analysis describes temporal patterns rather than adoption. Studying adoption would require complete version histories and dates of outcome-field changes.

These findings point to practical improvements in registry design. Structured fields could distinguish whether geriatric constructs function as restrictions, supports, measurements or intervention components; outcome entries could include clearer provenance; and posted results could use standardized age categories. Trial teams could also state the rationale for age thresholds, approaches to participation burden and consent access, and the condition-specific outcome domains covered by the protocol.

The cohort correction illustrates the value of sensitive retrieval, append-only correction and reproducible rebuilding. The 12 additions changed the cohort, while preservation of both versions made the correction and its consequences auditable. Other strengths include complete source-hash coverage, explicit retrieval paths, independent human review, principal-investigator adjudication, framework-specific denominators, preservation of indeterminate states, missingness bounds and deterministic reproduction.

Several limitations shape interpretation. ClinicalTrials.gov is not a global census, records can be incomplete or revised and complete version histories were unavailable. The measures describe registry documentation rather than participant prevalence, treatment effects or global trial quality. Publication-time strata were small, and the posted-results subgroup was selected and used heterogeneous age groups. The targeted exclusion scan focused on records meeting prespecified triggers, so residual misses remain possible. Some mappings required expert judgment, and the formal reliability sample included 120 records; the directionality and outcome-mapping agreement analyses were task-specific supplementary audits.

Overall, formal age accessibility, geriatric-context documentation and registered outcome-domain coverage were related but incompletely overlapping. Treating them as separate empirical dimensions offers a clearer basis for improving registry transparency and evaluating trial applicability for older adults.

## Data availability

ClinicalTrials.gov source records are publicly accessible by NCT identifier. The project retains the frozen 1,218-identifier list, source hashes, minimized derived data, signed coding, age-correction ledger, validated tables and provenance records. Data-minimized materials are available at https://github.com/wang177777/chronic-wound-aging-registry-audit.

## Code availability

Project code and data-minimized reproducibility materials are available at https://github.com/wang177777/chronic-wound-aging-registry-audit, with the manuscript-aligned version archived as release v1.2.12 (https://github.com/wang177777/chronic-wound-aging-registry-audit/releases/tag/v1.2.12).

## Author contributions

G.W.: Conceptualization, methodology, formal analysis, investigation, project administration, validation, visualization, writing—original draft, and writing—review and editing. F.H.: Methodology, investigation, validation, writing—original draft, and writing—review and editing. J.J.: Software, data curation, formal analysis, methodology, validation, visualization, and writing—review and editing. K.Z.: Methodology, investigation, literature verification, validation, and writing—review and editing. W.W.: Investigation, data curation, independent validation, and writing—review and editing. C.W.: Investigation, data curation, validation, funding acquisition, and writing—review and editing. H.B.: Methodology, geriatric-construct validation, clinical interpretation, and writing—review and editing. H.L.: Methodology, wound-clinical validation, outcome-framework validation, and writing—review and editing. Z.Q.: Supervision, resources, senior clinical validation, and writing—review and editing. Y.H.: Methodology, supervision, project administration, and writing—review and editing. Y.L.: Methodology, software audit, formal analysis, independent reproducibility validation of the preceding cohort-correction analysis, supervision, visualization, and writing—review and editing. X.Y.: Conceptualization, supervision, resources, funding acquisition, clinical validation, and writing—review and editing.

All authors reviewed and approved the final manuscript and agree to be accountable for their contributions and for the integrity of the work.

## Acknowledgements

The authors thank Weiwei Chen for independent verification of the analysis and supporting materials.

## Funding

X.Y. discloses support for this work from the Special Program for Clinical and Translational Medical Research of the Chinese Academy of Medical Sciences [grant 2025-12M-C&T-B-067], the National Clinical Key Specialty Construction Project [grant 23003], the Plastic Medicine Research Fund of the Chinese Academy of Medical Sciences [grant 2024-ZX-1-01], and the Special Research Fund for Plastic Surgery Hospital, Chinese Academy of Medical Sciences and Peking Union Medical College [grant YSZ2024CG007]. C.W. discloses support for this work from the Beijing Natural Science Foundation [grant L256048]. These awards supported student research-assistant personnel costs. The funders had no role in study design, data acquisition, analysis, interpretation, manuscript preparation or the decision to submit.

## Competing interests

All authors declare no financial or non-financial competing interests.

## Ethics statement

This study used publicly available, non-identifiable aggregate records from ClinicalTrials.gov and published literature and did not involve human participants. Ethics approval and informed consent were not applicable.


## Figure legends

**Figure 1 | Cohort identification and adjudication flow.** a, Non-additive query-hit counts from the frozen AACT and ClinicalTrials.gov API paths were deduplicated to 34,972 unique NCT identifiers. b, The prespecified 120-record reliability component contained 12 included and 108 excluded records; independent final human rereview of the remaining 34,852 records yielded 1,194 included and 33,658 excluded records before correction. A 500-record audit comprised 300 probability-sampled and 200 boundary-enriched exclusions and identified one eligible record in the enriched stratum. The audit and subsequent rule-based scan of all 33,658 exclusions flagged 915 records for human and expert review and resulted in 12 total additions, giving 1,206 included and 33,646 excluded records in the full-screening component. Combining both components gave 1,218 included and 33,754 excluded records.

**Figure 2 | Structured and reconciled age accessibility.** **a**, Accessibility at four prespecified chronological ages using structured registry fields and separately reconciled full-eligibility evidence. **b**, Structured maximum-age-field status. Percentages use all 1,218 included records; indeterminate counts were preserved. The figure describes protocol eligibility rather than actual enrollment or representation.

**Figure 3 | Public documentation of geriatric context with indeterminate states.** **a**, Eight clinical domains were kept separate and displayed as publicly specified, not publicly specified, or indeterminate after review. Values printed at right give specified and indeterminate counts. **b**, Proxy-consent pathways were reported separately because they describe consent access rather than a clinical geriatric domain. The variables characterize registry-level documentation rather than patient diagnoses or frailty measurements.

**Figure 4 | Framework-specific registered outcome-domain coverage.** **a**, Primary-registered CoreVen domain coverage in venous-leg-ulcer active-treatment records. **b**, Any-registered CoreVen domain coverage. **c**, Primary-registered OUTPUTs domain coverage in pressure-injury-prevention records. **d**, Any-registered OUTPUTs domain coverage. Bars show confirmed full-denominator proportions. Indeterminate mapping states and denominator-sensitive results are reported in the Supplementary Information.


## Table legend

**Table 1 | Characteristics of the 1,218 included trial-registration records.** Values are n/N (%) unless stated otherwise. Unknown values are explicit. VLU, venous leg ulcer; PI, pressure injury; IQR, interquartile range.

## References

1. Zulman DM et al. Examining the evidence: a systematic review of the inclusion and analysis of older adults in randomized controlled trials. *J Gen Intern Med* **26**, 783-90 (2011). https://doi.org/10.1007/s11606-010-1629-x
2. van Deudekom FJ et al. External validity of randomized controlled trials in older adults, a systematic review. *PLoS One* **12**, e0174053 (2017). https://doi.org/10.1371/journal.pone.0174053
3. Van Spall HG, Toren A, Kiss A & Fowler RA. Eligibility criteria of randomized controlled trials published in high-impact general medical journals: a systematic sampling review. *JAMA* **297**, 1233-40 (2007). https://doi.org/10.1001/jama.297.11.1233
4. McMurdo ME et al. Improving recruitment of older people to research through good practice. *Age Ageing* **40**, 659-65 (2011). https://doi.org/10.1093/ageing/afr115
5. Ludmir EB et al. Factors Associated With Age Disparities Among Cancer Clinical Trial Participants. *JAMA Oncol* **5**, 1769-1773 (2019). https://doi.org/10.1001/jamaoncol.2019.2055
6. Lau SWJ et al. Participation of Older Adults in Clinical Trials for New Drug Applications and Biologics License Applications From 2010 Through 2019. *JAMA Netw Open* **5**, e2236149 (2022). https://doi.org/10.1001/jamanetworkopen.2022.36149
7. Denson AC & Mahipal A. Participation of the elderly population in clinical trials: barriers and solutions. *Cancer Control* **21**, 209-14 (2014). https://doi.org/10.1177/107327481402100305
8. Fried LP et al. Frailty in older adults: evidence for a phenotype. *J Gerontol A Biol Sci Med Sci* **56**, M146-56 (2001). https://doi.org/10.1093/gerona/56.3.m146
9. Clegg A, Young J, Iliffe S, Rikkert MO & Rockwood K. Frailty in elderly people. *Lancet* **381**, 752-62 (2013). https://doi.org/10.1016/s0140-6736(12)62167-9
10. Inouye SK, Studenski S, Tinetti ME & Kuchel GA. Geriatric syndromes: clinical, research, and policy implications of a core geriatric concept. *J Am Geriatr Soc* **55**, 780-91 (2007). https://doi.org/10.1111/j.1532-5415.2007.01156.x
11. Marengoni A et al. Aging with multimorbidity: a systematic review of the literature. *Ageing Res Rev* **10**, 430-9 (2011). https://doi.org/10.1016/j.arr.2011.03.003
12. Boyd CM et al. Clinical practice guidelines and quality of care for older patients with multiple comorbid diseases: implications for pay for performance. *JAMA* **294**, 716-24 (2005). https://doi.org/10.1001/jama.294.6.716
13. Salive ME. Multimorbidity in older adults. *Epidemiol Rev* **35**, 75-83 (2013). https://doi.org/10.1093/epirev/mxs009
14. Maher RL, Hanlon J & Hajjar ER. Clinical consequences of polypharmacy in elderly. *Expert Opin Drug Saf* **13**, 57-65 (2014). https://doi.org/10.1517/14740338.2013.827660
15. Rockwood K & Mitnitski A. Frailty defined by deficit accumulation and geriatric medicine defined by frailty. *Clin Geriatr Med* **27**, 17-26 (2011). https://doi.org/10.1016/j.cger.2010.08.008
16. Sen CK et al. Human skin wounds: a major and snowballing threat to public health and the economy. *Wound Repair Regen* **17**, 763-71 (2009). https://doi.org/10.1111/j.1524-475x.2009.00543.x
17. Falanga V et al. Chronic wounds. *Nat Rev Dis Primers* **8**, 50 (2022). https://doi.org/10.1038/s41572-022-00377-3
18. Margolis DJ, Bilker W, Santanna J & Baumgarten M. Venous leg ulcer: incidence and prevalence in the elderly. *J Am Acad Dermatol* **46**, 381-6 (2002). https://doi.org/10.1067/mjd.2002.121739
19. Guest JF et al. Health economic burden that wounds impose on the National Health Service in the UK. *BMJ Open* **5**, e009283 (2015). https://doi.org/10.1136/bmjopen-2015-009283
20. Olsson M et al. The humanistic and economic burden of chronic wounds: A systematic review. *Wound Repair Regen* **27**, 114-125 (2019). https://doi.org/10.1111/wrr.12683
21. Jaul E, Barron J, Rosenzweig JP & Menczel J. An overview of co-morbidities and the development of pressure ulcers among older adults. *BMC Geriatr* **18**, 305 (2018). https://doi.org/10.1186/s12877-018-0997-7
22. Li Z, Lin F, Thalib L & Chaboyer W. Global prevalence and incidence of pressure injuries in hospitalised adult patients: A systematic review and meta-analysis. *Int J Nurs Stud* **105**, 103546 (2020). https://doi.org/10.1016/j.ijnurstu.2020.103546
23. Zarin DA, Tse T, Williams RJ & Carr S. Trial Reporting in ClinicalTrials.gov - The Final Rule. *N Engl J Med* **375**, 1998-2004 (2016). https://doi.org/10.1056/nejmsr1611785
24. Zarin DA, Tse T, Williams RJ, Califf RM & Ide NC. The ClinicalTrials.gov results database--update and key issues. *N Engl J Med* **364**, 852-60 (2011). https://doi.org/10.1056/nejmsa1012065
25. Anderson ML et al. Compliance with results reporting at ClinicalTrials.gov. *N Engl J Med* **372**, 1031-9 (2015). https://doi.org/10.1056/nejmsa1409364
26. DeVito NJ, Bacon S & Goldacre B. Compliance with legal requirement to report clinical trial results on ClinicalTrials.gov: a cohort study. *Lancet* **395**, 361-369 (2020). https://doi.org/10.1016/s0140-6736(19)33220-9
27. Hartung DM et al. Reporting discrepancies between the ClinicalTrials.gov results database and peer-reviewed publications. *Ann Intern Med* **160**, 477-83 (2014). https://doi.org/10.7326/m13-0480
28. Jones CW, Keil LG, Holland WC, Caughey MC & Platts-Mills TF. Comparison of registered and published outcomes in randomized controlled trials: a systematic review. *BMC Med* **13**, 282 (2015). https://doi.org/10.1186/s12916-015-0520-3
29. Tse T, Fain KM & Zarin DA. How to avoid common problems when using ClinicalTrials.gov in research: 10 issues to consider. *BMJ* **361**, k1452 (2018). https://doi.org/10.1136/bmj.k1452
30. Williamson PR et al. The COMET Handbook: version 1.0. *Trials* **18**, 280 (2017). https://doi.org/10.1186/s13063-017-1978-4
31. Williamson PR et al. Developing core outcome sets for clinical trials: issues to consider. *Trials* **13**, 132 (2012). https://doi.org/10.1186/1745-6215-13-132
32. Kirkham JJ et al. Core Outcome Set-STAndards for Reporting: The COS-STAR Statement. *PLoS Med* **13**, e1002148 (2016). https://doi.org/10.1371/journal.pmed.1002148
33. Kirkham JJ et al. Core Outcome Set-STAndards for Development: The COS-STAD recommendations. *PLoS Med* **14**, e1002447 (2017). https://doi.org/10.1371/journal.pmed.1002447
34. Hallas S et al. Development of a core outcome set for venous leg ulceration (CoreVen) research evaluations (protocol). *J Tissue Viability* **30**, 317-323 (2021). https://doi.org/10.1016/j.jtv.2021.03.005
35. Hallas S, Nelson EA, O'Meara S & Gethin G. Identifying outcomes reported in trials of interventions in venous leg ulceration for a core outcome set development: A scoping review. *J Tissue Viability* **31**, 751-760 (2022). https://doi.org/10.1016/j.jtv.2022.07.013
36. Hallas, S., Nelson, E. A., O’Meara, S. & Gethin, G. Development of a core outcome set for use in research evaluations of interventions for venous leg ulceration: International eDelphi consensus. *J. Tissue Viability* **33**, 324–331 (2024). https://doi.org/10.1016/j.jtv.2024.02.006
37. Patton D et al. A systematic review of the impact of compression therapy on quality of life and pain among people with a venous leg ulcer. *Int Wound J* **21**, e14816 (2024). https://doi.org/10.1111/iwj.14816
38. Lechner A et al. Outcomes for Pressure Ulcer Trials (OUTPUTs): protocol for the development of a core domain set for trials evaluating the clinical efficacy or effectiveness of pressure ulcer prevention interventions. *Trials* **20**, 449 (2019). https://doi.org/10.1186/s13063-019-3543-9
39. Lechner A et al. Outcomes for Pressure Ulcer Trials (OUTPUTs) project: review and classification of outcomes reported in pressure ulcer prevention research. *Br J Dermatol* **184**, 617-626 (2021). https://doi.org/10.1111/bjd.19304
40. Lechner A et al. Core outcomes for pressure ulcer prevention trials: results of an international consensus study: Classification: Outcomes and qualitative research. *Br J Dermatol* **187**, 743-752 (2022). https://doi.org/10.1111/bjd.21741
41. Fledderus AC & Gout HA. A core outcome set for pressure ulcers: an important step towards standardized outcome reporting of prevention strategies. *Br J Dermatol* **187**, 634-635 (2022). https://doi.org/10.1111/bjd.21814
42. von Elm E et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *PLoS Med* **4**, e296 (2007). https://doi.org/10.1371/journal.pmed.0040296
43. Benchimol EI et al. The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. *PLoS Med* **12**, e1001885 (2015). https://doi.org/10.1371/journal.pmed.1001885
44. Tasneem, A. et al. The database for aggregate analysis of ClinicalTrials.gov (AACT) and subsequent regrouping by clinical specialty. *PLoS One* **7**, e33677 (2012). https://doi.org/10.1371/journal.pone.0033677
