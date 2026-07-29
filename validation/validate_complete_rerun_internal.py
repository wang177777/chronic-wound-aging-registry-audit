#!/usr/bin/env python3
"""Internal QA for the R3C complete corrected 1,218-record Step 13 rerun."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

NUMERIC_RE = re.compile(r"^-?(?:\d+(?:\.\d+)?|\.\d+)(?:[eE][+-]?\d+)?$")
CROSS_SCALE_QC_LABEL = (
    "ACTUAL_HUMAN_CONFIRMED_CROSS_SCALE_WORKFLOW_QC_NOT_FORMAL_INDEPENDENT_REVIEWER_RELIABILITY"
)

ROW_KEYS = {
    "T01_FLOW_AND_INPUT_QA.csv": ["QA_Object"],
    "T02_AGE_ELIGIBILITY_THRESHOLDS.csv": [
        "Age_Scale",
        "Threshold_Years",
        "Category",
    ],
    "T03_AGE_NUMERIC_SUMMARY.csv": ["Field", "Unit"],
    "T04_AGE_FIELD_CONFLICT_AND_UPPER_LIMIT.csv": [
        "Age_Scale",
        "Threshold_Years",
        "Category",
    ],
    "T05_GERIATRIC_DOMAIN_CODES.csv": ["Domain_ID", "Category"],
    "T06_GERIATRIC_COMPOSITES.csv": ["Composite", "Category"],
    "T07_COREVEN_COVERAGE.csv": ["Framework", "Coverage_Window", "Domain"],
    "T08_OUTPUTS_COVERAGE.csv": ["Framework", "Coverage_Window", "Domain"],
    "T09_OUTCOME_COVERAGE_SCORES.csv": [
        "Framework",
        "Coverage_Window",
        "Metric",
        "Category",
    ],
    "T10_OUTCOME_CHARACTERISTICS.csv": [
        "Framework",
        "Coverage_Window",
        "Dimension",
        "Category",
    ],
    "T11_TRIAL_CHARACTERISTICS.csv": ["Population", "Dimension", "Category"],
    "T12_STRATIFIED_DESCRIPTIONS.csv": ["Stratum", "Metric"],
    "T13_ABSOLUTE_PERCENTAGE_POINT_DIFFERENCES.csv": [
        "Reference_Stratum",
        "Comparison_Stratum",
        "Metric",
    ],
    "T14_RELIABILITY_SUMMARY.csv": ["Module", "Field_or_Domain"],
    "T15_CONDITIONAL_MODULE_STATUS.csv": ["Conditional_Module"],
    "F01_AGE_ELIGIBILITY_LADDER_DATA.csv": [
        "Age_Scale",
        "Threshold_Years",
        "Category",
    ],
    "F02_AGE_FIELD_CONFLICT_DATA.csv": [
        "Age_Scale",
        "Threshold_Years",
        "Category",
    ],
    "F03_GERIATRIC_DOMAIN_MATRIX_DATA.csv": ["Domain_ID", "Category"],
    "F04_COREVEN_COVERAGE_DATA.csv": ["Framework", "Coverage_Window", "Domain"],
    "F05_OUTPUTS_COVERAGE_DATA.csv": ["Framework", "Coverage_Window", "Domain"],
    "F06_TEMPORAL_DESCRIPTIONS_DATA.csv": ["Stratum", "Metric"],
    "STEP13B_SENSITIVITY_RESULTS.csv": [
        "Sensitivity_ID",
        "Module",
        "Population",
        "Scenario",
        "Metric",
    ],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def is_numeric(value: str) -> bool:
    return bool(value and NUMERIC_RE.fullmatch(value.strip()))


def row_key(file_name: str, row: dict[str, str], row_number: int) -> str:
    keys = ROW_KEYS[file_name]
    return "|".join(f"{key}={row.get(key, '')}" for key in keys) or f"ROW={row_number}"


def boundary_for(file_name: str, row: dict[str, str], field: str) -> str:
    if file_name == "T14_RELIABILITY_SUMMARY.csv":
        if row.get("Module") == "WORKFLOW_QC":
            return CROSS_SCALE_QC_LABEL
        if row.get("Field_or_Domain") in {"Reporter", "Unit_of_Analysis"}:
            return "SUPPLEMENTARY_EXPLORATORY_ONLY_NOT_FOR_PRIMARY_CONCLUSIONS"
        return "HISTORICAL_1206_PAIRED_RELIABILITY_ONLY"
    if file_name in {"T07_COREVEN_COVERAGE.csv", "F04_COREVEN_COVERAGE_DATA.csv"}:
        return "COREVEN_ONLY_VLU_ACTIVE_TREATMENT_APPLICABLE_POPULATION"
    if file_name in {"T08_OUTPUTS_COVERAGE.csv", "F05_OUTPUTS_COVERAGE_DATA.csv"}:
        return "OUTPUTS_ONLY_PI_PREVENTION_APPLICABLE_POPULATION"
    if "AGE" in file_name:
        return "ELIGIBILITY_NOT_ACTUAL_OLDER_ADULT_ENROLLMENT_STRUCTURED_RECONCILED_SEPARATE"
    if file_name in {
        "T09_OUTCOME_COVERAGE_SCORES.csv",
        "T10_OUTCOME_CHARACTERISTICS.csv",
    }:
        return "PLANNED_OUTCOMES_NOT_REPORTED_CLINICAL_RESULTS"
    if field in {"Unknown_Count", "Category"}:
        return "UNKNOWN_UNCLEAR_NOT_PUBLICLY_SPECIFIED_NOT_APPLICABLE_REMAIN_DISTINCT"
    return "FINITE_POPULATION_DESCRIPTIVE_NO_CAUSAL_OR_INFERENTIAL_CLAIM"


def analytic_scope(root: Path) -> list[Path]:
    files = (
        list((root / "tables").glob("T*.csv"))
        + list((root / "figures").glob("F*_DATA.csv"))
        + list((root / "figures").glob("F*.svg"))
        + list((root / "data").glob("STEP13B_*.csv"))
        + list((root / "qa").glob("STEP13B_*.csv"))
        + list((root / "qa").glob("STEP13B_*.json"))
    )
    return sorted(path for path in files if path.is_file())


def source_files(output_root: Path) -> list[Path]:
    return sorted(
        list((output_root / "tables").glob("T*.csv"))
        + list((output_root / "figures").glob("F*_DATA.csv"))
        + [output_root / "data/STEP13B_SENSITIVITY_RESULTS.csv"]
    )


def build_numerical_register(output_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sequence = 0
    for path in source_files(output_root):
        source_rows = read_csv(path)
        digest = sha256(path)
        artifact_type = (
            "FIGURE_SOURCE"
            if path.parent.name == "figures"
            else ("TABLE" if path.parent.name == "tables" else "SENSITIVITY")
        )
        for row_number, row in enumerate(source_rows, start=2):
            key = row_key(path.name, row, row_number)
            for field, value in row.items():
                if not is_numeric(value):
                    continue
                sequence += 1
                numerator = row.get("Numerator") or row.get("Count") or row.get("Present_N", "")
                denominator = (
                    row.get("Denominator")
                    or row.get("Total_Denominator")
                    or row.get("Outcome_Row_Denominator", "")
                )
                percent = (
                    row.get("Percent")
                    or row.get("Percent_Total")
                    or row.get("Reference_Percent")
                    or row.get("Comparison_Percent", "")
                )
                rows.append(
                    {
                        "Register_ID": f"NRR{sequence:06d}",
                        "Artifact_Type": artifact_type,
                        "Source_File": path.relative_to(output_root.parent.parent).as_posix(),
                        "Source_Row_Number": row_number,
                        "Row_Key": key,
                        "Field": field,
                        "Value": value,
                        "Numerator_Context": numerator,
                        "Denominator_Context": denominator,
                        "Percent_Context": percent,
                        "Source_SHA256": digest,
                        "Interpretation_Boundary": boundary_for(path.name, row, field),
                    }
                )
    return rows


def indexed_rows(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    rows = read_csv(path)
    keys: dict[str, dict[str, str]] = {}
    for number, row in enumerate(rows, start=2):
        key = row_key(path.name, row, number)
        if key in keys:
            raise RuntimeError(f"duplicate row key in {path}: {key}")
        keys[key] = row
    fields = list(rows[0]) if rows else []
    return fields, keys


def build_change_ledger(historical_root: Path, corrected_root: Path) -> list[dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    corrected_files = source_files(corrected_root)
    for corrected in corrected_files:
        if corrected.parent.name == "tables":
            historical = historical_root / "tables" / corrected.name
        elif corrected.parent.name == "figures":
            historical = historical_root / "figures" / corrected.name
        else:
            historical = historical_root / "data" / corrected.name
        old_fields, old_rows = indexed_rows(historical)
        _, new_rows = indexed_rows(corrected)
        # Keep the frozen 5,560-cell historical comparison scope. The seven
        # R3C governance fields newly appended to T15 are tested separately.
        fields = old_fields
        for key in sorted(set(old_rows) | set(new_rows)):
            old = old_rows.get(key)
            new = new_rows.get(key)
            for field in fields:
                old_value = "" if old is None else old.get(field, "")
                new_value = "" if new is None else new.get(field, "")
                if old is None:
                    status = "ADDED_IN_1218"
                elif new is None:
                    status = "REMOVED_IN_1218"
                elif old_value == new_value:
                    status = "UNCHANGED"
                else:
                    status = "CHANGED"
                ledger.append(
                    {
                        "Artifact": corrected.name,
                        "Row_Key": key,
                        "Field": field,
                        "Historical_1206_Value": old_value,
                        "Corrected_1218_Value": new_value,
                        "Change_Status": status,
                        "Historical_Source_SHA256": sha256(historical),
                        "Corrected_Source_SHA256": sha256(corrected),
                        "Interpretation_Boundary": boundary_for(
                            corrected.name, new or old or {}, field
                        ),
                    }
                )
    return ledger


def find_row(path: Path, **criteria: str) -> dict[str, str]:
    matches = [
        row
        for row in read_csv(path)
        if all(row.get(field) == value for field, value in criteria.items())
    ]
    if len(matches) != 1:
        raise RuntimeError(f"anchor match {path.name} {criteria}: {len(matches)}")
    return matches[0]


def build_anchor_ledger(old_root: Path, new_root: Path) -> list[dict[str, Any]]:
    definitions = [
        (
            "FINITE_STRUCTURED_UPPER_LIMIT",
            "T02_AGE_ELIGIBILITY_THRESHOLDS.csv",
            {
                "Age_Scale": "STRUCTURED_UPPER_AGE_STATUS",
                "Category": "FINITE_UPPER_LIMIT",
            },
            "ELIGIBILITY_NOT_ACTUAL_ENROLLMENT",
        ),
        (
            "RECONCILED_ELIGIBLE_AT_85",
            "T02_AGE_ELIGIBILITY_THRESHOLDS.csv",
            {"Age_Scale": "RECONCILED", "Threshold_Years": "85", "Category": "YES"},
            "STRUCTURED_AND_RECONCILED_AGE_REMAIN_SEPARATE",
        ),
        (
            "ANY_PRIMARY_EIGHT_GERIATRIC_DOMAIN_PRESENT",
            "T06_GERIATRIC_COMPOSITES.csv",
            {"Composite": "PRIMARY_EIGHT_DOMAIN_ANY_PRESENT", "Category": "YES"},
            "REGISTRY_DOMAIN_NOT_DIAGNOSIS_OR_VALIDATED_FRAILTY_INDEX",
        ),
        (
            "COREVEN_ALL_DOMAINS_ANY_PLANNED",
            "T09_OUTCOME_COVERAGE_SCORES.csv",
            {
                "Framework": "COREVEN",
                "Coverage_Window": "ANY_PLANNED",
                "Metric": "ALL_DOMAINS_PRESENT",
                "Category": "YES",
            },
            "COREVEN_ONLY_VLU_ACTIVE_TREATMENT",
        ),
        (
            "OUTPUTS_ALL_DOMAINS_ANY_PLANNED",
            "T09_OUTCOME_COVERAGE_SCORES.csv",
            {
                "Framework": "OUTPUTS",
                "Coverage_Window": "ANY_PLANNED",
                "Metric": "ALL_DOMAINS_PRESENT",
                "Category": "YES",
            },
            "OUTPUTS_ONLY_PI_PREVENTION",
        ),
    ]
    rows: list[dict[str, Any]] = []
    for anchor, file_name, criteria, boundary in definitions:
        old_path = old_root / "tables" / file_name
        new_path = new_root / "tables" / file_name
        old = find_row(old_path, **criteria)
        new = find_row(new_path, **criteria)
        rows.append(
            {
                "Conclusion_Anchor": anchor,
                "Source_Table": file_name,
                "Criteria_JSON": json.dumps(criteria, ensure_ascii=False, sort_keys=True),
                "Historical_Numerator": old.get("Count", ""),
                "Historical_Denominator": old.get("Total_Denominator")
                or old.get("Denominator", ""),
                "Historical_Percent": old.get("Percent_Total") or old.get("Percent", ""),
                "Corrected_Numerator": new.get("Count", ""),
                "Corrected_Denominator": new.get("Total_Denominator") or new.get("Denominator", ""),
                "Corrected_Percent": new.get("Percent_Total") or new.get("Percent", ""),
                "Interpretation_Boundary": boundary,
                "Status": "TRACE_COMPLETE",
            }
        )
    return rows


def main(args: argparse.Namespace) -> int:
    root = args.project_root.resolve()
    corrected = args.output_root.resolve()
    historical = root / "outputs/step_13"
    recheck = args.recheck_output.resolve()
    reports = args.reports_root.resolve()
    qa = corrected / "qa"
    data = corrected / "data"

    numerical = build_numerical_register(corrected)
    register_path = data / "STEP13_CORRECTED_1218_NUMERICAL_RESULTS_REGISTER.csv"
    write_csv(
        register_path,
        numerical,
        [
            "Register_ID",
            "Artifact_Type",
            "Source_File",
            "Source_Row_Number",
            "Row_Key",
            "Field",
            "Value",
            "Numerator_Context",
            "Denominator_Context",
            "Percent_Context",
            "Source_SHA256",
            "Interpretation_Boundary",
        ],
    )
    ledger = build_change_ledger(historical, corrected)
    ledger_path = data / "STEP13_RESULT_CHANGE_LEDGER_1206_TO_1218.csv"
    write_csv(
        ledger_path,
        ledger,
        [
            "Artifact",
            "Row_Key",
            "Field",
            "Historical_1206_Value",
            "Corrected_1218_Value",
            "Change_Status",
            "Historical_Source_SHA256",
            "Corrected_Source_SHA256",
            "Interpretation_Boundary",
        ],
    )
    anchors = build_anchor_ledger(historical, corrected)
    anchor_path = data / "STEP13_CONCLUSION_ANCHOR_CHANGE_LEDGER_1206_TO_1218.csv"
    write_csv(anchor_path, anchors, list(anchors[0]))

    deterministic_rows: list[dict[str, Any]] = []
    final_files = analytic_scope(corrected)
    recheck_by_relative = {
        path.relative_to(recheck).as_posix(): path for path in analytic_scope(recheck)
    }
    for path in final_files:
        relative = path.relative_to(corrected).as_posix()
        other = recheck_by_relative.get(relative)
        status = other is not None and sha256(path) == sha256(other)
        deterministic_rows.append(
            {
                "Relative_Path": relative,
                "Primary_SHA256": sha256(path),
                "Recheck_SHA256": sha256(other) if other else "",
                "Status": "PASS" if status else "FAIL",
            }
        )
    deterministic_path = qa / "STEP13_CORRECTED_1218_DETERMINISTIC_RERUN.csv"
    write_csv(
        deterministic_path,
        deterministic_rows,
        ["Relative_Path", "Primary_SHA256", "Recheck_SHA256", "Status"],
    )

    denominator = read_csv(corrected / "data/STEP13B_DENOMINATOR_AUDIT.csv")
    figure = read_csv(corrected / "qa/STEP13B_TABLE_FIGURE_RECONCILIATION.csv")
    t14 = read_csv(corrected / "tables/T14_RELIABILITY_SUMMARY.csv")
    t02 = read_csv(corrected / "tables/T02_AGE_ELIGIBILITY_THRESHOLDS.csv")
    t05 = read_csv(corrected / "tables/T05_GERIATRIC_DOMAIN_CODES.csv")
    t07 = read_csv(corrected / "tables/T07_COREVEN_COVERAGE.csv")
    t08 = read_csv(corrected / "tables/T08_OUTPUTS_COVERAGE.csv")
    contact = read_csv(corrected / "qa/STEP13B_CONTACT_FIELD_SCAN.csv")
    prohibited = read_csv(corrected / "qa/STEP13B_PROHIBITED_INFERENCE_SCAN.csv")
    t15 = read_csv(corrected / "tables/T15_CONDITIONAL_MODULE_STATUS.csv")
    record_history = [row for row in t15 if row["Conditional_Module"] == "RECORD_HISTORY_AUDIT"]
    record_history_expected = {
        "Status": "NOT_EXECUTED_CONDITIONAL_MODULE",
        "Execution_Status": "NOT_EXECUTED_CONDITIONAL_MODULE",
        "Aims_Disposition": "REMOVE_FROM_CURRENT_AIMS",
        "Reason_Code": "NO_VERSION_LEVEL_OFFICIAL_HISTORY_DATASET_FROZEN",
        "Official_Version_Data_Coverage": "0/1218",
        "Guide_Document_Classification": "SUPPORTING_AUDIT_ONLY_NON_ANALYTIC",
        "Current_Analysis_Impact": "NONE",
        "Future_Amendment_Required": "YES",
    }
    manifest_path = (
        root / "governance/analysis/step13d_v12r4_r3c/input_freeze/"
        "STEP13D_V12R4_R3C_ANALYTICAL_INPUT_MANIFEST.csv"
    )
    manifest_rows = read_csv(manifest_path)
    manifest_hashes_ok = all(
        (root / row["Relative_Path"]).is_file()
        and (root / row["Relative_Path"]).stat().st_size == int(row["Size_Bytes"])
        and sha256(root / row["Relative_Path"]) == row["SHA256"]
        for row in manifest_rows
    )
    guide_in_manifest = any(
        "record_history_guide.html" in row["Relative_Path"].lower() for row in manifest_rows
    )
    analysis_source = (
        root / "analysis/step_13_corrected_1218/STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py"
    ).read_text(encoding="utf-8")
    forbidden_discovery_tokens = [
        '(project_root / "data/raw").rglob',
        "history_files =",
        "protocol_files =",
    ]
    qc_rows = [
        row
        for row in t14
        if row["Module"] == "WORKFLOW_QC"
        and row["Positive_Definition"] == CROSS_SCALE_QC_LABEL
        and row["Paired_N"] == "366"
        and row["Agreements"] == "309"
    ]
    low_reliability_ok = all(
        "SUPPLEMENTARY_EXPLORATORY_ONLY" in row["Weighting"]
        for row in t14
        if row["Field_or_Domain"] in {"Reporter", "Unit_of_Analysis"}
    )
    with sqlite3.connect(
        root / "data/locked/step_12/corrected_1218_final_detailed_coding/"
        "STEP12_CORRECTED_1218_DETAILED_CODING_MASTER.sqlite"
    ) as connection:
        duplicates = connection.execute(
            "select count(*) from ("
            "select Outcome_ID from outcome "
            "group by Outcome_ID having count(*)>1"
            ")"
        ).fetchone()[0]
        unresolved = connection.execute(
            "select value from qa_metadata where key='prohibited_unresolved_pi_final_values'"
        ).fetchone()[0]
    checks = [
        (
            "DENOMINATOR_AUDIT",
            bool(denominator) and all(r["Status"] == "PASS" for r in denominator),
        ),
        ("DENOMINATOR_AUDIT_ROWS", len(denominator) == 597),
        ("NUMERICAL_RESULTS_REGISTER", len(numerical) == 3051),
        (
            "NUMERICAL_REGISTER_RECONCILIATION",
            len(numerical)
            == sum(
                1
                for path in source_files(corrected)
                for row in read_csv(path)
                for value in row.values()
                if is_numeric(value)
            ),
        ),
        (
            "TABLE_FIGURE_SOURCE_RECONCILIATION",
            len(figure) == 6 and all(r["Status"] == "PASS" for r in figure),
        ),
        ("DUPLICATE_OUTCOME_IDS", duplicates == 0),
        ("PROHIBITED_UNRESOLVED_VALUES", str(unresolved) == "0"),
        (
            "STRUCTURED_RECONCILED_AGE_SEPARATE",
            {"STRUCTURED", "RECONCILED"} <= {r["Age_Scale"] for r in t02},
        ),
        (
            "COREVEN_OUTPUTS_SEPARATE",
            {r["Framework"] for r in t07} == {"COREVEN"}
            and {r["Framework"] for r in t08} == {"OUTPUTS"},
        ),
        (
            "MISSING_STATES_SEPARATE",
            "UNKNOWN" in {r["Category"] for r in t02}
            and "NOT_PUBLICLY_SPECIFIED" in {r["Category"] for r in t05},
        ),
        ("CONTACT_FIELD_SCAN", not contact),
        ("PROHIBITED_INFERENCE_SCAN", not prohibited),
        ("LOW_RELIABILITY_FIELDS_PRIMARY_USE", low_reliability_ok),
        ("CROSS_SCALE_QC_LABEL", len(qc_rows) == 1),
        (
            "CHANGE_LEDGER_COMPLETE",
            len(ledger) == 5560
            and all(
                r["Change_Status"] in {"UNCHANGED", "CHANGED", "ADDED_IN_1218", "REMOVED_IN_1218"}
                for r in ledger
            ),
        ),
        (
            "CONCLUSION_ANCHORS_TRACE_COMPLETE",
            len(anchors) == 5 and all(r["Status"] == "TRACE_COMPLETE" for r in anchors),
        ),
        (
            "DETERMINISTIC_RERUN",
            bool(deterministic_rows) and all(r["Status"] == "PASS" for r in deterministic_rows),
        ),
        (
            "T01_T15_COMPLETE",
            len(list((corrected / "tables").glob("T*.csv"))) == 15,
        ),
        (
            "F01_F06_COMPLETE",
            len(list((corrected / "figures").glob("F*.svg"))) == 6
            and len(list((corrected / "figures").glob("F*_DATA.csv"))) == 6,
        ),
        (
            "RECORD_HISTORY_APPROVED_SEMANTICS",
            len(record_history) == 1
            and all(
                record_history[0].get(field) == value
                for field, value in record_history_expected.items()
            ),
        ),
        (
            "EXPLICIT_ANALYTICAL_INPUT_MANIFEST",
            len(manifest_rows) == 1221
            and sum(row["Input_Role"] == "OFFICIAL_JSON_ANALYTICAL_INPUT" for row in manifest_rows)
            == 1218
            and manifest_hashes_ok,
        ),
        ("GUIDE_USED_AS_ANALYTICAL_INPUT", not guide_in_manifest),
        (
            "NO_BROAD_OR_SUBSTRING_INPUT_DISCOVERY",
            all(token not in analysis_source for token in forbidden_discovery_tokens),
        ),
    ]
    discrepancy_rows = [
        {
            "Discrepancy_ID": f"DISC{index:03d}",
            "Check": name,
            "Observed": "FAIL",
            "Expected": "PASS",
            "Status": "OPEN",
        }
        for index, (name, passed) in enumerate(checks, start=1)
        if not passed
    ]
    discrepancy_path = qa / "STEP13_CORRECTED_1218_INTERNAL_DISCREPANCY_REGISTER.csv"
    write_csv(
        discrepancy_path,
        discrepancy_rows,
        ["Discrepancy_ID", "Check", "Observed", "Expected", "Status"],
    )
    summary = {
        "status": "PASS" if not discrepancy_rows else "FAIL",
        "checks_total": len(checks),
        "checks_passed": sum(passed for _, passed in checks),
        "checks_failed": len(discrepancy_rows),
        "denominator_rows": len(denominator),
        "numerical_register_rows": len(numerical),
        "change_ledger_rows": len(ledger),
        "changed_cells": sum(r["Change_Status"] == "CHANGED" for r in ledger),
        "added_cells": sum(r["Change_Status"] == "ADDED_IN_1218" for r in ledger),
        "removed_cells": sum(r["Change_Status"] == "REMOVED_IN_1218" for r in ledger),
        "conclusion_anchors": len(anchors),
        "deterministic_files_compared": len(deterministic_rows),
        "deterministic_hash_mismatches": sum(r["Status"] != "PASS" for r in deterministic_rows),
        "cross_scale_qc_label": CROSS_SCALE_QC_LABEL,
        "independent_validation_executed": False,
        "record_history_execution_status": "NOT_EXECUTED_CONDITIONAL_MODULE",
        "guide_used_as_analytical_input": False,
        "partial_patch_performed": False,
        "manuscript_draft_created": False,
        "submission_authorized": False,
    }
    (qa / "STEP13_CORRECTED_1218_INTERNAL_QA_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = "\n".join(
        [
            "# R3C complete corrected 1,218-record Step 13 internal QA",
            "",
            f"Status: `{summary['status']}`",
            "",
            "This validation compares a complete second deterministic rerun "
            "with the primary corrected run.",
            "It does not perform the separately governed independent clean-room validation.",
            "",
            *[f"- {name}: {'PASS' if passed else 'FAIL'}" for name, passed in checks],
            "",
            f"- Numerical register rows: {len(numerical)}",
            f"- 1,206-to-1,218 cell-ledger rows: {len(ledger)}",
            f"- Deterministic files compared: {len(deterministic_rows)}",
            f"- Internal discrepancies: {len(discrepancy_rows)}",
            "",
        ]
    )
    (reports / "STEP13_CORRECTED_1218_INTERNAL_QA_REPORT.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if not discrepancy_rows else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--reports-root", required=True, type=Path)
    parser.add_argument("--recheck-output", required=True, type=Path)
    raise SystemExit(main(parser.parse_args()))
