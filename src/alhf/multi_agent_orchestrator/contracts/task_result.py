# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the task result payload produced by task
# execution within the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent task execution outcome.
# - Carry task result data.
# - Carry confidence and evidence information.
# - Act as payload for PipelineResult[TaskResult].
#
# Must Not:
# - Contain execution logic.
# - Contain persistence logic.
# - Contain retry logic.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TaskResult:
    """Task execution result payload."""

    task_id: str

    workflow_id: str

    capability: str

    status: str

    confidence: float = 0.0

    result: dict[str, Any] = field(
        default_factory=dict
    )

    evidence: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
