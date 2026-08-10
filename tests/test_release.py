import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))
def test_nct_manifest():
    data = rows(ROOT / "data/NCT_ID_FROZEN_JSON_HASH_MANIFEST.csv")
    assert len(data) == 1218
    assert len({r["NCT_ID"] for r in data}) == 1218
def test_scientific_outputs():
    assert len(list((ROOT / "results/tables").glob("T*.csv"))) == 15
    assert len(list((ROOT / "results/figures").glob("F*.svg"))) == 6
def test_publication_outputs():
    assert (ROOT / "publication/Table1.csv").is_file()
    assert len(list((ROOT / "publication").glob("Supplementary_Table_S*.csv"))) == 23
def test_privacy_boundary():
    assert not list(ROOT.rglob("*__v1__lastupdate-*.json"))
    assert not list(ROOT.rglob("*.sqlite"))
def test_current_release_status():
    import json
    state = json.loads((ROOT / "results/qa/FINAL_RELEASE_VALIDATION_STATE.json").read_text())
    assert state["current_release_status"] == "PUBLIC_RELEASE_VALIDATED"
    assert state["release_version"] == "v1.2.5"
    assert state["independent_validation_completed"] is True
    assert state["human_reviewed_outcome_table_alignment"] is True
    assert state["public_release_created"] is True
    assert state["publication_s15_alignment"] is True

def test_publication_s15_alignment():
    data = rows(ROOT / "publication/Supplementary_Table_S15.csv")
    assert len(data) == 4
    assert {row["Framework"] for row in data} == {"COREVEN", "OUTPUTS"}
