#!/usr/bin/env python3
"""Reproducible end-to-end implementation-status audit for all gold cases."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from nenologi import (
    ControlledEnglishAnalyzer, DeterministicComparator, DeterministicInferenceEngine,
    DeterministicPropositionAligner,
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
    cases: tuple[dict[str, object], ...] = ()


PARSER_BLOCKERS = {
    "temporal_001": "UNSUPPORTED_EVENT_TEMPORAL_ANCHOR",
    "temporal_003": "UNSUPPORTED_NESTED_TEMPORAL_PHRASE",
    "condition_003": "UNSUPPORTED_UNLESS",
    "entity_relation_001": "UNSUPPORTED_PAST_TRANSITIVE",
    "entity_relation_002": "UNSUPPORTED_PAST_TRANSITIVE",
    "scope_001": "UNSUPPORTED_EMBEDDED_VERB",
    "scope_002": "UNSUPPORTED_EMBEDDED_VERB",
    "addition_002": "UNSUPPORTED_MULTI_SENTENCE",
    "omission_002": "UNSUPPORTED_COORDINATED_PREDICATES",
}

COMPARATOR_BLOCKERS = {
    "addition_001": "UNSUPPORTED_COORDINATED_PREDICATE_REPRESENTATION",
    "equivalence_005": "UNSUPPORTED_SYMMETRIC_CONJUNCTION_ALIGNMENT",
}

INFERENCE_BLOCKERS = {
    "entailment_002": "UNIVERSAL_INSTANTIATION",
    "entailment_003": "DEFEASIBLE_PREDICTION",
    "entailment_004": "WORLD_KNOWLEDGE_NON_ENTAILMENT",
    "entailment_005": "LEXICAL_OPPOSITION_CONTRADICTION",
    "entailment_006": "COREFERENCE_AMBIGUITY",
    "entailment_007": "METAPHOR_NON_LITERAL_FORMALIZATION",
}


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
    inference_engine = DeterministicInferenceEngine()
    case_status: dict[str, ImplementationStatus] = {}
    totals: Counter[ImplementationStatus] = Counter()
    by_feature: dict[str, Counter[ImplementationStatus]] = defaultdict(Counter)
    case_results: list[dict[str, object]] = []

    for path in CASE_FILES:
        cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
        for case in cases:
            if case["case_type"] == "INFERENCE":
                parsed = []
                analyses = []
                for field in ("statement", "candidate_inference"):
                    try:
                        analyses.append(analyzer.analyze(case[field]))
                    except UnsupportedConstructionError:
                        parsed.append(False)
                    else:
                        parsed.append(True)
                exact = False
                if all(parsed):
                    inference = inference_engine.infer(analyses[0], analyses[1])
                    exact = inference.interpretation_status.value == case["expected"]["interpretation_status"]
                status = (
                    ImplementationStatus.END_TO_END_EXACT
                    if exact else ImplementationStatus.INFERENCE_NOT_IMPLEMENTED
                )
                pipeline = {
                    "parser": "SUPPORTED" if all(parsed) else "UNSUPPORTED",
                    "analysis": "AVAILABLE" if all(parsed) else "INCOMPLETE",
                    "alignment": "NOT_APPLICABLE", "comparator": "NOT_APPLICABLE",
                    "inference": inference.rule if exact else "NOT_IMPLEMENTED",
                    "blocking_reason": "NONE" if exact else INFERENCE_BLOCKERS[case["id"]],
                }
            else:
                try:
                    source = analyzer.analyze(case["source"])
                    target = analyzer.analyze(case["target"])
                except UnsupportedConstructionError as exc:
                    status = ImplementationStatus.PARSER_UNSUPPORTED
                    pipeline = {
                        "parser": "UNSUPPORTED", "analysis": "NOT_REACHED",
                        "alignment": "NOT_REACHED", "comparator": "NOT_REACHED",
                        "inference": "NOT_APPLICABLE",
                        "blocking_reason": PARSER_BLOCKERS.get(case["id"], "UNCLASSIFIED_PARSER_BLOCKER"),
                        "detail": str(exc),
                    }
                else:
                    alignment = DeterministicPropositionAligner().align(
                        source, target, allow_structural_counterparts=True,
                    )
                    alignment_status = (
                        "ALIGNED" if alignment.alignments else
                        "AMBIGUOUS" if alignment.ambiguous_source_ids or alignment.ambiguous_target_ids else
                        "UNALIGNED"
                    )
                    try:
                        comparison = comparator.compare(source, target)
                    except UnsupportedComparisonError as exc:
                        status = ImplementationStatus.COMPARATOR_UNSUPPORTED
                        pipeline = {
                            "parser": "SUPPORTED", "analysis": "AVAILABLE",
                            "alignment": alignment_status, "comparator": "UNSUPPORTED",
                            "inference": "NOT_APPLICABLE",
                            "blocking_reason": COMPARATOR_BLOCKERS.get(case["id"], "UNCLASSIFIED_COMPARATOR_BLOCKER"),
                            "detail": str(exc),
                        }
                    else:
                        exact = _actual_differences(comparison) == case["expected"]["differences"]
                        expected_relation = case["expected"].get("logical_relation")
                        if expected_relation is not None:
                            exact = exact and comparison.logical_relation.value == expected_relation
                        status = (
                            ImplementationStatus.END_TO_END_EXACT
                            if exact else ImplementationStatus.ANALYZABLE_BUT_NOT_EXACT
                        )
                        pipeline = {
                            "parser": "SUPPORTED", "analysis": "AVAILABLE",
                            "alignment": alignment_status, "comparator": "SUPPORTED",
                            "inference": "NOT_APPLICABLE",
                            "blocking_reason": "NONE" if exact else "EXPECTED_OUTPUT_MISMATCH",
                        }
            case_status[case["id"]] = status
            totals[status] += 1
            by_feature[case["category"]][status] += 1
            case_results.append({
                "case_id": case["id"], "category": case["category"], **pipeline,
                "final_status": status.value,
            })

    return AuditResult(case_status, totals, dict(by_feature), tuple(case_results))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit the complete per-case pipeline matrix as JSON")
    args = parser.parse_args()
    result = audit_gold_coverage()
    if args.json:
        print(json.dumps({
            "total": sum(result.totals.values()),
            "totals": {status.value: result.totals[status] for status in ImplementationStatus},
            "cases": result.cases,
        }, indent=2))
        return 0
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
