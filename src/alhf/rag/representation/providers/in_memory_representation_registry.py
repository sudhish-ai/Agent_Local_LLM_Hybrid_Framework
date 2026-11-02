# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the in-memory representation-provider registry used by the
# ALHF Knowledge Foundation representation layer.
#
# Problem Solved:
# Representation orchestration must resolve compatible providers without
# hard-coding embedding models, representation technologies, external
# frameworks, or provider-specific behavior into common Knowledge logic.
#
# Responsibilities:
# - Register configured RepresentationProvider implementations.
# - Preserve deterministic registration order.
# - Resolve a compatible provider for one KnowledgeUnit.
# - Report whether compatible representation behavior is available.
# - Reject duplicate provider references.
# - Validate provider identity and version during registration.
#
# Must Not:
# - Generate representations directly.
# - Modify KnowledgeUnit content or identity.
# - Contain embedding-model-specific behavior.
# - Contain vector-store-specific behavior.
# - Perform indexing, retrieval, reranking, or context construction.
# - Implement Representation Intelligence or adaptive provider selection.
# - Load plugins or external frameworks directly.
# - Implement concurrency, batching, or NFT execution policy.
#
# Architectural Position:
# - Concrete V1 implementation of RepresentationRegistry.
# - Composition mechanism for configured representation providers.
# - Keeps representation mechanisms behind stable ALHF boundaries.
#
# Reuse Value:
# - Dense representation providers.
# - Sparse and lexical representation providers.
# - Structured and graph representation providers.
# - Future multimodal representation providers.
# - Native and externally backed implementations.
#
# Future Extensibility:
# - Knowledge Intelligence can select among compatible providers.
# - Multiple representation providers can coexist.
# - Plugin-backed registries can implement RepresentationRegistry.
# - External framework adapters can implement RepresentationProvider
#   without changing common ALHF Knowledge contracts.
# - Parallel representation can evolve outside registry semantics.

from __future__ import annotations

from alhf.rag.chunking.contracts.knowledge_unit import (
    KnowledgeUnit,
)
from alhf.rag.representation.interfaces.representation_provider import (
    RepresentationProvider,
)
from alhf.rag.representation.interfaces.representation_registry import (
    RepresentationRegistry,
)


class InMemoryRepresentationRegistry(RepresentationRegistry):
    """In-memory registry of configured representation providers."""

    def __init__(self) -> None:
        self._providers: dict[str, RepresentationProvider] = {}

    def register(
        self,
        provider: RepresentationProvider,
    ) -> None:
        """Register one configured representation provider."""

        if not isinstance(
            provider,
            RepresentationProvider,
        ):
            raise TypeError(
                "provider must be an instance of RepresentationProvider"
            )

        provider_ref = self._required_text(
            value=provider.provider_ref,
            field_name="provider_ref",
        )

        self._required_text(
            value=provider.provider_version,
            field_name="provider_version",
        )

        if provider_ref in self._providers:
            raise ValueError(
                f"provider already registered: {provider_ref}"
            )

        self._providers[provider_ref] = provider

    def resolve(
        self,
        unit: KnowledgeUnit,
    ) -> RepresentationProvider:
        """Resolve the first compatible registered provider."""

        self._validate_unit(
            unit,
        )

        for provider in self._providers.values():
            if provider.supports(
                unit,
            ):
                return provider

        raise LookupError(
            "representation provider not found for Knowledge Unit"
        )

    def contains(
        self,
        unit: KnowledgeUnit,
    ) -> bool:
        """Return whether a compatible provider is registered."""

        self._validate_unit(
            unit,
        )

        return any(
            provider.supports(
                unit,
            )
            for provider in self._providers.values()
        )

    def __contains__(
        self,
        provider_ref: object,
    ) -> bool:
        """Return whether a provider reference is registered."""

        if not isinstance(
            provider_ref,
            str,
        ):
            return False

        normalized_ref = provider_ref.strip()

        if not normalized_ref:
            return False

        return normalized_ref in self._providers

    def __len__(self) -> int:
        """Return the number of registered providers."""

        return len(
            self._providers,
        )

    @staticmethod
    def _validate_unit(
        unit: KnowledgeUnit,
    ) -> None:
        """Validate Knowledge Unit supplied for resolution."""

        if not isinstance(
            unit,
            KnowledgeUnit,
        ):
            raise TypeError(
                "unit must be an instance of KnowledgeUnit"
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
