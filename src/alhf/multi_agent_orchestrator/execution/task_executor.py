# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides Runtime V1 task execution orchestration.
#
# Responsibilities:
# - Convert TaskDefinition into TaskContext.
# - Persist TaskContext.
# - Execute tasks through AgentRuntime.
# - Generate TaskResult.
# - Persist TaskResult.
# - Emit observability events.
#
# Must Not:
# - Perform scheduling.
# - Perform retries.
# - Perform recovery.
# - Perform workflow orchestration.
# - Execute dependency resolution.

from __future__ import annotations

from alhf.core.observability.correlation import CorrelationId
from alhf.core.observability.event_types import EventType
from alhf.core.observability.logger import ALHFLogger
from alhf.core.observability.metrics import MetricsRegistry
from alhf.multi_agent_orchestrator.contracts.task_context import TaskContext
from alhf.multi_agent_orchestrator.contracts.task_definition import TaskDefinition
from alhf.multi_agent_orchestrator.contracts.task_result import TaskResult
from alhf.multi_agent_orchestrator.interfaces.i_agent_runtime import (
    IAgentRuntime,
)
from alhf.multi_agent_orchestrator.interfaces.i_task_repository import (
    ITaskRepository,
)


class TaskExecutor:
    """Runtime V1 task executor."""

    def __init__(
        self,
        task_repository: ITaskRepository,
        agent_runtime: IAgentRuntime,
    ) -> None:
        self._task_repository = task_repository
        self._agent_runtime = agent_runtime

        self._logger = ALHFLogger(
            component="TaskExecutor",
        )

        self._metrics = MetricsRegistry()

    async def execute(
        self,
        task_definition: TaskDefinition,
    ) -> TaskResult:
        """Execute a task definition."""

        correlation_id = (
            task_definition.metadata.get("correlation_id")
            or CorrelationId.create()
        )

        self._logger.info(
            (
                f"{EventType.TASK_STARTED.value} | "
                f"task_id={task_definition.task_id} | "
                f"workflow_id={task_definition.workflow_id} | "
                f"correlation_id={correlation_id}"
            )
        )

        self._metrics.increment("task_started")

        task_context = TaskContext(
            task_id=task_definition.task_id,
            workflow_id=task_definition.workflow_id,
            capability=task_definition.capability,
            execution_constraints=task_definition.constraints,
            metadata={
                **task_definition.metadata,
                "correlation_id": correlation_id,
            },
        )

        await self._task_repository.create(task_context)

        try:
            agent_response = await self._agent_runtime.execute(
                task_context,
            )

            task_result = TaskResult(
                task_id=task_context.task_id,
                workflow_id=task_context.workflow_id,
                capability=task_context.capability,
                status=agent_response.status,
                confidence=agent_response.confidence,
                result=agent_response.result,
                evidence=agent_response.evidence,
                metadata={
                    **task_context.metadata,
                    **agent_response.metadata,
                },
            )

            await self._task_repository.store_result(
                task_result,
            )

            self._metrics.increment("task_completed")

            self._logger.info(
                (
                    f"{EventType.TASK_COMPLETED.value} | "
                    f"task_id={task_context.task_id} | "
                    f"workflow_id={task_context.workflow_id} | "
                    f"correlation_id={correlation_id}"
                )
            )

            return task_result

        except Exception as ex:
            self._metrics.increment("task_failed")

            self._logger.error(
                (
                    f"{EventType.TASK_FAILED.value} | "
                    f"task_id={task_definition.task_id} | "
                    f"workflow_id={task_definition.workflow_id} | "
                    f"correlation_id={correlation_id} | "
                    f"error={str(ex)}"
                )
            )

            raise
