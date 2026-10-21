# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides a reusable runtime execution
# context containing all assembled runtime
# execution components required by runtime
# consumers.
#
# Responsibilities:
# - Hold task repository.
# - Hold scheduler.
# - Hold agent runtime.
# - Hold task executor.
# - Hold workflow executor.
#
# Must Not:
# - Execute workflows.
# - Execute agents.
# - Perform orchestration.
# - Register agents.
# - Contain domain-specific logic.
#
# Architectural Position:
# - Composition layer context object.
# - Produced by execution bootstrap builders.
# - Consumed by demos and future runtimes.
#
# Reuse Value:
# - Travel domain.
# - Healthcare domain.
# - Finance domain.
# - Future worker runtime.
#
# Future Extensibility:
# - Runtime diagnostics.
# - Runtime metrics.
# - Runtime health monitoring.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass

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


@dataclass(
    frozen=True,
)
class RuntimeExecutionContext:
    """
    Immutable runtime execution context.

    Encapsulates runtime execution
    infrastructure required by consumers.
    """

    task_repository: (
        InMemoryTaskRepository
    )

    scheduler: (
        InMemoryScheduler
    )

    agent_runtime: (
        AgentRuntime
    )

    task_executor: (
        TaskExecutor
    )

    workflow_executor: (
        WorkflowExecutor
    )
