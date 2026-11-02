# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeEvidenceService.
#
# Responsibilities:
# - Validate Knowledge Operational Evidence service composition.
# - Validate factory delegation.
# - Validate publisher delegation.
# - Validate execution and Knowledge context preservation.
# - Validate event propagation.
# - Validate optional outcome propagation.
# - Validate optional measurement and relationship propagation.
# - Validate observation timestamp propagation.
# - Validate provider-neutral persistence-result propagation.
# - Validate invalid service dependencies.
#
# Must Not:
# - Test JSON or JSONL behavior.
# - Test concrete persistence providers.
# - Test retrieval, indexing, parsing, or evaluation execution.
# - Test failure analysis or root-cause analysis.
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


class StubEvidenceSink(EvidenceSink):
    """Evidence sink used to observe service publication."""

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


def _execution() -> ExecutionIdentity:
    return ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )


def _context() -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        revision_ref="revision-001",
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


def test_record_creates_and_publishes_evidence() -> None:
    sink = StubEvidenceSink()
    service = _service(sink)

    result = service.record(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
    )

    assert result.status == PersistenceStatus.PERSISTED
    assert result.record_id == "record-001"
    assert sink.persisted_record is not None
    assert sink.persisted_record.record_id == "record-001"


def test_record_preserves_execution_identity() -> None:
    sink = StubEvidenceSink()
    service = _service(sink)

    service.record(
        execution=_execution(),
        event_type=KnowledgeEventType.PARSING_STARTED,
        context=_context(),
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.execution == _execution()


def test_record_preserves_knowledge_event() -> None:
    sink = StubEvidenceSink()
    service = _service(sink)

    service.record(
        execution=_execution(),
        event_type=KnowledgeEventType.INDEXING_DEGRADED,
        context=_context(),
    )

    assert sink.persisted_record is not None
    assert (
        sink.persisted_record.event_name
        == "INDEXING_DEGRADED"
    )


def test_record_preserves_outcome() -> None:
    sink = StubEvidenceSink()
    service = _service(sink)

    outcome = OperationalOutcome(
        completion=CompletionState.PARTIAL,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
    )

    service.record(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_DEGRADED,
        context=_context(),
        outcome=outcome,
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.outcome == outcome


def test_record_preserves_measurements() -> None:
    sink = StubEvidenceSink()
    service = _service(sink)

    measurement = OperationalMeasurement(
        measurement_id="retrieved_items",
        value=5,
        unit="count",
    )

    service.record(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
        measurements=(measurement,),
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.measurements == (measurement,)


def test_record_preserves_relationships() -> None:
    sink = StubEvidenceSink()
    service = _service(sink)

    relationship = OperationalRelationship(
        source_ref="operation-001",
        target_ref="index-generation-001",
        relationship_type=RelationshipType.DEPENDS_ON,
    )

    service.record(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
        relationships=(relationship,),
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.relationships == (relationship,)


def test_record_preserves_observation_timestamp() -> None:
    sink = StubEvidenceSink()
    service = _service(sink)

    observed_at = datetime(
        2026,
        10,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )

    service.record(
        execution=_execution(),
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=_context(),
        observed_at=observed_at,
    )

    assert sink.persisted_record is not None
    assert sink.persisted_record.observed_at == observed_at


def test_service_rejects_invalid_factory() -> None:
    sink = StubEvidenceSink()

    with pytest.raises(
        TypeError,
        match=(
            "factory must be an instance of "
            "KnowledgeEvidenceFactory"
        ),
    ):
        KnowledgeEvidenceService(
            factory="invalid-factory",
            publisher=KnowledgeEvidencePublisher(
                sink=sink,
            ),
        )


def test_service_rejects_invalid_publisher() -> None:
    factory = KnowledgeEvidenceFactory(
        producer="knowledge-foundation",
        record_id_factory=lambda: "record-001",
    )

    with pytest.raises(
        TypeError,
        match=(
            "publisher must be an instance of "
            "KnowledgeEvidencePublisher"
        ),
    ):
        KnowledgeEvidenceService(
            factory=factory,
            publisher="invalid-publisher",
        )
