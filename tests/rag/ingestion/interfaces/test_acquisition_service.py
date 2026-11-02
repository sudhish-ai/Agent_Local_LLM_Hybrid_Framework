# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF AcquisitionService and AcquisitionSession
# interfaces.
#
# Responsibilities:
# - Validate the abstract acquisition-service boundary.
# - Validate the abstract bounded acquisition-session boundary.
# - Validate incremental AcquiredResource delivery.
# - Validate iterator-based resource consumption.
# - Validate terminal AcquisitionResult availability.
# - Validate resource streaming remains separate from result state.
# - Protect bounded acquisition semantics against regression.
#
# Must Not:
# - Test concrete Knowledge source adapters.
# - Test physical source acquisition.
# - Test provider routing or capability discovery.
# - Test synchronization orchestration.
# - Test parsing, chunking, embedding, indexing, or retrieval.
# - Materialize an unbounded Knowledge source.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

from collections.abc import Iterator

import pytest

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.acquisition_result import (
    AcquisitionResult,
    AcquisitionStatus,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.interfaces.acquisition_service import (
    AcquisitionService,
    AcquisitionSession,
)


class StubAcquisitionSession(AcquisitionSession):
    """Completed acquisition session used for interface testing."""

    def __init__(self) -> None:
        self._complete = False

    def resources(self):
        yield AcquiredResource(
            identity=ResourceIdentity(
                knowledge_scope_ref="scope-001",
                source_ref="source-001",
                logical_resource_id="resource-001",
                revision_id="revision-001",
            ),
            content=b"knowledge",
            media_type="text/plain",
        )
        self._complete = True

    def result(self) -> AcquisitionResult:
        if not self._complete:
            raise RuntimeError(
                "acquisition has not completed"
            )

        return AcquisitionResult(
            source_ref="source-001",
            status=AcquisitionStatus.COMPLETED,
            acquired_count=1,
            has_more=False,
        )


class StubAcquisitionService(AcquisitionService):
    """Concrete acquisition service used for interface testing."""

    def acquire(
        self,
        request: AcquisitionRequest,
    ) -> AcquisitionSession:
        return StubAcquisitionSession()


class MissingResourcesSession(AcquisitionSession):
    """Invalid session missing resources implementation."""

    def result(self) -> AcquisitionResult:
        raise NotImplementedError


class MissingResultSession(AcquisitionSession):
    """Invalid session missing result implementation."""

    def resources(self):
        return iter(())


class MissingAcquireService(AcquisitionService):
    """Invalid service missing acquire implementation."""

    pass


def _request() -> AcquisitionRequest:
    source = KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="test-adapter",
    )

    return AcquisitionRequest(
        source=source,
        max_resources=10,
    )


def test_acquisition_session_is_abstract() -> None:
    with pytest.raises(TypeError):
        AcquisitionSession()


def test_acquisition_service_is_abstract() -> None:
    with pytest.raises(TypeError):
        AcquisitionService()


def test_missing_resources_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingResourcesSession()


def test_missing_result_prevents_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingResultSession()


def test_missing_acquire_prevents_service_instantiation() -> None:
    with pytest.raises(TypeError):
        MissingAcquireService()


def test_service_returns_acquisition_session() -> None:
    session = StubAcquisitionService().acquire(
        _request(),
    )

    assert isinstance(
        session,
        AcquisitionSession,
    )


def test_session_resources_returns_iterator() -> None:
    session = StubAcquisitionSession()
    resources = session.resources()

    assert isinstance(
        resources,
        Iterator,
    )


def test_session_yields_acquired_resource() -> None:
    session = StubAcquisitionSession()
    resources = session.resources()
    resource = next(resources)

    assert isinstance(
        resource,
        AcquiredResource,
    )
    assert resource.resource_ref == "resource-001"
    assert resource.revision_ref == "revision-001"


def test_result_is_unavailable_before_completion() -> None:
    session = StubAcquisitionSession()

    with pytest.raises(
        RuntimeError,
        match="acquisition has not completed",
    ):
        session.result()


def test_result_available_after_completion() -> None:
    session = StubAcquisitionSession()

    resources = tuple(
        session.resources(),
    )
    result = session.result()

    assert len(resources) == 1
    assert isinstance(
        result,
        AcquisitionResult,
    )
    assert result.status == AcquisitionStatus.COMPLETED
    assert result.acquired_count == 1
    assert result.source_ref == "source-001"


def test_result_does_not_materialize_resources() -> None:
    session = StubAcquisitionSession()

    tuple(
        session.resources(),
    )
    result = session.result()

    assert not hasattr(
        result,
        "resources",
    )
