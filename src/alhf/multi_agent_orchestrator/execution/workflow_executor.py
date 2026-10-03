# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides Runtime V1 workflow execution orchestration.
#
# Responsibilities:
# - Execute workflow tasks.
# - Coordinate scheduler interactions.
# - Collect task results.
# - Build workflow result.
# - Emit observability events.
#
# Must Not:
# - Perform scheduling logic.
# - Perform retries.
# - Perform recovery.
# - Perform checkpointing.
# - Perform dependency resolution.

from __future__ import annotations

from alhf.core.observability.correlation import CorrelationId
from alhf.core.observability.event_types import EventType
from alhf.core.observability.logger import ALHFLogger
from alhf.core.observability.metrics import MetricsRegistry
from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)
from alhf.multi_agent_orchestrator.contracts.task_result import TaskResult
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)
from alhf.multi_agent_orchestrator.contracts.workflow_result import (
    WorkflowResult,
)
from alhf.multi_agent_orchestrator.execution.task_executor import (
    TaskExecutor,
)
from alhf.multi_agent_orchestrator.interfaces.i_scheduler import (
    IScheduler,
)


class WorkflowExecutor:
    """Runtime V1 workflow executor."""

    def __init__(
        self,
        scheduler: IScheduler,
        task_executor: TaskExecutor,
    ) -> None:
        self._scheduler = scheduler
        self._task_executor = task_executor

        self._logger = ALHFLogger(
            component="WorkflowExecutor",
        )

        self._metrics = MetricsRegistry()

    async def execute(
            self,
            workflow_definition: WorkflowDefinition,
    ) -> WorkflowResult:
        """Execute workflow."""

        correlation_id = CorrelationId.create()

        self._logger.info(
            (
                f"{EventType.WORKFLOW_STARTED.value} | "
                f"workflow_id={workflow_definition.workflow_id} | "
                f"workflow_type={workflow_definition.workflow_type} | "
                f"correlation_id={correlation_id}"
            )
        )

        self._metrics.increment(
            "workflow_started",
        )

        task_results: list[TaskResult] = []

        completed_tasks: set[str] = set()

        pending_tasks: dict[str, TaskDefinition] = {
            task.task_id: task
            for task in workflow_definition.tasks
        }

        try:
            while pending_tasks:
                executable_tasks: list[
                    TaskDefinition
                ] = []

                for (
                        task_definition
                ) in pending_tasks.values():
                    if all(
                            dependency
                            in completed_tasks
                            for dependency in (
                                    task_definition.dependencies
                            )
                    ):
                        executable_tasks.append(
                            task_definition,
                        )

                if not executable_tasks:
                    raise RuntimeError(
                        "Dependency resolution failed. "
                        "Circular or missing dependency detected."
                    )

                for task_definition in executable_tasks:
                    execution_task_definition = (
                        TaskDefinition(
                            task_id=task_definition.task_id,
                            workflow_id=task_definition.workflow_id,
                            capability=task_definition.capability,
                            dependencies=list(
                                task_definition.dependencies,
                            ),
                            constraints=dict(
                                task_definition.constraints,
                            ),
                            metadata={
                                **task_definition.metadata,
                                "correlation_id": (
                                    correlation_id
                                ),
                            },
                        )
                    )

                    await self._scheduler.enqueue(
                        execution_task_definition,
                    )

                    pending_tasks.pop(
                        task_definition.task_id,
                    )

                await self._scheduler.schedule()

                while True:
                    scheduled_task = (
                        await self._scheduler.dispatch()
                    )

                    if scheduled_task is None:
                        break

                    task_result = (
                        await self._task_executor.execute(
                            scheduled_task,
                        )
                    )

                    completed_tasks.add(
                        task_result.task_id,
                    )

                    task_results.append(
                        task_result,
                    )

            workflow_result = WorkflowResult(
                workflow_id=workflow_definition.workflow_id,
                workflow_type=workflow_definition.workflow_type,
                final_status="COMPLETED",
                results=[
                    {
                        "task_id": result.task_id,
                        "status": result.status,
                        "result": result.result,
                    }
                    for result in task_results
                ],
                metadata={
                    **workflow_definition.metadata,
                    "correlation_id": correlation_id,
                },
            )

            self._metrics.increment(
                "workflow_completed",
            )

            self._logger.info(
                (
                    f"{EventType.WORKFLOW_COMPLETED.value} | "
                    f"workflow_id={workflow_definition.workflow_id} | "
                    f"workflow_type={workflow_definition.workflow_type} | "
                    f"correlation_id={correlation_id}"
                )
            )

            return workflow_result

        except Exception as ex:
            self._metrics.increment(
                "workflow_failed",
            )

            self._logger.error(
                (
                    f"{EventType.WORKFLOW_FAILED.value} | "
                    f"workflow_id={workflow_definition.workflow_id} | "
                    f"workflow_type={workflow_definition.workflow_type} | "
                    f"correlation_id={correlation_id} | "
                    f"error={str(ex)}"
                )
            )

            raise
