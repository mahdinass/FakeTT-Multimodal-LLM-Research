"""Input validation and split loading for CSV data supplied by the user."""

from __future__ import annotations

import csv
import json
from pathlib import Path


REQUIRED_COLUMNS = {"sample_id", "split", "label", "description", "ocr", "asr"}


def load_rows(csv_path: str | Path) -> list[dict[str, object]]:
    path = Path(csv_path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"input CSV does not exist: {path}")
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - fields
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")
        rows: list[dict[str, object]] = []
        for line, row in enumerate(reader, start=2):
            label = str(row.get("label", "")).strip().lower()
            split = str(row.get("split", "")).strip().lower()
            if label not in {"fake", "real"}:
                raise ValueError(f"line {line}: label must be 'fake' or 'real'")
            if split not in {"train", "val", "test"}:
                raise ValueError(f"line {line}: split must be train, val, or test")
            item: dict[str, object] = {
                key: (value or "").strip()
                for key, value in row.items()
                if key is not None
            }
            item["label"] = label
            item["split"] = split
            item["_source_dir"] = path.parent
            raw_images = str(row.get("image_paths", "")).strip()
            if raw_images:
                try:
                    image_paths = (
                        json.loads(raw_images)
                        if raw_images.startswith("[")
                        else [part.strip() for part in raw_images.split(";") if part.strip()]
                    )
                except json.JSONDecodeError as error:
                    raise ValueError(f"line {line}: image_paths must be a JSON array or ;-separated paths") from error
                if not isinstance(image_paths, list) or not all(
                    isinstance(image, str) for image in image_paths
                ):
                    raise ValueError(f"line {line}: image_paths must be a JSON array of paths")
                item["image_paths"] = [
                    str((path.parent / image).resolve()) for image in image_paths
                ]
            else:
                item["image_paths"] = []
            rows.append(item)
    if not rows:
        raise ValueError("input CSV has a header but no data rows")
    return rows


def split_rows(rows: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    return {
        split: [row for row in rows if row["split"] == split]
        for split in ("train", "val", "test")
    }


def text_for(row: dict[str, object], fields: tuple[str, ...]) -> str:
    """Join only selected text fields, preserving a stable field order."""
    return "\n".join(
        f"{name}: {str(row.get(name, '')).strip()}"
        for name in fields
        if str(row.get(name, "")).strip()
    )
