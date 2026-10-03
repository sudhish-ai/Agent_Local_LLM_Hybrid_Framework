# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides a simple executable agent used for
# Runtime V1 validation.
#
# Responsibilities:
# - Expose a capability.
# - Execute a task.
# - Produce an AgentResponse.
#
# Must Not:
# - Perform orchestration.
# - Perform scheduling.
# - Access persistence.
# - Contain workflow logic.

from __future__ import annotations

from alhf.multi_agent_orchestrator.contracts.agent_response import (
    AgentResponse,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.interfaces.i_agent import (
    IAgent,
)


class DummyAgent(IAgent):
    """Simple runtime validation agent."""

    @property
    def agent_id(self) -> str:
        return "dummy-agent"

    @property
    def capability(self) -> str:
        return "dummy"

    async def execute(
        self,
        task_context: TaskContext,
    ) -> AgentResponse:
        return AgentResponse(
            status="SUCCESS",
            confidence=1.0,
            result={
                "message": (
                    f"Task {task_context.task_id} "
                    f"executed successfully"
                ),
            },
            metadata={
                "agent_id": self.agent_id,
                "capability": self.capability,
            },
        )
