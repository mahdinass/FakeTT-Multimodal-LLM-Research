"""Create tiny, original PNG icons used only by the synthetic demonstration."""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


def _chunk(kind: bytes, data: bytes) -> bytes:
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)


def _write_png(path: Path, pixels: list[list[tuple[int, int, int]]]) -> None:
    height, width = len(pixels), len(pixels[0])
    raw = b"".join(b"\x00" + bytes(channel for pixel in row for channel in pixel) for row in pixels)
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", zlib.compress(raw, level=9))
        + _chunk(b"IEND", b"")
    )


def generate(output_dir: str | Path) -> list[Path]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    width, height = 96, 64
    background = (244, 247, 250)
    fake = [[background for _ in range(width)] for _ in range(height)]
    real = [[background for _ in range(width)] for _ in range(height)]
    # The triangle and circle are abstract symbols, not frames or dataset examples.
    for y in range(10, 55):
        for x in range(22, 74):
            if abs(x - 48) <= (y - 10) * 0.58:
                fake[y][x] = (207, 69, 72)
            if (x - 48) ** 2 + (y - 32) ** 2 <= 22**2:
                real[y][x] = (29, 133, 115)
    paths = [target / "fake-symbol.png", target / "real-symbol.png"]
    _write_png(paths[0], fake)
    _write_png(paths[1], real)
    return paths


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    for asset in generate(root / "data" / "synthetic" / "images"):
        print(asset.relative_to(root))
