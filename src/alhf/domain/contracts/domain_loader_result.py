# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides the canonical result contract returned by
# domain loading operations across ALHF.
#
# Responsibilities:
# - Represent successfully loaded domains.
# - Represent failed domain load attempts.
# - Provide loading summary information.
# - Provide a stable loader response contract.
#
# Must Not:
# - Load domains from files.
# - Perform registration.
# - Perform validation.
# - Perform orchestration.
# - Perform planning.
# - Contain filesystem logic.
#
# Architectural Position:
# - Domain loading contract.
# - Produced by DomainLoader implementations.
# - Consumed by DomainRegistry initialization workflows.
#
# Reuse Value:
# - Shared by all future domain loading mechanisms.
# - Supports filesystem, database, API, and marketplace loaders.
#
# Future Extensibility:
# - Domain version compatibility reporting.
# - Warning collection.
# - Partial load recovery.
# - Marketplace distribution support.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from alhf.domain.contracts.domain_definition import (
    DomainDefinition,
)


@dataclass(frozen=True, slots=True)
class DomainLoaderResult:
    """
    Canonical ALHF domain loading result.

    Represents the outcome of a domain discovery
    and loading operation.
    """

    loaded_domains: tuple[DomainDefinition, ...] = field(
        default_factory=tuple,
    )

    failed_domain_identifiers: tuple[str, ...] = field(
        default_factory=tuple,
    )

    warning_messages: tuple[str, ...] = field(
        default_factory=tuple,
    )

    @property
    def loaded_count(self) -> int:
        """
        Number of successfully loaded domains.
        """

        return len(self.loaded_domains)

    @property
    def failed_count(self) -> int:
        """
        Number of failed domain loads.
        """

        return len(self.failed_domain_identifiers)

    @property
    def has_failures(self) -> bool:
        """
        Indicates whether any failures occurred.
        """

        return self.failed_count > 0

    @property
    def has_warnings(self) -> bool:
        """
        Indicates whether warnings were generated.
        """

        return len(self.warning_messages) > 0

    @property
    def is_successful(self) -> bool:
        """
        Indicates whether all domains loaded successfully.
        """

        return self.failed_count == 0
