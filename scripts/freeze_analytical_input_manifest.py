#!/usr/bin/env python3
"""Freeze and verify the explicit analytical inputs for the R3C full rerun."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
from pathlib import Path

LOCKED_MASTER = (
    "data/locked/step_12/corrected_1218_final_detailed_coding/"
    "STEP12_CORRECTED_1218_DETAILED_CODING_MASTER.sqlite"
)
SAP = "protocols/07_REVISED_STATISTICAL_ANALYSIS_PLAN_v2.md"
SCREENING = (
    "screening/step_11/corrected_1218/"
    "STEP11_CORRECTED_SCREENING_MASTER_34972.csv"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()

    root = args.project_root.resolve()
    fixed = [
        (
            "INPUT0001",
            "LOCKED_STEP12_MASTER",
            LOCKED_MASTER,
            "Frozen corrected 1,218-record Step 12 detailed-coding master",
        ),
        (
            "INPUT0002",
            "FROZEN_SAP",
            SAP,
            "Frozen SAP v2.0 governing the corrected Step 13 rerun",
        ),
        (
            "INPUT0003",
            "FROZEN_SCREENING_FRAME",
            SCREENING,
            "Frozen 34,972-record screening frame used to identify 1,218 inclusions",
        ),
    ]
    rows: list[dict[str, str | int]] = []
    for input_id, role, relative, use in fixed:
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows.append(
            {
                "Input_ID": input_id,
                "Input_Role": role,
                "Relative_Path": relative,
                "Size_Bytes": path.stat().st_size,
                "SHA256": sha256(path),
                "Required": "YES",
                "Analytical_Use": use,
            }
        )

    master = root / LOCKED_MASTER
    with sqlite3.connect(f"file:{master}?mode=ro", uri=True) as connection:
        framework = connection.execute(
            "SELECT NCT_ID, Raw_JSON_Path, Raw_JSON_SHA256 "
            "FROM framework ORDER BY NCT_ID"
        ).fetchall()
    if len(framework) != 1218:
        raise RuntimeError(f"framework rows: {len(framework)}")
    if len({row[1] for row in framework}) != 1218:
        raise RuntimeError("raw JSON paths are not unique")

    for sequence, (nct_id, relative, expected_hash) in enumerate(framework, start=4):
        path = root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        observed_hash = sha256(path)
        if observed_hash != expected_hash:
            raise RuntimeError(f"raw JSON hash mismatch: {nct_id}")
        rows.append(
            {
                "Input_ID": f"INPUT{sequence:04d}",
                "Input_Role": "OFFICIAL_JSON_ANALYTICAL_INPUT",
                "Relative_Path": relative,
                "Size_Bytes": path.stat().st_size,
                "SHA256": observed_hash,
                "Required": "YES",
                "Analytical_Use": f"Frozen complete official JSON for {nct_id}",
            }
        )

    if len(rows) != 1221:
        raise RuntimeError(f"analytical input rows: {len(rows)}")
    if any("record_history_guide.html" in str(row["Relative_Path"]) for row in rows):
        raise RuntimeError("supporting Record History guide entered analytical manifest")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "Input_ID",
        "Input_Role",
        "Relative_Path",
        "Size_Bytes",
        "SHA256",
        "Required",
        "Analytical_Use",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "status": "PASS",
        "manifest_rows": len(rows),
        "locked_step12_master": 1,
        "frozen_sap": 1,
        "frozen_screening_frame": 1,
        "official_json_analytical_inputs": len(framework),
        "record_history_version_analytical_inputs": 0,
        "protocol_sap_conditional_inputs": 0,
        "record_history_guide_in_analytical_manifest": False,
        "manifest_sha256": sha256(output),
    }
    summary_path = args.summary.resolve()
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
