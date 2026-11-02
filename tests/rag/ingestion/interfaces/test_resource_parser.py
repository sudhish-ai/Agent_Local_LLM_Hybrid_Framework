# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ResourceParser interface.
#
# Responsibilities:
# - Validate the abstract resource-parsing boundary.
# - Validate parser identity and version contracts.
# - Validate media-type capability declaration.
# - Validate AcquiredResource input handling.
# - Validate ParsedResource output behavior.
# - Validate ResourceIdentity preservation across parsing.
# - Protect format isolation from downstream Knowledge layers.
#
# Must Not:
# - Test concrete PDF, DOCX, CSV, HTML, or other parsers.
# - Test physical source acquisition.
# - Test parser registry or parser selection.
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
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)


class StubResourceParser(ResourceParser):
    """Minimal parser used to validate the universal parsing boundary."""

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
        return ParsedResource(
            identity=resource.identity,
            content=resource.content,
            content_media_type="text/plain",
            source_media_type=resource.media_type,
            parser_ref=self.parser_ref,
            parser_version=self.parser_version,
        )


class MissingParseParser(ResourceParser):
    """Invalid parser intentionally missing parse behavior."""

    @property
    def parser_ref(self) -> str:
        return "missing-parse"

    @property
    def parser_version(self) -> str:
        return "1.0"

    def supports(
        self,
        media_type: str,
    ) -> bool:
        return True


class MissingSupportsParser(ResourceParser):
    """Invalid parser intentionally missing supports behavior."""

    @property
    def parser_ref(self) -> str:
        return "missing-supports"

    @property
    def parser_version(self) -> str:
        return "1.0"

    def parse(
        self,
        resource: AcquiredResource,
    ) -> ParsedResource:
        raise NotImplementedError


def _resource() -> AcquiredResource:
    identity = ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )

    return AcquiredResource(
        identity=identity,
        content=b"enterprise knowledge",
        media_type="text/plain",
        content_fingerprint="sha256:abc123",
    )


def test_resource_parser_is_abstract() -> None:
    with pytest.raises(TypeError):
        ResourceParser()


def test_missing_parse_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingParseParser()


def test_missing_supports_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingSupportsParser()


def test_concrete_parser_can_be_instantiated() -> None:
    parser = StubResourceParser()

    assert isinstance(
        parser,
        ResourceParser,
    )


def test_parser_exposes_stable_reference() -> None:
    parser = StubResourceParser()

    assert parser.parser_ref == "text-parser"


def test_parser_exposes_stable_version() -> None:
    parser = StubResourceParser()

    assert parser.parser_version == "1.0"


def test_parser_reports_supported_media_type() -> None:
    parser = StubResourceParser()

    assert parser.supports("text/plain") is True


def test_parser_reports_unsupported_media_type() -> None:
    parser = StubResourceParser()

    assert parser.supports("application/pdf") is False


def test_parse_returns_parsed_resource() -> None:
    parser = StubResourceParser()

    parsed = parser.parse(
        _resource(),
    )

    assert isinstance(
        parsed,
        ParsedResource,
    )


def test_parse_preserves_resource_identity() -> None:
    parser = StubResourceParser()
    resource = _resource()

    parsed = parser.parse(
        resource,
    )

    assert parsed.identity is resource.identity
    assert parsed.resource_ref == "resource-001"
    assert parsed.revision_ref == "revision-001"


def test_parse_preserves_source_media_type() -> None:
    parser = StubResourceParser()

    parsed = parser.parse(
        _resource(),
    )

    assert parsed.source_media_type == "text/plain"


def test_parse_records_parser_reproducibility() -> None:
    parser = StubResourceParser()

    parsed = parser.parse(
        _resource(),
    )

    assert parsed.parser_ref == "text-parser"
    assert parsed.parser_version == "1.0"


def test_parse_preserves_content_for_stub_parser() -> None:
    parser = StubResourceParser()
    resource = _resource()

    parsed = parser.parse(
        resource,
    )

    assert parsed.content == resource.content
