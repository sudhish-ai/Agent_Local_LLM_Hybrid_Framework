# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal content-normalization boundary used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Parsed resources may originate from many sources and content formats,
# but downstream Knowledge processing must operate on stable canonical
# semantics without understanding those original technologies.
#
# Responsibilities:
# - Accept one provider-neutral ParsedResource.
# - Produce one CanonicalContent representation.
# - Preserve ResourceIdentity across normalization.
# - Preserve provenance from the parsed representation.
# - Expose normalizer identity and version for reproducibility.
# - Declare compatibility with parsed content semantics.
# - Keep normalization implementations replaceable.
#
# Must Not:
# - Acquire physical Knowledge resources.
# - Perform source-specific behavior.
# - Perform PDF, DOCX, CSV, HTML, or other parsing.
# - Generate or modify resource or revision identity.
# - Perform derivation or chunking.
# - Perform embedding, indexing, retrieval, or reranking.
# - Materialize collections of Knowledge resources.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Contain arbitrary metadata dictionaries.
#
# Architectural Position:
# - Stable canonicalization boundary of the ingestion plane.
# - Connects ParsedResource to CanonicalContent.
# - Marks the point after which downstream layers operate on ALHF
#   Knowledge semantics rather than source/file-format semantics.
#
# Reuse Value:
# - Text normalization.
# - Structured and tabular normalization.
# - Code normalization.
# - Future multimodal canonicalization.
# - Standard RAG, GraphRAG, and Agentic RAG foundations.
#
# Future Extensibility:
# - New source types remain isolated behind source adapters.
# - New file formats remain isolated behind ResourceParser implementations.
# - New canonical semantic capabilities can add normalizers without
#   changing downstream processing contracts.
# - Normalizer selection can evolve behind a registry.
# - Parallel and distributed normalization can evolve independently.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
)
from alhf.rag.ingestion.contracts.parsed_resource import (
    ParsedResource,
)


class ContentNormalizer(ABC):
    """
    Universal canonicalization boundary for parsed Knowledge content.

    Concrete implementations translate parsed representations into
    stable ALHF canonical Knowledge semantics. Downstream stages operate
    on CanonicalContent rather than physical source or file-format types.
    """

    @property
    @abstractmethod
    def normalizer_ref(self) -> str:
        """Return the stable logical normalizer identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def normalizer_version(self) -> str:
        """Return the stable normalizer behavior version."""

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        content_media_type: str,
    ) -> bool:
        """
        Return whether this normalizer supports parsed content semantics.

        Compatibility is based on the parsed representation rather than
        the original physical source or original file type.
        """

        raise NotImplementedError

    @abstractmethod
    def normalize(
        self,
        resource: ParsedResource,
    ) -> CanonicalContent:
        """
        Normalize one parsed Knowledge resource.

        Implementations must preserve ResourceIdentity and produce stable
        CanonicalContent for downstream Knowledge processing.
        """

        raise NotImplementedError
