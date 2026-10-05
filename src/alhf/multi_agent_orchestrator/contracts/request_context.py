# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Defines the immutable request context contract used by
# the Multi-Agent Orchestrator Runtime.
#
# Responsibilities:
# - Carry request metadata.
# - Provide traceability across runtime execution.
# - Support workflow creation.
# - Support observability and auditing.
#
# Must Not:
# - Contain business logic.
# - Contain workflow logic.
# - Contain persistence logic.

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class RequestContext:
    """Immutable request context for runtime execution."""

    request_id: str
    correlation_id: str
    tenant_id: str
    user_id: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    metadata: Mapping[str, Any] = field(
        default_factory=dict
    )

    def __post_init__(self) -> None:
        """Protect mutable metadata from external modification."""
        object.__setattr__(
            self,
            "metadata",
            MappingProxyType(dict(self.metadata)),
        )
