# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the planner-produced task contract used by
# the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent a workflow task.
# - Define task dependencies.
# - Define required capabilities.
# - Carry execution constraints.
#
# Must Not:
# - Contain execution logic.
# - Contain runtime state.
# - Contain persistence logic.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TaskDefinition:
    """Planner-produced task definition."""

    task_id: str

    workflow_id: str

    capability: str

    dependencies: list[str] = field(
        default_factory=list
    )

    constraints: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
