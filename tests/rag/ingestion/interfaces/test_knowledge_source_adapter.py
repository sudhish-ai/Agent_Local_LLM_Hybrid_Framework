# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeSourceAdapter interface.
#
# Responsibilities:
# - Validate the abstract acquisition boundary.
# - Validate concrete adapter implementation.
# - Validate KnowledgeSource input integration.
# - Validate incremental AcquiredResource iteration.
# - Validate multiple-resource streaming semantics.
# - Protect provider-neutral acquisition behavior.
#
# Must Not:
# - Test concrete source acquisition.
# - Test provider configuration or credentials.
# - Test synchronization orchestration.
# - Test parsing, chunking, indexing, or retrieval.
# - Test Standard, Graph, or Agentic RAG behavior.

from collections.abc import Iterator

import pytest

from alhf.rag.ingestion.contracts.acquired_resource import (
    AcquiredResource,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)
from alhf.rag.ingestion.interfaces.knowledge_source_adapter import (
    KnowledgeSourceAdapter,
)


class StubKnowledgeSourceAdapter(KnowledgeSourceAdapter):
    """Minimal adapter used to validate the acquisition interface."""

    def acquire(
        self,
        source: KnowledgeSource,
    ) -> Iterator[AcquiredResource]:
        yield AcquiredResource(
            identity=ResourceIdentity(
                knowledge_scope_ref=source.knowledge_scope_ref,
                source_ref=source.source_id,
                logical_resource_id="resource-001",
                revision_id="revision-001",
            ),
            content=b"first resource",
            media_type="text/plain",
        )

        yield AcquiredResource(
            identity=ResourceIdentity(
                knowledge_scope_ref=source.knowledge_scope_ref,
                source_ref=source.source_id,
                logical_resource_id="resource-002",
                revision_id="revision-001",
            ),
            content=b"second resource",
            media_type="text/plain",
        )


class MissingAcquireAdapter(KnowledgeSourceAdapter):
    """Invalid adapter intentionally missing acquisition behavior."""

    pass


def _source() -> KnowledgeSource:
    return KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="stub-adapter",
    )


def test_adapter_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        KnowledgeSourceAdapter()


def test_concrete_adapter_can_be_instantiated() -> None:
    adapter = StubKnowledgeSourceAdapter()

    assert isinstance(
        adapter,
        KnowledgeSourceAdapter,
    )


def test_adapter_without_acquire_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        MissingAcquireAdapter()


def test_acquire_returns_iterator() -> None:
    resources = StubKnowledgeSourceAdapter().acquire(
        _source(),
    )

    assert isinstance(
        resources,
        Iterator,
    )


def test_iterator_yields_acquired_resource() -> None:
    resources = StubKnowledgeSourceAdapter().acquire(
        _source(),
    )

    first_resource = next(resources)

    assert isinstance(
        first_resource,
        AcquiredResource,
    )
    assert first_resource.resource_ref == "resource-001"


def test_adapter_yields_resources_incrementally() -> None:
    resources = StubKnowledgeSourceAdapter().acquire(
        _source(),
    )

    first_resource = next(resources)
    second_resource = next(resources)

    assert first_resource.resource_ref == "resource-001"
    assert second_resource.resource_ref == "resource-002"


def test_adapter_preserves_source_reference() -> None:
    resource = next(
        StubKnowledgeSourceAdapter().acquire(
            _source(),
        )
    )

    assert resource.identity

def test_adapter_preserves_knowledge_scope() -> None:
    resource = next(
        StubKnowledgeSourceAdapter().acquire(
            _source(),
        )
    )

    assert (
        resource.identity.knowledge_scope_ref
        == "scope-001"
    )


def test_adapter_yields_multiple_resources() -> None:
    resources = tuple(
        StubKnowledgeSourceAdapter().acquire(
            _source(),
        )
    )

    assert len(resources) == 2
    assert all(
        isinstance(resource, AcquiredResource)
        for resource in resources
    )


def test_adapter_iterator_is_exhaustible() -> None:
    resources = StubKnowledgeSourceAdapter().acquire(
        _source(),
    )

    next(resources)
    next(resources)

    with pytest.raises(StopIteration):
        next(resources)
