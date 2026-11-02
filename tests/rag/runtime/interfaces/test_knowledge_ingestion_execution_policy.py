# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the stable execution-policy interface used by ALHF Knowledge
# ingestion after resource-level processing failures.
#
# Problem Solved:
# Ingestion orchestration must depend on an abstract policy boundary
# rather than embedding deterministic continuation behavior directly.
#
# Responsibilities:
# - Verify the policy interface cannot be instantiated directly.
# - Verify concrete implementations satisfy the policy contract.
# - Verify failure facts can be evaluated through the stable boundary.
# - Verify policy implementations return ingestion decisions.
#
# Must Not:
# - Define production V1 failure policy.
# - Execute Knowledge ingestion stages.
# - Execute continuation, termination, retry, or recovery.
# - Test Operational Evidence behavior.
# - Depend on Multi-Agent execution-governor contracts.

from __future__ import annotations

import pytest

from alhf.rag.runtime.contracts.knowledge_ingestion_decision import (
    KnowledgeIngestionAction,
    KnowledgeIngestionDecision,
)
from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionFailure,
    KnowledgeIngestionStage,
)
from alhf.rag.runtime.interfaces.knowledge_ingestion_execution_policy import (
    KnowledgeIngestionExecutionPolicy,
)


class _TestPolicy(KnowledgeIngestionExecutionPolicy):
    def __init__(
        self,
        decision: KnowledgeIngestionDecision,
    ) -> None:
        self._decision = decision
        self.received_failure: KnowledgeIngestionFailure | None = None

    def decide(
        self,
        failure: KnowledgeIngestionFailure,
    ) -> KnowledgeIngestionDecision:
        self.received_failure = failure
        return self._decision


def _failure() -> KnowledgeIngestionFailure:
    return KnowledgeIngestionFailure(
        knowledge_scope_ref="scope:test",
        source_ref="source:test",
        resource_ref="resource:test",
        revision_ref="revision:test",
        stage=KnowledgeIngestionStage.PARSING,
        error_code="PARSING_FAILED",
        error_message="resource parsing failed",
        retryable=False,
    )


def test_interface_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        KnowledgeIngestionExecutionPolicy()


def test_concrete_policy_is_execution_policy_contract() -> None:
    policy = _TestPolicy(
        KnowledgeIngestionDecision(
            action=KnowledgeIngestionAction.CONTINUE,
            reason="test policy",
        )
    )

    assert isinstance(
        policy,
        KnowledgeIngestionExecutionPolicy,
    )


@pytest.mark.parametrize(
    "action",
    [
        KnowledgeIngestionAction.CONTINUE,
        KnowledgeIngestionAction.STOP,
    ],
)
def test_policy_evaluates_failure_through_stable_boundary(
    action: KnowledgeIngestionAction,
) -> None:
    failure = _failure()
    decision = KnowledgeIngestionDecision(
        action=action,
        reason="test decision",
    )
    policy = _TestPolicy(decision)

    result = policy.decide(failure)

    assert result is decision
    assert policy.received_failure is failure


def test_interface_exposes_only_decision_responsibility() -> None:
    abstract_methods = (
        KnowledgeIngestionExecutionPolicy.__abstractmethods__
    )

    assert abstract_methods == frozenset({"decide"})
