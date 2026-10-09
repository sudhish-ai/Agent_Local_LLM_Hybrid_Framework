# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT

import pytest

from src.alhf.intent.contracts.intent_capability_mapping import (
    IntentCapabilityMapping,
)


def test_create_valid_mapping() -> None:
    mapping = IntentCapabilityMapping(
        intent_id="hotel_booking",
        capability_ids=(
            "hotel_search",
            "hotel_booking",
        ),
    )

    assert (
        mapping.intent_id
        == "hotel_booking"
    )

    assert (
        mapping.capability_ids
        == (
            "hotel_search",
            "hotel_booking",
        )
    )


def test_empty_intent_id_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="intent_id cannot be empty.",
    ):
        IntentCapabilityMapping(
            intent_id="",
            capability_ids=(
                "hotel_search",
            ),
        )


def test_whitespace_intent_id_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="intent_id cannot be empty.",
    ):
        IntentCapabilityMapping(
            intent_id="   ",
            capability_ids=(
                "hotel_search",
            ),
        )


def test_empty_capability_ids_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match="capability_ids cannot be empty.",
    ):
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(),
        )


def test_empty_capability_id_raises_error() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "capability_ids cannot contain "
            "empty values."
        ),
    ):
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(
                "hotel_search",
                "",
            ),
        )


def test_whitespace_capability_id_raises_error(
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "capability_ids cannot contain "
            "empty values."
        ),
    ):
        IntentCapabilityMapping(
            intent_id="hotel_booking",
            capability_ids=(
                "hotel_search",
                "   ",
            ),
        )


def test_mapping_is_immutable() -> None:
    mapping = IntentCapabilityMapping(
        intent_id="hotel_booking",
        capability_ids=(
            "hotel_search",
            "hotel_booking",
        ),
    )

    with pytest.raises(
        AttributeError,
    ):
        mapping.intent_id = (
            "flight_booking"
        )
