# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the V1 consumer-facing orchestration boundary for querying
# the ALHF Knowledge Foundation.
#
# Problem Solved:
# Knowledge consumers must not orchestrate Retrieval, Evidence,
# Context Packing, and Evaluation individually or depend on their
# concrete implementations.
#
# Responsibilities:
# - Accept one governed KnowledgeRequest.
# - Execute bounded Retrieval.
# - Convert Retrieval results into governed Evidence.
# - Pack Evidence into bounded KnowledgeContext.
# - Evaluate the resulting KnowledgeContext.
# - Return Context and Evaluation to the caller.
#
# Must Not:
# - Perform ingestion, derivation, representation, or indexing.
# - Implement retrieval or ranking algorithms.
# - Implement Evidence or Context algorithms.
# - Generate prompts or invoke models.
# - Select retrieval strategies dynamically.
# - Implement optimization, learning, or promotion.
# - Depend on external RAG or orchestration frameworks.
#
# Architectural Position:
# - Stable V1 entry point into the Knowledge query plane.
# - Shields consumers from internal query-pipeline orchestration.
# - Produces governed Context ready for downstream consumption.
#
# Reuse Value:
# - APIs and applications.
# - V3 runtime consumers.
# - Agents and workflows.
# - Local, cloud, and hybrid deployments.
#
# Future Extensibility:
# - Knowledge Profiles can simplify consumer configuration.
# - Retrieval Intelligence can govern execution strategy.
# - Evidence sufficiency can gate Context construction.
# - Context Intelligence can govern dynamic packing.
# - Model Request Assembly can consume KnowledgeContext downstream.

from __future__ import annotations

from alhf.rag.context_packing.context_packing_service import (
    ContextPackingService,
)
from alhf.rag.context_packing.contracts.knowledge_context import (
    KnowledgeContext,
)
from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
)
from alhf.rag.evaluation.evaluation_service import (
    EvaluationService,
)
from alhf.rag.evidence.evidence_service import (
    EvidenceService,
)
from alhf.rag.knowledge_request.contracts.knowledge_request import (
    KnowledgeRequest,
)
from alhf.rag.retrieval.retrieval_service import (
    RetrievalService,
)


class KnowledgeQueryService:
    """Orchestrate the ALHF V1 Knowledge query plane."""

    def __init__(
        self,
        *,
        retrieval_service: RetrievalService,
        evidence_service: EvidenceService,
        context_packing_service: ContextPackingService,
        evaluation_service: EvaluationService,
    ) -> None:
        checks = (
            (
                retrieval_service,
                RetrievalService,
                "retrieval_service",
            ),
            (
                evidence_service,
                EvidenceService,
                "evidence_service",
            ),
            (
                context_packing_service,
                ContextPackingService,
                "context_packing_service",
            ),
            (
                evaluation_service,
                EvaluationService,
                "evaluation_service",
            ),
        )

        for value, expected_type, field_name in checks:
            if not isinstance(
                value,
                expected_type,
            ):
                raise TypeError(
                    f"{field_name} must be an instance of "
                    f"{expected_type.__name__}"
                )

        self._retrieval = retrieval_service
        self._evidence = evidence_service
        self._packing = context_packing_service
        self._evaluation = evaluation_service

    def execute(
        self,
        *,
        request: KnowledgeRequest,
    ) -> tuple[KnowledgeContext, EvaluationResult]:
        """Execute one governed V1 Knowledge query."""

        if not isinstance(
            request,
            KnowledgeRequest,
        ):
            raise TypeError(
                "request must be an instance of KnowledgeRequest"
            )

        results = self._retrieval.retrieve(
            query=request.query,
            index_ref=request.index_ref,
            index_version=request.index_version,
            limit=request.retrieval_limit,
        )

        evidence = self._evidence.build_many(
            results=results,
        )

        context = self._packing.pack(
            evidence=evidence,
            knowledge_scope_ref=request.knowledge_scope_ref,
            max_bytes=request.max_context_bytes,
        )

        evaluation = self._evaluation.evaluate(
            subject=context,
        )

        return context, evaluation
