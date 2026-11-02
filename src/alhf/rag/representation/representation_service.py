# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides provider-neutral representation orchestration for the
# ALHF Knowledge Foundation representation layer.
#
# Problem Solved:
# Knowledge Units require retrieval representations, but common
# orchestration must remain independent from representation providers,
# embedding models, vector stores, external frameworks, and future
# retrieval technologies.
#
# Responsibilities:
# - Accept one provider-neutral KnowledgeUnit.
# - Resolve a compatible provider through RepresentationRegistry.
# - Validate provider compatibility before representation.
# - Delegate representation generation to RepresentationProvider.
# - Validate representation provenance continuity.
# - Return provider-neutral KnowledgeRepresentation.
#
# Must Not:
# - Modify KnowledgeUnit content or identity.
# - Generate representations directly.
# - Contain embedding-model-specific behavior.
# - Contain vector-store-specific behavior.
# - Perform indexing, retrieval, reranking, or context construction.
# - Implement Representation Intelligence or adaptive provider selection.
# - Implement concurrency, batching, or NFT execution policy.
# - Depend on LangChain, LangGraph, or external framework types.
#
# Architectural Position:
# - Common orchestration boundary of the representation layer.
# - Connects KnowledgeUnit to dynamically selected providers.
# - Keeps representation technology outside governed Knowledge semantics.
#
# Reuse Value:
# - Dense representations.
# - Sparse and lexical representations.
# - Structured and graph representations.
# - Future multimodal representations.
# - Local, cloud, hybrid, and external provider implementations.
#
# Future Extensibility:
# - Representation Intelligence can select providers above this layer.
# - Multiple representation workflows can compose around this service.
# - Provider/model migrations require no KnowledgeUnit redesign.
# - Batching and parallel execution can wrap this semantic boundary.
# - External providers can remain isolated behind ALHF interfaces.

from __future__ import annotations

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)
from alhf.rag.representation.interfaces.representation_provider import (
    RepresentationProvider,
)
from alhf.rag.representation.interfaces.representation_registry import (
    RepresentationRegistry,
)


class RepresentationService:
    """Provider-neutral orchestration for Knowledge representation."""

    def __init__(
        self,
        *,
        registry: RepresentationRegistry,
    ) -> None:
        if not isinstance(
            registry,
            RepresentationRegistry,
        ):
            raise TypeError(
                "registry must be an instance of RepresentationRegistry"
            )

        self._registry = registry

    def represent(
        self,
        unit: KnowledgeUnit,
    ) -> KnowledgeRepresentation:
        """Resolve and invoke a compatible representation provider."""

        if not isinstance(
            unit,
            KnowledgeUnit,
        ):
            raise TypeError(
                "unit must be an instance of KnowledgeUnit"
            )

        provider = self._registry.resolve(
            unit,
        )

        self._validate_provider(
            provider=provider,
            unit=unit,
        )

        representation = provider.represent(
            unit,
        )

        self._validate_result(
            unit=unit,
            representation=representation,
        )

        return representation

    @staticmethod
    def _validate_provider(
        *,
        provider: RepresentationProvider,
        unit: KnowledgeUnit,
    ) -> None:
        """Validate registry output and provider compatibility."""

        if not isinstance(
            provider,
            RepresentationProvider,
        ):
            raise TypeError(
                "registry must return RepresentationProvider"
            )

        if not provider.supports(
            unit,
        ):
            raise ValueError(
                "resolved provider does not support Knowledge Unit"
            )

    @staticmethod
    def _validate_result(
        *,
        unit: KnowledgeUnit,
        representation: KnowledgeRepresentation,
    ) -> None:
        """Protect Knowledge provenance across representation."""

        if not isinstance(
            representation,
            KnowledgeRepresentation,
        ):
            raise TypeError(
                "provider must return KnowledgeRepresentation"
            )

        if representation.knowledge_unit_ref != unit.unit_id:
            raise ValueError(
                "representation Knowledge Unit reference must match unit"
            )

        if representation.derivation_id != unit.derivation_id:
            raise ValueError(
                "representation derivation identity must match unit"
            )

        if representation.knowledge_scope_ref != unit.knowledge_scope_ref:
            raise ValueError(
                "representation Knowledge scope must match unit"
            )

        if representation.resource_ref != unit.resource_ref:
            raise ValueError(
                "representation resource reference must match unit"
            )

        if representation.revision_ref != unit.revision_ref:
            raise ValueError(
                "representation revision reference must match unit"
            )
