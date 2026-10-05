# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the immutable outcome request contract used by
# the Outcome Optimization Engine and Workflow Planner.
#
# Responsibilities:
# - Capture desired business outcome.
# - Capture planning constraints.
# - Capture planning preferences.
# - Support future Outcome Optimization Engine evolution.
# - Serve as the primary planner input contract.
#
# Must Not:
# - Contain workflow logic.
# - Contain task definitions.
# - Contain execution logic.
# - Contain persistence logic.
# - Contain planner intelligence.

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(slots=True)
class OutcomeRequest:
    """
    Customer outcome request.

    Examples:
        - Analyze repository build failure.
        - Generate release notes.
        - Create test strategy.
        - Book cheapest flight.

    Notes:
        Customers express desired outcomes,
        not workflow definitions.

        This contract is intentionally simple
        so that V1 implementation remains
        compatible with future V5 planner
        evolution.
    """

    request_id: str

    goal: str

    constraints: dict[str, Any] = field(
        default_factory=dict,
    )

    preferences: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
