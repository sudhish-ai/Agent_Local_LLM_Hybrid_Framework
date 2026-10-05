# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the governance decision contract for the
# Multi-Agent Orchestrator Execution Governor.
#
# Responsibilities:
# - Represent governor decisions.
# - Carry execution actions.
# - Carry governance reasoning.
# - Carry future governance metadata.
# - Act as the boundary between governance and execution.
#
# Must Not:
# - Contain execution logic.
# - Contain workflow logic.
# - Contain policy evaluation logic.
# - Contain retry implementation.
# - Contain escalation implementation.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# V1 primarily uses:
# - action
# - reason
#
# metadata exists to prevent future
# contract redesign as governance evolves.

from dataclasses import dataclass
from typing import Any

from alhf.multi_agent_orchestrator.contracts.execution_action import (
    ExecutionAction,
)


@dataclass(frozen=True)
class ExecutionDecision:
    """
    Represents the result of a governor evaluation.

    The governor evaluates.

    Runtime components consume the decision
    and perform the appropriate action.
    """

    action: ExecutionAction

    reason: str | None = None

    metadata: dict[str, Any] | None = None
