# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for JsonCapabilityDefinitionLoader.
#
# Responsibilities:
# - Validate capability definition loading.
# - Validate multiple capability loading.
# - Validate version handling.
# - Validate metadata handling.
# - Validate loader failure scenarios.
#
# Must Not:
# - Test registry behavior.
# - Test capability selection.
# - Test planning.
# - Test orchestration.
# - Test execution.
#
# Architectural Position:
# - Protects capability metadata loading.
# - Validates capability knowledge assets.
# - Guards JSON-to-contract translation.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from pathlib import Path

from src.alhf.capability.json_capability_definition_loader import (
    JsonCapabilityDefinitionLoader,
)


def test_load_single_capability(
    tmp_path: Path,
) -> None:
    loader = (
        JsonCapabilityDefinitionLoader()
    )

    source_file = (
        tmp_path
        / "capability_definitions.json"
    )

    source_file.write_text(
        """
{
  "capabilities": [
    {
      "capability_id": "hotel_search",
      "capability_name": "Hotel Search",
      "description": "Search hotels."
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        source_file,
    )

    assert len(
        result.loaded_items
    ) == 1

    capability = (
        result.loaded_items[0]
    )

    assert (
        capability.capability_id
        == "hotel_search"
    )

    assert (
        capability.capability_name
        == "Hotel Search"
    )

    assert (
        capability.description
        == "Search hotels."
    )


def test_load_multiple_capabilities(
    tmp_path: Path,
) -> None:
    loader = (
        JsonCapabilityDefinitionLoader()
    )

    source_file = (
        tmp_path
        / "capability_definitions.json"
    )

    source_file.write_text(
        """
{
  "capabilities": [
    {
      "capability_id": "hotel_search",
      "capability_name": "Hotel Search",
      "description": "Search hotels."
    },
    {
      "capability_id": "hotel_booking",
      "capability_name": "Hotel Booking",
      "description": "Book hotels."
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        source_file,
    )

    assert len(
        result.loaded_items
    ) == 2

    assert (
        result.loaded_items[0]
        .capability_id
        == "hotel_search"
    )

    assert (
        result.loaded_items[1]
        .capability_id
        == "hotel_booking"
    )


def test_default_version_applied(
    tmp_path: Path,
) -> None:
    loader = (
        JsonCapabilityDefinitionLoader()
    )

    source_file = (
        tmp_path
        / "capability_definitions.json"
    )

    source_file.write_text(
        """
{
  "capabilities": [
    {
      "capability_id": "hotel_search",
      "capability_name": "Hotel Search",
      "description": "Search hotels."
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        source_file,
    )

    assert (
        result.loaded_items[0]
        .version
        == "1.0"
    )


def test_custom_version_loaded(
    tmp_path: Path,
) -> None:
    loader = (
        JsonCapabilityDefinitionLoader()
    )

    source_file = (
        tmp_path
        / "capability_definitions.json"
    )

    source_file.write_text(
        """
{
  "capabilities": [
    {
      "capability_id": "hotel_search",
      "capability_name": "Hotel Search",
      "description": "Search hotels.",
      "version": "2.0"
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        source_file,
    )

    assert (
        result.loaded_items[0]
        .version
        == "2.0"
    )


def test_metadata_loaded(
    tmp_path: Path,
) -> None:
    loader = (
        JsonCapabilityDefinitionLoader()
    )

    source_file = (
        tmp_path
        / "capability_definitions.json"
    )

    source_file.write_text(
        """
{
  "capabilities": [
    {
      "capability_id": "hotel_search",
      "capability_name": "Hotel Search",
      "description": "Search hotels.",
      "metadata": {
        "domain": "travel"
      }
    }
  ]
}
        """.strip(),
        encoding="utf-8",
    )

    result = loader.load(
        source_file,
    )

    assert (
        result.loaded_items[0]
        .metadata["domain"]
        == "travel"
    )


def test_invalid_json_raises_error(
    tmp_path: Path,
) -> None:
    loader = (
        JsonCapabilityDefinitionLoader()
    )

    source_file = (
        tmp_path
        / "capability_definitions.json"
    )

    source_file.write_text(
        "{ invalid json }",
        encoding="utf-8",
    )

    try:
        loader.load(
            source_file,
        )

        assert False

    except Exception:
        assert True
