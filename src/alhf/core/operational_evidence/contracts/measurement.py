# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the universal measurement contract used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational evidence requires measurements that remain interpretable
# across executions, providers, storage technologies, and historical
# analysis.
#
# A numeric value alone is insufficient for reliable failure analysis,
# trend analysis, predictive analysis, or remediation validation because
# its metric identity, unit, and measurement methodology may be ambiguous.
#
# Responsibilities:
# - Represent one immutable operational measurement.
# - Preserve a stable measurement identity.
# - Preserve an explicit numeric value.
# - Preserve an explicit unit.
# - Support optional methodology identity and methodology version.
# - Preserve enough semantic information for historical comparison.
#
# Must Not:
# - Aggregate measurements.
# - Calculate metrics.
# - Perform statistical analysis.
# - Perform predictive analysis.
# - Define RAG or Knowledge-specific metrics.
# - Define logging behavior.
# - Define persistence, JSON, or JSONL behavior.
# - Define sampling, retention, or storage policies.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Independent from the existing in-memory MetricsRegistry.
# - Provides historically interpretable measurements for operational
#   evidence and future reliability analysis.
#
# Reuse Value:
# - Knowledge Foundation operational measurements.
# - Multi-agent operational measurements.
# - V3 operational measurements.
# - Failure analysis and RCA.
# - Reliability trend analysis.
# - Predictive analysis.
# - Before-and-after remediation validation.
#
# Future Extensibility:
# - Subsystems define their own governed measurement identities.
# - Measurement aggregation remains a separate responsibility.
# - Sampling and capture-policy semantics remain separate.
# - Provider-specific metrics can map into this contract without defining
#   universal ALHF measurement semantics.

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class OperationalMeasurement:
    """
    Immutable measurement captured as operational evidence.

    measurement_id:
        Stable semantic identifier describing what was measured.

    value:
        Finite numeric value produced by the measurement.

    unit:
        Explicit unit used to interpret the numeric value.

    methodology_id:
        Optional stable identifier for the methodology used to produce
        the measurement.

    methodology_version:
        Optional version of the identified measurement methodology.

    Methodology identity and methodology version must either both be
    provided or both be absent.
    """

    measurement_id: str
    value: int | float
    unit: str
    methodology_id: str | None = None
    methodology_version: str | None = None

    def __post_init__(self) -> None:
        measurement_id = self._normalize_required_text(
            value=self.measurement_id,
            field_name="measurement_id",
        )
        unit = self._normalize_required_text(
            value=self.unit,
            field_name="unit",
        )
        methodology_id = self._normalize_optional_text(
            value=self.methodology_id,
            field_name="methodology_id",
        )
        methodology_version = self._normalize_optional_text(
            value=self.methodology_version,
            field_name="methodology_version",
        )

        self._validate_numeric_value(
            value=self.value,
        )
        self._validate_methodology_pair(
            methodology_id=methodology_id,
            methodology_version=methodology_version,
        )

        object.__setattr__(
            self,
            "measurement_id",
            measurement_id,
        )
        object.__setattr__(
            self,
            "unit",
            unit,
        )
        object.__setattr__(
            self,
            "methodology_id",
            methodology_id,
        )
        object.__setattr__(
            self,
            "methodology_version",
            methodology_version,
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
    def _normalize_optional_text(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        """Validate and normalize an optional text value."""

        if value is None:
            return None

        if not isinstance(value, str):
            raise TypeError(
                f"{field_name} must be a string or None"
            )

        normalized_value = value.strip()

        if not normalized_value:
            raise ValueError(
                f"{field_name} cannot be empty when provided"
            )

        return normalized_value

    @staticmethod
    def _validate_numeric_value(
        *,
        value: int | float,
    ) -> None:
        """Validate that a measurement contains a finite numeric value."""

        if isinstance(value, bool) or not isinstance(
            value,
            (int, float),
        ):
            raise TypeError(
                "value must be an int or float"
            )

        if not isfinite(value):
            raise ValueError(
                "value must be finite"
            )

    @staticmethod
    def _validate_methodology_pair(
        *,
        methodology_id: str | None,
        methodology_version: str | None,
    ) -> None:
        """
        Validate methodology identity and version consistency.

        Versioned methodology information is meaningful only when both
        identity and version are available.
        """

        if (
            methodology_id is None
            and methodology_version is not None
        ):
            raise ValueError(
                "methodology_version requires methodology_id"
            )

        if (
            methodology_id is not None
            and methodology_version is None
        ):
            raise ValueError(
                "methodology_id requires methodology_version"
            )
