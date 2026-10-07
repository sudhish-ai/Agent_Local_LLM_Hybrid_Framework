# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Selects the most appropriate capability
# from a resolved capability set.
#
# Responsibilities:
# - Evaluate candidate capabilities.
# - Select best matching capability.
# - Provide deterministic capability ranking.
#
# Must Not:
# - Perform workflow planning.
# - Perform workflow execution.
# - Perform orchestration.
# - Perform LLM reasoning.
#
# Architectural Position:
# - Bridge between domain resolution
#   and workflow planning.
#
# Future Extensibility:
# - Semantic similarity.
# - Embedding ranking.
# - LLM-based selection.
# - Historical outcome scoring.
#
# Design Principle:
# Think Hard Once. Implement Many Times.

from __future__ import annotations

from src.alhf.capability.contracts.capability_definition import (
    CapabilityDefinition,
)


class CapabilitySelector:
    """
    Selects the most appropriate capability.
    """

    def select(
        self,
        intent_text: str,
        capabilities: tuple[
            CapabilityDefinition,
            ...
        ],
    ) -> CapabilityDefinition:
        """
        Select a capability from the
        provided candidates.
        """

        if not capabilities:
            raise ValueError(
                "At least one capability "
                "must be provided."
            )

        normalized_intent = (
            intent_text.lower()
        )

        best_capability = capabilities[0]
        best_score = -1

        for capability in capabilities:

            score = 0

            capability_name = (
                capability.capability_name
                .lower()
            )

            capability_id = (
                capability.capability_id
                .lower()
            )

            description = (
                capability.description
                .lower()
            )

            for token in (
                normalized_intent.split()
            ):
                if token in capability_id:
                    score += 3

                if token in capability_name:
                    score += 2

                if token in description:
                    score += 1

            if score > best_score:
                best_score = score
                best_capability = capability

        return best_capability
