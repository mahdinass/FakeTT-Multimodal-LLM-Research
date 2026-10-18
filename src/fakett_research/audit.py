"""Aggregate manifest, text-coverage, duplicate, and split-integrity audits."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from .data import load_rows, text_for


AUDIT_FIELDS = ("description", "asr", "ocr")


def audit_rows(rows: list[dict[str, object]], fields: tuple[str, ...] = AUDIT_FIELDS) -> dict[str, object]:
    if not rows:
        raise ValueError("cannot audit an empty row set")
    by_split: dict[str, list[dict[str, object]]] = defaultdict(list)
    id_splits: dict[str, set[str]] = defaultdict(set)
    text_splits: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        split = str(row["split"])
        by_split[split].append(row)
        id_splits[str(row["sample_id"])].add(split)
        normalized = " ".join(text_for(row, fields).lower().split())
        if normalized:
            text_splits[normalized].add(split)

    class_counts = {
        split: dict(Counter(str(row["label"]) for row in split_rows))
        for split, split_rows in sorted(by_split.items())
    }
    coverage = {}
    for field in fields:
        coverage[field] = {
            split: sum(bool(str(row.get(field, "")).strip()) for row in split_rows)
            for split, split_rows in sorted(by_split.items())
        }
    length_summary = {}
    for split, split_rows in sorted(by_split.items()):
        lengths = [len(text_for(row, fields)) for row in split_rows]
        length_summary[split] = {
            "count": len(lengths),
            "mean_characters": statistics.mean(lengths),
            "median_characters": statistics.median(lengths),
            "empty_documents": sum(length == 0 for length in lengths),
        }
    return {
        "n_rows": len(rows),
        "split_counts": {split: len(split_rows) for split, split_rows in sorted(by_split.items())},
        "class_counts": class_counts,
        "non_empty_text_fields": coverage,
        "document_length": length_summary,
        "sample_ids_present_in_multiple_splits": sum(len(splits) > 1 for splits in id_splits.values()),
        "identical_texts_present_in_multiple_splits": sum(len(splits) > 1 for splits in text_splits.values()),
        "fields_audited": list(fields),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--fields", default=",".join(AUDIT_FIELDS))
    parser.add_argument("--output", default="runs/input_audit.json")
    args = parser.parse_args()
    fields = tuple(part.strip() for part in args.fields.split(",") if part.strip())
    result = audit_rows(load_rows(args.csv), fields)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
