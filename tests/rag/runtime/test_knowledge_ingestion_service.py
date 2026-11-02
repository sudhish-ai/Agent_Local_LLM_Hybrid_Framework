# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies bounded production orchestration of ALHF Knowledge ingestion.

from pathlib import Path

from alhf.rag.chunking.derivation_service import DerivationService
from alhf.rag.chunking.providers.in_memory_derivation_registry import (
    InMemoryDerivationRegistry,
)
from alhf.rag.chunking.strategies.fixed_size_text_derivation import (
    FixedSizeTextDerivation,
)
from alhf.rag.indexing.indexing_service import IndexingService
from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.indexing.providers.in_memory_index_registry import (
    InMemoryIndexRegistry,
)
from alhf.rag.ingestion.contracts.knowledge_source import KnowledgeSourceKind
from alhf.rag.ingestion.normalization_service import NormalizationService
from alhf.rag.ingestion.normalizers.text_content_normalizer import (
    TextContentNormalizer,
)
from alhf.rag.ingestion.parsers.text_resource_parser import TextResourceParser
from alhf.rag.ingestion.parsing_service import ParsingService
from alhf.rag.ingestion.providers.in_memory_normalizer_registry import (
    InMemoryNormalizerRegistry,
)
from alhf.rag.ingestion.providers.in_memory_parser_registry import (
    InMemoryParserRegistry,
)
from alhf.rag.operational_evidence.contracts.knowledge_event_type import (
    KnowledgeEventType,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)
from alhf.rag.representation.providers.deterministic_text_representation_provider import (
    DeterministicTextRepresentationProvider,
)
from alhf.rag.representation.providers.in_memory_representation_registry import (
    InMemoryRepresentationRegistry,
)
from alhf.rag.representation.representation_service import RepresentationService
from alhf.rag.runtime.contracts.knowledge_ingestion_execution_config import (
    KnowledgeIngestionExecutionConfig,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_result import (
    KnowledgeIngestionStatus,
)
from alhf.rag.runtime.contracts.knowledge_source_input import KnowledgeSourceInput
from alhf.rag.runtime.contracts.knowledge_source_plan import KnowledgeSourcePlan
from alhf.rag.runtime.execution.deterministic_index_execution_plan import (
    DeterministicIndexExecutionPlan,
)
from alhf.rag.runtime.execution.deterministic_representation_execution_plan import (
    DeterministicRepresentationExecutionPlan,
)
from alhf.rag.runtime.failure_translation.deterministic_ingestion_failure_translator import (
    DeterministicIngestionFailureTranslator,
)
from alhf.rag.runtime.knowledge_ingestion_service import KnowledgeIngestionService
from alhf.rag.runtime.policies.deterministic_ingestion_execution_policy import (
    DeterministicIngestionExecutionPolicy,
)
from alhf.rag.runtime.source_binders.local_source_binder import LocalSourceBinder


class _Evidence(KnowledgeStageEvidence):
    def __init__(self) -> None:
        self.events: list[KnowledgeEventType] = []

    def emit(
        self,
        *,
        event_type: KnowledgeEventType,
        **kwargs,
    ):
        self.events.append(event_type)
        return None


def _binding(
    path: Path,
):
    return LocalSourceBinder(
        max_resource_bytes=4096,
    ).bind(
        source=KnowledgeSourceInput(
            source=str(path),
        ),
        plan=KnowledgeSourcePlan(
            source_id="source:test",
            knowledge_scope_ref="scope:test",
            source_kind=KnowledgeSourceKind.FILE,
            adapter_ref="local-file",
        ),
    )


def _runtime() -> tuple[
    KnowledgeIngestionService,
    InMemoryIndexProvider,
]:
    parsers = InMemoryParserRegistry()
    parsers.register(
        TextResourceParser()
    )

    normalizers = InMemoryNormalizerRegistry()
    normalizers.register(
        TextContentNormalizer()
    )

    derivations = InMemoryDerivationRegistry()
    derivations.register(
        FixedSizeTextDerivation(
            chunk_size_bytes=4096,
        )
    )

    representations = InMemoryRepresentationRegistry()
    representations.register(
        DeterministicTextRepresentationProvider()
    )

    indexes = InMemoryIndexRegistry()
    provider = InMemoryIndexProvider()
    indexes.register(
        index_ref="knowledge-index",
        provider=provider,
    )

    service = KnowledgeIngestionService(
        parsing=ParsingService(
            registry=parsers,
        ),
        normalization=NormalizationService(
            registry=normalizers,
        ),
        derivation=DerivationService(
            registry=derivations,
        ),
        representations=DeterministicRepresentationExecutionPlan(
            service=RepresentationService(
                registry=representations,
            ),
        ),
        indexes=DeterministicIndexExecutionPlan(
            service=IndexingService(
                registry=indexes,
            ),
            index_ref="knowledge-index",
        ),
        failure_translator=(
            DeterministicIngestionFailureTranslator()
        ),
        execution_policy=(
            DeterministicIngestionExecutionPolicy()
        ),
    )

    return service, provider


def test_real_text_resource_executes_ingestion_spine(
    tmp_path: Path,
) -> None:
    path = tmp_path / "knowledge.txt"
    path.write_bytes(
        b"Enterprise authentication requires MFA."
    )

    service, provider = _runtime()
    evidence = _Evidence()

    result = service.ingest(
        binding=_binding(path),
        config=KnowledgeIngestionExecutionConfig(
            execution_id="execution-001",
            max_resources=10,
        ),
        evidence=evidence,
    )

    assert result.status is KnowledgeIngestionStatus.COMPLETED
    assert result.acquired_count == 1
    assert result.parsed_count == 1
    assert result.normalized_count == 1
    assert result.derived_count == 1
    assert result.represented_count == 1
    assert result.indexed_count == 1
    assert result.failed_resource_count == 0
    assert len(provider) == 1


def test_success_emits_ingestion_stage_evidence(
    tmp_path: Path,
) -> None:
    path = tmp_path / "knowledge.txt"
    path.write_bytes(
        b"Enterprise knowledge"
    )

    service, _ = _runtime()
    evidence = _Evidence()

    service.ingest(
        binding=_binding(path),
        config=KnowledgeIngestionExecutionConfig(
            execution_id="execution-002",
            max_resources=10,
        ),
        evidence=evidence,
    )

    expected = {
        KnowledgeEventType.ACQUISITION_STARTED,
        KnowledgeEventType.PARSING_STARTED,
        KnowledgeEventType.PARSING_COMPLETED,
        KnowledgeEventType.NORMALIZATION_STARTED,
        KnowledgeEventType.NORMALIZATION_COMPLETED,
        KnowledgeEventType.DERIVATION_STARTED,
        KnowledgeEventType.DERIVATION_COMPLETED,
        KnowledgeEventType.REPRESENTATION_STARTED,
        KnowledgeEventType.REPRESENTATION_COMPLETED,
        KnowledgeEventType.INDEXING_STARTED,
        KnowledgeEventType.INDEXING_COMPLETED,
        KnowledgeEventType.ACQUISITION_COMPLETED,
    }

    assert set(evidence.events) == expected
