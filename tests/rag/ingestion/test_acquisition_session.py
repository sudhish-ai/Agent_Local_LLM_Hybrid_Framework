# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF BoundedAcquisitionSession implementation.
#
# Responsibilities:
# - Validate bounded incremental acquisition.
# - Validate terminal acquisition results.
# - Validate acquired-resource counting.
# - Validate partial and completed acquisition states.
# - Validate continuation behavior.
# - Validate source and Knowledge-scope continuity.
# - Validate invalid adapter output rejection.
# - Validate session lifecycle constraints.
#
# Must Not:
# - Test physical source acquisition.
# - Test adapter resolution or registration.
# - Test synchronization persistence.
# - Test parsing, chunking, embedding, indexing, or retrieval.
# - Materialize an unbounded Knowledge source.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

import pytest

from alhf.rag.ingestion.acquisition_session import (
    BoundedAcquisitionSession,
)
from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.acquisition_result import (
    AcquisitionStatus,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


def _source() -> KnowledgeSource:
    return KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="test-adapter",
    )


def _request(
    *,
    max_resources: int = 10,
    continuation_ref: str | None = None,
    checkpoint_ref: str | None = None,
) -> AcquisitionRequest:
    return AcquisitionRequest(
        source=_source(),
        max_resources=max_resources,
        continuation_ref=continuation_ref,
        checkpoint_ref=checkpoint_ref,
    )


def _resource(
    resource_id: str,
    *,
    source_ref: str = "source-001",
    knowledge_scope_ref: str = "scope-001",
) -> AcquiredResource:
    return AcquiredResource(
        identity=ResourceIdentity(
            knowledge_scope_ref=knowledge_scope_ref,
            source_ref=source_ref,
            logical_resource_id=resource_id,
            revision_id=f"{resource_id}-revision-001",
        ),
        content=b"knowledge",
        media_type="text/plain",
    )


def test_session_streams_all_resources_when_within_bound() -> None:
    session = BoundedAcquisitionSession(
        request=_request(
            max_resources=10,
        ),
        resources=iter(
            (
                _resource("resource-001"),
                _resource("resource-002"),
            )
        ),
    )

    resources = tuple(
        session.resources()
    )

    assert tuple(
        resource.resource_ref
        for resource in resources
    ) == (
        "resource-001",
        "resource-002",
    )


def test_completed_session_returns_completed_result() -> None:
    session = BoundedAcquisitionSession(
        request=_request(
            max_resources=10,
        ),
        resources=iter(
            (
                _resource("resource-001"),
            )
        ),
    )

    tuple(
        session.resources()
    )
    result = session.result()

    assert result.status == AcquisitionStatus.COMPLETED
    assert result.acquired_count == 1
    assert result.has_more is False
    assert result.continuation_ref is None


def test_empty_resource_stream_completes_with_zero_count() -> None:
    session = BoundedAcquisitionSession(
        request=_request(),
        resources=iter(()),
    )

    resources = tuple(
        session.resources()
    )
    result = session.result()

    assert resources == ()
    assert result.status == AcquisitionStatus.COMPLETED
    assert result.acquired_count == 0
    assert result.has_more is False


def test_result_rejected_before_resource_consumption() -> None:
    session = BoundedAcquisitionSession(
        request=_request(),
        resources=iter(()),
    )

    with pytest.raises(
        RuntimeError,
        match="acquisition has not completed",
    ):
        session.result()


def test_session_enforces_resource_bound() -> None:
    session = BoundedAcquisitionSession(
        request=_request(
            max_resources=2,
            continuation_ref="continuation-001",
        ),
        resources=iter(
            (
                _resource("resource-001"),
                _resource("resource-002"),
                _resource("resource-003"),
            )
        ),
    )

    resources = tuple(
        session.resources()
    )
    result = session.result()

    assert len(resources) == 2
    assert result.acquired_count == 2
    assert result.status == AcquisitionStatus.PARTIAL
    assert result.has_more is True


def test_partial_session_preserves_continuation_reference() -> None:
    session = BoundedAcquisitionSession(
        request=_request(
            max_resources=1,
            continuation_ref="continuation-001",
        ),
        resources=iter(
            (
                _resource("resource-001"),
                _resource("resource-002"),
            )
        ),
    )

    tuple(
        session.resources()
    )
    result = session.result()

    assert result.has_more is True
    assert result.continuation_ref == "continuation-001"


def test_completed_session_preserves_checkpoint_reference() -> None:
    session = BoundedAcquisitionSession(
        request=_request(
            checkpoint_ref="checkpoint-001",
        ),
        resources=iter(
            (
                _resource("resource-001"),
            )
        ),
    )

    tuple(
        session.resources()
    )
    result = session.result()

    assert result.checkpoint_ref == "checkpoint-001"


def test_session_rejects_resource_from_different_source() -> None:
    session = BoundedAcquisitionSession(
        request=_request(),
        resources=iter(
            (
                _resource(
                    "resource-001",
                    source_ref="different-source",
                ),
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "acquired resource source_ref must match request source"
        ),
    ):
        tuple(
            session.resources()
        )


def test_session_rejects_resource_from_different_scope() -> None:
    session = BoundedAcquisitionSession(
        request=_request(),
        resources=iter(
            (
                _resource(
                    "resource-001",
                    knowledge_scope_ref="different-scope",
                ),
            )
        ),
    )

    with pytest.raises(
        ValueError,
        match=(
            "acquired resource knowledge scope must match request"
        ),
    ):
        tuple(
            session.resources()
        )


def test_session_rejects_invalid_adapter_output() -> None:
    session = BoundedAcquisitionSession(
        request=_request(),
        resources=iter(
            (
                "invalid-resource",
            )
        ),
    )

    with pytest.raises(
        TypeError,
        match="adapter must yield AcquiredResource instances",
    ):
        tuple(
            session.resources()
        )


def test_completed_session_cannot_be_consumed_again() -> None:
    session = BoundedAcquisitionSession(
        request=_request(),
        resources=iter(
            (
                _resource("resource-001"),
            )
        ),
    )

    tuple(
        session.resources()
    )

    with pytest.raises(
        RuntimeError,
        match="acquisition session has already completed",
    ):
        tuple(
            session.resources()
        )


def test_session_rejects_invalid_request() -> None:
    with pytest.raises(
        TypeError,
        match="request must be an instance of AcquisitionRequest",
    ):
        BoundedAcquisitionSession(
            request="invalid-request",
            resources=iter(()),
        )


def test_session_rejects_non_iterator_resources() -> None:
    with pytest.raises(
        TypeError,
        match="resources must be an Iterator",
    ):
        BoundedAcquisitionSession(
            request=_request(),
            resources=[
                _resource("resource-001"),
            ],
        )
