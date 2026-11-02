# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal representation-provider boundary used by the
# ALHF Knowledge Foundation representation layer.
#
# Problem Solved:
# Knowledge Units must be converted into retrieval representations
# without coupling governed Knowledge semantics to embedding models,
# representation technologies, providers, vector stores, or external
# RAG frameworks.
#
# Responsibilities:
# - Accept one provider-neutral KnowledgeUnit.
# - Produce one provider-neutral KnowledgeRepresentation.
# - Declare whether the provider supports a Knowledge Unit.
# - Expose stable provider identity and version.
# - Preserve Knowledge Unit provenance through representation.
# - Keep representation generation replaceable behind one boundary.
#
# Must Not:
# - Modify KnowledgeUnit content or identity.
# - Perform Knowledge acquisition, parsing, or derivation.
# - Perform indexing, retrieval, reranking, or context construction.
# - Contain vector-store-specific behavior.
# - Assume dense vectors are the only representation mechanism.
# - Implement Representation Intelligence or adaptive provider selection.
# - Implement concurrency, batching, or NFT execution policy.
# - Expose LangChain, LangGraph, or external framework types.
#
# Architectural Position:
# - Stable execution boundary between KnowledgeUnit and
#   KnowledgeRepresentation.
# - Keeps retrieval representation technology independent from governed
#   Knowledge semantics.
# - Allows native and future provider-backed implementations to coexist.
#
# Reuse Value:
# - Dense embedding providers.
# - Sparse representation providers.
# - Lexical representation providers.
# - Structured representation providers.
# - Graph representation providers.
# - Future multimodal representation providers.
#
# Future Extensibility:
# - Multiple providers may represent the same Knowledge Unit.
# - Multiple representation versions may coexist during migration.
# - Provider capability discovery can evolve outside this interface.
# - Representation Intelligence can select providers above this boundary.
# - Batching and parallel execution can evolve without changing the
#   semantic provider contract.
# - External framework adapters may implement this interface while their
#   framework-specific types remain inside integration boundaries.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)


class RepresentationProvider(ABC):
    """
    Universal provider boundary for Knowledge representation generation.

    Implementations convert governed Knowledge Units into retrieval
    representations while preserving ALHF identity and provenance.
    """

    @property
    @abstractmethod
    def provider_ref(self) -> str:
        """Return the stable logical provider identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def provider_version(self) -> str:
        """Return the stable provider behavior version."""

        raise NotImplementedError

    @abstractmethod
    def supports(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        """
        Return whether this provider supports the Knowledge Unit.

        Compatibility must depend on governed Knowledge semantics rather
        than physical source type, original file format, or index
        technology.
        """

        raise NotImplementedError

    @abstractmethod
    def represent(
        self,
        unit: KnowledgeUnit,
    ) -> KnowledgeRepresentation:
        """
        Produce one retrieval representation for one Knowledge Unit.

        Implementations must preserve Knowledge Unit, derivation,
        Knowledge scope, resource, and revision provenance in the
        returned KnowledgeRepresentation.
        """

        raise NotImplementedError
