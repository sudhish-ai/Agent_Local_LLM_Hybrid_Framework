# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the task persistence boundary for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Create task records.
# - Retrieve task records.
# - Update task records.
# - Store task execution results.
#
# Must Not:
# - Execute tasks.
# - Perform scheduling.
# - Execute agents.
# - Perform business logic.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)
from alhf.multi_agent_orchestrator.contracts.task_result import (
    TaskResult,
)


class ITaskRepository(ABC):
    """Task repository interface."""

    @abstractmethod
    async def create(
        self,
        task_context: TaskContext,
    ) -> None:
        """Create a task record."""
        raise NotImplementedError

    @abstractmethod
    async def get(
        self,
        task_id: str,
    ) -> TaskContext | None:
        """Retrieve a task record."""
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        task_context: TaskContext,
    ) -> None:
        """Update a task record."""
        raise NotImplementedError

    @abstractmethod
    async def store_result(
        self,
        task_result: TaskResult,
    ) -> None:
        """Store a task execution result."""
        raise NotImplementedError
