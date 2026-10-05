# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the Runtime V1 agent execution runtime.
#
# Responsibilities:
# - Register agents.
# - Unregister agents.
# - Resolve agents by capability.
# - Execute tasks through agents.
# - Emit observability events.
#
# Must Not:
# - Contain workflow orchestration logic.
# - Contain scheduling logic.
# - Contain persistence logic.
# - Contain retry logic.

from __future__ import annotations

from alhf.core.observability.correlation import (
    CorrelationId,
)
from alhf.core.observability.event_types import (
    EventType,
)
from alhf.core.observability.logger import (
    ALHFLogger,
)
from alhf.core.observability.metrics import (
    MetricsRegistry,
)
from alhf.multi_agent_orchestrator.contracts.agent_response import (
    AgentResponse,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_agent import (
    IAgent,
)
from alhf.multi_agent_orchestrator.interfaces.i_agent_runtime import (
    IAgentRuntime,
)


class AgentRuntime(IAgentRuntime):
    """Runtime implementation for agent lifecycle management."""

    def __init__(self) -> None:
        self._agents: dict[str, IAgent] = {}

        self._logger = ALHFLogger(
            component="AgentRuntime",
        )

        self._metrics = MetricsRegistry()

    async def register_agent(
        self,
        agent: IAgent,
    ) -> None:
        """Register an agent."""

        self._agents[
            agent.agent_id
        ] = agent

        self._metrics.increment(
            "agent_registered",
        )

        self._logger.info(
            (
                f"{EventType.AGENT_REGISTERED.value} | "
                f"agent_id={agent.agent_id} | "
                f"capability={agent.capability}"
            )
        )

    async def unregister_agent(
        self,
        agent_id: str,
    ) -> None:
        """Remove an agent."""

        self._agents.pop(
            agent_id,
            None,
        )

    async def resolve_agent(
        self,
        capability: str,
    ) -> IAgent:
        """Resolve an agent by capability."""

        for agent in self._agents.values():
            if agent.capability == capability:
                self._logger.info(
                    (
                        f"{EventType.AGENT_RESOLVED.value} | "
                        f"agent_id={agent.agent_id} | "
                        f"capability={capability}"
                    )
                )

                return agent

        raise ValueError(
            f"No agent registered for capability: "
            f"{capability}"
        )

    async def execute(
        self,
        task_context: TaskContext,
    ) -> AgentResponse:
        """Execute a task through a resolved agent."""

        correlation_id = (
            task_context.metadata.get(
                "correlation_id",
            )
            or CorrelationId.create()
        )

        agent = await self.resolve_agent(
            task_context.capability,
        )

        self._metrics.increment(
            "agent_executed",
        )

        self._logger.info(
            (
                f"{EventType.AGENT_EXECUTED.value} | "
                f"agent_id={agent.agent_id} | "
                f"task_id={task_context.task_id} | "
                f"workflow_id={task_context.workflow_id} | "
                f"correlation_id={correlation_id}"
            )
        )

        try:
            response = await agent.execute(
                task_context,
            )

            return response

        except Exception as ex:
            self._metrics.increment(
                "agent_failed",
            )

            self._logger.error(
                (
                    f"{EventType.AGENT_FAILED.value} | "
                    f"agent_id={agent.agent_id} | "
                    f"task_id={task_context.task_id} | "
                    f"workflow_id={task_context.workflow_id} | "
                    f"correlation_id={correlation_id} | "
                    f"error={str(ex)}"
                )
            )

            raise
