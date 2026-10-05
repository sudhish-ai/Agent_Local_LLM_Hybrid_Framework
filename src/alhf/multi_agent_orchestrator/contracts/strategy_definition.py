# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the selected strategy contract produced by
# the planner and consumed by workflow generation.
#
# Responsibilities:
# - Represent selected strategy.
# - Carry strategy confidence.
# - Carry strategy metadata.
# - Act as the planner strategy handoff contract.
# - Support future Strategy Formation Engine evolution.
#
# Must Not:
# - Contain strategy selection logic.
# - Contain workflow generation logic.
# - Contain execution logic.
# - Contain persistence logic.
# - Contain planner intelligence.

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(slots=True)
class StrategyDefinition:
    """
    Selected planner strategy.

    Examples:
        - root_cause_analysis
        - release_note_generation
        - flight_search
        - test_strategy_generation

    Notes:
        Strategy represents the planner's
        chosen approach for achieving
        the customer's desired outcome.

        This contract intentionally remains
        lightweight in V1 while supporting
        future Strategy Formation Engine
        evolution.
    """

    strategy: str

    confidence: float = 1.0

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
