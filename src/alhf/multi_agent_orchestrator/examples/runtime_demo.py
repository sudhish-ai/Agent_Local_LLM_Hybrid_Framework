# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

from __future__ import annotations

import asyncio

from alhf.multi_agent_orchestrator.agents.dummy_agent import (
    DummyAgent,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.runtime.agent_runtime import (
    AgentRuntime,
)


async def main() -> None:
    runtime = AgentRuntime()

    await runtime.register_agent(
        DummyAgent(),
    )

    task_context = TaskContext(
        task_id="task_001",
        workflow_id="workflow_001",
        capability="dummy",
    )

    response = await runtime.execute(
        task_context,
    )

    print(
        "\n=== ALHF Runtime Demo ===",
    )

    print(
        f"Status: {response.status}",
    )

    print(
        f"Confidence: {response.confidence}",
    )

    print(
        f"Result: {response.result}",
    )


if __name__ == "__main__":
    asyncio.run(main())
