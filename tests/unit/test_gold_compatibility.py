import json
import unittest
from pathlib import Path

from nenologi import ControlledEnglishAnalyzer


ROOT = Path(__file__).resolve().parents[2]
COMPATIBLE_CASE_IDS = {
    "modality_001", "modality_002", "modality_003",
    "quantifier_001", "quantifier_002", "quantifier_003",
    "negation_001", "negation_002", "contradiction_001",
    "conjunction_001", "conjunction_002",
    "numeric_001", "numeric_002", "numeric_003", "numeric_004",
    "condition_001",
}


class GoldStandardCompatibilityTests(unittest.TestCase):
    def test_documented_comparison_cases_are_individually_analyzable(self) -> None:
        data = json.loads((ROOT / "tests/gold_standard/comparison/cases.json").read_text(encoding="utf-8"))
        cases = {case["id"]: case for case in data["cases"]}
        self.assertTrue(COMPATIBLE_CASE_IDS <= cases.keys())
        analyzer = ControlledEnglishAnalyzer()
        for case_id in sorted(COMPATIBLE_CASE_IDS):
            with self.subTest(case_id=case_id):
                analyzer.analyze(cases[case_id]["source"])
                analyzer.analyze(cases[case_id]["target"])


if __name__ == "__main__":
    unittest.main()
