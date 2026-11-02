# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeRepresentation contract.
#
# Responsibilities:
# - Validate provider-neutral representation construction.
# - Validate all universal representation kinds.
# - Validate Knowledge Unit and derivation provenance.
# - Validate Knowledge scope, resource, and revision provenance.
# - Validate representation payload and size semantics.
# - Validate strategy identity and version preservation.
# - Validate optional model identity and version semantics.
# - Validate required text normalization.
# - Validate representation immutability.
#
# Must Not:
# - Generate embeddings or representations.
# - Test representation providers or external frameworks.
# - Test vector-store-specific behavior.
# - Test indexing, retrieval, reranking, or context construction.
# - Assume dense vectors are the only representation type.
# - Test Representation Intelligence or adaptive selection.
# - Test concurrency or NFT execution strategies.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
    RepresentationKind,
)


def _representation(
    *,
    kind: RepresentationKind = RepresentationKind.DENSE,
    payload: bytes = b"representation-payload",
    model_ref: str | None = "embedding-model",
    model_version: str | None = "1.0",
) -> KnowledgeRepresentation:
    return KnowledgeRepresentation(
        representation_id="representation-001",
        knowledge_unit_ref="unit-001",
        derivation_id="derivation-001",
        knowledge_scope_ref="scope-001",
        resource_ref="resource-001",
        revision_ref="revision-001",
        kind=kind,
        payload=payload,
        media_type="application/octet-stream",
        strategy_ref="dense-representation",
        strategy_version="1.0",
        model_ref=model_ref,
        model_version=model_version,
    )


def test_create_knowledge_representation() -> None:
    representation = _representation()

    assert representation.representation_id == "representation-001"
    assert representation.knowledge_unit_ref == "unit-001"
    assert representation.derivation_id == "derivation-001"
    assert representation.knowledge_scope_ref == "scope-001"
    assert representation.resource_ref == "resource-001"
    assert representation.revision_ref == "revision-001"
    assert representation.kind == RepresentationKind.DENSE


def test_representation_preserves_payload() -> None:
    representation = _representation(
        payload=b"binary-representation",
    )

    assert representation.payload == b"binary-representation"


def test_size_bytes_reports_payload_size() -> None:
    payload = b"binary-representation"

    representation = _representation(
        payload=payload,
    )

    assert representation.size_bytes == len(payload)


def test_empty_payload_is_supported() -> None:
    representation = _representation(
        payload=b"",
    )

    assert representation.payload == b""
    assert representation.size_bytes == 0


@pytest.mark.parametrize(
    "kind",
    tuple(RepresentationKind),
)
def test_all_representation_kinds_are_supported(
    kind: RepresentationKind,
) -> None:
    representation = _representation(
        kind=kind,
    )

    assert representation.kind == kind


def test_representation_preserves_strategy_identity() -> None:
    representation = _representation()

    assert representation.strategy_ref == "dense-representation"
    assert representation.strategy_version == "1.0"


def test_representation_preserves_model_identity() -> None:
    representation = _representation()

    assert representation.model_ref == "embedding-model"
    assert representation.model_version == "1.0"


def test_representation_supports_no_model_identity() -> None:
    representation = _representation(
        model_ref=None,
        model_version=None,
    )

    assert representation.model_ref is None
    assert representation.model_version is None


def test_required_text_values_are_normalized() -> None:
    representation = KnowledgeRepresentation(
        representation_id="  representation-001  ",
        knowledge_unit_ref="  unit-001  ",
        derivation_id="  derivation-001  ",
        knowledge_scope_ref="  scope-001  ",
        resource_ref="  resource-001  ",
        revision_ref="  revision-001  ",
        kind=RepresentationKind.DENSE,
        payload=b"payload",
        media_type="  application/octet-stream  ",
        strategy_ref="  dense-representation  ",
        strategy_version="  1.0  ",
    )

    assert representation.representation_id == "representation-001"
    assert representation.knowledge_unit_ref == "unit-001"
    assert representation.derivation_id == "derivation-001"
    assert representation.knowledge_scope_ref == "scope-001"
    assert representation.resource_ref == "resource-001"
    assert representation.revision_ref == "revision-001"
    assert representation.media_type == "application/octet-stream"
    assert representation.strategy_ref == "dense-representation"
    assert representation.strategy_version == "1.0"


def test_model_identity_values_are_normalized() -> None:
    representation = _representation(
        model_ref="  embedding-model  ",
        model_version="  1.0  ",
    )

    assert representation.model_ref == "embedding-model"
    assert representation.model_version == "1.0"


def test_invalid_representation_kind_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="kind must be an instance of RepresentationKind",
    ):
        KnowledgeRepresentation(
            representation_id="representation-001",
            knowledge_unit_ref="unit-001",
            derivation_id="derivation-001",
            knowledge_scope_ref="scope-001",
            resource_ref="resource-001",
            revision_ref="revision-001",
            kind="DENSE",
            payload=b"payload",
            media_type="application/octet-stream",
            strategy_ref="dense-representation",
            strategy_version="1.0",
        )


def test_non_bytes_payload_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match="payload must be bytes",
    ):
        KnowledgeRepresentation(
            representation_id="representation-001",
            knowledge_unit_ref="unit-001",
            derivation_id="derivation-001",
            knowledge_scope_ref="scope-001",
            resource_ref="resource-001",
            revision_ref="revision-001",
            kind=RepresentationKind.DENSE,
            payload="invalid-payload",
            media_type="application/octet-stream",
            strategy_ref="dense-representation",
            strategy_version="1.0",
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "representation_id",
        "knowledge_unit_ref",
        "derivation_id",
        "knowledge_scope_ref",
        "resource_ref",
        "revision_ref",
        "media_type",
        "strategy_ref",
        "strategy_version",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
) -> None:
    values = {
        "representation_id": "representation-001",
        "knowledge_unit_ref": "unit-001",
        "derivation_id": "derivation-001",
        "knowledge_scope_ref": "scope-001",
        "resource_ref": "resource-001",
        "revision_ref": "revision-001",
        "kind": RepresentationKind.DENSE,
        "payload": b"payload",
        "media_type": "application/octet-stream",
        "strategy_ref": "dense-representation",
        "strategy_version": "1.0",
    }
    values[field_name] = "   "

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        KnowledgeRepresentation(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "representation_id",
        "knowledge_unit_ref",
        "derivation_id",
        "knowledge_scope_ref",
        "resource_ref",
        "revision_ref",
        "media_type",
        "strategy_ref",
        "strategy_version",
    ),
)
def test_required_text_rejects_non_string(
    field_name: str,
) -> None:
    values = {
        "representation_id": "representation-001",
        "knowledge_unit_ref": "unit-001",
        "derivation_id": "derivation-001",
        "knowledge_scope_ref": "scope-001",
        "resource_ref": "resource-001",
        "revision_ref": "revision-001",
        "kind": RepresentationKind.DENSE,
        "payload": b"payload",
        "media_type": "application/octet-stream",
        "strategy_ref": "dense-representation",
        "strategy_version": "1.0",
    }
    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        KnowledgeRepresentation(**values)


def test_model_ref_without_model_version_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "model_ref and model_version must be "
            "provided together"
        ),
    ):
        _representation(
            model_ref="embedding-model",
            model_version=None,
        )


def test_model_version_without_model_ref_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "model_ref and model_version must be "
            "provided together"
        ),
    ):
        _representation(
            model_ref=None,
            model_version="1.0",
        )


@pytest.mark.parametrize(
    ("model_ref", "model_version", "expected_field"),
    (
        ("   ", "1.0", "model_ref"),
        ("embedding-model", "   ", "model_version"),
    ),
)
def test_model_identity_rejects_empty_value(
    model_ref: str,
    model_version: str,
    expected_field: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{expected_field} cannot be empty",
    ):
        _representation(
            model_ref=model_ref,
            model_version=model_version,
        )


def test_knowledge_representation_is_immutable() -> None:
    representation = _representation()

    with pytest.raises(FrozenInstanceError):
        representation.strategy_version = "2.0"
