"""Configurable OpenAI-compatible chat completions client with bounded retries."""

from __future__ import annotations

import base64
import mimetypes
import os
import time
from pathlib import Path
from typing import Any

import requests


class InferenceError(RuntimeError):
    """Raised when the configured endpoint cannot return a usable completion."""


class OpenAICompatibleClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 90.0,
        retries: int = 2,
        session: Any = requests,
    ) -> None:
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        self.model = model or os.getenv("OPENAI_MODEL", "")
        self.timeout = timeout
        self.retries = retries
        self.session = session

    @staticmethod
    def _image_url(path: str | Path) -> str:
        image = Path(path).expanduser()
        if not image.is_file():
            raise FileNotFoundError(f"image does not exist: {image}")
        mime, _ = mimetypes.guess_type(image.name)
        if mime not in {"image/jpeg", "image/png", "image/webp", "image/gif"}:
            raise ValueError(f"unsupported image type for multimodal request: {image.suffix}")
        encoded = base64.b64encode(image.read_bytes()).decode("ascii")
        return f"data:{mime};base64,{encoded}"

    def complete(
        self,
        prompt: str,
        image_paths: list[str] | None = None,
        *,
        seed: int = 42,
        sample_id: str = "",
        branch: str = "combined",
    ) -> str:
        if not self.api_key:
            raise InferenceError("OPENAI_API_KEY is not configured")
        if not self.model:
            raise InferenceError("OPENAI_MODEL or an explicit model name is required")
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        for path in image_paths or []:
            content.append({"type": "image_url", "image_url": {"url": self._image_url(path)}})
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "temperature": 0,
            "seed": seed,
            "stream": False,
        }
        endpoint = f"{self.base_url}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.post(
                    endpoint, json=payload, headers=headers, timeout=self.timeout
                )
                response.raise_for_status()
                body = response.json()
                content_value = body["choices"][0]["message"]["content"]
                if not isinstance(content_value, str) or not content_value.strip():
                    raise InferenceError("endpoint returned an empty or non-text completion")
                return content_value
            except (requests.RequestException, KeyError, IndexError, TypeError, ValueError) as error:
                last_error = error
                if attempt < self.retries:
                    time.sleep(0.5 * (2**attempt))
        raise InferenceError(
            f"completion failed after {self.retries + 1} attempt(s): {last_error}"
        ) from last_error
