# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Demonstrates end-to-end travel outcome execution
# using the ALHF Runtime platform.
#
# Responsibilities:
# - Demonstrate travel workflow execution.
# - Demonstrate AgentRuntime reuse.
# - Demonstrate WorkflowExecutor reuse.
# - Demonstrate cross-domain runtime compatibility.
# - Demonstrate business outcome generation.
#
# Must Not:
# - Act as production code.
# - Modify runtime behavior.
# - Contain orchestration logic.
# - Duplicate runtime responsibilities.

from __future__ import annotations

import asyncio

from domains.travel.agents.hotel_booking_agent import (
    HotelBookingAgent,
)
from domains.travel.agents.hotel_search_agent import (
    HotelSearchAgent,
)
from domains.travel.agents.trip_planning_agent import (
    TripPlanningAgent,
)

from alhf.multi_agent_orchestrator.contracts.task_definition import (
    TaskDefinition,
)
from alhf.multi_agent_orchestrator.contracts.workflow_definition import (
    WorkflowDefinition,
)
from alhf.multi_agent_orchestrator.execution.task_executor import (
    TaskExecutor,
)
from alhf.multi_agent_orchestrator.execution.workflow_executor import (
    WorkflowExecutor,
)
from alhf.multi_agent_orchestrator.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from alhf.multi_agent_orchestrator.runtime.agent_runtime import (
    AgentRuntime,
)
from alhf.multi_agent_orchestrator.scheduler.in_memory_scheduler import (
    InMemoryScheduler,
)


def print_banner() -> None:
    print(
        "\n"
        "====================================================\n"
        "ALHF Travel Outcome Driven Runtime Demo\n"
        "===================================================="
    )


async def main() -> None:
    print_banner()

    print(
        "\n[STEP 1] Building Runtime Components..."
    )

    task_repository = (
        InMemoryTaskRepository()
    )

    scheduler = (
        InMemoryScheduler()
    )

    agent_runtime = (
        AgentRuntime()
    )

    print(
        "[SUCCESS] Runtime components initialized."
    )

    print(
        "\n[STEP 2] Registering Travel Agents..."
    )

    await agent_runtime.register_agent(
        HotelSearchAgent(),
    )

    await agent_runtime.register_agent(
        HotelBookingAgent(),
    )

    await agent_runtime.register_agent(
        TripPlanningAgent(),
    )

    print(
        "[SUCCESS] Travel agents registered."
    )

    print(
        "\n[STEP 3] Creating Travel Outcome..."
    )

    customer_goal = (
        "Book a beachfront hotel in Goa "
        "and create a 5 day itinerary."
    )

    print(
        f"Goal: {customer_goal}"
    )

    print(
        "\n[STEP 4] Building Workflow..."
    )

    workflow = WorkflowDefinition(
        workflow_id="travel_001",
        workflow_type="travel_booking",
        tasks=[
            TaskDefinition(
                task_id="hotel_search",
                workflow_id="travel_001",
                capability="hotel_search",
            ),
            TaskDefinition(
                task_id="hotel_booking",
                workflow_id="travel_001",
                capability="hotel_booking",
                dependencies=[
                    "hotel_search",
                ],
            ),
            TaskDefinition(
                task_id="trip_planning",
                workflow_id="travel_001",
                capability="trip_planning",
                dependencies=[
                    "hotel_booking",
                ],
            ),
        ],
    )

    print(
        "[SUCCESS] Workflow created."
    )

    print(
        "\nTravel Workflow:"
    )

    print(
        "Hotel Search"
    )

    print(
        "        ↓"
    )

    print(
        "Hotel Booking"
    )

    print(
        "        ↓"
    )

    print(
        "Trip Planning"
    )

    print(
        "\n[STEP 5] Building Executors..."
    )

    task_executor = TaskExecutor(
        task_repository=task_repository,
        agent_runtime=agent_runtime,
    )

    workflow_executor = WorkflowExecutor(
        scheduler=scheduler,
        task_executor=task_executor,
    )

    print(
        "[SUCCESS] Executors initialized."
    )

    print(
        "\n[STEP 6] Executing Travel Workflow..."
    )

    workflow_result = (
        await workflow_executor.execute(
            workflow,
        )
    )

    print(
        "\n"
        "====================================================\n"
        "TRAVEL EXECUTION SUMMARY\n"
        "===================================================="
    )

    print(
        f"Workflow Id      : "
        f"{workflow_result.workflow_id}"
    )

    print(
        f"Workflow Type    : "
        f"{workflow_result.workflow_type}"
    )

    print(
        f"Execution Status : "
        f"{workflow_result.final_status}"
    )

    print(
        f"Tasks Executed   : "
        f"{len(workflow_result.results)}"
    )

    hotel_search_result = None
    hotel_booking_result = None
    trip_plan_result = None

    for result in workflow_result.results:
        task_id = result["task_id"]

        if task_id == "hotel_search":
            hotel_search_result = (
                result["result"]
            )

        elif task_id == "hotel_booking":
            hotel_booking_result = (
                result["result"]
            )

        elif task_id == "trip_planning":
            trip_plan_result = (
                result["result"]
            )

    print(
        "\n"
        "====================================================\n"
        "TRAVEL OUTCOME\n"
        "===================================================="
    )

    if hotel_search_result:
        print(
            "\nHOTEL SEARCH"
        )

        print(
            "----------------------------------------------------"
        )

        print(
            f"Destination       : "
            f"{hotel_search_result.get('destination')}"
        )

        print(
            f"Hotels Found      : "
            f"{hotel_search_result.get('inventory_size')}"
        )

        print(
            f"Recommended Hotel : "
            f"{hotel_search_result.get('recommended_hotel')}"
        )

    if hotel_booking_result:
        print(
            "\nHOTEL BOOKING"
        )

        print(
            "----------------------------------------------------"
        )

        print(
            f"Booking Status    : "
            f"{hotel_booking_result.get('booking_status')}"
        )

        print(
            f"Booking Reference : "
            f"{hotel_booking_result.get('booking_reference')}"
        )

        print(
            f"Room Type         : "
            f"{hotel_booking_result.get('room_type')}"
        )

    if trip_plan_result:
        print(
            "\nTRIP PLAN"
        )

        print(
            "----------------------------------------------------"
        )

        print(
            f"Destination       : "
            f"{trip_plan_result.get('destination')}"
        )

        print(
            f"Trip Duration     : "
            f"{trip_plan_result.get('trip_duration')}"
        )

        print(
            f"Itinerary Status  : "
            f"{trip_plan_result.get('itinerary_status')}"
        )

    print(
        "\n"
        "===================================================="
    )

    print(
        "TRAVEL OUTCOME SUCCESSFULLY ACHIEVED"
    )

    print(
        "===================================================="
    )


if __name__ == "__main__":
    asyncio.run(main())
