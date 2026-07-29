from __future__ import annotations

import csv
import hashlib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/ANALYTICAL_INPUT_MANIFEST.csv"
ANALYSIS = ROOT / "analysis/STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_rows() -> list[dict[str, str]]:
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_explicit_analytical_input_manifest_has_frozen_scope() -> None:
    rows = manifest_rows()
    roles = Counter(row["Input_Role"] for row in rows)
    assert len(rows) == 1221
    assert roles == {
        "OFFICIAL_JSON_ANALYTICAL_INPUT": 1218,
        "LOCKED_STEP12_MASTER": 1,
        "FROZEN_SAP": 1,
        "FROZEN_SCREENING_FRAME": 1,
    }
    assert len({row["Input_ID"] for row in rows}) == 1221
    assert len({row["Relative_Path"] for row in rows}) == 1221


def test_public_release_does_not_publish_raw_complete_json() -> None:
    assert not list(ROOT.rglob("*.jsonl"))
    assert not list((ROOT / "data").rglob("*.json"))
    rows = manifest_rows()
    assert sum(row["Input_Role"] == "OFFICIAL_JSON_ANALYTICAL_INPUT" for row in rows) == 1218


def test_record_history_guide_is_quarantined_not_analytical() -> None:
    rows = manifest_rows()
    assert all(
        "record_history_guide.html" not in row["Relative_Path"].lower()
        for row in rows
    )
    assert not (
        ROOT
        / "data/raw/official_specs/clinicaltrials_gov/record_history_guide.html"
    ).exists()
    assert "SUPPORTING_AUDIT_ONLY_NON_ANALYTIC" in ANALYSIS.read_text(encoding="utf-8")


def test_analysis_has_no_raw_directory_or_substring_input_discovery() -> None:
    source = ANALYSIS.read_text(encoding="utf-8")
    forbidden = [
        '(project_root / "data/raw").rglob',
        "history_files =",
        "protocol_files =",
    ]
    assert all(token not in source for token in forbidden)
    assert "load_analytical_input_manifest" in source


def test_record_history_semantics_are_exactly_frozen() -> None:
    source = ANALYSIS.read_text(encoding="utf-8")
    for value in [
        "NOT_EXECUTED_CONDITIONAL_MODULE",
        "REMOVE_FROM_CURRENT_AIMS",
        "NO_VERSION_LEVEL_OFFICIAL_HISTORY_DATASET_FROZEN",
        "SUPPORTING_AUDIT_ONLY_NON_ANALYTIC",
        "Future_Amendment_Required",
    ]:
        assert value in source
