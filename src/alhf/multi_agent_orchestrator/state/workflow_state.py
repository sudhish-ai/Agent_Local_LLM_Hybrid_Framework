# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the workflow runtime state model for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Track workflow execution state.
# - Track workflow timestamps.
# - Support persistence and recovery.
#
# Must Not:
# - Execute workflows.
# - Perform state transitions.
# - Contain business logic.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)


@dataclass(slots=True)
class WorkflowState:
    """Workflow runtime state."""

    workflow_id: str

    status: WorkflowExecutionStatus

    created_at: datetime

    updated_at: datetime
