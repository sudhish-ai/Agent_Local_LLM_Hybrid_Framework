# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF TextContentNormalizer.
#
# Responsibilities:
# - Validate text-normalizer identity and version.
# - Validate parsed text compatibility.
# - Validate canonical TEXT content generation.
# - Validate ResourceIdentity preservation.
# - Validate deterministic Unicode normalization.
# - Validate deterministic line-ending normalization.
# - Validate parsed-artifact provenance.
# - Validate invalid input and malformed UTF-8 rejection.
#
# Must Not:
# - Test physical source acquisition.
# - Test format-specific parsing.
# - Test semantic rewriting or summarization.
# - Test derivation or chunking.
# - Test embedding, indexing, retrieval, or reranking.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import unicodedata

import pytest

from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.normalizers.text_content_normalizer import (
    TextContentNormalizer,
)


def _resource(
    *,
    content: bytes = b"enterprise knowledge",
    content_media_type: str = "text/plain",
) -> ParsedResource:
    return ParsedResource(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=content,
        content_media_type=content_media_type,
        source_media_type="application/pdf",
        parser_ref="parser-001",
        parser_version="1.0",
    )


def test_normalizer_exposes_stable_identity() -> None:
    normalizer = TextContentNormalizer()

    assert normalizer.normalizer_ref == "text-content-normalizer"
    assert normalizer.normalizer_version == "1.0"


def test_normalizer_supports_plain_text() -> None:
    normalizer = TextContentNormalizer()

    assert normalizer.supports("text/plain") is True


def test_support_is_case_insensitive() -> None:
    normalizer = TextContentNormalizer()

    assert normalizer.supports("TEXT/PLAIN") is True


def test_support_normalizes_whitespace() -> None:
    normalizer = TextContentNormalizer()

    assert normalizer.supports("  text/plain  ") is True


@pytest.mark.parametrize(
    "content_media_type",
    (
        "",
        "   ",
        None,
        123,
    ),
)
def test_invalid_media_type_is_not_supported(
    content_media_type: object,
) -> None:
    normalizer = TextContentNormalizer()

    assert normalizer.supports(content_media_type) is False


def test_normalize_returns_canonical_content() -> None:
    normalizer = TextContentNormalizer()

    canonical = normalizer.normalize(
        _resource()
    )

    assert isinstance(
        canonical,
        CanonicalContent,
    )


def test_normalize_preserves_resource_identity() -> None:
    normalizer = TextContentNormalizer()
    resource = _resource()

    canonical = normalizer.normalize(
        resource
    )

    assert canonical.identity is resource.identity
    assert canonical.resource_ref == "resource-001"
    assert canonical.revision_ref == "revision-001"
    assert canonical.knowledge_scope_ref == "scope-001"


def test_normalize_produces_text_semantics() -> None:
    canonical = TextContentNormalizer().normalize(
        _resource()
    )

    assert canonical.content_kind == CanonicalContentKind.TEXT
    assert canonical.media_type == "text/plain"


def test_normalize_preserves_utf8_text() -> None:
    content = "Enterprise knowledge ✓".encode(
        "utf-8"
    )

    canonical = TextContentNormalizer().normalize(
        _resource(
            content=content
        )
    )

    assert canonical.content == content


def test_normalize_converts_crlf_to_lf() -> None:
    canonical = TextContentNormalizer().normalize(
        _resource(
            content=b"line one\r\nline two"
        )
    )

    assert canonical.content == b"line one\nline two"


def test_normalize_converts_cr_to_lf() -> None:
    canonical = TextContentNormalizer().normalize(
        _resource(
            content=b"line one\rline two"
        )
    )

    assert canonical.content == b"line one\nline two"


def test_normalize_applies_unicode_nfc() -> None:
    decomposed = "Cafe\u0301"
    expected = unicodedata.normalize(
        "NFC",
        decomposed,
    )

    canonical = TextContentNormalizer().normalize(
        _resource(
            content=decomposed.encode("utf-8")
        )
    )

    assert canonical.content.decode("utf-8") == expected


def test_normalizer_records_reproducibility_identity() -> None:
    normalizer = TextContentNormalizer()

    canonical = normalizer.normalize(
        _resource()
    )

    assert canonical.normalizer_ref == normalizer.normalizer_ref
    assert canonical.normalizer_version == normalizer.normalizer_version


def test_parsed_artifact_provenance_is_deterministic() -> None:
    canonical = TextContentNormalizer().normalize(
        _resource()
    )

    assert canonical.parsed_artifact_ref == (
        "resource-001:"
        "revision-001:"
        "parser-001:"
        "1.0"
    )


def test_empty_text_content_is_supported() -> None:
    canonical = TextContentNormalizer().normalize(
        _resource(
            content=b""
        )
    )

    assert canonical.content == b""
    assert canonical.size_bytes == 0


def test_invalid_resource_is_rejected() -> None:
    normalizer = TextContentNormalizer()

    with pytest.raises(
        TypeError,
        match="resource must be an instance of ParsedResource",
    ):
        normalizer.normalize(
            "invalid-resource"
        )


def test_unsupported_content_media_type_is_rejected() -> None:
    normalizer = TextContentNormalizer()

    with pytest.raises(
        ValueError,
        match=(
            "unsupported content media type for "
            "TextContentNormalizer"
        ),
    ):
        normalizer.normalize(
            _resource(
                content_media_type="application/json"
            )
        )


def test_invalid_utf8_content_is_rejected() -> None:
    normalizer = TextContentNormalizer()

    with pytest.raises(
        ValueError,
        match="parsed text must contain valid UTF-8 content",
    ):
        normalizer.normalize(
            _resource(
                content=b"\xff\xfe\xfd"
            )
        )


def test_repeated_normalization_is_deterministic() -> None:
    normalizer = TextContentNormalizer()
    resource = _resource(
        content=b"line one\r\nline two"
    )

    first = normalizer.normalize(resource)
    second = normalizer.normalize(resource)

    assert first == second
