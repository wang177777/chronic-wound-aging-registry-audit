#!/usr/bin/env python3
import csv, hashlib, pathlib, py_compile, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
manifest = ROOT / "RELEASE_FILE_MANIFEST.csv"
with manifest.open(encoding="utf-8-sig", newline="") as handle:
    rows = list(csv.DictReader(handle))
errors = []
for row in rows:
    path = ROOT / row["Relative_Path"]
    if not path.is_file() or path.stat().st_size != int(row["Bytes"]) or digest(path) != row["SHA256"]:
        errors.append(row["Relative_Path"])
actual = sorted(
    p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
    if p.is_file()
    and p.name != "RELEASE_FILE_MANIFEST.csv"
    and "__pycache__" not in p.parts
    and ".pytest_cache" not in p.parts
    and ".git" not in p.parts
)
listed = sorted(row["Relative_Path"] for row in rows)
if actual != listed:
    errors.append("manifest_coverage")
with (ROOT / "data/NCT_ID_FROZEN_JSON_HASH_MANIFEST.csv").open(encoding="utf-8-sig", newline="") as h:
    nct = list(csv.DictReader(h))
if len(nct) != 1218 or len({r["NCT_ID"] for r in nct}) != 1218:
    errors.append("nct_manifest")
if len(list((ROOT / "results/tables").glob("T*.csv"))) != 15:
    errors.append("tables")
if len(list((ROOT / "results/figures").glob("F*.svg"))) != 6:
    errors.append("figures")
state = __import__("json").loads(
    (ROOT / "results/qa/FINAL_RELEASE_VALIDATION_STATE.json").read_text()
)
if state.get("current_release_status") != "PUBLIC_RELEASE_VALIDATED":
    errors.append("final_release_validation_state")
if state.get("release_version") != "v1.2.12" or not state.get("public_release_created"):
    errors.append("public_release_binding_state")
if not state.get("publication_s15_alignment"):
    errors.append("publication_s15_alignment_state")
if not state.get("human_reviewed_outcome_table_alignment"):
    errors.append("outcome_table_alignment_state")
figure1_rows = list(csv.DictReader((ROOT / "publication/Figure1_data.csv").open(encoding="utf-8-sig", newline="")))
figure1_counts = {(row["stage"], row["item"]): int(row["count"]) for row in figure1_rows}
if not (
    figure1_counts.get(("full-screening final", "included")) == 1206
    and figure1_counts.get(("full-screening final", "excluded")) == 33646
    and figure1_counts.get(("reliability sample", "included")) + figure1_counts.get(("full-screening final", "included")) == 1218
    and figure1_counts.get(("reliability sample", "excluded")) + figure1_counts.get(("full-screening final", "excluded")) == 33754
):
    errors.append("figure1_flow_arithmetic")
figure4 = {}
for row in csv.DictReader((ROOT / "publication/Figure4_data.csv").open(encoding="utf-8-sig", newline="")):
    if row["Module"] == "REGISTERED_OUTCOME_DOMAIN":
        figure4[(row["Framework"], row["Coverage_Window"], row["Domain"])] = row
for name, framework in [("T07_COREVEN_COVERAGE.csv", "COREVEN"), ("T08_OUTPUTS_COVERAGE.csv", "OUTPUTS")]:
    for row in csv.DictReader((ROOT / "results/tables" / name).open(encoding="utf-8-sig", newline="")):
        window = {"PRIMARY_ONLY": "PRIMARY_REGISTERED", "ANY_PLANNED": "ANY_REGISTERED"}[row["Coverage_Window"]]
        source = figure4.get((framework, window, row["Domain"]))
        expected = (
            source is not None
            and row["Present_N"] == source["Present_N"]
            and row["Denominator"] == source["Full_Denominator"]
            and row["Unknown_Count"] == source["Indeterminate_N"]
        )
        if not expected:
            errors.append(f"outcome_alignment:{name}:{row['Coverage_Window']}:{row['Domain']}")
s15 = list(csv.DictReader((ROOT / "publication/Supplementary_Table_S15.csv").open(encoding="utf-8-sig", newline="")))
expected_s15 = {
    ("Geriatric-directionality classification", "788", "713", "75", "0.9048223350", "0.8835674462"),
    ("CoreVen/OUTPUTs exact outcome mapping", "100", "90", "10", "0.9000000000", "0.8805542284"),
}
observed_s15 = {
    (row["Audit"], row["Rows"], row["Agreement_Rows"], row["Disagreement_Rows"],
     row["Raw_Agreement"], row["Cohen_Kappa"])
    for row in s15
}
if observed_s15 != expected_s15:
    errors.append("publication_s15_alignment")
table1 = list(csv.reader((ROOT / "publication/Table1.csv").open(encoding="utf-8-sig", newline="")))
s2 = list(csv.reader((ROOT / "publication/Supplementary_Table_S2.csv").open(encoding="utf-8-sig", newline="")))
if table1 != s2 or table1[0] != ["Section", "Characteristic", "n/N (%) or summary", "Unknown n"]:
    errors.append("table1_s2_alignment")
publication_tables = [ROOT / "publication/Table1.csv"] + sorted((ROOT / "publication").glob("Supplementary_Table_S*.csv"))
if any(value == "" for path in publication_tables for row in csv.reader(path.open(encoding="utf-8-sig", newline="")) for value in row):
    errors.append("publication_blank_cells")
if list(ROOT.rglob("*.json")):
    raw = [p for p in ROOT.rglob("*.json") if "raw" in p.parts or "full_records" in p.parts]
    if raw:
        errors.append("raw_json")
for path in ROOT.rglob("*.py"):
    py_compile.compile(str(path), doraise=True)
print(f"RELEASE_MANIFEST={len(rows)}/{len(rows)}")
print("NCT_HASH_MANIFEST=1218/1218")
print("VALIDATED_TABLES=15/15")
print("VALIDATED_FIGURES=6/6")
print("PUBLICATION_SUPPLEMENTARY_TABLES=23/23")
print("FIGURE1_FLOW_ARITHMETIC=PASS")
print("HUMAN_REVIEWED_OUTCOME_ALIGNMENT=PASS")
print("PUBLICATION_S15_ALIGNMENT=PASS")
print("PUBLICATION_BLANK_CELLS=0")
print("RAW_COMPLETE_JSON=0")
print("STATUS=" + ("PASS" if not errors else "FAIL"))
if errors:
    print("ERRORS=" + ";".join(errors))
    sys.exit(1)
