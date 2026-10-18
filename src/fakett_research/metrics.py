"""Small deterministic metrics with confusion-matrix order real, then fake."""

from __future__ import annotations

from collections import Counter
from typing import Iterable


LABELS = ("real", "fake")


def _prf(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def binary_metrics(y_true: Iterable[str], y_pred: Iterable[str]) -> dict[str, object]:
    """Return accuracy, macro/per-class F1, and a 2x2 matrix ordered real then fake."""
    truth, pred = list(y_true), list(y_pred)
    if not truth or len(truth) != len(pred):
        raise ValueError("truth and predictions must have the same non-zero length")
    if set(truth) - set(LABELS) or set(pred) - set(LABELS):
        raise ValueError("labels must be 'real' or 'fake'")

    counts = Counter(zip(truth, pred))
    per_class: dict[str, dict[str, float]] = {}
    for label in LABELS:
        tp = counts[(label, label)]
        fp = sum(counts[(other, label)] for other in LABELS if other != label)
        fn = sum(counts[(label, other)] for other in LABELS if other != label)
        precision, recall, f1 = _prf(tp, fp, fn)
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}

    matrix = [[counts[(actual, guess)] for guess in LABELS] for actual in LABELS]
    correct = sum(counts[(label, label)] for label in LABELS)
    return {
        "n": len(truth),
        "accuracy": correct / len(truth),
        "macro_f1": sum(per_class[label]["f1"] for label in LABELS) / 2,
        "per_class": per_class,
        "confusion_matrix_labels": list(LABELS),
        "confusion_matrix": matrix,
    }
