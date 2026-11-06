from pathlib import Path
import pytest


@pytest.fixture
def sample_pdf_path():
    fixture_file = Path(__file__).parent / "fixtures" / "sample.pdf"
    return fixture_file


@pytest.fixture
def sample_pdf_bytes(sample_pdf_path):
    with open(sample_pdf_path, "rb") as f:
        return f.read()
