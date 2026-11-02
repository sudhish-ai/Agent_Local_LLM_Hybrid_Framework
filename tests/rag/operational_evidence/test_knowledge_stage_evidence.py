# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeStageEvidence component.
#
# Responsibilities:
# - Validate stage-facing Operational Evidence emission.
# - Validate stable execution-context reuse.
# - Validate Knowledge event propagation.
# - Validate outcome propagation.
# - Validate measurement propagation.
# - Validate relationship propagation.
# - Validate observation timestamp propagation.
# - Validate persistence-result propagation.
# - Validate invalid dependency and event rejection.
#
# Must Not:
# - Test concrete JSON or JSONL persistence.
# - Test Knowledge pipeline-stage execution.
# - Test failure analysis or root-cause analysis.
# - Test retry, buffering, batching, or backpressure.
# - Test Knowledge content.

from datetime import datetime, timezone

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.measurement import (
    OperationalMeasurement,
)
from alhf.core.operational_evidence.contracts.outcome import (
    CompletionState,
    OperationalCriticality,
    OperationalOutcome,
    QualityState,
)
from alhf.core.operational_evidence.contracts.persistence_result import (
    PersistenceResult,
    PersistenceStatus,
)
from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.contracts.relationship import (
    OperationalRelationship,
    RelationshipType,
)
from alhf.core.operational_evidence.interfaces.evidence_sink import (
    EvidenceSink,
)
from alhf.rag.operational_evidence.contracts.knowledge_event_type import (
    KnowledgeEventType,
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
from alhf.rag.operational_evidence.knowledge_execution_context import (
    KnowledgeExecutionContext,
)
from alhf.rag.operational_evidence.knowledge_stage_evidence import (
    KnowledgeStageEvidence,
)


class StubEvidenceSink(EvidenceSink):
    """Evidence sink used to observe stage evidence publication."""

    def __init__(self) -> None:
        self.persisted_record: OperationalEvidenceRecord | None = None

    def persist(
        self,
        record: OperationalEvidenceRecord,
    ) -> PersistenceResult:
        self.persisted_record = record

        return PersistenceResult(
            record_id=record.record_id,
            status=PersistenceStatus.PERSISTED,
        )


def _execution_context() -> KnowledgeExecutionContext:
    return KnowledgeExecutionContext(
        execution=ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
            parent_operation_id="operation-parent",
        ),
        knowledge=KnowledgeEvidenceContext(
            knowledge_scope_ref="scope-001",
            logical_resource_ref="resource-001",
            revision_ref="revision-001",
        ),
    )


def _service(
    sink: StubEvidenceSink,
) -> KnowledgeEvidenceService:
    factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "record-001",
    )
    publisher = KnowledgeEvidencePublisher(
        sink=sink,
    )

    return KnowledgeEvidenceService(
        factory=factory,
        publisher=publisher,
    )


def test_create_knowledge_stage_evidence() -> None:
    sink = StubEvidenceSink()
    execution_context = _execution_context()

    stage_evidence = KnowledgeStageEvidence(
        execution_context=execution_context,
        service=_service(sink),
    )

    assert stage_evidence.execution_context is execution_context


def test_emit_publishes_knowledge_event() -> None:
    sink = StubEvidenceSink()
    stage_evidence = KnowledgeStageEvidence(
        execution_context=_execution_context(),
        service=_service(sink),
    )

    result = stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_STARTED,
    )

    assert result.status == PersistenceStatus.PERSISTED
    assert result.record_id == "record-001"
    assert sink.persisted_record is not None
    assert sink.persisted_record.event_name == "RETRIEVAL_STARTED"


def test_emit_preserves_execution_identity() -> None:
    sink = StubEvidenceSink()
    execution_context = _execution_context()

    stage_evidence = KnowledgeStageEvidence(
        execution_context=execution_context,
        service=_service(sink),
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.PARSING_STARTED,
    )

    assert sink.persisted_record is not None
    assert (
        sink.persisted_record.execution
        == execution_context.execution
    )


def test_emit_preserves_outcome() -> None:
    sink = StubEvidenceSink()
    stage_evidence = KnowledgeStageEvidence(
        execution_context=_execution_context(),
        service=_service(sink),
    )
    outcome = OperationalOutcome(
        completion=CompletionState.PARTIAL,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.PARSING_DEGRADED,
        outcome=outcome,
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.outcome == outcome


def test_emit_preserves_measurements() -> None:
    sink = StubEvidenceSink()
    stage_evidence = KnowledgeStageEvidence(
        execution_context=_execution_context(),
        service=_service(sink),
    )
    measurement = OperationalMeasurement(
        measurement_id="parsed_items",
        value=25,
        unit="count",
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.PARSING_COMPLETED,
        measurements=(measurement,),
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.measurements == (measurement,)


def test_emit_preserves_relationships() -> None:
    sink = StubEvidenceSink()
    stage_evidence = KnowledgeStageEvidence(
        execution_context=_execution_context(),
        service=_service(sink),
    )
    relationship = OperationalRelationship(
        source_ref="operation-001",
        target_ref="resource-001",
        relationship_type=RelationshipType.REFERENCES,
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.PARSING_COMPLETED,
        relationships=(relationship,),
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.relationships == (relationship,)


def test_emit_preserves_observed_at() -> None:
    sink = StubEvidenceSink()
    stage_evidence = KnowledgeStageEvidence(
        execution_context=_execution_context(),
        service=_service(sink),
    )
    observed_at = datetime(
        2026,
        10,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        observed_at=observed_at,
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.observed_at == observed_at


def test_multiple_events_reuse_same_execution_context() -> None:
    sink = StubEvidenceSink()
    execution_context = _execution_context()
    stage_evidence = KnowledgeStageEvidence(
        execution_context=execution_context,
        service=_service(sink),
    )

    stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_STARTED,
    )

    first_execution = sink.persisted_record.execution

    stage_evidence.emit(
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
    )

    second_execution = sink.persisted_record.execution

    assert first_execution == execution_context.execution
    assert second_execution == execution_context.execution


def test_rejects_invalid_execution_context() -> None:
    sink = StubEvidenceSink()

    with pytest.raises(
        TypeError,
        match=(
            "execution_context must be an instance of "
            "KnowledgeExecutionContext"
        ),
    ):
        KnowledgeStageEvidence(
            execution_context="invalid-context",
            service=_service(sink),
        )


def test_rejects_invalid_service() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "service must be an instance of "
            "KnowledgeEvidenceService"
        ),
    ):
        KnowledgeStageEvidence(
            execution_context=_execution_context(),
            service="invalid-service",
        )


def test_emit_rejects_invalid_event_type() -> None:
    sink = StubEvidenceSink()
    stage_evidence = KnowledgeStageEvidence(
        execution_context=_execution_context(),
        service=_service(sink),
    )

    with pytest.raises(
        TypeError,
        match=(
            "event_type must be an instance of KnowledgeEventType"
        ),
    ):
        stage_evidence.emit(
            event_type="RETRIEVAL_STARTED",
        )
