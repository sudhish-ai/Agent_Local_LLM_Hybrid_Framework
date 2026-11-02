# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeExecutionContext contract.
#
# Responsibilities:
# - Validate universal execution identity composition.
# - Validate Knowledge evidence context composition.
# - Validate correlation identity access.
# - Validate execution identity access.
# - Validate operation identity access.
# - Validate parent-operation identity access.
# - Validate Knowledge scope access.
# - Validate invalid composed contracts.
# - Validate immutability.
#
# Must Not:
# - Test identity generation.
# - Test Operational Evidence creation.
# - Test Operational Evidence persistence.
# - Test JSON or JSONL behavior.
# - Test Knowledge pipeline execution.
# - Test failure analysis or root-cause analysis.
# - Test Knowledge content.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.execution_identity import (
    ExecutionIdentity,
)
from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)
from alhf.rag.operational_evidence.knowledge_execution_context import (
    KnowledgeExecutionContext,
)


def _execution(
    *,
    parent_operation_id: str | None = None,
) -> ExecutionIdentity:
    return ExecutionIdentity(
        correlation_id="correlation-001",
        execution_id="execution-001",
        operation_id="operation-001",
        parent_operation_id=parent_operation_id,
    )


def _knowledge() -> KnowledgeEvidenceContext:
    return KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref="revision-001",
        derivation_ref="derivation-001",
    )


def test_create_knowledge_execution_context() -> None:
    execution = _execution()
    knowledge = _knowledge()

    context = KnowledgeExecutionContext(
        execution=execution,
        knowledge=knowledge,
    )

    assert context.execution is execution
    assert context.knowledge is knowledge


def test_correlation_id_returns_execution_correlation() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert context.correlation_id == "correlation-001"


def test_execution_id_returns_execution_identity() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert context.execution_id == "execution-001"


def test_operation_id_returns_operation_identity() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert context.operation_id == "operation-001"


def test_root_operation_returns_no_parent() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert context.parent_operation_id is None


def test_parent_operation_identity_is_preserved() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(
            parent_operation_id="operation-parent",
        ),
        knowledge=_knowledge(),
    )

    assert context.parent_operation_id == "operation-parent"


def test_knowledge_scope_ref_returns_governed_scope() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert context.knowledge_scope_ref == "scope-001"


def test_knowledge_context_preserves_governed_references() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert (
        context.knowledge.logical_resource_ref
        == "resource-001"
    )
    assert context.knowledge.revision_ref == "revision-001"
    assert (
        context.knowledge.derivation_ref
        == "derivation-001"
    )


def test_execution_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "execution must be an instance of ExecutionIdentity"
        ),
    ):
        KnowledgeExecutionContext(
            execution="invalid-execution",
            knowledge=_knowledge(),
        )


def test_knowledge_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "knowledge must be an instance of "
            "KnowledgeEvidenceContext"
        ),
    ):
        KnowledgeExecutionContext(
            execution=_execution(),
            knowledge="invalid-knowledge",
        )


def test_equal_contexts_have_equal_values() -> None:
    first_context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )
    second_context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    assert first_context == second_context


def test_knowledge_execution_context_is_immutable() -> None:
    context = KnowledgeExecutionContext(
        execution=_execution(),
        knowledge=_knowledge(),
    )

    with pytest.raises(FrozenInstanceError):
        context.execution = ExecutionIdentity(
            correlation_id="correlation-002",
            execution_id="execution-002",
            operation_id="operation-002",
        )
