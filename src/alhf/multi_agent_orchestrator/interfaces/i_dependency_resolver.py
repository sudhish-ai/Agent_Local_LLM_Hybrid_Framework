# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the dependency resolution boundary for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Resolve task dependencies.
# - Identify executable tasks.
# - Detect blocked tasks.
# - Detect dependency completion.
#
# Must Not:
# - Execute tasks.
# - Schedule tasks.
# - Modify workflow state.
# - Persist data.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)


class IDependencyResolver(ABC):
    """Dependency resolution interface."""

    @abstractmethod
    async def get_ready_tasks(
            self,
            tasks: list[TaskDefinition],
    ) -> list[TaskDefinition]:
        """Return tasks ready for execution."""
        raise NotImplementedError

    @abstractmethod
    async def get_blocked_tasks(
            self,
            tasks: list[TaskDefinition],
    ) -> list[TaskDefinition]:
        """Return tasks blocked by dependencies."""
        raise NotImplementedError

    @abstractmethod
    async def dependencies_satisfied(
            self,
            task: TaskDefinition,
    ) -> bool:
        """Return True when task dependencies are satisfied."""
        raise NotImplementedError
