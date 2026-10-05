# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the canonical agent interface for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Standardize agent execution.
# - Provide a common agent contract.
# - Enable runtime-driven agent invocation.
#
# Must Not:
# - Contain business logic.
# - Contain workflow logic.
# - Contain scheduling logic.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.agent_response import (
    AgentResponse,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)


class IAgent(ABC):
    """Base interface for all ALHF agents."""

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """Unique agent identifier."""
        raise NotImplementedError

    @property
    @abstractmethod
    def capability(self) -> str:
        """Capability exposed by the agent."""
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        task_context: TaskContext,
    ) -> AgentResponse:
        """Execute a task and return an agent response."""
        raise NotImplementedError
