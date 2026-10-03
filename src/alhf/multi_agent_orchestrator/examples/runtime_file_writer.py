# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

from __future__ import annotations

import asyncio

from alhf.multi_agent_orchestrator.agents.file_writer_agent import (
    FileWriterAgent,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.runtime.agent_runtime import (
    AgentRuntime,
)


async def main() -> None:
    print("\n=== ALHF Runtime Demo Started ===")

    runtime = AgentRuntime()

    print(
        "\n[STEP 1] Registering FileWriterAgent..."
    )

    await runtime.register_agent(
        FileWriterAgent(),
    )

    print(
        "[SUCCESS] FileWriterAgent registered."
    )

    print(
        "\n[STEP 2] Creating TaskContext..."
    )

    task_context = TaskContext(
        task_id="task_001",
        workflow_id="workflow_001",
        capability="file_writer",
        input_context={
            "description":
            "Create runtime validation file",
        },
    )

    print(
        "[SUCCESS] TaskContext created."
    )

    print(
        "\n[STEP 3] Executing task through AgentRuntime..."
    )

    response = await runtime.execute(
        task_context,
    )

    print(
        "[SUCCESS] Agent execution finished."
    )

    print(
        "\n=== AGENT RESPONSE ==="
    )

    print(
        f"Status     : {response.status}"
    )

    print(
        f"Confidence : {response.confidence}"
    )

    print(
        f"Result     : {response.result}"
    )

    print(
        f"Metadata   : {response.metadata}"
    )

    print(
        "\n=== ALHF Runtime Demo Completed ==="
    )


if __name__ == "__main__":
    asyncio.run(main())
