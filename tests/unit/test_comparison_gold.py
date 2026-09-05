import json
import unittest
from pathlib import Path

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator


ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_CASE_IDS = {
    "modality_001", "modality_002", "modality_003",
    "quantifier_001", "quantifier_002", "quantifier_003",
    "negation_001", "negation_002",
    "conjunction_001", "conjunction_002", "contradiction_001",
    "numeric_001", "numeric_002", "numeric_003", "numeric_004", "equivalence_003",
    "condition_001",
    "temporal_002",
    "equivalence_002",
    "equivalence_004",
    "entity_relation_003",
}


class ComparatorGoldStandardTests(unittest.TestCase):
    def test_supported_gold_cases_match_expected_findings(self) -> None:
        paths = ("comparison/cases.json", "equivalence/cases.json")
        cases = {
            case["id"]: case
            for path in paths
            for case in json.loads((ROOT / "tests/gold_standard" / path).read_text(encoding="utf-8"))["cases"]
        }
        analyzer = ControlledEnglishAnalyzer()
        comparator = DeterministicComparator()
        for case_id in sorted(SUPPORTED_CASE_IDS):
            case = cases[case_id]
            with self.subTest(case_id=case_id):
                result = comparator.compare(analyzer.analyze(case["source"]), analyzer.analyze(case["target"]))
                actual = [
                    {
                        "difference_type": finding.difference_type.value,
                        "source_value": finding.source_value,
                        "target_value": finding.target_value,
                        "severity": finding.severity.value,
                    }
                    for finding in result.differences
                ]
                self.assertEqual(actual, case["expected"]["differences"])
                if "logical_relation" in case["expected"]:
                    self.assertEqual(result.logical_relation.value, case["expected"]["logical_relation"])


if __name__ == "__main__":
    unittest.main()
