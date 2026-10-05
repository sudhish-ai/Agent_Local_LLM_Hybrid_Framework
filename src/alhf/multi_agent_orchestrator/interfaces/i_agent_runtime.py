# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the runtime agent execution boundary for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Agent registration.
# - Agent discovery.
# - Agent resolution.
# - Agent execution.
#
# Must Not:
# - Contain workflow logic.
# - Contain scheduling logic.
# - Contain persistence logic.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.agent_response import (
    AgentResponse,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_agent import (
    IAgent,
)


class IAgentRuntime(ABC):
    """Runtime boundary for agent lifecycle management."""

    @abstractmethod
    async def register_agent(
        self,
        agent: IAgent,
    ) -> None:
        """Register an agent with the runtime."""
        raise NotImplementedError

    @abstractmethod
    async def unregister_agent(
        self,
        agent_id: str,
    ) -> None:
        """Remove an agent from the runtime."""
        raise NotImplementedError

    @abstractmethod
    async def resolve_agent(
        self,
        capability: str,
    ) -> IAgent:
        """Resolve an agent for a capability."""
        raise NotImplementedError

    @abstractmethod
    async def execute(
        self,
        task_context: TaskContext,
    ) -> AgentResponse:
        """Execute a task through the runtime."""
        raise NotImplementedError
