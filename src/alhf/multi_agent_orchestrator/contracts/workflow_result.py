# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the workflow result payload produced by the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent final workflow outcome.
# - Capture workflow execution summary.
# - Carry evidence and confidence information.
# - Act as payload for PipelineResult[WorkflowResult].
#
# Must Not:
# - Contain execution logic.
# - Contain persistence logic.
# - Contain retry logic.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class WorkflowResult:
    """Final workflow completion result."""

    workflow_id: str

    workflow_type: str

    final_status: str

    confidence: float = 0.0

    results: list[dict[str, Any]] = field(
        default_factory=list
    )

    evidence: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
