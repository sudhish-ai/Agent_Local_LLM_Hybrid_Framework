# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF DefaultAcquisitionService.
#
# Responsibilities:
# - Validate provider-neutral acquisition orchestration.
# - Validate adapter resolution through AdapterRegistry.
# - Validate adapter capability enforcement.
# - Validate bounded AcquisitionSession creation.
# - Validate source synchronization requirements.
# - Validate continuation requirements.
# - Validate checkpoint requirements.
# - Validate invalid dependency and request rejection.
#
# Must Not:
# - Test physical source acquisition.
# - Test concrete provider behavior.
# - Test parsing, chunking, embedding, indexing, or retrieval.
# - Test threading, multiprocessing, or asynchronous execution.
# - Test performance, scalability, stress, or longevity behavior.
# - Test Standard RAG, GraphRAG, or Agentic RAG retrieval behavior.

import pytest

from alhf.rag.ingestion.acquisition_service import (
    DefaultAcquisitionService,
)
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.interfaces.acquisition_service import (
    AcquisitionSession,
)
from alhf.rag.ingestion.interfaces.adapter_registry import (
    AdapterRegistry,
)
from alhf.rag.ingestion.interfaces.knowledge_source_adapter import (
    KnowledgeSourceAdapter,
)
from alhf.rag.ingestion.providers.in_memory_adapter_registry import (
    InMemoryAdapterRegistry,
)


class StubKnowledgeSourceAdapter(KnowledgeSourceAdapter):
    """Minimal adapter used to validate acquisition orchestration."""

    def acquire(
        self,
        source: KnowledgeSource,
    ):
        return iter(())


def _source(
    *,
    synchronization_enabled: bool = False,
) -> KnowledgeSource:
    return KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="test-adapter",
        synchronization_enabled=synchronization_enabled,
    )


def _registry(
    *,
    capabilities: AdapterCapabilities | None = None,
) -> InMemoryAdapterRegistry:
    registry = InMemoryAdapterRegistry()

    registry.register(
        adapter_ref="test-adapter",
        adapter=StubKnowledgeSourceAdapter(),
        capabilities=(
            capabilities
            if capabilities is not None
            else AdapterCapabilities()
        ),
    )

    return registry


def test_create_default_acquisition_service() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )

    assert isinstance(
        service,
        DefaultAcquisitionService,
    )


def test_service_implements_acquisition_service() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )

    from alhf.rag.ingestion.interfaces.acquisition_service import (
        AcquisitionService,
    )

    assert isinstance(
        service,
        AcquisitionService,
    )


def test_acquire_returns_bounded_session() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )
    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    session = service.acquire(
        request,
    )

    assert isinstance(
        session,
        AcquisitionSession,
    )


def test_acquire_resolves_configured_adapter() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )
    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    session = service.acquire(
        request,
    )

    assert tuple(
        session.resources()
    ) == ()


def test_synchronization_requires_adapter_capability() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )
    request = AcquisitionRequest(
        source=_source(
            synchronization_enabled=True,
        ),
        max_resources=10,
    )

    with pytest.raises(
        ValueError,
        match="source requires synchronization capability",
    ):
        service.acquire(
            request,
        )


def test_synchronization_supported_when_declared() -> None:
    capabilities = AdapterCapabilities(
        supports_synchronization=True,
    )
    service = DefaultAcquisitionService(
        registry=_registry(
            capabilities=capabilities,
        ),
    )
    request = AcquisitionRequest(
        source=_source(
            synchronization_enabled=True,
        ),
        max_resources=10,
    )

    session = service.acquire(
        request,
    )

    assert isinstance(
        session,
        AcquisitionSession,
    )


def test_continuation_requires_adapter_capability() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )
    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
        continuation_ref="continuation-001",
    )

    with pytest.raises(
        ValueError,
        match=(
            "request continuation requires "
            "continuation capability"
        ),
    ):
        service.acquire(
            request,
        )


def test_checkpoint_requires_synchronization_capability() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )
    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
        checkpoint_ref="checkpoint-001",
    )

    with pytest.raises(
        ValueError,
        match="checkpoint requires synchronization capability",
    ):
        service.acquire(
            request,
        )


def test_unknown_adapter_is_rejected() -> None:
    service = DefaultAcquisitionService(
        registry=InMemoryAdapterRegistry(),
    )
    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    with pytest.raises(
        LookupError,
        match="adapter not found: test-adapter",
    ):
        service.acquire(
            request,
        )


def test_service_rejects_invalid_registry() -> None:
    with pytest.raises(
        TypeError,
        match="registry must be an instance of AdapterRegistry",
    ):
        DefaultAcquisitionService(
            registry="invalid-registry",
        )


def test_acquire_rejects_invalid_request() -> None:
    service = DefaultAcquisitionService(
        registry=_registry(),
    )

    with pytest.raises(
        TypeError,
        match=(
            "request must be an instance of AcquisitionRequest"
        ),
    ):
        service.acquire(
            "invalid-request",
        )


class InvalidCapabilitiesRegistry(AdapterRegistry):
    """Registry intentionally violating its capability contract."""

    def resolve(
        self,
        adapter_ref: str,
    ) -> KnowledgeSourceAdapter:
        return StubKnowledgeSourceAdapter()

    def capabilities(
        self,
        adapter_ref: str,
    ) -> AdapterCapabilities:
        return "invalid-capabilities"


def test_invalid_registry_capabilities_are_rejected() -> None:
    service = DefaultAcquisitionService(
        registry=InvalidCapabilitiesRegistry(),
    )
    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    with pytest.raises(
        TypeError,
        match="registry must return AdapterCapabilities",
    ):
        service.acquire(
            request,
        )
