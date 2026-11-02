# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeSource contract.
#
# Responsibilities:
# - Validate logical Knowledge source identity.
# - Validate governed Knowledge scope references.
# - Validate provider-neutral source kinds.
# - Validate acquisition adapter references.
# - Validate optional configuration references.
# - Validate synchronization declarations.
# - Validate normalization and immutability.
#
# Must Not:
# - Test source acquisition.
# - Test physical source locations.
# - Test credentials or connection details.
# - Test synchronization execution.
# - Test parsing, chunking, indexing, or retrieval.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSource,
    KnowledgeSourceKind,
)


def _source() -> KnowledgeSource:
    return KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.FILE,
        adapter_ref="local-file-adapter",
    )


def test_create_minimal_knowledge_source() -> None:
    source = _source()

    assert source.source_id == "source-001"
    assert source.knowledge_scope_ref == "scope-001"
    assert source.source_kind == KnowledgeSourceKind.FILE
    assert source.adapter_ref == "local-file-adapter"
    assert source.configuration_ref is None
    assert source.synchronization_enabled is False


def test_create_complete_knowledge_source() -> None:
    source = KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.OBJECT_STORAGE,
        adapter_ref="object-storage-adapter",
        configuration_ref="source-config-001",
        synchronization_enabled=True,
    )

    assert source.configuration_ref == "source-config-001"
    assert source.synchronization_enabled is True


@pytest.mark.parametrize(
    "source_kind",
    tuple(KnowledgeSourceKind),
)
def test_all_source_kinds_are_supported(
    source_kind: KnowledgeSourceKind,
) -> None:
    source = KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=source_kind,
        adapter_ref="source-adapter",
    )

    assert source.source_kind == source_kind


def test_required_text_is_normalized() -> None:
    source = KnowledgeSource(
        source_id="  source-001  ",
        knowledge_scope_ref="  scope-001  ",
        source_kind=KnowledgeSourceKind.API,
        adapter_ref="  api-adapter  ",
    )

    assert source.source_id == "source-001"
    assert source.knowledge_scope_ref == "scope-001"
    assert source.adapter_ref == "api-adapter"


def test_configuration_ref_is_normalized() -> None:
    source = KnowledgeSource(
        source_id="source-001",
        knowledge_scope_ref="scope-001",
        source_kind=KnowledgeSourceKind.DATABASE,
        adapter_ref="database-adapter",
        configuration_ref="  config-001  ",
    )

    assert source.configuration_ref == "config-001"


@pytest.mark.parametrize(
    "field_name",
    (
        "source_id",
        "knowledge_scope_ref",
        "adapter_ref",
    ),
)
@pytest.mark.parametrize(
    "invalid_value",
    (
        "",
        "   ",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
    invalid_value: str,
) -> None:
    values = {
        "source_id": "source-001",
        "knowledge_scope_ref": "scope-001",
        "source_kind": KnowledgeSourceKind.FILE,
        "adapter_ref": "source-adapter",
    }
    values[field_name] = invalid_value

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        KnowledgeSource(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "source_id",
        "knowledge_scope_ref",
        "adapter_ref",
    ),
)
def test_required_text_rejects_non_string(
    field_name: str,
) -> None:
    values = {
        "source_id": "source-001",
        "knowledge_scope_ref": "scope-001",
        "source_kind": KnowledgeSourceKind.FILE,
        "adapter_ref": "source-adapter",
    }
    values[field_name] = 123

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        KnowledgeSource(**values)


def test_source_kind_rejects_non_enum_value() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "source_kind must be an instance of "
            "KnowledgeSourceKind"
        ),
    ):
        KnowledgeSource(
            source_id="source-001",
            knowledge_scope_ref="scope-001",
            source_kind="FILE",
            adapter_ref="source-adapter",
        )


@pytest.mark.parametrize(
    "configuration_ref",
    (
        "",
        "   ",
    ),
)
def test_configuration_ref_rejects_empty_value(
    configuration_ref: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "configuration_ref cannot be empty when provided"
        ),
    ):
        KnowledgeSource(
            source_id="source-001",
            knowledge_scope_ref="scope-001",
            source_kind=KnowledgeSourceKind.FILE,
            adapter_ref="source-adapter",
            configuration_ref=configuration_ref,
        )


def test_configuration_ref_rejects_non_string() -> None:
    with pytest.raises(
        TypeError,
        match="configuration_ref must be a string or None",
    ):
        KnowledgeSource(
            source_id="source-001",
            knowledge_scope_ref="scope-001",
            source_kind=KnowledgeSourceKind.FILE,
            adapter_ref="source-adapter",
            configuration_ref=123,
        )


@pytest.mark.parametrize(
    "invalid_value",
    (
        0,
        1,
        "true",
        None,
    ),
)
def test_synchronization_enabled_requires_bool(
    invalid_value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="synchronization_enabled must be a bool",
    ):
        KnowledgeSource(
            source_id="source-001",
            knowledge_scope_ref="scope-001",
            source_kind=KnowledgeSourceKind.FILE,
            adapter_ref="source-adapter",
            synchronization_enabled=invalid_value,
        )


def test_knowledge_source_is_immutable() -> None:
    source = _source()

    with pytest.raises(FrozenInstanceError):
        source.adapter_ref = "different-adapter"
