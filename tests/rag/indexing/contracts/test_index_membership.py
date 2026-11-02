# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF IndexMembership contract.
#
# Responsibilities:
# - Validate provider-neutral index membership construction.
# - Validate representation-to-index traceability.
# - Validate logical index identity and exact version preservation.
# - Validate Knowledge Unit and derivation provenance.
# - Validate Knowledge scope, resource, and revision provenance.
# - Validate representation-kind compatibility semantics.
# - Validate required text normalization.
# - Validate contract immutability.
#
# Must Not:
# - Perform physical index writes.
# - Test vector-database-specific behavior.
# - Test provider-specific collection or namespace semantics.
# - Test retrieval, reranking, or context construction.
# - Test index promotion, rollback, or lifecycle orchestration.
# - Test concurrency, batching, or NFT execution strategies.
# - Depend on external RAG or orchestration frameworks.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.indexing.contracts.index_membership import (
    IndexMembership,
)
from alhf.rag.representation.contracts.knowledge_representation import (
    RepresentationKind,
)


def _membership(
    *,
    representation_kind: RepresentationKind = (
        RepresentationKind.DENSE
    ),
) -> IndexMembership:
    return IndexMembership(
        membership_id="membership-001",
        index_ref="knowledge-index",
        index_version="v1",
        representation_ref="representation-001",
        representation_kind=representation_kind,
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
    )


def test_create_index_membership() -> None:
    membership = _membership()

    assert membership.membership_id == "membership-001"
    assert membership.index_ref == "knowledge-index"
    assert membership.index_version == "v1"
    assert membership.representation_ref == "representation-001"
    assert membership.representation_kind == RepresentationKind.DENSE


def test_membership_preserves_knowledge_unit_reference() -> None:
    membership = _membership()

    assert membership.knowledge_unit_ref == "unit-001"


def test_membership_preserves_derivation_identity() -> None:
    membership = _membership()

    assert membership.derivation_id == "derivation-001"


def test_membership_preserves_knowledge_scope() -> None:
    membership = _membership()

    assert membership.knowledge_scope_ref == "scope-001"


def test_membership_preserves_resource_provenance() -> None:
    membership = _membership()

    assert membership.resource_ref == "resource-001"
    assert membership.revision_ref == "revision-001"


@pytest.mark.parametrize(
    "representation_kind",
    tuple(RepresentationKind),
)
def test_all_representation_kinds_are_supported(
    representation_kind: RepresentationKind,
) -> None:
    membership = _membership(
        representation_kind=representation_kind,
    )

    assert membership.representation_kind == representation_kind


def test_required_text_values_are_normalized() -> None:
    membership = IndexMembership(
        membership_id="  membership-001  ",
        index_ref="  knowledge-index  ",
        index_version="  v1  ",
        representation_ref="  representation-001  ",
        representation_kind=RepresentationKind.DENSE,
        knowledge_unit_ref="  unit-001  ",
        derivation_id="  derivation-001  ",
        knowledge_scope_ref="  scope-001  ",
        resource_ref="  resource-001  ",
        revision_ref="  revision-001  ",
    )

    assert membership.membership_id == "membership-001"
    assert membership.index_ref == "knowledge-index"
    assert membership.index_version == "v1"
    assert membership.representation_ref == "representation-001"
    assert membership.knowledge_unit_ref == "unit-001"
    assert membership.derivation_id == "derivation-001"
    assert membership.knowledge_scope_ref == "scope-001"
    assert membership.resource_ref == "resource-001"
    assert membership.revision_ref == "revision-001"


def test_invalid_representation_kind_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "representation_kind must be an instance of "
            "RepresentationKind"
        ),
    ):
        IndexMembership(
            membership_id="membership-001",
            index_ref="knowledge-index",
            index_version="v1",
            representation_ref="representation-001",
            representation_kind="DENSE",
            knowledge_unit_ref="unit-001",
            derivation_id="derivation-001",
            knowledge_scope_ref="scope-001",
            resource_ref="resource-001",
            revision_ref="revision-001",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "membership_id",
        "index_ref",
        "index_version",
        "representation_ref",
        "knowledge_unit_ref",
        "derivation_id",
        "knowledge_scope_ref",
        "resource_ref",
        "revision_ref",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "membership_id": "membership-001",
        "index_ref": "knowledge-index",
        "index_version": "v1",
        "representation_ref": "representation-001",
        "representation_kind": RepresentationKind.DENSE,
        "knowledge_unit_ref": "unit-001",
        "derivation_id": "derivation-001",
        "knowledge_scope_ref": "scope-001",
        "resource_ref": "resource-001",
        "revision_ref": "revision-001",
    }

    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        IndexMembership(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "membership_id",
        "index_ref",
        "index_version",
        "representation_ref",
        "knowledge_unit_ref",
        "derivation_id",
        "knowledge_scope_ref",
        "resource_ref",
        "revision_ref",
    ),
)
def test_required_text_rejects_non_string(
    field_name: str,
) -> None:
    values = {
        "membership_id": "membership-001",
        "index_ref": "knowledge-index",
        "index_version": "v1",
        "representation_ref": "representation-001",
        "representation_kind": RepresentationKind.DENSE,
        "knowledge_unit_ref": "unit-001",
        "derivation_id": "derivation-001",
        "knowledge_scope_ref": "scope-001",
        "resource_ref": "resource-001",
        "revision_ref": "revision-001",
    }

    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        IndexMembership(**values)


def test_same_values_produce_equal_memberships() -> None:
    first = _membership()
    second = _membership()

    assert first == second


def test_different_index_version_produces_distinct_membership() -> None:
    first = _membership()

    second = IndexMembership(
        membership_id="membership-002",
        index_ref="knowledge-index",
        index_version="v2",
        representation_ref="representation-001",
        representation_kind=RepresentationKind.DENSE,
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
    )

    assert first != second
    assert first.index_version == "v1"
    assert second.index_version == "v2"


def test_same_representation_can_reference_different_index_versions() -> None:
    first = _membership()

    second = IndexMembership(
        membership_id="membership-v2",
        index_ref="knowledge-index",
        index_version="v2",
        representation_ref=first.representation_ref,
        representation_kind=first.representation_kind,
        knowledge_unit_ref=first.knowledge_unit_ref,
        derivation_id=first.derivation_id,
        knowledge_scope_ref=first.knowledge_scope_ref,
        resource_ref=first.resource_ref,
        revision_ref=first.revision_ref,
    )

    assert (
        first.representation_ref
        == second.representation_ref
    )
    assert first.index_version != second.index_version


def test_index_membership_is_immutable() -> None:
    membership = _membership()

    with pytest.raises(FrozenInstanceError):
        membership.index_version = "v2"
