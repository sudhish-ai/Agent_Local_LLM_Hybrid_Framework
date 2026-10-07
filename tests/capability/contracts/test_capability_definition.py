# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for CapabilityDefinition.
#
# Responsibilities:
# - Validate capability contract creation.
# - Validate field initialization.
# - Validate immutable behavior.
# - Validate contract validation rules.
#
# Must Not:
# - Test capability registry behavior.
# - Test workflow planning behavior.
# - Test orchestration behavior.
# - Test runtime execution behavior.
#
# Architectural Position:
# - Protects ALHF capability contract.
# - Ensures consistent capability definitions
#   across all domains.
#
# Reuse Value:
# - Shared validation suite for all future
#   capability definitions.
#
# Future Extensibility:
# - Capability metadata.
# - Capability versioning.
# - Capability dependencies.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from dataclasses import FrozenInstanceError

import pytest

from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)


def test_create_capability_definition_success() -> None:
    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
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

    assert capability.version == "1.0"


def test_metadata_defaults_to_empty_mapping() -> None:
    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    assert capability.metadata == {}


def test_custom_metadata_is_supported() -> None:
    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
        metadata={
            "owner": "travel",
            "category": "search",
        },
    )

    assert (
        capability.metadata["owner"]
        == "travel"
    )

    assert (
        capability.metadata["category"]
        == "search"
    )


def test_empty_capability_id_raises_error() -> None:
    with pytest.raises(ValueError):
        CapabilityDefinition(
            capability_id="",
            capability_name="Hotel Search",
            description="Search hotels.",
        )


def test_whitespace_capability_id_raises_error() -> None:
    with pytest.raises(ValueError):
        CapabilityDefinition(
            capability_id="   ",
            capability_name="Hotel Search",
            description="Search hotels.",
        )


def test_empty_capability_name_raises_error() -> None:
    with pytest.raises(ValueError):
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="",
            description="Search hotels.",
        )


def test_whitespace_capability_name_raises_error() -> None:
    with pytest.raises(ValueError):
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="   ",
            description="Search hotels.",
        )


def test_empty_description_raises_error() -> None:
    with pytest.raises(ValueError):
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="",
        )


def test_whitespace_description_raises_error() -> None:
    with pytest.raises(ValueError):
        CapabilityDefinition(
            capability_id="hotel_search",
            capability_name="Hotel Search",
            description="   ",
        )


def test_default_version_is_assigned() -> None:
    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    assert capability.version == "1.0"


def test_custom_version_is_supported() -> None:
    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
        version="2.0",
    )

    assert capability.version == "2.0"


def test_capability_definition_is_immutable() -> None:
    capability = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    with pytest.raises(
        FrozenInstanceError
    ):
        capability.capability_name = (
            "Modified Capability"
        )
