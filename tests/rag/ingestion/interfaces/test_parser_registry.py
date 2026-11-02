# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ParserRegistry interface.
#
# Responsibilities:
# - Validate the abstract parser-registry boundary.
# - Validate compatible parser resolution by media type.
# - Validate parser-availability checks.
# - Validate unsupported media-type behavior.
# - Protect dynamic parser-selection semantics.
# - Protect format isolation from downstream Knowledge layers.
#
# Must Not:
# - Test concrete PDF, DOCX, CSV, HTML, or other parsers.
# - Test physical source acquisition.
# - Test parser plugin loading.
# - Test normalization or canonicalization.
# - Test chunking, embedding, indexing, or retrieval.
# - Test concurrency or NFT execution strategies.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)
from alhf.rag.ingestion.interfaces.parser_registry import (
    ParserRegistry,
)
from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)


class StubResourceParser(ResourceParser):
    """Minimal parser used to validate registry resolution."""

    @property
    def parser_ref(self) -> str:
        return "text-parser"

    @property
    def parser_version(self) -> str:
        return "1.0"

    def supports(
        self,
        media_type: str,
    ) -> bool:
        return media_type == "text/plain"

    def parse(
        self,
        resource: AcquiredResource,
    ) -> ParsedResource:
        raise NotImplementedError


class StubParserRegistry(ParserRegistry):
    """Minimal registry used to validate the interface contract."""

    def __init__(
        self,
        parser: ResourceParser,
    ) -> None:
        self._parser = parser

    def resolve(
        self,
        media_type: str,
    ) -> ResourceParser:
        if not self._parser.supports(media_type):
            raise LookupError(
                f"parser not found for media type: {media_type}"
            )

        return self._parser

    def contains(
        self,
        media_type: str,
    ) -> bool:
        return self._parser.supports(media_type)


class MissingResolveRegistry(ParserRegistry):
    """Invalid registry missing parser resolution."""

    def contains(
        self,
        media_type: str,
    ) -> bool:
        return False


class MissingContainsRegistry(ParserRegistry):
    """Invalid registry missing availability behavior."""

    def resolve(
        self,
        media_type: str,
    ) -> ResourceParser:
        return StubResourceParser()


def _registry() -> StubParserRegistry:
    return StubParserRegistry(
        StubResourceParser()
    )


def test_parser_registry_is_abstract() -> None:
    with pytest.raises(TypeError):
        ParserRegistry()


def test_missing_resolve_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingResolveRegistry()


def test_missing_contains_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingContainsRegistry()


def test_concrete_registry_can_be_instantiated() -> None:
    registry = _registry()

    assert isinstance(
        registry,
        ParserRegistry,
    )


def test_resolve_returns_resource_parser() -> None:
    registry = _registry()

    parser = registry.resolve(
        "text/plain",
    )

    assert isinstance(
        parser,
        ResourceParser,
    )


def test_resolve_returns_configured_parser() -> None:
    parser = StubResourceParser()
    registry = StubParserRegistry(
        parser,
    )

    resolved = registry.resolve(
        "text/plain",
    )

    assert resolved is parser


def test_contains_returns_true_for_supported_media_type() -> None:
    registry = _registry()

    assert registry.contains(
        "text/plain"
    ) is True


def test_contains_returns_false_for_unsupported_media_type() -> None:
    registry = _registry()

    assert registry.contains(
        "application/pdf"
    ) is False


def test_unknown_media_type_raises_lookup_error() -> None:
    registry = _registry()

    with pytest.raises(
        LookupError,
        match=(
            "parser not found for media type: application/pdf"
        ),
    ):
        registry.resolve(
            "application/pdf",
        )


def test_registry_resolution_preserves_parser_identity() -> None:
    registry = _registry()

    parser = registry.resolve(
        "text/plain",
    )

    assert parser.parser_ref == "text-parser"
    assert parser.parser_version == "1.0"
