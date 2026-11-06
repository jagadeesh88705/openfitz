import pytest
import fitz


def test_spatial_dict_structure(sample_pdf_bytes):
    """
    Tests that get_text('dict') produces a structured dictionary schema
    containing blocks, lines, and spans with bounding box metadata.
    """
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        page = doc[0]
        page_dict = page.get_text("dict")

        assert "blocks" in page_dict
        assert "width" in page_dict
        assert "height" in page_dict
        assert len(page_dict["blocks"]) > 0

        # Validate lines and spans inside blocks
        found_span = False
        for block in page_dict["blocks"]:
            assert "lines" in block
            assert "bbox" in block
            for line in block["lines"]:
                assert "spans" in line
                assert "bbox" in line
                for span in line["spans"]:
                    assert "text" in span
                    assert "bbox" in span
                    assert "size" in span
                    assert "font" in span
                    # Bounding box must be (x0, y0, x1, y1) with x0 <= x1, y0 <= y1
                    x0, y0, x1, y1 = span["bbox"]
                    assert x0 <= x1
                    assert y0 <= y1
                    found_span = True

        assert found_span is True


def test_checkbox_darkness_detection(sample_pdf_bytes):
    """
    Tests visual checkbox detection via raster rendering:
        fitz_rect = fitz.Rect(rect[0], rect[1], rect[2], rect[3])
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat, clip=fitz_rect)
        img_data = pix.samples
        total_pixels = len(img_data) // 3
        dark_pixels = sum(1 for i in range(0, len(img_data), 3) if img_data[i] < 200)
        darkness_ratio = dark_pixels / total_pixels
    """
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        page = doc[0]

        # 1. Check the box drawn at (50, 250, 65, 265)
        rect = (50, 250, 65, 265)
        fitz_rect = fitz.Rect(rect[0], rect[1], rect[2], rect[3])
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat, clip=fitz_rect)

        assert pix.samples is not None
        assert len(pix.samples) > 0

        img_data = pix.samples
        total_pixels = len(img_data) // 3
        assert total_pixels > 0
        dark_pixels = sum(1 for i in range(0, len(img_data), 3) if img_data[i] < 200)
        darkness_ratio = dark_pixels / total_pixels

        # The box has borders and an 'X' inside, so darkness_ratio > 0.05
        assert darkness_ratio > 0.05, f"Expected checked box, got ratio {darkness_ratio}"

        # 2. Check an empty white space at (50, 300, 65, 315)
        empty_rect = fitz.Rect(50, 300, 65, 315)
        empty_pix = page.get_pixmap(matrix=mat, clip=empty_rect)
        empty_data = empty_pix.samples
        empty_total = len(empty_data) // 3
        empty_dark = sum(1 for i in range(0, len(empty_data), 3) if empty_data[i] < 200)
        empty_ratio = empty_dark / empty_total

        # Empty white area should have ratio 0.0
        assert empty_ratio < 0.01, f"Expected empty space, got ratio {empty_ratio}"
