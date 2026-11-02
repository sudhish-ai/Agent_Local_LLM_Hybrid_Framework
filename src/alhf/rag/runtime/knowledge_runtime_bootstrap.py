# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Composes the deterministic ALHF Knowledge Foundation V1 runtime.
#
# Responsibilities:
# - Assemble one shared ingestion/query environment.
# - Own deterministic V1 technical defaults hidden from consumers.
# - Return the simple production-facing KnowledgeRuntime.
#
# Must Not:
# - Implement Knowledge pipeline algorithms.
# - Contain customer/domain-specific knowledge.
# - Change stable stage or provider contracts.

from __future__ import annotations

import uuid
from pathlib import Path

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.providers.jsonl_evidence_store import (
    JsonlEvidenceStore,
)
from alhf.rag.chunking.derivation_service import DerivationService
from alhf.rag.chunking.providers.in_memory_derivation_registry import (
    InMemoryDerivationRegistry,
)
from alhf.rag.chunking.strategies.fixed_size_text_derivation import (
    FixedSizeTextDerivation,
)
from alhf.rag.context_packing.context_packing_service import (
    ContextPackingService,
)
from alhf.rag.context_packing.providers.deterministic_context_packer import (
    DeterministicContextPacker,
)
from alhf.rag.evaluation.evaluation_service import EvaluationService
from alhf.rag.evaluation.providers.deterministic_context_evaluator import (
    DeterministicContextEvaluator,
)
from alhf.rag.evidence.evidence_service import EvidenceService
from alhf.rag.evidence.providers.candidate_evidence_builder import (
    CandidateEvidenceBuilder,
)
from alhf.rag.indexing.indexing_service import IndexingService
from alhf.rag.indexing.providers.in_memory_index_provider import (
    InMemoryIndexProvider,
)
from alhf.rag.indexing.providers.in_memory_index_registry import (
    InMemoryIndexRegistry,
)
from alhf.rag.ingestion.normalization_service import NormalizationService
from alhf.rag.ingestion.normalizers.text_content_normalizer import (
    TextContentNormalizer,
)
from alhf.rag.ingestion.parsers.pdf_resource_parser import PdfResourceParser
from alhf.rag.ingestion.parsers.text_resource_parser import TextResourceParser
from alhf.rag.ingestion.parsing_service import ParsingService
from alhf.rag.ingestion.providers.in_memory_normalizer_registry import (
    InMemoryNormalizerRegistry,
)
from alhf.rag.ingestion.providers.in_memory_parser_registry import (
    InMemoryParserRegistry,
)
from alhf.rag.knowledge_request.contracts.knowledge_request import (
    KnowledgeRequest,
)
from alhf.rag.knowledge_request.knowledge_query_service import (
    KnowledgeQueryService,
)
from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)
from alhf.rag.operational_evidence.knowledge_evidence_factory import (
    KnowledgeEvidenceFactory,
)
from alhf.rag.operational_evidence.knowledge_evidence_publisher import (
    KnowledgeEvidencePublisher,
)
from alhf.rag.operational_evidence.knowledge_evidence_service import (
    KnowledgeEvidenceService,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence_factory import (
    KnowledgeStageEvidenceFactory,
)
from alhf.rag.representation.providers.deterministic_text_representation_provider import (
    DeterministicTextRepresentationProvider,
)
from alhf.rag.representation.providers.in_memory_representation_registry import (
    InMemoryRepresentationRegistry,
)
from alhf.rag.representation.representation_service import (
    RepresentationService,
)
from alhf.rag.retrieval.providers.in_memory_lexical_retriever import (
    InMemoryLexicalRetriever,
)
from alhf.rag.retrieval.retrieval_service import RetrievalService
from alhf.rag.runtime.contracts.knowledge_ingestion_execution_config import (
    KnowledgeIngestionExecutionConfig,
)
from alhf.rag.runtime.execution.deterministic_index_execution_plan import (
    DeterministicIndexExecutionPlan,
)
from alhf.rag.runtime.execution.deterministic_representation_execution_plan import (
    DeterministicRepresentationExecutionPlan,
)
from alhf.rag.runtime.failure_translation.deterministic_ingestion_failure_translator import (
    DeterministicIngestionFailureTranslator,
)
from alhf.rag.runtime.knowledge_ingestion_service import (
    KnowledgeIngestionService,
)
from alhf.rag.runtime.knowledge_runtime import KnowledgeRuntime
from alhf.rag.runtime.policies.deterministic_ingestion_execution_policy import (
    DeterministicIngestionExecutionPolicy,
)
from alhf.rag.runtime.providers.in_memory_source_interpreter_registry import (
    InMemorySourceInterpreterRegistry,
)
from alhf.rag.runtime.source_binders.local_source_binder import (
    LocalSourceBinder,
)
from alhf.rag.runtime.source_interpretation_service import (
    SourceInterpretationService,
)
from alhf.rag.runtime.source_interpreters.local_source_interpreter import (
    LocalSourceInterpreter,
)


class KnowledgeRuntimeBootstrap:
    """Build the configured deterministic Knowledge Foundation V1 runtime."""

    _SCOPE = "default"
    _INDEX = "knowledge-index"
    _INDEX_VERSION = "v1"

    def build(
        self,
    ) -> KnowledgeRuntime:
        """Assemble one shared V1 ingestion and query environment."""

        source_registry = InMemorySourceInterpreterRegistry()
        source_registry.register(
            LocalSourceInterpreter(
                knowledge_scope_ref=self._SCOPE,
            )
        )

        parsers = InMemoryParserRegistry()
        parsers.register(
            PdfResourceParser()
        )
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
                chunk_size_bytes=16_384,
            )
        )

        representations = InMemoryRepresentationRegistry()
        representations.register(
            DeterministicTextRepresentationProvider()
        )

        index_provider = InMemoryIndexProvider()
        indexes = InMemoryIndexRegistry()
        indexes.register(
            index_ref=self._INDEX,
            provider=index_provider,
        )

        ingestion = KnowledgeIngestionService(
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
                index_ref=self._INDEX,
            ),
            failure_translator=(
                DeterministicIngestionFailureTranslator()
            ),
            execution_policy=(
                DeterministicIngestionExecutionPolicy()
            ),
        )

        query = KnowledgeQueryService(
            retrieval_service=RetrievalService(
                retriever=InMemoryLexicalRetriever(
                    provider=index_provider,
                ),
            ),
            evidence_service=EvidenceService(
                builder=CandidateEvidenceBuilder(),
                resolve_representation=index_provider.get,
            ),
            context_packing_service=ContextPackingService(
                packer=DeterministicContextPacker(),
            ),
            evaluation_service=EvaluationService(
                evaluator=DeterministicContextEvaluator(),
            ),
        )

        stage_factory = self._stage_factory()

        return KnowledgeRuntime(
            interpretation=SourceInterpretationService(
                registry=source_registry,
            ),
            binder=LocalSourceBinder(
                max_resource_bytes=32 * 1024 * 1024,
            ),
            ingestion=ingestion,
            query_service=query,
            ingestion_config_factory=self._ingestion_config,
            evidence_factory=lambda config: stage_factory.create(
                execution=ExecutionIdentity(
                    correlation_id=config.execution_id,
                    execution_id=config.execution_id,
                    operation_id=(
                        f"knowledge-ingest:{uuid.uuid4()}"
                    ),
                ),
                knowledge=KnowledgeEvidenceContext(
                    knowledge_scope_ref=self._SCOPE,
                ),
            ),
            query_request_factory=self._query_request,
        )

    @staticmethod
    def _ingestion_config(
    ) -> KnowledgeIngestionExecutionConfig:
        return KnowledgeIngestionExecutionConfig(
            execution_id=f"knowledge:{uuid.uuid4()}",
            max_resources=10_000,
        )

    def _query_request(
        self,
        question: str,
    ) -> KnowledgeRequest:
        return KnowledgeRequest(
            request_id=f"knowledge-query:{uuid.uuid4()}",
            knowledge_scope_ref=self._SCOPE,
            query=question,
            index_ref=self._INDEX,
            index_version=self._INDEX_VERSION,
            retrieval_limit=10,
            max_context_bytes=64 * 1024,
        )

    @staticmethod
    def _stage_factory(
    ) -> KnowledgeStageEvidenceFactory:
        store = JsonlEvidenceStore(
            Path("logs") / "knowledge_evidence",
            max_file_size_bytes=16 * 1024 * 1024,
        )

        service = KnowledgeEvidenceService(
            factory=KnowledgeEvidenceFactory(
                producer="alhf-knowledge-runtime",
            ),
            publisher=KnowledgeEvidencePublisher(
                sink=store,
            ),
        )

        return KnowledgeStageEvidenceFactory(
            service=service,
        )
