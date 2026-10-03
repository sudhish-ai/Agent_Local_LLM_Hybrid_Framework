# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines task execution lifecycle states for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent task runtime state.
# - Support scheduler decisions.
# - Support dependency resolution.
# - Support recovery and persistence.
#
# Must Not:
# - Contain execution logic.
# - Contain transition logic.
# - Contain scheduling logic.

from __future__ import annotations

from enum import Enum


class TaskExecutionStatus(str, Enum):
    """Task runtime lifecycle states."""

    NEW = "NEW"

    CREATED = "CREATED"

    READY = "READY"

    ASSIGNED = "ASSIGNED"

    RUNNING = "RUNNING"

    COMPLETED = "COMPLETED"

    FAILED = "FAILED"

    RETRY_PENDING = "RETRY_PENDING"

    ESCALATED = "ESCALATED"

    TERMINAL_FAILED = "TERMINAL_FAILED"
