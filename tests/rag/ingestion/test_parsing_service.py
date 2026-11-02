# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ParsingService.
#
# Responsibilities:
# - Validate dynamic parser resolution.
# - Validate AcquiredResource parsing.
# - Validate ParsedResource output.
# - Validate ResourceIdentity continuity.
# - Validate source media-type continuity.
# - Validate unsupported media-type behavior.
# - Validate invalid parser-registry behavior.
#
# Must Not:
# - Test physical source acquisition.
# - Test concrete PDF or document parsing.
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
from alhf.rag.ingestion.interfaces.parser_registry import (
    ParserRegistry,
)
from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)
from alhf.rag.ingestion.parsers.text_resource_parser import (
    TextResourceParser,
)
from alhf.rag.ingestion.parsing_service import (
    ParsingService,
)
from alhf.rag.ingestion.providers.in_memory_parser_registry import (
    InMemoryParserRegistry,
)


def _resource(
    media_type: str = "text/plain",
) -> AcquiredResource:
    return AcquiredResource(
        identity=ResourceIdentity(
            knowledge_scope_ref="scope-001",
            source_ref="source-001",
            logical_resource_id="resource-001",
            revision_id="revision-001",
        ),
        content=b"enterprise knowledge",
        media_type=media_type,
    )


def _service() -> ParsingService:
    registry = InMemoryParserRegistry()
    registry.register(
        TextResourceParser()
    )

    return ParsingService(
        registry=registry,
    )


def test_create_parsing_service() -> None:
    service = _service()

    assert isinstance(
        service,
        ParsingService,
    )


def test_parse_returns_parsed_resource() -> None:
    parsed = _service().parse(
        _resource()
    )

    assert isinstance(
        parsed,
        ParsedResource,
    )


def test_parse_preserves_resource_identity() -> None:
    resource = _resource()

    parsed = _service().parse(
        resource
    )

    assert parsed.identity is resource.identity
    assert parsed.resource_ref == "resource-001"
    assert parsed.revision_ref == "revision-001"


def test_parse_preserves_source_media_type() -> None:
    parsed = _service().parse(
        _resource()
    )

    assert parsed.source_media_type == "text/plain"


def test_parse_uses_resolved_parser() -> None:
    parsed = _service().parse(
        _resource()
    )

    assert parsed.parser_ref == "text-resource-parser"
    assert parsed.parser_version == "1.0"


def test_parse_preserves_content() -> None:
    resource = _resource()

    parsed = _service().parse(
        resource
    )

    assert parsed.content == resource.content


def test_unsupported_media_type_is_rejected() -> None:
    service = _service()

    with pytest.raises(
        LookupError,
        match=(
            "parser not found for media type: "
            "application/pdf"
        ),
    ):
        service.parse(
            _resource(
                media_type="application/pdf"
            )
        )


def test_invalid_resource_is_rejected() -> None:
    service = _service()

    with pytest.raises(
        TypeError,
        match=(
            "resource must be an instance of "
            "AcquiredResource"
        ),
    ):
        service.parse(
            "invalid-resource"
        )


def test_invalid_registry_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "registry must be an instance of "
            "ParserRegistry"
        ),
    ):
        ParsingService(
            registry="invalid-registry"
        )


class InvalidParserRegistry(ParserRegistry):
    """Registry intentionally returning an invalid parser."""

    def resolve(
        self,
        media_type: str,
    ):
        return "invalid-parser"

    def contains(
        self,
        media_type: str,
    ) -> bool:
        return True


def test_invalid_registry_parser_is_rejected() -> None:
    service = ParsingService(
        registry=InvalidParserRegistry()
    )

    with pytest.raises(
        TypeError,
        match="registry must return ResourceParser",
    ):
        service.parse(
            _resource()
        )


class IncompatibleParser(TextResourceParser):
    """Parser that becomes incompatible after registry resolution."""

    def supports(
        self,
        media_type: str,
    ) -> bool:
        return False


class IncompatibleParserRegistry(ParserRegistry):
    """Registry intentionally returning an incompatible parser."""

    def resolve(
        self,
        media_type: str,
    ) -> ResourceParser:
        return IncompatibleParser()

    def contains(
        self,
        media_type: str,
    ) -> bool:
        return True


def test_incompatible_resolved_parser_is_rejected() -> None:
    service = ParsingService(
        registry=IncompatibleParserRegistry()
    )

    with pytest.raises(
        ValueError,
        match=(
            "resolved parser does not support resource media type"
        ),
    ):
        service.parse(
            _resource()
        )
