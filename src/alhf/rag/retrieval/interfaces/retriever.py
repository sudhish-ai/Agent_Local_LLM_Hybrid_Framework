# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal retrieval boundary used by the ALHF Knowledge
# Foundation retrieval layer.
#
# Problem Solved:
# Indexed Knowledge must be retrieved without coupling callers to
# lexical search, dense similarity, sparse search, GraphRAG, physical
# index providers, or future retrieval technologies.
#
# Responsibilities:
# - Accept a query and logical index identity.
# - Return bounded provider-neutral RetrievalResult candidates.
# - Expose stable retriever identity and version.
# - Declare the representation kind supported by the retriever.
# - Preserve index and Knowledge provenance through retrieval results.
# - Keep retrieval mechanisms replaceable behind one stable boundary.
#
# Must Not:
# - Generate or mutate Knowledge representations.
# - Perform indexing or representation generation.
# - Treat retrieval candidates as validated Evidence.
# - Perform Evidence or Context construction.
# - Perform generation.
# - Implement Retrieval Intelligence or adaptive strategy selection.
# - Assume dense semantic retrieval is the only retrieval mechanism.
# - Implement GraphRAG or Agentic RAG orchestration in this interface.
# - Depend on LangChain, LangGraph, or external RAG frameworks.
#
# Architectural Position:
# - Stable execution boundary between searchable Knowledge and
#   provider-neutral retrieval candidates.
# - Keeps retrieval algorithms independent from downstream Evidence.
#
# Reuse Value:
# - V1 deterministic lexical retrieval.
# - Dense semantic retrieval.
# - Sparse retrieval.
# - Hybrid retrieval.
# - Structured and graph retrieval.
# - Future Agentic RAG retrieval mechanisms.
#
# Future Extensibility:
# - Evidence-driven Retrieval Intelligence may select retrievers later.
# - Multiple retrievers may participate in hybrid retrieval.
# - Adaptive retrieval depth can evolve above this boundary.
# - Query transformation and reranking remain separate concerns.
# - External retrieval tools can implement this interface through
#   adapters without changing ALHF Knowledge contracts.

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator

from alhf.rag.representation.contracts.knowledge_representation import (
    RepresentationKind,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)


class Retriever(ABC):
    """Universal provider-neutral Knowledge retrieval boundary."""

    @property
    @abstractmethod
    def retriever_ref(self) -> str:
        """Return the stable logical retriever identifier."""

        raise NotImplementedError

    @property
    @abstractmethod
    def retriever_version(self) -> str:
        """Return the stable retriever behavior version."""

        raise NotImplementedError

    @property
    @abstractmethod
    def representation_kind(self) -> RepresentationKind:
        """Return the representation kind consumed by this retriever."""

        raise NotImplementedError

    @abstractmethod
    def retrieve(
        self,
        *,
        query: str,
        index_ref: str,
        index_version: str,
        limit: int,
    ) -> Iterator[RetrievalResult]:
        """
        Yield bounded retrieval candidates in ranked order.

        Args:
            query:
                Query used for candidate retrieval.
            index_ref:
                Logical ALHF index reference.
            index_version:
                Exact logical index version searched.
            limit:
                Maximum number of candidates returned.

        Returns:
            Incremental iterator of RetrievalResult candidates ordered
            from best to worst according to the concrete retriever.
        """

        raise NotImplementedError
