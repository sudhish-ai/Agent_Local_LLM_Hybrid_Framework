# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the task execution context contract used by
# the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Carry task execution metadata.
# - Provide execution input context.
# - Support agent assignment.
# - Support scheduler and runtime execution.
# - Support execution-attempt awareness.
#
# Must Not:
# - Contain execution logic.
# - Contain scheduling logic.
# - Contain persistence logic.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# attempt_number provides execution-attempt awareness
# required by:
# - RetryEvaluator
# - TimeoutEvaluator
# - Future Observability
# - Future Governance Extensions

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass(slots=True)
class TaskContext:
    """Task execution context."""

    task_id: str

    workflow_id: str

    capability: str

    attempt_number: int = 1

    assigned_agent: str | None = None

    input_context: dict[str, Any] = field(
        default_factory=dict
    )

    execution_constraints: dict[str, Any] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
