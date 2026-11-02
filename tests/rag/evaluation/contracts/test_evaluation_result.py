# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF EvaluationResult contract.
#
# Responsibilities:
# - Validate immutable evaluation-result construction.
# - Validate evaluator and evaluated-subject identity.
# - Validate explicit evaluation status semantics.
# - Validate normalized bounded evaluation scores.
# - Validate evaluation reason preservation.
# - Validate required text normalization.
# - Validate invalid evaluation inputs.
#
# Must Not:
# - Perform retrieval or evaluation algorithms.
# - Construct Evidence or Context.
# - Generate answers.
# - Implement adaptive optimization or self-learning.
# - Implement configuration promotion.
# - Depend on external RAG frameworks.

import math
from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.evaluation.contracts.evaluation_result import (
    EvaluationResult,
    EvaluationStatus,
)


def _result(
    *,
    status: EvaluationStatus = EvaluationStatus.PASS,
    score: float = 1.0,
    reason: str = "evaluation passed",
) -> EvaluationResult:
    return EvaluationResult(
        evaluation_id="evaluation-001",
        subject_ref="context-001",
        evaluator_ref="deterministic-evaluator",
        evaluator_version="1.0",
        status=status,
        score=score,
        reason=reason,
    )


def test_create_evaluation_result() -> None:
    result = _result()

    assert result.evaluation_id == "evaluation-001"
    assert result.subject_ref == "context-001"
    assert result.evaluator_ref == "deterministic-evaluator"
    assert result.evaluator_version == "1.0"
    assert result.status == EvaluationStatus.PASS
    assert result.score == 1.0
    assert result.reason == "evaluation passed"


@pytest.mark.parametrize(
    "status",
    tuple(EvaluationStatus),
)
def test_all_evaluation_statuses_are_supported(
    status: EvaluationStatus,
) -> None:
    result = _result(
        status=status,
    )

    assert result.status == status


@pytest.mark.parametrize(
    "score",
    (
        0,
        0.5,
        1,
    ),
)
def test_valid_score_is_normalized(
    score: float,
) -> None:
    result = _result(
        score=score,
    )

    assert result.score == float(score)
    assert isinstance(
        result.score,
        float,
    )


@pytest.mark.parametrize(
    "score",
    (
        -0.1,
        1.1,
    ),
)
def test_out_of_range_score_is_rejected(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="score must be between 0.0 and 1.0",
    ):
        _result(
            score=score,
        )


@pytest.mark.parametrize(
    "score",
    (
        math.inf,
        -math.inf,
        math.nan,
    ),
)
def test_non_finite_score_is_rejected(
    score: float,
) -> None:
    with pytest.raises(
        ValueError,
        match="score must be finite",
    ):
        _result(
            score=score,
        )


@pytest.mark.parametrize(
    "score",
    (
        True,
        "1.0",
        None,
    ),
)
def test_invalid_score_type_is_rejected(
    score: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="score must be a number",
    ):
        _result(
            score=score,
        )


def test_invalid_status_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "status must be an instance of EvaluationStatus"
        ),
    ):
        _result(
            status="PASS",
        )


def test_required_text_values_are_normalized() -> None:
    result = EvaluationResult(
        evaluation_id="  evaluation-001  ",
        subject_ref="  context-001  ",
        evaluator_ref="  deterministic-evaluator  ",
        evaluator_version="  1.0  ",
        status=EvaluationStatus.PASS,
        score=1,
        reason="  evaluation passed  ",
    )

    assert result.evaluation_id == "evaluation-001"
    assert result.subject_ref == "context-001"
    assert result.evaluator_ref == "deterministic-evaluator"
    assert result.evaluator_version == "1.0"
    assert result.reason == "evaluation passed"


@pytest.mark.parametrize(
    "field_name",
    (
        "evaluation_id",
        "subject_ref",
        "evaluator_ref",
        "evaluator_version",
        "reason",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "evaluation_id": "evaluation-001",
        "subject_ref": "context-001",
        "evaluator_ref": "deterministic-evaluator",
        "evaluator_version": "1.0",
        "status": EvaluationStatus.PASS,
        "score": 1.0,
        "reason": "evaluation passed",
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        EvaluationResult(
            **values
        )


def test_evaluation_result_is_immutable() -> None:
    result = _result()

    with pytest.raises(FrozenInstanceError):
        result.score = 0.5
