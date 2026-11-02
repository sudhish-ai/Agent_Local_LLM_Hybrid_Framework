# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the simple production-facing entry point to the ALHF Knowledge
# Foundation runtime.
#
# Responsibilities:
# - Accept source-only ingestion requests from runtime consumers.
# - Hide source interpretation, binding, execution identity, and bounds.
# - Accept query-only Knowledge requests from runtime consumers.
# - Preserve one shared configured ingestion/query environment.
#
# Must Not:
# - Implement ingestion, retrieval, Evidence, Context, or evaluation logic.
# - Construct provider registries or concrete Knowledge providers.
# - Contain source-, format-, or RAG-mode-specific branching.

from __future__ import annotations

from collections.abc import Callable

from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
)
from alhf.rag.knowledge_request.contracts.knowledge_request import (
    KnowledgeRequest,
)
from alhf.rag.knowledge_request.knowledge_query_service import (
    KnowledgeQueryService,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_execution_config import (
    KnowledgeIngestionExecutionConfig,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_result import (
    KnowledgeIngestionResult,
)
from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)
from alhf.rag.runtime.interfaces.knowledge_source_binder import (
    KnowledgeSourceBinder,
)
from alhf.rag.runtime.knowledge_ingestion_service import (
    KnowledgeIngestionService,
)
from alhf.rag.runtime.source_interpretation_service import (
    SourceInterpretationService,
)


class KnowledgeRuntime:
    """Simple consumer entry point to configured Knowledge execution."""

    def __init__(
        self,
        *,
        interpretation: SourceInterpretationService,
        binder: KnowledgeSourceBinder,
        ingestion: KnowledgeIngestionService,
        query_service: KnowledgeQueryService,
        ingestion_config_factory: Callable[
            [],
            KnowledgeIngestionExecutionConfig,
        ],
        evidence_factory: Callable[
            [KnowledgeIngestionExecutionConfig],
            KnowledgeStageEvidence,
        ],
        query_request_factory: Callable[
            [str],
            KnowledgeRequest,
        ],
    ) -> None:
        checks = (
            (
                interpretation,
                SourceInterpretationService,
                "interpretation",
            ),
            (
                binder,
                KnowledgeSourceBinder,
                "binder",
            ),
            (
                ingestion,
                KnowledgeIngestionService,
                "ingestion",
            ),
            (
                query_service,
                KnowledgeQueryService,
                "query_service",
            ),
        )

        for value, expected, name in checks:
            if not isinstance(
                value,
                expected,
            ):
                raise TypeError(
                    f"{name} must be an instance of "
                    f"{expected.__name__}"
                )

        for value, name in (
            (
                ingestion_config_factory,
                "ingestion_config_factory",
            ),
            (
                evidence_factory,
                "evidence_factory",
            ),
            (
                query_request_factory,
                "query_request_factory",
            ),
        ):
            if not callable(value):
                raise TypeError(
                    f"{name} must be callable"
                )

        self._interpretation = interpretation
        self._binder = binder
        self._ingestion = ingestion
        self._query = query_service
        self._ingestion_config_factory = (
            ingestion_config_factory
        )
        self._evidence_factory = evidence_factory
        self._query_request_factory = (
            query_request_factory
        )

    def ingest(
        self,
        source: str,
    ) -> KnowledgeIngestionResult:
        """Ingest a source using ALHF-owned execution."""

        source_input = KnowledgeSourceInput(
            source=source,
        )

        plan = self._interpretation.interpret(
            source_input,
        )

        binding = self._binder.bind(
            source=source_input,
            plan=plan,
        )

        config = self._ingestion_config_factory()

        if not isinstance(
            config,
            KnowledgeIngestionExecutionConfig,
        ):
            raise TypeError(
                "ingestion_config_factory must return "
                "KnowledgeIngestionExecutionConfig"
            )

        evidence = self._evidence_factory(
            config,
        )

        if not isinstance(
            evidence,
            KnowledgeStageEvidence,
        ):
            raise TypeError(
                "evidence_factory must return "
                "KnowledgeStageEvidence"
            )

        return self._ingestion.ingest(
            binding=binding,
            config=config,
            evidence=evidence,
        )

    def query(
        self,
        question: str,
    ) -> tuple[KnowledgeContext, EvaluationResult]:
        """Query configured Knowledge using a question."""

        if not isinstance(
            question,
            str,
        ):
            raise TypeError(
                "question must be a string"
            )

        normalized = question.strip()

        if not normalized:
            raise ValueError(
                "question cannot be empty"
            )

        request = self._query_request_factory(
            normalized,
        )

        if not isinstance(
            request,
            KnowledgeRequest,
        ):
            raise TypeError(
                "query_request_factory must return "
                "KnowledgeRequest"
            )

        return self._query.execute(
            request=request,
        )
