# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF KnowledgeRequest contract.
#
# Responsibilities:
# - Validate immutable Knowledge request construction.
# - Validate Knowledge scope and query preservation.
# - Validate logical index identity and version.
# - Validate bounded retrieval configuration.
# - Validate bounded Context configuration.
# - Validate required text normalization.
# - Validate invalid request inputs.
#
# Must Not:
# - Execute retrieval or indexing.
# - Select providers or retrieval strategies.
# - Construct Evidence or Context.
# - Generate prompts or invoke models.
# - Test adaptive Knowledge Intelligence.
# - Depend on external RAG frameworks.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.knowledge_request.contracts.knowledge_request import (
    KnowledgeRequest,
)


def _request(
    **overrides,
) -> KnowledgeRequest:
    values = {
        "request_id": "request-001",
        "knowledge_scope_ref": "scope-001",
        "query": "enterprise authentication policy",
        "index_ref": "knowledge-index",
        "index_version": "v1",
        "retrieval_limit": 5,
        "max_context_bytes": 4096,
    }
    values.update(
        overrides
    )

    return KnowledgeRequest(
        **values
    )


def test_create_knowledge_request() -> None:
    request = _request()

    assert request.request_id == "request-001"
    assert request.knowledge_scope_ref == "scope-001"
    assert request.query == "enterprise authentication policy"
    assert request.index_ref == "knowledge-index"
    assert request.index_version == "v1"
    assert request.retrieval_limit == 5
    assert request.max_context_bytes == 4096


def test_required_text_values_are_normalized() -> None:
    request = _request(
        request_id="  request-001  ",
        knowledge_scope_ref="  scope-001  ",
        query="  enterprise policy  ",
        index_ref="  knowledge-index  ",
        index_version="  v1  ",
    )

    assert request.request_id == "request-001"
    assert request.knowledge_scope_ref == "scope-001"
    assert request.query == "enterprise policy"
    assert request.index_ref == "knowledge-index"
    assert request.index_version == "v1"


@pytest.mark.parametrize(
    "field_name",
    (
        "request_id",
        "knowledge_scope_ref",
        "query",
        "index_ref",
        "index_version",
    ),
)
def test_required_text_rejects_empty_value(
    field_name: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty",
    ):
        _request(
            **{
                field_name: "   ",
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "request_id",
        "knowledge_scope_ref",
        "query",
        "index_ref",
        "index_version",
    ),
)
def test_required_text_rejects_non_string(
    field_name: str,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string",
    ):
        _request(
            **{
                field_name: 123,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "retrieval_limit",
        "max_context_bytes",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        0,
        -1,
    ),
)
def test_bounded_value_must_be_positive(
    field_name: str,
    value: int,
) -> None:
    with pytest.raises(
        ValueError,
        match=f"{field_name} must be greater than zero",
    ):
        _request(
            **{
                field_name: value,
            }
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "retrieval_limit",
        "max_context_bytes",
    ),
)
@pytest.mark.parametrize(
    "value",
    (
        True,
        1.5,
        "5",
        None,
    ),
)
def test_bounded_value_must_be_integer(
    field_name: str,
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match=f"{field_name} must be an int",
    ):
        _request(
            **{
                field_name: value,
            }
        )


def test_knowledge_request_is_immutable() -> None:
    request = _request()

    with pytest.raises(FrozenInstanceError):
        request.query = "changed query"
