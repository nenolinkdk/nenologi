import json
import unittest
from pathlib import Path

from nenologi import ControlledEnglishAnalyzer, DeterministicComparator


ROOT = Path(__file__).resolve().parents[2]
SUPPORTED_CASE_IDS = {
    "modality_001", "modality_002", "modality_003",
    "quantifier_001", "quantifier_002", "quantifier_003",
    "negation_001", "negation_002",
}


class ComparatorGoldStandardTests(unittest.TestCase):
    def test_supported_gold_cases_match_expected_findings(self) -> None:
        data = json.loads((ROOT / "tests/gold_standard/comparison/cases.json").read_text(encoding="utf-8"))
        cases = {case["id"]: case for case in data["cases"]}
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

    def test_contradiction_case_exposes_documented_taxonomy_mismatch_without_duplicate(self) -> None:
        data = json.loads((ROOT / "tests/gold_standard/comparison/cases.json").read_text(encoding="utf-8"))
        case = next(item for item in data["cases"] if item["id"] == "contradiction_001")
        analyzer = ControlledEnglishAnalyzer()
        result = DeterministicComparator().compare(
            analyzer.analyze(case["source"]), analyzer.analyze(case["target"])
        )
        self.assertEqual(len(result.differences), 1)
        self.assertEqual(result.differences[0].difference_type.value, "NEGATION_CHANGE")
        self.assertEqual(case["expected"]["differences"][0]["difference_type"], "CONTRADICTION")


if __name__ == "__main__":
    unittest.main()
