# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the runtime error payload contract used by
# the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent structured runtime errors.
# - Support workflow and task failures.
# - Support observability and auditability.
# - Support escalation and recovery workflows.
#
# Must Not:
# - Contain execution logic.
# - Contain retry logic.
# - Replace ALHFError exception hierarchy.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from alhf.core.status import ErrorSeverity


@dataclass(slots=True, frozen=True)
class RuntimeErrorContract:
    """Structured runtime error payload."""

    error_code: str

    message: str

    severity: ErrorSeverity

    retryable: bool = False

    details: dict[str, Any] = field(
        default_factory=dict
    )
