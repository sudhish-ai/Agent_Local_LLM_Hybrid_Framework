# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Repository Intelligence Domain Pack.
#
# Responsibilities:
# - Define supported repository intents.
# - Define supported repository strategies.
# - Define workflow templates.
# - Provide repository domain knowledge.
#
# Must Not:
# - Contain planner logic.
# - Contain workflow execution logic.
# - Contain strategy selection logic.
# - Contain orchestration logic.

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class RepositoryDomainPack:
    """
    Repository Intelligence domain knowledge.
    """

    supported_intents: list[str] = field(
        default_factory=lambda: [
            "repository_analysis",
            "build_failure_analysis",
            "release_note_generation",
            "test_strategy_generation",
        ]
    )

    supported_strategies: list[str] = field(
        default_factory=lambda: [
            "root_cause_analysis",
            "release_note_generation",
            "risk_based_test_strategy",
            "repository_inspection",
        ]
    )

    workflow_templates: dict[str, str] = field(
        default_factory=lambda: {
            "repository_analysis":
                "root_cause_analysis",
            "build_failure_analysis":
                "root_cause_analysis",
            "release_note_generation":
                "release_note_generation",
            "test_strategy_generation":
                "risk_based_test_strategy",
        }
    )
