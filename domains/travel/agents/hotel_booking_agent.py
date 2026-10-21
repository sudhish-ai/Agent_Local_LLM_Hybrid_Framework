# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Performs hotel reservation activities for
# Travel Outcome execution.
#
# Responsibilities:
# - Validate selected hotel.
# - Verify room availability.
# - Reserve hotel inventory.
# - Generate booking confirmation.
# - Produce booking execution evidence.
#
# Must Not:
# - Execute workflow orchestration.
# - Perform trip planning.
# - Perform scheduler activities.
# - Process real payments.
#
# Design Philosophy:
# Design For V5.
# Implement For V1.
#
# V1:
# Produces deterministic but realistic
# hotel booking outcomes.
#
# V5:
# Will integrate:
# - Hotel reservation systems
# - OTA providers
# - Inventory services
# - Payment gateways
# - Cancellation workflows

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


class HotelBookingAgent(
    BaseOutcomeAgent,
):
    """
    Hotel booking capability.
    """

    @property
    def agent_id(
        self,
    ) -> str:
        return "hotel-booking-agent"

    @property
    def capability(
        self,
    ) -> str:
        return "hotel_booking"

    @property
    def success_message(
        self,
    ) -> str:
        return (
            "Hotel booking completed successfully."
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
            "\n[HotelBookingAgent]"
        )

        await self._show_progress(
            activity=(
                "Validating selected hotel..."
            ),
            duration_seconds=5,
        )

        await self._show_progress(
            activity=(
                "Checking room inventory..."
            ),
            duration_seconds=5,
        )

        await self._show_progress(
            activity=(
                "Creating reservation..."
            ),
            duration_seconds=5,
        )

        await self._show_progress(
            activity=(
                "Generating booking reference..."
            ),
            duration_seconds=5,
        )

        await self._show_progress(
            activity=(
                "Preparing customer confirmation..."
            ),
            duration_seconds=5,
        )

        return AgentResponse(
            status="SUCCESS",
            confidence=1.0,
            result={
                "booking_status":
                    "confirmed",
                "booking_reference":
                    "GOA-2026-0001",
                "hotel_name":
                    "Sea Breeze Resort",
                "room_type":
                    "Ocean View Deluxe",
                "stay_duration":
                    "5 Days",
                "reservation_status":
                    "completed",
            },
            evidence=[
                {
                    "activity":
                        "inventory_validation",
                    "status":
                        "completed",
                },
                {
                    "activity":
                        "hotel_reservation",
                    "status":
                        "completed",
                },
                {
                    "activity":
                        "confirmation_generation",
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
