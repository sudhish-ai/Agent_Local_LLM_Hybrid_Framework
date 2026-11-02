# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the in-memory index-provider registry used by the
# ALHF Knowledge Foundation V1 indexing layer.
#
# Problem Solved:
# Indexing orchestration must resolve logical ALHF index references
# without coupling callers to physical index technologies, provider
# configuration, vector databases, search engines, or external tools.
#
# Responsibilities:
# - Register an IndexProvider against one logical index reference.
# - Resolve the provider for a logical index reference.
# - Report whether a logical index reference is registered.
# - Reject duplicate logical index registrations.
# - Validate logical index and provider identity.
# - Preserve deterministic in-memory registry behavior.
#
# Must Not:
# - Generate Knowledge representations.
# - Perform physical index writes or deletes.
# - Perform retrieval, reranking, or context construction.
# - Contain vector-store-specific configuration.
# - Implement index selection intelligence.
# - Implement promotion, rollback, or lifecycle orchestration.
# - Implement concurrency, batching, or NFT execution policy.
# - Depend on LangChain, LangGraph, or external RAG frameworks.
#
# Architectural Position:
# - Concrete V1 implementation of IndexRegistry.
# - Maps logical ALHF index references to IndexProvider instances.
# - Keeps physical indexing technology behind provider boundaries.
#
# Reuse Value:
# - Local deterministic indexes.
# - Dense vector indexes.
# - Sparse and lexical indexes.
# - Structured and graph indexes.
# - Cloud and hybrid index providers.
#
# Future Extensibility:
# - Version-aware registries can implement IndexRegistry separately.
# - Candidate and active index routing can evolve above this boundary.
# - External provider adapters can register through the same mechanism.
# - Distributed providers can evolve without changing callers.

from __future__ import annotations

from alhf.rag.indexing.interfaces.index_provider import (
    IndexProvider,
)
from alhf.rag.indexing.interfaces.index_registry import (
    IndexRegistry,
)


class InMemoryIndexRegistry(IndexRegistry):
    """In-memory mapping of logical index references to providers."""

    def __init__(self) -> None:
        self._providers: dict[str, IndexProvider] = {}

    def register(
        self,
        *,
        index_ref: str,
        provider: IndexProvider,
    ) -> None:
        """Register one provider for one logical index reference."""

        normalized_ref = self._required_text(
            value=index_ref,
            field_name="index_ref",
        )

        if not isinstance(
            provider,
            IndexProvider,
        ):
            raise TypeError(
                "provider must be an instance of IndexProvider"
            )

        self._required_text(
            value=provider.provider_ref,
            field_name="provider_ref",
        )
        self._required_text(
            value=provider.provider_version,
            field_name="provider_version",
        )

        if normalized_ref in self._providers:
            raise ValueError(
                f"index already registered: {normalized_ref}"
            )

        self._providers[normalized_ref] = provider

    def resolve(
        self,
        index_ref: str,
    ) -> IndexProvider:
        """Resolve the provider for one logical index reference."""

        normalized_ref = self._required_text(
            value=index_ref,
            field_name="index_ref",
        )

        try:
            return self._providers[normalized_ref]
        except KeyError as error:
            raise LookupError(
                f"index provider not found: {normalized_ref}"
            ) from error

    def contains(
        self,
        index_ref: str,
    ) -> bool:
        """Return whether the logical index is registered."""

        normalized_ref = self._required_text(
            value=index_ref,
            field_name="index_ref",
        )

        return normalized_ref in self._providers

    def __contains__(
        self,
        index_ref: object,
    ) -> bool:
        """Support safe membership checks by logical index reference."""

        if not isinstance(
            index_ref,
            str,
        ):
            return False

        normalized_ref = index_ref.strip()

        if not normalized_ref:
            return False

        return normalized_ref in self._providers

    def __len__(self) -> int:
        """Return the number of registered logical indexes."""

        return len(
            self._providers
        )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize required registry text."""

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
