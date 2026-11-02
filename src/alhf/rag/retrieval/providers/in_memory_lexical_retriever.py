# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic lexical retrieval for ALHF RAG V1.
#
# Problem Solved:
# V1 requires bounded ranked retrieval over the native in-memory index
# without embeddings, vector databases, or external frameworks.
#
# Responsibilities:
# - Retrieve lexical KnowledgeRepresentation artifacts.
# - Tokenize queries and indexed text deterministically.
# - Score candidates using query-term coverage.
# - Return deterministic ranked RetrievalResult objects.
# - Enforce explicit bounded retrieval.
# - Preserve Knowledge and index provenance.
#
# Must Not:
# - Generate embeddings or perform semantic retrieval.
# - Modify indexed representations.
# - Treat retrieval candidates as validated Evidence.
# - Perform reranking, Evidence, or Context construction.
# - Implement adaptive Retrieval Intelligence.
# - Implement GraphRAG or Agentic RAG orchestration.
# - Depend on external RAG frameworks.

from __future__ import annotations

import re

from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    RepresentationKind,
)
from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)
from alhf.rag.retrieval.interfaces.retriever import (
    Retriever,
)


class InMemoryLexicalRetriever(Retriever):
    """Deterministic lexical retriever for the native V1 index."""

    _RETRIEVER_REF = "in-memory-lexical-retriever"
    _RETRIEVER_VERSION = "1.0"

    def __init__(
        self,
        *,
        provider: InMemoryIndexProvider,
    ) -> None:
        if not isinstance(
            provider,
            InMemoryIndexProvider,
        ):
            raise TypeError(
                "provider must be an instance of InMemoryIndexProvider"
            )

        self._provider = provider

    @property
    def retriever_ref(self) -> str:
        return self._RETRIEVER_REF

    @property
    def retriever_version(self) -> str:
        return self._RETRIEVER_VERSION

    @property
    def representation_kind(self) -> RepresentationKind:
        return RepresentationKind.LEXICAL

    def retrieve(
        self,
        *,
        query: str,
        index_ref: str,
        index_version: str,
        limit: int,
    ):
        query = self._required_text(
            value=query,
            field_name="query",
        )
        index_ref = self._required_text(
            value=index_ref,
            field_name="index_ref",
        )
        index_version = self._required_text(
            value=index_version,
            field_name="index_version",
        )
        self._validate_limit(limit)

        query_terms = self._terms(query)
        ranked = []

        for representation in self._provider.representations():
            if representation.kind != self.representation_kind:
                continue

            score = self._score(
                query_terms,
                representation.payload,
            )

            if score > 0.0:
                ranked.append(
                    (
                        score,
                        representation.representation_id,
                        representation,
                    )
                )

        ranked.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        for rank, item in enumerate(
            ranked[:limit],
            start=1,
        ):
            score, _, representation = item

            yield RetrievalResult(
                representation_ref=representation.representation_id,
                representation_kind=representation.kind,
                knowledge_unit_ref=representation.knowledge_unit_ref,
                derivation_id=representation.derivation_id,
                knowledge_scope_ref=representation.knowledge_scope_ref,
                resource_ref=representation.resource_ref,
                revision_ref=representation.revision_ref,
                index_ref=index_ref,
                index_version=index_version,
                score=score,
                rank=rank,
            )

    @staticmethod
    def _terms(
        text: str,
    ):
        return set(
            re.findall(
                r"[A-Za-z0-9_]+",
                text.lower(),
            )
        )

    def _score(
        self,
        query_terms: set[str],
        payload: bytes,
    ) -> float:
        if not query_terms:
            return 0.0

        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            return 0.0

        document_terms = self._terms(text)
        matches = len(query_terms & document_terms)

        return matches / len(query_terms)

    @staticmethod
    def _validate_limit(
        limit: int,
    ) -> None:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError(
                "limit must be an int"
            )

        if limit <= 0:
            raise ValueError(
                "limit must be greater than zero"
            )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
