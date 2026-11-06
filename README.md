# openfitz 🚀
*A Permissive (MIT) Drop-in Replacement for PyMuPDF (`fitz`) Powered by Google PDFium.*

[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://pypi.org/project/openfitz/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)](https://python.org)

---

## Why openfitz?

PyMuPDF (`fitz`) is an established library, but it is distributed under the **GNU AGPLv3**.
Under AGPL Section 13 (the Network Clause), linking PyMuPDF inside any backend service or SaaS application legally forces organizations to **open-source their entire proprietary backend codebase** or purchase commercial licenses costing thousands of dollars annually.

**openfitz** eliminates this problem:
- **100% Permissive (MIT License)**: Completely safe for commercial applications, private SaaS backends, and microservices.
- **Powered by Google PDFium**: Uses the battle-tested, high-performance C++ engine that powers **Google Chrome's PDF viewer** (`pypdfium2`).
- **Drop-in Namespace**: Installs as `fitz` so existing code continues to work **without changing a single line of application code**.

---

## Installation

```bash
# Uninstall AGPL PyMuPDF (if installed)
pip uninstall pymupdf

# Install openfitz (MIT)
pip install openfitz
```

---

## Quickstart

Your application code does **not** need to change:

```python
import fitz

# 1. Open from file or byte stream
doc = fitz.open("invoice.pdf")
print("Total pages:", doc.page_count)

# 2. Extract plain text or clipped bounding-box text
page = doc[0]
full_text = page.get_text("text")

# Exact clipped extraction (top-left coordinate system)
box_rect = fitz.Rect(50, 100, 300, 150)
field_text = page.get_text("text", clip=box_rect)

# 3. Spatial extraction hierarchy (blocks, lines, spans)
page_dict = page.get_text("dict")
for block in page_dict["blocks"]:
    for line in block["lines"]:
        for span in line["spans"]:
            print(f"Span: {span['text']} | BBox: {span['bbox']} | Font: {span['font']}")

# 4. Render to Pixmap (for checkbox/darkness detection or image export)
mat = fitz.Matrix(2, 2)
pix = page.get_pixmap(matrix=mat, clip=box_rect)
print("Raw RGB samples length:", len(pix.samples))
pix.save("extracted_field.png")

# 5. Bookmarks & Table of Contents
toc = doc.get_toc(simple=True)
# [[1, 'Section 1', 1], [2, 'Details', 2]]

doc.close()
```

---

## Feature Comparison

| Feature | PyMuPDF (`fitz`) | openfitz |
| :--- | :--- | :--- |
| **License** | ❌ **GNU AGPLv3** (Copyleft) | ✅ **MIT** (Permissive) |
| **Commercial SaaS Safe** | ❌ Requires costly license | ✅ 100% Safe & Free |
| **Core Engine** | MuPDF C library | Google Chrome PDFium C++ |
| **Top-Level `fitz` Import** | Yes | Yes (Drop-in) |
| **Top-Left Coordinate System** | Yes | Yes (Zero coordinate drift) |
| **`page.get_text("text", clip=...)`** | Yes | Yes |
| **`page.get_text("dict")`** | Yes | Yes (Blocks, lines, spans) |
| **`page.get_pixmap().samples`** | Yes | Yes (Raw packed RGB bytes) |
| **`doc.get_toc(simple=True)`** | Yes | Yes (`[[lvl, title, page], ...]`) |
| **`fitz.Rect` & `fitz.Matrix`** | Yes | Yes |

---

## Coordinate Precision Benchmark

Unlike pure-Python libraries like `pdfplumber` or `pdfminer`, which frequently experience coordinate offset bugs on cropped or rotated pages:

```text
Field           | PyMuPDF Extracted         | openfitz Extracted        | Match?
-----------------------------------------------------------------------------------
Name            | Partnership Alpha LLC     | Partnership Alpha LLC     | PASS ✅
EIN             | 12-3456789                | 12-3456789                | PASS ✅
Address         | 123 Market St, Suite 400  | 123 Market St, Suite 400  | PASS ✅
Total Income    | $1,250,000.00             | $1,250,000.00             | PASS ✅
Net Profit      | $480,250.50               | $480,250.50               | PASS ✅
```

---

## Testing

Run the test suite locally:

```bash
git clone https://github.com/jagadeesh88705/openfitz.git
cd openfitz
pip install -e .[dev]
pytest -v
```

---

## License

MIT License. Copyright (c) 2026 Jagadeesh Murugesan.
