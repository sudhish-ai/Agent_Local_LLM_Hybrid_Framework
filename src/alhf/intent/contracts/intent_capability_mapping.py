# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the relationship between an intent
# and the capabilities required to satisfy it.
#
# Responsibilities:
# - Represent intent-to-capability mappings.
# - Provide stable intent identifiers.
# - Provide capability relationships.
# - Act as a registration unit for
#   IntentCapabilityRegistry.
#
# Must Not:
# - Contain planning logic.
# - Contain execution logic.
# - Contain orchestration logic.
# - Contain capability resolution logic.
# - Contain persistence logic.
#
# Architectural Position:
# - Knowledge layer contract.
# - Consumed by IntentCapabilityRegistry.
# - Consumed by IntentCapabilityResolver.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass


@dataclass(
    frozen=True,
    slots=True,
)
class IntentCapabilityMapping:
    """
    Maps an intent to one or more capabilities.

    Examples:

        hotel_booking
            -> hotel_search
            -> hotel_booking

        flight_booking
            -> flight_search
            -> flight_booking
    """

    intent_id: str

    capability_ids: tuple[
        str,
        ...
    ]

    def __post_init__(
        self,
    ) -> None:
        """
        Validate required fields.
        """

        if not self.intent_id.strip():
            raise ValueError(
                "intent_id cannot be empty."
            )

        if not self.capability_ids:
            raise ValueError(
                "capability_ids cannot be empty."
            )

        for capability_id in (
            self.capability_ids
        ):
            if not capability_id.strip():
                raise ValueError(
                    "capability_ids cannot "
                    "contain empty values."
                )
