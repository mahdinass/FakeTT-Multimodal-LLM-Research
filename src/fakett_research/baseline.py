"""TF-IDF/logistic-regression baseline trained only on the supplied train split."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .data import load_rows, split_rows, text_for
from .metrics import binary_metrics


DEFAULT_FIELDS = ("description", "asr", "ocr")


def fit_baseline(
    train_rows: list[dict[str, object]], fields: tuple[str, ...] = DEFAULT_FIELDS
) -> tuple[TfidfVectorizer, LogisticRegression]:
    if not train_rows:
        raise ValueError("train split is empty")
    if {str(row["label"]) for row in train_rows} != {"fake", "real"}:
        raise ValueError("train split must contain at least one example of each label")
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_features=20_000,
        sublinear_tf=True,
    )
    x_train = vectorizer.fit_transform([text_for(row, fields) for row in train_rows])
    model = LogisticRegression(
        C=1.0,
        class_weight="balanced",
        max_iter=2_000,
        random_state=42,
        solver="liblinear",
    )
    model.fit(x_train, [str(row["label"]) for row in train_rows])
    return vectorizer, model


def fake_probabilities(
    rows: list[dict[str, object]],
    vectorizer: TfidfVectorizer,
    model: LogisticRegression,
    fields: tuple[str, ...] = DEFAULT_FIELDS,
) -> list[float]:
    if not rows:
        return []
    matrix = vectorizer.transform([text_for(row, fields) for row in rows])
    classes = list(model.classes_)
    if "fake" not in classes:
        return [0.0] * len(rows)
    column = classes.index("fake")
    return [float(value) for value in model.predict_proba(matrix)[:, column]]


def select_threshold(
    val_rows: list[dict[str, object]], probabilities: list[float]
) -> float:
    """Choose the macro-F1 threshold on validation only; ties choose the lower threshold."""
    if not val_rows or len(val_rows) != len(probabilities):
        raise ValueError("validation rows and probabilities must have equal non-zero length")
    candidates = sorted({0.0, 0.5, 1.0, *probabilities})
    truth = [str(row["label"]) for row in val_rows]
    scored = []
    for threshold in candidates:
        predicted = ["fake" if p >= threshold else "real" for p in probabilities]
        scored.append((binary_metrics(truth, predicted)["macro_f1"], threshold))
    best_score = max(score for score, _ in scored)
    return min(threshold for score, threshold in scored if score == best_score)


def run_baseline(
    rows: list[dict[str, object]],
    fields: tuple[str, ...] = DEFAULT_FIELDS,
    tune_threshold: bool = False,
) -> dict[str, object]:
    parts = split_rows(rows)
    if not parts["train"] or not parts["test"]:
        raise ValueError("the CSV must include non-empty train and test splits")
    vectorizer, model = fit_baseline(parts["train"], fields)
    threshold = 0.5
    validation_metrics = None
    if tune_threshold:
        if not parts["val"]:
            raise ValueError("threshold tuning requires a non-empty validation split")
        val_probabilities = fake_probabilities(parts["val"], vectorizer, model, fields)
        threshold = select_threshold(parts["val"], val_probabilities)
        val_labels = ["fake" if p >= threshold else "real" for p in val_probabilities]
        validation_metrics = binary_metrics(
            [str(row["label"]) for row in parts["val"]], val_labels
        )

    test_probabilities = fake_probabilities(parts["test"], vectorizer, model, fields)
    test_labels = ["fake" if p >= threshold else "real" for p in test_probabilities]
    return {
        "method": "TF-IDF + Logistic Regression",
        "fields": list(fields),
        "threshold": threshold,
        "threshold_selected_on": "validation" if tune_threshold else "fixed at 0.5",
        "train_n": len(parts["train"]),
        "validation_n": len(parts["val"]),
        "test_n": len(parts["test"]),
        "validation_metrics": validation_metrics,
        "test_metrics": binary_metrics(
            [str(row["label"]) for row in parts["test"]], test_labels
        ),
        "predictions": [
            {"sample_id": row["sample_id"], "label": label, "fake_probability": probability}
            for row, label, probability in zip(parts["test"], test_labels, test_probabilities)
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, help="CSV containing train/val/test rows")
    parser.add_argument("--fields", default=",".join(DEFAULT_FIELDS))
    parser.add_argument("--tune-threshold", action="store_true")
    parser.add_argument("--output", default="runs/baseline_metrics.json")
    args = parser.parse_args()
    fields = tuple(part.strip() for part in args.fields.split(",") if part.strip())
    result = run_baseline(load_rows(args.csv), fields, args.tune_threshold)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["test_metrics"], indent=2))


if __name__ == "__main__":
    main()
