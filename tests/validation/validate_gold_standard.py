#!/usr/bin/env python3
"""Validate Nenologi v0.1 schemas and controlled gold-standard data."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
GOLD_DIR = ROOT / "tests" / "gold_standard"
LANGUAGE_RE = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")
ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")

DIFFERENCE_TYPES = {
    "NEGATION_CHANGE", "CONJUNCTION_CHANGE", "QUANTIFIER_CHANGE",
    "MODALITY_CHANGE", "CONDITION_CHANGE", "TEMPORAL_CHANGE",
    "SCOPE_CHANGE", "ENTITY_RELATION_CHANGE", "ADDITION", "OMISSION",
    "NUMERIC_THRESHOLD_CHANGE",
}
SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
STATUSES = {
    "EXPLICIT", "ENTAILED", "PROBABLE", "AMBIGUOUS", "UNSUPPORTED",
    "CONTRADICTED", "CANNOT_BE_SAFELY_FORMALIZED",
}
LOGICAL_RELATIONS = {"EQUIVALENT", "CONTRADICTORY", "UNDETERMINED"}
NUMERIC_OPERATORS = {"GREATER_THAN", "GREATER_THAN_OR_EQUAL", "LESS_THAN", "LESS_THAN_OR_EQUAL", "EQUAL"}
CASE_FILES = (
    GOLD_DIR / "comparison" / "cases.json",
    GOLD_DIR / "equivalence" / "cases.json",
    GOLD_DIR / "entailment" / "cases.json",
)


class ValidationError(Exception):
    """Raised when committed specification data violates its contract."""


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{path.relative_to(ROOT)}: {exc}") from exc


def require_fields(value: dict[str, Any], fields: set[str], location: str) -> None:
    missing = fields - value.keys()
    if missing:
        raise ValidationError(f"{location}: missing fields {sorted(missing)}")


def validate_schemas() -> None:
    loaded = {}
    for name in (
        "analysis-v0.1.schema.json",
        "comparison-v0.1.schema.json",
        "test-case-v0.1.schema.json",
    ):
        schema = load_json(SCHEMA_DIR / name)
        loaded[name] = schema
        require_fields(schema, {"$schema", "$id", "title", "type"}, f"schemas/{name}")
        if schema["$schema"] != "https://json-schema.org/draft/2020-12/schema":
            raise ValidationError(f"schemas/{name}: unexpected JSON Schema dialect")
    analysis_statuses = set(loaded["analysis-v0.1.schema.json"]["$defs"]["interpretationStatus"]["enum"])
    numeric_operators = set(loaded["analysis-v0.1.schema.json"]["$defs"]["numericConstraint"]["properties"]["operator"]["enum"])
    comparison_differences = set(loaded["comparison-v0.1.schema.json"]["$defs"]["differenceType"]["enum"])
    comparison_severities = set(loaded["comparison-v0.1.schema.json"]["$defs"]["severity"]["enum"])
    comparison_relations = set(loaded["comparison-v0.1.schema.json"]["$defs"]["logicalRelation"]["enum"])
    test_defs = loaded["test-case-v0.1.schema.json"]["$defs"]
    if analysis_statuses != STATUSES or set(test_defs["status"]["enum"]) != STATUSES:
        raise ValidationError("interpretation-status enums are out of sync")
    if numeric_operators != NUMERIC_OPERATORS:
        raise ValidationError("numeric-operator enum is out of sync")
    if comparison_differences != DIFFERENCE_TYPES or set(test_defs["differenceType"]["enum"]) != DIFFERENCE_TYPES:
        raise ValidationError("difference-type enums are out of sync")
    if comparison_severities != SEVERITIES or set(test_defs["severity"]["enum"]) != SEVERITIES:
        raise ValidationError("severity enums are out of sync")
    if comparison_relations != LOGICAL_RELATIONS or set(test_defs["logicalRelation"]["enum"]) != LOGICAL_RELATIONS:
        raise ValidationError("logical-relation enums are out of sync")


def validate_comparison(case: dict[str, Any], location: str) -> None:
    require_fields(case, {"source", "target", "source_language", "target_language", "expected"}, location)
    for key in ("source", "target"):
        if not isinstance(case[key], str) or not case[key].strip():
            raise ValidationError(f"{location}: {key} must be non-empty text")
    for key in ("source_language", "target_language"):
        if not LANGUAGE_RE.fullmatch(case[key]):
            raise ValidationError(f"{location}: invalid {key} {case[key]!r}")

    expected = case["expected"]
    require_fields(expected, {"material_difference", "differences"}, f"{location}.expected")
    if "logical_relation" in expected and expected["logical_relation"] not in LOGICAL_RELATIONS:
        raise ValidationError(f"{location}.expected: invalid logical relation")
    if case["case_type"] == "CHANGE":
        if expected["material_difference"] is not True or not expected["differences"]:
            raise ValidationError(f"{location}: CHANGE must contain a material difference")
        for index, difference in enumerate(expected["differences"]):
            where = f"{location}.expected.differences[{index}]"
            require_fields(difference, {"difference_type", "source_value", "target_value", "severity"}, where)
            if difference["difference_type"] not in DIFFERENCE_TYPES:
                raise ValidationError(f"{where}: invalid difference type")
            if difference["severity"] not in SEVERITIES:
                raise ValidationError(f"{where}: invalid severity")
    elif case["case_type"] == "EQUIVALENCE":
        if expected["material_difference"] is not False or expected["differences"] != []:
            raise ValidationError(f"{location}: EQUIVALENCE must have no differences")
    else:
        raise ValidationError(f"{location}: invalid comparison case type")


def validate_inference(case: dict[str, Any], location: str) -> None:
    require_fields(case, {"statement", "candidate_inference", "source_language", "expected"}, location)
    if not LANGUAGE_RE.fullmatch(case["source_language"]):
        raise ValidationError(f"{location}: invalid source_language")
    if not case["statement"].strip() or not case["candidate_inference"].strip():
        raise ValidationError(f"{location}: statement and candidate must be non-empty")
    require_fields(case["expected"], {"interpretation_status"}, f"{location}.expected")
    if case["expected"]["interpretation_status"] not in STATUSES:
        raise ValidationError(f"{location}: invalid interpretation status")


def validate_gold_standard() -> Counter[str]:
    ids: set[str] = set()
    counts: Counter[str] = Counter()
    represented_differences: set[str] = set()
    represented_statuses: set[str] = set()

    for path in CASE_FILES:
        collection = load_json(path)
        require_fields(collection, {"schema_version", "cases"}, str(path.relative_to(ROOT)))
        if collection["schema_version"] != "0.1" or not isinstance(collection["cases"], list):
            raise ValidationError(f"{path.relative_to(ROOT)}: invalid collection header")
        for index, case in enumerate(collection["cases"]):
            location = f"{path.relative_to(ROOT)}[{index}]"
            require_fields(case, {"id", "case_type", "category", "description"}, location)
            if not ID_RE.fullmatch(case["id"]):
                raise ValidationError(f"{location}: invalid id {case['id']!r}")
            if case["id"] in ids:
                raise ValidationError(f"{location}: duplicate id {case['id']!r}")
            ids.add(case["id"])
            counts[case["case_type"]] += 1
            counts[f"category:{case['category']}"] += 1
            if case["case_type"] == "INFERENCE":
                validate_inference(case, location)
                represented_statuses.add(case["expected"]["interpretation_status"])
            else:
                validate_comparison(case, location)
                for difference in case["expected"]["differences"]:
                    represented_differences.add(difference["difference_type"])

    missing_differences = DIFFERENCE_TYPES - represented_differences
    if missing_differences:
        raise ValidationError(f"missing difference coverage: {sorted(missing_differences)}")
    required_statuses = {"EXPLICIT", "ENTAILED", "PROBABLE", "UNSUPPORTED", "CONTRADICTED"}
    if required_statuses - represented_statuses:
        raise ValidationError(f"missing status coverage: {sorted(required_statuses - represented_statuses)}")
    if counts["CHANGE"] == 0 or counts["EQUIVALENCE"] == 0 or counts["INFERENCE"] == 0:
        raise ValidationError("change, equivalence, and inference cases are all required")
    return counts


def main() -> int:
    try:
        validate_schemas()
        counts = validate_gold_standard()
    except ValidationError as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    print(
        "VALIDATION PASSED: "
        f"{counts['CHANGE']} change, {counts['EQUIVALENCE']} equivalence, "
        f"{counts['INFERENCE']} inference cases"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
