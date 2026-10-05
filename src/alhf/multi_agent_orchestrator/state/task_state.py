# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the task runtime state model for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Track task execution state.
# - Track task timestamps.
# - Support persistence and recovery.
#
# Must Not:
# - Execute tasks.
# - Perform state transitions.
# - Contain business logic.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from alhf.multi_agent_orchestrator.enums.task_execution_status import (
    TaskExecutionStatus,
)


@dataclass(slots=True)
class TaskState:
    """Task runtime state."""

    task_id: str

    workflow_id: str

    status: TaskExecutionStatus

    created_at: datetime

    updated_at: datetime
