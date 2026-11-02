# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the immutable execution identity contract used by the
# ALHF Operational Evidence Foundation.
#
# Problem Solved:
# Operational evidence must distinguish broader correlation from a concrete
# execution and from individual operations inside that execution.
# Reusing one identifier for all of these responsibilities would make
# execution reconstruction, failure analysis, root-cause analysis, and
# future remediation validation ambiguous.
#
# Responsibilities:
# - Preserve the broader ALHF correlation identifier.
# - Identify one concrete ALHF execution instance.
# - Identify one concrete operation within that execution.
# - Represent the immediate parent operation when one exists.
# - Provide a universal identity foundation for operational evidence.
#
# Must Not:
# - Generate identifiers.
# - Treat correlation identity as execution or operation identity.
# - Treat execution hierarchy as diagnosed causality.
# - Contain RAG or Knowledge-specific semantics.
# - Contain workflow, task, or agent-specific semantics.
# - Contain event, outcome, failure, or measurement semantics.
# - Contain timestamps or ordering semantics.
# - Contain arbitrary metadata or payload dictionaries.
# - Contain persistence, JSON, or JSONL logic.
# - Contain business or orchestration logic.
#
# Architectural Position:
# - Universal ALHF Operational Evidence contract.
# - Foundational identity context for future operational evidence records.
# - Independent from logging, metrics, storage, and analytical intelligence.
#
# Reuse Value:
# - Knowledge Foundation operational evidence.
# - Multi-agent operational evidence.
# - V3 operational evidence.
# - Future ALHF execution and reliability capabilities.
#
# Future Extensibility:
# - Operational evidence record identity is modeled separately.
# - Cross-execution relationships are modeled separately.
# - Diagnosed causal relationships are modeled separately from execution
#   hierarchy.
# - Knowledge-specific identity is provided through governed Knowledge
#   Operational Evidence extensions.
# - Persistence providers remain independent from these identity semantics.
#

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionIdentity:
    """
    Immutable identity context for one ALHF operation.

    correlation_id:
        Identifies the broader correlated request or activity.

    execution_id:
        Identifies one concrete ALHF execution instance.

    operation_id:
        Identifies one concrete operation within the execution.

    parent_operation_id:
        Identifies the immediate parent operation when one exists.
        Root operations have no parent operation.

    This contract deliberately contains identity semantics only.
    Identifier generation, persistence, operational outcomes, Knowledge
    identity, causal analysis, and execution intelligence are separate
    responsibilities.
    """

    correlation_id: str
    execution_id: str
    operation_id: str
    parent_operation_id: str | None = None

    def __post_init__(self) -> None:
        correlation_id = self._normalize_required_identifier(
            value=self.correlation_id,
            field_name="correlation_id",
        )
        execution_id = self._normalize_required_identifier(
            value=self.execution_id,
            field_name="execution_id",
        )
        operation_id = self._normalize_required_identifier(
            value=self.operation_id,
            field_name="operation_id",
        )
        parent_operation_id = self._normalize_optional_identifier(
            value=self.parent_operation_id,
            field_name="parent_operation_id",
        )

        if parent_operation_id == operation_id:
            raise ValueError(
                "parent_operation_id cannot equal operation_id"
            )

        object.__setattr__(
            self,
            "correlation_id",
            correlation_id,
        )
        object.__setattr__(
            self,
            "execution_id",
            execution_id,
        )
        object.__setattr__(
            self,
            "operation_id",
            operation_id,
        )
        object.__setattr__(
            self,
            "parent_operation_id",
            parent_operation_id,
        )

    @staticmethod
    def _normalize_required_identifier(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """
        Validate and normalize a required identity value.

        Required identifiers must be strings containing at least one
        non-whitespace character.
        """

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
    def _normalize_optional_identifier(
        *,
        value: str | None,
        field_name: str,
    ) -> str | None:
        """
        Validate and normalize an optional identity value.

        None represents the legitimate absence of a parent operation.
        When an optional identifier is supplied, it must contain at least
        one non-whitespace character.
        """

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
