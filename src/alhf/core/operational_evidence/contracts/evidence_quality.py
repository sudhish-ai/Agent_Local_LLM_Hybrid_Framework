# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines universal quality semantics for ALHF Operational Evidence.
#
# Problem Solved:
# Failure analysis, root-cause analysis, predictive analysis, and
# corrective recommendations must know whether the Operational Evidence
# supporting their conclusions is complete and trustworthy.
#
# Missing, partial, degraded, or uncertain evidence must remain explicit
# so downstream intelligence does not mistake limited evidence for a
# complete execution history.
#
# Responsibilities:
# - Represent Operational Evidence completeness.
# - Represent Operational Evidence integrity.
# - Preserve unknown quality states without forcing false certainty.
# - Keep evidence quality separate from workload outcome semantics.
# - Provide immutable quality semantics for evidence consumers.
#
# Must Not:
# - Describe the success or failure of the observed workload.
# - Replace OperationalOutcome.
# - Perform evidence validation or integrity verification.
# - Infer missing evidence.
# - Perform failure analysis or root-cause analysis.
# - Compute analytical confidence.
# - Contain RAG or Knowledge-specific semantics.
# - Contain persistence, JSON, or JSONL behavior.
# - Contain storage-provider-specific integrity semantics.
# - Contain arbitrary metadata or diagnostic payloads.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Describes the quality of available Operational Evidence itself.
# - Independent from the outcome of the operation being observed.
#
# Reuse Value:
# - Knowledge Foundation failure analysis.
# - Multi-agent failure analysis.
# - V3 operational diagnostics.
# - Root-cause analysis.
# - Predictive reliability analysis.
# - Corrective-action recommendations.
# - Post-remediation validation.
#
# Future Extensibility:
# - Capture-policy semantics remain separate from evidence quality.
# - Detailed repository-health diagnostics remain separate.
# - Provider-specific integrity mechanisms remain behind provider
#   boundaries.
# - Analytical consumers may use this contract when determining whether
#   available evidence is sufficient for a conclusion.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceCompleteness(str, Enum):
    """Completeness of available Operational Evidence."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"


class EvidenceIntegrity(str, Enum):
    """Integrity state of available Operational Evidence."""

    INTACT = "INTACT"
    DEGRADED = "DEGRADED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class EvidenceQuality:
    """
    Immutable quality state of available Operational Evidence.

    completeness:
        Describes whether the required Operational Evidence is known to
        be complete, known to be partial, or cannot currently be
        determined.

    integrity:
        Describes whether available Operational Evidence is known to be
        intact, known to have an integrity degradation, or cannot
        currently be determined.

    Completeness and integrity are independent dimensions. Evidence may
    be complete but degraded, partial but intact, or unknown in either
    dimension.

    This contract records evidence-quality facts only. It does not decide
    whether those facts are sufficient for RCA, prediction, remediation,
    or another analytical conclusion.
    """

    completeness: EvidenceCompleteness
    integrity: EvidenceIntegrity

    def __post_init__(self) -> None:
        self._validate_type(
            value=self.completeness,
            expected_type=EvidenceCompleteness,
            field_name="completeness",
        )
        self._validate_type(
            value=self.integrity,
            expected_type=EvidenceIntegrity,
            field_name="integrity",
        )

    @property
    def is_complete(self) -> bool:
        """Return whether evidence is explicitly known to be complete."""

        return self.completeness == EvidenceCompleteness.COMPLETE

    @property
    def is_partial(self) -> bool:
        """Return whether evidence is explicitly known to be partial."""

        return self.completeness == EvidenceCompleteness.PARTIAL

    @property
    def is_intact(self) -> bool:
        """Return whether evidence is explicitly known to be intact."""

        return self.integrity == EvidenceIntegrity.INTACT

    @property
    def is_degraded(self) -> bool:
        """Return whether evidence integrity is explicitly degraded."""

        return self.integrity == EvidenceIntegrity.DEGRADED

    @property
    def has_unknown_quality(self) -> bool:
        """Return whether any evidence-quality dimension is unknown."""

        return (
            self.completeness == EvidenceCompleteness.UNKNOWN
            or self.integrity == EvidenceIntegrity.UNKNOWN
        )

    @staticmethod
    def _validate_type(
        *,
        value: object,
        expected_type: type[Enum],
        field_name: str,
    ) -> None:
        """Validate a required evidence-quality enum value."""

        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{field_name} must be an instance of "
                f"{expected_type.__name__}"
            )
