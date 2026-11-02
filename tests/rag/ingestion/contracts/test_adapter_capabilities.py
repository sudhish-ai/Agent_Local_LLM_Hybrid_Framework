# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for the ALHF AdapterCapabilities contract.
#
# Responsibilities:
# - Validate default acquisition capabilities.
# - Validate explicitly enabled acquisition capabilities.
# - Validate synchronization capability dependencies.
# - Validate continuation and resume capability dependencies.
# - Validate strict boolean capability declarations.
# - Validate capability independence where appropriate.
# - Validate immutability.
#
# Must Not:
# - Test concrete Knowledge source adapters.
# - Test adapter registration or discovery.
# - Test provider-specific capabilities.
# - Test acquisition or synchronization execution.
# - Test parsing, chunking, embedding, indexing, or retrieval.
# - Test Standard RAG, GraphRAG, or Agentic RAG behavior.

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.ingestion.contracts.adapter_capabilities import (
    AdapterCapabilities,
)


def test_create_default_capabilities() -> None:
    capabilities = AdapterCapabilities()

    assert capabilities.supports_synchronization is False
    assert capabilities.supports_continuation is False
    assert capabilities.supports_incremental_changes is False
    assert capabilities.supports_deletion_detection is False
    assert capabilities.supports_resume is False


def test_create_fully_capable_adapter() -> None:
    capabilities = AdapterCapabilities(
        supports_synchronization=True,
        supports_continuation=True,
        supports_incremental_changes=True,
        supports_deletion_detection=True,
        supports_resume=True,
    )

    assert capabilities.supports_synchronization is True
    assert capabilities.supports_continuation is True
    assert capabilities.supports_incremental_changes is True
    assert capabilities.supports_deletion_detection is True
    assert capabilities.supports_resume is True


def test_synchronization_can_exist_without_incremental_changes() -> None:
    capabilities = AdapterCapabilities(
        supports_synchronization=True,
    )

    assert capabilities.supports_synchronization is True
    assert capabilities.supports_incremental_changes is False


def test_continuation_can_exist_without_resume() -> None:
    capabilities = AdapterCapabilities(
        supports_continuation=True,
    )

    assert capabilities.supports_continuation is True
    assert capabilities.supports_resume is False


def test_incremental_changes_require_synchronization() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "incremental changes require "
            "synchronization capability"
        ),
    ):
        AdapterCapabilities(
            supports_incremental_changes=True,
        )


def test_deletion_detection_requires_synchronization() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "deletion detection requires "
            "synchronization capability"
        ),
    ):
        AdapterCapabilities(
            supports_deletion_detection=True,
        )


def test_resume_requires_continuation() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "resume capability requires continuation capability"
        ),
    ):
        AdapterCapabilities(
            supports_resume=True,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "supports_synchronization",
        "supports_continuation",
        "supports_incremental_changes",
        "supports_deletion_detection",
        "supports_resume",
    ),
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
def test_capability_requires_boolean(
    field_name: str,
    invalid_value: object,
) -> None:
    values = {
        field_name: invalid_value,
    }

    with pytest.raises(
        TypeError,
        match=f"{field_name} must be a bool",
    ):
        AdapterCapabilities(
            **values,
        )


def test_incremental_changes_supported_with_synchronization() -> None:
    capabilities = AdapterCapabilities(
        supports_synchronization=True,
        supports_incremental_changes=True,
    )

    assert capabilities.supports_incremental_changes is True


def test_deletion_detection_supported_with_synchronization() -> None:
    capabilities = AdapterCapabilities(
        supports_synchronization=True,
        supports_deletion_detection=True,
    )

    assert capabilities.supports_deletion_detection is True


def test_resume_supported_with_continuation() -> None:
    capabilities = AdapterCapabilities(
        supports_continuation=True,
        supports_resume=True,
    )

    assert capabilities.supports_resume is True


def test_capability_equality_uses_all_fields() -> None:
    first = AdapterCapabilities(
        supports_synchronization=True,
        supports_continuation=True,
    )
    second = AdapterCapabilities(
        supports_synchronization=True,
        supports_continuation=True,
    )

    assert first == second


def test_different_capabilities_are_not_equal() -> None:
    first = AdapterCapabilities(
        supports_synchronization=True,
    )
    second = AdapterCapabilities(
        supports_continuation=True,
    )

    assert first != second


def test_adapter_capabilities_is_immutable() -> None:
    capabilities = AdapterCapabilities()

    with pytest.raises(FrozenInstanceError):
        capabilities.supports_continuation = True
