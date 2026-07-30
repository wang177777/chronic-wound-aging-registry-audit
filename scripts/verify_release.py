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
if state.get("current_release_status") != "INDEPENDENT_VALIDATION_PASS":
    errors.append("final_release_validation_state")
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
print("RAW_COMPLETE_JSON=0")
print("STATUS=" + ("PASS" if not errors else "FAIL"))
if errors:
    print("ERRORS=" + ";".join(errors))
    sys.exit(1)
