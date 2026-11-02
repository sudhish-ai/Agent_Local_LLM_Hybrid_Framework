# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Verifies bounded execution configuration for one ALHF Knowledge
# Foundation ingestion operation.
#
# Responsibilities:
# - Verify execution identity preservation and normalization.
# - Verify positive bounded acquisition configuration.
# - Verify invalid values are rejected.
# - Verify immutable execution configuration.

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from alhf.rag.runtime.contracts.knowledge_ingestion_execution_config import (
    KnowledgeIngestionExecutionConfig,
)


def test_preserves_execution_configuration() -> None:
    config = KnowledgeIngestionExecutionConfig(
        execution_id="execution-001",
        max_resources=100,
    )

    assert config.execution_id == "execution-001"
    assert config.max_resources == 100


def test_normalizes_execution_id() -> None:
    config = KnowledgeIngestionExecutionConfig(
        execution_id="  execution-001  ",
        max_resources=1,
    )

    assert config.execution_id == "execution-001"


@pytest.mark.parametrize(
    "execution_id",
    ["", "   "],
)
def test_rejects_empty_execution_id(
    execution_id: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="execution_id cannot be empty",
    ):
        KnowledgeIngestionExecutionConfig(
            execution_id=execution_id,
            max_resources=1,
        )


def test_rejects_non_string_execution_id() -> None:
    with pytest.raises(
        TypeError,
        match="execution_id must be a string",
    ):
        KnowledgeIngestionExecutionConfig(
            execution_id=123,  # type: ignore[arg-type]
            max_resources=1,
        )


@pytest.mark.parametrize(
    "max_resources",
    [0, -1],
)
def test_rejects_non_positive_max_resources(
    max_resources: int,
) -> None:
    with pytest.raises(
        ValueError,
        match="max_resources must be greater than zero",
    ):
        KnowledgeIngestionExecutionConfig(
            execution_id="execution-001",
            max_resources=max_resources,
        )


@pytest.mark.parametrize(
    "max_resources",
    [True, 1.5, "10", None],
)
def test_rejects_invalid_max_resources(
    max_resources: object,
) -> None:
    with pytest.raises(
        TypeError,
        match="max_resources must be an int",
    ):
        KnowledgeIngestionExecutionConfig(
            execution_id="execution-001",
            max_resources=max_resources,  # type: ignore[arg-type]
        )


def test_execution_configuration_is_immutable() -> None:
    config = KnowledgeIngestionExecutionConfig(
        execution_id="execution-001",
        max_resources=10,
    )

    with pytest.raises(FrozenInstanceError):
        config.max_resources = 20  # type: ignore[misc]
