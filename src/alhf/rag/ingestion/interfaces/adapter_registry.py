# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the provider-neutral adapter-registry boundary used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Acquisition orchestration must resolve configured Knowledge source
# adapters without hard-coded provider conditionals, imports, or physical
# source knowledge in the common ingestion path.
#
# Responsibilities:
# - Resolve acquisition adapters by stable adapter reference.
# - Expose adapter capabilities before acquisition is attempted.
# - Keep adapter discovery independent from concrete providers.
# - Allow local, cloud, hybrid, and customer adapters behind one boundary.
# - Fail explicitly when a requested adapter is unavailable.
#
# Must Not:
# - Implement adapter registration or plugin loading.
# - Instantiate provider-specific adapters.
# - Contain hard-coded provider names.
# - Store credentials, secrets, or connection information.
# - Perform acquisition or synchronization.
# - Perform parsing, chunking, embedding, indexing, or retrieval.
# - Contain Standard RAG, GraphRAG, or Agentic RAG behavior.
# - Contain arbitrary metadata dictionaries.
#
# Architectural Position:
# - Universal adapter-discovery boundary for Knowledge acquisition.
# - Separates acquisition orchestration from adapter composition.
# - Uses capability declarations to protect behavioral compatibility.
#
# Reuse Value:
# - Local acquisition adapters.
# - Cloud acquisition adapters.
# - Enterprise source adapters.
# - Customer-supplied source adapters.
# - Future plugin-based provider discovery.
#
# Future Extensibility:
# - Concrete registries may use configuration, dependency injection,
#   plugins, or deployment-specific composition.
# - Capability-aware orchestration can evolve without changing callers.
# - Provider registration lifecycle remains outside this interface.
# - Future source technologies can participate without core changes.

from __future__ import annotations

from abc import ABC, abstractmethod

from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.interfaces.knowledge_source_adapter import (
    KnowledgeSourceAdapter,
)


class AdapterRegistry(ABC):
    """
    Universal discovery boundary for Knowledge source adapters.

    Adapter references are stable logical identifiers. The registry maps
    those references to configured runtime implementations while keeping
    concrete composition outside the common acquisition pipeline.
    """

    @abstractmethod
    def resolve(
        self,
        adapter_ref: str,
    ) -> KnowledgeSourceAdapter:
        """
        Resolve one configured Knowledge source adapter.

        Args:
            adapter_ref:
                Stable logical reference identifying the required adapter.

        Returns:
            Configured KnowledgeSourceAdapter implementation.

        Raises:
            LookupError:
                When no adapter exists for the requested reference.
        """

        raise NotImplementedError

    @abstractmethod
    def capabilities(
        self,
        adapter_ref: str,
    ) -> AdapterCapabilities:
        """
        Return acquisition capabilities for one configured adapter.

        Args:
            adapter_ref:
                Stable logical reference identifying the adapter.

        Returns:
            Provider-neutral capability declaration.

        Raises:
            LookupError:
                When no adapter exists for the requested reference.
        """

        raise NotImplementedError
