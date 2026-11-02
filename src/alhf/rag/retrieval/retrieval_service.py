# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral retrieval orchestration for ALHF RAG V1.
#
# Problem Solved:
# Knowledge retrieval must remain independent from concrete retrieval
# algorithms while preserving bounded execution and result integrity.
#
# Responsibilities:
# - Accept one bounded retrieval request.
# - Delegate retrieval through the configured Retriever.
# - Validate query, index identity, version, and limit.
# - Validate provider-neutral RetrievalResult output.
# - Enforce contiguous result ranking.
# - Prevent concrete retrievers from exceeding the requested limit.
# - Preserve incremental retrieval semantics.
#
# Must Not:
# - Generate or index Knowledge representations.
# - Implement lexical, semantic, or hybrid scoring.
# - Treat retrieval candidates as validated Evidence.
# - Perform reranking, Evidence, or Context construction.
# - Implement adaptive Retrieval Intelligence.
# - Implement GraphRAG or Agentic RAG orchestration.
# - Depend on external RAG frameworks.
#
# Architectural Position:
# - Common orchestration boundary for candidate retrieval.
# - Separates retrieval mechanisms from downstream Evidence.
# - Protects bounded and reproducible V1 retrieval behavior.
#
# Reuse Value:
# - V1 lexical retrieval.
# - Future dense, sparse, hybrid, and graph retrieval.
# - Local, cloud, and hybrid retrieval implementations.
#
# Future Extensibility:
# - KnowledgeRequest can drive this service later.
# - Retrieval Intelligence can select retrievers above this boundary.
# - Dynamic retrieval depth can supply the bounded limit.
# - Reranking remains an independent downstream stage.

from __future__ import annotations

from collections.abc import Iterator

from alhf.rag.retrieval.contracts.retrieval_result import (
    RetrievalResult,
)
from alhf.rag.retrieval.interfaces.retriever import (
    Retriever,
)


class RetrievalService:
    """Provider-neutral orchestration for bounded retrieval."""

    def __init__(
        self,
        *,
        retriever: Retriever,
    ) -> None:
        if not isinstance(
            retriever,
            Retriever,
        ):
            raise TypeError(
                "retriever must be an instance of Retriever"
            )

        self._retriever = retriever

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
        self._validate_limit(
            limit
        )

        results = self._retriever.retrieve(
            query=query,
            index_ref=index_ref,
            index_version=index_version,
            limit=limit,
        )

        if not isinstance(
            results,
            Iterator,
        ):
            raise TypeError(
                "retriever must return an Iterator"
            )

        expected_rank = 1
        count = 0

        for result in results:
            if count >= limit:
                raise ValueError(
                    "retriever returned more results than limit"
                )

            self._validate_result(
                result=result,
                index_ref=index_ref,
                index_version=index_version,
                expected_rank=expected_rank,
            )

            yield result

            count += 1
            expected_rank += 1

    @staticmethod
    def _validate_result(
        *,
        result: RetrievalResult,
        index_ref: str,
        index_version: str,
        expected_rank: int,
    ) -> None:
        if not isinstance(
            result,
            RetrievalResult,
        ):
            raise TypeError(
                "retriever must yield RetrievalResult"
            )

        if result.index_ref != index_ref:
            raise ValueError(
                "RetrievalResult index_ref must match request"
            )

        if result.index_version != index_version:
            raise ValueError(
                "RetrievalResult index_version must match request"
            )

        if result.rank != expected_rank:
            raise ValueError(
                "RetrievalResult rank must be contiguous"
            )

    @staticmethod
    def _validate_limit(
        limit: int,
    ) -> None:
        if isinstance(
            limit,
            bool,
        ) or not isinstance(
            limit,
            int,
        ):
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
        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
