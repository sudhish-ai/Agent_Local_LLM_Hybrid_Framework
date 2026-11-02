# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF ResourceIdentity contract.
#
# Responsibilities:
# - Validate governed Knowledge scope identity.
# - Validate source identity preservation.
# - Validate logical resource identity.
# - Validate exact resource revision identity.
# - Validate logical-resource and revision separation.
# - Validate identity normalization.
# - Validate invalid identity rejection.
# - Validate convenience reference properties.
# - Validate immutability.
#
# Must Not:
# - Test resource acquisition.
# - Test revision generation.
# - Test content hashing.
# - Test synchronization or change detection.
# - Test parsing, chunking, indexing, or retrieval.
# - Test physical source locations.
# - Test provider-specific behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.resource_identity import (
    ResourceIdentity,
)


def _identity() -> ResourceIdentity:
    return ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )


def test_create_resource_identity() -> None:
    identity = _identity()

    assert identity.knowledge_scope_ref == "scope-001"
    assert identity.source_ref == "source-001"
    assert identity.logical_resource_id == "resource-001"
    assert identity.revision_id == "revision-001"


def test_identity_values_are_whitespace_normalized() -> None:
    identity = ResourceIdentity(
        knowledge_scope_ref="  scope-001  ",
        source_ref="  source-001  ",
        logical_resource_id="  resource-001  ",
        revision_id="  revision-001  ",
    )

    assert identity.knowledge_scope_ref == "scope-001"
    assert identity.source_ref == "source-001"
    assert identity.logical_resource_id == "resource-001"
    assert identity.revision_id == "revision-001"


def test_resource_ref_returns_logical_resource_identity() -> None:
    identity = _identity()

    assert identity.resource_ref == "resource-001"


def test_revision_ref_returns_exact_revision_identity() -> None:
    identity = _identity()

    assert identity.revision_ref == "revision-001"


def test_same_logical_resource_supports_different_revisions() -> None:
    first = ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )
    second = ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-002",
    )

    assert first.logical_resource_id == second.logical_resource_id
    assert first.revision_id != second.revision_id


def test_different_resources_can_belong_to_same_source() -> None:
    first = ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )
    second = ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-002",
        revision_id="revision-001",
    )

    assert first.source_ref == second.source_ref
    assert first.logical_resource_id != second.logical_resource_id


def test_same_resource_identifier_can_exist_in_different_scopes() -> None:
    first = ResourceIdentity(
        knowledge_scope_ref="scope-a",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )
    second = ResourceIdentity(
        knowledge_scope_ref="scope-b",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-001",
    )

    assert (
        first.knowledge_scope_ref
        != second.knowledge_scope_ref
    )


@pytest.mark.parametrize(
    "field_name",
    (
        "knowledge_scope_ref",
        "source_ref",
        "logical_resource_id",
        "revision_id",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        "",
        "   ",
    ),
)
def test_identity_field_rejects_empty_value(
    field_name: str,
    invalid_value: str,
) -> None:
    values = {
        "knowledge_scope_ref": "scope-001",
        "source_ref": "source-001",
        "logical_resource_id": "resource-001",
        "revision_id": "revision-001",
    }
    values[field_name] = invalid_value

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        ResourceIdentity(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "knowledge_scope_ref",
        "source_ref",
        "logical_resource_id",
        "revision_id",
    ),
)
def test_identity_field_rejects_non_string_value(
    field_name: str,
) -> None:
    values = {
        "knowledge_scope_ref": "scope-001",
        "source_ref": "source-001",
        "logical_resource_id": "resource-001",
        "revision_id": "revision-001",
    }
    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        ResourceIdentity(**values)


def test_equal_resource_identities_are_equal() -> None:
    first = _identity()
    second = _identity()

    assert first == second


def test_different_revision_changes_identity() -> None:
    first = _identity()
    second = ResourceIdentity(
        knowledge_scope_ref="scope-001",
        source_ref="source-001",
        logical_resource_id="resource-001",
        revision_id="revision-002",
    )

    assert first != second


def test_resource_identity_is_immutable() -> None:
    identity = _identity()

    with pytest.raises(FrozenInstanceError):
        identity.revision_id = "revision-002"
