# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeEvidenceContext contract.
#
# Responsibilities:
# - Validate required Knowledge scope references.
# - Validate optional governed Knowledge references.
# - Validate reference normalization.
# - Validate invalid required references.
# - Validate invalid optional references.
# - Validate affected-scope references.
# - Validate immutability.
#
# Must Not:
# - Test Knowledge content.
# - Test Knowledge identity generation.
# - Test Knowledge lifecycle behavior.
# - Test retrieval or indexing behavior.
# - Test Operational Evidence persistence.
# - Test JSON or JSONL behavior.
# - Test failure analysis or root-cause analysis.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.operational_evidence.contracts.knowledge_evidence_context import (
    KnowledgeEvidenceContext,
)


def test_create_minimal_knowledge_evidence_context() -> None:
    context = KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
    )

    assert context.knowledge_scope_ref == "scope-001"
    assert context.logical_resource_ref is None
    assert context.revision_ref is None
    assert context.derivation_ref is None
    assert context.knowledge_unit_ref is None
    assert context.derived_artifact_ref is None
    assert context.affected_scope_ref is None


def test_create_complete_knowledge_evidence_context() -> None:
    context = KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        logical_resource_ref="resource-001",
        revision_ref="revision-001",
        derivation_ref="derivation-001",
        knowledge_unit_ref="unit-001",
        derived_artifact_ref="artifact-001",
        affected_scope_ref="affected-scope-001",
    )

    assert context.knowledge_scope_ref == "scope-001"
    assert context.logical_resource_ref == "resource-001"
    assert context.revision_ref == "revision-001"
    assert context.derivation_ref == "derivation-001"
    assert context.knowledge_unit_ref == "unit-001"
    assert context.derived_artifact_ref == "artifact-001"
    assert context.affected_scope_ref == "affected-scope-001"


def test_all_references_are_whitespace_normalized() -> None:
    context = KnowledgeEvidenceContext(
        knowledge_scope_ref="  scope-001  ",
        logical_resource_ref="  resource-001  ",
        revision_ref="  revision-001  ",
        derivation_ref="  derivation-001  ",
        knowledge_unit_ref="  unit-001  ",
        derived_artifact_ref="  artifact-001  ",
        affected_scope_ref="  affected-scope-001  ",
    )

    assert context.knowledge_scope_ref == "scope-001"
    assert context.logical_resource_ref == "resource-001"
    assert context.revision_ref == "revision-001"
    assert context.derivation_ref == "derivation-001"
    assert context.knowledge_unit_ref == "unit-001"
    assert context.derived_artifact_ref == "artifact-001"
    assert context.affected_scope_ref == "affected-scope-001"


@pytest.mark.parametrize(
    "knowledge_scope_ref",
    (
        "",
        "   ",
    ),
)
def test_knowledge_scope_ref_rejects_empty_value(
    knowledge_scope_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="knowledge_scope_ref cannot be empty",
    ):
        KnowledgeEvidenceContext(
            knowledge_scope_ref=knowledge_scope_ref,
        )


def test_knowledge_scope_ref_rejects_non_string_value() -> None:
    with pytest.raises(
        TypeError,
        match="knowledge_scope_ref must be a string",
    ):
        KnowledgeEvidenceContext(
            knowledge_scope_ref=123,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "logical_resource_ref",
        "revision_ref",
        "derivation_ref",
        "knowledge_unit_ref",
        "derived_artifact_ref",
        "affected_scope_ref",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        "",
        "   ",
    ),
)
def test_optional_reference_rejects_empty_value(
    field_name: str,
    invalid_value: str,
) -> None:
    values = {
        "knowledge_scope_ref": "scope-001",
        field_name: invalid_value,
    }

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty when provided",
    ):
        KnowledgeEvidenceContext(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "logical_resource_ref",
        "revision_ref",
        "derivation_ref",
        "knowledge_unit_ref",
        "derived_artifact_ref",
        "affected_scope_ref",
    ),
)
def test_optional_reference_rejects_non_string_value(
    field_name: str,
) -> None:
    values = {
        "knowledge_scope_ref": "scope-001",
        field_name: 123,
    }

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string or None",
    ):
        KnowledgeEvidenceContext(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "logical_resource_ref",
        "revision_ref",
        "derivation_ref",
        "knowledge_unit_ref",
        "derived_artifact_ref",
        "affected_scope_ref",
    ),
)
def test_optional_reference_accepts_none(
    field_name: str,
) -> None:
    values = {
        "knowledge_scope_ref": "scope-001",
        field_name: None,
    }

    context = KnowledgeEvidenceContext(**values)

    assert getattr(context, field_name) is None


def test_affected_scope_can_exist_without_item_reference() -> None:
    context = KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        affected_scope_ref="affected-scope-001",
    )

    assert context.affected_scope_ref == "affected-scope-001"
    assert context.logical_resource_ref is None
    assert context.knowledge_unit_ref is None


def test_revision_and_derivation_references_are_independent() -> None:
    context = KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        revision_ref="revision-001",
        derivation_ref="derivation-001",
    )

    assert context.revision_ref == "revision-001"
    assert context.derivation_ref == "derivation-001"


def test_knowledge_evidence_context_equality_uses_all_fields() -> None:
    first_context = KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        revision_ref="revision-001",
    )
    second_context = KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
        revision_ref="revision-001",
    )

    assert first_context == second_context


def test_knowledge_evidence_context_is_immutable() -> None:
    context = KnowledgeEvidenceContext(
        knowledge_scope_ref="scope-001",
    )

    with pytest.raises(FrozenInstanceError):
        context.revision_ref = "revision-002"
