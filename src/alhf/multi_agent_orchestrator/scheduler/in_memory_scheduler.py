# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides a Runtime V1 in-memory scheduler implementation.
#
# Responsibilities:
# - Queue executable task definitions.
# - Dispatch executable task definitions.
# - Support pause/resume operations.
# - Provide a lightweight scheduler implementation
#   for demos, testing, and Runtime V1 orchestration.
#
# Must Not:
# - Execute agents.
# - Execute tasks.
# - Persist data.
# - Perform retries.
# - Perform escalation logic.
# - Perform dependency resolution.

from __future__ import annotations

from collections import deque

from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)
from alhf.multi_agent_orchestrator.interfaces.i_scheduler import (
    IScheduler,
)


class InMemoryScheduler(IScheduler):
    """Runtime V1 in-memory scheduler."""

    def __init__(self) -> None:
        self._queue: deque[TaskDefinition] = deque()
        self._paused = False

    async def enqueue(
        self,
        task_definition: TaskDefinition,
    ) -> None:
        """Enqueue a task for future dispatch."""

        self._queue.append(
            task_definition,
        )

    async def schedule(
        self,
    ) -> None:
        """
        Runtime V1 scheduling hook.

        Reserved for future scheduling policies.
        """
        return

    async def dispatch(
        self,
    ) -> TaskDefinition | None:
        """Dispatch the next executable task."""

        if self._paused:
            return None

        if not self._queue:
            return None

        return self._queue.popleft()

    async def pause(
        self,
    ) -> None:
        """Pause scheduler activity."""

        self._paused = True

    async def resume(
        self,
    ) -> None:
        """Resume scheduler activity."""

        self._paused = False
