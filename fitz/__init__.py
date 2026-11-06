"""openfitz - A permissive (MIT) drop-in replacement for PyMuPDF (fitz) powered by Google PDFium."""

from __future__ import annotations
import io
from pathlib import Path
from typing import Any, Optional, Union

from .constants import (
    TEXT_ALIGN_CENTER,
    TEXT_ALIGN_JUSTIFY,
    TEXT_ALIGN_LEFT,
    TEXT_ALIGN_RIGHT,
    TEXT_FONT_BOLD,
    TEXT_FONT_ITALIC,
    csGRAY,
    csRGB,
)
from .document import Document
from .geometry import Matrix, Point, Rect
from .page import Page
from .pixmap import Pixmap

__version__ = "0.1.0"
__doc_url__ = "https://github.com/jagadeesh88705/openfitz"


def open(
    filename: Optional[Union[str, Path]] = None,
    stream: Optional[Union[bytes, io.BytesIO]] = None,
    filetype: Optional[str] = "pdf",
    **kwargs: Any,
) -> Document:
    """
    Opens a PDF document from a file path or in-memory byte stream.
    Compatible with PyMuPDF's fitz.open().
    """
    return Document(filename=filename, stream=stream, filetype=filetype, **kwargs)


__all__ = [
    "open",
    "Document",
    "Page",
    "Rect",
    "Point",
    "Matrix",
    "Pixmap",
    "TEXT_ALIGN_LEFT",
    "TEXT_ALIGN_CENTER",
    "TEXT_ALIGN_RIGHT",
    "TEXT_ALIGN_JUSTIFY",
    "csRGB",
    "csGRAY",
    "TEXT_FONT_BOLD",
    "TEXT_FONT_ITALIC",
    "__version__",
]

