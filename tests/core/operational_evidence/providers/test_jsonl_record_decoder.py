# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF JSONL Operational Evidence record decoder.
#
# Responsibilities:
# - Validate reconstruction of OperationalEvidenceRecord.
# - Validate nested schema and execution reconstruction.
# - Validate operational outcome reconstruction.
# - Validate measurement reconstruction.
# - Validate relationship reconstruction.
# - Validate ISO 8601 observation timestamps.
# - Validate malformed structural input rejection.
# - Validate required-field rejection.
#
# Must Not:
# - Test JSONL file reading.
# - Test partition discovery.
# - Test repository queries.
# - Test Operational Evidence persistence.
# - Test RAG or Knowledge-specific semantics.
# - Test schema migration or compatibility behavior.

from datetime import datetime, timezone

import pytest

from alhf.core.operational_evidence.contracts.outcome import (
    CompletionState,
    FailureCause,
    OperationalCriticality,
    QualityState,
    RetryDisposition,
)
from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
)
from alhf.core.operational_evidence.contracts.relationship import (
    RelationshipType,
)
from alhf.core.operational_evidence.providers.jsonl_record_decoder import (
    JsonlRecordDecoder,
)


def _record_data() -> dict[str, object]:
    return {
        "record_id": "record-001",
        "schema": {
            "schema_id": "operational-evidence-record",
            "schema_version": "1.0",
        },
        "record_family": "OPERATIONAL_EVENT",
        "producer": "test-component",
        "event_name": "OPERATION_COMPLETED",
        "execution": {
            "correlation_id": "correlation-001",
            "execution_id": "execution-001",
            "operation_id": "operation-001",
            "parent_operation_id": None,
        },
        "observed_at": "2026-10-27T12:30:00+00:00",
        "outcome": None,
        "measurements": [],
        "relationships": [],
    }


def test_decode_minimal_record() -> None:
    record = JsonlRecordDecoder.decode(
        _record_data(),
    )

    assert record.record_id == "record-001"
    assert record.producer == "test-component"
    assert record.event_name == "OPERATION_COMPLETED"
    assert (
        record.record_family
        == OperationalRecordFamily.OPERATIONAL_EVENT
    )


def test_decode_schema_identity() -> None:
    record = JsonlRecordDecoder.decode(
        _record_data(),
    )

    assert (
        record.schema.schema_id
        == "operational-evidence-record"
    )
    assert record.schema.schema_version == "1.0"


def test_decode_execution_identity() -> None:
    record = JsonlRecordDecoder.decode(
        _record_data(),
    )

    assert (
        record.execution.correlation_id
        == "correlation-001"
    )
    assert record.execution.execution_id == "execution-001"
    assert record.execution.operation_id == "operation-001"
    assert record.execution.parent_operation_id is None


def test_decode_parent_operation_identity() -> None:
    data = _record_data()
    execution = data["execution"]

    assert isinstance(
        execution,
        dict,
    )

    execution["parent_operation_id"] = "operation-parent"

    record = JsonlRecordDecoder.decode(
        data,
    )

    assert (
        record.execution.parent_operation_id
        == "operation-parent"
    )


def test_decode_observed_at() -> None:
    record = JsonlRecordDecoder.decode(
        _record_data(),
    )

    assert record.observed_at == datetime(
        2026,
        10,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )


def test_decode_operational_outcome() -> None:
    data = _record_data()
    data["outcome"] = {
        "completion": "PARTIAL",
        "quality": "DEGRADED",
        "criticality": "REQUIRED",
        "failure_cause": "DEPENDENCY",
        "retry_disposition": "RETRYABLE",
    }

    record = JsonlRecordDecoder.decode(
        data,
    )

    assert record.outcome is not None
    assert (
        record.outcome.completion
        == CompletionState.PARTIAL
    )
    assert record.outcome.quality == QualityState.DEGRADED
    assert (
        record.outcome.criticality
        == OperationalCriticality.REQUIRED
    )
    assert (
        record.outcome.failure_cause
        == FailureCause.DEPENDENCY
    )
    assert (
        record.outcome.retry_disposition
        == RetryDisposition.RETRYABLE
    )


def test_decode_measurements() -> None:
    data = _record_data()
    data["measurements"] = [
        {
            "measurement_id": "operation_duration",
            "value": 125.5,
            "unit": "milliseconds",
            "methodology_id": None,
            "methodology_version": None,
        },
        {
            "measurement_id": "processed_items",
            "value": 10,
            "unit": "count",
            "methodology_id": "counter",
            "methodology_version": "1.0",
        },
    ]

    record = JsonlRecordDecoder.decode(
        data,
    )

    assert len(record.measurements) == 2
    assert (
        record.measurements[0].measurement_id
        == "operation_duration"
    )
    assert record.measurements[0].value == 125.5
    assert (
        record.measurements[1].measurement_id
        == "processed_items"
    )
    assert record.measurements[1].methodology_id == "counter"
    assert (
        record.measurements[1].methodology_version
        == "1.0"
    )


def test_decode_relationships() -> None:
    data = _record_data()
    data["relationships"] = [
        {
            "source_ref": "operation-002",
            "target_ref": "operation-001",
            "relationship_type": "DEPENDS_ON",
        },
    ]

    record = JsonlRecordDecoder.decode(
        data,
    )

    assert len(record.relationships) == 1
    assert record.relationships[0].source_ref == "operation-002"
    assert record.relationships[0].target_ref == "operation-001"
    assert (
        record.relationships[0].relationship_type
        == RelationshipType.DEPENDS_ON
    )


def test_decode_rejects_non_mapping_input() -> None:
    with pytest.raises(
        TypeError,
        match="data must be a mapping",
    ):
        JsonlRecordDecoder.decode(
            ["invalid"],
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "record_id",
        "schema",
        "record_family",
        "producer",
        "event_name",
        "execution",
        "observed_at",
        "measurements",
        "relationships",
    ),
)
def test_decode_rejects_missing_required_field(
    field_name: str,
) -> None:
    data = _record_data()
    del data[field_name]

    with pytest.raises(
        ValueError,
        match=f"missing required field: {field_name}",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_non_mapping_schema() -> None:
    data = _record_data()
    data["schema"] = "invalid"

    with pytest.raises(
        TypeError,
        match="schema must be a mapping",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_non_mapping_execution() -> None:
    data = _record_data()
    data["execution"] = "invalid"

    with pytest.raises(
        TypeError,
        match="execution must be a mapping",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_non_mapping_outcome() -> None:
    data = _record_data()
    data["outcome"] = "invalid"

    with pytest.raises(
        TypeError,
        match="outcome must be a mapping or None",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_invalid_observed_at_type() -> None:
    data = _record_data()
    data["observed_at"] = 123

    with pytest.raises(
        TypeError,
        match="observed_at must be an ISO 8601 string",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_invalid_observed_at_value() -> None:
    data = _record_data()
    data["observed_at"] = "not-a-datetime"

    with pytest.raises(ValueError):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_non_sequence_measurements() -> None:
    data = _record_data()
    data["measurements"] = "invalid"

    with pytest.raises(
        TypeError,
        match="measurements must be a list or tuple",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_non_mapping_measurement() -> None:
    data = _record_data()
    data["measurements"] = [
        "invalid",
    ]

    with pytest.raises(
        TypeError,
        match="measurement must be a mapping",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_non_sequence_relationships() -> None:
    data = _record_data()
    data["relationships"] = "invalid"

    with pytest.raises(
        TypeError,
        match="relationships must be a list or tuple",
    ):
        JsonlRecordDecoder.decode(
            data,
        )


def test_decode_rejects_non_mapping_relationship() -> None:
    data = _record_data()
    data["relationships"] = [
        "invalid",
    ]

    with pytest.raises(
        TypeError,
        match="relationship must be a mapping",
    ):
        JsonlRecordDecoder.decode(
            data,
        )
