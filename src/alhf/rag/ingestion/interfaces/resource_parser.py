# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal resource-parsing boundary used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# ALHF must parse many content formats without allowing PDF, DOCX, HTML,
# CSV, JSON, code, or future format-specific behavior to leak into
# downstream Knowledge Foundation layers.
#
# Responsibilities:
# - Accept one provider-neutral AcquiredResource.
# - Produce one provider-neutral ParsedResource.
# - Preserve resource and revision identity across parsing.
# - Expose parser identity and version for reproducibility.
# - Declare whether a parser supports a given media type.
# - Keep format-specific parsing behind concrete implementations.
#
# Must Not:
# - Acquire resources from physical sources.
# - Generate source, resource, or revision identities.
# - Modify Knowledge scope or provenance identity.
# - Normalize semantic Knowledge content.
# - Perform chunking, embedding, indexing, or retrieval.
# - Materialize collections of resources.
# - Select parsers through hard-coded file-type conditionals.
# - Contain provider-specific source behavior.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Implement threading, multiprocessing, or async execution policy.
#
# Architectural Position:
# - Stable format-isolation boundary of the ingestion plane.
# - Separates acquired physical content from downstream Knowledge logic.
# - New content formats extend this boundary through parser
#   implementations rather than downstream changes.
#
# Reuse Value:
# - Plain-text parsing.
# - PDF and document parsing.
# - Structured-data parsing.
# - Code parsing.
# - Future multimodal parsing implementations.
#
# Future Extensibility:
# - Parser registries can dynamically resolve compatible parsers.
# - Parser capabilities can evolve independently from this core boundary.
# - Parallel or distributed parsing can evolve behind execution policies.
# - Canonicalization can evolve after parsing without source coupling.
# - New formats should require parser implementations, not downstream
#   Knowledge Foundation modifications.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)


class ResourceParser(ABC):
    """
    Universal parsing boundary for acquired Knowledge resources.

    Concrete parsers own format-specific interpretation. Downstream
    Knowledge Foundation stages consume ParsedResource and therefore do
    not depend on individual source file formats.
    """

    @property
    @abstractmethod
    def parser_ref(self) -> str:
        """Return the stable logical parser identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def parser_version(self) -> str:
        """Return the stable parser behavior version."""

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        media_type: str,
    ) -> bool:
        """
        Return whether this parser supports the supplied media type.

        Parser selection must depend on declared compatibility rather than
        downstream file-format conditionals.
        """

        raise NotImplementedError

    @abstractmethod
    def parse(
        self,
        resource: AcquiredResource,
    ) -> ParsedResource:
        """
        Parse one acquired Knowledge resource.

        The returned ParsedResource must preserve the input
        ResourceIdentity unchanged.
        """

        raise NotImplementedError
