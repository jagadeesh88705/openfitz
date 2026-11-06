"""Pixmap implementation for visual raster rendering and pixel analysis."""

from __future__ import annotations
import io
from pathlib import Path
from typing import Optional, Union
from PIL import Image


class Pixmap:
    """Represents a rendered raster image with raw RGB/RGBA samples."""

    def __init__(
        self,
        width: int,
        height: int,
        samples: bytes,
        n: int = 3,
        stride: Optional[int] = None,
    ):
        self.width = int(width)
        self.height = int(height)
        self.samples = samples
        self.n = int(n)  # 3 for RGB, 4 for RGBA, 1 for Gray
        self.stride = stride if stride is not None else (self.width * self.n)

    @classmethod
    def from_pil(cls, pil_img: Image.Image) -> Pixmap:
        """Constructs a Pixmap from a PIL Image object."""
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        w, h = pil_img.size
        samples = pil_img.tobytes()
        return cls(width=w, height=h, samples=samples, n=3, stride=w * 3)

    def to_pil(self) -> Image.Image:
        """Converts Pixmap to a PIL Image."""
        mode = "RGB" if self.n == 3 else ("RGBA" if self.n == 4 else "L")
        return Image.frombytes(mode, (self.width, self.height), self.samples)

    def save(self, filename: Union[str, Path], output_format: Optional[str] = None) -> None:
        """Saves the pixmap image to disk."""
        img = self.to_pil()
        img.save(filename, format=output_format)

    def tobytes(self, output_format: str = "png") -> bytes:
        """Returns the image as encoded bytes in the specified format."""
        img = self.to_pil()
        buf = io.BytesIO()
        img.save(buf, format=output_format)
        return buf.getvalue()

    def __repr__(self) -> str:
        return f"Pixmap(width={self.width}, height={self.height}, n={self.n}, samples_len={len(self.samples)})"

