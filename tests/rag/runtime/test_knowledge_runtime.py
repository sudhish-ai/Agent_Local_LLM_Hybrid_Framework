# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the simple consumer-facing ALHF Knowledge runtime boundary.
#
# Responsibilities:
# - Verify source-only ingestion delegates ALHF-owned runtime mechanics.
# - Verify query-only execution builds and delegates a KnowledgeRequest.
# - Verify consumer input validation and internal factory contracts.
#
# Must Not:
# - Re-test ingestion or query pipeline internals.
# - Construct concrete provider registries or physical Knowledge providers.

from __future__ import annotations

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
    KnowledgeIngestionStatus,
)
from alhf.rag.runtime.interfaces.knowledge_source_binder import (
    KnowledgeSourceBinder,
)
from alhf.rag.runtime.knowledge_ingestion_service import (
    KnowledgeIngestionService,
)
from alhf.rag.runtime.knowledge_runtime import KnowledgeRuntime
from alhf.rag.runtime.source_interpretation_service import (
    SourceInterpretationService,
)


class _Interpretation(SourceInterpretationService):
    def __init__(self) -> None:
        self.received = None

    def interpret(
        self,
        source,
    ):
        self.received = source
        return "plan"


class _Binder(KnowledgeSourceBinder):
    def __init__(self) -> None:
        self.received = None

    def bind(
        self,
        *,
        source,
        plan,
    ):
        self.received = (
            source,
            plan,
        )
        return "binding"


class _Evidence(KnowledgeStageEvidence):
    def __init__(self) -> None:
        pass


class _Ingestion(KnowledgeIngestionService):
    def __init__(self) -> None:
        self.received = None

    def ingest(
        self,
        *,
        binding,
        config,
        evidence,
    ):
        self.received = (
            binding,
            config,
            evidence,
        )

        return KnowledgeIngestionResult(
            execution_id=config.execution_id,
            knowledge_scope_ref="scope:test",
            source_ref="source:test",
            status=KnowledgeIngestionStatus.COMPLETED,
        )


class _Query(KnowledgeQueryService):
    def __init__(self) -> None:
        self.received = None

    def execute(
        self,
        *,
        request,
    ):
        self.received = request

        return (
            "context",
            "evaluation",
        )


def _request(
    question: str,
) -> KnowledgeRequest:
    return KnowledgeRequest(
        request_id="request:test",
        knowledge_scope_ref="scope:test",
        query=question,
        index_ref="knowledge-index",
        index_version="v1",
        retrieval_limit=5,
        max_context_bytes=4096,
    )


def _runtime():
    interpretation = _Interpretation()
    binder = _Binder()
    ingestion = _Ingestion()
    query = _Query()
    evidence = _Evidence()

    runtime = KnowledgeRuntime(
        interpretation=interpretation,
        binder=binder,
        ingestion=ingestion,
        query_service=query,
        ingestion_config_factory=(
            lambda: KnowledgeIngestionExecutionConfig(
                execution_id="execution-001",
                max_resources=100,
            )
        ),
        evidence_factory=lambda config: evidence,
        query_request_factory=_request,
    )

    return (
        runtime,
        interpretation,
        binder,
        ingestion,
        query,
        evidence,
    )


def test_ingest_requires_only_customer_source() -> None:
    (
        runtime,
        interpretation,
        binder,
        ingestion,
        _,
        evidence,
    ) = _runtime()

    result = runtime.ingest(
        "customer-knowledge"
    )

    assert (
        interpretation.received.source
        == "customer-knowledge"
    )
    assert binder.received[1] == "plan"
    assert ingestion.received[0] == "binding"
    assert (
        ingestion.received[1].execution_id
        == "execution-001"
    )
    assert ingestion.received[2] is evidence
    assert (
        result.status
        is KnowledgeIngestionStatus.COMPLETED
    )


def test_query_requires_only_customer_question() -> None:
    runtime, _, _, _, query, _ = _runtime()

    result = runtime.query(
        "  authentication policy  "
    )

    assert query.received.query == "authentication policy"
    assert result == (
        "context",
        "evaluation",
    )


def test_query_rejects_empty_question() -> None:
    runtime, *_ = _runtime()

    try:
        runtime.query(
            "   "
        )
    except ValueError as error:
        assert str(error) == "question cannot be empty"
    else:
        raise AssertionError(
            "empty question must be rejected"
        )
