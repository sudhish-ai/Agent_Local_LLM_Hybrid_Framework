# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines task state transition rules for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Validate task transitions.
# - Protect task lifecycle integrity.
# - Centralize task state rules.
#
# Must Not:
# - Execute tasks.
# - Persist state.
# - Perform scheduling.
# - Execute agents.

from __future__ import annotations

from alhf.multi_agent_orchestrator.enums.task_execution_status import (
    TaskExecutionStatus,
)


class TaskStateMachine:
    """Task state transition validator."""

    _VALID_TRANSITIONS = {
        TaskExecutionStatus.NEW: {
            TaskExecutionStatus.CREATED,
        },
        TaskExecutionStatus.CREATED: {
            TaskExecutionStatus.READY,
        },
        TaskExecutionStatus.READY: {
            TaskExecutionStatus.ASSIGNED,
        },
        TaskExecutionStatus.ASSIGNED: {
            TaskExecutionStatus.RUNNING,
        },
        TaskExecutionStatus.RUNNING: {
            TaskExecutionStatus.COMPLETED,
            TaskExecutionStatus.FAILED,
            TaskExecutionStatus.ESCALATED,
        },
        TaskExecutionStatus.FAILED: {
            TaskExecutionStatus.RETRY_PENDING,
            TaskExecutionStatus.TERMINAL_FAILED,
            TaskExecutionStatus.ESCALATED,
        },
        TaskExecutionStatus.RETRY_PENDING: {
            TaskExecutionStatus.READY,
        },
        TaskExecutionStatus.ESCALATED: set(),
        TaskExecutionStatus.TERMINAL_FAILED: set(),
        TaskExecutionStatus.COMPLETED: set(),
    }

    @classmethod
    def can_transition(
        cls,
        current: TaskExecutionStatus,
        target: TaskExecutionStatus,
    ) -> bool:
        """Validate a task state transition."""

        return target in cls._VALID_TRANSITIONS.get(
            current,
            set(),
        )
