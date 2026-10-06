# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the generic loading result contract used across ALHF.
#
# Responsibilities:
# - Represent successful loads.
# - Represent failed loads.
# - Provide warning information.
# - Provide loading summary metrics.
#
# Must Not:
# - Contain domain-specific logic.
# - Contain capability-specific logic.
# - Perform loading operations.
# - Perform filesystem operations.
# - Perform orchestration.
#
# Architectural Position:
# - Core infrastructure contract.
# - Shared by all ALHF loaders.
#
# Reuse Value:
# - Domain Loader.
# - Capability Loader.
# - Knowledge Loader.
# - Strategy Loader.
# - Template Loader.
# - Solution Loader.
#
# Future Extensibility:
# - Loader diagnostics.
# - Partial recovery support.
# - Version compatibility reporting.
# - Load provenance tracking.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from typing import Generic
from typing import TypeVar


TItem = TypeVar("TItem")


@dataclass(frozen=True, slots=True)
class LoaderResult(Generic[TItem]):
    """
    Generic ALHF loader result.
    """

    loaded_items: tuple[TItem, ...] = field(
        default_factory=tuple
    )

    failed_identifiers: tuple[str, ...] = field(
        default_factory=tuple
    )

    warning_messages: tuple[str, ...] = field(
        default_factory=tuple
    )

    @property
    def loaded_count(self) -> int:
        return len(self.loaded_items)

    @property
    def failed_count(self) -> int:
        return len(self.failed_identifiers)

    @property
    def has_failures(self) -> bool:
        return self.failed_count > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warning_messages) > 0

    @property
    def is_successful(self) -> bool:
        return self.failed_count == 0
