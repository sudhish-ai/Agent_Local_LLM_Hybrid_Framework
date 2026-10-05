# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the agent execution response contract for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent agent execution output.
# - Carry execution results.
# - Carry evidence and confidence information.
# - Act as the boundary between Agent Runtime and
#   Workflow Engine.
#
# Must Not:
# - Contain execution logic.
# - Contain retry logic.
# - Contain persistence logic.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentResponse:
    """Agent execution response payload."""

    status: str

    confidence: float = 0.0

    result: dict[str, Any] = field(
        default_factory=dict
    )

    evidence: list[dict[str, Any]] = field(
        default_factory=list
    )

    metrics: dict[str, float] = field(
        default_factory=dict
    )

    errors: list[str] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )
