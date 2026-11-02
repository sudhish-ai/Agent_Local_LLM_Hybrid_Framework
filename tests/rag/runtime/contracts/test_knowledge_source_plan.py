# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the governed KnowledgeSourcePlan runtime contract.
#
# Responsibilities:
# - Validate governed source-plan identity and normalization.
# - Validate source-kind and synchronization semantics.
# - Validate conversion to the existing KnowledgeSource contract.
# - Protect the plan from parser, representation, index, and RAG coupling.
#
# Must Not:
# - Perform source interpretation.
# - Execute acquisition or other Knowledge stages.
# - Contain parser, derivation, representation, or index configuration.
# - Introduce Standard RAG, GraphRAG, or Agentic RAG semantics.

from dataclasses import FrozenInstanceError, fields

import pytest

from alhf.rag.ingestion.contracts.knowledge_source import (
    KnowledgeSourceKind,
)
from alhf.rag.runtime.contracts.knowledge_source_plan import (
    KnowledgeSourcePlan,
)


def _plan(
    **overrides,
) -> KnowledgeSourcePlan:
    values = {
        "source_id": "source-001",
        "knowledge_scope_ref": "scope-001",
        "source_kind": KnowledgeSourceKind.FILE,
        "adapter_ref": "local-file",
        "configuration_ref": None,
        "synchronization_enabled": False,
    }

    values.update(
        overrides
    )

    return KnowledgeSourcePlan(
        **values
    )


def test_plan_preserves_governed_source_semantics() -> None:
    plan = _plan(
        configuration_ref="config-001"
    )

    assert plan.source_id == "source-001"
    assert plan.knowledge_scope_ref == "scope-001"
    assert plan.source_kind == KnowledgeSourceKind.FILE
    assert plan.adapter_ref == "local-file"
    assert plan.configuration_ref == "config-001"
    assert plan.synchronization_enabled is False


def test_required_text_is_normalized() -> None:
    plan = _plan(
        source_id="  source-001  ",
        knowledge_scope_ref="  scope-001  ",
        adapter_ref="  local-file  ",
    )

    assert plan.source_id == "source-001"
    assert plan.knowledge_scope_ref == "scope-001"
    assert plan.adapter_ref == "local-file"


@pytest.mark.parametrize(
    "field_name",
    (
        "source_id",
        "knowledge_scope_ref",
        "adapter_ref",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        _plan(
            **{
                field_name: "   ",
            }
        )


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
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        _plan(
            **{
                field_name: 123,
            }
        )


def test_source_kind_requires_governed_enum() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "source_kind must be an instance of "
            "KnowledgeSourceKind"
        ),
    ):
        _plan(
            source_kind="FILE"
        )


def test_optional_configuration_ref_is_normalized() -> None:
    plan = _plan(
        configuration_ref="  config-001  "
    )

    assert plan.configuration_ref == "config-001"


def test_empty_configuration_ref_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "configuration_ref cannot be empty "
            "when provided"
        ),
    ):
        _plan(
            configuration_ref="   "
        )


def test_non_string_configuration_ref_is_rejected() -> None:
    with pytest.raises(
        TypeError,
        match=(
            "configuration_ref must be a string or None"
        ),
    ):
        _plan(
            configuration_ref=123
        )


@pytest.mark.parametrize(
    "value",
    (
        0,
        1,
        "false",
        None,
    ),
)
def test_synchronization_enabled_requires_bool(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=(
            "synchronization_enabled must be a bool"
        ),
    ):
        _plan(
            synchronization_enabled=value
        )


def test_plan_converts_to_existing_knowledge_source_contract() -> None:
    plan = _plan(
        configuration_ref="config-001",
        synchronization_enabled=True,
    )

    source = plan.to_knowledge_source()

    assert source.source_id == plan.source_id
    assert (
        source.knowledge_scope_ref
        == plan.knowledge_scope_ref
    )
    assert source.source_kind == plan.source_kind
    assert source.adapter_ref == plan.adapter_ref
    assert (
        source.configuration_ref
        == plan.configuration_ref
    )
    assert source.synchronization_enabled is True


def test_plan_contains_only_source_interpretation_fields() -> None:
    names = tuple(
        field.name
        for field in fields(
            KnowledgeSourcePlan
        )
    )

    assert names == (
        "source_id",
        "knowledge_scope_ref",
        "source_kind",
        "adapter_ref",
        "configuration_ref",
        "synchronization_enabled",
    )


def test_plan_exposes_no_rag_strategy_configuration() -> None:
    names = {
        field.name
        for field in fields(
            KnowledgeSourcePlan
        )
    }

    forbidden = {
        "parser",
        "chunk_size",
        "overlap",
        "embedding_model",
        "representation_provider",
        "index_ref",
        "retrieval_strategy",
        "rag_type",
    }

    assert names.isdisjoint(
        forbidden
    )


def test_plan_is_immutable() -> None:
    plan = _plan()

    with pytest.raises(
        FrozenInstanceError
    ):
        plan.adapter_ref = "changed"
