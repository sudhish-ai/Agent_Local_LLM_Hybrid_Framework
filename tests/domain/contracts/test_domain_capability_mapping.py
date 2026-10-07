# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT

from dataclasses import FrozenInstanceError

import pytest

from src.alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)


def test_create_mapping_success() -> None:
    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
        ),
    )

    assert mapping.domain_id == "travel"

    assert mapping.capability_ids == (
        "hotel_search",
        "flight_search",
    )


def test_capability_count_returns_correct_value() -> None:
    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
            "trip_planning",
        ),
    )

    assert mapping.capability_count == 3


def test_contains_capability_returns_true() -> None:
    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
        ),
    )

    assert mapping.contains_capability(
        "hotel_search",
    )


def test_contains_capability_returns_false() -> None:
    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
        ),
    )

    assert not mapping.contains_capability(
        "provider_search",
    )


def test_empty_domain_id_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainCapabilityMapping(
            domain_id="",
            capability_ids=(
                "hotel_search",
            ),
        )


def test_whitespace_domain_id_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainCapabilityMapping(
            domain_id="   ",
            capability_ids=(
                "hotel_search",
            ),
        )


def test_empty_capability_collection_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(),
        )


def test_empty_capability_identifier_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "",
            ),
        )


def test_whitespace_capability_identifier_raises_error() -> None:
    with pytest.raises(ValueError):
        DomainCapabilityMapping(
            domain_id="travel",
            capability_ids=(
                "   ",
            ),
        )


def test_mapping_is_immutable() -> None:
    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
        ),
    )

    with pytest.raises(
        FrozenInstanceError,
    ):
        mapping.domain_id = "healthcare"


def test_multiple_capabilities_supported() -> None:
    mapping = DomainCapabilityMapping(
        domain_id="travel",
        capability_ids=(
            "hotel_search",
            "flight_search",
            "car_rental",
            "trip_planning",
        ),
    )

    assert mapping.capability_count == 4
