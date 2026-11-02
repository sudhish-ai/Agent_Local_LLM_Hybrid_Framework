# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF OperationalEvidenceRecord contract.
#
# Responsibilities:
# - Validate required record-envelope semantics.
# - Validate composed Operational Evidence contracts.
# - Validate record text normalization.
# - Validate timezone-aware observation timestamps.
# - Validate optional operational outcomes.
# - Validate measurement collections.
# - Validate relationship collections.
# - Validate invalid contract rejection.
# - Validate tuple collection requirements.
# - Validate record immutability.
#
# Must Not:
# - Test RAG or Knowledge-specific semantics.
# - Test workflow, task, or agent-specific semantics.
# - Test identifier generation.
# - Test failure analysis or root-cause analysis.
# - Test persistence, JSON, or JSONL behavior.
# - Test logging or MetricsRegistry behavior.

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

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


def _schema() -> SchemaIdentity:
    return SchemaIdentity(
        schema_id="operational-evidence-record",
        schema_version="1.0",
    )


def _execution() -> ExecutionIdentity:
    return ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )


def _outcome() -> OperationalOutcome:
    return OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=OperationalCriticality.REQUIRED,
    )


def _measurement() -> OperationalMeasurement:
    return OperationalMeasurement(
        measurement_id="operation_duration",
        value=125.5,
        unit="milliseconds",
    )


def _relationship() -> OperationalRelationship:
    return OperationalRelationship(
        source_ref="operation-001",
        target_ref="dependency-001",
        relationship_type=RelationshipType.DEPENDS_ON,
    )


def test_create_minimal_operational_evidence_record() -> None:
    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=_execution(),
    )

    assert record.record_id == "record-001"
    assert record.schema == _schema()
    assert (
        record.record_family
        == OperationalRecordFamily.OPERATIONAL_EVENT
    )
    assert record.producer == "test-component"
    assert record.event_name == "OPERATION_COMPLETED"
    assert record.execution == _execution()
    assert record.outcome is None
    assert record.measurements == ()
    assert record.relationships == ()


def test_create_complete_operational_evidence_record() -> None:
    observed_at = datetime(
        2026,
        10,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )
    outcome = _outcome()
    measurement = _measurement()
    relationship = _relationship()

    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=_execution(),
        observed_at=observed_at,
        outcome=outcome,
        measurements=(measurement,),
        relationships=(relationship,),
    )

    assert record.observed_at == observed_at
    assert record.outcome == outcome
    assert record.measurements == (measurement,)
    assert record.relationships == (relationship,)


def test_record_text_fields_are_whitespace_normalized() -> None:
    record = OperationalEvidenceRecord(
        record_id="  record-001  ",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="  test-component  ",
        event_name="  OPERATION_COMPLETED  ",
        execution=_execution(),
    )

    assert record.record_id == "record-001"
    assert record.producer == "test-component"
    assert record.event_name == "OPERATION_COMPLETED"


@pytest.mark.parametrize(
    "field_name",
    (
        "record_id",
        "producer",
        "event_name",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        "",
        "   ",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
    invalid_value: str,
) -> None:
    values = {
        "record_id": "record-001",
        "schema": _schema(),
        "record_family": (
            OperationalRecordFamily.OPERATIONAL_EVENT
        ),
        "producer": "test-component",
        "event_name": "OPERATION_COMPLETED",
        "execution": _execution(),
    }

    values[field_name] = invalid_value

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        OperationalEvidenceRecord(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "record_id",
        "producer",
        "event_name",
    ),
)
def test_required_text_rejects_non_string_value(
    field_name: str,
) -> None:
    values = {
        "record_id": "record-001",
        "schema": _schema(),
        "record_family": (
            OperationalRecordFamily.OPERATIONAL_EVENT
        ),
        "producer": "test-component",
        "event_name": "OPERATION_COMPLETED",
        "execution": _execution(),
    }

    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        OperationalEvidenceRecord(**values)


def test_schema_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match="schema must be an instance of SchemaIdentity",
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema="schema-001",
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
        )


def test_record_family_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "record_family must be an instance of "
            "OperationalRecordFamily"
        ),
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family="OPERATIONAL_EVENT",
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
        )


def test_execution_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "execution must be an instance of ExecutionIdentity"
        ),
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution="execution-001",
        )


def test_outcome_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "outcome must be an instance of OperationalOutcome"
        ),
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
            outcome="COMPLETE",
        )


def test_observed_at_is_timezone_aware_by_default() -> None:
    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=_execution(),
    )

    assert record.observed_at.tzinfo is not None
    assert record.observed_at.utcoffset() is not None


def test_observed_at_accepts_timezone_aware_datetime() -> None:
    observed_at = datetime(
        2026,
        10,
        27,
        18,
        0,
        tzinfo=timezone(
            timedelta(hours=5, minutes=30)
        ),
    )

    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=_execution(),
        observed_at=observed_at,
    )

    assert record.observed_at == observed_at


def test_observed_at_rejects_naive_datetime() -> None:
    with pytest.raises(
        ValueError,
        match="observed_at must be timezone-aware",
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
            observed_at=datetime(
                2026,
                10,
                27,
                12,
                30,
            ),
        )


def test_observed_at_rejects_non_datetime_value() -> None:
    with pytest.raises(
        TypeError,
        match="observed_at must be a datetime",
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
            observed_at="2026-10-27T12:30:00Z",
        )


def test_measurements_preserve_multiple_measurements() -> None:
    duration = OperationalMeasurement(
        measurement_id="operation_duration",
        value=125.5,
        unit="milliseconds",
    )
    processed = OperationalMeasurement(
        measurement_id="processed_items",
        value=100,
        unit="count",
    )

    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=_execution(),
        measurements=(
            duration,
            processed,
        ),
    )

    assert record.measurements == (
        duration,
        processed,
    )


def test_measurements_reject_non_tuple_collection() -> None:
    with pytest.raises(
        TypeError,
        match="measurements must be a tuple",
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
            measurements=[_measurement()],
        )


def test_measurements_reject_invalid_tuple_member() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "measurements must contain only "
            "OperationalMeasurement instances"
        ),
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
            measurements=("invalid-measurement",),
        )


def test_relationships_preserve_multiple_relationships() -> None:
    first_relationship = OperationalRelationship(
        source_ref="operation-001",
        target_ref="dependency-001",
        relationship_type=RelationshipType.DEPENDS_ON,
    )
    second_relationship = OperationalRelationship(
        source_ref="operation-001",
        target_ref="artifact-001",
        relationship_type=RelationshipType.REFERENCES,
    )

    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=_execution(),
        relationships=(
            first_relationship,
            second_relationship,
        ),
    )

    assert record.relationships == (
        first_relationship,
        second_relationship,
    )


def test_relationships_reject_non_tuple_collection() -> None:
    with pytest.raises(
        TypeError,
        match="relationships must be a tuple",
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
            relationships=[_relationship()],
        )


def test_relationships_reject_invalid_tuple_member() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "relationships must contain only "
            "OperationalRelationship instances"
        ),
    ):
        OperationalEvidenceRecord(
            record_id="record-001",
            schema=_schema(),
            record_family=(
                OperationalRecordFamily.OPERATIONAL_EVENT
            ),
            producer="test-component",
            event_name="OPERATION_COMPLETED",
            execution=_execution(),
            relationships=("invalid-relationship",),
        )


def test_record_accepts_measurement_family() -> None:
    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.MEASUREMENT,
        producer="test-component",
        event_name="OPERATION_MEASURED",
        execution=_execution(),
        measurements=(_measurement(),),
    )

    assert (
        record.record_family
        == OperationalRecordFamily.MEASUREMENT
    )


def test_record_is_immutable() -> None:
    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=_schema(),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="test-component",
        event_name="OPERATION_COMPLETED",
        execution=_execution(),
    )

    with pytest.raises(FrozenInstanceError):
        record.event_name = "OPERATION_FAILED"
