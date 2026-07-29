#!/usr/bin/env python3
# ruff: noqa: E501
"""Corrected-cohort Step 13 prespecified finite-population analysis.

This implementation preserves the scientific functions and thresholds of the
frozen Step 13B implementation while reading the corrected 1,218-record Step 12
master. It is a full rerun, not a 12-record patch. Historical 1,206-record
outputs are never opened for writing.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import re
import sqlite3
import statistics
import sys
import zipfile
from collections import Counter, defaultdict
from collections.abc import Iterable, Sequence
from datetime import date
from pathlib import Path
from typing import Any

EXECUTION_DATE = "2026-07-28"
EXECUTION_TIMESTAMP_UTC = "2026-07-28T12:00:00Z"
EXPECTED = {
    "included_nct": 1218,
    "json_coverage": 1218,
    "trial_age": 18270,
    "geriatric_domains": 10962,
    "frameworks": 1218,
    "outcomes": 7633,
    "unresolved": 0,
}
EXPECTED_HASHES = {
    "locked_master": "a4a8a29ed3804a5f42559ee93c348a7111cfe8ead44bd1a072ae6723aced6345",
    "sap": "db5b8220e29e336815f1b74b4414b12e849b54c0378be1683a80fabac11cb497",
}
EXPECTED_ANALYTICAL_INPUT_ROWS = 1221
RECORD_HISTORY_EXECUTION_STATUS = "NOT_EXECUTED_CONDITIONAL_MODULE"
RECORD_HISTORY_AIMS_DISPOSITION = "REMOVE_FROM_CURRENT_AIMS"
RECORD_HISTORY_REASON_CODE = "NO_VERSION_LEVEL_OFFICIAL_HISTORY_DATASET_FROZEN"
RECORD_HISTORY_GUIDE_CLASSIFICATION = "SUPPORTING_AUDIT_ONLY_NON_ANALYTIC"
NEW_RECORD_DELTA_TYPE = "NEW_CORRECTED_COHORT_RECORD_HUMAN_CONFIRMED"
CROSS_SCALE_QC_LABEL = (
    "ACTUAL_HUMAN_CONFIRMED_CROSS_SCALE_WORKFLOW_QC_"
    "NOT_FORMAL_INDEPENDENT_REVIEWER_RELIABILITY"
)
COREVEN_DOMAINS = [
    "healing",
    "pain",
    "quality_of_life",
    "resource_use",
    "adverse_events",
]
OUTPUTS_DOMAINS = [
    "pressure_injury_occurrence",
    "precursor_signs_symptoms",
    "mobility",
    "acceptability_comfort",
    "adherence_compliance",
    "adverse_events_safety",
]
GERIATRIC_DOMAINS = [
    "frailty_direct",
    "mobility_adl_function",
    "cognition_decision_capacity",
    "proxy_consent_pathway",
    "nutrition_malnutrition",
    "multimorbidity_burden",
    "life_expectancy_advanced_illness",
    "care_setting_caregiver",
    "polypharmacy_medication_burden",
]
SEPARATE_MISSING_STATES = {
    "",
    "MISSING",
    "UNKNOWN",
    "NOT_APPLICABLE",
    "NOT_PUBLICLY_SPECIFIED",
    "UNPARSEABLE",
    "REQUIRES_EXPERT_DECISION",
}
CONTACT_KEY_RE = re.compile(
    r"(contact|email|phone|fax|investigator|facility|person_name|official_name|official_title)",
    re.IGNORECASE,
)
PROHIBITED_OUTPUT_PATTERNS = [
    re.compile(r"\bp[\s_-]*value\b", re.IGNORECASE),
    re.compile(r"\bconfidence" + r" interval\b", re.IGNORECASE),
    re.compile(r"\bfalse discovery" + r" rate\b", re.IGNORECASE),
    re.compile(r"\bcausal" + r" effect\b", re.IGNORECASE),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_analytical_input_manifest(
    project_root: Path, manifest_path: Path
) -> dict[str, list[dict[str, str]]]:
    """Verify every explicitly authorized input without discovering new inputs."""
    rows = read_csv(manifest_path)
    required_fields = {
        "Input_ID",
        "Input_Role",
        "Relative_Path",
        "Size_Bytes",
        "SHA256",
        "Required",
        "Analytical_Use",
    }
    if len(rows) != EXPECTED_ANALYTICAL_INPUT_ROWS:
        raise RuntimeError(f"analytical input manifest rows: {len(rows)}")
    if not rows or not required_fields <= set(rows[0]):
        raise RuntimeError("analytical input manifest schema")
    if len({row["Input_ID"] for row in rows}) != len(rows):
        raise RuntimeError("analytical input IDs are not unique")
    if len({row["Relative_Path"] for row in rows}) != len(rows):
        raise RuntimeError("analytical input paths are not unique")

    by_role: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        relative = Path(row["Relative_Path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise RuntimeError(f"unsafe analytical input path: {relative}")
        path = project_root / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        if path.stat().st_size != int(row["Size_Bytes"]):
            raise RuntimeError(f"analytical input size mismatch: {relative}")
        if sha256(path) != row["SHA256"]:
            raise RuntimeError(f"analytical input hash mismatch: {relative}")
        by_role[row["Input_Role"]].append(row)

    expected_singletons = {
        "LOCKED_STEP12_MASTER",
        "FROZEN_SAP",
        "FROZEN_SCREENING_FRAME",
    }
    for role in expected_singletons:
        if len(by_role.get(role, [])) != 1:
            raise RuntimeError(f"analytical input singleton role: {role}")
    if len(by_role.get("OFFICIAL_JSON_ANALYTICAL_INPUT", [])) != 1218:
        raise RuntimeError("official JSON analytical inputs are not 1218")
    if by_role.get("RECORD_HISTORY_VERSION_ANALYTICAL_INPUT"):
        raise RuntimeError("Record History version input is not authorized")
    if any(
        "record_history_guide.html" in row["Relative_Path"].lower() for row in rows
    ):
        raise RuntimeError("supporting Record History guide is not analytical input")
    return by_role


def write_csv(path: Path, rows: Sequence[dict[str, Any]], fields: Sequence[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=list(fields),
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_table(connection: sqlite3.Connection, name: str) -> list[dict[str, str]]:
    connection.row_factory = sqlite3.Row
    return [dict(row) for row in connection.execute(f'SELECT * FROM "{name}"')]


def parse_json_object(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def final_age_value(row: dict[str, str]) -> str:
    """Return the frozen human/PI-confirmed age disposition."""
    return (row.get("Expert_Proposed_Disposition") or "").strip()


def safe_float(value: str | None) -> float | None:
    if value is None or not str(value).strip():
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return number if math.isfinite(number) else None


def pct(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) * 100.0 / float(denominator), 6)


def fmt_number(value: float | None) -> str:
    if value is None:
        return ""
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def percentile_linear(values: Sequence[float], probability: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def descriptive_numeric(values: Sequence[float]) -> dict[str, Any]:
    values = [v for v in values if math.isfinite(v)]
    return {
        "n": len(values),
        "median": statistics.median(values) if values else None,
        "q1": percentile_linear(values, 0.25),
        "q3": percentile_linear(values, 0.75),
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
    }


def agreement_metrics(
    values_a: Sequence[str],
    values_b: Sequence[str],
    positive_values: set[str] | None = None,
) -> dict[str, Any]:
    if len(values_a) != len(values_b):
        raise ValueError("Paired agreement inputs have different lengths")
    n = len(values_a)
    if not n:
        return {
            "n": 0,
            "agreements": 0,
            "raw_agreement": None,
            "positive_agreement": None,
            "negative_agreement": None,
            "cohen_kappa": None,
            "gwet_ac1": None,
            "gwet_ac2": None,
        }
    values_a = [str(v) for v in values_a]
    values_b = [str(v) for v in values_b]
    agreements = sum(a == b for a, b in zip(values_a, values_b, strict=True))
    observed = agreements / n
    categories = sorted(set(values_a) | set(values_b))
    counts_a = Counter(values_a)
    counts_b = Counter(values_b)
    chance_kappa = sum((counts_a[c] / n) * (counts_b[c] / n) for c in categories)
    kappa = (observed - chance_kappa) / (1 - chance_kappa) if chance_kappa < 1 else None
    if len(categories) > 1:
        pooled = {c: (counts_a[c] + counts_b[c]) / (2 * n) for c in categories}
        chance_ac1 = sum(p * (1 - p) for p in pooled.values()) / (len(categories) - 1)
        ac1 = (observed - chance_ac1) / (1 - chance_ac1) if chance_ac1 < 1 else None
    else:
        ac1 = 1.0
    positive_agreement = None
    negative_agreement = None
    if positive_values is not None:
        a_pos = [value in positive_values for value in values_a]
        b_pos = [value in positive_values for value in values_b]
        both_pos = sum(a and b for a, b in zip(a_pos, b_pos, strict=True))
        both_neg = sum((not a) and (not b) for a, b in zip(a_pos, b_pos, strict=True))
        discordant = sum(a != b for a, b in zip(a_pos, b_pos, strict=True))
        positive_denominator = 2 * both_pos + discordant
        negative_denominator = 2 * both_neg + discordant
        positive_agreement = (
            2 * both_pos / positive_denominator if positive_denominator else None
        )
        negative_agreement = (
            2 * both_neg / negative_denominator if negative_denominator else None
        )
    return {
        "n": n,
        "agreements": agreements,
        "raw_agreement": observed,
        "positive_agreement": positive_agreement,
        "negative_agreement": negative_agreement,
        "cohen_kappa": kappa,
        "gwet_ac1": ac1,
        "gwet_ac2": ac1,
    }


def parse_registry_date(value: str | None) -> date | None:
    if not value:
        return None
    match = re.match(r"^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", value)
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2) or 1)
    day = int(match.group(3) or 1)
    try:
        return date(year, month, day)
    except ValueError:
        return None


def period_for_year(year: int | None) -> str:
    if year is None:
        return "UNKNOWN"
    if 2000 <= year <= 2007:
        return "2000-2007_HISTORICAL_APPENDIX"
    if 2008 <= year <= 2016:
        return "2008-2016"
    if 2017 <= year <= 2018:
        return "2017-2018"
    if 2019 <= year <= 2025:
        return "2019-2025"
    return "OUTSIDE_PRESPECIFIED_PERIODS"


def get_nested(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    current: Any = mapping
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def extract_trial_metadata(nct_id: str, document: dict[str, Any]) -> dict[str, Any]:
    protocol = document.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    design_info = design.get("designInfo", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    arms = protocol.get("armsInterventionsModule", {})
    eligibility = protocol.get("eligibilityModule", {})
    locations = get_nested(protocol, "contactsLocationsModule", "locations", default=[]) or []
    first_post_raw = get_nested(status, "studyFirstPostDateStruct", "date")
    first_submit_raw = status.get("studyFirstSubmitDate")
    start_raw = get_nested(status, "startDateStruct", "date")
    first_post = parse_registry_date(first_post_raw)
    first_submit = parse_registry_date(first_submit_raw)
    start = parse_registry_date(start_raw)
    allocation = str(design_info.get("allocation") or "UNKNOWN")
    intervention_model = str(design_info.get("interventionModel") or "UNKNOWN")
    interventions = arms.get("interventions", []) or []
    intervention_types = sorted(
        {str(item.get("type") or "UNKNOWN") for item in interventions if isinstance(item, dict)}
    )
    lead_class = str(get_nested(sponsor, "leadSponsor", "class", default="UNKNOWN"))
    collaborator_classes = {
        str(item.get("class") or "UNKNOWN")
        for item in (sponsor.get("collaborators", []) or [])
        if isinstance(item, dict)
    }
    if lead_class == "INDUSTRY":
        industry_role = "INDUSTRY_LEAD"
    elif "INDUSTRY" in collaborator_classes:
        industry_role = "INDUSTRY_COLLABORATOR"
    elif lead_class == "UNKNOWN" and not collaborator_classes:
        industry_role = "UNKNOWN"
    else:
        industry_role = "NO_RECORDED_INDUSTRY_ROLE"
    countries = sorted(
        {
            str(location.get("country"))
            for location in locations
            if isinstance(location, dict) and location.get("country")
        }
    )
    if len(countries) > 1:
        country_scope = "MULTICOUNTRY"
    elif len(countries) == 1:
        country_scope = "SINGLE_COUNTRY"
    else:
        country_scope = "UNKNOWN"
    us_center = (
        "YES"
        if any(country in {"United States", "USA", "United States of America"} for country in countries)
        else ("NO" if countries else "UNKNOWN")
    )
    if first_submit and start:
        registration_timing = (
            "PROSPECTIVE_OR_SAME_DAY" if first_submit <= start else "RETROSPECTIVE"
        )
    else:
        registration_timing = "UNKNOWN"
    std_ages = eligibility.get("stdAges", []) or []
    std_ages = [str(value) for value in std_ages]
    adult_relevant = (
        "YES" if {"ADULT", "OLDER_ADULT"}.intersection(std_ages) else ("NO" if std_ages else "UNKNOWN")
    )
    enrollment = design.get("enrollmentInfo", {}) or {}
    enrollment_count = enrollment.get("count")
    enrollment_number = safe_float(str(enrollment_count)) if enrollment_count is not None else None
    overall_status = str(status.get("overallStatus") or "UNKNOWN")
    return {
        "NCT_ID": nct_id,
        "Brief_Title": str(identification.get("briefTitle") or ""),
        "Study_Type": str(design.get("studyType") or "UNKNOWN"),
        "Allocation": allocation,
        "Intervention_Model": intervention_model,
        "Randomized": "YES" if allocation == "RANDOMIZED" else ("NO" if allocation != "UNKNOWN" else "UNKNOWN"),
        "Comparative": (
            "YES"
            if allocation in {"RANDOMIZED", "NON_RANDOMIZED"}
            and intervention_model != "SINGLE_GROUP"
            else ("UNKNOWN" if allocation == "UNKNOWN" else "NO")
        ),
        "Industry_Role": industry_role,
        "Device_Study": "YES" if "DEVICE" in intervention_types else "NO",
        "Intervention_Types": "|".join(intervention_types),
        "Country_Scope": country_scope,
        "Country_Count": len(countries),
        "US_Center": us_center,
        "Registration_Timing": registration_timing,
        "Overall_Status": overall_status,
        "Enrollment_Count": enrollment_count if enrollment_count is not None else "",
        "Withdrawn_Zero_Enrollment": (
            "YES" if overall_status == "WITHDRAWN" and enrollment_number == 0 else "NO"
        ),
        "Completed": "YES" if overall_status == "COMPLETED" else "NO",
        "Study_First_Post_Date": first_post_raw or "",
        "Study_First_Post_Year": first_post.year if first_post else "",
        "Period": period_for_year(first_post.year if first_post else None),
        "Study_Start_Date": start_raw or "",
        "Study_First_Submit_Date": first_submit_raw or "",
        "Std_Ages": "|".join(std_ages),
        "Adult_Relevant_Registry": adult_relevant,
        "Has_Results": "YES" if "resultsSection" in document else "NO",
    }


def result_row(
    result_id: str,
    module: str,
    population: str,
    stratum_variable: str,
    stratum_value: str,
    metric: str,
    category: str = "",
    numerator: int | float | str = "",
    denominator: int | float | str = "",
    unknown_count: int | float | str = "",
    percentage: float | None = None,
    value: int | float | str = "",
    unit: str = "",
    notes: str = "",
    source_table: str = "",
    framework: str = "",
) -> dict[str, Any]:
    return {
        "result_id": result_id,
        "module": module,
        "analysis_population": population,
        "stratum_variable": stratum_variable,
        "stratum_value": stratum_value,
        "metric": metric,
        "category": category,
        "numerator": numerator,
        "denominator": denominator,
        "unknown_count": unknown_count,
        "percentage": "" if percentage is None else percentage,
        "value": value,
        "unit": unit,
        "notes": notes,
        "source_table": source_table,
        "framework": framework,
    }


def svg_bar_chart(
    path: Path,
    title: str,
    subtitle: str,
    labels: Sequence[str],
    series: Sequence[tuple[str, Sequence[float], str]],
    y_label: str,
) -> None:
    width = 1100
    height = 620
    left, right, top, bottom = 110, 45, 100, 120
    chart_width = width - left - right
    chart_height = height - top - bottom
    all_values = [value for _, values, _ in series for value in values]
    maximum = max(all_values, default=1.0)
    ceiling = max(1.0, math.ceil(maximum / 10.0) * 10.0)
    group_width = chart_width / max(1, len(labels))
    bar_width = group_width * 0.75 / max(1, len(series))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="{left}" y="38" font-family="Arial" font-size="25" '
        f'font-weight="bold" fill="#172b4d">{html.escape(title)}</text>',
        f'<text x="{left}" y="68" font-family="Arial" font-size="14" '
        f'fill="#42526e">{html.escape(subtitle)}</text>',
    ]
    for tick in range(0, 6):
        value = ceiling * tick / 5
        y = top + chart_height - chart_height * tick / 5
        parts.append(
            f'<line x1="{left}" x2="{width-right}" y1="{y:.2f}" y2="{y:.2f}" '
            'stroke="#dfe1e6" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{left-12}" y="{y+5:.2f}" text-anchor="end" '
            f'font-family="Arial" font-size="12" fill="#5e6c84">{value:.0f}</text>'
        )
    for label_index, label in enumerate(labels):
        group_x = left + label_index * group_width
        for series_index, (_series_name, values, color) in enumerate(series):
            value = float(values[label_index])
            bar_height = chart_height * value / ceiling
            x = group_x + group_width * 0.125 + series_index * bar_width
            y = top + chart_height - bar_height
            parts.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width-3:.2f}" '
                f'height="{bar_height:.2f}" fill="{color}"/>'
            )
            parts.append(
                f'<text x="{x+(bar_width-3)/2:.2f}" y="{max(top+12, y-5):.2f}" '
                f'text-anchor="middle" font-family="Arial" font-size="11" '
                f'fill="#172b4d">{value:.1f}</text>'
            )
        label_text = html.escape(label)
        parts.append(
            f'<text x="{group_x+group_width/2:.2f}" y="{top+chart_height+28}" '
            f'text-anchor="middle" font-family="Arial" font-size="12" '
            f'fill="#172b4d">{label_text}</text>'
        )
    legend_x = left
    legend_y = height - 42
    for index, (series_name, _, color) in enumerate(series):
        x = legend_x + index * 260
        parts.append(f'<rect x="{x}" y="{legend_y-12}" width="16" height="16" fill="{color}"/>')
        parts.append(
            f'<text x="{x+24}" y="{legend_y+1}" font-family="Arial" font-size="13" '
            f'fill="#172b4d">{html.escape(series_name)}</text>'
        )
    parts.append(
        f'<text transform="translate(28 {top+chart_height/2}) rotate(-90)" '
        f'text-anchor="middle" font-family="Arial" font-size="13" '
        f'fill="#42526e">{html.escape(y_label)}</text>'
    )
    parts.append("</svg>")
    write_text(path, "\n".join(parts) + "\n")


def deterministic_zip(path: Path, members: Sequence[tuple[Path, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source, archive_name in sorted(members, key=lambda item: item[1]):
            info = zipfile.ZipInfo(archive_name, date_time=(2026, 7, 27, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, source.read_bytes())


def csv_bytes(rows: Sequence[dict[str, Any]], fields: Sequence[str]) -> bytes:
    import io

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(
        buffer,
        fieldnames=list(fields),
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def require(condition: bool, message: str, checks: list[dict[str, Any]]) -> None:
    checks.append({"check": message, "status": "PASS" if condition else "FAIL"})
    if not condition:
        raise RuntimeError(message)


def build_age_outputs(
    age_rows: Sequence[dict[str, str]],
    included_ids: set[str],
) -> tuple[
    dict[str, list[dict[str, Any]]],
    list[dict[str, Any]],
    dict[str, dict[str, str]],
    list[dict[str, Any]],
]:
    by_nct: dict[str, dict[str, str]] = defaultdict(dict)
    scale_a: dict[str, dict[str, str]] = defaultdict(dict)
    scale_b: dict[str, dict[str, str]] = defaultdict(dict)
    for row in age_rows:
        nct_id = row["NCT_ID"]
        by_nct[nct_id][row["Field_ID"]] = final_age_value(row)
        scale_a[nct_id][row["Field_ID"]] = row.get("Scale_A_Final_Value", "")
        scale_b[nct_id][row["Field_ID"]] = row.get("Scale_B_Final_Value", "")
    table_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    result_counter = 1
    for scale_name in ("Structured", "Reconciled"):
        for threshold in (65, 75, 80, 85):
            field = f"Eligible_{threshold}_{scale_name}"
            counts = Counter(by_nct[nct_id].get(field, "MISSING") for nct_id in included_ids)
            total = len(included_ids)
            unknown = counts["UNKNOWN"] + counts["MISSING"] + counts["REQUIRES_EXPERT_DECISION"]
            evaluable = total - unknown
            for category in ("YES", "NO", "UNKNOWN", "REQUIRES_EXPERT_DECISION", "MISSING"):
                number = counts[category]
                if not number and category == "MISSING":
                    continue
                table_rows.append(
                    {
                        "Age_Scale": scale_name.upper(),
                        "Threshold_Years": threshold,
                        "Category": category,
                        "Count": number,
                        "Total_Denominator": total,
                        "Evaluable_Denominator": evaluable,
                        "Unknown_Count": unknown,
                        "Percent_Total": pct(number, total),
                        "Percent_Evaluable": (
                            pct(number, evaluable) if category in {"YES", "NO"} else ""
                        ),
                    }
                )
                long_rows.append(
                    result_row(
                        f"AGE{result_counter:04d}",
                        "AGE_ELIGIBILITY",
                        "ALL_INCLUDED",
                        "AGE_SCALE_THRESHOLD",
                        f"{scale_name.upper()}_{threshold}",
                        "ELIGIBILITY_CATEGORY",
                        category,
                        number,
                        total,
                        unknown,
                        pct(number, total),
                        notes="Percent_Total uses all included records; evaluable percentage is in T02.",
                        source_table="T02_AGE_ELIGIBILITY_THRESHOLDS.csv",
                    )
                )
                result_counter += 1
    for field, label in [
        ("Structured_Upper_Age_Status", "STRUCTURED_UPPER_AGE_STATUS"),
        ("Age_Field_Conflict", "AGE_FIELD_CONFLICT"),
    ]:
        counts = Counter(by_nct[nct_id].get(field, "MISSING") for nct_id in included_ids)
        unknown = sum(counts[state] for state in SEPARATE_MISSING_STATES if state in counts)
        for category, number in sorted(counts.items()):
            table_rows.append(
                {
                    "Age_Scale": label,
                    "Threshold_Years": "",
                    "Category": category,
                    "Count": number,
                    "Total_Denominator": len(included_ids),
                    "Evaluable_Denominator": len(included_ids) - unknown,
                    "Unknown_Count": unknown,
                    "Percent_Total": pct(number, len(included_ids)),
                    "Percent_Evaluable": (
                        pct(number, len(included_ids) - unknown)
                        if category not in SEPARATE_MISSING_STATES
                        else ""
                    ),
                }
            )
            long_rows.append(
                result_row(
                    f"AGE{result_counter:04d}",
                    "AGE_ELIGIBILITY",
                    "ALL_INCLUDED",
                    label,
                    "ALL",
                    label,
                    category,
                    number,
                    len(included_ids),
                    unknown,
                    pct(number, len(included_ids)),
                    source_table="T02_AGE_ELIGIBILITY_THRESHOLDS.csv",
                )
            )
            result_counter += 1
    numeric_rows: list[dict[str, Any]] = []
    for field in ("Minimum_Age_Years", "Maximum_Age_Years"):
        values = [
            safe_float(by_nct[nct_id].get(field, ""))
            for nct_id in included_ids
        ]
        numeric_values = [value for value in values if value is not None]
        stats = descriptive_numeric(numeric_values)
        row = {
            "Field": field,
            "Observed_N": stats["n"],
            "Total_Denominator": len(included_ids),
            "Unknown_Count": len(included_ids) - stats["n"],
            "Median": stats["median"],
            "Q1": stats["q1"],
            "Q3": stats["q3"],
            "Minimum": stats["minimum"],
            "Maximum": stats["maximum"],
            "Unit": "years",
        }
        numeric_rows.append(row)
        for metric_name in ("median", "q1", "q3", "minimum", "maximum"):
            long_rows.append(
                result_row(
                    f"AGE{result_counter:04d}",
                    "AGE_ELIGIBILITY",
                    "ALL_INCLUDED",
                    "AGE_NUMERIC_FIELD",
                    field,
                    metric_name.upper(),
                    denominator=len(included_ids),
                    unknown_count=len(included_ids) - stats["n"],
                    value="" if stats[metric_name] is None else stats[metric_name],
                    unit="years",
                    source_table="T03_AGE_NUMERIC_SUMMARY.csv",
                )
            )
            result_counter += 1
    sensitivity_rows: list[dict[str, Any]] = []
    for scale_name in ("Structured", "Reconciled"):
        for threshold in (65, 75, 80, 85):
            field = f"Eligible_{threshold}_{scale_name}"
            values = [by_nct[nct_id].get(field, "MISSING") for nct_id in included_ids]
            yes = sum(value == "YES" for value in values)
            unknown = sum(value not in {"YES", "NO"} for value in values)
            sensitivity_rows.extend(
                [
                    {
                        "Sensitivity_ID": f"AGE_UNKNOWN_NO_{scale_name.upper()}_{threshold}",
                        "Module": "AGE",
                        "Population": "ALL_INCLUDED",
                        "Scenario": "UNKNOWN_ALL_NO",
                        "Metric": f"ELIGIBLE_{threshold}_{scale_name.upper()}",
                        "Numerator": yes,
                        "Denominator": len(values),
                        "Unknown_Count": unknown,
                        "Percent": pct(yes, len(values)),
                        "Status": "RUN",
                        "Notes": "Unknown and expert-decision states assigned NO for the bound.",
                    },
                    {
                        "Sensitivity_ID": f"AGE_UNKNOWN_YES_{scale_name.upper()}_{threshold}",
                        "Module": "AGE",
                        "Population": "ALL_INCLUDED",
                        "Scenario": "UNKNOWN_ALL_YES",
                        "Metric": f"ELIGIBLE_{threshold}_{scale_name.upper()}",
                        "Numerator": yes + unknown,
                        "Denominator": len(values),
                        "Unknown_Count": unknown,
                        "Percent": pct(yes + unknown, len(values)),
                        "Status": "RUN",
                        "Notes": "Unknown and expert-decision states assigned YES for the bound.",
                    },
                ]
            )
    return (
        {
            "T02_AGE_ELIGIBILITY_THRESHOLDS.csv": table_rows,
            "T03_AGE_NUMERIC_SUMMARY.csv": numeric_rows,
        },
        long_rows,
        by_nct,
        sensitivity_rows,
    )


def build_geriatric_outputs(
    rows: Sequence[dict[str, str]],
    included_ids: set[str],
) -> tuple[
    dict[str, list[dict[str, Any]]],
    list[dict[str, Any]],
    dict[str, dict[str, str]],
]:
    by_nct: dict[str, dict[str, str]] = defaultdict(dict)
    for row in rows:
        by_nct[row["NCT_ID"]][row["Domain_ID"]] = row.get("Expert_Proposed_Code", "")
    table_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    counter = 1
    for domain in GERIATRIC_DOMAINS:
        counts = Counter(by_nct[nct_id].get(domain, "MISSING") for nct_id in included_ids)
        unknown = (
            counts["REQUIRES_EXPERT_DECISION"]
            + counts["UNKNOWN"]
            + counts["MISSING"]
        )
        for category in sorted(counts):
            number = counts[category]
            table_rows.append(
                {
                    "Domain_ID": domain,
                    "Category": category,
                    "Count": number,
                    "Denominator": len(included_ids),
                    "Unknown_Count": unknown,
                    "Percent": pct(number, len(included_ids)),
                }
            )
            long_rows.append(
                result_row(
                    f"GER{counter:04d}",
                    "GERIATRIC_DOMAINS",
                    "ALL_INCLUDED",
                    "DOMAIN_ID",
                    domain,
                    "DOMAIN_CODE",
                    category,
                    number,
                    len(included_ids),
                    unknown,
                    pct(number, len(included_ids)),
                    source_table="T05_GERIATRIC_DOMAIN_CODES.csv",
                )
            )
            counter += 1
    composite_rows: list[dict[str, Any]] = []
    primary_domains = [
        domain for domain in GERIATRIC_DOMAINS if domain != "polypharmacy_medication_burden"
    ]
    for composite_name, domains in [
        ("PRIMARY_EIGHT_DOMAIN_ANY_PRESENT", primary_domains),
        ("ALL_NINE_DOMAIN_ANY_PRESENT", GERIATRIC_DOMAINS),
        ("PROXY_CONSENT_PATHWAY_PRESENT", ["proxy_consent_pathway"]),
    ]:
        statuses = []
        for nct_id in included_ids:
            values = [by_nct[nct_id].get(domain, "MISSING") for domain in domains]
            if any(value == "PRESENT" for value in values):
                status = "YES"
            elif any(value in {"REQUIRES_EXPERT_DECISION", "UNKNOWN", "MISSING"} for value in values):
                status = "UNKNOWN"
            else:
                status = "NO"
            statuses.append(status)
        counts = Counter(statuses)
        unknown = counts["UNKNOWN"]
        for category in ("YES", "NO", "UNKNOWN"):
            number = counts[category]
            composite_rows.append(
                {
                    "Composite": composite_name,
                    "Category": category,
                    "Count": number,
                    "Denominator": len(included_ids),
                    "Unknown_Count": unknown,
                    "Percent": pct(number, len(included_ids)),
                }
            )
            long_rows.append(
                result_row(
                    f"GER{counter:04d}",
                    "GERIATRIC_COMPOSITE",
                    "ALL_INCLUDED",
                    "COMPOSITE",
                    composite_name,
                    "COMPOSITE_STATUS",
                    category,
                    number,
                    len(included_ids),
                    unknown,
                    pct(number, len(included_ids)),
                    source_table="T06_GERIATRIC_COMPOSITES.csv",
                )
            )
            counter += 1
    return (
        {
            "T05_GERIATRIC_DOMAIN_CODES.csv": table_rows,
            "T06_GERIATRIC_COMPOSITES.csv": composite_rows,
        },
        long_rows,
        by_nct,
    )


def normalized_outcome_domain(row: dict[str, str], framework: str) -> str:
    domain = row.get("Final_Outcome_Domain", "")
    if framework == "OUTPUTS" and domain == "adverse_events":
        return "adverse_events_safety"
    return domain


def outcome_is_mapped(row: dict[str, str]) -> bool:
    return row.get("Final_Outcome_Mapping", "") not in {
        "",
        "unmapped_other",
        "REQUIRES_EXPERT_DECISION",
        "UNKNOWN",
        "NOT_APPLICABLE",
        "NOT_PUBLICLY_SPECIFIED",
    }


def build_outcome_outputs(
    rows: Sequence[dict[str, str]],
    frameworks: Sequence[dict[str, str]],
    included_ids: set[str],
) -> tuple[
    dict[str, list[dict[str, Any]]],
    list[dict[str, Any]],
    dict[str, dict[str, dict[str, str]]],
]:
    framework_by_nct = {row["NCT_ID"]: row["Final_Framework"] for row in frameworks}
    rows_by_nct: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        rows_by_nct[row["NCT_ID"]].append(row)
    coverage_by_framework: dict[str, dict[str, dict[str, str]]] = {}
    coverage_tables: dict[str, list[dict[str, Any]]] = {
        "T07_COREVEN_COVERAGE.csv": [],
        "T08_OUTPUTS_COVERAGE.csv": [],
    }
    long_rows: list[dict[str, Any]] = []
    score_rows: list[dict[str, Any]] = []
    dimension_rows: list[dict[str, Any]] = []
    counter = 1
    for framework, domains, table_name in [
        ("COREVEN", COREVEN_DOMAINS, "T07_COREVEN_COVERAGE.csv"),
        ("OUTPUTS", OUTPUTS_DOMAINS, "T08_OUTPUTS_COVERAGE.csv"),
    ]:
        population_ids = sorted(
            nct_id
            for nct_id in included_ids
            if framework_by_nct.get(nct_id) == framework
        )
        coverage_by_framework[framework] = {}
        for window in ("PRIMARY_ONLY", "ANY_PLANNED"):
            coverage_by_framework[framework][window] = {}
            per_trial_status: dict[str, dict[str, str]] = {}
            for nct_id in population_ids:
                eligible_rows = [
                    row
                    for row in rows_by_nct.get(nct_id, [])
                    if window == "ANY_PLANNED" or row.get("Outcome_Level") == "PRIMARY"
                ]
                has_unclear = any(
                    row.get("Final_Outcome_Domain") == "REQUIRES_EXPERT_DECISION"
                    or row.get("Final_Outcome_Mapping") == "REQUIRES_EXPERT_DECISION"
                    for row in eligible_rows
                )
                statuses: dict[str, str] = {}
                for domain in domains:
                    present = any(
                        normalized_outcome_domain(row, framework) == domain
                        and outcome_is_mapped(row)
                        for row in eligible_rows
                    )
                    statuses[domain] = "PRESENT" if present else ("UNKNOWN" if has_unclear else "ABSENT")
                per_trial_status[nct_id] = statuses
            coverage_by_framework[framework][window] = {
                nct_id: json.dumps(statuses, sort_keys=True)
                for nct_id, statuses in per_trial_status.items()
            }
            for domain in domains:
                counts = Counter(statuses[domain] for statuses in per_trial_status.values())
                unknown = counts["UNKNOWN"]
                row = {
                    "Framework": framework,
                    "Coverage_Window": window,
                    "Domain": domain,
                    "Present_N": counts["PRESENT"],
                    "Denominator": len(population_ids),
                    "Unknown_Count": unknown,
                    "Absent_N": counts["ABSENT"],
                    "Percent_Total": pct(counts["PRESENT"], len(population_ids)),
                    "Percent_Evaluable": pct(
                        counts["PRESENT"], len(population_ids) - unknown
                    ),
                }
                coverage_tables[table_name].append(row)
                long_rows.append(
                    result_row(
                        f"OUT{counter:04d}",
                        "OUTCOME_COVERAGE",
                        f"{framework}_APPLICABLE",
                        "COVERAGE_WINDOW",
                        window,
                        "DOMAIN_PRESENT",
                        domain,
                        counts["PRESENT"],
                        len(population_ids),
                        unknown,
                        pct(counts["PRESENT"], len(population_ids)),
                        source_table=table_name,
                        framework=framework,
                    )
                )
                counter += 1
            score_counts: Counter[int | str] = Counter()
            all_domain_counts: Counter[str] = Counter()
            for statuses in per_trial_status.values():
                present_count = sum(value == "PRESENT" for value in statuses.values())
                has_unknown = any(value == "UNKNOWN" for value in statuses.values())
                score_counts[present_count] += 1
                if present_count == len(domains):
                    all_domain_counts["YES"] += 1
                elif has_unknown:
                    all_domain_counts["UNKNOWN"] += 1
                else:
                    all_domain_counts["NO"] += 1
            for score in range(len(domains) + 1):
                score_rows.append(
                    {
                        "Framework": framework,
                        "Coverage_Window": window,
                        "Metric": "DOMAIN_COUNT",
                        "Category": score,
                        "Count": score_counts[score],
                        "Denominator": len(population_ids),
                        "Unknown_Count": all_domain_counts["UNKNOWN"],
                        "Percent": pct(score_counts[score], len(population_ids)),
                    }
                )
            for category in ("YES", "NO", "UNKNOWN"):
                score_rows.append(
                    {
                        "Framework": framework,
                        "Coverage_Window": window,
                        "Metric": "ALL_DOMAINS_PRESENT",
                        "Category": category,
                        "Count": all_domain_counts[category],
                        "Denominator": len(population_ids),
                        "Unknown_Count": all_domain_counts["UNKNOWN"],
                        "Percent": pct(all_domain_counts[category], len(population_ids)),
                    }
                )
                long_rows.append(
                    result_row(
                        f"OUT{counter:04d}",
                        "OUTCOME_COVERAGE",
                        f"{framework}_APPLICABLE",
                        "COVERAGE_WINDOW",
                        window,
                        "ALL_DOMAINS_PRESENT",
                        category,
                        all_domain_counts[category],
                        len(population_ids),
                        all_domain_counts["UNKNOWN"],
                        pct(all_domain_counts[category], len(population_ids)),
                        source_table="T09_OUTCOME_COVERAGE_SCORES.csv",
                        framework=framework,
                    )
                )
                counter += 1
        applicable_outcomes = [
            row
            for row in rows
            if row["NCT_ID"] in population_ids and row.get("Final_Outcome_Framework") == framework
        ]
        for window in ("PRIMARY_ONLY", "ANY_PLANNED"):
            window_rows = [
                row
                for row in applicable_outcomes
                if window == "ANY_PLANNED" or row.get("Outcome_Level") == "PRIMARY"
            ]
            dimensions = {
                "REPORTER": [row.get("Final_Reporter", "") or "MISSING" for row in window_rows],
                "INSTRUMENT_STATUS": [
                    row.get("Final_Instrument_Status", "") or "MISSING" for row in window_rows
                ],
                "UNIT_OF_ANALYSIS": [
                    row.get("Final_Unit_of_Analysis", "") or "MISSING" for row in window_rows
                ],
                "OUTCOME_NATURE": [
                    row.get("Final_Outcome_Nature", "") or "MISSING" for row in window_rows
                ],
                "TIME_FRAME_SPECIFIED": [
                    "YES"
                    if (row.get("Time_Frame") or "").strip()
                    else "NOT_PUBLICLY_SPECIFIED"
                    for row in window_rows
                ],
                "NAMED_INSTRUMENT": [
                    "YES"
                    if row.get("Final_Instrument_Status") == "NAMED"
                    and (row.get("Final_Instrument_Name") or "").strip()
                    else (
                        row.get("Final_Instrument_Status", "") or "MISSING"
                    )
                    for row in window_rows
                ],
            }
            for dimension, values in dimensions.items():
                counts = Counter(values)
                unknown = sum(
                    number for category, number in counts.items() if category in SEPARATE_MISSING_STATES
                )
                for category, number in sorted(counts.items()):
                    dimension_rows.append(
                        {
                            "Framework": framework,
                            "Coverage_Window": window,
                            "Dimension": dimension,
                            "Category": category,
                            "Outcome_Row_Count": number,
                            "Outcome_Row_Denominator": len(window_rows),
                            "Unknown_Count": unknown,
                            "Percent": pct(number, len(window_rows)),
                        }
                    )
    coverage_tables["T09_OUTCOME_COVERAGE_SCORES.csv"] = score_rows
    coverage_tables["T10_OUTCOME_CHARACTERISTICS.csv"] = dimension_rows
    return coverage_tables, long_rows, coverage_by_framework


def build_population_sets(
    metadata: dict[str, dict[str, Any]],
    screening_by_nct: dict[str, dict[str, str]],
    framework_by_nct: dict[str, str],
) -> dict[str, set[str]]:
    included_ids = set(metadata)
    adult_registry = {
        nct_id
        for nct_id, row in metadata.items()
        if row["Adult_Relevant_Registry"] == "YES"
    }
    adult_human_scope = {
        nct_id
        for nct_id, row in screening_by_nct.items()
        if row.get("Final_Adult_Pediatric_Scope")
        in {"ADULT_ONLY_OR_RELEVANT", "MIXED_AGE_OR_ADULT_RELEVANT"}
    }
    vlu = {nct_id for nct_id in included_ids if framework_by_nct.get(nct_id) == "COREVEN"}
    pi_prevention = {
        nct_id for nct_id in included_ids if framework_by_nct.get(nct_id) == "OUTPUTS"
    }
    cos_applicable = vlu | pi_prevention
    cos_adult_comparative = {
        nct_id
        for nct_id in cos_applicable & adult_registry
        if metadata[nct_id]["Comparative"] == "YES"
    }
    cos_adult_randomized = {
        nct_id
        for nct_id in cos_adult_comparative
        if metadata[nct_id]["Randomized"] == "YES"
    }
    return {
        "ALL_INCLUDED": included_ids,
        "ADULT_RELEVANT_REGISTRY": adult_registry,
        "ADULT_RELEVANT_HUMAN_SCOPE": adult_human_scope,
        "VLU_ACTIVE_TREATMENT": vlu,
        "PI_PREVENTION": pi_prevention,
        "COS_ADULT_COMPARATIVE": cos_adult_comparative,
        "COS_ADULT_RANDOMIZED": cos_adult_randomized,
    }


def build_characteristic_outputs(
    metadata: dict[str, dict[str, Any]],
    population_sets: dict[str, set[str]],
    age_by_nct: dict[str, dict[str, str]],
    geriatric_by_nct: dict[str, dict[str, str]],
    screening_by_nct: dict[str, dict[str, str]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    dimensions = [
        "Study_Type",
        "Randomized",
        "Industry_Role",
        "Device_Study",
        "Country_Scope",
        "US_Center",
        "Registration_Timing",
        "Overall_Status",
        "Period",
        "Adult_Relevant_Registry",
    ]
    rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    counter = 1
    for population_name, ids in population_sets.items():
        for dimension in dimensions:
            values = [
                str(metadata[nct_id].get(dimension, "") or "MISSING")
                for nct_id in sorted(ids)
            ]
            counts = Counter(values)
            unknown = sum(
                number for category, number in counts.items() if category in SEPARATE_MISSING_STATES
            )
            for category, number in sorted(counts.items()):
                rows.append(
                    {
                        "Population": population_name,
                        "Dimension": dimension,
                        "Category": category,
                        "Count": number,
                        "Denominator": len(ids),
                        "Unknown_Count": unknown,
                        "Percent": pct(number, len(ids)),
                        "Small_Denominator_Flag": "YES" if len(ids) < 10 else "NO",
                    }
                )
                long_rows.append(
                    result_row(
                        f"CHR{counter:05d}",
                        "TRIAL_CHARACTERISTICS",
                        population_name,
                        dimension,
                        "ALL",
                        "CATEGORY_COUNT",
                        category,
                        number,
                        len(ids),
                        unknown,
                        pct(number, len(ids)),
                        notes=(
                            "Counts are primary when denominator is below 10."
                            if len(ids) < 10
                            else ""
                        ),
                        source_table="T11_TRIAL_CHARACTERISTICS.csv",
                    )
                )
                counter += 1
    stratified_rows: list[dict[str, Any]] = []
    all_ids = population_sets["ALL_INCLUDED"]
    strata: dict[str, set[str]] = {}
    for period in (
        "2000-2007_HISTORICAL_APPENDIX",
        "2008-2016",
        "2017-2018",
        "2019-2025",
        "UNKNOWN",
    ):
        strata[f"PERIOD:{period}"] = {
            nct_id for nct_id in all_ids if metadata[nct_id]["Period"] == period
        }
    for disease in (
        "VLU_ACTIVE_TREATMENT",
        "PI_PREVENTION",
        "PI_TREATMENT",
        "VLU_RECURRENCE_PREVENTION",
        "MIXED_WOUND_EXPLICIT_TARGET",
    ):
        strata[f"DISEASE:{disease}"] = {
            nct_id
            for nct_id in all_ids
            if screening_by_nct[nct_id].get("Final_Disease_Intent_Group") == disease
        }

    def key_metric(ids: set[str], metric: str) -> tuple[int, int, int]:
        if metric == "FINITE_UPPER_AGE_LIMIT":
            values = [
                age_by_nct[nct_id].get("Structured_Upper_Age_Status", "MISSING")
                for nct_id in ids
            ]
            yes = sum(value == "FINITE_UPPER_LIMIT" for value in values)
            unknown = sum(value in {"UNKNOWN", "MISSING"} for value in values)
        elif metric == "ELIGIBLE_85_RECONCILED":
            values = [
                age_by_nct[nct_id].get("Eligible_85_Reconciled", "MISSING")
                for nct_id in ids
            ]
            yes = sum(value == "YES" for value in values)
            unknown = sum(value not in {"YES", "NO"} for value in values)
        elif metric == "ANY_PRIMARY_GERIATRIC_DOMAIN_PRESENT":
            primary_domains = [
                domain
                for domain in GERIATRIC_DOMAINS
                if domain != "polypharmacy_medication_burden"
            ]
            statuses = []
            for nct_id in ids:
                values = [
                    geriatric_by_nct[nct_id].get(domain, "MISSING")
                    for domain in primary_domains
                ]
                if any(value == "PRESENT" for value in values):
                    statuses.append("YES")
                elif any(
                    value in {"REQUIRES_EXPERT_DECISION", "UNKNOWN", "MISSING"}
                    for value in values
                ):
                    statuses.append("UNKNOWN")
                else:
                    statuses.append("NO")
            yes = statuses.count("YES")
            unknown = statuses.count("UNKNOWN")
        elif metric == "RANDOMIZED":
            values = [metadata[nct_id]["Randomized"] for nct_id in ids]
            yes = values.count("YES")
            unknown = values.count("UNKNOWN")
        elif metric == "COMPLETED":
            values = [metadata[nct_id]["Completed"] for nct_id in ids]
            yes = values.count("YES")
            unknown = values.count("UNKNOWN")
        else:
            raise ValueError(metric)
        return yes, len(ids), unknown

    metrics = [
        "FINITE_UPPER_AGE_LIMIT",
        "ELIGIBLE_85_RECONCILED",
        "ANY_PRIMARY_GERIATRIC_DOMAIN_PRESENT",
        "RANDOMIZED",
        "COMPLETED",
    ]
    for stratum, ids in strata.items():
        for metric in metrics:
            numerator, denominator, unknown = key_metric(ids, metric)
            stratified_rows.append(
                {
                    "Stratum": stratum,
                    "Metric": metric,
                    "Numerator": numerator,
                    "Denominator": denominator,
                    "Unknown_Count": unknown,
                    "Percent_Total": pct(numerator, denominator),
                    "Small_Denominator_Flag": "YES" if denominator < 10 else "NO",
                }
            )
    differences: list[dict[str, Any]] = []
    contrast_pairs = [
        ("PERIOD:2008-2016", "PERIOD:2019-2025"),
        ("DISEASE:VLU_ACTIVE_TREATMENT", "DISEASE:PI_PREVENTION"),
    ]
    indexed = {(row["Stratum"], row["Metric"]): row for row in stratified_rows}
    for reference, comparison in contrast_pairs:
        for metric in metrics:
            reference_row = indexed[(reference, metric)]
            comparison_row = indexed[(comparison, metric)]
            reference_pct = reference_row["Percent_Total"]
            comparison_pct = comparison_row["Percent_Total"]
            difference = (
                round(float(comparison_pct) - float(reference_pct), 6)
                if reference_pct is not None and comparison_pct is not None
                else ""
            )
            differences.append(
                {
                    "Reference_Stratum": reference,
                    "Comparison_Stratum": comparison,
                    "Metric": metric,
                    "Reference_Numerator": reference_row["Numerator"],
                    "Reference_Denominator": reference_row["Denominator"],
                    "Reference_Unknown": reference_row["Unknown_Count"],
                    "Reference_Percent": reference_pct,
                    "Comparison_Numerator": comparison_row["Numerator"],
                    "Comparison_Denominator": comparison_row["Denominator"],
                    "Comparison_Unknown": comparison_row["Unknown_Count"],
                    "Comparison_Percent": comparison_pct,
                    "Absolute_Percentage_Point_Difference": difference,
                    "Interpretation": "DESCRIPTIVE_ONLY",
                }
            )
    return (
        {
            "T11_TRIAL_CHARACTERISTICS.csv": rows,
            "T12_STRATIFIED_DESCRIPTIONS.csv": stratified_rows,
            "T13_ABSOLUTE_PERCENTAGE_POINT_DIFFERENCES.csv": differences,
        },
        long_rows,
    )


def metrics_to_row(
    module: str,
    field: str,
    metrics: dict[str, Any],
    positive_definition: str,
) -> dict[str, Any]:
    return {
        "Module": module,
        "Field_or_Domain": field,
        "Paired_N": metrics["n"],
        "Agreements": metrics["agreements"],
        "Raw_Agreement": metrics["raw_agreement"],
        "Positive_Agreement": metrics["positive_agreement"],
        "Negative_Agreement": metrics["negative_agreement"],
        "Cohen_Kappa": metrics["cohen_kappa"],
        "Gwet_AC1": metrics["gwet_ac1"],
        "Gwet_AC2": metrics["gwet_ac2"],
        "Positive_Definition": positive_definition,
        "Weighting": "NOMINAL_IDENTITY; AC2_EQUALS_AC1",
    }


def build_reliability_outputs(
    age_rows: Sequence[dict[str, str]],
    geriatric_rows: Sequence[dict[str, str]],
    framework_rows: Sequence[dict[str, str]],
    outcome_rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []
    categorical_age_fields = [
        "Age_Field_Conflict",
        "Structured_Upper_Age_Status",
        "Eligible_65_Structured",
        "Eligible_75_Structured",
        "Eligible_80_Structured",
        "Eligible_85_Structured",
        "Eligible_65_Reconciled",
        "Eligible_75_Reconciled",
        "Eligible_80_Reconciled",
        "Eligible_85_Reconciled",
    ]
    age_by_field: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in age_rows:
        age_by_field[row["Field_ID"]].append(row)
    for field in categorical_age_fields:
        field_rows = sorted(age_by_field[field], key=lambda row: row["NCT_ID"])
        positive = {"TRUE"} if field == "Age_Field_Conflict" else {"YES"}
        if field == "Structured_Upper_Age_Status":
            positive = {"FINITE_UPPER_LIMIT"}
        metrics = agreement_metrics(
            [row.get("Scale_A_Final_Value", "") for row in field_rows],
            [row.get("Scale_B_Final_Value", "") for row in field_rows],
            positive,
        )
        rows.append(metrics_to_row("AGE", field, metrics, "|".join(sorted(positive))))
    geriatric_by_domain: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in geriatric_rows:
        geriatric_by_domain[row["Domain_ID"]].append(row)
    pooled_a: list[str] = []
    pooled_b: list[str] = []
    for domain in GERIATRIC_DOMAINS:
        domain_rows = sorted(geriatric_by_domain[domain], key=lambda row: row["NCT_ID"])
        values_a = [row.get("Scale_A_Final_Code", "") for row in domain_rows]
        values_b = [row.get("Scale_B_Final_Code", "") for row in domain_rows]
        pooled_a.extend(values_a)
        pooled_b.extend(values_b)
        metrics = agreement_metrics(values_a, values_b, {"PRESENT"})
        rows.append(metrics_to_row("GERIATRIC", domain, metrics, "PRESENT"))
    rows.append(
        metrics_to_row(
            "GERIATRIC",
            "ALL_NINE_DOMAINS_POOLED",
            agreement_metrics(pooled_a, pooled_b, {"PRESENT"}),
            "PRESENT",
        )
    )
    framework_a: list[str] = []
    framework_b: list[str] = []
    for row in sorted(framework_rows, key=lambda item: item["NCT_ID"]):
        framework_a.append(
            str(parse_json_object(row.get("Scale_A_Final_Value_JSON", "")).get("Framework", ""))
        )
        framework_b.append(
            str(parse_json_object(row.get("Scale_B_Final_Value_JSON", "")).get("Framework", ""))
        )
    rows.append(
        metrics_to_row(
            "FRAMEWORK",
            "FRAMEWORK_CATEGORY",
            agreement_metrics(framework_a, framework_b),
            "NOT_APPLICABLE_MULTICATEGORY",
        )
    )
    outcome_fields = [
        ("Outcome_Domain", "MAPPED_DOMAIN"),
        ("Outcome_Mapping", "MAPPED_OUTCOME"),
        ("Reporter", "SPECIFIED_REPORTER"),
        ("Instrument_Status", "NAMED"),
        ("Unit_of_Analysis", "SPECIFIED_UNIT"),
        ("Outcome_Nature", "SPECIFIED_NATURE"),
    ]
    parsed_outcomes = [
        (
            parse_json_object(row.get("Scale_A_Final_Value_JSON", "")),
            parse_json_object(row.get("Scale_B_Final_Value_JSON", "")),
        )
        for row in sorted(outcome_rows, key=lambda item: item["Outcome_ID"])
    ]
    for field, positive_label in outcome_fields:
        values_a = [str(a.get(field, "")) for a, _ in parsed_outcomes]
        values_b = [str(b.get(field, "")) for _, b in parsed_outcomes]
        if field == "Outcome_Mapping":
            positive = {
                value
                for value in set(values_a) | set(values_b)
                if value
                and value
                not in {
                    "unmapped_other",
                    "REQUIRES_EXPERT_DECISION",
                    "UNKNOWN",
                    "NOT_APPLICABLE",
                }
            }
        elif field == "Instrument_Status":
            positive = {"NAMED"}
        else:
            positive = {
                value
                for value in set(values_a) | set(values_b)
                if value
                and value
                not in {
                    "UNKNOWN",
                    "REQUIRES_EXPERT_DECISION",
                    "NOT_APPLICABLE",
                    "NOT_PUBLICLY_SPECIFIED",
                }
            }
        metrics = agreement_metrics(values_a, values_b, positive)
        rows.append(metrics_to_row("OUTCOME", field, metrics, positive_label))
    for index, row in enumerate(rows, start=1):
        for metric_name in (
            "Raw_Agreement",
            "Positive_Agreement",
            "Negative_Agreement",
            "Cohen_Kappa",
            "Gwet_AC1",
            "Gwet_AC2",
        ):
            value = row[metric_name]
            long_rows.append(
                result_row(
                    f"REL{index:03d}_{metric_name}",
                    "RELIABILITY",
                    "PAIRED_CODER_RECORDS",
                    "FIELD_OR_DOMAIN",
                    row["Field_or_Domain"],
                    metric_name.upper(),
                    denominator=row["Paired_N"],
                    value="" if value is None else value,
                    unit="proportion",
                    notes=row["Positive_Definition"],
                    source_table="T14_RELIABILITY_SUMMARY.csv",
                    framework=row["Module"],
                )
            )
    return rows, long_rows


def build_corrected_reliability_outputs(
    age_rows: Sequence[dict[str, str]],
    geriatric_rows: Sequence[dict[str, str]],
    framework_rows: Sequence[dict[str, str]],
    outcome_rows: Sequence[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Preserve historical reliability and separately label new-record QC.

    The 12 newly included records were confirmed through a source-linked
    cross-scale quality-control workflow. Their 309/366 agreement is a
    workflow-QC result, not traditional unassisted human inter-rater
    reliability. The prespecified historical reliability functions therefore
    receive only the protected 1,206-record rows. Reporter and unit-of-analysis
    results remain explicitly supplementary/exploratory.
    """

    historical_age = [r for r in age_rows if r.get("Delta_Type") != NEW_RECORD_DELTA_TYPE]
    historical_geriatric = [
        r for r in geriatric_rows if r.get("Delta_Type") != NEW_RECORD_DELTA_TYPE
    ]
    historical_framework = [
        r for r in framework_rows if r.get("Delta_Type") != NEW_RECORD_DELTA_TYPE
    ]
    historical_outcome = [
        r for r in outcome_rows if r.get("Delta_Type") != NEW_RECORD_DELTA_TYPE
    ]
    rows, long_rows = build_reliability_outputs(
        historical_age,
        historical_geriatric,
        historical_framework,
        historical_outcome,
    )
    for row in rows:
        if row["Module"] == "OUTCOME" and row["Field_or_Domain"] in {
            "Reporter",
            "Unit_of_Analysis",
        }:
            row["Weighting"] = (
                f"{row['Weighting']}; SUPPLEMENTARY_EXPLORATORY_ONLY; "
                "NOT_FOR_PRIMARY_CONCLUSIONS"
            )

    new_rows = (
        [r for r in age_rows if r.get("Delta_Type") == NEW_RECORD_DELTA_TYPE]
        + [r for r in geriatric_rows if r.get("Delta_Type") == NEW_RECORD_DELTA_TYPE]
        + [r for r in framework_rows if r.get("Delta_Type") == NEW_RECORD_DELTA_TYPE]
        + [r for r in outcome_rows if r.get("Delta_Type") == NEW_RECORD_DELTA_TYPE]
    )
    require(len(new_rows) == 366, "new-record cross-scale QC rows are 366", [])
    agreements = 0
    for row in new_rows:
        if "Scale_A_Final_Value" in row:
            a_value = row.get("Scale_A_Final_Value", "")
            b_value = row.get("Scale_B_Final_Value", "")
        elif "Scale_A_Final_Code" in row:
            a_value = row.get("Scale_A_Final_Code", "")
            b_value = row.get("Scale_B_Final_Code", "")
        else:
            a_value = row.get("Scale_A_Final_Value_JSON", "")
            b_value = row.get("Scale_B_Final_Value_JSON", "")
        agreements += int(a_value == b_value)
    require(agreements == 309, "new-record cross-scale QC agreements are 309/366", [])
    qc_row = {
        "Module": "WORKFLOW_QC",
        "Field_or_Domain": "NEW_12_RECORD_ALL_CODING_ROWS",
        "Paired_N": 366,
        "Agreements": 309,
        "Raw_Agreement": 309 / 366,
        "Positive_Agreement": "",
        "Negative_Agreement": "",
        "Cohen_Kappa": "",
        "Gwet_AC1": "",
        "Gwet_AC2": "",
        "Positive_Definition": CROSS_SCALE_QC_LABEL,
        "Weighting": "NOT_TRADITIONAL_INDEPENDENT_HUMAN_RELIABILITY",
    }
    rows.append(qc_row)
    long_rows.append(
        result_row(
            "REL_WORKFLOW_QC_NEW12",
            "WORKFLOW_QC",
            "HUMAN_CONFIRMED_CROSS_SCALE_QC_ROWS",
            "FIELD_OR_DOMAIN",
            "NEW_12_RECORD_ALL_CODING_ROWS",
            "RAW_AGREEMENT",
            numerator=309,
            denominator=366,
            value=309 / 366,
            unit="proportion",
            notes=CROSS_SCALE_QC_LABEL,
            source_table="T14_RELIABILITY_SUMMARY.csv",
            framework="WORKFLOW_QC",
        )
    )
    return rows, long_rows


def build_sensitivity_outputs(
    initial_rows: Sequence[dict[str, Any]],
    metadata: dict[str, dict[str, Any]],
    population_sets: dict[str, set[str]],
    age_rows: Sequence[dict[str, str]],
    age_by_nct: dict[str, dict[str, str]],
    geriatric_rows: Sequence[dict[str, str]],
    geriatric_by_nct: dict[str, dict[str, str]],
    screening_by_nct: dict[str, dict[str, str]],
    outcome_rows: Sequence[dict[str, str]],
    framework_by_nct: dict[str, str],
) -> list[dict[str, Any]]:
    rows = list(initial_rows)
    all_ids = population_sets["ALL_INCLUDED"]
    scenarios: dict[str, set[str]] = {
        "PRIMARY_ALL_INCLUDED": set(all_ids),
        "PROSPECTIVE_REGISTRATION_ONLY": {
            nct_id
            for nct_id in all_ids
            if metadata[nct_id]["Registration_Timing"] == "PROSPECTIVE_OR_SAME_DAY"
        },
        "EXCLUDE_WITHDRAWN_ZERO_ENROLLMENT": {
            nct_id
            for nct_id in all_ids
            if metadata[nct_id]["Withdrawn_Zero_Enrollment"] != "YES"
        },
        "COMPLETED_ONLY": {
            nct_id for nct_id in all_ids if metadata[nct_id]["Completed"] == "YES"
        },
        "RANDOMIZED_COMPARATIVE_ONLY": {
            nct_id
            for nct_id in all_ids
            if metadata[nct_id]["Randomized"] == "YES"
            and metadata[nct_id]["Comparative"] == "YES"
        },
        "EXCLUDE_MIXED_WOUNDS": {
            nct_id
            for nct_id in all_ids
            if screening_by_nct[nct_id].get("Final_Disease_Intent_Group")
            != "MIXED_WOUND_EXPLICIT_TARGET"
        },
        "COS_APPLICABLE": population_sets["VLU_ACTIVE_TREATMENT"]
        | population_sets["PI_PREVENTION"],
        "ALL_INTERVENTIONAL": {
            nct_id
            for nct_id in all_ids
            if metadata[nct_id]["Study_Type"] == "INTERVENTIONAL"
        },
    }

    def append_metric(
        scenario: str,
        metric: str,
        numerator: int,
        denominator: int,
        unknown: int,
        notes: str = "",
    ) -> None:
        rows.append(
            {
                "Sensitivity_ID": f"SENS_{scenario}_{metric}",
                "Module": "PRESPECIFIED_POPULATION",
                "Population": scenario,
                "Scenario": scenario,
                "Metric": metric,
                "Numerator": numerator,
                "Denominator": denominator,
                "Unknown_Count": unknown,
                "Percent": pct(numerator, denominator),
                "Status": "RUN",
                "Notes": notes,
            }
        )

    primary_domains = [
        domain for domain in GERIATRIC_DOMAINS if domain != "polypharmacy_medication_burden"
    ]
    for scenario, ids in scenarios.items():
        age_values = [
            age_by_nct[nct_id].get("Eligible_85_Reconciled", "MISSING")
            for nct_id in ids
        ]
        append_metric(
            scenario,
            "ELIGIBLE_85_RECONCILED_YES",
            age_values.count("YES"),
            len(ids),
            sum(value not in {"YES", "NO"} for value in age_values),
        )
        upper_values = [
            age_by_nct[nct_id].get("Structured_Upper_Age_Status", "MISSING")
            for nct_id in ids
        ]
        append_metric(
            scenario,
            "FINITE_UPPER_LIMIT",
            upper_values.count("FINITE_UPPER_LIMIT"),
            len(ids),
            sum(value in {"UNKNOWN", "MISSING"} for value in upper_values),
        )
        composite = []
        for nct_id in ids:
            values = [
                geriatric_by_nct[nct_id].get(domain, "MISSING")
                for domain in primary_domains
            ]
            if any(value == "PRESENT" for value in values):
                composite.append("YES")
            elif any(
                value in {"REQUIRES_EXPERT_DECISION", "UNKNOWN", "MISSING"}
                for value in values
            ):
                composite.append("UNKNOWN")
            else:
                composite.append("NO")
        append_metric(
            scenario,
            "ANY_PRIMARY_GERIATRIC_DOMAIN_PRESENT",
            composite.count("YES"),
            len(ids),
            composite.count("UNKNOWN"),
        )
    age_85_rows = [
        row for row in age_rows if row["Field_ID"] == "Eligible_85_Reconciled"
    ]
    for source, field in [
        ("REVIEWER_A", "Scale_A_Final_Value"),
        ("REVIEWER_B", "Scale_B_Final_Value"),
        ("ADJUDICATED", "Expert_Proposed_Disposition"),
    ]:
        values = [row.get(field, "") for row in age_85_rows]
        append_metric(
            f"LABEL_SOURCE_{source}",
            "ELIGIBLE_85_RECONCILED_YES",
            values.count("YES"),
            len(values),
            sum(value not in {"YES", "NO"} for value in values),
            "Label-source sensitivity; original paired labels remain unchanged.",
        )
    for source, field in [
        ("REVIEWER_A", "Scale_A_Final_Code"),
        ("REVIEWER_B", "Scale_B_Final_Code"),
        ("ADJUDICATED", "Expert_Proposed_Code"),
    ]:
        by_id_domain: dict[str, dict[str, str]] = defaultdict(dict)
        for row in geriatric_rows:
            by_id_domain[row["NCT_ID"]][row["Domain_ID"]] = row.get(field, "")
        statuses = []
        for nct_id in sorted(all_ids):
            values = [by_id_domain[nct_id].get(domain, "MISSING") for domain in primary_domains]
            if any(value == "PRESENT" for value in values):
                statuses.append("YES")
            elif any(
                value in {"UNCLEAR", "REQUIRES_EXPERT_DECISION", "UNKNOWN", "MISSING"}
                for value in values
            ):
                statuses.append("UNKNOWN")
            else:
                statuses.append("NO")
        append_metric(
            f"LABEL_SOURCE_{source}",
            "ANY_PRIMARY_GERIATRIC_DOMAIN_PRESENT",
            statuses.count("YES"),
            len(statuses),
            statuses.count("UNKNOWN"),
            "Label-source sensitivity; original paired labels remain unchanged.",
        )
    for framework, domains in [("COREVEN", COREVEN_DOMAINS), ("OUTPUTS", OUTPUTS_DOMAINS)]:
        population_ids = {
            nct_id for nct_id in all_ids if framework_by_nct.get(nct_id) == framework
        }
        for window in ("PRIMARY_ONLY", "ANY_PLANNED"):
            all_domain_present = 0
            uncertain = 0
            for nct_id in population_ids:
                trial_rows = [
                    row
                    for row in outcome_rows
                    if row["NCT_ID"] == nct_id
                    and (window == "ANY_PLANNED" or row["Outcome_Level"] == "PRIMARY")
                ]
                statuses = []
                has_unclear = any(
                    row.get("Final_Outcome_Domain") == "REQUIRES_EXPERT_DECISION"
                    or row.get("Final_Outcome_Mapping") == "REQUIRES_EXPERT_DECISION"
                    for row in trial_rows
                )
                for domain in domains:
                    statuses.append(
                        any(
                            normalized_outcome_domain(row, framework) == domain
                            and outcome_is_mapped(row)
                            for row in trial_rows
                        )
                    )
                if all(statuses):
                    all_domain_present += 1
                elif has_unclear:
                    uncertain += 1
            append_metric(
                f"{framework}_{window}",
                "ALL_COS_DOMAINS_PRESENT",
                all_domain_present,
                len(population_ids),
                uncertain,
                "VLU CoreVen and PI-prevention OUTPUTs denominators remain separate.",
            )
    rows.extend(
        [
            {
                "Sensitivity_ID": "SENS_EXCLUDE_CONFIRMED_DUPLICATE_CLUSTERS",
                "Module": "DUPLICATE_CLUSTERS",
                "Population": "ALL_INCLUDED",
                "Scenario": "EXCLUDE_CONFIRMED_DUPLICATE_CLUSTERS",
                "Metric": "NOT_ESTIMABLE",
                "Numerator": "",
                "Denominator": len(all_ids),
                "Unknown_Count": len(all_ids),
                "Percent": "",
                "Status": "NOT_RUN",
                "Notes": "No frozen confirmed-duplicate-cluster variable exists in the locked master.",
            },
            {
                "Sensitivity_ID": "SENS_CURRENT_VERSION",
                "Module": "RECORD_HISTORY",
                "Population": "ALL_INCLUDED",
                "Scenario": "CURRENT_VERSION",
                "Metric": "AVAILABLE_CURRENT_RECORDS",
                "Numerator": len(all_ids),
                "Denominator": len(all_ids),
                "Unknown_Count": 0,
                "Percent": 100.0,
                "Status": RECORD_HISTORY_EXECUTION_STATUS,
                "Notes": (
                    "Fixed acquisition-window current official JSON is the primary input; "
                    "this row does not execute the conditional Record History module."
                ),
            },
            {
                "Sensitivity_ID": "SENS_HISTORICAL_VERSION",
                "Module": "RECORD_HISTORY",
                "Population": "ALL_INCLUDED",
                "Scenario": "HISTORICAL_VERSION",
                "Metric": "NOT_ESTIMABLE",
                "Numerator": "",
                "Denominator": len(all_ids),
                "Unknown_Count": len(all_ids),
                "Percent": "",
                "Status": RECORD_HISTORY_EXECUTION_STATUS,
                "Notes": (
                    "No official version-level Record History dataset was frozen; "
                    "the conditional module was not executed."
                ),
            },
        ]
    )
    return rows


def extract_actual_age_categories(
    documents: dict[str, dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    extracted: list[dict[str, Any]] = []
    records_with_results = 0
    records_with_age_categories = 0
    records_with_explicit_older_category = 0
    for nct_id, document in sorted(documents.items()):
        results = document.get("resultsSection", {})
        if not results:
            continue
        records_with_results += 1
        baseline = results.get("baselineCharacteristicsModule", {}) or {}
        groups = baseline.get("groups", []) or []
        total_group_ids = {
            str(group.get("id"))
            for group in groups
            if isinstance(group, dict) and str(group.get("title", "")).strip().lower() == "total"
        }
        measures = baseline.get("measures", []) or []
        record_has_age = False
        record_has_older = False
        for measure_index, measure in enumerate(measures):
            title = str(measure.get("title") or "")
            if "age" not in title.lower() or measure.get("paramType") != "COUNT_OF_PARTICIPANTS":
                continue
            record_has_age = True
            for class_index, class_row in enumerate(measure.get("classes", []) or []):
                for category_index, category in enumerate(class_row.get("categories", []) or []):
                    category_title = str(category.get("title") or "NOT_PUBLICLY_SPECIFIED")
                    if re.search(r"(>=?\s*65|65\s*(years|and older|or older)|elder)", category_title, re.I):
                        record_has_older = True
                    measurements = category.get("measurements", []) or []
                    selected = [
                        item
                        for item in measurements
                        if str(item.get("groupId")) in total_group_ids
                    ]
                    if not selected and len(measurements) == 1:
                        selected = measurements
                    for measurement in selected:
                        value = safe_float(str(measurement.get("value", "")))
                        if value is None:
                            continue
                        extracted.append(
                            {
                                "NCT_ID": nct_id,
                                "Measure_Title": title,
                                "Category": category_title,
                                "Participant_Count": value,
                                "Selected_Group_ID": str(measurement.get("groupId") or ""),
                                "Unit": str(measure.get("unitOfMeasure") or "Participants"),
                                "JSON_Pointer": (
                                    "/resultsSection/baselineCharacteristicsModule/measures/"
                                    f"{measure_index}/classes/{class_index}/categories/{category_index}"
                                ),
                            }
                        )
        records_with_age_categories += int(record_has_age)
        records_with_explicit_older_category += int(record_has_older)
    summary = [
        {
            "Conditional_Module": "ACTUAL_AGE_CATEGORIES",
            "Status": "RUN",
            "Records_With_Results": records_with_results,
            "Records_With_Interpretable_Age_Categories": records_with_age_categories,
            "Records_With_Explicit_Older_Category": records_with_explicit_older_category,
            "Extracted_Category_Rows": len(extracted),
            "Denominator": len(documents),
            "Unknown_Count": len(documents) - records_with_age_categories,
            "Notes": "Exact registered categories only; no threshold is inferred from a mean.",
        }
    ]
    return extracted, summary


def make_denominator_audit(
    long_rows: Sequence[dict[str, Any]],
    tables: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    audit: list[dict[str, Any]] = []
    for row in long_rows:
        numerator = safe_float(str(row.get("numerator", "")))
        denominator = safe_float(str(row.get("denominator", "")))
        unknown = safe_float(str(row.get("unknown_count", "")))
        percentage = safe_float(str(row.get("percentage", "")))
        checks: list[bool] = []
        if numerator is not None and denominator is not None:
            checks.append(0 <= numerator <= denominator)
        if unknown is not None and denominator is not None:
            checks.append(0 <= unknown <= denominator)
        if numerator is not None and denominator not in {None, 0} and percentage is not None:
            checks.append(abs(percentage - numerator * 100 / denominator) < 1e-5)
        audit.append(
            {
                "Audit_ID": f"DEN_{row['result_id']}",
                "Object": row["result_id"],
                "Source": row["source_table"],
                "Numerator": row["numerator"],
                "Denominator": row["denominator"],
                "Unknown_Count": row["unknown_count"],
                "Percentage": row["percentage"],
                "Status": "PASS" if all(checks) else "FAIL",
                "Rule": "0<=numerator<=denominator; 0<=unknown<=denominator; percentage reconciles",
            }
        )
    grouped_rules: list[tuple[str, tuple[str, ...], str, str, str]] = [
        (
            "T02_AGE_ELIGIBILITY_THRESHOLDS.csv",
            ("Age_Scale", "Threshold_Years"),
            "Count",
            "Total_Denominator",
            "age categories sum to the frozen denominator",
        ),
        (
            "T05_GERIATRIC_DOMAIN_CODES.csv",
            ("Domain_ID",),
            "Count",
            "Denominator",
            "geriatric categories sum to the frozen denominator",
        ),
        (
            "T06_GERIATRIC_COMPOSITES.csv",
            ("Composite",),
            "Count",
            "Denominator",
            "composite categories sum to the frozen denominator",
        ),
        (
            "T11_TRIAL_CHARACTERISTICS.csv",
            ("Population", "Dimension"),
            "Count",
            "Denominator",
            "characteristic categories sum to each population denominator",
        ),
    ]
    sequence = len(audit) + 1
    for table_name, keys, count_field, denominator_field, rule in grouped_rules:
        grouped: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
        for row in tables.get(table_name, []):
            grouped[tuple(str(row.get(key, "")) for key in keys)].append(row)
        for key, rows in sorted(grouped.items()):
            count_sum = sum(int(float(row[count_field])) for row in rows)
            denominators = {int(float(row[denominator_field])) for row in rows}
            status = len(denominators) == 1 and count_sum == next(iter(denominators))
            audit.append(
                {
                    "Audit_ID": f"DEN_GROUP_{sequence:05d}",
                    "Object": f"{table_name}:{'|'.join(key)}",
                    "Source": table_name,
                    "Numerator": count_sum,
                    "Denominator": next(iter(denominators)) if len(denominators) == 1 else "",
                    "Unknown_Count": "",
                    "Percentage": "",
                    "Status": "PASS" if status else "FAIL",
                    "Rule": rule,
                }
            )
            sequence += 1
    for table_name in ("T07_COREVEN_COVERAGE.csv", "T08_OUTPUTS_COVERAGE.csv"):
        for row in tables.get(table_name, []):
            total = int(row["Present_N"]) + int(row["Absent_N"]) + int(row["Unknown_Count"])
            denominator = int(row["Denominator"])
            audit.append(
                {
                    "Audit_ID": f"DEN_GROUP_{sequence:05d}",
                    "Object": (
                        f"{table_name}:{row['Coverage_Window']}:{row['Domain']}"
                    ),
                    "Source": table_name,
                    "Numerator": total,
                    "Denominator": denominator,
                    "Unknown_Count": row["Unknown_Count"],
                    "Percentage": row["Percent_Total"],
                    "Status": "PASS" if total == denominator else "FAIL",
                    "Rule": "present + absent + unknown equals framework denominator",
                }
            )
            sequence += 1
    return audit


def write_figures(
    figures_dir: Path,
    tables: dict[str, list[dict[str, Any]]],
) -> dict[str, list[dict[str, Any]]]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    figure_data: dict[str, list[dict[str, Any]]] = {}
    age_rows = [
        row
        for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
        if row["Category"] == "YES"
        and row["Age_Scale"] in {"STRUCTURED", "RECONCILED"}
    ]
    labels = ["65", "75", "80", "85"]
    structured = [
        float(
            next(
                row["Percent_Total"]
                for row in age_rows
                if row["Age_Scale"] == "STRUCTURED" and int(row["Threshold_Years"]) == threshold
            )
        )
        for threshold in (65, 75, 80, 85)
    ]
    reconciled = [
        float(
            next(
                row["Percent_Total"]
                for row in age_rows
                if row["Age_Scale"] == "RECONCILED" and int(row["Threshold_Years"]) == threshold
            )
        )
        for threshold in (65, 75, 80, 85)
    ]
    figure_data["F01_AGE_ELIGIBILITY_LADDER_DATA.csv"] = age_rows
    svg_bar_chart(
        figures_dir / "F01_AGE_ELIGIBILITY_LADDER.svg",
        "Age eligibility ladder",
        "YES among 1,206 included records; unknown counts are retained in the source table.",
        labels,
        [
            ("Structured", structured, "#0052cc"),
            ("Reconciled", reconciled, "#36b37e"),
        ],
        "Percent of frozen included records",
    )
    conflict_rows = [
        row
        for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
        if row["Age_Scale"] == "AGE_FIELD_CONFLICT"
    ]
    figure_data["F02_AGE_FIELD_CONFLICT_DATA.csv"] = conflict_rows
    svg_bar_chart(
        figures_dir / "F02_AGE_FIELD_CONFLICT.svg",
        "Structured/free-text age-field conflict",
        "All 1,206 records; expert-decision states remain separate.",
        [str(row["Category"]) for row in conflict_rows],
        [("Records", [float(row["Count"]) for row in conflict_rows], "#ff8b00")],
        "Record count",
    )
    geriatric_rows = tables["T05_GERIATRIC_DOMAIN_CODES.csv"]
    present = []
    unclear = []
    for domain in GERIATRIC_DOMAINS:
        present.append(
            float(
                next(
                    (row["Percent"] for row in geriatric_rows if row["Domain_ID"] == domain and row["Category"] == "PRESENT"),
                    0,
                )
            )
        )
        unclear.append(
            float(
                next(
                    (
                        row["Percent"]
                        for row in geriatric_rows
                        if row["Domain_ID"] == domain
                        and row["Category"] == "REQUIRES_EXPERT_DECISION"
                    ),
                    0,
                )
            )
        )
    figure_data["F03_GERIATRIC_DOMAIN_MATRIX_DATA.csv"] = geriatric_rows
    svg_bar_chart(
        figures_dir / "F03_GERIATRIC_DOMAIN_MATRIX.svg",
        "Frozen geriatric-domain codes",
        "All 1,206 records; not-publicly-specified is retained in the source table.",
        [
            "Frailty",
            "Mobility/ADL",
            "Cognition",
            "Proxy consent",
            "Nutrition",
            "Multimorb.",
            "Prognosis",
            "Caregiver",
            "Polypharm.",
        ],
        [
            ("Present", present, "#6554c0"),
            ("Expert-decision state", unclear, "#ffab00"),
        ],
        "Percent of frozen included records",
    )
    for framework, table_name, figure_name, domains, display_labels in [
        (
            "COREVEN",
            "T07_COREVEN_COVERAGE.csv",
            "F04_COREVEN_COVERAGE",
            COREVEN_DOMAINS,
            ["Healing", "Pain", "Quality of life", "Resource use", "Adverse events"],
        ),
        (
            "OUTPUTS",
            "T08_OUTPUTS_COVERAGE.csv",
            "F05_OUTPUTS_COVERAGE",
            OUTPUTS_DOMAINS,
            ["PI occurrence", "Precursors", "Mobility", "Comfort", "Adherence", "Safety"],
        ),
    ]:
        source_rows = tables[table_name]
        primary = [
            float(
                next(
                    row["Percent_Total"]
                    for row in source_rows
                    if row["Coverage_Window"] == "PRIMARY_ONLY" and row["Domain"] == domain
                )
            )
            for domain in domains
        ]
        any_planned = [
            float(
                next(
                    row["Percent_Total"]
                    for row in source_rows
                    if row["Coverage_Window"] == "ANY_PLANNED" and row["Domain"] == domain
                )
            )
            for domain in domains
        ]
        denominator = source_rows[0]["Denominator"] if source_rows else 0
        unknown_max = max((int(row["Unknown_Count"]) for row in source_rows), default=0)
        figure_data[f"{figure_name}_DATA.csv"] = source_rows
        svg_bar_chart(
            figures_dir / f"{figure_name}.svg",
            f"{framework} domain coverage",
            f"Framework-specific denominator n={denominator}; maximum domain unknown={unknown_max}.",
            display_labels,
            [
                ("Primary outcome", primary, "#0052cc"),
                ("Any planned outcome", any_planned, "#36b37e"),
            ],
            "Percent of applicable records",
        )
    period_rows = [
        row
        for row in tables["T12_STRATIFIED_DESCRIPTIONS.csv"]
        if row["Metric"] in {"FINITE_UPPER_AGE_LIMIT", "ELIGIBLE_85_RECONCILED"}
        and row["Stratum"]
        in {"PERIOD:2008-2016", "PERIOD:2017-2018", "PERIOD:2019-2025"}
    ]
    periods = ["PERIOD:2008-2016", "PERIOD:2017-2018", "PERIOD:2019-2025"]
    figure_data["F06_TEMPORAL_DESCRIPTIONS_DATA.csv"] = period_rows
    svg_bar_chart(
        figures_dir / "F06_TEMPORAL_DESCRIPTIONS.svg",
        "Prespecified temporal descriptions",
        "First-post periods; counts and unknowns for each denominator are in the source data.",
        [period.replace("PERIOD:", "") for period in periods],
        [
            (
                "Finite structured upper limit",
                [
                    float(
                        next(
                            row["Percent_Total"]
                            for row in period_rows
                            if row["Stratum"] == period and row["Metric"] == "FINITE_UPPER_AGE_LIMIT"
                        )
                    )
                    for period in periods
                ],
                "#ff8b00",
            ),
            (
                "Eligible at 85, reconciled",
                [
                    float(
                        next(
                            row["Percent_Total"]
                            for row in period_rows
                            if row["Stratum"] == period and row["Metric"] == "ELIGIBLE_85_RECONCILED"
                        )
                    )
                    for period in periods
                ],
                "#6554c0",
            ),
        ],
        "Percent of records in period",
    )
    for name, rows in figure_data.items():
        write_csv(figures_dir / name, rows)
    return figure_data


def make_role_packages(
    project_root: Path,
    output_root: Path,
    tables_dir: Path,
    figures_dir: Path,
    data_dir: Path,
    reports_dir: Path,
) -> list[Path]:
    review_dir = output_root / "review_packages"
    forms_dir = review_dir / "forms"
    forms_dir.mkdir(parents=True, exist_ok=True)
    common_footer = """

## Human completion fields

- Review status: PENDING_HUMAN_REVIEW
- Reviewer comments:
- Review date:
- Typed-name signature:

No field above has been completed automatically.
"""
    forms = {
        "JIYUE_JIANG_ANALYSIS_IMPLEMENTATION_RECORD.md": (
            "# Corrected 1,218-record Step 13 analysis implementation record\n\n"
            "Assigned human role: Jiyue Jiang / 姜继越\n\n"
            "The attached implementation is deterministic and reads the locked master in read-only mode. "
            "The human analyst must verify execution, exceptions, and denominator reconciliation."
            + common_footer
        ),
        "YU_LI_INDEPENDENT_REPRODUCTION_ATTESTATION.md": (
            "# Corrected 1,218-record Step 13 independent clean-room reproduction\n\n"
            "Assigned independent reviewer: Yu Li / 李煜\n\n"
            "Run the included script from a clean repository checkout, verify the locked input hashes, "
            "and compare every payload hash. Do not rely on the primary execution directory."
            + common_footer
        ),
        "HUI_BI_AGE_GERIATRIC_REVIEW.md": (
            "# Corrected 1,218-record Step 13 age and geriatric-domain review\n\n"
            "Assigned expert: Hui Bi / 毕慧\n\n"
            "Review age denominators, structured/reconciled separation, missing-state preservation, "
            "nine geriatric domains, composites, and the documented context-field limitation."
            + common_footer
        ),
        "HAOJUN_LIANG_WOUND_OUTCOME_REVIEW.md": (
            "# Corrected 1,218-record Step 13 wound and outcome review\n\n"
            "Assigned expert: Haojun Liang / 梁浩君\n\n"
            "Review CoreVen and OUTPUTs separately, primary versus any planned outcomes, framework "
            "denominators, instruments, reporters, time frames, and units of analysis."
            + common_footer
        ),
        "GUOYONG_WANG_FINAL_RESULT_APPROVAL_TEMPLATE.md": (
            "# Corrected 1,218-record Step 13 result/interpretation approval template\n\n"
            "Assigned research lead/PI: Guoyong Wang / 王国勇\n\n"
            "Decision: PENDING_HUMAN_SIGNATURE\n\n"
            "Independent validation must be complete before any final result or interpretation decision."
            + common_footer
        ),
    }
    for name, content in forms.items():
        write_text(forms_dir / name, content.strip() + "\n")
    input_hashes = [
        {
            "Input": "STEP12_CORRECTED_1218_DETAILED_CODING_MASTER.sqlite",
            "SHA256": EXPECTED_HASHES["locked_master"],
        },
        {
            "Input": "07_REVISED_STATISTICAL_ANALYSIS_PLAN_v2.md",
            "SHA256": EXPECTED_HASHES["sap"],
        },
    ]
    write_csv(
        review_dir / "STEP13B_INDEPENDENT_REPRODUCTION_INPUT_HASHES.csv",
        input_hashes,
    )
    reproduction = f"""# Independent reproduction instructions

1. Check out the evidence commit stated in the primary report.
2. Verify the two locked-input hashes in `STEP13B_INDEPENDENT_REPRODUCTION_INPUT_HASHES.csv`.
3. Run:

   `python3 analysis/step_13_corrected_1218/STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py --project-root "{project_root}"`

4. Verify every mandatory QA row is PASS.
5. Compare the regenerated payload SHA ledger with the primary execution.
6. Complete the Yu Li attestation only after an independent clean-room run.

Current independent-validation status: NOT_COMPLETED.
"""
    write_text(review_dir / "INDEPENDENT_REPRODUCTION_INSTRUCTIONS.md", reproduction)
    script = (
        project_root
        / "analysis/step_13_corrected_1218/STEP13_PRIMARY_ANALYSIS_CORRECTED_1218.py"
    )
    report = reports_dir / "STEP13B_PRIMARY_ANALYSIS_REPORT.md"
    tests = reports_dir / "STEP13B_PRIMARY_ANALYSIS_TESTS.txt"
    exceptions = reports_dir / "STEP13B_PRIMARY_ANALYSIS_EXCEPTIONS.csv"
    packages: list[tuple[str, list[Path]]] = [
        (
            "Jiyue_Jiang_Analysis_Implementation_Record.zip",
            [
                forms_dir / "JIYUE_JIANG_ANALYSIS_IMPLEMENTATION_RECORD.md",
                script,
                report,
                tests,
                exceptions,
            ],
        ),
        (
            "Yu_Li_Independent_Clean_Room_Reproduction.zip",
            [
                forms_dir / "YU_LI_INDEPENDENT_REPRODUCTION_ATTESTATION.md",
                review_dir / "INDEPENDENT_REPRODUCTION_INSTRUCTIONS.md",
                review_dir / "STEP13B_INDEPENDENT_REPRODUCTION_INPUT_HASHES.csv",
                script,
                tests,
            ],
        ),
        (
            "Hui_Bi_Age_Geriatric_Review.zip",
            [
                forms_dir / "HUI_BI_AGE_GERIATRIC_REVIEW.md",
                tables_dir / "T02_AGE_ELIGIBILITY_THRESHOLDS.csv",
                tables_dir / "T03_AGE_NUMERIC_SUMMARY.csv",
                tables_dir / "T05_GERIATRIC_DOMAIN_CODES.csv",
                tables_dir / "T06_GERIATRIC_COMPOSITES.csv",
                tables_dir / "T14_RELIABILITY_SUMMARY.csv",
                figures_dir / "F01_AGE_ELIGIBILITY_LADDER.svg",
                figures_dir / "F02_AGE_FIELD_CONFLICT.svg",
                figures_dir / "F03_GERIATRIC_DOMAIN_MATRIX.svg",
                data_dir / "STEP13B_DENOMINATOR_AUDIT.csv",
                exceptions,
            ],
        ),
        (
            "Haojun_Liang_Wound_Outcome_Review.zip",
            [
                forms_dir / "HAOJUN_LIANG_WOUND_OUTCOME_REVIEW.md",
                tables_dir / "T07_COREVEN_COVERAGE.csv",
                tables_dir / "T08_OUTPUTS_COVERAGE.csv",
                tables_dir / "T09_OUTCOME_COVERAGE_SCORES.csv",
                tables_dir / "T10_OUTCOME_CHARACTERISTICS.csv",
                tables_dir / "T14_RELIABILITY_SUMMARY.csv",
                figures_dir / "F04_COREVEN_COVERAGE.svg",
                figures_dir / "F05_OUTPUTS_COVERAGE.svg",
                data_dir / "STEP13B_DENOMINATOR_AUDIT.csv",
                exceptions,
            ],
        ),
        (
            "Guoyong_Wang_Final_Result_Approval_Template.zip",
            [
                forms_dir / "GUOYONG_WANG_FINAL_RESULT_APPROVAL_TEMPLATE.md",
                report,
                tests,
                exceptions,
                data_dir / "STEP13B_DENOMINATOR_AUDIT.csv",
            ],
        ),
    ]
    output_paths = []
    for package_name, files in packages:
        package_path = review_dir / package_name
        deterministic_zip(
            package_path,
            [(path, path.name) for path in files],
        )
        output_paths.append(package_path)
    return output_paths


def inventory_rows(paths: Iterable[Path], project_root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted(set(paths)):
        if path.is_file():
            rows.append(
                {
                    "Relative_Path": path.relative_to(project_root).as_posix(),
                    "Size_Bytes": path.stat().st_size,
                    "SHA256": sha256(path),
                }
            )
    return rows


def collect_analysis_payload(
    project_root: Path, output_dir: Path, report_dir: Path
) -> list[Path]:
    candidates: list[Path] = [
        project_root / "project_state.yaml",
        project_root / "config/stage_permissions.yaml",
        project_root / "risk_register.csv",
        project_root / "AI_USE_LOG.csv",
        project_root / "tests/integration/test_step13_corrected_1218_outputs.py",
        project_root / "tests/integration/test_step08_retrieval_audit.py",
        report_dir / "STEP13B_REPOSITORY_REGRESSION_TESTS.txt",
    ]
    analysis_dir = project_root / "analysis/step_13_corrected_1218"
    for base in (analysis_dir, output_dir):
        if base.exists():
            candidates.extend(path for path in base.rglob("*") if path.is_file())
    if report_dir.exists():
        candidates.extend(
            path
            for path in report_dir.glob("STEP13B_PRIMARY_ANALYSIS*")
            if path.is_file()
        )
        candidates.extend(
            path
            for path in (report_dir / "review_templates").rglob("*")
            if path.is_file()
        ) if (report_dir / "review_templates").exists() else None
    excluded_names = {
        "STEP13B_PRIMARY_ANALYSIS_MANIFEST.csv",
        "STEP13B_PRIMARY_ANALYSIS_SHA256.txt",
        "STEP13B_PAYLOAD_MANIFEST.csv",
        "STEP13B_PAYLOAD_SHA256.txt",
        "Step13B_主分析与独立复核整合包.zip",
    }
    return sorted(
        {
            path
            for path in candidates
            if path.is_file()
            and path.name not in excluded_names
            and "__pycache__" not in path.parts
            and not path.name.endswith(".pyc")
        }
    )


def run(
    project_root: Path,
    output_root_override: Path | None = None,
    reports_dir_override: Path | None = None,
    analytical_input_manifest_override: Path | None = None,
) -> None:
    analytical_input_manifest = (
        analytical_input_manifest_override
        if analytical_input_manifest_override is not None
        else project_root
        / "governance/analysis/step13d_v12r4_r3c/input_freeze/"
        "STEP13D_V12R4_R3C_ANALYTICAL_INPUT_MANIFEST.csv"
    )
    manifested_inputs = load_analytical_input_manifest(
        project_root, analytical_input_manifest
    )
    locked_master = project_root / manifested_inputs["LOCKED_STEP12_MASTER"][0][
        "Relative_Path"
    ]
    sap = project_root / manifested_inputs["FROZEN_SAP"][0]["Relative_Path"]
    screening_path = project_root / manifested_inputs["FROZEN_SCREENING_FRAME"][0][
        "Relative_Path"
    ]
    output_root = (
        output_root_override
        if output_root_override is not None
        else project_root / "outputs/step_13_corrected_1218"
    )
    tables_dir = output_root / "tables"
    figures_dir = output_root / "figures"
    data_dir = output_root / "data"
    qa_dir = output_root / "qa"
    reports_dir = (
        reports_dir_override
        if reports_dir_override is not None
        else project_root / "reports/step_13_corrected_1218"
    )
    for directory in (tables_dir, figures_dir, data_dir, qa_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []
    require(locked_master.exists(), "locked master exists", checks)
    require(sap.exists(), "SAP exists", checks)
    require(
        len(sum(manifested_inputs.values(), [])) == EXPECTED_ANALYTICAL_INPUT_ROWS,
        "analytical input manifest has 1221 verified rows",
        checks,
    )
    require(sha256(locked_master) == EXPECTED_HASHES["locked_master"], "locked master hash", checks)
    require(sha256(sap) == EXPECTED_HASHES["sap"], "SAP hash", checks)
    connection = sqlite3.connect(f"file:{locked_master}?mode=ro", uri=True)
    try:
        age_rows = load_table(connection, "age")
        geriatric_rows = load_table(connection, "geriatric")
        framework_rows = load_table(connection, "framework")
        outcome_rows = load_table(connection, "outcome")
        qa_metadata = dict(connection.execute("SELECT key, value FROM qa_metadata"))
    finally:
        connection.close()
    screening = read_csv(screening_path)
    included_screening = [
        row for row in screening if row["Final_Adjudicated_Eligibility"] == "INCLUDE"
    ]
    screening_by_nct = {row["NCT_ID"]: row for row in included_screening}
    included_ids = set(screening_by_nct)
    framework_ids = {row["NCT_ID"] for row in framework_rows}
    geriatric_ids = {row["NCT_ID"] for row in geriatric_rows}
    age_ids = {row["NCT_ID"] for row in age_rows}
    require(len(included_ids) == EXPECTED["included_nct"], "included NCT count is 1218", checks)
    require(len(age_rows) == EXPECTED["trial_age"], "age field rows are 18270", checks)
    require(len(geriatric_rows) == EXPECTED["geriatric_domains"], "geriatric rows are 10962", checks)
    require(len(framework_rows) == EXPECTED["frameworks"], "framework rows are 1218", checks)
    require(len(outcome_rows) == EXPECTED["outcomes"], "outcome rows are 7633", checks)
    require(
        qa_metadata.get("prohibited_unresolved_pi_final_values") == str(EXPECTED["unresolved"]),
        "unresolved final values are zero",
        checks,
    )
    require(
        qa_metadata.get("included_nct_ids") == "1218",
        "frozen master records 1218 included NCT IDs",
        checks,
    )
    require(
        included_ids == framework_ids == geriatric_ids == age_ids,
        "included NCT sets match all frozen trial-level tables",
        checks,
    )
    outcome_ids = [row["Outcome_ID"] for row in outcome_rows]
    require(len(outcome_ids) == len(set(outcome_ids)), "outcome row IDs are unique", checks)
    require(
        {row["NCT_ID"] for row in outcome_rows} <= included_ids,
        "all outcome rows belong to included NCT IDs",
        checks,
    )
    raw_paths: dict[str, tuple[Path, str]] = {}
    manifested_raw = {
        row["Relative_Path"]: row["SHA256"]
        for row in manifested_inputs["OFFICIAL_JSON_ANALYTICAL_INPUT"]
    }
    for row in framework_rows:
        nct_id = row["NCT_ID"]
        raw_path = project_root / row["Raw_JSON_Path"]
        raw_hash = row["Raw_JSON_SHA256"]
        if manifested_raw.get(row["Raw_JSON_Path"]) != raw_hash:
            raise RuntimeError(f"raw JSON is not explicitly manifested: {nct_id}")
        raw_paths[nct_id] = (raw_path, raw_hash)
    documents: dict[str, dict[str, Any]] = {}
    raw_hash_failures: list[dict[str, str]] = []
    for nct_id, (path, expected_hash) in sorted(raw_paths.items()):
        if not path.exists():
            raw_hash_failures.append(
                {"NCT_ID": nct_id, "Raw_JSON_Path": str(path), "Issue": "MISSING"}
            )
            continue
        observed_hash = sha256(path)
        if observed_hash != expected_hash:
            raw_hash_failures.append(
                {
                    "NCT_ID": nct_id,
                    "Raw_JSON_Path": str(path),
                    "Issue": "HASH_MISMATCH",
                }
            )
            continue
        with path.open("r", encoding="utf-8") as handle:
            documents[nct_id] = json.load(handle)
    write_csv(
        qa_dir / "STEP13B_RAW_JSON_HASH_EXCEPTIONS.csv",
        raw_hash_failures,
        ["NCT_ID", "Raw_JSON_Path", "Issue"],
    )
    require(not raw_hash_failures, "all raw JSON hashes match", checks)
    require(len(documents) == EXPECTED["json_coverage"], "full JSON hash coverage is 1218/1218", checks)
    metadata = {
        nct_id: extract_trial_metadata(nct_id, document)
        for nct_id, document in documents.items()
    }
    for nct_id, row in metadata.items():
        row["Disease_Intent_Group"] = screening_by_nct[nct_id][
            "Final_Disease_Intent_Group"
        ]
        row["Human_Frozen_Adult_Scope"] = screening_by_nct[nct_id][
            "Final_Adult_Pediatric_Scope"
        ]
    framework_by_nct = {row["NCT_ID"]: row["Final_Framework"] for row in framework_rows}
    population_sets = build_population_sets(metadata, screening_by_nct, framework_by_nct)
    age_tables, age_long, age_by_nct, age_sensitivity = build_age_outputs(age_rows, included_ids)
    age_tables["T04_AGE_FIELD_CONFLICT_AND_UPPER_LIMIT.csv"] = [
        row
        for row in age_tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
        if row["Age_Scale"] in {"STRUCTURED_UPPER_AGE_STATUS", "AGE_FIELD_CONFLICT"}
    ]
    geriatric_tables, geriatric_long, geriatric_by_nct = build_geriatric_outputs(
        geriatric_rows, included_ids
    )
    outcome_tables, outcome_long, _ = build_outcome_outputs(
        outcome_rows, framework_rows, included_ids
    )
    characteristic_tables, characteristic_long = build_characteristic_outputs(
        metadata,
        population_sets,
        age_by_nct,
        geriatric_by_nct,
        screening_by_nct,
    )
    reliability_rows, reliability_long = build_corrected_reliability_outputs(
        age_rows, geriatric_rows, framework_rows, outcome_rows
    )
    sensitivity_rows = build_sensitivity_outputs(
        age_sensitivity,
        metadata,
        population_sets,
        age_rows,
        age_by_nct,
        geriatric_rows,
        geriatric_by_nct,
        screening_by_nct,
        outcome_rows,
        framework_by_nct,
    )
    actual_age_rows, conditional_rows = extract_actual_age_categories(documents)
    protocol_inputs = manifested_inputs.get("PROTOCOL_SAP_CONDITIONAL_INPUT", [])
    record_history_inputs = manifested_inputs.get(
        "RECORD_HISTORY_VERSION_ANALYTICAL_INPUT", []
    )
    conditional_rows.extend(
        [
            {
                "Conditional_Module": "PROTOCOL_SAP_VALIDATION",
                "Status": "RUN" if len(protocol_inputs) >= 30 else "NOT_RUN",
                "Records_With_Results": "",
                "Records_With_Interpretable_Age_Categories": "",
                "Records_With_Explicit_Older_Category": "",
                "Extracted_Category_Rows": len(protocol_inputs),
                "Denominator": 30,
                "Unknown_Count": max(0, 30 - len(protocol_inputs)),
                "Notes": (
                    "Prerequisite passed."
                    if len(protocol_inputs) >= 30
                    else "Fewer than 30 protocol/SAP files are explicitly frozen in the analytical input manifest."
                ),
            },
            {
                "Conditional_Module": "RECORD_HISTORY_AUDIT",
                "Status": RECORD_HISTORY_EXECUTION_STATUS,
                "Records_With_Results": "",
                "Records_With_Interpretable_Age_Categories": "",
                "Records_With_Explicit_Older_Category": "",
                "Extracted_Category_Rows": len(record_history_inputs),
                "Denominator": len(included_ids),
                "Unknown_Count": len(included_ids),
                "Notes": (
                    "No version-level official history dataset was frozen. The guide is "
                    "supporting audit only and does not enter analytical inputs."
                ),
            },
        ]
    )
    for row in conditional_rows:
        row.setdefault("Execution_Status", "")
        row.setdefault("Aims_Disposition", "")
        row.setdefault("Reason_Code", "")
        row.setdefault("Official_Version_Data_Coverage", "")
        row.setdefault("Guide_Document_Classification", "")
        row.setdefault("Current_Analysis_Impact", "")
        row.setdefault("Future_Amendment_Required", "")
        if row["Conditional_Module"] == "RECORD_HISTORY_AUDIT":
            row.update(
                {
                    "Execution_Status": RECORD_HISTORY_EXECUTION_STATUS,
                    "Aims_Disposition": RECORD_HISTORY_AIMS_DISPOSITION,
                    "Reason_Code": RECORD_HISTORY_REASON_CODE,
                    "Official_Version_Data_Coverage": "0/1218",
                    "Guide_Document_Classification": (
                        RECORD_HISTORY_GUIDE_CLASSIFICATION
                    ),
                    "Current_Analysis_Impact": "NONE",
                    "Future_Amendment_Required": "YES",
                }
            )
    flow_rows = [
        {
            "QA_Object": "FINAL_INCLUDED_NCT_IDS",
            "Observed": len(included_ids),
            "Expected": 1218,
            "Status": "PASS",
            "Unknown_Count": 0,
        },
        {
            "QA_Object": "FULL_JSON_HASH_COVERAGE",
            "Observed": len(documents),
            "Expected": 1218,
            "Status": "PASS",
            "Unknown_Count": 0,
        },
        {
            "QA_Object": "AGE_FIELD_ROWS",
            "Observed": len(age_rows),
            "Expected": 18270,
            "Status": "PASS",
            "Unknown_Count": 0,
        },
        {
            "QA_Object": "GERIATRIC_DOMAIN_ROWS",
            "Observed": len(geriatric_rows),
            "Expected": 10962,
            "Status": "PASS",
            "Unknown_Count": 0,
        },
        {
            "QA_Object": "FRAMEWORK_ROWS",
            "Observed": len(framework_rows),
            "Expected": 1218,
            "Status": "PASS",
            "Unknown_Count": 0,
        },
        {
            "QA_Object": "OUTCOME_ROWS",
            "Observed": len(outcome_rows),
            "Expected": 7633,
            "Status": "PASS",
            "Unknown_Count": 0,
        },
        {
            "QA_Object": "UNRESOLVED_FINAL_VALUES",
            "Observed": int(qa_metadata["prohibited_unresolved_pi_final_values"]),
            "Expected": 0,
            "Status": "PASS",
            "Unknown_Count": 0,
        },
    ]
    tables: dict[str, list[dict[str, Any]]] = {
        "T01_FLOW_AND_INPUT_QA.csv": flow_rows,
        **age_tables,
        **geriatric_tables,
        **outcome_tables,
        **characteristic_tables,
        "T14_RELIABILITY_SUMMARY.csv": reliability_rows,
        "T15_CONDITIONAL_MODULE_STATUS.csv": conditional_rows,
    }
    for name, rows in tables.items():
        write_csv(tables_dir / name, rows)
    write_csv(data_dir / "STEP13B_SENSITIVITY_RESULTS.csv", sensitivity_rows)
    write_csv(data_dir / "STEP13B_ACTUAL_AGE_CATEGORY_DATA.csv", actual_age_rows)
    trial_data_fields = [
        "NCT_ID",
        "Disease_Intent_Group",
        "Human_Frozen_Adult_Scope",
        "Study_Type",
        "Allocation",
        "Intervention_Model",
        "Randomized",
        "Comparative",
        "Industry_Role",
        "Device_Study",
        "Intervention_Types",
        "Country_Scope",
        "Country_Count",
        "US_Center",
        "Registration_Timing",
        "Overall_Status",
        "Enrollment_Count",
        "Withdrawn_Zero_Enrollment",
        "Completed",
        "Study_First_Post_Date",
        "Study_First_Post_Year",
        "Period",
        "Study_Start_Date",
        "Study_First_Submit_Date",
        "Std_Ages",
        "Adult_Relevant_Registry",
        "Has_Results",
    ]
    write_csv(
        data_dir / "STEP13B_TRIAL_ANALYSIS_DATA.csv",
        [metadata[nct_id] for nct_id in sorted(metadata)],
        trial_data_fields,
    )
    long_rows = age_long + geriatric_long + outcome_long + characteristic_long + reliability_long
    write_csv(data_dir / "STEP13B_ANALYSIS_RESULTS_LONG.csv", long_rows)
    figure_data = write_figures(figures_dir, tables)
    denominator_audit = make_denominator_audit(long_rows, tables)
    write_csv(data_dir / "STEP13B_DENOMINATOR_AUDIT.csv", denominator_audit)
    require(
        all(row["Status"] == "PASS" for row in denominator_audit),
        "denominator audit passes",
        checks,
    )
    figure_reconciliation = []
    for file_name, rows in figure_data.items():
        expected_rows: Sequence[dict[str, Any]]
        if file_name == "F01_AGE_ELIGIBILITY_LADDER_DATA.csv":
            expected_rows = [
                row
                for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
                if row["Category"] == "YES"
                and row["Age_Scale"] in {"STRUCTURED", "RECONCILED"}
            ]
        elif file_name == "F02_AGE_FIELD_CONFLICT_DATA.csv":
            expected_rows = [
                row
                for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
                if row["Age_Scale"] == "AGE_FIELD_CONFLICT"
            ]
        elif file_name == "F03_GERIATRIC_DOMAIN_MATRIX_DATA.csv":
            expected_rows = tables["T05_GERIATRIC_DOMAIN_CODES.csv"]
        elif file_name == "F04_COREVEN_COVERAGE_DATA.csv":
            expected_rows = tables["T07_COREVEN_COVERAGE.csv"]
        elif file_name == "F05_OUTPUTS_COVERAGE_DATA.csv":
            expected_rows = tables["T08_OUTPUTS_COVERAGE.csv"]
        else:
            expected_rows = [
                row
                for row in tables["T12_STRATIFIED_DESCRIPTIONS.csv"]
                if row["Metric"] in {"FINITE_UPPER_AGE_LIMIT", "ELIGIBLE_85_RECONCILED"}
                and row["Stratum"]
                in {"PERIOD:2008-2016", "PERIOD:2017-2018", "PERIOD:2019-2025"}
            ]
        status = rows == list(expected_rows)
        figure_reconciliation.append(
            {
                "Figure_Data_File": file_name,
                "Rows": len(rows),
                "Source_Rows": len(expected_rows),
                "Status": "PASS" if status else "FAIL",
            }
        )
    write_csv(qa_dir / "STEP13B_TABLE_FIGURE_RECONCILIATION.csv", figure_reconciliation)
    require(
        all(row["Status"] == "PASS" for row in figure_reconciliation),
        "table and figure data reconcile",
        checks,
    )
    contact_exceptions: list[dict[str, str]] = []
    email_re = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
    phone_re = re.compile(r"\b(?:tel(?:ephone)?|phone|fax)\s*[:=]\s*\+?[\d() .-]{7,}", re.I)
    for path in sorted(list(tables_dir.glob("*.csv")) + list(data_dir.glob("*.csv"))):
        text = path.read_text(encoding="utf-8")
        header = text.splitlines()[0] if text else ""
        if CONTACT_KEY_RE.search(header) or email_re.search(text) or phone_re.search(text):
            contact_exceptions.append(
                {
                    "File": path.relative_to(project_root).as_posix(),
                    "Issue": "CONTACT_FIELD_OR_VALUE_DETECTED",
                }
            )
    write_csv(
        qa_dir / "STEP13B_CONTACT_FIELD_SCAN.csv",
        contact_exceptions,
        ["File", "Issue"],
    )
    require(not contact_exceptions, "processed outputs contain no contact fields or values", checks)
    require(
        {row["Framework"] for row in tables["T07_COREVEN_COVERAGE.csv"]} == {"COREVEN"}
        and {row["Framework"] for row in tables["T08_OUTPUTS_COVERAGE.csv"]} == {"OUTPUTS"},
        "VLU and PI outcome frameworks remain separate",
        checks,
    )
    require(
        any(
            row["Category"] == "NOT_PUBLICLY_SPECIFIED"
            for row in tables["T05_GERIATRIC_DOMAIN_CODES.csv"]
        )
        and any(
            row["Category"] == "UNKNOWN"
            for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
        )
        and any(
            row["Category"] == "NO_EXPLICIT_STRUCTURED_UPPER_LIMIT"
            for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
        ),
        "missing-state categories remain separate",
        checks,
    )
    exceptions = [
        {
            "Exception_ID": "EXC13B-001",
            "Severity": "MODERATE",
            "Module": "GERIATRIC_CONTEXT",
            "Status": "PRESPECIFIED_NOT_ESTIMABLE_FROM_FROZEN_MASTER",
            "Description": (
                "The frozen master provides one final code per domain but no separate facilitating, "
                "restriction, assessment, outcome, or stratification context fields."
            ),
            "Action": "Report domain-level codes and composites only; no new text coding was performed.",
        },
        {
            "Exception_ID": "EXC13B-002",
            "Severity": "MODERATE",
            "Module": "RECORD_HISTORY",
            "Status": RECORD_HISTORY_EXECUTION_STATUS,
            "Description": (
                "No official version-level Record History dataset was frozen; "
                "the guide is supporting audit only and non-analytic."
            ),
            "Action": (
                "Remove Record History from current aims and result claims; "
                "a future governed amendment is required."
            ),
        },
        {
            "Exception_ID": "EXC13B-003",
            "Severity": "MODERATE",
            "Module": "PROTOCOL_SAP_VALIDATION",
            "Status": "CONDITIONAL_PREREQUISITE_NOT_MET",
            "Description": f"Only {len(protocol_inputs)} protocol/SAP files were explicitly manifested; 30 are required.",
            "Action": "Conditional validation was not run.",
        },
        {
            "Exception_ID": "EXC13B-004",
            "Severity": "INFORMATIONAL",
            "Module": "DUPLICATE_CLUSTER_SENSITIVITY",
            "Status": "PRESPECIFIED_NOT_ESTIMABLE_FROM_FROZEN_MASTER",
            "Description": "No confirmed duplicate-cluster variable exists in the locked master.",
            "Action": "No record was removed or relabeled.",
        },
        {
            "Exception_ID": "EXC13B-005",
            "Severity": "INFORMATIONAL",
            "Module": "ADULT_POPULATION",
            "Status": "DUAL_OPERATIONALIZATION_REPORTED",
            "Description": (
                "The human-frozen adult-scope field contains many UNKNOWN values; registry stdAges supplies "
                "an independent explicit adult-relevant operationalization."
            ),
            "Action": "Both denominators are reported separately; neither is silently substituted.",
        },
        {
            "Exception_ID": "EXC13B-006",
            "Severity": "INFORMATIONAL",
            "Module": "OUTCOME_SOURCE",
            "Status": "PLANNED_OUTCOMES_ONLY",
            "Description": "All 7,633 frozen outcome rows are planned outcomes from frozen registry records.",
            "Action": "Coverage is labeled planned outcome coverage and not reported-results coverage.",
        },
    ]
    write_csv(reports_dir / "STEP13B_PRIMARY_ANALYSIS_EXCEPTIONS.csv", exceptions)
    key_age = next(
        row
        for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
        if row["Age_Scale"] == "STRUCTURED_UPPER_AGE_STATUS"
        and row["Category"] == "FINITE_UPPER_LIMIT"
    )
    key_age85 = next(
        row
        for row in tables["T02_AGE_ELIGIBILITY_THRESHOLDS.csv"]
        if row["Age_Scale"] == "RECONCILED"
        and int(row["Threshold_Years"]) == 85
        and row["Category"] == "YES"
    )
    key_geriatric = next(
        row
        for row in tables["T06_GERIATRIC_COMPOSITES.csv"]
        if row["Composite"] == "PRIMARY_EIGHT_DOMAIN_ANY_PRESENT"
        and row["Category"] == "YES"
    )
    coreven_all = next(
        row
        for row in tables["T09_OUTCOME_COVERAGE_SCORES.csv"]
        if row["Framework"] == "COREVEN"
        and row["Coverage_Window"] == "ANY_PLANNED"
        and row["Metric"] == "ALL_DOMAINS_PRESENT"
        and row["Category"] == "YES"
    )
    outputs_all = next(
        row
        for row in tables["T09_OUTCOME_COVERAGE_SCORES.csv"]
        if row["Framework"] == "OUTPUTS"
        and row["Coverage_Window"] == "ANY_PLANNED"
        and row["Metric"] == "ALL_DOMAINS_PRESENT"
        and row["Category"] == "YES"
    )
    output_relative = output_root.relative_to(project_root).as_posix()
    report = f"""# Corrected 1,218-record Step 13 prespecified primary analysis report

Status: `PRIMARY_ANALYSIS_COMPLETED_PENDING_INDEPENDENT_VALIDATION`

Execution date: {EXECUTION_DATE}

## Scope and statistical position

This is a descriptive audit of the complete frozen population. The implementation reports observed
counts, denominators, percentages, unknown counts, medians, interquartile ranges, ranges, and
prespecified absolute percentage-point differences. It makes no final interpretation.

## Locked-input conservation

- Included NCT IDs: {len(included_ids)}/1,218
- Complete official JSON with matching hash: {len(documents)}/1,218
- Age rows: {len(age_rows)}/18,270
- Geriatric-domain rows: {len(geriatric_rows)}/10,962
- Framework rows: {len(framework_rows)}/1,218
- Planned outcome rows: {len(outcome_rows)}/7,633
- Unresolved final values: {qa_metadata['prohibited_unresolved_pi_final_values']}
- Duplicate outcome IDs: 0

## Prespecified descriptive checkpoints

- Explicit finite structured upper-age limit: {key_age['Count']}/{key_age['Total_Denominator']}
  ({key_age['Percent_Total']:.2f}%); unknown={key_age['Unknown_Count']}.
- Reconciled eligibility at age 85, YES: {key_age85['Count']}/{key_age85['Total_Denominator']}
  ({key_age85['Percent_Total']:.2f}%); unknown={key_age85['Unknown_Count']}.
- Any of the eight primary geriatric domains PRESENT: {key_geriatric['Count']}/{key_geriatric['Denominator']}
  ({key_geriatric['Percent']:.2f}%); unknown={key_geriatric['Unknown_Count']}.
- CoreVen all five domains covered by any planned outcome: {coreven_all['Count']}/{coreven_all['Denominator']}
  ({coreven_all['Percent']:.2f}%); unknown={coreven_all['Unknown_Count']}.
- OUTPUTs all six domains covered by any planned outcome: {outputs_all['Count']}/{outputs_all['Denominator']}
  ({outputs_all['Percent']:.2f}%); unknown={outputs_all['Unknown_Count']}.

These checkpoints are navigation aids to the populated tables, not final interpretation. CoreVen and
OUTPUTs use separate populations and are never combined into one score.

## Outputs

- 15 populated prespecified tables in `{output_relative}/tables/`
- 6 SVG figures with source-data CSV files in `{output_relative}/figures/`
- Long-format results, denominator audit, sensitivity results, minimized trial characteristics,
  and exact registered actual-age category rows in `{output_relative}/data/`
- Historical 1,206-record reliability summaries plus separately labeled new-record cross-scale workflow QC
- Five role-specific packages with all review, date, and signature fields blank

## Conditional modules and exceptions

The registered-results actual-age category module ran because explicit categorical distributions were
available. It preserves exact registered labels and never derives an older-age threshold from a mean.
The protocol/SAP prerequisite did not pass. Record History was not executed because no version-level
official history dataset was frozen; the guide is supporting audit only and non-analytic. The frozen master also does not
contain separate geriatric-context fields or a confirmed duplicate-cluster variable. These limitations
are preserved in `STEP13B_PRIMARY_ANALYSIS_EXCEPTIONS.csv`; no new coding was invented.

## Internal QA

All mandatory row-count, source-hash, unique-key, denominator, missing-state, contact-minimization,
framework-separation, and table/figure reconciliation checks passed. Independent clean-room validation
has not been performed. Final result interpretation, manuscript result finalization, and submission
preparation remain unauthorized.

## Hash-ledger convention

The payload ledger covers every payload file and the delivery bundle. A ledger cannot contain its own
stable digest; this self-exclusion is explicit and does not omit any analytic payload.
"""
    write_text(reports_dir / "STEP13B_PRIMARY_ANALYSIS_REPORT.md", report)
    tests_text = "\n".join(
        [
            "STEP13B PRIMARY ANALYSIS QA",
            f"execution_timestamp_utc={EXECUTION_TIMESTAMP_UTC}",
            *(f"{index:03d} {row['status']} {row['check']}" for index, row in enumerate(checks, 1)),
            f"checks_total={len(checks)}",
            f"checks_passed={sum(row['status'] == 'PASS' for row in checks)}",
            f"checks_failed={sum(row['status'] == 'FAIL' for row in checks)}",
            "PROHIBITED_INFERENCE_FOUND=NO",
            "INDEPENDENT_VALIDATION_COMPLETED=NO",
            "exit_code=0",
            "",
        ]
    )
    write_text(reports_dir / "STEP13B_PRIMARY_ANALYSIS_TESTS.txt", tests_text)
    completion_state = {
        "current_step": "13D-v12R4-R2",
        "current_step_status": "CORRECTED_STEP13_PRIMARY_RERUN_COMPLETE_PENDING_INDEPENDENT_VALIDATION",
        "primary_analysis_allowed": False,
        "primary_results_calculated": True,
        "independent_validation_completed": False,
        "final_interpretation_authorized": False,
        "manuscript_results_finalized": False,
        "included_nct_count": len(included_ids),
        "full_json_hash_coverage": f"{len(documents)}/1218",
        "execution_timestamp_utc": EXECUTION_TIMESTAMP_UTC,
    }
    write_text(
        qa_dir / "STEP13B_COMPLETION_STATE.json",
        json.dumps(completion_state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
    )
    make_role_packages(
        project_root,
        output_root,
        tables_dir,
        figures_dir,
        data_dir,
        reports_dir,
    )
    generated_text_files = (
        list(tables_dir.glob("*.csv"))
        + list(figures_dir.glob("*.csv"))
        + list(figures_dir.glob("*.svg"))
        + list(data_dir.glob("*.csv"))
        + [
            reports_dir / "STEP13B_PRIMARY_ANALYSIS_REPORT.md",
            reports_dir / "STEP13B_PRIMARY_ANALYSIS_TESTS.txt",
            reports_dir / "STEP13B_PRIMARY_ANALYSIS_EXCEPTIONS.csv",
        ]
    )
    prohibited_hits = []
    for path in generated_text_files:
        text = path.read_text(encoding="utf-8")
        for pattern in PROHIBITED_OUTPUT_PATTERNS:
            if pattern.search(text):
                prohibited_hits.append(
                    {
                        "File": path.relative_to(project_root).as_posix(),
                        "Pattern": pattern.pattern,
                    }
                )
    write_csv(
        qa_dir / "STEP13B_PROHIBITED_INFERENCE_SCAN.csv",
        prohibited_hits,
        ["File", "Pattern"],
    )
    require(not prohibited_hits, "no prohibited inferential output found", checks)
    # Re-write the tests file after the final internal scan.
    tests_text = "\n".join(
        [
            "STEP13B PRIMARY ANALYSIS QA",
            f"execution_timestamp_utc={EXECUTION_TIMESTAMP_UTC}",
            *(f"{index:03d} {row['status']} {row['check']}" for index, row in enumerate(checks, 1)),
            f"checks_total={len(checks)}",
            f"checks_passed={sum(row['status'] == 'PASS' for row in checks)}",
            f"checks_failed={sum(row['status'] == 'FAIL' for row in checks)}",
            "PROHIBITED_INFERENCE_FOUND=NO",
            "INDEPENDENT_VALIDATION_COMPLETED=NO",
            "exit_code=0",
            "",
        ]
    )
    write_text(reports_dir / "STEP13B_PRIMARY_ANALYSIS_TESTS.txt", tests_text)
    # Rebuild role packages so their test evidence is the final evidence.
    make_role_packages(
        project_root,
        output_root,
        tables_dir,
        figures_dir,
        data_dir,
        reports_dir,
    )
    payload_files = collect_analysis_payload(project_root, output_root, reports_dir)
    payload_manifest_rows = inventory_rows(payload_files, project_root)
    payload_manifest = reports_dir / "STEP13B_PAYLOAD_MANIFEST.csv"
    write_csv(payload_manifest, payload_manifest_rows)
    payload_sha = reports_dir / "STEP13B_PAYLOAD_SHA256.txt"
    write_text(
        payload_sha,
        "".join(
            f"{row['SHA256']}  {row['Relative_Path']}\n" for row in payload_manifest_rows
        ),
    )
    integrated_bundle = output_root / "Step13B_主分析与独立复核整合包.zip"
    integrated_members = [
        (path, path.relative_to(project_root).as_posix())
        for path in payload_files + [payload_manifest, payload_sha]
    ]
    deterministic_zip(integrated_bundle, integrated_members)
    final_files = payload_files + [payload_manifest, payload_sha, integrated_bundle]
    final_manifest_rows = inventory_rows(final_files, project_root)
    final_manifest = reports_dir / "STEP13B_PRIMARY_ANALYSIS_MANIFEST.csv"
    write_csv(final_manifest, final_manifest_rows)
    final_sha = reports_dir / "STEP13B_PRIMARY_ANALYSIS_SHA256.txt"
    sha_rows = final_manifest_rows + [
        {
            "Relative_Path": final_manifest.relative_to(project_root).as_posix(),
            "Size_Bytes": final_manifest.stat().st_size,
            "SHA256": sha256(final_manifest),
        }
    ]
    write_text(
        final_sha,
        "".join(f"{row['SHA256']}  {row['Relative_Path']}\n" for row in sha_rows),
    )
    print("CORRECTED_STEP13_PRIMARY_ANALYSIS_COMPLETED")
    print(f"INCLUDED_NCT_COUNT={len(included_ids)}")
    print(f"FULL_JSON_HASH_COVERAGE={len(documents)}/1218")
    print(f"TABLES={len(tables)}")
    print("FIGURES=6")
    print(f"QA_CHECKS={len(checks)}/{len(checks)}")
    print("INDEPENDENT_VALIDATION_COMPLETED=NO")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--output-root", type=Path)
    parser.add_argument("--reports-root", type=Path)
    parser.add_argument("--analytical-input-manifest", type=Path)
    args = parser.parse_args()
    try:
        run(
            args.project_root.resolve(),
            args.output_root.resolve() if args.output_root else None,
            args.reports_root.resolve() if args.reports_root else None,
            (
                args.analytical_input_manifest.resolve()
                if args.analytical_input_manifest
                else None
            ),
        )
    except Exception as exc:  # noqa: BLE001
        print(f"STEP13B_PRIMARY_ANALYSIS_FAILED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
