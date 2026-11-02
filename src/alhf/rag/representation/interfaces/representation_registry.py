# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the representation-provider registry boundary used by the
# ALHF Knowledge Foundation representation layer.
#
# Problem Solved:
# Knowledge Units may require different retrieval representations while
# common representation orchestration must remain independent from
# concrete providers, models, embedding technologies, and external
# frameworks.
#
# Responsibilities:
# - Resolve a compatible RepresentationProvider for a Knowledge Unit.
# - Report whether compatible representation behavior is available.
# - Keep provider selection independent from concrete implementations.
# - Support dynamic extension of representation capabilities.
# - Preserve KnowledgeUnit as the provider-selection boundary.
#
# Must Not:
# - Generate Knowledge representations directly.
# - Modify KnowledgeUnit content or identity.
# - Contain embedding-model-specific behavior.
# - Contain vector-store-specific behavior.
# - Perform indexing, retrieval, reranking, or context construction.
# - Implement Representation Intelligence or adaptive provider selection.
# - Load external frameworks or plugins directly.
# - Implement concurrency, batching, or NFT execution policy.
# - Expose LangChain, LangGraph, or external framework types.
#
# Architectural Position:
# - Universal representation-provider discovery boundary.
# - Separates provider resolution from representation generation.
# - Keeps Knowledge semantics independent from retrieval technology.
#
# Reuse Value:
# - Dense representation providers.
# - Sparse representation providers.
# - Lexical representation providers.
# - Structured and graph representation providers.
# - Future multimodal representation providers.
#
# Future Extensibility:
# - Multiple compatible providers may coexist.
# - Knowledge Intelligence may later select providers using evidence.
# - Provider capabilities can evolve behind separate contracts.
# - Native and external implementations can use the same boundary.
# - Provider/model migrations do not require Knowledge re-derivation.
# - Parallel representation can evolve outside registry semantics.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.representation.interfaces.representation_provider import (
    RepresentationProvider,
)


class RepresentationRegistry(ABC):
    """
    Universal discovery boundary for representation providers.

    Resolution depends on governed Knowledge Unit semantics rather than
    source technologies, file formats, index providers, or external
    framework types.
    """

    @abstractmethod
    def resolve(
        self,
        unit: KnowledgeUnit,
    ) -> RepresentationProvider:
        """
        Resolve a compatible provider for one Knowledge Unit.

        Args:
            unit:
                Governed Knowledge Unit requiring representation.

        Returns:
            Compatible RepresentationProvider implementation.

        Raises:
            LookupError:
                When no compatible provider is registered.
        """

        raise NotImplementedError

    @abstractmethod
    def contains(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        """
        Return whether compatible representation behavior is available.

        This permits orchestration to detect unsupported Knowledge
        semantics before representation generation begins.
        """

        raise NotImplementedError
