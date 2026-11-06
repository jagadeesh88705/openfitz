"""openfitz - A fast, lightweight Python library for PDF parsing, spatial extraction, and raster rendering."""

from fitz import (
    Document,
    Matrix,
    Page,
    Pixmap,
    Point,
    Rect,
    TEXT_ALIGN_CENTER,
    TEXT_ALIGN_JUSTIFY,
    TEXT_ALIGN_LEFT,
    TEXT_ALIGN_RIGHT,
    TEXT_FONT_BOLD,
    TEXT_FONT_ITALIC,
    __version__,
    csGRAY,
    csRGB,
    open,
)

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

