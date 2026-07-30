# Corrected 1,218-record Step 13 prespecified primary analysis report

Historical primary-run status at execution: `PRIMARY_ANALYSIS_COMPLETED_PENDING_INDEPENDENT_VALIDATION`

Current release status: `INDEPENDENT_VALIDATION_PASS`

Execution date: 2026-07-28

## Scope and statistical position

This is a descriptive audit of the complete frozen population. The implementation reports observed
counts, denominators, percentages, unknown counts, medians, interquartile ranges, ranges, and
prespecified absolute percentage-point differences. It makes no final interpretation.

## Locked-input conservation

- Included NCT IDs: 1218/1,218
- Complete official JSON with matching hash: 1218/1,218
- Age rows: 18270/18,270
- Geriatric-domain rows: 10962/10,962
- Framework rows: 1218/1,218
- Planned outcome rows: 7633/7,633
- Unresolved final values: 0
- Duplicate outcome IDs: 0

## Prespecified descriptive checkpoints

- Explicit finite structured upper-age limit: 456/1218
  (37.44%); unknown=38.
- Reconciled eligibility at age 85, YES: 858/1218
  (70.44%); unknown=27.
- Any of the eight primary geriatric domains PRESENT: 575/1218
  (47.21%); unknown=319.
- CoreVen all five domains covered by any planned outcome: 2/304
  (0.66%); unknown=61.
- OUTPUTs all six domains covered by any planned outcome: 0/184
  (0.00%); unknown=33.

These checkpoints are navigation aids to the populated tables, not final interpretation. CoreVen and
OUTPUTs use separate populations and are never combined into one score.

## Outputs

- 15 populated prespecified tables in `outputs/step_13_age_confirmed_20260730/tables/`
- 6 SVG figures with source-data CSV files in `outputs/step_13_age_confirmed_20260730/figures/`
- Long-format results, denominator audit, sensitivity results, minimized trial characteristics,
  and exact registered actual-age category rows in `outputs/step_13_age_confirmed_20260730/data/`
- Historical 1,206-record reliability summaries plus separately labeled new-record cross-scale workflow QC
- Five role-specific packages with all review, date, and signature fields blank

## Conditional modules and exceptions

The registered-results actual-age category module ran because explicit categorical distributions were
available. It preserves exact registered labels and never derives an older-age threshold from a mean.
The protocol/SAP prerequisite did not pass. Record History was not executed because no version-level
official history dataset was frozen; the guide is supporting audit only and non-analytic. The frozen master also does not
contain separate geriatric-context fields or a confirmed duplicate-cluster variable. These limitations
are preserved in `STEP13B_PRIMARY_ANALYSIS_EXCEPTIONS.csv`; no new coding was invented.

## Internal QA

All mandatory row-count, source-hash, unique-key, denominator, missing-state, contact-minimization,
framework-separation, and table/figure reconciliation checks passed. Independent clean-room validation
has not been performed. Final result interpretation, manuscript result finalization, and submission
preparation remain unauthorized.

## Hash-ledger convention

The payload ledger covers every payload file and the delivery bundle. A ledger cannot contain its own
stable digest; this self-exclusion is explicit and does not omit any analytic payload.
