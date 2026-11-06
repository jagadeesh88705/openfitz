# openfitz 🚀
*A Fast, Lightweight Python Library for PDF Document Parsing, Spatial Text Extraction, and Raster Rendering Powered by Google PDFium.*

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/openfitz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://python.org)

---

## Features

- **Permissive MIT License**: 100% free for commercial use, private SaaS backends, and microservices.
- **Powered by Google PDFium**: Utilizes the battle-tested, high-performance C++ engine that powers Google Chrome's PDF viewer via `pypdfium2`.
- **Top-Left Coordinate System**: Native `(x0, y0, x1, y1)` bounding box coordinate mapping with zero coordinate inversion drift.
- **Spatial Text Extraction**: Extract text bounded by exact clipping rectangles or inspect full document block, line, and span hierarchies.
- **Raster Rendering & Pixel Inspection**: Render pages or clipped areas directly to memory bitmaps with raw packed RGB `.samples` for checkbox/darkness ratio analysis.
- **Bookmark / TOC Traversal**: Fast hierarchical Table of Contents and bookmark extraction.
- **Flexible Namespaces**: Usable as either `import fitz` or `import openfitz`.

---

## Installation

```bash
pip install openfitz
```

---

## Quickstart

```python
import fitz

# 1. Open a PDF document (from file path or bytes)
doc = fitz.open("sample.pdf")
print("Total pages:", doc.page_count)

# 2. Extract full page text or bounded text
page = doc[0]
full_text = page.get_text("text")

# Clipped extraction (top-left origin coordinates)
field_rect = fitz.Rect(50, 100, 300, 150)
field_text = page.get_text("text", clip=field_rect)
print("Extracted field:", field_text.strip())

# 3. Spatial text hierarchy (blocks, lines, spans)
page_dict = page.get_text("dict")
for block in page_dict["blocks"]:
    for line in block["lines"]:
        for span in line["spans"]:
            print(f"Text: {span['text']} | Box: {span['bbox']} | Font: {span['font']}")

# 4. Render to Pixmap (for image export or darkness/checkbox detection)
mat = fitz.Matrix(2, 2)  # 2x zoom
pix = page.get_pixmap(matrix=mat, clip=field_rect)
print("Pixel buffer length:", len(pix.samples))
pix.save("field_preview.png")

# 5. Extract Bookmarks / Table of Contents
toc = doc.get_toc(simple=True)
for level, title, page_num in toc:
    print(f"Level {level}: {title} (page {page_num})")

doc.close()
```

---

## Architecture

`openfitz` wraps Google PDFium's C++ rasterization and layout engine into clean, Pythonic classes:

| Class | Description |
| :--- | :--- |
| **`fitz.Document`** | Manages document lifecycle, page loading (`doc[i]`), saving, and bookmark traversal. |
| **`fitz.Page`** | Provides bounded text extraction, character spatial search, and rasterization. |
| **`fitz.Rect`** | Represents 2D bounding boxes `(x0, y0, x1, y1)` with intersection and union math. |
| **`fitz.Matrix`** | Represents 2D affine transformation matrices for scaling and rotation. |
| **`fitz.Pixmap`** | Contains rasterized image pixels, supporting raw `.samples` byte buffers and image export. |

---

## Running Tests

```bash
git clone https://github.com/jagadeesh88705/openfitz.git
cd openfitz
pip install -e .[dev]
pytest -v
```

---

## License

MIT License. Copyright (c) 2026 Jagadeesh Murugesan.
