# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides an in-memory task repository implementation
# for Runtime V1.
#
# Responsibilities:
# - Store task state.
# - Retrieve task state.
# - Update task state.
# - Store task execution results.
#
# Must Not:
# - Execute tasks.
# - Perform scheduling.
# - Execute agents.
# - Contain business logic.

from __future__ import annotations

from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.contracts.task_result import (
    TaskResult,
)
from alhf.multi_agent_orchestrator.interfaces.i_task_repository import (
    ITaskRepository,
)


class InMemoryTaskRepository(ITaskRepository):
    """In-memory task repository."""

    def __init__(self) -> None:
        self._tasks: dict[str, TaskContext] = {}
        self._results: dict[str, TaskResult] = {}

    async def create(
        self,
        task_context: TaskContext,
    ) -> None:
        self._tasks[task_context.task_id] = task_context

    async def get(
        self,
        task_id: str,
    ) -> TaskContext | None:
        return self._tasks.get(task_id)

    async def update(
        self,
        task_context: TaskContext,
    ) -> None:
        self._tasks[task_context.task_id] = task_context

    async def store_result(
        self,
        task_result: TaskResult,
    ) -> None:
        self._results[task_result.task_id] = task_result
