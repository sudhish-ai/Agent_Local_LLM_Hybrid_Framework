# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for BaseLoader.
#
# Responsibilities:
# - Validate reusable loader contract behavior.
# - Validate LoaderResult integration.
# - Validate loader inheritance model.
# - Validate source-driven loading.
#
# Must Not:
# - Test filesystem loading.
# - Test domain loading.
# - Test capability loading.
# - Test orchestration behavior.
#
# Architectural Position:
# - Protects BaseLoader abstraction.
# - Shared validation suite for future loader implementations.
#
# Reuse Value:
# - DomainLoader
# - CapabilityLoader
# - StrategyLoader
# - KnowledgeLoader
# - TemplateLoader
# - SolutionLoader
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from typing import Final

from src.alhf.core.contracts.loader_result import (
    LoaderResult,
)
from src.alhf.core.loaders.base_loader import (
    BaseLoader,
)


class DummyLoader(
    BaseLoader[str, str],
):
    """
    Minimal loader used for testing.
    """

    def load(
        self,
        source: str,
    ) -> LoaderResult[str]:
        return LoaderResult(
            loaded_items=(
                source,
                "finance",
            ),
        )


def test_load_returns_loader_result() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert isinstance(
        result,
        LoaderResult,
    )


def test_source_is_used_during_loading() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert result.loaded_items[0] == "travel"


def test_loaded_items_are_returned() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert result.loaded_items == (
        "travel",
        "finance",
    )


def test_loaded_count_is_correct() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert result.loaded_count == 2


def test_failed_count_is_zero() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert result.failed_count == 0


def test_is_successful_is_true() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert result.is_successful is True


def test_has_failures_is_false() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert result.has_failures is False


def test_has_warnings_is_false() -> None:
    loader = DummyLoader()

    result = loader.load("travel")

    assert result.has_warnings is False


def test_multiple_load_invocations_are_supported() -> None:
    loader = DummyLoader()

    first_result = loader.load("travel")
    second_result = loader.load("healthcare")

    assert first_result.loaded_items[0] == "travel"
    assert second_result.loaded_items[0] == "healthcare"


def test_loader_result_type_is_preserved() -> None:
    loader = DummyLoader()

    result: Final = loader.load("travel")

    assert result.loaded_items[0] == "travel"


def test_base_loader_supports_generic_item_and_source_types() -> None:
    class IntegerLoader(
        BaseLoader[int, int]
    ):
        def load(
            self,
            source: int,
        ) -> LoaderResult[int]:
            return LoaderResult(
                loaded_items=(
                    source,
                    source + 1,
                    source + 2,
                ),
            )

    loader = IntegerLoader()

    result = loader.load(1)

    assert result.loaded_items == (
        1,
        2,
        3,
    )

    assert result.loaded_count == 3
