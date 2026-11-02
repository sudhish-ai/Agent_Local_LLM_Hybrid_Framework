# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines universal capture-policy semantics used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational Evidence may be captured at different levels of detail
# for scalability, diagnostics, evaluation, and reliability.
#
# Historical analysis must be able to distinguish exhaustive capture
# from aggregated, sampled, bounded, or selectively detailed evidence.
# Otherwise changes in capture behavior could be mistaken for changes
# in the system being observed.
#
# Responsibilities:
# - Identify the policy used to capture Operational Evidence.
# - Preserve an explicit capture-policy version.
# - Represent the completeness model of captured evidence.
# - Represent the configured evidence-detail level.
# - Preserve whether abnormal conditions receive additional detail.
# - Provide immutable, storage-independent capture semantics.
#
# Must Not:
# - Perform sampling.
# - Perform aggregation.
# - Perform buffering or batching.
# - Define retention or durability policy.
# - Determine Operational Evidence quality or integrity.
# - Replace EvidenceQuality.
# - Contain RAG or Knowledge-specific semantics.
# - Contain provider-specific configuration.
# - Contain persistence, JSON, or JSONL behavior.
# - Contain arbitrary metadata or payload dictionaries.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Describes how evidence was captured without implementing capture.
# - Independent from evidence quality, persistence, and storage providers.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Failure analysis and RCA.
# - Reliability trend analysis.
# - Predictive analysis.
# - Performance and storage optimization.
#
# Future Extensibility:
# - Concrete capture behavior remains configurable outside this contract.
# - Sampling methodology can be referenced separately when required.
# - Aggregation methodology remains separately versioned.
# - Provider-specific capture mechanisms remain behind provider
#   boundaries.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CaptureCompleteness(str, Enum):
    """Declared completeness model of captured Operational Evidence."""

    EXHAUSTIVE = "EXHAUSTIVE"
    AGGREGATED = "AGGREGATED"
    SAMPLED = "SAMPLED"
    SELECTIVE = "SELECTIVE"
    BOUNDED = "BOUNDED"


class CaptureDetailLevel(str, Enum):
    """Configured detail level of Operational Evidence capture."""

    BASELINE = "BASELINE"
    DETAILED = "DETAILED"
    DIAGNOSTIC = "DIAGNOSTIC"


@dataclass(frozen=True, slots=True)
class CapturePolicy:
    """
    Immutable description of Operational Evidence capture policy.

    policy_id:
        Stable identifier of the capture policy.

    policy_version:
        Explicit version of the capture policy.

    completeness:
        Describes whether evidence capture is exhaustive, aggregated,
        sampled, selective, or bounded.

    detail_level:
        Describes the configured level of evidence detail.

    abnormal_detail_enabled:
        Indicates whether known abnormal conditions are configured to
        preserve additional detail beyond the normal capture level.

    This contract describes capture behavior only. It does not perform
    capture or establish whether the resulting evidence is complete,
    intact, sufficient, or trustworthy for a particular analysis.
    """

    policy_id: str
    policy_version: str
    completeness: CaptureCompleteness
    detail_level: CaptureDetailLevel
    abnormal_detail_enabled: bool

    def __post_init__(self) -> None:
        policy_id = self._normalize_required_text(
            value=self.policy_id,
            field_name="policy_id",
        )
        policy_version = self._normalize_required_text(
            value=self.policy_version,
            field_name="policy_version",
        )

        self._validate_enum(
            value=self.completeness,
            expected_type=CaptureCompleteness,
            field_name="completeness",
        )
        self._validate_enum(
            value=self.detail_level,
            expected_type=CaptureDetailLevel,
            field_name="detail_level",
        )

        if not isinstance(
            self.abnormal_detail_enabled,
            bool,
        ):
            raise TypeError(
                "abnormal_detail_enabled must be a bool"
            )

        object.__setattr__(
            self,
            "policy_id",
            policy_id,
        )
        object.__setattr__(
            self,
            "policy_version",
            policy_version,
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
    def _validate_enum(
        *,
        value: object,
        expected_type: type[Enum],
        field_name: str,
    ) -> None:
        """Validate a required capture-policy enum value."""

        if not isinstance(
            value,
            expected_type,
        ):
            raise TypeError(
                f"{field_name} must be an instance of "
                f"{expected_type.__name__}"
            )
