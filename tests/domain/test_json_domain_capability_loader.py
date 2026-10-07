# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for JsonDomainCapabilityLoader.
#
# Responsibilities:
# - Validate JSON knowledge loading.
# - Validate DomainCapabilityMapping creation.
# - Validate LoaderResult integration.
# - Validate failure handling.
#
# Must Not:
# - Test capability selection.
# - Test orchestration.
# - Test workflow planning.
# - Test execution.
#
# Architectural Position:
# - Protects JSON knowledge adapter.
# - Validates Knowledge -> Runtime conversion.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from pathlib import Path

from src.alhf.domain.json_domain_capability_loader import (
    JsonDomainCapabilityLoader,
)


def test_load_domain_capability_mapping_success(
    tmp_path: Path,
) -> None:
    loader = (
        JsonDomainCapabilityLoader()
    )

    source_file = (
        tmp_path
        / "capabilities.json"
    )

    source_file.write_text(
        """
        {
            "domain_id": "travel",
            "capability_ids": [
                "hotel_search",
                "flight_search",
                "trip_planning"
            ]
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        source_file
    )

    assert result.loaded_count == 1

    mapping = result.loaded_items[0]

    assert mapping.domain_id == "travel"

    assert mapping.capability_count == 3


def test_missing_source_returns_warning(
    tmp_path: Path,
) -> None:
    loader = (
        JsonDomainCapabilityLoader()
    )

    missing_file = (
        tmp_path
        / "missing.json"
    )

    result = loader.load(
        missing_file
    )

    assert result.loaded_count == 0
    assert result.has_warnings is True


def test_capability_ids_loaded_correctly(
    tmp_path: Path,
) -> None:
    loader = (
        JsonDomainCapabilityLoader()
    )

    source_file = (
        tmp_path
        / "capabilities.json"
    )

    source_file.write_text(
        """
        {
            "domain_id": "travel",
            "capability_ids": [
                "hotel_search",
                "flight_search"
            ]
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        source_file
    )

    mapping = result.loaded_items[0]

    assert (
        mapping.capability_ids
        == (
            "hotel_search",
            "flight_search",
        )
    )


def test_contains_capability_after_load(
    tmp_path: Path,
) -> None:
    loader = (
        JsonDomainCapabilityLoader()
    )

    source_file = (
        tmp_path
        / "capabilities.json"
    )

    source_file.write_text(
        """
        {
            "domain_id": "travel",
            "capability_ids": [
                "hotel_search",
                "flight_search"
            ]
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        source_file
    )

    mapping = result.loaded_items[0]

    assert mapping.contains_capability(
        "hotel_search"
    )


def test_capability_absence_after_load(
    tmp_path: Path,
) -> None:
    loader = (
        JsonDomainCapabilityLoader()
    )

    source_file = (
        tmp_path
        / "capabilities.json"
    )

    source_file.write_text(
        """
        {
            "domain_id": "travel",
            "capability_ids": [
                "hotel_search"
            ]
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        source_file
    )

    mapping = result.loaded_items[0]

    assert not mapping.contains_capability(
        "provider_search"
    )


def test_invalid_json_raises_error(
    tmp_path: Path,
) -> None:
    loader = (
        JsonDomainCapabilityLoader()
    )

    source_file = (
        tmp_path
        / "capabilities.json"
    )

    source_file.write_text(
        "{ invalid json }",
        encoding="utf-8",
    )

    try:
        loader.load(
            source_file
        )
        assert False
    except Exception:
        assert True


def test_domain_id_loaded_correctly(
    tmp_path: Path,
) -> None:
    loader = (
        JsonDomainCapabilityLoader()
    )

    source_file = (
        tmp_path
        / "capabilities.json"
    )

    source_file.write_text(
        """
        {
            "domain_id": "healthcare",
            "capability_ids": [
                "provider_search"
            ]
        }
        """,
        encoding="utf-8",
    )

    result = loader.load(
        source_file
    )

    mapping = result.loaded_items[0]

    assert (
        mapping.domain_id
        == "healthcare"
    )
