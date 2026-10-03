# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines workflow state transition rules for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Validate workflow transitions.
# - Protect workflow lifecycle integrity.
# - Centralize workflow state rules.
#
# Must Not:
# - Execute workflows.
# - Persist state.
# - Perform scheduling.
# - Execute agents.

from __future__ import annotations

from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)


class WorkflowStateMachine:
    """Workflow state transition validator."""

    _VALID_TRANSITIONS = {
        WorkflowExecutionStatus.NEW: {
            WorkflowExecutionStatus.CREATED,
        },
        WorkflowExecutionStatus.CREATED: {
            WorkflowExecutionStatus.PLANNED,
        },
        WorkflowExecutionStatus.PLANNED: {
            WorkflowExecutionStatus.READY,
        },
        WorkflowExecutionStatus.READY: {
            WorkflowExecutionStatus.RUNNING,
        },
        WorkflowExecutionStatus.RUNNING: {
            WorkflowExecutionStatus.COMPLETED,
            WorkflowExecutionStatus.FAILED,
            WorkflowExecutionStatus.ESCALATED,
            WorkflowExecutionStatus.CANCELLED,
        },
        WorkflowExecutionStatus.FAILED: {
            WorkflowExecutionStatus.READY,
            WorkflowExecutionStatus.ESCALATED,
        },
        WorkflowExecutionStatus.ESCALATED: set(),
        WorkflowExecutionStatus.CANCELLED: set(),
        WorkflowExecutionStatus.COMPLETED: set(),
    }

    @classmethod
    def can_transition(
        cls,
        current: WorkflowExecutionStatus,
        target: WorkflowExecutionStatus,
    ) -> bool:
        """Validate a workflow state transition."""

        return target in cls._VALID_TRANSITIONS.get(
            current,
            set(),
        )
