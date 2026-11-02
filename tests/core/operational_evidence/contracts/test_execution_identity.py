# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the universal ALHF ExecutionIdentity contract.
#
# Responsibilities:
# - Validate required execution identity semantics.
# - Validate broader correlation identity preservation.
# - Validate operation and parent-operation relationships.
# - Validate identifier normalization.
# - Validate invalid identifier rejection.
# - Validate self-parent protection.
# - Validate immutability.
#
# Must Not:
# - Test RAG or Knowledge-specific semantics.
# - Test identifier generation.
# - Test persistence or serialization.
# - Test JSON or JSONL behavior.
# - Test logging or metrics behavior.
# - Test workflow, task, agent, or orchestration behavior.
#
# Architectural Position:
# - Protects the first ALHF Operational Evidence foundation contract.
# - Guards universal execution identity semantics from regression.
#
# Design Principles:
# - Think Hard Once. Implement Many Times.
# - Test outputs. Test failures. Test invariants.
# - Production-grade architecture from Day 1.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)


def test_execution_identity_preserves_required_identifiers() -> None:
    identity = ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )

    assert identity.correlation_id == "correlation-001"
    assert identity.execution_id == "execution-001"
    assert identity.operation_id == "operation-001"


def test_root_operation_allows_no_parent_operation() -> None:
    identity = ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-root",
    )

    assert identity.parent_operation_id is None


def test_child_operation_preserves_parent_operation() -> None:
    identity = ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-child",
        parent_operation_id="operation-root",
    )

    assert identity.parent_operation_id == "operation-root"


def test_identifiers_are_whitespace_normalized() -> None:
    identity = ExecutionIdentity(
        correlation_id="  correlation-001  ",
        execution_id="  execution-001  ",
        operation_id="  operation-child  ",
        parent_operation_id="  operation-root  ",
    )

    assert identity.correlation_id == "correlation-001"
    assert identity.execution_id == "execution-001"
    assert identity.operation_id == "operation-child"
    assert identity.parent_operation_id == "operation-root"


@pytest.mark.parametrize(
    "field_name",
    (
        "correlation_id",
        "execution_id",
        "operation_id",
    ),
)
def test_required_identifier_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "correlation_id": "correlation-001",
        "execution_id": "execution-001",
        "operation_id": "operation-001",
    }

    values[field_name] = ""

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        ExecutionIdentity(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "correlation_id",
        "execution_id",
        "operation_id",
    ),
)
def test_required_identifier_rejects_whitespace_only_value(
    field_name: str,
) -> None:
    values = {
        "correlation_id": "correlation-001",
        "execution_id": "execution-001",
        "operation_id": "operation-001",
    }

    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        ExecutionIdentity(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "correlation_id",
        "execution_id",
        "operation_id",
    ),
)
def test_required_identifier_rejects_non_string_value(
    field_name: str,
) -> None:
    values = {
        "correlation_id": "correlation-001",
        "execution_id": "execution-001",
        "operation_id": "operation-001",
    }

    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        ExecutionIdentity(**values)


def test_parent_operation_rejects_empty_value() -> None:
    with pytest.raises(
        ValueError,
        match="parent_operation_id cannot be empty when provided",
    ):
        ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
            parent_operation_id="",
        )


def test_parent_operation_rejects_whitespace_only_value() -> None:
    with pytest.raises(
        ValueError,
        match="parent_operation_id cannot be empty when provided",
    ):
        ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
            parent_operation_id="   ",
        )


def test_parent_operation_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="parent_operation_id must be a string or None",
    ):
        ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
            parent_operation_id=123,
        )


def test_operation_cannot_be_its_own_parent() -> None:
    with pytest.raises(
        ValueError,
        match="parent_operation_id cannot equal operation_id",
    ):
        ExecutionIdentity(
            correlation_id="correlation-001",
            execution_id="execution-001",
            operation_id="operation-001",
            parent_operation_id="operation-001",
        )


def test_execution_identity_is_immutable() -> None:
    identity = ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
    )

    with pytest.raises(FrozenInstanceError):
        identity.operation_id = "operation-002"


def test_distinct_identity_dimensions_can_hold_distinct_values() -> None:
    identity = ExecutionIdentity(
        correlation_id="business-correlation-001",
        execution_id="execution-017",
        operation_id="operation-093",
        parent_operation_id="operation-010",
    )

    assert identity.correlation_id != identity.execution_id
    assert identity.execution_id != identity.operation_id
    assert identity.operation_id != identity.parent_operation_id
