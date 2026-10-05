# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

from __future__ import annotations

import asyncio

from alhf.multi_agent_orchestrator.agents.file_writer_agent import (
    FileWriterAgent,
)
from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)
from alhf.multi_agent_orchestrator.execution.task_executor import (
    TaskExecutor,
)
from alhf.multi_agent_orchestrator.execution.workflow_executor import (
    WorkflowExecutor,
)
from alhf.multi_agent_orchestrator.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from alhf.multi_agent_orchestrator.runtime.agent_runtime import (
    AgentRuntime,
)
from alhf.multi_agent_orchestrator.scheduler.in_memory_scheduler import (
    InMemoryScheduler,
)


async def main() -> None:
    print(
        "\n=== ALHF Dependency Workflow Demo Started ==="
    )

    task_repository = InMemoryTaskRepository()

    scheduler = InMemoryScheduler()

    agent_runtime = AgentRuntime()

    await agent_runtime.register_agent(
        FileWriterAgent(),
    )

    task_executor = TaskExecutor(
        task_repository=task_repository,
        agent_runtime=agent_runtime,
    )

    workflow_executor = WorkflowExecutor(
        scheduler=scheduler,
        task_executor=task_executor,
    )

    #
    # Intentionally unordered.
    #
    workflow_definition = WorkflowDefinition(
        workflow_id="workflow_dependency_demo",
        workflow_type="DEPENDENCY_DEMO",
        tasks=[
            TaskDefinition(
                task_id="task_003",
                workflow_id="workflow_dependency_demo",
                capability="file_writer",
                dependencies=[
                    "task_002",
                ],
            ),
            TaskDefinition(
                task_id="task_001",
                workflow_id="workflow_dependency_demo",
                capability="file_writer",
            ),
            TaskDefinition(
                task_id="task_002",
                workflow_id="workflow_dependency_demo",
                capability="file_writer",
                dependencies=[
                    "task_001",
                ],
            ),
        ],
        metadata={
            "demo": True,
            "dependency_demo": True,
        },
    )

    workflow_result = (
        await workflow_executor.execute(
            workflow_definition,
        )
    )

    print(
        "\n=== DEPENDENCY WORKFLOW RESULT ==="
    )

    print(
        f"Workflow Id   : {workflow_result.workflow_id}"
    )

    print(
        f"Workflow Type : {workflow_result.workflow_type}"
    )

    print(
        f"Status        : {workflow_result.final_status}"
    )

    print(
        f"Results       : {workflow_result.results}"
    )

    print(
        "\nExpected execution order:"
    )

    print(
        "task_001 -> task_002 -> task_003"
    )

    print(
        "\n=== ALHF Dependency Workflow Demo Completed ==="
    )


if __name__ == "__main__":
    asyncio.run(main())
