# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies the immutable resource-level ingestion failure contract used
# by the ALHF Knowledge Foundation production runtime.
#
# Problem Solved:
# Resource-processing failures must preserve bounded, validated facts
# independently from execution-policy decisions and Operational Evidence.
#
# Responsibilities:
# - Verify supported ingestion-stage semantics.
# - Verify resource, revision, source, and scope identity preservation.
# - Verify failure classification and retryability preservation.
# - Verify required text normalization and validation.
# - Verify strict stage and retryability type validation.
# - Verify immutable contract behavior.
#
# Must Not:
# - Test execution-policy decisions.
# - Test retry, continuation, or recovery behavior.
# - Test Operational Evidence emission.
# - Execute Knowledge ingestion stages.

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.runtime.contracts.knowledge_ingestion_failure import (
    KnowledgeIngestionFailure,
    KnowledgeIngestionStage,
)


def _failure(
    **overrides: object,
) -> KnowledgeIngestionFailure:
    values: dict[str, object] = {
        "knowledge_scope_ref": "scope:test",
        "source_ref": "source:test",
        "resource_ref": "resource:test",
        "revision_ref": "revision:test",
        "stage": KnowledgeIngestionStage.PARSING,
        "error_code": "PARSING_FAILED",
        "error_message": "resource parsing failed",
        "retryable": False,
    }
    values.update(overrides)

    return KnowledgeIngestionFailure(
        **values,  # type: ignore[arg-type]
    )


@pytest.mark.parametrize(
    "stage",
    list(KnowledgeIngestionStage),
)
def test_preserves_supported_ingestion_stage(
    stage: KnowledgeIngestionStage,
) -> None:
    failure = _failure(stage=stage)

    assert failure.stage is stage


def test_preserves_failure_facts() -> None:
    failure = _failure(retryable=True)

    assert failure.knowledge_scope_ref == "scope:test"
    assert failure.source_ref == "source:test"
    assert failure.resource_ref == "resource:test"
    assert failure.revision_ref == "revision:test"
    assert failure.error_code == "PARSING_FAILED"
    assert failure.error_message == "resource parsing failed"
    assert failure.retryable is True


@pytest.mark.parametrize(
    "field_name",
    [
        "knowledge_scope_ref",
        "source_ref",
        "resource_ref",
        "revision_ref",
        "error_code",
        "error_message",
    ],
)
def test_normalizes_required_text(
    field_name: str,
) -> None:
    failure = _failure(
        **{field_name: "  normalized-value  "},
    )

    assert getattr(failure, field_name) == "normalized-value"


@pytest.mark.parametrize(
    "field_name",
    [
        "knowledge_scope_ref",
        "source_ref",
        "resource_ref",
        "revision_ref",
        "error_code",
        "error_message",
    ],
)
@pytest.mark.parametrize(
    "value",
    ["", "   "],
)
def test_rejects_empty_required_text(
    field_name: str,
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        _failure(**{field_name: value})


@pytest.mark.parametrize(
    "field_name",
    [
        "knowledge_scope_ref",
        "source_ref",
        "resource_ref",
        "revision_ref",
        "error_code",
        "error_message",
    ],
)
def test_rejects_non_string_required_text(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        _failure(**{field_name: 123})


def test_rejects_invalid_stage_contract() -> None:
    with pytest.raises(
        TypeError,
        match="KnowledgeIngestionStage",
    ):
        _failure(stage="PARSING")


@pytest.mark.parametrize(
    "retryable",
    [0, 1, "false", None],
)
def test_rejects_non_boolean_retryable(
    retryable: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="retryable must be a bool",
    ):
        _failure(retryable=retryable)


def test_contract_is_immutable() -> None:
    failure = _failure()

    with pytest.raises(FrozenInstanceError):
        failure.error_code = "CHANGED"  # type: ignore[misc]
