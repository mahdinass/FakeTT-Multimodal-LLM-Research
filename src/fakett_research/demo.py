"""Run both research workflows using synthetic rows and static mock LLM responses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .baseline import run_baseline
from .data import load_rows
from .fixture_client import FixtureResponseClient
from .mllm import run_experiment
from .synthetic_assets import generate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="runs/synthetic-demo")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    data_dir = root / "data" / "synthetic"
    generate(data_dir / "images")
    rows = load_rows(data_dir / "demo.csv")
    baseline = run_baseline(rows)
    client = FixtureResponseClient(data_dir / "mock_responses.json")
    multimodal = run_experiment(
        rows,
        client,
        family="c",
        few_shot="dynamic",
        n_shot=2,
        self_consistency=1,
        tune_threshold=True,
        model_name="static-synthetic-fixtures",
        inference_mode="mocked_static_fixtures",
    )
    if not client.calls or not all(branch in {"text", "visual"} for _, branch in client.calls):
        raise RuntimeError("synthetic MLLM demo did not exercise the two evidence branches")
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "baseline.json").write_text(json.dumps(baseline, indent=2) + "\n", encoding="utf-8")
    (output_dir / "mllm_mocked.json").write_text(json.dumps(multimodal, indent=2) + "\n", encoding="utf-8")
    summary: dict[str, Any] = {
        "note": "Synthetic data and static responses; these metrics are a workflow check, not model results.",
        "baseline_test_metrics": baseline["test_metrics"],
        "mllm_test_metrics": multimodal["test_metrics"],
        "mllm_inference_mode": multimodal["inference_mode"],
        "mocked_branch_calls": len(client.calls),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
