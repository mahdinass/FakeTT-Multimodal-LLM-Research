import unittest
from pathlib import Path

from fakett_research.baseline import run_baseline
from fakett_research.audit import audit_rows
from fakett_research.data import load_rows, split_rows


ROOT = Path(__file__).resolve().parents[1]


class BaselineTests(unittest.TestCase):
    def test_demo_baseline_fits_train_and_evaluates_test(self):
        rows = load_rows(ROOT / "data" / "synthetic" / "demo.csv")
        result = run_baseline(rows)
        self.assertEqual((result["train_n"], result["validation_n"], result["test_n"]), (12, 4, 4))
        self.assertEqual(result["threshold"], 0.5)
        self.assertEqual(result["test_metrics"]["n"], 4)
        self.assertEqual(len(result["predictions"]), 4)

    def test_validation_threshold_is_selected_from_validation_rows(self):
        rows = load_rows(ROOT / "data" / "synthetic" / "demo.csv")
        result = run_baseline(rows, tune_threshold=True)
        self.assertEqual(result["threshold_selected_on"], "validation")
        self.assertIsNotNone(result["validation_metrics"])
        self.assertEqual(result["test_metrics"]["n"], 4)

    def test_csv_images_resolve_relative_to_csv(self):
        rows = load_rows(ROOT / "data" / "synthetic" / "demo.csv")
        image = Path(rows[0]["image_paths"][0])
        self.assertTrue(image.is_file())

    def test_input_audit_reports_aggregate_split_and_coverage_counts(self):
        rows = load_rows(ROOT / "data" / "synthetic" / "demo.csv")
        summary = audit_rows(rows)
        self.assertEqual(summary["split_counts"], {"test": 4, "train": 12, "val": 4})
        self.assertEqual(summary["sample_ids_present_in_multiple_splits"], 0)
        self.assertEqual(summary["identical_texts_present_in_multiple_splits"], 0)
        self.assertEqual(summary["non_empty_text_fields"]["ocr"]["train"], 12)


if __name__ == "__main__":
    unittest.main()
