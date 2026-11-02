# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 local-text ingestion path from physical source
# acquisition through parsing and canonical Knowledge normalization.
#
# Responsibilities:
# - Acquire real local text resources.
# - Resolve acquisition dynamically through AdapterRegistry.
# - Parse resources dynamically through ParserRegistry.
# - Normalize parsed content dynamically through NormalizerRegistry.
# - Produce stable CanonicalContent.
# - Preserve source, scope, resource, and revision identity.
# - Preserve reproducibility and parsed-artifact provenance.
# - Validate deterministic canonicalization with real local content.
#
# Must Not:
# - Test derivation or chunking.
# - Test embedding, indexing, retrieval, or reranking.
# - Test PDF or other physical content formats.
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
from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)
from alhf.rag.ingestion.contracts.canonical_content import (
    CanonicalContent,
    CanonicalContentKind,
)
from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)
from alhf.rag.ingestion.normalization_service import (
    NormalizationService,
)
from alhf.rag.ingestion.normalizers.text_content_normalizer import (
    TextContentNormalizer,
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
from alhf.rag.ingestion.providers.in_memory_normalizer_registry import (
    InMemoryNormalizerRegistry,
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


def _normalization_service() -> NormalizationService:
    registry = InMemoryNormalizerRegistry()
    registry.register(
        TextContentNormalizer()
    )

    return NormalizationService(
        registry=registry,
    )


def _canonicalize(
    root: Path,
) -> CanonicalContent:
    session = _acquisition_service(
        root
    ).acquire(
        AcquisitionRequest(
            source=_source(),
            max_resources=10,
        )
    )

    acquired = next(
        session.resources()
    )

    parsed = _parsing_service().parse(
        acquired
    )

    return _normalization_service().normalize(
        parsed
    )


def test_local_text_reaches_canonical_boundary(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"Customer X enterprise policy"
    )

    canonical = _canonicalize(
        tmp_path
    )

    assert isinstance(
        canonical,
        CanonicalContent,
    )
    assert canonical.content == (
        b"Customer X enterprise policy"
    )
    assert canonical.content_kind == CanonicalContentKind.TEXT
    assert canonical.media_type == "text/plain"


def test_identity_survives_complete_ingestion_path(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"enterprise policy"
    )

    canonical = _canonicalize(
        tmp_path
    )

    assert canonical.knowledge_scope_ref == "customer-x"
    assert canonical.resource_ref == "policy.txt"
    assert canonical.revision_ref.startswith(
        "sha256:"
    )


def test_parser_provenance_survives_canonicalization(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"enterprise policy"
    )

    canonical = _canonicalize(
        tmp_path
    )

    assert "text-resource-parser" in (
        canonical.parsed_artifact_ref
    )
    assert canonical.normalizer_ref == (
        "text-content-normalizer"
    )
    assert canonical.normalizer_version == "1.0"


def test_line_endings_are_canonicalized(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"line one\r\nline two\rline three"
    )

    canonical = _canonicalize(
        tmp_path
    )

    assert canonical.content == (
        b"line one\nline two\nline three"
    )


def test_same_content_produces_stable_revision(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.txt"
    path.write_bytes(
        b"stable enterprise policy"
    )

    first = _canonicalize(
        tmp_path
    )
    second = _canonicalize(
        tmp_path
    )

    assert first.resource_ref == second.resource_ref
    assert first.revision_ref == second.revision_ref
    assert first.content == second.content


def test_changed_content_produces_new_revision(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.txt"

    path.write_bytes(
        b"policy version one"
    )

    first = _canonicalize(
        tmp_path
    )

    path.write_bytes(
        b"policy version two"
    )

    second = _canonicalize(
        tmp_path
    )

    assert first.resource_ref == second.resource_ref
    assert first.revision_ref != second.revision_ref


def test_multiple_files_share_same_common_pipeline(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.txt").write_bytes(
        b"knowledge a"
    )
    (tmp_path / "b.txt").write_bytes(
        b"knowledge b"
    )

    session = _acquisition_service(
        tmp_path
    ).acquire(
        AcquisitionRequest(
            source=_source(),
            max_resources=10,
        )
    )

    parsing = _parsing_service()
    normalization = _normalization_service()

    canonical = tuple(
        normalization.normalize(
            parsing.parse(resource)
        )
        for resource in session.resources()
    )

    assert tuple(
        content.resource_ref
        for content in canonical
    ) == (
        "a.txt",
        "b.txt",
    )

    assert tuple(
        content.content
        for content in canonical
    ) == (
        b"knowledge a",
        b"knowledge b",
    )
