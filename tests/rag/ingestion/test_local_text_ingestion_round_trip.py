# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 local-text ingestion path from physical file
# acquisition through provider-neutral parsing.
#
# Responsibilities:
# - Acquire real local text files through LocalFileAdapter.
# - Resolve acquisition through the adapter registry.
# - Run bounded acquisition through DefaultAcquisitionService.
# - Resolve text parsing dynamically through the parser registry.
# - Parse acquired files through ParsingService.
# - Validate source, resource, and revision identity preservation.
# - Validate content and media-type preservation.
# - Validate multiple files without format-specific downstream logic.
#
# Must Not:
# - Test semantic normalization.
# - Test chunking, embedding, indexing, or retrieval.
# - Test PDF or other content parsers.
# - Test synchronization execution.
# - Test concurrency or NFT optimization.
# - Test Standard RAG answer generation.

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
from alhf.rag.ingestion.parsers.text_resource_parser import (
    TextResourceParser,
)
from alhf.rag.ingestion.parsing_service import (
    ParsingService,
)
from alhf.rag.ingestion.providers.in_memory_adapter_registry import (
    InMemoryAdapterRegistry,
)
from alhf.rag.ingestion.providers.in_memory_parser_registry import (
    InMemoryParserRegistry,
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


def _acquisition_service(
    root: Path,
) -> DefaultAcquisitionService:
    registry = InMemoryAdapterRegistry()

    registry.register(
        adapter_ref="local-file-adapter",
        adapter=LocalFileAdapter(
            root_directory=root,
            max_resource_bytes=4096,
            recursive=True,
        ),
        capabilities=AdapterCapabilities(),
    )

    return DefaultAcquisitionService(
        registry=registry,
    )


def _parsing_service() -> ParsingService:
    registry = InMemoryParserRegistry()
    registry.register(
        TextResourceParser()
    )

    return ParsingService(
        registry=registry,
    )


def test_local_text_file_reaches_parsed_resource(
    tmp_path: Path,
) -> None:
    content = b"Customer X enterprise knowledge"

    (tmp_path / "policy.txt").write_bytes(
        content
    )

    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    acquisition = _acquisition_service(
        tmp_path
    ).acquire(
        request
    )

    acquired = tuple(
        acquisition.resources()
    )

    assert len(acquired) == 1

    parsed = _parsing_service().parse(
        acquired[0]
    )

    assert parsed.content == content
    assert parsed.content_media_type == "text/plain"
    assert parsed.source_media_type == "text/plain"


def test_identity_survives_acquisition_and_parsing(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"enterprise policy"
    )

    request = AcquisitionRequest(
        source=_source(),
        max_resources=10,
    )

    acquisition = _acquisition_service(
        tmp_path
    ).acquire(
        request
    )

    acquired = next(
        acquisition.resources()
    )

    parsed = _parsing_service().parse(
        acquired
    )

    assert parsed.identity is acquired.identity
    assert parsed.identity.source_ref == "customer-x-local"
    assert (
        parsed.identity.knowledge_scope_ref
        == "customer-x"
    )
    assert parsed.resource_ref == "policy.txt"
    assert parsed.revision_ref == acquired.revision_ref


def test_parser_reproducibility_survives_real_flow(
    tmp_path: Path,
) -> None:
    (tmp_path / "knowledge.txt").write_bytes(
        b"stable knowledge"
    )

    acquisition = _acquisition_service(
        tmp_path
    ).acquire(
        AcquisitionRequest(
            source=_source(),
            max_resources=10,
        )
    )

    acquired = next(
        acquisition.resources()
    )

    parsed = _parsing_service().parse(
        acquired
    )

    assert parsed.parser_ref == "text-resource-parser"
    assert parsed.parser_version == "1.0"


def test_multiple_text_files_use_same_common_pipeline(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.txt").write_bytes(
        b"knowledge a"
    )
    (tmp_path / "b.txt").write_bytes(
        b"knowledge b"
    )

    acquisition = _acquisition_service(
        tmp_path
    ).acquire(
        AcquisitionRequest(
            source=_source(),
            max_resources=10,
        )
    )

    acquired = tuple(
        acquisition.resources()
    )

    parsing = _parsing_service()

    parsed = tuple(
        parsing.parse(resource)
        for resource in acquired
    )

    assert tuple(
        resource.resource_ref
        for resource in parsed
    ) == (
        "a.txt",
        "b.txt",
    )

    assert tuple(
        resource.content
        for resource in parsed
    ) == (
        b"knowledge a",
        b"knowledge b",
    )


def test_acquisition_result_remains_independent_from_parsing(
    tmp_path: Path,
) -> None:
    (tmp_path / "knowledge.txt").write_bytes(
        b"enterprise knowledge"
    )

    acquisition = _acquisition_service(
        tmp_path
    ).acquire(
        AcquisitionRequest(
            source=_source(),
            max_resources=10,
        )
    )

    acquired = tuple(
        acquisition.resources()
    )

    parsed = _parsing_service().parse(
        acquired[0]
    )

    result = acquisition.result()

    assert parsed.resource_ref == "knowledge.txt"
    assert result.status == AcquisitionStatus.COMPLETED
    assert result.acquired_count == 1
    assert result.has_more is False


def test_content_change_preserves_resource_but_changes_revision(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.txt"

    path.write_bytes(
        b"policy version one"
    )

    first_session = _acquisition_service(
        tmp_path
    ).acquire(
        AcquisitionRequest(
            source=_source(),
            max_resources=10,
        )
    )

    first_acquired = next(
        first_session.resources()
    )
    first_parsed = _parsing_service().parse(
        first_acquired
    )

    path.write_bytes(
        b"policy version two"
    )

    second_session = _acquisition_service(
        tmp_path
    ).acquire(
        AcquisitionRequest(
            source=_source(),
            max_resources=10,
        )
    )

    second_acquired = next(
        second_session.resources()
    )
    second_parsed = _parsing_service().parse(
        second_acquired
    )

    assert (
        first_parsed.resource_ref
        == second_parsed.resource_ref
    )
    assert (
        first_parsed.revision_ref
        != second_parsed.revision_ref
    )
