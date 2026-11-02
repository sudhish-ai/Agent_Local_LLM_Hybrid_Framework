# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Reconstructs validated ALHF Operational Evidence records from decoded
# JSON-compatible mappings used by the local JSONL provider.
#
# Responsibilities:
# - Decode one mapping into OperationalEvidenceRecord.
# - Reconstruct validated nested universal evidence contracts.
# - Reconstruct enum values through their governed contract types.
# - Parse observation timestamps from ISO 8601 strings.
# - Reject malformed or structurally invalid record representations.
#
# Must Not:
# - Read JSONL files.
# - Discover or select physical partitions.
# - Perform repository queries.
# - Persist Operational Evidence.
# - Perform failure analysis or root-cause analysis.
# - Contain RAG or Knowledge-specific semantics.
# - Silently repair malformed evidence.
# - Expose filesystem or provider locations.
#
# Architectural Position:
# - Local JSONL provider decoding component.
# - Separates contract reconstruction from physical JSONL reading.
# - Produces validated universal Operational Evidence records.
#
# Future Extensibility:
# - Schema migration remains a separate responsibility.
# - Compatibility handling remains a separate responsibility.
# - Alternative persistence providers can use independent decoders.

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.measurement import (
    OperationalMeasurement,
)
from alhf.core.operational_evidence.contracts.outcome import (
    CompletionState,
    FailureCause,
    OperationalCriticality,
    OperationalOutcome,
    QualityState,
    RetryDisposition,
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


class JsonlRecordDecoder:
    """Decode JSON-compatible mappings into validated evidence records."""

    @classmethod
    def decode(
        cls,
        data: Mapping[str, Any],
    ) -> OperationalEvidenceRecord:
        """Decode one Operational Evidence record."""

        if not isinstance(data, Mapping):
            raise TypeError(
                "data must be a mapping"
            )

        return OperationalEvidenceRecord(
            record_id=cls._required(data, "record_id"),
            schema=cls._decode_schema(
                cls._mapping(data, "schema")
            ),
            record_family=OperationalRecordFamily(
                cls._required(data, "record_family")
            ),
            producer=cls._required(data, "producer"),
            event_name=cls._required(data, "event_name"),
            execution=cls._decode_execution(
                cls._mapping(data, "execution")
            ),
            observed_at=cls._decode_datetime(
                cls._required(data, "observed_at")
            ),
            outcome=cls._decode_outcome(
                data.get("outcome")
            ),
            measurements=tuple(
                cls._decode_measurement(item)
                for item in cls._sequence(data, "measurements")
            ),
            relationships=tuple(
                cls._decode_relationship(item)
                for item in cls._sequence(data, "relationships")
            ),
        )

    @staticmethod
    def _decode_schema(
        data: Mapping[str, Any],
    ) -> SchemaIdentity:
        return SchemaIdentity(
            schema_id=JsonlRecordDecoder._required(
                data,
                "schema_id",
            ),
            schema_version=JsonlRecordDecoder._required(
                data,
                "schema_version",
            ),
        )

    @staticmethod
    def _decode_execution(
        data: Mapping[str, Any],
    ) -> ExecutionIdentity:
        return ExecutionIdentity(
            correlation_id=JsonlRecordDecoder._required(
                data,
                "correlation_id",
            ),
            execution_id=JsonlRecordDecoder._required(
                data,
                "execution_id",
            ),
            operation_id=JsonlRecordDecoder._required(
                data,
                "operation_id",
            ),
            parent_operation_id=data.get(
                "parent_operation_id"
            ),
        )

    @staticmethod
    def _decode_outcome(
        value: object,
    ) -> OperationalOutcome | None:
        if value is None:
            return None

        if not isinstance(value, Mapping):
            raise TypeError(
                "outcome must be a mapping or None"
            )

        failure_cause = value.get("failure_cause")
        retry_disposition = value.get("retry_disposition")

        return OperationalOutcome(
            completion=CompletionState(
                JsonlRecordDecoder._required(
                    value,
                    "completion",
                )
            ),
            quality=QualityState(
                JsonlRecordDecoder._required(
                    value,
                    "quality",
                )
            ),
            criticality=OperationalCriticality(
                JsonlRecordDecoder._required(
                    value,
                    "criticality",
                )
            ),
            failure_cause=(
                FailureCause(failure_cause)
                if failure_cause is not None
                else None
            ),
            retry_disposition=(
                RetryDisposition(retry_disposition)
                if retry_disposition is not None
                else None
            ),
        )

    @staticmethod
    def _decode_measurement(
        value: object,
    ) -> OperationalMeasurement:
        if not isinstance(value, Mapping):
            raise TypeError(
                "measurement must be a mapping"
            )

        return OperationalMeasurement(
            measurement_id=JsonlRecordDecoder._required(
                value,
                "measurement_id",
            ),
            value=JsonlRecordDecoder._required(
                value,
                "value",
            ),
            unit=JsonlRecordDecoder._required(
                value,
                "unit",
            ),
            methodology_id=value.get("methodology_id"),
            methodology_version=value.get(
                "methodology_version"
            ),
        )

    @staticmethod
    def _decode_relationship(
        value: object,
    ) -> OperationalRelationship:
        if not isinstance(value, Mapping):
            raise TypeError(
                "relationship must be a mapping"
            )

        return OperationalRelationship(
            source_ref=JsonlRecordDecoder._required(
                value,
                "source_ref",
            ),
            target_ref=JsonlRecordDecoder._required(
                value,
                "target_ref",
            ),
            relationship_type=RelationshipType(
                JsonlRecordDecoder._required(
                    value,
                    "relationship_type",
                )
            ),
        )

    @staticmethod
    def _decode_datetime(
        value: object,
    ) -> datetime:
        if not isinstance(value, str):
            raise TypeError(
                "observed_at must be an ISO 8601 string"
            )

        return datetime.fromisoformat(value)

    @staticmethod
    def _required(
        data: Mapping[str, Any],
        field_name: str,
    ) -> Any:
        if field_name not in data:
            raise ValueError(
                f"missing required field: {field_name}"
            )

        return data[field_name]

    @staticmethod
    def _mapping(
        data: Mapping[str, Any],
        field_name: str,
    ) -> Mapping[str, Any]:
        value = JsonlRecordDecoder._required(
            data,
            field_name,
        )

        if not isinstance(value, Mapping):
            raise TypeError(
                f"{field_name} must be a mapping"
            )

        return value

    @staticmethod
    def _sequence(
        data: Mapping[str, Any],
        field_name: str,
    ) -> list[Any] | tuple[Any, ...]:
        value = JsonlRecordDecoder._required(
            data,
            field_name,
        )

        if not isinstance(value, (list, tuple)):
            raise TypeError(
                f"{field_name} must be a list or tuple"
            )

        return value
