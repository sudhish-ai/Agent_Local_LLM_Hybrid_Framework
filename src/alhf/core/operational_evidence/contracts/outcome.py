# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines universal operational outcome semantics for ALHF.
#
# Responsibilities:
# - Represent execution completion independently from quality.
# - Represent operational quality independently from failure cause.
# - Represent failure cause independently from retryability.
# - Represent retryability without forcing false certainty.
# - Represent operational criticality independently from severity.
# - Provide immutable outcome semantics for Operational Evidence.
#
# Must Not:
# - Replace or modify PipelineStatus.
# - Replace or modify PipelineResult.
# - Contain RAG or Knowledge-specific semantics.
# - Contain stage-specific event names.
# - Perform failure analysis or root-cause analysis.
# - Infer causality.
# - Contain persistence, JSON, or JSONL behavior.
# - Contain logging or metrics behavior.
# - Contain provider-specific failure semantics.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Additive to existing ALHF result and status contracts.
# - Used by future operational evidence records across ALHF.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Failure analysis and RCA.
# - Reliability and remediation validation.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CompletionState(str, Enum):
    """Completion state of an observed operation."""

    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    INCOMPLETE = "INCOMPLETE"
    NOT_STARTED = "NOT_STARTED"
    UNKNOWN = "UNKNOWN"


class QualityState(str, Enum):
    """Usability or quality state of an observed operation."""

    ACCEPTABLE = "ACCEPTABLE"
    DEGRADED = "DEGRADED"
    UNUSABLE = "UNUSABLE"
    NOT_ASSESSED = "NOT_ASSESSED"
    UNKNOWN = "UNKNOWN"


class FailureCause(str, Enum):
    """High-level cause classification for an operational failure."""

    INPUT = "INPUT"
    POLICY = "POLICY"
    CONFIGURATION = "CONFIGURATION"
    COMPATIBILITY = "COMPATIBILITY"
    DEPENDENCY = "DEPENDENCY"
    PROCESSING = "PROCESSING"
    INTEGRITY = "INTEGRITY"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    INTERNAL = "INTERNAL"
    UNKNOWN = "UNKNOWN"


class RetryDisposition(str, Enum):
    """Whether another attempt is currently justified."""

    RETRYABLE = "RETRYABLE"
    NOT_RETRYABLE = "NOT_RETRYABLE"
    UNKNOWN = "UNKNOWN"


class OperationalCriticality(str, Enum):
    """Importance of an operation to the enclosing execution."""

    OPTIONAL = "OPTIONAL"
    REQUIRED = "REQUIRED"
    MANDATORY = "MANDATORY"


@dataclass(frozen=True, slots=True)
class OperationalOutcome:
    """
    Immutable multidimensional outcome for an ALHF operation.

    Completion, quality, failure cause, retryability, and criticality are
    deliberately independent dimensions.

    failure_cause:
        None means no failure cause was reported for this outcome.

    retry_disposition:
        None means retry semantics are not applicable because no failure
        cause was reported.
    """

    completion: CompletionState
    quality: QualityState
    criticality: OperationalCriticality
    failure_cause: FailureCause | None = None
    retry_disposition: RetryDisposition | None = None

    def __post_init__(self) -> None:
        self._validate_type(
            value=self.completion,
            expected_type=CompletionState,
            field_name="completion",
        )
        self._validate_type(
            value=self.quality,
            expected_type=QualityState,
            field_name="quality",
        )
        self._validate_type(
            value=self.criticality,
            expected_type=OperationalCriticality,
            field_name="criticality",
        )

        if self.failure_cause is not None:
            self._validate_type(
                value=self.failure_cause,
                expected_type=FailureCause,
                field_name="failure_cause",
            )

        if self.retry_disposition is not None:
            self._validate_type(
                value=self.retry_disposition,
                expected_type=RetryDisposition,
                field_name="retry_disposition",
            )

        if (
            self.failure_cause is None
            and self.retry_disposition is not None
        ):
            raise ValueError(
                "retry_disposition requires failure_cause"
            )

        if (
            self.failure_cause is not None
            and self.retry_disposition is None
        ):
            raise ValueError(
                "failure_cause requires retry_disposition"
            )

    @property
    def has_failure(self) -> bool:
        """Return whether a failure cause is present."""

        return self.failure_cause is not None

    @property
    def is_complete(self) -> bool:
        """Return whether the operation completed fully."""

        return self.completion == CompletionState.COMPLETE

    @property
    def is_degraded(self) -> bool:
        """Return whether the operation completed with degraded quality."""

        return self.quality == QualityState.DEGRADED

    @staticmethod
    def _validate_type(
        *,
        value: object,
        expected_type: type[Enum],
        field_name: str,
    ) -> None:
        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{field_name} must be an instance of "
                f"{expected_type.__name__}"
            )
