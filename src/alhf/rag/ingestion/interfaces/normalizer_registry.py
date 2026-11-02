# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the normalizer-registry boundary used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Parsed Knowledge representations may require different canonicalization
# behavior, while downstream Knowledge layers must remain independent
# from parser, source, and original content-format specifics.
#
# Responsibilities:
# - Resolve a compatible ContentNormalizer by parsed media type.
# - Report whether compatible normalization behavior is available.
# - Keep normalizer resolution independent from concrete implementations.
# - Support dynamic extension of canonicalization capabilities.
# - Preserve the stable canonical Knowledge boundary.
#
# Must Not:
# - Normalize content directly.
# - Acquire or parse physical resources.
# - Contain source-specific behavior.
# - Contain PDF, DOCX, CSV, HTML, or other file-format logic.
# - Generate or modify resource or revision identities.
# - Perform derivation, chunking, embedding, indexing, or retrieval.
# - Load normalizer plugins directly.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Universal normalizer-discovery boundary inside the ingestion plane.
# - Separates canonicalization selection from concrete normalizers.
# - Protects downstream layers from ingestion-format complexity.
#
# Reuse Value:
# - Text canonicalization.
# - Structured and tabular canonicalization.
# - Code canonicalization.
# - Future multimodal Knowledge canonicalization.
# - Customer-specific canonicalization extensions.
#
# Future Extensibility:
# - Registries may use configuration, dependency injection, or plugins.
# - Multiple compatible normalizers may later use selection policies.
# - Capability-aware selection can evolve behind this boundary.
# - Parallel normalization can evolve outside semantic contracts.
# - New formats mapping to existing canonical semantics must not require
#   downstream Knowledge Foundation changes.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.ingestion.interfaces.content_normalizer import (
    ContentNormalizer,
)


class NormalizerRegistry(ABC):
    """
    Universal discovery boundary for Knowledge content normalizers.

    Resolution depends on parsed representation semantics rather than
    original source technology or original physical file type.
    """

    @abstractmethod
    def resolve(
        self,
        content_media_type: str,
    ) -> ContentNormalizer:
        """
        Resolve a compatible normalizer for parsed content semantics.

        Raises:
            LookupError:
                When no compatible normalizer is available.
        """

        raise NotImplementedError

    @abstractmethod
    def contains(
        self,
        content_media_type: str,
    ) -> bool:
        """
        Return whether compatible normalization behavior is available.

        This allows ingestion orchestration to detect unsupported
        canonicalization before downstream processing begins.
        """

        raise NotImplementedError
