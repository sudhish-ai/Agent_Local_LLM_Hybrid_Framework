# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Bootstrap runtime execution components
# into a reusable runtime execution context.
#
# Responsibilities:
# - Create task repository.
# - Create scheduler.
# - Create agent runtime.
# - Create task executor.
# - Create workflow executor.
# - Return RuntimeExecutionContext.
#
# Must Not:
# - Register agents.
# - Execute workflows.
# - Execute agents.
# - Load capability intelligence.
# - Contain domain-specific logic.
#
# Architectural Position:
# - Composition layer bootstrap.
# - Creates runtime execution graph.
# - Consumed by demos and future runtimes.
#
# Reuse Value:
# - Travel domain.
# - Healthcare domain.
# - Finance domain.
# - Future worker runtime.
#
# Future Extensibility:
# - Distributed repositories.
# - Persistent schedulers.
# - Runtime diagnostics.
# - Runtime metrics aggregation.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from alhf.composition.runtime_execution_context import (
    RuntimeExecutionContext,
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


class RuntimeExecutionBootstrap:
    """
    Creates runtime execution context.
    """

    def build(
        self,
    ) -> RuntimeExecutionContext:
        task_repository = (
            InMemoryTaskRepository()
        )

        scheduler = (
            InMemoryScheduler()
        )

        agent_runtime = (
            AgentRuntime()
        )

        task_executor = (
            TaskExecutor(
                task_repository=(
                    task_repository
                ),
                agent_runtime=(
                    agent_runtime
                ),
            )
        )

        workflow_executor = (
            WorkflowExecutor(
                scheduler=(
                    scheduler
                ),
                task_executor=(
                    task_executor
                ),
            )
        )

        return (
            RuntimeExecutionContext(
                task_repository=(
                    task_repository
                ),
                scheduler=(
                    scheduler
                ),
                agent_runtime=(
                    agent_runtime
                ),
                task_executor=(
                    task_executor
                ),
                workflow_executor=(
                    workflow_executor
                ),
            )
        )
