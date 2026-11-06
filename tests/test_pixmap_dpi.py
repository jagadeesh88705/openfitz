import io
import fitz
from PIL import Image


def test_get_pixmap_dpi_and_ppm_format(sample_pdf_bytes):
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        page = doc[0]
        pix = page.get_pixmap(dpi=150)
        assert pix.width > 0
        assert pix.height > 0

        # Verify PPM export used in ui_box_editor.py
        ppm_bytes = pix.tobytes("ppm")
        assert len(ppm_bytes) > 0
        img = Image.open(io.BytesIO(ppm_bytes))
        assert img.width == pix.width
        assert img.height == pix.height
