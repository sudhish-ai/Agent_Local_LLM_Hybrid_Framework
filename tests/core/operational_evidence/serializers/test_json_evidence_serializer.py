# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF JsonEvidenceSerializer.
#
# Responsibilities:
# - Validate Operational Evidence record serialization.
# - Validate deterministic JSON output.
# - Validate nested Operational Evidence contract serialization.
# - Validate enum serialization using stable values.
# - Validate datetime serialization using ISO 8601.
# - Validate tuple serialization using JSON-compatible lists.
# - Validate supported primitive values.
# - Validate mapping serialization.
# - Validate invalid record rejection.
# - Validate unsupported-value rejection.
# - Validate invalid mapping-key rejection.
#
# Must Not:
# - Test JSONL persistence.
# - Test filesystem behavior.
# - Test evidence repositories.
# - Test RAG or Knowledge-specific semantics.
# - Test failure analysis or root-cause analysis.
# - Test identifier generation.

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

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
from alhf.core.operational_evidence.serializers.json_evidence_serializer import (
    JsonEvidenceSerializer,
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
            parent_operation_id="operation-root",
        ),
        observed_at=datetime(
            2026,
            10,
            27,
            12,
            30,
            45,
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
                source_ref="operation-001",
                target_ref="operation-root",
                relationship_type=RelationshipType.DEPENDS_ON,
            ),
        ),
    )


def test_to_dict_returns_dictionary() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert isinstance(
        serialized,
        dict,
    )


def test_to_dict_preserves_record_identity() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert serialized["record_id"] == "record-001"


def test_to_dict_serializes_schema_identity() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert serialized["schema"] == {
        "schema_id": "operational-evidence-record",
        "schema_version": "1.0",
    }


def test_to_dict_serializes_record_family_value() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert (
        serialized["record_family"]
        == "OPERATIONAL_EVENT"
    )


def test_to_dict_preserves_producer_and_event_name() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert serialized["producer"] == "test-component"
    assert serialized["event_name"] == "OPERATION_COMPLETED"


def test_to_dict_serializes_execution_identity() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert serialized["execution"] == {
        "correlation_id": "correlation-001",
        "execution_id": "execution-001",
        "operation_id": "operation-001",
        "parent_operation_id": "operation-root",
    }


def test_to_dict_serializes_datetime_using_iso_8601() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert (
        serialized["observed_at"]
        == "2026-10-27T12:30:45+00:00"
    )


def test_to_dict_serializes_operational_outcome() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert serialized["outcome"] == {
        "completion": "COMPLETE",
        "quality": "ACCEPTABLE",
        "criticality": "REQUIRED",
        "failure_cause": None,
        "retry_disposition": None,
    }


def test_to_dict_serializes_measurements_as_list() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert serialized["measurements"] == [
        {
            "measurement_id": "operation_duration",
            "value": 125.5,
            "unit": "milliseconds",
            "methodology_id": None,
            "methodology_version": None,
        }
    ]


def test_to_dict_serializes_relationships_as_list() -> None:
    serialized = JsonEvidenceSerializer.to_dict(
        _record()
    )

    assert serialized["relationships"] == [
        {
            "source_ref": "operation-001",
            "target_ref": "operation-root",
            "relationship_type": "DEPENDS_ON",
        }
    ]


def test_to_json_returns_string() -> None:
    serialized = JsonEvidenceSerializer.to_json(
        _record()
    )

    assert isinstance(
        serialized,
        str,
    )


def test_to_json_produces_valid_json() -> None:
    serialized = JsonEvidenceSerializer.to_json(
        _record()
    )

    decoded = json.loads(serialized)

    assert decoded["record_id"] == "record-001"
    assert decoded["producer"] == "test-component"


def test_to_json_matches_to_dict_semantics() -> None:
    record = _record()

    serialized_json = JsonEvidenceSerializer.to_json(
        record
    )
    serialized_dict = JsonEvidenceSerializer.to_dict(
        record
    )

    assert json.loads(serialized_json) == serialized_dict


def test_to_json_is_deterministic() -> None:
    record = _record()

    first_serialization = JsonEvidenceSerializer.to_json(
        record
    )
    second_serialization = JsonEvidenceSerializer.to_json(
        record
    )

    assert first_serialization == second_serialization


def test_to_json_uses_compact_separators() -> None:
    serialized = JsonEvidenceSerializer.to_json(
        _record()
    )

    assert ": " not in serialized
    assert ", " not in serialized


def test_to_json_keeps_unicode_content() -> None:
    record = OperationalEvidenceRecord(
        record_id="record-001",
        schema=SchemaIdentity(
            schema_id="operational-evidence-record",
            schema_version="1.0",
        ),
        record_family=OperationalRecordFamily.OPERATIONAL_EVENT,
        producer="component-भारत",
        event_name="OPERATION_COMPLETED",
        execution=ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
        ),
    )

    serialized = JsonEvidenceSerializer.to_json(
        record
    )

    assert "भारत" in serialized


def test_to_dict_rejects_non_record_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "record must be an instance of "
            "OperationalEvidenceRecord"
        ),
    ):
        JsonEvidenceSerializer.to_dict(
            "not-a-record"
        )


def test_to_json_rejects_non_record_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "record must be an instance of "
            "OperationalEvidenceRecord"
        ),
    ):
        JsonEvidenceSerializer.to_json(
            "not-a-record"
        )


def test_serialize_value_supports_none() -> None:
    assert (
        JsonEvidenceSerializer._serialize_value(None)
        is None
    )


def test_serialize_value_supports_boolean() -> None:
    assert (
        JsonEvidenceSerializer._serialize_value(True)
        is True
    )
    assert (
        JsonEvidenceSerializer._serialize_value(False)
        is False
    )


def test_serialize_value_supports_string() -> None:
    assert (
        JsonEvidenceSerializer._serialize_value(
            "value"
        )
        == "value"
    )


def test_serialize_value_supports_integer() -> None:
    assert (
        JsonEvidenceSerializer._serialize_value(
            42
        )
        == 42
    )


def test_serialize_value_supports_float() -> None:
    assert (
        JsonEvidenceSerializer._serialize_value(
            42.5
        )
        == 42.5
    )


def test_serialize_value_supports_enum() -> None:
    assert (
        JsonEvidenceSerializer._serialize_value(
            OperationalRecordFamily.MEASUREMENT
        )
        == "MEASUREMENT"
    )


def test_serialize_value_supports_datetime() -> None:
    value = datetime(
        2026,
        10,
        27,
        12,
        30,
        tzinfo=timezone.utc,
    )

    assert (
        JsonEvidenceSerializer._serialize_value(
            value
        )
        == "2026-10-27T12:30:00+00:00"
    )


def test_serialize_value_supports_tuple() -> None:
    serialized = JsonEvidenceSerializer._serialize_value(
        (
            "first",
            2,
            True,
        )
    )

    assert serialized == [
        "first",
        2,
        True,
    ]


def test_serialize_value_supports_list() -> None:
    serialized = JsonEvidenceSerializer._serialize_value(
        [
            "first",
            2,
            False,
        ]
    )

    assert serialized == [
        "first",
        2,
        False,
    ]


def test_serialize_value_supports_string_keyed_mapping() -> None:
    serialized = JsonEvidenceSerializer._serialize_value(
        {
            "name": "value",
            "count": 2,
        }
    )

    assert serialized == {
        "name": "value",
        "count": 2,
    }


def test_mapping_rejects_non_string_key() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "Operational Evidence JSON mapping keys "
            "must be strings"
        ),
    ):
        JsonEvidenceSerializer._serialize_value(
            {
                1: "value",
            }
        )


class UnsupportedValue:
    pass


def test_serialize_value_rejects_unsupported_type() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "unsupported value type for Operational Evidence "
            "JSON serialization: UnsupportedValue"
        ),
    ):
        JsonEvidenceSerializer._serialize_value(
            UnsupportedValue()
        )


class ExampleEnum(str, Enum):
    VALUE = "VALUE"


@dataclass(frozen=True)
class NestedContract:
    name: str
    status: ExampleEnum
    values: tuple[int, ...]


def test_serialize_value_recursively_serializes_dataclass() -> None:
    value = NestedContract(
        name="example",
        status=ExampleEnum.VALUE,
        values=(
            1,
            2,
            3,
        ),
    )

    serialized = JsonEvidenceSerializer._serialize_value(
        value
    )

    assert serialized == {
        "name": "example",
        "status": "VALUE",
        "values": [
            1,
            2,
            3,
        ],
    }
