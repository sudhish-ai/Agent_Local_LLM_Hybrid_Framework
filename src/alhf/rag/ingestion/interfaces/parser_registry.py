# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the parser-registry boundary used by the ALHF Knowledge
# Foundation ingestion plane.
#
# Problem Solved:
# ALHF must dynamically resolve parsers for acquired content without
# spreading PDF, DOCX, CSV, HTML, JSON, code, or future format-specific
# conditionals throughout ingestion and downstream Knowledge layers.
#
# Responsibilities:
# - Resolve a compatible ResourceParser by media type.
# - Keep parser selection independent from concrete parser classes.
# - Provide a stable boundary for parser registration mechanisms.
# - Reject unsupported media types explicitly.
# - Keep format-specific complexity inside the parsing boundary.
#
# Must Not:
# - Parse resources directly.
# - Acquire physical resources.
# - Contain hard-coded parser implementations.
# - Generate source, resource, or revision identities.
# - Normalize semantic Knowledge content.
# - Perform chunking, embedding, indexing, or retrieval.
# - Contain source-provider-specific behavior.
# - Contain arbitrary metadata dictionaries.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Universal parser-discovery boundary for Knowledge ingestion.
# - Separates media-type routing from concrete parser implementations.
# - Ensures format diversity terminates inside the ingestion layer.
#
# Reuse Value:
# - Plain-text parsing.
# - PDF and document parsing.
# - Structured-data parsing.
# - Code parsing.
# - Future multimodal parsing.
# - Customer-supplied parser plugins.
#
# Future Extensibility:
# - Registries may use dependency injection, configuration, or plugins.
# - Parser capability discovery can evolve independently.
# - Multiple parser implementations may later support selection policy.
# - Parser execution strategies can evolve without downstream changes.
# - New formats should require parser registration rather than changes
#   to Normalization, Chunking, Indexing, or Retrieval.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.ingestion.interfaces.resource_parser import (
    ResourceParser,
)


class ParserRegistry(ABC):
    """
    Universal discovery boundary for Knowledge resource parsers.

    Parser resolution is based on declared media-type compatibility.
    Downstream Knowledge Foundation layers remain independent from the
    original resource format and parser implementation.
    """

    @abstractmethod
    def resolve(
        self,
        media_type: str,
    ) -> ResourceParser:
        """
        Resolve a parser compatible with one media type.

        Args:
            media_type:
                Media type of the acquired resource.

        Returns:
            Compatible ResourceParser implementation.

        Raises:
            LookupError:
                When no compatible parser is registered.
        """

        raise NotImplementedError

    @abstractmethod
    def contains(
        self,
        media_type: str,
    ) -> bool:
        """
        Return whether a compatible parser exists for a media type.

        This permits callers to validate parser availability before
        beginning resource processing.
        """

        raise NotImplementedError
