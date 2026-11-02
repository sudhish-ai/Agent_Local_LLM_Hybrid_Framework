# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the ALHF V1 local-text Knowledge path from physical source
# acquisition through canonicalization and deterministic derivation.
#
# Responsibilities:
# - Acquire real local text resources.
# - Parse acquired resources through the parser boundary.
# - Normalize parsed resources into CanonicalContent.
# - Resolve the configured derivation strategy dynamically.
# - Derive bounded KnowledgeUnit instances.
# - Validate identity and provenance continuity.
# - Validate deterministic derivation behavior.
#
# Must Not:
# - Test embeddings or representations.
# - Test indexing, retrieval, reranking, or evidence construction.
# - Treat fixed-size derivation as North-Star behavior.
# - Test adaptive Derivation Intelligence.
# - Test concurrency or NFT optimization.
# - Depend on external RAG or orchestration frameworks.

from pathlib import Path

from alhf.rag.chunking.providers.in_memory_derivation_registry import (
    InMemoryDerivationRegistry,
)
from alhf.rag.chunking.strategies.fixed_size_text_derivation import (
    FixedSizeTextDerivation,
)
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


def _derivation_registry() -> InMemoryDerivationRegistry:
    registry = InMemoryDerivationRegistry()

    registry.register(
        FixedSizeTextDerivation(
            chunk_size_bytes=12,
            overlap_bytes=0,
        )
    )

    return registry


def _derive(
    root: Path,
):
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

    canonical = _normalization_service().normalize(
        parsed
    )

    strategy = _derivation_registry().resolve(
        canonical
    )

    return canonical, tuple(
        strategy.derive(
            canonical
        )
    )


def test_local_text_reaches_knowledge_units(
    tmp_path: Path,
) -> None:
    content = b"abcdefghijklmnopqrstuvwx"

    (tmp_path / "policy.txt").write_bytes(
        content
    )

    canonical, units = _derive(
        tmp_path
    )

    assert canonical.content == content
    assert len(units) == 2
    assert units[0].content == b"abcdefghijkl"
    assert units[1].content == b"mnopqrstuvwx"


def test_identity_survives_complete_derivation_path(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"enterprise policy"
    )

    canonical, units = _derive(
        tmp_path
    )

    assert units

    for unit in units:
        assert unit.identity is canonical.identity
        assert unit.knowledge_scope_ref == "customer-x"
        assert unit.resource_ref == "policy.txt"
        assert unit.revision_ref == canonical.revision_ref


def test_units_preserve_canonical_provenance(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"enterprise policy knowledge"
    )

    _, units = _derive(
        tmp_path
    )

    canonical_refs = {
        unit.canonical_artifact_ref
        for unit in units
    }
    derivation_ids = {
        unit.derivation_id
        for unit in units
    }

    assert len(canonical_refs) == 1
    assert len(derivation_ids) == 1


def test_units_preserve_strategy_reproducibility(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"enterprise policy knowledge"
    )

    _, units = _derive(
        tmp_path
    )

    assert all(
        unit.strategy_ref == "fixed-size-text-derivation"
        for unit in units
    )
    assert all(
        unit.strategy_version == "1.0"
        for unit in units
    )


def test_units_have_deterministic_sequence(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"abcdefghijklmnopqrstuvwx"
    )

    _, units = _derive(
        tmp_path
    )

    assert tuple(
        unit.sequence
        for unit in units
    ) == (
        0,
        1,
    )


def test_repeated_derivation_is_deterministic(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"stable enterprise knowledge"
    )

    _, first = _derive(
        tmp_path
    )
    _, second = _derive(
        tmp_path
    )

    assert tuple(
        unit.derivation_id
        for unit in first
    ) == tuple(
        unit.derivation_id
        for unit in second
    )

    assert tuple(
        unit.unit_id
        for unit in first
    ) == tuple(
        unit.unit_id
        for unit in second
    )


def test_content_change_changes_derived_identity(
    tmp_path: Path,
) -> None:
    path = tmp_path / "policy.txt"

    path.write_bytes(
        b"policy version one"
    )

    _, first = _derive(
        tmp_path
    )

    path.write_bytes(
        b"policy version two"
    )

    _, second = _derive(
        tmp_path
    )

    assert first[0].resource_ref == second[0].resource_ref
    assert first[0].revision_ref != second[0].revision_ref
    assert first[0].derivation_id != second[0].derivation_id


def test_multiple_units_remain_bounded(
    tmp_path: Path,
) -> None:
    (tmp_path / "policy.txt").write_bytes(
        b"abcdefghijklmnopqrstuvwxyz"
    )

    _, units = _derive(
        tmp_path
    )

    assert all(
        unit.size_bytes <= 12
        for unit in units
    )
