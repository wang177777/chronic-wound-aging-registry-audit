#!/usr/bin/env python3
"""Build the self-contained, deterministic R3D validation package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path

ZIP_TIMESTAMP = (2026, 7, 28, 12, 0, 0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def blank_form(role: str, person: str, held: bool = False) -> str:
    status = "HELD_PENDING_FRESH_R3_PASS" if held else "BLANK_PENDING_FRESH_R3_REVIEW"
    return "\n".join(
        [
            f"# {role} final-result review form",
            "",
            f"Assigned human reviewer: {person}",
            "",
            f"Current status: `{status}`",
            "",
            "This form may be completed only after the separately executed fresh R3 passes.",
            "",
            "- Human decision:",
            "- Human rationale:",
            "- Review date:",
            "- Typed-name signature:",
            "- Human-origin evidence reference:",
            "",
            "Automated or non-human completion of any field above is prohibited.",
            "",
        ]
    )


def deterministic_zip(
    destination: Path, members: dict[str, Path]
) -> tuple[int, str]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        destination,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
        strict_timestamps=True,
    ) as archive:
        for archive_name, source in sorted(members.items()):
            info = zipfile.ZipInfo(archive_name, ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("fresh R3 package CRC failure")
        member_count = len(archive.infolist())
    return member_count, sha256(destination)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--package-dir", required=True, type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    package_dir = args.package_dir.resolve()
    package_dir.mkdir(parents=True, exist_ok=True)

    forms = package_dir / "review_forms"
    forms.mkdir(parents=True, exist_ok=True)
    form_specs = [
        (
            "YU_LI_FINAL_RESULT_REVIEW_BLANK.md",
            "Independent statistical validation",
            "Yu Li / 李煜",
            False,
        ),
        (
            "JIYUE_JIANG_PROVENANCE_REVIEW_BLANK.md",
            "Source-lineage validation",
            "Jiyue Jiang / 姜继越",
            False,
        ),
        (
            "HUI_BI_GERIATRIC_REVIEW_BLANK.md",
            "Age and geriatric result validation",
            "Hui Bi / 毕慧",
            False,
        ),
        (
            "HAOJUN_LIANG_WOUND_OUTCOME_REVIEW_BLANK.md",
            "Wound and outcome result validation",
            "Haojun Liang / 梁浩君",
            False,
        ),
        (
            "GUOYONG_WANG_PI_FINAL_APPROVAL_HELD.md",
            "PI final result approval",
            "Guoyong Wang / 王国勇",
            True,
        ),
    ]
    for name, role, person, held in form_specs:
        (forms / name).write_text(
            blank_form(role, person, held),
            encoding="utf-8",
        )

    instructions = package_dir / "FRESH_R3D_CLEAN_WORKTREE_INSTRUCTIONS.md"
    instructions.write_text(
        """# Fresh R3D independent machine validation instructions

Status: `HELD_FOR_SEPARATE_NEXT_STEP`

1. Create a new detached worktree from the R3C internal-QA commit.
2. Before extraction, verify HEAD/tree equality, zero tracked modifications,
   zero untracked entries, no reused worktree, and zero output symlinks.
3. Extract this package outside both worktrees and verify its SHA-256 and
   `validation/STEP13D_R3D_PACKAGE_MEMBER_MANIFEST.csv`.
4. Use only the packaged analytical input manifest and its packaged inputs.
5. Independently execute the full R3D protocol. Do not import the primary
   generator or the R3C internal validator as an independent calculator.
6. Keep every human decision, rationale, date, signature, and human-origin
   evidence field blank/HELD until machine R3D passes.

Required machine scope remains: 20/20 frozen governance inputs, 1,218/1,218
official JSON files, 37/37 deterministic files, 597/597 denominator checks,
5/5 conclusion anchors, 3,051/3,051 numerical-register rows,
5,560/5,560 change-ledger rows, T01-T15, F01-F06, and 6/6 table/figure
reconciliation checks.

This package preparation does not execute independent R3D.
""",
        encoding="utf-8",
    )

    input_manifest = (
        root
        / "governance/analysis/step13d_v12r4_r3c/input_freeze/"
        "STEP13D_V12R4_R3C_ANALYTICAL_INPUT_MANIFEST.csv"
    )
    input_rows = read_csv(input_manifest)
    if len(input_rows) != 1221:
        raise RuntimeError("analytical input manifest does not contain 1221 rows")
    if any(
        "record_history_guide.html" in row["Relative_Path"].lower()
        for row in input_rows
    ):
        raise RuntimeError("Record History guide entered fresh R3 inputs")

    frozen_governance_paths = [
        "project_state.yaml",
        "pyproject.toml",
        "requirements.lock",
        "requirements-dev.lock",
        "analysis/step_13_corrected_1218/STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py",
        "scripts/step13d_v12r4_r3c/freeze_analytical_input_manifest.py",
        "scripts/step13d_v12r4_r3c/generate_r3c_trace_ledgers.py",
        "scripts/step13d_v12r4_r3c/validate_r3c_complete_rerun_internal.py",
        "scripts/step13d_v12r4_r3c/run_r3c_security_and_boundary_scan.py",
        "scripts/step13d_v12r4_r3c/build_fresh_r3_validation_package.py",
        "governance/analysis/step13d_v12r4_r3c/input_freeze/STEP13D_V12R4_R3C_ANALYTICAL_INPUT_MANIFEST.csv",
        "governance/analysis/step13d_v12r4_r3c/input_freeze/STEP13D_V12R4_R3C_ANALYTICAL_INPUT_MANIFEST_SUMMARY.json",
        "governance/analysis/step13d_v12r4_r3c/input_freeze/STEP13D_V12R4_R3C_RECORD_HISTORY_AND_INPUT_FREEZE.yaml",
        "governance/analysis/step13d_v12r4_r3c/input_freeze/STEP13D_V12R4_R3C_SUPPORTING_AUDIT_QUARANTINE_LEDGER.csv",
        "governance/analysis/step13d_v12r4_r3c/review_completion/RECORD_HISTORY_MODULE_SEMANTICS_HUMAN_EXPERT_PI_APPROVED_v1.2.yaml",
        "governance/analysis/step13d_v12r4_r3c/review_completion/SIGNOFF_STEP13D_V12R4_R3C_REMEDIATION_APPROVED_COMPLETE_RERUN_AUTHORIZED.md",
        "governance/analysis/step13d_v12r4_r3c/review_completion/STEP13D_V12R4_R3C_FINAL_HUMAN_FIELD_AND_GATE_QA.json",
        "governance/analysis/step13d_v12r4_r3c/review_completion/STEP13D_V12R4_R3C_IMPORT_VALIDATION_RECEIPT.json",
        "provenance/step_13/step13d_v12r4_r3c/source/package_contents/sources/STEP13_CORRECTED_1218_FINAL_MACHINE_VALIDATION_SUMMARY.json",
        "provenance/step_13/step13d_v12r4_r3c/source/package_contents/sources/STEP13_CORRECTED_1218_MACHINE_GATE_BLOCKER_REPORT.md",
    ]
    if len(frozen_governance_paths) != 20:
        raise RuntimeError("fresh R3 frozen governance scope must contain 20 files")
    frozen_governance_rows = []
    for relative in frozen_governance_paths:
        source = root / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        frozen_governance_rows.append(
            {
                "Relative_Path": relative,
                "Size_Bytes": source.stat().st_size,
                "SHA256": sha256(source),
                "Validation_Role": "FROZEN_GOVERNANCE_OR_EXECUTION_INPUT",
            }
        )
    frozen_governance_manifest = (
        package_dir
        / "STEP13D_R3D_FROZEN_GOVERNANCE_AND_EXECUTION_INPUT_MANIFEST.csv"
    )
    write_csv(frozen_governance_manifest, frozen_governance_rows)

    members: dict[str, Path] = {}
    for row in input_rows:
        source = root / row["Relative_Path"]
        if not source.is_file() or sha256(source) != row["SHA256"]:
            raise RuntimeError(f"analytical input binding: {row['Relative_Path']}")
        members[row["Relative_Path"]] = source

    output_root = root / "outputs/step_13_corrected_1218_r3c"
    report_root = root / "reports/step_13_corrected_1218_r3c"
    post_build_paths = {
        (
            report_root
            / "STEP13D_V12R4_R3C_COMPLETE_RERUN_MANIFEST.csv"
        ).resolve(),
        (
            report_root
            / "STEP13D_V12R4_R3C_COMPLETE_RERUN_SHA256.txt"
        ).resolve(),
        (
            report_root
            / "STEP13D_V12R4_R3C_FINAL_QA_AND_PACKAGE_RECEIPT.json"
        ).resolve(),
        (report_root / "execution/FRESH_R3_PACKAGE_ZIP_TEST.txt").resolve(),
        (report_root / "execution/FRESH_R3_PACKAGE_BUILD_STDOUT.txt").resolve(),
        (report_root / "execution/FRESH_R3_PACKAGE_BUILD_STDERR.txt").resolve(),
        (
            report_root / "execution/POSTPACKAGE_SECURITY_SCAN_STDOUT.txt"
        ).resolve(),
        (
            report_root / "execution/POSTPACKAGE_SECURITY_SCAN_STDERR.txt"
        ).resolve(),
    }
    for base in (output_root, report_root):
        for source in base.rglob("*"):
            if (
                source.is_file()
                and package_dir not in source.parents
                and source != package_dir
                and (report_root / "execution") not in source.parents
                and source.resolve() not in post_build_paths
            ):
                members[source.relative_to(root).as_posix()] = source

    historical_manifest = (
        root
        / "governance/analysis/step13d_v12r4_r2/input_freeze/"
        "STEP13_HISTORICAL_1206_OUTPUT_CLASSIFICATION_MANIFEST.csv"
    )
    historical_manifest_rows = read_csv(historical_manifest)
    historical_by_path = {
        row["Relative_Path"]: row for row in historical_manifest_rows
    }
    historical_trace_paths = [
        (
            root
            / "outputs/step_13/data/STEP13B_SENSITIVITY_RESULTS.csv"
        ).relative_to(root).as_posix(),
        *[
            path.relative_to(root).as_posix()
            for path in sorted((root / "outputs/step_13/tables").glob("T*.csv"))
        ],
        *[
            path.relative_to(root).as_posix()
            for path in sorted(
                (root / "outputs/step_13/figures").glob("F*_DATA.csv")
            )
        ],
    ]
    if len(historical_trace_paths) != 22:
        raise RuntimeError("historical trace source scope must contain 22 files")
    historical_trace_rows = []
    for relative in historical_trace_paths:
        source = root / relative
        expected = historical_by_path.get(relative)
        if expected is None:
            raise RuntimeError(f"historical manifest missing {relative}")
        if (
            not source.is_file()
            or source.stat().st_size != int(expected["Size_Bytes"])
            or sha256(source) != expected["SHA256"]
        ):
            raise RuntimeError(f"historical trace source binding: {relative}")
        members[relative] = source
        historical_trace_rows.append(
            {
                "Relative_Path": relative,
                "Size_Bytes": source.stat().st_size,
                "SHA256": sha256(source),
                "Validation_Role": "HISTORICAL_1206_CHANGE_LEDGER_SOURCE",
            }
        )
    historical_trace_manifest = (
        package_dir
        / "STEP13D_R3D_HISTORICAL_1206_TRACE_SOURCE_MANIFEST.csv"
    )
    write_csv(historical_trace_manifest, historical_trace_rows)
    members[historical_manifest.relative_to(root).as_posix()] = historical_manifest

    explicit_evidence = [
        "project_state.yaml",
        "pyproject.toml",
        "requirements.in",
        "requirements.lock",
        "requirements-dev.in",
        "requirements-dev.lock",
        "analysis/step_13_corrected_1218/STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py",
        "scripts/step13d_v12r4_r3c/freeze_analytical_input_manifest.py",
        "scripts/step13d_v12r4_r3c/generate_r3c_trace_ledgers.py",
        "scripts/step13d_v12r4_r3c/validate_r3c_complete_rerun_internal.py",
        "scripts/step13d_v12r4_r3c/run_r3c_security_and_boundary_scan.py",
        "scripts/step13d_v12r4_r3c/build_fresh_r3_validation_package.py",
        "tests/integration/test_step13d_v12r4_r3c_input_freeze.py",
        "governance/analysis/step13d_v12r4_r3c/input_freeze/STEP13D_V12R4_R3C_RECORD_HISTORY_AND_INPUT_FREEZE.yaml",
        "governance/analysis/step13d_v12r4_r3c/input_freeze/STEP13D_V12R4_R3C_SUPPORTING_AUDIT_QUARANTINE_LEDGER.csv",
        "governance/analysis/step13d_v12r4_r3c/review_completion/RECORD_HISTORY_MODULE_SEMANTICS_HUMAN_EXPERT_PI_APPROVED_v1.2.yaml",
        "governance/analysis/step13d_v12r4_r3c/review_completion/SIGNOFF_STEP13D_V12R4_R3C_REMEDIATION_APPROVED_COMPLETE_RERUN_AUTHORIZED.md",
        "governance/analysis/step13d_v12r4_r3c/review_completion/STEP13D_V12R4_R3C_FINAL_HUMAN_FIELD_AND_GATE_QA.json",
        "governance/analysis/step13d_v12r4_r3c/review_completion/STEP13D_V12R4_R3C_IMPORT_VALIDATION_RECEIPT.json",
        "provenance/step_13/step13d_v12r4_r3c/source/package_contents/sources/STEP13_CORRECTED_1218_FINAL_MACHINE_VALIDATION_SUMMARY.json",
        "provenance/step_13/step13d_v12r4_r3c/source/package_contents/sources/STEP13_CORRECTED_1218_MACHINE_GATE_BLOCKER_REPORT.md",
        "provenance/step_13/step13d_v12r4_r3c/source/package_contents/sources/STEP13_CORRECTED_1218_VALIDATION_DISCREPANCY_REGISTER.csv",
    ]
    for relative in explicit_evidence:
        source = root / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        members[relative] = source
    for source in sorted(
        (root / "human_review/step_13d_v12r4_r3c/final_returns").glob("*.xlsx")
    ):
        members[source.relative_to(root).as_posix()] = source
    for source in sorted(forms.glob("*.md")) + [instructions]:
        members[f"validation/{source.name}"] = source
    members[
        "validation/"
        "STEP13D_R3D_FROZEN_GOVERNANCE_AND_EXECUTION_INPUT_MANIFEST.csv"
    ] = frozen_governance_manifest
    members[
        "validation/STEP13D_R3D_HISTORICAL_1206_TRACE_SOURCE_MANIFEST.csv"
    ] = historical_trace_manifest

    member_rows = [
        {
            "Archive_Path": archive_name,
            "Size_Bytes": source.stat().st_size,
            "SHA256": sha256(source),
        }
        for archive_name, source in sorted(members.items())
    ]
    member_manifest = package_dir / "STEP13D_R3D_PACKAGE_MEMBER_MANIFEST.csv"
    write_csv(member_manifest, member_rows)
    members["validation/STEP13D_R3D_PACKAGE_MEMBER_MANIFEST.csv"] = member_manifest

    package = (
        package_dir
        / "Step13D_v12R4_R3D_Fresh_Independent_Machine_Validation_Package.zip"
    )
    member_count, package_hash = deterministic_zip(package, members)
    checksum = package_dir / "STEP13D_R3D_PACKAGE_SHA256.txt"
    checksum.write_text(
        f"{package_hash}  {package.name}\n",
        encoding="utf-8",
    )
    status = {
        "status": "READY_NOT_EXECUTED",
        "package": package.name,
        "package_size_bytes": package.stat().st_size,
        "package_sha256": package_hash,
        "package_members": member_count,
        "frozen_governance_and_execution_inputs": len(
            frozen_governance_rows
        ),
        "analytical_input_manifest_rows": len(input_rows),
        "official_json_inputs": sum(
            row["Input_Role"] == "OFFICIAL_JSON_ANALYTICAL_INPUT"
            for row in input_rows
        ),
        "historical_1206_trace_sources": len(historical_trace_rows),
        "record_history_guide_in_package": False,
        "blank_human_review_forms": 4,
        "held_pi_review_forms": 1,
        "fresh_r3_executed": False,
        "final_result_attestation_authorized": False,
        "manuscript_created": False,
        "submission_authorized": False,
    }
    (package_dir / "STEP13D_R3D_PACKAGE_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(status, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
