# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for universal ALHF operational relationship semantics.
#
# Responsibilities:
# - Validate relationship source and target references.
# - Validate all supported universal relationship types.
# - Validate relationship reference normalization.
# - Validate invalid reference rejection.
# - Validate invalid relationship-type rejection.
# - Validate self-referential relationship rejection.
# - Validate relationship immutability.
#
# Must Not:
# - Test diagnosed causal relationships.
# - Test root-cause analysis.
# - Test RAG or Knowledge-specific relationships.
# - Test workflow, task, or agent-specific relationships.
# - Test persistence, JSON, or JSONL behavior.
# - Test provider-specific storage references.

from dataclasses import FrozenInstanceError

import pytest

from alhf.core.operational_evidence.contracts.relationship import (
    OperationalRelationship,
    RelationshipType,
)


def test_create_operational_relationship() -> None:
    relationship = OperationalRelationship(
        source_ref="operation-002",
        target_ref="operation-001",
        relationship_type=RelationshipType.DEPENDS_ON,
    )

    assert relationship.source_ref == "operation-002"
    assert relationship.target_ref == "operation-001"
    assert (
        relationship.relationship_type
        == RelationshipType.DEPENDS_ON
    )


@pytest.mark.parametrize(
    "relationship_type",
    tuple(RelationshipType),
)
def test_all_relationship_types_are_supported(
    relationship_type: RelationshipType,
) -> None:
    relationship = OperationalRelationship(
        source_ref="source-001",
        target_ref="target-001",
        relationship_type=relationship_type,
    )

    assert relationship.relationship_type == relationship_type


def test_relationship_references_are_whitespace_normalized() -> None:
    relationship = OperationalRelationship(
        source_ref="  source-001  ",
        target_ref="  target-001  ",
        relationship_type=RelationshipType.REFERENCES,
    )

    assert relationship.source_ref == "source-001"
    assert relationship.target_ref == "target-001"


@pytest.mark.parametrize(
    "source_ref",
    (
        "",
        "   ",
    ),
)
def test_source_ref_rejects_empty_value(
    source_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="source_ref cannot be empty",
    ):
        OperationalRelationship(
            source_ref=source_ref,
            target_ref="target-001",
            relationship_type=RelationshipType.REFERENCES,
        )


def test_source_ref_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="source_ref must be a string",
    ):
        OperationalRelationship(
            source_ref=123,
            target_ref="target-001",
            relationship_type=RelationshipType.REFERENCES,
        )


@pytest.mark.parametrize(
    "target_ref",
    (
        "",
        "   ",
    ),
)
def test_target_ref_rejects_empty_value(
    target_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="target_ref cannot be empty",
    ):
        OperationalRelationship(
            source_ref="source-001",
            target_ref=target_ref,
            relationship_type=RelationshipType.REFERENCES,
        )


def test_target_ref_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="target_ref must be a string",
    ):
        OperationalRelationship(
            source_ref="source-001",
            target_ref=123,
            relationship_type=RelationshipType.REFERENCES,
        )


def test_relationship_type_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "relationship_type must be an instance of "
            "RelationshipType"
        ),
    ):
        OperationalRelationship(
            source_ref="source-001",
            target_ref="target-001",
            relationship_type="DEPENDS_ON",
        )


def test_relationship_rejects_exact_self_reference() -> None:
    with pytest.raises(
        ValueError,
        match="source_ref cannot equal target_ref",
    ):
        OperationalRelationship(
            source_ref="operation-001",
            target_ref="operation-001",
            relationship_type=RelationshipType.DEPENDS_ON,
        )


def test_relationship_rejects_self_reference_after_normalization() -> None:
    with pytest.raises(
        ValueError,
        match="source_ref cannot equal target_ref",
    ):
        OperationalRelationship(
            source_ref="  operation-001",
            target_ref="operation-001  ",
            relationship_type=RelationshipType.REFERENCES,
        )


def test_relationship_direction_is_preserved() -> None:
    relationship = OperationalRelationship(
        source_ref="derived-artifact",
        target_ref="source-artifact",
        relationship_type=RelationshipType.DERIVED_FROM,
    )

    assert relationship.source_ref == "derived-artifact"
    assert relationship.target_ref == "source-artifact"


def test_dependency_relationship_does_not_change_references() -> None:
    relationship = OperationalRelationship(
        source_ref="consumer-operation",
        target_ref="provider-operation",
        relationship_type=RelationshipType.DEPENDS_ON,
    )

    assert relationship.source_ref == "consumer-operation"
    assert relationship.target_ref == "provider-operation"


def test_remediation_relationship_is_supported() -> None:
    relationship = OperationalRelationship(
        source_ref="corrective-action-001",
        target_ref="finding-001",
        relationship_type=RelationshipType.REMEDIATES,
    )

    assert (
        relationship.relationship_type
        == RelationshipType.REMEDIATES
    )


def test_validation_relationship_is_supported() -> None:
    relationship = OperationalRelationship(
        source_ref="validation-001",
        target_ref="corrective-action-001",
        relationship_type=RelationshipType.VALIDATES,
    )

    assert (
        relationship.relationship_type
        == RelationshipType.VALIDATES
    )


def test_relationship_is_immutable() -> None:
    relationship = OperationalRelationship(
        source_ref="source-001",
        target_ref="target-001",
        relationship_type=RelationshipType.RELATED_TO,
    )

    with pytest.raises(FrozenInstanceError):
        relationship.target_ref = "target-002"
