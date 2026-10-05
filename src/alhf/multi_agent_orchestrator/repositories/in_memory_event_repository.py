# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides an in-memory event repository implementation
# for Runtime V1.
#
# Responsibilities:
# - Store runtime events.
# - Retrieve workflow events.
# - Stream workflow events.
#
# Must Not:
# - Execute workflows.
# - Perform recovery.
# - Execute agents.
# - Contain business logic.

from __future__ import annotations

from collections import defaultdict

from alhf.multi_agent_orchestrator.contracts.events import (
    RuntimeEvent,
)
from alhf.multi_agent_orchestrator.interfaces.i_event_repository import (
    IEventRepository,
)


class InMemoryEventRepository(IEventRepository):
    """In-memory event repository."""

    def __init__(self) -> None:
        self._events: dict[str, list[RuntimeEvent]] = (
            defaultdict(list)
        )

    async def append(
        self,
        event: RuntimeEvent,
    ) -> None:
        self._events[event.workflow_id].append(event)

    async def get_events(
            self,
            workflow_id: str,
    ) -> list[RuntimeEvent]:
        return list(
            self._events.get(
                workflow_id,
                [],
            )
        )

    async def stream_events(
            self,
            workflow_id: str,
    ) -> list[RuntimeEvent]:
        """Stream workflowurun"""
        list(
            self._events.get(
                workflow_id,
                [],
            )
        )
