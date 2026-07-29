#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"RELEASE_FILE_MANIFEST.csv"

def sha256(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):
            h.update(b)
    return h.hexdigest()

def main()->int:
    with MANIFEST.open("r",encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    failures=[]
    for row in rows:
        p=ROOT/row["Relative_Path"]
        if not p.is_file():
            failures.append("missing: "+row["Relative_Path"]);continue
        if p.stat().st_size!=int(row["Size_Bytes"]):
            failures.append("size: "+row["Relative_Path"])
        if sha256(p)!=row["SHA256"]:
            failures.append("sha256: "+row["Relative_Path"])
    if failures:
        print("\n".join(failures));return 1
    print(f"PASS: {len(rows)}/{len(rows)} release files verified")
    return 0
if __name__=="__main__":
    raise SystemExit(main())
