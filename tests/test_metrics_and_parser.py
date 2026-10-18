import unittest

from fakett_research.metrics import binary_metrics
from fakett_research.structured_output import StructuredOutputError, normalize_response


class MetricAndParserTests(unittest.TestCase):
    def test_metrics_use_fixed_real_then_fake_matrix_order(self):
        result = binary_metrics(["real", "fake", "fake"], ["real", "real", "fake"])
        self.assertEqual(result["confusion_matrix_labels"], ["real", "fake"])
        self.assertEqual(result["confusion_matrix"], [[1, 0], [1, 1]])
        self.assertAlmostEqual(result["accuracy"], 2 / 3)

    def test_parser_extracts_json_from_fenced_text(self):
        parsed = normalize_response('```json\n{"label":"REAL","confidence":0.75}\n```')
        self.assertEqual(parsed["label"], "real")
        self.assertAlmostEqual(parsed["fake_probability"], 0.25)

    def test_parser_handles_braces_inside_rationale(self):
        parsed = normalize_response('Result: {"label":"fake","confidence":0.7,"rationale":"tag {x}"}')
        self.assertAlmostEqual(parsed["fake_probability"], 0.7)

    def test_parser_rejects_invalid_confidence_and_labels(self):
        for payload in (
            {"label": "maybe", "confidence": 0.5},
            {"label": "fake", "confidence": 1.2},
            {"label": "real", "confidence": True},
        ):
            with self.subTest(payload=payload), self.assertRaises(StructuredOutputError):
                normalize_response(payload)


if __name__ == "__main__":
    unittest.main()
