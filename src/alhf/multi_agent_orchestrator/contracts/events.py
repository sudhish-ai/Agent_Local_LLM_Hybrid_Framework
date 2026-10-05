# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the canonical runtime event contract used by
# the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Represent immutable runtime events.
# - Support observability and auditability.
# - Support event persistence.
# - Support recovery and replay.
#
# Must Not:
# - Contain event processing logic.
# - Contain workflow logic.
# - Contain persistence logic.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping

from alhf.multi_agent_orchestrator.enums.event_type import EventType


@dataclass(frozen=True)
class RuntimeEvent:
    """Canonical runtime event."""

    event_id: str

    correlation_id: str

    workflow_id: str

    event_type: EventType

    task_id: str | None = None

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    payload: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Protect payload from accidental mutation."""
        object.__setattr__(
            self,
            "payload",
            MappingProxyType(dict(self.payload)),
        )
