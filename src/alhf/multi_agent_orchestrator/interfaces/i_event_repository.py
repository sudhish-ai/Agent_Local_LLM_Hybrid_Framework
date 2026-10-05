# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the event persistence boundary for the
# Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Persist runtime events.
# - Retrieve workflow events.
# - Stream workflow events.
#
# Must Not:
# - Execute workflows.
# - Apply business rules.
# - Perform scheduling.
# - Execute recovery operations.

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from alhf.multi_agent_orchestrator.contracts.events import (
    RuntimeEvent,
)


class IEventRepository(ABC):
    """Event repository interface."""

    @abstractmethod
    async def append(
        self,
        event: RuntimeEvent,
    ) -> None:
        """Persist a runtime event."""
        raise NotImplementedError

    @abstractmethod
    async def get_events(
        self,
        workflow_id: str,
    ) -> list[RuntimeEvent]:
        """Retrieve workflow events."""
        raise NotImplementedError

    @abstractmethod
    async def stream_events(
            self,
            workflow_id: str,
    ) -> list[RuntimeEvent]:
        """Stream workflow events."""
        raise NotImplementedError
