# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the planner-produced workflow contract consumed
# by the Workflow Engine.
#
# Responsibilities:
# - Represent a fully planned workflow.
# - Carry task definitions.
# - Carry execution constraints.
# - Act as the handoff boundary between planning and execution.
#
# Must Not:
# - Contain execution logic.
# - Contain runtime state.
# - Contain persistence logic.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)


@dataclass(slots=True)
class WorkflowDefinition:
    """Planner-produced workflow definition."""

    workflow_id: str

    workflow_type: str

    tasks: list[TaskDefinition] = field(
        default_factory=list,
    )

    constraints: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
