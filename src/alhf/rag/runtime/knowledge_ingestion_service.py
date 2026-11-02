# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Executes one bounded ALHF Knowledge Foundation ingestion operation.
#
# Responsibilities:
# - Execute bound acquisition through indexing incrementally.
# - Apply governed fan-out, failure policy, and Operational Evidence.
# - Return bounded aggregate ingestion results.
#
# Must Not:
# - Interpret sources, select providers, or generate runtime defaults.
# - Contain source-, format-, or RAG-mode-specific behavior.

from __future__ import annotations

from alhf.rag.chunking.derivation_service import DerivationService
from alhf.rag.ingestion.contracts.acquisition_request import AcquisitionRequest
from alhf.rag.ingestion.contracts.acquisition_result import AcquisitionStatus
from alhf.rag.ingestion.normalization_service import NormalizationService
from alhf.rag.ingestion.parsing_service import ParsingService
from alhf.rag.operational_evidence.contracts.knowledge_event_type import (
    KnowledgeEventType,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_decision import (
    KnowledgeIngestionAction,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_execution_config import (
    KnowledgeIngestionExecutionConfig,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionStage,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_result import (
    KnowledgeIngestionResult,
    KnowledgeIngestionStatus,
)
from alhf.rag.runtime.contracts.knowledge_source_binding import (
    KnowledgeSourceBinding,
)
from alhf.rag.runtime.interfaces.knowledge_index_execution_plan import (
    KnowledgeIndexExecutionPlan,
)
from alhf.rag.runtime.interfaces.knowledge_ingestion_execution_policy import (
    KnowledgeIngestionExecutionPolicy,
)
from alhf.rag.runtime.interfaces.knowledge_ingestion_failure_translator import (
    KnowledgeIngestionFailureTranslator,
)
from alhf.rag.runtime.interfaces.knowledge_representation_execution_plan import (
    KnowledgeRepresentationExecutionPlan,
)


class KnowledgeIngestionService:
    """Execute one provider-neutral bounded Knowledge ingestion operation."""

    def __init__(
        self,
        *,
        parsing: ParsingService,
        normalization: NormalizationService,
        derivation: DerivationService,
        representations: KnowledgeRepresentationExecutionPlan,
        indexes: KnowledgeIndexExecutionPlan,
        failure_translator: KnowledgeIngestionFailureTranslator,
        execution_policy: KnowledgeIngestionExecutionPolicy,
    ) -> None:
        dependencies = (
            (parsing, ParsingService, "parsing"),
            (normalization, NormalizationService, "normalization"),
            (derivation, DerivationService, "derivation"),
            (
                representations,
                KnowledgeRepresentationExecutionPlan,
                "representations",
            ),
            (indexes, KnowledgeIndexExecutionPlan, "indexes"),
            (
                failure_translator,
                KnowledgeIngestionFailureTranslator,
                "failure_translator",
            ),
            (
                execution_policy,
                KnowledgeIngestionExecutionPolicy,
                "execution_policy",
            ),
        )

        for value, expected, name in dependencies:
            if not isinstance(value, expected):
                raise TypeError(
                    f"{name} must be an instance of {expected.__name__}"
                )

        self._parsing = parsing
        self._normalization = normalization
        self._derivation = derivation
        self._representations = representations
        self._indexes = indexes
        self._translator = failure_translator
        self._policy = execution_policy

    def ingest(
        self,
        *,
        binding: KnowledgeSourceBinding,
        config: KnowledgeIngestionExecutionConfig,
        evidence: KnowledgeStageEvidence,
    ) -> KnowledgeIngestionResult:
        """Execute one bounded ingestion operation."""

        self._validate_inputs(
            binding,
            config,
            evidence,
        )

        counts = {
            name: 0
            for name in (
                "acquired",
                "parsed",
                "normalized",
                "derived",
                "represented",
                "indexed",
                "failed",
            )
        }

        evidence.emit(
            event_type=KnowledgeEventType.ACQUISITION_STARTED
        )

        session = binding.acquisition_service.acquire(
            AcquisitionRequest(
                source=binding.source,
                max_resources=config.max_resources,
            )
        )

        resources = session.resources()
        stopped = False

        while not stopped:
            try:
                resource = next(resources)
            except StopIteration:
                break
            except Exception:
                evidence.emit(
                    event_type=KnowledgeEventType.ACQUISITION_FAILED
                )
                raise

            counts["acquired"] += 1
            stage = None

            try:
                evidence.emit(
                    event_type=KnowledgeEventType.PARSING_STARTED
                )
                stage = KnowledgeIngestionStage.PARSING
                parsed = self._parsing.parse(resource)
                counts["parsed"] += 1
                stage = None
                evidence.emit(
                    event_type=KnowledgeEventType.PARSING_COMPLETED
                )

                evidence.emit(
                    event_type=KnowledgeEventType.NORMALIZATION_STARTED
                )
                stage = KnowledgeIngestionStage.NORMALIZATION
                canonical = self._normalization.normalize(parsed)
                counts["normalized"] += 1
                stage = None
                evidence.emit(
                    event_type=KnowledgeEventType.NORMALIZATION_COMPLETED
                )

                evidence.emit(
                    event_type=KnowledgeEventType.DERIVATION_STARTED
                )
                stage = KnowledgeIngestionStage.DERIVATION

                for unit in self._derivation.derive(canonical):
                    counts["derived"] += 1
                    stage = None

                    evidence.emit(
                        event_type=KnowledgeEventType.REPRESENTATION_STARTED
                    )
                    stage = KnowledgeIngestionStage.REPRESENTATION

                    for representation in self._representations.execute(unit):
                        counts["represented"] += 1
                        stage = None

                        evidence.emit(
                            event_type=KnowledgeEventType.REPRESENTATION_COMPLETED
                        )
                        evidence.emit(
                            event_type=KnowledgeEventType.INDEXING_STARTED
                        )

                        stage = KnowledgeIngestionStage.INDEXING
                        counts["indexed"] += self._indexes.execute(
                            representation
                        )

                        stage = None
                        evidence.emit(
                            event_type=KnowledgeEventType.INDEXING_COMPLETED
                        )
                        stage = KnowledgeIngestionStage.REPRESENTATION

                    stage = KnowledgeIngestionStage.DERIVATION

                stage = None
                evidence.emit(
                    event_type=KnowledgeEventType.DERIVATION_COMPLETED
                )

            except Exception as error:
                if stage is None:
                    raise

                evidence.emit(
                    event_type=self._failed_event(stage)
                )

                failure = self._translator.translate(
                    error=error,
                    stage=stage,
                    identity=resource.identity,
                )

                if failure is None:
                    raise

                counts["failed"] += 1
                stopped = (
                    self._policy.decide(failure).action
                    is KnowledgeIngestionAction.STOP
                )

        if stopped:
            status = KnowledgeIngestionStatus.PARTIAL
            evidence.emit(
                event_type=KnowledgeEventType.ACQUISITION_DEGRADED
            )
        else:
            status = self._finish(
                session,
                evidence,
                counts["failed"],
            )

        return KnowledgeIngestionResult(
            execution_id=config.execution_id,
            knowledge_scope_ref=binding.source.knowledge_scope_ref,
            source_ref=binding.source.source_id,
            status=status,
            acquired_count=counts["acquired"],
            parsed_count=counts["parsed"],
            normalized_count=counts["normalized"],
            derived_count=counts["derived"],
            represented_count=counts["represented"],
            indexed_count=counts["indexed"],
            failed_resource_count=counts["failed"],
        )

    @staticmethod
    def _validate_inputs(
        binding,
        config,
        evidence,
    ) -> None:
        for value, expected, name in (
            (binding, KnowledgeSourceBinding, "binding"),
            (config, KnowledgeIngestionExecutionConfig, "config"),
            (evidence, KnowledgeStageEvidence, "evidence"),
        ):
            if not isinstance(value, expected):
                raise TypeError(
                    f"{name} must be an instance of {expected.__name__}"
                )

    @staticmethod
    def _failed_event(
        stage: KnowledgeIngestionStage,
    ) -> KnowledgeEventType:
        return KnowledgeEventType[
            f"{stage.value}_FAILED"
        ]

    @staticmethod
    def _finish(
        session,
        evidence: KnowledgeStageEvidence,
        failed: int,
    ) -> KnowledgeIngestionStatus:
        result = session.result()

        if result.status is AcquisitionStatus.FAILED:
            evidence.emit(
                event_type=KnowledgeEventType.ACQUISITION_FAILED
            )
            return KnowledgeIngestionStatus.FAILED

        if failed or result.status is AcquisitionStatus.PARTIAL:
            evidence.emit(
                event_type=KnowledgeEventType.ACQUISITION_DEGRADED
            )
            return KnowledgeIngestionStatus.PARTIAL

        evidence.emit(
            event_type=KnowledgeEventType.ACQUISITION_COMPLETED
        )
        return KnowledgeIngestionStatus.COMPLETED
