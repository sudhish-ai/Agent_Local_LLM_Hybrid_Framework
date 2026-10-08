# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Performs hotel search activities for
# Travel Outcome execution.
#
# Responsibilities:
# - Validate destination information.
# - Search hotel inventory.
# - Apply customer preferences.
# - Rank candidate properties.
# - Produce hotel recommendations.
#
# Must Not:
# - Execute workflow orchestration.
# - Perform booking operations.
# - Perform payment processing.
# - Manage scheduler state.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# V1:
# Returns deterministic but realistic
# hotel discovery results.
#
# V5:
# Will integrate:
# - Hotel provider APIs
# - OTA inventory systems
# - Dynamic pricing engines
# - Recommendation intelligence
# - Preference optimization

from __future__ import annotations

import asyncio

from alhf.multi_agent_orchestrator.agents.base_outcome_agent import (
    BaseOutcomeAgent,
)
from alhf.multi_agent_orchestrator.contracts.agent_response import (
    AgentResponse,
)
from alhf.multi_agent_orchestrator.contracts.task_context import (
    TaskContext,
)


class HotelSearchAgent(
    BaseOutcomeAgent,
):
    """
    Hotel search capability.
    """

    @property
    def agent_id(
        self,
    ) -> str:
        return "hotel-search-agent"

    @property
    def capability(
        self,
    ) -> str:
        return "hotel_search"

    @property
    def success_message(
        self,
    ) -> str:
        return (
            "Hotel search completed successfully."
        )

    async def _show_progress(
        self,
        activity: str,
        duration_seconds: float,
    ) -> None:
        """
        Simulate realistic execution progress.
        """

        print(
            f"\n{activity}"
        )

        for progress in (
            20,
            40,
            60,
            80,
            100,
        ):
            await asyncio.sleep(
                duration_seconds / 5,
            )

            print(
                f"   [{progress}%]"
            )

        print(
            "   ✓ Completed"
        )

    async def execute(
        self,
        task_context: TaskContext,
    ) -> AgentResponse:
        print(
            "\n[HotelSearchAgent]"
        )

        await self._show_progress(
            activity=(
                "Validating destination..."
            ),
            duration_seconds=20,
        )

        await self._show_progress(
            activity=(
                "Searching Goa hotel inventory..."
            ),
            duration_seconds=20,
        )

        await self._show_progress(
            activity=(
                "Applying customer preferences..."
            ),
            duration_seconds=20,
        )

        await self._show_progress(
            activity=(
                "Ranking candidate properties..."
            ),
            duration_seconds=20,
        )

        return AgentResponse(
            status="SUCCESS",
            confidence=1.0,
            result={
                "destination":
                    "Goa",
                "inventory_size":
                    124,
                "matching_hotels":
                    15,
                "recommended_hotel":
                    "Sea Breeze Resort",
                "hotel_rating":
                    4.7,
                "distance_to_beach":
                    "200m",
                "search_status":
                    "completed",
            },
            evidence=[
                {
                    "activity":
                        "hotel_inventory_search",
                    "status":
                        "completed",
                },
                {
                    "activity":
                        "hotel_ranking",
                    "status":
                        "completed",
                },
            ],
            metadata={
                "agent_id":
                    self.agent_id,
                "capability":
                    self.capability,
            },
        )
