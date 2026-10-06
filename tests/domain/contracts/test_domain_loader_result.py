# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for DomainLoaderResult.
#
# Responsibilities:
# - Verify domain loading result behavior.
# - Verify success and failure tracking.
# - Verify warning tracking.
# - Verify immutable contract behavior.
#
# Must Not:
# - Test domain loading logic.
# - Test filesystem behavior.
# - Test domain registry behavior.
# - Test orchestration behavior.
#
# Architectural Position:
# - Protects the domain loading contract.
# - Ensures stable loader responses across ALHF.
#
# Reuse Value:
# - Shared validation suite for all future
#   domain loading implementations.
#
# Future Extensibility:
# - Supports version-aware loading.
# - Supports warning reporting.
# - Supports partial load scenarios.

from dataclasses import FrozenInstanceError

import pytest

from src.alhf.domain.contracts.domain_definition import (
    DomainDefinition,
)
from src.alhf.domain.contracts.domain_loader_result import (
    DomainLoaderResult,
)


def test_create_empty_loader_result() -> None:
    result = DomainLoaderResult()

    assert result.loaded_count == 0
    assert result.failed_count == 0
    assert result.has_failures is False
    assert result.has_warnings is False
    assert result.is_successful is True


def test_loaded_count_returns_number_of_domains() -> None:
    result = DomainLoaderResult(
        loaded_domains=(
            DomainDefinition(
                domain_id="travel",
                domain_name="Travel",
                description="Travel domain.",
            ),
            DomainDefinition(
                domain_id="finance",
                domain_name="Finance",
                description="Finance domain.",
            ),
        )
    )

    assert result.loaded_count == 2


def test_failed_count_returns_number_of_failures() -> None:
    result = DomainLoaderResult(
        failed_domain_identifiers=(
            "travel",
            "finance",
        )
    )

    assert result.failed_count == 2


def test_has_failures_returns_true_when_failures_exist() -> None:
    result = DomainLoaderResult(
        failed_domain_identifiers=(
            "travel",
        )
    )

    assert result.has_failures is True


def test_has_failures_returns_false_when_no_failures_exist() -> None:
    result = DomainLoaderResult()

    assert result.has_failures is False


def test_has_warnings_returns_true_when_warnings_exist() -> None:
    result = DomainLoaderResult(
        warning_messages=(
            "Travel version mismatch.",
        )
    )

    assert result.has_warnings is True


def test_has_warnings_returns_false_when_no_warnings_exist() -> None:
    result = DomainLoaderResult()

    assert result.has_warnings is False


def test_is_successful_returns_true_when_no_failures_exist() -> None:
    result = DomainLoaderResult(
        loaded_domains=(
            DomainDefinition(
                domain_id="travel",
                domain_name="Travel",
                description="Travel domain.",
            ),
        )
    )

    assert result.is_successful is True


def test_is_successful_returns_false_when_failures_exist() -> None:
    result = DomainLoaderResult(
        failed_domain_identifiers=(
            "travel",
        )
    )

    assert result.is_successful is False


def test_loaded_domains_are_preserved() -> None:
    travel_domain = DomainDefinition(
        domain_id="travel",
        domain_name="Travel",
        description="Travel domain.",
    )

    finance_domain = DomainDefinition(
        domain_id="finance",
        domain_name="Finance",
        description="Finance domain.",
    )

    result = DomainLoaderResult(
        loaded_domains=(
            travel_domain,
            finance_domain,
        )
    )

    assert travel_domain in result.loaded_domains
    assert finance_domain in result.loaded_domains


def test_failed_domain_identifiers_are_preserved() -> None:
    result = DomainLoaderResult(
        failed_domain_identifiers=(
            "travel",
            "finance",
        )
    )

    assert result.failed_domain_identifiers == (
        "travel",
        "finance",
    )


def test_warning_messages_are_preserved() -> None:
    result = DomainLoaderResult(
        warning_messages=(
            "Travel warning.",
            "Finance warning.",
        )
    )

    assert result.warning_messages == (
        "Travel warning.",
        "Finance warning.",
    )


def test_domain_loader_result_is_immutable() -> None:
    result = DomainLoaderResult()

    with pytest.raises(FrozenInstanceError):
        result.loaded_domains = ()
