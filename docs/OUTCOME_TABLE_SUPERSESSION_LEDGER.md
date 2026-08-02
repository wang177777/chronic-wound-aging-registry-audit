# Outcome-table supersession ledger

## Active publication layer

The human-reviewed outcome mappings in `data/minimized_derived/OUTCOME_LEVEL_FINAL_HUMAN_CONFIRMED_MINIMIZED.csv` are the authoritative source for publication-facing CoreVen and OUTPUTs domain counts. The aligned active tables are:

- `results/tables/T07_COREVEN_COVERAGE.csv`;
- `results/tables/T08_OUTPUTS_COVERAGE.csv`;
- `results/figures/F04_COREVEN_COVERAGE_DATA.csv`;
- `results/figures/F05_OUTPUTS_COVERAGE_DATA.csv`;
- `publication/Figure4_data.csv`;
- `publication/Supplementary_Table_S7.csv`;
- `publication/Supplementary_Table_S9.csv`.

## Historical layer

The v1.2.1 copies of T07, T08, F04 data and F05 data were produced before the later human outcome-mapping reconciliation. They are retained in `historical/v1.2.1_pre_outcome_mapping_reconciliation/` for audit only and are superseded for manuscript reporting. Other legacy Step13B long-format and denominator-audit files remain historical supporting evidence where they reproduce those pre-reconciliation rows; they are not the source for current CoreVen or OUTPUTs publication claims.

No historical file was overwritten in the original v1.2.1 release. The public v1.2.2 release is append-only relative to that release and records the aligned files explicitly.

## v1.2.3 supplementary-table alignment

The v1.2.2 public release retained an earlier two-row Supplementary Table S15 agreement audit while the current submission package used the governed four-row outcome-mapping disagreement-impact table. Version v1.2.3 aligns the public S15 file with the submission package. The v1.2.2 S15 is preserved under `historical/v1.2.2_pre_s15_publication_alignment/`; no v1.2.2 tag or asset was overwritten.
