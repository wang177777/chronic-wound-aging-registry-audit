#!/usr/bin/env python3
"""Unit tests for the standalone R3D-R1 validator."""

from __future__ import annotations

import ast
import argparse
import hashlib
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "validation/independent_validate.py"
SPEC = importlib.util.spec_from_file_location("r3d_r1_validator", TARGET)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_percentage() -> None:
    assert MODULE.pct(1097, 1218) == "90.065681"
    assert MODULE.pct(0, 0) == ""


def test_number_equal() -> None:
    assert MODULE.number_equal("90.065681", "90.0656814")
    assert not MODULE.number_equal("", "0")
    assert not MODULE.number_equal("A", "B")


def test_row_key() -> None:
    parsed = MODULE.parse_row_key("A=one|B=two=three")
    assert parsed == {"A": "one", "B": "two=three"}
    rows = [{"A": "one", "B": "two=three"}, {"A": "other", "B": "x"}]
    assert MODULE.locate_row(rows, parsed) == rows[0]


def test_deterministic_scope() -> None:
    paths = MODULE.exact_deterministic_paths()
    assert len(paths) == 37
    assert len(set(paths)) == 37


def test_forbidden_dependencies() -> None:
    tree = ast.parse(TARGET.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    assert "subprocess" not in imports
    assert not any(name.startswith("analysis.") for name in imports)
    source = TARGET.read_text(encoding="utf-8")
    assert ".rglob(" not in source
    assert ".glob(" not in source
    assert "os.walk(" not in source


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence")
    args = parser.parse_args()
    tests = [
        test_percentage,
        test_number_equal,
        test_row_key,
        test_deterministic_scope,
        test_forbidden_dependencies,
    ]
    for test in tests:
        test()
    print(f"{len(tests)}/{len(tests)} tests passed")
    if args.evidence:
        evidence = {
            "completed_utc": datetime.now(timezone.utc).isoformat(),
            "tests_total": len(tests),
            "tests_passed": len(tests),
            "tests_failed": 0,
            "validator_sha256": hashlib.sha256(TARGET.read_bytes()).hexdigest(),
            "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
        Path(args.evidence).write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
