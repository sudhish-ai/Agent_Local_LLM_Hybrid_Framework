# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the derivation-strategy registry boundary used by the
# ALHF Knowledge Foundation chunking layer.
#
# Problem Solved:
# Canonical Knowledge may require different derivation strategies while
# common chunking orchestration and downstream Knowledge layers must
# remain independent from concrete chunking implementations.
#
# Responsibilities:
# - Resolve a compatible DerivationStrategy for CanonicalContent.
# - Report whether compatible derivation behavior is available.
# - Keep strategy selection independent from concrete implementations.
# - Support dynamic extension of derivation capabilities.
# - Preserve canonical content as the strategy-selection boundary.
#
# Must Not:
# - Derive Knowledge Units directly.
# - Acquire, parse, or normalize Knowledge content.
# - Contain source-specific or file-format-specific behavior.
# - Contain hard-coded chunking strategy selection.
# - Generate embeddings or vector representations.
# - Perform indexing, retrieval, reranking, or context construction.
# - Load plugins directly.
# - Materialize unbounded Knowledge Unit collections.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG retrieval logic.
#
# Architectural Position:
# - Universal derivation-strategy discovery boundary.
# - Separates strategy resolution from concrete chunking algorithms.
# - Allows downstream layers to consume stable KnowledgeUnit contracts.
#
# Reuse Value:
# - Fixed-size text derivation.
# - Recursive derivation.
# - Semantic derivation.
# - Hierarchical derivation.
# - Graph-aware derivation.
# - Future adaptive derivation strategies.
#
# Future Extensibility:
# - Registries may use configuration, dependency injection, or plugins.
# - Multiple compatible strategies may later use governed selection policy.
# - Retrieval-quality intelligence may later influence strategy selection.
# - GraphRAG and Agentic RAG can add strategies without changing callers.
# - Parallel or distributed derivation can evolve outside this boundary.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.chunking.interfaces.derivation_strategy import (
    DerivationStrategy,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
)


class DerivationRegistry(ABC):
    """
    Universal discovery boundary for Knowledge derivation strategies.

    Resolution depends only on canonical Knowledge semantics rather than
    physical source technology, original file format, or parser behavior.
    """

    @abstractmethod
    def resolve(
        self,
        content: CanonicalContent,
    ) -> DerivationStrategy:
        """
        Resolve a compatible strategy for canonical Knowledge content.

        Args:
            content:
                Canonical Knowledge content requiring derivation.

        Returns:
            Compatible DerivationStrategy implementation.

        Raises:
            LookupError:
                When no compatible strategy is registered.
        """

        raise NotImplementedError

    @abstractmethod
    def contains(
        self,
        content: CanonicalContent,
    ) -> bool:
        """
        Return whether compatible derivation behavior is available.

        This permits orchestration to detect unsupported canonical
        semantics before derivation begins.
        """

        raise NotImplementedError
