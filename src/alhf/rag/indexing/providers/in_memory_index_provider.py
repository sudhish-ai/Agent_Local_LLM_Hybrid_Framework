# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the native in-memory index provider used by the ALHF
# Knowledge Foundation V1 indexing layer.
#
# Problem Solved:
# V1 requires a deterministic searchable-state implementation that
# proves representation indexing without introducing a vector database,
# search engine, cloud service, or external framework dependency.
#
# Responsibilities:
# - Accept supported KnowledgeRepresentation artifacts.
# - Store representations by stable representation identity.
# - Provide idempotent upsert behavior.
# - Support deletion from searchable state.
# - Preserve representation objects without transformation.
# - Expose stable provider identity and version.
# - Support deterministic inspection for V1 retrieval integration.
#
# Must Not:
# - Generate Knowledge representations.
# - Modify representation identity or payload.
# - Perform retrieval ranking or reranking.
# - Implement vector similarity or embedding behavior.
# - Implement Index Intelligence or lifecycle promotion.
# - Implement concurrency, batching, or NFT execution policy.
# - Depend on LangChain, LangGraph, or external RAG frameworks.
#
# Architectural Position:
# - Concrete V1 implementation of IndexProvider.
# - Native deterministic searchable-state provider.
# - Establishes the physical indexing path before Retrieval.
#
# Reuse Value:
# - V1 Standard RAG execution.
# - Deterministic indexing tests.
# - Local development and E2E validation.
# - Baseline for future index-provider comparisons.
#
# Future Extensibility:
# - Dense, sparse, graph, and cloud providers can implement IndexProvider.
# - Retrieval can consume provider-neutral indexed representations.
# - Versioned index lifecycle can evolve above this provider.
# - Distributed storage can replace this implementation unchanged.

from __future__ import annotations

from collections.abc import Iterator

from alhf.rag.indexing.interfaces.index_provider import (
    IndexProvider,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)


class InMemoryIndexProvider(IndexProvider):
    """Native deterministic in-memory provider for V1 indexing."""

    _PROVIDER_REF = "in-memory-index"
    _PROVIDER_VERSION = "1.0"

    def __init__(self) -> None:
        self._representations: dict[
            str,
            KnowledgeRepresentation,
        ] = {}

    @property
    def provider_ref(self) -> str:
        """Return the stable logical provider identifier."""

        return self._PROVIDER_REF

    @property
    def provider_version(self) -> str:
        """Return the stable provider behavior version."""

        return self._PROVIDER_VERSION

    def supports(
        self,
        representation: KnowledgeRepresentation,
    ) -> bool:
        """Return whether V1 can index the representation."""

        return (
            isinstance(
                representation,
                KnowledgeRepresentation,
            )
            and representation.kind == RepresentationKind.LEXICAL
        )

    def upsert(
        self,
        representation: KnowledgeRepresentation,
    ) -> None:
        """Store one representation idempotently."""

        self._validate_representation(
            representation,
        )

        if not self.supports(
            representation,
        ):
            raise ValueError(
                "InMemoryIndexProvider requires "
                "a lexical KnowledgeRepresentation"
            )

        self._representations[
            representation.representation_id
        ] = representation

    def delete(
        self,
        representation_id: str,
    ) -> None:
        """Remove one representation idempotently."""

        normalized_id = self._required_text(
            value=representation_id,
            field_name="representation_id",
        )

        self._representations.pop(
            normalized_id,
            None,
        )

    def get(
        self,
        representation_id: str,
    ) -> KnowledgeRepresentation | None:
        """Return one indexed representation when present."""

        normalized_id = self._required_text(
            value=representation_id,
            field_name="representation_id",
        )

        return self._representations.get(
            normalized_id
        )

    def representations(
        self,
    ) -> Iterator:
        """Yield currently indexed representations incrementally."""

        return iter(
            self._representations.values()
        )

    def __contains__(
        self,
        representation_id: object,
    ) -> bool:
        """Return whether representation identity is indexed."""

        if not isinstance(
            representation_id,
            str,
        ):
            return False

        normalized_id = representation_id.strip()

        if not normalized_id:
            return False

        return normalized_id in self._representations

    def __len__(self) -> int:
        """Return the number of indexed representations."""

        return len(
            self._representations
        )

    @staticmethod
    def _validate_representation(
        representation: KnowledgeRepresentation,
    ) -> None:
        if not isinstance(
            representation,
            KnowledgeRepresentation,
        ):
            raise TypeError(
                "representation must be an instance of "
                "KnowledgeRepresentation"
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
