# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the production KnowledgeIngestionResult contract.
#
# Responsibilities:
# - Validate bounded terminal ingestion semantics.
# - Validate identity normalization and immutability.
# - Validate aggregate stage counts without enforcing 1:1 fan-out.
# - Validate completed, partial, and failed outcomes.
# - Protect North-Star-compatible ingestion topology.
#
# Must Not:
# - Execute Knowledge ingestion.
# - Assume one derivation maps to one representation or index.
# - Expose intermediate Knowledge artifacts.
# - Introduce Standard RAG, GraphRAG, or Agentic RAG coupling.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.runtime.contracts.knowledge_ingestion_result import (
    KnowledgeIngestionResult,
    KnowledgeIngestionStatus,
)


def _result(
    **overrides,
) -> KnowledgeIngestionResult:
    values = {
        "execution_id": "execution-001",
        "knowledge_scope_ref": "scope-001",
        "source_ref": "source-001",
        "status": KnowledgeIngestionStatus.COMPLETED,
        "acquired_count": 2,
        "parsed_count": 2,
        "normalized_count": 2,
        "derived_count": 4,
        "represented_count": 6,
        "indexed_count": 8,
        "failed_resource_count": 0,
    }

    values.update(
        overrides
    )

    return KnowledgeIngestionResult(
        **values
    )


def test_completed_result_preserves_aggregate_facts() -> None:
    result = _result()

    assert result.execution_id == "execution-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.source_ref == "source-001"
    assert result.status == KnowledgeIngestionStatus.COMPLETED

    assert result.acquired_count == 2
    assert result.parsed_count == 2
    assert result.normalized_count == 2
    assert result.derived_count == 4
    assert result.represented_count == 6
    assert result.indexed_count == 8
    assert result.failed_resource_count == 0


def test_identity_values_are_normalized() -> None:
    result = _result(
        execution_id="  execution-001  ",
        knowledge_scope_ref="  scope-001  ",
        source_ref="  source-001  ",
    )

    assert result.execution_id == "execution-001"
    assert result.knowledge_scope_ref == "scope-001"
    assert result.source_ref == "source-001"


@pytest.mark.parametrize(
    "field_name",
    (
        "execution_id",
        "knowledge_scope_ref",
        "source_ref",
    ),
)
def test_required_identity_rejects_empty_text(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        _result(
            **{
                field_name: "   ",
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "execution_id",
        "knowledge_scope_ref",
        "source_ref",
    ),
)
def test_required_identity_rejects_non_string(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        _result(
            **{
                field_name: 123,
            }
        )


def test_status_requires_governed_enum() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "status must be an instance of "
            "KnowledgeIngestionStatus"
        ),
    ):
        _result(
            status="COMPLETED"
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "acquired_count",
        "parsed_count",
        "normalized_count",
        "derived_count",
        "represented_count",
        "indexed_count",
        "failed_resource_count",
    ),
)
def test_counts_reject_negative_values(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be negative",
    ):
        _result(
            **{
                field_name: -1,
            }
        )


@pytest.mark.parametrize(
    "value",
    (
        True,
        1.5,
        "1",
        None,
    ),
)
def test_counts_reject_non_integer_values(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="indexed_count must be an int",
    ):
        _result(
            indexed_count=value
        )


def test_parsed_count_cannot_exceed_acquired_count() -> None:
    with pytest.raises(
        ValueError,
        match="parsed_count cannot exceed acquired_count",
    ):
        _result(
            acquired_count=1,
            parsed_count=2,
            normalized_count=1,
        )


def test_normalized_count_cannot_exceed_parsed_count() -> None:
    with pytest.raises(
        ValueError,
        match="normalized_count cannot exceed parsed_count",
    ):
        _result(
            parsed_count=1,
            normalized_count=2,
        )


def test_failed_resource_count_cannot_exceed_acquired_count() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "failed_resource_count cannot exceed "
            "acquired_count"
        ),
    ):
        _result(
            acquired_count=1,
            parsed_count=1,
            normalized_count=1,
            failed_resource_count=2,
        )


def test_completed_result_cannot_contain_failed_resources() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "completed ingestion cannot contain "
            "failed resources"
        ),
    ):
        _result(
            failed_resource_count=1
        )


def test_partial_result_can_preserve_resource_failures() -> None:
    result = _result(
        status=KnowledgeIngestionStatus.PARTIAL,
        acquired_count=3,
        parsed_count=2,
        normalized_count=2,
        failed_resource_count=1,
    )

    assert result.status == KnowledgeIngestionStatus.PARTIAL
    assert result.failed_resource_count == 1


def test_failed_result_can_preserve_completed_work() -> None:
    result = _result(
        status=KnowledgeIngestionStatus.FAILED,
        acquired_count=3,
        parsed_count=2,
        normalized_count=2,
        derived_count=4,
        represented_count=4,
        indexed_count=3,
        failed_resource_count=1,
    )

    assert result.status == KnowledgeIngestionStatus.FAILED
    assert result.indexed_count == 3
    assert result.failed_resource_count == 1


def test_future_fan_out_counts_are_not_forced_to_match() -> None:
    result = _result(
        derived_count=3,
        represented_count=9,
        indexed_count=14,
    )

    assert result.derived_count == 3
    assert result.represented_count == 9
    assert result.indexed_count == 14


def test_zero_resource_completed_execution_is_valid() -> None:
    result = _result(
        acquired_count=0,
        parsed_count=0,
        normalized_count=0,
        derived_count=0,
        represented_count=0,
        indexed_count=0,
    )

    assert result.status == KnowledgeIngestionStatus.COMPLETED
    assert result.acquired_count == 0


def test_result_is_immutable() -> None:
    result = _result()

    with pytest.raises(
        FrozenInstanceError
    ):
        result.status = KnowledgeIngestionStatus.FAILED
