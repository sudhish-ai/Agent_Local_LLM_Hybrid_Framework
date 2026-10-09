# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Loads ALHF domain definitions from filesystem sources.
#
# Responsibilities:
# - Discover domain definition files.
# - Deserialize domain definitions.
# - Create DomainDefinition objects.
# - Return LoaderResult[DomainDefinition].
#
# Must Not:
# - Contain domain business logic.
# - Register domains.
# - Perform orchestration.
# - Perform planning.
# - Depend on runtime components.
#
# Architectural Position:
# - First concrete BaseLoader implementation.
# - Produces DomainDefinition instances.
# - Consumed by DomainRegistry initialization workflows.
#
# Reuse Value:
# - Enables plug-and-play domain onboarding.
# - Separates storage concerns from runtime concerns.
#
# Future Extensibility:
# - YAML domain definitions.
# - Database-backed domain sources.
# - Marketplace sources.
# - Remote domain repositories.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from alhf.core.contracts.loader_result import (
    LoaderResult,
)
from alhf.core.loaders.base_loader import (
    BaseLoader,
)
from alhf.domain.contracts.domain_definition import (
    DomainDefinition,
)


class DomainLoader(
    BaseLoader[
        DomainDefinition,
        Path,
    ]
):
    """
    Loads domain definitions from a directory.

    Expected structure:

    domains/
        travel/
            domain.json

        healthcare/
            domain.json
    """

    DOMAIN_FILE_NAME = "domain.json"

    def load(
        self,
        source: Path,
    ) -> LoaderResult[DomainDefinition]:
        """
        Load domain definitions from the supplied path.
        """

        loaded_domains: list[DomainDefinition] = []
        failed_identifiers: list[str] = []
        warning_messages: list[str] = []

        if not source.exists():
            warning_messages.append(
                f"Source path does not exist: {source}"
            )

            return LoaderResult(
                warning_messages=tuple(
                    warning_messages
                ),
            )

        if not source.is_dir():
            warning_messages.append(
                f"Source is not a directory: {source}"
            )

            return LoaderResult(
                warning_messages=tuple(
                    warning_messages
                ),
            )

        for domain_directory in source.iterdir():

            if not domain_directory.is_dir():
                continue

            domain_file = (
                domain_directory
                / self.DOMAIN_FILE_NAME
            )

            if not domain_file.exists():
                warning_messages.append(
                    f"Missing domain file: {domain_file}"
                )
                continue

            try:
                domain_definition = (
                    self._load_domain_file(
                        domain_file
                    )
                )

                loaded_domains.append(
                    domain_definition
                )

            except Exception:
                failed_identifiers.append(
                    domain_directory.name
                )

        return LoaderResult(
            loaded_items=tuple(
                loaded_domains
            ),
            failed_identifiers=tuple(
                failed_identifiers
            ),
            warning_messages=tuple(
                warning_messages
            ),
        )

    def _load_domain_file(
        self,
        domain_file: Path,
    ) -> DomainDefinition:
        """
        Load a single domain definition file.
        """

        with open(
            domain_file,
            mode="r",
            encoding="utf-8",
        ) as file_handle:
            data = json.load(
                file_handle
            )

        return self._build_domain_definition(
            data=data,
        )

    def _build_domain_definition(
        self,
        data: dict[str, Any],
    ) -> DomainDefinition:
        """
        Convert raw dictionary data into
        a DomainDefinition.
        """

        return DomainDefinition(
            domain_id=data["domain_id"],
            domain_name=data["domain_name"],
            description=data["description"],
            version=data.get(
                "version",
                "1.0",
            ),
            metadata=data.get(
                "metadata",
                {},
            ),
        )
