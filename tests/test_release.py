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

def test_figure1_flow_arithmetic():
    data = rows(ROOT / "publication/Figure1_data.csv")
    counts = {(row["stage"], row["item"]): int(row["count"]) for row in data}
    assert counts[("full-screening final", "included")] == 1206
    assert counts[("full-screening final", "excluded")] == 33646
    assert counts[("reliability sample", "included")] + counts[("full-screening final", "included")] == 1218
    assert counts[("reliability sample", "excluded")] + counts[("full-screening final", "excluded")] == 33754
def test_privacy_boundary():
    assert not list(ROOT.rglob("*__v1__lastupdate-*.json"))
    assert not list(ROOT.rglob("*.sqlite"))
def test_current_release_status():
    import json
    state = json.loads((ROOT / "results/qa/FINAL_RELEASE_VALIDATION_STATE.json").read_text())
    assert state["current_release_status"] == "PUBLIC_RELEASE_VALIDATED"
    assert state["release_version"] == "v1.2.12"
    assert state["independent_validation_completed"] is True
    assert state["human_reviewed_outcome_table_alignment"] is True
    assert state["public_release_created"] is True
    assert state["publication_s15_alignment"] is True

def test_publication_s15_alignment():
    data = rows(ROOT / "publication/Supplementary_Table_S15.csv")
    assert len(data) == 2
    assert {row["Audit"] for row in data} == {
        "Geriatric-directionality classification",
        "CoreVen/OUTPUTs exact outcome mapping",
    }
    assert {row["Raw_Agreement"] for row in data} == {"0.9048223350", "0.9000000000"}

def test_publication_tables_are_explicit_and_aligned():
    with (ROOT / "publication/Table1.csv").open(encoding="utf-8-sig", newline="") as handle:
        table1 = list(csv.reader(handle))
    with (ROOT / "publication/Supplementary_Table_S2.csv").open(encoding="utf-8-sig", newline="") as handle:
        s2 = list(csv.reader(handle))
    assert table1 == s2
    assert table1[0] == ["Section", "Characteristic", "n/N (%) or summary", "Unknown n"]
    publication_tables = [ROOT / "publication/Table1.csv"] + sorted((ROOT / "publication").glob("Supplementary_Table_S*.csv"))
    for path in publication_tables:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            assert all(value != "" for row in csv.reader(handle) for value in row)
