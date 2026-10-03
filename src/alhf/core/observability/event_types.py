# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines ALHF-wide observability event names.
#
# Responsibilities:
# - Standardize event naming.
# - Support logging.
# - Support metrics.
# - Support tracing.
# - Support governance.
#
# Must Not:
# - Contain business logic.
# - Contain orchestration logic.

from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    """ALHF standard event types."""

    # Workflow events

    WORKFLOW_CREATED = "WORKFLOW_CREATED"
    WORKFLOW_STARTED = "WORKFLOW_STARTED"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"

    # Task events

    TASK_CREATED = "TASK_CREATED"
    TASK_STARTED = "TASK_STARTED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_FAILED = "TASK_FAILED"

    # Agent events

    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_RESOLVED = "AGENT_RESOLVED"
    AGENT_EXECUTED = "AGENT_EXECUTED"
    AGENT_FAILED = "AGENT_FAILED"

    # Runtime events

    RUNTIME_STARTED = "RUNTIME_STARTED"
    RUNTIME_STOPPED = "RUNTIME_STOPPED"

    # Scheduler events

    SCHEDULE_CREATED = "SCHEDULE_CREATED"
    TASK_DISPATCHED = "TASK_DISPATCHED"

    # Recovery events

    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"
    CHECKPOINT_RESTORED = "CHECKPOINT_RESTORED"
    RECOVERY_STARTED = "RECOVERY_STARTED"
    RECOVERY_COMPLETED = "RECOVERY_COMPLETED"

    # Governance events

    EXECUTION_BLOCKED = "EXECUTION_BLOCKED"
    EXECUTION_APPROVED = "EXECUTION_APPROVED"
