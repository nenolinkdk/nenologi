import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("validate_gold_standard.py")
SPEC = importlib.util.spec_from_file_location("gold_validator", MODULE_PATH)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class GoldStandardValidationTests(unittest.TestCase):
    def test_schema_documents_parse(self) -> None:
        VALIDATOR.validate_schemas()

    def test_gold_standard_contract_and_coverage(self) -> None:
        counts = VALIDATOR.validate_gold_standard()
        self.assertEqual(counts["CHANGE"], 30)
        self.assertGreaterEqual(counts["EQUIVALENCE"], 1)
        self.assertGreaterEqual(counts["INFERENCE"], 5)


if __name__ == "__main__":
    unittest.main()
