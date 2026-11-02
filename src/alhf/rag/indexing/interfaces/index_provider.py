# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal indexing-provider boundary used by the
# ALHF Knowledge Foundation indexing layer.
#
# Problem Solved:
# Knowledge representations must become searchable without coupling
# governed Knowledge semantics to vector databases, search engines,
# graph stores, local indexes, cloud services, or external frameworks.
#
# Responsibilities:
# - Accept provider-neutral KnowledgeRepresentation artifacts.
# - Declare whether a representation can be indexed.
# - Write one representation idempotently.
# - Remove one representation from searchable state.
# - Expose stable provider identity and version.
# - Preserve provider independence above the indexing boundary.
#
# Must Not:
# - Generate Knowledge representations.
# - Modify Knowledge Unit or representation identity.
# - Perform retrieval, reranking, or context construction.
# - Contain Knowledge derivation or embedding logic.
# - Implement Index Intelligence or provider-selection policy.
# - Assume dense vectors are the only indexable representation.
# - Expose provider-specific database or framework types.
# - Implement concurrency, batching, or NFT execution policy.
# - Depend on LangChain, LangGraph, or external RAG frameworks.
#
# Architectural Position:
# - Stable execution boundary between KnowledgeRepresentation and
#   physical retrieval indexes.
# - Keeps index technology replaceable behind ALHF contracts.
# - Supports local, cloud, hybrid, and future index implementations.
#
# Reuse Value:
# - Dense vector indexes.
# - Sparse and lexical indexes.
# - Structured search indexes.
# - Graph indexes.
# - Future multimodal retrieval indexes.
#
# Future Extensibility:
# - Multiple index providers may coexist for hybrid retrieval.
# - Versioned candidate indexes can evolve behind this boundary.
# - Batch, partitioned, and distributed indexing can be added later.
# - Provider capability discovery can evolve independently.
# - Promotion, rollback, and index lifecycle remain separate concerns.
# - External tools can implement this interface through adapters without
#   changing common ALHF Knowledge contracts.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)


class IndexProvider(ABC):
    """
    Universal boundary for physical Knowledge indexing.

    Concrete providers own index-specific persistence while callers
    remain independent from the underlying retrieval technology.
    """

    @property
    @abstractmethod
    def provider_ref(self) -> str:
        """Return the stable logical index-provider identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def provider_version(self) -> str:
        """Return the stable index-provider behavior version."""

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        representation: KnowledgeRepresentation,
    ) -> bool:
        """
        Return whether this provider supports the representation.

        Compatibility must depend on representation semantics rather
        than source technology or original content format.
        """

        raise NotImplementedError

    @abstractmethod
    def upsert(
        self,
        representation: KnowledgeRepresentation,
    ) -> None:
        """
        Make one representation searchable idempotently.

        Repeating the same logical write must not create duplicate
        searchable membership.
        """

        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        representation_id: str,
    ) -> None:
        """
        Remove one representation from searchable state.

        Implementations own physical deletion behavior while preserving
        the provider-neutral representation identity boundary.
        """

        raise NotImplementedError
