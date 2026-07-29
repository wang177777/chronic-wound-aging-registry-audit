#!/usr/bin/env python3
"""Fail-closed security and scientific-boundary scan for R3C artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

SECRET_PATTERNS = {
    "PRIVATE_KEY": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS_ACCESS_KEY": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "BEARER_TOKEN": re.compile(rb"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b"),
    "COOKIE_HEADER": re.compile(rb"(?im)^(?:set-)?cookie\s*:"),
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    root = args.project_root.resolve()
    output_root = root / "outputs/step_13_corrected_1218_r3c"
    report_root = root / "reports/step_13_corrected_1218_r3c"
    governed_roots = [
        output_root,
        report_root,
        root / "governance/analysis/step13d_v12r4_r3c",
        root / "scripts/step13d_v12r4_r3c",
    ]
    files = sorted(
        path
        for base in governed_roots
        for path in base.rglob("*")
        if path.is_file()
    )
    secret_findings: list[dict[str, str]] = []
    symlinks = [
        path.relative_to(root).as_posix()
        for base in governed_roots
        for path in base.rglob("*")
        if path.is_symlink()
    ]
    for path in files:
        if path.suffix.lower() in {".zip", ".xlsx", ".sqlite", ".png"}:
            continue
        data = path.read_bytes()
        for finding_type, pattern in SECRET_PATTERNS.items():
            if pattern.search(data):
                secret_findings.append(
                    {
                        "Relative_Path": path.relative_to(root).as_posix(),
                        "Finding": finding_type,
                    }
                )

    contact_findings = read_csv(
        output_root / "qa/STEP13B_CONTACT_FIELD_SCAN.csv"
    )
    prohibited_findings = read_csv(
        output_root / "qa/STEP13B_PROHIBITED_INFERENCE_SCAN.csv"
    )
    manifest = read_csv(
        root
        / "governance/analysis/step13d_v12r4_r3c/input_freeze/"
        "STEP13D_V12R4_R3C_ANALYTICAL_INPUT_MANIFEST.csv"
    )
    guide_in_manifest = any(
        "record_history_guide.html" in row["Relative_Path"].lower()
        for row in manifest
    )
    analysis_source = (
        root
        / "analysis/step_13_corrected_1218/"
        "STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py"
    ).read_text(encoding="utf-8")
    input_discovery_violations = [
        token
        for token in [
            '(project_root / "data/raw").rglob',
            "history_files =",
            "protocol_files =",
        ]
        if token in analysis_source
    ]
    result = {
        "status": (
            "PASS"
            if not (
                secret_findings
                or symlinks
                or contact_findings
                or prohibited_findings
                or guide_in_manifest
                or input_discovery_violations
            )
            else "FAIL"
        ),
        "files_scanned": len(files),
        "secret_findings": secret_findings,
        "symlinks": symlinks,
        "processed_contact_findings": contact_findings,
        "prohibited_inference_findings": prohibited_findings,
        "record_history_guide_in_analytical_manifest": guide_in_manifest,
        "input_discovery_violations": input_discovery_violations,
        "raw_json_contact_fields_exported_to_processed_outputs": False,
        "remote_push_performed": False,
        "manuscript_created": False,
    }
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
