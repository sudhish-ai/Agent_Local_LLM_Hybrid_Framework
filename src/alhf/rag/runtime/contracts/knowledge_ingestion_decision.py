# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the immutable execution decision returned by ALHF Knowledge
# ingestion policy after evaluating a resource-level failure.
#
# Problem Solved:
# Production ingestion must not hard-code whether resource-processing
# failures cause execution to continue or stop. That decision belongs
# behind a replaceable Knowledge ingestion policy boundary.
#
# Responsibilities:
# - Represent an executable ingestion-policy action.
# - Preserve a stable reason explaining the policy decision.
# - Keep policy evaluation separate from ingestion orchestration.
# - Provide immutable provider-neutral decision semantics.
#
# Must Not:
# - Evaluate Knowledge ingestion failures.
# - Execute continuation, termination, retry, or recovery.
# - Contain exception objects or stack traces.
# - Contain Knowledge content or intermediate artifacts.
# - Perform Operational Evidence emission.
# - Perform failure analysis or root-cause analysis.
# - Contain source-specific or provider-specific behavior.
#
# Architectural Position:
# - Stable decision contract between ingestion policy and orchestration.
# - Consumed by Knowledge ingestion execution after policy evaluation.
# - Separates execution decisions from failure facts and final results.
#
# Future Extensibility:
# - More capable policy implementations can reuse this decision boundary.
# - Retry and governance execution can compose through additive runtime
#   capabilities without embedding policy inside ingestion orchestration.
# - Profile and Knowledge Intelligence can evolve behind policy boundaries.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KnowledgeIngestionAction(str, Enum):
    """Actions currently executable by Knowledge ingestion orchestration."""

    CONTINUE = "CONTINUE"
    STOP = "STOP"


@dataclass(frozen=True, slots=True)
class KnowledgeIngestionDecision:
    """Immutable execution decision produced by ingestion policy."""

    action: KnowledgeIngestionAction
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.action,
            KnowledgeIngestionAction,
        ):
            raise TypeError(
                "action must be an instance of KnowledgeIngestionAction"
            )

        normalized_reason = self._required_text(
            value=self.reason,
            field_name="reason",
        )

        object.__setattr__(
            self,
            "reason",
            normalized_reason,
        )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize one required decision value."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
