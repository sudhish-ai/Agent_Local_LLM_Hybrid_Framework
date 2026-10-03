# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines workflow execution lifecycle states for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent workflow runtime state.
# - Provide standardized workflow lifecycle values.
# - Support persistence, recovery, scheduling, and observability.
#
# Must Not:
# - Contain transition logic.
# - Contain workflow execution logic.
# - Contain persistence logic.

from __future__ import annotations

from enum import Enum


class WorkflowExecutionStatus(str, Enum):
    """Workflow runtime lifecycle states.

    These states describe how a workflow progresses
    through the Multi-Agent Orchestrator Runtime.
    """

    NEW = "NEW"

    CREATED = "CREATED"

    PLANNED = "PLANNED"

    READY = "READY"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    ESCALATED = "ESCALATED"

    CANCELLED = "CANCELLED"
