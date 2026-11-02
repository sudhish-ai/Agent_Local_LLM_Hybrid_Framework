# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral indexing orchestration for the ALHF
# Knowledge Foundation V1 indexing layer.
#
# Problem Solved:
# Knowledge representations must become searchable through configured
# index providers without coupling common orchestration to physical
# databases, search engines, deployment technologies, or frameworks.
#
# Responsibilities:
# - Accept one KnowledgeRepresentation and logical index reference.
# - Resolve the configured IndexProvider through IndexRegistry.
# - Validate provider compatibility before indexing.
# - Delegate idempotent representation upsert to the provider.
# - Delegate representation deletion to the provider.
#
# Must Not:
# - Generate Knowledge representations.
# - Modify representation content or identity.
# - Contain vector-store-specific behavior.
# - Perform retrieval, reranking, evidence, or context construction.
# - Implement index lifecycle, promotion, or rollback.
# - Implement Index Intelligence or adaptive provider selection.
# - Implement concurrency, batching, or NFT execution policy.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Common orchestration boundary for physical Knowledge indexing.
# - Connects logical ALHF index references to configured providers.
# - Keeps physical indexing technology behind provider contracts.
#
# Reuse Value:
# - Native in-memory indexing.
# - Dense, sparse, lexical, structured, and graph indexes.
# - Local, cloud, and hybrid deployments.
#
# Future Extensibility:
# - Versioned lifecycle orchestration can compose above this service.
# - Batch and partitioned indexing can wrap this semantic boundary.
# - Additional providers require no representation-contract changes.
# - Index Intelligence can select governed indexes above this layer.

from __future__ import annotations

from alhf.rag.indexing.interfaces.index_provider import (
    IndexProvider,
)
from alhf.rag.indexing.interfaces.index_registry import (
    IndexRegistry,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)


class IndexingService:
    """Provider-neutral orchestration for Knowledge indexing."""

    def __init__(
        self,
        *,
        registry: IndexRegistry,
    ) -> None:
        if not isinstance(
            registry,
            IndexRegistry,
        ):
            raise TypeError(
                "registry must be an instance of IndexRegistry"
            )

        self._registry = registry

    def index(
        self,
        *,
        index_ref: str,
        representation: KnowledgeRepresentation,
    ) -> None:
        """Index one governed representation idempotently."""

        self._validate_representation(
            representation
        )

        provider = self._resolve_provider(
            index_ref=index_ref,
        )

        if not provider.supports(
            representation
        ):
            raise ValueError(
                "resolved index provider does not support "
                "KnowledgeRepresentation"
            )

        provider.upsert(
            representation
        )

    def delete(
        self,
        *,
        index_ref: str,
        representation_id: str,
    ) -> None:
        """Remove one representation from searchable state."""

        representation_id = self._required_text(
            value=representation_id,
            field_name="representation_id",
        )

        provider = self._resolve_provider(
            index_ref=index_ref,
        )

        provider.delete(
            representation_id
        )

    def _resolve_provider(
        self,
        *,
        index_ref: str,
    ) -> IndexProvider:
        """Resolve and validate one configured index provider."""

        index_ref = self._required_text(
            value=index_ref,
            field_name="index_ref",
        )

        provider = self._registry.resolve(
            index_ref
        )

        if not isinstance(
            provider,
            IndexProvider,
        ):
            raise TypeError(
                "registry must return IndexProvider"
            )

        return provider

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
