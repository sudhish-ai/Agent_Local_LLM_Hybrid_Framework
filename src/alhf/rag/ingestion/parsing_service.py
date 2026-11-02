# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral parsing orchestration for the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Acquired Knowledge resources may use many content formats. The common
# ingestion pipeline must dynamically resolve compatible parsers without
# containing PDF, DOCX, CSV, HTML, JSON, code, or future format-specific
# branching.
#
# Responsibilities:
# - Accept one provider-neutral AcquiredResource.
# - Resolve a compatible parser through ParserRegistry.
# - Delegate format-specific interpretation to ResourceParser.
# - Validate parser compatibility before parsing.
# - Validate parser output identity continuity.
# - Return provider-neutral ParsedResource.
#
# Must Not:
# - Contain hard-coded content-format conditionals.
# - Perform physical source acquisition.
# - Implement format-specific parsing.
# - Generate or modify resource and revision identities.
# - Perform semantic normalization.
# - Perform chunking, embedding, indexing, or retrieval.
# - Materialize collections of resources.
# - Implement concurrency, threading, multiprocessing, or async policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Common parsing orchestration boundary inside the ingestion plane.
# - Connects AcquiredResource to dynamically selected ResourceParser.
# - Terminates content-format complexity before downstream processing.
#
# Reuse Value:
# - Local and cloud acquisition pipelines.
# - Heterogeneous enterprise content ingestion.
# - Customer-specific parser extensions.
# - Future multimodal parser composition.
#
# Future Extensibility:
# - New formats require parser registration rather than service changes.
# - Parser-selection intelligence can evolve behind ParserRegistry.
# - Parser capability semantics can evolve independently.
# - Parallel parsing can later wrap this semantic boundary.
# - Downstream Knowledge layers remain independent from source formats.

from __future__ import annotations

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
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


class ParsingService:
    """Provider-neutral orchestration for Knowledge resource parsing."""

    def __init__(
        self,
        *,
        registry: ParserRegistry,
    ) -> None:
        if not isinstance(
            registry,
            ParserRegistry,
        ):
            raise TypeError(
                "registry must be an instance of ParserRegistry"
            )

        self._registry = registry

    def parse(
        self,
        resource: AcquiredResource,
    ) -> ParsedResource:
        """Resolve and invoke the compatible parser for one resource."""

        if not isinstance(
            resource,
            AcquiredResource,
        ):
            raise TypeError(
                "resource must be an instance of AcquiredResource"
            )

        parser = self._registry.resolve(
            resource.media_type,
        )

        self._validate_parser(
            parser=parser,
            media_type=resource.media_type,
        )

        parsed = parser.parse(
            resource,
        )

        self._validate_result(
            resource=resource,
            parsed=parsed,
        )

        return parsed

    @staticmethod
    def _validate_parser(
        *,
        parser: ResourceParser,
        media_type: str,
    ) -> None:
        """Validate registry output and declared compatibility."""

        if not isinstance(
            parser,
            ResourceParser,
        ):
            raise TypeError(
                "registry must return ResourceParser"
            )

        if not parser.supports(
            media_type,
        ):
            raise ValueError(
                "resolved parser does not support resource media type"
            )

    @staticmethod
    def _validate_result(
        *,
        resource: AcquiredResource,
        parsed: ParsedResource,
    ) -> None:
        """Protect provenance identity across the parsing boundary."""

        if not isinstance(
            parsed,
            ParsedResource,
        ):
            raise TypeError(
                "parser must return ParsedResource"
            )

        if parsed.identity != resource.identity:
            raise ValueError(
                "parsed resource identity must match acquired resource"
            )

        if parsed.source_media_type != resource.media_type:
            raise ValueError(
                "parsed source_media_type must match acquired media type"
            )
