# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for universal ALHF operational outcome semantics.
#
# Responsibilities:
# - Validate completion-state semantics.
# - Validate quality-state semantics.
# - Validate failure-cause semantics.
# - Validate retry-disposition semantics.
# - Validate operational-criticality semantics.
# - Validate multidimensional outcome combinations.
# - Validate invalid type rejection.
# - Validate failure and retry consistency.
# - Validate immutable outcome behavior.
#
# Must Not:
# - Test PipelineStatus or PipelineResult behavior.
# - Test RAG or Knowledge-specific outcomes.
# - Test stage-specific event semantics.
# - Test persistence, JSON, or JSONL behavior.
# - Test logging or metrics behavior.
# - Test root-cause analysis.
# - Test provider-specific failures.
#
# Architectural Position:
# - Protects universal ALHF Operational Evidence outcome semantics.
# - Guards multidimensional operational outcomes from regression.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.outcome import (
    CompletionState,
    FailureCause,
    OperationalCriticality,
    OperationalOutcome,
    QualityState,
    RetryDisposition,
)


def test_create_healthy_complete_outcome() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.completion == CompletionState.COMPLETE
    assert outcome.quality == QualityState.ACCEPTABLE
    assert outcome.criticality == OperationalCriticality.REQUIRED
    assert outcome.failure_cause is None
    assert outcome.retry_disposition is None


def test_complete_outcome_reports_is_complete() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.is_complete is True


@pytest.mark.parametrize(
    "completion",
    (
        CompletionState.PARTIAL,
        CompletionState.INCOMPLETE,
        CompletionState.NOT_STARTED,
        CompletionState.UNKNOWN,
    ),
)
def test_non_complete_states_report_not_complete(
    completion: CompletionState,
) -> None:
    outcome = OperationalOutcome(
        completion=completion,
        quality=QualityState.NOT_ASSESSED,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.is_complete is False


def test_degraded_quality_reports_is_degraded() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.is_degraded is True


@pytest.mark.parametrize(
    "quality",
    (
        QualityState.ACCEPTABLE,
        QualityState.UNUSABLE,
        QualityState.NOT_ASSESSED,
        QualityState.UNKNOWN,
    ),
)
def test_non_degraded_quality_states_report_not_degraded(
    quality: QualityState,
) -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=quality,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.is_degraded is False


def test_outcome_without_failure_reports_no_failure() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.has_failure is False


def test_outcome_with_failure_reports_failure() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.PARTIAL,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
        failure_cause=FailureCause.DEPENDENCY,
        retry_disposition=RetryDisposition.RETRYABLE,
    )

    assert outcome.has_failure is True


def test_complete_operation_can_have_degraded_quality() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.is_complete is True
    assert outcome.is_degraded is True
    assert outcome.has_failure is False


def test_complete_operation_can_preserve_recovered_failure() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=OperationalCriticality.REQUIRED,
        failure_cause=FailureCause.DEPENDENCY,
        retry_disposition=RetryDisposition.RETRYABLE,
    )

    assert outcome.is_complete is True
    assert outcome.has_failure is True
    assert outcome.failure_cause == FailureCause.DEPENDENCY
    assert (
        outcome.retry_disposition
        == RetryDisposition.RETRYABLE
    )


def test_partial_operation_does_not_require_failure_cause() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.PARTIAL,
        quality=QualityState.DEGRADED,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.is_complete is False
    assert outcome.is_degraded is True
    assert outcome.has_failure is False


def test_unknown_completion_is_preserved_without_inference() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.UNKNOWN,
        quality=QualityState.UNKNOWN,
        criticality=OperationalCriticality.REQUIRED,
    )

    assert outcome.completion == CompletionState.UNKNOWN
    assert outcome.quality == QualityState.UNKNOWN
    assert outcome.has_failure is False


def test_unknown_failure_cause_and_retryability_are_supported() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.INCOMPLETE,
        quality=QualityState.UNKNOWN,
        criticality=OperationalCriticality.REQUIRED,
        failure_cause=FailureCause.UNKNOWN,
        retry_disposition=RetryDisposition.UNKNOWN,
    )

    assert outcome.failure_cause == FailureCause.UNKNOWN
    assert (
        outcome.retry_disposition
        == RetryDisposition.UNKNOWN
    )


@pytest.mark.parametrize(
    "failure_cause",
    tuple(FailureCause),
)
def test_all_failure_causes_are_supported(
    failure_cause: FailureCause,
) -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.INCOMPLETE,
        quality=QualityState.UNUSABLE,
        criticality=OperationalCriticality.REQUIRED,
        failure_cause=failure_cause,
        retry_disposition=RetryDisposition.UNKNOWN,
    )

    assert outcome.failure_cause == failure_cause
    assert outcome.has_failure is True


@pytest.mark.parametrize(
    "retry_disposition",
    tuple(RetryDisposition),
)
def test_all_retry_dispositions_are_supported(
    retry_disposition: RetryDisposition,
) -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.INCOMPLETE,
        quality=QualityState.UNUSABLE,
        criticality=OperationalCriticality.REQUIRED,
        failure_cause=FailureCause.DEPENDENCY,
        retry_disposition=retry_disposition,
    )

    assert outcome.retry_disposition == retry_disposition


@pytest.mark.parametrize(
    "criticality",
    tuple(OperationalCriticality),
)
def test_all_operational_criticalities_are_supported(
    criticality: OperationalCriticality,
) -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=criticality,
    )

    assert outcome.criticality == criticality


def test_retry_disposition_requires_failure_cause() -> None:
    with pytest.raises(
        ValueError,
        match="retry_disposition requires failure_cause",
    ):
        OperationalOutcome(
            completion=CompletionState.COMPLETE,
            quality=QualityState.ACCEPTABLE,
            criticality=OperationalCriticality.REQUIRED,
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_failure_cause_requires_retry_disposition() -> None:
    with pytest.raises(
        ValueError,
        match="failure_cause requires retry_disposition",
    ):
        OperationalOutcome(
            completion=CompletionState.INCOMPLETE,
            quality=QualityState.UNUSABLE,
            criticality=OperationalCriticality.REQUIRED,
            failure_cause=FailureCause.DEPENDENCY,
        )


@pytest.mark.parametrize(
    (
        "field_name",
        "invalid_value",
        "expected_message",
    ),
    (
        (
            "completion",
            "COMPLETE",
            "completion must be an instance of CompletionState",
        ),
        (
            "quality",
            "ACCEPTABLE",
            "quality must be an instance of QualityState",
        ),
        (
            "criticality",
            "REQUIRED",
            (
                "criticality must be an instance of "
                "OperationalCriticality"
            ),
        ),
    ),
)
def test_required_enum_fields_reject_non_enum_values(
    field_name: str,
    invalid_value: str,
    expected_message: str,
) -> None:
    values = {
        "completion": CompletionState.COMPLETE,
        "quality": QualityState.ACCEPTABLE,
        "criticality": OperationalCriticality.REQUIRED,
    }

    values[field_name] = invalid_value

    with pytest.raises(
        TypeError,
        match=expected_message,
    ):
        OperationalOutcome(**values)


def test_failure_cause_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match="failure_cause must be an instance of FailureCause",
    ):
        OperationalOutcome(
            completion=CompletionState.INCOMPLETE,
            quality=QualityState.UNUSABLE,
            criticality=OperationalCriticality.REQUIRED,
            failure_cause="DEPENDENCY",
            retry_disposition=RetryDisposition.RETRYABLE,
        )


def test_retry_disposition_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "retry_disposition must be an instance of "
            "RetryDisposition"
        ),
    ):
        OperationalOutcome(
            completion=CompletionState.INCOMPLETE,
            quality=QualityState.UNUSABLE,
            criticality=OperationalCriticality.REQUIRED,
            failure_cause=FailureCause.DEPENDENCY,
            retry_disposition="RETRYABLE",
        )


def test_operational_outcome_is_immutable() -> None:
    outcome = OperationalOutcome(
        completion=CompletionState.COMPLETE,
        quality=QualityState.ACCEPTABLE,
        criticality=OperationalCriticality.REQUIRED,
    )

    with pytest.raises(FrozenInstanceError):
        outcome.quality = QualityState.DEGRADED
