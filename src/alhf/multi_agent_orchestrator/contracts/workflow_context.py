# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the workflow execution context contract used by
# the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Carry workflow execution metadata.
# - Provide workflow identity and state information.
# - Support policy, execution, and audit contexts.
# - Support execution timing information.
# - Serve as the primary workflow contract across runtime boundaries.
#
# Must Not:
# - Contain workflow execution logic.
# - Contain state transition logic.
# - Contain persistence logic.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# Notes:
# execution_start_time_utc provides runtime timing
# information required by:
# - TimeoutEvaluator
# - Runtime Observability
# - Execution Auditing
# - Future Governance Extensions

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any

from alhf.multi_agent_orchestrator.enums.workflow_execution_status import (
    WorkflowExecutionStatus,
)


@dataclass(slots=True)
class WorkflowContext:
    """Workflow execution context."""

    workflow_id: str

    workflow_type: str

    workflow_state: WorkflowExecutionStatus

    execution_start_time_utc: datetime | None = None

    policy_context: dict[str, Any] = field(
        default_factory=dict,
    )

    execution_context: dict[str, Any] = field(
        default_factory=dict,
    )

    audit_context: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
