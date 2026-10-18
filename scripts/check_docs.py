"""Validate documentation JSON/SVG assets and local Markdown links."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "runs", "build", "dist"}
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def project_files(suffix: str) -> list[Path]:
    return [
        path
        for path in ROOT.rglob(f"*{suffix}")
        if path.is_file() and not SKIP_DIRS.intersection(path.relative_to(ROOT).parts)
    ]


def check_docs(root: Path = ROOT) -> list[str]:
    problems: list[str] = []
    files = lambda suffix: [
        p for p in root.rglob(f"*{suffix}")
        if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(root).parts)
    ]

    json_files = files(".json")
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            problems.append(f"invalid JSON {path.relative_to(root)}: {exc}")

    svg_files = files(".svg")
    for path in svg_files:
        try:
            ET.parse(path)
        except (OSError, ET.ParseError) as exc:
            problems.append(f"invalid SVG {path.relative_to(root)}: {exc}")

    for markdown in files(".md"):
        try:
            content = markdown.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            problems.append(f"unreadable Markdown {markdown.relative_to(root)}: {exc}")
            continue
        for raw_target in MARKDOWN_LINK.findall(content):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            local_path = (markdown.parent / parsed.path).resolve()
            if not local_path.exists():
                problems.append(
                    f"broken local link in {markdown.relative_to(root)}: {raw_target}"
                )
    return problems


def main() -> int:
    problems = check_docs()
    if problems:
        print("Documentation checks found issues:")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print(
        f"Documentation checks passed: {len(project_files('.json'))} JSON files, "
        f"{len(project_files('.svg'))} SVG files, local Markdown links resolved."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
