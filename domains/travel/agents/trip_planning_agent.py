# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Performs trip planning activities for
# Travel Outcome execution.
#
# Responsibilities:
# - Generate travel itinerary.
# - Recommend local attractions.
# - Organize daily activities.
# - Produce travel summary.
# - Generate travel execution evidence.
#
# Must Not:
# - Execute workflow orchestration.
# - Perform hotel search.
# - Perform hotel booking.
# - Manage scheduler state.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# V1:
# Produces deterministic but realistic
# trip planning outcomes.
#
# V5:
# Will integrate:
# - Destination intelligence
# - Live attractions
# - Weather services
# - Local travel optimization
# - Dynamic itinerary generation

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


class TripPlanningAgent(
    BaseOutcomeAgent,
):
    """
    Trip planning capability.
    """

    @property
    def agent_id(
        self,
    ) -> str:
        return "trip-planning-agent"

    @property
    def capability(
        self,
    ) -> str:
        return "trip_planning"

    @property
    def success_message(
        self,
    ) -> str:
        return (
            "Trip planning completed successfully."
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
            "\n[TripPlanningAgent]"
        )

        await self._show_progress(
            activity=(
                "Building travel itinerary..."
            ),
            duration_seconds=20,
        )

        await self._show_progress(
            activity=(
                "Analyzing local attractions..."
            ),
            duration_seconds=20,
        )

        await self._show_progress(
            activity=(
                "Planning daily activities..."
            ),
            duration_seconds=20,
        )

        await self._show_progress(
            activity=(
                "Generating travel recommendations..."
            ),
            duration_seconds=20,
        )

        await self._show_progress(
            activity=(
                "Preparing travel package..."
            ),
            duration_seconds=20,
        )

        return AgentResponse(
            status="SUCCESS",
            confidence=1.0,
            result={
                "destination":
                    "Goa",
                "trip_duration":
                    "5 Days",
                "itinerary_status":
                    "generated",
                "recommended_attractions": [
                    "Calangute Beach",
                    "Fort Aguada",
                    "Dudhsagar Falls",
                ],
                "day_1_plan":
                    "Beach and Resort Activities",
                "day_2_plan":
                    "North Goa Sightseeing",
                "day_3_plan":
                    "Adventure Activities",
                "travel_package_status":
                    "completed",
            },
            evidence=[
                {
                    "activity":
                        "itinerary_generation",
                    "status":
                        "completed",
                },
                {
                    "activity":
                        "attraction_analysis",
                    "status":
                        "completed",
                },
                {
                    "activity":
                        "travel_package_creation",
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
