# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF TextResourceParser.
#
# Responsibilities:
# - Validate plain-text parser identity and version.
# - Validate supported and unsupported media types.
# - Validate UTF-8 text parsing.
# - Validate ResourceIdentity preservation.
# - Validate source and parsed media-type preservation.
# - Validate deterministic parsed content.
# - Validate invalid input and malformed UTF-8 rejection.
#
# Must Not:
# - Test physical source acquisition.
# - Test PDF, DOCX, CSV, HTML, or other parsers.
# - Test parser registry behavior.
# - Test semantic normalization.
# - Test chunking, embedding, indexing, or retrieval.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.parsers.text_resource_parser import (
    TextResourceParser,
)


def _resource(
    *,
    content: bytes = b"enterprise knowledge",
    media_type: str = "text/plain",
) -> AcquiredResource:
    return AcquiredResource(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=content,
        media_type=media_type,
        content_fingerprint="sha256:abc123",
    )


def test_parser_exposes_stable_identity() -> None:
    parser = TextResourceParser()

    assert parser.parser_ref == "text-resource-parser"
    assert parser.parser_version == "1.0"


def test_parser_supports_plain_text() -> None:
    parser = TextResourceParser()

    assert parser.supports("text/plain") is True


def test_media_type_support_is_case_insensitive() -> None:
    parser = TextResourceParser()

    assert parser.supports("TEXT/PLAIN") is True


def test_media_type_support_normalizes_whitespace() -> None:
    parser = TextResourceParser()

    assert parser.supports("  text/plain  ") is True


def test_parser_rejects_unsupported_media_type() -> None:
    parser = TextResourceParser()

    assert parser.supports("application/pdf") is False


@pytest.mark.parametrize(
    "media_type",
    (
        "",
        "   ",
        None,
        123,
    ),
)
def test_supports_returns_false_for_invalid_media_type(
    media_type: object,
) -> None:
    parser = TextResourceParser()

    assert parser.supports(media_type) is False


def test_parse_returns_parsed_resource() -> None:
    parser = TextResourceParser()

    parsed = parser.parse(
        _resource(),
    )

    assert isinstance(
        parsed,
        ParsedResource,
    )


def test_parse_preserves_resource_identity() -> None:
    parser = TextResourceParser()
    resource = _resource()

    parsed = parser.parse(
        resource,
    )

    assert parsed.identity is resource.identity
    assert parsed.resource_ref == "resource-001"
    assert parsed.revision_ref == "revision-001"


def test_parse_preserves_utf8_content() -> None:
    parser = TextResourceParser()
    content = "Enterprise knowledge ✓".encode("utf-8")

    parsed = parser.parse(
        _resource(
            content=content,
        ),
    )

    assert parsed.content == content


def test_parse_uses_canonical_text_media_type() -> None:
    parser = TextResourceParser()

    parsed = parser.parse(
        _resource(),
    )

    assert parsed.content_media_type == "text/plain"


def test_parse_preserves_source_media_type() -> None:
    parser = TextResourceParser()

    parsed = parser.parse(
        _resource(),
    )

    assert parsed.source_media_type == "text/plain"


def test_parse_records_parser_identity() -> None:
    parser = TextResourceParser()

    parsed = parser.parse(
        _resource(),
    )

    assert parsed.parser_ref == parser.parser_ref
    assert parsed.parser_version == parser.parser_version


def test_empty_text_content_is_supported() -> None:
    parser = TextResourceParser()

    parsed = parser.parse(
        _resource(
            content=b"",
        ),
    )

    assert parsed.content == b""
    assert parsed.size_bytes == 0


def test_invalid_resource_contract_is_rejected() -> None:
    parser = TextResourceParser()

    with pytest.raises(
        TypeError,
        match="resource must be an instance of AcquiredResource",
    ):
        parser.parse(
            "invalid-resource",
        )


def test_unsupported_resource_media_type_is_rejected() -> None:
    parser = TextResourceParser()

    with pytest.raises(
        ValueError,
        match="unsupported media type for TextResourceParser",
    ):
        parser.parse(
            _resource(
                media_type="application/pdf",
            ),
        )


def test_invalid_utf8_content_is_rejected() -> None:
    parser = TextResourceParser()

    with pytest.raises(
        ValueError,
        match="text resource must contain valid UTF-8 content",
    ):
        parser.parse(
            _resource(
                content=b"\xff\xfe\xfd",
            ),
        )


def test_repeated_parsing_is_deterministic() -> None:
    parser = TextResourceParser()
    resource = _resource(
        content=b"stable knowledge",
    )

    first = parser.parse(resource)
    second = parser.parse(resource)

    assert first == second
