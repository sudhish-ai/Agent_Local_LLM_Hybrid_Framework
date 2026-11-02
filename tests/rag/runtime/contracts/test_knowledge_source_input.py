# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the minimal KnowledgeSourceInput runtime contract.
#
# Responsibilities:
# - Validate the source-only customer input boundary.
# - Validate source normalization and required-value handling.
# - Validate immutability.
# - Protect the contract from technical RAG configuration coupling.
#
# Must Not:
# - Interpret source technology or media type.
# - Access the filesystem or network.
# - Configure adapters, parsers, strategies, providers, or indexes.
# - Encode Standard RAG, GraphRAG, or Agentic RAG behavior.

from dataclasses import FrozenInstanceError, fields

import pytest

from alhf.rag.runtime.contracts.knowledge_source_input import (
    KnowledgeSourceInput,
)


def test_source_input_preserves_source() -> None:
    source = KnowledgeSourceInput(
        source="D:/CompanyKnowledge",
    )

    assert source.source == "D:/CompanyKnowledge"


def test_source_input_normalizes_surrounding_whitespace() -> None:
    source = KnowledgeSourceInput(
        source="  D:/CompanyKnowledge  ",
    )

    assert source.source == "D:/CompanyKnowledge"


@pytest.mark.parametrize(
    "value",
    (
        "",
        "   ",
        "\t\n",
    ),
)
def test_source_input_rejects_empty_source(
    value: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="source cannot be empty",
    ):
        KnowledgeSourceInput(
            source=value,
        )


@pytest.mark.parametrize(
    "value",
    (
        None,
        123,
        True,
        b"source",
    ),
)
def test_source_input_rejects_non_string_source(
    value: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="source must be a string",
    ):
        KnowledgeSourceInput(
            source=value,
        )


def test_source_input_does_not_interpret_local_path() -> None:
    value = "D:/CompanyKnowledge/policy.pdf"

    source = KnowledgeSourceInput(
        source=value,
    )

    assert source.source == value


def test_source_input_does_not_interpret_uri() -> None:
    value = "https://knowledge.example/source"

    source = KnowledgeSourceInput(
        source=value,
    )

    assert source.source == value


def test_source_input_has_only_customer_source_field() -> None:
    contract_fields = tuple(
        field.name
        for field in fields(
            KnowledgeSourceInput
        )
    )

    assert contract_fields == (
        "source",
    )


def test_source_input_is_immutable() -> None:
    source = KnowledgeSourceInput(
        source="D:/CompanyKnowledge",
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        source.source = "changed"


def test_equivalent_normalized_inputs_are_equal() -> None:
    first = KnowledgeSourceInput(
        source="D:/CompanyKnowledge",
    )

    second = KnowledgeSourceInput(
        source="  D:/CompanyKnowledge  ",
    )

    assert first == second
