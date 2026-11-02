# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF EvidenceSink interface.
#
# Responsibilities:
# - Validate that EvidenceSink is an abstract contract.
# - Validate that concrete evidence sinks can implement persistence.
# - Validate OperationalEvidenceRecord integration.
# - Validate PersistenceResult integration.
# - Protect storage-provider independence.
#
# Must Not:
# - Test JSON or JSONL persistence.
# - Test filesystem behavior.
# - Test database behavior.
# - Test provider-specific implementation.
# - Test RAG or Knowledge-specific semantics.
# - Test buffering, batching, or retry execution.
# - Test failure analysis or root-cause analysis.

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


class StubEvidenceSink(EvidenceSink):
    """Minimal concrete sink used to validate the interface contract."""

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


def _record() -> OperationalEvidenceRecord:
    return OperationalEvidenceRecord(
        record_id="record-001",
        schema=SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version="1.0",
        ),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
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
            0,
            tzinfo=timezone.utc,
        ),
    )


def test_evidence_sink_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        EvidenceSink()


def test_concrete_sink_can_be_instantiated() -> None:
    sink = StubEvidenceSink()

    assert isinstance(
        sink,
        EvidenceSink,
    )


def test_persist_accepts_operational_evidence_record() -> None:
    sink = StubEvidenceSink()
    record = _record()

    result = sink.persist(record)

    assert sink.persisted_record is record
    assert result.record_id == record.record_id


def test_persist_returns_persistence_result() -> None:
    sink = StubEvidenceSink()

    result = sink.persist(
        _record(),
    )

    assert isinstance(
        result,
        PersistenceResult,
    )


def test_successful_sink_returns_persisted_status() -> None:
    sink = StubEvidenceSink()

    result = sink.persist(
        _record(),
    )

    assert result.status == PersistenceStatus.PERSISTED
    assert result.is_persisted is True
    assert result.has_failure is False


def test_sink_preserves_record_identity() -> None:
    sink = StubEvidenceSink()
    record = _record()

    result = sink.persist(record)

    assert result.record_id == "record-001"


def test_sink_contract_does_not_require_storage_specific_input() -> None:
    sink = StubEvidenceSink()
    record = _record()

    result = sink.persist(record)

    assert result.is_persisted is True
    assert sink.persisted_record == record


class MissingPersistEvidenceSink(EvidenceSink):
    """Invalid sink intentionally missing the persistence implementation."""

    pass


def test_subclass_without_persist_implementation_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingPersistEvidenceSink()
