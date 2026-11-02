# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the concrete provider-neutral acquisition service used by the
# ALHF Knowledge Foundation ingestion plane.
#
# Problem Solved:
# Knowledge acquisition requires orchestration that resolves configured
# source adapters, validates their declared capabilities, starts bounded
# acquisition, and exposes resources through a streaming session without
# coupling callers to physical source technologies.
#
# Responsibilities:
# - Implement the universal AcquisitionService boundary.
# - Resolve source adapters through AdapterRegistry.
# - Resolve adapter capabilities before acquisition.
# - Reject acquisition requests requiring unsupported capabilities.
# - Start provider-neutral source acquisition.
# - Return a bounded streaming acquisition session.
# - Preserve source and Knowledge-scope boundaries.
#
# Must Not:
# - Contain hard-coded source-provider conditionals.
# - Materialize an entire Knowledge source in memory.
# - Store credentials, secrets, paths, URLs, or connection information.
# - Parse or normalize acquired content.
# - Perform chunking, embedding, indexing, or retrieval.
# - Generate source, resource, or revision identities.
# - Persist synchronization checkpoints.
# - Implement threading, multiprocessing, or async execution policy.
# - Contain Standard RAG, GraphRAG, or Agentic RAG retrieval logic.
#
# Architectural Position:
# - Concrete orchestration implementation of AcquisitionService.
# - Connects logical Knowledge sources to configured acquisition adapters.
# - Keeps provider resolution and capability validation outside callers.
# - Preserves bounded streaming semantics for large-scale ingestion.
#
# Reuse Value:
# - Local development and production deployments.
# - Cloud and hybrid deployments.
# - Customer-specific Knowledge source adapters.
# - Incremental and resumable acquisition workflows.
# - Future performance-oriented ingestion execution.
#
# Future Extensibility:
# - Concurrency and worker execution remain separate execution policies.
# - Adapter selection intelligence can evolve behind registry boundaries.
# - Synchronization orchestration can build on the same service.
# - Capability-aware routing can evolve without changing callers.
# - Distributed acquisition can preserve this logical service boundary.

from __future__ import annotations

from alhf.rag.ingestion.acquisition_session import (
    BoundedAcquisitionSession,
)
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.interfaces.acquisition_service import (
    AcquisitionService,
    AcquisitionSession,
)
from alhf.rag.ingestion.interfaces.adapter_registry import (
    AdapterRegistry,
)


class DefaultAcquisitionService(AcquisitionService):
    """Provider-neutral bounded Knowledge acquisition orchestrator."""

    def __init__(
        self,
        *,
        registry: AdapterRegistry,
    ) -> None:
        if not isinstance(
            registry,
            AdapterRegistry,
        ):
            raise TypeError(
                "registry must be an instance of AdapterRegistry"
            )

        self._registry = registry

    def acquire(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionSession:
        """Start one bounded acquisition session."""

        if not isinstance(
            request,
            AcquisitionRequest,
        ):
            raise TypeError(
                "request must be an instance of AcquisitionRequest"
            )

        adapter_ref = request.source.adapter_ref

        capabilities = self._registry.capabilities(
            adapter_ref,
        )

        self._validate_capabilities(
            request=request,
            capabilities=capabilities,
        )

        adapter = self._registry.resolve(
            adapter_ref,
        )

        resources = adapter.acquire(
            request.source,
        )

        return BoundedAcquisitionSession(
            request=request,
            resources=resources,
        )

    @staticmethod
    def _validate_capabilities(
        *,
        request: AcquisitionRequest,
        capabilities: AdapterCapabilities,
    ) -> None:
        """Validate requested behavior against adapter capabilities."""

        if not isinstance(
            capabilities,
            AdapterCapabilities,
        ):
            raise TypeError(
                "registry must return AdapterCapabilities"
            )

        if (
            request.source.synchronization_enabled
            and not capabilities.supports_synchronization
        ):
            raise ValueError(
                "source requires synchronization capability"
            )

        if (
            request.continuation_ref is not None
            and not capabilities.supports_continuation
        ):
            raise ValueError(
                "request continuation requires continuation capability"
            )

        if (
            request.checkpoint_ref is not None
            and not capabilities.supports_synchronization
        ):
            raise ValueError(
                "checkpoint requires synchronization capability"
            )
