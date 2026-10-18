"""Scan the release tree for common accidental data, secret, and artifact inclusions."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "runs", "build", "dist"}
BLOCKED_SUFFIXES = {
    ".mp4", ".mov", ".avi", ".mkv", ".pkl", ".joblib", ".parquet", ".sqlite", ".db", ".npy", ".npz"
}
BLOCKED_DATA_DIRS = {"authorized", "private", "raw", "processed", "keyframes", "frames", "metadata"}
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"(?i)authorization\s*:\s*bearer\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"(?i)(?:api[_-]?key|token|password)\s*[=:]\s*['\"][^'\"]{12,}['\"]"),
)


def audit(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in SKIP_DIRS for part in relative.parts):
            continue
        lower = path.name.lower()
        rel = relative.as_posix().lower()
        if BLOCKED_DATA_DIRS.intersection(part.lower() for part in relative.parts):
            problems.append(f"restricted data directory included: {relative}")
        if relative.parts[0].lower() == "data" and not rel.startswith("data/synthetic/"):
            problems.append(f"non-synthetic data tree included: {relative}")
        if lower == ".env" or (lower.startswith(".env.") and lower != ".env.example"):
            problems.append(f"credential file included: {relative}")
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            problems.append(f"restricted/generated artifact extension included: {relative}")
        if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"} and not rel.startswith(
            "data/synthetic/images/"
        ):
            problems.append(f"non-synthetic image included: {relative}")
        if path.stat().st_size > 2_000_000:
            problems.append(f"large file requires manual review: {relative}")
        if path.suffix.lower() not in {".txt", ".md", ".py", ".toml", ".yml", ".yaml", ".csv", ".json", ".svg"}:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            problems.append(f"text file is not UTF-8: {relative}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(content):
                problems.append(f"possible credential pattern in: {relative}")
                break
        institutional_host = "openwebui.ux." + "uis.no"
        if institutional_host in content.lower():
            problems.append(f"institutional endpoint in release content: {relative}")
        if re.search(r"(?i)[A-Z]:\\Users\\[^\\\s]+", content):
            problems.append(f"local Windows user path in release content: {relative}")
    return problems


def main() -> int:
    problems = audit()
    if problems:
        print("Release audit found items to review:")
        for item in problems:
            print(f"- {item}")
        return 1
    print("Release content scan passed. This does not establish ownership or dataset rights.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
