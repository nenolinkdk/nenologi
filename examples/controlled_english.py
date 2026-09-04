"""Run the deterministic text-to-Analysis path."""

import sys

from nenologi import ControlledEnglishAnalyzer, analysis_to_json


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    result = ControlledEnglishAnalyzer().analyze("All employees must register.")
    print(analysis_to_json(result))
