# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the bounded production result of one ALHF Knowledge Foundation
# ingestion execution.
#
# Problem Solved:
# Production ingestion requires a stable terminal result without exposing
# internal parsers, strategies, providers, indexes, intermediate artifacts,
# or unbounded collections to runtime consumers.
#
# Responsibilities:
# - Preserve production execution identity.
# - Preserve Knowledge scope and logical source identity.
# - Declare the governed terminal ingestion status.
# - Preserve bounded aggregate stage counts.
# - Support partial and failed production executions.
# - Remain independent from concrete ingestion technologies.
#
# Must Not:
# - Contain Knowledge content or intermediate artifacts.
# - Contain file paths, URLs, credentials, or provider configuration.
# - Expose parser, derivation, representation, or index implementations.
# - Assume one derivation produces exactly one representation.
# - Assume one representation targets exactly one future index.
# - Contain Standard RAG, GraphRAG, or Agentic RAG semantics.
# - Perform execution, retry, recovery, or Operational Evidence emission.
#
# Architectural Position:
# - Stable production outcome contract of the ingestion plane.
# - Returned through the Knowledge Foundation runtime boundary.
# - Correlates with Operational Evidence through execution identity.
#
# Future Extensibility:
# - Multiple derivation and representation workflows remain compatible.
# - Graph, multimodal, and future Knowledge artifacts can fan out.
# - Durable lifecycle and continuation remain separate capabilities.
# - Runtime diagnostics remain queryable through Operational Evidence.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KnowledgeIngestionStatus(str, Enum):
    """Terminal status of one production ingestion execution."""

    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class KnowledgeIngestionResult:
    """Bounded terminal result of one Knowledge ingestion execution."""

    execution_id: str
    knowledge_scope_ref: str
    source_ref: str
    status: KnowledgeIngestionStatus
    acquired_count: int = 0
    parsed_count: int = 0
    normalized_count: int = 0
    derived_count: int = 0
    represented_count: int = 0
    indexed_count: int = 0
    failed_resource_count: int = 0

    def __post_init__(self) -> None:
        for field_name in (
            "execution_id",
            "knowledge_scope_ref",
            "source_ref",
        ):
            normalized = self._required_text(
                value=getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )

            object.__setattr__(
                self,
                field_name,
                normalized,
            )

        if not isinstance(
            self.status,
            KnowledgeIngestionStatus,
        ):
            raise TypeError(
                "status must be an instance of "
                "KnowledgeIngestionStatus"
            )

        count_fields = (
            "acquired_count",
            "parsed_count",
            "normalized_count",
            "derived_count",
            "represented_count",
            "indexed_count",
            "failed_resource_count",
        )

        for field_name in count_fields:
            self._non_negative_int(
                value=getattr(
                    self,
                    field_name,
                ),
                field_name=field_name,
            )

        if self.parsed_count > self.acquired_count:
            raise ValueError(
                "parsed_count cannot exceed acquired_count"
            )

        if self.normalized_count > self.parsed_count:
            raise ValueError(
                "normalized_count cannot exceed parsed_count"
            )

        if self.failed_resource_count > self.acquired_count:
            raise ValueError(
                "failed_resource_count cannot exceed acquired_count"
            )

        if (
            self.status == KnowledgeIngestionStatus.COMPLETED
            and self.failed_resource_count != 0
        ):
            raise ValueError(
                "completed ingestion cannot contain failed resources"
            )

        if (
            self.status == KnowledgeIngestionStatus.FAILED
            and self.acquired_count == 0
            and self.failed_resource_count != 0
        ):
            raise ValueError(
                "failed_resource_count requires an acquired resource"
            )

    @staticmethod
    def _non_negative_int(
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

        if value < 0:
            raise ValueError(
                f"{field_name} cannot be negative"
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
