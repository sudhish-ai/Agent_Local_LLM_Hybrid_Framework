# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT

import pytest

from src.alhf.capability.capability_selector import (
    CapabilitySelector,
)
from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)


def test_select_single_capability() -> None:
    selector = CapabilitySelector()

    hotel_search = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    result = selector.select(
        intent_text="find hotel",
        capabilities=(
            hotel_search,
        ),
    )

    assert result == hotel_search


def test_select_best_matching_capability() -> None:
    selector = CapabilitySelector()

    hotel_search = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    flight_search = CapabilityDefinition(
        capability_id="flight_search",
        capability_name="Flight Search",
        description="Search flights.",
    )

    result = selector.select(
        intent_text="search hotel in goa",
        capabilities=(
            hotel_search,
            flight_search,
        ),
    )

    assert result == hotel_search


def test_select_flight_capability() -> None:
    selector = CapabilitySelector()

    hotel_search = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Hotel Search",
        description="Search hotels.",
    )

    flight_search = CapabilityDefinition(
        capability_id="flight_search",
        capability_name="Flight Search",
        description="Search flights.",
    )

    result = selector.select(
        intent_text="book flight to delhi",
        capabilities=(
            hotel_search,
            flight_search,
        ),
    )

    assert result == flight_search


def test_empty_capability_collection_raises_error(
) -> None:
    selector = CapabilitySelector()

    with pytest.raises(
        ValueError,
    ):
        selector.select(
            intent_text="hotel",
            capabilities=(),
        )


def test_first_capability_wins_tie() -> None:
    selector = CapabilitySelector()

    capability_one = CapabilityDefinition(
        capability_id="capability_one",
        capability_name="Capability One",
        description="General capability",
    )

    capability_two = CapabilityDefinition(
        capability_id="capability_two",
        capability_name="Capability Two",
        description="General capability",
    )

    result = selector.select(
        intent_text="unmatched",
        capabilities=(
            capability_one,
            capability_two,
        ),
    )

    assert result == capability_one


def test_description_matching_contributes_to_score(
) -> None:
    selector = CapabilitySelector()

    reporting = CapabilityDefinition(
        capability_id="reporting",
        capability_name="Reporting",
        description="Generate root cause reports.",
    )

    analytics = CapabilityDefinition(
        capability_id="analytics",
        capability_name="Analytics",
        description="Analyze trends.",
    )

    result = selector.select(
        intent_text="generate report",
        capabilities=(
            analytics,
            reporting,
        ),
    )

    assert result == reporting


def test_capability_id_matching_has_high_priority(
) -> None:
    selector = CapabilitySelector()

    hotel_search = CapabilityDefinition(
        capability_id="hotel_search",
        capability_name="Search",
        description="Generic search.",
    )

    flight_search = CapabilityDefinition(
        capability_id="flight_search",
        capability_name="Search",
        description="Generic search.",
    )

    result = selector.select(
        intent_text="hotel",
        capabilities=(
            flight_search,
            hotel_search,
        ),
    )

    assert result == hotel_search
