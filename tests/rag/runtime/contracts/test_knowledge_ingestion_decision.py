# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the immutable execution-decision contract used by ALHF
# Knowledge ingestion policy.
#
# Problem Solved:
# Ingestion continuation decisions must remain validated, explainable,
# and independent from failure facts and orchestration implementation.
#
# Responsibilities:
# - Verify supported executable ingestion actions.
# - Verify mandatory decision rationale.
# - Verify reason normalization and validation.
# - Verify strict action contract validation.
# - Verify immutable decision semantics.
#
# Must Not:
# - Evaluate ingestion failures.
# - Execute continuation or termination.
# - Test retry, recovery, or governance behavior.
# - Test Operational Evidence emission.
# - Execute Knowledge ingestion stages.

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.runtime.contracts.knowledge_ingestion_decision import (
    KnowledgeIngestionAction,
    KnowledgeIngestionDecision,
)


@pytest.mark.parametrize(
    "action",
    list(KnowledgeIngestionAction),
)
def test_preserves_supported_ingestion_action(
    action: KnowledgeIngestionAction,
) -> None:
    decision = KnowledgeIngestionDecision(
        action=action,
        reason="deterministic policy decision",
    )

    assert decision.action is action
    assert decision.reason == "deterministic policy decision"


def test_normalizes_decision_reason() -> None:
    decision = KnowledgeIngestionDecision(
        action=KnowledgeIngestionAction.CONTINUE,
        reason="  resource failure may be isolated  ",
    )

    assert decision.reason == "resource failure may be isolated"


@pytest.mark.parametrize(
    "reason",
    ["", "   "],
)
def test_rejects_empty_decision_reason(
    reason: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="reason cannot be empty",
    ):
        KnowledgeIngestionDecision(
            action=KnowledgeIngestionAction.STOP,
            reason=reason,
        )


@pytest.mark.parametrize(
    "reason",
    [123, False, None],
)
def test_rejects_non_string_decision_reason(
    reason: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="reason must be a string",
    ):
        KnowledgeIngestionDecision(
            action=KnowledgeIngestionAction.STOP,
            reason=reason,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "action",
    ["CONTINUE", "STOP", None, object()],
)
def test_rejects_invalid_action_contract(
    action: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="KnowledgeIngestionAction",
    ):
        KnowledgeIngestionDecision(
            action=action,  # type: ignore[arg-type]
            reason="policy decision",
        )


def test_decision_contract_is_immutable() -> None:
    decision = KnowledgeIngestionDecision(
        action=KnowledgeIngestionAction.CONTINUE,
        reason="continue processing",
    )

    with pytest.raises(FrozenInstanceError):
        decision.reason = "changed"  # type: ignore[misc]


def test_action_vocabulary_contains_only_executable_actions() -> None:
    assert tuple(KnowledgeIngestionAction) == (
        KnowledgeIngestionAction.CONTINUE,
        KnowledgeIngestionAction.STOP,
    )
