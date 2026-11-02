# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeEventType contract.
#
# Responsibilities:
# - Validate Knowledge Foundation event values.
# - Validate event-value uniqueness.
# - Validate string compatibility.
# - Validate lifecycle coverage across Knowledge stages.
# - Protect Knowledge-specific event semantics from regression.
#
# Must Not:
# - Test universal ALHF EventType contracts.
# - Test event processing or orchestration.
# - Test Operational Evidence persistence.
# - Test failure analysis or root-cause analysis.
# - Test GraphRAG-only or Agentic-RAG-only semantics.

from enum import Enum

import pytest

from alhf.rag.operational_evidence.contracts.knowledge_event_type import (
    KnowledgeEventType,
)


def test_knowledge_event_type_inherits_from_string() -> None:
    assert issubclass(
        KnowledgeEventType,
        str,
    )


def test_knowledge_event_type_inherits_from_enum() -> None:
    assert issubclass(
        KnowledgeEventType,
        Enum,
    )


@pytest.mark.parametrize(
    ("event_type", "expected_value"),
    (
        (
            KnowledgeEventType.ACQUISITION_STARTED,
            "ACQUISITION_STARTED",
        ),
        (
            KnowledgeEventType.ACQUISITION_COMPLETED,
            "ACQUISITION_COMPLETED",
        ),
        (
            KnowledgeEventType.ACQUISITION_DEGRADED,
            "ACQUISITION_DEGRADED",
        ),
        (
            KnowledgeEventType.ACQUISITION_FAILED,
            "ACQUISITION_FAILED",
        ),
        (
            KnowledgeEventType.PARSING_STARTED,
            "PARSING_STARTED",
        ),
        (
            KnowledgeEventType.PARSING_COMPLETED,
            "PARSING_COMPLETED",
        ),
        (
            KnowledgeEventType.PARSING_DEGRADED,
            "PARSING_DEGRADED",
        ),
        (
            KnowledgeEventType.PARSING_FAILED,
            "PARSING_FAILED",
        ),
        (
            KnowledgeEventType.NORMALIZATION_STARTED,
            "NORMALIZATION_STARTED",
        ),
        (
            KnowledgeEventType.NORMALIZATION_COMPLETED,
            "NORMALIZATION_COMPLETED",
        ),
        (
            KnowledgeEventType.NORMALIZATION_DEGRADED,
            "NORMALIZATION_DEGRADED",
        ),
        (
            KnowledgeEventType.NORMALIZATION_FAILED,
            "NORMALIZATION_FAILED",
        ),
        (
            KnowledgeEventType.DERIVATION_STARTED,
            "DERIVATION_STARTED",
        ),
        (
            KnowledgeEventType.DERIVATION_COMPLETED,
            "DERIVATION_COMPLETED",
        ),
        (
            KnowledgeEventType.DERIVATION_DEGRADED,
            "DERIVATION_DEGRADED",
        ),
        (
            KnowledgeEventType.DERIVATION_FAILED,
            "DERIVATION_FAILED",
        ),
        (
            KnowledgeEventType.REPRESENTATION_STARTED,
            "REPRESENTATION_STARTED",
        ),
        (
            KnowledgeEventType.REPRESENTATION_COMPLETED,
            "REPRESENTATION_COMPLETED",
        ),
        (
            KnowledgeEventType.REPRESENTATION_DEGRADED,
            "REPRESENTATION_DEGRADED",
        ),
        (
            KnowledgeEventType.REPRESENTATION_FAILED,
            "REPRESENTATION_FAILED",
        ),
        (
            KnowledgeEventType.INDEXING_STARTED,
            "INDEXING_STARTED",
        ),
        (
            KnowledgeEventType.INDEXING_COMPLETED,
            "INDEXING_COMPLETED",
        ),
        (
            KnowledgeEventType.INDEXING_DEGRADED,
            "INDEXING_DEGRADED",
        ),
        (
            KnowledgeEventType.INDEXING_FAILED,
            "INDEXING_FAILED",
        ),
        (
            KnowledgeEventType.RETRIEVAL_STARTED,
            "RETRIEVAL_STARTED",
        ),
        (
            KnowledgeEventType.RETRIEVAL_COMPLETED,
            "RETRIEVAL_COMPLETED",
        ),
        (
            KnowledgeEventType.RETRIEVAL_DEGRADED,
            "RETRIEVAL_DEGRADED",
        ),
        (
            KnowledgeEventType.RETRIEVAL_FAILED,
            "RETRIEVAL_FAILED",
        ),
        (
            KnowledgeEventType.EVIDENCE_CONSTRUCTION_STARTED,
            "EVIDENCE_CONSTRUCTION_STARTED",
        ),
        (
            KnowledgeEventType.EVIDENCE_CONSTRUCTION_COMPLETED,
            "EVIDENCE_CONSTRUCTION_COMPLETED",
        ),
        (
            KnowledgeEventType.EVIDENCE_CONSTRUCTION_DEGRADED,
            "EVIDENCE_CONSTRUCTION_DEGRADED",
        ),
        (
            KnowledgeEventType.EVIDENCE_CONSTRUCTION_FAILED,
            "EVIDENCE_CONSTRUCTION_FAILED",
        ),
        (
            KnowledgeEventType.CONTEXT_CONSTRUCTION_STARTED,
            "CONTEXT_CONSTRUCTION_STARTED",
        ),
        (
            KnowledgeEventType.CONTEXT_CONSTRUCTION_COMPLETED,
            "CONTEXT_CONSTRUCTION_COMPLETED",
        ),
        (
            KnowledgeEventType.CONTEXT_CONSTRUCTION_DEGRADED,
            "CONTEXT_CONSTRUCTION_DEGRADED",
        ),
        (
            KnowledgeEventType.CONTEXT_CONSTRUCTION_FAILED,
            "CONTEXT_CONSTRUCTION_FAILED",
        ),
        (
            KnowledgeEventType.EVALUATION_STARTED,
            "EVALUATION_STARTED",
        ),
        (
            KnowledgeEventType.EVALUATION_COMPLETED,
            "EVALUATION_COMPLETED",
        ),
        (
            KnowledgeEventType.EVALUATION_DEGRADED,
            "EVALUATION_DEGRADED",
        ),
        (
            KnowledgeEventType.EVALUATION_FAILED,
            "EVALUATION_FAILED",
        ),
    ),
)
def test_knowledge_event_type_has_stable_value(
    event_type: KnowledgeEventType,
    expected_value: str,
) -> None:
    assert event_type.value == expected_value


def test_knowledge_event_values_are_unique() -> None:
    values = tuple(
        event_type.value
        for event_type in KnowledgeEventType
    )

    assert len(values) == len(set(values))


@pytest.mark.parametrize(
    "event_type",
    tuple(KnowledgeEventType),
)
def test_knowledge_event_values_are_string_compatible(
    event_type: KnowledgeEventType,
) -> None:
    assert isinstance(
        event_type,
        str,
    )
    assert isinstance(
        event_type.value,
        str,
    )


@pytest.mark.parametrize(
    "stage_prefix",
    (
        "ACQUISITION",
        "PARSING",
        "NORMALIZATION",
        "DERIVATION",
        "REPRESENTATION",
        "INDEXING",
        "RETRIEVAL",
        "EVIDENCE_CONSTRUCTION",
        "CONTEXT_CONSTRUCTION",
        "EVALUATION",
    ),
)
def test_each_stage_has_complete_operational_lifecycle(
    stage_prefix: str,
) -> None:
    values = {
        event_type.value
        for event_type in KnowledgeEventType
    }

    assert f"{stage_prefix}_STARTED" in values
    assert f"{stage_prefix}_COMPLETED" in values
    assert f"{stage_prefix}_DEGRADED" in values
    assert f"{stage_prefix}_FAILED" in values


def test_event_type_can_be_created_from_stable_value() -> None:
    event_type = KnowledgeEventType(
        "RETRIEVAL_DEGRADED"
    )

    assert event_type is KnowledgeEventType.RETRIEVAL_DEGRADED


def test_unknown_event_type_is_rejected() -> None:
    with pytest.raises(ValueError):
        KnowledgeEventType(
            "UNKNOWN_KNOWLEDGE_EVENT"
        )
