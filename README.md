# Chronic wound aging registry audit

This data-minimized release accompanies the human-confirmed age-corrected analysis of 1,218 ClinicalTrials.gov records. It includes the locked analytical-input manifest, minimized derived layers, analysis and independent-validation code, validated T01–T15 tables, F01–F06 figure source data, and publication source tables. Complete registry JSON and contact fields are not redistributed.

A large-language-model-assisted computational workflow organized source-linked evidence and generated provisional full-screening classifications. Named investigators reviewed the frozen evidence and made or approved every final eligibility, coding, adjudication, analysis, interpretation and manuscript decision; the model was not a reviewer, expert or adjudicator. The complete age-corrected analysis was rerun in a fresh detached worktree; 36/36 deterministic scientific outputs, 596/596 denominator rows, 17/17 age checks and 7/7 conclusion anchors passed independent verification.

The frozen input manifest retains historical source filenames where needed for exact provenance. Those filenames do not indicate the current governance status of the human-confirmed values.

Repository: https://github.com/wang177777/chronic-wound-aging-registry-audit
Release: https://github.com/wang177777/chronic-wound-aging-registry-audit/releases/tag/v1.2.2
Version: v1.2.2

## v1.2.2 outcome-mapping alignment

The human-reviewed outcome mappings already distributed in the minimized outcome file and publication tables are now also reflected in `results/tables/T07_COREVEN_COVERAGE.csv` and `results/tables/T08_OUTPUTS_COVERAGE.csv`. Version v1.2.1 is preserved as historical release evidence and is not overwritten.
