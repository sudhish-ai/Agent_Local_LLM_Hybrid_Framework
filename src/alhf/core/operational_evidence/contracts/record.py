# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal immutable record contract used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational evidence requires one stable record envelope that preserves
# identity, schema semantics, execution context, record classification,
# observed event semantics, outcomes, measurements, and relationships
# without coupling producers to logging or persistence technology.
#
# Responsibilities:
# - Identify one operational-evidence record.
# - Preserve the schema used to interpret the record.
# - Preserve the semantic family of the record.
# - Preserve the producer and event semantic.
# - Preserve execution and operation identity.
# - Preserve the observation timestamp.
# - Preserve an optional operational outcome.
# - Preserve immutable measurements and relationships.
# - Validate and normalize universal record fields.
#
# Must Not:
# - Contain RAG or Knowledge-specific semantics.
# - Contain workflow, task, or agent-specific semantics.
# - Infer root cause or causality.
# - Perform failure analysis.
# - Perform predictive analysis.
# - Recommend or execute corrective actions.
# - Generate record, execution, or operation identifiers.
# - Contain persistence, JSON, or JSONL behavior.
# - Contain logging or metrics-registry behavior.
# - Contain storage-provider locations.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence record contract.
# - Composes previously validated Operational Evidence contracts.
# - Independent from physical storage and analytical intelligence.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Failure analysis and RCA.
# - Reliability and predictive analysis.
# - Corrective-action traceability.
# - Post-remediation validation.
#
# Future Extensibility:
# - Subsystem-specific semantics remain outside this universal record.
# - Knowledge-specific facts are provided through separate governed
#   Knowledge Operational Evidence contracts.
# - Security and scope contracts can be composed without changing
#   persistence semantics.
# - Diagnostic artifacts remain separately governed.
# - Persistence providers serialize this contract without defining it.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.core.operational_evidence.contracts.measurement import (
    OperationalMeasurement,
)
from alhf.core.operational_evidence.contracts.outcome import (
    OperationalOutcome,
)
from alhf.core.operational_evidence.contracts.record_family import (
    OperationalRecordFamily,
)
from alhf.core.operational_evidence.contracts.relationship import (
    OperationalRelationship,
)
from alhf.core.operational_evidence.contracts.schema_identity import (
    SchemaIdentity,
)


@dataclass(frozen=True, slots=True)
class OperationalEvidenceRecord:
    """
    Immutable universal ALHF Operational Evidence record.

    record_id:
        Storage-independent identity of this evidence record.

    schema:
        Semantic schema identity used to interpret this record.

    record_family:
        Classifies what kind of governed record this represents.

    producer:
        Stable identity of the ALHF component that produced the record.

    event_name:
        Stable subsystem-defined semantic name for the observed event.

    execution:
        Execution and operation identity associated with the record.

    observed_at:
        UTC timestamp representing when the operational fact was observed.

    outcome:
        Optional multidimensional operational outcome.

    measurements:
        Immutable measurements directly associated with the record.

    relationships:
        Immutable explicit relationships associated with the record.

    This contract records universal operational facts and references only.
    Subsystem-specific semantics remain outside this common record.
    """

    record_id: str
    schema: SchemaIdentity
    record_family: OperationalRecordFamily
    producer: str
    event_name: str
    execution: ExecutionIdentity
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    outcome: OperationalOutcome | None = None
    measurements: tuple[OperationalMeasurement, ...] = ()
    relationships: tuple[OperationalRelationship, ...] = ()

    def __post_init__(self) -> None:
        record_id = self._normalize_required_text(
            value=self.record_id,
            field_name="record_id",
        )
        producer = self._normalize_required_text(
            value=self.producer,
            field_name="producer",
        )
        event_name = self._normalize_required_text(
            value=self.event_name,
            field_name="event_name",
        )

        self._validate_required_contract(
            value=self.schema,
            expected_type=SchemaIdentity,
            field_name="schema",
        )
        self._validate_required_contract(
            value=self.record_family,
            expected_type=OperationalRecordFamily,
            field_name="record_family",
        )
        self._validate_required_contract(
            value=self.execution,
            expected_type=ExecutionIdentity,
            field_name="execution",
        )

        if self.outcome is not None:
            self._validate_required_contract(
                value=self.outcome,
                expected_type=OperationalOutcome,
                field_name="outcome",
            )

        observed_at = self._validate_observed_at(
            value=self.observed_at,
        )
        measurements = self._validate_contract_tuple(
            values=self.measurements,
            expected_type=OperationalMeasurement,
            field_name="measurements",
        )
        relationships = self._validate_contract_tuple(
            values=self.relationships,
            expected_type=OperationalRelationship,
            field_name="relationships",
        )

        object.__setattr__(
            self,
            "record_id",
            record_id,
        )
        object.__setattr__(
            self,
            "producer",
            producer,
        )
        object.__setattr__(
            self,
            "event_name",
            event_name,
        )
        object.__setattr__(
            self,
            "observed_at",
            observed_at,
        )
        object.__setattr__(
            self,
            "measurements",
            measurements,
        )
        object.__setattr__(
            self,
            "relationships",
            relationships,
        )

    @staticmethod
    def _normalize_required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize a required text value."""

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized_value

    @staticmethod
    def _validate_required_contract(
        *,
        value: object,
        expected_type: type,
        field_name: str,
    ) -> None:
        """Validate a required composed contract."""

        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{field_name} must be an instance of "
                f"{expected_type.__name__}"
            )

    @staticmethod
    def _validate_observed_at(
        *,
        value: datetime,
    ) -> datetime:
        """Validate that observation time is timezone-aware."""

        if not isinstance(value, datetime):
            raise TypeError(
                "observed_at must be a datetime"
            )

        if (
            value.tzinfo is None
            or value.utcoffset() is None
        ):
            raise ValueError(
                "observed_at must be timezone-aware"
            )

        return value

    @staticmethod
    def _validate_contract_tuple(
        *,
        values: tuple,
        expected_type: type,
        field_name: str,
    ) -> tuple:
        """Validate an immutable tuple of composed contracts."""

        if not isinstance(values, tuple):
            raise TypeError(
                f"{field_name} must be a tuple"
            )

        for value in values:
            if not isinstance(
                value,
                expected_type,
            ):
                raise TypeError(
                    f"{field_name} must contain only "
                    f"{expected_type.__name__} instances"
                )

        return values
