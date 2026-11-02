# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the in-memory parser registry implementation used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Parsing orchestration must dynamically resolve compatible parsers
# without hard-coded PDF, DOCX, CSV, HTML, JSON, code, or future
# content-format conditionals in common ingestion logic.
#
# Responsibilities:
# - Register configured ResourceParser implementations.
# - Preserve parser registration order deterministically.
# - Resolve a compatible parser by media type.
# - Report parser availability by media type.
# - Reject duplicate parser references.
# - Validate parser identity during registration.
#
# Must Not:
# - Parse Knowledge resources directly.
# - Load parser plugins dynamically.
# - Contain format-specific parsing logic.
# - Acquire physical Knowledge resources.
# - Modify ResourceIdentity or provenance.
# - Perform normalization, chunking, embedding, indexing, or retrieval.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Concrete V1 implementation of ParserRegistry.
# - Composition mechanism for dynamically configured parsers.
# - Keeps format diversity inside the ingestion parsing boundary.
#
# Reuse Value:
# - Local development and production.
# - Deterministic integration testing.
# - Customer-specific parser composition.
# - Future parser plugin composition.
#
# Future Extensibility:
# - Plugin-backed registries can implement ParserRegistry independently.
# - Parser-selection intelligence can evolve behind this boundary.
# - Parser capabilities can later participate in compatibility decisions.
# - New formats require parser registration rather than downstream
#   Knowledge Foundation changes.

from __future__ import annotations

from alhf.rag.ingestion.interfaces.parser_registry import (
    ParserRegistry,
)
from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)


class InMemoryParserRegistry(ParserRegistry):
    """In-memory registry of configured Knowledge resource parsers."""

    def __init__(self) -> None:
        self._parsers: dict[str, ResourceParser] = {}

    def register(
        self,
        parser: ResourceParser,
    ) -> None:
        """Register one configured resource parser."""

        if not isinstance(
            parser,
            ResourceParser,
        ):
            raise TypeError(
                "parser must be an instance of ResourceParser"
            )

        parser_ref = self._normalize_required_text(
            value=parser.parser_ref,
            field_name="parser_ref",
        )
        self._normalize_required_text(
            value=parser.parser_version,
            field_name="parser_version",
        )

        if parser_ref in self._parsers:
            raise ValueError(
                f"parser already registered: {parser_ref}"
            )

        self._parsers[parser_ref] = parser

    def resolve(
        self,
        media_type: str,
    ) -> ResourceParser:
        """Resolve the first registered parser supporting a media type."""

        normalized_media_type = self._normalize_required_text(
            value=media_type,
            field_name="media_type",
        )

        for parser in self._parsers.values():
            if parser.supports(
                normalized_media_type,
            ):
                return parser

        raise LookupError(
            "parser not found for media type: "
            f"{normalized_media_type}"
        )

    def contains(
        self,
        media_type: str,
    ) -> bool:
        """Return whether a compatible parser is registered."""

        normalized_media_type = self._normalize_required_text(
            value=media_type,
            field_name="media_type",
        )

        return any(
            parser.supports(
                normalized_media_type,
            )
            for parser in self._parsers.values()
        )

    def __contains__(
        self,
        parser_ref: object,
    ) -> bool:
        """Return whether a parser reference is registered."""

        if not isinstance(
            parser_ref,
            str,
        ):
            return False

        normalized_ref = parser_ref.strip()

        if not normalized_ref:
            return False

        return normalized_ref in self._parsers

    def __len__(self) -> int:
        """Return the number of registered parsers."""

        return len(
            self._parsers,
        )

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required registry text."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
