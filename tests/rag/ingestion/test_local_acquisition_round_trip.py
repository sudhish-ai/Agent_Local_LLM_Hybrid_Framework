# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the complete local-file acquisition path through the
# ALHF Knowledge Foundation V1 ingestion architecture.
#
# Responsibilities:
# - Register the real LocalFileAdapter.
# - Resolve the adapter through InMemoryAdapterRegistry.
# - Acquire local files through DefaultAcquisitionService.
# - Consume resources through BoundedAcquisitionSession.
# - Validate source, scope, resource, and revision identity.
# - Validate binary content and media-type preservation.
# - Validate terminal AcquisitionResult semantics.
# - Validate bounded acquisition behavior.
#
# Must Not:
# - Test parsing or normalization.
# - Test chunking, embedding, indexing, or retrieval.
# - Test synchronization execution.
# - Test concurrency or NFT optimization.
# - Test cloud source providers.
# - Test Standard RAG response generation.

from pathlib import Path

from alhf.rag.ingestion.acquisition_service import (
    DefaultAcquisitionService,
)
from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
from alhf.rag.ingestion.contracts.acquisition_result import (
    AcquisitionStatus,
)
from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.providers.in_memory_adapter_registry import (
    InMemoryAdapterRegistry,
)
from alhf.rag.ingestion.providers.local_file_adapter import (
    LocalFileAdapter,
)


def _source() -> KnowledgeSource:
    return KnowledgeSource(
        source_id="customer-x-local",
        knowledge_scope_ref="customer-x",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="local-file-adapter",
    )


def _service(
    root_directory: Path,
) -> DefaultAcquisitionService:
    adapter = LocalFileAdapter(
        root_directory=root_directory,
        max_resource_bytes=4096,
        recursive=True,
    )

    registry = InMemoryAdapterRegistry()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=adapter,
        capabilities=AdapterCapabilities(),
    )

    return DefaultAcquisitionService(
        registry=registry,
    )


def test_local_file_acquisition_round_trip(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(
        b"Customer X enterprise policy"
    )

    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    session = _service(
        tmp_path,
    ).acquire(
        request,
    )

    resources = tuple(
        session.resources()
    )
    result = session.result()

    assert len(resources) == 1

    resource = resources[0]

    assert resource.identity.source_ref == "customer-x-local"
    assert (
        resource.identity.knowledge_scope_ref
        == "customer-x"
    )
    assert resource.resource_ref == "policy.txt"
    assert resource.content == b"Customer X enterprise policy"
    assert resource.media_type == "text/plain"
    assert resource.content_fingerprint is not None

    assert result.status == AcquisitionStatus.COMPLETED
    assert result.source_ref == "customer-x-local"
    assert result.acquired_count == 1
    assert result.has_more is False


def test_multiple_files_preserve_deterministic_order(
    tmp_path: Path,
) -> None:
    (tmp_path / "z.txt").write_bytes(b"z")
    (tmp_path / "a.txt").write_bytes(b"a")
    (tmp_path / "m.txt").write_bytes(b"m")

    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    session = _service(
        tmp_path,
    ).acquire(
        request,
    )

    resources = tuple(
        session.resources()
    )

    assert tuple(
        resource.resource_ref
        for resource in resources
    ) == (
        "a.txt",
        "m.txt",
        "z.txt",
    )

    result = session.result()

    assert result.status == AcquisitionStatus.COMPLETED
    assert result.acquired_count == 3


def test_nested_files_are_acquired(
    tmp_path: Path,
) -> None:
    policies = tmp_path / "policies"
    policies.mkdir()

    (policies / "security.txt").write_bytes(
        b"security policy"
    )

    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    session = _service(
        tmp_path,
    ).acquire(
        request,
    )

    resources = tuple(
        session.resources()
    )

    assert len(resources) == 1
    assert (
        resources[0].resource_ref
        == "policies/security.txt"
    )


def test_acquired_revision_is_content_stable(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(
        b"stable policy content"
    )

    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    first_session = _service(
        tmp_path,
    ).acquire(
        request,
    )

    first_resources = tuple(
        first_session.resources()
    )

    second_session = _service(
        tmp_path,
    ).acquire(
        request,
    )

    second_resources = tuple(
        second_session.resources()
    )

    assert (
        first_resources[0].revision_ref
        == second_resources[0].revision_ref
    )
    assert (
        first_resources[0].content_fingerprint
        == second_resources[0].content_fingerprint
    )


def test_changed_content_produces_new_revision(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(
        b"policy version one"
    )

    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    first_session = _service(
        tmp_path,
    ).acquire(
        request,
    )
    first_resource = tuple(
        first_session.resources()
    )[0]

    path.write_bytes(
        b"policy version two"
    )

    second_session = _service(
        tmp_path,
    ).acquire(
        request,
    )
    second_resource = tuple(
        second_session.resources()
    )[0]

    assert (
        first_resource.resource_ref
        == second_resource.resource_ref
    )
    assert (
        first_resource.revision_ref
        != second_resource.revision_ref
    )


def test_bounded_acquisition_reports_partial_result(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.txt").write_bytes(b"a")
    (tmp_path / "b.txt").write_bytes(b"b")
    (tmp_path / "c.txt").write_bytes(b"c")

    request = AcquisitionRequest(
        source=_source(),
        max_resources=2,
    )

    session = _service(
        tmp_path,
    ).acquire(
        request,
    )

    resources = tuple(
        session.resources()
    )
    result = session.result()

    assert len(resources) == 2
    assert result.status == AcquisitionStatus.PARTIAL
    assert result.acquired_count == 2
    assert result.has_more is True
    assert result.continuation_ref is not None
