# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeEvidenceRuntime.
#
# Responsibilities:
# - Validate Knowledge Operational Evidence runtime composition.
# - Validate creation of stage-facing evidence emitters.
# - Validate execution identity preservation.
# - Validate governed Knowledge context preservation.
# - Validate runtime reuse across independent Knowledge operations.
# - Validate invalid runtime dependencies.
# - Validate invalid execution and Knowledge contracts.
#
# Must Not:
# - Test JSON or JSONL persistence.
# - Test Knowledge pipeline-stage execution.
# - Test identity generation.
# - Test failure analysis or root-cause analysis.
# - Test Knowledge content.

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceResult,
    PersistenceStatus,
)
from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.interfaces.evidence_sink import (
    EvidenceSink,
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
from alhf.rag.operational_evidence.knowledge_evidence_runtime import (
    KnowledgeEvidenceRuntime,
)
from alhf.rag.operational_evidence.knowledge_evidence_service import (
    KnowledgeEvidenceService,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)


class StubEvidenceSink(EvidenceSink):
    """Minimal sink used to build the Knowledge evidence runtime."""

    def persist(
        self,
        record: OperationalEvidenceRecord,
    ) -> PersistenceResult:
        return PersistenceResult(
            record_id=record.record_id,
            status=PersistenceStatus.PERSISTED,
        )


def _service() -> KnowledgeEvidenceService:
    evidence_factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "record-001",
    )
    publisher = KnowledgeEvidencePublisher(
        sink=StubEvidenceSink(),
    )

    return KnowledgeEvidenceService(
        factory=evidence_factory,
        publisher=publisher,
    )


def _execution(
    operation_id: str = "operation-001",
) -> ExecutionIdentity:
    return ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id=operation_id,
    )


def _knowledge(
    revision_ref: str = "revision-001",
) -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref=revision_ref,
    )


def test_create_knowledge_evidence_runtime() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    assert isinstance(
        runtime,
        KnowledgeEvidenceRuntime,
    )


def test_for_operation_returns_stage_evidence() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert isinstance(
        stage_evidence,
        KnowledgeStageEvidence,
    )


def test_for_operation_preserves_execution_identity() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )
    execution = _execution()

    stage_evidence = runtime.for_operation(
        execution=execution,
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.execution
        is execution
    )


def test_for_operation_preserves_knowledge_context() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )
    knowledge = _knowledge()

    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=knowledge,
    )

    assert (
        stage_evidence.execution_context.knowledge
        is knowledge
    )


def test_for_operation_exposes_execution_id() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.execution_id
        == "execution-001"
    )


def test_for_operation_exposes_operation_id() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    stage_evidence = runtime.for_operation(
        execution=_execution(
            operation_id="operation-777",
        ),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.operation_id
        == "operation-777"
    )


def test_for_operation_exposes_knowledge_scope() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    stage_evidence = runtime.for_operation(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.knowledge_scope_ref
        == "scope-001"
    )


def test_runtime_supports_independent_operations() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    first = runtime.for_operation(
        execution=_execution(
            operation_id="operation-001",
        ),
        knowledge=_knowledge(
            revision_ref="revision-001",
        ),
    )
    second = runtime.for_operation(
        execution=_execution(
            operation_id="operation-002",
        ),
        knowledge=_knowledge(
            revision_ref="revision-002",
        ),
    )

    assert (
        first.execution_context.operation_id
        == "operation-001"
    )
    assert (
        second.execution_context.operation_id
        == "operation-002"
    )
    assert (
        first.execution_context.knowledge.revision_ref
        == "revision-001"
    )
    assert (
        second.execution_context.knowledge.revision_ref
        == "revision-002"
    )


def test_runtime_rejects_invalid_service() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "service must be an instance of "
            "KnowledgeEvidenceService"
        ),
    ):
        KnowledgeEvidenceRuntime(
            service="invalid-service",
        )


def test_for_operation_rejects_invalid_execution() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    with pytest.raises(
        TypeError,
        match=(
            "execution must be an instance of ExecutionIdentity"
        ),
    ):
        runtime.for_operation(
            execution="invalid-execution",
            knowledge=_knowledge(),
        )


def test_for_operation_rejects_invalid_knowledge_context() -> None:
    runtime = KnowledgeEvidenceRuntime(
        service=_service(),
    )

    with pytest.raises(
        TypeError,
        match=(
            "knowledge must be an instance of "
            "KnowledgeEvidenceContext"
        ),
    ):
        runtime.for_operation(
            execution=_execution(),
            knowledge="invalid-knowledge",
        )
