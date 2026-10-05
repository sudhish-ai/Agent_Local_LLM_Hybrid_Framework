# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

from __future__ import annotations

import asyncio

from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)
from alhf.multi_agent_orchestrator.scheduler.in_memory_scheduler import (
    InMemoryScheduler,
)


async def main() -> None:
    print("\n=== ALHF Scheduler Demo Started ===")

    scheduler = InMemoryScheduler()

    task_1 = TaskDefinition(
        task_id="task_001",
        workflow_id="workflow_001",
        capability="file_writer",
    )

    task_2 = TaskDefinition(
        task_id="task_002",
        workflow_id="workflow_001",
        capability="file_writer",
    )

    task_3 = TaskDefinition(
        task_id="task_003",
        workflow_id="workflow_001",
        capability="file_writer",
    )

    await scheduler.enqueue(task_1)
    await scheduler.enqueue(task_2)
    await scheduler.enqueue(task_3)

    print("\nDispatch Order:")

    while True:
        task = await scheduler.dispatch()

        if task is None:
            break

        print(
            f"Task Id={task.task_id} | "
            f"Workflow Id={task.workflow_id} | "
            f"Capability={task.capability}"
        )

    print(
        "\nTesting Pause/Resume..."
    )

    await scheduler.enqueue(task_1)

    await scheduler.pause()

    paused_task = await scheduler.dispatch()

    print(
        f"Dispatch While Paused: {paused_task}"
    )

    await scheduler.resume()

    resumed_task = await scheduler.dispatch()

    print(
        f"Dispatch After Resume: "
        f"{resumed_task.task_id if resumed_task else None}"
    )

    print(
        "\n=== ALHF Scheduler Demo Completed ==="
    )


if __name__ == "__main__":
    asyncio.run(main())
