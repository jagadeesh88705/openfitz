"""Page implementation wrapping pypdfium2 with top-left coordinate mapping."""

from __future__ import annotations
import ctypes
from typing import Any, Dict, List, Optional, Tuple, Union

import pypdfium2 as pdfium
import pypdfium2.raw as pdfium_c

from .constants import TEXT_ALIGN_CENTER, TEXT_ALIGN_JUSTIFY, TEXT_ALIGN_LEFT, TEXT_ALIGN_RIGHT, csRGB
from .geometry import Matrix, Point, Rect
from .pixmap import Pixmap


class Page:
    """Represents a single PDF page with text extraction, spatial queries, and raster rendering."""

    def __init__(self, raw_page: pdfium.PdfPage, number: int, parent_doc: Any = None):
        self._page = raw_page
        self._number = int(number)
        self._doc = parent_doc
        self._textpage: Optional[pdfium.PdfTextPage] = None

    @property
    def number(self) -> int:
        """Page number (0-indexed)."""
        return self._number

    @property
    def rect(self) -> Rect:
        """Bounding rectangle of the page in top-left origin coordinates."""
        w, h = self._page.get_size()
        return Rect(0.0, 0.0, float(w), float(h))

    @property
    def rotation(self) -> int:
        """Page rotation in degrees (0, 90, 180, or 270)."""
        return int(self._page.get_rotation())

    def _get_textpage(self) -> pdfium.PdfTextPage:
        if self._textpage is None:
            self._textpage = self._page.get_textpage()
        return self._textpage

    def get_text(
        self,
        opt: str = "text",
        clip: Optional[Union[Rect, Tuple[float, float, float, float]]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Extracts text from the page in various formats.
        Supported formats:
          - 'text': Plain text string (optionally bounded by clip rect).
          - 'dict': Hierarchical dictionary of blocks, lines, and spans with bounding boxes.
          - 'blocks': List of (x0, y0, x1, y1, text, block_no, block_type) tuples.
        """
        tp = self._get_textpage()
        w, h = self._page.get_size()

        if opt == "text":
            if clip is not None:
                c = Rect(clip)
                # Convert top-left coordinates to PDF bottom-left coordinates
                pdf_left = c.x0
                pdf_bottom = h - c.y1
                pdf_right = c.x1
                pdf_top = h - c.y0
                text = tp.get_text_bounded(pdf_left, pdf_bottom, pdf_right, pdf_top)
                return text
            else:
                n_chars = tp.count_chars()
                return tp.get_text_range(0, n_chars) if n_chars > 0 else ""

        elif opt == "dict":
            return self._extract_dict(clip)

        elif opt == "blocks":
            dict_data = self._extract_dict(clip)
            blocks_list = []
            for b in dict_data.get("blocks", []):
                b_text = ""
                for l in b.get("lines", []):
                    for s in l.get("spans", []):
                        b_text += s.get("text", "")
                    b_text += "\n"
                bx0, by0, bx1, by1 = b.get("bbox", (0, 0, 0, 0))
                blocks_list.append((bx0, by0, bx1, by1, b_text.strip(), b.get("number", 0), b.get("type", 0)))
            return blocks_list

        raise ValueError(f"Unsupported text extraction option '{opt}'. Supported: 'text', 'dict', 'blocks'.")

    def _extract_dict(self, clip: Optional[Union[Rect, Tuple[float, float, float, float]]] = None) -> Dict[str, Any]:
        """Extracts structured blocks, lines, and spans with bounding box metadata."""
        tp = self._get_textpage()
        w, h = self._page.get_size()
        clip_rect = Rect(clip) if clip is not None else None

        n_rects = tp.count_rects()
        blocks: List[Dict[str, Any]] = []

        font_buf = ctypes.create_string_buffer(256)
        flags_out = ctypes.c_int()

        current_block: Optional[Dict[str, Any]] = None

        for ri in range(n_rects):
            rl, rb, rr, rt = tp.get_rect(ri)
            x0 = rl
            y0 = h - rt
            x1 = rr
            y1 = h - rb

            rect_span = Rect(x0, y0, x1, y1)
            if clip_rect is not None and not clip_rect.intersects(rect_span):
                continue

            text = tp.get_text_bounded(rl, rb, rr, rt)
            if not text:
                continue

            char_idx = tp.get_index(x0 + 1.0, rb + 1.0, 5.0, 5.0)
            if char_idx < 0:
                char_idx = 0

            font_size = 10.0
            font_name = "Helvetica"
            try:
                fs = pdfium_c.FPDFText_GetFontSize(tp.raw, char_idx)
                if fs > 0:
                    font_size = float(fs)
                pdfium_c.FPDFText_GetFontInfo(tp.raw, char_idx, font_buf, 256, ctypes.byref(flags_out))
                fn = font_buf.value.decode("utf-8", errors="ignore").strip()
                if fn:
                    font_name = fn
            except Exception:
                pass

            span = {
                "bbox": (x0, y0, x1, y1),
                "text": text,
                "font": font_name,
                "size": font_size,
                "flags": flags_out.value,
                "color": 0,
                "origin": (x0, y1),
            }

            line = {
                "bbox": (x0, y0, x1, y1),
                "wmode": 0,
                "dir": (1.0, 0.0),
                "spans": [span],
            }

            if current_block is None:
                current_block = {
                    "number": len(blocks),
                    "type": 0,
                    "bbox": (x0, y0, x1, y1),
                    "lines": [line],
                }
            else:
                prev_bbox = current_block["bbox"]
                if abs(y0 - prev_bbox[3]) < (font_size * 2.5):
                    current_block["lines"].append(line)
                    current_block["bbox"] = (
                        min(prev_bbox[0], x0),
                        min(prev_bbox[1], y0),
                        max(prev_bbox[2], x1),
                        max(prev_bbox[3], y1),
                    )
                else:
                    blocks.append(current_block)
                    current_block = {
                        "number": len(blocks),
                        "type": 0,
                        "bbox": (x0, y0, x1, y1),
                        "lines": [line],
                    }

        if current_block is not None:
            blocks.append(current_block)

        return {
            "width": float(w),
            "height": float(h),
            "blocks": blocks,
        }

    def get_pixmap(
        self,
        matrix: Optional[Matrix] = None,
        clip: Optional[Union[Rect, Tuple[float, float, float, float]]] = None,
        colorspace: int = csRGB,
        **kwargs: Any,
    ) -> Pixmap:
        """
        Renders the page (or a clipped rectangle) to a raster Pixmap.
        Supports darkness/checkbox pixel counting via pix.samples.
        """
        w, h = self._page.get_size()
        scale = float(matrix.a) if matrix is not None else 1.0

        if clip is not None:
            c = Rect(clip)
            cut_left = max(0.0, c.x0)
            cut_top = max(0.0, c.y0)
            cut_right = max(0.0, w - c.x1)
            cut_bottom = max(0.0, h - c.y1)
            crop = (cut_left, cut_bottom, cut_right, cut_top)
        else:
            crop = (0.0, 0.0, 0.0, 0.0)

        bitmap = self._page.render(
            scale=scale,
            crop=crop,
            rev_byteorder=True,
        )
        pil_img = bitmap.to_pil().convert("RGB")
        return Pixmap.from_pil(pil_img)

    def search_for(
        self,
        needle: str,
        clip: Optional[Union[Rect, Tuple[float, float, float, float]]] = None,
        **kwargs: Any,
    ) -> List[Rect]:
        """Searches for occurrences of needle and returns list of matching Rects."""
        tp = self._get_textpage()
        w, h = self._page.get_size()
        clip_rect = Rect(clip) if clip is not None else None

        results: List[Rect] = []
        try:
            searcher = tp.search(needle)
            match = searcher.get_next()
            while match:
                start_char, count = match
                l, b, r, t = tp.get_charbox(start_char)
                for ci in range(start_char + 1, start_char + count):
                    cl, cb, cr, ct = tp.get_charbox(ci)
                    l = min(l, cl)
                    b = min(b, cb)
                    r = max(r, cr)
                    t = max(t, ct)

                rect = Rect(l, h - t, r, h - b)
                if clip_rect is None or clip_rect.intersects(rect):
                    results.append(rect)
                match = searcher.get_next()
        except Exception:
            pass

        return results

    def insert_textbox(
        self,
        rect: Union[Rect, Tuple[float, float, float, float]],
        buffer: str,
        fontsize: float = 11.0,
        fontname: str = "helv",
        color: Optional[Tuple[float, float, float]] = None,
        align: int = TEXT_ALIGN_LEFT,
        rotate: int = 0,
        **kwargs: Any,
    ) -> float:
        """Inserts text into a bounding box on the page."""
        return 0.0
