# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the deterministic fail-closed execution policy used by ALHF
# Knowledge Foundation ingestion.
#
# Problem Solved:
# Unclassified ingestion failures must stop execution safely without
# inferring continuation from stage, error code, or retryability.
#
# Responsibilities:
# - Verify valid failures produce STOP decisions.
# - Verify deterministic and explainable decision rationale.
# - Verify every current ingestion stage remains fail-closed.
# - Verify retryability does not imply continuation.
# - Verify arbitrary error codes remain fail-closed.
# - Verify invalid failure contracts are rejected.
# - Verify policy evaluation does not mutate failure facts.
#
# Must Not:
# - Execute Knowledge ingestion stages.
# - Test retry, recovery, or continuation execution.
# - Infer resource isolation from exception messages.
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
from alhf.rag.runtime.policies.deterministic_ingestion_execution_policy import (
    DeterministicIngestionExecutionPolicy,
)


def _failure(
    *,
    stage: KnowledgeIngestionStage = KnowledgeIngestionStage.PARSING,
    error_code: str = "TEST_FAILURE",
    retryable: bool = False,
) -> KnowledgeIngestionFailure:
    return KnowledgeIngestionFailure(
        knowledge_scope_ref="scope:test",
        source_ref="source:test",
        resource_ref="resource:test",
        revision_ref="revision:test",
        stage=stage,
        error_code=error_code,
        error_message="resource processing failed",
        retryable=retryable,
    )


def test_valid_failure_returns_stop_decision() -> None:
    policy = DeterministicIngestionExecutionPolicy()

    decision = policy.decide(_failure())

    assert isinstance(
        decision,
        KnowledgeIngestionDecision,
    )
    assert decision.action is KnowledgeIngestionAction.STOP


def test_decision_reason_is_deterministic_and_explainable() -> None:
    policy = DeterministicIngestionExecutionPolicy()

    first = policy.decide(_failure())
    second = policy.decide(_failure())

    assert first.reason == second.reason
    assert first.reason == (
        "resource failure is not explicitly classified as safely isolatable"
    )


@pytest.mark.parametrize(
    "stage",
    list(KnowledgeIngestionStage),
)
def test_every_current_stage_fails_closed(
    stage: KnowledgeIngestionStage,
) -> None:
    policy = DeterministicIngestionExecutionPolicy()

    decision = policy.decide(
        _failure(stage=stage),
    )

    assert decision.action is KnowledgeIngestionAction.STOP


@pytest.mark.parametrize(
    "retryable",
    [False, True],
)
def test_retryability_does_not_imply_continuation(
    retryable: bool,
) -> None:
    policy = DeterministicIngestionExecutionPolicy()

    decision = policy.decide(
        _failure(retryable=retryable),
    )

    assert decision.action is KnowledgeIngestionAction.STOP


@pytest.mark.parametrize(
    "error_code",
    [
        "UNKNOWN_FAILURE",
        "RESOURCE_FAILURE",
        "DEPENDENCY_FAILURE",
        "RETRYABLE_FAILURE",
    ],
)
def test_unclassified_error_codes_fail_closed(
    error_code: str,
) -> None:
    policy = DeterministicIngestionExecutionPolicy()

    decision = policy.decide(
        _failure(error_code=error_code),
    )

    assert decision.action is KnowledgeIngestionAction.STOP


@pytest.mark.parametrize(
    "failure",
    [
        None,
        object(),
        "failure",
    ],
)
def test_rejects_invalid_failure_contract(
    failure: object,
) -> None:
    policy = DeterministicIngestionExecutionPolicy()

    with pytest.raises(
        TypeError,
        match="KnowledgeIngestionFailure",
    ):
        policy.decide(
            failure,  # type: ignore[arg-type]
        )


def test_policy_does_not_mutate_failure() -> None:
    policy = DeterministicIngestionExecutionPolicy()
    failure = _failure(
        stage=KnowledgeIngestionStage.INDEXING,
        error_code="INDEX_FAILURE",
        retryable=True,
    )
    before = failure

    policy.decide(failure)

    assert failure == before
    assert failure.stage is KnowledgeIngestionStage.INDEXING
    assert failure.error_code == "INDEX_FAILURE"
    assert failure.retryable is True
