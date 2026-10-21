# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Demonstrates end-to-end healthcare outcome
# execution using the ALHF Runtime platform.
#
# Responsibilities:
# - Demonstrate healthcare workflow execution.
# - Demonstrate AgentRuntime reuse.
# - Demonstrate WorkflowExecutor reuse.
# - Demonstrate CapabilityRuntime reuse.
# - Demonstrate cross-domain runtime compatibility.
# - Demonstrate business outcome generation.
#
# Must Not:
# - Act as production code.
# - Modify runtime behavior.
# - Contain orchestration logic.
# - Duplicate runtime responsibilities.
#
# Design Philosophy:
# Design For V5.
# Implement For V2.
#
# V2 Goal:
# Prove ALHF runtime remains domain agnostic
# while executing healthcare workflows using
# the same runtime foundation used by Travel.

from __future__ import annotations

import asyncio
import time

from pathlib import Path

from domains.healthcare.agents.appointment_booking_agent import (
    AppointmentBookingAgent,
)
from domains.healthcare.agents.provider_search_agent import (
    ProviderSearchAgent,
)

from alhf.capability.capability_registry import (
    CapabilityRegistry,
)
from alhf.capability.capability_runtime import (
    CapabilityRuntime,
)
from alhf.capability.capability_selection_engine import (
    CapabilitySelectionEngine,
)
from alhf.capability.json_capability_definition_loader import (
    JsonCapabilityDefinitionLoader,
)

from alhf.domain.domain_capability_registry import (
    DomainCapabilityRegistry,
)
from alhf.domain.domain_capability_resolver import (
    DomainCapabilityResolver,
)
from alhf.domain.json_domain_capability_loader import (
    JsonDomainCapabilityLoader,
)

from alhf.intent.intent_capability_registry import (
    IntentCapabilityRegistry,
)
from alhf.intent.intent_capability_resolver import (
    IntentCapabilityResolver,
)
from alhf.intent.json_intent_capability_loader import (
    JsonIntentCapabilityLoader,
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
        "ALHF Healthcare Outcome Driven Runtime Demo\n"
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
        "\n[STEP 2] Registering Healthcare Agents..."
    )

    await agent_runtime.register_agent(
        ProviderSearchAgent(),
    )

    await agent_runtime.register_agent(
        AppointmentBookingAgent(),
    )

    print(
        "[SUCCESS] Healthcare agents registered."
    )

    print(
        "\n[STEP 3] Creating Healthcare Outcome..."
    )

    customer_goal = (
        "Book an appointment with a "
        "cardiologist tomorrow."
    )

    print(
        f"Goal: {customer_goal}"
    )

    print(
        "\n[STEP 4] Building Capability Intelligence..."
    )

    capability_registry = (
        CapabilityRegistry()
    )

    intent_registry = (
        IntentCapabilityRegistry()
    )

    domain_registry = (
        DomainCapabilityRegistry()
    )

    capability_loader = (
        JsonCapabilityDefinitionLoader()
    )

    capability_result = (
        capability_loader.load(
            Path(
                "capabilities/"
                "capability_definitions.json"
            )
        )
    )

    for capability in (
        capability_result.loaded_items
    ):
        capability_registry.register(
            capability
        )

    domain_loader = (
        JsonDomainCapabilityLoader()
    )

    domain_result = (
        domain_loader.load(
            Path(
                "domains/healthcare/"
                "capabilities.json"
            )
        )
    )

    for mapping in (
        domain_result.loaded_items
    ):
        domain_registry.register(
            mapping
        )

    intent_loader = (
        JsonIntentCapabilityLoader()
    )

    intent_result = (
        intent_loader.load(
            Path(
                "domains/healthcare/"
                "intents.json"
            )
        )
    )

    for mapping in (
        intent_result.loaded_items
    ):
        intent_registry.register(
            mapping
        )

    print(
        f"Capabilities Loaded : "
        f"{capability_result.loaded_count}"
    )

    for warning in (
        capability_result.warning_messages
    ):
        print(
            f"[WARNING] {warning}"
        )

    print(
        f"Capabilities Registered : "
        f"{capability_registry.count()}"
    )

    print(
        f"Intent Mappings Loaded : "
        f"{intent_result.loaded_count}"
    )

    print(
        f"Domain Mappings Loaded : "
        f"{domain_result.loaded_count}"
    )

    capability_runtime = (
        CapabilityRuntime(
            intent_capability_resolver=(
                IntentCapabilityResolver(
                    capability_registry=
                    capability_registry,
                    intent_capability_registry=
                    intent_registry,
                )
            ),
            domain_capability_resolver=(
                DomainCapabilityResolver(
                    capability_registry=
                    capability_registry,
                    domain_capability_registry=
                    domain_registry,
                )
            ),
            domain_capability_registry=(
                domain_registry
            ),
            capability_selection_engine=(
                CapabilitySelectionEngine()
            ),
        )
    )

    selected_capabilities = (
        capability_runtime
        .select_capabilities(
            intent_id=
            "appointment_booking",
            domain_id=
            "healthcare",
        )
    )

    print(
        "[SUCCESS] Capability "
        "Runtime initialized."
    )

    print(
        "\nSelected Capabilities:"
    )

    for capability in (
        selected_capabilities
    ):
        print(
            f"  - "
            f"{capability.capability_id}"
        )

    print(
        "=======" * 20
    )

    time.sleep(10)

    print(
        "\n[STEP 5] Building Workflow..."
    )

    workflow = WorkflowDefinition(
        workflow_id=
        "healthcare_001",
        workflow_type=
        "appointment_booking",
        tasks=[
            TaskDefinition(
                task_id=
                "provider_search",
                workflow_id=
                "healthcare_001",
                capability=
                "provider_search",
            ),
            TaskDefinition(
                task_id=
                "appointment_booking",
                workflow_id=
                "healthcare_001",
                capability=
                "appointment_booking",
                dependencies=[
                    "provider_search",
                ],
            ),
        ],
    )

    print(
        "[SUCCESS] Workflow created."
    )

    print(
        "\nHealthcare Workflow:"
    )

    print(
        "Provider Search"
    )

    print(
        "        ↓"
    )

    print(
        "Appointment Booking"
    )

    print(
        "\n[STEP 6] Building Executors..."
    )

    task_executor = TaskExecutor(
        task_repository=
        task_repository,
        agent_runtime=
        agent_runtime,
    )

    workflow_executor = WorkflowExecutor(
        scheduler=
        scheduler,
        task_executor=
        task_executor,
    )

    print(
        "[SUCCESS] Executors initialized."
    )

    print(
        "\n[STEP 7] Executing Healthcare Workflow..."
    )

    workflow_result = (
        await workflow_executor.execute(
            workflow,
        )
    )

    print(
        "\n"
        "====================================================\n"
        "HEALTHCARE EXECUTION SUMMARY\n"
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

    provider_search_result = None
    appointment_booking_result = None

    for result in workflow_result.results:
        task_id = result["task_id"]

        if task_id == "provider_search":
            provider_search_result = (
                result["result"]
            )

        elif task_id == "appointment_booking":
            appointment_booking_result = (
                result["result"]
            )

    print(
        "\n"
        "====================================================\n"
        "HEALTHCARE OUTCOME\n"
        "===================================================="
    )

    if provider_search_result:
        print(
            "\nPROVIDER SEARCH"
        )

        print(
            "----------------------------------------------------"
        )

        print(
            f"Specialty             : "
            f"{provider_search_result.get('specialty')}"
        )

        print(
            f"Providers Found       : "
            f"{provider_search_result.get('provider_count')}"
        )

        print(
            f"Matching Providers    : "
            f"{provider_search_result.get('matching_providers')}"
        )

        print(
            f"Recommended Provider  : "
            f"{provider_search_result.get('recommended_provider')}"
        )

    if appointment_booking_result:
        print(
            "\nAPPOINTMENT BOOKING"
        )

        print(
            "----------------------------------------------------"
        )

        print(
            f"Booking Status        : "
            f"{appointment_booking_result.get('booking_status')}"
        )

        print(
            f"Appointment Ref       : "
            f"{appointment_booking_result.get('appointment_reference')}"
        )

        print(
            f"Provider              : "
            f"{appointment_booking_result.get('provider_name')}"
        )

        print(
            f"Appointment Time      : "
            f"{appointment_booking_result.get('appointment_time')}"
        )

    print(
        "\n"
        "===================================================="
    )

    print(
        "HEALTHCARE OUTCOME SUCCESSFULLY ACHIEVED"
    )

    print(
        "===================================================="
    )


if __name__ == "__main__":
    asyncio.run(main())
