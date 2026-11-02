# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF EvidenceSerializer interface.
#
# Responsibilities:
# - Validate that EvidenceSerializer is an abstract contract.
# - Validate serialization of Operational Evidence records.
# - Validate deserialization into Operational Evidence records.
# - Validate bytes as the serialization boundary.
# - Validate round-trip record preservation.
# - Protect serialization-format independence.
#
# Must Not:
# - Test JSON or JSONL serialization.
# - Test filesystem or database behavior.
# - Test physical persistence.
# - Test schema migration or compatibility policy.
# - Test RAG or Knowledge-specific semantics.
# - Test buffering, batching, retry, or retention behavior.

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
from alhf.core.operational_evidence.interfaces.evidence_serializer import (
    EvidenceSerializer,
)


class StubEvidenceSerializer(EvidenceSerializer):
    """Minimal serializer used to validate the interface contract."""

    def __init__(
        self,
        record: OperationalEvidenceRecord,
    ) -> None:
        self._record = record
        self.serialized_record: OperationalEvidenceRecord | None = None
        self.deserialized_payload: bytes | None = None

    def serialize(
        self,
        record: OperationalEvidenceRecord,
    ) -> bytes:
        self.serialized_record = record

        return b"encoded-operational-evidence"

    def deserialize(
        self,
        payload: bytes,
    ) -> OperationalEvidenceRecord:
        self.deserialized_payload = payload

        return self._record


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


def test_evidence_serializer_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        EvidenceSerializer()


def test_concrete_serializer_can_be_instantiated() -> None:
    record = _record()

    serializer = StubEvidenceSerializer(
        record=record,
    )

    assert isinstance(
        serializer,
        EvidenceSerializer,
    )


def test_serialize_accepts_operational_evidence_record() -> None:
    record = _record()
    serializer = StubEvidenceSerializer(
        record=record,
    )

    serializer.serialize(record)

    assert serializer.serialized_record is record


def test_serialize_returns_bytes() -> None:
    record = _record()
    serializer = StubEvidenceSerializer(
        record=record,
    )

    payload = serializer.serialize(record)

    assert isinstance(
        payload,
        bytes,
    )


def test_deserialize_accepts_bytes() -> None:
    record = _record()
    serializer = StubEvidenceSerializer(
        record=record,
    )
    payload = b"encoded-operational-evidence"

    result = serializer.deserialize(payload)

    assert serializer.deserialized_payload == payload
    assert result is record


def test_deserialize_returns_operational_evidence_record() -> None:
    record = _record()
    serializer = StubEvidenceSerializer(
        record=record,
    )

    result = serializer.deserialize(
        b"encoded-operational-evidence",
    )

    assert isinstance(
        result,
        OperationalEvidenceRecord,
    )


def test_deserialize_preserves_record_identity() -> None:
    record = _record()
    serializer = StubEvidenceSerializer(
        record=record,
    )

    result = serializer.deserialize(
        b"encoded-operational-evidence",
    )

    assert result.record_id == record.record_id


def test_serializer_supports_round_trip_contract() -> None:
    record = _record()
    serializer = StubEvidenceSerializer(
        record=record,
    )

    payload = serializer.serialize(record)
    restored_record = serializer.deserialize(payload)

    assert restored_record == record


class MissingSerializeEvidenceSerializer(EvidenceSerializer):
    """Invalid serializer missing serialization implementation."""

    def deserialize(
        self,
        payload: bytes,
    ) -> OperationalEvidenceRecord:
        return _record()


def test_serializer_missing_serialize_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingSerializeEvidenceSerializer()


class MissingDeserializeEvidenceSerializer(EvidenceSerializer):
    """Invalid serializer missing deserialization implementation."""

    def serialize(
        self,
        record: OperationalEvidenceRecord,
    ) -> bytes:
        return b"encoded-operational-evidence"


def test_serializer_missing_deserialize_cannot_instantiate() -> None:
    with pytest.raises(TypeError):
        MissingDeserializeEvidenceSerializer()
