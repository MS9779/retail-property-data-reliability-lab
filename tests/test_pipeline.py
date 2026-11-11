import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from run_pipeline import build_report


class PipelineTests(unittest.TestCase):
    def test_pipeline_detects_expected_synthetic_exceptions(self):
        report = build_report()
        codes = {item["code"] for item in report["issues"]}
        self.assertEqual(report["records_checked"], {"leases": 5, "finance": 4, "locations": 4})
        self.assertTrue({"MISSING_FINANCE_RECORD", "ORPHAN_FINANCE_RECORD", "RENT_VARIANCE"}.issubset(codes))


if __name__ == "__main__":
    unittest.main()
