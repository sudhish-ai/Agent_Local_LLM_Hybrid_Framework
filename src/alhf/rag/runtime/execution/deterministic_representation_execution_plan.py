# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic V1 representation fan-out for the ALHF Knowledge
# Foundation production ingestion runtime.
#
# Responsibilities:
# - Accept one validated Knowledge Unit.
# - Delegate representation creation to configured RepresentationService.
# - Yield representation artifacts incrementally.
# - Keep V1 provider execution behind the stable fan-out boundary.
#
# Must Not:
# - Select representation providers dynamically.
# - Perform indexing, retrieval, Evidence, or Context construction.
# - Materialize representation collections.
# - Contain source-specific or file-format-specific behavior.
# - Implement Representation Intelligence or execution policy.
#
# Architectural Position:
# - Deterministic V1 implementation of representation execution planning.
# - Consumed by Knowledge ingestion orchestration.
#
# Future Extensibility:
# - Future plans can execute multiple governed representation services.
# - Intelligence can evolve behind the stable execution-plan interface.

from __future__ import annotations

from collections.abc import Iterator

from alhf.rag.chunking.contracts.knowledge_unit import KnowledgeUnit
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)
from alhf.rag.representation.representation_service import (
    RepresentationService,
)
from alhf.rag.runtime.interfaces.knowledge_representation_execution_plan import (
    KnowledgeRepresentationExecutionPlan,
)


class DeterministicRepresentationExecutionPlan(
    KnowledgeRepresentationExecutionPlan,
):
    """Execute one configured deterministic representation path."""

    def __init__(
        self,
        *,
        service: RepresentationService,
    ) -> None:
        if not isinstance(
            service,
            RepresentationService,
        ):
            raise TypeError(
                "service must be an instance of RepresentationService"
            )

        self._service = service

    def execute(
        self,
        unit: KnowledgeUnit,
    ) -> Iterator:
        """Yield the representation produced for one Knowledge Unit."""

        if not isinstance(
            unit,
            KnowledgeUnit,
        ):
            raise TypeError(
                "unit must be an instance of KnowledgeUnit"
            )

        representation = self._service.represent(
            unit
        )

        if not isinstance(
            representation,
            KnowledgeRepresentation,
        ):
            raise TypeError(
                "RepresentationService must return "
                "KnowledgeRepresentation"
            )

        yield representation
