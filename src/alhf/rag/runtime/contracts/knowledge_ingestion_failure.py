# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the immutable failure fact produced when processing one resource
# during ALHF Knowledge Foundation ingestion.
#
# Problem Solved:
# Production ingestion must represent resource-level processing failures
# independently from execution-policy decisions, Operational Evidence,
# exception implementations, and final aggregate ingestion results.
#
# Responsibilities:
# - Identify the resource and revision affected by a failure.
# - Preserve the governed Knowledge scope and source identity.
# - Identify the Knowledge ingestion stage that failed.
# - Preserve stable failure classification and retryability facts.
# - Preserve a bounded human-readable failure message.
# - Provide immutable input to ingestion execution-policy evaluation.
#
# Must Not:
# - Decide whether ingestion continues, stops, retries, or escalates.
# - Execute retry, recovery, quarantine, or remediation.
# - Contain exception objects or stack traces.
# - Contain Knowledge content or intermediate artifacts.
# - Duplicate Operational Evidence records.
# - Perform failure analysis or root-cause analysis.
# - Contain provider-specific or source-specific behavior.
#
# Architectural Position:
# - Knowledge-runtime failure-fact contract for resource processing.
# - Separates observed failure facts from execution-policy decisions.
# - Supports bounded aggregation without changing stage contracts.
#
# Future Extensibility:
# - Policy implementations can evolve independently from failure facts.
# - Retry and governance capabilities can consume this contract.
# - Distributed execution can report the same provider-neutral semantics.
# - Operational Evidence can observe decisions without owning them.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class KnowledgeIngestionStage(str, Enum):
    """Resource-processing stages capable of producing failure facts."""

    PARSING = "PARSING"
    NORMALIZATION = "NORMALIZATION"
    DERIVATION = "DERIVATION"
    REPRESENTATION = "REPRESENTATION"
    INDEXING = "INDEXING"


@dataclass(frozen=True, slots=True)
class KnowledgeIngestionFailure:
    """Immutable failure fact for one acquired Knowledge resource."""

    knowledge_scope_ref: str
    source_ref: str
    resource_ref: str
    revision_ref: str
    stage: KnowledgeIngestionStage
    error_code: str
    error_message: str
    retryable: bool

    def __post_init__(self) -> None:
        for field_name in (
            "knowledge_scope_ref",
            "source_ref",
            "resource_ref",
            "revision_ref",
            "error_code",
            "error_message",
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
            self.stage,
            KnowledgeIngestionStage,
        ):
            raise TypeError(
                "stage must be an instance of KnowledgeIngestionStage"
            )

        if not isinstance(
            self.retryable,
            bool,
        ):
            raise TypeError(
                "retryable must be a bool"
            )

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize one required failure value."""

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
