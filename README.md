# Chronic-wound aging registry audit

Reproducibility release for **Age accessibility, geriatric-context specification, and planned outcome coverage in registered chronic-wound trials**.

## Validated scope

- 1,218 adjudicated ClinicalTrials.gov interventional-study records
- 37/37 deterministic result files independently reproduced
- 3,051/3,051 numerical-register bindings
- 5,560/5,560 change-ledger validations
- 277/277 manuscript numeric occurrences source-bound
- 54/54 manuscript claims source-bound

## Repository layout

- `analysis/`: corrected primary analysis
- `validation/`: internal and fresh independent validation
- `tests/`: audited tests
- `environment/`: locked requirements
- `manifests/`: explicit frozen analytical inputs
- `data/`: NCT identifiers and frozen JSON hashes
- `results/`: validated tables, figures and ledgers
- `manuscript/`: manuscript and declarations

## Verify the release

```bash
python scripts/verify_release.py
bash scripts/verify_release.sh
```

Version `v1.0.1` is available from the
[GitHub release](https://github.com/wang177777/chronic-wound-aging-registry-audit/releases/tag/v1.0.1).
The release asset `chronic-wound-aging-registry-audit-code-v1.0.1.zip` has
SHA-256 `7070dd149bbd99e36f2b07440fea54ef54b158584ea77b7bdc1913c79449c2c0`.

## Full rerun

The primary analysis is fail-closed. Supply the exact inputs and hashes in `manifests/ANALYTICAL_INPUT_MANIFEST.csv`, then inspect:

```bash
python analysis/STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py --help
```

The Git repository is data-minimized; complete frozen registry JSON is not redistributed in Git. Validated derived outputs and the NCT/hash manifest are included.

## License

Code: MIT. Documentation and derived tables: CC BY 4.0, subject to attribution of the underlying ClinicalTrials.gov source.
