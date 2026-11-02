# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeEvidencePublisher.
#
# Responsibilities:
# - Validate publication through the universal EvidenceSink.
# - Validate universal record forwarding.
# - Validate PersistenceResult propagation.
# - Validate persistence record identity consistency.
# - Validate invalid evidence rejection.
# - Validate invalid sink configuration.
# - Validate invalid sink-result rejection.
#
# Must Not:
# - Test JSON or JSONL persistence.
# - Test concrete persistence providers.
# - Test Operational Evidence construction.
# - Test retry, buffering, batching, or backpressure.
# - Test failure analysis or root-cause analysis.
# - Test Knowledge content.

from datetime import datetime, timezone

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
from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
)
from alhf.core.operational_evidence.contracts.schema_identity import (
    SchemaIdentity,
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
from alhf.rag.operational_evidence.contracts.knowledge_operation_evidence import (
    KnowledgeOperationEvidence,
)
from alhf.rag.operational_evidence.knowledge_evidence_publisher import (
    KnowledgeEvidencePublisher,
)


class StubEvidenceSink(EvidenceSink):
    """Evidence sink used to validate successful publication."""

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


class MismatchedRecordIdSink(EvidenceSink):
    """Evidence sink returning an invalid persistence identity."""

    def persist(
        self,
        record: OperationalEvidenceRecord,
    ) -> PersistenceResult:
        return PersistenceResult(
            record_id="different-record",
            status=PersistenceStatus.PERSISTED,
        )


class InvalidResultSink(EvidenceSink):
    """Evidence sink returning an invalid result contract."""

    def persist(
        self,
        record: OperationalEvidenceRecord,
    ) -> PersistenceResult:
        return "invalid-result"


def _evidence() -> KnowledgeOperationEvidence:
    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version="1.0",
        ),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="knowledge-foundation",
        event_name="RETRIEVAL_COMPLETED",
        execution=ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
        ),
        observed_at=datetime(
            2026,
            10,
            27,
            12,
            30,
            tzinfo=timezone.utc,
        ),
    )

    return KnowledgeOperationEvidence(
        record=record,
        event_type=KnowledgeEventType.RETRIEVAL_COMPLETED,
        context=KnowledgeEvidenceContext(
            knowledge_scope_ref="scope-001",
            revision_ref="revision-001",
        ),
    )


def test_create_knowledge_evidence_publisher() -> None:
    sink = StubEvidenceSink()

    publisher = KnowledgeEvidencePublisher(
        sink=sink,
    )

    assert isinstance(
        publisher,
        KnowledgeEvidencePublisher,
    )


def test_publish_forwards_universal_record_to_sink() -> None:
    sink = StubEvidenceSink()
    publisher = KnowledgeEvidencePublisher(
        sink=sink,
    )
    evidence = _evidence()

    publisher.publish(
        evidence,
    )

    assert sink.persisted_record is evidence.record


def test_publish_returns_persistence_result() -> None:
    publisher = KnowledgeEvidencePublisher(
        sink=StubEvidenceSink(),
    )

    result = publisher.publish(
        _evidence(),
    )

    assert isinstance(
        result,
        PersistenceResult,
    )


def test_publish_returns_persisted_status() -> None:
    publisher = KnowledgeEvidencePublisher(
        sink=StubEvidenceSink(),
    )

    result = publisher.publish(
        _evidence(),
    )

    assert result.status == PersistenceStatus.PERSISTED
    assert result.is_persisted is True


def test_publish_preserves_record_identity() -> None:
    publisher = KnowledgeEvidencePublisher(
        sink=StubEvidenceSink(),
    )

    result = publisher.publish(
        _evidence(),
    )

    assert result.record_id == "record-001"


def test_publisher_rejects_invalid_sink() -> None:
    with pytest.raises(
        TypeError,
        match="sink must be an instance of EvidenceSink",
    ):
        KnowledgeEvidencePublisher(
            sink="invalid-sink",
        )


def test_publish_rejects_invalid_evidence() -> None:
    publisher = KnowledgeEvidencePublisher(
        sink=StubEvidenceSink(),
    )

    with pytest.raises(
        TypeError,
        match=(
            "evidence must be an instance of "
            "KnowledgeOperationEvidence"
        ),
    ):
        publisher.publish(
            "invalid-evidence",
        )


def test_publish_rejects_invalid_sink_result() -> None:
    publisher = KnowledgeEvidencePublisher(
        sink=InvalidResultSink(),
    )

    with pytest.raises(
        TypeError,
        match=(
            "EvidenceSink.persist must return PersistenceResult"
        ),
    ):
        publisher.publish(
            _evidence(),
        )


def test_publish_rejects_mismatched_record_identity() -> None:
    publisher = KnowledgeEvidencePublisher(
        sink=MismatchedRecordIdSink(),
    )

    with pytest.raises(
        ValueError,
        match=(
            "persistence result record_id must match evidence record_id"
        ),
    ):
        publisher.publish(
            _evidence(),
        )
