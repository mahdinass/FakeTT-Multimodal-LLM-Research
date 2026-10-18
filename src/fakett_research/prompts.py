"""Versioned, independently authored prompt rendering and train-only exemplar retrieval."""

from __future__ import annotations

import re
from pathlib import Path

from .data import text_for


PROMPT_DIR = Path(__file__).resolve().parent / "prompts" / "v1"
FIELDS = ("description", "asr", "ocr")
TOKEN = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _tokens(text: str) -> set[str]:
    return {token.lower() for token in TOKEN.findall(text)}


def select_examples(
    query: dict[str, object],
    train_rows: list[dict[str, object]],
    strategy: str,
    n_shot: int,
) -> list[dict[str, object]]:
    """Select zero/fixed/dynamic exemplars from training rows only."""
    if n_shot < 0:
        raise ValueError("n_shot must be non-negative")
    if n_shot == 0 or strategy == "none":
        return []
    candidates = [row for row in train_rows if row["sample_id"] != query.get("sample_id")]
    if strategy == "fixed":
        return candidates[:n_shot]
    if strategy != "dynamic":
        raise ValueError("few-shot strategy must be none, fixed, or dynamic")
    query_tokens = _tokens(text_for(query, FIELDS))

    def score(row: dict[str, object]) -> tuple[float, str]:
        tokens = _tokens(text_for(row, FIELDS))
        overlap = len(query_tokens & tokens) / max(1, len(query_tokens | tokens))
        return overlap, str(row["sample_id"])

    return sorted(candidates, key=lambda row: (-score(row)[0], score(row)[1]))[:n_shot]


def render_prompt(
    family: str,
    branch: str,
    row: dict[str, object],
    examples: list[dict[str, object]],
) -> str:
    if family not in {"a", "b", "c"}:
        raise ValueError("prompt family must be a, b, or c")
    file_name = f"family_{family}_{branch}.txt"
    path = PROMPT_DIR / file_name
    template = path.read_text(encoding="utf-8")
    evidence = text_for(row, FIELDS) or "No text evidence was supplied."
    example_block = "No examples provided."
    if examples:
        example_block = "\n\n".join(
            f"Example {index}:\n{text_for(example, FIELDS)}\nLabel: {example['label']}"
            for index, example in enumerate(examples, start=1)
        )
    return (
        template.replace("{{EVIDENCE}}", evidence)
        .replace("{{EXAMPLES}}", example_block)
        .replace("{{SAMPLE_ID}}", str(row.get("sample_id", "unknown")))
    )
