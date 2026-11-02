# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF PdfResourceParser.
#
# Responsibilities:
# - Validate PDF media-type compatibility.
# - Validate deterministic text extraction behavior.
# - Validate ResourceIdentity preservation.
# - Validate ParsedResource output semantics.
# - Validate page-order preservation.
# - Validate invalid, empty, encrypted, and textless PDFs.
# - Validate extraction failure handling.
#
# Must Not:
# - Perform acquisition or normalization.
# - Perform OCR.
# - Test chunking, representation, indexing, or retrieval.
# - Test downstream RAG behavior.
# - Depend on external RAG frameworks.

from io import BytesIO

import pytest
from pypdf import PdfWriter

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.parsers.pdf_resource_parser import (
    PdfResourceParser,
)


def _identity() -> ResourceIdentity:
    return ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )


def _blank_pdf() -> bytes:
    stream = BytesIO()

    writer = PdfWriter()
    writer.add_blank_page(
        width=72,
        height=72,
    )
    writer.write(
        stream
    )

    return stream.getvalue()


def _resource(
    *,
    content: bytes | None = None,
    media_type: str = "application/pdf",
) -> AcquiredResource:
    return AcquiredResource(
        identity=_identity(),
        content=(
            _blank_pdf()
            if content is None
            else content
        ),
        media_type=media_type,
        content_fingerprint="sha256:test",
    )


def test_parser_exposes_stable_identity() -> None:
    parser = PdfResourceParser()

    assert parser.parser_ref == "pdf-resource-parser"
    assert parser.parser_version == "1.0"


def test_parser_supports_pdf_media_type() -> None:
    parser = PdfResourceParser()

    assert parser.supports(
        "application/pdf"
    ) is True
    assert parser.supports(
        "  APPLICATION/PDF  "
    ) is True


def test_parser_rejects_unsupported_media_type() -> None:
    parser = PdfResourceParser()

    assert parser.supports(
        "text/plain"
    ) is False
    assert parser.supports(
        123
    ) is False


def test_invalid_resource_type_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "resource must be an instance of "
            "AcquiredResource"
        ),
    ):
        PdfResourceParser().parse(
            "invalid-resource"
        )


def test_resource_with_unsupported_media_type_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "unsupported media type for "
            "PdfResourceParser"
        ),
    ):
        PdfResourceParser().parse(
            _resource(
                media_type="text/plain",
            )
        )


def test_empty_pdf_content_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="PDF resource content cannot be empty",
    ):
        PdfResourceParser().parse(
            _resource(
                content=b"",
            )
        )


def test_invalid_pdf_content_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="invalid PDF resource content",
    ):
        PdfResourceParser().parse(
            _resource(
                content=b"not-a-pdf",
            )
        )


def test_pdf_without_extractable_text_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "PDF resource contains no extractable text"
        ),
    ):
        PdfResourceParser().parse(
            _resource()
        )


def test_parsed_resource_preserves_identity(
    monkeypatch,
) -> None:
    class Page:
        def extract_text(self):
            return "Enterprise authentication policy"

    class Reader:
        is_encrypted = False
        pages = (
            Page(),
        )

    monkeypatch.setattr(
        PdfResourceParser,
        "_reader",
        staticmethod(
            lambda content: Reader()
        ),
    )

    resource = _resource()

    parsed = PdfResourceParser().parse(
        resource
    )

    assert parsed.identity is resource.identity
    assert parsed.resource_ref == resource.resource_ref
    assert parsed.revision_ref == resource.revision_ref


def test_parsed_resource_contains_utf8_text(
    monkeypatch,
) -> None:
    class Page:
        def extract_text(self):
            return "Enterprise authentication policy"

    class Reader:
        is_encrypted = False
        pages = (
            Page(),
        )

    monkeypatch.setattr(
        PdfResourceParser,
        "_reader",
        staticmethod(
            lambda content: Reader()
        ),
    )

    parsed = PdfResourceParser().parse(
        _resource()
    )

    assert parsed.content == (
        b"Enterprise authentication policy"
    )
    assert parsed.content_media_type == "text/plain"
    assert parsed.source_media_type == "application/pdf"
    assert parsed.parser_ref == "pdf-resource-parser"
    assert parsed.parser_version == "1.0"


def test_multiple_pages_are_joined_deterministically(
    monkeypatch,
) -> None:
    class Page:
        def __init__(
            self,
            text: str,
        ) -> None:
            self._text = text

        def extract_text(self):
            return self._text

    class Reader:
        is_encrypted = False
        pages = (
            Page("  first page  "),
            Page("second page"),
        )

    monkeypatch.setattr(
        PdfResourceParser,
        "_reader",
        staticmethod(
            lambda content: Reader()
        ),
    )

    parsed = PdfResourceParser().parse(
        _resource()
    )

    assert parsed.content == (
        b"first page\n\nsecond page"
    )


def test_encrypted_pdf_is_rejected(
    monkeypatch,
) -> None:
    class Reader:
        is_encrypted = True
        pages = ()

    monkeypatch.setattr(
        PdfResourceParser,
        "_reader",
        staticmethod(
            lambda content: Reader()
        ),
    )

    with pytest.raises(
        ValueError,
        match="encrypted PDF resources are not supported",
    ):
        PdfResourceParser().parse(
            _resource()
        )


def test_extraction_failure_is_wrapped(
    monkeypatch,
) -> None:
    class Page:
        def extract_text(self):
            raise RuntimeError(
                "test extraction failure"
            )

    class Reader:
        is_encrypted = False
        pages = (
            Page(),
        )

    monkeypatch.setattr(
        PdfResourceParser,
        "_reader",
        staticmethod(
            lambda content: Reader()
        ),
    )

    with pytest.raises(
        ValueError,
        match="PDF text extraction failed",
    ):
        PdfResourceParser().parse(
            _resource()
        )
