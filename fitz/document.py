"""Document implementation wrapping pypdfium2 with high-level Pythonic interface."""

from __future__ import annotations
import io
from pathlib import Path
from typing import Any, Iterator, List, Optional, Union

import pypdfium2 as pdfium

from .page import Page


class Document:
    """Represents a PDF document with page access, bookmark traversal, and save operations."""

    def __init__(
        self,
        filename: Optional[Union[str, Path]] = None,
        stream: Optional[Union[bytes, io.BytesIO]] = None,
        filetype: Optional[str] = "pdf",
        **kwargs: Any,
    ):
        self._filename = str(filename) if filename is not None else None
        self._is_closed = False

        if stream is not None:
            if isinstance(stream, bytes):
                self._doc = pdfium.PdfDocument(stream)
            elif hasattr(stream, "read"):
                content = stream.read()
                self._doc = pdfium.PdfDocument(content)
            else:
                self._doc = pdfium.PdfDocument(stream)
        elif filename is not None:
            self._doc = pdfium.PdfDocument(str(filename))
        else:
            # Create an empty document
            self._doc = pdfium.PdfDocument.new()

        self._pages_cache: dict[int, Page] = {}

    @property
    def page_count(self) -> int:
        """Total number of pages in the document."""
        if self._is_closed:
            return 0
        return len(self._doc)

    def __len__(self) -> int:
        return self.page_count

    def load_page(self, page_id: int) -> Page:
        """Loads and returns a Page object by page index (0-indexed)."""
        if self._is_closed:
            raise ValueError("Document is closed")
        if not (0 <= page_id < self.page_count):
            raise IndexError(f"Page index {page_id} out of range (0..{self.page_count - 1})")

        if page_id not in self._pages_cache:
            raw_page = self._doc[page_id]
            self._pages_cache[page_id] = Page(raw_page, page_id, parent_doc=self)
        return self._pages_cache[page_id]

    def __getitem__(self, page_id: int) -> Page:
        return self.load_page(page_id)

    def __iter__(self) -> Iterator[Page]:
        for i in range(self.page_count):
            yield self.load_page(i)

    def get_toc(self, simple: bool = True) -> List[Any]:
        """
        Returns the table of contents / bookmarks.
        When simple=True, returns list of [level, title, page_number] where
        level >= 1 and page_number is 1-indexed.
        """
        if self._is_closed:
            return []

        toc_list: List[Any] = []
        try:
            for item in self._doc.get_toc():
                level = int(item.level) + 1  # 1-based hierarchy level
                title = str(item.title) if item.title else ""
                page_num = (int(item.page_index) + 1) if item.page_index is not None else 1
                if simple:
                    toc_list.append([level, title, page_num])
                else:
                    toc_list.append([level, title, page_num, item.view_pos or {}])
        except Exception:
            pass

        return toc_list

    def save(self, target: Union[str, Path, io.BytesIO], **kwargs: Any) -> None:
        """Saves the PDF document to a file or stream."""
        if self._is_closed:
            raise ValueError("Document is closed")

        if isinstance(target, (str, Path)):
            with open(target, "wb") as f:
                self._doc.save(f)
        elif hasattr(target, "write"):
            self._doc.save(target)
        else:
            raise TypeError(f"Unsupported save target type: {type(target)}")

    def tobytes(self) -> bytes:
        """Returns the PDF document as bytes."""
        buf = io.BytesIO()
        self.save(buf)
        return buf.getvalue()

    def close(self) -> None:
        """Closes the document and releases resources."""
        if not self._is_closed:
            self._pages_cache.clear()
            try:
                self._doc.close()
            except Exception:
                pass
            self._is_closed = True

    def __enter__(self) -> Document:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        state = "closed" if self._is_closed else f"pages={self.page_count}"
        return f"Document({self._filename or 'stream'}, {state})"
