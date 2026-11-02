# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh
#
# Purpose:
# Provides deterministic V1 indexing behind the stable ALHF Knowledge
# Foundation index-execution fan-out boundary.
#
# Problem Solved:
# V1 requires one governed logical index destination without embedding
# that destination or single-index assumptions in ingestion orchestration.
#
# Responsibilities:
# - Accept one validated KnowledgeRepresentation.
# - Delegate indexing to the configured IndexingService.
# - Target one configured logical V1 index.
# - Return the number of successful logical index writes.
#
# Must Not:
# - Generate or modify Knowledge representations.
# - Implement physical index-provider behavior.
# - Select indexes dynamically.
# - Perform retrieval, Evidence, or Context construction.
# - Contain source-specific or file-format-specific behavior.
#
# Architectural Position:
# - Deterministic V1 implementation of KnowledgeIndexExecutionPlan.
# - Keeps logical index destination outside KnowledgeIngestionService.
#
# Future Extensibility:
# - Future plans may fan out to multiple governed logical indexes.
# - Index Intelligence can evolve behind the stable execution boundary.

from __future__ import annotations

from alhf.rag.indexing.indexing_service import IndexingService
from alhf.rag.representation.contracts.knowledge_representation import (
    KnowledgeRepresentation,
)
from alhf.rag.runtime.interfaces.knowledge_index_execution_plan import (
    KnowledgeIndexExecutionPlan,
)


class DeterministicIndexExecutionPlan(KnowledgeIndexExecutionPlan):
    """Execute one configured logical V1 index write."""

    def __init__(
        self,
        *,
        service: IndexingService,
        index_ref: str,
    ) -> None:
        if not isinstance(
            service,
            IndexingService,
        ):
            raise TypeError(
                "service must be an instance of IndexingService"
            )

        self._service = service
        self._index_ref = self._required_text(
            value=index_ref,
            field_name="index_ref",
        )

    def execute(
        self,
        representation: KnowledgeRepresentation,
    ) -> int:
        """Index one representation and report one successful write."""

        if not isinstance(
            representation,
            KnowledgeRepresentation,
        ):
            raise TypeError(
                "representation must be an instance of "
                "KnowledgeRepresentation"
            )

        self._service.index(
            index_ref=self._index_ref,
            representation=representation,
        )

        return 1

    @staticmethod
    def _required_text(
        *,
        value: str,
        field_name: str,
    ) -> str:
        """Validate and normalize one required configuration value."""

        if not isinstance(
            value,
            str,
        ):
            raise TypeError(
                f"{field_name} must be a string"
            )

        normalized = value.strip()

        if not normalized:
            raise ValueError(
                f"{field_name} cannot be empty"
            )

        return normalized
