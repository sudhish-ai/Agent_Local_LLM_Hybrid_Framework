# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines bounded execution configuration for one ALHF Knowledge
# Foundation ingestion operation.
#
# Problem Solved:
# Production ingestion needs ALHF-owned execution bounds without exposing
# technical controls to normal runtime consumers or hard-coding them in
# KnowledgeIngestionService.
#
# Responsibilities:
# - Preserve one production execution identity.
# - Preserve the bounded acquisition resource limit.
# - Provide immutable validated execution configuration.
#
# Must Not:
# - Contain customer source location or credentials.
# - Select adapters, parsers, strategies, representations, or indexes.
# - Contain provider-specific configuration.
# - Execute ingestion, retry, recovery, or Operational Evidence.
#
# Architectural Position:
# - Internal resolved execution input consumed by KnowledgeIngestionService.
# - Produced above ingestion execution by runtime composition.
#
# Future Extensibility:
# - Profiles and execution intelligence may resolve these values.
# - Additional proven universal execution controls can evolve separately.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KnowledgeIngestionExecutionConfig:
    """Immutable resolved configuration for one ingestion execution."""

    execution_id: str
    max_resources: int

    def __post_init__(self) -> None:
        normalized_execution_id = self._required_text(
            value=self.execution_id,
            field_name="execution_id",
        )

        object.__setattr__(
            self,
            "execution_id",
            normalized_execution_id,
        )

        self._positive_int(
            value=self.max_resources,
            field_name="max_resources",
        )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
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

    @staticmethod
    def _positive_int(
        *,
        value: int,
        field_name: str,
    ) -> None:
        if isinstance(
            value,
            bool,
        ) or not isinstance(
            value,
            int,
        ):
            raise TypeError(
                f"{field_name} must be an int"
            )

        if value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero"
            )
