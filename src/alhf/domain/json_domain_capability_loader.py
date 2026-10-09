# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Loads DomainCapabilityMapping instances
# from JSON knowledge assets.
#
# Responsibilities:
# - Read JSON knowledge assets.
# - Deserialize JSON content.
# - Create DomainCapabilityMapping.
# - Return LoaderResult[DomainCapabilityMapping].
#
# Must Not:
# - Perform capability selection.
# - Perform planning.
# - Perform orchestration.
# - Perform execution.
# - Perform registration.
#
# Architectural Position:
# - JSON knowledge adapter.
# - First implementation of loading
#   DomainCapabilityMapping knowledge assets.
#
# Future Extensibility:
# - DatabaseDomainCapabilityLoader
# - ApiDomainCapabilityLoader
# - LearningStoreDomainCapabilityLoader
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

import json
from pathlib import Path

from alhf.core.contracts.loader_result import (
    LoaderResult,
)
from alhf.core.loaders.base_loader import (
    BaseLoader,
)
from alhf.domain.contracts.domain_capability_mapping import (
    DomainCapabilityMapping,
)


class JsonDomainCapabilityLoader(
    BaseLoader[
        DomainCapabilityMapping,
        Path,
    ]
):
    """
    Loads DomainCapabilityMapping instances
    from JSON knowledge assets.
    """

    def load(
        self,
        source: Path,
    ) -> LoaderResult[
        DomainCapabilityMapping
    ]:
        """
        Load a DomainCapabilityMapping
        from a JSON knowledge asset.
        """

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

        with open(
            source,
            mode="r",
            encoding="utf-8",
        ) as file_handle:
            data = json.load(
                file_handle,
            )

        mapping = DomainCapabilityMapping(
            domain_id=data["domain_id"],
            capability_ids=tuple(
                data["capability_ids"],
            ),
            mandatory_capability_ids=tuple(
                data.get(
                    "mandatory_capability_ids",
                    [],
                ),
            ),
        )

        return LoaderResult(
            loaded_items=(
                mapping,
            ),
        )
