import pytest
import fitz


def test_page_text_full(sample_pdf_bytes):
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        p0 = doc[0]
        text = p0.get_text("text")
        assert "Form 1065" in text
        assert "Acme Holdings LLC" in text
        assert "12-3456789" in text
        assert "$1,250,000.00" in text


def test_page_text_clipped(sample_pdf_bytes):
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        p0 = doc[0]
        # Target EIN field box at (300, 100, 500, 130)
        ein_rect = fitz.Rect(290, 95, 510, 135)
        ein_text = p0.get_text("text", clip=ein_rect).strip()
        assert "12-3456789" in ein_text
        assert "Acme Holdings" not in ein_text


def test_page_search_for(sample_pdf_bytes):
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        p0 = doc[0]
        matches = p0.search_for("Acme Holdings")
        assert len(matches) >= 1
        m = matches[0]
        assert isinstance(m, fitz.Rect)
        assert m.intersects(fitz.Rect(50, 100, 250, 130))


def test_page_get_text_blocks(sample_pdf_bytes):
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        p0 = doc[0]
        blocks = p0.get_text("blocks")
        assert len(blocks) >= 3
        # Each block tuple: (x0, y0, x1, y1, text, block_no, block_type)
        first = blocks[0]
        assert len(first) == 7
        assert isinstance(first[4], str)

