# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF EvidenceRepository interface.
#
# Responsibilities:
# - Validate that EvidenceRepository is an abstract contract.
# - Validate exact record lookup semantics.
# - Validate bounded execution-based retrieval semantics.
# - Validate bounded correlation-based retrieval semantics.
# - Validate immutable tuple-based collection results.
# - Validate OperationalEvidenceRecord integration.
# - Protect storage-provider independence.
#
# Must Not:
# - Test physical persistence.
# - Test JSON or JSONL behavior.
# - Test filesystem or database behavior.
# - Test provider-specific indexing.
# - Test RAG or Knowledge-specific query semantics.
# - Test failure analysis or root-cause analysis.
# - Test predictive or statistical analysis.

from datetime import datetime, timezone

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
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
from alhf.core.operational_evidence.interfaces.evidence_repository import (
    EvidenceRepository,
)


def _record(
    *,
    record_id: str,
    correlation_id: str = "correlation-001",
    execution_id: str = "execution-001",
    operation_id: str = "operation-001",
) -> OperationalEvidenceRecord:
    return OperationalEvidenceRecord(
        record_id=record_id,
        schema=SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version="1.0",
        ),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=ExecutionIdentity(
            correlation_id=correlation_id,
            execution_id=execution_id,
            operation_id=operation_id,
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


class StubEvidenceRepository(EvidenceRepository):
    """Minimal repository used to validate the interface contract."""

    def __init__(
        self,
        records: tuple[OperationalEvidenceRecord, ...],
    ) -> None:
        self._records = records

    def get_by_record_id(
        self,
        record_id: str,
    ) -> OperationalEvidenceRecord | None:
        for record in self._records:
            if record.record_id == record_id:
                return record

        return None

    def get_by_execution_id(
        self,
        execution_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        matching_records = tuple(
            record
            for record in self._records
            if record.execution.execution_id == execution_id
        )

        return matching_records[:limit]

    def get_by_correlation_id(
        self,
        correlation_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        matching_records = tuple(
            record
            for record in self._records
            if record.execution.correlation_id == correlation_id
        )

        return matching_records[:limit]


def test_evidence_repository_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        EvidenceRepository()


def test_concrete_repository_can_be_instantiated() -> None:
    repository = StubEvidenceRepository(
        records=(),
    )

    assert isinstance(
        repository,
        EvidenceRepository,
    )


def test_get_by_record_id_returns_matching_record() -> None:
    expected_record = _record(
        record_id="record-001",
    )
    repository = StubEvidenceRepository(
        records=(expected_record,),
    )

    result = repository.get_by_record_id(
        "record-001",
    )

    assert result is expected_record


def test_get_by_record_id_returns_none_when_record_is_missing() -> None:
    repository = StubEvidenceRepository(
        records=(
            _record(
                record_id="record-001",
            ),
        ),
    )

    result = repository.get_by_record_id(
        "record-missing",
    )

    assert result is None


def test_get_by_execution_id_returns_matching_records() -> None:
    first_record = _record(
        record_id="record-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )
    second_record = _record(
        record_id="record-002",
        execution_id="execution-001",
        operation_id="operation-002",
    )
    unrelated_record = _record(
        record_id="record-003",
        execution_id="execution-002",
        operation_id="operation-003",
    )

    repository = StubEvidenceRepository(
        records=(
            first_record,
            second_record,
            unrelated_record,
        ),
    )

    result = repository.get_by_execution_id(
        "execution-001",
        limit=10,
    )

    assert result == (
        first_record,
        second_record,
    )


def test_get_by_execution_id_returns_empty_tuple_when_missing() -> None:
    repository = StubEvidenceRepository(
        records=(
            _record(
                record_id="record-001",
                execution_id="execution-001",
            ),
        ),
    )

    result = repository.get_by_execution_id(
        "execution-missing",
        limit=10,
    )

    assert result == ()


def test_get_by_execution_id_respects_limit() -> None:
    first_record = _record(
        record_id="record-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )
    second_record = _record(
        record_id="record-002",
        execution_id="execution-001",
        operation_id="operation-002",
    )

    repository = StubEvidenceRepository(
        records=(
            first_record,
            second_record,
        ),
    )

    result = repository.get_by_execution_id(
        "execution-001",
        limit=1,
    )

    assert result == (first_record,)


def test_get_by_execution_id_returns_tuple() -> None:
    repository = StubEvidenceRepository(
        records=(
            _record(
                record_id="record-001",
                execution_id="execution-001",
            ),
        ),
    )

    result = repository.get_by_execution_id(
        "execution-001",
        limit=10,
    )

    assert isinstance(
        result,
        tuple,
    )


def test_get_by_correlation_id_returns_matching_records() -> None:
    first_record = _record(
        record_id="record-001",
        correlation_id="correlation-001",
        execution_id="execution-001",
    )
    second_record = _record(
        record_id="record-002",
        correlation_id="correlation-001",
        execution_id="execution-002",
    )
    unrelated_record = _record(
        record_id="record-003",
        correlation_id="correlation-002",
        execution_id="execution-003",
    )

    repository = StubEvidenceRepository(
        records=(
            first_record,
            second_record,
            unrelated_record,
        ),
    )

    result = repository.get_by_correlation_id(
        "correlation-001",
        limit=10,
    )

    assert result == (
        first_record,
        second_record,
    )


def test_get_by_correlation_id_returns_empty_tuple_when_missing() -> None:
    repository = StubEvidenceRepository(
        records=(
            _record(
                record_id="record-001",
                correlation_id="correlation-001",
            ),
        ),
    )

    result = repository.get_by_correlation_id(
        "correlation-missing",
        limit=10,
    )

    assert result == ()


def test_get_by_correlation_id_respects_limit() -> None:
    first_record = _record(
        record_id="record-001",
        correlation_id="correlation-001",
        execution_id="execution-001",
    )
    second_record = _record(
        record_id="record-002",
        correlation_id="correlation-001",
        execution_id="execution-002",
    )

    repository = StubEvidenceRepository(
        records=(
            first_record,
            second_record,
        ),
    )

    result = repository.get_by_correlation_id(
        "correlation-001",
        limit=1,
    )

    assert result == (first_record,)


def test_get_by_correlation_id_returns_tuple() -> None:
    repository = StubEvidenceRepository(
        records=(
            _record(
                record_id="record-001",
                correlation_id="correlation-001",
            ),
        ),
    )

    result = repository.get_by_correlation_id(
        "correlation-001",
        limit=10,
    )

    assert isinstance(
        result,
        tuple,
    )


class MissingRecordLookupRepository(EvidenceRepository):
    """Invalid repository missing exact record lookup."""

    def get_by_execution_id(
        self,
        execution_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        return ()

    def get_by_correlation_id(
        self,
        correlation_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        return ()


def test_repository_missing_record_lookup_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingRecordLookupRepository()


class MissingExecutionLookupRepository(EvidenceRepository):
    """Invalid repository missing execution lookup."""

    def get_by_record_id(
        self,
        record_id: str,
    ) -> OperationalEvidenceRecord | None:
        return None

    def get_by_correlation_id(
        self,
        correlation_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        return ()


def test_repository_missing_execution_lookup_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingExecutionLookupRepository()


class MissingCorrelationLookupRepository(EvidenceRepository):
    """Invalid repository missing correlation lookup."""

    def get_by_record_id(
        self,
        record_id: str,
    ) -> OperationalEvidenceRecord | None:
        return None

    def get_by_execution_id(
        self,
        execution_id: str,
        *,
        limit: int,
    ) -> tuple[OperationalEvidenceRecord, ...]:
        return ()


def test_repository_missing_correlation_lookup_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingCorrelationLookupRepository()
