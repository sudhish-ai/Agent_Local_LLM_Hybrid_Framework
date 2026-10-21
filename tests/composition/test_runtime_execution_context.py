# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Unit tests for RuntimeExecutionContext.
#
# Responsibilities:
# - Validate context creation.
# - Validate dependency preservation.
# - Validate immutability.
#
# Must Not:
# - Test workflow execution.
# - Test scheduling.
# - Test agent execution.
# - Test orchestration.
#
# Architectural Position:
# - Protects composition layer contracts.
# - Guards runtime execution transport.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from dataclasses import (
    FrozenInstanceError,
)

import pytest

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


def _build_runtime_execution_graph():
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
        task_repository,
        scheduler,
        agent_runtime,
        task_executor,
        workflow_executor,
    )


def test_context_preserves_dependencies(
) -> None:
    (
        task_repository,
        scheduler,
        agent_runtime,
        task_executor,
        workflow_executor,
    ) = _build_runtime_execution_graph()

    context = (
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

    assert (
        context.task_repository
        is task_repository
    )

    assert (
        context.scheduler
        is scheduler
    )

    assert (
        context.agent_runtime
        is agent_runtime
    )

    assert (
        context.task_executor
        is task_executor
    )

    assert (
        context.workflow_executor
        is workflow_executor
    )


def test_context_contains_execution_components(
) -> None:
    (
        task_repository,
        scheduler,
        agent_runtime,
        task_executor,
        workflow_executor,
    ) = _build_runtime_execution_graph()

    context = (
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


def test_context_is_immutable(
) -> None:
    (
        task_repository,
        scheduler,
        agent_runtime,
        task_executor,
        workflow_executor,
    ) = _build_runtime_execution_graph()

    context = (
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

    with pytest.raises(
        FrozenInstanceError
    ):
        context.scheduler = (
            InMemoryScheduler()
        )
