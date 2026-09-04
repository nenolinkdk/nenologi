#!/usr/bin/env python3
"""Reproducible end-to-end implementation-status audit for all gold cases."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator,
    UnsupportedComparisonError, UnsupportedConstructionError,
)

ROOT = Path(__file__).resolve().parents[2]
CASE_FILES = (
    ROOT / "tests/gold_standard/comparison/cases.json",
    ROOT / "tests/gold_standard/equivalence/cases.json",
    ROOT / "tests/gold_standard/entailment/cases.json",
)


class ImplementationStatus(StrEnum):
    END_TO_END_EXACT = "END_TO_END_EXACT"
    ANALYZABLE_BUT_NOT_EXACT = "ANALYZABLE_BUT_NOT_EXACT"
    PARSER_UNSUPPORTED = "PARSER_UNSUPPORTED"
    COMPARATOR_UNSUPPORTED = "COMPARATOR_UNSUPPORTED"
    INFERENCE_NOT_IMPLEMENTED = "INFERENCE_NOT_IMPLEMENTED"


@dataclass(frozen=True, slots=True)
class AuditResult:
    case_status: dict[str, ImplementationStatus]
    totals: Counter[ImplementationStatus]
    by_feature: dict[str, Counter[ImplementationStatus]]


def _actual_differences(comparison) -> list[dict[str, object]]:
    return [
        {
            "difference_type": finding.difference_type.value,
            "source_value": finding.source_value,
            "target_value": finding.target_value,
            "severity": finding.severity.value,
        }
        for finding in comparison.differences
    ]


def audit_gold_coverage() -> AuditResult:
    analyzer = ControlledEnglishAnalyzer()
    comparator = DeterministicComparator()
    case_status: dict[str, ImplementationStatus] = {}
    totals: Counter[ImplementationStatus] = Counter()
    by_feature: dict[str, Counter[ImplementationStatus]] = defaultdict(Counter)

    for path in CASE_FILES:
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            if case["case_type"] == "INFERENCE":
                status = ImplementationStatus.INFERENCE_NOT_IMPLEMENTED
            else:
                try:
                    source = analyzer.analyze(case["source"])
                    target = analyzer.analyze(case["target"])
                except UnsupportedConstructionError:
                    status = ImplementationStatus.PARSER_UNSUPPORTED
                else:
                    try:
                        comparison = comparator.compare(source, target)
                    except UnsupportedComparisonError:
                        status = ImplementationStatus.COMPARATOR_UNSUPPORTED
                    else:
                        exact = _actual_differences(comparison) == case["expected"]["differences"]
                        expected_relation = case["expected"].get("logical_relation")
                        if expected_relation is not None:
                            exact = exact and comparison.logical_relation.value == expected_relation
                        status = (
                            ImplementationStatus.END_TO_END_EXACT
                            if exact else ImplementationStatus.ANALYZABLE_BUT_NOT_EXACT
                        )
            case_status[case["id"]] = status
            totals[status] += 1
            by_feature[case["category"]][status] += 1

    return AuditResult(case_status, totals, dict(by_feature))


def main() -> int:
    result = audit_gold_coverage()
    print(f"TOTAL {sum(result.totals.values())}")
    for status in ImplementationStatus:
        print(f"{status.value} {result.totals[status]}")
    for feature in sorted(result.by_feature):
        values = ", ".join(
            f"{status.value}={result.by_feature[feature][status]}"
            for status in ImplementationStatus
            if result.by_feature[feature][status]
        )
        print(f"FEATURE {feature}: {values}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
