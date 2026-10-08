# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Loads CapabilityDefinition instances
# from JSON knowledge assets.
#
# Responsibilities:
# - Read JSON knowledge assets.
# - Deserialize JSON content.
# - Create CapabilityDefinition objects.
# - Return LoaderResult[CapabilityDefinition].
#
# Must Not:
# - Register capabilities.
# - Perform capability selection.
# - Perform planning.
# - Perform orchestration.
# - Perform execution.
#
# Architectural Position:
# - JSON knowledge adapter.
# - First implementation of loading
#   CapabilityDefinition knowledge assets.
#
# Future Extensibility:
# - DatabaseCapabilityDefinitionLoader
# - ApiCapabilityDefinitionLoader
# - LearningStoreCapabilityDefinitionLoader
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

import json
from pathlib import Path

from alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)
from alhf.core.contracts.loader_result import (
    LoaderResult,
)
from alhf.core.loaders.base_loader import (
    BaseLoader,
)


class JsonCapabilityDefinitionLoader(
    BaseLoader[
        CapabilityDefinition,
        Path,
    ]
):
    """
    Loads CapabilityDefinition instances
    from JSON knowledge assets.
    """

    def load(
        self,
        source: Path,
    ) -> LoaderResult[
        CapabilityDefinition
    ]:
        """
        Load capability definitions
        from a JSON knowledge asset.
        """

        warning_messages: list[
            str
        ] = []

        if not source.exists():
            warning_messages.append(
                (
                    "Source path does not exist: "
                    f"{source}"
                )
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

        capabilities = tuple(
            CapabilityDefinition(
                capability_id=item[
                    "capability_id"
                ],
                capability_name=item[
                    "capability_name"
                ],
                description=item[
                    "description"
                ],
                version=item.get(
                    "version",
                    "1.0",
                ),
                metadata=item.get(
                    "metadata",
                    {},
                ),
            )
            for item in data[
                "capabilities"
            ]
        )

        return LoaderResult(
            loaded_items=capabilities,
        )
