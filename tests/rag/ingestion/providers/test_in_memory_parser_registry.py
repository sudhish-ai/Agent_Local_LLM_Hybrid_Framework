# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF InMemoryParserRegistry provider.
#
# Responsibilities:
# - Validate parser registration.
# - Validate parser resolution by media type.
# - Validate parser availability checks.
# - Validate deterministic registration-order selection.
# - Validate duplicate parser-reference rejection.
# - Validate unsupported media-type behavior.
# - Validate parser-reference membership and registry size.
#
# Must Not:
# - Test concrete PDF, DOCX, CSV, HTML, or other parsers.
# - Test parser plugin loading.
# - Test physical source acquisition.
# - Test normalization or canonicalization.
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
from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)
from alhf.rag.ingestion.providers.in_memory_parser_registry import (
    InMemoryParserRegistry,
)


class StubResourceParser(ResourceParser):
    """Configurable parser used for registry testing."""

    def __init__(
        self,
        *,
        parser_ref: str,
        media_type: str,
    ) -> None:
        self._parser_ref = parser_ref
        self._media_type = media_type

    @property
    def parser_ref(self) -> str:
        return self._parser_ref

    @property
    def parser_version(self) -> str:
        return "1.0"

    def supports(
        self,
        media_type: str,
    ) -> bool:
        return media_type == self._media_type

    def parse(
        self,
        resource: AcquiredResource,
    ) -> ParsedResource:
        raise NotImplementedError


def _parser(
    parser_ref: str = "text-parser",
    media_type: str = "text/plain",
) -> StubResourceParser:
    return StubResourceParser(
        parser_ref=parser_ref,
        media_type=media_type,
    )


def test_create_empty_registry() -> None:
    registry = InMemoryParserRegistry()

    assert len(registry) == 0


def test_register_parser() -> None:
    registry = InMemoryParserRegistry()

    registry.register(
        _parser(),
    )

    assert len(registry) == 1


def test_resolve_returns_registered_parser() -> None:
    registry = InMemoryParserRegistry()
    parser = _parser()

    registry.register(
        parser,
    )

    resolved = registry.resolve(
        "text/plain",
    )

    assert resolved is parser


def test_contains_supported_media_type() -> None:
    registry = InMemoryParserRegistry()

    registry.register(
        _parser(),
    )

    assert registry.contains(
        "text/plain",
    ) is True


def test_contains_unsupported_media_type() -> None:
    registry = InMemoryParserRegistry()

    registry.register(
        _parser(),
    )

    assert registry.contains(
        "application/pdf",
    ) is False


def test_unknown_media_type_raises_lookup_error() -> None:
    registry = InMemoryParserRegistry()

    registry.register(
        _parser(),
    )

    with pytest.raises(
        LookupError,
        match=(
            "parser not found for media type: "
            "application/pdf"
        ),
    ):
        registry.resolve(
            "application/pdf",
        )


def test_multiple_parsers_are_resolved_independently() -> None:
    registry = InMemoryParserRegistry()
    text_parser = _parser(
        "text-parser",
        "text/plain",
    )
    pdf_parser = _parser(
        "pdf-parser",
        "application/pdf",
    )

    registry.register(text_parser)
    registry.register(pdf_parser)

    assert registry.resolve(
        "text/plain",
    ) is text_parser

    assert registry.resolve(
        "application/pdf",
    ) is pdf_parser


def test_first_compatible_parser_is_selected() -> None:
    registry = InMemoryParserRegistry()
    first = _parser(
        "first-text-parser",
        "text/plain",
    )
    second = _parser(
        "second-text-parser",
        "text/plain",
    )

    registry.register(first)
    registry.register(second)

    assert registry.resolve(
        "text/plain",
    ) is first


def test_duplicate_parser_reference_is_rejected() -> None:
    registry = InMemoryParserRegistry()

    registry.register(
        _parser(),
    )

    with pytest.raises(
        ValueError,
        match="parser already registered: text-parser",
    ):
        registry.register(
            _parser(),
        )


def test_invalid_parser_is_rejected() -> None:
    registry = InMemoryParserRegistry()

    with pytest.raises(
        TypeError,
        match="parser must be an instance of ResourceParser",
    ):
        registry.register(
            "invalid-parser",
        )


def test_registered_parser_supports_membership() -> None:
    registry = InMemoryParserRegistry()

    registry.register(
        _parser(),
    )

    assert "text-parser" in registry
    assert "  text-parser  " in registry


def test_unknown_parser_is_not_member() -> None:
    registry = InMemoryParserRegistry()

    assert "missing-parser" not in registry


def test_invalid_membership_value_returns_false() -> None:
    registry = InMemoryParserRegistry()

    assert 123 not in registry
    assert "   " not in registry


@pytest.mark.parametrize(
    "media_type",
    (
        "",
        "   ",
    ),
)
def test_resolve_rejects_empty_media_type(
    media_type: str,
) -> None:
    registry = InMemoryParserRegistry()

    with pytest.raises(
        ValueError,
        match="media_type cannot be empty",
    ):
        registry.resolve(
            media_type,
        )


def test_resolve_rejects_non_string_media_type() -> None:
    registry = InMemoryParserRegistry()

    with pytest.raises(
        TypeError,
        match="media_type must be a string",
    ):
        registry.resolve(
            123,
        )
