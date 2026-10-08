# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Loads IntentCapabilityMapping instances
# from JSON knowledge assets.
#
# Responsibilities:
# - Read JSON knowledge assets.
# - Deserialize JSON content.
# - Create IntentCapabilityMapping objects.
# - Return LoaderResult[IntentCapabilityMapping].
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
#   IntentCapabilityMapping knowledge assets.
#
# Future Extensibility:
# - DatabaseIntentCapabilityLoader
# - ApiIntentCapabilityLoader
# - LearningStoreIntentCapabilityLoader
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
from alhf.intent.contracts.intent_capability_mapping import (
    IntentCapabilityMapping,
)


class JsonIntentCapabilityLoader(
    BaseLoader[
        IntentCapabilityMapping,
        Path,
    ]
):
    """
    Loads IntentCapabilityMapping instances
    from JSON knowledge assets.
    """

    def load(
        self,
        source: Path,
    ) -> LoaderResult[
        IntentCapabilityMapping
    ]:
        """
        Load intent capability mappings
        from a JSON knowledge asset.
        """

        warning_messages: list[str] = []

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

        mappings = tuple(
            IntentCapabilityMapping(
                intent_id=item[
                    "intent_id"
                ],
                capability_ids=tuple(
                    item[
                        "capability_ids"
                    ]
                ),
            )
            for item in data[
                "intent_capability_mappings"
            ]
        )

        return LoaderResult(
            loaded_items=mappings,
        )
