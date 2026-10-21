# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for LoaderResult.
#
# Responsibilities:
# - Validate generic loader result behavior.
# - Validate loading statistics.
# - Validate warning tracking.
# - Validate failure tracking.
# - Validate immutability guarantees.
#
# Must Not:
# - Test domain loading logic.
# - Test capability loading logic.
# - Test filesystem behavior.
# - Test orchestration behavior.
#
# Architectural Position:
# - Protects ALHF generic loader contract.
# - Shared across all future loader implementations.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from dataclasses import FrozenInstanceError

import pytest

from src.alhf.core.contracts.loader_result import LoaderResult


def test_create_empty_loader_result() -> None:
    result = LoaderResult()

    assert result.loaded_count == 0
    assert result.failed_count == 0
    assert result.has_failures is False
    assert result.has_warnings is False
    assert result.is_successful is True


def test_loaded_count_returns_number_of_items() -> None:
    result = LoaderResult(
        loaded_items=(
            "travel",
            "finance",
        )
    )

    assert result.loaded_count == 2


def test_failed_count_returns_number_of_failures() -> None:
    result = LoaderResult(
        failed_identifiers=(
            "travel",
            "finance",
        )
    )

    assert result.failed_count == 2


def test_has_failures_returns_true_when_failures_exist() -> None:
    result = LoaderResult(
        failed_identifiers=(
            "travel",
        )
    )

    assert result.has_failures is True


def test_has_failures_returns_false_when_no_failures_exist() -> None:
    result = LoaderResult()

    assert result.has_failures is False


def test_has_warnings_returns_true_when_warnings_exist() -> None:
    result = LoaderResult(
        warning_messages=(
            "Version mismatch.",
        )
    )

    assert result.has_warnings is True


def test_has_warnings_returns_false_when_no_warnings_exist() -> None:
    result = LoaderResult()

    assert result.has_warnings is False


def test_is_successful_returns_true_when_no_failures_exist() -> None:
    result = LoaderResult(
        loaded_items=(
            "travel",
        )
    )

    assert result.is_successful is True


def test_is_successful_returns_false_when_failures_exist() -> None:
    result = LoaderResult(
        failed_identifiers=(
            "travel",
        )
    )

    assert result.is_successful is False


def test_loaded_items_are_preserved() -> None:
    result = LoaderResult(
        loaded_items=(
            "travel",
            "finance",
        )
    )

    assert result.loaded_items == (
        "travel",
        "finance",
    )


def test_failed_identifiers_are_preserved() -> None:
    result = LoaderResult(
        failed_identifiers=(
            "travel",
            "finance",
        )
    )

    assert result.failed_identifiers == (
        "travel",
        "finance",
    )


def test_warning_messages_are_preserved() -> None:
    result = LoaderResult(
        warning_messages=(
            "Warning One",
            "Warning Two",
        )
    )

    assert result.warning_messages == (
        "Warning One",
        "Warning Two",
    )


def test_loader_result_is_immutable() -> None:
    result = LoaderResult()

    with pytest.raises(FrozenInstanceError):
        result.loaded_items = ()
