"""Prompt-family A/B/C inference, train-only few-shot selection, and test evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .client import OpenAICompatibleClient
from .data import load_rows, split_rows
from .fixture_client import FixtureResponseClient
from .metrics import binary_metrics
from .prompts import render_prompt, select_examples
from .structured_output import normalize_response


def _mean(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot average an empty set of model responses")
    return sum(values) / len(values)


def fuse_branches(text_result: dict[str, Any], visual_result: dict[str, Any]) -> dict[str, Any]:
    """Apply the original project's transparent evidence-weighted late-fusion idea."""
    visual_type = str(visual_result.get("visual_evidence_type", "unclear")).lower()
    text_strength = str(text_result.get("text_evidence_strength", "medium")).lower()
    visual_strength = str(visual_result.get("visual_evidence_strength", "medium")).lower()
    if visual_type == "text_overlay_only":
        text_weight = 0.8
    elif visual_strength == "weak":
        text_weight = 0.7
    elif text_strength == "weak" and visual_strength == "strong":
        text_weight = 0.3
    else:
        text_weight = 0.5
    probability = (
        text_weight * float(text_result["fake_probability"])
        + (1 - text_weight) * float(visual_result["fake_probability"])
    )
    return {
        "label": "fake" if probability >= 0.5 else "real",
        "confidence": max(probability, 1 - probability),
        "fake_probability": probability,
        "text_weight": text_weight,
        "visual_weight": 1 - text_weight,
        "text_branch": text_result,
        "visual_branch": visual_result,
    }


def _sample_branch(
    client: Any,
    row: dict[str, object],
    prompt: str,
    branch: str,
    images: list[str],
    repeats: int,
    seed: int,
) -> dict[str, Any]:
    outputs = []
    for offset in range(repeats):
        raw = client.complete(
            prompt,
            image_paths=images,
            seed=seed + offset,
            sample_id=str(row["sample_id"]),
            branch=branch,
        )
        outputs.append(normalize_response(raw))
    probability = _mean([float(item["fake_probability"]) for item in outputs])
    labels = ["fake" if probability >= 0.5 else "real"]
    result = dict(outputs[0])
    result.update(
        {
            "fake_probability": probability,
            "label": labels[0],
            "self_consistency_samples": repeats,
            "sample_probabilities": [item["fake_probability"] for item in outputs],
        }
    )
    return result


def predict_row(
    row: dict[str, object],
    train_rows: list[dict[str, object]],
    client: Any,
    *,
    family: str = "c",
    few_shot: str = "dynamic",
    n_shot: int = 0,
    no_visual: bool = False,
    self_consistency: int = 1,
    seed: int = 42,
) -> dict[str, Any]:
    if self_consistency < 1:
        raise ValueError("self_consistency must be at least 1")
    examples = select_examples(row, train_rows, few_shot, n_shot)
    images = list(row.get("image_paths", [])) if not no_visual else []

    if family != "c":
        prompt = render_prompt(family, "combined", row, examples)
        return _sample_branch(
            client, row, prompt, "combined", images, self_consistency, seed
        )

    text_prompt = render_prompt("c", "text", row, examples)
    text_result = _sample_branch(
        client, row, text_prompt, "text", [], self_consistency, seed
    )
    if no_visual or not images:
        text_result["visual_branch"] = None
        text_result["fusion"] = "text_only"
        return text_result

    visual_prompt = render_prompt("c", "visual", row, examples)
    visual_result = _sample_branch(
        client, row, visual_prompt, "visual", images, self_consistency, seed
    )
    fused = fuse_branches(text_result, visual_result)
    fused["fusion"] = "evidence_weighted_late_fusion"
    return fused


def select_threshold(
    rows: list[dict[str, object]], predictions: list[dict[str, Any]]
) -> float:
    if not rows or len(rows) != len(predictions):
        raise ValueError("validation rows and predictions must have equal non-zero length")
    candidates = sorted(
        {0.0, 0.5, 1.0, *(float(item["fake_probability"]) for item in predictions)}
    )
    truth = [str(row["label"]) for row in rows]
    scored = []
    for threshold in candidates:
        labels = [
            "fake" if float(item["fake_probability"]) >= threshold else "real"
            for item in predictions
        ]
        scored.append((binary_metrics(truth, labels)["macro_f1"], threshold))
    best = max(score for score, _ in scored)
    return min(threshold for score, threshold in scored if score == best)


def _predict_all(rows: list[dict[str, object]], train_rows: list[dict[str, object]], client: Any, **config: Any) -> list[dict[str, Any]]:
    return [predict_row(row, train_rows, client, **config) for row in rows]


def run_experiment(
    rows: list[dict[str, object]],
    client: Any,
    *,
    family: str = "c",
    few_shot: str = "dynamic",
    n_shot: int = 0,
    no_visual: bool = False,
    self_consistency: int = 1,
    tune_threshold: bool = False,
    threshold: float = 0.5,
    seed: int = 42,
    model_name: str = "configured-model",
    inference_mode: str = "real_endpoint",
) -> dict[str, object]:
    parts = split_rows(rows)
    if not parts["train"] or not parts["test"]:
        raise ValueError("the CSV must include non-empty train and test splits")
    config = {
        "family": family,
        "few_shot": few_shot,
        "n_shot": n_shot,
        "no_visual": no_visual,
        "self_consistency": self_consistency,
        "seed": seed,
    }
    val_predictions: list[dict[str, Any]] = []
    val_metrics = None
    threshold_source = "fixed"
    if tune_threshold:
        if not parts["val"]:
            raise ValueError("threshold tuning requires a non-empty validation split")
        val_predictions = _predict_all(parts["val"], parts["train"], client, **config)
        threshold = select_threshold(parts["val"], val_predictions)
        threshold_source = "validation"
        val_metrics = binary_metrics(
            [str(row["label"]) for row in parts["val"]],
            [
                "fake" if float(item["fake_probability"]) >= threshold else "real"
                for item in val_predictions
            ],
        )

    # The held-out test split is read once here, after all optional selection uses validation.
    test_predictions = _predict_all(parts["test"], parts["train"], client, **config)
    test_labels = [
        "fake" if float(item["fake_probability"]) >= threshold else "real"
        for item in test_predictions
    ]
    return {
        "method": "OpenAI-compatible multimodal prompting",
        "prompt_family": family,
        "few_shot_strategy": few_shot,
        "n_shot": n_shot,
        "visual_input": not no_visual,
        "self_consistency": self_consistency,
        "model": model_name,
        "seed": seed,
        "threshold": threshold,
        "threshold_selected_on": threshold_source,
        "train_n": len(parts["train"]),
        "validation_n": len(parts["val"]),
        "test_n": len(parts["test"]),
        "validation_metrics": val_metrics,
        "test_metrics": binary_metrics(
            [str(row["label"]) for row in parts["test"]], test_labels
        ),
        "predictions": [
            {
                "sample_id": row["sample_id"],
                "label": label,
                "fake_probability": item["fake_probability"],
                "fusion": item.get("fusion", "single_branch"),
            }
            for row, label, item in zip(parts["test"], test_labels, test_predictions)
        ],
        "inference_mode": inference_mode,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--family", choices=("a", "b", "c"), default="c")
    parser.add_argument("--few-shot", choices=("none", "fixed", "dynamic"), default="dynamic")
    parser.add_argument("--n-shot", type=int, default=0)
    parser.add_argument("--no-visual", action="store_true")
    parser.add_argument("--self-consistency", type=int, default=1)
    parser.add_argument("--tune-threshold", action="store_true")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--mock-fixtures", default=None, help="JSON fixture file; disables network access")
    parser.add_argument("--timeout", type=float, default=90.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--output", default="runs/mllm_metrics.json")
    args = parser.parse_args()
    client = (
        FixtureResponseClient(args.mock_fixtures)
        if args.mock_fixtures
        else OpenAICompatibleClient(
            base_url=args.base_url, model=args.model, timeout=args.timeout, retries=args.retries
        )
    )
    result = run_experiment(
        load_rows(args.csv),
        client,
        family=args.family,
        few_shot=args.few_shot,
        n_shot=args.n_shot,
        no_visual=args.no_visual,
        self_consistency=args.self_consistency,
        tune_threshold=args.tune_threshold,
        threshold=args.threshold,
        seed=args.seed,
        model_name=args.model or ("static-fixture" if args.mock_fixtures else client.model),
        inference_mode="mocked_static_fixtures" if args.mock_fixtures else "real_endpoint",
    )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["test_metrics"], indent=2))


if __name__ == "__main__":
    main()
