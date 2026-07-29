#!/usr/bin/env python3
"""Generate complete R3C numerical, change, anchor, and file ledgers."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_trace_module(root: Path) -> ModuleType:
    path = (
        root
        / "scripts/step13d_v12r4_r2/"
        "validate_corrected_step13_internal.py"
    )
    spec = importlib.util.spec_from_file_location("step13_trace", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load trace module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_change_ledger(
    trace: ModuleType, historical_root: Path, corrected_root: Path
) -> list[dict[str, Any]]:
    """Retain the frozen 5,560-cell comparison scope.

    Seven new R3C governance fields in T15 are validated separately and are not
    retroactively added to the prespecified 1,206-to-1,218 cell comparison.
    """
    ledger: list[dict[str, Any]] = []
    for corrected in trace.source_files(corrected_root):
        if corrected.parent.name == "tables":
            historical = historical_root / "tables" / corrected.name
        elif corrected.parent.name == "figures":
            historical = historical_root / "figures" / corrected.name
        else:
            historical = historical_root / "data" / corrected.name
        old_fields, old_rows = trace.indexed_rows(historical)
        _, new_rows = trace.indexed_rows(corrected)
        for key in sorted(set(old_rows) | set(new_rows)):
            old = old_rows.get(key)
            new = new_rows.get(key)
            for field in old_fields:
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
                        "Interpretation_Boundary": trace.boundary_for(
                            corrected.name, new or old or {}, field
                        ),
                    }
                )
    return ledger


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--reports-root", required=True, type=Path)
    args = parser.parse_args()

    root = args.project_root.resolve()
    output = args.output_root.resolve()
    reports = args.reports_root.resolve()
    historical = root / "outputs/step_13"
    data = output / "data"
    trace = load_trace_module(root)

    numerical = trace.build_numerical_register(output)
    if len(numerical) != 3051:
        raise RuntimeError(f"numerical register rows: {len(numerical)}")
    trace.write_csv(
        data / "STEP13_CORRECTED_1218_NUMERICAL_RESULTS_REGISTER.csv",
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

    ledger = build_change_ledger(trace, historical, output)
    if len(ledger) != 5560:
        raise RuntimeError(f"change ledger rows: {len(ledger)}")
    trace.write_csv(
        data / "STEP13_RESULT_CHANGE_LEDGER_1206_TO_1218.csv",
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

    anchors = trace.build_anchor_ledger(historical, output)
    if len(anchors) != 5:
        raise RuntimeError(f"conclusion anchors: {len(anchors)}")
    trace.write_csv(
        data / "STEP13_CONCLUSION_ANCHOR_CHANGE_LEDGER_1206_TO_1218.csv",
        anchors,
        list(anchors[0]),
    )

    summary = {
        "status": "PASS",
        "numerical_register_rows": len(numerical),
        "change_ledger_rows": len(ledger),
        "conclusion_anchors": len(anchors),
        "t15_governance_only_fields_excluded_from_frozen_change_scope": [
            "Execution_Status",
            "Aims_Disposition",
            "Reason_Code",
            "Official_Version_Data_Coverage",
            "Guide_Document_Classification",
            "Current_Analysis_Impact",
            "Future_Amendment_Required",
        ],
        "partial_patch_performed": False,
        "complete_primary_rerun": True,
    }
    summary_path = data / "STEP13D_V12R4_R3C_TRACE_GENERATION_SUMMARY.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    excluded = {
        "STEP13D_V12R4_R3C_COMPLETE_RERUN_MANIFEST.csv",
        "STEP13D_V12R4_R3C_COMPLETE_RERUN_SHA256.txt",
    }
    files = sorted(
        [
            path
            for base in (output, reports)
            for path in base.rglob("*")
            if path.is_file() and path.name not in excluded
        ]
        + [
            root / "project_state.yaml",
            root
            / "analysis/step_13_corrected_1218/"
            "STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py",
            root
            / "scripts/step13d_v12r4_r3c/"
            "freeze_analytical_input_manifest.py",
            root
            / "scripts/step13d_v12r4_r3c/"
            "generate_r3c_trace_ledgers.py",
            root
            / "governance/analysis/step13d_v12r4_r3c/input_freeze/"
            "STEP13D_V12R4_R3C_ANALYTICAL_INPUT_MANIFEST.csv",
            root
            / "governance/analysis/step13d_v12r4_r3c/input_freeze/"
            "STEP13D_V12R4_R3C_RECORD_HISTORY_AND_INPUT_FREEZE.yaml",
            root
            / "tests/integration/"
            "test_step13d_v12r4_r3c_input_freeze.py",
        ]
    )
    manifest_rows = [
        {
            "Relative_Path": path.relative_to(root).as_posix(),
            "Size_Bytes": path.stat().st_size,
            "SHA256": sha256(path),
        }
        for path in files
    ]
    manifest = reports / "STEP13D_V12R4_R3C_COMPLETE_RERUN_MANIFEST.csv"
    trace.write_csv(
        manifest,
        manifest_rows,
        ["Relative_Path", "Size_Bytes", "SHA256"],
    )
    checksum = reports / "STEP13D_V12R4_R3C_COMPLETE_RERUN_SHA256.txt"
    checksum.write_text(
        "".join(
            f"{row['SHA256']}  {row['Relative_Path']}\n"
            for row in manifest_rows
        )
        + f"{sha256(manifest)}  {manifest.relative_to(root).as_posix()}\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
