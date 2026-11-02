# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF AcquisitionRequest contract.
#
# Responsibilities:
# - Validate bounded Knowledge acquisition requests.
# - Validate logical KnowledgeSource composition.
# - Validate positive resource-count bounds.
# - Validate continuation references.
# - Validate synchronization checkpoint references.
# - Validate reference normalization.
# - Validate convenience source and scope properties.
# - Validate immutability.
#
# Must Not:
# - Test physical source acquisition.
# - Test provider-specific pagination.
# - Test synchronization execution.
# - Test parsing, chunking, indexing, or retrieval.
# - Test credentials or provider configuration.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.acquisition_request import (
    AcquisitionRequest,
)
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


def test_create_minimal_acquisition_request() -> None:
    source = _source()

    request = AcquisitionRequest(
        source=source,
        max_resources=100,
    )

    assert request.source is source
    assert request.max_resources == 100
    assert request.continuation_ref is None
    assert request.checkpoint_ref is None


def test_create_complete_acquisition_request() -> None:
    request = AcquisitionRequest(
        source=_source(),
        max_resources=250,
        continuation_ref="continuation-001",
        checkpoint_ref="checkpoint-001",
    )

    assert request.max_resources == 250
    assert request.continuation_ref == "continuation-001"
    assert request.checkpoint_ref == "checkpoint-001"


def test_source_id_returns_logical_source_identity() -> None:
    request = AcquisitionRequest(
        source=_source(),
        max_resources=100,
    )

    assert request.source_id == "source-001"


def test_knowledge_scope_ref_returns_source_scope() -> None:
    request = AcquisitionRequest(
        source=_source(),
        max_resources=100,
    )

    assert request.knowledge_scope_ref == "scope-001"


def test_optional_references_are_normalized() -> None:
    request = AcquisitionRequest(
        source=_source(),
        max_resources=100,
        continuation_ref="  continuation-001  ",
        checkpoint_ref="  checkpoint-001  ",
    )

    assert request.continuation_ref == "continuation-001"
    assert request.checkpoint_ref == "checkpoint-001"


def test_single_resource_bound_is_supported() -> None:
    request = AcquisitionRequest(
        source=_source(),
        max_resources=1,
    )

    assert request.max_resources == 1


def test_source_rejects_invalid_contract() -> None:
    with pytest.raises(
        TypeError,
        match="source must be an instance of KnowledgeSource",
    ):
        AcquisitionRequest(
            source="invalid-source",
            max_resources=100,
        )


@pytest.mark.parametrize(
    "max_resources",
    (
        0,
        -1,
        -100,
    ),
)
def test_max_resources_rejects_non_positive_value(
    max_resources: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_resources must be greater than zero",
    ):
        AcquisitionRequest(
            source=_source(),
            max_resources=max_resources,
        )


@pytest.mark.parametrize(
    "max_resources",
    (
        True,
        False,
        1.5,
        "100",
        None,
    ),
)
def test_max_resources_rejects_non_integer_value(
    max_resources: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="max_resources must be an int",
    ):
        AcquisitionRequest(
            source=_source(),
            max_resources=max_resources,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "continuation_ref",
        "checkpoint_ref",
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
        "source": _source(),
        "max_resources": 100,
        field_name: invalid_value,
    }

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be empty when provided",
    ):
        AcquisitionRequest(**values)


@pytest.mark.parametrize(
    "field_name",
    (
        "continuation_ref",
        "checkpoint_ref",
    ),
)
def test_optional_reference_rejects_non_string_value(
    field_name: str,
) -> None:
    values = {
        "source": _source(),
        "max_resources": 100,
        field_name: 123,
    }

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a string or None",
    ):
        AcquisitionRequest(**values)


def test_acquisition_request_is_immutable() -> None:
    request = AcquisitionRequest(
        source=_source(),
        max_resources=100,
    )

    with pytest.raises(FrozenInstanceError):
        request.max_resources = 200
