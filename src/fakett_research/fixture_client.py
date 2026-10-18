"""Read-only fixture client for deterministic demos and tests; never contacts a model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FixtureResponseClient:
    def __init__(self, fixture_path: str | Path) -> None:
        self.responses = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
        self.calls: list[tuple[str, str]] = []

    def complete(
        self,
        prompt: str,
        image_paths: list[str] | None = None,
        *,
        seed: int = 42,
        sample_id: str = "",
        branch: str = "combined",
    ) -> str:
        self.calls.append((sample_id, branch))
        try:
            response: Any = self.responses[sample_id][branch]
        except KeyError as error:
            raise RuntimeError(f"no fixture response for {sample_id}/{branch}") from error
        return json.dumps(response)
