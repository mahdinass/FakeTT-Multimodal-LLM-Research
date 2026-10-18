"""Defensive parsing and normalization for structured model responses."""

from __future__ import annotations

import json
import math
import re
from typing import Any


class StructuredOutputError(ValueError):
    """Raised when a model response cannot be safely interpreted."""


def _extract_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)\s*```", candidate, flags=re.IGNORECASE | re.DOTALL)
    if fence:
        candidate = fence.group(1).strip()
    decoder = json.JSONDecoder()
    starts = [match.start() for match in re.finditer(r"\{", candidate)]
    for start in starts:
        try:
            value, _ = decoder.raw_decode(candidate[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    raise StructuredOutputError("response did not contain a valid JSON object")


def normalize_response(value: str | dict[str, Any]) -> dict[str, Any]:
    """Validate a model label and confidence; never guess on malformed output."""
    parsed = _extract_object(value) if isinstance(value, str) else value
    if not isinstance(parsed, dict):
        raise StructuredOutputError("response must be a JSON object")
    label = str(parsed.get("label", "")).strip().lower()
    if label not in {"fake", "real"}:
        raise StructuredOutputError("label must be either 'fake' or 'real'")
    confidence = parsed.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        raise StructuredOutputError("confidence must be a number between 0 and 1")
    confidence = float(confidence)
    if not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise StructuredOutputError("confidence must be a finite number between 0 and 1")
    fake_probability = confidence if label == "fake" else 1.0 - confidence
    return {
        **parsed,
        "label": label,
        "confidence": confidence,
        "fake_probability": fake_probability,
    }
