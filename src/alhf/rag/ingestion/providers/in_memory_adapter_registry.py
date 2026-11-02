# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the in-memory adapter registry implementation used by the
# ALHF Knowledge Foundation acquisition plane.
#
# Problem Solved:
# Acquisition orchestration requires a concrete way to resolve configured
# Knowledge source adapters and their capabilities without hard-coded
# provider conditionals in the common ingestion path.
#
# Responsibilities:
# - Register configured Knowledge source adapters.
# - Associate adapters with provider-neutral capability declarations.
# - Resolve adapters by stable logical adapter reference.
# - Resolve capabilities by the same stable adapter reference.
# - Reject duplicate adapter references.
# - Normalize and validate adapter references.
#
# Must Not:
# - Instantiate source adapters.
# - Load plugins dynamically.
# - Contain provider-specific source behavior.
# - Store credentials, secrets, or connection information.
# - Perform Knowledge acquisition.
# - Perform synchronization.
# - Perform parsing, chunking, embedding, indexing, or retrieval.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
#
# Architectural Position:
# - Concrete V1 implementation of AdapterRegistry.
# - Composition mechanism for local and deterministic execution.
# - Keeps acquisition orchestration independent from adapter instances.
#
# Reuse Value:
# - Local development.
# - Deterministic integration testing.
# - Application composition.
# - Customer-specific adapter composition.
#
# Future Extensibility:
# - Plugin-backed registries can implement AdapterRegistry independently.
# - Cloud composition mechanisms can replace this implementation.
# - Capability discovery can evolve without changing acquisition callers.
# - Runtime adapter selection remains governed by stable references.

from __future__ import annotations

from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.interfaces.adapter_registry import (
    AdapterRegistry,
)
from alhf.rag.ingestion.interfaces.knowledge_source_adapter import (
    KnowledgeSourceAdapter,
)


class InMemoryAdapterRegistry(AdapterRegistry):
    """In-memory registry of configured Knowledge source adapters."""

    def __init__(self) -> None:
        self._adapters: dict[str, KnowledgeSourceAdapter] = {}
        self._capabilities: dict[str, AdapterCapabilities] = {}

    def register(
        self,
        *,
        adapter_ref: str,
        adapter: KnowledgeSourceAdapter,
        capabilities: AdapterCapabilities,
    ) -> None:
        """Register one adapter and its declared capabilities."""

        normalized_ref = self._normalize_adapter_ref(
            adapter_ref,
        )

        if not isinstance(
            adapter,
            KnowledgeSourceAdapter,
        ):
            raise TypeError(
                "adapter must be an instance of KnowledgeSourceAdapter"
            )

        if not isinstance(
            capabilities,
            AdapterCapabilities,
        ):
            raise TypeError(
                "capabilities must be an instance of "
                "AdapterCapabilities"
            )

        if normalized_ref in self._adapters:
            raise ValueError(
                f"adapter already registered: {normalized_ref}"
            )

        self._adapters[normalized_ref] = adapter
        self._capabilities[normalized_ref] = capabilities

    def resolve(
        self,
        adapter_ref: str,
    ) -> KnowledgeSourceAdapter:
        """Resolve one registered Knowledge source adapter."""

        normalized_ref = self._normalize_adapter_ref(
            adapter_ref,
        )

        try:
            return self._adapters[normalized_ref]
        except KeyError as exc:
            raise LookupError(
                f"adapter not found: {normalized_ref}"
            ) from exc

    def capabilities(
        self,
        adapter_ref: str,
    ) -> AdapterCapabilities:
        """Resolve capabilities for one registered adapter."""

        normalized_ref = self._normalize_adapter_ref(
            adapter_ref,
        )

        try:
            return self._capabilities[normalized_ref]
        except KeyError as exc:
            raise LookupError(
                f"adapter not found: {normalized_ref}"
            ) from exc

    def __contains__(
        self,
        adapter_ref: object,
    ) -> bool:
        """Return whether a normalized adapter reference is registered."""

        if not isinstance(
            adapter_ref,
            str,
        ):
            return False

        normalized_ref = adapter_ref.strip()

        if not normalized_ref:
            return False

        return normalized_ref in self._adapters

    def __len__(self) -> int:
        """Return the number of registered adapters."""

        return len(
            self._adapters,
        )

    @staticmethod
    def _normalize_adapter_ref(
        adapter_ref: str,
    ) -> str:
        """Validate and normalize a logical adapter reference."""

        if not isinstance(
            adapter_ref,
            str,
        ):
            raise TypeError(
                "adapter_ref must be a string"
            )

        normalized_ref = adapter_ref.strip()

        if not normalized_ref:
            raise ValueError(
                "adapter_ref cannot be empty"
            )

        return normalized_ref
