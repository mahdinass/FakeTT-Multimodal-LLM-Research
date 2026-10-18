import json
import unittest
from pathlib import Path

from fakett_research.data import load_rows, split_rows
from fakett_research.mllm import fuse_branches, run_experiment
from fakett_research.prompts import select_examples


ROOT = Path(__file__).resolve().parents[1]


class FixtureClient:
    def __init__(self):
        self.fixtures = json.loads(
            (ROOT / "data" / "synthetic" / "mock_responses.json").read_text(encoding="utf-8")
        )
        self.calls = []

    def complete(self, prompt, image_paths=None, *, seed=42, sample_id="", branch="combined"):
        self.calls.append((sample_id, branch, tuple(image_paths or [])))
        return json.dumps(self.fixtures[sample_id][branch])


class MllmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_rows(ROOT / "data" / "synthetic" / "demo.csv")

    def test_dynamic_examples_are_selected_only_from_training_pool(self):
        parts = split_rows(self.rows)
        query = parts["test"][0]
        examples = select_examples(query, parts["train"], "dynamic", 3)
        self.assertEqual(len(examples), 3)
        self.assertTrue(all(row["split"] == "train" for row in examples))
        self.assertNotIn(query["sample_id"], {row["sample_id"] for row in examples})

    def test_fusion_weights_overlay_text_more_than_visual_branch(self):
        text = {"fake_probability": 0.8, "text_evidence_strength": "strong"}
        visual = {
            "fake_probability": 0.1,
            "visual_evidence_strength": "strong",
            "visual_evidence_type": "text_overlay_only",
        }
        result = fuse_branches(text, visual)
        self.assertAlmostEqual(result["text_weight"], 0.8)
        self.assertAlmostEqual(result["fake_probability"], 0.66)

    def test_mocked_multimodal_flow_uses_validation_then_test(self):
        client = FixtureClient()
        result = run_experiment(
            self.rows,
            client,
            family="c",
            few_shot="dynamic",
            n_shot=2,
            tune_threshold=True,
            model_name="static-fixture",
            inference_mode="mocked_static_fixtures",
        )
        self.assertEqual(result["inference_mode"], "mocked_static_fixtures")
        self.assertEqual(result["validation_n"], 4)
        self.assertEqual(result["test_n"], 4)
        self.assertEqual(len(result["predictions"]), 4)
        self.assertEqual(len(client.calls), 16)
        self.assertTrue(all(branch in {"text", "visual"} for _, branch, _ in client.calls))
        self.assertTrue(all(len(images) == 1 for _, branch, images in client.calls if branch == "visual"))
        self.assertEqual(result["test_metrics"]["accuracy"], 0.75)


if __name__ == "__main__":
    unittest.main()
