# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeStageEvidenceFactory.
#
# Responsibilities:
# - Validate KnowledgeStageEvidence creation.
# - Validate KnowledgeEvidenceService composition.
# - Validate execution identity preservation.
# - Validate governed Knowledge context preservation.
# - Validate created stage-evidence execution context.
# - Validate invalid factory dependencies.
# - Validate invalid execution contracts.
# - Validate invalid Knowledge context contracts.
#
# Must Not:
# - Test Operational Evidence persistence.
# - Test JSON or JSONL behavior.
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
from alhf.rag.operational_evidence.knowledge_evidence_service import (
    KnowledgeEvidenceService,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence_factory import (
    KnowledgeStageEvidenceFactory,
)


class StubEvidenceSink(EvidenceSink):
    """Minimal sink used to construct a real evidence service."""

    def persist(
        self,
        record: OperationalEvidenceRecord,
    ) -> PersistenceResult:
        return PersistenceResult(
            record_id=record.record_id,
            status=PersistenceStatus.PERSISTED,
        )


def _execution() -> ExecutionIdentity:
    return ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
        parent_operation_id="operation-parent",
    )


def _knowledge() -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref="revision-001",
        derivation_ref="derivation-001",
    )


def _service() -> KnowledgeEvidenceService:
    factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "record-001",
    )
    publisher = KnowledgeEvidencePublisher(
        sink=StubEvidenceSink(),
    )

    return KnowledgeEvidenceService(
        factory=factory,
        publisher=publisher,
    )


def test_create_stage_evidence() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert isinstance(
        stage_evidence,
        KnowledgeStageEvidence,
    )


def test_create_preserves_execution_identity() -> None:
    execution = _execution()
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=execution,
        knowledge=_knowledge(),
    )

    assert stage_evidence.execution_context.execution is execution


def test_create_preserves_knowledge_context() -> None:
    knowledge = _knowledge()
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=_execution(),
        knowledge=knowledge,
    )

    assert stage_evidence.execution_context.knowledge is knowledge


def test_created_context_exposes_correlation_id() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.correlation_id
        == "correlation-001"
    )


def test_created_context_exposes_execution_id() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.execution_id
        == "execution-001"
    )


def test_created_context_exposes_operation_id() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.operation_id
        == "operation-001"
    )


def test_created_context_exposes_parent_operation_id() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.parent_operation_id
        == "operation-parent"
    )


def test_created_context_exposes_knowledge_scope() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    stage_evidence = factory.create(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        stage_evidence.execution_context.knowledge_scope_ref
        == "scope-001"
    )


def test_factory_rejects_invalid_service() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "service must be an instance of "
            "KnowledgeEvidenceService"
        ),
    ):
        KnowledgeStageEvidenceFactory(
            service="invalid-service",
        )


def test_create_rejects_invalid_execution() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    with pytest.raises(
        TypeError,
        match=(
            "execution must be an instance of ExecutionIdentity"
        ),
    ):
        factory.create(
            execution="invalid-execution",
            knowledge=_knowledge(),
        )


def test_create_rejects_invalid_knowledge_context() -> None:
    factory = KnowledgeStageEvidenceFactory(
        service=_service(),
    )

    with pytest.raises(
        TypeError,
        match=(
            "knowledge must be an instance of "
            "KnowledgeEvidenceContext"
        ),
    ):
        factory.create(
            execution=_execution(),
            knowledge="invalid-knowledge",
        )
