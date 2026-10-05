# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the detected intent contract produced by
# the Intent Discovery layer and consumed by
# downstream planner components.
#
# Responsibilities:
# - Represent detected intent.
# - Carry detection confidence.
# - Carry intent-related metadata.
# - Act as the planner intent handoff contract.
# - Support future Intent Discovery Engine evolution.
#
# Must Not:
# - Contain detection logic.
# - Contain workflow logic.
# - Contain strategy selection logic.
# - Contain persistence logic.
# - Contain planner intelligence.

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(slots=True)
class IntentDefinition:
    """
    Detected planner intent.

    Examples:
        - repository_analysis
        - flight_booking
        - release_note_generation

    Notes:
        Intent represents the planner's
        understanding of the customer's goal.

        This contract intentionally remains
        lightweight in V1 while supporting
        future Intent Discovery Engine evolution.
    """

    intent: str

    confidence: float = 1.0

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
