# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the scheduling interface for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Accept executable tasks.
# - Queue executable tasks.
# - Dispatch executable tasks.
# - Pause scheduling.
# - Resume scheduling.
#
# Must Not:
# - Execute agents.
# - Persist data.
# - Modify workflow state directly.
# - Perform retries or escalations.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)


class IScheduler(ABC):
    """Scheduler interface."""

    @abstractmethod
    async def enqueue(
        self,
        task_definition: TaskDefinition,
    ) -> None:
        """Enqueue a task for future dispatch."""
        raise NotImplementedError

    @abstractmethod
    async def schedule(
        self,
    ) -> None:
        """Schedule queued tasks."""
        raise NotImplementedError

    @abstractmethod
    async def dispatch(
        self,
    ) -> TaskDefinition | None:
        """Dispatch the next executable task."""
        raise NotImplementedError

    @abstractmethod
    async def pause(
        self,
    ) -> None:
        """Pause scheduler activity."""
        raise NotImplementedError

    @abstractmethod
    async def resume(
        self,
    ) -> None:
        """Resume scheduler activity."""
        raise NotImplementedError
