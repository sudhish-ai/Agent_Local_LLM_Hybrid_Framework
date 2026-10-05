# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines canonical runtime event types used by the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Standardize event classification.
# - Support observability and auditability.
# - Support event persistence and recovery.
# - Provide consistent event naming across the runtime.
#
# Must Not:
# - Contain business logic.
# - Contain event processing logic.
# - Contain persistence logic.

from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    """Canonical runtime event types."""

    WORKFLOW_CREATED = "WORKFLOW_CREATED"

    WORKFLOW_PLANNED = "WORKFLOW_PLANNED"

    WORKFLOW_STARTED = "WORKFLOW_STARTED"

    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"

    WORKFLOW_FAILED = "WORKFLOW_FAILED"

    WORKFLOW_ESCALATED = "WORKFLOW_ESCALATED"

    TASK_ASSIGNED = "TASK_ASSIGNED"

    TASK_STARTED = "TASK_STARTED"

    TASK_COMPLETED = "TASK_COMPLETED"

    TASK_FAILED = "TASK_FAILED"

    TASK_RETRIED = "TASK_RETRIED"

    TASK_ESCALATED = "TASK_ESCALATED"

    CHECKPOINT_CREATED = "CHECKPOINT_CREATED"

    RECOVERY_STARTED = "RECOVERY_STARTED"

    RECOVERY_COMPLETED = "RECOVERY_COMPLETED"

    GOVERNOR_BLOCKED = "GOVERNOR_BLOCKED"

    POLICY_VALIDATED = "POLICY_VALIDATED"
