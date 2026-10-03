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
from alhf.multi_agent_orchestrator.engine.workflow_engine import (
    WorkflowEngine,
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
from alhf.multi_agent_orchestrator.repositories.in_memory_workflow_repository import (
    InMemoryWorkflowRepository,
)
from alhf.multi_agent_orchestrator.runtime.agent_runtime import (
    AgentRuntime,
)
from alhf.multi_agent_orchestrator.scheduler.in_memory_scheduler import (
    InMemoryScheduler,
)


async def main() -> None:
    print("\n=== ALHF Workflow Engine Demo Started ===")

    workflow_repository = (
        InMemoryWorkflowRepository()
    )

    task_repository = (
        InMemoryTaskRepository()
    )

    scheduler = (
        InMemoryScheduler()
    )

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
    # NOTE:
    # This demo assumes WorkflowEngine
    # will be updated next to accept:
    #
    # workflow_executor: WorkflowExecutor
    #
    # in its constructor.
    #
    workflow_engine = WorkflowEngine(
        workflow_repository=workflow_repository,
        workflow_executor=workflow_executor,
    )

    workflow_definition = WorkflowDefinition(
        workflow_id="workflow_001",
        workflow_type="FILE_WRITER_ENGINE_DEMO",
        tasks=[
            TaskDefinition(
                task_id="task_001",
                workflow_id="workflow_001",
                capability="file_writer",
            ),
            TaskDefinition(
                task_id="task_002",
                workflow_id="workflow_001",
                capability="file_writer",
            ),
            TaskDefinition(
                task_id="task_003",
                workflow_id="workflow_001",
                capability="file_writer",
            ),
        ],
        metadata={
            "demo": True,
            "entry_point": "workflow_engine",
        },
    )

    workflow_result = (
        await workflow_engine.start_workflow(
            workflow_definition,
        )
    )

    print(
        "\n=== WORKFLOW ENGINE RESULT ==="
    )

    print(workflow_result)

    print(
        "\n=== ALHF Workflow Engine Demo Completed ==="
    )


if __name__ == "__main__":
    asyncio.run(main())
