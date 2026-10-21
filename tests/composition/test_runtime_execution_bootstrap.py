# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for RuntimeExecutionBootstrap.
#
# Responsibilities:
# - Validate runtime execution bootstrap.
# - Validate execution graph creation.
# - Validate context creation.
# - Validate component wiring.
#
# Must Not:
# - Test workflow execution.
# - Test agent execution.
# - Test scheduling behavior.
# - Test orchestration logic.
#
# Architectural Position:
# - Protects composition layer bootstrap.
# - Validates runtime execution assembly.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from alhf.composition.runtime_execution_bootstrap import (
    RuntimeExecutionBootstrap,
)
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


def test_build_creates_runtime_execution_context(
) -> None:
    bootstrap = (
        RuntimeExecutionBootstrap()
    )

    context = (
        bootstrap.build()
    )

    assert isinstance(
        context,
        RuntimeExecutionContext,
    )


def test_build_creates_execution_components(
) -> None:
    bootstrap = (
        RuntimeExecutionBootstrap()
    )

    context = (
        bootstrap.build()
    )

    assert isinstance(
        context.task_repository,
        InMemoryTaskRepository,
    )

    assert isinstance(
        context.scheduler,
        InMemoryScheduler,
    )

    assert isinstance(
        context.agent_runtime,
        AgentRuntime,
    )

    assert isinstance(
        context.task_executor,
        TaskExecutor,
    )

    assert isinstance(
        context.workflow_executor,
        WorkflowExecutor,
    )


def test_build_wires_task_executor(
) -> None:
    bootstrap = (
        RuntimeExecutionBootstrap()
    )

    context = (
        bootstrap.build()
    )

    assert (
        context.task_executor
        is not None
    )

    assert (
        context.task_executor
        == context.task_executor
    )


def test_build_wires_workflow_executor(
) -> None:
    bootstrap = (
        RuntimeExecutionBootstrap()
    )

    context = (
        bootstrap.build()
    )

    assert (
        context.workflow_executor
        is not None
    )

    assert (
        context.workflow_executor
        == context.workflow_executor
    )
