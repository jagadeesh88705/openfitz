import io
import pytest
import fitz


def test_document_open_stream(sample_pdf_bytes):
    doc = fitz.open(stream=sample_pdf_bytes, filetype="pdf")
    assert doc.page_count == 2
    assert len(doc) == 2
    assert repr(doc).startswith("Document")

    # Access page 0 and page 1
    p0 = doc[0]
    p1 = doc.load_page(1)
    assert p0.number == 0
    assert p1.number == 1

    # Bounds check
    with pytest.raises(IndexError):
        doc.load_page(99)

    doc.close()


def test_document_context_manager(sample_pdf_bytes):
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        assert doc.page_count == 2
        pages = list(doc)
        assert len(pages) == 2
    # Verify closed
    assert doc.page_count == 0


def test_document_get_toc(sample_pdf_bytes):
    with fitz.open(stream=sample_pdf_bytes, filetype="pdf") as doc:
        toc = doc.get_toc(simple=True)
        assert len(toc) >= 2
        # Verify structure: [level, title, page]
        assert toc[0][0] == 1
        assert "Form 1065" in toc[0][1]
        assert toc[0][2] == 1


def test_document_save_and_reopen(tmp_path, sample_pdf_bytes):
    doc = fitz.open(stream=sample_pdf_bytes, filetype="pdf")
    out_file = tmp_path / "saved.pdf"
    doc.save(out_file)
    doc.close()

    assert out_file.exists()
    assert out_file.stat().st_size > 0

    reopened = fitz.open(out_file)
    assert reopened.page_count == 2
    reopened.close()
