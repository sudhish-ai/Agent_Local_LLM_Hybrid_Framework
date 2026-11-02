# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Validates the local JSONL Operational Evidence write-read round trip.
#
# Responsibilities:
# - Persist Operational Evidence through JsonlEvidenceStore.
# - Retrieve persisted evidence through JsonlEvidenceRepository.
# - Validate record identity preservation across persistence.
# - Validate execution and correlation query behavior.
# - Validate nested outcome, measurement, and relationship preservation.
# - Validate retrieval across rotated JSONL partitions.
#
# Must Not:
# - Test RAG or Knowledge-specific semantics.
# - Perform failure analysis or root-cause analysis.
# - Test retention or archival behavior.
# - Test distributed or multi-process persistence.

from datetime import datetime, timezone
from pathlib import Path

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
from alhf.core.operational_evidence.contracts.record import (
    OperationalEvidenceRecord,
)
from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
)
from alhf.core.operational_evidence.contracts.relationship import (
    OperationalRelationship,
    RelationshipType,
)
from alhf.core.operational_evidence.contracts.schema_identity import (
    SchemaIdentity,
)
from alhf.core.operational_evidence.providers.jsonl_evidence_repository import (
    JsonlEvidenceRepository,
)
from alhf.core.operational_evidence.providers.jsonl_evidence_store import (
    JsonlEvidenceStore,
)


def _record(
    record_id: str,
    *,
    execution_id: str = "execution-001",
    correlation_id: str = "correlation-001",
) -> OperationalEvidenceRecord:
    return OperationalEvidenceRecord(
        record_id=record_id,
        schema=SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version="1.0",
        ),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="round-trip-test",
        event_name="OPERATION_COMPLETED",
        execution=ExecutionIdentity(
            correlation_id=correlation_id,
            execution_id=execution_id,
            operation_id=f"operation-{record_id}",
        ),
        observed_at=datetime(
            2026,
            10,
            27,
            12,
            30,
            tzinfo=timezone.utc,
        ),
        outcome=OperationalOutcome(
            completion=CompletionState.COMPLETE,
            quality=QualityState.ACCEPTABLE,
            criticality=OperationalCriticality.REQUIRED,
        ),
        measurements=(
            OperationalMeasurement(
                measurement_id="operation_duration",
                value=125.5,
                unit="milliseconds",
            ),
        ),
        relationships=(
            OperationalRelationship(
                source_ref=f"operation-{record_id}",
                target_ref="dependency-001",
                relationship_type=RelationshipType.DEPENDS_ON,
            ),
        ),
    )


def _store(
    directory: Path,
    *,
    max_file_size_bytes: int = 16_384,
) -> JsonlEvidenceStore:
    return JsonlEvidenceStore(
        directory,
        max_file_size_bytes=max_file_size_bytes,
    )


def _repository(
    directory: Path,
) -> JsonlEvidenceRepository:
    return JsonlEvidenceRepository(
        directory,
        max_line_bytes=16_384,
        max_scan_entries=100,
    )


def test_persisted_record_can_be_read_by_record_id(
    tmp_path: Path,
) -> None:
    record = _record("record-001")

    persistence_result = _store(tmp_path).persist(record)

    assert persistence_result.is_persisted is True

    restored = _repository(tmp_path).get_by_record_id(
        "record-001"
    )

    assert restored == record


def test_round_trip_preserves_execution_identity(
    tmp_path: Path,
) -> None:
    record = _record(
        "record-001",
        execution_id="execution-777",
        correlation_id="correlation-888",
    )

    _store(tmp_path).persist(record)

    restored = _repository(tmp_path).get_by_record_id(
        record.record_id
    )

    assert restored is not None
    assert restored.execution == record.execution


def test_round_trip_preserves_outcome(
    tmp_path: Path,
) -> None:
    record = _record("record-001")

    _store(tmp_path).persist(record)

    restored = _repository(tmp_path).get_by_record_id(
        record.record_id
    )

    assert restored is not None
    assert restored.outcome == record.outcome


def test_round_trip_preserves_measurements(
    tmp_path: Path,
) -> None:
    record = _record("record-001")

    _store(tmp_path).persist(record)

    restored = _repository(tmp_path).get_by_record_id(
        record.record_id
    )

    assert restored is not None
    assert restored.measurements == record.measurements


def test_round_trip_preserves_relationships(
    tmp_path: Path,
) -> None:
    record = _record("record-001")

    _store(tmp_path).persist(record)

    restored = _repository(tmp_path).get_by_record_id(
        record.record_id
    )

    assert restored is not None
    assert restored.relationships == record.relationships


def test_execution_query_reads_persisted_records(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)

    first = _record(
        "record-001",
        execution_id="execution-a",
    )
    second = _record(
        "record-002",
        execution_id="execution-b",
    )
    third = _record(
        "record-003",
        execution_id="execution-a",
    )

    assert store.persist(first).is_persisted is True
    assert store.persist(second).is_persisted is True
    assert store.persist(third).is_persisted is True

    records = _repository(tmp_path).get_by_execution_id(
        "execution-a",
        limit=10,
    )

    assert tuple(record.record_id for record in records) == (
        "record-001",
        "record-003",
    )


def test_correlation_query_reads_persisted_records(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)

    first = _record(
        "record-001",
        correlation_id="correlation-a",
    )
    second = _record(
        "record-002",
        correlation_id="correlation-b",
    )
    third = _record(
        "record-003",
        correlation_id="correlation-a",
    )

    assert store.persist(first).is_persisted is True
    assert store.persist(second).is_persisted is True
    assert store.persist(third).is_persisted is True

    records = _repository(tmp_path).get_by_correlation_id(
        "correlation-a",
        limit=10,
    )

    assert tuple(record.record_id for record in records) == (
        "record-001",
        "record-003",
    )


def test_repository_reads_across_rotated_partitions(
    tmp_path: Path,
) -> None:
    first = _record("record-001")
    second = _record("record-002")

    probe_directory = tmp_path / "probe"
    probe_store = _store(
        probe_directory,
        max_file_size_bytes=16_384,
    )

    assert probe_store.persist(first).is_persisted is True

    first_partition = next(
        probe_directory.glob("*.jsonl")
    )
    single_record_size = first_partition.stat().st_size

    evidence_directory = tmp_path / "evidence"
    store = _store(
        evidence_directory,
        max_file_size_bytes=single_record_size,
    )

    assert store.persist(first).is_persisted is True
    assert store.persist(second).is_persisted is True

    partitions = tuple(
        evidence_directory.glob("*.jsonl")
    )

    assert len(partitions) == 2

    restored = _repository(
        evidence_directory
    ).get_by_record_id(
        "record-002"
    )

    assert restored == second


def test_missing_record_returns_none_after_round_trip_setup(
    tmp_path: Path,
) -> None:
    store = _store(tmp_path)

    assert store.persist(
        _record("record-001")
    ).is_persisted is True

    restored = _repository(tmp_path).get_by_record_id(
        "missing-record"
    )

    assert restored is None
