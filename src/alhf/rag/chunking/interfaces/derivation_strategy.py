# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal derivation strategy boundary used by the
# ALHF Knowledge Foundation chunking layer.
#
# Problem Solved:
# Canonical Knowledge may require different derivation strategies while
# representation, indexing, and retrieval must remain independent from
# concrete chunking algorithms.
#
# Responsibilities:
# - Accept one CanonicalContent resource.
# - Produce KnowledgeUnit instances incrementally.
# - Preserve ResourceIdentity across derivation.
# - Preserve canonical-artifact provenance.
# - Expose derivation strategy identity and version.
# - Declare compatibility with canonical Knowledge semantics.
# - Keep concrete derivation algorithms replaceable.
#
# Must Not:
# - Acquire or parse physical resources.
# - Contain source-specific or file-format-specific behavior.
# - Normalize canonical content.
# - Materialize an unbounded Knowledge Unit collection.
# - Generate embeddings or vector representations.
# - Perform indexing, retrieval, reranking, or context construction.
# - Contain vector-store or embedding-provider behavior.
# - Implement concurrency or NFT execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG retrieval logic.
#
# Architectural Position:
# - Universal strategy boundary for Knowledge derivation and chunking.
# - Consumes only CanonicalContent from the ingestion abstraction
#   firewall.
# - Produces bounded KnowledgeUnit instances for downstream processing.
#
# Reuse Value:
# - Fixed-size derivation.
# - Recursive text derivation.
# - Semantic derivation.
# - Hierarchical derivation.
# - Graph-oriented Knowledge-unit derivation.
# - Future adaptive derivation strategies.
#
# Future Extensibility:
# - New chunking strategies require strategy implementations rather than
#   downstream changes.
# - Strategy selection can evolve behind a registry or intelligence layer.
# - GraphRAG can derive graph-aware units behind this boundary.
# - Agentic RAG can consume units without owning derivation internals.
# - Parallel derivation can evolve behind execution policies.
# - Evaluation can compare strategies using stable KnowledgeUnit output.

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
)


class DerivationStrategy(ABC):
    """
    Universal derivation boundary for canonical Knowledge content.

    Concrete implementations decide how canonical Knowledge becomes
    bounded Knowledge Units. Downstream stages consume KnowledgeUnit and
    remain independent from the chosen derivation algorithm.
    """

    @property
    @abstractmethod
    def strategy_ref(self) -> str:
        """Return the stable logical strategy identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def strategy_version(self) -> str:
        """Return the stable derivation behavior version."""

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        content: CanonicalContent,
    ) -> bool:
        """
        Return whether this strategy supports the canonical content.

        Compatibility must depend on canonical Knowledge semantics rather
        than the original source or physical file format.
        """

        raise NotImplementedError

    @abstractmethod
    def derive(
        self,
        content: CanonicalContent,
    ) -> Iterator[KnowledgeUnit]:
        """
        Derive bounded Knowledge Units incrementally.

        Implementations must preserve source ResourceIdentity and
        canonical provenance while avoiding unbounded materialization.
        """

        raise NotImplementedError
